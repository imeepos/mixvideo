# MixVideo - 视频混剪工具

一个简单易用的基于 Web 的视频混剪工具，支持视频上传、预览、时间轴编辑和导出功能。

## 🚀 快速开始

### 启动开发服务器

```bash
cd apps/web
npm run dev
```

访问 http://localhost:3001 查看应用。

### 主要功能

#### 📁 视频上传

- **拖拽上传**: 直接将视频文件拖拽到上传区域
- **点击上传**: 点击"选择视频文件"按钮选择文件
- **支持格式**: MP4, WebM, OGG, AVI, MOV
- **文件大小限制**: 最大 100MB

#### 🎭 演示模式

- 点击"加载演示"按钮可以快速体验功能
- 自动加载 4 个演示视频片段
- 包含开场动画、主要内容、转场效果、结尾片段

#### 📹 视频管理

- **视频列表**: 显示所有已添加的视频
- **视频预览**: 点击视频项可以在预览区域查看
- **删除视频**: 每个视频项都有删除按钮
- **视频信息**: 显示文件名、时长、大小等信息

#### ⏱️ 时间轴编辑

- **可视化时间轴**: 直观显示视频片段的时间分布
- **拖拽排序**: 可以拖拽时间轴上的视频块调整顺序
- **缩放功能**: 支持时间轴的放大和缩小
- **总时长显示**: 实时显示整个项目的总时长

#### 🎬 播放控制

- **播放/暂停**: 控制当前预览视频的播放
- **视频预览**: 在预览区域查看选中的视频
- **播放进度**: 显示当前播放位置

#### 📤 导出功能

- **一键导出**: 将所有视频片段合并导出
- **进度显示**: 导出过程中显示进度条
- **格式支持**: 目前支持导出为文本格式（演示版本）

## 🛠️ 技术架构

### 前端技术栈

- **TypeScript**: 类型安全的 JavaScript
- **Vite**: 快速的构建工具和开发服务器
- **原生 Web APIs**: 使用 Canvas、File API、Drag & Drop API
- **CSS3**: 现代 CSS 特性，包括 Grid、Flexbox、动画

### 核心模块

#### VideoEditor (视频编辑器)

```typescript
class VideoEditor {
  play(): void; // 播放当前视频
  pause(): void; // 暂停播放
  loadVideo(video): void; // 加载视频到预览区
  exportVideo(videos): Promise<void>; // 导出视频
}
```

#### FileHandler (文件处理器)

```typescript
class FileHandler {
  processVideoFile(file): Promise<Video>; // 处理上传的视频文件
  getVideoThumbnail(video): Promise<string>; // 生成视频缩略图
  validateVideoFile(file): boolean; // 验证文件格式和大小
}
```

#### Timeline (时间轴)

```typescript
class Timeline {
  addVideo(video): void; // 添加视频到时间轴
  removeVideo(id): void; // 从时间轴移除视频
  zoomIn(): void; // 放大时间轴
  zoomOut(): void; // 缩小时间轴
}
```

## 🎨 界面特性

### 响应式设计

- 适配不同屏幕尺寸
- 移动端友好的触摸操作

### 动画效果

- 平滑的过渡动画
- 悬停效果和交互反馈
- 加载和状态变化动画

### 用户体验

- 直观的拖拽操作
- 实时的视觉反馈
- 清晰的状态提示

## 🔧 开发说明

### 项目结构

```
apps/web/
├── src/
│   ├── main.ts           # 主应用逻辑
│   ├── video-editor.ts   # 视频编辑器
│   ├── file-handler.ts   # 文件处理
│   ├── timeline.ts       # 时间轴组件
│   └── demo-data.ts      # 演示数据
├── index.html            # HTML 入口文件
├── vite.config.ts        # Vite 配置
└── package.json          # 依赖配置
```

### 构建和部署

```bash
# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 🚧 未来计划

- [ ] 集成 FFmpeg.js 实现真实的视频处理
- [ ] 添加视频剪切和分割功能
- [ ] 支持音频轨道编辑
- [ ] 添加转场效果和滤镜
- [ ] 支持字幕和文字叠加
- [ ] 云端存储和分享功能

## 📝 使用提示

1. **首次使用**: 建议先点击"加载演示"体验功能
2. **文件上传**: 支持多文件同时上传，会自动按顺序添加到时间轴
3. **预览操作**: 点击视频列表中的任意项目可以在预览区查看
4. **时间轴操作**: 可以拖拽视频块调整播放顺序
5. **导出功能**: 目前为演示版本，实际项目中需要集成视频处理库

---

🎬 享受视频创作的乐趣！
