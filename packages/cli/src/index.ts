#!/usr/bin/env node

/**
 * 设计一个cli工具
 * 
 * 模板库 
 * 产品库
 * 产品素材分类库
 * 产品素材库
 * 
 * 功能：
 * 1. 登录/退出
 * 2. 分析商品视频(上传视频)，【离线：提取商品信息并分类 大模型 入库】
 * 3. 生成视频，产品视频/产品图片/产品文案->匹配模板->循环[分类匹配素材->视频模板填充] x n -> 生成 n 个 draft_content.json -> 剪映预览出片
 * 4. 查看任务状态
 */
import { parse } from '@mixvideo/jianying'
import { readdir, writeFile } from 'fs/promises';
import path, { join } from 'path';
import { Command } from 'commander'
import { createVideoAnalyzer } from '@mixvideo/video-analyzer';
import fs from 'fs'
const root = process.cwd()
async function main() {
    const program = new Command()
    program.name(`mixvideo`)
        .version(`1.0.0`)
        .description(`MixVideo CLI tool`)

    program.command(`login`)
        .description(`Login to MixVideo`)
        .action(() => {
            console.log(`Login`)
        })

    program.command(`logout`)
        .description(`Logout from MixVideo`)
        .action(() => {
            console.log(`Logout`)
        })

    program.command(`analyze`)
        .description(`Analyze a product video`)
        .argument(`<dir>`, `Product video file`)
        .action(async (dir) => {
            // 分析视频并上传
            try {
                console.log('🎬 开始视频分析...');
                const root = process.cwd()
                // 创建视频分析器实例
                const analyzer = createVideoAnalyzer({
                    upload: {
                        bucketName: 'dy-media-storage',
                        filePrefix: 'processed',
                        maxRetries: 3
                    }
                });

                // 资源目录路径
                const resourcesDir = path.join(root, dir);

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
        })

    program.command(`generate`)
        .description(`Generate a video`)
        .argument(`<dir>`, `Product video path`)
        .option(`-t, --template [template]`, `Template to use`, `draft_content.json`)
        .action(async (dir, options) => {
            const draft = parse(join(root, options.template))
            draft.materials.videos = await Promise.all(draft.materials.videos.map(async video => {
                const material_name = video.material_name
                const videoPath = await getMaterialVideoByName(dir, material_name)
                video.path = videoPath;
                return video;
            }))
            await writeFile(join(root, options.template), JSON.stringify(draft, null, 2))
            console.log(`恭喜您，生成成功`)
        })

    program.parse()

}
// 排除已经用过的文件
let set = new Set()
async function getMaterialVideoByName(dir: string, name: string): Promise<string> {
    const files = await readdir(join(root, dir))
    const file = files[Math.floor(Math.random() * files.length)]
    const used = join(root, dir, file)
    if (set.has(used)) return getMaterialVideoByName(dir, name)
    set.add(used)
    return used;
}

main();

