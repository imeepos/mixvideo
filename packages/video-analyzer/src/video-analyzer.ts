/**
 * Main VideoAnalyzer class - 完整的视频分析和组织工作流程
 *
 * 核心流程：
 * 1. AI分析视频内容和质量
 * 2. 根据内容匹配合适的文件夹
 * 3. 移动视频到相应文件夹并重命名
 */

import { VideoScanner } from './video-scanner';
import { VideoUploader, UploadConfig } from './video-uploader';
import { AnalysisEngine } from './analysis-engine';
import { ProductAnalyzer } from './product-analyzer';
import { FolderMatcher, FolderMatchConfig } from './folder-matcher';
import { ReportGenerator, ReportOptions } from './report-generator';
import { FrameAnalyzer } from './frame-analyzer';
import { WorkflowManager, WorkflowConfig, WorkflowResult, WorkflowProgress } from './workflow-manager';
import { FileOrganizer, FileOrganizerConfig, FileOperationResult } from './file-organizer';
import {
  VideoFile,
  VideoScanOptions,
  VideoAnalysisResult,
  AnalysisMode,
  AnalysisOptions,
  AnalysisProgress,
  FolderMatchResult,
  VideoAnalyzerConfig,
  VideoAnalyzerError
} from './types';

/**
 * 扩展的配置接口，包含工作流程配置
 */
export interface ExtendedVideoAnalyzerConfig extends VideoAnalyzerConfig {
  /** 工作流程配置 */
  workflow?: WorkflowConfig;
}

/**
 * Main VideoAnalyzer class - 完整的视频分析和组织系统
 */
export class VideoAnalyzer {
  private config: ExtendedVideoAnalyzerConfig;
  private scanner: VideoScanner;
  private uploader: VideoUploader | null = null;
  private analysisEngine: AnalysisEngine;
  private productAnalyzer: ProductAnalyzer;
  private folderMatcher: FolderMatcher | null = null;
  private reportGenerator: ReportGenerator;
  private frameAnalyzer: FrameAnalyzer;
  private workflowManager: WorkflowManager;
  private fileOrganizer: FileOrganizer;

  constructor(config: ExtendedVideoAnalyzerConfig = {}) {
    this.config = config;

    // Initialize core components
    this.scanner = new VideoScanner();
    this.analysisEngine = new AnalysisEngine();
    this.productAnalyzer = new ProductAnalyzer();
    this.reportGenerator = new ReportGenerator();
    this.frameAnalyzer = new FrameAnalyzer();

    // Initialize workflow components
    this.workflowManager = new WorkflowManager(config.workflow);
    this.fileOrganizer = new FileOrganizer(config.workflow?.fileOrganizerConfig);
  }

  /**
   * 🎯 核心方法：完整的视频分析和组织工作流程
   *
   * 执行完整流程：扫描 → 分析 → 匹配 → 移动重命名
   */
  async processVideosComplete(
    sourceDirectory: string,
    analysisMode: AnalysisMode,
    onProgress?: (progress: WorkflowProgress) => void
  ): Promise<WorkflowResult> {
    try {
      return await this.workflowManager.executeWorkflow(
        sourceDirectory,
        analysisMode,
        onProgress
      );
    } catch (error) {
      throw new VideoAnalyzerError(
        `完整工作流程执行失败: ${error instanceof Error ? error.message : String(error)}`,
        'WORKFLOW_FAILED',
        error
      );
    }
  }

  /**
   * 🔍 分析单个视频并推荐文件夹
   */
  async analyzeAndRecommend(
    videoFile: VideoFile,
    analysisMode: AnalysisMode,
    targetDirectory: string,
    options: AnalysisOptions = {}
  ): Promise<{
    analysis: VideoAnalysisResult;
    recommendations: FolderMatchResult[];
  }> {
    try {
      // 1. 分析视频
      const analysis = await this.analyzeVideo(videoFile, analysisMode, options);

      // 2. 匹配文件夹
      let recommendations: FolderMatchResult[] = [];
      if (this.folderMatcher) {
        recommendations = await this.folderMatcher.findMatchingFolders(analysis);
      } else {
        // 如果没有配置文件夹匹配器，创建临时的
        const tempMatcher = new FolderMatcher({ baseDirectory: targetDirectory });
        recommendations = await tempMatcher.findMatchingFolders(analysis);
      }

      return { analysis, recommendations };
    } catch (error) {
      throw new VideoAnalyzerError(
        `视频分析和推荐失败: ${error instanceof Error ? error.message : String(error)}`,
        'ANALYZE_RECOMMEND_FAILED',
        error
      );
    }
  }

