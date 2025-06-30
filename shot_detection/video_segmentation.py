#!/usr/bin/env python3
"""
完整的视频自动分段和切分系统
包含镜头检测、FFmpeg切分、文件组织等完整功能
"""

import sys
import os
import time
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import ConfigManager, load_config
from detectors.frame_diff import FrameDifferenceDetector
from detectors.histogram import HistogramDetector
from detectors.base import MultiDetector
from processors.video_processor import VideoProcessor, VideoSegment
from exporters.project_exporter import ProjectExporter
from utils.video_utils import validate_video_file, get_basic_video_info
from utils.report_generator import ReportGenerator
from classification_config import get_classification_manager
from file_organizer import create_file_organizer
from loguru import logger


def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )


def check_ffmpeg():
    """检查FFmpeg是否可用"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("✅ FFmpeg 可用")
            return True
        else:
            logger.error("❌ FFmpeg 不可用")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.error("❌ FFmpeg 未安装或不在PATH中")
        return False


def find_ffmpeg_executable():
    """查找可用的FFmpeg可执行文件"""
    # 可能的FFmpeg路径
    possible_paths = [
        'ffmpeg',  # 系统PATH中的ffmpeg
        'bin/ffmpeg.exe',  # 本地bin目录
        'ffmpeg.exe',  # 当前目录
        'ffmpeg/bin/ffmpeg.exe',  # ffmpeg子目录
        Path(__file__).parent / 'bin' / 'ffmpeg.exe',  # 相对于脚本的bin目录
    ]

    for path in possible_paths:
        try:
            result = subprocess.run([str(path), '-version'],
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"找到FFmpeg: {path}")
                return str(path)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            continue

    return None


def create_segment_with_ffmpeg(video_path: str, segment: VideoSegment,
                              quality: str = "medium") -> bool:
    """使用FFmpeg创建视频分段"""
    try:
        # 查找FFmpeg可执行文件
        ffmpeg_cmd = find_ffmpeg_executable()
        if not ffmpeg_cmd:
            logger.error("❌ 未找到FFmpeg可执行文件")
            logger.error("请安装FFmpeg或运行: python install_ffmpeg.py")
            return False

        # 确保输出目录存在
        output_dir = Path(segment.file_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # 构建FFmpeg命令
        cmd = [
            ffmpeg_cmd, '-y',  # 使用找到的FFmpeg路径，覆盖输出文件
            '-i', video_path,  # 输入文件
            '-ss', str(segment.start_time),  # 开始时间
            '-t', str(segment.duration),  # 持续时间
        ]
        
        # 根据质量设置编码参数
        if quality == "lossless":
            cmd.extend(['-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '0'])
        elif quality == "high":
            cmd.extend(['-c:v', 'libx264', '-preset', 'slow', '-crf', '18'])
        elif quality == "medium":
            cmd.extend(['-c:v', 'libx264', '-preset', 'medium', '-crf', '23'])
        else:  # low
            cmd.extend(['-c:v', 'libx264', '-preset', 'fast', '-crf', '28'])
        
        # 音频设置
        cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
        
        # 其他设置
        cmd.extend([
            '-avoid_negative_ts', 'make_zero',
            '-movflags', '+faststart',
            str(segment.file_path)  # 确保路径是字符串
        ])
        
        # 执行命令
        logger.debug(f"执行FFmpeg命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode != 0:
            logger.error(f"FFmpeg错误: {result.stderr}")
            return False
        
        # 验证输出文件
        if not os.path.exists(segment.file_path):
            logger.error(f"输出文件未创建: {segment.file_path}")
            return False
        
        # 检查文件大小
        file_size = os.path.getsize(segment.file_path)
        if file_size < 1024:  # 小于1KB可能是错误
            logger.error(f"输出文件过小: {segment.file_path} ({file_size} bytes)")
            return False
        
        logger.info(f"✅ 分段创建成功: {Path(segment.file_path).name} ({file_size/1024/1024:.1f}MB)")
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"FFmpeg超时: {segment.file_path}")
        return False
    except Exception as e:
        logger.error(f"创建分段时出错: {e}")
        return False


def organize_segments_by_duration(segments: List[VideoSegment], 
                                output_base_dir: Path) -> Dict[str, List[VideoSegment]]:
    """根据时长组织分段到不同文件夹"""
    categories = {
        "short": [],      # 0-5秒
        "medium": [],     # 5-30秒
        "long": [],       # 30秒以上
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
            file_path=str(new_path),
            metadata=segment.metadata
        )
        
        categories[category].append(new_segment)
    
    return categories


def organize_segments_by_quality(segments: List[VideoSegment], 
                                output_base_dir: Path) -> Dict[str, List[VideoSegment]]:
    """根据检测置信度组织分段到不同文件夹"""
    categories = {
        "high_confidence": [],    # 置信度 > 0.8
        "medium_confidence": [],  # 置信度 0.5-0.8
        "low_confidence": [],     # 置信度 < 0.5
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
            file_path=str(new_path),
            metadata=segment.metadata
        )
        
        categories[category].append(new_segment)
    
    return categories


def process_video_segmentation(video_path: str, output_dir: str = None,
                             organize_by: str = "duration",
                             quality: str = "medium",
                             enable_classification: bool = False,
                             classification_config: dict = None) -> bool:
    """完整的视频分段处理流程"""
    
    logger.info("🎬 开始视频自动分段和切分")
    logger.info("=" * 60)
    
    # 1. 验证输入
    if not validate_video_file(video_path):
        logger.error(f"无效的视频文件: {video_path}")
        return False
    
    if not check_ffmpeg():
        logger.error("FFmpeg不可用，无法进行视频切分")
        return False
    
    # 2. 设置输出目录
    if output_dir is None:
        output_dir = Path(video_path).parent / f"{Path(video_path).stem}_segments"
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 3. 获取视频信息
    video_info = get_basic_video_info(video_path)
    logger.info(f"📹 视频信息: {video_info['duration']:.1f}s, {video_info['fps']:.1f} FPS, {video_info['resolution']}")
    
    try:
        # 4. 加载配置
        config = load_config("config.yaml")

        # 4.1. 初始化归类管理器
        classification_manager = get_classification_manager()
        file_organizer = None

        if enable_classification:
            logger.info("🗂️ 启用自动归类功能")

            # 更新归类配置
            if classification_config:
                classification_manager.update_config(**classification_config)

            # 设置归类模式
            classification_manager.update_config(
                enable_classification=True,
                classification_mode=organize_by,
                base_output_dir=str(output_dir)
            )

            # 创建文件组织器
            file_organizer = create_file_organizer(classification_manager)

            logger.info(f"归类模式: {organize_by}")
            logger.info(f"输出目录: {output_dir}")

        # 5. 初始化检测器
        logger.info("🤖 初始化镜头检测算法...")
        multi_detector = MultiDetector()
        
        # 添加检测器
        frame_diff_detector = FrameDifferenceDetector(threshold=0.3)
        histogram_detector = HistogramDetector(threshold=0.4)
        
        multi_detector.add_detector(frame_diff_detector, weight=0.5)
        multi_detector.add_detector(histogram_detector, weight=0.5)
        
        if not multi_detector.initialize_all():
            logger.error("检测器初始化失败")
            return False
        
        # 6. 执行镜头检测
        logger.info("🎯 执行镜头检测...")
        start_time = time.time()
        
        detection_result = multi_detector.detect_shots_ensemble(video_path)
        detection_time = time.time() - start_time
        
        logger.info(f"检测完成! 耗时: {detection_time:.2f}s")
        logger.info(f"检测到 {len(detection_result.boundaries)} 个镜头边界")
        
        if not detection_result.boundaries:
            logger.warning("未检测到镜头边界，将整个视频作为一个分段")
            # 创建单个分段
            segments = [VideoSegment(
                index=0,
                start_time=0.0,
                end_time=video_info['duration'],
                duration=video_info['duration'],
                start_frame=0,
                end_frame=int(video_info['duration'] * video_info['fps']),
                file_path=str(output_path / f"{Path(video_path).stem}_full.mp4"),
                metadata={'boundary_confidence': 1.0}
            )]
        else:
            # 7. 生成分段信息
            logger.info("📋 生成视频分段信息...")
            video_processor = VideoProcessor(config)
            segments = video_processor._generate_segment_info(
                detection_result.boundaries, 
                video_info['fps'], 
                video_info['duration'], 
                str(output_path), 
                video_path
            )
            
            # 过滤过短的分段
            min_duration = 1.0  # 最小1秒
            segments = [s for s in segments if s.duration >= min_duration]
            logger.info(f"过滤后保留 {len(segments)} 个分段 (≥{min_duration}s)")
        
        # 8. 组织分段到不同文件夹
        if organize_by == "duration":
            logger.info("📁 按时长组织分段...")
            categorized_segments = organize_segments_by_duration(segments, output_path)
        elif organize_by == "quality":
            logger.info("📁 按质量组织分段...")
            categorized_segments = organize_segments_by_quality(segments, output_path)
        else:
            # 默认：所有分段放在同一目录
            categorized_segments = {"all": segments}
        
        # 9. 使用FFmpeg切分视频
        logger.info("✂️ 开始视频切分...")
        total_segments = sum(len(segs) for segs in categorized_segments.values())
        processed_count = 0
        success_count = 0
        
        for category, category_segments in categorized_segments.items():
            if not category_segments:
                continue
                
            logger.info(f"处理类别: {category} ({len(category_segments)} 个分段)")
            
            for segment in category_segments:
                processed_count += 1
                logger.info(f"[{processed_count}/{total_segments}] 切分: {Path(segment.file_path).name}")
                logger.info(f"  时间: {segment.start_time:.2f}s - {segment.end_time:.2f}s (时长: {segment.duration:.2f}s)")
                
                if create_segment_with_ffmpeg(video_path, segment, quality):
                    success_count += 1

                    # 如果启用归类，进行自动归类
                    if enable_classification and file_organizer:
                        segment_info = {
                            'duration': segment.duration,
                            'confidence': segment.metadata.get('boundary_confidence', 1.0),
                            'start_time': segment.start_time,
                            'end_time': segment.end_time,
                            'category': category,
                            'content_description': f"segment_{segment.index}"
                        }

                        # 执行归类
                        organize_result = file_organizer.organize_segment(
                            segment.file_path,
                            segment_info,
                            str(output_path)
                        )

                        if organize_result.success:
                            logger.info(f"  📁 归类成功: {organize_result.category} -> {organize_result.new_path}")
                        else:
                            logger.warning(f"  ⚠️ 归类失败: {organize_result.error}")
                else:
                    logger.error(f"  ❌ 切分失败")
        
        # 10. 生成项目文件和报告
        logger.info("📤 生成项目文件和报告...")
        
        # 展平所有分段用于报告生成
        all_segments = []
        for segs in categorized_segments.values():
            all_segments.extend(segs)
        
        project_exporter = ProjectExporter(config)
        project_exporter.export_all_formats(video_path, detection_result, all_segments, str(output_path))
        
        report_generator = ReportGenerator(config)
        report_generator.generate_report(video_path, detection_result, all_segments, str(output_path))
        
        # 11. 清理资源
        multi_detector.cleanup_all()
        
        # 12. 显示结果
        logger.info("📊 处理结果:")
        logger.info(f"  总分段数: {total_segments}")
        logger.info(f"  成功切分: {success_count}")
        logger.info(f"  失败数量: {total_segments - success_count}")
        logger.info(f"  成功率: {success_count/total_segments*100:.1f}%")

        # 显示归类统计
        if enable_classification and file_organizer:
            organize_summary = file_organizer.get_operation_summary()
            logger.info("📁 归类统计:")
            logger.info(f"  归类总数: {organize_summary['total']}")
            logger.info(f"  归类成功: {organize_summary['success']}")
            logger.info(f"  归类失败: {organize_summary['failed']}")

            if organize_summary['categories']:
                logger.info("  分类分布:")
                for cat, count in organize_summary['categories'].items():
                    logger.info(f"    {cat}: {count} 个")

            if organize_summary['operations']:
                logger.info("  操作统计:")
                for op, count in organize_summary['operations'].items():
                    logger.info(f"    {op}: {count} 个")
        
        logger.info("📁 输出目录结构:")
        for root, dirs, files in os.walk(output_path):
            level = root.replace(str(output_path), '').count(os.sep)
            indent = ' ' * 2 * level
            logger.info(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                if file.endswith(('.mp4', '.avi', '.mov')):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path) / 1024 / 1024
                    logger.info(f"{subindent}{file} ({file_size:.1f}MB)")
        
        logger.info("✅ 视频分段和切分完成!")
        return success_count > 0
        
    except Exception as e:
        logger.error(f"处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="视频自动分段和切分系统")
    parser.add_argument("video", help="输入视频文件路径")
    parser.add_argument("-o", "--output", help="输出目录路径")
    parser.add_argument("--organize", choices=["duration", "quality", "content", "none"],
                       default="duration", help="分段组织方式")
    parser.add_argument("--quality", choices=["low", "medium", "high", "lossless"],
                       default="medium", help="输出视频质量")
    parser.add_argument("--classify", action="store_true", help="启用自动归类功能")
    parser.add_argument("--move-files", action="store_true", help="移动文件而不是复制")
    parser.add_argument("--min-confidence", type=float, default=0.6, help="归类最小置信度")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    setup_logging()
    
    if args.debug:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    # 准备归类配置
    classification_config = None
    if args.classify:
        classification_config = {
            'move_files': args.move_files,
            'min_confidence_for_move': args.min_confidence,
            'create_directories': True,
            'conflict_resolution': 'rename'
        }

    success = process_video_segmentation(
        args.video,
        args.output,
        args.organize,
        args.quality,
        args.classify,
        classification_config
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
