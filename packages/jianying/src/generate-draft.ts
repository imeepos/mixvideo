#!/usr/bin/env ts-node

/**
 * 自动生成剪映草稿文件生成器
 * 扫描指定目录的视频文件，自动生成 draft_content.json
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

// 简单的 UUID 生成函数
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// 支持的视频文件扩展名
const VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'];
const AUDIO_EXTENSIONS = ['.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg'];

interface VideoFileInfo {
  filePath: string;
  fileName: string;
  extension: string;
  size: number;
  isVideo: boolean;
  isAudio: boolean;
}

interface GeneratedVideoClip {
  aigc_type: string;
  audio_fade: null;
  cartoon_path: string;
  category_id: string;
  category_name: string;
  check_flag: number;
  crop: {
    lower_left_x: number;
    lower_left_y: number;
    lower_right_x: number;
    lower_right_y: number;
    upper_left_x: number;
    upper_left_y: number;
    upper_right_x: number;
    upper_right_y: number;
  };
  crop_ratio: string;
  crop_scale: number;
  duration: number;
  extra_type_option: number;
  formula_id: string;
  freeze: null;
  has_audio: boolean;
  height: number;
  id: string;
  intensifies_audio_path: string;
  intensifies_path: string;
  is_ai_generate_content: boolean;
  is_copyright: boolean;
  is_text_edit_overdub: boolean;
  is_unified_beauty_mode: boolean;
  local_id: string;
  local_material_id: string;
  material_id: string;
  material_name: string;
  material_url: string;
  matting: {
    flag: number;
    has_use_quick_brush: boolean;
    has_use_quick_eraser: boolean;
    interactiveTime: any[];
    path: string;
    strokes: any[];
  };
  media_path: string;
  object_locked: null;
  origin_material_id: string;
  path: string;
  picture_from: string;
  picture_set_category_id: string;
  picture_set_category_name: string;
  request_id: string;
  reverse_intensifies_path: string;
  reverse_path: string;
  smart_motion: null;
  source: number;
  source_platform: number;
  stable: {
    matrix_path: string;
    stable_level: number;
    time_range: {
      duration: number;
      start: number;
    };
  };
  team_id: string;
  type: string;
  video_algorithm: {
    algorithms: any[];
    deflicker: null;
    motion_blur_config: null;
    noise_reduction: null;
    path: string;
    time_range: null;
  };
  width: number;
}

interface GeneratedAudioClip {
  app_id: number;
  category_id: string;
  category_name: string;
  check_flag: number;
  copyright_limit_type: string;
  duration: number;
  effect_id: string;
  formula_id: string;
  id: string;
  intensifies_path: string;
  is_ai_clone_tone: boolean;
  is_text_edit_overdub: boolean;
  is_ugc: boolean;
  local_material_id: string;
  music_id: string;
  name: string;
  path: string;
  query: string;
  request_id: string;
  resource_id: string;
  search_id: string;
  source_from: string;
  source_platform: number;
  team_id: string;
  text_id: string;
  tone_category_id: string;
  tone_category_name: string;
  tone_effect_id: string;
  tone_effect_name: string;
  tone_platform: string;
  tone_second_category_id: string;
  tone_second_category_name: string;
  tone_speaker: string;
  tone_type: string;
  type: string;
  video_id: string;
  wave_points: any[];
}

interface GeneratedTrackSegment {
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

interface GeneratedTrack {
  attribute: number;
  flag: number;
  id: string;
  segments: GeneratedTrackSegment[];
  type: string;
}

interface GeneratedDraft {
  canvas_config: {
    height: number;
    ratio: string;
    width: number;
  };
  color_space: number;
  config: {
    adjust_max_index: number;
    attachment_info: any[];
    combination_max_index: number;
    export_range: null;
    extract_audio_last_index: number;
    lyrics_recognition_id: string;
    lyrics_sync: boolean;
    lyrics_taskinfo: any[];
    maintrack_adsorb: boolean;
    material_save_mode: number;
    multi_language_current: string;
    multi_language_list: any[];
    multi_language_main: string;
    multi_language_mode: string;
    original_sound_last_index: number;
    record_audio_last_index: number;
    sticker_max_index: number;
    subtitle_keywords_config: null;
    subtitle_recognition_id: string;
    subtitle_sync: boolean;
    subtitle_taskinfo: any[];
    system_font_list: any[];
    text_recognition_id: string;
    text_sync: boolean;
    text_taskinfo: any[];
    video_recognition_id: string;
    video_sync: boolean;
    video_taskinfo: any[];
  };
  create_time: number;
  draft_fold_path: string;
  draft_id: string;
  draft_name: string;
  draft_removable_storage_device: string;
  duration: number;
  fps: number;
  id: string;
  last_modified_platform: {
    app_id: number;
    app_source: string;
    app_version: string;
    device_id: string;
    hard_disk_id: string;
    mac_address: string;
    os_version: string;
    platform: string;
    screen_height: number;
    screen_width: number;
  };
  materials: {
    audio_effects: any[];
    audio_fades: any[];
    audio_track_indexes: any[];
    audios: any[];
    beats: any[];
    canvases: any[];
    chromas: any[];
    color_curves: any[];
    color_wheels: any[];
    effects: any[];
    flowers: any[];
    handwrites: any[];
    hsl: any[];
    images: any[];
    keyframes: any[];
    masks: any[];
    material_animations: any[];
    placeholders: any[];
    plugin_effects: any[];
    shapes: any[];
    sounds: any[];
    stickers: any[];
    texts: any[];
    videos: any[];
  };
  mutable_config: null;
  name: string;
  new_version: string;
  platform: {
    app_id: number;
    app_source: string;
    app_version: string;
    device_id: string;
    hard_disk_id: string;
    mac_address: string;
    os_version: string;
    platform: string;
    screen_height: number;
    screen_width: number;
  };
  relationships: any[];
  revert_generate_segment_config: null;
  source: string;
  tracks: GeneratedTrack[];
  update_time: number;
  version: string;
}

/**
 * 扫描目录获取所有媒体文件
 */
