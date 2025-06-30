#!/usr/bin/env python3
"""
带回调的视频处理模块
支持进度更新和日志回调的视频分段处理
"""

import sys
import time
from pathlib import Path
from typing import Callable, Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from video_segmentation import process_video_segmentation, create_segment_with_ffmpeg
from utils.video_utils import validate_video_file, get_basic_video_info
from detectors.base import MultiDetector
from detectors.frame_diff import FrameDifferenceDetector
from detectors.histogram import HistogramDetector
from processors.video_processor import VideoProcessor, VideoSegment
from exporters.project_exporter import ProjectExporter
from utils.report_generator import ReportGenerator
from config import ConfigManager


class VideoProcessingWithCallbacks:
    """带回调的视频处理器"""
    
    def __init__(self, progress_callback: Optional[Callable] = None, 
                 log_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.current_step = 0
        self.total_steps = 7
        
    def log(self, message: str, level: str = "INFO"):
        """发送日志消息"""
        if self.log_callback:
            self.log_callback(message, level)
        else:
            print(f"[{level}] {message}")
    
    def update_progress(self, step_progress: float = None, description: str = ""):
        """更新进度"""
        if step_progress is not None:
            # 基于步骤的进度
            base_progress = (self.current_step / self.total_steps) * 100
            step_size = 100 / self.total_steps
            total_progress = base_progress + (step_progress * step_size / 100)
        else:
            # 步骤完成
            self.current_step += 1
            total_progress = (self.current_step / self.total_steps) * 100
        
        if self.progress_callback:
            self.progress_callback(min(total_progress, 100), description)

    def organize_segments_by_duration(self, segments, output_base_dir):
        """根据时长组织分段到不同文件夹"""
        from pathlib import Path

        categories = {
            "short": [],      # 0-5秒
            "medium": [],     # 5-30秒
            "long": []        # >30秒
        }

        for segment in segments:
            if segment.duration <= 5.0:
                category = "short"
            elif segment.duration <= 30.0:
                category = "medium"
            else:
                category = "long"

            # 更新文件路径到对应类别文件夹
            category_dir = output_base_dir / category
            original_name = Path(segment.file_path).name
            new_path = category_dir / original_name

            # 创建新的分段对象
            new_segment = VideoSegment(
                index=segment.index,
                start_time=segment.start_time,
                end_time=segment.end_time,
                duration=segment.duration,
                start_frame=segment.start_frame,
                end_frame=segment.end_frame,
                file_path=new_path,
                metadata=segment.metadata
            )

            categories[category].append(new_segment)

        return categories

    def organize_segments_by_quality(self, segments, output_base_dir):
        """根据检测置信度组织分段到不同文件夹"""
        from pathlib import Path

        categories = {
            "high_confidence": [],    # 置信度 > 0.8
            "medium_confidence": [],  # 置信度 0.5-0.8
            "low_confidence": []      # 置信度 <= 0.5
        }

        for segment in segments:
            confidence = segment.metadata.get('boundary_confidence', 0.5)

            if confidence > 0.8:
                category = "high_confidence"
            elif confidence > 0.5:
                category = "medium_confidence"
            else:
                category = "low_confidence"

            # 更新文件路径
            category_dir = output_base_dir / category
            original_name = Path(segment.file_path).name
            new_path = category_dir / original_name

            new_segment = VideoSegment(
                index=segment.index,
                start_time=segment.start_time,
                end_time=segment.end_time,
                duration=segment.duration,
                start_frame=segment.start_frame,
                end_frame=segment.end_frame,
                file_path=new_path,
                metadata=segment.metadata
            )

            categories[category].append(new_segment)

        return categories
    
    def process_video_with_callbacks(self, video_path: str, output_dir: str,
                                   organize_by: str = "duration",
                                   quality: str = "medium",
                                   enable_classification: bool = False,
                                   classification_config: dict = None) -> bool:
        """带回调的视频处理"""
        try:
            # 直接调用video_segmentation中的完整处理函数
            from video_segmentation import process_video_segmentation

            return process_video_segmentation(
                video_path=video_path,
                output_dir=output_dir,
                organize_by=organize_by,
                quality=quality,
                enable_classification=enable_classification,
                classification_config=classification_config
            )
            
        except Exception as e:
            self.log(f"❌ 处理过程中出错: {e}", "ERROR")
            import traceback
            self.log(f"错误详情: {traceback.format_exc()}", "ERROR")
            return False


def process_video_with_gui_callbacks(video_path: str, output_dir: str,
                                   organize_by: str = "duration",
                                   quality: str = "medium",
                                   progress_callback: Optional[Callable] = None,
                                   log_callback: Optional[Callable] = None,
                                   enable_classification: bool = False,
                                   classification_config: dict = None) -> bool:
    """带GUI回调的视频处理函数"""
    processor = VideoProcessingWithCallbacks(progress_callback, log_callback)
    return processor.process_video_with_callbacks(
        video_path, output_dir, organize_by, quality,
        enable_classification, classification_config
    )


# 测试函数
def test_callbacks():
    """测试回调功能"""
    def progress_callback(progress, description):
        print(f"进度: {progress:.1f}% - {description}")
    
    def log_callback(message, level):
        print(f"[{level}] {message}")
    
    # 测试处理
    video_path = "test_video.mp4"
    output_dir = "callback_test_output"
    
    if Path(video_path).exists():
        print("🧪 测试带回调的视频处理...")
        success = process_video_with_gui_callbacks(
            video_path, output_dir, "duration", "medium",
            progress_callback, log_callback
        )
        print(f"测试结果: {'成功' if success else '失败'}")
    else:
        print(f"测试视频不存在: {video_path}")


if __name__ == "__main__":
    test_callbacks()
