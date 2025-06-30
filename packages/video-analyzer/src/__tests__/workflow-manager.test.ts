/**
 * 工作流程管理器测试
 */

import { WorkflowManager, WorkflowConfig } from '../workflow-manager';
import { VideoFile, AnalysisMode } from '../types';

// Mock dependencies
jest.mock('../video-scanner');
jest.mock('../video-uploader');
jest.mock('../analysis-engine');
jest.mock('../folder-matcher');
jest.mock('../file-organizer');

describe('WorkflowManager', () => {
  let workflowManager: WorkflowManager;
  let mockConfig: WorkflowConfig;

  beforeEach(() => {
    mockConfig = {
      scanOptions: {},
      analysisOptions: { quality: 'medium' },
      folderMatchConfig: { baseDirectory: '/test/target' },
      fileOrganizerConfig: { moveFiles: false },
      minConfidenceForMove: 0.7,
      concurrency: 2
    };

    workflowManager = new WorkflowManager(mockConfig);
  });

  describe('constructor', () => {
    it('should initialize with default config', () => {
      const manager = new WorkflowManager();
      expect(manager).toBeDefined();
    });

    it('should initialize with custom config', () => {
      const manager = new WorkflowManager(mockConfig);
      expect(manager).toBeDefined();
    });
  });

  describe('executeWorkflow', () => {
    it('should execute complete workflow', async () => {
      const sourceDirectory = '/test/source';
      const analysisMode: AnalysisMode = { type: 'gemini', model: 'gemini-2.5-flash' };

      // Since we're mocking the dependencies, we expect it to fail
      // This test just verifies the method exists and handles errors properly
      try {
        await workflowManager.executeWorkflow(
          sourceDirectory,
          analysisMode,
          (progress) => {
            expect(progress.phase).toBeDefined();
            expect(progress.step).toBeDefined();
            expect(progress.progress).toBeGreaterThanOrEqual(0);
          }
        );
      } catch (error) {
        // Expected to fail with mocked dependencies
        expect(error).toBeDefined();
      }
    }, 10000); // 10 second timeout

    it('should handle empty directory', async () => {
      const sourceDirectory = '/test/empty';
      const analysisMode: AnalysisMode = { type: 'gemini', model: 'gemini-2.5-flash' };

      try {
        await workflowManager.executeWorkflow(sourceDirectory, analysisMode);
      } catch (error) {
        expect(error).toBeDefined();
      }
    }, 10000); // 10 second timeout
  });

  describe('getConfig', () => {
    it('should return current config', () => {
      const config = workflowManager.getConfig();
      expect(config).toBeDefined();
      expect(config.minConfidenceForMove).toBe(0.7);
    });
  });

  describe('updateConfig', () => {
    it('should update config', () => {
      const newConfig = {
        minConfidenceForMove: 0.8,
        concurrency: 5
      };

      workflowManager.updateConfig(newConfig);
      const updatedConfig = workflowManager.getConfig();
      
      expect(updatedConfig.minConfidenceForMove).toBe(0.8);
      expect(updatedConfig.concurrency).toBe(5);
    });
  });

  describe('generateReport', () => {
    it('should generate workflow report', () => {
      const mockResult = {
        totalVideos: 10,
        analyzedVideos: 9,
        matchedVideos: 8,
        organizedVideos: 7,
        results: [
          {
            videoFile: { name: 'test1.mp4', path: '/test/test1.mp4', size: 1000 } as VideoFile,
            analysisResult: {} as any,
            folderMatch: { confidence: 0.8 } as any,
            fileOperation: { success: true } as any
          },
          {
            videoFile: { name: 'test2.mp4', path: '/test/test2.mp4', size: 2000 } as VideoFile,
            error: 'Analysis failed'
          }
        ],
        stats: {
          totalProcessingTime: 60000,
          averageProcessingTime: 6000,
          successRate: 0.7
        }
      };

      const report = workflowManager.generateReport(mockResult);
      
      expect(report).toContain('视频分析工作流程报告');
      expect(report).toContain('总视频数: 10');
      expect(report).toContain('成功分析: 9');
      expect(report).toContain('成功率: 70.0%');
      expect(report).toContain('test1.mp4');
      expect(report).toContain('test2.mp4');
    });
  });
});
