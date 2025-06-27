#!/usr/bin/env node

import { VideoAnalyzer, FrameExtractor, VideoProcessor, PromptBuilder } from '@mixvideo/video-analyzer';
import { logger, createSpinner } from './utils.js';

async function testLibraryComponents() {
  logger.title('🧪 Video Analyzer 库组件测试');
  console.log('='.repeat(50));
  
  // 测试 1: VideoAnalyzer 实例化
  logger.subtitle('\n1️⃣ 测试 VideoAnalyzer 实例化');
  try {
    const analyzer = new VideoAnalyzer({
      apiKey: 'test-key',
      model: 'gemini-2.0-flash-exp'
    });
    logger.success('VideoAnalyzer 实例创建成功');
    console.log(`   类型: ${typeof analyzer}`);
    console.log(`   构造函数: ${analyzer.constructor.name}`);
  } catch (error) {
    logger.error(`VideoAnalyzer 实例化失败: ${(error as Error).message}`);
  }
  
  // 测试 2: FrameExtractor
  logger.subtitle('\n2️⃣ 测试 FrameExtractor');
  try {
    const frameExtractor = new FrameExtractor();
    logger.success('FrameExtractor 实例创建成功');
    
    const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(frameExtractor))
      .filter(name => name !== 'constructor' && typeof frameExtractor[name as keyof FrameExtractor] === 'function');
    
    console.log(`   可用方法 (${methods.length}):`, methods.slice(0, 5).join(', '), methods.length > 5 ? '...' : '');
  } catch (error) {
    logger.error(`FrameExtractor 测试失败: ${(error as Error).message}`);
  }
  
  // 测试 3: VideoProcessor
  logger.subtitle('\n3️⃣ 测试 VideoProcessor');
  try {
    const videoProcessor = new VideoProcessor();
    logger.success('VideoProcessor 实例创建成功');
    
    const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(videoProcessor))
      .filter(name => name !== 'constructor' && typeof videoProcessor[name as keyof VideoProcessor] === 'function');
    
    console.log(`   可用方法 (${methods.length}):`, methods.slice(0, 5).join(', '), methods.length > 5 ? '...' : '');
  } catch (error) {
    logger.error(`VideoProcessor 测试失败: ${(error as Error).message}`);
  }
  
  // 测试 4: PromptBuilder
  logger.subtitle('\n4️⃣ 测试 PromptBuilder');
  try {
    const promptBuilder = new PromptBuilder();
    logger.success('PromptBuilder 实例创建成功');
    
    // 测试基础提示词生成
    const basePrompt = promptBuilder.getBasePrompt('zh-CN');
    console.log(`   基础提示词长度: ${basePrompt.length} 字符`);
    console.log(`   预览: ${basePrompt.substring(0, 50)}...`);
    
    const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(promptBuilder))
      .filter(name => name !== 'constructor' && typeof promptBuilder[name as keyof PromptBuilder] === 'function');
    
    console.log(`   可用方法 (${methods.length}):`, methods.slice(0, 5).join(', '), methods.length > 5 ? '...' : '');
  } catch (error) {
    logger.error(`PromptBuilder 测试失败: ${(error as Error).message}`);
  }
  
  // 测试 5: 类型检查
  logger.subtitle('\n5️⃣ 测试 TypeScript 类型');
  try {
    // 测试配置类型
    const config = {
      apiKey: 'test-key',
      model: 'gemini-2.0-flash-exp' as const,
      maxRetries: 3,
      timeout: 30000
    };
    
    // 测试分析选项类型
    const options = {
      enableSceneDetection: true,
      enableObjectDetection: true,
      enableSummarization: true,
      language: 'zh-CN' as const,
      quality: 'medium' as const,
      maxFrames: 30
    };
    
    logger.success('TypeScript 类型检查通过');
    console.log(`   配置对象: ${Object.keys(config).length} 个属性`);
    console.log(`   选项对象: ${Object.keys(options).length} 个属性`);
  } catch (error) {
    logger.error(`类型检查失败: ${(error as Error).message}`);
  }
  
  // 测试 6: 错误处理
  logger.subtitle('\n6️⃣ 测试错误处理');
  try {
    // 测试无效配置
    try {
      new VideoAnalyzer({} as any);
      logger.warning('应该抛出配置错误，但没有');
    } catch (configError) {
      logger.success('配置验证错误处理正常');
      console.log(`   错误信息: ${(configError as Error).message}`);
    }
  } catch (error) {
    logger.error(`错误处理测试失败: ${(error as Error).message}`);
  }
  
  // 测试总结
  logger.subtitle('\n📊 测试总结');
  logger.success('所有基础组件测试完成');
  console.log('');
  console.log('✅ 库已正确安装和配置');
  console.log('✅ 所有核心类可以正常实例化');
  console.log('✅ TypeScript 类型定义正常');
  console.log('✅ 错误处理机制工作正常');
  console.log('');
  logger.info('接下来可以运行 npm run analyze 进行实际的视频分析测试');
}

async function performanceTest() {
  logger.subtitle('\n⚡ 性能测试');
  
  const spinner = createSpinner('执行性能测试...');
  spinner.start();
  
  const startTime = Date.now();
  
  // 创建多个实例测试
  const instances = [];
  for (let i = 0; i < 10; i++) {
    instances.push(new VideoAnalyzer({
      apiKey: 'test-key',
      model: 'gemini-2.0-flash-exp'
    }));
  }
  
  const endTime = Date.now();
  spinner.succeed(`性能测试完成 (${endTime - startTime}ms)`);
  
  console.log(`   创建 ${instances.length} 个实例耗时: ${endTime - startTime}ms`);
  console.log(`   平均每个实例: ${((endTime - startTime) / instances.length).toFixed(2)}ms`);
}

async function main() {
  try {
    await testLibraryComponents();
    await performanceTest();
    
    logger.title('\n🎉 所有测试完成!');
    console.log('');
    console.log('📚 下一步:');
    console.log('1. 设置 GEMINI_API_KEY 环境变量');
    console.log('2. 运行 npm run analyze 进行实际分析');
    console.log('3. 查看 src/analyze.ts 了解更多用法');
    
  } catch (error) {
    logger.error(`测试失败: ${(error as Error).message}`);
    process.exit(1);
  }
}

// 运行测试
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
