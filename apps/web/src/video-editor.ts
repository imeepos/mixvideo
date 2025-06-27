import { Video } from '@mixvideo/shared';

export class VideoEditor {
  private currentVideo: HTMLVideoElement | null = null;
  private previewArea: HTMLElement;

  constructor() {
    this.previewArea = document.getElementById('preview-area') as HTMLElement;
  }

  public play(): void {
    if (this.currentVideo) {
      this.currentVideo.play().catch(error => {
        console.error('Error playing video:', error);
      });
    }
  }

  public pause(): void {
    if (this.currentVideo) {
      this.currentVideo.pause();
    }
  }

  public clear(): void {
    if (this.currentVideo) {
      this.currentVideo.remove();
      this.currentVideo = null;
    }
    this.previewArea.innerHTML = '<p>视频预览将显示在这里</p>';
  }

  public loadVideo(video: Video): void {
    this.clear();

    // 检查是否是演示视频（图片格式）
    if (video.url.startsWith('data:image/')) {
      const img = document.createElement('img');
      img.src = video.url;
      img.style.cssText = `
        width: 100%;
        height: 100%;
        object-fit: contain;
      `;
      this.previewArea.appendChild(img);

      // 添加播放提示
      const playHint = document.createElement('div');
      playHint.style.cssText = `
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0,0,0,0.7);
        color: white;
        padding: 10px 20px;
        border-radius: 20px;
        font-size: 14px;
      `;
      playHint.textContent = '演示视频预览';
      this.previewArea.style.position = 'relative';
      this.previewArea.appendChild(playHint);
    } else {
      const videoElement = document.createElement('video');
      videoElement.src = video.url;
      videoElement.controls = true;
      videoElement.style.cssText = `
        width: 100%;
        height: 100%;
        object-fit: contain;
      `;

      this.previewArea.appendChild(videoElement);
      this.currentVideo = videoElement;
    }
  }

  public async exportVideo(videos: Video[]): Promise<void> {
    // 模拟视频导出过程
    return new Promise((resolve, reject) => {
      if (videos.length === 0) {
        reject(new Error('No videos to export'));
        return;
      }

      // 模拟导出延迟
      setTimeout(() => {
        try {
          // 在实际应用中，这里会调用视频处理库（如 FFmpeg.js）
          // 来合并和处理视频文件
          console.log(
            'Exporting videos:',
            videos.map(v => v.title)
          );

          // 创建一个模拟的导出文件下载
          this.downloadMockVideo(videos);

          resolve();
        } catch (error) {
          reject(error);
        }
      }, 2000);
    });
  }

  private downloadMockVideo(videos: Video[]): void {
    // 创建一个模拟的视频文件下载
    const mockVideoContent = `# MixVideo Export\n\n导出的视频包含以下片段：\n\n${videos.map((v, i) => `${i + 1}. ${v.title} (${v.duration}秒)`).join('\n')}\n\n导出时间: ${new Date().toLocaleString()}`;

    const blob = new Blob([mockVideoContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `mixvideo-export-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    URL.revokeObjectURL(url);
  }

  public setCurrentTime(time: number): void {
    if (this.currentVideo) {
      this.currentVideo.currentTime = time;
    }
  }

  public getCurrentTime(): number {
    return this.currentVideo ? this.currentVideo.currentTime : 0;
  }

  public getDuration(): number {
    return this.currentVideo ? this.currentVideo.duration : 0;
  }
}
