# @mixvideo/video-analyzer

🎬 A powerful TypeScript library for intelligent video analysis using Google's Gemini 2.0 Flash model.

## Features

- 🤖 **AI-Powered Analysis**: Leverage Gemini 2.0 Flash for advanced video understanding
- 🎯 **Scene Detection**: Automatically identify and categorize video scenes
- 🔍 **Object Recognition**: Detect and track objects throughout the video
- 📝 **Content Summarization**: Generate comprehensive video summaries
- ✨ **Highlight Extraction**: Find the most engaging moments in your videos
- 🔄 **Video Comparison**: Compare similarities between different videos
- 📊 **Batch Processing**: Analyze multiple videos efficiently
- 🎨 **TypeScript Support**: Full type safety and excellent developer experience

## Installation

```bash
npm install @mixvideo/video-analyzer
```

## Quick Start

```typescript
import { VideoAnalyzer } from '@mixvideo/video-analyzer';

// Initialize the analyzer
const analyzer = new VideoAnalyzer({
  apiKey: 'your-gemini-api-key'
});

// Analyze a video file
const result = await analyzer.analyzeVideo(videoFile, {
  enableSceneDetection: true,
  enableObjectDetection: true,
  enableSummarization: true
});

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
  enableSceneDetection: true
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
  enableSceneDetection?: boolean;
  enableObjectDetection?: boolean;
  enableSummarization?: boolean;
  frameSamplingInterval?: number;
  maxFrames?: number;
  quality?: 'low' | 'medium' | 'high';
  customPrompt?: string;
  language?: string;
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
  {
    enableSceneDetection: true,
    enableObjectDetection: true,
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
