import { Video } from '@mixvideo/shared';

// 创建演示用的视频数据
export function createDemoVideo(name: string, duration: number): Video {
  return {
    id: `demo-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    title: name,
    url: createDemoVideoBlob(duration, name),
    duration: duration,
    userId: 'demo-user',
    createdAt: new Date(),
  };
}

// 创建一个演示用的视频 Blob URL
function createDemoVideoBlob(duration: number, title: string): string {
  // 创建一个简单的 canvas 视频
  const canvas = document.createElement('canvas');
  canvas.width = 640;
  canvas.height = 360;
  const ctx = canvas.getContext('2d');

  if (!ctx) {
    return '';
  }

  // 绘制一个简单的演示画面
  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  gradient.addColorStop(0, '#667eea');
  gradient.addColorStop(1, '#764ba2');

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = 'white';
  ctx.font = '32px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('🎬 演示视频', canvas.width / 2, canvas.height / 2 - 40);

  ctx.font = '24px Arial';
  ctx.fillText(title, canvas.width / 2, canvas.height / 2);

  ctx.font = '18px Arial';
  ctx.fillText(`时长: ${duration}秒`, canvas.width / 2, canvas.height / 2 + 40);

  // 将 canvas 转换为 blob URL
  return canvas.toDataURL('image/png');
}

// 预定义的演示视频
export const demoVideos = [
  {
    name: '开场动画.mp4',
    duration: 5,
  },
  {
    name: '主要内容.mp4',
    duration: 30,
  },
  {
    name: '转场效果.mp4',
    duration: 3,
  },
  {
    name: '结尾片段.mp4',
    duration: 8,
  },
];

// 添加演示视频的函数
export function addDemoVideos(): Video[] {
  return demoVideos.map(demo => createDemoVideo(demo.name, demo.duration));
}
