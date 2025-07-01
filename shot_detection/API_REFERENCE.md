# 📚 Shot Detection v2.0 API 参考文档

## 🎯 概述

本文档提供 Shot Detection v2.0 的完整 API 参考，包括所有核心模块、类和方法的详细说明。

## 📦 模块结构

```
shot_detection/
├── core/                   # 核心模块
│   ├── detection/         # 检测算法
│   ├── processing/        # 视频处理
│   ├── services/          # 业务服务
│   └── plugins/           # 插件系统
├── gui/                   # GUI界面
├── config/                # 配置管理
└── jianying/             # 剪映功能
```

## 🔍 检测模块 (core.detection)

### BaseDetector

所有检测器的抽象基类。

```python
from core.detection import BaseDetector

class BaseDetector(ABC):
    def __init__(self, threshold: float = 0.3):
        """
        初始化检测器
        
        Args:
            threshold: 检测阈值 (0.0-1.0)
        """
    
    @abstractmethod
    def detect_boundaries(self, video_path: str, 
                         progress_callback: Optional[Callable] = None) -> DetectionResult:
        """
        检测镜头边界
        
        Args:
            video_path: 视频文件路径
            progress_callback: 进度回调函数
            
        Returns:
            DetectionResult: 检测结果对象
        """
    
    def initialize(self) -> bool:
        """初始化检测器"""
    
    def cleanup(self):
        """清理资源"""
```

### FrameDifferenceDetector

基于帧差的镜头检测器。

```python
from core.detection import FrameDifferenceDetector

# 创建检测器
detector = FrameDifferenceDetector(threshold=0.3)

# 初始化
detector.initialize()

# 检测镜头边界
result = detector.detect_boundaries("video.mp4")

# 清理资源
detector.cleanup()
```

**参数说明**:
- `threshold` (float): 帧差阈值，范围 0.0-1.0，默认 0.3
- `min_interval` (int): 最小镜头间隔帧数，默认 30

### HistogramDetector

基于直方图的镜头检测器。

```python
from core.detection import HistogramDetector

# 创建检测器
detector = HistogramDetector(
    threshold=0.5,
    bins=256,
    method='correlation'
)

# 检测镜头边界
result = detector.detect_boundaries("video.mp4")
```

**参数说明**:
- `threshold` (float): 直方图差异阈值，范围 0.0-1.0，默认 0.5
- `bins` (int): 直方图bins数量，默认 256
- `method` (str): 比较方法，可选 'correlation', 'chi_square', 'intersection'

### MultiDetector

多算法融合检测器。

```python
from core.detection import MultiDetector, FrameDifferenceDetector, HistogramDetector

# 创建子检测器
fd_detector = FrameDifferenceDetector(threshold=0.3)
hist_detector = HistogramDetector(threshold=0.5)

# 创建融合检测器
multi_detector = MultiDetector(
    detectors=[fd_detector, hist_detector],
    fusion_weights={"FrameDifference": 0.6, "Histogram": 0.4}
)

# 检测镜头边界
result = multi_detector.detect_boundaries("video.mp4")
```

**参数说明**:
- `detectors` (List[BaseDetector]): 子检测器列表
- `fusion_weights` (Dict[str, float]): 融合权重字典
- `clustering_tolerance` (int): 边界聚类容差，默认 5

### DetectionResult

检测结果数据类。

```python
from core.detection import DetectionResult, ShotBoundary

# 创建边界对象
boundary = ShotBoundary(
    frame_number=150,
    timestamp=5.0,
    confidence=0.85,
    boundary_type="shot"
)

# 创建检测结果
result = DetectionResult(
    boundaries=[boundary],
    algorithm_name="FrameDifference",
    processing_time=12.34,
    frame_count=7200,
    confidence_scores=[0.85]
)

# 获取统计信息
stats = result.get_statistics()
print(f"总边界数: {stats['total_boundaries']}")
print(f"平均置信度: {stats['avg_confidence']}")

# 转换为字典
result_dict = result.to_dict()
```

## 🎬 服务模块 (core.services)

### VideoService

单视频处理服务。

```python
from core.services import VideoService
from core.detection import FrameDifferenceDetector

# 创建检测器
detector = FrameDifferenceDetector()

# 创建视频服务
video_service = VideoService(
    detector=detector,
    enable_cache=True,
    cache_dir="./cache"
)

# 检测镜头边界
result = video_service.detect_shots(
    video_path="video.mp4",
    output_dir="./output"
)

# 异步检测
import asyncio
async_result = await video_service.detect_shots_async("video.mp4")

# 获取视频信息
info = video_service.get_video_info("video.mp4")

# 获取性能统计
stats = video_service.get_performance_stats()

# 清理资源
video_service.cleanup()
```

