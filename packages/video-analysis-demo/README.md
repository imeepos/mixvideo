# 🎬 Video Analysis Demo

这是一个演示如何使用 `@mixvideo/video-analyzer` 库进行智能视频分析的示例项目。

## ✨ 功能特性

- 🎭 **场景检测** - 自动识别视频中的不同场景和转换点
- 🔍 **物体识别** - 检测和定位视频中的物体和人物
- 📝 **内容总结** - 生成智能的视频内容摘要
- ✨ **高光提取** - 自动识别视频中的精彩时刻
- 🔄 **视频对比** - 分析两个视频的相似性和差异
- 📦 **批量处理** - 支持同时处理多个视频文件

## 🚀 快速开始

### 1. 环境配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置您的 Gemini API Key
# GEMINI_API_KEY=your_api_key_here
```

### 2. 安装依赖

```bash
npm install
```

### 3. 运行测试

```bash
# 测试库组件是否正常工作
npm run test
```

### 4. 开始分析

```bash
# 启动交互式分析程序
npm run analyze

# 或者启动主程序
npm run dev
```

## 📖 使用说明

### 基础视频分析

```typescript
import { VideoAnalyzer } from '@mixvideo/video-analyzer';

const analyzer = new VideoAnalyzer({
  apiKey: 'your-gemini-api-key'
});

const result = await analyzer.analyzeVideo(videoFile, {
  enableSceneDetection: true,
  enableObjectDetection: true,
  enableSummarization: true,
  language: 'zh-CN'
});

console.log('分析结果:', result);
```

### 高光时刻提取

```typescript
const highlights = await analyzer.extractHighlights(videoFile, {
  language: 'zh-CN'
});

highlights.forEach(highlight => {
  console.log(`${highlight.type}: ${highlight.description}`);
  console.log(`时间: ${highlight.startTime}s - ${highlight.endTime}s`);
});
```

### 视频对比

```typescript
const comparison = await analyzer.compareVideos(video1, video2, {
  language: 'zh-CN'
});

console.log(`相似度: ${comparison.similarity * 100}%`);
console.log(`分析: ${comparison.analysis}`);
```

## 🛠️ 可用脚本

| 脚本 | 描述 |
|------|------|
| `npm run dev` | 启动交互式演示程序 |
| `npm run test` | 运行库组件测试 |
| `npm run analyze` | 开始视频分析 |
| `npm run build` | 构建 TypeScript 项目 |
| `npm start` | 运行构建后的程序 |

## 📁 项目结构

```
src/
├── index.ts      # 主入口程序
├── analyze.ts    # 视频分析功能
├── test.ts       # 库组件测试
├── config.ts     # 配置管理
└── utils.ts      # 工具函数
```

## 🔧 配置选项

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `GEMINI_API_KEY` | Gemini API 密钥 | 必需 |
| `GEMINI_MODEL` | 使用的模型 | `gemini-2.0-flash-exp` |
| `MAX_RETRIES` | 最大重试次数 | `3` |
| `TIMEOUT` | 请求超时时间 | `30000` |

### 分析选项

```typescript
const options = {
  enableSceneDetection: true,    // 启用场景检测
  enableObjectDetection: true,   // 启用物体识别
  enableSummarization: true,     // 启用内容总结
  frameSamplingInterval: 2,      // 帧采样间隔(秒)
  maxFrames: 30,                 // 最大分析帧数
  quality: 'medium',             // 分析质量
  language: 'zh-CN'              // 输出语言
};
```

## 🎯 示例场景

### 1. 教育视频分析
- 自动生成课程章节
- 识别关键知识点
- 提取重要概念

### 2. 营销视频优化
- 找出最吸引人的片段
- 分析用户关注点
- 优化内容结构

### 3. 内容审核
- 检测不当内容
- 分类视频类型
- 评估内容质量

## 🔗 相关链接

- [Video Analyzer 库文档](../video-analyzer/README.md)
- [详细使用指南](../video-analyzer/USAGE.md)
- [API 类型定义](../video-analyzer/src/types/index.ts)
- [Gemini API 文档](https://ai.google.dev/docs)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
