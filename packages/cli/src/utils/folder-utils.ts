import { mkdir } from 'fs/promises';
import { join } from 'path';

/**
 * 默认分类文件夹列表
 */
export const DEFAULT_FOLDERS = [
    '产品展示',
    '产品使用', 
    '生活场景',
    '模特实拍'
];

/**
 * 创建默认分类文件夹
 */
export async function createDefaultFolders(targetDir: string): Promise<void> {
    const folders = DEFAULT_FOLDERS.map(folder => folder);
    
    console.log(`📁 已创建分类目录: ${folders.join(', ')}`);
    
    for (const folder of folders) {
        try {
            await mkdir(join(targetDir, folder), { recursive: true });
        } catch (error) {
            // 目录可能已存在，忽略错误
            console.warn('⚠️ 创建目录时出现警告:', error);
        }
    }
}

/**
 * 创建自定义分类文件夹
 */
export async function createCustomFolders(targetDir: string, folders: string[]): Promise<void> {
    console.log(`📁 创建自定义分类目录: ${folders.join(', ')}`);
    
    for (const folder of folders) {
        try {
            await mkdir(join(targetDir, folder), { recursive: true });
        } catch (error) {
            console.warn(`⚠️ 创建目录 ${folder} 时出现警告:`, error);
        }
    }
}

/**
 * 确保目录存在
 */
export async function ensureDirectory(dirPath: string): Promise<void> {
    try {
        await mkdir(dirPath, { recursive: true });
    } catch (error) {
        console.warn(`⚠️ 创建目录 ${dirPath} 时出现警告:`, error);
    }
}
