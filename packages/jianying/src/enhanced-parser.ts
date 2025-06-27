#!/usr/bin/env ts-node

/**
 * 增强版剪映草稿文件解析器
 * 提供更多分析功能和可视化输出
 */

import { parseJianyingDraft, VideoInfo } from './parse-draft';
import * as fs from 'fs';
import * as path from 'path';

interface EnhancedAnalysis {
  basicInfo: VideoInfo;
  analysis: {
    complexity: {
      score: number;
      level: 'Simple' | 'Medium' | 'Complex' | 'Very Complex';
      factors: string[];
    };
    timeline: {
      totalDuration: number;
      segmentCount: number;
      averageSegmentLength: number;
      shortestSegment: number;
      longestSegment: number;
    };
    materials: {
      videoFileUsage: Array<{
        filePath: string;
        usageCount: number;
        totalDuration: number;
        segments: Array<{
          trackId: string;
          startTime: number;
          duration: number;
        }>;
      }>;
      audioFileUsage: Array<{
        filePath: string;
        usageCount: number;
        totalDuration: number;
      }>;
    };
    editing: {
      hasTransformations: boolean;
      hasScaling: boolean;
      hasRotation: boolean;
      hasPositionChanges: boolean;
      hasFlipping: boolean;
      transformationCount: number;
    };
  };
  recommendations: Array<{
    type: string;
    description: string;
  }>;
}

/**
 * 计算项目复杂度
 */
function calculateComplexity(info: VideoInfo): EnhancedAnalysis['analysis']['complexity'] {
  let score = 0;
  const factors: string[] = [];

  // 基于轨道数量
  if (info.tracks.length > 3) {
    score += 20;
    factors.push(`多轨道编辑 (${info.tracks.length}个轨道)`);
  }

  // 基于片段数量
  const totalSegments = info.statistics.totalSegments;
  if (totalSegments > 20) {
    score += 30;
    factors.push(`大量片段 (${totalSegments}个片段)`);
  } else if (totalSegments > 10) {
    score += 15;
    factors.push(`中等片段数量 (${totalSegments}个片段)`);
  }

  // 基于素材数量
  if (info.statistics.totalVideoClips > 10) {
    score += 20;
    factors.push(`多个视频素材 (${info.statistics.totalVideoClips}个)`);
  }

  // 基于变换复杂度
  let transformationCount = 0;
  info.tracks.forEach(track => {
    track.segments.forEach(segment => {
      if (segment.transform.rotation !== 0) transformationCount++;
      if (segment.transform.scale.x !== 1 || segment.transform.scale.y !== 1) transformationCount++;
      if (segment.transform.position.x !== 0 || segment.transform.position.y !== 0) transformationCount++;
      if (segment.transform.flip.horizontal || segment.transform.flip.vertical) transformationCount++;
    });
  });

  if (transformationCount > 10) {
    score += 25;
    factors.push(`复杂变换 (${transformationCount}个变换)`);
  } else if (transformationCount > 5) {
    score += 10;
    factors.push(`中等变换 (${transformationCount}个变换)`);
  }

  // 基于时长
  if (info.projectDurationSeconds > 300) { // 5分钟以上
    score += 15;
    factors.push(`长视频 (${info.projectDurationSeconds}秒)`);
  }

  let level: EnhancedAnalysis['analysis']['complexity']['level'];
  if (score >= 70) level = 'Very Complex';
  else if (score >= 50) level = 'Complex';
  else if (score >= 30) level = 'Medium';
  else level = 'Simple';

  return { score, level, factors };
}

/**
 * 分析时间轴信息
 */
function analyzeTimeline(info: VideoInfo): EnhancedAnalysis['analysis']['timeline'] {
  const allSegments = info.tracks.flatMap(track => track.segments);
  const durations = allSegments.map(seg => seg.timeRange.durationSeconds);
  
  return {
    totalDuration: info.projectDurationSeconds,
    segmentCount: allSegments.length,
    averageSegmentLength: durations.reduce((a, b) => a + b, 0) / durations.length,
    shortestSegment: Math.min(...durations),
    longestSegment: Math.max(...durations)
  };
}

/**
 * 分析素材使用情况
 */
