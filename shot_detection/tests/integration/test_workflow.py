"""
Integration Tests for Complete Workflow
完整工作流集成测试
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.services import VideoService, BatchService
from core.detection import FrameDifferenceDetector, HistogramDetector
from core.performance import MemoryManager, PerformanceMonitor
from jianying.services import JianYingService
from config import get_config


class TestVideoWorkflow:
    """视频处理工作流测试"""
    
    def test_complete_video_processing_workflow(self, sample_video_path, output_dir):
        """测试完整的视频处理工作流"""
        # 1. 初始化检测器
        detector = FrameDifferenceDetector(threshold=0.3)
        
        # 2. 创建服务
        video_service = VideoService(detector)
        
        # 3. 模拟视频处理
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                5: 30.0, 7: 300
            }.get(prop, 0)
            
            import numpy as np
            frames = [(True, np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)) 
                     for _ in range(10)]
            mock_cap.return_value.read.side_effect = frames + [(False, None)]
            
            # 4. 执行检测
            result = video_service.detect_shots(
                video_path=sample_video_path,
                output_dir=output_dir
            )
        
        # 5. 验证结果
        assert result["success"] == True
        assert "boundaries" in result
        assert "processing_time" in result
        assert len(result["boundaries"]) >= 0
        
        # 6. 验证输出文件
        output_files = list(Path(output_dir).glob("*.json"))
        assert len(output_files) > 0
    
    def test_batch_processing_workflow(self, mock_video_files, output_dir):
        """测试批量处理工作流"""
        # 1. 初始化检测器和服务
        detector = FrameDifferenceDetector(threshold=0.3)
        batch_service = BatchService(detector, max_workers=2)
        
        # 2. 模拟视频处理
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                5: 30.0, 7: 100
            }.get(prop, 0)
            
            import numpy as np
            frames = [(True, np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)) 
                     for _ in range(5)]
            mock_cap.return_value.read.side_effect = frames + [(False, None)]
            
            # 3. 执行批量处理
            results = batch_service.process_videos(
                video_paths=mock_video_files,
                output_dir=output_dir
            )
        
        # 4. 验证结果
        assert len(results) == len(mock_video_files)
        for result in results:
            assert "success" in result
            assert "video_path" in result
        
        # 5. 清理
        batch_service.cleanup()
    
    def test_multi_algorithm_workflow(self, sample_video_path, output_dir):
        """测试多算法工作流"""
        from core.detection import MultiDetector
        
        # 1. 创建多个检测器
        fd_detector = FrameDifferenceDetector(threshold=0.3)
        hist_detector = HistogramDetector(threshold=0.4)
        
        # 2. 创建多算法检测器
        multi_detector = MultiDetector([fd_detector, hist_detector])
        
        # 3. 创建服务
        video_service = VideoService(multi_detector)
        
        # 4. 模拟处理
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                5: 30.0, 7: 200
            }.get(prop, 0)
            
            import numpy as np
            frames = [(True, np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)) 
                     for _ in range(8)]
            mock_cap.return_value.read.side_effect = frames + [(False, None)]
            
            # 5. 执行检测
            result = video_service.detect_shots(
                video_path=sample_video_path,
                output_dir=output_dir
            )
        
        # 6. 验证结果
        assert result["success"] == True
        assert result["algorithm"] == "Multi"


class TestJianYingWorkflow:
    """剪映工作流测试"""
    
    def test_jianying_project_creation_workflow(self, mock_video_files, output_dir):
        """测试剪映项目创建工作流"""
        # 1. 初始化剪映服务
        jianying_service = JianYingService()
        
        # 2. 创建项目
        project_result = jianying_service.create_project(
            project_name="test_project",
            video_files=mock_video_files,
            output_dir=output_dir
        )
        
        # 3. 验证结果
        assert project_result["success"] == True
        assert "project_path" in project_result
        
        # 4. 验证项目文件
        project_path = Path(project_result["project_path"])
        assert project_path.exists()
        
        required_files = ["draft_content.json", "draft_meta_info.json", "draft_virtual_store.json"]
        for file_name in required_files:
            assert (project_path / file_name).exists()
        
        # 5. 清理
        jianying_service.cleanup()
    
    def test_video_mix_workflow(self, mock_video_files, output_dir):
        """测试视频混剪工作流"""
        from jianying.services import VideoMixService
        
        # 1. 初始化视频混剪服务
        mix_service = VideoMixService()
        
        # 2. 执行混剪
        mix_result = mix_service.create_mix_project(
            video_files=mock_video_files,
            template_config={
                "style": "dynamic",
                "duration": 60,
                "transitions": True
            },
            output_dir=output_dir
        )
        
        # 3. 验证结果
        assert mix_result["success"] == True
        assert "project_path" in mix_result
        
        # 4. 清理
        mix_service.cleanup()


class TestPerformanceWorkflow:
    """性能监控工作流测试"""
    
    def test_memory_management_workflow(self, sample_video_path):
        """测试内存管理工作流"""
        # 1. 初始化内存管理器
        memory_manager = MemoryManager()
        memory_manager.start_monitoring()
        
        # 2. 执行内存密集型操作
        detector = FrameDifferenceDetector(threshold=0.3)
        video_service = VideoService(detector)
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                5: 30.0, 7: 1000  # 大量帧
            }.get(prop, 0)
            
            import numpy as np
            frames = [(True, np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)) 
                     for _ in range(50)]
            mock_cap.return_value.read.side_effect = frames + [(False, None)]
            
            # 3. 执行检测
            result = video_service.detect_shots(video_path=sample_video_path)
        
        # 4. 检查内存状态
        memory_info = memory_manager.get_memory_info()
        assert "virtual_memory" in memory_info
        assert "statistics" in memory_info
        
        # 5. 优化内存
        optimization_result = memory_manager.optimize_memory_usage()
        assert optimization_result["success"] == True
        
        # 6. 清理
        memory_manager.cleanup()
    
    def test_performance_monitoring_workflow(self, sample_video_path):
        """测试性能监控工作流"""
        # 1. 初始化性能监控器
        performance_monitor = PerformanceMonitor()
        performance_monitor.start_monitoring()
        
        # 2. 执行计算密集型操作
        detector = FrameDifferenceDetector(threshold=0.3)
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                5: 30.0, 7: 500
            }.get(prop, 0)
            
            import numpy as np
            frames = [(True, np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)) 
                     for _ in range(20)]
            mock_cap.return_value.read.side_effect = frames + [(False, None)]
            
            # 3. 执行检测
            result = detector.detect_boundaries(sample_video_path)
        
        # 4. 获取性能数据
        performance_data = performance_monitor.get_current_performance()
        assert "cpu" in performance_data
        assert "memory" in performance_data
        
        # 5. 获取性能摘要
        summary = performance_monitor.get_performance_summary()
        assert "current" in summary
        assert "statistics" in summary
        
        # 6. 清理
        performance_monitor.cleanup()


class TestConfigurationWorkflow:
    """配置管理工作流测试"""
    
    def test_configuration_loading_workflow(self, temp_dir):
        """测试配置加载工作流"""
        # 1. 创建测试配置文件
        config_file = Path(temp_dir) / "test_config.yaml"
        config_content = """