  /**
   * 📁 组织单个视频文件
   */
  async organizeVideo(
    videoFile: VideoFile,
    analysisResult: VideoAnalysisResult,
    targetFolder: string
  ): Promise<FileOperationResult> {
    try {
      return await this.fileOrganizer.organizeVideo(videoFile, analysisResult, targetFolder);
    } catch (error) {
      throw new VideoAnalyzerError(
        `视频组织失败: ${error instanceof Error ? error.message : String(error)}`,
        'ORGANIZE_FAILED',
        error
      );
    }
  }

  /**
   * Scan directory for video files
   */
  async scanDirectory(
    directoryPath: string,
    options?: VideoScanOptions
  ): Promise<VideoFile[]> {
    try {
      return await this.scanner.scanDirectory(directoryPath);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new VideoAnalyzerError(
        `Directory scan failed: ${errorMessage}`,
        'SCAN_FAILED',
        error
      );
    }
  }

  /**
   * Analyze a single video file
   */
  async analyzeVideo(
    videoFile: VideoFile,
    mode: AnalysisMode,
    options: AnalysisOptions = {},
    onProgress?: (progress: AnalysisProgress) => void
  ): Promise<VideoAnalysisResult> {
    try {
      // Initialize uploader if not already done
      if (!this.uploader) {
        this.initializeUploader();
      }

      const progress: AnalysisProgress = {
        step: 'Starting analysis',
        progress: 0,
        currentFile: videoFile.name,
        stage: 'upload'
      };
      onProgress?.(progress);

      // Upload video to Gemini
      progress.step = 'Uploading video';
      progress.progress = 10;
      onProgress?.(progress);

      const uploadResult = await this.uploader!.uploadVideo(videoFile);
      if (!uploadResult.success) {
        throw new Error(`Upload failed: ${uploadResult.error}`);
      }

      // Perform analysis based on mode
      let analysisResult: VideoAnalysisResult;

      if (mode.type === 'gemini') {
        analysisResult = await this.analysisEngine.analyzeVideo(
          videoFile,
          uploadResult.gcsPath!,
          mode,
          options,
          onProgress
        );
      } else if (mode.type === 'gpt4') {
        // GPT-4 mode with frame analysis
        progress.step = 'Analyzing frames';
        progress.stage = 'analysis';
        onProgress?.(progress);

        const frameAnalysis = await this.frameAnalyzer.analyzeFrames(videoFile, options);
        
        // Create basic analysis result for GPT-4 mode
        analysisResult = {
          metadata: {
            file: videoFile,
            technical: {
              codec: 'unknown',
              container: videoFile.format || 'unknown',
              hasAudio: true
            }
          },
          analysisMode: mode,
          scenes: [],
          objects: [],
          summary: {
            description: 'GPT-4 frame-by-frame analysis completed',
            highlights: [],
            topics: [],
            keywords: []
          },
          frameAnalysis,
          analyzedAt: new Date(),
          processingTime: Date.now()
        };
      } else {
        throw new Error(`Unsupported analysis mode: ${mode.type}`);
      }

      // Add product analysis for Gemini mode (always enabled now since we use unified prompts)
      if (mode.type === 'gemini') {
        progress.step = 'Analyzing product features';
        progress.progress = 80;
        onProgress?.(progress);

        analysisResult.productFeatures = await this.productAnalyzer.analyzeProductFeatures(
          videoFile,
          uploadResult.gcsPath!,
          options
        );
      }

      progress.step = 'Analysis completed';
      progress.progress = 100;
      progress.stage = 'complete';
      onProgress?.(progress);

      return analysisResult;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new VideoAnalyzerError(
        `Video analysis failed: ${errorMessage}`,
        'ANALYSIS_FAILED',
        error
      );
    }
  }

