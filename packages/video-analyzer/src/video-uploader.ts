/**
 * Video file uploader for Gemini AI
 */

import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { uploadFileToGemini } from '@mixvideo/gemini';
import type { GeminiUploadResult } from '@mixvideo/gemini'
import { VideoFile, UploadProgress, VideoAnalyzerError } from './types';
import FormData from 'form-data';
import { extname } from 'path';
import mime from 'mime-types';
const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const stat = promisify(fs.stat);
const access = promisify(fs.access);

/**
 * Upload cache entry
 */
export interface UploadCacheEntry {
  /** Original video file information */
  videoFile: VideoFile;
  /** Upload result from Gemini */
  result: GeminiUploadResult;
  /** Timestamp when cached */
  timestamp: number;
  /** File checksum for validation */
  checksum: string;
}

/**
 * Upload configuration options
 */
export interface UploadConfig {
  /** GCS bucket name for uploads */
  bucketName: string;
  /** File prefix for organization */
  filePrefix: string;
  /** Chunk size for large file uploads (bytes) */
  chunkSize?: number;
  /** Maximum number of retry attempts */
  maxRetries?: number;
  /** Timeout for upload operations (ms) */
  timeout?: number;
  /** Progress callback */
  onProgress?: (progress: UploadProgress) => void;
  /** Enable local cache to avoid duplicate uploads */
  enableCache?: boolean;
  /** Cache directory path */
  cacheDir?: string;
  /** Cache expiry time in milliseconds (default: 24 hours) */
  cacheExpiry?: number;
}

/**
 * Default upload configuration
 */
export const DEFAULT_UPLOAD_CONFIG: Required<Omit<UploadConfig, 'bucketName' | 'filePrefix'>> = {
  chunkSize: 10 * 1024 * 1024, // 10MB chunks
  maxRetries: 3,
  timeout: 300000, // 5 minutes
  onProgress: () => { },
  enableCache: true,
  cacheDir: '.video-upload-cache',
  cacheExpiry: 24 * 60 * 60 * 1000 // 24 hours
};

/**
 * Upload result information
 */
export interface UploadResult {
  /** Original video file */
  videoFile: VideoFile;
  /** Upload success status */
  success: boolean;
  /** GCS file path */
  gcsPath?: string;
  /** Upload duration in milliseconds */
  uploadTime: number;
  /** File size uploaded */
  bytesUploaded: number;
  /** Error information if upload failed */
  error?: string;
  /** Upload metadata */
  metadata?: {
    uploadId: string;
    timestamp: Date;
    checksum?: string;
  };
}

/**
 * Video uploader class
 */
export class VideoUploader {
  private config: Required<UploadConfig>;

  constructor(config: UploadConfig) {
    this.config = {
      ...DEFAULT_UPLOAD_CONFIG,
      ...config
    };
  }

  /**
   * Upload a single video file to Gemini
   */
  async uploadVideo(videoFile: VideoFile): Promise<UploadResult> {
    const startTime = Date.now();
    const uploadId = this.generateUploadId(videoFile);

    const progress: UploadProgress = {
      step: 'Preparing upload',
      progress: 0,
      currentFile: videoFile.name,
      bytesUploaded: 0,
      totalBytes: videoFile.size
    };

    this.config.onProgress(progress);

    try {
      // 检查本地缓存
      progress.step = 'Checking cache';
      progress.progress = 5;
      this.config.onProgress(progress);

      const cachedResult = await this.checkLocalCache(videoFile);
      if (cachedResult) {
        const uploadTime = Date.now() - startTime;

        progress.step = 'Using cached result';
        progress.progress = 100;
        progress.bytesUploaded = videoFile.size;
        this.config.onProgress(progress);

        return {
          videoFile,
          success: true,
          gcsPath: cachedResult.urn,
          uploadTime,
          bytesUploaded: videoFile.size,
          metadata: {
            uploadId,
            timestamp: new Date(),
            checksum: await this.calculateChecksum(await this.readVideoFile(videoFile))
          }
        };
      }

      // Validate file before upload
      await this.validateFileForUpload(videoFile);

      progress.step = 'Reading file';
      progress.progress = 10;
      this.config.onProgress(progress);

      // Read file content
      const fileBuffer = await this.readVideoFile(videoFile);
      const mimeType = this.getMimeType(videoFile.path);
      progress.step = 'Uploading to Gemini';
      progress.progress = 20;
      this.config.onProgress(progress);

      // Generate GCS path
      const gcsPath = this.generateGcsPath(videoFile);

      // Upload with retry logic
      const uploadResult = await this.uploadWithRetry(fileBuffer, videoFile, progress, mimeType, gcsPath);

      const uploadTime = Date.now() - startTime;

      progress.step = 'Upload completed';
      progress.progress = 100;
      progress.bytesUploaded = videoFile.size;
      this.config.onProgress(progress);

      return {
        videoFile,
        success: true,
        gcsPath: uploadResult.urn,
        uploadTime,
        bytesUploaded: videoFile.size,
        metadata: {
          uploadId,
          timestamp: new Date(),
          checksum: await this.calculateChecksum(fileBuffer)
        }
      };

    } catch (error) {
      const uploadTime = Date.now() - startTime;

      return {
        videoFile,
        success: false,
        uploadTime,
        bytesUploaded: progress.bytesUploaded,
        error: this.getErrorMessage(error),
        metadata: {
          uploadId,
          timestamp: new Date()
        }
      };
    }
  }

