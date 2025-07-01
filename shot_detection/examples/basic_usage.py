#!/usr/bin/env python3
"""
Basic Usage Examples
基础使用示例
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def example_single_video_detection():
    """示例1: 单个视频镜头检测"""
    print("🎬 示例1: 单个视频镜头检测")
    print("-" * 40)
    
    from core.detection import FrameDifferenceDetector
    from core.services import VideoService
    
    # 创建检测器
    detector = FrameDifferenceDetector(threshold=0.3)
    
    # 创建视频服务
    video_service = VideoService(detector, enable_cache=True)
    
    # 模拟视频文件路径（实际使用时替换为真实路径）
    video_path = "sample_video.mp4"
    output_dir = "./output"
    
    print(f"检测视频: {video_path}")
    print(f"输出目录: {output_dir}")
    
    # 进度回调函数
    def progress_callback(progress, status):
        print(f"进度: {progress:.1%} - {status}")
    
    try:
        # 执行检测
        result = video_service.detect_shots(
            video_path=video_path,
            output_dir=output_dir,
            progress_callback=progress_callback
        )
        
        if result["success"]:
            print(f"✅ 检测成功!")
            print(f"   算法: {result['algorithm']}")
            print(f"   处理时间: {result['processing_time']:.2f} 秒")
            print(f"   总帧数: {result['frame_count']}")
            print(f"   检测到边界: {len(result['boundaries'])} 个")
            
            # 显示前几个边界
            for i, boundary in enumerate(result['boundaries'][:5]):
                print(f"   边界 {i+1}: 帧{boundary['frame_number']} "
                      f"({boundary['timestamp']:.2f}s) "
                      f"置信度{boundary['confidence']:.2f}")
            
            if len(result['boundaries']) > 5:
                print(f"   ... 还有 {len(result['boundaries']) - 5} 个边界")
        else:
            print(f"❌ 检测失败: {result.get('error', '未知错误')}")
    
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    finally:
        # 清理资源
        video_service.cleanup()
    
    print()


def example_multi_algorithm_detection():
    """示例2: 多算法融合检测"""
    print("🔍 示例2: 多算法融合检测")
    print("-" * 40)
    
    from core.detection import FrameDifferenceDetector, HistogramDetector, MultiDetector
    from core.services import VideoService
    
    # 创建多个检测器
    fd_detector = FrameDifferenceDetector(threshold=0.3)
    hist_detector = HistogramDetector(threshold=0.5, bins=256)
    
    # 创建融合检测器
    multi_detector = MultiDetector(
        detectors=[fd_detector, hist_detector],
        fusion_weights={"FrameDifference": 0.6, "Histogram": 0.4}
    )
    
    # 创建视频服务
    video_service = VideoService(multi_detector)
    
    video_path = "sample_video.mp4"
    
    print(f"使用多算法融合检测: {video_path}")
    print(f"算法权重: 帧差60%, 直方图40%")
    
    try:
        result = video_service.detect_shots(video_path)
        
        if result["success"]:
            print(f"✅ 融合检测成功!")
            print(f"   检测到边界: {len(result['boundaries'])} 个")
            
            # 显示置信度统计
            confidences = [b['confidence'] for b in result['boundaries']]
            if confidences:
                print(f"   平均置信度: {sum(confidences)/len(confidences):.2f}")
                print(f"   最高置信度: {max(confidences):.2f}")
                print(f"   最低置信度: {min(confidences):.2f}")
        else:
            print(f"❌ 检测失败: {result.get('error', '未知错误')}")
    
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    finally:
        video_service.cleanup()
    
    print()


def example_batch_processing():
    """示例3: 批量处理"""
    print("📦 示例3: 批量处理")
    print("-" * 40)
    
    from core.detection import FrameDifferenceDetector
    from core.services import BatchService
    
    # 创建批量服务
    detector = FrameDifferenceDetector(threshold=0.3)
    batch_service = BatchService(detector, max_workers=2)
    
    # 扫描视频文件
    video_dir = "./sample_videos"
    print(f"扫描目录: {video_dir}")
    
    try:
        # 扫描文件
        video_files = batch_service.scan_video_files(
            directory=video_dir,
            recursive=True,
            min_size_mb=1.0,
            max_size_mb=500.0
        )
        
        print(f"找到 {len(video_files)} 个视频文件")
        
        if video_files:
            # 批量进度回调
            def batch_progress(completed, total, current_file):
                print(f"批量进度: {completed}/{total} - {current_file}")
            
            # 执行批量处理
            results = batch_service.process_batch(
                video_files=video_files,
                output_dir="./batch_output",
                progress_callback=batch_progress
            )
            
            # 统计结果
            success_count = sum(1 for r in results if r.get("success", False))
            print(f"✅ 批量处理完成: {success_count}/{len(results)} 成功")
            
            # 生成报告
            report_file = batch_service.create_batch_report(results, "./reports")
            print(f"📊 报告已生成: {report_file}")
        else:
            print("⚠️ 未找到视频文件")
    
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    finally:
        batch_service.stop_processing()
    
    print()


def example_advanced_analysis():
    """示例4: 高级视频分析"""
    print("🔬 示例4: 高级视频分析")
    print("-" * 40)
    
    from core.services import AdvancedAnalysisService
    
    # 创建分析服务
    analysis_service = AdvancedAnalysisService()
    
    video_path = "sample_video.mp4"
    
    print(f"分析视频: {video_path}")
    
    # 分析进度回调
    def analysis_progress(progress, status):
        print(f"分析进度: {progress:.1%} - {status}")
    
    try:
        # 执行综合分析
        result = analysis_service.analyze_video_comprehensive(
            video_path=video_path,
            progress_callback=analysis_progress
        )
        
        if result["success"]:
            print(f"✅ 分析成功!")
            
            # 显示视频指标
            metrics = result.get("video_metrics", {})
            print(f"   时长: {metrics.get('duration', 0):.2f} 秒")
            print(f"   分辨率: {metrics.get('resolution', (0, 0))[0]}x{metrics.get('resolution', (0, 0))[1]}")
            print(f"   帧率: {metrics.get('fps', 0):.2f} fps")
            
            # 显示质量分析
            quality = result.get("quality_analysis", {})
            print(f"   质量分数: {quality.get('quality_score', 0):.2f}")
            print(f"   平均亮度: {quality.get('avg_brightness', 0):.1f}")
            print(f"   平均对比度: {quality.get('avg_contrast', 0):.1f}")
            
            # 显示分析报告
            report = result.get("analysis_report", {})
            summary = report.get("summary", {})
            print(f"   总镜头数: {summary.get('total_shots', 0)}")
            print(f"   平均镜头时长: {summary.get('avg_shot_duration', 0):.2f} 秒")
            
            # 显示建议
            recommendations = report.get("recommendations", [])
            if recommendations:
                print("   改进建议:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"     {i}. {rec}")
        else:
            print(f"❌ 分析失败: {result.get('error', '未知错误')}")
    
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    print()


def example_configuration():
    """示例5: 配置管理"""
    print("⚙️ 示例5: 配置管理")
    print("-" * 40)
    
    from config import get_config
    
    # 获取配置
    config = get_config()
    
    print("当前配置:")
    print(f"   应用名称: {config.get('app.name')}")
    print(f"   应用版本: {config.get('app.version')}")
    print(f"   日志级别: {config.get('app.log_level')}")
    
    # 获取检测配置
    detection_config = config.get_detection_config()
    print(f"   默认检测器: {detection_config.get('default_detector')}")
    
    fd_config = detection_config.get('frame_difference', {})
    print(f"   帧差阈值: {fd_config.get('threshold', 0.3)}")
    
    # 修改配置
    print("\n修改配置:")
    original_threshold = config.get('detection.frame_difference.threshold')
    config.set('detection.frame_difference.threshold', 0.4)
    new_threshold = config.get('detection.frame_difference.threshold')
    print(f"   帧差阈值: {original_threshold} → {new_threshold}")
    
    # 恢复原值
    config.set('detection.frame_difference.threshold', original_threshold)
    print(f"   已恢复原值: {config.get('detection.frame_difference.threshold')}")
    
    # 验证配置
    is_valid, errors = config.validate_config()
    print(f"   配置有效性: {'✅ 有效' if is_valid else '❌ 无效'}")
    if errors:
        for error in errors:
            print(f"     错误: {error}")
    
    print()


def example_performance_monitoring():
    """示例6: 性能监控"""
    print("📊 示例6: 性能监控")
    print("-" * 40)
    
    from core.detection import FrameDifferenceDetector
    from core.services import VideoService
    
    # 创建带缓存的视频服务
    detector = FrameDifferenceDetector()
    video_service = VideoService(detector, enable_cache=True)
    
    print("性能监控示例:")
    
    # 获取初始统计
    initial_stats = video_service.get_performance_stats()
    print(f"   初始处理文件数: {initial_stats['total_processed']}")
    print(f"   初始缓存命中数: {initial_stats['cache_hits']}")
    
    # 模拟处理（实际使用时会有真实的处理）
    video_service.performance_stats['total_processed'] += 1
    video_service.performance_stats['total_processing_time'] += 5.5
    video_service.performance_stats['cache_hits'] += 1
    
    # 获取更新后的统计
    updated_stats = video_service.get_performance_stats()
    print(f"   更新后处理文件数: {updated_stats['total_processed']}")
    print(f"   平均处理时间: {updated_stats['avg_processing_time']:.2f} 秒")
    print(f"   缓存命中率: {updated_stats['cache_hit_rate']:.1%}")
    
    # 获取缓存信息
    cache_info = video_service.get_cache_info()
    print(f"   缓存状态: {'启用' if cache_info['enabled'] else '禁用'}")
    if cache_info['enabled']:
        print(f"   缓存文件数: {cache_info.get('cache_files_count', 0)}")
        print(f"   缓存大小: {cache_info.get('total_size_mb', 0):.1f} MB")
    
    # 清理
    video_service.cleanup()
    
    print()


def main():
    """主函数"""
    print("🧪 Shot Detection v2.0 基础使用示例")
    print("=" * 50)
    print()
    
    # 运行所有示例
    examples = [
        example_single_video_detection,
        example_multi_algorithm_detection,
        example_batch_processing,
        example_advanced_analysis,
        example_configuration,
        example_performance_monitoring
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ 示例运行失败: {e}")
            print()
    
    print("=" * 50)
    print("📋 示例说明:")
    print("1. 这些示例使用模拟的视频文件路径")
    print("2. 实际使用时请替换为真实的视频文件路径")
    print("3. 确保视频文件存在且格式支持")
    print("4. 某些功能需要安装额外的依赖包")
    print()
    print("🎉 所有示例运行完成!")


if __name__ == "__main__":
    main()
