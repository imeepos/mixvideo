"""
Unit Tests for Detection Module
检测模块单元测试
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from core.detection import (
    FrameDifferenceDetector, 
    HistogramDetector, 
    MultiDetector,
    DetectionResult,
    ShotBoundary
)
from core.detection.base import BaseDetector


class TestBaseDetector:
    """基础检测器测试"""
    
    def test_base_detector_initialization(self):
        """测试基础检测器初始化"""
        detector = BaseDetector(threshold=0.5)
        assert detector.threshold == 0.5
        assert detector.name == "BaseDetector"
    
    def test_base_detector_invalid_threshold(self):
        """测试无效阈值"""
        with pytest.raises(ValueError):
            BaseDetector(threshold=-0.1)
        
        with pytest.raises(ValueError):
            BaseDetector(threshold=1.1)
    
    def test_base_detector_abstract_method(self):
        """测试抽象方法"""
        detector = BaseDetector()
        with pytest.raises(NotImplementedError):
            detector.detect_boundaries("test.mp4")


class TestFrameDifferenceDetector:
    """帧差检测器测试"""
    
    def test_initialization(self, frame_difference_detector):
        """测试初始化"""
        assert frame_difference_detector.threshold == 0.3
        assert frame_difference_detector.name == "FrameDifference"
    
    def test_initialization_with_custom_params(self):
        """测试自定义参数初始化"""
        detector = FrameDifferenceDetector(
            threshold=0.5,
            min_shot_length=2.0,
            blur_kernel_size=7
        )
        assert detector.threshold == 0.5
        assert detector.min_shot_length == 2.0
        assert detector.blur_kernel_size == 7
    
    @patch('cv2.VideoCapture')
    def test_detect_boundaries_success(self, mock_video_capture, frame_difference_detector):
        """测试成功检测边界"""
        # 设置模拟视频捕获
        mock_cap = mock_video_capture.return_value
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            0: 1920,  # width
            1: 1080,  # height
            5: 30.0,  # fps
            7: 300    # frame_count
        }.get(prop, 0)
        
        # 模拟帧读取
        frames = []
        for i in range(10):
            frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
            frames.append((True, frame))
        
        mock_cap.read.side_effect = frames + [(False, None)]
        
        # 执行检测
        result = frame_difference_detector.detect_boundaries("test_video.mp4")
        
        # 验证结果
        assert isinstance(result, DetectionResult)
        assert result.algorithm_name == "FrameDifference"
        assert result.frame_count > 0
        assert result.processing_time > 0
        assert isinstance(result.boundaries, list)
    
    @patch('cv2.VideoCapture')
    def test_detect_boundaries_invalid_video(self, mock_video_capture, frame_difference_detector):
        """测试无效视频文件"""
        mock_cap = mock_video_capture.return_value
        mock_cap.isOpened.return_value = False
        
        with pytest.raises(Exception):
            frame_difference_detector.detect_boundaries("invalid_video.mp4")
    
    def test_calculate_frame_difference(self, frame_difference_detector):
        """测试帧差计算"""
        # 创建测试帧
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        # 计算帧差
        diff = frame_difference_detector._calculate_frame_difference(frame1, frame2)
        
        # 验证结果
        assert isinstance(diff, float)
        assert diff > 0
    
    def test_is_shot_boundary(self, frame_difference_detector):
        """测试镜头边界判断"""
        # 测试超过阈值的情况
        assert frame_difference_detector._is_shot_boundary(0.5) == True
        
        # 测试未超过阈值的情况
        assert frame_difference_detector._is_shot_boundary(0.2) == False


class TestHistogramDetector:
    """直方图检测器测试"""
    
    def test_initialization(self, histogram_detector):
        """测试初始化"""
        assert histogram_detector.threshold == 0.4
        assert histogram_detector.bins == 64
        assert histogram_detector.name == "Histogram"
    
    def test_calculate_histogram_difference(self, histogram_detector):
        """测试直方图差异计算"""
        # 创建测试帧
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        # 计算直方图差异
        diff = histogram_detector._calculate_histogram_difference(frame1, frame2)
        
        # 验证结果
        assert isinstance(diff, float)
        assert 0 <= diff <= 1
    
    @patch('cv2.VideoCapture')
    def test_detect_boundaries_with_histogram(self, mock_video_capture, histogram_detector):
        """测试直方图检测边界"""
        # 设置模拟视频捕获
        mock_cap = mock_video_capture.return_value
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            5: 30.0,  # fps
            7: 100    # frame_count
        }.get(prop, 0)
        
        # 模拟帧读取
        frames = []
        for i in range(5):
            frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            frames.append((True, frame))
        
        mock_cap.read.side_effect = frames + [(False, None)]
        
        # 执行检测
        result = histogram_detector.detect_boundaries("test_video.mp4")
        
        # 验证结果
        assert isinstance(result, DetectionResult)
        assert result.algorithm_name == "Histogram"


class TestMultiDetector:
    """多检测器测试"""
    
    def test_initialization(self):
        """测试初始化"""
        fd_detector = FrameDifferenceDetector(threshold=0.3)
        hist_detector = HistogramDetector(threshold=0.4)
        
        multi_detector = MultiDetector([fd_detector, hist_detector])
        
        assert len(multi_detector.detectors) == 2
        assert multi_detector.name == "Multi"
    
    def test_initialization_with_weights(self):
        """测试带权重的初始化"""
        fd_detector = FrameDifferenceDetector(threshold=0.3)
        hist_detector = HistogramDetector(threshold=0.4)
        
        weights = {"FrameDifference": 0.7, "Histogram": 0.3}
        multi_detector = MultiDetector([fd_detector, hist_detector], fusion_weights=weights)
        
        assert multi_detector.fusion_weights == weights
    
    @patch('cv2.VideoCapture')
    def test_detect_boundaries_fusion(self, mock_video_capture):
        """测试融合检测"""
        # 创建检测器
        fd_detector = FrameDifferenceDetector(threshold=0.3)
        hist_detector = HistogramDetector(threshold=0.4)
        multi_detector = MultiDetector([fd_detector, hist_detector])
        
        # 设置模拟视频捕获
        mock_cap = mock_video_capture.return_value
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            5: 30.0,  # fps
            7: 100    # frame_count
        }.get(prop, 0)
        
        # 模拟帧读取
        frames = []
        for i in range(5):
            frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
            frames.append((True, frame))
        
        mock_cap.read.side_effect = frames + [(False, None)]
        
        # 执行检测
        result = multi_detector.detect_boundaries("test_video.mp4")
        
        # 验证结果
        assert isinstance(result, DetectionResult)
        assert result.algorithm_name == "Multi"
    
    def test_fuse_results(self):
        """测试结果融合"""
        fd_detector = FrameDifferenceDetector(threshold=0.3)
        hist_detector = HistogramDetector(threshold=0.4)
        multi_detector = MultiDetector([fd_detector, hist_detector])
        
        # 创建测试结果
        boundaries1 = [
            ShotBoundary(frame_number=30, timestamp=1.0, confidence=0.8),
            ShotBoundary(frame_number=90, timestamp=3.0, confidence=0.9),
        ]
        
        boundaries2 = [
            ShotBoundary(frame_number=35, timestamp=1.17, confidence=0.7),
            ShotBoundary(frame_number=150, timestamp=5.0, confidence=0.8),
        ]
        
        result1 = DetectionResult(boundaries1, "FrameDifference", 1.0, 180)
        result2 = DetectionResult(boundaries2, "Histogram", 1.2, 180)
        
        # 融合结果
        fused_result = multi_detector._fuse_results([result1, result2])
        
        # 验证融合结果
        assert isinstance(fused_result, DetectionResult)
        assert fused_result.algorithm_name == "Multi"
        assert len(fused_result.boundaries) > 0


class TestDetectionResult:
    """检测结果测试"""
    
    def test_detection_result_creation(self, mock_detection_result):
        """测试检测结果创建"""
        result = mock_detection_result
        
        assert len(result.boundaries) == 3
        assert result.algorithm_name == "MockDetector"
        assert result.processing_time == 2.5
        assert result.frame_count == 180
    
    def test_detection_result_to_dict(self, mock_detection_result):
        """测试转换为字典"""
        result = mock_detection_result
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "boundaries" in result_dict
        assert "algorithm_name" in result_dict
        assert "processing_time" in result_dict
        assert "frame_count" in result_dict
    
    def test_detection_result_statistics(self, mock_detection_result):
        """测试统计信息"""
        result = mock_detection_result
        stats = result.get_statistics()
        
        assert isinstance(stats, dict)
        assert "boundary_count" in stats
        assert "average_confidence" in stats
        assert "total_duration" in stats


class TestShotBoundary:
    """镜头边界测试"""
    
    def test_shot_boundary_creation(self):
        """测试镜头边界创建"""
        boundary = ShotBoundary(
            frame_number=100,
            timestamp=3.33,
            confidence=0.85,
            boundary_type="shot"
        )
        
        assert boundary.frame_number == 100
        assert boundary.timestamp == 3.33
        assert boundary.confidence == 0.85
        assert boundary.boundary_type == "shot"
    
    def test_shot_boundary_to_dict(self):
        """测试转换为字典"""
        boundary = ShotBoundary(frame_number=100, timestamp=3.33, confidence=0.85)
        boundary_dict = boundary.to_dict()
        
        assert isinstance(boundary_dict, dict)
        assert boundary_dict["frame_number"] == 100
        assert boundary_dict["timestamp"] == 3.33
        assert boundary_dict["confidence"] == 0.85
    
    def test_shot_boundary_comparison(self):
        """测试边界比较"""
        boundary1 = ShotBoundary(frame_number=100, timestamp=3.33, confidence=0.85)
        boundary2 = ShotBoundary(frame_number=200, timestamp=6.67, confidence=0.75)
        
        assert boundary1 < boundary2  # 按时间戳比较
        assert boundary2 > boundary1


@pytest.mark.performance
class TestDetectionPerformance:
    """检测性能测试"""
    
    def test_frame_difference_performance(self, frame_difference_detector, sample_video_path):
        """测试帧差检测性能"""
        import time
        
        start_time = time.time()
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                5: 30.0, 7: 1000
            }.get(prop, 0)
            
            # 模拟大量帧
            frames = [(True, np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)) 
                     for _ in range(100)]
            mock_cap.return_value.read.side_effect = frames + [(False, None)]
            
            result = frame_difference_detector.detect_boundaries(sample_video_path)
        
        processing_time = time.time() - start_time
        
        # 性能断言
        assert processing_time < 10.0  # 应该在10秒内完成
        assert result.processing_time > 0
    
    @pytest.mark.slow
    def test_memory_usage(self, frame_difference_detector, sample_video_path):
        """测试内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                5: 30.0, 7: 5000  # 大量帧
            }.get(prop, 0)
            
            frames = [(True, np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)) 
                     for _ in range(1000)]
            mock_cap.return_value.read.side_effect = frames + [(False, None)]
            
            result = frame_difference_detector.detect_boundaries(sample_video_path)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # 内存使用不应该过度增长
        assert memory_increase < 500 * 1024 * 1024  # 不超过500MB
