#!/usr/bin/env ts-node

/**
 * 剪映草稿文件解析器
 * 解析 draft_content.json 文件，提取视频的详细信息
 */

import * as fs from 'fs';

// 类型定义
interface CanvasConfig {
  height: number;
  width: number;
  ratio: string;
}

interface CropInfo {
  lower_left_x: number;
  lower_left_y: number;
  lower_right_x: number;
  lower_right_y: number;
  upper_left_x: number;
  upper_left_y: number;
  upper_right_x: number;
  upper_right_y: number;
}

interface VideoClip {
  id: string;
  material_name: string;
  path: string;
  duration: number;
  width: number;
  height: number;
  has_audio: boolean;
  crop: CropInfo;
  crop_ratio: string;
  crop_scale: number;
  type: string;
  source: number;
  is_ai_generate_content: boolean;
  is_copyright: boolean;
}

interface AudioClip {
  id: string;
  name: string;
  path: string;
  duration: number;
  type: string;
  source_platform: number;
  is_ai_clone_tone: boolean;
  is_text_edit_overdub: boolean;
}

interface TrackSegment {
  clip?: {
    alpha: number;
    flip: {
      horizontal: boolean;
      vertical: boolean;
    };
    rotation: number;
    scale: {
      x: number;
      y: number;
    };
    transform: {
      x: number;
      y: number;
    };
  };
  material_id: string;
  target_timerange: {
    duration: number;
    start: number;
  };
  source_timerange?: {
    duration: number;
    start: number;
  } | null;
}

interface Track {
  id: string;
  name: string;
  attribute: number;
  flag: number;
  is_default_name: boolean;
  segments: TrackSegment[];
}

interface JianyingDraft {
  id: string;
  duration: number;
  fps: number;
  canvas_config: CanvasConfig;
  color_space: number;
  create_time: number;
  last_modified_platform: {
    app_id: number;
    app_source: string;
    app_version: string;
    device_id: string;
    os: string;
    platform: string;
  };
  materials: {
    videos: VideoClip[];
    audios: AudioClip[];
  };
  tracks: Track[];
}

interface Transform {
  position: { x: number; y: number };
  rotation: number;
  scale: { x: number; y: number };
}

interface TimeRange {
  start: number;
  duration: number;
  durationSeconds: number;
}

interface AppInfo {
  appId: string;
  version: string;
  platform: string;
}

interface Statistics {
  totalVideoClips: number;
  totalAudioClips: number;
  totalTracks: number;
  totalSegments: number;
  uniqueVideoFiles: number;
  uniqueAudioFiles: number;
}

interface VideoInfo {
  // 项目基本信息
  projectId: string;
  projectDuration: number; // 微秒
  projectDurationSeconds: number; // 秒
  fps: number;
  canvasSize: {
    width: number;
    height: number;
    ratio: string;
  };
  
  // 视频素材信息
  videoClips: Array<{
    id: string;
    fileName: string;
    filePath: string;
    duration: number; // 微秒
    durationSeconds: number; // 秒
    resolution: {
      width: number;
      height: number;
      aspectRatio: string;
    };
    hasAudio: boolean;
    cropInfo: {
      ratio: string;
      scale: number;
      coordinates: CropInfo;
    };
    isAIGenerated: boolean;
    isCopyrighted: boolean;
  }>;
  
  // 音频素材信息
  audioClips: Array<{
    id: string;
    name: string;
    filePath: string;
    duration: number; // 微秒
    durationSeconds: number; // 秒
    type: string;
    isAIClone: boolean;
    isTextOverdub: boolean;
  }>;
  
  // 轨道信息
  tracks: Array<{
    id: string;
    name: string;
    type: string; // video, audio, etc.
    segmentCount: number;
    segments: Array<{
      materialId: string;
      timeRange: {
        start: number; // 微秒
        duration: number; // 微秒
        startSeconds: number; // 秒
        durationSeconds: number; // 秒
      };
      sourceTimeRange: {
        start: number; // 微秒
        duration: number; // 微秒
        startSeconds: number; // 秒
        durationSeconds: number; // 秒
      };
      transform: {
        alpha: number;
        rotation: number;
        scale: { x: number; y: number };
        position: { x: number; y: number };
        flip: { horizontal: boolean; vertical: boolean };
      };
    }>;
  }>;
  
