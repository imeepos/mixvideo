#!/usr/bin/env ts-node

/**
 * @mixvideo/jianying 基本使用示例
 */

import {
  parseJianyingDraft,
  analyzeJianyingProjectFromData,
  generateDraft,
  scanDirectory,
  JianyingUtils,
  JIANYING_CONSTANTS
} from '../src/index';
import * as path from 'path';
import * as fs from 'fs';

// 示例 1: 解析现有的剪映草稿文件
function example1_parseExistingDraft() {
  console.log('📋 示例 1: 解析剪映草稿文件');
  console.log('=' .repeat(50));
  
  const draftPath = path.join(__dirname, 'sample_draft.json');
  
  if (fs.existsSync(draftPath)) {
    try {
      // 解析草稿文件
      const videoInfo = parseJianyingDraft(draftPath);
      
      console.log(`项目ID: ${videoInfo.projectId}`);
      console.log(`时长: ${videoInfo.projectDurationSeconds} 秒`);
      console.log(`画布尺寸: ${videoInfo.canvasSize.width}x${videoInfo.canvasSize.height} (${videoInfo.canvasSize.ratio})`);
      console.log(`视频素材: ${videoInfo.videoClips.length} 个`);
      console.log(`音频素材: ${videoInfo.audioClips.length} 个`);
      console.log(`轨道: ${videoInfo.tracks.length} 个`);
      
      // 增强分析
      const analysis = analyzeJianyingProjectFromData(videoInfo);
      console.log(`\n复杂度: ${analysis.analysis.complexity.level} (评分: ${analysis.analysis.complexity.score})`);
      console.log(`建议数量: ${analysis.recommendations.length}`);
      
      if (analysis.recommendations.length > 0) {
        console.log('\n建议:');
        analysis.recommendations.forEach(rec => {
          console.log(`  • [${rec.type}] ${rec.description}`);
        });
      }
      
    } catch (error) {
      console.error('解析失败:', error instanceof Error ? error.message : String(error));
    }
  } else {
    console.log('示例草稿文件不存在，跳过此示例');
  }
}

// 示例 2: 从媒体文件生成新的草稿
function example2_generateFromMedia() {
  console.log('\n🚀 示例 2: 从媒体文件生成草稿');
  console.log('=' .repeat(50));
  
  // 创建示例媒体目录
  const mediaDir = path.join(__dirname, 'sample-media');
  if (!fs.existsSync(mediaDir)) {
    fs.mkdirSync(mediaDir, { recursive: true });
  }
  
  // 创建一些示例文件（空文件用于演示）
  const sampleFiles = [
    'intro.mp4',
    'main_content.mov',
    'background_music.mp3',
    'voice_over.wav'
  ];
  
  sampleFiles.forEach(filename => {
    const filePath = path.join(mediaDir, filename);
    if (!fs.existsSync(filePath)) {
      fs.writeFileSync(filePath, ''); // 创建空文件
    }
  });
  
  // 扫描媒体文件
  const files = scanDirectory(mediaDir);
  console.log(`扫描到 ${files.length} 个媒体文件:`);
  files.forEach(file => {
    const type = file.isVideo ? '视频' : file.isAudio ? '音频' : '未知';
    console.log(`  • ${file.fileName} (${type})`);
  });
  
  if (files.length > 0) {
    // 生成草稿
    const draft = generateDraft(files, {
      canvasWidth: JIANYING_CONSTANTS.DEFAULT_CANVAS_WIDTH,
      canvasHeight: JIANYING_CONSTANTS.DEFAULT_CANVAS_HEIGHT,
      fps: JIANYING_CONSTANTS.DEFAULT_FPS,
      projectName: '自动生成的项目',
      useFFProbe: false // 不使用 ffprobe，因为是空文件
    });
    
    // 保存生成的草稿
    const outputPath = path.join(mediaDir, 'generated_draft.json');
    fs.writeFileSync(outputPath, JSON.stringify(draft, null, 2));
    
    console.log(`\n✅ 草稿文件已生成: ${outputPath}`);
    console.log(`项目ID: ${draft.draft_id}`);
    console.log(`项目名称: ${draft.draft_name}`);
    console.log(`视频素材: ${draft.materials.videos.length} 个`);
    console.log(`音频素材: ${draft.materials.audios.length} 个`);
    console.log(`轨道: ${draft.tracks.length} 个`);
  }
}

// 示例 3: 使用工具函数
function example3_utilityFunctions() {
  console.log('\n🔧 示例 3: 工具函数使用');
  console.log('=' .repeat(50));
  
  // 时间转换
  const microseconds = 10000000; // 10秒
  const seconds = JianyingUtils.microsecondsToSeconds(microseconds);
  console.log(`时间转换: ${microseconds} 微秒 = ${seconds} 秒`);
  
  // 宽高比计算
  const ratio = JianyingUtils.calculateAspectRatio(1920, 1080);
  console.log(`宽高比: 1920x1080 = ${ratio}`);
  
  // 文件类型检查
  const testFiles = ['video.mp4', 'audio.mp3', 'image.jpg'];
  console.log('\n文件类型检查:');
  testFiles.forEach(filename => {
    const isVideo = JianyingUtils.isVideoFile(filename);
    const isAudio = JianyingUtils.isAudioFile(filename);
    const isMedia = JianyingUtils.isMediaFile(filename);
    console.log(`  ${filename}: 视频=${isVideo}, 音频=${isAudio}, 媒体=${isMedia}`);
  });
  
  // 常量使用
  console.log('\n默认常量:');
  console.log(`  默认FPS: ${JIANYING_CONSTANTS.DEFAULT_FPS}`);
  console.log(`  默认画布: ${JIANYING_CONSTANTS.DEFAULT_CANVAS_WIDTH}x${JIANYING_CONSTANTS.DEFAULT_CANVAS_HEIGHT}`);
  console.log(`  支持的视频格式: ${JianyingUtils.VIDEO_EXTENSIONS.join(', ')}`);
  console.log(`  支持的音频格式: ${JianyingUtils.AUDIO_EXTENSIONS.join(', ')}`);
}

// 运行所有示例
function runAllExamples() {
  console.log('🎬 @mixvideo/jianying 使用示例\n');
  
  example1_parseExistingDraft();
  example2_generateFromMedia();
  example3_utilityFunctions();
  
  console.log('\n✅ 所有示例运行完成!');
  console.log('\n📚 更多信息请查看 README.md 文档');
}

// 如果直接运行此脚本，执行所有示例
if (require.main === module) {
  runAllExamples();
}

export {
  example1_parseExistingDraft,
  example2_generateFromMedia,
  example3_utilityFunctions,
  runAllExamples
};
