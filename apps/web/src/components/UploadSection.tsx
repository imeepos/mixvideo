import React, { useRef, useState } from 'react';
import { Upload, FolderOpen } from 'lucide-react';

interface UploadSectionProps {
  onFilesSelected: (files: FileList) => void;
}

const UploadSection: React.FC<UploadSectionProps> = ({ onFilesSelected }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      onFilesSelected(files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFilesSelected(files);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <section className="mb-10">
      <div
        className={`upload-area ${isDragOver ? 'dragover' : ''} group`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <div className="relative mb-8">
          <div className="text-6xl mb-4 text-white/80 group-hover:text-white transition-colors duration-300">
            <FolderOpen size={80} className="mx-auto drop-shadow-lg" />
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-20 h-20 bg-white/20 rounded-full blur-xl group-hover:bg-white/30 transition-all duration-300"></div>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-3xl font-bold text-white drop-shadow-lg">
            🎥 拖拽视频文件到这里
          </h3>
          <p className="text-white/90 text-lg font-medium">
            支持 MP4、AVI、MOV 等格式 • 或者点击选择文件
          </p>

          <div className="pt-4">
            <button className="btn text-lg group-hover:scale-110 transition-transform duration-300">
              <Upload size={24} className="inline mr-3" />
              选择视频文件
            </button>
          </div>

          <div className="flex items-center justify-center space-x-6 pt-4 text-white/80 text-sm font-medium">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-success-400 rounded-full animate-pulse"></div>
              <span>多文件上传</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse" style={{ animationDelay: '0.3s' }}></div>
              <span>拖拽排序</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-secondary-400 rounded-full animate-pulse" style={{ animationDelay: '0.6s' }}></div>
              <span>实时预览</span>
            </div>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="video/*"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>
    </section>
  );
};

export default UploadSection;