  /**
   * 🚀 快速处理：分析目录中的所有视频并自动组织
   *
   * 这是最常用的方法，一键完成所有操作
   */
  async processDirectory(
    sourceDirectory: string,
    targetDirectory: string,
    analysisMode: AnalysisMode,
    options: {
      analysisOptions?: AnalysisOptions;
      fileOrganizerConfig?: FileOrganizerConfig;
      minConfidenceForMove?: number;
    } = {},
    onProgress?: (progress: WorkflowProgress) => void
  ): Promise<WorkflowResult> {
    // 更新工作流程配置
    this.workflowManager.updateConfig({
      folderMatchConfig: { baseDirectory: targetDirectory },
      fileOrganizerConfig: options.fileOrganizerConfig,
      minConfidenceForMove: options.minConfidenceForMove || 0.6,
      analysisOptions: options.analysisOptions
    });

    return await this.processVideosComplete(sourceDirectory, analysisMode, onProgress);
  }

  /**
   * Analyze multiple videos in a directory
   */
  async analyzeDirectory(
    directoryPath: string,
    mode: AnalysisMode,
    scanOptions?: VideoScanOptions,
    analysisOptions?: AnalysisOptions,
    onProgress?: (progress: AnalysisProgress) => void
  ): Promise<VideoAnalysisResult[]> {
    try {
      // Scan directory for videos
      const videoFiles = await this.scanDirectory(directoryPath, scanOptions);
      
      if (videoFiles.length === 0) {
        throw new Error('No video files found in directory');
      }

      const results: VideoAnalysisResult[] = [];

      // Analyze each video
      for (let i = 0; i < videoFiles.length; i++) {
        const videoFile = videoFiles[i];
        
        const overallProgress: AnalysisProgress = {
          step: `Analyzing video ${i + 1}/${videoFiles.length}: ${videoFile.name}`,
          progress: (i / videoFiles.length) * 100,
          currentFile: videoFile.name,
          stage: 'processing'
        };
        onProgress?.(overallProgress);

        try {
          const result = await this.analyzeVideo(videoFile, mode, analysisOptions);
          results.push(result);
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : String(error);
          console.warn(`Failed to analyze ${videoFile.name}:`, errorMessage);
        }
      }

      return results;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new VideoAnalyzerError(
        `Directory analysis failed: ${errorMessage}`,
        'DIRECTORY_ANALYSIS_FAILED',
        error
      );
    }
  }

  /**
   * Find matching folders for analysis results
   */
  async findMatchingFolders(
    analysisResults: VideoAnalysisResult[],
    folderConfig: FolderMatchConfig
  ): Promise<Record<string, FolderMatchResult[]>> {
    try {
      if (!this.folderMatcher) {
        this.folderMatcher = new FolderMatcher(folderConfig);
      }

      const matches: Record<string, FolderMatchResult[]> = {};

      for (const result of analysisResults) {
        const videoPath = result.metadata.file.path;
        matches[videoPath] = await this.folderMatcher.findMatchingFolders(result);
      }

      return matches;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new VideoAnalyzerError(
        `Folder matching failed: ${errorMessage}`,
        'FOLDER_MATCHING_FAILED',
        error
      );
    }
  }

  /**
   * Generate analysis report
   */
  async generateReport(
    analysisResults: VideoAnalysisResult[],
    folderMatches: Record<string, FolderMatchResult[]> = {},
    reportOptions: ReportOptions
  ): Promise<string> {
    try {
      return await this.reportGenerator.generateReport(
        analysisResults,
        folderMatches,
        reportOptions
      );
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new VideoAnalyzerError(
        `Report generation failed: ${errorMessage}`,
        'REPORT_GENERATION_FAILED',
        error
      );
    }
  }

