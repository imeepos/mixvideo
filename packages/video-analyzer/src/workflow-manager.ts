/**
 * 工作流程管理器 - 协调完整的视频分析和组织流程
 * 
 * 流程：扫描视频 → AI分析 → 匹配文件夹 → 移动文件并重命名
 */

import { VideoScanner } from './video-scanner';
import { VideoUploader } from './video-uploader';
import { AnalysisEngine } from './analysis-engine';
import { FolderMatcher, FolderMatchConfig } from './folder-matcher';
import { FileOrganizer, FileOrganizerConfig, FileOperationResult } from './file-organizer';
import {
  VideoFile,
  VideoScanOptions,
  VideoAnalysisResult,
  AnalysisMode,
  AnalysisOptions,
  FolderMatchResult,
  AnalysisProgress,
  VideoAnalyzerError
} from './types';

/**
 * 工作流程配置
 */
export interface WorkflowConfig {
  /** 视频扫描选项 */
  scanOptions?: VideoScanOptions;
  /** 分析选项 */
  analysisOptions?: AnalysisOptions;
  /** 文件夹匹配配置 */
  folderMatchConfig?: FolderMatchConfig;
  /** 文件组织配置 */
  fileOrganizerConfig?: FileOrganizerConfig;
  /** 最小匹配置信度（低于此值不会移动文件） */
  minConfidenceForMove?: number;
  /** 是否在移动前确认 */
  requireConfirmation?: boolean;
  /** 并发处理数量 */
  concurrency?: number;
}

/**
 * 工作流程结果
 */
export interface WorkflowResult {
  /** 处理的视频总数 */
  totalVideos: number;
  /** 成功分析的视频数 */
  analyzedVideos: number;
  /** 成功匹配文件夹的视频数 */
  matchedVideos: number;
  /** 成功组织的视频数 */
  organizedVideos: number;
  /** 详细结果 */
  results: Array<{
    videoFile: VideoFile;
    analysisResult?: VideoAnalysisResult;
    folderMatch?: FolderMatchResult;
    fileOperation?: FileOperationResult;
    error?: string;
  }>;
  /** 处理统计 */
  stats: {
    totalProcessingTime: number;
    averageProcessingTime: number;
    successRate: number;
  };
}

/**
 * 工作流程进度
 */
export interface WorkflowProgress {
  /** 当前阶段 */
  phase: 'scanning' | 'analyzing' | 'matching' | 'organizing' | 'complete';
  /** 当前步骤 */
  step: string;
  /** 进度百分比 (0-100) */
  progress: number;
  /** 已处理的视频数 */
  processedVideos: number;
  /** 总视频数 */
  totalVideos: number;
  /** 处理阶段 */
  stage: 'upload' | 'processing' | 'analysis' | 'complete';
}

/**
 * 工作流程管理器
 */
export class WorkflowManager {
  private scanner: VideoScanner;
  private uploader: VideoUploader;
  private analysisEngine: AnalysisEngine;
  private folderMatcher: FolderMatcher | null = null;
  private fileOrganizer: FileOrganizer;
  private config: Required<WorkflowConfig>;

  constructor(config: WorkflowConfig = {}) {
    this.config = {
      scanOptions: {},
      analysisOptions: {},
      folderMatchConfig: { baseDirectory: '' },
      fileOrganizerConfig: {},
      minConfidenceForMove: 0.6,
      requireConfirmation: false,
      concurrency: 3,
      ...config
    };

    // 初始化组件
    this.scanner = new VideoScanner();
    this.uploader = new VideoUploader({
      bucketName: 'dy-media-storage',
      filePrefix: 'analysis'
    });
    this.analysisEngine = new AnalysisEngine();
    this.fileOrganizer = new FileOrganizer(this.config.fileOrganizerConfig);

    // 初始化文件夹匹配器（如果配置了）
    if (this.config.folderMatchConfig.baseDirectory) {
      this.folderMatcher = new FolderMatcher(this.config.folderMatchConfig);
    }
  }

