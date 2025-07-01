# 🛠️ Shot Detection v2.0 开发指南

## 📋 概述

本指南为 Shot Detection v2.0 的开发者提供详细的开发环境搭建、代码规范、开发流程和最佳实践。

## 🚀 快速开始

### 环境要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **内存**: 建议 8GB 以上
- **存储**: 至少 2GB 可用空间

### 开发环境搭建

#### 1. 克隆项目
```bash
git clone <repository-url>
cd shot_detection
```

#### 2. 创建虚拟环境
```bash
# 使用 venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 使用 conda
conda create -n shot_detection python=3.8
conda activate shot_detection
```

#### 3. 安装依赖
```bash
# 基础依赖
pip install -r requirements.txt

# 开发依赖
pip install -r requirements-dev.txt

# 可选依赖
pip install -r requirements-optional.txt
```

#### 4. 配置开发环境
```bash
# 设置环境变量
export SHOT_DETECTION_ENV=development
export SHOT_DETECTION_LOG_LEVEL=DEBUG

# 初始化配置
python setup_dev.py
```

## 📁 项目结构

```
shot_detection/
├── core/                    # 核心模块
│   ├── detection/          # 检测算法
│   ├── processing/         # 视频处理
│   ├── services/           # 业务服务
│   ├── performance/        # 性能优化
│   └── plugins/            # 插件系统
├── gui/                    # 用户界面
│   ├── components/         # GUI组件
│   ├── dialogs/           # 对话框
│   └── main_window.py     # 主窗口
├── config/                 # 配置管理
├── jianying/              # 剪映功能
├── tests/                 # 测试代码
├── examples/              # 示例代码
├── docs/                  # 文档
├── requirements.txt       # 基础依赖
├── requirements-dev.txt   # 开发依赖
├── setup.py              # 安装脚本
└── README.md             # 项目说明
```

## 📝 代码规范

### Python 代码风格

遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范：

#### 1. 命名规范
```python
# 类名：大驼峰命名
class VideoDetector:
    pass

# 函数和变量：小写下划线
def detect_shot_boundaries():
    video_path = "example.mp4"
    
# 常量：大写下划线
MAX_VIDEO_SIZE = 1024 * 1024 * 1024

# 私有成员：前缀下划线
class MyClass:
    def __init__(self):
        self._private_var = None
        self.__very_private = None
```

#### 2. 文档字符串
```python
def detect_boundaries(video_path: str, threshold: float = 0.3) -> DetectionResult:
    """
    检测视频镜头边界
    
    Args:
        video_path: 视频文件路径
        threshold: 检测阈值，范围 0.0-1.0
        
    Returns:
        DetectionResult: 检测结果对象
        
    Raises:
        VideoLoadError: 视频文件无法加载
        DetectionError: 检测过程中出现错误
        
    Example:
        >>> detector = FrameDifferenceDetector()
        >>> result = detector.detect_boundaries("video.mp4", 0.3)
        >>> print(f"Found {len(result.boundaries)} boundaries")
    """
```

#### 3. 类型注解
```python
from typing import List, Dict, Optional, Union, Callable

def process_videos(video_paths: List[str], 
                  config: Dict[str, Any],
                  callback: Optional[Callable[[float, str], None]] = None) -> List[Dict[str, Any]]:
    """处理多个视频文件"""
    pass
```

#### 4. 错误处理
```python
# 使用具体的异常类型
try:
    result = detector.detect_boundaries(video_path)
except VideoLoadError as e:
    logger.error(f"Failed to load video {video_path}: {e}")
    raise
except DetectionError as e:
    logger.warning(f"Detection failed: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise DetectionError(f"Unexpected error during detection: {e}")
```

### 代码质量工具

#### 1. 代码格式化
```bash
# 使用 black 格式化代码
black shot_detection/

# 使用 isort 排序导入
isort shot_detection/
```

#### 2. 代码检查
```bash
# 使用 flake8 检查代码风格
flake8 shot_detection/

# 使用 pylint 进行静态分析
pylint shot_detection/

# 使用 mypy 进行类型检查
mypy shot_detection/
```

#### 3. 配置文件
```ini
# setup.cfg
[flake8]
max-line-length = 88
exclude = .git,__pycache__,venv
ignore = E203,W503

[isort]
profile = black
multi_line_output = 3

[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
```

## 🧪 测试指南

### 测试结构