function analyzeMaterials(info: VideoInfo): EnhancedAnalysis['analysis']['materials'] {
  // 分析视频文件使用情况
  const videoFileUsage = new Map<string, {
    usageCount: number;
    totalDuration: number;
    segments: Array<{ trackId: string; startTime: number; duration: number; }>;
  }>();

  info.tracks.forEach(track => {
    track.segments.forEach(segment => {
      // 通过素材ID找到对应的视频文件
      const videoClip = info.videoClips.find(clip => clip.id === segment.materialId);
      if (videoClip) {
        const filePath = videoClip.filePath;
        if (!videoFileUsage.has(filePath)) {
          videoFileUsage.set(filePath, { usageCount: 0, totalDuration: 0, segments: [] });
        }
        const usage = videoFileUsage.get(filePath)!;
        usage.usageCount++;
        usage.totalDuration += segment.timeRange.durationSeconds;
        usage.segments.push({
          trackId: track.id,
          startTime: segment.timeRange.startSeconds,
          duration: segment.timeRange.durationSeconds
        });
      }
    });
  });

  // 分析音频文件使用情况
  const audioFileUsage = info.audioClips.map(clip => ({
    filePath: clip.filePath,
    usageCount: 1, // 简化处理，假设每个音频素材只使用一次
    totalDuration: clip.durationSeconds
  }));

  return {
    videoFileUsage: Array.from(videoFileUsage.entries()).map(([filePath, usage]) => ({
      filePath,
      ...usage
    })),
    audioFileUsage
  };
}

/**
 * 分析编辑特性
 */
function analyzeEditing(info: VideoInfo): EnhancedAnalysis['analysis']['editing'] {
  let hasTransformations = false;
  let hasScaling = false;
  let hasRotation = false;
  let hasPositionChanges = false;
  let hasFlipping = false;
  let transformationCount = 0;

  info.tracks.forEach(track => {
    track.segments.forEach(segment => {
      if (segment.transform.rotation !== 0) {
        hasRotation = true;
        hasTransformations = true;
        transformationCount++;
      }
      if (segment.transform.scale.x !== 1 || segment.transform.scale.y !== 1) {
        hasScaling = true;
        hasTransformations = true;
        transformationCount++;
      }
      if (segment.transform.position.x !== 0 || segment.transform.position.y !== 0) {
        hasPositionChanges = true;
        hasTransformations = true;
        transformationCount++;
      }
      if (segment.transform.flip.horizontal || segment.transform.flip.vertical) {
        hasFlipping = true;
        hasTransformations = true;
        transformationCount++;
      }
    });
  });

  return {
    hasTransformations,
    hasScaling,
    hasRotation,
    hasPositionChanges,
    hasFlipping,
    transformationCount
  };
}

/**
 * 生成建议
 */
function generateRecommendations(analysis: Omit<EnhancedAnalysis['analysis'], 'recommendations'>): Array<{type: string; description: string}> {
  const recommendations: Array<{type: string; description: string}> = [];

  if (analysis.complexity.level === 'Very Complex') {
    recommendations.push({
      type: 'performance',
      description: '项目复杂度很高，建议分段处理或简化编辑'
    });
  }

  if (analysis.timeline.segmentCount > 50) {
    recommendations.push({
      type: 'optimization',
      description: '片段数量较多，考虑合并相似片段以提高性能'
    });
  }

  if (analysis.timeline.averageSegmentLength < 1) {
    recommendations.push({
      type: 'content',
      description: '平均片段时长较短，可能影响观看体验'
    });
  }

  if (analysis.editing.transformationCount > 20) {
    recommendations.push({
      type: 'performance',
      description: '变换操作较多，注意检查渲染性能'
    });
  }

  const videoFileCount = analysis.materials.videoFileUsage.length;
  if (videoFileCount === 1) {
    recommendations.push({
      type: 'content',
      description: '只使用了一个视频文件，考虑添加更多素材丰富内容'
    });
  } else if (videoFileCount > 10) {
    recommendations.push({
      type: 'management',
      description: '使用了大量视频文件，注意素材管理和存储空间'
    });
  }

  if (recommendations.length === 0) {
    recommendations.push({
      type: 'general',
      description: '项目结构良好，无特殊建议'
    });
  }

  return recommendations;
}

/**
 * 执行增强分析
 */
function performEnhancedAnalysis(filePath: string): EnhancedAnalysis {
  const basicInfo = parseJianyingDraft(filePath);

  const complexity = calculateComplexity(basicInfo);
  const timeline = analyzeTimeline(basicInfo);
  const materials = analyzeMaterials(basicInfo);
  const editing = analyzeEditing(basicInfo);
  const analysisData = { complexity, timeline, materials, editing };
  const recommendations = generateRecommendations(analysisData);

  return {
    basicInfo,
    analysis: {
      complexity,
      timeline,
      materials,
      editing
    },
    recommendations
  };
}

/**
 * 格式化增强分析结果
 */