**主要方法**:

#### detect_shots()
```python
def detect_shots(self, video_path: str, 
                output_dir: Optional[str] = None,
                progress_callback: Optional[Callable] = None,
                force_reprocess: bool = False) -> Dict[str, Any]:
    """
    检测视频镜头边界
    
    Args:
        video_path: 视频文件路径
        output_dir: 输出目录
        progress_callback: 进度回调函数
        force_reprocess: 是否强制重新处理
        
    Returns:
        检测结果字典
    """
```

#### get_performance_stats()
```python
def get_performance_stats(self) -> Dict[str, Any]:
    """
    获取性能统计信息
    
    Returns:
        性能统计字典，包含：
        - total_processed: 总处理文件数
        - total_processing_time: 总处理时间
        - avg_processing_time: 平均处理时间
        - cache_hits: 缓存命中次数
        - cache_misses: 缓存未命中次数
        - cache_hit_rate: 缓存命中率
        - errors: 错误次数
    """
```

### BatchService

批量处理服务。

```python
from core.services import BatchService

# 创建批量服务
batch_service = BatchService(
    detector=detector,
    max_workers=4
)

# 扫描视频文件
video_files = batch_service.scan_video_files(
    directory="./videos",
    recursive=True,
    min_size_mb=1.0,
    max_size_mb=1000.0
)

# 批量处理
results = batch_service.process_batch(
    video_files=video_files,
    output_dir="./batch_output",
    progress_callback=lambda completed, total, current: print(f"{completed}/{total}: {current}")
)

# 创建批量报告
report_file = batch_service.create_batch_report(results, "./reports")

# 获取统计信息
stats = batch_service.get_batch_statistics(results)

# 停止处理
batch_service.stop_processing()
```

### WorkflowService

完整工作流服务。

```python
from core.services import WorkflowService

# 创建工作流服务
with WorkflowService() as workflow:
    # 处理单个视频
    result = workflow.process_single_video(
        video_path="video.mp4",
        output_dir="./output",
        include_analysis=True
    )
    
    # 批量处理
    batch_result = workflow.process_batch_videos(
        video_paths=["video1.mp4", "video2.mp4"],
        output_dir="./batch_output",
        include_analysis=True
    )
    
    # 获取服务状态
    status = workflow.get_service_status()
```

### AdvancedAnalysisService

高级视频分析服务。

```python
from core.services import AdvancedAnalysisService

# 创建分析服务
analysis_service = AdvancedAnalysisService()

# 综合视频分析
result = analysis_service.analyze_video_comprehensive(
    video_path="video.mp4",
    detection_result=detection_result,
    progress_callback=lambda p, s: print(f"{p:.1%}: {s}")
)

# 分析结果包含：
# - video_metrics: 视频基本指标
# - quality_analysis: 质量分析结果
# - shot_analyses: 镜头分析结果
# - analysis_report: 综合分析报告
```

## ⚙️ 配置模块 (config)

### ConfigManager

配置管理器。

```python
from config import ConfigManager, get_config

# 获取全局配置实例
config = get_config()

# 获取配置值
app_name = config.get('app.name')
threshold = config.get('detection.frame_difference.threshold', 0.3)

# 设置配置值
config.set('detection.frame_difference.threshold', 0.4)

# 保存配置
config.save_config()

# 获取专门配置
detection_config = config.get_detection_config()
processing_config = config.get_processing_config()
gui_config = config.get_gui_config()

# 验证配置
is_valid, errors = config.validate_config()

# 重置为默认值
config.reset_to_defaults()

# 创建备份
backup_file = config.create_backup()

# 恢复备份
config.restore_backup(backup_file)
```

## 🔌 插件模块 (core.plugins)

### BasePlugin

插件基类。

```python
from core.plugins import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
        
    def initialize(self) -> bool:
        """初始化插件"""
        # 插件初始化逻辑
        return True
        
    def cleanup(self):
        """清理插件资源"""
        pass
        
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "My custom plugin"
        }
```

### PluginManager

插件管理器。

```python
from core.plugins import PluginManager

# 创建插件管理器
plugin_manager = PluginManager(plugin_dir="./plugins")

# 发现插件
discovered = plugin_manager.discover_plugins()

# 加载插件
success = plugin_manager.load_plugin("my_plugin")

# 启用插件
plugin_manager.enable_plugin("my_plugin")

# 获取插件实例
plugin = plugin_manager.get_plugin("my_plugin")

# 列出插件
all_plugins = plugin_manager.list_plugins()
enabled_plugins = plugin_manager.list_enabled_plugins()

# 获取插件状态
status = plugin_manager.get_plugin_status()

# 重新加载插件
plugin_manager.reload_plugin("my_plugin")

# 清理所有插件
plugin_manager.cleanup_all()
```

