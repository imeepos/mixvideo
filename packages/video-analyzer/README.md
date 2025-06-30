# @mixvideo/video-analyzer

🎯 **完整的视频分析和组织工作流程**

AI驱动的视频分析工具，实现完整的工作流程：**AI分析视频内容和质量 → 智能匹配文件夹 → 自动移动重命名文件**

## 🌟 核心功能

### 完整工作流程
1. **🔍 AI分析视频内容和质量** - 使用 Gemini/GPT-4 深度分析视频
2. **📁 智能匹配文件夹** - 根据内容自动推荐最合适的文件夹
3. **📂 自动移动和重命名** - 将视频移动到目标文件夹并智能重命名

### 核心特性
- 🎬 **多模态分析**: 支持 GPT-4 Vision (逐帧) 和 Gemini (整体视频分析)
- 🔍 **智能内容检测**: 场景检测、物体识别、内容总结
- 📊 **产品特征分析**: 专门针对产品视频的外观、材质、功能分析
- 📁 **智能文件夹匹配**: 基于内容自动匹配合适的文件夹
- 📂 **智能文件组织**: 自动移动、重命名、创建目录结构
- 📈 **全面报告**: 生成详细的分析和组织报告
- 🚀 **批量处理**: 高效处理整个目录的视频
- 🎯 **灵活配置**: 可自定义分析选项、命名策略、组织规则

## Installation

```bash
npm install @mixvideo/video-analyzer
```

## 🚀 快速开始

### 一键完成所有操作
```typescript
import { VideoAnalyzer } from '@mixvideo/video-analyzer';

// 初始化分析器
const analyzer = new VideoAnalyzer({
  workflow: {
    minConfidenceForMove: 0.7, // 置信度阈值
    fileOrganizerConfig: {
      moveFiles: true,        // 移动文件
      namingMode: 'smart',    // 智能命名
      createBackup: true      // 创建备份
    }
  }
});

// 🎯 一键处理：分析 + 匹配 + 组织
const result = await analyzer.processDirectory(
  '/path/to/source/videos',      // 源视频目录
  '/path/to/organized/videos',   // 目标组织目录
  { type: 'gemini', model: 'gemini-2.5-flash' },
  {
    minConfidenceForMove: 0.8,   // 高置信度要求
    fileOrganizerConfig: {
      namingMode: 'smart',
      createDirectories: true
    }
  },
  (progress) => {
    console.log(`[${progress.phase}] ${progress.step}: ${progress.progress}%`);
    console.log(`已处理: ${progress.processedVideos}/${progress.totalVideos}`);
  }
);

console.log(`成功组织 ${result.organizedVideos}/${result.totalVideos} 个视频`);
```

### 分步骤处理（精细控制）
```typescript
// 1. 分析视频并获取推荐
const { analysis, recommendations } = await analyzer.analyzeAndRecommend(
  videoFile,
  { type: 'gemini', model: 'gemini-2.5-flash' },
  '/path/to/target/directory'
);

// 2. 查看推荐结果
recommendations.forEach(rec => {
  console.log(`${rec.folderName}: ${rec.confidence} - ${rec.reasons.join(', ')}`);
});

// 3. 选择并组织文件
if (recommendations[0].confidence > 0.7) {
  const result = await analyzer.organizeVideo(
    videoFile,
    analysis,
    recommendations[0].folderPath
  );
  console.log(`文件已移动: ${result.originalPath} -> ${result.newPath}`);
}
```

## Analysis Modes

### Gemini Mode
Uses Google's Gemini AI for comprehensive video analysis:

```typescript
const geminiMode = {
  type: 'gemini' as const,
  model: 'gemini-2.5-flash',
  analysisType: 'comprehensive' // or 'product_focused', 'scene_detection', 'object_detection'
};

const result = await analyzer.analyzeVideo(videoFile, geminiMode, {
  quality: 'high',
  maxFrames: 50
});
```

### GPT-4 Frame Analysis Mode
Extracts frames and analyzes them with GPT-4 Vision:

```typescript
const gpt4Mode = {
  type: 'gpt4' as const,
  model: 'gpt-4-vision-preview'
};

const result = await analyzer.analyzeVideo(videoFile, gpt4Mode, {
  frameSamplingInterval: 1, // Extract frame every 1 second
  maxFrames: 30
});
```

## Complete Workflow

For a full analysis workflow including folder matching and report generation:

```typescript
const workflowResult = await analyzer.analyzeDirectoryComplete(
  '/path/to/videos',
  { type: 'gemini', model: 'gemini-2.5-flash' },
  {
    // Scan options
    scanOptions: {
      recursive: true,
      maxDepth: 3
    },

    // Analysis options
    analysisOptions: {
      quality: 'high',
      maxFrames: 30
    },

    // Folder matching configuration
    folderConfig: {
      baseDirectory: '/path/to/organize',
      maxDepth: 2,
      minConfidence: 0.4,
      enableSemanticAnalysis: true
    },

    // Report generation options
    reportOptions: {
      format: 'xml',
      outputPath: '/path/to/report.xml',
      includeFolderMatching: true,
      includeDetailedAnalysis: true
    },

    // Progress tracking
    onProgress: (progress) => {
      console.log(`${progress.step}: ${progress.progress}%`);
    }
  }
);

console.log('Workflow complete:');
console.log('- Analysis results:', workflowResult.analysisResults.length);
console.log('- Folder matches:', Object.keys(workflowResult.folderMatches).length);
console.log('- Report saved to:', workflowResult.reportPath);
```

## API Reference

### VideoAnalyzer Class

#### Constructor
```typescript
new VideoAnalyzer(config?: VideoAnalyzerConfig)
```

#### Methods

##### `scanDirectory(directoryPath: string, options?: VideoScanOptions): Promise<VideoFile[]>`
Scan a directory for video files.

##### `analyzeVideo(videoFile: VideoFile, mode: AnalysisMode, options?: AnalysisOptions, onProgress?: (progress: AnalysisProgress) => void): Promise<VideoAnalysisResult>`
Analyze a single video file.

##### `analyzeDirectory(directoryPath: string, mode: AnalysisMode, scanOptions?: VideoScanOptions, analysisOptions?: AnalysisOptions, onProgress?: (progress: AnalysisProgress) => void): Promise<VideoAnalysisResult[]>`
Analyze all videos in a directory.

##### `findMatchingFolders(analysisResults: VideoAnalysisResult[], folderConfig: FolderMatchConfig): Promise<Record<string, FolderMatchResult[]>>`
Find matching folders for analysis results.

##### `generateReport(analysisResults: VideoAnalysisResult[], folderMatches: Record<string, FolderMatchResult[]>, reportOptions: ReportOptions): Promise<string>`
Generate analysis report.

##### `analyzeDirectoryComplete(directoryPath: string, mode: AnalysisMode, options: CompleteWorkflowOptions): Promise<CompleteWorkflowResult>`
Complete workflow: scan, analyze, match folders, and generate report.

## Configuration

### VideoAnalyzerConfig
```typescript
interface VideoAnalyzerConfig {
  upload?: {
    bucketName?: string;
    filePrefix?: string;
    chunkSize?: number;
    maxRetries?: number;
  };
}
```

### AnalysisOptions
```typescript
interface AnalysisOptions {
  frameSamplingInterval?: number; // For GPT-4 mode
  maxFrames?: number; // For GPT-4 mode
  quality?: 'low' | 'medium' | 'high';
  language?: string;
  customPrompts?: string[];
}
```

### ReportOptions
```typescript
interface ReportOptions {
  format: 'xml' | 'json' | 'csv' | 'html';
  outputPath: string;
  includeThumbnails?: boolean;
  includeDetailedAnalysis?: boolean;
  includeFolderMatching?: boolean;
  title?: string;
  metadata?: Record<string, any>;
}
```

## Error Handling

The library provides comprehensive error handling with specific error codes:

