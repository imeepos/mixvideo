"""
Unit Tests for Detection Module
检测模块单元测试
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.detection import FrameDifferenceDetector, HistogramDetector, MultiDetector
from core.detection.base import ShotBoundary, DetectionResult


class TestFrameDifferenceDetector(unittest.TestCase):
    """帧差检测器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = FrameDifferenceDetector(threshold=0.3)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.detector.threshold, 0.3)
        self.assertEqual(self.detector.name, "FrameDifference")
        self.assertFalse(self.detector.is_initialized)
    
    def test_initialize(self):
        """测试初始化方法"""
        result = self.detector.initialize()
        self.assertTrue(result)
        self.assertTrue(self.detector.is_initialized)
    
    def test_calculate_frame_difference(self):
        """测试帧差计算"""
        # 创建测试帧
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        # 计算帧差
        diff = self.detector._calculate_frame_difference(frame1, frame2)
        
        # 验证结果
        self.assertIsInstance(diff, float)
        self.assertGreater(diff, 0)
        self.assertLessEqual(diff, 1.0)
    
    def test_is_boundary(self):
        """测试边界判断"""
        # 测试超过阈值的情况
        self.assertTrue(self.detector._is_boundary(0.5, 100))
        
        # 测试未超过阈值的情况
        self.assertFalse(self.detector._is_boundary(0.1, 100))
    
    def test_cleanup(self):
        """测试清理方法"""
        self.detector.initialize()
        self.detector.cleanup()
        self.assertFalse(self.detector.is_initialized)


class TestHistogramDetector(unittest.TestCase):
    """直方图检测器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.detector = HistogramDetector(threshold=0.5, bins=256)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.detector.threshold, 0.5)
        self.assertEqual(self.detector.bins, 256)
        self.assertEqual(self.detector.name, "Histogram")
    
    def test_calculate_histogram_difference(self):
        """测试直方图差异计算"""
        # 创建测试帧
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        # 计算直方图差异
        diff = self.detector._calculate_histogram_difference(frame1, frame2)
        
        # 验证结果
        self.assertIsInstance(diff, float)
        self.assertGreaterEqual(diff, 0)
        self.assertLessEqual(diff, 1.0)


class TestMultiDetector(unittest.TestCase):
    """多检测器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.fd_detector = FrameDifferenceDetector(threshold=0.3)
        self.hist_detector = HistogramDetector(threshold=0.5)
        self.detectors = [self.fd_detector, self.hist_detector]
        self.fusion_weights = {"FrameDifference": 0.6, "Histogram": 0.4}
        self.multi_detector = MultiDetector(self.detectors, self.fusion_weights)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(len(self.multi_detector.detectors), 2)
        self.assertEqual(self.multi_detector.fusion_weights, self.fusion_weights)
        self.assertEqual(self.multi_detector.name, "MultiDetector")
    
    def test_initialize_all(self):
        """测试初始化所有检测器"""
        result = self.multi_detector.initialize_all()
        self.assertTrue(result)
        
        for detector in self.multi_detector.detectors:
            self.assertTrue(detector.is_initialized)
    
    def test_fuse_confidences(self):
        """测试置信度融合"""
        confidences = {"FrameDifference": 0.8, "Histogram": 0.6}
        
        fused_confidence = self.multi_detector._fuse_confidences(confidences)
        
        # 验证融合结果
        expected = 0.8 * 0.6 + 0.6 * 0.4
        self.assertAlmostEqual(fused_confidence, expected, places=2)
    
    def test_cluster_boundaries(self):
        """测试边界聚类"""
        # 创建测试边界
        boundaries = [
            ShotBoundary(100, 3.33, 0.8, "shot"),
            ShotBoundary(102, 3.40, 0.7, "shot"),
            ShotBoundary(200, 6.67, 0.9, "shot")
        ]
        
        clustered = self.multi_detector._cluster_boundaries(boundaries, tolerance=5)
        
        # 验证聚类结果
        self.assertLessEqual(len(clustered), len(boundaries))
    
    def test_cleanup(self):
        """测试清理方法"""
        self.multi_detector.initialize_all()
        self.multi_detector.cleanup()
        
        for detector in self.multi_detector.detectors:
            self.assertFalse(detector.is_initialized)