## 🖥️ GUI模块 (gui)

### MainWindow

主窗口类。

```python
from gui import MainWindow
from config import get_config

# 创建主窗口
config = get_config()
main_window = MainWindow(config)

# 运行应用
main_window.run()
```

### BaseTab

Tab基类。

```python
from gui.components import BaseTab
import tkinter as tk
from tkinter import ttk

class MyTab(BaseTab):
    def setup_ui(self):
        """设置UI界面"""
        label = ttk.Label(self.frame, text="My Custom Tab")
        label.pack(pady=20)
        
    def bind_events(self):
        """绑定事件"""
        pass
        
    def on_tab_selected(self):
        """Tab被选中时的回调"""
        super().on_tab_selected()
        print("My tab selected")
        
    def cleanup(self):
        """清理资源"""
        super().cleanup()
```

## 📊 数据类型

### ShotBoundary

镜头边界数据类。

```python
from core.detection import ShotBoundary

boundary = ShotBoundary(
    frame_number=150,      # 帧号
    timestamp=5.0,         # 时间戳(秒)
    confidence=0.85,       # 置信度(0.0-1.0)
    boundary_type="shot",  # 边界类型
    metadata={}           # 元数据
)

# 转换为字典
boundary_dict = boundary.to_dict()
```

### VideoMetrics

视频指标数据类。

```python
from core.services import VideoMetrics

metrics = VideoMetrics(
    duration=120.5,           # 时长(秒)
    frame_count=3615,         # 总帧数
    fps=30.0,                # 帧率
    resolution=(1920, 1080),  # 分辨率
    bitrate=5000000,         # 比特率
    file_size_mb=50.2        # 文件大小(MB)
)
```

## 🔧 实用工具

### 进度回调函数

```python
def progress_callback(progress: float, status: str):
    """
    进度回调函数
    
    Args:
        progress: 进度值 (0.0-1.0)
        status: 状态描述
    """
    print(f"进度: {progress:.1%} - {status}")

# 在检测中使用
result = detector.detect_boundaries("video.mp4", progress_callback)
```

### 批量进度回调

```python
def batch_progress_callback(completed: int, total: int, current_file: str):
    """
    批量处理进度回调
    
    Args:
        completed: 已完成数量
        total: 总数量
        current_file: 当前处理文件
    """
    print(f"批量进度: {completed}/{total} - 当前: {current_file}")

# 在批量处理中使用
results = batch_service.process_batch(files, progress_callback=batch_progress_callback)
```

## 🚨 异常处理

### 自定义异常

```python
from core.detection import DetectionError
from core.plugins import PluginError, PluginInitializationError

try:
    result = detector.detect_boundaries("video.mp4")
except DetectionError as e:
    print(f"检测错误: {e}")
except PluginError as e:
    print(f"插件错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

### 错误处理最佳实践

```python
# 使用上下文管理器自动清理资源
with VideoService(detector) as service:
    result = service.detect_shots("video.mp4")
    # 自动调用 cleanup()

# 检查结果状态
if result["success"]:
    boundaries = result["boundaries"]
    print(f"检测到 {len(boundaries)} 个镜头边界")
else:
    error_msg = result.get("error", "未知错误")
    print(f"检测失败: {error_msg}")
```

## 📈 性能优化

### 缓存配置

```python
# 启用缓存
video_service = VideoService(
    detector=detector,
    enable_cache=True,
    cache_dir="./cache"
)

# 获取缓存信息
cache_info = video_service.get_cache_info()
print(f"缓存命中率: {cache_info['cache_hit_rate']:.1%}")

# 清空缓存
video_service.clear_cache()
```

### 并行处理优化

```python
# 根据系统资源自动优化
optimization = batch_service.optimize_batch_parameters(
    file_count=100,
    avg_file_size_mb=50.0
)

print(f"推荐工作线程数: {optimization['max_workers']}")
print(f"推荐块大小: {optimization['chunk_size']}")
```

## 🔍 调试和日志

### 日志配置

```python
from loguru import logger

# 配置日志
logger.add("shot_detection.log", 
          level="INFO", 
          rotation="10 MB",
          retention="7 days")

# 在代码中使用
logger.info("开始处理视频")
logger.error("处理失败: {error}", error=str(e))
```

### 调试模式

```python
# 启用详细日志
import os
os.environ['SHOT_DETECTION_LOG_LEVEL'] = 'DEBUG'

# 启用性能分析
video_service = VideoService(detector, enable_profiling=True)
```

---

**📚 这是 Shot Detection v2.0 的完整 API 参考文档。**

如需更多信息，请参考源代码注释或联系技术支持。
