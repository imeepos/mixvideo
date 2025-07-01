"""
Test Utilities
测试工具
"""

import json
import random
import string
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from loguru import logger


class TestUtils:
    """测试工具类"""
    
    @staticmethod
    def generate_random_string(length: int = 10) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def generate_random_number(min_val: float = 0, max_val: float = 100) -> float:
        """生成随机数字"""
        return random.uniform(min_val, max_val)
    
    @staticmethod
    def generate_random_boolean() -> bool:
        """生成随机布尔值"""
        return random.choice([True, False])
    
    @staticmethod
    def generate_random_list(item_count: int = 5, item_type: str = 'string') -> List[Any]:
        """生成随机列表"""
        items = []
        
        for _ in range(item_count):
            if item_type == 'string':
                items.append(TestUtils.generate_random_string())
            elif item_type == 'number':
                items.append(TestUtils.generate_random_number())
            elif item_type == 'boolean':
                items.append(TestUtils.generate_random_boolean())
            else:
                items.append(TestUtils.generate_random_string())
        
        return items
    
    @staticmethod
    def generate_random_dict(key_count: int = 5) -> Dict[str, Any]:
        """生成随机字典"""
        result = {}
        
        for _ in range(key_count):
            key = TestUtils.generate_random_string(8)
            value_type = random.choice(['string', 'number', 'boolean', 'list'])
            
            if value_type == 'string':
                result[key] = TestUtils.generate_random_string()
            elif value_type == 'number':
                result[key] = TestUtils.generate_random_number()
            elif value_type == 'boolean':
                result[key] = TestUtils.generate_random_boolean()
            elif value_type == 'list':
                result[key] = TestUtils.generate_random_list(3)
        
        return result
    
    @staticmethod
    def create_mock_file(file_path: Path, content: str = "", encoding: str = 'utf-8'):
        """创建模拟文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    
    @staticmethod
    def create_mock_json_file(file_path: Path, data: Dict[str, Any]):
        """创建模拟JSON文件"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_test_data(file_path: Path) -> Any:
        """加载测试数据"""
        if not file_path.exists():
            raise FileNotFoundError(f"Test data file not found: {file_path}")
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    @staticmethod
    def compare_files(file1: Path, file2: Path) -> bool:
        """比较两个文件是否相同"""
        if not file1.exists() or not file2.exists():
            return False
        
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            return f1.read() == f2.read()
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """获取文件大小"""
        if file_path.exists():
            return file_path.stat().st_size
        return 0
    
    @staticmethod
    def wait_for_condition(condition_func: callable, timeout: float = 10.0, 
                          interval: float = 0.1) -> bool:
        """等待条件满足"""
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(interval)
        
        return False
    
    @staticmethod
    def measure_execution_time(func: callable, *args, **kwargs) -> tuple[Any, float]:
        """测量函数执行时间"""
        import time
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        return result, duration
    
    @staticmethod
    def create_temporary_directory(base_dir: Optional[Path] = None) -> Path:
        """创建临时目录"""
        import tempfile
        
        if base_dir:
            temp_dir = base_dir / f"temp_{TestUtils.generate_random_string(8)}"
            temp_dir.mkdir(parents=True, exist_ok=True)
            return temp_dir
        else:
            return Path(tempfile.mkdtemp())
    
    @staticmethod
    def cleanup_directory(directory: Path):
        """清理目录"""
        import shutil
        
        if directory.exists():
            shutil.rmtree(directory)


