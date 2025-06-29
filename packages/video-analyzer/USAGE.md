# 使用指南 - @mixvideo/video-analyzer

## 快速开始

### 1. 安装

```bash
npm install @mixvideo/video-analyzer
```

### 2. 获取 Gemini API Key

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建新的 API Key
3. 如需要，设置计费信息

### 3. 基础使用

```typescript
import { VideoAnalyzer } from '@mixvideo/video-analyzer';

// 初始化分析器
const analyzer = new VideoAnalyzer({
  apiKey: 'your-gemini-api-key'
});

// 分析视频文件
const result = await analyzer.analyzeVideo(
  videoFile,
  { type: 'gemini', model: 'gemini-2.5-flash' },
  {
    quality: 'high',
    language: 'zh-CN'
  }
);

console.log('分析结果:', result);
```

## 详细功能

### 视频分析

```typescript
const result = await analyzer.analyzeVideo(
  videoFile,
  { type: 'gemini', model: 'gemini-2.5-flash' },
  {
    // 分析质量
    quality: 'high',

    // 帧采样间隔（秒）
    frameSamplingInterval: 2,

    // 最大帧数
  maxFrames: 30,
  
  // 质量设置
  quality: 'medium', // 'low' | 'medium' | 'high'
  
  // 语言设置
  language: 'zh-CN'
});

// 处理结果
console.log('视频信息:', result.metadata);
console.log('场景数量:', result.scenes.length);
console.log('检测到的物体:', result.objects.length);
console.log('内容总结:', result.summary.description);
```

### 高光时刻提取

```typescript
const highlights = await analyzer.extractHighlights(videoFile, {
  language: 'zh-CN'
});

// 筛选适合社交媒体的高光
const socialHighlights = highlights.filter(h => 
  h.socialMediaReady && h.importance > 0.7
);

socialHighlights.forEach(highlight => {
  console.log(`${highlight.type}: ${highlight.description}`);
  console.log(`时间: ${highlight.startTime}s - ${highlight.endTime}s`);
  console.log(`重要性: ${highlight.importance * 100}%`);
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

### 批量处理

```typescript
const videos = [
  { input: video1File, id: 'video1' },
  { input: video2File, id: 'video2' },
  { input: 'https://example.com/video3.mp4', id: 'video3' }
];

const results = await analyzer.analyzeBatch(videos, {
  quality: 'medium',
  maxFrames: 20
}, (progress) => {
  console.log(`进度: ${progress.step} (${progress.progress}%)`);
});

// 处理批量结果
for (const [videoId, result] of results) {
  console.log(`视频 ${videoId}: ${result.summary.description}`);
}
```

## 工具函数

### 快速分析

```typescript
import { analyzeVideoQuick } from '@mixvideo/video-analyzer';

const result = await analyzeVideoQuick(videoFile, 'your-api-key', {
  quality: 'medium'
});
```

### 快速高光提取

```typescript
import { extractVideoHighlights } from '@mixvideo/video-analyzer';

const highlights = await extractVideoHighlights(videoFile, 'your-api-key');
```

### 快速视频对比

```typescript
import { compareVideos } from '@mixvideo/video-analyzer';

const comparison = await compareVideos(video1, video2, 'your-api-key');
```

## 自定义分析

### 使用自定义提示词

```typescript
const result = await analyzer.analyzeVideo(videoFile, {
  customPrompt: `
    请专门分析这个视频的以下方面：
    1. 营销潜力和商业价值
    2. 品牌安全性评估
    3. 观众参与度因素
    4. 推荐的社交媒体平台
    
    请为每个方面提供详细的见解和建议。
  `,
  language: 'zh-CN'
});
```

## 错误处理

```typescript
import { VideoAnalyzerError, ERROR_CODES } from '@mixvideo/video-analyzer';

try {
  const result = await analyzer.analyzeVideo(videoFile);
} catch (error) {
  if (error instanceof VideoAnalyzerError) {
    switch (error.code) {
      case ERROR_CODES.INVALID_API_KEY:
        console.error('API Key 无效');
        break;
      case ERROR_CODES.QUOTA_EXCEEDED:
        console.error('API 配额已用完');
        break;
      case ERROR_CODES.VIDEO_TOO_LARGE:
        console.error('视频文件过大');
        break;
      case ERROR_CODES.UNSUPPORTED_FORMAT:
        console.error('不支持的视频格式');
        break;
      default:
        console.error('分析失败:', error.message);
    }
  }
}
```

## 性能优化建议

### 1. 帧采样优化

```typescript
// 对于长视频，减少帧采样频率
const result = await analyzer.analyzeVideo(longVideo, {
  frameSamplingInterval: 5, // 每5秒采样一帧
  maxFrames: 20 // 限制最大帧数
});
```

### 2. 质量设置

```typescript
// 根据需求调整质量
const result = await analyzer.analyzeVideo(videoFile, {
  quality: 'low' // 快速分析，较低质量
});
```

### 3. 选择性分析

```typescript
// 调整分析质量以平衡速度和准确性
const result = await analyzer.analyzeVideo(
  videoFile,
  { type: 'gemini', model: 'gemini-2.5-flash' },
  {
    quality: 'medium', // 使用中等质量以提高速度
    maxFrames: 20      // 限制帧数以提高速度
  }
);
```

## 支持的视频格式

- MP4 (H.264/H.265)
- WebM (VP8/VP9)
- MOV (QuickTime)
- AVI
- MKV (Matroska)
- FLV (Flash Video)
- WMV (Windows Media)
- M4V (iTunes Video)

## 限制说明

- 最大文件大小: 500MB
- 最大视频时长: 1小时
- 最小分辨率: 240p
- API 调用频率限制: 根据 Google AI 配额

## 最佳实践

### 1. 视频预处理

```typescript
// 检查视频是否适合分析
const processor = new VideoProcessor();
const metadata = await processor.extractMetadata(videoFile);
const { ready, issues } = processor.isAnalysisReady(metadata);

if (!ready) {
  console.log('视频问题:', issues);
  return;
}
```

### 2. 进度跟踪

```typescript
const result = await analyzer.analyzeVideo(videoFile, {}, (progress) => {
  // 更新UI进度条
  updateProgressBar(progress.progress);
  console.log(progress.step);
});
```

### 3. 结果缓存

```typescript
// 缓存分析结果避免重复分析
const cacheKey = `analysis_${videoFile.name}_${videoFile.size}`;
let result = getFromCache(cacheKey);

if (!result) {
  result = await analyzer.analyzeVideo(videoFile);
  saveToCache(cacheKey, result);
}
```

## 常见问题

### Q: 如何提高分析准确性？
A: 使用更高的质量设置，增加帧采样频率，提供更详细的自定义提示词。

### Q: 分析速度太慢怎么办？
A: 减少帧采样频率，降低质量设置，禁用不需要的分析功能。

### Q: 支持实时视频分析吗？
A: 目前不支持实时分析，只支持已录制的视频文件。

### Q: 可以分析视频中的音频吗？
A: 目前主要分析视觉内容，音频分析功能正在开发中。

## 更多示例

查看 `examples/` 目录获取更多使用示例：
- `basic-usage.ts` - 基础功能演示
- `react-component.tsx` - React 组件集成示例
