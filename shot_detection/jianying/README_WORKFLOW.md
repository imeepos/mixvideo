# 🎬 抖音视频制作完整工作流程

这是一个自动化的抖音视频制作工作流程，可以智能地将视频素材分配到抖音项目模板中，生成多个视频项目。

## 📋 功能特性

- **🔍 资源扫描**: 自动扫描 `resources/` 目录下的所有视频、音频、图片文件
- **📊 项目管理**: 管理 `templates/` 目录下的抖音项目模板
- **🤖 智能分配**: 使用优化算法将视频素材智能分配到模板中
- **📤 批量输出**: 将生成的项目保存到 `outputs/` 目录

## 📁 目录结构

```
your_project/
├── resources/              # 视频素材目录
│   ├── 0630-交付素材1/
│   ├── 0630-交付素材2/
│   ├── 0630-换背景素材5/
│   └── ...
├── templates/              # 抖音项目模板目录
│   ├── 5个镜头/
│   │   ├── draft_content.json
│   │   ├── draft_meta_info.json
│   │   └── draft_virtual_store.json
│   ├── 6个镜头/
│   ├── 8个镜头/
│   └── ...
└── outputs/               # 输出目录 (自动创建)
    ├── 5个镜头_第1轮_1/
    ├── 6个镜头_第1轮_2/
    ├── allocation_report.json
    ├── media_inventory.json
    └── ...
```

## 🚀 快速开始

### 方法1: 使用启动脚本 (推荐)

**Windows 用户:**
```bash
# 双击运行或在命令行中执行
run_douyin_workflow.bat
```

**Linux/Mac 用户:**
```bash
# 在终端中执行
./run_douyin_workflow.sh
```

### 方法2: 使用 Python 命令

```bash
# 预览模式 (只分析，不生成文件)
python douyin_workflow.py --preview

# 完整运行
python douyin_workflow.py

# 指定工作目录
python douyin_workflow.py -d /path/to/your/project

# 显示详细日志
python douyin_workflow.py -v
```

### 方法3: 使用原始工作流程

```bash
# 运行完整工作流程
python run_allocation.py

# 指定工作目录
python run_allocation.py -d /path/to/your/project
```

## 📊 工作流程步骤

### 1️⃣ 扫描资源 (media_scanner.py)
- 递归扫描 `resources/` 目录
- 识别视频、音频、图片文件
- 提取文件元数据 (时长、分辨率等)
- 生成资源清单报告

### 2️⃣ 管理模板 (jianying_project_manager.py)
- 扫描 `templates/` 目录下的抖音项目
- 验证项目文件完整性
- 分析每个模板需要的视频位置数量

### 3️⃣ 智能分配 (video_allocation_algorithm.py)
- 使用优化算法分配视频到模板
- 确保全局唯一性 (每个视频只用一次)
- 避免连续重复放置
- 支持1-2个位置占用策略
- 最大化视频生成数量

### 4️⃣ 输出结果
- 复制模板到 `outputs/` 目录
- 更新 JSON 文件中的视频路径
- 生成分配报告和统计信息

## 📈 输出文件说明

### 生成的项目目录
每个生成的项目包含完整的抖音项目文件:
- `draft_content.json` - 项目内容配置
- `draft_meta_info.json` - 媒体元数据
- `draft_virtual_store.json` - 虚拟存储配置

### 报告文件
- `media_inventory.json` - 资源清单 (JSON格式)
- `media_inventory.html` - 资源清单 (HTML格式)
- `project_summary.json` - 项目模板摘要
- `allocation_report.json` - 视频分配报告
- `workflow_final_report.json` - 最终工作流程报告

## ⚙️ 配置选项

### 命令行参数

```bash
python douyin_workflow.py [选项]

选项:
  -d, --directory PATH    工作目录路径 (默认: 当前目录)
  --preview              预览模式，只分析不生成文件
  --formats FORMAT...    资源清单输出格式 (json, html, csv, markdown, excel)
  -v, --verbose          显示详细日志
  -h, --help            显示帮助信息
```

### 视频分配算法参数

算法会自动优化以下策略:
- **全局唯一性**: 每个视频文件只使用一次
- **位置分配**: 每个视频最多占用2个不连续位置
- **最小化使用**: 优先使用较少视频生成更多项目
- **智能匹配**: 根据模板需求智能分配视频数量

## 🔧 故障排除

### 常见问题

**1. 找不到 resources 或 templates 目录**
```
❌ 错误: 资源目录不存在: /path/to/resources
💡 解决: 确保在包含 resources 和 templates 文件夹的目录中运行脚本
```

**2. 模板文件无效**
```
❌ 错误: 缺少文件: draft_content.json
💡 解决: 确保每个模板目录包含完整的抖音项目文件
```

**3. 没有找到视频文件**
```
❌ 错误: 没有找到视频文件
💡 解决: 检查 resources 目录是否包含 .mp4, .avi, .mov 等视频文件
```

### 日志文件

工作流程会生成详细的日志文件:
- `douyin_workflow.log` - 完整的执行日志

## 📞 技术支持

如果遇到问题，请检查:
1. Python 版本 (需要 3.7+)
2. 必要的依赖包是否安装
3. 目录结构是否正确
4. 文件权限是否足够

## 🎯 最佳实践

1. **素材准备**: 将视频素材按类别整理到 resources 子目录中
2. **模板管理**: 确保模板项目文件完整且有效
3. **预览优先**: 首次使用建议先运行预览模式
4. **备份重要**: 重要的模板文件建议先备份
5. **批量处理**: 一次性准备多个素材可以提高效率
