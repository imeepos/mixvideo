#!/usr/bin/env node

import { VideoAnalyzer } from '@mixvideo/video-analyzer';
import { getGeminiConfig, checkEnvironment } from './config.js';
import { logger, createSpinner, printAnalysisResult, printHighlights, printComparison } from './utils.js';
import inquirer from 'inquirer';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

async function main() {
  logger.title('🎬 视频分析演示程序');
  console.log('='.repeat(50));
  
  // 检查环境配置
  if (!checkEnvironment()) {
    process.exit(1);
  }
  
  try {
    // 创建分析器实例
    const config = getGeminiConfig();
    const analyzer = new VideoAnalyzer(config);
    logger.success('VideoAnalyzer 初始化成功');
    
    // 选择分析类型
    const { analysisType } = await inquirer.prompt([
      {
        type: 'list',
        name: 'analysisType',
        message: '请选择分析类型:',
        choices: [
          { name: '📊 基础视频分析', value: 'basic' },
          { name: '✨ 高光时刻提取', value: 'highlights' },
          { name: '🔄 视频对比分析', value: 'comparison' },
          { name: '📦 批量处理演示', value: 'batch' },
          { name: '🧪 模拟数据测试', value: 'mock' }
        ]
      }
    ]);
    
    switch (analysisType) {
      case 'basic':
        await performBasicAnalysis(analyzer);
        break;
      case 'highlights':
        await performHighlightAnalysis(analyzer);
        break;
      case 'comparison':
        await performComparisonAnalysis(analyzer);
        break;
      case 'batch':
        await performBatchAnalysis(analyzer);
        break;
      case 'mock':
        await performMockAnalysis();
        break;
    }
    
  } catch (error) {
    logger.error(`分析失败: ${(error as Error).message}`);
    process.exit(1);
  }
}

async function performBasicAnalysis(analyzer: VideoAnalyzer) {
  logger.subtitle('\n📊 基础视频分析');
  
  const { videoSource } = await inquirer.prompt([
    {
      type: 'list',
      name: 'videoSource',
      message: '请选择视频源:',
      choices: [
        { name: '📁 本地文件', value: 'file' },
        { name: '🌐 网络URL', value: 'url' },
        { name: '🧪 模拟数据', value: 'mock' }
      ]
    }
  ]);
  
  if (videoSource === 'mock') {
    return performMockAnalysis();
  }
  
  let videoInput: string;
  
  if (videoSource === 'file') {
    const { filePath } = await inquirer.prompt([
      {
        type: 'input',
        name: 'filePath',
        message: '请输入视频文件路径:',
        validate: (input) => {
          if (!input.trim()) return '请输入文件路径';
          if (!existsSync(input)) return '文件不存在';
          return true;
        }
      }
    ]);
    videoInput = filePath;
  } else {
    const { url } = await inquirer.prompt([
      {
        type: 'input',
        name: 'url',
        message: '请输入视频URL:',
        validate: (input) => {
          if (!input.trim()) return '请输入URL';
          try {
            new URL(input);
            return true;
          } catch {
            return '请输入有效的URL';
          }
        }
      }
    ]);
    videoInput = url;
  }
  
  const spinner = createSpinner('正在分析视频...');
  spinner.start();
  
  try {
    const result = await analyzer.analyzeVideo(videoInput, {
      enableSceneDetection: true,
      enableObjectDetection: true,
      enableSummarization: true,
      language: 'zh-CN',
      quality: 'medium',
      maxFrames: 20
    }, (progress) => {
      spinner.text = `正在分析视频... ${progress.step} (${progress.progress}%)`;
    });
    
    spinner.succeed('视频分析完成!');
    printAnalysisResult(result);
    
  } catch (error) {
    spinner.fail('视频分析失败');
    throw error;
  }
}

async function performHighlightAnalysis(analyzer: VideoAnalyzer) {
  logger.subtitle('\n✨ 高光时刻提取');
  
  // 这里可以添加类似的视频输入逻辑
  logger.info('高光分析功能演示 (需要实际视频文件)');
  
  // 模拟高光分析结果
  const mockHighlights = [
    {
      type: '精彩瞬间',
      description: '关键动作场景',
      startTime: 15.5,
      endTime: 18.2,
      importance: 0.9,
      socialMediaReady: true
    },
    {
      type: '情感高潮',
      description: '感人时刻',
      startTime: 45.1,
      endTime: 52.3,
      importance: 0.85,
      socialMediaReady: true
    }
  ];
  
  printHighlights(mockHighlights);
}

async function performComparisonAnalysis(analyzer: VideoAnalyzer) {
  logger.subtitle('\n🔄 视频对比分析');
  
  // 模拟对比结果
  const mockComparison = {
    similarity: 0.75,
    analysis: '两个视频在内容主题和视觉风格上有较高相似性，但在具体场景和时长上存在差异。',
    commonElements: ['人物', '室内场景', '对话'],
    differences: ['视频长度不同', '拍摄角度差异', '背景音乐风格不同']
  };
  
  printComparison(mockComparison);
}

async function performBatchAnalysis(analyzer: VideoAnalyzer) {
  logger.subtitle('\n📦 批量处理演示');
  
  logger.info('批量处理功能演示');
  console.log('');
  console.log('批量处理可以同时分析多个视频文件:');
  console.log('• 支持并发处理');
  console.log('• 实时进度跟踪');
  console.log('• 统一结果输出');
  console.log('• 错误处理和重试');
}

async function performMockAnalysis() {
  logger.subtitle('\n🧪 模拟数据测试');
  
  const spinner = createSpinner('生成模拟分析结果...');
  spinner.start();
  
  // 模拟处理时间
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  const mockResult = {
    metadata: {
      duration: 120.5,
      width: 1920,
      height: 1080,
      fileSize: 15728640, // 15MB
      format: 'mp4',
      frameRate: 30
    },
    scenes: [
      {
        startTime: 0,
        endTime: 25.3,
        description: '开场介绍场景',
        type: 'introduction',
        confidence: 0.92
      },
      {
        startTime: 25.3,
        endTime: 85.7,
        description: '主要内容展示',
        type: 'main_content',
        confidence: 0.88
      },
      {
        startTime: 85.7,
        endTime: 120.5,
        description: '总结结尾场景',
        type: 'conclusion',
        confidence: 0.90
      }
    ],
    objects: [
      { name: '人物', confidence: 0.95, category: 'person' },
      { name: '桌子', confidence: 0.87, category: 'furniture' },
      { name: '电脑', confidence: 0.82, category: 'electronics' }
    ],
    summary: {
      description: '这是一个关于产品演示的视频，包含详细的功能介绍和使用说明。',
      themes: ['教育', '技术', '演示'],
      contentRating: {
        category: 'general',
        confidence: 0.95
      }
    },
    processingTime: 2000,
    analyzedAt: new Date(),
    modelVersion: 'gemini-2.0-flash-exp'
  };
  
  spinner.succeed('模拟分析完成!');
  printAnalysisResult(mockResult);
}

// 运行主程序
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
