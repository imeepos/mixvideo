#!/usr/bin/env node

import { logger, createSpinner, printAnalysisResult, printHighlights, printComparison } from './utils.js';

async function runMockAnalysis() {
  logger.title('🎬 视频分析演示 - 模拟数据');
  console.log('='.repeat(50));
  
  logger.info('使用模拟数据演示 @mixvideo/video-analyzer 的功能');
  console.log('');
  
  // 演示 1: 基础视频分析
  await demonstrateBasicAnalysis();
  
  // 演示 2: 高光时刻提取
  await demonstrateHighlightExtraction();
  
  // 演示 3: 视频对比分析
  await demonstrateVideoComparison();
  
  // 演示 4: 批量处理
  await demonstrateBatchProcessing();
  
  // 总结
  showSummary();
}

async function demonstrateBasicAnalysis() {
  logger.subtitle('\n📊 演示 1: 基础视频分析');
  console.log('分析视频: demo-video.mp4 (模拟)');
  
  const spinner = createSpinner('正在分析视频内容...');
  spinner.start();
  
  // 模拟分析过程
  await sleep(1000);
  spinner.text = '正在提取视频帧... (20%)';
  await sleep(500);
  spinner.text = '正在进行场景检测... (40%)';
  await sleep(500);
  spinner.text = '正在识别物体... (60%)';
  await sleep(500);
  spinner.text = '正在生成内容总结... (80%)';
  await sleep(500);
  spinner.text = '正在整理分析结果... (100%)';
  await sleep(300);
  
  spinner.succeed('视频分析完成!');
  
  const mockResult = {
    metadata: {
      duration: 185.7,
      width: 1920,
      height: 1080,
      fileSize: 45678912, // ~43.5MB
      format: 'mp4',
      frameRate: 30,
      bitrate: 2048
    },
    scenes: [
      {
        startTime: 0,
        endTime: 32.1,
        description: '开场动画和标题介绍',
        type: 'introduction',
        confidence: 0.94
      },
      {
        startTime: 32.1,
        endTime: 98.5,
        description: '产品功能演示和操作指南',
        type: 'demonstration',
        confidence: 0.91
      },
      {
        startTime: 98.5,
        endTime: 156.2,
        description: '用户案例分享和效果展示',
        type: 'case_study',
        confidence: 0.88
      },
      {
        startTime: 156.2,
        endTime: 185.7,
        description: '总结和行动号召',
        type: 'conclusion',
        confidence: 0.92
      }
    ],
    objects: [
      { name: '人物', confidence: 0.96, category: 'person', count: 3 },
      { name: '电脑屏幕', confidence: 0.89, category: 'electronics', count: 2 },
      { name: '办公桌', confidence: 0.85, category: 'furniture', count: 1 },
      { name: '手机', confidence: 0.82, category: 'electronics', count: 1 },
      { name: '文档', confidence: 0.78, category: 'object', count: 5 }
    ],
    summary: {
      description: '这是一个关于新产品功能介绍的营销视频。视频展示了产品的核心功能、使用方法以及实际应用案例。内容结构清晰，包含开场介绍、功能演示、案例分享和总结四个部分。',
      themes: ['产品介绍', '功能演示', '用户案例', '营销推广'],
      contentRating: {
        category: 'business',
        confidence: 0.93,
        reasons: ['商业内容', '产品展示', '专业制作']
      },
      keyPoints: [
        '产品核心功能介绍',
        '实际操作演示',
        '用户成功案例',
        '使用效果展示'
      ]
    },
    processingTime: 2800,
    analyzedAt: new Date(),
    modelVersion: 'gemini-2.0-flash-exp'
  };
  
  printAnalysisResult(mockResult);
}

async function demonstrateHighlightExtraction() {
  logger.subtitle('\n✨ 演示 2: 高光时刻提取');
  console.log('从视频中提取精彩片段...');
  
  const spinner = createSpinner('正在分析高光时刻...');
  spinner.start();
  
  await sleep(1500);
  spinner.succeed('高光时刻提取完成!');
  
  const mockHighlights = [
    {
      type: '产品亮点',
      description: '核心功能演示 - 一键智能分析',
      startTime: 45.2,
      endTime: 52.8,
      importance: 0.95,
      socialMediaReady: true,
      tags: ['功能演示', '核心卖点']
    },
    {
      type: '用户反馈',
      description: '客户满意度展示和推荐',
      startTime: 125.1,
      endTime: 135.6,
      importance: 0.88,
      socialMediaReady: true,
      tags: ['用户见证', '社会证明']
    },
    {
      type: '效果对比',
      description: '使用前后效果对比展示',
      startTime: 78.3,
      endTime: 89.7,
      importance: 0.92,
      socialMediaReady: true,
      tags: ['效果展示', '对比分析']
    },
    {
      type: '行动号召',
      description: '立即体验的呼吁和联系方式',
      startTime: 170.5,
      endTime: 180.2,
      importance: 0.85,
      socialMediaReady: false,
      tags: ['CTA', '转化引导']
    }
  ];
  
  printHighlights(mockHighlights);
}