class MockDataGenerator:
    """模拟数据生成器"""
    
    def __init__(self):
        """初始化模拟数据生成器"""
        self.logger = logger.bind(component="MockDataGenerator")
    
    def generate_mock_video_metadata(self, video_count: int = 1) -> List[Dict[str, Any]]:
        """生成模拟视频元数据"""
        videos = []
        
        for i in range(video_count):
            video = {
                'id': f"video_{i:04d}",
                'filename': f"test_video_{i:04d}.mp4",
                'path': f"/test/videos/test_video_{i:04d}.mp4",
                'duration': TestUtils.generate_random_number(10, 300),  # 10秒到5分钟
                'width': random.choice([640, 720, 1280, 1920]),
                'height': random.choice([480, 576, 720, 1080]),
                'fps': random.choice([24, 25, 30, 60]),
                'format': random.choice(['mp4', 'avi', 'mov', 'mkv']),
                'size_bytes': random.randint(1024*1024, 100*1024*1024),  # 1MB到100MB
                'created_at': self._generate_random_datetime(),
                'modified_at': self._generate_random_datetime()
            }
            videos.append(video)
        
        return videos
    
    def generate_mock_detection_results(self, video_duration: float = 60.0,
                                      shot_count: Optional[int] = None) -> Dict[str, Any]:
        """生成模拟检测结果"""
        if shot_count is None:
            shot_count = random.randint(3, 10)
        
        boundaries = []
        
        # 生成镜头边界
        for i in range(shot_count):
            timestamp = (video_duration / shot_count) * i
            frame_number = int(timestamp * 30)  # 假设30fps
            
            boundary = {
                'frame_number': frame_number,
                'timestamp': timestamp,
                'confidence': TestUtils.generate_random_number(0.5, 1.0),
                'boundary_type': random.choice(['cut', 'fade', 'dissolve'])
            }
            boundaries.append(boundary)
        
        return {
            'success': True,
            'boundaries': boundaries,
            'algorithm_name': random.choice(['frame_difference', 'histogram', 'optical_flow']),
            'processing_time': TestUtils.generate_random_number(1.0, 10.0),
            'frame_count': int(video_duration * 30),
            'parameters': {
                'threshold': TestUtils.generate_random_number(0.1, 0.9),
                'min_shot_duration': TestUtils.generate_random_number(0.5, 2.0)
            }
        }
    
    def generate_mock_export_data(self, boundary_count: int = 5) -> Dict[str, Any]:
        """生成模拟导出数据"""
        shots = []
        
        for i in range(boundary_count - 1):
            shot = {
                'shot_id': i + 1,
                'start_frame': i * 30,
                'end_frame': (i + 1) * 30,
                'start_time': i * 1.0,
                'end_time': (i + 1) * 1.0,
                'duration': 1.0,
                'confidence': TestUtils.generate_random_number(0.7, 1.0)
            }
            shots.append(shot)
        
        return {
            'video_info': {
                'filename': 'test_video.mp4',
                'duration': boundary_count * 1.0,
                'fps': 30,
                'width': 1920,
                'height': 1080
            },
            'detection_info': {
                'algorithm': 'frame_difference',
                'threshold': 0.5,
                'total_shots': len(shots)
            },
            'shots': shots,
            'export_info': {
                'format': 'json',
                'exported_at': datetime.now().isoformat(),
                'version': '2.0.0'
            }
        }
    
    def generate_mock_config_data(self) -> Dict[str, Any]:
        """生成模拟配置数据"""
        return {
            'app': {
                'name': 'Shot Detection Test',
                'version': '2.0.0',
                'debug': TestUtils.generate_random_boolean(),
                'log_level': random.choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'])
            },
            'detection': {
                'default_algorithm': random.choice(['frame_difference', 'histogram', 'optical_flow']),
                'threshold': TestUtils.generate_random_number(0.1, 0.9),
                'min_shot_duration': TestUtils.generate_random_number(0.5, 3.0),
                'max_shot_duration': TestUtils.generate_random_number(60.0, 300.0)
            },
            'processing': {
                'max_workers': random.randint(1, 8),
                'chunk_size': random.randint(500, 2000),
                'memory_limit_mb': random.randint(512, 4096),
                'temp_dir': './temp'
            },
            'export': {
                'default_format': random.choice(['json', 'csv', 'xml']),
                'include_metadata': TestUtils.generate_random_boolean(),
                'compress_output': TestUtils.generate_random_boolean()
            }
        }
    
    def generate_mock_user_settings(self) -> Dict[str, Any]:
        """生成模拟用户设置"""
        return {
            'ui': {
                'theme': random.choice(['default', 'dark', 'light']),
                'language': random.choice(['en_US', 'zh_CN', 'ja_JP']),
                'font_size': random.randint(10, 16),
                'window_size': [random.randint(800, 1920), random.randint(600, 1080)],
                'auto_save': TestUtils.generate_random_boolean()
            },
            'detection': {
                'default_threshold': TestUtils.generate_random_number(0.3, 0.7),
                'preview_enabled': TestUtils.generate_random_boolean(),
                'auto_detect_on_load': TestUtils.generate_random_boolean()
            },
            'recent': {
                'files': [f"/path/to/video_{i}.mp4" for i in range(5)],
                'projects': [f"/path/to/project_{i}" for i in range(3)]
            }
        }
    
    def generate_mock_performance_data(self, test_count: int = 10) -> List[Dict[str, Any]]:
        """生成模拟性能数据"""
        performance_data = []
        
        algorithms = ['frame_difference', 'histogram', 'optical_flow']
        
        for i in range(test_count):
            data = {
                'test_id': f"perf_test_{i:03d}",
                'algorithm': random.choice(algorithms),
                'video_duration': TestUtils.generate_random_number(30, 300),
                'video_resolution': random.choice(['720p', '1080p', '4K']),
                'processing_time': TestUtils.generate_random_number(5, 60),
                'memory_usage_mb': random.randint(100, 1000),
                'cpu_usage_percent': TestUtils.generate_random_number(20, 90),
                'shots_detected': random.randint(5, 50),
                'accuracy_score': TestUtils.generate_random_number(0.7, 0.95),
                'timestamp': self._generate_random_datetime()
            }
            performance_data.append(data)
        
        return performance_data
    
    def _generate_random_datetime(self) -> str:
        """生成随机日期时间"""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        
        random_date = start_date + timedelta(days=random_days)
        return random_date.isoformat()
    
    def create_mock_test_environment(self, base_dir: Path) -> Dict[str, Path]:
        """创建模拟测试环境"""
        try:
            # 创建目录结构
            directories = {
                'videos': base_dir / 'videos',
                'output': base_dir / 'output',
                'config': base_dir / 'config',
                'temp': base_dir / 'temp',
                'logs': base_dir / 'logs'
            }
            
            for dir_path in directories.values():
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # 创建模拟配置文件
            config_data = self.generate_mock_config_data()
            TestUtils.create_mock_json_file(directories['config'] / 'config.json', config_data)
            
            # 创建模拟用户设置
            user_settings = self.generate_mock_user_settings()
            TestUtils.create_mock_json_file(directories['config'] / 'user_settings.json', user_settings)
            
            # 创建模拟视频元数据
            video_metadata = self.generate_mock_video_metadata(5)
            TestUtils.create_mock_json_file(directories['videos'] / 'metadata.json', video_metadata)
            
            self.logger.info(f"Mock test environment created at: {base_dir}")
            
            return directories
            
        except Exception as e:
            self.logger.error(f"Failed to create mock test environment: {e}")
            raise
