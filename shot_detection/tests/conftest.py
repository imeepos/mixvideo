"""
Pytest Configuration and Fixtures
pytest配置和测试夹具
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock

# 导入测试配置
from . import TEST_CONFIG

# 导入项目模块
from core.detection import FrameDifferenceDetector, HistogramDetector
from core.services import VideoService, BatchService
from config import get_config


@pytest.fixture(scope="session")
def test_config():
    """测试配置夹具"""
    return TEST_CONFIG


@pytest.fixture(scope="session")
def sample_video_path(test_config):
    """示例视频路径夹具"""
    # 创建一个模拟视频文件
    test_data_dir = test_config["test_data_dir"]
    test_data_dir.mkdir(exist_ok=True)
    
    sample_video = test_data_dir / "sample_video.mp4"
    if not sample_video.exists():
        # 创建一个空的测试文件
        sample_video.write_bytes(b"fake video content")
    
    return str(sample_video)


@pytest.fixture(scope="function")
def temp_dir(test_config):
    """临时目录夹具"""
    temp_dir = tempfile.mkdtemp(dir=test_config["temp_dir"])
    yield temp_dir
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def output_dir(test_config):
    """输出目录夹具"""
    output_dir = tempfile.mkdtemp(dir=test_config["output_dir"])
    yield output_dir
    # 清理
    shutil.rmtree(output_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def mock_video_capture():
    """模拟视频捕获夹具"""
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.get.side_effect = lambda prop: {
        0: 1920,  # CAP_PROP_FRAME_WIDTH
        1: 1080,  # CAP_PROP_FRAME_HEIGHT
        5: 30.0,  # CAP_PROP_FPS
        7: 1000   # CAP_PROP_FRAME_COUNT
    }.get(prop, 0)
    
    # 模拟帧读取
    import numpy as np
    fake_frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    mock_cap.read.return_value = (True, fake_frame)
    
    return mock_cap


@pytest.fixture(scope="function")
def frame_difference_detector():
    """帧差检测器夹具"""
    return FrameDifferenceDetector(threshold=0.3)


@pytest.fixture(scope="function")
def histogram_detector():
    """直方图检测器夹具"""
    return HistogramDetector(threshold=0.4, bins=64)


@pytest.fixture(scope="function")
def video_service(frame_difference_detector):
    """视频服务夹具"""
    return VideoService(frame_difference_detector)


@pytest.fixture(scope="function")
def batch_service(frame_difference_detector):
    """批量服务夹具"""
    return BatchService(frame_difference_detector)


@pytest.fixture(scope="function")
def test_config_manager():
    """测试配置管理器夹具"""
    config = get_config()
    # 设置测试模式
    config.set('testing.enabled', True)
    config.set('testing.use_mock_data', True)
    config.set('logging.level', 'DEBUG')
    return config


@pytest.fixture(scope="function")
def mock_detection_result():
    """模拟检测结果夹具"""
    from core.detection.models import DetectionResult, ShotBoundary
    
    boundaries = [
        ShotBoundary(frame_number=30, timestamp=1.0, confidence=0.8),
        ShotBoundary(frame_number=90, timestamp=3.0, confidence=0.9),
        ShotBoundary(frame_number=150, timestamp=5.0, confidence=0.7),
    ]
    
    return DetectionResult(
        boundaries=boundaries,
        algorithm_name="MockDetector",
        processing_time=2.5,
        frame_count=180
    )


@pytest.fixture(scope="function")
def mock_video_files(temp_dir):
    """模拟视频文件列表夹具"""
    video_files = []
    for i in range(3):
        video_file = Path(temp_dir) / f"test_video_{i}.mp4"
        video_file.write_bytes(b"fake video content")
        video_files.append(str(video_file))
    
    return video_files


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """自动设置测试环境"""
    # 设置环境变量
    monkeypatch.setenv("SHOT_DETECTION_ENV", "testing")
    monkeypatch.setenv("SHOT_DETECTION_LOG_LEVEL", "DEBUG")
    
    # 禁用GUI相关功能
    monkeypatch.setenv("SHOT_DETECTION_DISABLE_GUI", "1")


@pytest.fixture(scope="function")
def performance_monitor():
    """性能监控器夹具"""
    from core.performance import PerformanceMonitor
    monitor = PerformanceMonitor()
    yield monitor
    monitor.cleanup()


@pytest.fixture(scope="function")
def memory_manager():
    """内存管理器夹具"""
    from core.performance import MemoryManager
    manager = MemoryManager()
    yield manager
    manager.cleanup()


# 测试标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "performance: 性能测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )
    config.addinivalue_line(
        "markers", "gpu: GPU测试"
    )
    config.addinivalue_line(
        "markers", "cloud: 云服务测试"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    # 跳过GPU测试（如果未启用）
    if not TEST_CONFIG.get("enable_gpu_tests", False):
        skip_gpu = pytest.mark.skip(reason="GPU tests disabled")
        for item in items:
            if "gpu" in item.keywords:
                item.add_marker(skip_gpu)
    
    # 跳过云服务测试（如果未启用）
    if not TEST_CONFIG.get("enable_cloud_tests", False):
        skip_cloud = pytest.mark.skip(reason="Cloud tests disabled")
        for item in items:
            if "cloud" in item.keywords:
                item.add_marker(skip_cloud)
    
    # 跳过性能测试（如果未启用）
    if not TEST_CONFIG.get("enable_performance_tests", True):
        skip_performance = pytest.mark.skip(reason="Performance tests disabled")
        for item in items:
            if "performance" in item.keywords:
                item.add_marker(skip_performance)


# 测试报告钩子
def pytest_html_report_title(report):
    """自定义HTML报告标题"""
    report.title = "Shot Detection v2.0 Test Report"


def pytest_html_results_summary(prefix, summary, postfix):
    """自定义HTML报告摘要"""
    prefix.extend([
        "<h2>Shot Detection v2.0</h2>",
        "<p>Advanced Video Shot Boundary Detection System</p>"
    ])


# 测试失败时的调试信息
@pytest.fixture(autouse=True)
def capture_debug_info(request):
    """捕获调试信息"""
    yield
    
    if request.node.rep_call.failed:
        # 测试失败时收集调试信息
        print("\n=== DEBUG INFO ===")
        print(f"Test: {request.node.name}")
        print(f"File: {request.node.fspath}")
        
        # 可以添加更多调试信息收集逻辑


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """生成测试报告"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
