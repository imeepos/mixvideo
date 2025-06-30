/**
 * 文件组织器 - 负责视频文件的移动、重命名和组织
 */

import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { VideoFile, VideoAnalysisResult, FolderMatchResult, VideoAnalyzerError } from './types';

const rename = promisify(fs.rename);
const mkdir = promisify(fs.mkdir);
const access = promisify(fs.access);
const copyFile = promisify(fs.copyFile);
const unlink = promisify(fs.unlink);

/**
 * 文件操作配置
 */
export interface FileOrganizerConfig {
  /** 是否移动文件（false则复制） */
  moveFiles?: boolean;
  /** 是否创建不存在的目录 */
  createDirectories?: boolean;
  /** 文件名冲突时的处理方式 */
  conflictResolution?: 'skip' | 'overwrite' | 'rename';
  /** 是否备份原文件 */
  createBackup?: boolean;
  /** 备份目录 */
  backupDirectory?: string;
  /** 文件名生成模式 */
  namingMode?: 'smart' | 'timestamp' | 'original' | 'custom';
  /** 自定义文件名生成函数 */
  customNamingFunction?: (analysis: VideoAnalysisResult, originalName: string) => string;
}

/**
 * 文件操作结果
 */
export interface FileOperationResult {
  /** 操作是否成功 */
  success: boolean;
  /** 原始文件路径 */
  originalPath: string;
  /** 新文件路径 */
  newPath?: string;
  /** 操作类型 */
  operation: 'move' | 'copy' | 'skip';
  /** 错误信息 */
  error?: string;
  /** 备份文件路径 */
  backupPath?: string;
}

/**
 * 文件组织器类
 */
export class FileOrganizer {
  private config: Required<FileOrganizerConfig>;

  constructor(config: FileOrganizerConfig = {}) {
    this.config = {
      moveFiles: true,
      createDirectories: true,
      conflictResolution: 'rename',
      createBackup: false,
      backupDirectory: './backup',
      namingMode: 'smart',
      customNamingFunction: this.defaultNamingFunction.bind(this),
      ...config
    };
  }

