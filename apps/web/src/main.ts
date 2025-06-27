import { formatDuration, Video } from '@mixvideo/shared';
import { VideoEditor } from './video-editor';
import { FileHandler } from './file-handler';
import { Timeline } from './timeline';
import { addDemoVideos } from './demo-data';

class MixVideoApp {
  private videoEditor: VideoEditor;
  private fileHandler: FileHandler;
  private timeline: Timeline;
  private videos: Video[] = [];

  constructor() {
    this.videoEditor = new VideoEditor();
    this.fileHandler = new FileHandler();
    this.timeline = new Timeline();

    this.initializeEventListeners();
    console.log('🎬 MixVideo App initialized');
  }

  private initializeEventListeners(): void {
    // 文件上传
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    const uploadArea = document.getElementById('upload-area') as HTMLElement;

    fileInput?.addEventListener('change', e => this.handleFileSelect(e));

    // 拖拽上传
    uploadArea?.addEventListener('dragover', e => {
      e.preventDefault();
      uploadArea.classList.add('dragover');
    });

    uploadArea?.addEventListener('dragleave', () => {
      uploadArea.classList.remove('dragover');
    });

    uploadArea?.addEventListener('drop', e => {
      e.preventDefault();
      uploadArea.classList.remove('dragover');
      const files = e.dataTransfer?.files;
      if (files) {
        this.handleFiles(Array.from(files));
      }
    });

    uploadArea?.addEventListener('click', () => {
      fileInput?.click();
    });

    // 控制按钮
    document
      .getElementById('demo-btn')
      ?.addEventListener('click', () => this.loadDemo());
    document
      .getElementById('play-btn')
      ?.addEventListener('click', () => this.play());
    document
      .getElementById('pause-btn')
      ?.addEventListener('click', () => this.pause());
    document
      .getElementById('export-btn')
      ?.addEventListener('click', () => this.exportVideo());
    document
      .getElementById('clear-btn')
      ?.addEventListener('click', () => this.clearAll());
  }

  private handleFileSelect(event: Event): void {
    const target = event.target as HTMLInputElement;
    const files = target.files;
    if (files) {
      this.handleFiles(Array.from(files));
    }
  }

  private async handleFiles(files: File[]): Promise<void> {
    const videoFiles = files.filter(file => file.type.startsWith('video/'));

    for (const file of videoFiles) {
      try {
        const video = await this.fileHandler.processVideoFile(file);
        this.addVideo(video);
      } catch (error) {
        console.error('Error processing video file:', error);
        this.showNotification(`处理视频文件 ${file.name} 时出错`, 'error');
      }
    }
  }

  private addVideo(video: Video): void {
    this.videos.push(video);
    this.updateVideoList();
    this.timeline.addVideo(video);
    this.showNotification(`已添加视频: ${video.title}`, 'success');
  }

  private updateVideoList(): void {
    const container = document.getElementById('video-items');
    if (!container) return;

    container.innerHTML = '';

    this.videos.forEach((video, index) => {
      const videoItem = document.createElement('div');
      videoItem.className = 'video-item';
      videoItem.style.cursor = 'pointer';
      videoItem.innerHTML = `
        <div onclick="app.previewVideo(${index})">
          <strong>${video.title}</strong>
          <br>
          <small>时长: ${formatDuration(video.duration)} | 大小: ${this.formatFileSize(video.url.length * 1000)}</small>
        </div>
        <div>
          <button class="btn" onclick="app.removeVideo(${index})">删除</button>
        </div>
      `;
      container.appendChild(videoItem);
    });
  }

  public removeVideo(index: number): void {
    if (index >= 0 && index < this.videos.length) {
      const removedVideo = this.videos.splice(index, 1)[0];
      this.updateVideoList();
      this.timeline.removeVideo(removedVideo.id);
      this.showNotification(`已删除视频: ${removedVideo.title}`, 'info');
    }
  }

  public previewVideo(index: number): void {
    if (index >= 0 && index < this.videos.length) {
      const video = this.videos[index];
      this.videoEditor.loadVideo(video);
      this.showNotification(`正在预览: ${video.title}`, 'info');
    }
  }

  private formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  private play(): void {
    this.videoEditor.play();
    this.showNotification('开始播放', 'info');
  }

  private pause(): void {
    this.videoEditor.pause();
    this.showNotification('暂停播放', 'info');
  }

  private async exportVideo(): Promise<void> {
    if (this.videos.length === 0) {
      this.showNotification('请先添加视频文件', 'warning');
      return;
    }

    try {
      this.showProgress(true);
      await this.videoEditor.exportVideo(this.videos);
      this.showNotification('视频导出成功！', 'success');
    } catch (error) {
      console.error('Export error:', error);
      this.showNotification('视频导出失败', 'error');
    } finally {
      this.showProgress(false);
    }
  }

  private clearAll(): void {
    this.videos = [];
    this.updateVideoList();
    this.timeline.clear();
    this.videoEditor.clear();
    this.showNotification('已清空所有内容', 'info');
  }

  private loadDemo(): void {
    this.clearAll();
    const demoVideos = addDemoVideos();

    demoVideos.forEach(video => {
      this.addVideo(video);
    });

    this.showNotification('已加载演示视频', 'success');
  }

  private showNotification(
    message: string,
    type: 'success' | 'error' | 'warning' | 'info'
  ): void {
    // 简单的通知实现
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 15px 20px;
      border-radius: 8px;
      color: white;
      font-weight: bold;
      z-index: 1000;
      animation: slideIn 0.3s ease;
    `;

    const colors = {
      success: '#4CAF50',
      error: '#f44336',
      warning: '#ff9800',
      info: '#2196F3',
    };

    notification.style.backgroundColor = colors[type];
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
      notification.remove();
    }, 3000);
  }

  private showProgress(show: boolean): void {
    const progressBar = document.getElementById('progress-bar');
    if (progressBar) {
      progressBar.style.display = show ? 'block' : 'none';
      if (show) {
        // 模拟进度
        const fill = document.getElementById('progress-fill');
        if (fill) {
          let progress = 0;
          const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
              progress = 100;
              clearInterval(interval);
            }
            fill.style.width = `${progress}%`;
          }, 200);
        }
      }
    }
  }
}

// 全局实例，供 HTML 中的 onclick 使用
declare global {
  interface Window {
    app: MixVideoApp;
    timeline: Timeline;
  }
}

// 初始化应用
const app = new MixVideoApp();
window.app = app;
window.timeline = app['timeline'];
