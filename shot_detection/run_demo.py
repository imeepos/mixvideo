#!/usr/bin/env python3
"""
镜头检测系统演示脚本
简化版本，用于快速测试和演示
"""

import sys
import os
import time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    import cv2
    import numpy as np
    print("✅ OpenCV 已安装")
except ImportError:
    print("❌ OpenCV 未安装，请运行: pip install opencv-python")
    sys.exit(1)

try:
    from loguru import logger
    print("✅ Loguru 已安装")
except ImportError:
    print("❌ Loguru 未安装，请运行: pip install loguru")
    sys.exit(1)

# 导入我们的模块
from config import ConfigManager, load_config
from detectors.frame_diff import FrameDifferenceDetector
from detectors.histogram import HistogramDetector
from detectors.base import MultiDetector
from utils.video_utils import validate_video_file, get_basic_video_info


def setup_logging():
    """设置简单的日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )


def create_test_video(output_path: str, duration: int = 10):
    """创建一个测试视频文件"""
    try:
        logger.info(f"创建测试视频: {output_path}")
        
        # 视频参数
        fps = 25
        width, height = 640, 480
        total_frames = duration * fps
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # 生成不同颜色的帧来模拟镜头切换
        colors = [
            (255, 0, 0),    # 红色
            (0, 255, 0),    # 绿色
            (0, 0, 255),    # 蓝色
            (255, 255, 0),  # 黄色
            (255, 0, 255),  # 紫色
        ]
        
        frames_per_scene = total_frames // len(colors)
        
        for i in range(total_frames):
            # 确定当前场景
            scene_idx = min(i // frames_per_scene, len(colors) - 1)
            color = colors[scene_idx]
            
            # 创建纯色帧
            frame = np.full((height, width, 3), color, dtype=np.uint8)
            
            # 添加一些文本
            cv2.putText(frame, f"Scene {scene_idx + 1}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Frame {i + 1}", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            out.write(frame)
        
        out.release()
        logger.info(f"测试视频创建完成: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"创建测试视频失败: {e}")
        return False


def run_detection_demo(video_path: str):
    """运行检测演示"""
    logger.info("🎬 开始镜头检测演示")
    
    # 验证视频文件
    if not validate_video_file(video_path):
        logger.error(f"无效的视频文件: {video_path}")
        return False
    
    # 获取视频信息
    video_info = get_basic_video_info(video_path)
    logger.info(f"视频信息: {video_info['duration']:.1f}s, {video_info['fps']:.1f} FPS, {video_info['resolution']}")
    
    # 创建检测器
    logger.info("初始化检测器...")
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
    
    # 执行检测
    logger.info("开始执行镜头检测...")
    start_time = time.time()
    
    try:
        result = multi_detector.detect_shots_ensemble(video_path)
        detection_time = time.time() - start_time
        
        logger.info(f"检测完成! 耗时: {detection_time:.2f}s")
        logger.info(f"检测到 {len(result.boundaries)} 个镜头边界")
        
        # 显示检测结果
        if result.boundaries:
            logger.info("检测到的镜头边界:")
            for i, boundary in enumerate(result.boundaries, 1):
                logger.info(f"  {i}. 时间: {boundary.timestamp:.2f}s, 帧: {boundary.frame_number}, 置信度: {boundary.confidence:.3f}")
        else:
            logger.warning("未检测到镜头边界")
        
        # 清理资源
        multi_detector.cleanup_all()
        
        return True
        
    except Exception as e:
        logger.error(f"检测过程中出错: {e}")
        return False


def main():
    """主函数"""
    setup_logging()
    
    logger.info("🎬 智能镜头检测与分段系统 - 演示版本")
    logger.info("=" * 50)
    
    # 检查是否提供了视频文件
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        if not os.path.exists(video_path):
            logger.error(f"视频文件不存在: {video_path}")
            sys.exit(1)
    else:
        # 创建测试视频
        test_video_path = "test_video.mp4"
        logger.info("未提供视频文件，将创建测试视频...")
        
        if not create_test_video(test_video_path):
            logger.error("无法创建测试视频")
            sys.exit(1)
        
        video_path = test_video_path
    
    # 运行检测演示
    success = run_detection_demo(video_path)
    
    if success:
        logger.info("✅ 演示完成!")
    else:
        logger.error("❌ 演示失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()
