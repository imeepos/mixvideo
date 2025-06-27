import React from 'react';
import { 
  Play, 
  Pause, 
  Download, 
  Trash2, 
  Sparkles,
  Loader2
} from 'lucide-react';

interface ControlsProps {
  onLoadDemo: () => void;
  onPlay: () => void;
  onPause: () => void;
  onExport: () => void;
  onClear: () => void;
  isExporting: boolean;
}

const Controls: React.FC<ControlsProps> = ({
  onLoadDemo,
  onPlay,
  onPause,
  onExport,
  onClear,
  isExporting
}) => {
  return (
    <section className="mt-12">
      <div className="text-center mb-8">
        <h4 className="text-2xl font-bold text-white mb-2">🎮 控制面板</h4>
        <p className="text-white/80">使用下方按钮控制您的视频项目</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 max-w-4xl mx-auto">
        <button
          onClick={onLoadDemo}
          className="btn-accent group relative overflow-hidden"
          title="加载演示数据体验功能"
        >
          <Sparkles size={20} className="mr-2 group-hover:animate-spin" />
          <span className="relative z-10">✨ 演示</span>
        </button>

        <button
          onClick={onPlay}
          className="btn-success group relative overflow-hidden"
          title="播放当前选中的视频"
        >
          <Play size={20} className="mr-2 group-hover:scale-110 transition-transform" />
          <span className="relative z-10">▶️ 播放</span>
        </button>

        <button
          onClick={onPause}
          className="btn-secondary group relative overflow-hidden"
          title="暂停当前播放的视频"
        >
          <Pause size={20} className="mr-2 group-hover:scale-110 transition-transform" />
          <span className="relative z-10">⏸️ 暂停</span>
        </button>

        <button
          onClick={onExport}
          disabled={isExporting}
          className="btn disabled:opacity-50 disabled:cursor-not-allowed group relative overflow-hidden"
          title="导出混剪后的视频"
        >
          {isExporting ? (
            <>
              <Loader2 size={20} className="mr-2 animate-spin" />
              <span className="relative z-10">导出中...</span>
            </>
          ) : (
            <>
              <Download size={20} className="mr-2 group-hover:animate-bounce" />
              <span className="relative z-10">📥 导出</span>
            </>
          )}
        </button>

        <button
          onClick={onClear}
          className="btn-danger group relative overflow-hidden"
          title="清空所有视频文件"
        >
          <Trash2 size={20} className="mr-2 group-hover:animate-pulse" />
          <span className="relative z-10">🗑️ 清空</span>
        </button>
      </div>

      {/* 装饰性提示 */}
      <div className="flex justify-center mt-8 space-x-8 text-white/70 text-sm font-medium">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-success-400 rounded-full animate-pulse"></div>
          <span>实时预览</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse" style={{ animationDelay: '0.5s' }}></div>
          <span>快速导出</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-secondary-400 rounded-full animate-pulse" style={{ animationDelay: '1s' }}></div>
          <span>专业品质</span>
        </div>
      </div>
    </section>
  );
};

export default Controls;
