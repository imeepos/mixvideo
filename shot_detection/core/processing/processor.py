"""
Video Processor Module
视频处理器模块
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from pathlib import Path
import cv2
import numpy as np
from loguru import logger

from ..detection.base import DetectionResult, ShotBoundary


@dataclass
class ProcessingConfig:
    """处理配置"""
    output_format: str = "mp4"
    quality: str = "high"  # low, medium, high
    resolution: Optional[tuple] = None  # (width, height)
    fps: Optional[float] = None
    codec: str = "h264"
    audio_codec: str = "aac"
    bitrate: Optional[str] = None
    
    # 分割相关配置
    min_segment_duration: float = 1.0  # 最小片段时长（秒）
    max_segment_duration: float = 300.0  # 最大片段时长（秒）
    
    # 输出配置
    output_dir: Optional[Path] = None
    filename_template: str = "{base_name}_segment_{index:03d}.{ext}"
    
    # 处理选项
    enable_preview: bool = False
    preview_size: tuple = (320, 240)
    enable_metadata: bool = True


class VideoProcessor:
    """视频处理器"""
    
    def __init__(self, config: ProcessingConfig = None):
        """
        初始化视频处理器
        
        Args:
            config: 处理配置
        """
        self.config = config or ProcessingConfig()
        self.logger = logger.bind(component="VideoProcessor")
        
        # 质量预设
        self.quality_presets = {
            "low": {"crf": 28, "preset": "fast"},
            "medium": {"crf": 23, "preset": "medium"},
            "high": {"crf": 18, "preset": "slow"}
        }
    
    def process_video(self, video_path: str, detection_result: DetectionResult,
                     progress_callback: Callable[[float], None] = None) -> Dict[str, Any]:
        """
        处理视频
        
        Args:
            video_path: 视频文件路径
            detection_result: 检测结果
            progress_callback: 进度回调函数
            
        Returns:
            处理结果字典
        """
        self.logger.info(f"Starting video processing: {video_path}")
        
        try:
            # 获取视频信息
            video_info = self._get_video_info(video_path)
            
            # 生成分割点
            segments = self._generate_segments(detection_result, video_info)
            
            # 处理分割
            results = self._process_segments(video_path, segments, progress_callback)
            
            return {
                "success": True,
                "video_info": video_info,
                "segments": segments,
                "output_files": results,
                "total_segments": len(segments)
            }
            
        except Exception as e:
            self.logger.error(f"Error processing video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        cap = cv2.VideoCapture(video_path)
        
        try:
            info = {
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": cap.get(cv2.CAP_PROP_FPS),
                "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
                "codec": int(cap.get(cv2.CAP_PROP_FOURCC))
            }
            
            self.logger.debug(f"Video info: {info}")
            return info
            
        finally:
            cap.release()
    
    def _generate_segments(self, detection_result: DetectionResult, 
                          video_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成分割片段"""
        segments = []
        boundaries = detection_result.boundaries
        
        if not boundaries:
            # 如果没有检测到边界，返回整个视频作为一个片段
            segments.append({
                "start_time": 0.0,
                "end_time": video_info["duration"],
                "start_frame": 0,
                "end_frame": video_info["frame_count"] - 1,
                "confidence": 1.0,
                "index": 0
            })
            return segments
        
        # 添加视频开始边界
        if boundaries[0].timestamp > 0:
            boundaries.insert(0, ShotBoundary(
                frame_number=0,
                timestamp=0.0,
                confidence=1.0,
                boundary_type='start'
            ))
        
        # 添加视频结束边界
        if boundaries[-1].timestamp < video_info["duration"]:
            boundaries.append(ShotBoundary(
                frame_number=video_info["frame_count"] - 1,
                timestamp=video_info["duration"],
                confidence=1.0,
                boundary_type='end'
            ))
        
        # 生成片段
        for i in range(len(boundaries) - 1):
            start_boundary = boundaries[i]
            end_boundary = boundaries[i + 1]
            
            duration = end_boundary.timestamp - start_boundary.timestamp
            
            # 检查片段时长限制
            if duration < self.config.min_segment_duration:
                self.logger.debug(f"Skipping short segment: {duration:.2f}s")
                continue
            
            if duration > self.config.max_segment_duration:
                # 分割长片段
                sub_segments = self._split_long_segment(
                    start_boundary, end_boundary, video_info
                )
                segments.extend(sub_segments)
            else:
                segments.append({
                    "start_time": start_boundary.timestamp,
                    "end_time": end_boundary.timestamp,
                    "start_frame": start_boundary.frame_number,
                    "end_frame": end_boundary.frame_number,
                    "confidence": min(start_boundary.confidence, end_boundary.confidence),
                    "index": len(segments)
                })
        
        self.logger.info(f"Generated {len(segments)} segments")
        return segments
    
    def _split_long_segment(self, start_boundary: ShotBoundary, 
                           end_boundary: ShotBoundary,
                           video_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分割长片段"""
        segments = []
        total_duration = end_boundary.timestamp - start_boundary.timestamp
        num_splits = int(np.ceil(total_duration / self.config.max_segment_duration))
        
        for i in range(num_splits):
            segment_start = start_boundary.timestamp + i * self.config.max_segment_duration
            segment_end = min(
                start_boundary.timestamp + (i + 1) * self.config.max_segment_duration,
                end_boundary.timestamp
            )
            
            start_frame = int(segment_start * video_info["fps"])
            end_frame = int(segment_end * video_info["fps"])
            
            segments.append({
                "start_time": segment_start,
                "end_time": segment_end,
                "start_frame": start_frame,
                "end_frame": end_frame,
                "confidence": 0.5,  # 人工分割的置信度较低
                "index": len(segments),
                "is_split": True
            })
        
        return segments
    
    def _process_segments(self, video_path: str, segments: List[Dict[str, Any]],
                         progress_callback: Callable[[float], None] = None) -> List[str]:
        """处理分割片段"""
        output_files = []
        total_segments = len(segments)
        
        for i, segment in enumerate(segments):
            try:
                output_file = self._extract_segment(video_path, segment)
                output_files.append(output_file)
                
                if progress_callback:
                    progress = (i + 1) / total_segments
                    progress_callback(progress)
                    
            except Exception as e:
                self.logger.error(f"Error processing segment {i}: {e}")
                continue
        
        return output_files
    
    def _extract_segment(self, video_path: str, segment: Dict[str, Any]) -> str:
        """提取视频片段"""
        input_path = Path(video_path)
        output_dir = self.config.output_dir or input_path.parent / "segments"
        output_dir.mkdir(exist_ok=True)
        
        # 生成输出文件名
        output_filename = self.config.filename_template.format(
            base_name=input_path.stem,
            index=segment["index"],
            ext=self.config.output_format
        )
        output_path = output_dir / output_filename
        
        # 使用ffmpeg提取片段（这里简化为示例）
        # 实际实现需要调用ffmpeg或使用moviepy等库
        self.logger.info(f"Extracting segment {segment['index']}: "
                        f"{segment['start_time']:.2f}s - {segment['end_time']:.2f}s")
        
        # TODO: 实现实际的视频分割逻辑
        # 这里返回模拟的输出路径
        return str(output_path)
    
    def create_preview(self, video_path: str, segments: List[Dict[str, Any]]) -> str:
        """创建预览视频"""
        if not self.config.enable_preview:
            return ""
        
        # TODO: 实现预览视频创建
        self.logger.info("Creating preview video")
        return ""
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return {
            "config": self.config.__dict__,
            "quality_presets": self.quality_presets
        }
