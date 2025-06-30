import { Command } from 'commander';
import { join } from 'path';
import { writeFile } from 'fs/promises';
import { VideoAnalyzer } from '@mixvideo/video-analyzer';
import type { AnalysisMode, AnalysisOptions } from '@mixvideo/video-analyzer';
import { createDefaultFolders } from '../utils/folder-utils';

/**
 * 创建分析命令
 */
export function createAnalyzeCommand(): Command {
    return new Command('analyze')
        .description('分析视频文件并自动分类组织')
        .argument('<source>', '源视频目录路径')
        .option('-o, --output <path>', '输出目录路径', 'outputs')
        .option('-m, --mode <mode>', '分析模式 (gemini|gpt4)', 'gemini')
        .option('--temperature <number>', 'AI 模型温度参数 (0.0-1.0)', '0.3')
        .option('--max-tokens <number>', '最大输出 token 数', '4096')
        .option('--move-files', '移动文件而不是复制', false)
        .option('--create-backup', '创建备份文件', false)
        .option('--confidence <number>', '文件移动的最小置信度 (0.0-1.0)', '0.4')
        .action(async (source, options) => {
            try {
                console.log('🎬 开始视频分析...');
                
                // 验证分析模式
                const validModes = ['gemini', 'gpt4'] as const;
                if (!validModes.includes(options.mode as any)) {
                    throw new Error(`无效的分析模式: ${options.mode}. 支持的模式: ${validModes.join(', ')}`);
                }

                // 构建分析模式对象
                const analysisMode: AnalysisMode = {
                    type: options.mode as 'gemini' | 'gpt4',
                    model: options.mode === 'gemini' ? 'gemini-2.5-flash' : 'gpt-4-vision-preview'
                };

                // 设置路径
                const resourcesDir = join(process.cwd(), source);
                const targetDir = join(process.cwd(), options.output);

                // 创建默认分类目录
                await createDefaultFolders(targetDir);

                // 创建视频分析器
                const analyzer = new VideoAnalyzer();

                // 配置分析选项
                const analysisOptions: AnalysisOptions = {
                    frameSamplingInterval: 2.0,
                    maxFrames: 10,
                    quality: 'high',
                    language: 'zh-CN'
                };
                
                // 执行完整的分析工作流
                const result = await analyzer.processDirectory(
                    resourcesDir,
                    targetDir,
                    analysisMode,
                    {
                        analysisOptions,
                        fileOrganizerConfig: {
                            moveFiles: options.moveFiles, // 根据选项决定是否移动文件
                            namingMode: 'preserve-original', // 保留原始文件名，只修复后缀
                            createDirectories: true,
                            conflictResolution: 'rename',
                            createBackup: options.createBackup
                        },
                        minConfidenceForMove: parseFloat(options.confidence)
                    },
                    (progress) => {
                        console.log(`📊 [${progress.phase}] ${progress.step} (${progress.progress}%)`);
                        console.log(`   已处理: ${progress.processedVideos}/${progress.totalVideos}`);
                    }
                );
                
                // 保存分析报告
                await writeFile(
                    join(targetDir, 'report.json'), 
                    JSON.stringify(result, null, 2)
                );
                
                console.log('✅ 视频分析完成！');
                console.log(`📊 总计: ${result.totalVideos} 个视频`);
                console.log(`✅ 已分析: ${result.analyzedVideos} 个`);
                console.log(`📁 已分类: ${result.matchedVideos} 个`);
                console.log(`📦 已组织: ${result.organizedVideos} 个`);
                console.log(`📄 报告已保存到: ${join(targetDir, 'report.json')}`);
                
            } catch (error) {
                console.error('❌ 分析过程中出现错误:', error);
                process.exit(1);
            }
        });
}
