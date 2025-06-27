import React from 'react';
import { Video, formatDuration } from '@mixvideo/shared';
import { Play, Trash2, Video as VideoIcon } from 'lucide-react';

interface VideoListProps {
  videos: Video[];
  onVideoSelect: (video: Video) => void;
  onRemoveVideo: (videoId: string) => void;
}

const VideoList: React.FC<VideoListProps> = ({ 
  videos, 
  onVideoSelect, 
  onRemoveVideo 
}) => {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <section className="mb-10">
      <h3 className="text-3xl font-bold mb-8 flex items-center gap-3 text-white drop-shadow-lg">
        <div className="relative">
          <VideoIcon size={32} className="text-white" />
          <div className="absolute inset-0 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-lg opacity-30 blur-sm"></div>
        </div>
        📹 视频素材库
      </h3>

      <div className="space-y-4">
        {videos.length === 0 ? (
          <div className="text-center py-16 text-white/80">
            <div className="relative mb-6">
              <VideoIcon size={64} className="mx-auto opacity-60" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-16 h-16 bg-white/10 rounded-full blur-xl"></div>
              </div>
            </div>
            <div className="space-y-4">
              <p className="text-2xl font-semibold">🎬 开始您的创作之旅</p>
              <p className="text-lg opacity-90">点击"加载演示"体验功能，或上传您的视频文件</p>
              <p className="text-base opacity-75 max-w-md mx-auto">
                💡 支持多种格式 • 拖拽排序 • 实时预览 • 一键导出
              </p>
            </div>
          </div>
        ) : (
          videos.map((video, index) => (
            <div key={video.id} className="video-item group relative overflow-hidden">
              {/* 背景渐变效果 */}
              <div className="absolute inset-0 bg-gradient-to-r from-primary-500/10 to-secondary-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

              <div
                className="flex-1 cursor-pointer relative z-10"
                onClick={() => onVideoSelect(video)}
              >
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="w-12 h-12 bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 rounded-full flex items-center justify-center shadow-lg">
                      <Play size={20} className="text-white ml-1" />
                    </div>
                    <div className="absolute -top-1 -right-1 w-6 h-6 bg-success-500 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-md">
                      {index + 1}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="font-bold text-gray-800 text-lg group-hover:text-primary-600 transition-colors">
                      {video.title}
                    </div>
                    <div className="text-sm text-gray-600 flex items-center gap-4 mt-1">
                      <span className="flex items-center gap-1">
                        ⏱️ {formatDuration(video.duration)}
                      </span>
                      <span className="flex items-center gap-1">
                        📁 {formatFileSize(video.url.length * 1000)}
                      </span>
                      <span className="flex items-center gap-1">
                        🎯 {video.url.startsWith('data:image/') ? '演示视频' : '用户视频'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={() => onRemoveVideo(video.id)}
                className="btn-secondary hover:bg-danger-100 hover:text-danger-600 hover:border-danger-300 transition-all duration-200 relative z-10 px-4 py-2 text-sm"
                title="删除视频"
              >
                <Trash2 size={16} className="mr-1" />
                删除
              </button>
            </div>
          ))
        )}
      </div>
    </section>
  );
};

export default VideoList;