async function demonstrateVideoComparison() {
  logger.subtitle('\n🔄 演示 3: 视频对比分析');
  console.log('对比视频: demo-video-v1.mp4 vs demo-video-v2.mp4 (模拟)');
  
  const spinner = createSpinner('正在对比分析两个视频...');
  spinner.start();
  
  await sleep(2000);
  spinner.succeed('视频对比分析完成!');
  
  const mockComparison = {
    similarity: 0.73,
    analysis: '两个视频在整体结构和内容主题上保持高度一致，但在具体的演示方式、视觉效果和时长上存在明显差异。第二版本在视觉呈现和用户体验方面有显著改进。',
    commonElements: [
      '产品核心功能介绍',
      '用户界面展示',
      '品牌标识和配色',
      '专业的旁白解说',
      '相似的音乐风格'
    ],
    differences: [
      '第二版本增加了动画效果',
      '用户案例部分更加详细',
      '视频时长从3分钟增加到3分30秒',
      '添加了更多的图表和数据展示',
      '结尾部分的行动号召更加明确'
    ],
    recommendations: [
      '保持第二版本的视觉效果',
      '可以进一步优化音频质量',
      '考虑添加字幕支持',
      '建议制作不同时长的版本'
    ]
  };
  
  printComparison(mockComparison);
}

async function demonstrateBatchProcessing() {
  logger.subtitle('\n📦 演示 4: 批量处理');
  console.log('批量分析多个视频文件...');
  
  const videos = [
    'product-intro.mp4',
    'feature-demo.mp4',
    'customer-testimonial.mp4',
    'tutorial-basic.mp4',
    'tutorial-advanced.mp4'
  ];
  
  const spinner = createSpinner('正在批量处理视频...');
  spinner.start();
  
  for (let i = 0; i < videos.length; i++) {
    const progress = Math.round(((i + 1) / videos.length) * 100);
    spinner.text = `正在处理 ${videos[i]}... (${progress}%)`;
    await sleep(800);
  }
  
  spinner.succeed('批量处理完成!');
  
  console.log('\n📊 批量处理结果:');
  console.log('='.repeat(30));
  
  const batchResults = [
    { file: 'product-intro.mp4', status: '✅ 成功', duration: '2:15', scenes: 3, objects: 8 },
    { file: 'feature-demo.mp4', status: '✅ 成功', duration: '4:32', scenes: 5, objects: 12 },
    { file: 'customer-testimonial.mp4', status: '✅ 成功', duration: '1:45', scenes: 2, objects: 4 },
    { file: 'tutorial-basic.mp4', status: '✅ 成功', duration: '6:18', scenes: 8, objects: 15 },
    { file: 'tutorial-advanced.mp4', status: '✅ 成功', duration: '9:42', scenes: 12, objects: 23 }
  ];
  
  batchResults.forEach((result, index) => {
    console.log(`${index + 1}. ${result.file}`);
    console.log(`   状态: ${result.status}`);
    console.log(`   时长: ${result.duration}`);
    console.log(`   场景: ${result.scenes} 个`);
    console.log(`   物体: ${result.objects} 个`);
    console.log('');
  });
  
  console.log('📈 统计信息:');
  console.log(`   总视频数: ${batchResults.length}`);
  console.log(`   成功处理: ${batchResults.filter(r => r.status.includes('成功')).length}`);
  console.log(`   总场景数: ${batchResults.reduce((sum, r) => sum + r.scenes, 0)}`);
  console.log(`   总物体数: ${batchResults.reduce((sum, r) => sum + r.objects, 0)}`);
}

function showSummary() {
  logger.title('\n🎉 演示完成!');
  console.log('='.repeat(50));
  
  console.log('\n✅ 已演示的功能:');
  console.log('• 📊 基础视频分析 - 场景检测、物体识别、内容总结');
  console.log('• ✨ 高光时刻提取 - 自动识别精彩片段');
  console.log('• 🔄 视频对比分析 - 相似性分析和差异对比');
  console.log('• 📦 批量处理 - 同时处理多个视频文件');
  
  console.log('\n🚀 实际使用步骤:');
  console.log('1. 获取 Gemini API Key: https://makersuite.google.com/app/apikey');
  console.log('2. 设置环境变量: export GEMINI_API_KEY="your-api-key"');
  console.log('3. 运行真实分析: npm run analyze');
  
  console.log('\n📚 更多资源:');
  console.log('• 查看源码: src/analyze.ts');
  console.log('• 阅读文档: README.md');
  console.log('• 库文档: ../video-analyzer/README.md');
  
  console.log('\n💡 提示:');
  console.log('• 支持多种视频格式 (MP4, AVI, MOV, WebM)');
  console.log('• 支持本地文件和网络URL');
  console.log('• 可自定义分析参数和语言');
  console.log('• 提供详细的进度回调');
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// 运行演示
if (import.meta.url === `file://${process.argv[1]}`) {
  runMockAnalysis().catch((error) => {
    logger.error(`演示失败: ${error.message}`);
    process.exit(1);
  });
}
