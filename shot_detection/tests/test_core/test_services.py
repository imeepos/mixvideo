"""
Unit Tests for Services Module
服务模块单元测试
"""

import unittest
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.services import VideoService, BatchService, WorkflowService
from core.detection import FrameDifferenceDetector
from core.processing import ProcessingConfig


class TestVideoService(unittest.TestCase):
    """视频服务测试"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = FrameDifferenceDetector(threshold=0.3)
        self.temp_dir = tempfile.mkdtemp()
        self.video_service = VideoService(
            detector=self.detector,
            enable_cache=True,
            cache_dir=self.temp_dir
        )
    
    def tearDown(self):
        """测试后清理"""
        self.video_service.cleanup()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.video_service.detector)
        self.assertTrue(self.video_service.enable_cache)
        self.assertEqual(str(self.video_service.cache_dir), self.temp_dir)
    
    def test_get_supported_formats(self):
        """测试获取支持的格式"""
        formats = self.video_service.get_supported_formats()
        self.assertIsInstance(formats, list)
        self.assertIn('.mp4', formats)
        self.assertIn('.avi', formats)
    
    def test_validate_video_file(self):
        """测试视频文件验证"""
        # 测试不存在的文件
        result = self.video_service.validate_video_file("nonexistent.mp4")
        self.assertFalse(result)
        
        # 创建临时文件测试
        temp_file = Path(self.temp_dir) / "test.mp4"
        temp_file.write_text("dummy content")
        
        result = self.video_service.validate_video_file(str(temp_file))
        self.assertTrue(result)
    
    def test_generate_cache_key(self):
        """测试缓存键生成"""
        key1 = self.video_service._generate_cache_key("test.mp4", {"param": "value"})
        key2 = self.video_service._generate_cache_key("test.mp4", {"param": "value"})
        key3 = self.video_service._generate_cache_key("test.mp4", {"param": "other"})
        
        # 相同输入应该生成相同的键
        self.assertEqual(key1, key2)
        # 不同输入应该生成不同的键
        self.assertNotEqual(key1, key3)
    
    def test_performance_stats(self):
        """测试性能统计"""
        stats = self.video_service.get_performance_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_processed', stats)
        self.assertIn('cache_hits', stats)
        self.assertIn('cache_misses', stats)
        self.assertIn('errors', stats)
    
    def test_cache_info(self):
        """测试缓存信息"""
        cache_info = self.video_service.get_cache_info()
        
        self.assertIsInstance(cache_info, dict)
        self.assertTrue(cache_info['enabled'])
        self.assertEqual(cache_info['cache_dir'], self.temp_dir)
    
    def test_clear_cache(self):
        """测试清空缓存"""
        # 创建一些缓存文件
        cache_file = Path(self.temp_dir) / "test_cache.json"
        cache_file.write_text('{"test": "data"}')
        
        result = self.video_service.clear_cache()
        self.assertTrue(result)
        self.assertFalse(cache_file.exists())
    
    @patch('core.services.video_service.cv2.VideoCapture')
    def test_get_video_info(self, mock_video_capture):
        """测试获取视频信息"""
        # 模拟视频捕获
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            3: 1920,  # WIDTH
            4: 1080,  # HEIGHT
            5: 30.0,  # FPS
            7: 900    # FRAME_COUNT
        }.get(prop, 0)
        
        result = self.video_service.get_video_info("test.mp4")
        
        self.assertTrue(result['success'])
        self.assertIn('info', result)
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with VideoService(self.detector) as service:
            self.assertIsNotNone(service)
        # 上下文退出后应该自动清理


class TestBatchService(unittest.TestCase):
    """批量服务测试"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = FrameDifferenceDetector(threshold=0.3)
        self.temp_dir = tempfile.mkdtemp()
        self.batch_service = BatchService(self.detector, max_workers=2)
    
    def tearDown(self):
        """测试后清理"""
        self.batch_service.stop_processing()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.batch_service.max_workers, 2)
        self.assertIsNotNone(self.batch_service.video_service)
    
    def test_scan_video_files(self):
        """测试扫描视频文件"""
        # 创建测试文件
        test_files = [
            Path(self.temp_dir) / "video1.mp4",
            Path(self.temp_dir) / "video2.avi",
            Path(self.temp_dir) / "document.txt"  # 非视频文件
        ]
        
        for file_path in test_files:
            file_path.write_text("dummy content")
        
        video_files = self.batch_service.scan_video_files(self.temp_dir)
        
        # 应该只找到视频文件
        self.assertEqual(len(video_files), 2)
        video_names = [f['name'] for f in video_files]
        self.assertIn('video1.mp4', video_names)
        self.assertIn('video2.avi', video_names)
        self.assertNotIn('document.txt', video_names)
    
    def test_filter_files_by_size(self):
        """测试按大小过滤文件"""
        # 创建不同大小的测试文件
        small_file = Path(self.temp_dir) / "small.mp4"
        large_file = Path(self.temp_dir) / "large.mp4"
        
        small_file.write_text("small")  # 很小的文件
        large_file.write_text("large" * 1000)  # 较大的文件
        
        all_files = self.batch_service.scan_video_files(self.temp_dir)
        
        # 测试最小大小过滤
        filtered_files = self.batch_service._filter_files_by_size(all_files, min_size_mb=0.001)
        self.assertLessEqual(len(filtered_files), len(all_files))
    
    def test_get_processing_status(self):
        """测试获取处理状态"""
        status = self.batch_service.get_processing_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('is_processing', status)
        self.assertIn('max_workers', status)
        self.assertEqual(status['max_workers'], 2)
    
    def test_stop_processing(self):
        """测试停止处理"""
        self.batch_service.stop_processing()
        status = self.batch_service.get_processing_status()
        self.assertFalse(status['is_processing'])
    
    def test_create_batch_report(self):
        """测试创建批量报告"""
        # 模拟处理结果
        results = [
            {
                "success": True,
                "processing_time": 1.5,
                "boundaries": [{"frame": 100}, {"frame": 200}],
                "file_info": {"name": "video1.mp4", "size_mb": 10.5}
            },
            {
                "success": False,
                "error": "Processing failed",
                "file_info": {"name": "video2.mp4", "size_mb": 5.2}
            }
        ]
        
        report_file = self.batch_service.create_batch_report(results, self.temp_dir)
        
        self.assertTrue(Path(report_file).exists())
        
        # 验证报告内容
        with open(report_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        self.assertEqual(report_data['summary']['total_files'], 2)
        self.assertEqual(report_data['summary']['success_count'], 1)
        self.assertEqual(report_data['summary']['failed_count'], 1)
    
    def test_get_batch_statistics(self):
        """测试获取批量统计"""
        results = [
            {
                "success": True,
                "processing_time": 1.5,
                "boundaries": [{"frame": 100}, {"frame": 200}],
                "file_info": {"size_mb": 10.5}
            },
            {
                "success": True,
                "processing_time": 2.0,
                "boundaries": [{"frame": 150}],
                "file_info": {"size_mb": 8.0}
            }
        ]
        
        stats = self.batch_service.get_batch_statistics(results)
        
        self.assertEqual(stats['total_files'], 2)
        self.assertEqual(stats['success_count'], 2)
        self.assertEqual(stats['failed_count'], 0)
        self.assertEqual(stats['success_rate'], 1.0)
        self.assertEqual(stats['total_boundaries'], 3)
        self.assertAlmostEqual(stats['avg_processing_time'], 1.75)


class TestWorkflowService(unittest.TestCase):
    """工作流服务测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.services.workflow_service.get_config')
    def test_initialization(self, mock_get_config):
        """测试初始化"""
        # 模拟配置
        mock_config = MagicMock()
        mock_config.get_detection_config.return_value = {
            'default_detector': 'frame_difference',
            'frame_difference': {'threshold': 0.3}
        }
        mock_config.get_processing_config.return_value = {
            'output': {'format': 'mp4', 'quality': 'high'},
            'segmentation': {'min_segment_duration': 1.0, 'max_segment_duration': 300.0}
        }
        mock_get_config.return_value = mock_config
        
        workflow_service = WorkflowService()
        
        self.assertIsNotNone(workflow_service.video_service)
        self.assertIsNotNone(workflow_service.batch_service)
        self.assertIsNotNone(workflow_service.analysis_service)
        
        workflow_service.cleanup()
    
    @patch('core.services.workflow_service.get_config')
    def test_get_service_status(self, mock_get_config):
        """测试获取服务状态"""
        # 模拟配置
        mock_config = MagicMock()
        mock_config.get_detection_config.return_value = {'default_detector': 'frame_difference'}
        mock_config.get_processing_config.return_value = {'output': {'format': 'mp4'}}
        mock_get_config.return_value = mock_config
        
        workflow_service = WorkflowService()
        status = workflow_service.get_service_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('video_service', status)
        self.assertIn('batch_service', status)
        self.assertIn('detector_info', status)
        self.assertIn('config', status)
        
        workflow_service.cleanup()
    
    @patch('core.services.workflow_service.get_config')
    def test_context_manager(self, mock_get_config):
        """测试上下文管理器"""
        # 模拟配置
        mock_config = MagicMock()
        mock_config.get_detection_config.return_value = {'default_detector': 'frame_difference'}
        mock_config.get_processing_config.return_value = {'output': {'format': 'mp4'}}
        mock_get_config.return_value = mock_config
        
        with WorkflowService() as workflow:
            self.assertIsNotNone(workflow)
            status = workflow.get_service_status()
            self.assertIsInstance(status, dict)
        # 上下文退出后应该自动清理


class TestServiceIntegration(unittest.TestCase):
    """服务集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_service_chain(self):
        """测试服务链调用"""
        # 创建检测器
        detector = FrameDifferenceDetector(threshold=0.3)
        
        # 创建视频服务
        video_service = VideoService(detector, enable_cache=True, cache_dir=self.temp_dir)
        
        # 创建批量服务
        batch_service = BatchService(detector, max_workers=1)
        
        # 测试服务间的协作
        self.assertIsNotNone(video_service.detector)
        self.assertIsNotNone(batch_service.video_service)
        
        # 清理
        video_service.cleanup()
        batch_service.stop_processing()
    
    def test_error_handling(self):
        """测试错误处理"""
        detector = FrameDifferenceDetector(threshold=0.3)
        video_service = VideoService(detector)
        
        # 测试处理不存在的文件
        result = video_service.detect_shots("nonexistent_file.mp4")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        
        video_service.cleanup()


if __name__ == '__main__':
    unittest.main()
