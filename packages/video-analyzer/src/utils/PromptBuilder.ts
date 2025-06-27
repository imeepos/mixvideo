import { VideoMetadata, AnalysisOptions } from '../types';

/**
 * Utility class for building prompts for Gemini analysis
 */
export class PromptBuilder {
  /**
   * Build comprehensive analysis prompt
   */
  buildAnalysisPrompt(metadata: VideoMetadata, options: AnalysisOptions): string {
    const language = options.language || 'zh-CN';
    const customPrompt = options.customPrompt;
    
    if (customPrompt) {
      return this.buildCustomPrompt(customPrompt, metadata, language);
    }

    const basePrompt = this.getBasePrompt(language);
    const metadataInfo = this.formatMetadataInfo(metadata, language);
    const analysisInstructions = this.buildAnalysisInstructions(options, language);
    
    return `${basePrompt}\n\n${metadataInfo}\n\n${analysisInstructions}`;
  }

  /**
   * Build highlight detection prompt
   */
  buildHighlightPrompt(language: string = 'zh-CN'): string {
    if (language === 'zh-CN') {
      return `
请分析这些视频帧，识别出最精彩的高光时刻。对于每个高光时刻，请提供：

1. 开始和结束时间
2. 高光类型（动作、情感、视觉效果、音频、转场等）
3. 详细描述
4. 重要性评分（0-1）
5. 是否适合社交媒体分享

请以JSON格式返回结果：
\`\`\`json
{
  "highlights": [
    {
      "startTime": 0.0,
      "endTime": 5.0,
      "type": "action",
      "description": "精彩的动作场面",
      "importance": 0.9,
      "socialMediaReady": true
    }
  ]
}
\`\`\`
`;
    } else {
      return `
Please analyze these video frames to identify the most exciting highlight moments. For each highlight, provide:

1. Start and end time
2. Highlight type (action, emotional, visual, audio, transition, etc.)
3. Detailed description
4. Importance score (0-1)
5. Whether it's suitable for social media sharing

Please return results in JSON format:
\`\`\`json
{
  "highlights": [
    {
      "startTime": 0.0,
      "endTime": 5.0,
      "type": "action",
      "description": "Exciting action sequence",
      "importance": 0.9,
      "socialMediaReady": true
    }
  ]
}
\`\`\`
`;
    }
  }

  /**
   * Build video comparison prompt
   */
  buildComparisonPrompt(language: string = 'zh-CN'): string {
    if (language === 'zh-CN') {
      return `
请比较这两个视频的相似性。分析以下方面：

1. 视觉内容相似度
2. 场景和构图
3. 色彩和风格
4. 主题和内容
5. 整体相似性评分（0-1）

请以JSON格式返回结果：
\`\`\`json
{
  "similarity": 0.75,
  "analysis": "详细的比较分析...",
  "commonElements": ["相同的场景", "相似的色彩"],
  "differences": ["不同的主角", "不同的情节"]
}
\`\`\`
`;
    } else {
      return `
Please compare the similarity between these two videos. Analyze the following aspects:

1. Visual content similarity
2. Scenes and composition
3. Colors and style
4. Themes and content
5. Overall similarity score (0-1)

Please return results in JSON format:
\`\`\`json
{
  "similarity": 0.75,
  "analysis": "Detailed comparison analysis...",
  "commonElements": ["Same scenes", "Similar colors"],
  "differences": ["Different characters", "Different plot"]
}
\`\`\`
`;
    }
  }

  /**
   * Get base analysis prompt
   */
  private getBasePrompt(language: string): string {
    if (language === 'zh-CN') {
      return `
你是一个专业的视频分析AI助手。请仔细分析提供的视频帧，并提供详细的分析报告。

请分析以下内容：
1. 场景检测和描述
2. 物体识别和定位
3. 视频内容总结
4. 关键时刻识别
5. 情感和氛围分析
6. 内容分类和评级

请确保分析结果准确、详细且有用。
`;
    } else {
      return `
You are a professional video analysis AI assistant. Please carefully analyze the provided video frames and provide a detailed analysis report.

Please analyze the following content:
1. Scene detection and description
2. Object recognition and localization
3. Video content summary
4. Key moment identification
5. Emotion and atmosphere analysis
6. Content classification and rating

Please ensure the analysis results are accurate, detailed, and useful.
`;
    }
  }

