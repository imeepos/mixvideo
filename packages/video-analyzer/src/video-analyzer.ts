/**
 * Main VideoAnalyzer class - orchestrates all video analysis functionality
 */

import { VideoScanner } from './video-scanner';
import { VideoUploader, UploadConfig } from './video-uploader';
import { AnalysisEngine } from './analysis-engine';
import { ProductAnalyzer } from './product-analyzer';
import { FolderMatcher, FolderMatchConfig } from './folder-matcher';
import { ReportGenerator, ReportOptions } from './report-generator';
import { FrameAnalyzer } from './frame-analyzer';
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
 * Main VideoAnalyzer class
 */
export class VideoAnalyzer {
  private config: VideoAnalyzerConfig;
  private scanner: VideoScanner;
  private uploader: VideoUploader | null = null;
  private analysisEngine: AnalysisEngine;
  private productAnalyzer: ProductAnalyzer;
  private folderMatcher: FolderMatcher | null = null;
  private reportGenerator: ReportGenerator;
  private frameAnalyzer: FrameAnalyzer;

  constructor(config: VideoAnalyzerConfig = {}) {
    this.config = config;
    
    // Initialize components
    this.scanner = new VideoScanner();
    this.analysisEngine = new AnalysisEngine();
    this.productAnalyzer = new ProductAnalyzer();
    this.reportGenerator = new ReportGenerator();
    this.frameAnalyzer = new FrameAnalyzer();
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

      // Add product analysis if enabled
      if (options.enableProductAnalysis && mode.type === 'gemini') {
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
      bucketName: this.config.upload?.bucketName || 'default-bucket',
      filePrefix: this.config.upload?.filePrefix || 'video-analysis/',
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
export function createVideoAnalyzer(config?: VideoAnalyzerConfig): VideoAnalyzer {
  return new VideoAnalyzer(config);
}