```typescript
try {
  const result = await analyzer.analyzeVideo(videoFile, mode);
} catch (error) {
  if (error instanceof VideoAnalyzerError) {
    console.error('Analysis failed:', error.code, error.message);
    console.error('Details:', error.details);
  }
}
```

### Error Codes
- `SCAN_FAILED`: Directory scanning failed
- `UPLOAD_FAILED`: Video upload failed
- `ANALYSIS_FAILED`: Video analysis failed
- `FOLDER_MATCHING_FAILED`: Folder matching failed
- `REPORT_GENERATION_FAILED`: Report generation failed
- `WORKFLOW_FAILED`: Complete workflow failed

## Testing

Run the test suite:

```bash
npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

console.log('Analysis Result:', result);
```

## API Reference

### VideoAnalyzer

The main class for video analysis.

#### Constructor

```typescript
new VideoAnalyzer(config: GeminiConfig)
```

**Parameters:**
- `config.apiKey` (string): Your Gemini API key
- `config.model` (string, optional): Model name (default: 'gemini-2.0-flash-exp')
- `config.timeout` (number, optional): Request timeout in ms (default: 60000)
- `config.maxRetries` (number, optional): Maximum retry attempts (default: 3)

#### Methods

##### analyzeVideo()

Analyze a single video file or URL.

```typescript
async analyzeVideo(
  videoInput: File | string | ArrayBuffer,
  options?: AnalysisOptions,
  progressCallback?: ProgressCallback
): Promise<VideoAnalysisResult>
```

**Example:**
```typescript
const result = await analyzer.analyzeVideo(videoFile, {
  frameSamplingInterval: 2,
  maxFrames: 30,
  quality: 'high',
  language: 'zh-CN'
});
```

##### extractHighlights()

Extract highlight moments from a video.

```typescript
async extractHighlights(
  videoInput: File | string | ArrayBuffer,
  options?: AnalysisOptions
): Promise<HighlightDetection[]>
```

**Example:**
```typescript
const highlights = await analyzer.extractHighlights(videoFile);
highlights.forEach(highlight => {
  console.log(`${highlight.type}: ${highlight.description} (${highlight.startTime}s - ${highlight.endTime}s)`);
});
```

##### compareVideos()

Compare two videos for similarity.

```typescript
async compareVideos(
  video1: File | string | ArrayBuffer,
  video2: File | string | ArrayBuffer,
  options?: AnalysisOptions
): Promise<{ similarity: number; analysis: string }>
```

##### analyzeBatch()

Analyze multiple videos in batch.

```typescript
async analyzeBatch(
  videos: Array<{ input: File | string | ArrayBuffer; id: string }>,
  options?: AnalysisOptions,
  progressCallback?: ProgressCallback
): Promise<Map<string, VideoAnalysisResult>>
```

### Utility Functions

#### Quick Analysis

```typescript
import { analyzeVideoQuick } from '@mixvideo/video-analyzer';

const result = await analyzeVideoQuick(videoFile, 'your-api-key', {
  quality: 'medium'
});
```

#### Extract Highlights

```typescript
import { extractVideoHighlights } from '@mixvideo/video-analyzer';

const highlights = await extractVideoHighlights(videoFile, 'your-api-key');
```

#### Compare Videos

```typescript
import { compareVideos } from '@mixvideo/video-analyzer';

const comparison = await compareVideos(video1, video2, 'your-api-key');
console.log(`Similarity: ${comparison.similarity * 100}%`);
```

## Types

### VideoAnalysisResult

```typescript
interface VideoAnalysisResult {
  metadata: VideoMetadata;
  scenes: SceneDetection[];
  objects: ObjectDetection[];
  summary: VideoSummary;
  analyzedAt: Date;
  processingTime: number;
  modelVersion: string;
}
```

### AnalysisOptions

```typescript
interface AnalysisOptions {
  frameSamplingInterval?: number;
  maxFrames?: number;
  quality?: 'low' | 'medium' | 'high';
  language?: string;
  customPrompts?: string[];
}
```

