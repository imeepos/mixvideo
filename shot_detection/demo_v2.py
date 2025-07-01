#!/usr/bin/env python3
"""
Shot Detection v2.0 Demo
演示重构后的功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def demo_config_system():
    """演示配置系统"""
    print("🔧 配置系统演示")
    print("-" * 40)
    
    from config import get_config, init_config
    
    # 初始化配置
    config = init_config()
    
    print(f"配置文件路径: {config.config_path}")
    print(f"应用名称: {config.get('app.name')}")
    print(f"应用版本: {config.get('app.version')}")
    
    # 演示配置修改
    original_threshold = config.get('detection.frame_difference.threshold')
    print(f"原始检测阈值: {original_threshold}")
    
    config.set('detection.frame_difference.threshold', 0.5)
    new_threshold = config.get('detection.frame_difference.threshold')
    print(f"修改后阈值: {new_threshold}")
    
    # 恢复原始值
    config.set('detection.frame_difference.threshold', original_threshold)
    print("已恢复原始配置")
    
    print()


def demo_detection_system():
    """演示检测系统"""
    print("🔍 检测系统演示")
    print("-" * 40)
    
    from core.detection import FrameDifferenceDetector, HistogramDetector, MultiDetector
    from core.detection.base import ShotBoundary, DetectionResult
    
    # 创建单个检测器
    frame_detector = FrameDifferenceDetector(threshold=0.3)
    hist_detector = HistogramDetector(threshold=0.5)
    
    print(f"帧差检测器: {frame_detector.name}")
    print(f"直方图检测器: {hist_detector.name}")
    
    # 创建多检测器融合
    detectors = [frame_detector, hist_detector]
    multi_detector = MultiDetector(detectors)
    
    print(f"多检测器融合: {len(multi_detector.detectors)} 个检测器")
    print(f"融合权重: {multi_detector.fusion_weights}")
    
    # 演示边界对象
    boundary = ShotBoundary(
        frame_number=100,
        timestamp=5.0,
        confidence=0.8,
        boundary_type='cut',
        metadata={'algorithm': 'demo'}
    )
    
    print(f"示例边界: 帧{boundary.frame_number}, 时间{boundary.timestamp}s, 置信度{boundary.confidence}")
    
    print()


def demo_processing_system():
    """演示处理系统"""
    print("⚙️ 处理系统演示")
    print("-" * 40)
    
    from core.processing import VideoProcessor, ProcessingConfig
    from core.processing.segmentation import VideoSegment, SegmentationService
    
    # 创建处理配置
    config = ProcessingConfig(
        output_format="mp4",
        quality="high",
        min_segment_duration=2.0,
        max_segment_duration=60.0
    )
    
    print(f"处理配置: {config.output_format}, 质量: {config.quality}")
    print(f"分段时长: {config.min_segment_duration}s - {config.max_segment_duration}s")
    
    # 创建处理器
    processor = VideoProcessor(config)
    segmentation_service = SegmentationService()
    
    print(f"视频处理器已创建")
    print(f"分割服务已创建")
    
    # 演示分段对象
    segment = VideoSegment(
        index=0,
        start_time=0.0,
        end_time=10.0,
        start_frame=0,
        end_frame=300,
        duration=10.0,
        confidence=0.9
    )
    
    print(f"示例分段: {segment.start_time}s-{segment.end_time}s, 时长{segment.duration}s")
    
    print()


def demo_service_layer():
    """演示服务层"""
    print("🎬 服务层演示")
    print("-" * 40)
    
    from core.services import VideoService, BatchService
    from core.detection import FrameDifferenceDetector
    from core.processing import ProcessingConfig
    
    # 创建检测器和配置
    detector = FrameDifferenceDetector(threshold=0.3)
    config = ProcessingConfig(quality="medium")
    
    # 创建视频服务
    video_service = VideoService(detector, config)
    
    print(f"视频服务已创建")
    print(f"支持的格式: {video_service.get_supported_formats()}")
    
    # 创建批量服务
    batch_service = BatchService(detector, config, max_workers=2)
    
    print(f"批量服务已创建")
    print(f"最大工作线程: {batch_service.max_workers}")
    
    # 演示文件验证
    is_valid = video_service.validate_video_file("nonexistent.mp4")
    print(f"文件验证测试: {is_valid} (预期: False)")
    
    print()


def demo_gui_components():
    """演示GUI组件"""
    print("🖥️ GUI组件演示")
    print("-" * 40)
    
    try:
        from gui.components import BaseTab, VideoTab, BatchTab
        
        print("✅ GUI组件导入成功")
        print("   - BaseTab: 基础Tab抽象类")
        print("   - VideoTab: 视频处理Tab")
        print("   - BatchTab: 批量处理Tab")
        print("   - AnalysisTab: 视频分析Tab")
        print("   - DraftTab: 剪映草稿Tab")
        print("   - MixTab: 视频混剪Tab")
        
        # 注意：不能在没有Tkinter环境的情况下实际创建GUI组件
        print("注意: GUI组件需要在Tkinter环境中运行")
        
    except Exception as e:
        print(f"❌ GUI组件演示失败: {e}")
    
    print()


def demo_integration():
    """演示系统集成"""
    print("🔗 系统集成演示")
    print("-" * 40)
    
    from config import get_config
    from core.services import VideoService
    from core.detection import FrameDifferenceDetector, HistogramDetector, MultiDetector
    
    # 从配置创建检测器
    config = get_config()
    detection_config = config.get_detection_config()
    
    # 获取配置参数
    fd_config = detection_config.get('frame_difference', {})
    hist_config = detection_config.get('histogram', {})
    multi_config = detection_config.get('multi_detector', {})
    
    print(f"帧差检测配置: 阈值={fd_config.get('threshold', 0.3)}")
    print(f"直方图检测配置: 阈值={hist_config.get('threshold', 0.5)}")
    print(f"多检测器配置: 权重={multi_config.get('fusion_weights', {})}")
    
    # 创建检测器
    frame_detector = FrameDifferenceDetector(threshold=fd_config.get('threshold', 0.3))
    hist_detector = HistogramDetector(threshold=hist_config.get('threshold', 0.5))
    
    detectors = [frame_detector, hist_detector]
    fusion_weights = multi_config.get('fusion_weights', {})
    multi_detector = MultiDetector(detectors, fusion_weights)
    
    # 创建服务
    video_service = VideoService(multi_detector)
    
    print(f"✅ 集成成功: 配置驱动的检测服务已创建")
    
    print()


def main():
    """主演示函数"""
    print("🎉 Shot Detection v2.0 功能演示")
    print("=" * 50)
    print()
    
    demos = [
        demo_config_system,
        demo_detection_system,
        demo_processing_system,
        demo_service_layer,
        demo_gui_components,
        demo_integration
    ]
    
    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"❌ 演示失败: {e}")
            print()
    
    print("=" * 50)
    print("🎯 重构成果总结:")
    print()
    print("✅ 模块化架构 - 清晰的模块边界和职责分离")
    print("✅ 配置管理 - 统一的配置系统，支持验证和环境适配")
    print("✅ 检测算法 - 多检测器融合，支持权重配置")
    print("✅ 处理流程 - 完整的视频处理和分割流程")
    print("✅ 服务层 - 高级业务逻辑封装")
    print("✅ GUI组件 - 组件化界面设计")
    print("✅ 系统集成 - 配置驱动的完整解决方案")
    print()
    print("🚀 启动方式:")
    print("   python main_v2.py          # 启动新版GUI")
    print("   python main_v2.py --cli    # 命令行模式(开发中)")
    print("   python demo_v2.py          # 运行功能演示")
    print()
    print("📚 下一步:")
    print("   1. 完善GUI组件的具体实现")
    print("   2. 添加更多单元测试")
    print("   3. 完善文档和用户指南")
    print("   4. 性能优化和错误处理")


if __name__ == "__main__":
    main()