  /**
   * Complete workflow: scan, analyze, match folders, and generate report
   */
  async analyzeDirectoryComplete(
    directoryPath: string,
    mode: AnalysisMode,
    options: {
      scanOptions?: VideoScanOptions;
      analysisOptions?: AnalysisOptions;
      folderConfig?: FolderMatchConfig;
      reportOptions?: ReportOptions;
      onProgress?: (progress: AnalysisProgress) => void;
    } = {}
  ): Promise<{
    analysisResults: VideoAnalysisResult[];
    folderMatches: Record<string, FolderMatchResult[]>;
    reportPath?: string;
  }> {
    try {
      const { scanOptions, analysisOptions, folderConfig, reportOptions, onProgress } = options;

      // Step 1: Analyze directory
      onProgress?.({
        step: 'Analyzing videos',
        progress: 0,
        stage: 'processing'
      } as AnalysisProgress);

      const analysisResults = await this.analyzeDirectory(
        directoryPath,
        mode,
        scanOptions,
        analysisOptions,
        onProgress
      );

      // Step 2: Find matching folders (if config provided)
      let folderMatches: Record<string, FolderMatchResult[]> = {};
      if (folderConfig) {
        onProgress?.({
          step: 'Finding matching folders',
          progress: 80,
          stage: 'processing'
        } as AnalysisProgress);

        folderMatches = await this.findMatchingFolders(analysisResults, folderConfig);
      }

      // Step 3: Generate report (if options provided)
      let reportPath: string | undefined;
      if (reportOptions) {
        onProgress?.({
          step: 'Generating report',
          progress: 90,
          stage: 'processing'
        } as AnalysisProgress);

        reportPath = await this.generateReport(analysisResults, folderMatches, reportOptions);
      }

      onProgress?.({
        step: 'Complete',
        progress: 100,
        stage: 'complete'
      } as AnalysisProgress);

      return {
        analysisResults,
        folderMatches,
        reportPath
      };

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new VideoAnalyzerError(
        `Complete analysis workflow failed: ${errorMessage}`,
        'WORKFLOW_FAILED',
        error
      );
    }
  }

  /**
   * Initialize uploader with configuration
   */
  private initializeUploader(): void {
    const uploadConfig: UploadConfig = {
      bucketName: this.config.upload?.bucketName || 'dy-media-storage',
      filePrefix: this.config.upload?.filePrefix || 'video-analysis',
      chunkSize: this.config.upload?.chunkSize,
      maxRetries: this.config.upload?.maxRetries,
      onProgress: (_progress) => {
        // Handle upload progress if needed
      }
    };

    this.uploader = new VideoUploader(uploadConfig);
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<VideoAnalyzerConfig>): void {
    this.config = { ...this.config, ...config };
    
    // Reinitialize components if needed
    if (config.upload && this.uploader) {
      this.initializeUploader();
    }
  }

  /**
   * Get current configuration
   */
  getConfig(): VideoAnalyzerConfig {
    return { ...this.config };
  }

  /**
   * Get analysis statistics
   */
  getAnalysisStatistics(results: VideoAnalysisResult[]): {
    totalVideos: number;
    totalProcessingTime: number;
    averageProcessingTime: number;
    totalScenes: number;
    totalObjects: number;
    averageQualityScore: number;
  } {
    const totalVideos = results.length;
    const totalProcessingTime = results.reduce((sum, r) => sum + r.processingTime, 0);
    const averageProcessingTime = totalVideos > 0 ? totalProcessingTime / totalVideos : 0;
    const totalScenes = results.reduce((sum, r) => sum + r.scenes.length, 0);
    const totalObjects = results.reduce((sum, r) => sum + r.objects.length, 0);
    
    const qualityScores = results
      .map(r => r.qualityMetrics?.overallScore || 0)
      .filter(score => score > 0);
    const averageQualityScore = qualityScores.length > 0 
      ? qualityScores.reduce((sum, score) => sum + score, 0) / qualityScores.length 
      : 0;

    return {
      totalVideos,
      totalProcessingTime,
      averageProcessingTime,
      totalScenes,
      totalObjects,
      averageQualityScore
    };
  }
}

/**
 * Convenience function to create VideoAnalyzer instance
 */
export function createVideoAnalyzer(config?: ExtendedVideoAnalyzerConfig): VideoAnalyzer {
  return new VideoAnalyzer(config);
}
