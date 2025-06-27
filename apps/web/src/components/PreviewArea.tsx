import React from 'react';
import { Video } from '@mixvideo/shared';
import { Monitor } from 'lucide-react';

interface PreviewAreaProps {
  currentVideo: Video | null;
}

const PreviewArea: React.FC<PreviewAreaProps> = ({ currentVideo }) => {
  return (
    <section className="preview-area relative group">
      {currentVideo ? (
        <div className="relative w-full h-full rounded-3xl overflow-hidden">
          {currentVideo.url.startsWith('data:image/') ? (
            // Demo video (image)
            <div className="relative w-full h-full">
              <img
                src={currentVideo.url}
                alt={currentVideo.title}
                className="w-full h-full object-contain"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent"></div>
              <div className="absolute bottom-6 left-6 right-6">
                <div className="bg-white/90 backdrop-blur-sm text-gray-800 px-6 py-3 rounded-2xl shadow-xl">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="font-semibold">🎬 演示视频预览</span>
                  </div>
                  <p className="text-sm opacity-80 mt-1">{currentVideo.title}</p>
                </div>
              </div>
            </div>
          ) : (
            // Real video
            <div className="relative w-full h-full">
              <video
                src={currentVideo.url}
                controls
                className="w-full h-full object-contain rounded-3xl"
                title={currentVideo.title}
              />
              <div className="absolute top-4 left-4">
                <div className="bg-black/70 text-white px-4 py-2 rounded-full text-sm font-medium">
                  📹 {currentVideo.title}
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center h-full text-white/90 relative">
          {/* 背景装饰 */}
          <div className="absolute inset-0 flex items-center justify-center opacity-10">
            <div className="w-64 h-64 bg-white rounded-full blur-3xl animate-pulse-slow"></div>
          </div>

          <div className="relative z-10 text-center">
            <div className="relative mb-8">
              <Monitor size={80} className="mx-auto drop-shadow-2xl" />
              <div className="absolute inset-0 bg-white/20 rounded-2xl blur-xl"></div>
            </div>

            <div className="space-y-4">
              <h3 className="text-3xl font-bold drop-shadow-lg">
                🎥 视频预览区域
              </h3>
              <p className="text-xl opacity-90 max-w-md mx-auto leading-relaxed">
                点击左侧视频列表中的项目开始预览
              </p>
              <div className="flex items-center justify-center space-x-6 pt-4 text-white/80 font-medium">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-primary-400 rounded-full animate-ping"></div>
                  <span>高清预览</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-success-400 rounded-full animate-ping" style={{ animationDelay: '0.5s' }}></div>
                  <span>实时播放</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-secondary-400 rounded-full animate-ping" style={{ animationDelay: '1s' }}></div>
                  <span>全屏支持</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default PreviewArea;
