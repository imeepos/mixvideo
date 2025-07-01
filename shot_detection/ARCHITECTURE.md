# 🏗️ Shot Detection v2.0 架构文档

## 📋 概述

Shot Detection v2.0 采用现代化的分层架构设计，实现了高内聚、低耦合的模块化系统。本文档详细描述了系统的架构设计、模块组织和设计模式。

## 🎯 架构原则

### 1. 分层架构 (Layered Architecture)
- **表示层 (Presentation Layer)**: GUI界面和用户交互
- **业务逻辑层 (Business Logic Layer)**: 核心业务逻辑和算法
- **数据访问层 (Data Access Layer)**: 数据存储和缓存管理
- **基础设施层 (Infrastructure Layer)**: 系统服务和工具

### 2. 模块化设计 (Modular Design)
- 每个模块职责单一，边界清晰
- 模块间通过定义良好的接口通信
- 支持插件化扩展

### 3. 依赖注入 (Dependency Injection)
- 通过配置管理器注入依赖
- 便于测试和模块替换
- 降低模块间耦合度

## 🏛️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Shot Detection v2.0                     │
├─────────────────────────────────────────────────────────────┤
│                   Presentation Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Main Window │  │ Components  │  │   Dialogs   │        │
│  │             │  │             │  │             │        │
│  │ - VideoTab  │  │ - BaseTab   │  │ - Settings  │        │
│  │ - BatchTab  │  │ - Controls  │  │ - About     │        │
│  │ - ToolsTab  │  │ - Widgets   │  │ - Progress  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                  Business Logic Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Detection  │  │ Processing  │  │  Services   │        │
│  │             │  │             │  │             │        │
│  │ - Detectors │  │ - Processor │  │ - Video     │        │
│  │ - Algorithms│  │ - Segments  │  │ - Batch     │        │
│  │ - Results   │  │ - Analysis  │  │ - Workflow  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                  Data Access Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Config    │  │   Cache     │  │   Export    │        │
│  │             │  │             │  │             │        │
│  │ - Manager   │  │ - Memory    │  │ - Formats   │        │
│  │ - Schemas   │  │ - Disk      │  │ - Handlers  │        │
│  │ - Defaults  │  │ - Optimizer │  │ - Projects  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                Infrastructure Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Plugins    │  │ Performance │  │   JianYing  │        │
│  │             │  │             │  │             │        │
│  │ - Manager   │  │ - Monitor   │  │ - Services  │        │
│  │ - Base      │  │ - Memory    │  │ - Managers  │        │
│  │ - Registry  │  │ - Resources │  │ - Models    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 📦 模块详细设计

### Core 模块

#### Detection (检测模块)
```python
core/detection/
├── __init__.py           # 模块导出
├── base.py              # 基础检测器抽象类
├── frame_diff.py        # 帧差检测器
├── histogram.py         # 直方图检测器
├── multi_detector.py    # 多算法融合检测器
└── models.py           # 数据模型
```

**设计模式**: 策略模式 (Strategy Pattern)
- `BaseDetector`: 抽象策略
- `FrameDifferenceDetector`, `HistogramDetector`: 具体策略
- `MultiDetector`: 策略组合器

#### Services (服务模块)
```python
core/services/
├── __init__.py           # 模块导出
├── video_service.py     # 单视频处理服务
├── batch_service.py     # 批量处理服务
├── workflow_service.py  # 工作流服务
└── analysis_service.py  # 分析服务
```

**设计模式**: 门面模式 (Facade Pattern)
- 为复杂的子系统提供简化接口
- 封装业务逻辑复杂性

#### Performance (性能模块)
```python
core/performance/
├── __init__.py           # 模块导出
├── memory_manager.py    # 内存管理器
├── performance_monitor.py # 性能监控器
├── cache_optimizer.py   # 缓存优化器
└── resource_manager.py  # 资源管理器
```

**设计模式**: 观察者模式 (Observer Pattern)
- 性能监控器作为主题
- 各种回调函数作为观察者

