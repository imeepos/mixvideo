/**
 * Video analysis types and interfaces
 */

export interface VideoMetadata {
  /** Video file name */
  filename: string;
  /** Video duration in seconds */
  duration: number;
  /** Video width in pixels */
  width: number;
  /** Video height in pixels */
  height: number;
  /** Frame rate (fps) */
  frameRate: number;
  /** Video format/codec */
  format: string;
  /** File size in bytes */
  fileSize: number;
  /** Creation timestamp */
  createdAt?: Date;
}

export interface VideoFrame {
  /** Frame timestamp in seconds */
  timestamp: number;
  /** Frame index */
  frameIndex: number;
  /** Base64 encoded image data */
  imageData: string;
  /** Frame width */
  width: number;
  /** Frame height */
  height: number;
}

export interface SceneDetection {
  /** Scene start time in seconds */
  startTime: number;
  /** Scene end time in seconds */
  endTime: number;
  /** Scene duration in seconds */
  duration: number;
  /** Scene description */
  description: string;
  /** Scene type (e.g., 'action', 'dialogue', 'landscape') */
  type: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Key objects detected in scene */
  objects: string[];
  /** Scene mood/emotion */
  mood?: string;
}

export interface ObjectDetection {
  /** Object name/label */
  name: string;
  /** Detection confidence (0-1) */
  confidence: number;
  /** Bounding box coordinates */
  boundingBox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  /** Frame timestamp where object was detected */
  timestamp: number;
  /** Object category */
  category: string;
}

export interface VideoSummary {
  /** Overall video description */
  description: string;
  /** Main themes/topics */
  themes: string[];
  /** Key moments with timestamps */
  keyMoments: Array<{
    timestamp: number;
    description: string;
    importance: number;
  }>;
  /** Detected emotions throughout video */
  emotions: Array<{
    timestamp: number;
    emotion: string;
    intensity: number;
  }>;
  /** Content rating/classification */
  contentRating: {
    category: string;
    reasons: string[];
    confidence: number;
  };
}

export interface VideoAnalysisResult {
  /** Video metadata */
  metadata: VideoMetadata;
  /** Scene detection results */
  scenes: SceneDetection[];
  /** Object detection results */
  objects: ObjectDetection[];
  /** Video summary */
  summary: VideoSummary;
  /** Analysis timestamp */
  analyzedAt: Date;
  /** Processing time in milliseconds */
  processingTime: number;
  /** Analysis model version */
  modelVersion: string;
}

export interface AnalysisOptions {
  /** Enable scene detection */
  enableSceneDetection?: boolean;
  /** Enable object detection */
  enableObjectDetection?: boolean;
  /** Enable video summarization */
  enableSummarization?: boolean;
  /** Frame sampling interval in seconds */
  frameSamplingInterval?: number;
  /** Maximum number of frames to analyze */
  maxFrames?: number;
  /** Analysis quality level */
  quality?: 'low' | 'medium' | 'high';
  /** Custom prompt for analysis */
  customPrompt?: string;
  /** Language for analysis results */
  language?: string;
}

export interface GeminiConfig {
  /** Gemini API key */
  apiKey: string;
  /** Model name (default: gemini-2.0-flash-exp) */
  model?: string;
  /** API endpoint URL */
  endpoint?: string;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Maximum retries for failed requests */
  maxRetries?: number;
}

export interface AnalysisProgress {
  /** Current step description */
  step: string;
  /** Progress percentage (0-100) */
  progress: number;
  /** Current frame being processed */
  currentFrame?: number;
  /** Total frames to process */
  totalFrames?: number;
  /** Estimated time remaining in seconds */
  estimatedTimeRemaining?: number;
}

export type ProgressCallback = (progress: AnalysisProgress) => void;

export interface VideoAnalyzerError extends Error {
  code: string;
  details?: any;
}

export interface FrameExtractionOptions {
  /** Start time in seconds */
  startTime?: number;
  /** End time in seconds */
  endTime?: number;
  /** Interval between frames in seconds */
  interval?: number;
  /** Maximum number of frames to extract */
  maxFrames?: number;
  /** Frame quality (0-100) */
  quality?: number;
  /** Output format */
  format?: 'jpeg' | 'png' | 'webp';
}

export interface BatchAnalysisOptions extends AnalysisOptions {
  /** Maximum concurrent analyses */
  concurrency?: number;
  /** Batch processing callback */
  onBatchProgress?: (completed: number, total: number) => void;
}

export interface VideoComparisonResult {
  /** Similarity score (0-1) */
  similarity: number;
  /** Common scenes between videos */
  commonScenes: Array<{
    video1Timestamp: number;
    video2Timestamp: number;
    description: string;
    similarity: number;
  }>;
  /** Differences between videos */
  differences: string[];
  /** Comparison summary */
  summary: string;
}

export interface HighlightDetection {
  /** Highlight start time */
  startTime: number;
  /** Highlight end time */
  endTime: number;
  /** Highlight type */
  type: 'action' | 'emotional' | 'visual' | 'audio' | 'transition';
  /** Highlight description */
  description: string;
  /** Importance score (0-1) */
  importance: number;
  /** Recommended for social media */
  socialMediaReady: boolean;
}
