/**
 * Video file uploader for Gemini AI
 */

import * as fs from 'fs';
import { promisify } from 'util';
import { uploadFileToGemini } from '@mixvideo/gemini';
import { VideoFile, UploadProgress, VideoAnalyzerError } from './types';

const readFile = promisify(fs.readFile);
const stat = promisify(fs.stat);

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
}

/**
 * Default upload configuration
 */
export const DEFAULT_UPLOAD_CONFIG: Required<Omit<UploadConfig, 'bucketName' | 'filePrefix'>> = {
  chunkSize: 10 * 1024 * 1024, // 10MB chunks
  maxRetries: 3,
  timeout: 300000, // 5 minutes
  onProgress: () => {}
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
      // Validate file before upload
      await this.validateFileForUpload(videoFile);

      progress.step = 'Reading file';
      progress.progress = 10;
      this.config.onProgress(progress);

      // Read file content
      const fileBuffer = await this.readVideoFile(videoFile);

      progress.step = 'Uploading to Gemini';
      progress.progress = 20;
      this.config.onProgress(progress);

      // Generate GCS path
      const gcsPath = this.generateGcsPath(videoFile);

      // Upload with retry logic
      await this.uploadWithRetry(fileBuffer, gcsPath, progress);

      const uploadTime = Date.now() - startTime;

      progress.step = 'Upload completed';
      progress.progress = 100;
      progress.bytesUploaded = videoFile.size;
      this.config.onProgress(progress);

      return {
        videoFile,
        success: true,
        gcsPath,
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

  /**
   * Upload with retry logic
   */
  private async uploadWithRetry(
    fileBuffer: Buffer,
    gcsPath: string,
    progress: UploadProgress
  ): Promise<void> {
    let lastError: Error | null = null;
    
    for (let attempt = 1; attempt <= this.config.maxRetries; attempt++) {
      try {
        progress.step = `Upload attempt ${attempt}/${this.config.maxRetries}`;
        this.config.onProgress(progress);

        await uploadFileToGemini(
          this.config.bucketName,
          gcsPath,
          fileBuffer
        );

        // Upload successful
        return;

      } catch (error) {
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
    return `upload_${timestamp}_${random}`;
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
