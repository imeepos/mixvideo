"""
智能镜头检测与分段系统 - 主程序
提供命令行界面和批处理功能
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional
import time
from loguru import logger

from config import ConfigManager, load_config
from detectors.base import MultiDetector
from detectors.frame_diff import FrameDifferenceDetector, EnhancedFrameDifferenceDetector
from detectors.histogram import HistogramDetector, MultiChannelHistogramDetector, AdaptiveHistogramDetector
from processors.video_processor import VideoProcessor
from exporters.project_exporter import ProjectExporter
from utils.video_utils import get_video_info, validate_video_file
from utils.report_generator import ReportGenerator


class ShotDetectionSystem:
    """镜头检测系统主类"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = load_config(config_file)
        self.setup_logging()
        self.multi_detector = MultiDetector()
        self.video_processor = VideoProcessor(self.config)
        self.project_exporter = ProjectExporter(self.config)
        self.report_generator = ReportGenerator(self.config)
        
        self.initialize_detectors()
    
    def setup_logging(self):
        """设置日志系统"""
        logger.remove()  # 移除默认处理器
        
        # 控制台输出
        logger.add(
            sys.stderr,
            level=self.config.system.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        # 文件输出
        logger.add(
            self.config.system.log_file,
            level=self.config.system.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation=self.config.system.log_rotation,
            retention=self.config.system.log_retention
        )
        
        logger.info("Shot Detection System initialized")
    
    def initialize_detectors(self):
        """初始化所有检测器"""
        logger.info("Initializing detection algorithms...")
        
        # 帧差检测器
        if self.config.detection.fusion_weights.get('frame_diff', 0) > 0:
            frame_diff_detector = EnhancedFrameDifferenceDetector(
                threshold=self.config.detection.frame_diff_threshold,
                min_scene_length=self.config.detection.frame_diff_min_scene_len
            )
            self.multi_detector.add_detector(
                frame_diff_detector, 
                self.config.detection.fusion_weights['frame_diff']
            )
        
        # 直方图检测器
        if self.config.detection.fusion_weights.get('histogram', 0) > 0:
            histogram_detector = AdaptiveHistogramDetector(
                threshold=self.config.detection.histogram_threshold,
                bins=self.config.detection.histogram_bins
            )
            self.multi_detector.add_detector(
                histogram_detector,
                self.config.detection.fusion_weights['histogram']
            )
        
        # 初始化所有检测器
        if not self.multi_detector.initialize_all():
            logger.error("Failed to initialize detection algorithms")
            sys.exit(1)
        
        logger.info("All detection algorithms initialized successfully")
    
    def process_single_video(self, video_path: str, output_dir: str = None) -> bool:
        """处理单个视频文件"""
        try:
            logger.info(f"Processing video: {video_path}")
            
            # 验证视频文件
            if not validate_video_file(video_path):
                logger.error(f"Invalid video file: {video_path}")
                return False
            
            # 获取视频信息
            video_info = get_video_info(video_path)
            logger.info(f"Video info: {video_info['duration']:.2f}s, {video_info['fps']:.2f} FPS, {video_info['resolution']}")
            
            # 设置输出目录
            if output_dir is None:
                output_dir = Path(video_path).parent / f"{Path(video_path).stem}_segments"
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 执行镜头检测
            logger.info("Starting shot detection...")
            start_time = time.time()
            
            detection_result = self.multi_detector.detect_shots_ensemble(video_path)
            
            detection_time = time.time() - start_time
            logger.info(f"Shot detection completed in {detection_time:.2f}s")
            logger.info(f"Found {len(detection_result.boundaries)} shot boundaries")
            
            # 生成分段
            if detection_result.boundaries:
                logger.info("Generating video segments...")
                segments = self.video_processor.create_segments(
                    video_path, detection_result.boundaries, output_dir
                )
                logger.info(f"Generated {len(segments)} video segments")
                
                # 导出项目文件
                logger.info("Exporting project files...")
                self.project_exporter.export_all_formats(
                    video_path, detection_result, segments, output_dir
                )
                
                # 生成报告
                logger.info("Generating analysis report...")
                self.report_generator.generate_report(
                    video_path, detection_result, segments, output_dir
                )
            
            logger.info(f"Processing completed successfully. Output: {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
            return False
    
    def process_batch(self, input_dir: str, output_dir: str = None) -> int:
        """批量处理视频文件"""
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.error(f"Input directory does not exist: {input_dir}")
            return 0
        
        # 查找所有视频文件
        video_files = []
        for ext in self.config.processing.input_formats:
            video_files.extend(input_path.glob(f"**/*{ext}"))
        
        if not video_files:
            logger.warning(f"No video files found in {input_dir}")
            return 0
        
        logger.info(f"Found {len(video_files)} video files for batch processing")
        
        # 设置输出目录
        if output_dir is None:
            output_dir = input_path / "shot_detection_output"
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 处理每个视频文件
        success_count = 0
        for i, video_file in enumerate(video_files, 1):
            logger.info(f"Processing {i}/{len(video_files)}: {video_file.name}")
            
            video_output_dir = output_path / video_file.stem
            if self.process_single_video(str(video_file), str(video_output_dir)):
                success_count += 1
            
            logger.info(f"Progress: {i}/{len(video_files)} ({success_count} successful)")
        
        logger.info(f"Batch processing completed: {success_count}/{len(video_files)} successful")
        return success_count
    
    def cleanup(self):
        """清理资源"""
        logger.info("Cleaning up resources...")
        self.multi_detector.cleanup_all()


def create_argument_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="智能镜头检测与分段系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 处理单个视频文件
  python main.py -i video.mp4 -o output_dir
  
  # 批量处理目录中的所有视频
  python main.py -i videos_dir -o output_dir --batch
  
  # 使用自定义配置文件
  python main.py -i video.mp4 -c config.yaml
  
  # 启用调试模式
  python main.py -i video.mp4 --debug
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='输入视频文件或目录路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出目录路径（默认为输入文件同级目录）'
    )
    
    parser.add_argument(
        '-c', '--config',
        help='配置文件路径'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='批量处理模式'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--threshold',
        type=float,
        help='检测阈值（覆盖配置文件设置）'
    )
    
    parser.add_argument(
        '--min-scene-length',
        type=int,
        help='最小镜头长度（帧数）'
    )
    
    parser.add_argument(
        '--format',
        choices=['mp4', 'avi', 'mov'],
        help='输出视频格式'
    )
    
    return parser


def main():
    """主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    try:
        # 初始化系统
        system = ShotDetectionSystem(args.config)
        
        # 应用命令行参数覆盖
        if args.debug:
            system.config.system.debug_mode = True
            system.config.system.log_level = 'DEBUG'
        
        if args.threshold:
            system.config.detection.frame_diff_threshold = args.threshold
            system.config.detection.histogram_threshold = args.threshold
        
        if args.min_scene_length:
            system.config.detection.frame_diff_min_scene_len = args.min_scene_length
        
        if args.format:
            system.config.processing.output_format = args.format
        
        # 执行处理
        if args.batch:
            success_count = system.process_batch(args.input, args.output)
            if success_count == 0:
                sys.exit(1)
        else:
            if not system.process_single_video(args.input, args.output):
                sys.exit(1)
        
        # 清理资源
        system.cleanup()
        
        logger.info("Program completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