detection:
  default_algorithm: "frame_difference"
  threshold: 0.35
  
processing:
  max_workers: 4
  enable_cache: true
  
output:
  format: "json"
  include_metadata: true
"""
        config_file.write_text(config_content)
        
        # 2. 加载配置
        config = get_config()
        config.load_config(str(config_file))
        
        # 3. 验证配置
        assert config.get('detection.default_algorithm') == "frame_difference"
        assert config.get('detection.threshold') == 0.35
        assert config.get('processing.max_workers') == 4
        assert config.get('processing.enable_cache') == True
        
        # 4. 使用配置创建检测器
        threshold = config.get('detection.threshold')
        detector = FrameDifferenceDetector(threshold=threshold)
        assert detector.threshold == 0.35
    
    def test_configuration_validation_workflow(self):
        """测试配置验证工作流"""
        config = get_config()
        
        # 1. 验证当前配置
        is_valid, errors = config.validate_config()
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
        
        # 2. 测试无效配置
        config.set('detection.threshold', 1.5)  # 无效值
        is_valid, errors = config.validate_config()
        assert is_valid == False
        assert len(errors) > 0
        
        # 3. 修复配置
        config.set('detection.threshold', 0.3)
        is_valid, errors = config.validate_config()
        assert is_valid == True


class TestErrorHandlingWorkflow:
    """错误处理工作流测试"""
    
    def test_video_loading_error_workflow(self):
        """测试视频加载错误工作流"""
        detector = FrameDifferenceDetector(threshold=0.3)
        video_service = VideoService(detector)
        
        # 1. 测试不存在的文件
        result = video_service.detect_shots(
            video_path="nonexistent_video.mp4",
            output_dir="/tmp"
        )
        
        # 2. 验证错误处理
        assert result["success"] == False
        assert "error" in result
        assert "video" in result["error"].lower()
    
    def test_processing_error_recovery_workflow(self, sample_video_path, output_dir):
        """测试处理错误恢复工作流"""
        detector = FrameDifferenceDetector(threshold=0.3)
        video_service = VideoService(detector)
        
        # 1. 模拟处理过程中的错误
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                5: 30.0, 7: 100
            }.get(prop, 0)
            
            # 模拟读取错误
            mock_cap.return_value.read.side_effect = Exception("Simulated read error")
            
            # 2. 执行检测
            result = video_service.detect_shots(
                video_path=sample_video_path,
                output_dir=output_dir
            )
        
        # 3. 验证错误处理
        assert result["success"] == False
        assert "error" in result


@pytest.mark.slow
class TestLongRunningWorkflow:
    """长时间运行工作流测试"""
    
    def test_large_batch_processing_workflow(self, temp_dir, output_dir):
        """测试大批量处理工作流"""
        # 1. 创建大量模拟视频文件
        video_files = []
        for i in range(20):  # 20个文件
            video_file = Path(temp_dir) / f"large_video_{i}.mp4"
            video_file.write_bytes(b"fake large video content" * 1000)
            video_files.append(str(video_file))
        
        # 2. 初始化批量服务
        detector = FrameDifferenceDetector(threshold=0.3)
        batch_service = BatchService(detector, max_workers=4)
        
        # 3. 模拟处理
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                5: 30.0, 7: 300
            }.get(prop, 0)
            
            import numpy as np
            frames = [(True, np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)) 
                     for _ in range(10)]
            mock_cap.return_value.read.side_effect = frames + [(False, None)]
            
            # 4. 执行批量处理
            start_time = time.time()
            results = batch_service.process_videos(
                video_paths=video_files,
                output_dir=output_dir
            )
            processing_time = time.time() - start_time
        
        # 5. 验证结果
        assert len(results) == len(video_files)
        assert processing_time < 60.0  # 应该在1分钟内完成
        
        # 6. 验证并行处理效果
        successful_results = [r for r in results if r.get("success", False)]
        assert len(successful_results) > 0
        
        # 7. 清理
        batch_service.cleanup()


@pytest.mark.integration
class TestEndToEndWorkflow:
    """端到端工作流测试"""
    
    def test_complete_end_to_end_workflow(self, mock_video_files, output_dir):
        """测试完整的端到端工作流"""
        # 1. 配置管理
        config = get_config()
        config.set('detection.threshold', 0.3)
        config.set('processing.enable_cache', True)
        
        # 2. 性能监控
        performance_monitor = PerformanceMonitor()
        performance_monitor.start_monitoring()
        
        # 3. 内存管理
        memory_manager = MemoryManager()
        memory_manager.start_monitoring()
        
        try:
            # 4. 视频检测
            detector = FrameDifferenceDetector(threshold=config.get('detection.threshold'))
            video_service = VideoService(detector)
            
            detection_results = []
            for video_file in mock_video_files:
                with patch('cv2.VideoCapture') as mock_cap:
                    mock_cap.return_value.isOpened.return_value = True
                    mock_cap.return_value.get.side_effect = lambda prop: {
                        5: 30.0, 7: 150
                    }.get(prop, 0)
                    
                    import numpy as np
                    frames = [(True, np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)) 
                             for _ in range(6)]
                    mock_cap.return_value.read.side_effect = frames + [(False, None)]
                    
                    result = video_service.detect_shots(
                        video_path=video_file,
                        output_dir=output_dir
                    )
                    detection_results.append(result)
            
            # 5. 剪映项目创建
            jianying_service = JianYingService()
            project_result = jianying_service.create_project(
                project_name="end_to_end_test",
                video_files=mock_video_files,
                output_dir=output_dir
            )
            
            # 6. 验证所有结果
            assert all(r["success"] for r in detection_results)
            assert project_result["success"] == True
            
            # 7. 性能检查
            performance_data = performance_monitor.get_performance_summary()
            memory_info = memory_manager.get_memory_info()
            
            assert "current" in performance_data
            assert "virtual_memory" in memory_info
            
            # 8. 清理
            jianying_service.cleanup()
            
        finally:
            # 9. 清理监控器
            performance_monitor.cleanup()
            memory_manager.cleanup()
