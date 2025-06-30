/**
 * 完整工作流程示例
 * 
 * 演示如何使用 @mixvideo/video-analyzer 进行完整的视频分析和组织流程：
 * 1. AI分析视频内容和质量
 * 2. 根据内容匹配合适的文件夹
 * 3. 移动视频到相应文件夹并重命名
 */

import { VideoAnalyzer, WorkflowProgress } from '../src';

/**
 * 示例1：一键完成所有操作
 */
async function example1_OneClickProcess() {
  console.log('=== 示例1：一键完成所有操作 ===\n');

  const analyzer = new VideoAnalyzer({
    workflow: {
      minConfidenceForMove: 0.7, // 只有置信度 >= 0.7 才移动文件
      fileOrganizerConfig: {
        moveFiles: true, // 移动文件而不是复制
        namingMode: 'smart', // 智能命名
        createBackup: true, // 创建备份
        conflictResolution: 'rename' // 重名时自动重命名
      }
    }
  });

  try {
    const result = await analyzer.processDirectory(
      '/path/to/source/videos',      // 源视频目录
      '/path/to/organized/videos',   // 目标组织目录
      { type: 'gemini', model: 'gemini-2.5-flash' }, // 使用 Gemini 分析
      {
        minConfidenceForMove: 0.8,   // 高置信度要求
        fileOrganizerConfig: {
          namingMode: 'smart',
          createDirectories: true
        }
      },
      (progress: WorkflowProgress) => {
        console.log(`[${progress.phase}] ${progress.step}: ${progress.progress}%`);
        console.log(`已处理: ${progress.processedVideos}/${progress.totalVideos}`);
      }
    );

    console.log('\n处理完成！');
    console.log(`总视频数: ${result.totalVideos}`);
    console.log(`成功分析: ${result.analyzedVideos}`);
    console.log(`成功匹配: ${result.matchedVideos}`);
    console.log(`成功组织: ${result.organizedVideos}`);
    console.log(`成功率: ${(result.stats.successRate * 100).toFixed(1)}%`);

  } catch (error) {
    console.error('处理失败:', error);
  }
}

/**
 * 示例2：分步骤处理（更精细的控制）
 */
async function example2_StepByStep() {
  console.log('\n=== 示例2：分步骤处理 ===\n');

  const analyzer = new VideoAnalyzer();

  try {
    // 步骤1：扫描视频文件
    console.log('1. 扫描视频文件...');
    const videoFiles = await analyzer.scanDirectory('/path/to/videos');
    console.log(`找到 ${videoFiles.length} 个视频文件`);

    // 步骤2：分析每个视频并获取推荐
    for (const videoFile of videoFiles.slice(0, 3)) { // 只处理前3个作为示例
      console.log(`\n2. 分析视频: ${videoFile.name}`);
      
      const { analysis, recommendations } = await analyzer.analyzeAndRecommend(
        videoFile,
        { type: 'gemini', model: 'gemini-2.5-flash' },
        '/path/to/target/directory'
      );

      console.log('分析结果:');
      console.log(`- 类别: ${analysis.summary.category}`);
      console.log(`- 关键词: ${analysis.summary.keywords.join(', ')}`);
      console.log(`- 描述: ${analysis.summary.description.substring(0, 100)}...`);

      console.log('\n文件夹推荐:');
      recommendations.forEach((rec, index) => {
        console.log(`${index + 1}. ${rec.folderName} (置信度: ${rec.confidence.toFixed(2)})`);
        console.log(`   原因: ${rec.reasons.join(', ')}`);
      });

      // 步骤3：选择最佳匹配并组织文件
      if (recommendations.length > 0 && recommendations[0].confidence > 0.7) {
        console.log(`\n3. 组织文件到: ${recommendations[0].folderPath}`);
        
        const result = await analyzer.organizeVideo(
          videoFile,
          analysis,
          recommendations[0].folderPath
        );

        if (result.success) {
          console.log(`✓ 文件已移动: ${result.originalPath} -> ${result.newPath}`);
        } else {
          console.log(`✗ 移动失败: ${result.error}`);
        }
      } else {
        console.log('置信度不足，跳过文件组织');
      }
    }

  } catch (error) {
    console.error('处理失败:', error);
  }
}

/**
 * 示例3：自定义文件命名和组织策略
 */
