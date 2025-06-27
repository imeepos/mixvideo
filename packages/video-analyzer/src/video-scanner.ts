/**
 * Video file scanner and validation utilities
 */

import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { VideoFile, VideoScanOptions, ScanProgress, VideoAnalyzerError } from './types';

const stat = promisify(fs.stat);
const readdir = promisify(fs.readdir);

/**
 * Default supported video file extensions
 */
export const DEFAULT_VIDEO_EXTENSIONS = [
  '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.ogv'
];

/**
 * Default scan options
 */
export const DEFAULT_SCAN_OPTIONS: Required<VideoScanOptions> = {
  extensions: DEFAULT_VIDEO_EXTENSIONS,
  recursive: true,
  maxFileSize: 500 * 1024 * 1024, // 500MB
  minFileSize: 1024, // 1KB
  onProgress: () => {}
};

/**
 * Video file scanner class
 */
export class VideoScanner {
  private options: Required<VideoScanOptions>;

  constructor(options: VideoScanOptions = {}) {
    this.options = { ...DEFAULT_SCAN_OPTIONS, ...options };
  }

  /**
   * Scan a directory for video files
   */
  async scanDirectory(directoryPath: string): Promise<VideoFile[]> {
    if (!await this.isValidDirectory(directoryPath)) {
      throw new VideoAnalyzerError(
        `Invalid directory path: ${directoryPath}`,
        'INVALID_DIRECTORY'
      );
    }

    const videoFiles: VideoFile[] = [];
    const progress: ScanProgress = {
      step: 'Initializing scan',
      progress: 0,
      filesFound: 0,
      directoriesScanned: 0
    };

    this.options.onProgress(progress);

    try {
      await this.scanDirectoryRecursive(directoryPath, videoFiles, progress);
      
      progress.step = 'Scan completed';
      progress.progress = 100;
      this.options.onProgress(progress);

      return videoFiles;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new VideoAnalyzerError(
        `Failed to scan directory: ${errorMessage}`,
        'SCAN_FAILED',
        error
      );
    }
  }