  private getErrorMessage(error: unknown): string {
    return error instanceof Error ? error.message : String(error);
  }

  /**
   * Upload multiple video files
   */
  async uploadVideos(videoFiles: VideoFile[]): Promise<UploadResult[]> {
    const results: UploadResult[] = [];

    for (let i = 0; i < videoFiles.length; i++) {
      const videoFile = videoFiles[i];

      try {
        const result = await this.uploadVideo(videoFile);
        results.push(result);

        // Update overall progress
        const overallProgress = ((i + 1) / videoFiles.length) * 100;
        this.config.onProgress({
          step: `Uploaded ${i + 1}/${videoFiles.length} files`,
          progress: overallProgress,
          currentFile: videoFile.name,
          bytesUploaded: results.reduce((sum, r) => sum + r.bytesUploaded, 0),
          totalBytes: videoFiles.reduce((sum, f) => sum + f.size, 0)
        });

      } catch (error) {
        results.push({
          videoFile,
          success: false,
          uploadTime: 0,
          bytesUploaded: 0,
          error: error instanceof Error ? error.message : String(error)
        });
      }
    }

    return results;
  }

  /**
   * Validate file before upload
   */
  private async validateFileForUpload(videoFile: VideoFile): Promise<void> {
    // Check if file exists
    try {
      await stat(videoFile.path);
    } catch (error) {
      throw new VideoAnalyzerError(
        `File not found: ${videoFile.path}`,
        'FILE_NOT_FOUND'
      );
    }

    // Check file size
    if (videoFile.size === 0) {
      throw new VideoAnalyzerError(
        `File is empty: ${videoFile.path}`,
        'EMPTY_FILE'
      );
    }

    // Check if file is too large (Gemini has limits)
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (videoFile.size > maxSize) {
      throw new VideoAnalyzerError(
        `File too large: ${videoFile.size} bytes (max: ${maxSize} bytes)`,
        'FILE_TOO_LARGE'
      );
    }
  }

  /**
   * Read video file into buffer
   */
  private async readVideoFile(videoFile: VideoFile): Promise<Buffer> {
    try {
      return await readFile(videoFile.path);
    } catch (error) {
      throw new VideoAnalyzerError(
        `Failed to read file: ${videoFile.path}`,
        'READ_FAILED',
        error
      );
    }
  }
  private getMimeType(fileName: string) {
    const extension = extname(fileName).slice(1); // 去掉点号
    /**
     * 'video/mp4', 'video/mpeg', 'video/mov', 'video/avi', 'video/x-flv', 'video/mpg',
                                'video/webm', 'video/wmv', 'video/3gpp'
     */
    switch (extension) {
      case 'mp4':
        return `video/mp4`
      default:
        return mime.lookup(extension) || 'application/octet-stream';
    }
  }
  /**
   * 将上传结果保存到本地缓存
   */
  private async saveToLocalDb(videoFile: VideoFile, result: GeminiUploadResult): Promise<void> {
    if (!this.config.enableCache) {
      return;
    }

    try {
      // 确保缓存目录存在
      await this.ensureCacheDir();

      // 计算文件校验和
      const fileBuffer = await readFile(videoFile.path);
      const checksum = await this.calculateChecksum(fileBuffer);

      // 创建缓存条目
      const cacheEntry: UploadCacheEntry = {
        videoFile,
        result,
        timestamp: Date.now(),
        checksum
      };

      // 生成缓存文件路径
      const cacheKey = this.generateCacheKey(videoFile.path);
      const cacheFilePath = path.join(this.config.cacheDir, `${cacheKey}.json`);

      // 保存到缓存文件
      await writeFile(cacheFilePath, JSON.stringify(cacheEntry, null, 2), 'utf8');

      console.log(`✅ 缓存已保存: ${videoFile.name} -> ${cacheFilePath}`);
    } catch (error) {
      console.warn(`⚠️ 保存缓存失败: ${videoFile.name}`, error);
      // 缓存失败不应该影响主流程
    }
  }

