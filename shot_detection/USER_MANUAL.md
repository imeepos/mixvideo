# 📖 Shot Detection v2.0 用户手册

## 🎯 概述

Shot Detection 是一个专业的视频镜头边界检测工具，支持多种检测算法、批量处理、高级分析等功能。本手册将帮助您快速上手并充分利用所有功能。

## 🚀 快速开始

### 系统要求

- **操作系统**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.8 或更高版本
- **内存**: 建议 4GB 以上
- **存储**: 至少 1GB 可用空间

### 安装依赖

```bash
# 安装基础依赖
pip install opencv-python numpy loguru pyyaml

# 可选依赖（用于高级功能）
pip install scikit-learn psutil
```

### 启动应用

```bash
# 启动新版GUI（推荐）
python main_v2.py

# 启动原版GUI（向后兼容）
python main.py
```

## 🖥️ 界面介绍

### 主窗口

Shot Detection v2.0 采用标签页设计，包含以下功能模块：

- **📄 视频分镜**: 单个视频的镜头检测
- **📦 批量处理**: 批量处理多个视频文件
- **🔍 视频分析**: 高级视频内容分析
- **📝 剪映草稿**: 剪映项目文件生成
- **🎬 视频混剪**: 视频混剪功能
- **🔧 实用工具**: 系统工具和维护功能

### 菜单栏

- **文件**: 打开、保存、退出等基本操作
- **编辑**: 设置、偏好等配置选项
- **视图**: 界面主题、布局等显示选项
- **工具**: 实用工具和插件管理
- **帮助**: 用户手册、关于等信息

## 📄 视频分镜功能

### 基本使用

1. **选择视频文件**
   - 点击"浏览..."按钮选择视频文件
   - 支持格式：MP4, AVI, MOV, MKV, WMV, FLV

2. **设置输出目录**
   - 选择检测结果的保存位置
   - 系统会自动创建子目录存放结果

3. **选择检测算法**
   - **帧差检测**: 基于相邻帧差异的快速检测
   - **直方图检测**: 基于颜色直方图的精确检测
   - **多算法融合**: 结合多种算法的高精度检测

4. **调整参数**
   - **阈值**: 控制检测敏感度（0.1-1.0）
   - **最小间隔**: 镜头间最小时间间隔
   - **输出格式**: 选择结果输出格式

5. **开始检测**
   - 点击"开始检测"按钮
   - 实时查看处理进度
   - 检测完成后查看结果

### 高级设置

#### 检测参数优化

```yaml
# 帧差检测参数
frame_difference:
  threshold: 0.3        # 检测阈值
  min_interval: 1.0     # 最小间隔(秒)
  
# 直方图检测参数
histogram:
  threshold: 0.5        # 检测阈值
  bins: 256            # 直方图bins数量
  
# 多算法融合参数
multi_detector:
  fusion_weights:
    FrameDifference: 0.6
    Histogram: 0.4
  clustering_tolerance: 5  # 边界聚类容差(帧)
```

#### 输出格式选项

- **JSON**: 结构化数据，便于程序处理
- **CSV**: 表格格式，便于Excel分析
- **TXT**: 纯文本格式，便于阅读
- **XML**: 标准化格式，便于交换

### 结果解读

检测结果包含以下信息：

```json
{
  "success": true,
  "video_path": "video.mp4",
  "algorithm": "MultiDetector",
  "processing_time": 12.34,
  "frame_count": 7200,
  "boundaries": [
    {
      "frame_number": 150,
      "timestamp": 5.0,
      "confidence": 0.85,
      "boundary_type": "shot"
    }
  ],
  "statistics": {
    "total_shots": 24,
    "avg_shot_duration": 5.2,
    "confidence_scores": [0.85, 0.92, ...]
  }
}
```

## 📦 批量处理功能

### 使用流程

1. **选择输入目录**
   - 包含多个视频文件的文件夹
   - 支持递归扫描子目录

2. **设置过滤条件**
   - **文件大小**: 最小/最大文件大小限制
   - **文件格式**: 指定处理的视频格式
   - **时长范围**: 视频时长过滤条件

3. **扫描文件**
   - 点击"扫描文件"查看待处理文件列表
   - 预览文件信息和统计数据

4. **配置处理参数**
   - 选择检测算法和参数
   - 设置并行处理线程数
   - 配置输出选项

