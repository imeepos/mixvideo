/**
 * 文件组织器 - 负责视频文件的移动、重命名和组织
 */

import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { VideoFile, VideoAnalysisResult, FolderMatchResult } from './types';

const rename = promisify(fs.rename);
const mkdir = promisify(fs.mkdir);
const access = promisify(fs.access);
const copyFile = promisify(fs.copyFile);

/**
 * 文件操作配置
 */
export interface FileOrganizerConfig {
  /** 是否移动文件（false则复制，原文件保持不变） */
  moveFiles?: boolean;
  /** 是否创建不存在的目录 */
  createDirectories?: boolean;
  /** 文件名冲突时的处理方式 */
  conflictResolution?: 'skip' | 'overwrite' | 'rename';
  /** 是否备份原文件（仅在移动文件时有效，复制时无需备份） */
  createBackup?: boolean;
  /** 备份目录 */
  backupDirectory?: string;
  /** 文件名生成模式 */
  namingMode?: 'smart' | 'timestamp' | 'original' | 'custom' | 'content-based' | 'preserve-original';
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
      moveFiles: false, // 默认复制文件，更安全
      createDirectories: true,
      conflictResolution: 'rename',
      createBackup: false, // 默认不备份（复制模式下无需备份）
      backupDirectory: './backup',
      namingMode: 'preserve-original', // 默认保留原始文件名
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

      // 执行文件操作
      const operation = this.config.moveFiles ? 'move' : 'copy';
      let backupPath: string | undefined;