```
tests/
├── unit/                   # 单元测试
│   ├── test_detection/    # 检测模块测试
│   ├── test_services/     # 服务模块测试
│   └── test_config/       # 配置模块测试
├── integration/           # 集成测试
├── performance/           # 性能测试
├── fixtures/              # 测试数据
└── conftest.py           # pytest 配置
```

### 编写测试

#### 1. 单元测试示例
```python
import pytest
from unittest.mock import Mock, patch
from core.detection import FrameDifferenceDetector

class TestFrameDifferenceDetector:
    
    def setup_method(self):
        """每个测试方法前执行"""
        self.detector = FrameDifferenceDetector(threshold=0.3)
    
    def test_initialization(self):
        """测试初始化"""
        assert self.detector.threshold == 0.3
        assert self.detector.name == "FrameDifference"
    
    def test_detect_boundaries_success(self):
        """测试成功检测"""
        with patch('cv2.VideoCapture') as mock_cap:
            # 模拟视频捕获
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.return_value = 30.0
            
            result = self.detector.detect_boundaries("test_video.mp4")
            
            assert result.success
            assert isinstance(result.boundaries, list)
    
    def test_detect_boundaries_invalid_video(self):
        """测试无效视频文件"""
        with pytest.raises(VideoLoadError):
            self.detector.detect_boundaries("nonexistent.mp4")
    
    @pytest.mark.parametrize("threshold,expected", [
        (0.1, True),
        (0.5, True),
        (1.0, True),
        (-0.1, False),
        (1.1, False),
    ])
    def test_threshold_validation(self, threshold, expected):
        """测试阈值验证"""
        if expected:
            detector = FrameDifferenceDetector(threshold=threshold)
            assert detector.threshold == threshold
        else:
            with pytest.raises(ValueError):
                FrameDifferenceDetector(threshold=threshold)
```

#### 2. 集成测试示例
```python
import tempfile
from pathlib import Path
from core.services import VideoService
from core.detection import FrameDifferenceDetector

class TestVideoServiceIntegration:
    
    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = FrameDifferenceDetector()
        self.service = VideoService(self.detector)
    
    def teardown_method(self):
        """清理测试环境"""
        self.service.cleanup()
        # 清理临时目录
    
    def test_end_to_end_processing(self):
        """端到端处理测试"""
        # 使用测试视频文件
        test_video = "tests/fixtures/sample_video.mp4"
        
        result = self.service.detect_shots(
            video_path=test_video,
            output_dir=self.temp_dir
        )
        
        assert result["success"]
        assert len(result["boundaries"]) > 0
        
        # 检查输出文件
        output_files = list(Path(self.temp_dir).glob("*.json"))
        assert len(output_files) > 0
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_detection/test_frame_diff.py

# 运行特定测试类
pytest tests/unit/test_detection/test_frame_diff.py::TestFrameDifferenceDetector

# 运行特定测试方法
pytest tests/unit/test_detection/test_frame_diff.py::TestFrameDifferenceDetector::test_initialization

# 生成覆盖率报告
pytest --cov=shot_detection --cov-report=html

# 并行运行测试
pytest -n auto
```

## 🔧 开发工具

### IDE 配置

#### VS Code 配置
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm 配置
- 启用 Code inspection
- 配置 Black 作为代码格式化工具
- 设置 pytest 作为默认测试运行器

### 调试技巧

#### 1. 日志调试
```python
from loguru import logger

# 配置日志
logger.add("debug.log", level="DEBUG", rotation="10 MB")

# 使用日志
logger.debug("Processing video: {}", video_path)
logger.info("Detection completed: {} boundaries found", len(boundaries))
logger.warning("Low confidence boundary at frame {}", frame_number)
logger.error("Failed to process video: {}", error_message)
```

#### 2. 断点调试
```python
import pdb

def detect_boundaries(self, video_path):
    # 设置断点
    pdb.set_trace()
    
    # 或使用 breakpoint() (Python 3.7+)
    breakpoint()
    
    # 调试代码
    result = self._process_video(video_path)
    return result
```

#### 3. 性能分析
```python
import cProfile
import pstats

# 性能分析
profiler = cProfile.Profile()
profiler.enable()

# 执行代码
result = detector.detect_boundaries(video_path)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

## 🔄 开发流程

### Git 工作流

#### 1. 分支策略
```bash
# 主分支
main          # 生产环境代码
develop       # 开发环境代码

