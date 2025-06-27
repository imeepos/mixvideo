import React from 'react';

interface ProgressBarProps {
  progress: number; // 0-100
}

const ProgressBar: React.FC<ProgressBarProps> = ({ progress }) => {
  return (
    <div className="mt-8 bg-white/90 backdrop-blur-sm rounded-2xl p-6 border border-white/30 shadow-xl">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-3">
          <div className="w-4 h-4 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full animate-pulse"></div>
          <span className="text-lg font-bold text-gray-800">🚀 导出进度</span>
        </div>
        <div className="bg-gradient-to-r from-primary-500 via-secondary-500 to-accent-500 text-white px-6 py-3 rounded-full font-bold text-lg shadow-xl">
          {progress}%
        </div>
      </div>

      <div className="progress-bar relative overflow-hidden">
        <div
          className="progress-fill relative overflow-hidden"
          style={{ width: `${progress}%` }}
        >
          {/* 动画光效 */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
        </div>

        {/* 背景网格效果 */}
        <div className="absolute inset-0 opacity-20">
          <div className="w-full h-full bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200"></div>
        </div>
      </div>

      <div className="flex justify-between items-center mt-3 text-sm text-gray-600">
        <span>正在处理视频文件...</span>
        <span className="font-medium">
          {progress < 30 ? '📹 分析中' :
           progress < 70 ? '⚙️ 处理中' :
           progress < 100 ? '📦 打包中' : '✅ 完成'}
        </span>
      </div>
    </div>
  );
};

export default ProgressBar;
