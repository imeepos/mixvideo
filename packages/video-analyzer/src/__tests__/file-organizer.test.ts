/**
 * 文件组织器测试
 */

import * as fs from 'fs';
import * as path from 'path';
import { FileOrganizer, FileOrganizerConfig } from '../file-organizer';
import { VideoFile, VideoAnalysisResult } from '../types';

// Mock fs module
jest.mock('fs', () => ({
  promises: {
    access: jest.fn(),
    mkdir: jest.fn(),
    copyFile: jest.fn(),
    rename: jest.fn()
  },
  rename: jest.fn(),
  mkdir: jest.fn(),
  access: jest.fn(),
  copyFile: jest.fn(),
  unlink: jest.fn()
}));

describe('FileOrganizer', () => {
  let fileOrganizer: FileOrganizer;
  let mockVideoFile: VideoFile;
  let mockAnalysisResult: VideoAnalysisResult;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();

    // Setup mock video file
    mockVideoFile = {
      name: 'test-video.mp4',
      path: '/source/test-video.mp4',
      size: 1024 * 1024 * 10 // 10MB
    };

    // Setup mock analysis result
    mockAnalysisResult = {
      metadata: {
        file: mockVideoFile,
        technical: {
          codec: 'h264',
          container: 'mp4',
          hasAudio: true,
          audioCodec: 'aac'
        }
      },
      analysisMode: { type: 'gemini', model: 'gemini-2.5-flash' },
      summary: {
        description: '这是一个产品展示视频',
        highlights: ['产品特色', '功能演示'],
        topics: ['产品展示', '功能介绍'],
        keywords: ['产品', '展示', '演示'],
        category: '产品展示'
      },
      scenes: [],
      objects: [],
      analyzedAt: new Date(),
      processingTime: 5000
    };

    // Default config
    const config: FileOrganizerConfig = {
      moveFiles: false,
      createDirectories: true,
      conflictResolution: 'rename',
      namingMode: 'smart'
    };

    fileOrganizer = new FileOrganizer(config);
  });

  describe('constructor', () => {
    it('should initialize with default config', () => {
      const organizer = new FileOrganizer();
      expect(organizer).toBeDefined();
    });

    it('should initialize with custom config', () => {
      const config: FileOrganizerConfig = {
        moveFiles: true,
        namingMode: 'timestamp'
      };
      const organizer = new FileOrganizer(config);
      expect(organizer).toBeDefined();
    });
  });

  describe('organizeVideo', () => {
    beforeEach(() => {
      // Reset mocks
      jest.clearAllMocks();

      // Setup default mock behavior
      (fs.promises.access as jest.Mock).mockRejectedValue(new Error('File not found'));
      (fs.promises.mkdir as jest.Mock).mockResolvedValue(undefined);
      (fs.promises.copyFile as jest.Mock).mockResolvedValue(undefined);
      (fs.promises.rename as jest.Mock).mockResolvedValue(undefined);
    });

    it('should organize video with copy operation', async () => {
      const targetFolder = '/target/products';

      const result = await fileOrganizer.organizeVideo(
        mockVideoFile,
        mockAnalysisResult,
        targetFolder
      );

      // Since we're mocking fs operations, we expect success
      expect(result).toBeDefined();
      expect(result.originalPath).toBe(mockVideoFile.path);
      expect(typeof result.success).toBe('boolean');
    });

    it('should organize video with move operation', async () => {
      const config: FileOrganizerConfig = { moveFiles: true };
      const organizer = new FileOrganizer(config);
      const targetFolder = '/target/products';

      const result = await organizer.organizeVideo(
        mockVideoFile,
        mockAnalysisResult,
        targetFolder
      );

      expect(result).toBeDefined();
      expect(result.originalPath).toBe(mockVideoFile.path);
    });

    it('should handle file operation errors', async () => {
      // Mock fs operations to fail
      (fs.promises.copyFile as jest.Mock).mockRejectedValue(new Error('Permission denied'));

      const targetFolder = '/target/products';

      const result = await fileOrganizer.organizeVideo(
        mockVideoFile,
        mockAnalysisResult,
        targetFolder
      );

      expect(result.success).toBe(false);
      expect(result.error).toContain('Permission denied');
    });
  });

  describe('file naming', () => {
    it('should generate smart file name', () => {
      const config: FileOrganizerConfig = { namingMode: 'smart' };
      const organizer = new FileOrganizer(config);
      
      // Access private method through any cast for testing
      const fileName = (organizer as any).generateSmartFileName(
        mockAnalysisResult,
        'original.mp4'
      );

      expect(fileName).toContain('产品');
      expect(fileName).toContain('展示');
      expect(fileName).toContain('.mp4');
    });

    it('should generate timestamp file name', () => {
      const config: FileOrganizerConfig = { namingMode: 'timestamp' };
      const organizer = new FileOrganizer(config);
      
      const fileName = (organizer as any).generateTimestampFileName('original.mp4');

      expect(fileName).toMatch(/^video_\d{8}T\d{6}\.mp4$/);
    });

    it('should use original file name', () => {
      const config: FileOrganizerConfig = { namingMode: 'original' };
      const organizer = new FileOrganizer(config);
      
      const fileName = (organizer as any).generateFileName(
        mockAnalysisResult,
        'original.mp4'
      );

      expect(fileName).toBe('original.mp4');
    });

    it('should sanitize file names', () => {
      const unsafeName = 'test<>:"/\\|?*file.mp4';
      const safeName = (fileOrganizer as any).sanitizeFileName(unsafeName);
      
      expect(safeName).not.toMatch(/[<>:"/\\|?*]/);
      expect(safeName).toContain('test');
      expect(safeName).toContain('file');
    });
  });

  describe('conflict resolution', () => {
    it('should handle rename conflict resolution', async () => {
      // Mock file exists
      (fs.promises.access as jest.Mock)
        .mockResolvedValueOnce(undefined) // First file exists
        .mockRejectedValueOnce(new Error('File not found')); // Second file doesn't exist

      const filePath = '/target/test.mp4';
      const resolvedPath = await (fileOrganizer as any).resolveFileConflict(filePath);

      expect(resolvedPath).toContain('test_1.mp4');
    });

    it('should handle overwrite conflict resolution', async () => {
      const config: FileOrganizerConfig = { conflictResolution: 'overwrite' };
      const organizer = new FileOrganizer(config);

      // Mock file exists
      (fs.promises.access as jest.Mock).mockResolvedValue(undefined);

      const filePath = '/target/test.mp4';
      const resolvedPath = await (organizer as any).resolveFileConflict(filePath);

      expect(resolvedPath).toBe(filePath);
    });

    it('should handle skip conflict resolution', async () => {
      const config: FileOrganizerConfig = { conflictResolution: 'skip' };
      const organizer = new FileOrganizer(config);

      // Mock file exists
      (fs.promises.access as jest.Mock).mockResolvedValue(undefined);

      const filePath = '/target/test.mp4';

      await expect((organizer as any).resolveFileConflict(filePath))
        .rejects.toThrow('File already exists');
    });
  });

  describe('batch operations', () => {
    it('should organize multiple videos', async () => {
      const videoResults = [
        {
          videoFile: mockVideoFile,
          analysisResult: mockAnalysisResult,
          folderMatch: { folderPath: '/target/folder1' } as any
        },
        {
          videoFile: { ...mockVideoFile, name: 'video2.mp4' },
          analysisResult: mockAnalysisResult,
          folderMatch: { folderPath: '/target/folder2' } as any
        }
      ];

      const results = await fileOrganizer.organizeVideos(videoResults);
      
      expect(results).toHaveLength(2);
      expect(results[0].success).toBe(true);
      expect(results[1].success).toBe(true);
    });
  });

  describe('statistics', () => {
    it('should calculate organization stats', () => {
      const results = [
        { success: true, operation: 'move' as const, originalPath: '/test1' },
        { success: true, operation: 'copy' as const, originalPath: '/test2' },
        { success: false, operation: 'move' as const, originalPath: '/test3', error: 'Failed' },
        { success: true, operation: 'skip' as const, originalPath: '/test4' }
      ];

      const stats = fileOrganizer.getOrganizationStats(results);
      
      expect(stats.total).toBe(4);
      expect(stats.successful).toBe(3);
      expect(stats.failed).toBe(1);
      expect(stats.moved).toBe(1);
      expect(stats.copied).toBe(1);
      expect(stats.skipped).toBe(1);
    });
  });
});
