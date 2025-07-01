"""
Base Test Classes
基础测试类
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger

# Import from parent directory
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.detection import ShotDetector
from core.processing import VideoProcessor


class BaseTestCase(unittest.TestCase):
    """基础测试用例"""
    
    @classmethod
    def setUpClass(cls):
        """类级别初始化"""
        cls.logger = logger.bind(component=cls.__name__)
        cls.test_data_dir = Path(__file__).parent / "fixtures"
        cls.temp_dir = Path(tempfile.mkdtemp())
        cls.output_dir = cls.temp_dir / "output"
        cls.output_dir.mkdir(exist_ok=True)
        
        cls.logger.info(f"Test class setup: {cls.__name__}")
    
    @classmethod
    def tearDownClass(cls):
        """类级别清理"""
        try:
            if cls.temp_dir.exists():
                shutil.rmtree(cls.temp_dir)
            cls.logger.info(f"Test class cleanup: {cls.__name__}")
        except Exception as e:
            cls.logger.error(f"Cleanup failed: {e}")
    
    def setUp(self):
        """测试用例初始化"""
        self.test_start_time = self._get_current_time()
        self.logger.debug(f"Test setup: {self._testMethodName}")
    
    def tearDown(self):
        """测试用例清理"""
        duration = self._get_current_time() - self.test_start_time
        self.logger.debug(f"Test cleanup: {self._testMethodName} ({duration:.3f}s)")
    
    def _get_current_time(self) -> float:
        """获取当前时间"""
        import time
        return time.time()
    
    def create_temp_file(self, content: str = "", suffix: str = ".txt") -> Path:
        """
        创建临时文件
        
        Args:
            content: 文件内容
            suffix: 文件后缀
            
        Returns:
            临时文件路径
        """
        temp_file = self.temp_dir / f"temp_{self._get_current_time()}{suffix}"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return temp_file
    
    def create_temp_dir(self, name: str = "") -> Path:
        """
        创建临时目录
        
        Args:
            name: 目录名称
            
        Returns:
            临时目录路径
        """
        if not name:
            name = f"temp_dir_{self._get_current_time()}"
        
        temp_dir = self.temp_dir / name
        temp_dir.mkdir(exist_ok=True)
        
        return temp_dir
    
    def assert_file_exists(self, file_path: Path, msg: str = ""):
        """断言文件存在"""
        self.assertTrue(file_path.exists(), msg or f"File does not exist: {file_path}")
    
    def assert_file_not_exists(self, file_path: Path, msg: str = ""):
        """断言文件不存在"""
        self.assertFalse(file_path.exists(), msg or f"File should not exist: {file_path}")
    
    def assert_dir_exists(self, dir_path: Path, msg: str = ""):
        """断言目录存在"""
        self.assertTrue(dir_path.is_dir(), msg or f"Directory does not exist: {dir_path}")
    
    def assert_json_equal(self, json1: Dict[str, Any], json2: Dict[str, Any], msg: str = ""):
        """断言JSON相等"""
        import json
        
        json1_str = json.dumps(json1, sort_keys=True)
        json2_str = json.dumps(json2, sort_keys=True)
        
        self.assertEqual(json1_str, json2_str, msg or "JSON objects are not equal")
    
    def assert_approximately_equal(self, value1: float, value2: float, 
                                  tolerance: float = 0.001, msg: str = ""):
        """断言近似相等"""
        diff = abs(value1 - value2)
        self.assertLessEqual(diff, tolerance, 
                           msg or f"Values not approximately equal: {value1} vs {value2} (tolerance: {tolerance})")
    
    def assert_list_contains_subset(self, subset: List[Any], superset: List[Any], msg: str = ""):
        """断言列表包含子集"""
        for item in subset:
            self.assertIn(item, superset, msg or f"Item {item} not found in superset")
    
    def skip_if_no_gpu(self):
        """如果没有GPU则跳过测试"""
        try:
            import torch
            if not torch.cuda.is_available():
                self.skipTest("GPU not available")
        except ImportError:
            self.skipTest("PyTorch not available")
    
    def skip_if_no_opencv(self):
        """如果没有OpenCV则跳过测试"""
        try:
            import cv2
        except ImportError:
            self.skipTest("OpenCV not available")
    
    def skip_if_slow_test(self):
        """如果是慢速测试则跳过"""
        import os
        if os.getenv('SKIP_SLOW_TESTS', 'false').lower() == 'true':
            self.skipTest("Slow tests disabled")


class DetectionTestCase(BaseTestCase):
    """检测测试用例基类"""
    
    @classmethod
    def setUpClass(cls):
        """类级别初始化"""
        super().setUpClass()
        
        # 创建检测器
        cls.detector = ShotDetector()
        
        # 创建视频处理器
        cls.video_processor = VideoProcessor()
        
        # 测试视频配置
        cls.test_video_config = {
            'width': 640,
            'height': 480,
            'fps': 30,
            'duration': 10,  # 秒
            'format': 'mp4'
        }
        
        cls.logger.info("Detection test class setup completed")
    
    def create_test_video(self, config: Optional[Dict[str, Any]] = None) -> Path:
        """
        创建测试视频
        
        Args:
            config: 视频配置
            
        Returns:
            测试视频路径
        """
        try:
            import cv2
            import numpy as np
            
            video_config = config or self.test_video_config
            
            # 创建视频文件
            video_path = self.temp_dir / f"test_video_{self._get_current_time()}.mp4"
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(
                str(video_path),
                fourcc,
                video_config['fps'],
                (video_config['width'], video_config['height'])
            )
            
            # 生成测试帧
            total_frames = int(video_config['fps'] * video_config['duration'])
            
            for frame_idx in range(total_frames):
                # 创建渐变帧（模拟场景变化）
                frame = np.zeros((video_config['height'], video_config['width'], 3), dtype=np.uint8)
                
                # 每30帧改变颜色（模拟镜头切换）
                color_idx = frame_idx // 30
                colors = [
                    (255, 0, 0),    # 红色
                    (0, 255, 0),    # 绿色
                    (0, 0, 255),    # 蓝色
                    (255, 255, 0),  # 黄色
                    (255, 0, 255),  # 紫色
                    (0, 255, 255),  # 青色
                ]
                
                color = colors[color_idx % len(colors)]
                frame[:] = color
                
                # 添加一些噪声
                noise = np.random.randint(0, 50, frame.shape, dtype=np.uint8)
                frame = cv2.add(frame, noise)
                
                writer.write(frame)
            
            writer.release()
            
            self.logger.debug(f"Created test video: {video_path}")
            return video_path
            
        except ImportError:
            self.skipTest("OpenCV not available for video creation")
        except Exception as e:
            self.fail(f"Failed to create test video: {e}")
    
    def create_test_video_with_shots(self, shot_durations: List[float]) -> Path:
        """
        创建包含指定镜头的测试视频
        
        Args:
            shot_durations: 镜头持续时间列表（秒）
            
        Returns:
            测试视频路径
        """
        try:
            import cv2
            import numpy as np
            
            video_path = self.temp_dir / f"test_shots_video_{self._get_current_time()}.mp4"
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(
                str(video_path),
                fourcc,
                self.test_video_config['fps'],
                (self.test_video_config['width'], self.test_video_config['height'])
            )
            
            colors = [
                (255, 0, 0),    # 红色
                (0, 255, 0),    # 绿色
                (0, 0, 255),    # 蓝色
                (255, 255, 0),  # 黄色
                (255, 0, 255),  # 紫色
                (0, 255, 255),  # 青色
            ]
            
            for shot_idx, duration in enumerate(shot_durations):
                color = colors[shot_idx % len(colors)]
                frames_count = int(duration * self.test_video_config['fps'])
                
                for _ in range(frames_count):
                    frame = np.zeros((
                        self.test_video_config['height'],
                        self.test_video_config['width'],
                        3
                    ), dtype=np.uint8)
                    
                    frame[:] = color
                    
                    # 添加轻微噪声
                    noise = np.random.randint(0, 20, frame.shape, dtype=np.uint8)
                    frame = cv2.add(frame, noise)
                    
                    writer.write(frame)
            
            writer.release()
            
            self.logger.debug(f"Created test video with shots: {video_path}")
            return video_path
            
        except ImportError:
            self.skipTest("OpenCV not available for video creation")
        except Exception as e:
            self.fail(f"Failed to create test video with shots: {e}")
    
    def assert_detection_results_valid(self, results: Dict[str, Any], msg: str = ""):
        """断言检测结果有效"""
        # 检查基本结构
        self.assertIn('success', results, msg or "Missing 'success' field")
        self.assertIn('boundaries', results, msg or "Missing 'boundaries' field")
        
        if results['success']:
            boundaries = results['boundaries']
            self.assertIsInstance(boundaries, list, msg or "Boundaries should be a list")
            
            # 检查边界格式
            for boundary in boundaries:
                self.assertIn('frame_number', boundary, msg or "Missing 'frame_number' in boundary")
                self.assertIn('timestamp', boundary, msg or "Missing 'timestamp' in boundary")
                self.assertIsInstance(boundary['frame_number'], int, msg or "frame_number should be int")
                self.assertIsInstance(boundary['timestamp'], (int, float), msg or "timestamp should be numeric")
    
    def assert_shot_count_approximately(self, results: Dict[str, Any], 
                                      expected_count: int, tolerance: int = 1, msg: str = ""):
        """断言镜头数量近似正确"""
        if results.get('success', False):
            actual_count = len(results.get('boundaries', []))
            diff = abs(actual_count - expected_count)
            self.assertLessEqual(diff, tolerance, 
                               msg or f"Shot count not approximately correct: {actual_count} vs {expected_count}")
    
    def assert_shot_durations_valid(self, results: Dict[str, Any], 
                                   min_duration: float = 0.1, max_duration: float = 300.0, msg: str = ""):
        """断言镜头持续时间有效"""
        if results.get('success', False):
            boundaries = results.get('boundaries', [])
            
            if len(boundaries) > 1:
                for i in range(len(boundaries) - 1):
                    duration = boundaries[i + 1]['timestamp'] - boundaries[i]['timestamp']
                    
                    self.assertGreaterEqual(duration, min_duration, 
                                          msg or f"Shot duration too short: {duration}")
                    self.assertLessEqual(duration, max_duration, 
                                       msg or f"Shot duration too long: {duration}")
    
    def run_detection_test(self, video_path: Path, algorithm: str = "frame_difference",
                          **kwargs) -> Dict[str, Any]:
        """
        运行检测测试
        
        Args:
            video_path: 视频路径
            algorithm: 检测算法
            **kwargs: 其他参数
            
        Returns:
            检测结果
        """
        try:
            # 配置检测器
            self.detector.set_algorithm(algorithm)
            
            # 设置参数
            for key, value in kwargs.items():
                self.detector.set_parameter(key, value)
            
            # 运行检测
            results = self.detector.detect_shots(str(video_path))
            
            # 验证结果
            self.assert_detection_results_valid(results)
            
            return results
            
        except Exception as e:
            self.fail(f"Detection test failed: {e}")
    
    def benchmark_detection_speed(self, video_path: Path, algorithm: str = "frame_difference",
                                 iterations: int = 3) -> Dict[str, Any]:
        """
        基准测试检测速度
        
        Args:
            video_path: 视频路径
            algorithm: 检测算法
            iterations: 迭代次数
            
        Returns:
            性能统计
        """
        try:
            import time
            
            times = []
            
            for i in range(iterations):
                start_time = time.time()
                
                results = self.run_detection_test(video_path, algorithm)
                
                end_time = time.time()
                duration = end_time - start_time
                times.append(duration)
                
                self.logger.debug(f"Iteration {i + 1}: {duration:.3f}s")
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            return {
                'algorithm': algorithm,
                'iterations': iterations,
                'times': times,
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'video_path': str(video_path)
            }
            
        except Exception as e:
            self.fail(f"Speed benchmark failed: {e}")