### GUI 模块

#### Components (组件模块)
```python
gui/components/
├── __init__.py          # 模块导出
├── base_tab.py         # 基础Tab抽象类
├── video_tab.py        # 视频处理Tab
├── batch_tab.py        # 批量处理Tab
├── analysis_tab.py     # 分析Tab
└── tools_tab.py        # 工具Tab
```

**设计模式**: 模板方法模式 (Template Method Pattern)
- `BaseTab`: 定义Tab的基本结构和流程
- 具体Tab类: 实现特定的业务逻辑

#### Main Window (主窗口)
```python
gui/main_window.py       # 主窗口实现
```

**设计模式**: 单例模式 (Singleton Pattern)
- 确保应用程序只有一个主窗口实例

### Config 模块

#### Configuration Management
```python
config/
├── __init__.py          # 模块导出
├── manager.py          # 配置管理器
├── defaults.py         # 默认配置
└── schemas.py          # 配置模式
```

**设计模式**: 单例模式 + 工厂模式
- 全局配置管理器单例
- 配置对象工厂创建

### Plugins 模块

#### Plugin System
```python
core/plugins/
├── __init__.py          # 模块导出
├── base_plugin.py      # 插件基类
├── plugin_manager.py   # 插件管理器
└── registry.py         # 插件注册表
```

**设计模式**: 插件模式 (Plugin Pattern)
- 动态加载和管理插件
- 支持运行时扩展功能

## 🔄 数据流设计

### 1. 视频处理流程

```
用户输入 → GUI组件 → 服务层 → 检测器 → 处理器 → 导出器 → 结果输出
    ↓         ↓        ↓        ↓        ↓        ↓        ↓
  验证    → 事件处理 → 业务逻辑 → 算法执行 → 数据处理 → 格式转换 → 文件保存
```

### 2. 配置管理流程

```
配置文件 → 配置管理器 → 配置验证 → 配置分发 → 模块配置
    ↓         ↓          ↓        ↓        ↓
  YAML解析 → 对象创建 → 模式验证 → 依赖注入 → 运行时配置
```

### 3. 插件加载流程

```
插件目录 → 插件发现 → 插件加载 → 插件验证 → 插件注册 → 插件激活
    ↓         ↓        ↓        ↓        ↓        ↓
  文件扫描 → 动态导入 → 类实例化 → 接口检查 → 注册表更新 → 功能可用
```

## 🎨 设计模式应用

### 1. 创建型模式

#### 工厂方法模式 (Factory Method)
```python
class DetectorFactory:
    @staticmethod
    def create_detector(detector_type: str, **kwargs) -> BaseDetector:
        if detector_type == "frame_difference":
            return FrameDifferenceDetector(**kwargs)
        elif detector_type == "histogram":
            return HistogramDetector(**kwargs)
        # ...
```

#### 建造者模式 (Builder)
```python
class WorkflowBuilder:
    def __init__(self):
        self.workflow = Workflow()
    
    def add_detection_step(self, detector):
        self.workflow.add_step(DetectionStep(detector))
        return self
    
    def add_analysis_step(self, analyzer):
        self.workflow.add_step(AnalysisStep(analyzer))
        return self
    
    def build(self):
        return self.workflow
```

### 2. 结构型模式

#### 适配器模式 (Adapter)
```python
class LegacyDetectorAdapter(BaseDetector):
    def __init__(self, legacy_detector):
        self.legacy_detector = legacy_detector
    
    def detect_boundaries(self, video_path):
        # 适配旧接口到新接口
        legacy_result = self.legacy_detector.detect(video_path)
        return self._convert_result(legacy_result)
```

#### 装饰器模式 (Decorator)
```python
class CachedDetector(BaseDetector):
    def __init__(self, detector, cache_manager):
        self.detector = detector
        self.cache_manager = cache_manager
    
    def detect_boundaries(self, video_path):
        cache_key = self._generate_cache_key(video_path)
        if self.cache_manager.has(cache_key):
            return self.cache_manager.get(cache_key)
        
        result = self.detector.detect_boundaries(video_path)
        self.cache_manager.set(cache_key, result)
        return result
```