  /**
   * 从本地缓存检查是否已上传
   */
  private async checkLocalCache(videoFile: VideoFile): Promise<GeminiUploadResult | null> {
    if (!this.config.enableCache) {
      return null;
    }

    try {
      // 生成缓存文件路径
      const cacheKey = this.generateCacheKey(videoFile.path);
      const cacheFilePath = path.join(this.config.cacheDir, `${cacheKey}.json`);

      // 检查缓存文件是否存在
      await access(cacheFilePath, fs.constants.F_OK);

      // 读取缓存内容
      const cacheContent = await readFile(cacheFilePath, 'utf8');
      const cacheEntry: UploadCacheEntry = JSON.parse(cacheContent);

      // 检查缓存是否过期
      const now = Date.now();
      if (now - cacheEntry.timestamp > this.config.cacheExpiry) {
        console.log(`⏰ 缓存已过期: ${videoFile.name}`);
        // 删除过期缓存
        await fs.promises.unlink(cacheFilePath).catch(() => {});
        return null;
      }

      // 验证文件是否发生变化
      const fileBuffer = await readFile(videoFile.path);
      const currentChecksum = await this.calculateChecksum(fileBuffer);

      if (currentChecksum !== cacheEntry.checksum) {
        console.log(`🔄 文件已变更: ${videoFile.name}`);
        // 删除无效缓存
        await fs.promises.unlink(cacheFilePath).catch(() => {});
        return null;
      }

      console.log(`🎯 使用缓存结果: ${videoFile.name}`);
      return cacheEntry.result;

    } catch (error) {
      // 缓存不存在或读取失败
      return null;
    }
  }

  /**
   * 确保缓存目录存在
   */
  private async ensureCacheDir(): Promise<void> {
    try {
      await access(this.config.cacheDir, fs.constants.F_OK);
    } catch {
      // 目录不存在，创建它
      await fs.promises.mkdir(this.config.cacheDir, { recursive: true });
      console.log(`📁 创建缓存目录: ${this.config.cacheDir}`);
    }
  }

  /**
   * 生成缓存键
   */
  private generateCacheKey(filePath: string): string {
    // 使用文件路径的哈希作为缓存键
    const crypto = require('crypto');
    return crypto.createHash('md5').update(filePath).digest('hex');
  }

  /**
   * 清理过期的缓存文件
   */
  async cleanExpiredCache(): Promise<void> {
    if (!this.config.enableCache) {
      return;
    }

    try {
      await this.ensureCacheDir();
      const files = await fs.promises.readdir(this.config.cacheDir);
      const now = Date.now();
      let cleanedCount = 0;

      for (const file of files) {
        if (!file.endsWith('.json')) continue;

        const filePath = path.join(this.config.cacheDir, file);
        try {
          const content = await readFile(filePath, 'utf8');
          const cacheEntry: UploadCacheEntry = JSON.parse(content);

          if (now - cacheEntry.timestamp > this.config.cacheExpiry) {
            await fs.promises.unlink(filePath);
            cleanedCount++;
          }
        } catch (error) {
          // 删除损坏的缓存文件
          await fs.promises.unlink(filePath).catch(() => {});
          cleanedCount++;
        }
      }

      if (cleanedCount > 0) {
        console.log(`🧹 清理了 ${cleanedCount} 个过期缓存文件`);
      }
    } catch (error) {
      console.warn('清理缓存失败:', error);
    }
  }