5. **开始批量处理**
   - 实时监控处理进度
   - 查看成功/失败统计
   - 生成批量处理报告

### 性能优化

#### 并行处理配置

```python
# 根据系统资源自动优化
batch_service.optimize_batch_parameters(
    file_count=100,
    avg_file_size_mb=50.0
)

# 手动配置
batch_service = BatchService(
    detector=detector,
    max_workers=4,        # 最大工作线程数
    chunk_size=2          # 每次处理的文件数
)
```

#### 内存管理

- **大文件处理**: 自动调整线程数避免内存溢出
- **缓存策略**: 智能缓存减少重复计算
- **资源监控**: 实时监控CPU和内存使用

### 批量报告

处理完成后生成详细报告：

- **JSON报告**: 完整的处理结果数据
- **CSV摘要**: 便于Excel分析的表格
- **统计信息**: 成功率、处理时间等统计
- **错误日志**: 失败文件的详细错误信息

## 🔍 视频分析功能

### 分析类型

#### 基础信息分析
- 视频时长、分辨率、帧率
- 文件大小、编码格式
- 基本元数据信息

#### 质量分析
- **亮度分析**: 平均亮度、亮度分布
- **对比度分析**: 对比度统计和变化
- **清晰度分析**: 基于拉普拉斯算子的清晰度评估
- **噪声检测**: 视频噪声水平评估

#### 内容分析
- **运动检测**: 场景运动强度分析
- **颜色分析**: 主要颜色提取和分布
- **复杂度分析**: 场景复杂度评估
- **镜头统计**: 镜头时长分布和变化

#### 高级分析（实验性）
- **对象检测**: 识别视频中的物体
- **场景分类**: 自动场景类型识别
- **文本检测**: 视频中的文字识别

### 分析报告

分析完成后生成综合报告：

```json
{
  "video_metrics": {
    "duration": 120.5,
    "resolution": [1920, 1080],
    "fps": 30.0,
    "quality_score": 0.85
  },
  "quality_analysis": {
    "avg_brightness": 128.5,
    "avg_contrast": 45.2,
    "sharpness_score": 0.78
  },
  "content_analysis": {
    "motion_intensity": 0.65,
    "scene_complexity": 0.42,
    "dominant_colors": [[255, 0, 0], [0, 255, 0]]
  },
  "recommendations": [
    "视频亮度适中，质量良好",
    "建议增加镜头切换以提升观看体验"
  ]
}
```

## 📝 剪映草稿功能

### 功能概述

自动生成剪映（JianYing）项目文件，支持：

- **草稿项目创建**: 基于检测结果创建剪映项目
- **素材管理**: 自动导入视频素材
- **时间轴生成**: 根据镜头边界生成时间轴
- **效果应用**: 自动添加转场和效果

### 使用方法

1. **完成镜头检测**
   - 先使用视频分镜功能检测镜头边界

2. **配置剪映参数**
   - 设置项目名称和保存位置
   - 选择转场效果和时长
   - 配置输出分辨率和质量

3. **生成草稿项目**
   - 自动创建剪映项目文件
   - 生成必要的配置文件
   - 导入视频素材

4. **在剪映中打开**
   - 使用剪映打开生成的项目文件
   - 进行进一步编辑和调整

### 项目结构

```
project_name/
├── draft_content.json      # 主要内容配置
├── draft_meta_info.json    # 元数据信息
├── draft_virtual_store.json # 虚拟存储配置
└── materials/              # 素材文件夹
    └── videos/             # 视频素材
```

## 🔧 实用工具功能

### 系统信息

- **硬件信息**: CPU、内存、磁盘使用情况
- **软件环境**: Python版本、依赖包信息
- **性能监控**: 实时系统资源监控

### 缓存管理

- **缓存状态**: 查看缓存使用情况
- **缓存清理**: 清空所有缓存文件
- **缓存优化**: 自动优化缓存策略

### 配置管理

- **配置编辑**: 直接编辑配置文件
- **配置备份**: 创建配置文件备份
- **配置恢复**: 从备份恢复配置
- **配置重置**: 重置为默认设置

### 维护工具

- **系统测试**: 运行完整的功能测试
- **依赖检查**: 检查必需的依赖包
- **诊断报告**: 生成系统诊断报告
- **日志管理**: 查看和管理日志文件

