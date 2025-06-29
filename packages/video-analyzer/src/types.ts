/**
 * Core types and interfaces for video analysis
 */

export interface VideoFile {
  path: string;
  name: string;
  size: number;
  duration?: number;
  format?: string;
  resolution?: {
    width: number;
    height: number;
  };
  frameRate?: number;
  bitrate?: number;
  createdAt?: Date;
  modifiedAt?: Date;
}

export interface VideoScanOptions {
  /** Supported video extensions to scan for */
  extensions?: string[];
  /** Whether to scan subdirectories recursively */
  recursive?: boolean;
  /** Maximum file size in bytes (default: 500MB) */
  maxFileSize?: number;
  /** Minimum file size in bytes (default: 1KB) */
  minFileSize?: number;
  /** Progress callback for scanning */
  onProgress?: (progress: ScanProgress) => void;
}

export interface ScanProgress {
  /** Current step being performed */
  step: string;
  /** Progress percentage (0-100) */
  progress: number;
  /** Current file being processed */
  currentFile?: string;
  /** Total files found so far */
  filesFound: number;
  /** Total directories scanned */
  directoriesScanned: number;
}

export interface UploadProgress {
  /** Current step being performed */
  step: string;
  /** Progress percentage (0-100) */
  progress: number;
  /** Current file being uploaded */
  currentFile?: string;
  /** Bytes uploaded */
  bytesUploaded: number;
  /** Total bytes to upload */
  totalBytes: number;
  /** Upload speed in bytes/second */
  uploadSpeed?: number;
}

export interface AnalysisMode {
  /** Analysis mode type */
  type: 'gemini' | 'gpt4';
  /** Model configuration */
  model?: string;
  /** Analysis options */
  options?: AnalysisOptions;
}

export interface AnalysisOptions {
  /** Frame sampling interval in seconds (for GPT-4 mode) */
  frameSamplingInterval?: number;
  /** Maximum number of frames to analyze */
  maxFrames?: number;
  /** Analysis quality level */
  quality?: 'low' | 'medium' | 'high';
  /** Language for analysis results */
  language?: string;
  /** Custom analysis prompts */
  customPrompts?: string[];
}

export interface AnalysisProgress {
  /** Current step being performed */
  step: string;
  /** Progress percentage (0-100) */
  progress: number;
  /** Current file being analyzed */
  currentFile?: string;
  /** Current frame being processed (for GPT-4 mode) */
  currentFrame?: number;
  /** Total frames to process */
  totalFrames?: number;
  /** Analysis stage */
  stage: 'upload' | 'processing' | 'analysis' | 'complete';
}

export interface VideoMetadata {
  /** Video file information */
  file: VideoFile;
  /** Technical metadata */
  technical: {
    codec: string;
    container: string;
    hasAudio: boolean;
    audioCodec?: string;
    channels?: number;
    sampleRate?: number;
  };
  /** Content metadata */
  content?: {
    title?: string;
    description?: string;
    tags?: string[];
    thumbnail?: string;
  };
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
  /** Scene type/category */
  type?: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Key objects in scene */
  objects?: string[];
  /** Scene thumbnail timestamp */
  thumbnailTime?: number;
}

export interface ObjectDetection {
  /** Object name/label */
  name: string;
  /** Object category */
  category: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Bounding box coordinates (if available) */
  boundingBox?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  /** Time range when object appears */
  timeRange?: {
    start: number;
    end: number;
  };
  /** Additional attributes */
  attributes?: Record<string, any>;
}

export interface ProductFeatures {
  /** Product appearance details */
  appearance: {
    colors: string[];
    shape: string;
    size: string;
    style: string;
  };
  /** Material analysis */
  materials: string[];
  /** Functional features */
  functionality: string[];
  /** Usage scenarios */
  usageScenarios: string[];
  /** Target audience */
  targetAudience?: string;
  /** Brand elements */
  brandElements?: string[];
}

export interface ContentSummary {
  /** Overall description */
  description: string;
  /** Key highlights */
  highlights: string[];
  /** Main topics/themes */
  topics: string[];
  /** Emotional tone */
  tone?: string;
  /** Content category */
  category?: string;
  /** Keywords */
  keywords: string[];
}

export interface FrameAnalysis {
  /** Frame timestamp in seconds */
  timestamp: number;
  /** Frame description */
  description: string;
  /** Objects detected in frame */
  objects: ObjectDetection[];
  /** Frame quality score */
  quality: number;
  /** Frame type (keyframe, etc.) */
  type?: string;
}

export interface VideoAnalysisResult {
  /** Video metadata */
  metadata: VideoMetadata;
  /** Analysis mode used */
  analysisMode: AnalysisMode;
  /** Scene detection results */
  scenes: SceneDetection[];
  /** Object detection results */
  objects: ObjectDetection[];
  /** Product feature analysis */
  productFeatures?: ProductFeatures;
  /** Content summary */
  summary: ContentSummary;
  /** Frame-by-frame analysis (GPT-4 mode) */
  frameAnalysis?: FrameAnalysis[];
  /** Analysis timestamp */
  analyzedAt: Date;
  /** Processing time in milliseconds */
  processingTime: number;
  /** Analysis quality metrics */
  qualityMetrics?: {
    overallScore: number;
    detectionAccuracy: number;
    analysisDepth: number;
  };
}

export interface FolderMatchResult {
  /** Folder path */
  folderPath: string;
  /** Folder name */
  folderName: string;
  /** Match confidence score (0-1) */
  confidence: number;
  /** Matching reasons */
  reasons: string[];
  /** Semantic similarity score */
  semanticScore: number;
  /** Content relevance score */
  relevanceScore: number;
  /** Recommended action */
  action: 'move' | 'copy' | 'link' | 'ignore';
}

export interface AnalysisReport {
  /** Report metadata */
  metadata: {
    generatedAt: Date;
    version: string;
    totalVideos: number;
    totalProcessingTime: number;
  };
  /** Individual video results */
  videoResults: VideoAnalysisResult[];
  /** Folder matching results */
  folderMatches?: Record<string, FolderMatchResult[]>;
  /** Summary statistics */
  summary: {
    totalScenes: number;
    totalObjects: number;
    commonThemes: string[];
    recommendedCategories: string[];
  };
  /** Export options */
  exportOptions?: {
    format: 'xml' | 'json' | 'csv' | 'html';
    includeImages: boolean;
    includeThumbnails: boolean;
  };
}

export interface VideoAnalyzerConfig {
  /** Gemini API configuration */
  gemini?: {
    accessToken?: string;
    cloudflareProjectId?: string;
    cloudflareGatewayId?: string;
    googleProjectId?: string;
    regions?: string[];
  };
  /** Upload configuration */
  upload?: {
    bucketName?: string;
    filePrefix?: string;
    chunkSize?: number;
    maxRetries?: number;
  };
  /** Analysis configuration */
  analysis?: {
    defaultMode?: 'gemini' | 'gpt4';
    defaultOptions?: AnalysisOptions;
    maxConcurrentAnalysis?: number;
  };
  /** Logging configuration */
  logging?: {
    enabled: boolean;
    level: 'debug' | 'info' | 'warn' | 'error';
    outputFile?: string;
  };
}

export class VideoAnalyzerError extends Error {
  public code: string;
  public details?: any;
  public file?: string;
  public stage?: string;

  constructor(message: string, code: string, details?: any, file?: string, stage?: string) {
    super(message);
    this.name = 'VideoAnalyzerError';
    this.code = code;
    this.details = details;
    this.file = file;
    this.stage = stage;

    // Maintains proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, VideoAnalyzerError);
    }
  }
}