  /**
   * 执行完整的工作流程
   */
  async executeWorkflow(
    sourceDirectory: string,
    analysisMode: AnalysisMode,
    onProgress?: (progress: WorkflowProgress) => void
  ): Promise<WorkflowResult> {
    const startTime = Date.now();
    const result: WorkflowResult = {
      totalVideos: 0,
      analyzedVideos: 0,
      matchedVideos: 0,
      organizedVideos: 0,
      results: [],
      stats: {
        totalProcessingTime: 0,
        averageProcessingTime: 0,
        successRate: 0
      }
    };

    try {
      // 阶段1: 扫描视频文件
      onProgress?.({
        phase: 'scanning',
        step: '扫描视频文件',
        progress: 0,
        processedVideos: 0,
        totalVideos: 0,
        stage: 'processing'
      });

      const videoFiles = await this.scanner.scanDirectory(sourceDirectory);

      result.totalVideos = videoFiles.length;

      if (videoFiles.length === 0) {
        throw new VideoAnalyzerError('未找到视频文件', 'NO_VIDEOS_FOUND');
      }

      // 阶段2: 分析视频
      onProgress?.({
        phase: 'analyzing',
        step: '开始分析视频',
        progress: 10,
        processedVideos: 0,
        totalVideos: videoFiles.length,
        stage: 'analysis'
      });

      await this.processVideosInBatches(
        videoFiles,
        analysisMode,
        result,
        onProgress
      );

      // 计算统计信息
      const endTime = Date.now();
      result.stats.totalProcessingTime = endTime - startTime;
      result.stats.averageProcessingTime = result.analyzedVideos > 0 
        ? result.stats.totalProcessingTime / result.analyzedVideos 
        : 0;
      result.stats.successRate = result.totalVideos > 0 
        ? result.organizedVideos / result.totalVideos 
        : 0;

      onProgress?.({
        phase: 'complete',
        step: '工作流程完成',
        progress: 100,
        processedVideos: result.totalVideos,
        totalVideos: result.totalVideos,
        stage: 'complete'
      });

      return result;

    } catch (error) {
      throw new VideoAnalyzerError(
        `工作流程执行失败: ${error instanceof Error ? error.message : String(error)}`,
        'WORKFLOW_FAILED',
        error
      );
    }
  }

  /**
   * 批量处理视频
   */
  private async processVideosInBatches(
    videoFiles: VideoFile[],
    analysisMode: AnalysisMode,
    result: WorkflowResult,
    onProgress?: (progress: WorkflowProgress) => void
  ): Promise<void> {
    const batchSize = this.config.concurrency;
    
    for (let i = 0; i < videoFiles.length; i += batchSize) {
      const batch = videoFiles.slice(i, i + batchSize);
      const batchPromises = batch.map(videoFile => 
        this.processVideoFile(videoFile, analysisMode, result, onProgress)
      );

      await Promise.allSettled(batchPromises);

      // 更新进度
      const processedCount = Math.min(i + batchSize, videoFiles.length);
      const progress = Math.round((processedCount / videoFiles.length) * 80) + 10; // 10-90%

      onProgress?.({
        phase: 'analyzing',
        step: `已处理 ${processedCount}/${videoFiles.length} 个视频`,
        progress,
        processedVideos: processedCount,
        totalVideos: videoFiles.length,
        stage: 'analysis'
      });
    }
  }

