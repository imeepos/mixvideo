import { readdir, stat } from 'fs/promises';
import { join, extname } from 'path';

/**
 * 支持的视频格式
 */
export const SUPPORTED_VIDEO_FORMATS = [
    '.mp4', '.mov', '.avi', '.mkv', '.webm', 
    '.flv', '.wmv', '.m4v', '.3gp', '.ts'
];

/**
 * 视频文件信息
 */
export interface VideoInfo {
    path: string;
    name: string;
    size: number;
    format: string;
    createdAt: Date;
    modifiedAt: Date;
}

/**
 * 扫描目录中的视频文件
 */
export async function scanVideoDirectory(dirPath: string): Promise<VideoInfo[]> {
    const videos: VideoInfo[] = [];
    
    try {
        const files = await readdir(dirPath);
        
        for (const file of files) {
            const filePath = join(dirPath, file);
            const stats = await stat(filePath);
            
            // 跳过目录
            if (stats.isDirectory()) {
                continue;
            }
            
            // 检查是否是支持的视频格式
            const ext = extname(file).toLowerCase();
            if (!SUPPORTED_VIDEO_FORMATS.includes(ext)) {
                continue;
            }
            
            // 创建视频信息对象
            const videoInfo: VideoInfo = {
                path: filePath,
                name: file.replace(ext, ''), // 移除扩展名
                size: stats.size,
                format: ext.substring(1), // 移除点号
                createdAt: stats.birthtime,
                modifiedAt: stats.mtime
            };
            
            videos.push(videoInfo);
        }
        
    } catch (error) {
        throw new Error(`扫描视频目录失败: ${error}`);
    }
    
    return videos;
}

/**
 * 递归扫描目录中的视频文件
 */
export async function scanVideoDirectoryRecursive(dirPath: string): Promise<VideoInfo[]> {
    const videos: VideoInfo[] = [];
    
    async function scanDir(currentPath: string): Promise<void> {
        try {
            const files = await readdir(currentPath);
            
            for (const file of files) {
                const filePath = join(currentPath, file);
                const stats = await stat(filePath);
                
                if (stats.isDirectory()) {
                    // 递归扫描子目录
                    await scanDir(filePath);
                } else {
                    // 检查是否是支持的视频格式
                    const ext = extname(file).toLowerCase();
                    if (SUPPORTED_VIDEO_FORMATS.includes(ext)) {
                        const videoInfo: VideoInfo = {
                            path: filePath,
                            name: file.replace(ext, ''),
                            size: stats.size,
                            format: ext.substring(1),
                            createdAt: stats.birthtime,
                            modifiedAt: stats.mtime
                        };
                        
                        videos.push(videoInfo);
                    }
                }
            }
        } catch (error) {
            console.warn(`扫描目录 ${currentPath} 时出现警告:`, error);
        }
    }
    
    await scanDir(dirPath);
    return videos;
}

/**
 * 检查是否是视频文件
 */
export function isVideoFile(filePath: string): boolean {
    const ext = extname(filePath).toLowerCase();
    return SUPPORTED_VIDEO_FORMATS.includes(ext);
}

/**
 * 获取视频文件统计信息
 */
export function getVideoStats(videos: VideoInfo[]): {
    totalCount: number;
    totalSize: number;
    formatCounts: Record<string, number>;
    averageSize: number;
} {
    const formatCounts: Record<string, number> = {};
    let totalSize = 0;
    
    for (const video of videos) {
        totalSize += video.size;
        formatCounts[video.format] = (formatCounts[video.format] || 0) + 1;
    }
    
    return {
        totalCount: videos.length,
        totalSize,
        formatCounts,
        averageSize: videos.length > 0 ? totalSize / videos.length : 0
    };
}
