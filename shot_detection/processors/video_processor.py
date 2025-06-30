"""
视频处理器
负责视频分段、格式转换和质量优化
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger

from detectors.base import ShotBoundary
from config import ConfigManager


@dataclass
class VideoSegment:
    """视频分段信息"""
    index: int
    start_time: float
    end_time: float
    duration: float
    start_frame: int
    end_frame: int
    file_path: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class VideoProcessor:
    """视频处理器"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logger.bind(component="VideoProcessor")
        
    def create_segments(self, video_path: str, boundaries: List[ShotBoundary], 
                       output_dir: str) -> List[VideoSegment]:
        """创建视频分段"""
        self.logger.info(f"Creating segments for {len(boundaries)} boundaries")
        
        # 获取视频信息
        video_info = self._get_video_info(video_path)
        fps = video_info['fps']
        duration = video_info['duration']
        
        # 生成分段信息
        segments = self._generate_segment_info(boundaries, fps, duration, output_dir, video_path)
        
        # 并行处理分段
        if self.config.processing.max_workers > 1:
            segments = self._process_segments_parallel(video_path, segments)
        else:
            segments = self._process_segments_sequential(video_path, segments)
        
        self.logger.info(f"Successfully created {len(segments)} video segments")
        return segments
    
    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # 查找视频流
            video_stream = None
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                raise ValueError("No video stream found")
            
            # 提取信息
            fps = eval(video_stream.get('r_frame_rate', '25/1'))
            duration = float(data['format']['duration'])
            width = int(video_stream['width'])
            height = int(video_stream['height'])
            
            return {
                'fps': fps,
                'duration': duration,
                'width': width,
                'height': height,
                'format': data['format']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get video info: {e}")
            # 返回默认值
            return {'fps': 25.0, 'duration': 0.0, 'width': 1920, 'height': 1080}
    
    def _generate_segment_info(self, boundaries: List[ShotBoundary], fps: float, 
                              duration: float, output_dir: str, video_path: str) -> List[VideoSegment]:
        """生成分段信息"""
        segments = []
        video_name = Path(video_path).stem
        
        # 添加起始边界（如果需要）
        all_boundaries = [ShotBoundary(0, 0.0, 1.0)] + boundaries
        
        for i in range(len(all_boundaries)):
            start_boundary = all_boundaries[i]
            
            # 确定结束边界
            if i + 1 < len(all_boundaries):
                end_boundary = all_boundaries[i + 1]
                end_time = end_boundary.timestamp
                end_frame = end_boundary.frame_number
            else:
                end_time = duration
                end_frame = int(duration * fps)
            
            # 计算分段信息
            start_time = start_boundary.timestamp
            start_frame = start_boundary.frame_number
            segment_duration = end_time - start_time
            
            # 跳过过短的分段
            if segment_duration < self.config.quality.min_segment_duration:
                continue
            
            # 生成输出文件名
            output_filename = self.config.output.segment_naming_pattern.format(
                basename=video_name,
                index=i,
                ext=self.config.processing.output_format
            )
            output_path = os.path.join(output_dir, output_filename)
            
            segment = VideoSegment(
                index=i,
                start_time=start_time,
                end_time=end_time,
                duration=segment_duration,
                start_frame=start_frame,
                end_frame=end_frame,
                file_path=output_path,
                metadata={
                    'boundary_confidence': start_boundary.confidence,
                    'boundary_type': start_boundary.boundary_type
                }
            )
            
            segments.append(segment)
        
        return segments
    
    def _process_segments_parallel(self, video_path: str, segments: List[VideoSegment]) -> List[VideoSegment]:
        """并行处理分段"""
        self.logger.info(f"Processing {len(segments)} segments in parallel with {self.config.processing.max_workers} workers")
        
        successful_segments = []
        
        with ThreadPoolExecutor(max_workers=self.config.processing.max_workers) as executor:
            # 提交所有任务
            future_to_segment = {
                executor.submit(self._extract_segment, video_path, segment): segment
                for segment in segments
            }
            
            # 收集结果
            for future in as_completed(future_to_segment):
                segment = future_to_segment[future]
                try:
                    success = future.result()
                    if success:
                        successful_segments.append(segment)
                        self.logger.debug(f"Successfully processed segment {segment.index}")
                    else:
                        self.logger.error(f"Failed to process segment {segment.index}")
                except Exception as e:
                    self.logger.error(f"Error processing segment {segment.index}: {e}")
        
        return successful_segments
    
    def _process_segments_sequential(self, video_path: str, segments: List[VideoSegment]) -> List[VideoSegment]:
        """顺序处理分段"""
        self.logger.info(f"Processing {len(segments)} segments sequentially")
        
        successful_segments = []
        
        for segment in segments:
            try:
                if self._extract_segment(video_path, segment):
                    successful_segments.append(segment)
                    self.logger.debug(f"Successfully processed segment {segment.index}")
                else:
                    self.logger.error(f"Failed to process segment {segment.index}")
            except Exception as e:
                self.logger.error(f"Error processing segment {segment.index}: {e}")
        
        return successful_segments
    
    def _extract_segment(self, video_path: str, segment: VideoSegment) -> bool:
        """提取单个视频分段"""
        try:
            # 构建FFmpeg命令
            cmd = self._build_ffmpeg_command(video_path, segment)
            
            # 执行命令
            self.logger.debug(f"Executing: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode != 0:
                self.logger.error(f"FFmpeg error for segment {segment.index}: {result.stderr}")
                return False
            
            # 验证输出文件
            if not os.path.exists(segment.file_path):
                self.logger.error(f"Output file not created: {segment.file_path}")
                return False
            
            # 检查文件大小
            file_size = os.path.getsize(segment.file_path)
            if file_size < 1024:  # 小于1KB可能是错误
                self.logger.error(f"Output file too small: {segment.file_path} ({file_size} bytes)")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout extracting segment {segment.index}")
            return False
        except Exception as e:
            self.logger.error(f"Error extracting segment {segment.index}: {e}")
            return False
    
    def _build_ffmpeg_command(self, video_path: str, segment: VideoSegment) -> List[str]:
        """构建FFmpeg命令"""
        cmd = ['ffmpeg', '-y']  # -y 覆盖输出文件
        
        # 输入文件
        cmd.extend(['-i', video_path])
        
        # 时间范围
        cmd.extend(['-ss', str(segment.start_time)])
        cmd.extend(['-t', str(segment.duration)])
        
        # 编码设置
        quality_preset = self.config.processing.quality_preset
        
        if quality_preset == 'lossless':
            cmd.extend(['-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '0'])
        elif quality_preset == 'high':
            cmd.extend(['-c:v', 'libx264', '-preset', 'slow', '-crf', '18'])
        elif quality_preset == 'medium':
            cmd.extend(['-c:v', 'libx264', '-preset', 'medium', '-crf', '23'])
        else:  # low
            cmd.extend(['-c:v', 'libx264', '-preset', 'fast', '-crf', '28'])
        
        # 音频处理
        if self.config.output.preserve_audio:
            cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
        else:
            cmd.extend(['-an'])  # 无音频
        
        # 分辨率设置
        if self.config.processing.target_resolution:
            width, height = self.config.processing.target_resolution
            cmd.extend(['-s', f'{width}x{height}'])
        
        # 帧率设置
        if self.config.processing.target_fps:
            cmd.extend(['-r', str(self.config.processing.target_fps)])
        
        # 其他设置
        cmd.extend(['-avoid_negative_ts', 'make_zero'])
        cmd.extend(['-movflags', '+faststart'])
        
        # 输出文件
        cmd.append(segment.file_path)
        
        return cmd
    
    def merge_segments(self, segments: List[VideoSegment], output_path: str) -> bool:
        """合并视频分段"""
        try:
            self.logger.info(f"Merging {len(segments)} segments into {output_path}")
            
            # 创建文件列表
            list_file = output_path + '.list'
            with open(list_file, 'w') as f:
                for segment in segments:
                    f.write(f"file '{segment.file_path}'\n")
            
            # 构建FFmpeg命令
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path
            ]
            
            # 执行合并
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 清理临时文件
            os.remove(list_file)
            
            if result.returncode != 0:
                self.logger.error(f"Failed to merge segments: {result.stderr}")
                return False
            
            self.logger.info(f"Successfully merged segments to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error merging segments: {e}")
            return False
    
    def optimize_segments(self, segments: List[VideoSegment]) -> List[VideoSegment]:
        """优化分段（移除过短或过长的分段）"""
        optimized = []
        
        for segment in segments:
            # 检查时长限制
            if (segment.duration < self.config.quality.min_segment_duration or
                segment.duration > self.config.quality.max_segment_duration):
                self.logger.debug(f"Skipping segment {segment.index} due to duration: {segment.duration:.2f}s")
                continue
            
            optimized.append(segment)
        
        self.logger.info(f"Optimized segments: {len(segments)} -> {len(optimized)}")
        return optimized
