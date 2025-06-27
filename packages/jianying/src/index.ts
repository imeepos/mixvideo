

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

export function parse(filePath: string): JianyingDraft {
  if (!fs.existsSync(filePath)) {
    throw new Error(`文件不存在: ${filePath}`);
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  const draft: JianyingDraft = JSON.parse(content);
  return draft;
}