  /**
   * Format metadata information
   */
  private formatMetadataInfo(metadata: VideoMetadata, language: string): string {
    if (language === 'zh-CN') {
      return `
视频信息：
- 文件名：${metadata.filename}
- 时长：${this.formatDuration(metadata.duration)}
- 分辨率：${metadata.width}x${metadata.height}
- 帧率：${metadata.frameRate} fps
- 格式：${metadata.format}
- 文件大小：${this.formatFileSize(metadata.fileSize)}
`;
    } else {
      return `
Video Information:
- Filename: ${metadata.filename}
- Duration: ${this.formatDuration(metadata.duration)}
- Resolution: ${metadata.width}x${metadata.height}
- Frame Rate: ${metadata.frameRate} fps
- Format: ${metadata.format}
- File Size: ${this.formatFileSize(metadata.fileSize)}
`;
    }
  }

  /**
   * Build analysis instructions based on options
   */
  private buildAnalysisInstructions(options: AnalysisOptions, language: string): string {
    const instructions: string[] = [];
    
    if (language === 'zh-CN') {
      instructions.push('请以JSON格式返回分析结果，包含以下结构：');
      
      if (options.enableSceneDetection !== false) {
        instructions.push(`
"scenes": [
  {
    "startTime": 0.0,
    "endTime": 5.0,
    "duration": 5.0,
    "description": "场景描述",
    "type": "场景类型",
    "confidence": 0.9,
    "objects": ["检测到的物体"],
    "mood": "情绪/氛围"
  }
]`);
      }

      if (options.enableObjectDetection !== false) {
        instructions.push(`
"objects": [
  {
    "name": "物体名称",
    "confidence": 0.9,
    "boundingBox": {"x": 0, "y": 0, "width": 100, "height": 100},
    "timestamp": 2.5,
    "category": "物体类别"
  }
]`);
      }

      if (options.enableSummarization !== false) {
        instructions.push(`
"summary": {
  "description": "视频整体描述",
  "themes": ["主题1", "主题2"],
  "keyMoments": [
    {"timestamp": 10.0, "description": "关键时刻描述", "importance": 0.8}
  ],
  "emotions": [
    {"timestamp": 5.0, "emotion": "情感", "intensity": 0.7}
  ],
  "contentRating": {
    "category": "内容分类",
    "reasons": ["分类原因"],
    "confidence": 0.9
  }
}`);
      }
    } else {
      instructions.push('Please return analysis results in JSON format with the following structure:');
      
      if (options.enableSceneDetection !== false) {
        instructions.push(`
"scenes": [
  {
    "startTime": 0.0,
    "endTime": 5.0,
    "duration": 5.0,
    "description": "Scene description",
    "type": "Scene type",
    "confidence": 0.9,
    "objects": ["Detected objects"],
    "mood": "Mood/atmosphere"
  }
]`);
      }

      if (options.enableObjectDetection !== false) {
        instructions.push(`
"objects": [
  {
    "name": "Object name",
    "confidence": 0.9,
    "boundingBox": {"x": 0, "y": 0, "width": 100, "height": 100},
    "timestamp": 2.5,
    "category": "Object category"
  }
]`);
      }

      if (options.enableSummarization !== false) {
        instructions.push(`
"summary": {
  "description": "Overall video description",
  "themes": ["Theme1", "Theme2"],
  "keyMoments": [
    {"timestamp": 10.0, "description": "Key moment description", "importance": 0.8}
  ],
  "emotions": [
    {"timestamp": 5.0, "emotion": "Emotion", "intensity": 0.7}
  ],
  "contentRating": {
    "category": "Content category",
    "reasons": ["Classification reasons"],
    "confidence": 0.9
  }
}`);
      }
    }

    return instructions.join('\n\n');
  }

  /**
   * Build custom prompt
   */
  private buildCustomPrompt(customPrompt: string, metadata: VideoMetadata, language: string): string {
    const metadataInfo = this.formatMetadataInfo(metadata, language);
    return `${customPrompt}\n\n${metadataInfo}`;
  }

  /**
   * Format duration
   */
  private formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
      return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
  }

  /**
   * Format file size
   */
  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '未知';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
}