class TestShotBoundary(unittest.TestCase):
    """镜头边界测试"""
    
    def test_creation(self):
        """测试创建边界对象"""
        boundary = ShotBoundary(
            frame_number=100,
            timestamp=3.33,
            confidence=0.8,
            boundary_type="shot",
            metadata={"test": "data"}
        )
        
        self.assertEqual(boundary.frame_number, 100)
        self.assertEqual(boundary.timestamp, 3.33)
        self.assertEqual(boundary.confidence, 0.8)
        self.assertEqual(boundary.boundary_type, "shot")
        self.assertEqual(boundary.metadata["test"], "data")
    
    def test_to_dict(self):
        """测试转换为字典"""
        boundary = ShotBoundary(100, 3.33, 0.8, "shot")
        boundary_dict = boundary.to_dict()
        
        self.assertIsInstance(boundary_dict, dict)
        self.assertEqual(boundary_dict["frame_number"], 100)
        self.assertEqual(boundary_dict["timestamp"], 3.33)
        self.assertEqual(boundary_dict["confidence"], 0.8)
        self.assertEqual(boundary_dict["boundary_type"], "shot")


class TestDetectionResult(unittest.TestCase):
    """检测结果测试"""
    
    def test_creation(self):
        """测试创建检测结果"""
        boundaries = [
            ShotBoundary(100, 3.33, 0.8, "shot"),
            ShotBoundary(200, 6.67, 0.9, "shot")
        ]
        
        result = DetectionResult(
            boundaries=boundaries,
            algorithm_name="TestAlgorithm",
            processing_time=1.5,
            frame_count=300,
            confidence_scores=[0.8, 0.9]
        )
        
        self.assertEqual(len(result.boundaries), 2)
        self.assertEqual(result.algorithm_name, "TestAlgorithm")
        self.assertEqual(result.processing_time, 1.5)
        self.assertEqual(result.frame_count, 300)
        self.assertEqual(result.confidence_scores, [0.8, 0.9])
    
    def test_to_dict(self):
        """测试转换为字典"""
        boundaries = [ShotBoundary(100, 3.33, 0.8, "shot")]
        result = DetectionResult(boundaries, "TestAlgorithm", 1.5, 300, [0.8])
        
        result_dict = result.to_dict()
        
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(len(result_dict["boundaries"]), 1)
        self.assertEqual(result_dict["algorithm_name"], "TestAlgorithm")
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        boundaries = [
            ShotBoundary(100, 3.33, 0.8, "shot"),
            ShotBoundary(200, 6.67, 0.9, "shot"),
            ShotBoundary(300, 10.0, 0.7, "shot")
        ]
        
        result = DetectionResult(boundaries, "TestAlgorithm", 1.5, 300, [0.8, 0.9, 0.7])
        stats = result.get_statistics()
        
        self.assertEqual(stats["total_boundaries"], 3)
        self.assertAlmostEqual(stats["avg_confidence"], 0.8, places=2)
        self.assertEqual(stats["min_confidence"], 0.7)
        self.assertEqual(stats["max_confidence"], 0.9)


class TestDetectionIntegration(unittest.TestCase):
    """检测模块集成测试"""
    
    @patch('cv2.VideoCapture')
    def test_video_detection_workflow(self, mock_video_capture):
        """测试视频检测工作流"""
        # 模拟视频捕获
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        
        # 模拟视频属性
        mock_cap.get.side_effect = lambda prop: {
            1: 30.0,  # FPS
            7: 900    # FRAME_COUNT
        }.get(prop, 0)
        
        # 模拟帧读取
        mock_frames = [
            (True, np.zeros((100, 100, 3), dtype=np.uint8)),
            (True, np.ones((100, 100, 3), dtype=np.uint8) * 128),
            (True, np.ones((100, 100, 3), dtype=np.uint8) * 255),
            (False, None)
        ]
        mock_cap.read.side_effect = mock_frames
        
        # 测试检测
        detector = FrameDifferenceDetector(threshold=0.1)
        detector.initialize()
        
        # 这里应该调用实际的检测方法，但由于需要完整的视频处理逻辑，
        # 我们只测试检测器的基本功能
        self.assertTrue(detector.is_initialized)
        
        detector.cleanup()


if __name__ == '__main__':
    unittest.main()
