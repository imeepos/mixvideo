import React, { useState, useCallback } from 'react';
import { Music, Zap, BarChart3, Clock, Upload, Play, Download } from 'lucide-react';

interface AudioAnalysisResult {
  success: boolean;
  metadata: {
    audio_duration: number;
    total_beats: number;
    estimated_bpm: number;
    rhythm_stability: number;
  };
  beat_points: number[];
  highlights: Array<{
    time: number;
    type: string;
    description: string;
  }>;
  cut_suggestions: Array<{
    start: number;
    end: number;
    duration: number;
    type: string;
  }>;
}

interface AudioAnalyzerProps {
  onBeatPointsDetected?: (beatPoints: number[]) => void;
  onAnalysisComplete?: (result: AudioAnalysisResult) => void;
}

const AudioAnalyzer: React.FC<AudioAnalyzerProps> = ({ 
  onBeatPointsDetected, 
  onAnalysisComplete 
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AudioAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAudioUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    
    const file = e.target.files[0];
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('audio', file);
      
      const response = await fetch('http://localhost:8080/analyze', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (result.success) {
        setAnalysisResult(result);
        onBeatPointsDetected?.(result.beat_points);
        onAnalysisComplete?.(result);
        setError(null);
      } else {
        setError(result.error?.message || '音频分析失败');
      }
    } catch (error) {
      console.error('音频分析错误:', error);
      setError('音频分析失败，请确保API服务器正在运行 (端口8080)');
    } finally {
      setIsAnalyzing(false);
    }
  }, [onBeatPointsDetected, onAnalysisComplete]);

  const handleDemoAnalysis = useCallback(async () => {
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8080/demo');
      const result = await response.json();
      
      if (result.demo) {
        // 转换演示数据格式
        const demoResult: AudioAnalysisResult = {
          success: true,
          metadata: result.metadata,
          beat_points: result.beat_points,
          highlights: result.beat_points.slice(0, 5).map((time: number, index: number) => ({
            time,
            type: 'demo_beat',
            description: `演示节拍点 #${index + 1}`
          })),
          cut_suggestions: []
        };
        
        setAnalysisResult(demoResult);
        onBeatPointsDetected?.(demoResult.beat_points);
        onAnalysisComplete?.(demoResult);
        setError(null);
      }
    } catch (error) {
      console.error('演示分析错误:', error);
      setError('演示分析失败，请确保API服务器正在运行 (端口8080)');
    } finally {
      setIsAnalyzing(false);
    }
  }, [onBeatPointsDetected, onAnalysisComplete]);

  const exportBeatPoints = useCallback(() => {
    if (!analysisResult) return;
    
    const exportData = {
      metadata: analysisResult.metadata,
      beat_points: analysisResult.beat_points,
      highlights: analysisResult.highlights,
      export_timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
      type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `beat_analysis_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [analysisResult]);

  return (
    <section className="mb-10">
      <div className="bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 bg-accent-500/20 rounded-2xl">
            <Zap className="w-8 h-8 text-accent-400" />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-white">🎵 音频节拍分析</h2>
            <p className="text-white/70">智能检测音频节拍，为视频剪辑提供精准卡点</p>
          </div>
        </div>
        
        {/* 错误提示 */}
        {error && (
          <div className="mb-6 p-4 bg-danger-500/20 border border-danger-500/30 rounded-2xl">
            <div className="flex items-center space-x-2 text-danger-200">
              <Zap className="w-5 h-5" />
              <span className="font-medium">分析失败</span>
            </div>
            <p className="text-danger-100 mt-1">{error}</p>
          </div>
        )}
        
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* 上传音频 */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Music className="w-6 h-6 text-primary-400" />
              <h3 className="text-xl font-semibold text-white">上传音频文件</h3>
            </div>
            <p className="text-white/70">
              支持 WAV、MP3、M4A 等格式，获取精准的节拍检测结果
            </p>
            <label className="btn-secondary cursor-pointer inline-flex items-center space-x-2 w-full justify-center">
              <Upload className="w-5 h-5" />
              <span>{isAnalyzing ? '分析中...' : '选择音频文件'}</span>
              <input
                type="file"
                accept="audio/*,.wav,.mp3,.m4a,.aac,.flac"
                onChange={handleAudioUpload}
                disabled={isAnalyzing}
                className="hidden"
              />
            </label>
          </div>

          {/* 演示分析 */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-6 h-6 text-accent-400" />
              <h3 className="text-xl font-semibold text-white">演示功能</h3>
            </div>
            <p className="text-white/70">
              体验音频节拍检测功能，查看120 BPM测试音频的分析结果
            </p>
            <button
              onClick={handleDemoAnalysis}
              disabled={isAnalyzing}
              className="btn-accent w-full justify-center"
            >
              <Play className="w-5 h-5 mr-2" />
              {isAnalyzing ? '生成中...' : '演示分析'}
            </button>
          </div>
        </div>

        {/* 分析结果显示 */}
        {analysisResult && (
          <div className="space-y-6">
            {/* 统计信息 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-primary-500/20 rounded-2xl p-4 text-center border border-primary-500/30">
                <div className="text-3xl font-bold text-primary-300 mb-1">
                  {analysisResult.metadata.estimated_bpm}
                </div>
                <div className="text-sm text-white/70">BPM</div>
              </div>
              
              <div className="bg-secondary-500/20 rounded-2xl p-4 text-center border border-secondary-500/30">
                <div className="text-3xl font-bold text-secondary-300 mb-1">
                  {analysisResult.metadata.total_beats}
                </div>
                <div className="text-sm text-white/70">节拍点</div>
              </div>
              
              <div className="bg-accent-500/20 rounded-2xl p-4 text-center border border-accent-500/30">
                <div className="text-3xl font-bold text-accent-300 mb-1">
                  {analysisResult.metadata.audio_duration.toFixed(1)}s
                </div>
                <div className="text-sm text-white/70">时长</div>
              </div>

              <div className="bg-success-500/20 rounded-2xl p-4 text-center border border-success-500/30">
                <div className="text-3xl font-bold text-success-300 mb-1">
                  {(analysisResult.metadata.rhythm_stability * 100).toFixed(0)}%
                </div>
                <div className="text-sm text-white/70">稳定性</div>
              </div>
            </div>

            {/* 节拍点预览 */}
            <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-white flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-primary-400" />
                  节拍时间点
                </h4>
                <button
                  onClick={exportBeatPoints}
                  className="btn-secondary text-sm"
                >
                  <Download className="w-4 h-4 mr-1" />
                  导出
                </button>
              </div>
              
              <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                {analysisResult.beat_points.map((beat, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-primary-500/30 text-primary-200 rounded-full text-sm font-mono hover:bg-primary-500/50 transition-colors cursor-pointer"
                    title={`节拍点 ${index + 1}: ${beat.toFixed(3)}秒`}
                  >
                    {beat.toFixed(2)}s
                  </span>
                ))}
              </div>
              
              {analysisResult.beat_points.length > 20 && (
                <p className="text-white/50 text-sm mt-3">
                  显示了 {Math.min(20, analysisResult.beat_points.length)} / {analysisResult.beat_points.length} 个节拍点
                </p>
              )}
            </div>

            {/* 高光时刻 */}
            {analysisResult.highlights.length > 0 && (
              <div className="bg-white/5 rounded-2xl p-6 border border-white/10">
                <h4 className="font-semibold text-white flex items-center mb-4">
                  <Zap className="w-5 h-5 mr-2 text-accent-400" />
                  推荐卡点时刻
                </h4>
                <div className="space-y-3">
                  {analysisResult.highlights.slice(0, 8).map((highlight, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-accent-500/20 rounded-xl border border-accent-500/30 hover:bg-accent-500/30 transition-colors"
                    >
                      <div className="flex items-center space-x-3">
                        <span className="w-8 h-8 bg-accent-500 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {index + 1}
                        </span>
                        <span className="text-white font-mono text-lg">
                          {highlight.time.toFixed(2)}s
                        </span>
                      </div>
                      <span className="text-accent-200 text-sm">
                        {highlight.description}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 使用提示 */}
            <div className="bg-primary-500/10 rounded-2xl p-4 border border-primary-500/20">
              <h5 className="text-white font-medium mb-2">💡 使用提示</h5>
              <ul className="text-white/70 text-sm space-y-1">
                <li>• 节拍点已自动应用到时间轴，可用于精准剪辑</li>
                <li>• 推荐卡点时刻是最佳的视频切换位置</li>
                <li>• 点击导出按钮可保存分析结果为JSON文件</li>
                <li>• BPM值可用于匹配视频节奏</li>
              </ul>
            </div>
          </div>
        )}

        {/* 加载状态 */}
        {isAnalyzing && (
          <div className="text-center py-8">
            <div className="inline-flex items-center space-x-3">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-400"></div>
              <span className="text-white font-medium">正在分析音频节拍...</span>
            </div>
            <p className="text-white/60 text-sm mt-2">
              这可能需要几秒钟时间，请稍候
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default AudioAnalyzer;