### 3. 行为型模式

#### 策略模式 (Strategy)
```python
class DetectionStrategy:
    def __init__(self, detector: BaseDetector):
        self.detector = detector
    
    def execute(self, video_path):
        return self.detector.detect_boundaries(video_path)

class DetectionContext:
    def __init__(self, strategy: DetectionStrategy):
        self.strategy = strategy
    
    def set_strategy(self, strategy: DetectionStrategy):
        self.strategy = strategy
    
    def detect(self, video_path):
        return self.strategy.execute(video_path)
```

#### 观察者模式 (Observer)
```python
class ProgressSubject:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer):
        self.observers.append(observer)
    
    def notify(self, progress, status):
        for observer in self.observers:
            observer.update(progress, status)

class ProgressObserver:
    def update(self, progress, status):
        # 更新进度显示
        pass
```

## 🔧 扩展性设计

### 1. 插件扩展

系统支持通过插件扩展功能：

```python
class CustomDetectorPlugin(BasePlugin):
    def initialize(self):
        # 注册自定义检测器
        detector_registry.register("custom", CustomDetector)
    
    def cleanup(self):
        # 清理资源
        detector_registry.unregister("custom")
```

### 2. 算法扩展

新的检测算法可以通过继承`BaseDetector`轻松添加：

```python
class AIDetector(BaseDetector):
    def __init__(self, model_path):
        super().__init__()
        self.model = load_model(model_path)
    
    def detect_boundaries(self, video_path):
        # AI模型检测逻辑
        pass
```

### 3. 格式扩展

新的导出格式可以通过实现`FormatHandler`接口添加：

```python
class CustomFormatHandler(FormatHandler):
    def export(self, data, output_path):
        # 自定义格式导出逻辑
        pass
```

## 📊 性能考虑

### 1. 内存管理
- 使用内存管理器监控和优化内存使用
- 实现智能缓存策略
- 支持大文件的流式处理

### 2. 并发处理
- 批量处理支持多线程并行
- 异步I/O操作
- 线程池管理

### 3. 缓存策略
- 多级缓存设计
- LRU缓存淘汰策略
- 缓存预热和失效机制

## 🛡️ 错误处理

### 1. 异常层次
```python
ShotDetectionError
├── DetectionError
│   ├── VideoLoadError
│   ├── AlgorithmError
│   └── ResultError
├── ProcessingError
│   ├── SegmentationError
│   └── AnalysisError
└── ConfigurationError
    ├── ValidationError
    └── LoadError
```

### 2. 错误恢复
- 自动重试机制
- 降级处理策略
- 用户友好的错误提示

## 🔍 测试架构

### 1. 测试层次
- **单元测试**: 测试单个模块和函数
- **集成测试**: 测试模块间交互
- **系统测试**: 测试完整工作流
- **性能测试**: 测试系统性能指标

### 2. 测试工具
- pytest: 单元测试框架
- mock: 模拟对象
- coverage: 代码覆盖率
- benchmark: 性能基准测试

## 📈 监控和日志

### 1. 日志系统
- 结构化日志记录
- 多级别日志输出
- 日志轮转和归档

### 2. 性能监控
- 实时性能指标收集
- 资源使用监控
- 性能瓶颈分析

## 🔮 未来扩展

### 1. 微服务架构
- 将核心功能拆分为独立服务
- 支持分布式部署
- API网关和服务发现

### 2. 云原生支持
- 容器化部署
- Kubernetes编排
- 云存储集成

### 3. AI/ML集成
- 深度学习模型集成
- 自动模型训练
- 智能参数调优

---

**📝 文档版本**: v2.0.0  
**📅 最后更新**: 2025-07-01  
**👥 维护团队**: Shot Detection Team
