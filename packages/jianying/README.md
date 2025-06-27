# @mixvideo/jianying

剪映草稿文件工具包 - 提供剪映（CapCut）草稿文件的解析、分析和生成功能。

## 🎯 功能特性

### 📖 解析功能
- **📋 项目信息**: 提取项目ID、时长、帧率、画布尺寸等基本信息
- **🎥 视频素材**: 解析所有视频素材的详细信息（文件路径、分辨率、时长等）
- **🎵 音频素材**: 提取音频素材信息（类型、时长、AI特性等）
- **🛤️ 轨道分析**: 详细分析视频轨道和片段信息
- **📊 统计数据**: 提供项目的统计信息和文件使用情况

### 🔍 增强分析
- **🧮 复杂度分析**: 评估项目编辑复杂度
- **⏱️ 时间轴分析**: 分析时间轴结构和片段分布
- **📁 素材使用**: 统计素材使用情况和重复使用
- **🎛️ 编辑特性**: 识别使用的编辑功能和效果
- **💡 智能建议**: 提供优化建议和最佳实践

### 🚀 生成功能
- **📁 目录扫描**: 自动扫描指定目录的所有视频和音频文件
- **🎬 草稿生成**: 根据媒体文件自动生成完整的剪映草稿文件
- **🎛️ 参数配置**: 支持自定义画布尺寸、帧率、项目名称等
- **📹 视频信息**: 集成 ffprobe 获取真实的视频信息（分辨率、时长等）
- **🔄 格式兼容**: 生成的文件完全兼容剪映格式，可直接导入使用

## 📦 安装

```bash
npm install @mixvideo/jianying
```

## 🚀 使用方法

### 基本解析

```typescript
import { parseJianyingDraft, formatVideoInfo } from '@mixvideo/jianying';

// 解析草稿文件
const videoInfo = parseJianyingDraft('./draft_content.json');

// 输出格式化信息
formatVideoInfo(videoInfo);

// 访问解析结果
console.log('项目时长:', videoInfo.projectDurationSeconds, '秒');
console.log('视频素材数量:', videoInfo.videoClips.length);
console.log('音频素材数量:', videoInfo.audioClips.length);
```

### 增强分析

```typescript
import { analyzeJianyingProject, analyzeJianyingProjectFromData } from '@mixvideo/jianying';

// 从文件路径分析
const analysis = analyzeJianyingProject('./draft_content.json');

// 从已解析的数据分析
const videoInfo = parseJianyingDraft('./draft_content.json');
const analysis2 = analyzeJianyingProjectFromData(videoInfo);

// 访问分析结果
console.log('复杂度评分:', analysis.analysis.complexity.score);
console.log('复杂度等级:', analysis.analysis.complexity.level);
console.log('建议:', analysis.recommendations);
```

### 生成草稿文件

```typescript
import { generateDraft, scanDirectory } from '@mixvideo/jianying';

// 扫描目录获取媒体文件
const files = scanDirectory('./videos');

// 生成草稿文件
const draft = generateDraft(files, {
  canvasWidth: 1920,
  canvasHeight: 1080,
  fps: 60,
  projectName: '我的项目',
  useFFProbe: true // 使用 ffprobe 获取真实视频信息
});

// 保存草稿文件
import * as fs from 'fs';
fs.writeFileSync('./generated_project.json', JSON.stringify(draft, null, 2));
```

### 工具函数

```typescript
import { JianyingUtils, JIANYING_CONSTANTS } from '@mixvideo/jianying';

// 时间转换
const seconds = JianyingUtils.microsecondsToSeconds(1000000); // 1秒
const microseconds = JianyingUtils.secondsToMicroseconds(10); // 10000000微秒

// 宽高比计算
const ratio = JianyingUtils.calculateAspectRatio(1920, 1080); // "16:9"

// 文件类型检查
const isVideo = JianyingUtils.isVideoFile('video.mp4'); // true
const isAudio = JianyingUtils.isAudioFile('audio.mp3'); // true

// 常量使用
console.log('默认帧率:', JIANYING_CONSTANTS.DEFAULT_FPS); // 30
console.log('支持的视频格式:', JianyingUtils.VIDEO_EXTENSIONS);
```

## 📋 API 参考

### 类型定义

```typescript
interface VideoInfo {
  projectId: string;
  projectDuration: number;
  projectDurationSeconds: number;
  fps: number;
  canvasSize: { width: number; height: number; ratio: string };
  videoClips: VideoClip[];
  audioClips: AudioClip[];
  tracks: Track[];
  appInfo: AppInfo;
  statistics: Statistics;
}

interface EnhancedAnalysis {
  basicInfo: VideoInfo;
  analysis: {
    complexity: ComplexityAnalysis;
    timeline: TimelineAnalysis;
    materials: MaterialUsage;
    editing: EditingFeatures;
  };
  recommendations: Recommendation[];
}
```

### 主要函数

- `parseJianyingDraft(filePath: string): VideoInfo` - 解析草稿文件
- `analyzeJianyingProject(filePath: string): EnhancedAnalysis` - 增强分析
- `generateDraft(files: VideoFileInfo[], options: GenerateOptions): GeneratedDraft` - 生成草稿
- `scanDirectory(dirPath: string): VideoFileInfo[]` - 扫描目录

## 🔧 开发

```bash
# 克隆仓库
git clone https://github.com/mixvideo/mixvideo.git
cd mixvideo/packages/jianying

# 安装依赖
npm install

# 构建
npm run build

# 测试
npm run test

# 开发模式
npm run dev
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📚 相关链接

- [剪映官网](https://www.capcut.com/)
- [项目仓库](https://github.com/mixvideo/mixvideo)
- [问题反馈](https://github.com/mixvideo/mixvideo/issues)