      if (this.config.moveFiles) {
        // 移动文件时，创建备份（如果需要）
        if (this.config.createBackup) {
          backupPath = await this.createBackup(videoFile.path);
          console.log(`💾 已创建备份: ${backupPath}`);
        }
        await rename(videoFile.path, resolvedPath);
        console.log(`📦 移动文件: ${videoFile.path} -> ${resolvedPath}`);
      } else {
        // 复制文件时，不需要备份（原文件保持不变）
        await copyFile(videoFile.path, resolvedPath);
        console.log(`📋 复制文件: ${videoFile.path} -> ${resolvedPath} (原文件保留)`);
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
      case 'content-based':
        return this.generateContentBasedFileName(analysisResult, originalName);
      case 'preserve-original':
        return this.generatePreserveOriginalFileName(analysisResult, originalName);
      case 'timestamp':
        return this.generateTimestampFileName(originalName);
      case 'original':
        return originalName;
      case 'custom':
        return this.config.customNamingFunction(analysisResult, originalName);
      default:
        return this.generatePreserveOriginalFileName(analysisResult, originalName); // 默认保留原始文件名
    }
  }

  /**
   * 生成智能文件名（基于分析结果，保留原始文件名）
   */
  private generateSmartFileName(analysisResult: VideoAnalysisResult, originalName: string): string {
    const originalExt = path.extname(originalName).toLowerCase();
    const baseName = path.basename(originalName, originalExt);

    // 修复后缀名问题：确保使用正确的视频格式
    const ext = this.normalizeVideoExtension(originalExt);

    console.log(`📝 生成智能文件名: 原始=${originalName}, 后缀=${originalExt} -> ${ext}`);

    // 提取关键信息作为前缀
    const summary = analysisResult.summary;
    const category = summary.category || '未分类';

    // 生成描述性前缀
    const descriptivePrefix = this.generateDescriptivePrefix(summary, category);

    // 构建最终文件名：[描述前缀]_[原始文件名].[标准化后缀]
    let finalName: string;
    if (descriptivePrefix && descriptivePrefix !== '未分类') {
      // 清理描述前缀
      const cleanPrefix = this.sanitizeFileName(descriptivePrefix);
      // 保留原始文件名，添加描述前缀
      finalName = `${cleanPrefix}_${baseName}${ext}`;
    } else {
      // 如果没有有效的描述信息，只修复后缀名
      finalName = `${baseName}${ext}`;
    }

    console.log(`✅ 生成的智能文件名: ${finalName}`);

    return finalName;
  }

  /**
   * 生成保留原始文件名的文件名（只修复后缀名）
   */
  private generatePreserveOriginalFileName(_analysisResult: VideoAnalysisResult, originalName: string): string {
    const originalExt = path.extname(originalName).toLowerCase();
    const baseName = path.basename(originalName, originalExt);

    // 只修复后缀名问题：确保使用正确的视频格式
    const ext = this.normalizeVideoExtension(originalExt);

    console.log(`📝 保留原始文件名: 原始=${originalName}, 后缀=${originalExt} -> ${ext}`);

    const finalName = `${baseName}${ext}`;
    console.log(`✅ 保留原始文件名结果: ${finalName}`);

    return finalName;
  }

  /**
   * 标准化视频文件扩展名
   */
  private normalizeVideoExtension(ext: string): string {
    const normalizedExt = ext.toLowerCase();

    // 标准化常见的视频格式
    const extensionMap: Record<string, string> = {
      '.mp4': '.mp4',
      '.mov': '.mov',
      '.avi': '.avi',
      '.mkv': '.mkv',
      '.webm': '.webm',
      '.flv': '.flv',
      '.wmv': '.wmv',
      '.m4v': '.mp4', // M4V 转换为 MP4
      '.3gp': '.3gp',
      '.ts': '.ts'
    };

    return extensionMap[normalizedExt] || '.mp4'; // 默认使用 .mp4
  }

  /**
   * 生成描述性前缀
   */
  private generateDescriptivePrefix(summary: any, category: string): string {
    // 优先级：类别 > 关键词 > 描述提取

    // 1. 优先使用类别（简洁明了）
    const translatedCategory = this.translateCategory(category);
    if (translatedCategory && translatedCategory !== '未分类' && translatedCategory !== '其他') {
      return translatedCategory;
    }

    // 2. 使用第一个关键词
    if (summary.keywords && summary.keywords.length > 0) {
      const firstKeyword = summary.keywords[0];
      if (firstKeyword && firstKeyword.length > 0) {
        return this.translateKeyword(firstKeyword);
      }
    }

    // 3. 从描述中提取简短信息
    if (summary.description) {
      const extractedName = this.extractSimpleNameFromDescription(summary.description);
      if (extractedName) {
        return extractedName;
      }
    }

    // 4. 返回空字符串，表示不添加前缀
    return '';
  }

  /**
   * 翻译和优化关键词
   */
  private translateKeyword(keyword: string): string {
    const translations: Record<string, string> = {
      // 产品相关
      '产品': '产品',
      '商品': '商品',
      '物品': '物品',
      '设备': '设备',
      '工具': '工具',

      // 动作相关
      '展示': '展示',
      '演示': '演示',
      '使用': '使用',
      '操作': '操作',
      '功能': '功能',

      // 服装相关
      '服装': '服装',
      '衣服': '衣服',
      '外套': '外套',
      '上衣': '上衣',
      '裤子': '裤子',

      // 美妆相关
      '化妆': '化妆',
      '美妆': '美妆',
      '护肤': '护肤',
      '保养': '保养',

      // 功能特性
      '收纳': '收纳',
      '便携': '便携',
      '折叠': '折叠',
      '轻便': '轻便'
    };

    return translations[keyword] || keyword;
  }

  /**
   * 从描述中提取简单名称
   */
  private extractSimpleNameFromDescription(description: string): string | null {
    // 简化提取逻辑，只提取最关键的产品类型
    const productTypes = [
      '外套', '上衣', '裤子', '裙子', '鞋子', '包包', '帽子',
      '化妆品', '护肤品', '面膜', '口红', '粉底',
      '手机', '耳机', '相机', '电脑'
    ];

    for (const type of productTypes) {
      if (description.includes(type)) {
        return type;
      }
    }

    // 提取动作类型
    const actions = ['演示', '展示', '使用', '试穿', '化妆', '收纳'];
    for (const action of actions) {
      if (description.includes(action)) {
        return action;
      }
    }

    return null;
  }

  /**
   * 翻译类别名称
   */
  private translateCategory(category: string): string {
    const categoryMap: Record<string, string> = {
      '产品展示': '产品展示',
      '产品使用': '产品使用',
      '生活场景': '生活场景',
      '模特实拍': '模特实拍',
      '服装配饰': '服装配饰',
      '美妆护肤': '美妆护肤',
      '其他': '其他',
      '未分类': '未分类'
    };

    return categoryMap[category] || category;
  }

  /**
   * 生成基于内容的文件名（保留原始文件名，添加内容前缀）
   */
  private generateContentBasedFileName(analysisResult: VideoAnalysisResult, originalName: string): string {
    const originalExt = path.extname(originalName).toLowerCase();
    const baseName = path.basename(originalName, originalExt);
    const ext = this.normalizeVideoExtension(originalExt);

    console.log(`📝 生成基于内容的文件名: ${originalName}`);

    const summary = analysisResult.summary;
    const scenes = analysisResult.scenes || [];
    const objects = analysisResult.objects || [];

    // 构建内容前缀组件（最多2个）
    const components: string[] = [];

    // 1. 主要内容类型
    const contentType = this.identifyContentType(summary, scenes, objects);
    if (contentType) {
      components.push(contentType);
    }

    // 2. 主要对象/产品（如果与内容类型不同）
    const mainObject = this.identifyMainObject(summary, objects);
    if (mainObject && mainObject !== contentType && components.length < 2) {
      components.push(mainObject);
    }

    // 构建最终文件名
    let finalName: string;
    if (components.length > 0) {
      const prefix = this.sanitizeFileName(components.join('_'));
      finalName = `${prefix}_${baseName}${ext}`;
    } else {
      // 如果没有识别到内容，只修复后缀名
      finalName = `${baseName}${ext}`;
    }

    console.log(`✅ 生成的基于内容文件名: ${finalName}`);

    return finalName;
  }

  /**
   * 识别内容类型
   */
  private identifyContentType(summary: any, _scenes: any[], _objects: any[]): string | null {
    const description = summary.description?.toLowerCase() || '';
    const category = summary.category || '';

    // 基于描述识别
    if (description.includes('演示') || description.includes('教程')) {
      return '演示';
    }
    if (description.includes('展示') || description.includes('介绍')) {
      return '展示';
    }
    if (description.includes('使用') || description.includes('操作')) {
      return '使用';
    }
    if (description.includes('试穿') || description.includes('穿搭')) {
      return '试穿';
    }
    if (description.includes('化妆') || description.includes('美妆')) {
      return '美妆';
    }

    // 基于类别
    const categoryMap: Record<string, string> = {
      '产品展示': '展示',
      '产品使用': '使用',
      '模特实拍': '实拍',
      '美妆护肤': '美妆'
    };

    return categoryMap[category] || null;
  }

  /**
   * 识别主要对象
   */
  private identifyMainObject(summary: any, _objects: any[]): string | null {
    const description = summary.description || '';
    const keywords = summary.keywords || [];

    // 从关键词中识别产品
    const productKeywords = keywords.filter((kw: string) =>
      ['外套', '上衣', '裤子', '裙子', '鞋子', '包包', '帽子',
       '化妆品', '护肤品', '面膜', '口红', '粉底'].includes(kw)
    );

    if (productKeywords.length > 0) {
      return productKeywords[0];
    }

    // 从描述中提取
    const objectPatterns = [
      /(外套|上衣|裤子|裙子|鞋子|包包|帽子)/,
      /(化妆品|护肤品|面膜|口红|粉底|眼影|腮红)/,
      /(手机|电脑|耳机|音响|相机)/,
      /(食品|饮料|零食|水果|蔬菜)/
    ];

    for (const pattern of objectPatterns) {
      const match = description.match(pattern);
      if (match) {
        return match[1];
      }
    }

    return null;
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
      .replace(/[\s\u00A0]+/g, '_') // 替换空格和不间断空格
      .replace(/[，。！？；：""''（）【】]/g, '_') // 替换中文标点
      .replace(/_+/g, '_') // 合并多个下划线
      .replace(/^_|_$/g, '') // 移除首尾下划线
      .substring(0, 50) // 限制长度为50字符，更合理
      .trim(); // 移除首尾空格
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
