#!/usr/bin/env python3
"""
测试配置修复
验证ConfigManager的正确属性访问
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import ConfigManager


def test_config_access():
    """测试配置访问"""
    print("🧪 测试ConfigManager配置访问...")
    
    try:
        config = ConfigManager()
        
        print("✅ ConfigManager创建成功")
        print(f"可用属性: {dir(config)}")
        
        # 测试各个配置部分
        print(f"detection配置: {config.detection}")
        print(f"processing配置: {config.processing}")
        print(f"output配置: {config.output}")
        print(f"quality配置: {config.quality}")
        print(f"system配置: {config.system}")
        
        # 测试min_segment_duration访问
        min_duration = config.quality.min_segment_duration
        print(f"✅ min_segment_duration: {min_duration}")
        
        print("🎉 配置访问测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 配置访问测试失败: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return False


def test_video_processing_import():
    """测试视频处理模块导入"""
    print("\n🧪 测试视频处理模块导入...")
    
    try:
        from video_processing_with_callbacks import VideoProcessingWithCallbacks
        print("✅ VideoProcessingWithCallbacks导入成功")
        
        # 创建处理器实例
        processor = VideoProcessingWithCallbacks()
        print("✅ VideoProcessingWithCallbacks实例创建成功")
        
        print("🎉 视频处理模块导入测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 视频处理模块导入失败: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return False


def main():
    """主函数"""
    print("🔧 配置修复验证测试")
    print("=" * 50)
    
    # 测试配置访问
    config_ok = test_config_access()
    
    # 测试模块导入
    import_ok = test_video_processing_import()
    
    print("\n📊 测试结果:")
    print(f"配置访问: {'✅ 通过' if config_ok else '❌ 失败'}")
    print(f"模块导入: {'✅ 通过' if import_ok else '❌ 失败'}")
    
    if config_ok and import_ok:
        print("\n🎉 所有测试通过！配置修复成功。")
    else:
        print("\n❌ 部分测试失败，需要进一步修复。")


if __name__ == "__main__":
    main()
