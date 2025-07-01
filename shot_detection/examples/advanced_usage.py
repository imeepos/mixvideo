#!/usr/bin/env python3
"""
Advanced Usage Examples
高级使用示例
"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def example_async_processing():
    """示例1: 异步处理"""
    print("⚡ 示例1: 异步处理")
    print("-" * 40)
    
    from core.detection import FrameDifferenceDetector
    from core.services import VideoService
    
    # 创建视频服务
    detector = FrameDifferenceDetector()
    video_service = VideoService(detector)
    
    video_paths = ["video1.mp4", "video2.mp4", "video3.mp4"]
    
    print(f"异步处理 {len(video_paths)} 个视频文件")
    
    try:
        # 创建异步任务
        tasks = []
        for video_path in video_paths:
            task = video_service.detect_shots_async(video_path)
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        success_count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"   视频 {i+1}: ❌ 异常 - {result}")
            elif result.get("success", False):
                print(f"   视频 {i+1}: ✅ 成功 - {len(result['boundaries'])} 个边界")
                success_count += 1
            else:
                print(f"   视频 {i+1}: ❌ 失败 - {result.get('error', '未知错误')}")
        
        print(f"异步处理完成: {success_count}/{len(video_paths)} 成功")
    
    except Exception as e:
        print(f"❌ 异步处理异常: {e}")
    
    finally:
        video_service.cleanup()
    
    print()


def example_custom_detector():
    """示例2: 自定义检测器"""
    print("🔧 示例2: 自定义检测器")
    print("-" * 40)
    
    from core.detection.base import BaseDetector, DetectionResult, ShotBoundary
    import cv2
    import numpy as np
    
    class CustomDetector(BaseDetector):
        """自定义检测器示例"""
        
        def __init__(self, threshold=0.3, custom_param=1.0):
            super().__init__(threshold)
            self.custom_param = custom_param
            self.name = "CustomDetector"
        
        def detect_boundaries(self, video_path, progress_callback=None):
            """实现自定义检测逻辑"""
            boundaries = []
            
            try:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    raise Exception(f"无法打开视频文件: {video_path}")
                
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                prev_frame = None
                frame_idx = 0
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    if prev_frame is not None:
                        # 自定义检测逻辑：基于边缘密度变化
                        curr_edges = cv2.Canny(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 50, 150)
                        prev_edges = cv2.Canny(cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY), 50, 150)
                        
                        curr_density = np.sum(curr_edges > 0) / curr_edges.size
                        prev_density = np.sum(prev_edges > 0) / prev_edges.size
                        
                        edge_diff = abs(curr_density - prev_density)
                        
                        if edge_diff > self.threshold * self.custom_param:
                            boundary = ShotBoundary(
                                frame_number=frame_idx,
                                timestamp=frame_idx / fps,
                                confidence=min(edge_diff / self.threshold, 1.0),
                                boundary_type="shot"
                            )
                            boundaries.append(boundary)
                    
                    prev_frame = frame.copy()
                    frame_idx += 1
                    
                    # 更新进度
                    if progress_callback and frame_idx % 30 == 0:
                        progress = frame_idx / frame_count
                        progress_callback(progress, f"处理帧 {frame_idx}/{frame_count}")
                
                cap.release()
                
                return DetectionResult(
                    boundaries=boundaries,
                    algorithm_name=self.name,
                    processing_time=0.0,  # 实际应该计算处理时间
                    frame_count=frame_count,
                    confidence_scores=[b.confidence for b in boundaries]
                )
                
            except Exception as e:
                raise Exception(f"自定义检测失败: {e}")
    
    # 使用自定义检测器
    custom_detector = CustomDetector(threshold=0.2, custom_param=1.5)
    
    print(f"创建自定义检测器: {custom_detector.name}")
    print(f"参数: threshold={custom_detector.threshold}, custom_param={custom_detector.custom_param}")
    
    # 可以像使用其他检测器一样使用
    from core.services import VideoService
    
    video_service = VideoService(custom_detector)
    
    print("自定义检测器已集成到视频服务中")
    print("可以正常使用 detect_shots() 方法")
    
    video_service.cleanup()
    
    print()


def example_plugin_development():
    """示例3: 插件开发"""
    print("🔌 示例3: 插件开发")
    print("-" * 40)
    
    from core.plugins import BasePlugin, PluginManager
    
    class ExamplePlugin(BasePlugin):
        """示例插件"""
        
        def __init__(self, name: str, version: str = "1.0.0"):
            super().__init__(name, version)
            self.data = {}
        
        def initialize(self) -> bool:
            """初始化插件"""
            print(f"   初始化插件: {self.name}")
            
            # 设置默认配置
            self.set_config("enabled_features", ["feature1", "feature2"])
            self.set_config("max_items", 100)
            
            # 初始化数据
            self.data["initialized_at"] = "2024-01-01 12:00:00"
            self.data["status"] = "active"
            
            return True
        
        def cleanup(self):
            """清理插件资源"""
            print(f"   清理插件: {self.name}")
            self.data.clear()
        
        def get_info(self) -> dict:
            """获取插件信息"""
            return {
                "name": self.name,
                "version": self.version,
                "description": "这是一个示例插件",
                "author": "Shot Detection Team",
                "features": self.get_config("enabled_features", []),
                "status": self.data.get("status", "unknown")
            }
        
        def process_video(self, video_path: str) -> dict:
            """插件特定功能：处理视频"""
            print(f"   插件处理视频: {video_path}")
            
            # 模拟处理逻辑
            result = {
                "plugin": self.name,
                "video_path": video_path,
                "processed": True,
                "features_used": self.get_config("enabled_features", [])
            }
            
            return result
    
    # 创建插件管理器
    plugin_manager = PluginManager()
    
    print("插件开发示例:")
    
    # 手动注册插件类（实际使用中会从文件加载）
    plugin_manager.plugin_classes["example_plugin"] = ExamplePlugin
    
    # 加载插件
    success = plugin_manager.load_plugin("example_plugin")
    print(f"   加载插件: {'✅ 成功' if success else '❌ 失败'}")
    
    # 启用插件
    if success:
        plugin_manager.enable_plugin("example_plugin")
        
        # 获取插件实例
        plugin = plugin_manager.get_plugin("example_plugin")
        if plugin:
            # 获取插件信息
            info = plugin.get_info()
            print(f"   插件信息: {info['name']} v{info['version']}")
            print(f"   描述: {info['description']}")
            print(f"   功能: {', '.join(info['features'])}")
            
            # 使用插件功能
            result = plugin.process_video("sample_video.mp4")
            print(f"   处理结果: {result}")
        
        # 获取插件状态
        status = plugin_manager.get_plugin_status()
        print(f"   插件状态: {status}")
    
    # 清理插件
    plugin_manager.cleanup_all()
    
    print()


def example_workflow_integration():
    """示例4: 完整工作流集成"""
    print("🔄 示例4: 完整工作流集成")
    print("-" * 40)
    
    from core.services import WorkflowService
    
    # 自定义配置
    config_override = {
        "detection": {
            "default_detector": "multi_detector",
            "frame_difference": {"threshold": 0.25},
            "histogram": {"threshold": 0.6}
        },
        "processing": {
            "output": {"format": "mp4", "quality": "high"}
        }
    }
    
    print("创建完整工作流服务:")
    print(f"   检测器: {config_override['detection']['default_detector']}")
    print(f"   输出格式: {config_override['processing']['output']['format']}")
    
    try:
        with WorkflowService(config_override) as workflow:
            # 获取服务状态
            status = workflow.get_service_status()
            print(f"   集成服务数: {len(status)}")
            
            # 显示各服务状态
            for service_name, service_status in status.items():
                if isinstance(service_status, dict):
                    print(f"     {service_name}: 已就绪")
            
            # 模拟单视频处理
            print("\n模拟单视频处理工作流:")
            print("   1. 镜头检测")
            print("   2. 高级分析")
            print("   3. 结果整合")
            print("   4. 报告生成")
            
            # 实际使用时的代码示例：
            # result = workflow.process_single_video(
            #     video_path="sample_video.mp4",
            #     output_dir="./workflow_output",
            #     include_analysis=True
            # )
            
            print("   ✅ 工作流配置完成")
    
    except Exception as e:
        print(f"❌ 工作流异常: {e}")
    
    print()


def example_performance_optimization():
    """示例5: 性能优化"""
    print("🚀 示例5: 性能优化")
    print("-" * 40)
    
    from core.services import BatchService
    from core.detection import FrameDifferenceDetector
    import psutil
    
    # 创建批量服务
    detector = FrameDifferenceDetector()
    batch_service = BatchService(detector)
    
    print("性能优化示例:")
    
    # 获取系统信息
    cpu_count = psutil.cpu_count()
    memory_gb = psutil.virtual_memory().total / (1024**3)
    
    print(f"   系统信息:")
    print(f"     CPU核心数: {cpu_count}")
    print(f"     内存总量: {memory_gb:.1f} GB")
    
    # 模拟文件信息
    file_count = 50
    avg_file_size_mb = 100.0
    
    print(f"   处理任务:")
    print(f"     文件数量: {file_count}")
    print(f"     平均文件大小: {avg_file_size_mb} MB")
    
    # 获取优化建议
    optimization = batch_service.optimize_batch_parameters(
        file_count=file_count,
        avg_file_size_mb=avg_file_size_mb
    )
    
    print(f"   优化建议:")
    print(f"     推荐工作线程数: {optimization['max_workers']}")
    print(f"     推荐块大小: {optimization['chunk_size']}")
    print(f"     预估内存使用: {optimization['estimated_memory_usage_mb']:.1f} MB")
    print(f"     CPU利用率: {optimization['cpu_utilization']:.1%}")
    
    # 显示优化建议
    recommendations = optimization.get('recommendations', [])
    if recommendations:
        print(f"   性能建议:")
        for i, rec in enumerate(recommendations, 1):
            print(f"     {i}. {rec}")
    
    # 应用优化设置
    batch_service.max_workers = optimization['max_workers']
    print(f"   ✅ 已应用优化设置")
    
    batch_service.stop_processing()
    
    print()


def example_error_handling():
    """示例6: 错误处理和恢复"""
    print("🛡️ 示例6: 错误处理和恢复")
    print("-" * 40)
    
    from core.detection import FrameDifferenceDetector
    from core.services import VideoService
    
    # 创建视频服务
    detector = FrameDifferenceDetector()
    video_service = VideoService(detector)
    
    print("错误处理示例:")
    
    # 测试各种错误情况
    test_cases = [
        ("nonexistent_file.mp4", "文件不存在"),
        ("", "空文件路径"),
        ("invalid_format.txt", "不支持的格式"),
    ]
    
    for video_path, description in test_cases:
        print(f"\n   测试: {description}")
        print(f"   文件: {video_path}")
        
        try:
            result = video_service.detect_shots(video_path)
            
            if result["success"]:
                print(f"     ✅ 意外成功")
            else:
                error_msg = result.get("error", "未知错误")
                print(f"     ❌ 预期失败: {error_msg}")
                
                # 检查错误处理是否完善
                required_fields = ["success", "error", "video_path"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"     ⚠️ 缺少字段: {missing_fields}")
                else:
                    print(f"     ✅ 错误处理完善")
        
        except Exception as e:
            print(f"     💥 未捕获异常: {e}")
    
    # 测试资源清理
    print(f"\n   测试资源清理:")
    try:
        video_service.cleanup()
        print(f"     ✅ 资源清理成功")
    except Exception as e:
        print(f"     ❌ 清理失败: {e}")
    
    # 测试上下文管理器
    print(f"\n   测试上下文管理器:")
    try:
        with VideoService(detector) as service:
            print(f"     ✅ 上下文管理器正常")
        print(f"     ✅ 自动清理成功")
    except Exception as e:
        print(f"     ❌ 上下文管理器异常: {e}")
    
    print()


async def main():
    """主函数"""
    print("🧪 Shot Detection v2.0 高级使用示例")
    print("=" * 50)
    print()
    
    # 运行异步示例
    await example_async_processing()
    
    # 运行同步示例
    examples = [
        example_custom_detector,
        example_plugin_development,
        example_workflow_integration,
        example_performance_optimization,
        example_error_handling
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ 示例运行失败: {e}")
            print()
    
    print("=" * 50)
    print("📋 高级示例说明:")
    print("1. 异步处理可以显著提升多文件处理效率")
    print("2. 自定义检测器允许实现特定的检测逻辑")
    print("3. 插件系统支持功能扩展和模块化开发")
    print("4. 工作流服务提供完整的端到端处理")
    print("5. 性能优化可以根据系统资源自动调整")
    print("6. 健壮的错误处理确保系统稳定性")
    print()
    print("🎉 所有高级示例运行完成!")


if __name__ == "__main__":
    asyncio.run(main())
