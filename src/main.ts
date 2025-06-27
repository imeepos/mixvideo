/**
 * 使用 @mixvideo/video-analyzer
 * 处理 ./resources 里的视频
 */

import { createVideoAnalyzer } from '@mixvideo/video-analyzer';
import * as path from 'path';
import * as fs from 'fs';

async function main() {
  try {
    console.log('🎬 开始视频分析...');

    // 创建视频分析器实例
    const analyzer = createVideoAnalyzer({
      upload: {
        bucketName: 'dy-media-storage',
        filePrefix: 'processed',
        maxRetries: 3
      }
    });

    // 资源目录路径
    const resourcesDir = path.join(__dirname, '../resources');

    // 检查资源目录是否存在
    if (!fs.existsSync(resourcesDir)) {
      console.log('📁 创建 resources 目录...');
      fs.mkdirSync(resourcesDir, { recursive: true });
      console.log('✅ resources 目录已创建，请将视频文件放入该目录');
      return;
    }

    // 配置分析模式 - 使用 Gemini 进行综合分析
    const analysisMode = {
      type: 'gemini' as const,
      model: 'gemini-2.5-flash',
      analysisType: 'comprehensive' as const
    };

    // 分析选项
    const analysisOptions = {
      enableProductAnalysis: true,  // 启用产品分析
      maxScenes: 20,               // 最大场景数
      confidenceThreshold: 0.7     // 置信度阈值
    };

    // 进度回调
    const onProgress = (progress: any) => {
      console.log(`📊 ${progress.step}: ${progress.progress}% (${progress.currentFile || ''})`);
    };

    console.log(`🔍 扫描目录: ${resourcesDir}`);

    // 执行完整的分析工作流
    const result = await analyzer.analyzeDirectoryComplete(
      resourcesDir,
      analysisMode,
      {
        // 扫描选项
        scanOptions: {
          recursive: true,
          maxFileSize: 1024 * 1024 * 1024, // 1GB
          minFileSize: 1024 // 1KB
        },

        // 分析选项
        analysisOptions,

        // 文件夹匹配配置
        folderConfig: {
          baseDirectory: resourcesDir,
          maxDepth: 2,
          minConfidence: 0.4,
          enableSemanticAnalysis: true
        },

        // 报告生成选项
        reportOptions: {
          format: 'xml',
          outputPath: path.join(__dirname, '../analysis-report.xml'),
          includeFolderMatching: true,
          includeDetailedAnalysis: true,
          title: 'MixVideo 视频分析报告'
        },

        // 进度跟踪
        onProgress
      }
    );

    // 输出结果统计
    console.log('\n🎉 分析完成！');
    console.log(`📹 分析视频数量: ${result.analysisResults.length}`);
    console.log(`📂 文件夹匹配数量: ${Object.keys(result.folderMatches).length}`);
    console.log(`📄 报告保存位置: ${result.reportPath}`);

    // 显示详细统计
    const stats = analyzer.getAnalysisStatistics(result.analysisResults);
    console.log('\n📊 详细统计:');
    console.log(`- 总处理时间: ${stats.totalProcessingTime}ms`);
    console.log(`- 总场景数: ${stats.totalScenes}`);
    console.log(`- 总对象数: ${stats.totalObjects}`);
    console.log(`- 平均质量分数: ${stats.averageQualityScore.toFixed(2)}`);

    // 显示文件夹匹配建议
    if (Object.keys(result.folderMatches).length > 0) {
      console.log('\n📁 智能文件夹匹配建议:');
      for (const [videoPath, matches] of Object.entries(result.folderMatches)) {
        const videoName = path.basename(videoPath);
        console.log(`\n🎬 ${videoName}:`);
        matches.slice(0, 3).forEach((match, index) => {
          console.log(`  ${index + 1}. ${match.folderPath} (置信度: ${(match.confidence * 100).toFixed(1)}%)`);
          if (match.reasons && match.reasons.length > 0) {
            console.log(`     理由: ${match.reasons.join(', ')}`);
          }
        });
      }
    }

  } catch (error) {
    console.error('❌ 分析过程中出现错误:', error);
    process.exit(1);
  }
}

// 运行主函数
if (require.main === module) {
  main().catch(console.error);
}