"""
Shot Detection v2.0 Test Suite
测试套件
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
TEST_DIR = Path(__file__).parent
ROOT_DIR = TEST_DIR.parent
sys.path.insert(0, str(ROOT_DIR))

# 测试配置
TEST_CONFIG = {
    "test_data_dir": TEST_DIR / "fixtures",
    "temp_dir": TEST_DIR / "temp",
    "output_dir": TEST_DIR / "output",
    "sample_videos": [
        "sample_video_1.mp4",
        "sample_video_2.avi",
        "sample_video_3.mov"
    ],
    "test_timeout": 30.0,
    "enable_gpu_tests": False,
    "enable_cloud_tests": False,
    "enable_performance_tests": True
}

# 创建测试目录
for dir_path in [TEST_CONFIG["temp_dir"], TEST_CONFIG["output_dir"]]:
    dir_path.mkdir(exist_ok=True)

__version__ = "2.0.0"
__author__ = "Shot Detection Team"

# Import testing framework components
from .test_runner import TestRunner, TestSuite
from .test_base import BaseTestCase, DetectionTestCase
from .test_utils import TestUtils, MockDataGenerator
from .performance_tests import PerformanceTestRunner, BenchmarkSuite
from .integration_tests import IntegrationTestRunner, SystemTestSuite

__all__ = [
    "TestRunner",
    "TestSuite",
    "BaseTestCase",
    "DetectionTestCase",
    "TestUtils",
    "MockDataGenerator",
    "PerformanceTestRunner",
    "BenchmarkSuite",
    "IntegrationTestRunner",
    "SystemTestSuite",
    "TEST_CONFIG",
    "TEST_DIR",
    "ROOT_DIR",
]