# 功能分支
feature/xxx   # 新功能开发
bugfix/xxx    # Bug修复
hotfix/xxx    # 紧急修复
release/xxx   # 发布准备
```

#### 2. 提交规范
```bash
# 提交消息格式
<type>(<scope>): <subject>

<body>

<footer>

# 示例
feat(detection): add histogram detector

Add new histogram-based shot boundary detection algorithm
with configurable bin size and comparison methods.

Closes #123
```

#### 3. 代码审查
- 所有代码必须通过 Pull Request
- 至少需要一个审查者批准
- 必须通过所有自动化测试
- 代码覆盖率不能降低

### 持续集成

#### GitHub Actions 配置
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: flake8 shot_detection/
    
    - name: Test with pytest
      run: pytest --cov=shot_detection
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 📦 模块开发

### 创建新的检测器

#### 1. 实现检测器类
```python
# core/detection/my_detector.py
from .base import BaseDetector, DetectionResult, ShotBoundary

class MyDetector(BaseDetector):
    """自定义检测器"""
    
    def __init__(self, threshold: float = 0.3, **kwargs):
        super().__init__(threshold)
        self.name = "MyDetector"
        # 初始化特定参数
    
    def detect_boundaries(self, video_path: str, 
                         progress_callback=None) -> DetectionResult:
        """实现检测逻辑"""
        try:
            # 检测逻辑实现
            boundaries = self._detect_boundaries_impl(video_path, progress_callback)
            
            return DetectionResult(
                boundaries=boundaries,
                algorithm_name=self.name,
                processing_time=processing_time,
                frame_count=frame_count
            )
        except Exception as e:
            raise DetectionError(f"Detection failed: {e}")
    
    def _detect_boundaries_impl(self, video_path, progress_callback):
        """具体的检测实现"""
        # 实现检测算法
        pass
```

#### 2. 注册检测器
```python
# core/detection/__init__.py
from .my_detector import MyDetector

__all__ = [
    # ... 其他检测器
    "MyDetector",
]
```

#### 3. 编写测试
```python
# tests/unit/test_detection/test_my_detector.py
import pytest
from core.detection import MyDetector

class TestMyDetector:
    def test_initialization(self):
        detector = MyDetector(threshold=0.5)
        assert detector.threshold == 0.5
        assert detector.name == "MyDetector"
    
    # 更多测试...
```

### 创建新的服务

#### 1. 实现服务类
```python
# core/services/my_service.py
from typing import Dict, Any, Optional
from loguru import logger

class MyService:
    """自定义服务"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.bind(component="MyService")
    
    def process(self, input_data: Any) -> Dict[str, Any]:
        """处理逻辑"""
        try:
            # 实现处理逻辑
            result = self._process_impl(input_data)
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup(self):
        """清理资源"""
        pass
```

## 🐛 调试和故障排除

### 常见问题

#### 1. 导入错误
```python
# 问题：ModuleNotFoundError
# 解决：检查 PYTHONPATH 和 __init__.py 文件

# 添加项目根目录到路径
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

#### 2. 内存泄漏
```python
# 问题：内存使用持续增长
# 解决：使用内存分析工具

import tracemalloc

tracemalloc.start()

# 执行代码
process_videos(video_list)

# 获取内存使用情况
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")

tracemalloc.stop()
```

#### 3. 性能问题
```python
# 使用 line_profiler 分析性能
@profile
def slow_function():
    # 慢函数实现
    pass

# 运行：kernprof -l -v script.py
```

### 日志分析

#### 查看日志
```bash
# 查看最新日志
tail -f logs/shot_detection.log

# 搜索错误
grep "ERROR" logs/shot_detection.log

# 按时间过滤
grep "2024-01-01" logs/shot_detection.log
```

## 📚 学习资源

### 推荐阅读
- [Clean Code](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350884)
- [Effective Python](https://effectivepython.com/)
- [Design Patterns](https://refactoring.guru/design-patterns)

### 在线资源
- [Python 官方文档](https://docs.python.org/3/)
- [OpenCV 文档](https://docs.opencv.org/)
- [pytest 文档](https://docs.pytest.org/)

## 🤝 贡献指南

### 提交贡献

1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 确保所有测试通过
5. 提交 Pull Request

### 代码审查清单

- [ ] 代码符合项目规范
- [ ] 包含适当的测试
- [ ] 文档已更新
- [ ] 所有测试通过
- [ ] 代码覆盖率满足要求

---

**📝 文档版本**: v2.0.0  
**📅 最后更新**: 2025-07-01  
**👥 维护团队**: Shot Detection Team
