import React from 'react';
import { Film, Sparkles, Video } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="text-center mb-12 text-white relative">
      {/* 背景装饰 */}
      <div className="absolute inset-0 flex items-center justify-center opacity-10">
        <div className="w-96 h-96 bg-white rounded-full blur-3xl animate-pulse-slow"></div>
      </div>

      <div className="relative z-10">
        <div className="flex items-center justify-center gap-6 mb-6 animate-float">
          <div className="relative">
            <Film size={64} className="text-white drop-shadow-2xl" />
            <Sparkles size={24} className="absolute -top-2 -right-2 text-yellow-300 animate-pulse" />
          </div>
          <h1 className="text-6xl font-bold bg-gradient-to-r from-white via-primary-100 to-secondary-100 bg-clip-text text-transparent drop-shadow-2xl">
            MixVideo
          </h1>
          <div className="relative">
            <Video size={64} className="text-white drop-shadow-2xl" />
            <div className="absolute inset-0 bg-gradient-to-r from-primary-400 to-secondary-400 rounded-lg opacity-20 blur-sm"></div>
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-2xl font-medium opacity-95 drop-shadow-lg">
            🎬 专业级视频混剪工具
          </p>
          <p className="text-lg opacity-80 max-w-2xl mx-auto leading-relaxed">
            拖拽上传 • 智能剪辑 • 一键导出 • 让创意无限可能
          </p>
        </div>

        {/* 装饰性元素 */}
        <div className="flex justify-center mt-8 space-x-8 opacity-60">
          <div className="w-2 h-2 bg-white rounded-full animate-ping"></div>
          <div className="w-2 h-2 bg-white rounded-full animate-ping" style={{ animationDelay: '0.5s' }}></div>
          <div className="w-2 h-2 bg-white rounded-full animate-ping" style={{ animationDelay: '1s' }}></div>
        </div>
      </div>
    </header>
  );
};

export default Header;
