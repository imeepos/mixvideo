/**
 * @mixvideo/video-analyzer
 * 
 * A TypeScript library for intelligent video analysis using Gemini 2.0 Flash
 * 
 * @author MixVideo Team
 * @version 1.0.0
 */

// Core exports
export { VideoAnalyzer } from './core/VideoAnalyzer';

// Utility exports
export { FrameExtractor } from './utils/FrameExtractor';
export { VideoProcessor } from './utils/VideoProcessor';
export { PromptBuilder } from './utils/PromptBuilder';

// Type exports
export type {
  VideoMetadata,
  VideoFrame,
  SceneDetection,
  ObjectDetection,
  VideoSummary,
  VideoAnalysisResult,
  AnalysisOptions,
  GeminiConfig,
  AnalysisProgress,
  ProgressCallback,
  VideoAnalyzerError,
  FrameExtractionOptions,
  BatchAnalysisOptions,
  VideoComparisonResult,
  HighlightDetection
} from './types';

// Factory function for easy initialization
export function createVideoAnalyzer(config: import('./types').GeminiConfig) {
  return new VideoAnalyzer(config);
}

// Utility functions
export async function analyzeVideoQuick(
  videoInput: File | string | ArrayBuffer,
  apiKey: string,
  options?: import('./types').AnalysisOptions
): Promise<import('./types').VideoAnalysisResult> {
  const analyzer = createVideoAnalyzer({ apiKey });
  return analyzer.analyzeVideo(videoInput, options);
}

export async function extractVideoHighlights(
  videoInput: File | string | ArrayBuffer,
  apiKey: string,
  options?: import('./types').AnalysisOptions
): Promise<import('./types').HighlightDetection[]> {
  const analyzer = createVideoAnalyzer({ apiKey });
  return analyzer.extractHighlights(videoInput, options);
}

export async function compareVideos(
  video1: File | string | ArrayBuffer,
  video2: File | string | ArrayBuffer,
  apiKey: string,
  options?: import('./types').AnalysisOptions
): Promise<{ similarity: number; analysis: string }> {
  const analyzer = createVideoAnalyzer({ apiKey });
  return analyzer.compareVideos(video1, video2, options);
}

// Version info
export const VERSION = '1.0.0';
export const SUPPORTED_FORMATS = [
  'mp4', 'webm', 'mov', 'avi', 'mkv', 'flv', 'wmv', 'm4v'
];

// Default configurations
export const DEFAULT_CONFIG = {
  model: 'gemini-2.0-flash-exp',
  timeout: 60000,
  maxRetries: 3,
  frameSamplingInterval: 2,
  maxFrames: 30,
  quality: 'medium' as const
};

// Error codes
export const ERROR_CODES = {
  INVALID_API_KEY: 'INVALID_API_KEY',
  UNSUPPORTED_FORMAT: 'UNSUPPORTED_FORMAT',
  ANALYSIS_FAILED: 'ANALYSIS_FAILED',
  FRAME_EXTRACTION_FAILED: 'FRAME_EXTRACTION_FAILED',
  NETWORK_ERROR: 'NETWORK_ERROR',
  PARSE_ERROR: 'PARSE_ERROR',
  QUOTA_EXCEEDED: 'QUOTA_EXCEEDED',
  VIDEO_TOO_LARGE: 'VIDEO_TOO_LARGE',
  VIDEO_TOO_SHORT: 'VIDEO_TOO_SHORT'
} as const;