  // 应用信息
  appInfo: {
    appId: number;
    appSource: string;
    appVersion: string;
    platform: string;
    os: string;
    deviceId: string;
  };
  
  // 统计信息
  statistics: {
    totalVideoClips: number;
    totalAudioClips: number;
    totalTracks: number;
    totalSegments: number;
    uniqueVideoFiles: string[];
    uniqueAudioFiles: string[];
  };
}

/**
 * 微秒转换为秒
 */
function microsecondsToSeconds(microseconds: number): number {
  return Math.round((microseconds / 1000000) * 100) / 100;
}

/**
 * 计算宽高比
 */
function calculateAspectRatio(width: number, height: number): string {
  const gcd = (a: number, b: number): number => b === 0 ? a : gcd(b, a % b);
  const divisor = gcd(width, height);
  return `${width / divisor}:${height / divisor}`;
}

/**
 * 解析剪映草稿文件
 */
function parseJianyingDraft(filePath: string): VideoInfo {
  if (!fs.existsSync(filePath)) {
    throw new Error(`文件不存在: ${filePath}`);
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  const draft: JianyingDraft = JSON.parse(content);

  // 解析视频素材
  const videoClips = draft.materials.videos.map(video => ({
    id: video.id,
    fileName: video.material_name,
    filePath: video.path,
    duration: video.duration,
    durationSeconds: microsecondsToSeconds(video.duration),
    resolution: {
      width: video.width,
      height: video.height,
      aspectRatio: calculateAspectRatio(video.width, video.height)
    },
    hasAudio: video.has_audio,
    cropInfo: {
      ratio: video.crop_ratio,
      scale: video.crop_scale,
      coordinates: video.crop
    },
    isAIGenerated: video.is_ai_generate_content,
    isCopyrighted: video.is_copyright
  }));

  // 解析音频素材
  const audioClips = draft.materials.audios.map(audio => ({
    id: audio.id,
    name: audio.name,
    filePath: audio.path,
    duration: audio.duration,
    durationSeconds: microsecondsToSeconds(audio.duration),
    type: audio.type,
    isAIClone: audio.is_ai_clone_tone,
    isTextOverdub: audio.is_text_edit_overdub
  }));

  // 解析轨道信息
  const tracks = draft.tracks.map(track => {
    const segments = track.segments.map(segment => ({
      materialId: segment.material_id,
      timeRange: {
        start: segment.target_timerange.start,
        duration: segment.target_timerange.duration,
        startSeconds: microsecondsToSeconds(segment.target_timerange.start),
        durationSeconds: microsecondsToSeconds(segment.target_timerange.duration)
      },
      sourceTimeRange: segment.source_timerange ? {
        start: segment.source_timerange.start,
        duration: segment.source_timerange.duration,
        startSeconds: microsecondsToSeconds(segment.source_timerange.start),
        durationSeconds: microsecondsToSeconds(segment.source_timerange.duration)
      } : {
        start: 0,
        duration: 0,
        startSeconds: 0,
        durationSeconds: 0
      },
      transform: segment.clip ? {
        alpha: segment.clip.alpha,
        rotation: segment.clip.rotation,
        scale: segment.clip.scale,
        position: segment.clip.transform,
        flip: segment.clip.flip
      } : {
        alpha: 1.0,
        rotation: 0.0,
        scale: { x: 1.0, y: 1.0 },
        position: { x: 0.0, y: 0.0 },
        flip: { horizontal: false, vertical: false }
      }
    }));

    return {
      id: track.id,
      name: track.name || `轨道 ${track.attribute}`,
      type: track.attribute === 0 ? 'video' : 'audio',
      segmentCount: segments.length,
      segments
    };
  });

  // 统计信息
  const uniqueVideoFiles = [...new Set(videoClips.map(v => v.filePath))];
  const uniqueAudioFiles = [...new Set(audioClips.map(a => a.filePath))];
  const totalSegments = tracks.reduce((sum, track) => sum + track.segmentCount, 0);

  return {
    projectId: draft.id,
    projectDuration: draft.duration,
    projectDurationSeconds: microsecondsToSeconds(draft.duration),
    fps: draft.fps,
    canvasSize: {
      width: draft.canvas_config.width,
      height: draft.canvas_config.height,
      ratio: draft.canvas_config.ratio
    },
    videoClips,
    audioClips,
    tracks,
    appInfo: {
      appId: draft.last_modified_platform.app_id,
      appSource: draft.last_modified_platform.app_source,
      appVersion: draft.last_modified_platform.app_version,
      platform: draft.last_modified_platform.platform,
      os: draft.last_modified_platform.os,
      deviceId: draft.last_modified_platform.device_id
    },
    statistics: {
      totalVideoClips: videoClips.length,
      totalAudioClips: audioClips.length,
      totalTracks: tracks.length,
      totalSegments,
      uniqueVideoFiles,
      uniqueAudioFiles
    }
  };
}

/**
 * 格式化输出视频信息
 */
function formatVideoInfo(info: VideoInfo): void {
  console.log('🎬 剪映项目详细信息');
  console.log('=' .repeat(60));

  // 项目基本信息
  console.log('\n📋 项目基本信息:');
  console.log(`  项目ID: ${info.projectId}`);
  console.log(`  总时长: ${info.projectDurationSeconds}秒 (${info.projectDuration}微秒)`);
  console.log(`  帧率: ${info.fps} FPS`);
  console.log(`  画布尺寸: ${info.canvasSize.width}x${info.canvasSize.height} (${info.canvasSize.ratio})`);

  // 应用信息
  console.log('\n📱 应用信息:');
  console.log(`  应用: ${info.appInfo.appSource} v${info.appInfo.appVersion}`);
  console.log(`  平台: ${info.appInfo.platform} (${info.appInfo.os})`);
  console.log(`  设备ID: ${info.appInfo.deviceId}`);

  // 统计信息
  console.log('\n📊 统计信息:');
  console.log(`  视频素材: ${info.statistics.totalVideoClips}个`);
  console.log(`  音频素材: ${info.statistics.totalAudioClips}个`);
  console.log(`  轨道数量: ${info.statistics.totalTracks}个`);
  console.log(`  片段总数: ${info.statistics.totalSegments}个`);
  console.log(`  独立视频文件: ${info.statistics.uniqueVideoFiles.length}个`);
  console.log(`  独立音频文件: ${info.statistics.uniqueAudioFiles.length}个`);

  // 视频素材详情
  if (info.videoClips.length > 0) {
    console.log('\n🎥 视频素材详情:');
    info.videoClips.forEach((clip, index) => {
      console.log(`  ${index + 1}. ${clip.fileName}`);
      console.log(`     文件路径: ${clip.filePath}`);
      console.log(`     时长: ${clip.durationSeconds}秒`);
      console.log(`     分辨率: ${clip.resolution.width}x${clip.resolution.height} (${clip.resolution.aspectRatio})`);
      console.log(`     包含音频: ${clip.hasAudio ? '是' : '否'}`);
      console.log(`     裁剪比例: ${clip.cropInfo.ratio} (缩放: ${clip.cropInfo.scale})`);
      console.log(`     AI生成: ${clip.isAIGenerated ? '是' : '否'}`);
      console.log(`     版权内容: ${clip.isCopyrighted ? '是' : '否'}`);
      console.log('');
    });
  }

  // 音频素材详情
  if (info.audioClips.length > 0) {
    console.log('\n🎵 音频素材详情:');
    info.audioClips.forEach((clip, index) => {
      console.log(`  ${index + 1}. ${clip.name}`);
      console.log(`     文件路径: ${clip.filePath}`);
      console.log(`     时长: ${clip.durationSeconds}秒`);
      console.log(`     类型: ${clip.type}`);
      console.log(`     AI克隆音色: ${clip.isAIClone ? '是' : '否'}`);
      console.log(`     文本配音: ${clip.isTextOverdub ? '是' : '否'}`);
      console.log('');
    });
  }

  // 轨道详情
  if (info.tracks.length > 0) {
    console.log('\n🛤️ 轨道详情:');
    info.tracks.forEach((track, index) => {
      console.log(`  ${index + 1}. ${track.name} (${track.type})`);
      console.log(`     轨道ID: ${track.id}`);
      console.log(`     片段数量: ${track.segmentCount}个`);

      if (track.segments.length > 0) {
        console.log('     片段详情:');
        track.segments.forEach((segment, segIndex) => {
          console.log(`       ${segIndex + 1}. 素材ID: ${segment.materialId}`);
          console.log(`          时间轴: ${segment.timeRange.startSeconds}s - ${segment.timeRange.startSeconds + segment.timeRange.durationSeconds}s (时长: ${segment.timeRange.durationSeconds}s)`);
          console.log(`          源时间: ${segment.sourceTimeRange.startSeconds}s - ${segment.sourceTimeRange.startSeconds + segment.sourceTimeRange.durationSeconds}s`);
          console.log(`          变换: 透明度=${segment.transform.alpha}, 旋转=${segment.transform.rotation}°`);
          console.log(`          缩放: x=${segment.transform.scale.x}, y=${segment.transform.scale.y}`);
          console.log(`          位置: x=${segment.transform.position.x}, y=${segment.transform.position.y}`);
          console.log(`          翻转: 水平=${segment.transform.flip.horizontal}, 垂直=${segment.transform.flip.vertical}`);
        });
      }
      console.log('');
    });
  }

  // 文件列表
  console.log('\n📁 使用的文件列表:');
  console.log('  视频文件:');
  info.statistics.uniqueVideoFiles.forEach((file, index) => {
    console.log(`    ${index + 1}. ${file}`);
  });

  if (info.statistics.uniqueAudioFiles.length > 0) {
    console.log('  音频文件:');
    info.statistics.uniqueAudioFiles.forEach((file, index) => {
      console.log(`    ${index + 1}. ${file}`);
    });
  }
}

/**
 * 导出为JSON文件
 */
function exportToJson(info: VideoInfo, outputPath: string): void {
  const jsonContent = JSON.stringify(info, null, 2);
  fs.writeFileSync(outputPath, jsonContent, 'utf-8');
  console.log(`\n💾 详细信息已导出到: ${outputPath}`);
}

/**
 * 主函数
 */
function main(): void {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('使用方法:');
    console.log('  ts-node parse-draft.ts <draft_content.json路径> [输出JSON路径]');
    console.log('');
    console.log('示例:');
    console.log('  ts-node parse-draft.ts ./draft_content.json');
    console.log('  ts-node parse-draft.ts ./draft_content.json ./output.json');
    process.exit(1);
  }

  const inputPath = args[0];
  const outputPath = args[1];

  try {
    console.log(`🔍 正在解析剪映草稿文件: ${inputPath}`);

    const videoInfo = parseJianyingDraft(inputPath);

    // 输出格式化信息
    formatVideoInfo(videoInfo);

    // 如果指定了输出路径，导出JSON
    if (outputPath) {
      exportToJson(videoInfo, outputPath);
    }

    console.log('\n✅ 解析完成!');

  } catch (error) {
    console.error('❌ 解析失败:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

// 如果直接运行此脚本，执行主函数
if (require.main === module) {
  main();
}

// 导出主要函数
export { parseJianyingDraft, formatVideoInfo, exportToJson };

// 导出工具函数
export { microsecondsToSeconds, calculateAspectRatio };

// 添加缺失的工具函数
export function secondsToMicroseconds(seconds: number): number {
  return seconds * 1000000;
}

// 导出类型定义
export type {
  VideoInfo,
  VideoClip,
  AudioClip,
  TrackSegment,
  Track,
  AppInfo,
  Statistics,
  CanvasConfig,
  Transform,
  TimeRange,
  CropInfo
};
