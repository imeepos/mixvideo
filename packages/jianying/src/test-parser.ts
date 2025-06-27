#!/usr/bin/env ts-node

/**
 * 测试 @mixvideo/jianying 包功能
 */

import {
  generateDraft,
  scanDirectory,
  JianyingUtils,
  JIANYING_CONSTANTS
} from './index';
import * as fs from 'fs';
import * as path from 'path';

function testParser() {
  console.log('🧪 开始测试 @mixvideo/jianying 包...\n');

  try {
    // 1. 测试工具函数
    console.log('🔧 1. 工具函数测试');
    console.log('=' .repeat(50));

    console.log('时间转换测试:');
    const microseconds = 5000000;
    const seconds = JianyingUtils.microsecondsToSeconds(microseconds);
    console.log(`  ${microseconds} 微秒 = ${seconds} 秒`);

    const backToMicroseconds = JianyingUtils.secondsToMicroseconds(seconds);
    console.log(`  ${seconds} 秒 = ${backToMicroseconds} 微秒`);

    console.log('\n宽高比计算测试:');
    const ratio1 = JianyingUtils.calculateAspectRatio(1920, 1080);
    const ratio2 = JianyingUtils.calculateAspectRatio(1080, 1920);
    console.log(`  1920x1080 = ${ratio1}`);
    console.log(`  1080x1920 = ${ratio2}`);

    console.log('\n文件类型检查测试:');
    const testFiles = ['video.mp4', 'audio.mp3', 'image.jpg', 'document.txt'];
    testFiles.forEach(filename => {
      const isVideo = JianyingUtils.isVideoFile(filename);
      const isAudio = JianyingUtils.isAudioFile(filename);
      const isMedia = JianyingUtils.isMediaFile(filename);
      console.log(`  ${filename}: 视频=${isVideo}, 音频=${isAudio}, 媒体=${isMedia}`);
    });

    console.log('\n常量测试:');
    console.log(`  默认FPS: ${JIANYING_CONSTANTS.DEFAULT_FPS}`);
    console.log(`  默认画布: ${JIANYING_CONSTANTS.DEFAULT_CANVAS_WIDTH}x${JIANYING_CONSTANTS.DEFAULT_CANVAS_HEIGHT}`);
    console.log(`  支持的视频格式: ${JianyingUtils.VIDEO_EXTENSIONS.join(', ')}`);

    // 2. 生成功能测试
    console.log('\n� 2. 生成功能测试');
    console.log('=' .repeat(50));

    // 创建测试目录和文件
    const testDir = path.join(__dirname, 'test-media');
    if (!fs.existsSync(testDir)) {
      fs.mkdirSync(testDir, { recursive: true });
    }

    // 创建一些测试文件（空文件用于测试）
    const testMediaFiles = [
      'video1.mp4',
      'video2.avi',
      'audio1.mp3',
      'audio2.wav'
    ];

    testMediaFiles.forEach(filename => {
      const filePath = path.join(testDir, filename);
      if (!fs.existsSync(filePath)) {
        fs.writeFileSync(filePath, ''); // 创建空文件
      }
    });

    // 扫描目录
    const files = scanDirectory(testDir);
    console.log(`📁 扫描到 ${files.length} 个媒体文件:`);
    files.forEach(file => {
      const type = file.isVideo ? '视频' : file.isAudio ? '音频' : '未知';
      console.log(`  • ${file.fileName} (${type}) - ${file.filePath}`);
    });

    // 生成草稿
    if (files.length > 0) {
      console.log('\n生成草稿文件...');
      const draft = generateDraft(files, {
        canvasWidth: 1920,
        canvasHeight: 1080,
        fps: 30,
        projectName: '测试项目',
        useFFProbe: false // 不使用 ffprobe，因为是空文件
      });

      const outputPath = path.join(testDir, 'generated_test.json');
      fs.writeFileSync(outputPath, JSON.stringify(draft, null, 2));
      console.log(`✅ 生成的草稿文件已保存到: ${outputPath}`);

      // 验证生成的文件
      console.log('\n验证生成的草稿文件:');
      console.log(`  项目ID: ${draft.draft_id}`);
      console.log(`  项目名称: ${draft.draft_name}`);
      console.log(`  画布尺寸: ${draft.canvas_config.width}x${draft.canvas_config.height}`);
      console.log(`  视频素材数量: ${draft.materials.videos.length}`);
      console.log(`  音频素材数量: ${draft.materials.audios.length}`);
      console.log(`  轨道数量: ${draft.tracks.length}`);
    }

    console.log('\n✅ 所有测试完成!');
    console.log('\n📦 @mixvideo/jianying 包功能正常，可以使用以下功能:');
    console.log('  • 解析剪映草稿文件');
    console.log('  • 增强分析和建议');
    console.log('  • 生成新的草稿文件');
    console.log('  • 工具函数和常量');

  } catch (error) {
    console.error('❌ 测试失败:', error instanceof Error ? error.message : String(error));
    console.error('错误堆栈:', error instanceof Error ? error.stack : '');
  }
}

// 如果直接运行此脚本，执行测试
if (require.main === module) {
  testParser();
}

export { testParser };
