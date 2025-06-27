import { VideoFrame, FrameExtractionOptions } from '../types';

/**
 * Utility class for extracting frames from video files
 */
export class FrameExtractor {
  /**
   * Extract frames from video input
   */
  async extractFrames(
    videoInput: File | string | ArrayBuffer,
    options: FrameExtractionOptions = {}
  ): Promise<VideoFrame[]> {
    const {
      startTime = 0,
      endTime,
      interval = 2,
      maxFrames = 30,
      quality = 75,
      format = 'jpeg'
    } = options;

    if (typeof videoInput === 'string') {
      return this.extractFramesFromUrl(videoInput, options);
    } else if (videoInput instanceof File) {
      return this.extractFramesFromFile(videoInput, options);
    } else if (videoInput instanceof ArrayBuffer) {
      return this.extractFramesFromBuffer(videoInput, options);
    }

    throw new Error('Unsupported video input type');
  }

  /**
   * Extract frames from video file
   */
  private async extractFramesFromFile(
    file: File,
    options: FrameExtractionOptions
  ): Promise<VideoFrame[]> {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      if (!ctx) {
        reject(new Error('Failed to get canvas context'));
        return;
      }

      const frames: VideoFrame[] = [];
      let currentTime = options.startTime || 0;
      const interval = options.interval || 2;
      const maxFrames = options.maxFrames || 30;
      let frameIndex = 0;

      video.addEventListener('loadedmetadata', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const endTime = options.endTime || video.duration;
        
        const extractNextFrame = () => {
          if (frameIndex >= maxFrames || currentTime >= endTime) {
            resolve(frames);
            return;
          }

          video.currentTime = currentTime;
        };

        video.addEventListener('seeked', () => {
          // Draw current frame to canvas
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          
          // Convert to base64
          const imageData = canvas.toDataURL(`image/${options.format || 'jpeg'}`, (options.quality || 75) / 100);
          
          frames.push({
            timestamp: currentTime,
            frameIndex,
            imageData,
            width: canvas.width,
            height: canvas.height
          });

          frameIndex++;
          currentTime += interval;
          
          // Extract next frame
          setTimeout(extractNextFrame, 100);
        });

        // Start extraction
        extractNextFrame();
      });

      video.addEventListener('error', (e) => {
        reject(new Error(`Video loading failed: ${e.message}`));
      });

      // Load video
      video.src = URL.createObjectURL(file);
      video.load();
    });
  }

  /**
   * Extract frames from video URL
   */
  private async extractFramesFromUrl(
    url: string,
    options: FrameExtractionOptions
  ): Promise<VideoFrame[]> {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      if (!ctx) {
        reject(new Error('Failed to get canvas context'));
        return;
      }

      video.crossOrigin = 'anonymous';
      
      const frames: VideoFrame[] = [];
      let currentTime = options.startTime || 0;
      const interval = options.interval || 2;
      const maxFrames = options.maxFrames || 30;
      let frameIndex = 0;

      video.addEventListener('loadedmetadata', () => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const endTime = options.endTime || video.duration;
        
        const extractNextFrame = () => {
          if (frameIndex >= maxFrames || currentTime >= endTime) {
            resolve(frames);
            return;
          }

          video.currentTime = currentTime;
        };

        video.addEventListener('seeked', () => {
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          
          const imageData = canvas.toDataURL(`image/${options.format || 'jpeg'}`, (options.quality || 75) / 100);
          
          frames.push({
            timestamp: currentTime,
            frameIndex,
            imageData,
            width: canvas.width,
            height: canvas.height
          });

          frameIndex++;
          currentTime += interval;
          
          setTimeout(extractNextFrame, 100);
        });

        extractNextFrame();
      });

      video.addEventListener('error', (e) => {
        reject(new Error(`Video loading failed: ${e.message}`));
      });

      video.src = url;
      video.load();
    });
  }

  /**
   * Extract frames from ArrayBuffer
   */
  private async extractFramesFromBuffer(
    buffer: ArrayBuffer,
    options: FrameExtractionOptions
  ): Promise<VideoFrame[]> {
    const blob = new Blob([buffer], { type: 'video/mp4' });
    const file = new File([blob], 'video.mp4', { type: 'video/mp4' });
    return this.extractFramesFromFile(file, options);
  }

  /**
   * Extract a single frame at specific timestamp
   */
  async extractSingleFrame(
    videoInput: File | string | ArrayBuffer,
    timestamp: number,
    quality: number = 75
  ): Promise<VideoFrame> {
    const frames = await this.extractFrames(videoInput, {
      startTime: timestamp,
      endTime: timestamp + 0.1,
      interval: 0.1,
      maxFrames: 1,
      quality
    });

    if (frames.length === 0) {
      throw new Error(`Failed to extract frame at timestamp ${timestamp}`);
    }

    return frames[0];
  }

  /**
   * Extract frames at specific timestamps
   */
  async extractFramesAtTimestamps(
    videoInput: File | string | ArrayBuffer,
    timestamps: number[],
    quality: number = 75
  ): Promise<VideoFrame[]> {
    const frames: VideoFrame[] = [];
    
    for (const timestamp of timestamps) {
      try {
        const frame = await this.extractSingleFrame(videoInput, timestamp, quality);
        frames.push(frame);
      } catch (error) {
        console.warn(`Failed to extract frame at ${timestamp}s:`, error);
      }
    }

    return frames;
  }

  /**
   * Get video thumbnail (first frame)
   */
  async getThumbnail(
    videoInput: File | string | ArrayBuffer,
    quality: number = 75
  ): Promise<VideoFrame> {
    return this.extractSingleFrame(videoInput, 0, quality);
  }

  /**
   * Extract frames for preview (evenly distributed)
   */
  async extractPreviewFrames(
    videoInput: File | string | ArrayBuffer,
    count: number = 9,
    quality: number = 60
  ): Promise<VideoFrame[]> {
    // First get video duration
    const metadata = await this.getVideoMetadata(videoInput);
    const duration = metadata.duration;
    
    // Calculate timestamps for evenly distributed frames
    const timestamps: number[] = [];
    for (let i = 0; i < count; i++) {
      const timestamp = (duration / (count + 1)) * (i + 1);
      timestamps.push(timestamp);
    }

    return this.extractFramesAtTimestamps(videoInput, timestamps, quality);
  }

  /**
   * Get basic video metadata
   */
  private async getVideoMetadata(videoInput: File | string | ArrayBuffer): Promise<{ duration: number; width: number; height: number }> {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      
      video.addEventListener('loadedmetadata', () => {
        resolve({
          duration: video.duration,
          width: video.videoWidth,
          height: video.videoHeight
        });
      });

      video.addEventListener('error', (e) => {
        reject(new Error(`Failed to load video metadata: ${e.message}`));
      });

      if (typeof videoInput === 'string') {
        video.src = videoInput;
      } else if (videoInput instanceof File) {
        video.src = URL.createObjectURL(videoInput);
      } else if (videoInput instanceof ArrayBuffer) {
        const blob = new Blob([videoInput], { type: 'video/mp4' });
        video.src = URL.createObjectURL(blob);
      }

      video.load();
    });
  }
}
