
/**
 * @mixvideo/jianying - 剪映草稿文件工具包
 *
 * 提供剪映（CapCut）草稿文件的解析、分析和生成功能
 */

// 解析功能
export {
  parseJianyingDraft,
  formatVideoInfo,
  exportToJson,
  microsecondsToSeconds,
  secondsToMicroseconds,
  calculateAspectRatio,
  type VideoInfo,
  type VideoClip,
  type AudioClip,
  type TrackSegment,
  type Track,
  type AppInfo,
  type Statistics,
  type CanvasConfig,
  type Transform,
  type TimeRange
} from './parse-draft';

// 增强分析功能
export {
  analyzeJianyingProject,
  analyzeJianyingProjectFromData,
  generateRecommendationsFromAnalysis,
  performEnhancedAnalysis,
  formatEnhancedAnalysis,
  type EnhancedAnalysis,
  type ComplexityAnalysis,
  type TimelineAnalysis,
  type MaterialUsage,
  type EditingFeatures,
  type Recommendation
} from './enhanced-parser';

// 生成功能
export {
  generateDraft,
  scanDirectory,
  checkFFProbe,
  getVideoInfoWithFFProbe,
  generateVideoClips,
  generateAudioClips,
  generateTracks,
  type VideoFileInfo,
  type GeneratedVideoClip,
  type GeneratedAudioClip,
  type GeneratedTrack,
  type GeneratedTrackSegment,
  type GeneratedDraft
} from './generate-draft';

// 工具函数
export const JianyingUtils = {
  // 时间转换
  microsecondsToSeconds: (microseconds: number): number => microseconds / 1000000,
  secondsToMicroseconds: (seconds: number): number => seconds * 1000000,

  // 宽高比计算
  calculateAspectRatio: (width: number, height: number): string => {
    const gcd = (a: number, b: number): number => b === 0 ? a : gcd(b, a % b);
    const divisor = gcd(width, height);
    return `${width / divisor}:${height / divisor}`;
  },

  // 支持的文件格式
  VIDEO_EXTENSIONS: ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'],
  AUDIO_EXTENSIONS: ['.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg'],

  // 检查文件类型
  isVideoFile: (filename: string): boolean => {
    const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
    return JianyingUtils.VIDEO_EXTENSIONS.includes(ext);
  },

  isAudioFile: (filename: string): boolean => {
    const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
    return JianyingUtils.AUDIO_EXTENSIONS.includes(ext);
  },

  isMediaFile: (filename: string): boolean => {
    return JianyingUtils.isVideoFile(filename) || JianyingUtils.isAudioFile(filename);
  }
};

// 常量
export const JIANYING_CONSTANTS = {
  // 默认配置
  DEFAULT_FPS: 30,
  DEFAULT_CANVAS_WIDTH: 1080,
  DEFAULT_CANVAS_HEIGHT: 1920,
  DEFAULT_ASPECT_RATIO: '9:16',

  // 时间单位
  MICROSECONDS_PER_SECOND: 1000000,

  // 剪映版本信息
  SUPPORTED_VERSIONS: ['13.2.0', '110.0.0'],
  DEFAULT_VERSION: '13.2.0',

  // 平台信息
  PLATFORM_INFO: {
    app_id: 3704,
    app_source: 'auto-generator',
    platform: 'auto'
  }
};