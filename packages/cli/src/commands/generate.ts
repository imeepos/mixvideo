import { Command } from 'commander';
import { join } from 'path';
import { writeFile, readdir } from 'fs/promises';
import { parse } from '@mixvideo/jianying';
import { scanVideoDirectory, type VideoInfo } from '../utils/video-scanner';

// 排除已经用过的文件
const usedFiles = new Set<string>();

/**
 * 根据名称获取素材视频
 */
async function getMaterialVideoByName(dir: string, name: string): Promise<string> {
    const root = process.cwd();
    const files = await readdir(join(root, dir));
    const file = files[Math.floor(Math.random() * files.length)];
    const used = join(root, dir, file);

    if (usedFiles.has(used)) {
        return getMaterialVideoByName(dir, name);
    }

    usedFiles.add(used);
    return used;
}

/**
 * 创建生成命令
 */
export function createGenerateCommand(): Command {
    const command = new Command('generate')
        .description('生成剪映草稿文件');

    // 子命令：从视频目录生成草稿
    command.command('from-videos')
        .description('从视频目录生成剪映草稿文件')
        .argument('<source>', '源视频目录路径')
        .option('-o, --output <path>', '输出文件路径', 'draft_content.json')
        .option('--title <title>', '项目标题', '视频项目')
        .option('--fps <number>', '帧率', '30')
        .option('--resolution <resolution>', '分辨率 (1080p|720p|4k)', '1080p')
        .action(async (source, options) => {
            try {
                console.log('🎬 开始从视频目录生成剪映草稿...');

                // 扫描视频目录
                const sourceDir = join(process.cwd(), source);
                const videos = await scanVideoDirectory(sourceDir);

                if (videos.length === 0) {
                    console.log('⚠️ 未找到视频文件');
                    return;
                }

                console.log(`📁 找到 ${videos.length} 个视频文件`);

                // 创建简单的草稿内容
                const draftContent = {
                    version: "13.8.0",
                    materials: {
                        videos: videos.map((video: VideoInfo, index: number) => ({
                            id: `video_${index}`,
                            path: video.path,
                            name: video.name,
                            duration: 5000000, // 默认5秒，微秒单位
                            width: 1920,
                            height: 1080
                        }))
                    },
                    tracks: [
                        {
                            type: "video",
                            segments: videos.map((_video: VideoInfo, index: number) => ({
                                id: `segment_${index}`,
                                material_id: `video_${index}`,
                                target_timerange: {
                                    start: index * 5000000,
                                    duration: 5000000
                                }
                            }))
                        }
                    ]
                };

                // 保存草稿文件
                const outputPath = join(process.cwd(), options.output);
                await writeFile(outputPath, JSON.stringify(draftContent, null, 2));

                console.log('✅ 剪映草稿生成完成！');
                console.log(`📄 草稿文件已保存到: ${outputPath}`);
                console.log(`🎬 包含 ${videos.length} 个视频片段`);

            } catch (error) {
                console.error('❌ 生成草稿过程中出现错误:', error);
                process.exit(1);
            }
        });

    // 子命令：从模板生成草稿
    command.command('from-template')
        .description('从模板生成剪映草稿文件')
        .argument('<dir>', '素材目录路径')
        .option('-t, --template <template>', '模板文件路径', 'draft_content.json')
        .action(async (dir, options) => {
            try {
                console.log('🎬 开始从模板生成剪映草稿...');

                const root = process.cwd();
                const templatePath = join(root, options.template);

                // 解析模板文件
                const draft = parse(templatePath);

                // 替换视频素材
                draft.materials.videos = await Promise.all(
                    draft.materials.videos.map(async (video: any) => {
                        const materialName = video.material_name;
                        const videoPath = await getMaterialVideoByName(dir, materialName);
                        video.path = videoPath;
                        return video;
                    })
                );

                // 保存更新后的草稿文件
                await writeFile(templatePath, JSON.stringify(draft, null, 2));

                console.log('✅ 草稿生成成功！');
                console.log(`📄 已更新模板文件: ${templatePath}`);

            } catch (error) {
                console.error('❌ 生成草稿过程中出现错误:', error);
                process.exit(1);
            }
        });

    return command;
}