function formatEnhancedAnalysis(analysis: EnhancedAnalysis): void {
  console.log('🚀 剪映项目增强分析报告');
  console.log('=' .repeat(80));
  
  // 复杂度分析
  console.log('\n📊 项目复杂度分析:');
  console.log(`  复杂度等级: ${analysis.analysis.complexity.level}`);
  console.log(`  复杂度评分: ${analysis.analysis.complexity.score}/100`);
  console.log('  影响因素:');
  analysis.analysis.complexity.factors.forEach(factor => {
    console.log(`    • ${factor}`);
  });

  // 时间轴分析
  console.log('\n⏱️ 时间轴分析:');
  console.log(`  总时长: ${analysis.analysis.timeline.totalDuration.toFixed(2)}秒`);
  console.log(`  片段总数: ${analysis.analysis.timeline.segmentCount}个`);
  console.log(`  平均片段时长: ${analysis.analysis.timeline.averageSegmentLength.toFixed(2)}秒`);
  console.log(`  最短片段: ${analysis.analysis.timeline.shortestSegment.toFixed(2)}秒`);
  console.log(`  最长片段: ${analysis.analysis.timeline.longestSegment.toFixed(2)}秒`);

  // 素材使用分析
  console.log('\n📁 素材使用分析:');
  console.log('  视频文件使用情况:');
  analysis.analysis.materials.videoFileUsage.forEach((usage, index) => {
    console.log(`    ${index + 1}. ${path.basename(usage.filePath)}`);
    console.log(`       使用次数: ${usage.usageCount}次`);
    console.log(`       总使用时长: ${usage.totalDuration.toFixed(2)}秒`);
    console.log(`       片段分布: ${usage.segments.length}个片段`);
  });

  // 编辑特性分析
  console.log('\n🎨 编辑特性分析:');
  console.log(`  使用变换效果: ${analysis.analysis.editing.hasTransformations ? '是' : '否'}`);
  console.log(`  使用缩放: ${analysis.analysis.editing.hasScaling ? '是' : '否'}`);
  console.log(`  使用旋转: ${analysis.analysis.editing.hasRotation ? '是' : '否'}`);
  console.log(`  使用位置调整: ${analysis.analysis.editing.hasPositionChanges ? '是' : '否'}`);
  console.log(`  使用翻转: ${analysis.analysis.editing.hasFlipping ? '是' : '否'}`);
  console.log(`  变换操作总数: ${analysis.analysis.editing.transformationCount}个`);

  // 建议
  console.log('\n💡 优化建议:');
  analysis.recommendations.forEach(rec => {
    console.log(`  • [${rec.type}] ${rec.description}`);
  });
}

/**
 * 主函数
 */
function main(): void {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('使用方法:');
    console.log('  ts-node enhanced-parser.ts <draft_content.json路径> [输出JSON路径]');
    console.log('');
    console.log('示例:');
    console.log('  ts-node enhanced-parser.ts ./draft_content.json');
    console.log('  ts-node enhanced-parser.ts ./draft_content.json ./enhanced_analysis.json');
    process.exit(1);
  }
  
  const inputPath = args[0];
  const outputPath = args[1];
  
  try {
    console.log(`🔍 正在执行增强分析: ${inputPath}`);
    
    const analysis = performEnhancedAnalysis(inputPath);
    
    // 输出分析结果
    formatEnhancedAnalysis(analysis);
    
    // 如果指定了输出路径，导出JSON
    if (outputPath) {
      const jsonContent = JSON.stringify(analysis, null, 2);
      fs.writeFileSync(outputPath, jsonContent, 'utf-8');
      console.log(`\n💾 增强分析结果已导出到: ${outputPath}`);
    }
    
    console.log('\n✅ 增强分析完成!');
    
  } catch (error) {
    console.error('❌ 分析失败:', error instanceof Error ? error.message : String(error));
    process.exit(1);
  }
}

// 如果直接运行此脚本，执行主函数
if (require.main === module) {
  main();
}

// 主要分析函数
export { performEnhancedAnalysis, formatEnhancedAnalysis };

// 添加单独的分析函数导出
export function analyzeJianyingProject(filePath: string): EnhancedAnalysis {
  return performEnhancedAnalysis(filePath);
}

export function analyzeJianyingProjectFromData(videoInfo: VideoInfo): EnhancedAnalysis {
  const complexity = calculateComplexity(videoInfo);
  const timeline = analyzeTimeline(videoInfo);
  const materials = analyzeMaterials(videoInfo);
  const editing = analyzeEditing(videoInfo);
  const analysisData = { complexity, timeline, materials, editing };
  const recommendations = generateRecommendationsFromAnalysis(analysisData);

  return {
    basicInfo: videoInfo,
    analysis: analysisData,
    recommendations
  };
}

export function generateRecommendationsFromAnalysis(analysis: any): any[] {
  const recommendations: any[] = [];

  if (analysis.complexity.level === 'Very Complex') {
    recommendations.push({
      type: 'performance',
      description: '项目复杂度很高，建议优化性能'
    });
  }

  return recommendations;
}

// 导出类型定义
export type { EnhancedAnalysis };

// 添加类型别名
export type ComplexityAnalysis = EnhancedAnalysis['analysis']['complexity'];
export type TimelineAnalysis = EnhancedAnalysis['analysis']['timeline'];
export type MaterialUsage = EnhancedAnalysis['analysis']['materials'];
export type EditingFeatures = EnhancedAnalysis['analysis']['editing'];
export type Recommendation = {
  type: string;
  description: string;
};
