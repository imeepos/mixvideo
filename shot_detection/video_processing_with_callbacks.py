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
                                   quality: str = "medium") -> bool:
        """带回调的视频处理"""
        try:
            self.log("🎬 开始智能镜头检测与分段处理", "INFO")
            self.log(f"视频文件: {video_path}", "INFO")
            self.log(f"输出目录: {output_dir}", "INFO")
            self.log(f"组织方式: {organize_by}", "INFO")
            self.log(f"输出质量: {quality}", "INFO")
            
            # 步骤1: 验证输入文件
            self.update_progress(0, "验证输入文件...")
            self.log("📋 验证输入文件", "INFO")
            
            if not validate_video_file(video_path):
                self.log("❌ 无效的视频文件", "ERROR")
                return False
            
            video_info = get_basic_video_info(video_path)
            self.log(f"📹 视频信息: {video_info['duration']:.1f}s, {video_info['fps']:.1f} FPS, ({video_info['width']}, {video_info['height']})", "INFO")
            self.update_progress(100, "文件验证完成")
            
            # 步骤2: 初始化检测器
            self.update_progress(0, "初始化检测器...")
            self.log("🤖 初始化镜头检测算法", "INFO")

            config = ConfigManager()
            multi_detector = MultiDetector()

            # 添加检测器
            frame_diff_detector = FrameDifferenceDetector(threshold=0.3)
            histogram_detector = HistogramDetector(threshold=0.4)

            multi_detector.add_detector(frame_diff_detector, weight=0.5)
            multi_detector.add_detector(histogram_detector, weight=0.5)

            if not multi_detector.initialize_all():
                self.log("❌ 检测器初始化失败", "ERROR")
                return False

            self.log("✅ 检测器初始化完成", "SUCCESS")
            self.update_progress(100, "检测器初始化完成")
            
            # 步骤3: 执行镜头检测
            self.update_progress(0, "执行镜头检测...")
            self.log("🎯 开始镜头检测", "INFO")
            
            start_time = time.time()
            detection_result = multi_detector.detect_shots_ensemble(video_path)
            detection_time = time.time() - start_time
            
            self.log(f"✅ 检测完成! 耗时: {detection_time:.2f}s", "SUCCESS")
            self.log(f"🎯 检测到 {len(detection_result.boundaries)} 个镜头边界", "INFO")
            self.update_progress(100, f"检测到 {len(detection_result.boundaries)} 个边界")
            
            # 步骤4: 生成分段信息
            self.update_progress(0, "生成分段信息...")
            self.log("📋 生成视频分段信息", "INFO")

            processor = VideoProcessor(config)
            segments = processor._generate_segment_info(
                detection_result.boundaries,
                video_info['fps'],
                video_info['duration'],
                output_dir,
                video_path
            )
            
            # 过滤短分段
            min_duration = config.quality.min_segment_duration
            filtered_segments = [s for s in segments if s.duration >= min_duration]
            
            self.log(f"📊 过滤后保留 {len(filtered_segments)} 个分段 (≥{min_duration}s)", "INFO")
            self.update_progress(100, f"生成 {len(filtered_segments)} 个分段")
            
            # 步骤5: 切分视频文件
            self.update_progress(0, "切分视频文件...")
            self.log("✂️ 开始视频切分", "INFO")
            
            # 组织分段
            from pathlib import Path
            output_path = Path(output_dir)

            if organize_by == "duration":
                self.log("📁 按时长组织分段...", "INFO")
                organized_segments = self.organize_segments_by_duration(filtered_segments, output_path)
            elif organize_by == "quality":
                self.log("📁 按质量组织分段...", "INFO")
                organized_segments = self.organize_segments_by_quality(filtered_segments, output_path)
            else:
                # 默认：所有分段放在同一目录
                organized_segments = {"all": filtered_segments}
            
            # 切分视频
            success_count = 0
            total_segments = sum(len(segments) for segments in organized_segments.values())
            
            for category, category_segments in organized_segments.items():
                self.log(f"📁 处理类别: {category} ({len(category_segments)} 个分段)", "INFO")
                
                for i, segment in enumerate(category_segments):
                    segment_progress = ((success_count + i) / total_segments) * 100
                    self.update_progress(segment_progress, f"切分视频 {success_count + i + 1}/{total_segments}")
                    
                    self.log(f"[{i+1}/{len(category_segments)}] 切分: {segment.file_path.name}", "INFO")
                    self.log(f"  时间: {segment.start_time:.2f}s - {segment.end_time:.2f}s (时长: {segment.duration:.2f}s)", "INFO")

                    success = create_segment_with_ffmpeg(video_path, segment, quality)
                    
                    if success:
                        success_count += 1
                        self.log(f"✅ 分段创建成功: {segment.file_path.name}", "SUCCESS")
                    else:
                        self.log(f"❌ 分段创建失败: {segment.file_path.name}", "ERROR")
            
            self.update_progress(100, f"视频切分完成 ({success_count}/{total_segments})")
            
            # 步骤6: 生成项目文件
            self.update_progress(0, "生成项目文件...")
            self.log("📤 生成项目文件", "INFO")
            
            exporter = ProjectExporter(config)
            exporter.export_all_formats(video_path, detection_result, filtered_segments, output_dir)
            
            self.log("✅ 项目文件生成完成", "SUCCESS")
            self.update_progress(100, "项目文件生成完成")
            
            # 步骤7: 生成分析报告
            self.update_progress(0, "生成分析报告...")
            self.log("📊 生成分析报告", "INFO")
            
            report_generator = ReportGenerator(config)
            report_generator.generate_report(video_path, detection_result, filtered_segments, output_dir)
            
            self.log("✅ 分析报告生成完成", "SUCCESS")
            self.update_progress(100, "分析报告生成完成")
            
            # 清理资源
            multi_detector.cleanup_all()
            
            # 显示最终结果
            self.log("📊 处理结果:", "INFO")
            self.log(f"  总分段数: {len(filtered_segments)}", "INFO")
            self.log(f"  成功切分: {success_count}", "INFO")
            self.log(f"  失败数量: {len(filtered_segments) - success_count}", "INFO")
            self.log(f"  成功率: {(success_count/len(filtered_segments)*100):.1f}%", "INFO")
            
            self.log("🎉 视频分段和切分完成!", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"❌ 处理过程中出错: {e}", "ERROR")
            import traceback
            self.log(f"错误详情: {traceback.format_exc()}", "ERROR")
            return False


def process_video_with_gui_callbacks(video_path: str, output_dir: str, 
                                   organize_by: str = "duration", 
                                   quality: str = "medium",
                                   progress_callback: Optional[Callable] = None,
                                   log_callback: Optional[Callable] = None) -> bool:
    """带GUI回调的视频处理函数"""
    processor = VideoProcessingWithCallbacks(progress_callback, log_callback)
    return processor.process_video_with_callbacks(video_path, output_dir, organize_by, quality)


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