  /**
   * Recursively scan directory for video files
   */
  private async scanDirectoryRecursive(
    dirPath: string,
    videoFiles: VideoFile[],
    progress: ScanProgress
  ): Promise<void> {
    progress.directoriesScanned++;
    progress.step = `Scanning: ${path.basename(dirPath)}`;
    this.options.onProgress(progress);

    const entries = await readdir(dirPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name);

      if (entry.isDirectory() && this.options.recursive) {
        await this.scanDirectoryRecursive(fullPath, videoFiles, progress);
      } else if (entry.isFile()) {
        progress.currentFile = entry.name;
        this.options.onProgress(progress);

        if (this.isVideoFile(fullPath)) {
          try {
            const videoFile = await this.createVideoFile(fullPath);
            if (this.isValidVideoFile(videoFile)) {
              videoFiles.push(videoFile);
              progress.filesFound++;
              progress.progress = Math.min(95, (progress.filesFound / 10) * 100);
              this.options.onProgress(progress);
            }
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            console.warn(`Failed to process video file ${fullPath}:`, errorMessage);
          }
        }
      }
    }
  }

  /**
   * Check if a file is a video file based on extension (synchronous)
   */
  isVideoFile(filePath: string): boolean {
    const ext = path.extname(filePath).toLowerCase();
    return this.options.extensions.includes(ext);
  }

  /**
   * Check if a file is a video file based on extension (async version for compatibility)
   */
  async isVideoFileAsync(filePath: string): Promise<boolean> {
    return this.isVideoFile(filePath);
  }

  /**
   * Create VideoFile object from file path
   */
  async createVideoFile(filePath: string): Promise<VideoFile> {
    const stats = await stat(filePath);
    const parsedPath = path.parse(filePath);

    return {
      path: filePath,
      name: parsedPath.name,
      size: stats.size,
      format: parsedPath.ext.toLowerCase().substring(1),
      createdAt: stats.birthtime,
      modifiedAt: stats.mtime
    };
  }

  /**
   * Validate video file against size constraints
   */
  isValidVideoFile(videoFile: VideoFile): boolean {
    return (
      videoFile.size >= this.options.minFileSize &&
      videoFile.size <= this.options.maxFileSize
    );
  }

  /**
   * Check if directory exists and is accessible
   */
  async isValidDirectory(dirPath: string): Promise<boolean> {
    try {
      const stats = await stat(dirPath);
      return stats.isDirectory();
    } catch {
      return false;
    }
  }

  /**
   * Get video file metadata using basic file system info
   */
  async getBasicMetadata(videoFile: VideoFile): Promise<VideoFile> {
    // This is a basic implementation
    // In a real-world scenario, you might want to use ffprobe or similar tools
    // to extract detailed video metadata like duration, resolution, etc.
    
    try {
      const stats = await stat(videoFile.path);
      return {
        ...videoFile,
        size: stats.size,
        createdAt: stats.birthtime,
        modifiedAt: stats.mtime
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new VideoAnalyzerError(
        `Failed to get metadata for ${videoFile.path}: ${errorMessage}`,
        'METADATA_FAILED',
        error
      );
    }
  }

  /**
   * Validate multiple video files
   */
  async validateVideoFiles(videoFiles: VideoFile[]): Promise<{
    valid: VideoFile[];
    invalid: Array<{ file: VideoFile; reason: string }>;
  }> {
    const valid: VideoFile[] = [];
    const invalid: Array<{ file: VideoFile; reason: string }> = [];

    for (const videoFile of videoFiles) {
      try {
        // Check if file still exists
        if (!await this.fileExists(videoFile.path)) {
          invalid.push({ file: videoFile, reason: 'File not found' });
          continue;
        }

        // Check file size constraints
        if (!this.isValidVideoFile(videoFile)) {
          invalid.push({ 
            file: videoFile, 
            reason: `File size ${videoFile.size} bytes is outside allowed range` 
          });
          continue;
        }

        // Check if it's still a video file
        if (!this.isVideoFile(videoFile.path)) {
          invalid.push({ file: videoFile, reason: 'Not a supported video format' });
          continue;
        }

        valid.push(videoFile);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        invalid.push({ file: videoFile, reason: errorMessage });
      }
    }

    return { valid, invalid };
  }

  /**
   * Check if file exists
   */
  private async fileExists(filePath: string): Promise<boolean> {
    try {
      await stat(filePath);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get scan statistics
   */
  async getScanStatistics(directoryPath: string): Promise<{
    totalFiles: number;
    totalVideoFiles: number;
    totalSize: number;
    averageSize: number;
    formatDistribution: Record<string, number>;
  }> {
    const videoFiles = await this.scanDirectory(directoryPath);
    
    const totalFiles = videoFiles.length;
    const totalSize = videoFiles.reduce((sum, file) => sum + file.size, 0);
    const averageSize = totalFiles > 0 ? totalSize / totalFiles : 0;
    
    const formatDistribution: Record<string, number> = {};
    videoFiles.forEach(file => {
      const format = file.format || 'unknown';
      formatDistribution[format] = (formatDistribution[format] || 0) + 1;
    });

    return {
      totalFiles,
      totalVideoFiles: totalFiles,
      totalSize,
      averageSize,
      formatDistribution
    };
  }

  /**
   * Update scan options
   */
  updateOptions(options: Partial<VideoScanOptions>): void {
    this.options = { ...this.options, ...options };
  }

  /**
   * Get current scan options
   */
  getOptions(): VideoScanOptions {
    return { ...this.options };
  }
}

/**
 * Convenience function to scan directory with default options
 */
export async function scanVideoDirectory(
  directoryPath: string,
  options?: VideoScanOptions
): Promise<VideoFile[]> {
  const scanner = new VideoScanner(options);
  return scanner.scanDirectory(directoryPath);
}

/**
 * Convenience function to get video scan statistics
 */
export async function getVideoScanStatistics(
  directoryPath: string,
  options?: VideoScanOptions
): Promise<{
  totalFiles: number;
  totalVideoFiles: number;
  totalSize: number;
  averageSize: number;
  formatDistribution: Record<string, number>;
}> {
  const scanner = new VideoScanner(options);
  return scanner.getScanStatistics(directoryPath);
}
