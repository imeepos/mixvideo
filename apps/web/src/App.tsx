import React, { useState } from 'react';
import { Video } from '@mixvideo/shared';
import Header from './components/Header';
import UploadSection from './components/UploadSection';
import VideoList from './components/VideoList';
import Timeline from './components/Timeline';
import PreviewArea from './components/PreviewArea';
import Controls from './components/Controls';
import ProgressBar from './components/ProgressBar';
import { addDemoVideos } from './demo-data';

function App() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [currentVideo, setCurrentVideo] = useState<Video | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);

  const handleFilesSelected = async (files: FileList) => {
    const newVideos: Video[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (file.type.startsWith('video/')) {
        const video: Video = {
          id: `video-${Date.now()}-${i}`,
          title: file.name,
          url: URL.createObjectURL(file),
          duration: 0, // Will be updated when video loads
          userId: 'user',
          createdAt: new Date(),
        };
        newVideos.push(video);
      }
    }
    
    setVideos(prev => [...prev, ...newVideos]);
  };

  const handleLoadDemo = () => {
    setVideos([]);
    const demoVideos = addDemoVideos();
    setVideos(demoVideos);
  };

  const handleVideoSelect = (video: Video) => {
    setCurrentVideo(video);
  };

  const handleRemoveVideo = (videoId: string) => {
    setVideos(prev => prev.filter(v => v.id !== videoId));
    if (currentVideo?.id === videoId) {
      setCurrentVideo(null);
    }
  };

  const handleExport = async () => {
    if (videos.length === 0) return;
    
    setIsExporting(true);
    setExportProgress(0);
    
    // Simulate export progress
    for (let i = 0; i <= 100; i += 10) {
      setExportProgress(i);
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    // Create a simple text file as demo export
    const exportData = videos.map(v => `${v.title} (${v.duration}s)`).join('\n');
    const blob = new Blob([exportData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mixvideo-export.txt';
    a.click();
    
    URL.revokeObjectURL(url);
    setIsExporting(false);
    setExportProgress(0);
  };

  const handleClear = () => {
    setVideos([]);
    setCurrentVideo(null);
  };

  return (
    <div className="min-h-screen">
      <div className="container mx-auto max-w-6xl px-4 py-6">
        <Header />
        
        <main className="card animate-fade-in">
          <UploadSection onFilesSelected={handleFilesSelected} />
          
          <VideoList 
            videos={videos}
            onVideoSelect={handleVideoSelect}
            onRemoveVideo={handleRemoveVideo}
          />
          
          <Timeline videos={videos} />
          
          <PreviewArea currentVideo={currentVideo} />
          
          <Controls
            onLoadDemo={handleLoadDemo}
            onPlay={() => {/* TODO: Implement play */}}
            onPause={() => {/* TODO: Implement pause */}}
            onExport={handleExport}
            onClear={handleClear}
            isExporting={isExporting}
          />
          
          {isExporting && <ProgressBar progress={exportProgress} />}
        </main>
      </div>
    </div>
  );
}

export default App;