## ⚙️ 配置说明

### 配置文件位置

- **主配置**: `config_v2.yaml`
- **用户配置**: `~/.shot_detection/config.yaml`
- **插件配置**: `plugins/configs/`

### 主要配置项

```yaml
# 应用配置
app:
  name: "Shot Detection"
  version: "2.0.0"
  log_level: "INFO"
  enable_cache: true

# 检测配置
detection:
  default_detector: "multi_detector"
  frame_difference:
    threshold: 0.3
  histogram:
    threshold: 0.5
    bins: 256

# 处理配置
processing:
  output:
    format: "mp4"
    quality: "high"
  segmentation:
    min_segment_duration: 1.0
    max_segment_duration: 300.0

# GUI配置
gui:
  theme: "default"
  font_size: 10
  remember_window_size: true
```

### 环境变量

```bash
# 设置日志级别
export SHOT_DETECTION_LOG_LEVEL=DEBUG

# 设置配置文件路径
export SHOT_DETECTION_CONFIG=/path/to/config.yaml

# 设置缓存目录
export SHOT_DETECTION_CACHE_DIR=/path/to/cache
```

## 🔌 插件系统

### 插件开发

创建自定义插件：

```python
from core.plugins import BasePlugin

class MyPlugin(BasePlugin):
    def __init__(self, name: str, version: str = "1.0.0"):
        super().__init__(name, version)
    
    def initialize(self) -> bool:
        # 插件初始化逻辑
        return True
    
    def cleanup(self):
        # 清理资源
        pass
    
    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": "My custom plugin"
        }
```

### 插件管理

```python
from core.plugins import PluginManager

# 创建插件管理器
plugin_manager = PluginManager()

# 发现插件
plugins = plugin_manager.discover_plugins()

# 加载插件
plugin_manager.load_plugin("my_plugin")

# 启用插件
plugin_manager.enable_plugin("my_plugin")
```

## 🚨 故障排除

### 常见问题

#### 1. 视频文件无法打开
**问题**: 提示"无法打开视频文件"
**解决方案**:
- 检查文件路径是否正确
- 确认文件格式是否支持
- 检查文件是否损坏
- 安装必要的编解码器

#### 2. 检测结果不准确
**问题**: 镜头边界检测不准确
**解决方案**:
- 调整检测阈值参数
- 尝试不同的检测算法
- 检查视频质量和内容特点
- 使用多算法融合提高精度

#### 3. 批量处理内存不足
**问题**: 处理大量文件时内存溢出
**解决方案**:
- 减少并行处理线程数
- 启用智能缓存管理
- 分批处理大文件
- 增加系统内存

#### 4. GUI界面无响应
**问题**: 界面卡死或无响应
**解决方案**:
- 检查后台处理任务
- 重启应用程序
- 检查系统资源使用
- 查看错误日志

### 日志分析

查看日志文件获取详细错误信息：

```bash
# 查看最新日志
tail -f logs/shot_detection.log

# 搜索错误信息
grep "ERROR" logs/shot_detection.log

# 查看特定时间的日志
grep "2024-01-01" logs/shot_detection.log
```

### 性能优化

#### 系统优化
- 关闭不必要的后台程序
- 确保足够的可用内存
- 使用SSD存储提升I/O性能
- 定期清理临时文件

#### 应用优化
- 启用智能缓存
- 调整并行处理参数
- 使用合适的检测算法
- 定期清理缓存文件

## 📞 技术支持

### 获取帮助

- **用户手册**: 查看完整的使用说明
- **在线文档**: 访问最新的技术文档
- **示例代码**: 参考示例和最佳实践
- **社区论坛**: 与其他用户交流经验

### 报告问题

提交问题时请包含：

1. **系统信息**: 操作系统、Python版本
2. **错误描述**: 详细的问题描述
3. **重现步骤**: 问题重现的具体步骤
4. **错误日志**: 相关的错误日志信息
5. **配置文件**: 当前的配置设置

### 版本更新

- **自动检查**: 应用会自动检查新版本
- **手动更新**: 从官方网站下载最新版本
- **更新日志**: 查看版本更新内容
- **兼容性**: 确认新版本兼容性

---

**🎉 感谢使用 Shot Detection v2.0！**

如有任何问题或建议，欢迎联系我们。祝您使用愉快！
