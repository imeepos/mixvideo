# 🗂️ 智能视频分段自动归类功能

## 📋 功能概述

参考 `video-analyzer` 项目的实现，为 `shot_detection` 项目新增了智能视频分段自动归类功能。该功能可以根据视频分段的特征（时长、质量、内容等）自动将分段归类到不同的文件夹中，提高素材管理效率。

## 🎯 核心特性

### **1. 多种归类模式**
- **按时长分类** (`duration`): 短片段(≤5s) / 中等片段(5-30s) / 长片段(>30s)
- **按质量分类** (`quality`): 高质量 / 中等质量 / 低质量（基于检测置信度）
- **按内容分类** (`content`): 动作场景 / 对话场景 / 风景场景 / 特写场景等
- **自定义规则** (`custom`): 用户自定义的分类规则

### **2. 灵活的文件操作**
- **复制模式**: 保留原文件，创建分类副本
- **移动模式**: 移动原文件到分类目录
- **冲突处理**: 跳过 / 覆盖 / 重命名
- **备份功能**: 可选的文件备份机制

### **3. 智能命名策略**
- **保持原名**: 保留原始文件名
- **智能命名**: 添加分类和时长信息
- **内容命名**: 基于内容特征命名
- **时间戳命名**: 使用时间戳避免冲突

### **4. 置信度控制**
- 设置最小置信度阈值
- 只有高置信度的分段才会被归类
- 避免错误分类的风险

## 🏗️ 架构设计

### **核心模块**

```
classification_config.py     # 归类配置管理
├── ClassificationConfig     # 配置数据类
├── ClassificationManager    # 归类管理器
└── FolderMatchConfig       # 文件夹匹配配置

file_organizer.py           # 文件组织器
├── FileOrganizer           # 文件组织核心类
├── FileOperationResult     # 操作结果数据类
└── 文件操作和冲突处理逻辑

video_segmentation.py       # 集成归类功能
├── 修改主处理函数支持归类参数
└── 在分段创建后执行归类操作

gui_app.py                  # GUI界面集成
├── 添加归类功能开关
├── 归类参数配置界面
└── 归类状态显示
```

### **配置文件**
```
classification_config.yaml  # YAML配置文件
├── 归类功能开关和模式
├── 文件操作配置
├── 分类阈值设置
└── 自定义规则定义
```

## 🚀 使用方法

### **1. 命令行使用**

```bash
# 启用按时长归类
python video_segmentation.py input.mp4 --output output_dir --classify --organize duration

# 启用按质量归类，移动文件
python video_segmentation.py input.mp4 --output output_dir --classify --organize quality --move-files

# 设置最小置信度
python video_segmentation.py input.mp4 --output output_dir --classify --min-confidence 0.7
```

### **2. GUI界面使用**

1. **启用归类功能**
   - 勾选 "启用自动归类功能" 复选框
   - 选择组织方式（时长/质量/内容）

2. **配置归类选项**
   - 文件操作：选择复制或移动文件
   - 最小置信度：调整置信度滑块
   - 命名模式：选择文件命名方式

3. **开始处理**
   - 点击 "开始处理" 按钮
   - 系统会自动进行分段和归类

### **3. 编程接口使用**

```python
from classification_config import ClassificationManager
from file_organizer import FileOrganizer
from video_segmentation import process_video_segmentation

# 创建归类管理器
manager = ClassificationManager()
manager.update_config(
    enable_classification=True,
    classification_mode="duration",
    move_files=False,
    min_confidence_for_move=0.6
)

# 处理视频并归类
success = process_video_segmentation(
    video_path="input.mp4",
    output_dir="output",
    organize_by="duration",
    quality="medium",
    enable_classification=True,
    classification_config={
        'move_files': False,
        'min_confidence_for_move': 0.6,
        'naming_mode': 'smart'
    }
)
```

## ⚙️ 配置选项

### **归类模式配置**

