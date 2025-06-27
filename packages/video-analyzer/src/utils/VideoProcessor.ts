import { VideoMetadata } from '../types';

/**
 * Utility class for video processing and metadata extraction
 */
export class VideoProcessor {
  /**
   * Extract metadata from video input
   */
  async extractMetadata(videoInput: File | string | ArrayBuffer): Promise<VideoMetadata> {
    if (typeof videoInput === 'string') {
      return this.extractMetadataFromUrl(videoInput);
    } else if (videoInput instanceof File) {
      return this.extractMetadataFromFile(videoInput);
    } else if (videoInput instanceof ArrayBuffer) {
      return this.extractMetadataFromBuffer(videoInput);
    }

    throw new Error('Unsupported video input type');
  }

  /**
   * Extract metadata from video file
   */
  private async extractMetadataFromFile(file: File): Promise<VideoMetadata> {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      
      video.addEventListener('loadedmetadata', () => {
        const metadata: VideoMetadata = {
          filename: file.name,
          duration: video.duration,
          width: video.videoWidth,
          height: video.videoHeight,
          frameRate: this.estimateFrameRate(video),
          format: this.getVideoFormat(file),
          fileSize: file.size,
          createdAt: new Date(file.lastModified)
        };
        
        resolve(metadata);
      });

      video.addEventListener('error', (e) => {
        reject(new Error(`Failed to load video metadata: ${e.message}`));
      });

      video.src = URL.createObjectURL(file);
      video.load();
    });
  }

  /**
   * Extract metadata from video URL
   */
  private async extractMetadataFromUrl(url: string): Promise<VideoMetadata> {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      video.crossOrigin = 'anonymous';
      
      video.addEventListener('loadedmetadata', () => {
        const metadata: VideoMetadata = {
          filename: this.extractFilenameFromUrl(url),
          duration: video.duration,
          width: video.videoWidth,
          height: video.videoHeight,
          frameRate: this.estimateFrameRate(video),
          format: this.getVideoFormatFromUrl(url),
          fileSize: 0, // Cannot determine from URL
          createdAt: new Date()
        };
        
        resolve(metadata);
      });

      video.addEventListener('error', (e) => {
        reject(new Error(`Failed to load video from URL: ${e.message}`));
      });

      video.src = url;
      video.load();
    });
  }

  /**
   * Extract metadata from ArrayBuffer
   */
  private async extractMetadataFromBuffer(buffer: ArrayBuffer): Promise<VideoMetadata> {
    const blob = new Blob([buffer], { type: 'video/mp4' });
    const file = new File([blob], 'video.mp4', { 
      type: 'video/mp4',
      lastModified: Date.now()
    });
    
    return this.extractMetadataFromFile(file);
  }

  /**
   * Estimate frame rate from video element
   */
  private estimateFrameRate(video: HTMLVideoElement): number {
    // Default frame rates for common video types
    const commonFrameRates = [23.976, 24, 25, 29.97, 30, 50, 59.94, 60];
    
    // Try to get frame rate from video if available
    // Note: This is a simplified estimation
    const duration = video.duration;
    if (duration > 0) {
      // Estimate based on common frame rates
      return 30; // Default assumption
    }
    
    return 30;
  }

  /**
   * Get video format from file
   */
  private getVideoFormat(file: File): string {
    const extension = file.name.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'mp4':
        return 'MP4/H.264';
      case 'webm':
        return 'WebM/VP8';
      case 'mov':
        return 'QuickTime/H.264';
      case 'avi':
        return 'AVI';
      case 'mkv':
        return 'Matroska/H.264';
      case 'flv':
        return 'Flash Video';
      case 'wmv':
        return 'Windows Media Video';
      case 'm4v':
        return 'iTunes Video/H.264';
      default:
        return file.type || 'Unknown';
    }
  }

  /**
   * Get video format from URL
   */
  private getVideoFormatFromUrl(url: string): string {
    const extension = url.split('.').pop()?.split('?')[0]?.toLowerCase();
    
    switch (extension) {
      case 'mp4':
        return 'MP4/H.264';
      case 'webm':
        return 'WebM/VP8';
      case 'mov':
        return 'QuickTime/H.264';
      case 'avi':
        return 'AVI';
      case 'mkv':
        return 'Matroska/H.264';
      default:
        return 'Unknown';
    }
  }

  /**
   * Extract filename from URL
   */
  private extractFilenameFromUrl(url: string): string {
    try {
      const urlObj = new URL(url);
      const pathname = urlObj.pathname;
      const filename = pathname.split('/').pop() || 'video';
      return filename.split('?')[0]; // Remove query parameters
    } catch {
      return 'video';
    }
  }

  /**
   * Validate video file
   */
  async validateVideo(videoInput: File | string | ArrayBuffer): Promise<boolean> {
    try {
      const metadata = await this.extractMetadata(videoInput);
      
      // Basic validation checks
      if (metadata.duration <= 0) {
        return false;
      }
      
      if (metadata.width <= 0 || metadata.height <= 0) {
        return false;
      }
      
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get video aspect ratio
   */
  getAspectRatio(metadata: VideoMetadata): number {
    return metadata.width / metadata.height;
  }

  /**
   * Determine video orientation
   */
  getOrientation(metadata: VideoMetadata): 'landscape' | 'portrait' | 'square' {
    const aspectRatio = this.getAspectRatio(metadata);
    
    if (aspectRatio > 1.1) {
      return 'landscape';
    } else if (aspectRatio < 0.9) {
      return 'portrait';
    } else {
      return 'square';
    }
  }

  /**
   * Get video resolution category
   */
  getResolutionCategory(metadata: VideoMetadata): string {
    const { width, height } = metadata;
    const pixels = width * height;
    
    if (pixels >= 3840 * 2160) {
      return '4K UHD';
    } else if (pixels >= 2560 * 1440) {
      return '2K QHD';
    } else if (pixels >= 1920 * 1080) {
      return '1080p FHD';
    } else if (pixels >= 1280 * 720) {
      return '720p HD';
    } else if (pixels >= 854 * 480) {
      return '480p SD';
    } else {
      return 'Low Resolution';
    }
  }

  /**
   * Calculate video bitrate estimation
   */
  estimateBitrate(metadata: VideoMetadata): number {
    // Rough estimation based on resolution and duration
    const pixels = metadata.width * metadata.height;
    const pixelsPerSecond = pixels * metadata.frameRate;
    
    // Estimate bits per pixel based on quality assumptions
    let bitsPerPixel = 0.1; // Conservative estimate
    
    if (pixels >= 1920 * 1080) {
      bitsPerPixel = 0.15;
    } else if (pixels >= 1280 * 720) {
      bitsPerPixel = 0.12;
    }
    
    return Math.round(pixelsPerSecond * bitsPerPixel);
  }

  /**
   * Check if video is suitable for analysis
   */
  isAnalysisReady(metadata: VideoMetadata): { ready: boolean; issues: string[] } {
    const issues: string[] = [];
    
    // Check duration
    if (metadata.duration < 1) {
      issues.push('Video too short (minimum 1 second)');
    } else if (metadata.duration > 3600) {
      issues.push('Video too long (maximum 1 hour for analysis)');
    }
    
    // Check resolution
    if (metadata.width < 240 || metadata.height < 240) {
      issues.push('Resolution too low (minimum 240p)');
    }
    
    // Check file size (if available)
    if (metadata.fileSize > 0) {
      const maxSize = 500 * 1024 * 1024; // 500MB
      if (metadata.fileSize > maxSize) {
        issues.push('File size too large (maximum 500MB)');
      }
    }
    
    return {
      ready: issues.length === 0,
      issues
    };
  }

  /**
   * Generate video summary info
   */
  generateSummaryInfo(metadata: VideoMetadata): string {
    const orientation = this.getOrientation(metadata);
    const resolution = this.getResolutionCategory(metadata);
    const duration = this.formatDuration(metadata.duration);
    
    return `${resolution} ${orientation} video, ${duration} duration, ${metadata.format}`;
  }

  /**
   * Format duration in human readable format
   */
  private formatDuration(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
      return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
  }
}