  /**
   * 处理单个视频文件
   */
  private async processVideoFile(
    videoFile: VideoFile,
    analysisMode: AnalysisMode,
    result: WorkflowResult,
    onProgress?: (progress: WorkflowProgress) => void
  ): Promise<void> {
    const videoResult: WorkflowResult['results'][0] = {
      videoFile
    };

    try {
      // 步骤1: 分析视频
      const analysisResult = await this.analyzeVideo(videoFile, analysisMode);
      videoResult.analysisResult = analysisResult;
      result.analyzedVideos++;

      // 步骤2: 匹配文件夹
      if (this.folderMatcher) {
        const folderMatches = await this.folderMatcher.findMatchingFolders(analysisResult);
        
        if (folderMatches.length > 0) {
          const bestMatch = folderMatches[0];
          videoResult.folderMatch = bestMatch;
          result.matchedVideos++;

          // 步骤3: 组织文件（如果置信度足够高）
          if (bestMatch.confidence >= this.config.minConfidenceForMove) {
            if (!this.config.requireConfirmation || await this.confirmFileMove(videoFile, bestMatch)) {
              const fileOperation = await this.fileOrganizer.organizeVideo(
                videoFile,
                analysisResult,
                bestMatch.folderPath
              );
              
              videoResult.fileOperation = fileOperation;
              
              if (fileOperation.success) {
                result.organizedVideos++;
              }
            }
          }
        }
      }

    } catch (error) {
      videoResult.error = error instanceof Error ? error.message : String(error);
    }

    result.results.push(videoResult);
  }

  /**
   * 分析单个视频
   */
  private async analyzeVideo(
    videoFile: VideoFile,
    analysisMode: AnalysisMode
  ): Promise<VideoAnalysisResult> {
    // 上传视频
    const uploadResult = await this.uploader.uploadVideo(videoFile);
    if (!uploadResult.success) {
      throw new Error(`视频上传失败: ${uploadResult.error}`);
    }

    // 执行分析
    return await this.analysisEngine.analyzeVideo(
      videoFile,
      uploadResult.gcsPath!,
      analysisMode,
      this.config.analysisOptions
    );
  }

  /**
   * 确认文件移动（可以被子类重写）
   */
  protected async confirmFileMove(
    videoFile: VideoFile,
    folderMatch: FolderMatchResult
  ): Promise<boolean> {
    // 默认实现：总是确认
    // 在实际应用中，这里可以显示UI确认对话框
    console.log(`确认移动文件: ${videoFile.name} -> ${folderMatch.folderPath} (置信度: ${folderMatch.confidence})`);
    return true;
  }

  /**
   * 获取工作流程配置
   */
  getConfig(): WorkflowConfig {
    return { ...this.config };
  }

  /**
   * 更新工作流程配置
   */
  updateConfig(newConfig: Partial<WorkflowConfig>): void {
    this.config = { ...this.config, ...newConfig };
    
    // 重新初始化相关组件
    if (newConfig.fileOrganizerConfig) {
      this.fileOrganizer = new FileOrganizer(this.config.fileOrganizerConfig);
    }
    
    if (newConfig.folderMatchConfig && newConfig.folderMatchConfig.baseDirectory) {
      this.folderMatcher = new FolderMatcher(this.config.folderMatchConfig);
    }
  }

  /**
   * 生成工作流程报告
   */
  generateReport(result: WorkflowResult): string {
    const { stats } = result;
    
    return `
# 视频分析工作流程报告

## 处理统计
- 总视频数: ${result.totalVideos}
- 成功分析: ${result.analyzedVideos}
- 成功匹配: ${result.matchedVideos}
- 成功组织: ${result.organizedVideos}
- 成功率: ${(stats.successRate * 100).toFixed(1)}%

## 性能统计
- 总处理时间: ${(stats.totalProcessingTime / 1000).toFixed(1)}秒
- 平均处理时间: ${(stats.averageProcessingTime / 1000).toFixed(1)}秒/视频

## 详细结果
${result.results.map((r, i) => `
${i + 1}. ${r.videoFile.name}
   - 分析: ${r.analysisResult ? '✓' : '✗'}
   - 匹配: ${r.folderMatch ? `✓ (${r.folderMatch.confidence.toFixed(2)})` : '✗'}
   - 组织: ${r.fileOperation?.success ? '✓' : '✗'}
   ${r.error ? `   - 错误: ${r.error}` : ''}
`).join('')}
    `.trim();
  }
}
