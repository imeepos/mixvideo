import { Video, formatDuration } from '@mixvideo/shared';

interface TimelineItem {
  video: Video;
  startTime: number;
  endTime: number;
  element: HTMLElement;
}

export class Timeline {
  private container: HTMLElement;
  private items: TimelineItem[] = [];
  private totalDuration: number = 0;
  private scale: number = 10; // 像素每秒

  constructor() {
    this.container = document.getElementById('timeline-content') as HTMLElement;
    this.initializeTimeline();
  }

  private initializeTimeline(): void {
    this.container.innerHTML = `
      <div class="timeline-header">
        <div class="timeline-controls">
          <button class="btn" onclick="timeline.zoomIn()">🔍+ 放大</button>
          <button class="btn" onclick="timeline.zoomOut()">🔍- 缩小</button>
          <span>总时长: <span id="total-duration">0:00</span></span>
        </div>
      </div>
      <div class="timeline-ruler" id="timeline-ruler"></div>
      <div class="timeline-tracks" id="timeline-tracks"></div>
    `;

    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
      .timeline-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e0e0e0;
      }
      
      .timeline-controls {
        display: flex;
        gap: 10px;
        align-items: center;
      }
      
      .timeline-ruler {
        height: 30px;
        background: #f5f5f5;
        border: 1px solid #ddd;
        position: relative;
        margin-bottom: 10px;
        overflow-x: auto;
      }
      
      .timeline-tracks {
        min-height: 100px;
        border: 1px solid #ddd;
        position: relative;
        overflow-x: auto;
        background: #fafafa;
      }
      
      .timeline-item {
        position: absolute;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        color: white;
        padding: 8px;
        cursor: move;
        user-select: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: column;
        justify-content: center;
      }
      
      .timeline-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      }
      
      .timeline-item-title {
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 2px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      
      .timeline-item-duration {
        font-size: 10px;
        opacity: 0.9;
      }
      
      .ruler-mark {
        position: absolute;
        top: 0;
        bottom: 0;
        border-left: 1px solid #999;
        font-size: 10px;
        padding-left: 2px;
        color: #666;
      }
      
      .playhead {
        position: absolute;
        top: 0;
        bottom: 0;
        width: 2px;
        background: #ff4444;
        z-index: 10;
        pointer-events: none;
      }
    `;
    document.head.appendChild(style);

    this.updateRuler();
  }

  public addVideo(video: Video): void {
    const startTime = this.totalDuration;
    const endTime = startTime + video.duration;

    const element = this.createTimelineItem(video, startTime, endTime);

    const item: TimelineItem = {
      video,
      startTime,
      endTime,
      element,
    };

    this.items.push(item);
    this.totalDuration = endTime;

    this.updateTimeline();
    this.makeDraggable(element, item);
  }

  public removeVideo(videoId: string): void {
    const index = this.items.findIndex(item => item.video.id === videoId);
    if (index !== -1) {
      const item = this.items[index];
      item.element.remove();
      this.items.splice(index, 1);

      // 重新计算时间轴
      this.recalculateTimeline();
    }
  }

  public clear(): void {
    this.items.forEach(item => item.element.remove());
    this.items = [];
    this.totalDuration = 0;
    this.updateTimeline();
  }

  private createTimelineItem(
    video: Video,
    startTime: number,
    endTime: number
  ): HTMLElement {
    const element = document.createElement('div');
    element.className = 'timeline-item';
    element.style.left = `${startTime * this.scale}px`;
    element.style.width = `${video.duration * this.scale}px`;
    element.style.top = '10px';

    element.innerHTML = `
      <div class="timeline-item-title">${video.title}</div>
      <div class="timeline-item-duration">${formatDuration(video.duration)}</div>
    `;

    const tracksContainer = document.getElementById('timeline-tracks');
    if (tracksContainer) {
      tracksContainer.appendChild(element);
    }

    return element;
  }

  private makeDraggable(element: HTMLElement, item: TimelineItem): void {
    let isDragging = false;
    let startX = 0;
    let startLeft = 0;

    element.addEventListener('mousedown', e => {
      isDragging = true;
      startX = e.clientX;
      startLeft = parseInt(element.style.left);
      element.style.cursor = 'grabbing';
      e.preventDefault();
    });

    document.addEventListener('mousemove', e => {
      if (!isDragging) return;

      const deltaX = e.clientX - startX;
      const newLeft = Math.max(0, startLeft + deltaX);
      const newStartTime = newLeft / this.scale;

      element.style.left = `${newLeft}px`;
      item.startTime = newStartTime;
      item.endTime = newStartTime + item.video.duration;
    });

    document.addEventListener('mouseup', () => {
      if (isDragging) {
        isDragging = false;
        element.style.cursor = 'move';
        this.recalculateTimeline();
      }
    });
  }

  private recalculateTimeline(): void {
    // 重新排序项目
    this.items.sort((a, b) => a.startTime - b.startTime);

    // 重新计算总时长
    this.totalDuration = Math.max(...this.items.map(item => item.endTime), 0);

    this.updateTimeline();
  }

  private updateTimeline(): void {
    this.updateRuler();
    this.updateTotalDuration();
  }

  private updateRuler(): void {
    const ruler = document.getElementById('timeline-ruler');
    if (!ruler) return;

    ruler.innerHTML = '';
    ruler.style.width = `${Math.max(this.totalDuration * this.scale, 800)}px`;

    // 添加时间刻度
    const interval = Math.max(1, Math.floor(10 / this.scale));
    for (let i = 0; i <= this.totalDuration; i += interval) {
      const mark = document.createElement('div');
      mark.className = 'ruler-mark';
      mark.style.left = `${i * this.scale}px`;
      mark.textContent = formatDuration(i);
      ruler.appendChild(mark);
    }
  }

  private updateTotalDuration(): void {
    const durationElement = document.getElementById('total-duration');
    if (durationElement) {
      durationElement.textContent = formatDuration(this.totalDuration);
    }

    // 更新轨道容器宽度
    const tracksContainer = document.getElementById('timeline-tracks');
    if (tracksContainer) {
      tracksContainer.style.width = `${Math.max(this.totalDuration * this.scale, 800)}px`;
    }
  }

  public zoomIn(): void {
    this.scale = Math.min(this.scale * 1.5, 50);
    this.updateItemPositions();
    this.updateTimeline();
  }

  public zoomOut(): void {
    this.scale = Math.max(this.scale / 1.5, 2);
    this.updateItemPositions();
    this.updateTimeline();
  }

  private updateItemPositions(): void {
    this.items.forEach(item => {
      item.element.style.left = `${item.startTime * this.scale}px`;
      item.element.style.width = `${item.video.duration * this.scale}px`;
    });
  }

  public getTimelineData(): TimelineItem[] {
    return [...this.items];
  }
}

// 全局实例供按钮调用
declare global {
  interface Window {
    timeline: Timeline;
  }
}
