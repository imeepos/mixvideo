#!/usr/bin/env python3
"""
自动归类功能测试脚本
演示如何使用新增的归类功能
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from classification_config import ClassificationManager, ClassificationConfig
from file_organizer import FileOrganizer
from video_segmentation import process_video_segmentation


def test_classification_config():
    """测试归类配置"""
    print("🧪 测试归类配置...")
    
    # 创建归类管理器
    manager = ClassificationManager()
    
    # 测试默认配置
    print(f"默认归类模式: {manager.config.classification_mode}")
    print(f"默认置信度阈值: {manager.config.min_confidence_for_move}")
    print(f"默认输出目录: {manager.config.base_output_dir}")
    
    # 测试分类类别
    categories = manager.get_classification_categories()
    print(f"分类类别: {categories}")
    
    # 测试分段分类
    test_segments = [
        {'duration': 3.0, 'confidence': 0.8},  # 短片段，高质量
        {'duration': 15.0, 'confidence': 0.5}, # 中等片段，中等质量
        {'duration': 45.0, 'confidence': 0.3}, # 长片段，低质量
    ]
    
    for i, segment_info in enumerate(test_segments):
        category = manager.classify_segment(segment_info)
        print(f"分段 {i+1}: 时长={segment_info['duration']}s, 置信度={segment_info['confidence']:.2f} -> 分类={category}")
    
    print("✅ 归类配置测试完成\n")


def test_file_organizer():
    """测试文件组织器"""
    print("🗂️ 测试文件组织器...")
    
    # 创建测试目录和文件
    test_dir = Path("test_classification_output")
    test_dir.mkdir(exist_ok=True)
    
    # 创建一些测试文件
    test_files = []
    for i in range(3):
        test_file = test_dir / f"test_segment_{i:03d}.mp4"
        test_file.touch()  # 创建空文件
        test_files.append(str(test_file))
    
    # 创建归类管理器和文件组织器
    manager = ClassificationManager()
    manager.update_config(
        enable_classification=True,
        classification_mode="duration",
        base_output_dir=str(test_dir / "classified"),
        move_files=False,  # 使用复制模式进行测试
        min_confidence_for_move=0.5
    )
    
    organizer = FileOrganizer(manager)
    
    # 测试组织文件
    test_segments_info = [
        {'duration': 3.0, 'confidence': 0.8, 'content_description': 'short_action'},
        {'duration': 15.0, 'confidence': 0.6, 'content_description': 'medium_dialogue'},
        {'duration': 45.0, 'confidence': 0.7, 'content_description': 'long_landscape'},
    ]
    
    results = []
    for i, (file_path, segment_info) in enumerate(zip(test_files, test_segments_info)):
        print(f"组织文件 {i+1}: {os.path.basename(file_path)}")
        result = organizer.organize_segment(file_path, segment_info)
        results.append(result)
        
        if result.success:
            print(f"  ✅ 成功: {result.category} -> {result.new_path}")
        else:
            print(f"  ❌ 失败: {result.error}")
    
    # 显示操作总结
    summary = organizer.get_operation_summary()
    print(f"\n📊 操作总结:")
    print(f"  总计: {summary['total']}")
    print(f"  成功: {summary['success']}")
    print(f"  失败: {summary['failed']}")
    print(f"  分类分布: {summary['categories']}")
    
    # 清理测试文件
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    print("✅ 文件组织器测试完成\n")


def test_video_processing_with_classification():
    """测试带归类功能的视频处理"""
    print("🎬 测试带归类功能的视频处理...")
    
    # 检查是否有测试视频
    test_video = "test_video.mp4"
    if not os.path.exists(test_video):
        print(f"⚠️ 测试视频 {test_video} 不存在，跳过视频处理测试")
        return
    
    # 设置输出目录
    output_dir = "test_classification_video_output"
    
    # 归类配置
    classification_config = {
        'move_files': False,  # 复制模式
        'min_confidence_for_move': 0.5,
        'naming_mode': 'smart',
        'create_directories': True,
        'conflict_resolution': 'rename',
        'create_backup': False
    }
    
    print(f"处理视频: {test_video}")
    print(f"输出目录: {output_dir}")
    print(f"归类配置: {classification_config}")
    
    # 执行处理
    success = process_video_segmentation(
        video_path=test_video,
        output_dir=output_dir,
        organize_by="duration",
        quality="medium",
        enable_classification=True,
        classification_config=classification_config
    )
    
    if success:
        print("✅ 带归类功能的视频处理测试完成")
        
        # 检查输出结果
        output_path = Path(output_dir)
        if output_path.exists():
            print(f"\n📁 输出目录结构:")
            for item in output_path.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(output_path)
                    print(f"  📄 {relative_path}")
                elif item.is_dir() and item != output_path:
                    relative_path = item.relative_to(output_path)
                    print(f"  📁 {relative_path}/")
    else:
        print("❌ 带归类功能的视频处理测试失败")
    
    print()


def test_configuration_loading():
    """测试配置文件加载"""
    print("⚙️ 测试配置文件加载...")
    
    config_file = "classification_config.yaml"
    
    if os.path.exists(config_file):
        manager = ClassificationManager()
        manager.load_from_file(config_file)
        
        print(f"从配置文件加载: {config_file}")
        print(f"归类模式: {manager.config.classification_mode}")
        print(f"置信度阈值: {manager.config.min_confidence_for_move}")
        print(f"文件操作: {'移动' if manager.config.move_files else '复制'}")
        print(f"命名模式: {manager.config.naming_mode}")
        
        # 测试保存配置
        test_config_file = "test_classification_config.yaml"
        manager.save_to_file(test_config_file)
        print(f"配置已保存到: {test_config_file}")
        
        # 清理测试配置文件
        if os.path.exists(test_config_file):
            os.remove(test_config_file)
        
        print("✅ 配置文件加载测试完成")
    else:
        print(f"⚠️ 配置文件 {config_file} 不存在，跳过配置加载测试")
    
    print()


def main():
    """主测试函数"""
    print("🧪 智能镜头检测与分段系统 - 自动归类功能测试")
    print("=" * 60)
    
    try:
        # 测试归类配置
        test_classification_config()
        
        # 测试文件组织器
        test_file_organizer()
        
        # 测试配置文件加载
        test_configuration_loading()
        
        # 测试带归类功能的视频处理
        test_video_processing_with_classification()
        
        print("🎉 所有测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
