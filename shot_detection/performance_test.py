#!/usr/bin/env python3
"""
性能测试脚本
测试不同算法的性能和准确性
"""

import sys
import os
import time
from pathlib import Path
import statistics

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from detectors.frame_diff import FrameDifferenceDetector, EnhancedFrameDifferenceDetector
from detectors.histogram import HistogramDetector, MultiChannelHistogramDetector, AdaptiveHistogramDetector
from detectors.base import MultiDetector
from utils.video_utils import get_basic_video_info
from loguru import logger


def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>"
    )


def test_detector_performance(detector, video_path, runs=3):
    """测试单个检测器的性能"""
    logger.info(f"测试检测器: {detector.name}")
    
    if not detector.initialize():
        logger.error(f"检测器 {detector.name} 初始化失败")
        return None
    
    times = []
    results = []
    
    for i in range(runs):
        logger.info(f"  运行 {i+1}/{runs}...")
        start_time = time.time()
        
        try:
            result = detector.detect_shots(video_path)
            end_time = time.time()
            
            processing_time = end_time - start_time
            times.append(processing_time)
            results.append(result)
            
            logger.info(f"    耗时: {processing_time:.2f}s, 检测到: {len(result.boundaries)} 个边界")
            
        except Exception as e:
            logger.error(f"    运行失败: {e}")
            continue
    
    detector.cleanup()
    
    if not times:
        return None
    
    return {
        'detector_name': detector.name,
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'std_time': statistics.stdev(times) if len(times) > 1 else 0,
        'avg_boundaries': statistics.mean([len(r.boundaries) for r in results]),
        'avg_confidence': statistics.mean([
            statistics.mean(r.confidence_scores) if r.confidence_scores else 0 
            for r in results
        ]),
        'runs': len(times)
    }


def performance_benchmark():
    """性能基准测试"""
    setup_logging()
    
    logger.info("🚀 镜头检测系统性能测试")
    logger.info("=" * 50)
    
    video_path = "test_video.mp4"
    
    if not os.path.exists(video_path):
        logger.error(f"测试视频不存在: {video_path}")
        return False
    
    # 获取视频信息
    video_info = get_basic_video_info(video_path)
    logger.info(f"测试视频: {video_info['duration']:.1f}s, {video_info['fps']:.1f} FPS, {video_info['resolution']}")
    
    # 测试的检测器列表
    detectors = [
        FrameDifferenceDetector(threshold=0.3),
        EnhancedFrameDifferenceDetector(threshold=0.3),
        HistogramDetector(threshold=0.4),
        MultiChannelHistogramDetector(threshold=0.4),
        AdaptiveHistogramDetector(threshold=0.4),
    ]
    
    results = []
    
    # 测试每个检测器
    for detector in detectors:
        try:
            result = test_detector_performance(detector, video_path, runs=3)
            if result:
                results.append(result)
        except Exception as e:
            logger.error(f"测试 {detector.name} 时出错: {e}")
    
    # 显示结果
    logger.info("\n📊 性能测试结果:")
    logger.info("-" * 80)
    logger.info(f"{'检测器':<25} {'平均时间':<10} {'检测边界':<10} {'平均置信度':<12} {'速度比':<10}")
    logger.info("-" * 80)
    
    video_duration = video_info['duration']
    
    for result in results:
        speed_ratio = video_duration / result['avg_time']
        logger.info(
            f"{result['detector_name']:<25} "
            f"{result['avg_time']:.2f}s{'':<5} "
            f"{result['avg_boundaries']:.1f}{'':<6} "
            f"{result['avg_confidence']:.3f}{'':<8} "
            f"{speed_ratio:.1f}x{'':<6}"
        )
    
    # 测试融合检测器
    logger.info("\n🔄 测试融合检测器...")
    multi_detector = MultiDetector()
    
    # 添加最佳检测器
    frame_diff = FrameDifferenceDetector(threshold=0.3)
    histogram = HistogramDetector(threshold=0.4)
    
    multi_detector.add_detector(frame_diff, weight=0.5)
    multi_detector.add_detector(histogram, weight=0.5)
    
    if multi_detector.initialize_all():
        start_time = time.time()
        ensemble_result = multi_detector.detect_shots_ensemble(video_path)
        end_time = time.time()
        
        ensemble_time = end_time - start_time
        ensemble_speed = video_duration / ensemble_time
        
        logger.info(f"融合检测器结果:")
        logger.info(f"  耗时: {ensemble_time:.2f}s")
        logger.info(f"  检测边界: {len(ensemble_result.boundaries)}")
        logger.info(f"  处理速度: {ensemble_speed:.1f}x")
        
        multi_detector.cleanup_all()
    
    # 性能分析
    logger.info("\n📈 性能分析:")
    
    if results:
        fastest = min(results, key=lambda x: x['avg_time'])
        most_boundaries = max(results, key=lambda x: x['avg_boundaries'])
        highest_confidence = max(results, key=lambda x: x['avg_confidence'])
        
        logger.info(f"  最快检测器: {fastest['detector_name']} ({fastest['avg_time']:.2f}s)")
        logger.info(f"  检测边界最多: {most_boundaries['detector_name']} ({most_boundaries['avg_boundaries']:.1f}个)")
        logger.info(f"  置信度最高: {highest_confidence['detector_name']} ({highest_confidence['avg_confidence']:.3f})")
        
        # 计算性能指标
        avg_speed = statistics.mean([video_duration / r['avg_time'] for r in results])
        logger.info(f"  平均处理速度: {avg_speed:.1f}x 实时")
        
        # 检查是否满足性能要求
        target_speed = 5.0  # 目标：5倍实时速度
        if avg_speed >= target_speed:
            logger.info(f"  ✅ 满足性能要求 (≥{target_speed}x)")
        else:
            logger.info(f"  ⚠️ 未达到性能要求 (目标≥{target_speed}x)")
    
    logger.info("\n✅ 性能测试完成!")
    return True


if __name__ == "__main__":
    success = performance_benchmark()
    sys.exit(0 if success else 1)
