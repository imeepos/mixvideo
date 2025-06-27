import chalk from 'chalk';
import ora from 'ora';

export const logger = {
  info: (message: string) => console.log(chalk.blue('ℹ'), message),
  success: (message: string) => console.log(chalk.green('✅'), message),
  warning: (message: string) => console.log(chalk.yellow('⚠️'), message),
  error: (message: string) => console.log(chalk.red('❌'), message),
  title: (message: string) => console.log(chalk.bold.cyan(message)),
  subtitle: (message: string) => console.log(chalk.bold(message)),
};

export const createSpinner = (text: string) => {
  return ora({
    text,
    spinner: 'dots',
    color: 'cyan'
  });
};

export const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

export const formatFileSize = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`;
};

export const printHighlights = (highlights: any[]) => {
  logger.title('\n✨ 高光时刻');
  console.log('='.repeat(50));

  if (highlights.length === 0) {
    logger.warning('未检测到高光时刻');
    return;
  }

  highlights.forEach((highlight, index) => {
    console.log(`\n${index + 1}. ${highlight.type}: ${highlight.description}`);
    console.log(`   时间: ${formatDuration(highlight.startTime)} - ${formatDuration(highlight.endTime)}`);
    console.log(`   重要性: ${(highlight.importance * 100).toFixed(1)}%`);
    console.log(`   社交媒体适用: ${highlight.socialMediaReady ? '✅' : '❌'}`);
  });
};

export const printComparison = (comparison: any) => {
  logger.title('\n🔄 视频对比结果');
  console.log('='.repeat(50));

  console.log(`\n相似度: ${(comparison.similarity * 100).toFixed(1)}%`);
  console.log(`\n分析: ${comparison.analysis}`);

  if (comparison.commonElements && comparison.commonElements.length > 0) {
    logger.subtitle('\n🔗 共同元素:');
    comparison.commonElements.forEach((element: string) => {
      console.log(`   • ${element}`);
    });
  }

  if (comparison.differences && comparison.differences.length > 0) {
    logger.subtitle('\n🔀 主要差异:');
    comparison.differences.forEach((diff: string) => {
      console.log(`   • ${diff}`);
    });
  }
};

export const printAnalysisResult = (result: any) => {
  logger.title('\n🎬 视频分析结果');
  console.log('='.repeat(50));
  
  // 基本信息
  logger.subtitle('\n📊 基本信息:');
  console.log(`   时长: ${formatDuration(result.metadata.duration)}`);
  console.log(`   分辨率: ${result.metadata.width}x${result.metadata.height}`);
  console.log(`   文件大小: ${formatFileSize(result.metadata.fileSize)}`);
  console.log(`   格式: ${result.metadata.format}`);
  
  // 场景分析
  if (result.scenes && result.scenes.length > 0) {
    logger.subtitle('\n🎭 场景分析:');
    result.scenes.forEach((scene: any, index: number) => {
      console.log(`   ${index + 1}. ${scene.description}`);
      console.log(`      时间: ${formatDuration(scene.startTime)} - ${formatDuration(scene.endTime)}`);
      console.log(`      类型: ${scene.type} | 置信度: ${(scene.confidence * 100).toFixed(1)}%`);
    });
  }
  
  // 物体检测
  if (result.objects && result.objects.length > 0) {
    logger.subtitle('\n🔍 检测到的物体:');
    const objectCounts = result.objects.reduce((acc: any, obj: any) => {
      acc[obj.name] = (acc[obj.name] || 0) + 1;
      return acc;
    }, {});
    
    Object.entries(objectCounts).forEach(([name, count]) => {
      console.log(`   ${name}: ${count} 次`);
    });
  }
  
  // 内容总结
  if (result.summary) {
    logger.subtitle('\n📝 内容总结:');
    console.log(`   ${result.summary.description}`);
    
    if (result.summary.themes && result.summary.themes.length > 0) {
      console.log(`   主题: ${result.summary.themes.join(', ')}`);
    }
    
    if (result.summary.contentRating) {
      console.log(`   内容评级: ${result.summary.contentRating.category}`);
    }
  }
  
  // 处理信息
  logger.subtitle('\n⚡ 处理信息:');
  console.log(`   处理时间: ${(result.processingTime / 1000).toFixed(2)} 秒`);
  console.log(`   分析时间: ${new Date(result.analyzedAt).toLocaleString()}`);
  console.log(`   模型版本: ${result.modelVersion}`);
};