  /**
   * 组织单个视频文件
   */
  async organizeVideo(
    videoFile: VideoFile,
    analysisResult: VideoAnalysisResult,
    targetFolder: string
  ): Promise<FileOperationResult> {
    try {
      // 确保目标目录存在
      if (this.config.createDirectories) {
        await this.ensureDirectoryExists(targetFolder);
      }

      // 生成新文件名
      const newFileName = this.generateFileName(analysisResult, videoFile.name);
      const newFilePath = path.join(targetFolder, newFileName);

      // 检查文件冲突
      const resolvedPath = await this.resolveFileConflict(newFilePath);

      // 创建备份（如果需要）
      let backupPath: string | undefined;
      if (this.config.createBackup) {
        backupPath = await this.createBackup(videoFile.path);
      }

      // 执行文件操作
      const operation = this.config.moveFiles ? 'move' : 'copy';
      
      if (this.config.moveFiles) {
        await rename(videoFile.path, resolvedPath);
      } else {
        await copyFile(videoFile.path, resolvedPath);
      }

      return {
        success: true,
        originalPath: videoFile.path,
        newPath: resolvedPath,
        operation,
        backupPath
      };

    } catch (error) {
      return {
        success: false,
        originalPath: videoFile.path,
        operation: this.config.moveFiles ? 'move' : 'copy',
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }

  /**
   * 批量组织视频文件
   */
  async organizeVideos(
    videoResults: Array<{
      videoFile: VideoFile;
      analysisResult: VideoAnalysisResult;
      folderMatch: FolderMatchResult;
    }>
  ): Promise<FileOperationResult[]> {
    const results: FileOperationResult[] = [];

    for (const { videoFile, analysisResult, folderMatch } of videoResults) {
      const result = await this.organizeVideo(
        videoFile,
        analysisResult,
        folderMatch.folderPath
      );
      results.push(result);
    }

    return results;
  }

  /**
   * 生成智能文件名
   */
  private generateFileName(analysisResult: VideoAnalysisResult, originalName: string): string {
    switch (this.config.namingMode) {
      case 'smart':
        return this.generateSmartFileName(analysisResult, originalName);
      case 'timestamp':
        return this.generateTimestampFileName(originalName);
      case 'original':
        return originalName;
      case 'custom':
        return this.config.customNamingFunction(analysisResult, originalName);
      default:
        return originalName;
    }
  }

  /**
   * 生成智能文件名（基于分析结果）
   */
  private generateSmartFileName(analysisResult: VideoAnalysisResult, originalName: string): string {
    const ext = path.extname(originalName);
    const baseName = path.basename(originalName, ext);
    
    // 提取关键信息
    const summary = analysisResult.summary;
    const keywords = summary.keywords.slice(0, 3); // 取前3个关键词
    const category = summary.category || '未分类';
    
    // 生成描述性名称
    let smartName = '';
    
    if (keywords.length > 0) {
      smartName = keywords.join('_');
    } else if (summary.description) {
      // 从描述中提取关键词
      const words = summary.description
        .split(/[\s,，。！？]+/)
        .filter(word => word.length > 1 && word.length < 10)
        .slice(0, 3);
      smartName = words.join('_');
    } else {
      smartName = category;
    }

    // 清理文件名（移除特殊字符）
    smartName = this.sanitizeFileName(smartName);
    
    // 添加时间戳避免冲突
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
    
    return `${smartName}_${timestamp}${ext}`;
  }

  /**
   * 生成时间戳文件名
   */
  private generateTimestampFileName(originalName: string): string {
    const ext = path.extname(originalName);
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
    return `video_${timestamp}${ext}`;
  }

  /**
   * 默认自定义命名函数
   */
  private defaultNamingFunction(analysisResult: VideoAnalysisResult, originalName: string): string {
    return this.generateSmartFileName(analysisResult, originalName);
  }

  /**
   * 清理文件名（移除不安全字符）
   */
  private sanitizeFileName(fileName: string): string {
    return fileName
      .replace(/[<>:"/\\|?*]/g, '_') // 替换不安全字符
      .replace(/\s+/g, '_') // 替换空格
      .replace(/_+/g, '_') // 合并多个下划线
      .replace(/^_|_$/g, '') // 移除首尾下划线
      .substring(0, 100); // 限制长度
  }

  /**
   * 确保目录存在
   */
  private async ensureDirectoryExists(dirPath: string): Promise<void> {
    try {
      await access(dirPath);
    } catch {
      await mkdir(dirPath, { recursive: true });
    }
  }

  /**
   * 解决文件名冲突
   */
  private async resolveFileConflict(filePath: string): Promise<string> {
    try {
      await access(filePath);
      // 文件存在，需要解决冲突
      
      switch (this.config.conflictResolution) {
        case 'skip':
          throw new Error(`File already exists: ${filePath}`);
        case 'overwrite':
          return filePath;
        case 'rename':
          return this.generateUniqueFileName(filePath);
        default:
          return filePath;
      }
    } catch {
      // 文件不存在，可以直接使用
      return filePath;
    }
  }

  /**
   * 生成唯一文件名
   */
  private async generateUniqueFileName(filePath: string): Promise<string> {
    const dir = path.dirname(filePath);
    const ext = path.extname(filePath);
    const baseName = path.basename(filePath, ext);
    
    let counter = 1;
    let newPath = filePath;
    
    while (true) {
      try {
        await access(newPath);
        newPath = path.join(dir, `${baseName}_${counter}${ext}`);
        counter++;
      } catch {
        return newPath;
      }
    }
  }

  /**
   * 创建备份文件
   */
  private async createBackup(filePath: string): Promise<string> {
    await this.ensureDirectoryExists(this.config.backupDirectory);
    
    const fileName = path.basename(filePath);
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '');
    const backupFileName = `${timestamp}_${fileName}`;
    const backupPath = path.join(this.config.backupDirectory, backupFileName);
    
    await copyFile(filePath, backupPath);
    return backupPath;
  }

  /**
   * 获取组织统计信息
   */
  getOrganizationStats(results: FileOperationResult[]): {
    total: number;
    successful: number;
    failed: number;
    moved: number;
    copied: number;
    skipped: number;
  } {
    const total = results.length;
    const successful = results.filter(r => r.success).length;
    const failed = total - successful;
    const moved = results.filter(r => r.operation === 'move' && r.success).length;
    const copied = results.filter(r => r.operation === 'copy' && r.success).length;
    const skipped = results.filter(r => r.operation === 'skip').length;

    return { total, successful, failed, moved, copied, skipped };
  }
}