  /**
   * 获取缓存统计信息
   */
  async getCacheStats(): Promise<{
    totalFiles: number;
    totalSize: number;
    oldestEntry: Date | null;
    newestEntry: Date | null;
  }> {
    if (!this.config.enableCache) {
      return { totalFiles: 0, totalSize: 0, oldestEntry: null, newestEntry: null };
    }

    try {
      await this.ensureCacheDir();
      const files = await fs.promises.readdir(this.config.cacheDir);
      let totalFiles = 0;
      let totalSize = 0;
      let oldestTimestamp = Infinity;
      let newestTimestamp = 0;

      for (const file of files) {
        if (!file.endsWith('.json')) continue;

        const filePath = path.join(this.config.cacheDir, file);
        try {
          const stats = await stat(filePath);
          const content = await readFile(filePath, 'utf8');
          const cacheEntry: UploadCacheEntry = JSON.parse(content);

          totalFiles++;
          totalSize += stats.size;
          oldestTimestamp = Math.min(oldestTimestamp, cacheEntry.timestamp);
          newestTimestamp = Math.max(newestTimestamp, cacheEntry.timestamp);
        } catch (error) {
          // 忽略损坏的文件
        }
      }

      return {
        totalFiles,
        totalSize,
        oldestEntry: oldestTimestamp === Infinity ? null : new Date(oldestTimestamp),
        newestEntry: newestTimestamp === 0 ? null : new Date(newestTimestamp)
      };
    } catch (error) {
      return { totalFiles: 0, totalSize: 0, oldestEntry: null, newestEntry: null };
    }
  }
  /**
   * Upload with retry logic
   */
  private async uploadWithRetry(
    fileBuffer: Buffer,
    videoFile: VideoFile,
    progress: UploadProgress,
    mimeType: string,
    gcsPath: string
  ): Promise<GeminiUploadResult> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.config.maxRetries; attempt++) {
      try {
        progress.step = `Upload attempt ${attempt}/${this.config.maxRetries}`;
        this.config.onProgress(progress);

        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', fileBuffer, {
          filename: gcsPath,
          contentType: mimeType
        });

        // Use the uploadFileToGemini function from @mixvideo/gemini
        const result = await uploadFileToGemini(
          this.config.bucketName,
          this.config.filePrefix,
          formData
        );

        // 保存到数据库
        await this.saveToLocalDb(videoFile, result)
        // Return the full upload result
        return result;

      } catch (error) {
        console.log(`Upload attempt ${attempt} failed:`, error);
        lastError = error instanceof Error ? error : new Error(String(error));

        if (attempt < this.config.maxRetries) {
          // Wait before retry with exponential backoff
          const delay = Math.pow(2, attempt - 1) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw new VideoAnalyzerError(
      `Upload failed after ${this.config.maxRetries} attempts: ${lastError?.message}`,
      'UPLOAD_FAILED',
      lastError
    );
  }

  /**
   * Generate GCS path for video file
   */
  private generateGcsPath(videoFile: VideoFile): string {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const sanitizedName = videoFile.name.replace(/[^a-zA-Z0-9.-]/g, '_');
    return `${this.config.filePrefix}${timestamp}_${sanitizedName}.${videoFile.format}`;
  }

  /**
   * Generate unique upload ID
   */
  private generateUploadId(videoFile: VideoFile): string {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2);
    const sanitizedName = videoFile.name.replace(/[^a-zA-Z0-9]/g, '_');
    return `upload_${timestamp}_${sanitizedName}_${random}`;
  }

  /**
   * Calculate file checksum for verification
   */
  private async calculateChecksum(buffer: Buffer): Promise<string> {
    const crypto = await import('crypto');
    return crypto.createHash('md5').update(buffer).digest('hex');
  }

  /**
   * Get upload statistics
   */
  getUploadStatistics(results: UploadResult[]): {
    totalFiles: number;
    successfulUploads: number;
    failedUploads: number;
    totalBytesUploaded: number;
    averageUploadTime: number;
    successRate: number;
  } {
    const totalFiles = results.length;
    const successfulUploads = results.filter(r => r.success).length;
    const failedUploads = totalFiles - successfulUploads;
    const totalBytesUploaded = results.reduce((sum, r) => sum + r.bytesUploaded, 0);
    const totalUploadTime = results.reduce((sum, r) => sum + r.uploadTime, 0);
    const averageUploadTime = totalFiles > 0 ? totalUploadTime / totalFiles : 0;
    const successRate = totalFiles > 0 ? (successfulUploads / totalFiles) * 100 : 0;

    return {
      totalFiles,
      successfulUploads,
      failedUploads,
      totalBytesUploaded,
      averageUploadTime,
      successRate
    };
  }

  /**
   * Update upload configuration
   */
  updateConfig(config: Partial<UploadConfig>): void {
    this.config = { ...this.config, ...config };
  }

  /**
   * Get current upload configuration
   */
  getConfig(): UploadConfig {
    return { ...this.config };
  }
}

/**
 * Convenience function to upload a single video
 */
export async function uploadVideoToGemini(
  videoFile: VideoFile,
  config: UploadConfig
): Promise<UploadResult> {
  const uploader = new VideoUploader(config);
  return uploader.uploadVideo(videoFile);
}

/**
 * Convenience function to upload multiple videos
 */
export async function uploadVideosToGemini(
  videoFiles: VideoFile[],
  config: UploadConfig
): Promise<UploadResult[]> {
  const uploader = new VideoUploader(config);
  return uploader.uploadVideos(videoFiles);
}
