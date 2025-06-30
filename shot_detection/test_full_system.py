#!/usr/bin/env python3
"""
完整系统测试脚本
测试镜头检测、视频分段、项目导出等完整功能
"""

import sys
import os
import time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import ConfigManager, load_config
from detectors.frame_diff import FrameDifferenceDetector
from detectors.histogram import HistogramDetector
from detectors.base import MultiDetector
from processors.video_processor import VideoProcessor
from exporters.project_exporter import ProjectExporter
from utils.video_utils import validate_video_file, get_basic_video_info
from utils.report_generator import ReportGenerator
from loguru import logger


def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )


def test_full_system():
    """测试完整系统功能"""
    setup_logging()
    
    logger.info("🎬 智能镜头检测与分段系统 - 完整功能测试")
    logger.info("=" * 60)
    
    # 使用现有的测试视频
    video_path = "test_video.mp4"
    output_dir = Path("test_output")
    
    if not os.path.exists(video_path):
        logger.error(f"测试视频不存在: {video_path}")
        return False
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    
    try:
        # 1. 加载配置
        logger.info("📋 加载系统配置...")
        config = load_config("config.yaml")
        
        # 2. 验证视频文件
        logger.info("🔍 验证视频文件...")
        if not validate_video_file(video_path):
            logger.error("视频文件验证失败")
            return False
        
        video_info = get_basic_video_info(video_path)
        logger.info(f"视频信息: {video_info['duration']:.1f}s, {video_info['fps']:.1f} FPS, {video_info['resolution']}")
        
        # 3. 初始化检测器
        logger.info("🤖 初始化检测算法...")
        multi_detector = MultiDetector()
        
        # 添加帧差检测器
        frame_diff_detector = FrameDifferenceDetector(threshold=0.3)
        multi_detector.add_detector(frame_diff_detector, weight=0.5)
        
        # 添加直方图检测器
        histogram_detector = HistogramDetector(threshold=0.4)
        multi_detector.add_detector(histogram_detector, weight=0.5)
        
        # 初始化所有检测器
        if not multi_detector.initialize_all():
            logger.error("检测器初始化失败")
            return False
        
        # 4. 执行镜头检测
        logger.info("🎯 执行镜头检测...")
        start_time = time.time()
        
        detection_result = multi_detector.detect_shots_ensemble(video_path)
        detection_time = time.time() - start_time
        
        logger.info(f"检测完成! 耗时: {detection_time:.2f}s")
        logger.info(f"检测到 {len(detection_result.boundaries)} 个镜头边界")
        
        if detection_result.boundaries:
            logger.info("检测到的镜头边界:")
            for i, boundary in enumerate(detection_result.boundaries, 1):
                logger.info(f"  {i}. 时间: {boundary.timestamp:.2f}s, 帧: {boundary.frame_number}, 置信度: {boundary.confidence:.3f}")
        
        # 5. 生成视频分段（模拟）
        logger.info("✂️ 生成视频分段信息...")
        video_processor = VideoProcessor(config)
        
        # 生成分段信息（不实际切割视频）
        segments = []
        if detection_result.boundaries:
            fps = video_info['fps']
            duration = video_info['duration']
            
            # 添加起始边界
            all_boundaries = [type('Boundary', (), {'frame_number': 0, 'timestamp': 0.0, 'confidence': 1.0})()] + detection_result.boundaries
            
            for i in range(len(all_boundaries)):
                start_boundary = all_boundaries[i]
                
                if i + 1 < len(all_boundaries):
                    end_boundary = all_boundaries[i + 1]
                    end_time = end_boundary.timestamp
                else:
                    end_time = duration
                
                segment_duration = end_time - start_boundary.timestamp
                if segment_duration > 0.5:  # 只保留大于0.5秒的分段
                    segment = type('Segment', (), {
                        'index': i,
                        'start_time': start_boundary.timestamp,
                        'end_time': end_time,
                        'duration': segment_duration,
                        'start_frame': start_boundary.frame_number,
                        'end_frame': int(end_time * fps),
                        'file_path': str(output_dir / f"segment_{i:03d}.mp4"),
                        'metadata': {'confidence': start_boundary.confidence}
                    })()
                    segments.append(segment)
        
        logger.info(f"生成 {len(segments)} 个视频分段")
        
        # 6. 导出项目文件
        logger.info("📤 导出项目文件...")
        project_exporter = ProjectExporter(config)
        project_exporter.export_all_formats(video_path, detection_result, segments, str(output_dir))
        
        # 7. 生成分析报告
        logger.info("📊 生成分析报告...")
        report_generator = ReportGenerator(config)
        report_generator.generate_report(video_path, detection_result, segments, str(output_dir))
        
        # 8. 显示输出文件
        logger.info("📁 生成的文件:")
        for file_path in output_dir.glob("*"):
            if file_path.is_file():
                logger.info(f"  - {file_path.name}")
        
        # 9. 清理资源
        multi_detector.cleanup_all()
        
        logger.info("✅ 完整功能测试成功完成!")
        return True
        
    except Exception as e:
        logger.error(f"测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_system()
    sys.exit(0 if success else 1)
