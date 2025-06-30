import { Command } from 'commander';
import { join, basename, extname } from 'path';
import { writeFile, readdir, mkdir, copyFile } from 'fs/promises';
import { parse } from '@mixvideo/jianying';
import { scanVideoDirectory, type VideoInfo } from '../utils/video-scanner';
import { execSync } from 'child_process';
import { randomUUID } from 'crypto';
import { homedir, platform } from 'os';

/**
 * 视频元数据接口
 */
interface VideoMetadata {
    duration: number; // 纳秒
    width: number;
    height: number;
}

/**
 * 剪映素材接口
 */
interface JianyingMaterial {
    id: string;
    path: string;
    duration: number;
    width: number;
    height: number;
    has_audio: boolean;
    import_time: number;
    type: string;
    [key: string]: any;
}

/**
 * 剪映轨道片段接口
 */
interface JianyingSegment {
    id: string;
    material_id: string;
    source_timerange: { duration: number; start: number };
    target_timerange: { duration: number; start: number };
    [key: string]: any;
}

/**
 * 使用 ffprobe 获取视频元数据
 */
async function getVideoMetadata(videoPath: string): Promise<VideoMetadata | null> {
    try {
        const cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            `"${videoPath}"`
        ].join(' ');

        const result = execSync(cmd, { encoding: 'utf-8' });
        const data = JSON.parse(result);

        const videoStream = data.streams?.find((stream: any) => stream.codec_type === 'video');

        if (!videoStream) {
            console.warn(`⚠️ 未找到视频流: ${videoPath}`);
            return null;
        }

        const duration = parseFloat(videoStream.duration || '0') * 1_000_000_000; // 转换为纳秒
        const width = parseInt(videoStream.width || '0');
        const height = parseInt(videoStream.height || '0');

        return { duration, width, height };

    } catch (error) {
        console.error(`❌ 获取视频元数据失败: ${videoPath}`, error);
        return null;
    }
}

/**
 * 生成 UUID（大写格式，符合剪映要求）
 */
function generateUUID(): string {
    return randomUUID().toUpperCase();
}

/**
 * 获取剪映草稿目录路径
 */
function getJianyingDraftPath(): string {
    const home = homedir();
    const os = platform();

    switch (os) {
        case 'win32':
            return join(home, 'AppData', 'Local', 'JianyingPro', 'User Data', 'Projects', 'com.lveditor.draft');
        case 'darwin':
            return join(home, 'Movies', 'JianyingPro', 'User Data', 'Projects', 'com.lveditor.draft');
        default: // Linux
            return join(home, '.local', 'share', 'JianyingPro', 'User Data', 'Projects', 'com.lveditor.draft');
    }
}

/**
 * 创建完整的剪映工程（包括目录结构和文件复制）
 */
