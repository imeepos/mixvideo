#!/usr/bin/env python3
"""
批量视频分段处理脚本
支持目录批量处理和多种组织方式
"""

import sys
import os
import time
from pathlib import Path
from typing import List
import argparse

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from video_segmentation import process_video_segmentation
from utils.video_utils import find_video_files, format_duration, format_file_size
from loguru import logger


def setup_logging(debug: bool = False):
    """设置日志"""
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )


def batch_process_videos(input_dir: str, output_base_dir: str = None,
                        organize_by: str = "duration", quality: str = "medium",
                        recursive: bool = True) -> dict:
    """批量处理视频文件"""
    
    logger.info("🎬 批量视频分段处理系统")
    logger.info("=" * 60)
    
    # 查找视频文件
    logger.info(f"🔍 搜索视频文件: {input_dir}")
    video_files = find_video_files(input_dir, recursive)
    
    if not video_files:
        logger.error(f"未找到视频文件: {input_dir}")
        return {"success": 0, "failed": 0, "total": 0}
    
    logger.info(f"找到 {len(video_files)} 个视频文件")
    
    # 设置输出基础目录
    if output_base_dir is None:
        output_base_dir = Path(input_dir) / "batch_segments"
    
    output_base_path = Path(output_base_dir)
    output_base_path.mkdir(parents=True, exist_ok=True)
    
    # 处理统计
    results = {
        "success": 0,
        "failed": 0,
        "total": len(video_files),
        "processed_files": [],
        "failed_files": []
    }
    
    start_time = time.time()
    
    # 处理每个视频文件
    for i, video_path in enumerate(video_files, 1):
        video_name = Path(video_path).stem
        logger.info(f"\n[{i}/{len(video_files)}] 处理视频: {video_name}")
        logger.info(f"文件路径: {video_path}")
        
        # 为每个视频创建独立的输出目录
        video_output_dir = output_base_path / f"{video_name}_segments"
        
        try:
            # 处理单个视频
            success = process_video_segmentation(
                video_path,
                str(video_output_dir),
                organize_by,
                quality
            )
            
            if success:
                results["success"] += 1
                results["processed_files"].append({
                    "path": video_path,
                    "output_dir": str(video_output_dir),
                    "status": "success"
                })
                logger.info(f"✅ 处理成功: {video_name}")
            else:
                results["failed"] += 1
                results["failed_files"].append({
                    "path": video_path,
                    "error": "处理失败"
                })
                logger.error(f"❌ 处理失败: {video_name}")
                
        except Exception as e:
            results["failed"] += 1
            results["failed_files"].append({
                "path": video_path,
                "error": str(e)
            })
            logger.error(f"❌ 处理出错: {video_name} - {e}")
    
    # 显示处理结果
    total_time = time.time() - start_time
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 批量处理结果:")
    logger.info(f"  总文件数: {results['total']}")
    logger.info(f"  成功处理: {results['success']}")
    logger.info(f"  处理失败: {results['failed']}")
    logger.info(f"  成功率: {results['success']/results['total']*100:.1f}%")
    logger.info(f"  总耗时: {format_duration(total_time)}")
    logger.info(f"  平均耗时: {format_duration(total_time/results['total'])}/文件")
    
    if results["failed_files"]:
        logger.info("\n❌ 失败的文件:")
        for failed in results["failed_files"]:
            logger.info(f"  - {Path(failed['path']).name}: {failed['error']}")
    
    if results["processed_files"]:
        logger.info("\n✅ 成功处理的文件:")
        for processed in results["processed_files"]:
            logger.info(f"  - {Path(processed['path']).name} -> {processed['output_dir']}")
    
    # 显示输出目录结构
    logger.info(f"\n📁 输出目录: {output_base_path}")
    
    return results


def create_summary_report(results: dict, output_dir: str):
    """创建批量处理摘要报告"""
    try:
        summary_file = Path(output_dir) / "batch_processing_summary.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("批量视频分段处理摘要报告\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"总文件数: {results['total']}\n")
            f.write(f"成功处理: {results['success']}\n")
            f.write(f"处理失败: {results['failed']}\n")
            f.write(f"成功率: {results['success']/results['total']*100:.1f}%\n\n")
            
            if results["processed_files"]:
                f.write("成功处理的文件:\n")
                f.write("-" * 30 + "\n")
                for processed in results["processed_files"]:
                    f.write(f"- {Path(processed['path']).name}\n")
                    f.write(f"  输出目录: {processed['output_dir']}\n\n")
            
            if results["failed_files"]:
                f.write("失败的文件:\n")
                f.write("-" * 30 + "\n")
                for failed in results["failed_files"]:
                    f.write(f"- {Path(failed['path']).name}\n")
                    f.write(f"  错误: {failed['error']}\n\n")
        
        logger.info(f"📄 摘要报告已保存: {summary_file}")
        
    except Exception as e:
        logger.error(f"创建摘要报告失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="批量视频分段处理系统")
    
    parser.add_argument("input_dir", help="输入视频目录路径")
    parser.add_argument("-o", "--output", help="输出基础目录路径")
    parser.add_argument("--organize", choices=["duration", "quality", "none"], 
                       default="duration", help="分段组织方式")
    parser.add_argument("--quality", choices=["low", "medium", "high", "lossless"], 
                       default="medium", help="输出视频质量")
    parser.add_argument("--no-recursive", action="store_true", 
                       help="不递归搜索子目录")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--summary", action="store_true", 
                       help="生成摘要报告")
    
    args = parser.parse_args()
    
    setup_logging(args.debug)
    
    # 验证输入目录
    if not os.path.exists(args.input_dir):
        logger.error(f"输入目录不存在: {args.input_dir}")
        sys.exit(1)
    
    if not os.path.isdir(args.input_dir):
        logger.error(f"输入路径不是目录: {args.input_dir}")
        sys.exit(1)
    
    # 执行批量处理
    results = batch_process_videos(
        args.input_dir,
        args.output,
        args.organize,
        args.quality,
        not args.no_recursive
    )
    
    # 生成摘要报告
    if args.summary and args.output:
        create_summary_report(results, args.output)
    
    # 根据结果设置退出码
    if results["success"] == 0:
        logger.error("所有文件处理失败")
        sys.exit(1)
    elif results["failed"] > 0:
        logger.warning(f"部分文件处理失败 ({results['failed']}/{results['total']})")
        sys.exit(2)
    else:
        logger.info("所有文件处理成功")
        sys.exit(0)


if __name__ == "__main__":
    main()
