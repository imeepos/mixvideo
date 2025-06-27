# 剪映草稿文件工具包

一个强大的 TypeScript 工具包，用于剪映（CapCut）草稿文件的解析、分析和生成。支持从现有草稿文件提取详细信息，也可以从视频文件自动生成草稿文件。

## 🎯 功能特性

### 📖 解析功能
- **📋 项目信息**: 提取项目ID、时长、帧率、画布尺寸等基本信息
- **🎥 视频素材**: 解析所有视频素材的详细信息（文件路径、分辨率、时长等）
- **🎵 音频素材**: 提取音频素材信息（类型、时长、AI特性等）
- **🛤️ 轨道分析**: 详细分析视频轨道和片段信息
- **📊 统计数据**: 提供项目的统计信息和文件使用情况
- **💾 数据导出**: 支持导出为结构化的 JSON 文件
- **🔍 智能解析**: 自动处理各种剪映项目格式

### 🚀 生成功能
- **📁 目录扫描**: 自动扫描指定目录的所有视频和音频文件
- **🎬 草稿生成**: 根据媒体文件自动生成完整的剪映草稿文件
- **🎛️ 参数配置**: 支持自定义画布尺寸、帧率、项目名称等
- **📹 视频信息**: 集成 ffprobe 获取真实的视频信息（分辨率、时长等）
- **🔄 格式兼容**: 生成的文件完全兼容剪映格式，可直接导入使用

## 📦 安装

```bash
# 安装依赖
npm install

# 或者全局安装 TypeScript 和 ts-node
npm install -g typescript ts-node
```

## 🚀 使用方法

### 命令行使用

#### 📖 解析现有草稿文件

```bash
# 基本解析（输出到控制台）
npx ts-node parse-draft.ts ./draft_content.json

# 解析并导出到 JSON 文件
npx ts-node parse-draft.ts ./draft_content.json ./output.json

# 增强分析（包含复杂度分析、建议等）
npx ts-node enhanced-parser.ts ./draft_content.json ./enhanced_analysis.json

# 使用 npm 脚本
npm run parse ./draft_content.json
npm run analyze ./draft_content.json
npm run demo  # 运行完整演示
```

#### 🚀 生成新的草稿文件

```bash
# 基本生成（扫描目录并生成草稿文件）
npx ts-node generate-draft.ts ./videos

# 指定输出文件
npx ts-node generate-draft.ts ./videos ./my_project.json

# 自定义参数
npx ts-node generate-draft.ts ./videos ./project.json --width=1920 --height=1080 --fps=60 --name="我的项目"

# 使用 npm 脚本
npm run generate ./videos ./output.json
npm run demo-generate  # 运行生成演示
```

#### 🎛️ 生成器参数说明

- `<扫描目录>`: 要扫描的视频/音频文件目录（必需）
- `[输出文件路径]`: 生成的草稿文件路径（可选，默认: `./generated_draft_content.json`）
- `--width=<数字>`: 画布宽度（可选，默认: 1080）
- `--height=<数字>`: 画布高度（可选，默认: 1920）
- `--fps=<数字>`: 帧率（可选，默认: 30）
- `--name=<字符串>`: 项目名称（可选）

### 编程方式使用

```typescript
import { parseJianyingDraft, formatVideoInfo, exportToJson } from './parse-draft';

// 解析草稿文件
const videoInfo = parseJianyingDraft('./draft_content.json');

// 输出格式化信息
formatVideoInfo(videoInfo);

// 导出为 JSON
exportToJson(videoInfo, './output.json');
```

## 📊 输出信息

解析器会提取以下详细信息：

### 项目基本信息
- 项目ID和时长
- 帧率和画布尺寸
- 应用版本和平台信息

### 视频素材详情
- 文件名和路径
- 分辨率和宽高比
- 时长和音频信息
- 裁剪和缩放设置
- AI生成和版权标识

### 音频素材详情
- 音频文件信息
- 类型（原声、配音等）
- AI克隆和文本配音标识

### 轨道和片段信息
- 轨道类型和片段数量
- 时间轴位置和时长
- 变换信息（位置、缩放、旋转、透明度）
- 翻转和特效设置

### 统计信息
- 素材数量统计
- 独立文件列表
- 项目复杂度分析

## 📋 输出示例

```
🎬 剪映项目详细信息
============================================================

📋 项目基本信息:
  项目ID: 101E9A73-BF96-45a5-A8B5-D757DB9F7943
  总时长: 13.73秒 (13733333微秒)
  帧率: 30 FPS
  画布尺寸: 1080x1920 (9:16)

📱 应用信息:
  应用: lv v5.9.0
  平台: undefined (windows)
  设备ID: f9e35bee017c23bfd04e38159f79d170

📊 统计信息:
  视频素材: 11个
  音频素材: 1个
  轨道数量: 4个
  片段总数: 14个
  独立视频文件: 1个
  独立音频文件: 1个

🎥 视频素材详情:
  1. 飞书20250627-102843.mp4
     文件路径: C:/Users/15371/Desktop/飞书20250627-102843.mp4
     时长: 13.93秒
     分辨率: 720x960 (3:4)
     包含音频: 是
     裁剪比例: free (缩放: 1)
     AI生成: 否
     版权内容: 否
```

## 🔧 开发

```bash
# 运行测试
npm test

# 构建项目
npm run build

# 开发模式运行
npx ts-node parse-draft.ts
```

## 📁 文件结构

```
scripts/jianying/
├── parse-draft.ts          # 主解析器
├── enhanced-parser.ts      # 增强分析器
├── test-parser.ts          # 测试脚本
├── draft_content.json      # 示例草稿文件
├── parsed_video_info.json  # 基本解析结果
├── enhanced_analysis.json  # 增强分析结果
├── package.json           # 项目配置
└── README.md             # 说明文档
```

## 🔧 工具特性

### 基础解析器 (parse-draft.ts)
- ✅ 提取项目基本信息
- ✅ 解析视频和音频素材
- ✅ 分析轨道和片段结构
- ✅ 输出详细的控制台报告
- ✅ 导出结构化 JSON 数据

### 增强分析器 (enhanced-parser.ts)
- ✅ 项目复杂度评估
- ✅ 时间轴深度分析
- ✅ 素材使用情况统计
- ✅ 编辑特性识别
- ✅ 智能优化建议
- ✅ 可视化分析报告

## 🎯 支持的剪映版本

- ✅ 剪映 5.9.0+
- ✅ Windows/Mac/移动端版本
- ✅ 各种项目格式和复杂度

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [剪映官网](https://www.capcut.com/)
- [TypeScript 文档](https://www.typescriptlang.org/)