async function example3_CustomNaming() {
  console.log('\n=== 示例3：自定义文件命名策略 ===\n');

  // 演示自定义命名策略配置
  const customConfig = {
    workflow: {
      fileOrganizerConfig: {
        namingMode: 'custom' as const,
        customNamingFunction: (analysis: any, originalName: string) => {
          // 自定义命名逻辑
          const category = analysis.summary.category || '未分类';
          const keywords = analysis.summary.keywords.slice(0, 2).join('_');
          const timestamp = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
          const ext = originalName.split('.').pop();

          return `${category}_${keywords}_${timestamp}.${ext}`;
        },
        conflictResolution: 'rename' as const,
        createBackup: true
      }
    }
  };

  console.log('自定义命名策略配置:', customConfig);
  console.log('使用自定义命名策略处理视频...');
  // 这里可以调用 new VideoAnalyzer(customConfig).processDirectory() 等方法
}

/**
 * 示例4：批量处理大量视频
 */
async function example4_BatchProcessing() {
  console.log('\n=== 示例4：批量处理大量视频 ===\n');

  const analyzer = new VideoAnalyzer({
    workflow: {
      concurrency: 5, // 并发处理5个视频
      minConfidenceForMove: 0.6,
      fileOrganizerConfig: {
        moveFiles: false, // 复制而不是移动（更安全）
        createBackup: false, // 不创建备份以节省空间
        namingMode: 'smart'
      }
    }
  });

  let lastLogTime = Date.now();

  const result = await analyzer.processVideosComplete(
    '/path/to/large/video/collection',
    { type: 'gemini', model: 'gemini-2.5-flash' },
    (progress: WorkflowProgress) => {
      // 每5秒输出一次进度
      const now = Date.now();
      if (now - lastLogTime > 5000) {
        console.log(`进度: ${progress.processedVideos}/${progress.totalVideos} (${progress.progress}%)`);
        console.log(`当前阶段: ${progress.phase} - ${progress.step}`);
        lastLogTime = now;
      }
    }
  );

  console.log('\n批量处理完成！');
  console.log(`处理时间: ${(result.stats.totalProcessingTime / 1000 / 60).toFixed(1)} 分钟`);
  console.log(`平均每个视频: ${(result.stats.averageProcessingTime / 1000).toFixed(1)} 秒`);
}

/**
 * 示例5：错误处理和恢复
 */
async function example5_ErrorHandling() {
  console.log('\n=== 示例5：错误处理和恢复 ===\n');

  const analyzer = new VideoAnalyzer({
    workflow: {
      fileOrganizerConfig: {
        createBackup: true, // 启用备份以便恢复
        conflictResolution: 'skip' // 遇到冲突时跳过
      }
    }
  });

  try {
    const result = await analyzer.processDirectory(
      '/path/to/videos',
      '/path/to/target',
      { type: 'gemini', model: 'gemini-2.5-flash' }
    );

    // 检查失败的操作
    const failedOperations = result.results.filter(r => r.error || !r.fileOperation?.success);
    
    if (failedOperations.length > 0) {
      console.log(`\n发现 ${failedOperations.length} 个失败的操作:`);
      failedOperations.forEach((op, index) => {
        console.log(`${index + 1}. ${op.videoFile.name}`);
        console.log(`   错误: ${op.error || op.fileOperation?.error}`);
      });

      // 可以选择重试失败的操作
      console.log('\n重试失败的操作...');
      // 这里可以实现重试逻辑
    }

  } catch (error) {
    console.error('工作流程失败:', error);
    
    // 可以实现恢复逻辑，比如从备份恢复文件
    console.log('尝试从备份恢复...');
  }
}

/**
 * 运行所有示例
 */
async function runAllExamples() {
  console.log('🎬 视频分析完整工作流程示例\n');
  
  try {
    await example1_OneClickProcess();
    await example2_StepByStep();
    await example3_CustomNaming();
    await example4_BatchProcessing();
    await example5_ErrorHandling();
    
    console.log('\n✅ 所有示例运行完成！');
  } catch (error) {
    console.error('示例运行失败:', error);
  }
}

// 如果直接运行此文件
if (require.main === module) {
  runAllExamples();
}

export {
  example1_OneClickProcess,
  example2_StepByStep,
  example3_CustomNaming,
  example4_BatchProcessing,
  example5_ErrorHandling,
  runAllExamples
};
