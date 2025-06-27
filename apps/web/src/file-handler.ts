import { Video } from '@mixvideo/shared';

export class FileHandler {
  public async processVideoFile(file: File): Promise<Video> {
    return new Promise((resolve, reject) => {
      const video = document.createElement('video');
      const url = URL.createObjectURL(file);

      video.onloadedmetadata = () => {
        const videoData: Video = {
          id: this.generateId(),
          title: file.name,
          url: url,
          duration: Math.round(video.duration),
          userId: 'current-user',
          createdAt: new Date(),
        };

        resolve(videoData);
      };

      video.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error(`Failed to load video: ${file.name}`));
      };

      video.src = url;
    });
  }

  public async getVideoThumbnail(video: Video): Promise<string> {
    return new Promise((resolve, reject) => {
      const videoElement = document.createElement('video');
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      if (!ctx) {
        reject(new Error('Cannot get canvas context'));
        return;
      }

      videoElement.onloadeddata = () => {
        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;

        // 跳到视频的中间位置获取缩略图
        videoElement.currentTime = video.duration / 2;
      };

      videoElement.onseeked = () => {
        ctx.drawImage(videoElement, 0, 0);
        const thumbnail = canvas.toDataURL('image/jpeg', 0.8);
        URL.revokeObjectURL(videoElement.src);
        resolve(thumbnail);
      };

      videoElement.onerror = () => {
        URL.revokeObjectURL(videoElement.src);
        reject(new Error('Failed to generate thumbnail'));
      };

      videoElement.src = video.url;
    });
  }

  public validateVideoFile(file: File): boolean {
    // 检查文件类型
    if (!file.type.startsWith('video/')) {
      return false;
    }

    // 检查文件大小（限制为 100MB）
    const maxSize = 100 * 1024 * 1024; // 100MB
    if (file.size > maxSize) {
      return false;
    }

    // 检查支持的视频格式
    const supportedFormats = ['mp4', 'webm', 'ogg', 'avi', 'mov'];
    const fileExtension = file.name.split('.').pop()?.toLowerCase();

    return supportedFormats.includes(fileExtension || '');
  }

  public getFileInfo(file: File): {
    name: string;
    size: string;
    type: string;
    lastModified: string;
  } {
    return {
      name: file.name,
      size: this.formatFileSize(file.size),
      type: file.type,
      lastModified: new Date(file.lastModified).toLocaleString(),
    };
  }

  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  private generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  public async convertToWebM(file: File): Promise<Blob> {
    // 这里可以集成 FFmpeg.js 来进行视频格式转换
    // 目前返回原文件作为示例
    return new Promise(resolve => {
      resolve(file);
    });
  }

  public async extractAudio(video: Video): Promise<Blob> {
    // 提取音频的模拟实现
    return new Promise((resolve, reject) => {
      const audioContext = new (window.AudioContext ||
        (window as any).webkitAudioContext)();

      fetch(video.url)
        .then(response => response.arrayBuffer())
        .then(data => audioContext.decodeAudioData(data))
        .then(audioBuffer => {
          // 这里应该将 AudioBuffer 转换为音频文件
          // 目前返回一个空的 Blob 作为示例
          const blob = new Blob([], { type: 'audio/wav' });
          resolve(blob);
        })
        .catch(reject);
    });
  }
}
