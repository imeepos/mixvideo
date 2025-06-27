import React, { useState } from 'react';
import { Video, formatDuration } from '@mixvideo/shared';
import { Clock, ZoomIn, ZoomOut } from 'lucide-react';

interface TimelineProps {
  videos: Video[];
}

const Timeline: React.FC<TimelineProps> = ({ videos }) => {
  const [zoom, setZoom] = useState(1);
  
  const totalDuration = videos.reduce((sum, video) => sum + video.duration, 0);
  
  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.5, 5));
  };
  
  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.5, 0.5));
  };

  return (
    <section className="timeline">
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-3xl font-bold flex items-center gap-3 text-gray-800">
          <div className="relative">
            <Clock size={32} className="text-primary-600" />
            <div className="absolute inset-0 bg-primary-200 rounded-full blur-sm opacity-50"></div>
          </div>
          ⏰ 时间轴编辑器
        </h3>

        <div className="flex items-center gap-4">
          <div className="bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 text-white px-6 py-3 rounded-full font-bold shadow-xl">
            总时长: {formatDuration(totalDuration)}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleZoomOut}
              className="btn-secondary p-3 hover:scale-110 transition-transform"
              title="缩小视图"
            >
              <ZoomOut size={18} />
            </button>
            <div className="text-sm text-gray-600 font-medium px-2">
              {zoom.toFixed(1)}x
            </div>
            <button
              onClick={handleZoomIn}
              className="btn-secondary p-3 hover:scale-110 transition-transform"
              title="放大视图"
            >
              <ZoomIn size={18} />
            </button>
          </div>
        </div>
      </div>
      
      <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 min-h-[160px] border border-white/30 shadow-xl">
        {videos.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-gray-500">
            <div className="relative mb-4">
              <div className="w-16 h-16 bg-gradient-to-r from-primary-200 to-secondary-200 rounded-full flex items-center justify-center">
                <Clock size={24} className="text-primary-600" />
              </div>
              <div className="absolute inset-0 bg-primary-100 rounded-full blur-lg opacity-50"></div>
            </div>
            <p className="text-lg font-medium">📽️ 时间轴等待您的素材</p>
            <p className="text-sm opacity-75 mt-1">添加视频文件后，时间轴将在这里显示</p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Time ruler */}
            <div className="flex items-center text-sm font-medium text-gray-600 border-b-2 border-gradient-to-r from-primary-200 to-secondary-200 pb-3">
              <div className="mr-4 text-primary-600 font-bold">时间标尺:</div>
              {Array.from({ length: Math.ceil(totalDuration / 10) + 1 }, (_, i) => (
                <div
                  key={i}
                  className="flex-shrink-0 text-center relative"
                  style={{ width: `${100 * zoom}px` }}
                >
                  <div className="text-primary-600 font-semibold">{i * 10}s</div>
                  {i > 0 && (
                    <div className="absolute left-0 top-6 w-px h-4 bg-gray-300"></div>
                  )}
                </div>
              ))}
            </div>

            {/* Video blocks */}
            <div className="space-y-3">
              <div className="text-sm font-medium text-gray-700 mb-2">视频轨道:</div>
              <div className="flex items-center gap-2 overflow-x-auto pb-2">
                {videos.map((video, index) => {
                  const widthPercent = (video.duration / Math.max(totalDuration, 1)) * 100;
                  const widthPx = Math.max(widthPercent * zoom * 5, 100); // Minimum width of 100px

                  return (
                    <div
                      key={video.id}
                      className="bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 text-white rounded-xl p-4 cursor-move hover:shadow-xl hover:scale-105 transition-all duration-300 flex-shrink-0 relative overflow-hidden group"
                      style={{ width: `${widthPx}px` }}
                      title={`${video.title} - ${formatDuration(video.duration)}`}
                    >
                      {/* 背景动画效果 */}
                      <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>

                      <div className="relative z-10">
                        <div className="flex items-center justify-between mb-2">
                          <div className="text-xs font-bold bg-white/20 px-2 py-1 rounded-full">
                            #{index + 1}
                          </div>
                          <div className="text-xs opacity-90 font-medium">
                            {formatDuration(video.duration)}
                          </div>
                        </div>
                        <div className="text-sm font-semibold truncate">
                          {video.title}
                        </div>
                        <div className="text-xs opacity-80 mt-1">
                          {video.url.startsWith('data:image/') ? '🎬 演示' : '📹 用户'}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default Timeline;
