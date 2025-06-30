/**
 * @mixvideo/video-analyzer
 *
 * Video analysis toolkit using Gemini AI for intelligent video feature extraction
 * Supports folder scanning, video upload, content analysis, and smart categorization
 */

export * from './types';
export * from './video-scanner';
export * from './video-uploader';
export * from './analysis-engine';
export * from './product-analyzer';
export * from './folder-matcher';
export * from './report-generator';
export * from './frame-analyzer';
export * from './video-analyzer';

// 导出扩展配置类型
export type { ExtendedVideoAnalyzerConfig } from './video-analyzer';

// 导出简化的提示词系统
export * from './simple-prompts';

// 导出新的工作流程组件
export * from './workflow-manager';
export * from './file-organizer';