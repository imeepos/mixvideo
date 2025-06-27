/**
 * 离线演示 @mixvideo/video-analyzer 库的基本功能
 * 不需要 API Key，只演示库的结构和接口
 */

const { VideoAnalyzer, FrameExtractor, VideoProcessor, PromptBuilder } = require('./dist/index.js');

function demo() {
  console.log('🎬 Video Analyzer 离线演示');
  console.log('============================\n');

  try {
    // 1. 演示创建 VideoAnalyzer 实例
    console.log('1️⃣  创建 VideoAnalyzer 实例:');
    const analyzer = new VideoAnalyzer({
      apiKey: 'demo-key',
      model: 'gemini-2.0-flash-exp'
    });
    console.log('✅ VideoAnalyzer 实例创建成功');
    console.log('   - 类型:', typeof analyzer);
    console.log('   - 构造函数:', analyzer.constructor.name);
    console.log('');

    // 2. 演示 FrameExtractor
    console.log('2️⃣  FrameExtractor 工具类:');
    const frameExtractor = new FrameExtractor();
    console.log('✅ FrameExtractor 实例创建成功');
    console.log('   - 类型:', typeof frameExtractor);
    console.log('   - 构造函数:', frameExtractor.constructor.name);
    console.log('   - 可用方法:', Object.getOwnPropertyNames(Object.getPrototypeOf(frameExtractor)).filter(name => name !== 'constructor'));
    console.log('');

    // 3. 演示 VideoProcessor
    console.log('3️⃣  VideoProcessor 工具类:');
    const videoProcessor = new VideoProcessor();
    console.log('✅ VideoProcessor 实例创建成功');
    console.log('   - 类型:', typeof videoProcessor);
    console.log('   - 构造函数:', videoProcessor.constructor.name);
    console.log('   - 可用方法:', Object.getOwnPropertyNames(Object.getPrototypeOf(videoProcessor)).filter(name => name !== 'constructor'));
    console.log('');

    // 4. 演示 PromptBuilder
    console.log('4️⃣  PromptBuilder 工具类:');
    const promptBuilder = new PromptBuilder();
    console.log('✅ PromptBuilder 实例创建成功');
    console.log('   - 类型:', typeof promptBuilder);
    console.log('   - 构造函数:', promptBuilder.constructor.name);
    console.log('   - 可用方法:', Object.getOwnPropertyNames(Object.getPrototypeOf(promptBuilder)).filter(name => name !== 'constructor'));
    console.log('');

    // 5. 演示提示词构建
    console.log('5️⃣  提示词构建演示:');
    try {
      const basePrompt = promptBuilder.getBasePrompt('zh-CN');
      console.log('✅ 基础提示词构建成功');
      console.log('   - 长度:', basePrompt.length, '字符');
      console.log('   - 预览:', basePrompt.substring(0, 100) + '...');
      console.log('');
    } catch (error) {
      console.log('⚠️  提示词构建需要完整的参数，跳过演示');
      console.log('');
    }

    // 6. 演示 VideoAnalyzer 方法
    console.log('6️⃣  VideoAnalyzer 可用方法:');
    const analyzerMethods = Object.getOwnPropertyNames(Object.getPrototypeOf(analyzer))
      .filter(name => name !== 'constructor' && typeof analyzer[name] === 'function');
    
    analyzerMethods.forEach(method => {
      console.log(`   - ${method}()`);
    });
    console.log('');

    // 7. 演示类型定义
    console.log('7️⃣  TypeScript 类型支持:');
    console.log('✅ 库提供完整的 TypeScript 类型定义');
    console.log('   - VideoAnalysisResult');
    console.log('   - AnalysisOptions');
    console.log('   - GeminiConfig');
    console.log('   - VideoMetadata');
    console.log('   - SceneDetection');
    console.log('   - ObjectDetection');
    console.log('   - VideoSummary');
    console.log('   - HighlightDetection');
    console.log('   - VideoComparison');
    console.log('');

    // 8. 演示错误处理
    console.log('8️⃣  错误处理:');
    console.log('✅ 库提供自定义错误类型');
    console.log('   - VideoAnalyzerError');
    console.log('   - 错误代码常量 (ERROR_CODES)');
    console.log('   - 详细错误信息和上下文');
    console.log('');

    // 9. 演示配置选项
    console.log('9️⃣  配置选项:');
    const defaultConfig = {
      apiKey: 'your-api-key',
      model: 'gemini-2.0-flash-exp',
      maxRetries: 3,
      timeout: 30000,
      baseURL: 'https://generativelanguage.googleapis.com'
    };
    
    console.log('✅ 支持的配置选项:');
    Object.entries(defaultConfig).forEach(([key, value]) => {
      console.log(`   - ${key}: ${typeof value} (默认: ${value})`);
    });
    console.log('');

    // 10. 演示分析选项
    console.log('🔟 分析选项:');
    const analysisOptions = {
      enableSceneDetection: true,
      enableObjectDetection: true,
      enableSummarization: true,
      frameSamplingInterval: 2,
      maxFrames: 30,
      quality: 'medium',
      language: 'zh-CN',
      customPrompt: '自定义分析提示词'
    };
    
    console.log('✅ 支持的分析选项:');
    Object.entries(analysisOptions).forEach(([key, value]) => {
      console.log(`   - ${key}: ${typeof value} (示例: ${value})`);
    });
    console.log('');

    console.log('🎉 演示完成！');
    console.log('');
    console.log('📚 接下来的步骤:');
    console.log('1. 获取 Gemini API Key: https://makersuite.google.com/app/apikey');
    console.log('2. 设置环境变量: export GEMINI_API_KEY="your-api-key"');
    console.log('3. 运行完整演示: node demo.js');
    console.log('4. 查看使用示例: cat examples/basic-usage.ts');
    console.log('5. 阅读使用指南: cat USAGE.md');

  } catch (error) {
    console.error('❌ 演示失败:', error.message);
    console.error('   堆栈:', error.stack);
  }
}

// 运行演示
demo();