function scanDirectory(dirPath: string): VideoFileInfo[] {
  const files: VideoFileInfo[] = [];
  
  function scanRecursive(currentPath: string) {
    try {
      const items = fs.readdirSync(currentPath);
      
      for (const item of items) {
        const fullPath = path.join(currentPath, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          // 递归扫描子目录
          scanRecursive(fullPath);
        } else if (stat.isFile()) {
          const ext = path.extname(item).toLowerCase();
          const isVideo = VIDEO_EXTENSIONS.includes(ext);
          const isAudio = AUDIO_EXTENSIONS.includes(ext);
          
          if (isVideo || isAudio) {
            files.push({
              filePath: fullPath,
              fileName: path.basename(item, ext),
              extension: ext,
              size: stat.size,
              isVideo,
              isAudio
            });
          }
        }
      }
    } catch (error) {
      console.warn(`警告: 无法访问目录 ${currentPath}:`, error instanceof Error ? error.message : String(error));
    }
  }
  
  scanRecursive(dirPath);
  return files;
}

/**
 * 检查是否安装了 ffprobe
 */
function checkFFProbe(): boolean {
  try {
    execSync('ffprobe -version', { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

/**
 * 使用 ffprobe 获取真实的视频信息
 */
function getVideoInfoWithFFProbe(filePath: string): { duration: number; width: number; height: number; hasAudio: boolean } | null {
  try {
    const command = `ffprobe -v quiet -print_format json -show_format -show_streams "${filePath}"`;
    const output = execSync(command, { encoding: 'utf-8' });
    const data = JSON.parse(output);

    let duration = 0;
    let width = 1920;
    let height = 1080;
    let hasAudio = false;

    // 获取时长
    if (data.format && data.format.duration) {
      duration = Math.floor(parseFloat(data.format.duration) * 1000000); // 转换为微秒
    }

    // 获取视频流信息
    if (data.streams) {
      for (const stream of data.streams) {
        if (stream.codec_type === 'video') {
          width = stream.width || width;
          height = stream.height || height;
        } else if (stream.codec_type === 'audio') {
          hasAudio = true;
        }
      }
    }

    return { duration, width, height, hasAudio };
  } catch (error) {
    console.warn(`警告: 无法获取文件信息 ${filePath}:`, error instanceof Error ? error.message : String(error));
    return null;
  }
}

/**
 * 获取视频文件的基本信息（优先使用 ffprobe，回退到估算）
 */
function getVideoInfo(file: VideoFileInfo, useFFProbe: boolean = true) {
  // 如果可以使用 ffprobe，尝试获取真实信息
  if (useFFProbe && checkFFProbe()) {
    const realInfo = getVideoInfoWithFFProbe(file.filePath);
    if (realInfo) {
      return realInfo;
    }
  }

  // 回退到默认估算
  const defaultWidth = 1920;
  const defaultHeight = 1080;

  // 根据文件大小粗略估算时长（这只是示例，不准确）
  const estimatedDuration = Math.max(1000000, Math.min(60000000, file.size / 1000)); // 1秒到60秒

  return {
    duration: Math.floor(estimatedDuration),
    width: defaultWidth,
    height: defaultHeight,
    hasAudio: file.isVideo // 假设视频文件都有音频
  };
}

/**
 * 生成视频素材
 */
function generateVideoClips(videoFiles: VideoFileInfo[], useFFProbe: boolean = true): GeneratedVideoClip[] {
  return videoFiles.map(file => {
    const info = getVideoInfo(file, useFFProbe);

    return {
      aigc_type: "none",
      audio_fade: null,
      cartoon_path: "",
      category_id: "",
      category_name: "",
      check_flag: 63487,
      crop: {
        lower_left_x: 0.0,
        lower_left_y: 1.0,
        lower_right_x: 1.0,
        lower_right_y: 1.0,
        upper_left_x: 0.0,
        upper_left_y: 0.0,
        upper_right_x: 1.0,
        upper_right_y: 0.0
      },
      crop_ratio: "free",
      crop_scale: 1.0,
      duration: info.duration,
      extra_type_option: 1,
      formula_id: "",
      freeze: null,
      has_audio: info.hasAudio,
      height: info.height,
      id: generateUUID().toUpperCase(),
      intensifies_audio_path: "",
      intensifies_path: "",
      is_ai_generate_content: false,
      is_copyright: false,
      is_text_edit_overdub: false,
      is_unified_beauty_mode: false,
      local_id: "",
      local_material_id: "",
      material_id: "",
      material_name: file.fileName + file.extension,
      material_url: "",
      matting: {
        flag: 0,
        has_use_quick_brush: false,
        has_use_quick_eraser: false,
        interactiveTime: [],
        path: "",
        strokes: []
      },
      media_path: "",
      object_locked: null,
      origin_material_id: "",
      path: file.filePath,
      picture_from: "none",
      picture_set_category_id: "",
      picture_set_category_name: "",
      request_id: "",
      reverse_intensifies_path: "",
      reverse_path: "",
      smart_motion: null,
      source: 0,
      source_platform: 0,
      stable: {
        matrix_path: "",
        stable_level: 0,
        time_range: {
          duration: info.duration,
          start: 0
        }
      },
      team_id: "",
      type: "video",
      video_algorithm: {
        algorithms: [],
        deflicker: null,
        motion_blur_config: null,
        noise_reduction: null,
        path: "",
        time_range: null
      },
      width: info.width
    };
  });
}

/**
 * 生成音频素材
 */
function generateAudioClips(audioFiles: VideoFileInfo[], useFFProbe: boolean = true): GeneratedAudioClip[] {
  return audioFiles.map(file => {
    const info = getVideoInfo(file, useFFProbe);

    return {
      app_id: 0,
      category_id: "",
      category_name: "",
      check_flag: 1,
      copyright_limit_type: "none",
      duration: info.duration,
      effect_id: "",
      formula_id: "",
      id: generateUUID().toUpperCase(),
      intensifies_path: "",
      is_ai_clone_tone: false,
      is_text_edit_overdub: false,
      is_ugc: false,
      local_material_id: "",
      music_id: "",
      name: file.fileName,
      path: file.filePath,
      query: "",
      request_id: "",
      resource_id: "",
      search_id: "",
      source_from: "",
      source_platform: 0,
      team_id: "",
      text_id: "",
      tone_category_id: "",
      tone_category_name: "",
      tone_effect_id: "",
      tone_effect_name: "",
      tone_platform: "",
      tone_second_category_id: "",
      tone_second_category_name: "",
      tone_speaker: "",
      tone_type: "",
      type: file.isVideo ? "video_original_sound" : "audio",
      video_id: "",
      wave_points: []
    };
  });
}

/**
 * 生成轨道和片段
 */
function generateTracks(videoClips: GeneratedVideoClip[], audioClips: GeneratedAudioClip[]): GeneratedTrack[] {
  const tracks: GeneratedTrack[] = [];
  
  // 生成主视频轨道
  if (videoClips.length > 0) {
    let currentTime = 0;
    const segments: GeneratedTrackSegment[] = [];
    
    for (const clip of videoClips) {
      segments.push({
        clip: {
          alpha: 1.0,
          flip: {
            horizontal: false,
            vertical: false
          },
          rotation: 0.0,
          scale: {
            x: 1.0,
            y: 1.0
          },
          transform: {
            x: 0.0,
            y: 0.0
          }
        },
        material_id: clip.id,
        target_timerange: {
          duration: clip.duration,
          start: currentTime
        },
        source_timerange: {
          duration: clip.duration,
          start: 0
        }
      });
      
      currentTime += clip.duration;
    }
    
    tracks.push({
      attribute: 0,
      flag: 0,
      id: generateUUID().toUpperCase(),
      segments,
      type: "video"
    });
  }
  
  // 生成音频轨道
  if (audioClips.length > 0) {
    let currentTime = 0;
    const segments: GeneratedTrackSegment[] = [];
    
    for (const clip of audioClips) {
      segments.push({
        material_id: clip.id,
        target_timerange: {
          duration: clip.duration,
          start: currentTime
        },
        source_timerange: {
          duration: clip.duration,
          start: 0
        }
      });
      
      currentTime += clip.duration;
    }
    
    tracks.push({
      attribute: 0,
      flag: 0,
      id: generateUUID().toUpperCase(),
      segments,
      type: "audio"
    });
  }
  
  return tracks;
}

/**
 * 生成完整的草稿文件
 */
function generateDraft(files: VideoFileInfo[], options: {
  canvasWidth?: number;
  canvasHeight?: number;
  fps?: number;
  projectName?: string;
  useFFProbe?: boolean;
}): GeneratedDraft {
  const videoFiles = files.filter(f => f.isVideo);
  const audioFiles = files.filter(f => f.isAudio);

  const useFFProbe = options.useFFProbe !== false; // 默认启用
  const videoClips = generateVideoClips(videoFiles, useFFProbe);
  const audioClips = generateAudioClips(audioFiles, useFFProbe);
  const tracks = generateTracks(videoClips, audioClips);
  
  // 计算总时长
  const totalDuration = Math.max(
    ...tracks.map(track => 
      track.segments.reduce((sum, seg) => Math.max(sum, seg.target_timerange.start + seg.target_timerange.duration), 0)
    ),
    0
  );
  
  const canvasWidth = options.canvasWidth || 1080;
  const canvasHeight = options.canvasHeight || 1920;
  const ratio = `${canvasWidth}:${canvasHeight}`;
  const deviceId = "auto-generated-" + Date.now();
  const currentTime = Date.now() * 1000;

  return {
    canvas_config: {
      height: canvasHeight,
      ratio: ratio,
      width: canvasWidth
    },
    color_space: 0,
    config: {
      adjust_max_index: 2,
      attachment_info: [],
      combination_max_index: 1,
      export_range: null,
      extract_audio_last_index: 1,
      lyrics_recognition_id: "",
      lyrics_sync: true,
      lyrics_taskinfo: [],
      maintrack_adsorb: true,
      material_save_mode: 0,
      multi_language_current: "none",
      multi_language_list: [],
      multi_language_main: "none",
      multi_language_mode: "none",
      original_sound_last_index: 2,
      record_audio_last_index: 1,
      sticker_max_index: 1,
      subtitle_keywords_config: null,
      subtitle_recognition_id: "",
      subtitle_sync: true,
      subtitle_taskinfo: [],
      system_font_list: [],
      text_recognition_id: "",
      text_sync: true,
      text_taskinfo: [],
      video_recognition_id: "",
      video_sync: true,
      video_taskinfo: []
    },
    create_time: currentTime,
    draft_fold_path: "",
    draft_id: generateUUID().toUpperCase(),
    draft_name: options.projectName || "Auto Generated Project",
    draft_removable_storage_device: "",
    duration: totalDuration,
    fps: options.fps || 30,
    id: generateUUID().toUpperCase(),
    last_modified_platform: {
      app_id: 3704,
      app_source: "auto-generator",
      app_version: "1.0.0",
      device_id: deviceId,
      hard_disk_id: "",
      mac_address: "",
      os_version: "auto",
      platform: "auto",
      screen_height: 1080,
      screen_width: 1920
    },
    materials: {
      audio_effects: [],
      audio_fades: [],
      audio_track_indexes: [],
      audios: audioClips,
      beats: [],
      canvases: [],
      chromas: [],
      color_curves: [],
      color_wheels: [],
      effects: [],
      flowers: [],
      handwrites: [],
      hsl: [],
      images: [],
      keyframes: [],
      masks: [],
      material_animations: [],
      placeholders: [],
      plugin_effects: [],
      shapes: [],
      sounds: [],
      stickers: [],
      texts: [],
      videos: videoClips
    },
    mutable_config: null,
    name: options.projectName || "",
    new_version: "110.0.0",
    platform: {
      app_id: 3704,
      app_source: "auto-generator",
      app_version: "1.0.0",
      device_id: deviceId,
      hard_disk_id: "",
      mac_address: "",
      os_version: "auto",
      platform: "auto",
      screen_height: 1080,
      screen_width: 1920
    },
    relationships: [],
    revert_generate_segment_config: null,
    source: "auto-generator",
    tracks,
    update_time: currentTime,
    version: "13.2.0"
  };
}

/**
 * 主函数
 */
function main(): void {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('使用方法:');
    console.log('  ts-node generate-draft.ts <扫描目录> [输出文件路径] [选项]');
    console.log('');
    console.log('示例:');
    console.log('  ts-node generate-draft.ts ./videos');
    console.log('  ts-node generate-draft.ts ./videos ./generated_draft.json');
    console.log('  ts-node generate-draft.ts ./videos ./draft.json --width=1920 --height=1080 --fps=60');
    console.log('');
    console.log('选项:');
    console.log('  --width=<数字>     画布宽度 (默认: 1080)');
    console.log('  --height=<数字>    画布高度 (默认: 1920)');
    console.log('  --fps=<数字>       帧率 (默认: 30)');
    console.log('  --name=<字符串>    项目名称');
    process.exit(1);
  }
  
  const scanDir = args[0];
  const outputPath = args[1] || './generated_draft_content.json';
  
  // 解析选项
  const options: any = {};
  for (let i = 2; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--width=')) {
      options.canvasWidth = parseInt(arg.split('=')[1]);
    } else if (arg.startsWith('--height=')) {
      options.canvasHeight = parseInt(arg.split('=')[1]);
    } else if (arg.startsWith('--fps=')) {
      options.fps = parseInt(arg.split('=')[1]);
    } else if (arg.startsWith('--name=')) {
      options.projectName = arg.split('=')[1];
    }
  }
  
  try {
    console.log(`🔍 正在扫描目录: ${scanDir}`);
    
    if (!fs.existsSync(scanDir)) {
      throw new Error(`目录不存在: ${scanDir}`);
    }
    
    const files = scanDirectory(scanDir);
    
    if (files.length === 0) {
      console.log('❌ 未找到任何媒体文件');
      process.exit(1);
    }
    
    console.log(`📁 找到 ${files.length} 个媒体文件:`);
    files.forEach((file, index) => {
      const type = file.isVideo ? '🎥' : '🎵';
      console.log(`  ${index + 1}. ${type} ${file.fileName}${file.extension} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
    });
    
    console.log('\n🚀 正在生成草稿文件...');
    const draft = generateDraft(files, options);
    
    // 保存文件
    const jsonContent = JSON.stringify(draft, null, 2);
    fs.writeFileSync(outputPath, jsonContent, 'utf-8');
    
    console.log(`\n✅ 草稿文件生成成功!`);
    console.log(`📄 输出文件: ${outputPath}`);
    console.log(`📊 项目信息:`);
    console.log(`   项目ID: ${draft.id}`);
    console.log(`   总时长: ${(draft.duration / 1000000).toFixed(2)}秒`);
    console.log(`   画布尺寸: ${draft.canvas_config.width}x${draft.canvas_config.height}`);
    console.log(`   帧率: ${draft.fps} FPS`);
    console.log(`   视频素材: ${draft.materials.videos.length}个`);
    console.log(`   音频素材: ${draft.materials.audios.length}个`);
    console.log(`   轨道数量: ${draft.tracks.length}个`);
    
    console.log('\n💡 提示: 生成的文件使用了默认的视频信息。');
    console.log('   如需准确的视频信息，建议集成 ffprobe 工具。');
    
  } catch (error) {
    console.error('❌ 生成失败:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

// 如果直接运行此脚本，执行主函数
if (require.main === module) {
  main();
}

// 导出主要函数
export {
  generateDraft,
  scanDirectory,
  checkFFProbe,
  getVideoInfoWithFFProbe,
  generateVideoClips,
  generateAudioClips,
  generateTracks
};

// 导出类型定义
export type {
  VideoFileInfo,
  GeneratedVideoClip,
  GeneratedAudioClip,
  GeneratedTrack,
  GeneratedTrackSegment,
  GeneratedDraft
};
