"""
视频处理工具函数
提供视频文件操作和信息获取功能
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import cv2
import numpy as np
from loguru import logger


def validate_video_file(video_path: str) -> bool:
    """验证视频文件是否有效"""
    try:
        if not os.path.exists(video_path):
            return False
        
        # 检查文件扩展名
        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
        if not any(video_path.lower().endswith(ext) for ext in valid_extensions):
            return False
        
        # 尝试打开视频文件
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
        
        # 检查是否能读取帧
        ret, frame = cap.read()
        cap.release()
        
        return ret and frame is not None
        
    except Exception as e:
        logger.error(f"Error validating video file {video_path}: {e}")
        return False


def get_video_info(video_path: str) -> Dict[str, Any]:
    """获取视频文件详细信息"""
    try:
        # 使用ffprobe获取详细信息
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # 查找视频流和音频流
        video_stream = None
        audio_streams = []
        
        for stream in data['streams']:
            if stream['codec_type'] == 'video' and video_stream is None:
                video_stream = stream
            elif stream['codec_type'] == 'audio':
                audio_streams.append(stream)
        
        if not video_stream:
            raise ValueError("No video stream found")
        
        # 提取视频信息
        fps = eval(video_stream.get('r_frame_rate', '25/1'))
        duration = float(data['format']['duration'])
        width = int(video_stream['width'])
        height = int(video_stream['height'])
        frame_count = int(video_stream.get('nb_frames', duration * fps))
        
        # 计算比特率
        bitrate = int(data['format'].get('bit_rate', 0))
        
        # 获取编码信息
        video_codec = video_stream.get('codec_name', 'unknown')
        pixel_format = video_stream.get('pix_fmt', 'unknown')
        
        # 音频信息
        audio_info = []
        for audio_stream in audio_streams:
            audio_info.append({
                'codec': audio_stream.get('codec_name', 'unknown'),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'bitrate': int(audio_stream.get('bit_rate', 0))
            })
        
        return {
            'duration': duration,
            'fps': fps,
            'frame_count': frame_count,
            'resolution': (width, height),
            'width': width,
            'height': height,
            'bitrate': bitrate,
            'video_codec': video_codec,
            'pixel_format': pixel_format,
            'audio_streams': audio_info,
            'file_size': os.path.getsize(video_path),
            'format': data['format']
        }
        
    except Exception as e:
        logger.error(f"Failed to get video info for {video_path}: {e}")
        # 返回基础信息作为后备
        return get_basic_video_info(video_path)


def get_basic_video_info(video_path: str) -> Dict[str, Any]:
    """使用OpenCV获取基础视频信息"""
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError("Cannot open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'duration': duration,
            'fps': fps,
            'frame_count': frame_count,
            'resolution': (width, height),
            'width': width,
            'height': height,
            'bitrate': 0,
            'video_codec': 'unknown',
            'pixel_format': 'unknown',
            'audio_streams': [],
            'file_size': os.path.getsize(video_path)
        }
        
    except Exception as e:
        logger.error(f"Failed to get basic video info for {video_path}: {e}")
        return {
            'duration': 0,
            'fps': 25,
            'frame_count': 0,
            'resolution': (0, 0),
            'width': 0,
            'height': 0,
            'bitrate': 0,
            'video_codec': 'unknown',
            'pixel_format': 'unknown',
            'audio_streams': [],
            'file_size': 0
        }


def extract_frames(video_path: str, frame_numbers: List[int], output_dir: str) -> List[str]:
    """提取指定帧并保存为图片"""
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Cannot open video file")
        
        extracted_files = []
        video_name = Path(video_path).stem
        
        for frame_num in frame_numbers:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if ret:
                output_file = output_dir / f"{video_name}_frame_{frame_num:06d}.jpg"
                cv2.imwrite(str(output_file), frame)
                extracted_files.append(str(output_file))
                logger.debug(f"Extracted frame {frame_num} to {output_file}")
            else:
                logger.warning(f"Failed to extract frame {frame_num}")
        
        cap.release()
        logger.info(f"Extracted {len(extracted_files)} frames from {video_path}")
        
        return extracted_files
        
    except Exception as e:
        logger.error(f"Error extracting frames from {video_path}: {e}")
        return []


def create_thumbnail(video_path: str, timestamp: float, output_path: str, size: Tuple[int, int] = (320, 240)) -> bool:
    """创建视频缩略图"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False
        
        # 跳转到指定时间
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(timestamp * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return False
        
        # 调整大小
        thumbnail = cv2.resize(frame, size)
        
        # 保存缩略图
        cv2.imwrite(output_path, thumbnail)
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating thumbnail for {video_path}: {e}")
        return False


def calculate_video_quality_metrics(video_path: str, sample_frames: int = 10) -> Dict[str, float]:
    """计算视频质量指标"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {}
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 采样帧
        sample_indices = np.linspace(0, frame_count - 1, sample_frames, dtype=int)
        
        brightness_values = []
        contrast_values = []
        sharpness_values = []
        
        for frame_idx in sample_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 计算亮度（均值）
            brightness = np.mean(gray)
            brightness_values.append(brightness)
            
            # 计算对比度（标准差）
            contrast = np.std(gray)
            contrast_values.append(contrast)
            
            # 计算清晰度（拉普拉斯方差）
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            sharpness_values.append(sharpness)
        
        cap.release()
        
        return {
            'avg_brightness': np.mean(brightness_values),
            'avg_contrast': np.mean(contrast_values),
            'avg_sharpness': np.mean(sharpness_values),
            'brightness_std': np.std(brightness_values),
            'contrast_std': np.std(contrast_values),
            'sharpness_std': np.std(sharpness_values)
        }
        
    except Exception as e:
        logger.error(f"Error calculating quality metrics for {video_path}: {e}")
        return {}


def detect_scene_complexity(video_path: str, sample_frames: int = 20) -> Dict[str, float]:
    """检测场景复杂度"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {}
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_indices = np.linspace(0, frame_count - 1, sample_frames, dtype=int)
        
        edge_densities = []
        color_diversities = []
        motion_magnitudes = []
        
        prev_frame = None
        
        for frame_idx in sample_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 边缘密度
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            edge_densities.append(edge_density)
            
            # 颜色多样性（直方图熵）
            hist = cv2.calcHist([frame], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist = hist.flatten()
            hist = hist / np.sum(hist)  # 归一化
            entropy = -np.sum(hist * np.log2(hist + 1e-10))
            color_diversities.append(entropy)
            
            # 运动幅度
            if prev_frame is not None:
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_frame, gray,
                    np.array([[gray.shape[1]//2, gray.shape[0]//2]], dtype=np.float32),
                    None
                )[0]
                if flow is not None and len(flow) > 0:
                    motion_magnitude = np.linalg.norm(flow[0])
                    motion_magnitudes.append(motion_magnitude)
            
            prev_frame = gray
        
        cap.release()
        
        return {
            'avg_edge_density': np.mean(edge_densities),
            'avg_color_diversity': np.mean(color_diversities),
            'avg_motion_magnitude': np.mean(motion_magnitudes) if motion_magnitudes else 0,
            'complexity_score': (
                np.mean(edge_densities) * 0.4 +
                np.mean(color_diversities) * 0.3 +
                (np.mean(motion_magnitudes) if motion_magnitudes else 0) * 0.3
            )
        }
        
    except Exception as e:
        logger.error(f"Error detecting scene complexity for {video_path}: {e}")
        return {}


def find_video_files(directory: str, recursive: bool = True) -> List[str]:
    """查找目录中的所有视频文件"""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
    video_files = []
    
    directory = Path(directory)
    
    if recursive:
        pattern = "**/*"
    else:
        pattern = "*"
    
    for file_path in directory.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in video_extensions:
            video_files.append(str(file_path))
    
    return sorted(video_files)


def format_duration(seconds: float) -> str:
    """格式化时长显示"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    else:
        return f"{minutes:02d}:{secs:06.3f}"


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
