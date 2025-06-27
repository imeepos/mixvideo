/**
 * React component example for @mixvideo/video-analyzer
 */

import React, { useState, useCallback, useRef } from 'react';
import { 
  VideoAnalyzer, 
  VideoAnalysisResult, 
  AnalysisProgress,
  HighlightDetection 
} from '../src';

interface VideoAnalyzerComponentProps {
  apiKey: string;
  onAnalysisComplete?: (result: VideoAnalysisResult) => void;
  onHighlightsExtracted?: (highlights: HighlightDetection[]) => void;
}

export const VideoAnalyzerComponent: React.FC<VideoAnalyzerComponentProps> = ({
  apiKey,
  onAnalysisComplete,
  onHighlightsExtracted
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState<AnalysisProgress | null>(null);
  const [result, setResult] = useState<VideoAnalysisResult | null>(null);
  const [highlights, setHighlights] = useState<HighlightDetection[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const analyzerRef = useRef<VideoAnalyzer | null>(null);

  // Initialize analyzer
  React.useEffect(() => {
    if (apiKey) {
      analyzerRef.current = new VideoAnalyzer({ apiKey });
    }
  }, [apiKey]);

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setHighlights([]);
      setError(null);
    }
  }, []);

  const handleAnalyze = useCallback(async () => {
    if (!selectedFile || !analyzerRef.current) return;

    setIsAnalyzing(true);
    setError(null);
    setProgress(null);

    try {
      const analysisResult = await analyzerRef.current.analyzeVideo(
        selectedFile,
        {
          enableSceneDetection: true,
          enableObjectDetection: true,
          enableSummarization: true,
          frameSamplingInterval: 2,
          maxFrames: 30,
          quality: 'medium',
          language: 'zh-CN'
        },
        (progressUpdate) => {
          setProgress(progressUpdate);
        }
      );

      setResult(analysisResult);
      onAnalysisComplete?.(analysisResult);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
    } finally {
      setIsAnalyzing(false);
      setProgress(null);
    }
  }, [selectedFile, onAnalysisComplete]);

  const handleExtractHighlights = useCallback(async () => {
    if (!selectedFile || !analyzerRef.current) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const extractedHighlights = await analyzerRef.current.extractHighlights(
        selectedFile,
        { language: 'zh-CN' }
      );

      setHighlights(extractedHighlights);
      onHighlightsExtracted?.(extractedHighlights);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Highlight extraction failed');
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedFile, onHighlightsExtracted]);

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="video-analyzer-component p-6 max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">🎬 Video Analyzer</h2>
      
      {/* File Upload */}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-2">
          Select Video File
        </label>
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleFileSelect}
          className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        {selectedFile && (
          <p className="mt-2 text-sm text-gray-600">
            Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={handleAnalyze}
          disabled={!selectedFile || isAnalyzing}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAnalyzing ? '🔄 Analyzing...' : '🎯 Analyze Video'}
        </button>
        
        <button
          onClick={handleExtractHighlights}
          disabled={!selectedFile || isAnalyzing}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAnalyzing ? '🔄 Extracting...' : '✨ Extract Highlights'}
        </button>
      </div>

      {/* Progress */}
      {progress && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">{progress.step}</span>
            <span className="text-sm text-gray-600">{progress.progress.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">❌ {error}</p>
        </div>
      )}

      {/* Analysis Results */}
      {result && (
        <div className="mb-6 space-y-6">
          <h3 className="text-xl font-semibold">📊 Analysis Results</h3>
          
          {/* Video Metadata */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">📹 Video Information</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>Duration: {formatDuration(result.metadata.duration)}</div>
              <div>Resolution: {result.metadata.width}×{result.metadata.height}</div>
              <div>Format: {result.metadata.format}</div>
              <div>Processing Time: {result.processingTime}ms</div>
            </div>
          </div>

          {/* Summary */}
          <div className="p-4 bg-blue-50 rounded-lg">
            <h4 className="font-medium mb-2">📝 Summary</h4>
            <p className="text-sm mb-2">{result.summary.description}</p>
            {result.summary.themes.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {result.summary.themes.map((theme, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-blue-200 text-blue-800 rounded-full text-xs"
                  >
                    {theme}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Scenes */}
          {result.scenes.length > 0 && (
            <div className="p-4 bg-green-50 rounded-lg">
              <h4 className="font-medium mb-2">🎭 Scenes ({result.scenes.length})</h4>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {result.scenes.map((scene, index) => (
                  <div key={index} className="p-2 bg-white rounded border">
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-medium text-sm">{scene.description}</span>
                      <span className="text-xs text-gray-500">
                        {formatDuration(scene.startTime)} - {formatDuration(scene.endTime)}
                      </span>
                    </div>
                    <div className="flex gap-2 text-xs">
                      <span className="px-2 py-1 bg-gray-100 rounded">
                        {scene.type}
                      </span>
                      <span className="px-2 py-1 bg-gray-100 rounded">
                        {(scene.confidence * 100).toFixed(1)}%
                      </span>
                      {scene.mood && (
                        <span className="px-2 py-1 bg-gray-100 rounded">
                          {scene.mood}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Objects */}
          {result.objects.length > 0 && (
            <div className="p-4 bg-yellow-50 rounded-lg">
              <h4 className="font-medium mb-2">🔍 Objects ({result.objects.length})</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-h-40 overflow-y-auto">
                {result.objects.map((obj, index) => (
                  <div key={index} className="p-2 bg-white rounded border text-sm">
                    <div className="font-medium">{obj.name}</div>
                    <div className="text-xs text-gray-500">
                      {formatDuration(obj.timestamp)} • {(obj.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Highlights */}
      {highlights.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-xl font-semibold">✨ Highlights ({highlights.length})</h3>
          <div className="space-y-3">
            {highlights.map((highlight, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  highlight.socialMediaReady
                    ? 'bg-green-50 border-green-500'
                    : 'bg-gray-50 border-gray-300'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium">{highlight.description}</h4>
                  <div className="flex gap-2 text-xs">
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                      {highlight.type}
                    </span>
                    <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded">
                      {(highlight.importance * 100).toFixed(0)}%
                    </span>
                    {highlight.socialMediaReady && (
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded">
                        📱 Social Ready
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  ⏰ {formatDuration(highlight.startTime)} - {formatDuration(highlight.endTime)}
                  ({(highlight.endTime - highlight.startTime).toFixed(1)}s)
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoAnalyzerComponent;
