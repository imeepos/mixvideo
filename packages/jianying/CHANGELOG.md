# Changelog

## [1.0.0] - 2025-06-27

### 🎉 Initial Release

完成了 `@mixvideo/jianying` 包的首次发布，提供完整的剪映草稿文件处理功能。

### ✨ Features

#### 📋 解析功能 (Parse)
- **parseJianyingDraft()** - 解析剪映草稿文件 (draft_content.json)
- **formatVideoInfo()** - 格式化输出视频信息
- **exportToJson()** - 导出解析结果到 JSON 文件
- 支持完整的剪映数据结构解析，包括：
  - 项目基本信息（ID、时长、FPS、画布尺寸）
  - 视频素材信息（路径、尺寸、时长、裁剪信息）
  - 音频素材信息（路径、时长、类型）
  - 轨道和片段信息（变换、特效、时间轴）
  - 统计信息（素材数量、片段数量等）

#### 🔍 增强分析功能 (Enhanced Analysis)
- **analyzeJianyingProjectFromData()** - 基于解析数据进行增强分析
- **performEnhancedAnalysis()** - 直接从文件进行增强分析
- **formatEnhancedAnalysis()** - 格式化输出分析结果
- 分析维度包括：
  - **复杂度评估** - 基于轨道数、片段数、素材数等因素
  - **时间轴分析** - 片段统计、平均时长、最短/最长片段
  - **素材使用分析** - 文件使用频率、重复使用统计
  - **编辑特性分析** - 变换操作、缩放、旋转、位置变化
  - **智能建议** - 基于分析结果提供优化建议

#### 🚀 生成功能 (Generation)
- **generateDraft()** - 从媒体文件生成剪映草稿
- **scanDirectory()** - 扫描目录中的媒体文件
- **generateVideoClip()** - 生成视频素材对象
- **generateAudioClip()** - 生成音频素材对象
- 支持功能：
  - 自动扫描视频和音频文件
  - 可选的 FFProbe 集成获取真实媒体信息
  - 自动生成轨道和片段
  - 可配置的画布尺寸和帧率
  - UUID 生成确保唯一性

#### 🔧 工具函数 (Utilities)
- **JianyingUtils** 对象包含：
  - `microsecondsToSeconds()` / `secondsToMicroseconds()` - 时间单位转换
  - `calculateAspectRatio()` - 宽高比计算
  - `isVideoFile()` / `isAudioFile()` / `isMediaFile()` - 文件类型检查
  - `VIDEO_EXTENSIONS` / `AUDIO_EXTENSIONS` - 支持的文件格式常量
- **JIANYING_CONSTANTS** 对象包含：
  - 默认 FPS、画布尺寸等常量
  - 平台信息和版本信息

### 📦 Package Structure

```
packages/jianying/
├── src/
│   ├── index.ts              # 主入口文件，导出所有功能
│   ├── parse-draft.ts        # 解析功能
│   ├── enhanced-parser.ts    # 增强分析功能
│   ├── generate-draft.ts     # 生成功能
│   └── test-parser.ts        # 测试文件
├── examples/
│   └── basic-usage.ts        # 使用示例
├── dist/                     # 构建输出
│   ├── index.js              # CommonJS 版本
│   ├── index.mjs             # ES Module 版本
│   ├── index.d.ts            # TypeScript 类型定义
│   └── ...
├── package.json
├── tsconfig.json
├── tsup.config.ts
├── README.md
└── CHANGELOG.md
```

### 🛠️ Build & Development

- **TypeScript** - 完整的类型支持
- **tsup** - 现代化的构建工具，支持 CommonJS 和 ES Module
- **双格式输出** - 同时支持 CJS 和 ESM
- **类型定义** - 完整的 TypeScript 类型定义文件

### 📚 Scripts

```bash
npm run build     # 构建包
npm run dev       # 开发模式（监听文件变化）
npm run test      # 运行测试
npm run example   # 运行使用示例
npm run parse     # 运行解析功能
npm run analyze   # 运行分析功能
npm run generate  # 运行生成功能
```

### 🎯 Usage Examples

```typescript
import {
  parseJianyingDraft,
  analyzeJianyingProjectFromData,
  generateDraft,
  scanDirectory,
  JianyingUtils,
  JIANYING_CONSTANTS
} from '@mixvideo/jianying';

// 解析现有草稿
const videoInfo = parseJianyingDraft('draft_content.json');

// 增强分析
const analysis = analyzeJianyingProjectFromData(videoInfo);

// 从媒体文件生成草稿
const files = scanDirectory('./media');
const draft = generateDraft(files, {
  canvasWidth: 1920,
  canvasHeight: 1080,
  fps: 30,
  projectName: '我的项目'
});

// 使用工具函数
const seconds = JianyingUtils.microsecondsToSeconds(5000000);
const ratio = JianyingUtils.calculateAspectRatio(1920, 1080);
```

### 🔧 Technical Details

- **Node.js** >= 16.0.0
- **TypeScript** 5.0+
- **无外部运行时依赖** (除了可选的 uuid 包)
- **跨平台支持** - Windows, macOS, Linux
- **内置 UUID 生成** - 不依赖外部 UUID 库

### 🎉 What's Next

这个 1.0.0 版本提供了完整的剪映草稿文件处理功能，包括解析、分析和生成。未来版本可能会添加：

- 更多的分析维度和建议类型
- 支持更多的媒体格式
- 性能优化和错误处理改进
- 更多的工具函数和常量

---

**完整功能测试通过** ✅
- 解析功能测试通过
- 增强分析功能测试通过  
- 生成功能测试通过
- 工具函数测试通过
- 构建测试通过
- 类型定义测试通过