async function createJianyingProject(
    videoPaths: string[],
    outputPath: string,
    options: { useDraftDir?: boolean; projectName?: string } = {}
): Promise<{ projectData: any; projectDir: string; isDraftProject: boolean }> {
    const now = Math.floor(Date.now() / 1000);
    let totalDuration = 0;

    // 确定项目目录
    let projectDir: string;
    let isDraftProject = false;

    if (options.useDraftDir) {
        // 在剪映草稿目录创建项目
        const draftBasePath = getJianyingDraftPath();
        const projectId = generateUUID();
        projectDir = join(draftBasePath, projectId);
        isDraftProject = true;
        console.log(`📁 在剪映草稿目录创建项目: ${projectId}`);
    } else {
        // 在指定位置创建项目
        projectDir = outputPath.replace('.json', '');
        console.log(`📁 创建工程目录: ${projectDir}`);
    }

    const videoDir = join(projectDir, 'video');

    try {
        await mkdir(projectDir, { recursive: true });
        await mkdir(videoDir, { recursive: true });
    } catch (error) {
        console.error('❌ 创建目录失败:', error);
        throw error;
    }

    // 创建主轨道 ID
    const mainTrackId = generateUUID();

    // 初始化工程数据结构
    const projectData = {
        version: "13.8.0",
        id: generateUUID(),
        create_time: now,
        update_time: now,
        duration: 0, // 将在后面更新
        materials: {
            videos: [] as JianyingMaterial[],
            audios: [],
            images: [],
            texts: [],
            effects: [],
            transitions: [],
            stickers: [],
            charts: []
        },
        tracks: [
            {
                attribute: 0,
                flag: 0,
                id: mainTrackId,
                is_default_name: true,
                segments: [] as JianyingSegment[],
                type: "video"
            }
        ],
        extra: {
            draft_fold_path: "",
            draft_removable_storage_device: ""
        }
    };

    // 处理每个视频文件
    for (let i = 0; i < videoPaths.length; i++) {
        const videoPath = videoPaths[i];
        const metadata = await getVideoMetadata(videoPath);

        if (!metadata) {
            console.warn(`⚠️ 跳过文件: ${videoPath} (无法获取元数据)`);
            continue;
        }

        // 复制视频文件到工程目录
        const fileExt = extname(videoPath);
        const newFileName = `video_${String(i + 1).padStart(3, '0')}${fileExt}`;
        const destPath = join(videoDir, newFileName);

        try {
            await copyFile(videoPath, destPath);
            console.log(`📋 复制视频 ${i + 1}: ${basename(videoPath)} -> ${newFileName}`);
        } catch (error) {
            console.error(`❌ 复制文件失败: ${videoPath}`, error);
            continue;
        }

        const materialId = generateUUID();
        const segmentId = generateUUID();

        // 创建视频素材
        const videoMaterial: JianyingMaterial = {
            aigc_type: "none",
            algorithm_gear: "default",
            audio_fade: null,
            cartoon_path: "",
            category_id: "",
            category_name: "local",
            check_flag: 63487,
            crop: {
                lower_left_x: 0.0,
                lower_left_y: 1.0,
                lower_right_x: 1.0,
                lower_right_y: 1.0,
                upper_left_x: 0.0,
                upper_left_y: 0.0,
                upper_right_x: 1.0,
                upper_right_y: 0.0
            },
            crop_ratio: "free",
            crop_scale: 1.0,
            duration: metadata.duration,
            extra_type_option: 0,
            formula_id: "",
            freeze: null,
            gameplay: null,
            has_audio: true,
            height: metadata.height,
            id: materialId,
            import_time: now,
            intensifies_audio_path: "",
            intensifies_path: "",
            is_ai_matting: false,
            is_trans_video: false,
            local_id: "",
            matting: {
                flag: 0,
                has_real_time_matting: false,
                interactive_matting_path: "",
                path: ""
            },
            media_meta: null,
            path: join("video", newFileName),
            real_duration: metadata.duration,
            recognize_type: 0,
            reverse_intensifies_path: "",
            reverse_path: "",
            source: 0,
            source_platform: 0,
            stable: null,
            team_id: "",
            type: "video",
            video_algorithm: {
                algorithms: [],
                deflicker: null,
                motion_blur_config: null,
                noise_reduction: null,
                path: "",
                time_range: null
            },
            width: metadata.width
        };

        projectData.materials.videos.push(videoMaterial);

        // 创建轨道片段
        const trackSegment: JianyingSegment = {
            cartoon: false,
            clip: {
                alpha: 1.0,
                flip: { horizontal: false, vertical: false },
                rotation: 0.0,
                scale: { x: 1.0, y: 1.0 },
                transform: { x: 0.0, y: 0.0 }
            },
            enable_adjust: true,
            enable_color_curves: true,
            enable_color_wheels: true,
            enable_lut: false,
            extra_material_refs: [],
            got_audio_recognize_result: true,
            hdr_settings: { intensity: 1.0, mode: 1, sdr_mode: 1 },
            id: segmentId,
            intensifies_audio: false,
            is_placeholder: false,
            is_tone_modify: false,
            key_frame_refs: [],
            last_operation_id: "",
            material_id: materialId,
            render_index: 0,
            responsive_layout: {
                enable: false,
                target_adaptive_type: 0,
                target_follow_type: 0,
                target_id: ""
            },
            reverse: false,
            source_timerange: { duration: metadata.duration, start: 0 },
            speed: 1.0,
            target_timerange: { duration: metadata.duration, start: totalDuration },
            template_id: "",
            template_scene: "default",
            track_attribute: 0,
            track_render_index: 0,
            uniform_scale: null,
            visible: true
        };

        projectData.tracks[0].segments.push(trackSegment);
        totalDuration += metadata.duration;
    }

    // 更新总时长
    projectData.duration = totalDuration;

    return { projectData, projectDir, isDraftProject };
}

/**
 * 创建 draft_meta_info.json 文件
 */
function createDraftMetaInfo(projectName: string): any {
    const now = Math.floor(Date.now() / 1000);

    return {
        "create_time": now,
        "draft_cover": "",
        "draft_fold_path": "",
        "draft_id": generateUUID(),
        "draft_name": projectName,
        "draft_removable_storage_device": "",
        "draft_root_path": "",
        "tm_draft_create": now,
        "tm_draft_modified": now
    };
}

/**
 * 根据名称获取素材视频
 */
async function getMaterialVideoByName(dir: string, _name: string): Promise<string> {
    const root = process.cwd();
    const files = await readdir(join(root, dir));
    const file = files[Math.floor(Math.random() * files.length)];
    return join(root, dir, file);
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
        .option('--draft-dir', '直接在剪映草稿目录创建项目')
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

                // 获取视频路径列表
                const videoPaths = videos.map(video => video.path);

                // 保存草稿文件路径
                const outputPath = join(process.cwd(), options.output);

                // 创建完整的剪映工程
                console.log('🔍 分析视频元数据并创建工程...');
                const result = await createJianyingProject(videoPaths, outputPath, {
                    useDraftDir: options.draftDir,
                    projectName: options.title
                });

                // 保存草稿 JSON 文件到工程目录内
                const draftJsonPath = join(result.projectDir, 'draft_content.json');
                await writeFile(draftJsonPath, JSON.stringify(result.projectData, null, 2));

                // 如果是草稿项目，还需要创建 draft_meta_info.json
                if (result.isDraftProject) {
                    const metaInfo = createDraftMetaInfo(options.title);
                    const metaJsonPath = join(result.projectDir, 'draft_meta_info.json');
                    await writeFile(metaJsonPath, JSON.stringify(metaInfo, null, 2));
                    console.log('📄 已创建草稿元信息文件');
                }

                console.log('✅ 剪映草稿生成完成！');
                if (result.isDraftProject) {
                    console.log('🎯 项目已直接创建在剪映草稿目录中');
                    console.log('💡 重启剪映即可在草稿列表中看到项目');
                }
                console.log(`📁 工程目录: ${result.projectDir}`);
                console.log(`📄 草稿文件: ${draftJsonPath}`);
                console.log(`🎬 包含 ${videos.length} 个视频片段`);
                console.log(`⏱️ 总时长: ${(result.projectData.duration / 1_000_000_000).toFixed(2)} 秒`);

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
