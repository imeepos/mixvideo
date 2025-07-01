#!/usr/bin/env python3
"""
Test Refactored Modules
测试重构后的模块
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_manager():
    """测试配置管理器"""
    print("🔧 测试配置管理器...")
    
    try:
        from config import ConfigManager, get_config
        
        # 测试配置管理器初始化
        config = ConfigManager()
        print(f"✅ 配置管理器初始化成功")
        print(f"   配置文件路径: {config.config_path}")
        
        # 测试配置获取
        app_name = config.get('app.name', 'Unknown')
        print(f"   应用名称: {app_name}")
        
        # 测试配置设置
        config.set('test.value', 'test_data')
        test_value = config.get('test.value')
        print(f"   测试值设置/获取: {test_value}")
        
        # 测试全局配置实例
        global_config = get_config()
        print(f"✅ 全局配置实例获取成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        return False


def test_detection_modules():
    """测试检测模块"""
    print("\n🔍 测试检测模块...")
    
    try:
        from core.detection import BaseDetector, ShotBoundary, DetectionResult
        from core.detection import FrameDifferenceDetector, HistogramDetector
        from core.detection import MultiDetector
        
        print("✅ 检测模块导入成功")
        
        # 测试边界对象创建
        boundary = ShotBoundary(
            frame_number=100,
            timestamp=5.0,
            confidence=0.8,
            boundary_type='cut'
        )
        print(f"   边界对象: frame={boundary.frame_number}, time={boundary.timestamp}s")
        
        # 测试检测结果对象
        result = DetectionResult(
            boundaries=[boundary],
            algorithm_name="test",
            processing_time=1.0,
            frame_count=1000,
            confidence_scores=[0.8]
        )
        print(f"   检测结果: {len(result.boundaries)} 个边界")
        
        # 测试多检测器创建
        detectors = [
            FrameDifferenceDetector(),
            HistogramDetector()
        ]
        multi_detector = MultiDetector(detectors)
        print(f"✅ 多检测器创建成功: {len(multi_detector.detectors)} 个检测器")
        
        return True
        
    except Exception as e:
        print(f"❌ 检测模块测试失败: {e}")
        return False


def test_processing_modules():
    """测试处理模块"""
    print("\n⚙️ 测试处理模块...")
    
    try:
        from core.processing import VideoProcessor, ProcessingConfig
        
        print("✅ 处理模块导入成功")
        
        # 测试处理配置
        config = ProcessingConfig(
            output_format="mp4",
            quality="high",
            min_segment_duration=2.0
        )
        print(f"   处理配置: format={config.output_format}, quality={config.quality}")
        
        # 测试视频处理器
        processor = VideoProcessor(config)
        print(f"✅ 视频处理器创建成功")
        
        # 测试性能统计
        stats = processor.get_processing_stats()
        print(f"   处理统计: {len(stats)} 项配置")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理模块测试失败: {e}")
        return False


def test_gui_components():
    """测试GUI组件"""
    print("\n🖥️ 测试GUI组件...")
    
    try:
        from gui.components import BaseTab
        
        print("✅ GUI组件导入成功")
        
        # 注意：BaseTab是抽象类，不能直接实例化
        # 这里只测试导入是否成功
        print("   BaseTab抽象类导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI组件测试失败: {e}")
        return False


def test_main_entry():
    """测试主程序入口"""
    print("\n🚀 测试主程序入口...")
    
    try:
        # 测试主程序文件是否可以导入
        import main_v2
        
        print("✅ 主程序入口导入成功")
        
        # 测试环境设置函数
        config = main_v2.setup_environment()
        print(f"   环境设置成功: {config.config_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 主程序入口测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 Shot Detection v2.0 重构模块测试")
    print("=" * 50)
    
    tests = [
        test_config_manager,
        test_detection_modules,
        test_processing_modules,
        test_gui_components,
        test_main_entry
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！重构模块基本功能正常")
    else:
        print("⚠️ 部分测试失败，需要检查相关模块")
    
    print("\n📋 重构进度:")
    print("✅ 配置管理 - 完成")
    print("✅ 检测模块 - 基础完成")
    print("✅ 处理模块 - 基础完成")
    print("🔄 GUI组件 - 进行中")
    print("⏳ 服务层 - 待开发")
    print("⏳ 测试覆盖 - 待开发")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
