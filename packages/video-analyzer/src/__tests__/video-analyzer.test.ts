/**
 * Basic tests for VideoAnalyzer functionality
 */

import { VideoAnalyzer, createVideoAnalyzer } from '../video-analyzer';
import { VideoScanner } from '../video-scanner';
import { AnalysisMode } from '../types';

describe('VideoAnalyzer', () => {
  let analyzer: VideoAnalyzer;

  beforeEach(() => {
    analyzer = createVideoAnalyzer();
  });

  describe('initialization', () => {
    it('should create VideoAnalyzer instance', () => {
      expect(analyzer).toBeInstanceOf(VideoAnalyzer);
    });

    it('should create VideoAnalyzer with config', () => {
      const config = {
        upload: {
          bucketName: 'test-bucket',
          filePrefix: 'test-prefix/'
        }
      };
      const configuredAnalyzer = createVideoAnalyzer(config);
      expect(configuredAnalyzer).toBeInstanceOf(VideoAnalyzer);
      expect(configuredAnalyzer.getConfig()).toEqual(expect.objectContaining(config));
    });
  });

  describe('configuration', () => {
    it('should update configuration', () => {
      const newConfig = {
        upload: {
          bucketName: 'updated-bucket'
        }
      };
      analyzer.updateConfig(newConfig);
      expect(analyzer.getConfig()).toEqual(expect.objectContaining(newConfig));
    });

    it('should get current configuration', () => {
      const config = analyzer.getConfig();
      expect(config).toBeDefined();
      expect(typeof config).toBe('object');
    });
  });

  describe('statistics', () => {
    it('should calculate analysis statistics', () => {
      const mockResults = [
        {
          metadata: {
            file: { name: 'test1.mp4', path: '/test1.mp4', size: 1000, format: 'mp4' },
            technical: { codec: 'h264', container: 'mp4', hasAudio: true }
          },
          analysisMode: { type: 'gemini' as const, model: 'gemini-2.5-flash' },
          scenes: [{ startTime: 0, endTime: 10, duration: 10, description: 'test', confidence: 0.8 }],
          objects: [{ name: 'test', category: 'test', confidence: 0.8 }],
          summary: {
            description: 'test',
            highlights: [],
            topics: [],
            keywords: []
          },
          analyzedAt: new Date(),
          processingTime: 1000,
          qualityMetrics: {
            overallScore: 0.8,
            detectionAccuracy: 0.9,
            analysisDepth: 0.7
          }
        },
        {
          metadata: {
            file: { name: 'test2.mp4', path: '/test2.mp4', size: 2000, format: 'mp4' },
            technical: { codec: 'h264', container: 'mp4', hasAudio: true }
          },
          analysisMode: { type: 'gemini' as const, model: 'gemini-2.5-flash' },
          scenes: [],
          objects: [],
          summary: {
            description: 'test2',
            highlights: [],
            topics: [],
            keywords: []
          },
          analyzedAt: new Date(),
          processingTime: 2000,
          qualityMetrics: {
            overallScore: 0.9,
            detectionAccuracy: 0.8,
            analysisDepth: 0.9
          }
        }
      ];

      const stats = analyzer.getAnalysisStatistics(mockResults);

      expect(stats.totalVideos).toBe(2);
      expect(stats.totalProcessingTime).toBe(3000);
      expect(stats.averageProcessingTime).toBe(1500);
      expect(stats.totalScenes).toBe(1);
      expect(stats.totalObjects).toBe(1);
      expect(stats.averageQualityScore).toBeCloseTo(0.85, 2);
    });

    it('should handle empty results', () => {
      const stats = analyzer.getAnalysisStatistics([]);

      expect(stats.totalVideos).toBe(0);
      expect(stats.totalProcessingTime).toBe(0);
      expect(stats.averageProcessingTime).toBe(0);
      expect(stats.totalScenes).toBe(0);
      expect(stats.totalObjects).toBe(0);
      expect(stats.averageQualityScore).toBe(0);
    });
  });
});

describe('VideoScanner', () => {
  let scanner: VideoScanner;

  beforeEach(() => {
    scanner = new VideoScanner();
  });

  describe('file validation', () => {
    it('should identify video files correctly', () => {
      expect(scanner.isVideoFile('test.mp4')).toBe(true);
      expect(scanner.isVideoFile('test.mov')).toBe(true);
      expect(scanner.isVideoFile('test.avi')).toBe(true);
      expect(scanner.isVideoFile('test.txt')).toBe(false);
      expect(scanner.isVideoFile('test.jpg')).toBe(false);
    });

    it('should handle case insensitive extensions', () => {
      expect(scanner.isVideoFile('test.MP4')).toBe(true);
      expect(scanner.isVideoFile('test.MOV')).toBe(true);
      expect(scanner.isVideoFile('test.AVI')).toBe(true);
    });

    it('should handle files without extensions', () => {
      expect(scanner.isVideoFile('test')).toBe(false);
      expect(scanner.isVideoFile('')).toBe(false);
    });
  });
});

describe('Analysis Modes', () => {
  it('should support Gemini analysis mode', () => {
    const mode: AnalysisMode = {
      type: 'gemini',
      model: 'gemini-2.5-flash'
    };
    expect(mode.type).toBe('gemini');
    expect(mode.model).toBe('gemini-2.5-flash');
  });

  it('should support GPT-4 analysis mode', () => {
    const mode: AnalysisMode = {
      type: 'gpt4',
      model: 'gpt-4-vision-preview'
    };
    expect(mode.type).toBe('gpt4');
    expect(mode.model).toBe('gpt-4-vision-preview');
  });
});