```yaml
classification:
  enable_classification: true
  classification_mode: "duration"  # duration, quality, content, custom
  min_confidence_for_move: 0.6
  
  # 时长分类阈值
  duration_thresholds:
    short: [0.0, 5.0]      # 0-5秒
    medium: [5.0, 30.0]    # 5-30秒
    long: [30.0, inf]      # 30秒以上
  
  # 质量分类阈值
  quality_thresholds:
    low: [0.0, 0.4]        # 低质量
    medium: [0.4, 0.7]     # 中等质量
    high: [0.7, 1.0]       # 高质量
```

### **文件操作配置**

```yaml
file_operations:
  move_files: false              # false=复制，true=移动
  create_directories: true       # 自动创建目录
  conflict_resolution: "rename"  # skip, overwrite, rename
  create_backup: false           # 是否创建备份
  naming_mode: "preserve-original"  # 命名模式
```

## 📊 输出结构

### **按时长归类示例**
```
output_dir/
├── short/                    # 短片段 (≤5秒)
│   ├── video_segment_001.mp4
│   ├── video_segment_005.mp4
│   └── video_segment_012.mp4
├── medium/                   # 中等片段 (5-30秒)
│   ├── video_segment_002.mp4
│   ├── video_segment_007.mp4
│   └── video_segment_015.mp4
├── long/                     # 长片段 (>30秒)
│   ├── video_segment_003.mp4
│   └── video_segment_018.mp4
└── video_segments.csv        # 分段信息文件
```

### **智能命名示例**
```
short/
├── video_segment_001_short_d3.2s_c0.85.mp4
├── video_segment_005_short_d4.1s_c0.92.mp4
└── video_segment_012_short_d2.8s_c0.78.mp4
```

## 🧪 测试和验证

### **运行测试脚本**
```bash
# 运行完整测试
python test_classification.py

# 测试特定功能
python -c "from test_classification import test_classification_config; test_classification_config()"
```

### **测试覆盖范围**
- ✅ 归类配置管理
- ✅ 文件组织器功能
- ✅ 配置文件加载/保存
- ✅ 视频处理集成
- ✅ GUI界面集成

## 📈 性能特性

### **处理效率**
- **并发处理**: 支持多线程文件操作
- **智能缓存**: 避免重复计算
- **增量处理**: 只处理新增分段

### **资源使用**
- **内存优化**: 流式处理大文件
- **磁盘优化**: 最小化磁盘I/O
- **CPU优化**: 多核并行处理

## 🔧 高级功能

### **自定义分类规则**
```python
# 添加自定义规则
custom_rules = [
    {
        'name': 'very_short',
        'conditions': {'duration_max': 2.0},
        'category': 'very_short'
    },
    {
        'name': 'high_confidence_long',
        'conditions': {
            'duration_min': 20.0,
            'confidence_min': 0.8
        },
        'category': 'premium'
    }
]

manager.config.custom_rules = custom_rules
```

### **文件夹匹配**
```python
# 基于现有文件夹结构的智能匹配
folder_config = FolderMatchConfig(
    base_directory="/path/to/existing/structure",
    max_depth=3,
    min_confidence=0.3
)
```

## 🎯 最佳实践

### **1. 归类策略选择**
- **按时长归类**: 适合基于时长的素材管理
- **按质量归类**: 适合质量控制和筛选
- **按内容归类**: 适合主题化素材组织

### **2. 置信度设置**
- **保守策略**: 设置较高置信度 (0.7-0.9)
- **平衡策略**: 使用默认置信度 (0.6)
- **激进策略**: 设置较低置信度 (0.3-0.5)

### **3. 文件操作选择**
- **复制模式**: 安全，保留原文件
- **移动模式**: 节省空间，整理文件
- **备份模式**: 最安全，但占用更多空间

## 🔮 未来扩展

### **计划功能**
- **AI内容分析**: 基于深度学习的内容识别
- **语义分类**: 基于视频内容的语义理解
- **批量处理**: 支持多视频批量归类
- **云端集成**: 支持云存储服务

### **集成可能**
- **与video-analyzer深度集成**: 共享分析结果
- **与编辑软件集成**: 直接导入到编辑时间线
- **与素材库集成**: 自动标签和索引

---

© 2024 Smart Shot Detection System - 自动归类功能文档
