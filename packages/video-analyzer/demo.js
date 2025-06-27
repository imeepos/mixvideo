/**
 * 演示如何使用 @mixvideo/video-analyzer 库
 * 
 * 使用方法:
 * 1. 设置环境变量 GEMINI_API_KEY
 * 2. 运行: node demo.js
 */

const { VideoAnalyzer, createVideoAnalyzer } = require('./dist/index.js');

async function demo() {
  console.log('🎬 Video Analyzer Demo');
  console.log('======================\n');

  // 检查API Key
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    console.error('❌ 请设置环境变量 GEMINI_API_KEY');
    console.log('   export GEMINI_API_KEY="your-api-key"');
    process.exit(1);
  }

  try {
    // 创建分析器实例
    console.log('📝 创建 VideoAnalyzer 实例...');
    const analyzer = createVideoAnalyzer({
      apiKey: apiKey,
      model: 'gemini-2.0-flash-exp',
      maxRetries: 3,
      timeout: 30000
    });
    console.log('✅ VideoAnalyzer 创建成功\n');

    // 演示配置信息
    console.log('⚙️  配置信息:');
    console.log(`   - 模型: gemini-2.0-flash-exp`);
    console.log(`   - 最大重试次数: 3`);
    console.log(`   - 超时时间: 30秒`);
    console.log(`   - API Key: ${apiKey.substring(0, 10)}...`);
    console.log('');

    // 演示分析选项
    console.log('🔧 分析选项示例:');
    const analysisOptions = {
      enableSceneDetection: true,
      enableObjectDetection: true,
      enableSummarization: true,
      frameSamplingInterval: 2,
      maxFrames: 30,
      quality: 'medium',
      language: 'zh-CN'
    };
    
    console.log('   - 场景检测: ✅');
    console.log('   - 物体识别: ✅');
    console.log('   - 内容总结: ✅');
    console.log('   - 帧采样间隔: 2秒');
    console.log('   - 最大帧数: 30');
    console.log('   - 质量: 中等');
    console.log('   - 语言: 中文');
    console.log('');

    // 演示使用方法
    console.log('📖 使用方法示例:');
    console.log('');
    
    console.log('1️⃣  基础视频分析:');
    console.log(`
const result = await analyzer.analyzeVideo(videoFile, {
  enableSceneDetection: true,
  enableObjectDetection: true,
  enableSummarization: true,
  language: 'zh-CN'
});

console.log('场景数量:', result.scenes.length);
console.log('检测到的物体:', result.objects.length);
console.log('内容总结:', result.summary.description);
    `);

    console.log('2️⃣  高光时刻提取:');
    console.log(`
const highlights = await analyzer.extractHighlights(videoFile, {
  language: 'zh-CN'
});

highlights.forEach(highlight => {
  console.log(\`\${highlight.type}: \${highlight.description}\`);
  console.log(\`时间: \${highlight.startTime}s - \${highlight.endTime}s\`);
});
    `);

    console.log('3️⃣  视频对比:');
    console.log(`
const comparison = await analyzer.compareVideos(video1, video2, {
  language: 'zh-CN'
});

console.log(\`相似度: \${comparison.similarity * 100}%\`);
console.log(\`分析: \${comparison.analysis}\`);
    `);

    console.log('4️⃣  批量处理:');
    console.log(`
const videos = [
  { input: video1File, id: 'video1' },
  { input: video2File, id: 'video2' }
];

const results = await analyzer.analyzeBatch(videos, {
  quality: 'medium'
}, (progress) => {
  console.log(\`进度: \${progress.progress}%\`);
});
    `);

    console.log('✨ 库已成功初始化，可以开始分析视频了！');
    console.log('');
    console.log('📚 更多使用示例请查看:');
    console.log('   - examples/basic-usage.ts');
    console.log('   - examples/react-component.tsx');
    console.log('   - USAGE.md');

  } catch (error) {
    console.error('❌ 演示失败:', error.message);
    process.exit(1);
  }
}

// 运行演示
demo().catch(console.error);
