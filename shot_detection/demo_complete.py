#!/usr/bin/env python3
"""
完整功能演示脚本
展示智能镜头检测与分段系统的所有功能
"""

import sys
import os
import time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from video_segmentation import process_video_segmentation
from batch_segmentation import batch_process_videos
from performance_test import performance_benchmark
from loguru import logger


def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )


def demo_single_video():
    """演示单个视频处理"""
    logger.info("🎬 演示1: 单个视频自动分段")
    logger.info("-" * 40)
    
    video_path = "test_video.mp4"
    if not os.path.exists(video_path):
        logger.error(f"测试视频不存在: {video_path}")
        return False
    
    # 按时长组织
    logger.info("📁 按时长组织分段...")
    success1 = process_video_segmentation(
        video_path, 
        "demo_duration", 
        "duration", 
        "medium"
    )
    
    # 按质量组织
    logger.info("\n📁 按质量组织分段...")
    success2 = process_video_segmentation(
        video_path, 
        "demo_quality", 
        "quality", 
        "high"
    )
    
    return success1 and success2


def demo_batch_processing():
    """演示批量处理"""
    logger.info("\n🎬 演示2: 批量视频处理")
    logger.info("-" * 40)
    
    # 创建测试目录结构
    test_dir = Path("test_videos")
    test_dir.mkdir(exist_ok=True)
    
    # 复制测试视频到不同子目录
    import shutil
    
    if os.path.exists("test_video.mp4"):
        # 创建子目录
        (test_dir / "category1").mkdir(exist_ok=True)
        (test_dir / "category2").mkdir(exist_ok=True)
        
        # 复制视频文件
        shutil.copy("test_video.mp4", test_dir / "category1" / "video1.mp4")
        shutil.copy("test_video.mp4", test_dir / "category2" / "video2.mp4")
        
        logger.info(f"创建测试目录结构: {test_dir}")
        
        # 执行批量处理
        results = batch_process_videos(
            str(test_dir),
            "batch_demo_output",
            "duration",
            "medium",
            True
        )
        
        return results["success"] > 0
    else:
        logger.error("测试视频不存在，跳过批量处理演示")
        return False


def demo_performance_test():
    """演示性能测试"""
    logger.info("\n🎬 演示3: 性能基准测试")
    logger.info("-" * 40)
    
    return performance_benchmark()


def demo_advanced_features():
    """演示高级功能"""
    logger.info("\n🎬 演示4: 高级功能展示")
    logger.info("-" * 40)
    
    video_path = "test_video.mp4"
    if not os.path.exists(video_path):
        logger.error(f"测试视频不存在: {video_path}")
        return False
    
    # 无损质量处理
    logger.info("🔧 无损质量处理...")
    success1 = process_video_segmentation(
        video_path, 
        "demo_lossless", 
        "quality", 
        "lossless"
    )
    
    # 低质量快速处理
    logger.info("\n⚡ 低质量快速处理...")
    success2 = process_video_segmentation(
        video_path, 
        "demo_fast", 
        "none", 
        "low"
    )
    
    return success1 and success2


def show_results_summary():
    """显示结果摘要"""
    logger.info("\n📊 演示结果摘要")
    logger.info("=" * 50)
    
    # 统计生成的文件
    demo_dirs = [
        "demo_duration", "demo_quality", "demo_lossless", "demo_fast",
        "batch_demo_output", "test_output", "video_segments", "video_segments_quality"
    ]
    
    total_segments = 0
    total_size = 0
    
    for demo_dir in demo_dirs:
        if os.path.exists(demo_dir):
            for root, dirs, files in os.walk(demo_dir):
                for file in files:
                    if file.endswith(('.mp4', '.avi', '.mov')):
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        total_segments += 1
                        total_size += file_size
    
    logger.info(f"📹 总生成分段数: {total_segments}")
    logger.info(f"💾 总文件大小: {total_size/1024/1024:.1f} MB")
    
    # 显示目录结构
    logger.info("\n📁 生成的目录结构:")
    for demo_dir in demo_dirs:
        if os.path.exists(demo_dir):
            logger.info(f"  {demo_dir}/")
            for item in os.listdir(demo_dir):
                item_path = os.path.join(demo_dir, item)
                if os.path.isdir(item_path):
                    count = len([f for f in os.listdir(item_path) if f.endswith(('.mp4', '.avi', '.mov'))])
                    logger.info(f"    {item}/ ({count} 个视频)")


def cleanup_demo_files():
    """清理演示文件"""
    logger.info("\n🧹 清理演示文件...")
    
    import shutil
    
    cleanup_dirs = [
        "demo_duration", "demo_quality", "demo_lossless", "demo_fast",
        "batch_demo_output", "test_videos"
    ]
    
    for cleanup_dir in cleanup_dirs:
        if os.path.exists(cleanup_dir):
            try:
                shutil.rmtree(cleanup_dir)
                logger.info(f"  已删除: {cleanup_dir}")
            except Exception as e:
                logger.error(f"  删除失败: {cleanup_dir} - {e}")


def main():
    """主演示函数"""
    setup_logging()
    
    logger.info("🎬 智能镜头检测与分段系统 - 完整功能演示")
    logger.info("=" * 60)
    logger.info("本演示将展示系统的所有核心功能:")
    logger.info("1. 单个视频自动分段")
    logger.info("2. 批量视频处理")
    logger.info("3. 性能基准测试")
    logger.info("4. 高级功能展示")
    logger.info("=" * 60)
    
    start_time = time.time()
    results = []
    
    try:
        # 演示1: 单个视频处理
        results.append(("单个视频处理", demo_single_video()))
        
        # 演示2: 批量处理
        results.append(("批量视频处理", demo_batch_processing()))
        
        # 演示3: 性能测试
        results.append(("性能基准测试", demo_performance_test()))
        
        # 演示4: 高级功能
        results.append(("高级功能展示", demo_advanced_features()))
        
        # 显示结果摘要
        show_results_summary()
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ 演示被用户中断")
    except Exception as e:
        logger.error(f"\n❌ 演示过程中出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 显示演示结果
    total_time = time.time() - start_time
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 演示完成结果:")
    
    success_count = 0
    for name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        logger.info(f"  {name}: {status}")
        if success:
            success_count += 1
    
    logger.info(f"\n📊 总体结果: {success_count}/{len(results)} 个演示成功")
    logger.info(f"⏱️ 总耗时: {total_time:.1f} 秒")
    
    # 询问是否清理文件
    try:
        response = input("\n🗑️ 是否清理演示生成的文件? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            cleanup_demo_files()
            logger.info("✅ 清理完成")
        else:
            logger.info("📁 演示文件已保留，您可以手动查看")
    except KeyboardInterrupt:
        logger.info("\n📁 演示文件已保留")
    
    logger.info("\n🎉 演示程序结束，感谢使用智能镜头检测与分段系统！")


if __name__ == "__main__":
    main()