### SceneDetection

```typescript
interface SceneDetection {
  startTime: number;
  endTime: number;
  duration: number;
  description: string;
  type: string;
  confidence: number;
  objects: string[];
  mood?: string;
}
```

## Examples

### Basic Video Analysis

```typescript
import { VideoAnalyzer } from '@mixvideo/video-analyzer';

const analyzer = new VideoAnalyzer({
  apiKey: process.env.GEMINI_API_KEY!
});

// Analyze with progress tracking
const result = await analyzer.analyzeVideo(
  videoFile,
  { type: 'gemini', model: 'gemini-2.5-flash' },
  {
    quality: 'high',
    frameSamplingInterval: 1,
    maxFrames: 50
  },
  (progress) => {
    console.log(`${progress.step}: ${progress.progress}%`);
  }
);

// Process results
result.scenes.forEach(scene => {
  console.log(`Scene: ${scene.description} (${scene.startTime}s - ${scene.endTime}s)`);
});

result.objects.forEach(obj => {
  console.log(`Object: ${obj.name} at ${obj.timestamp}s (confidence: ${obj.confidence})`);
});
```

### Highlight Extraction for Social Media

```typescript
const highlights = await analyzer.extractHighlights(videoFile, {
  language: 'zh-CN'
});

// Filter highlights suitable for social media
const socialHighlights = highlights.filter(h => h.socialMediaReady && h.importance > 0.7);

socialHighlights.forEach(highlight => {
  console.log(`📱 Social Media Highlight: ${highlight.description}`);
  console.log(`⏱️  Duration: ${highlight.endTime - highlight.startTime}s`);
  console.log(`⭐ Importance: ${highlight.importance}`);
});
```

### Batch Processing

```typescript
const videos = [
  { input: video1File, id: 'video1' },
  { input: video2File, id: 'video2' },
  { input: 'https://example.com/video3.mp4', id: 'video3' }
];

const results = await analyzer.analyzeBatch(videos, {
  quality: 'medium',
  maxFrames: 20
});

// Process batch results
for (const [videoId, result] of results) {
  console.log(`Video ${videoId}: ${result.summary.description}`);
}
```

### Custom Analysis Prompt

```typescript
const result = await analyzer.analyzeVideo(videoFile, {
  customPrompt: `
    Please analyze this video focusing on:
    1. Marketing potential
    2. Brand safety
    3. Audience engagement factors
    4. Recommended social media platforms
    
    Provide detailed insights for each aspect.
  `,
  language: 'en'
});
```

## Error Handling

```typescript
import { VideoAnalyzerError, ERROR_CODES } from '@mixvideo/video-analyzer';

try {
  const result = await analyzer.analyzeVideo(videoFile);
} catch (error) {
  if (error instanceof VideoAnalyzerError) {
    switch (error.code) {
      case ERROR_CODES.INVALID_API_KEY:
        console.error('Invalid API key provided');
        break;
      case ERROR_CODES.QUOTA_EXCEEDED:
        console.error('API quota exceeded');
        break;
      case ERROR_CODES.VIDEO_TOO_LARGE:
        console.error('Video file is too large');
        break;
      default:
        console.error('Analysis failed:', error.message);
    }
  }
}
```

## Supported Formats

- MP4 (H.264/H.265)
- WebM (VP8/VP9)
- MOV (QuickTime)
- AVI
- MKV (Matroska)
- FLV (Flash Video)
- WMV (Windows Media)
- M4V (iTunes Video)

## Requirements

- Node.js 16+
- Modern browser with Canvas API support
- Gemini API key from Google AI Studio

## Getting Your API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set up billing if required
4. Use the API key in your application

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## Support

- 📖 [Documentation](https://github.com/imeepos/verve/tree/main/packages/video-analyzer)
- 🐛 [Issue Tracker](https://github.com/imeepos/verve/issues)
- 💬 [Discussions](https://github.com/imeepos/verve/discussions)
