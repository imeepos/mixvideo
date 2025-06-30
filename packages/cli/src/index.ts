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
import { readdir, writeFile, mkdir } from 'fs/promises';
import path, { join } from 'path';
import { Command } from 'commander'
import { createVideoAnalyzer, type AnalysisMode, type AnalysisOptions } from '@mixvideo/video-analyzer';
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
                    analysis: {
                        defaultMode: 'gemini' as const,
                        defaultOptions: {
                            quality: 'high',
                            language: 'zh-CN'
                        }
                    },
                    upload: {
                        bucketName: 'dy-media-storage',
                        filePrefix: 'processed',
                        maxRetries: 3
                    },
                    workflow: {
                        minConfidenceForMove: 0.6, // 降低置信度阈值，更容易匹配
                        fileOrganizerConfig: {
                            moveFiles: false, // ✅ 启用文件移动
                            namingMode: 'smart',
                            createDirectories: true,
                            conflictResolution: 'rename',
                            createBackup: true // 移动前创建备份，更安全
                        },
                        folderMatchConfig: {
                            baseDirectory: join(root, 'outputs') // 设置基础目录为 outputs
                        }
                    }
                } as any); // 临时使用 any 类型，等待类型更新

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
                const analysisMode: AnalysisMode = {
                    type: 'gemini' as const,
                    model: 'gemini-2.5-flash',
                    options: {}
                };

                // 分析选项
                const analysisOptions: AnalysisOptions = {};

                console.log(`🔍 扫描目录: ${resourcesDir}`);
                const targetDir = join(root, 'outputs');
                console.log(` 结果目录: ${targetDir}`);

                // 确保输出目录存在并创建分类子目录
                try {
                    await mkdir(targetDir, { recursive: true });

                    // 创建常见的分类目录
                    const categories = [
                        '产品展示', '产品使用', '生活场景', '模特实拍'
                    ];

                    for (const category of categories) {
                        await mkdir(join(targetDir, category), { recursive: true });
                    }

                    console.log(`📁 已创建分类目录: ${categories.join(', ')}`);
                } catch (error) {
                    console.warn('⚠️ 创建目录时出现警告:', error);
                }

                // 执行完整的分析工作流
                const result = await analyzer.processDirectory(
                    resourcesDir,
                    targetDir,
                    analysisMode,
                    {
                        analysisOptions,
                        fileOrganizerConfig: {
                            moveFiles: false, // 📋 复制文件（更安全，原文件保持不变）
                            namingMode: 'preserve-original', // 🎯 保留原始文件名，只修复后缀
                            createDirectories: true,
                            conflictResolution: 'rename'
                            // 复制模式下无需备份设置
                        },
                        minConfidenceForMove: 0.4 // 降低置信度阈值，更容易移动文件
                    },
                    (progress) => {
                        console.log(`📊 [${progress.phase}] ${progress.step} (${progress.progress}%)`);
                        console.log(`   已处理: ${progress.processedVideos}/${progress.totalVideos}`);
                    }
                );
                await writeFile(join(targetDir, 'report.json'), JSON.stringify(result, null, 2))
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

