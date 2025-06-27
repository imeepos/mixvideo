/**
 * Core video analysis engine using Gemini AI
 */

import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { useGemini } from '@mixvideo/gemini';
import {
  VideoFile,
  VideoAnalysisResult,
  AnalysisMode,
  AnalysisOptions,
  AnalysisProgress,
  VideoMetadata,
  SceneDetection,
  ObjectDetection,
  ContentSummary,
  VideoAnalyzerError
} from './types';

const readFile = promisify(fs.readFile);
const writeFile = promisify(fs.writeFile);
const access = promisify(fs.access);

/**
 * Analysis cache entry
 */
export interface AnalysisCacheEntry {
  /** Video file path used as key */
  videoPath: string;
  /** GCS path of the uploaded video */
  gcsPath: string;
  /** Analysis prompt used */
  prompt: string;
  /** Analysis options used */
  options: AnalysisOptions;
  /** Analysis result */
  result: any;
  /** Timestamp when cached */
  timestamp: number;
  /** File checksum for validation */
  checksum: string;
}

/**
 * Analysis cache configuration
 */
export interface AnalysisCacheConfig {
  /** Enable analysis result caching */
  enableCache?: boolean;
  /** Cache directory path */
  cacheDir?: string;
  /** Cache expiry time in milliseconds (default: 7 days) */
  cacheExpiry?: number;
}

/**
 * Default analysis cache configuration
 */
export const DEFAULT_ANALYSIS_CACHE_CONFIG: Required<AnalysisCacheConfig> = {
  enableCache: true,
  cacheDir: '.video-analysis-cache',
  cacheExpiry: 7 * 24 * 60 * 60 * 1000 // 7 days
};

/**
 * Analysis prompts for different types of content analysis
 */
export const ANALYSIS_PROMPTS = {
  COMPREHENSIVE: `请对这个视频进行全面分析，包括：
1. 场景检测：识别视频中的不同场景，包括开始时间、结束时间和场景描述
2. 物体识别：识别视频中出现的主要物体、人物和元素
3. 内容总结：提供视频的整体描述、关键亮点和主要主题
4. 情感基调：分析视频的情感氛围和风格
5. 关键词提取：提取最相关的关键词

请以JSON格式返回结果，包含scenes、objects、summary等字段。`,

  PRODUCT_FOCUSED: `请专门分析这个视频中的产品相关内容：
1. 产品外观：颜色、形状、尺寸、风格
2. 材质分析：识别产品使用的材料
3. 功能特征：产品展示的功能和特性
4. 使用场景：产品的使用环境和场景
5. 目标受众：分析产品的目标用户群体
6. 品牌元素：识别品牌标识、logo等元素

请以JSON格式返回详细的产品分析结果。`,

  SCENE_DETECTION: `请详细分析视频中的场景变化：
1. 识别每个独立的场景
2. 标记场景的开始和结束时间
3. 描述每个场景的内容和特征
4. 评估场景转换的流畅性
5. 识别关键帧时间点

请以JSON格式返回场景分析结果。`,

  OBJECT_DETECTION: `请识别和分析视频中的所有重要物体：
1. 物体名称和类别
2. 物体在视频中出现的时间范围
3. 物体的重要性和相关性评分
4. 物体之间的关系和交互
5. 物体的属性和特征

请以JSON格式返回物体检测结果。`
};

/**
 * Video analysis engine class
 */
export class AnalysisEngine {
  private geminiClient: any = null;
  private cacheConfig: Required<AnalysisCacheConfig>;

  constructor(cacheConfig: AnalysisCacheConfig = {}) {
    // Gemini client will be initialized when needed
    this.cacheConfig = {
      ...DEFAULT_ANALYSIS_CACHE_CONFIG,
      ...cacheConfig
    };
  }

  /**
   * Initialize Gemini client
   */
  private async initializeGeminiClient(): Promise<void> {
    if (!this.geminiClient) {
      this.geminiClient = await useGemini();
    }
  }

  /**
   * Analyze video using Gemini AI
   */
  async analyzeVideo(
    videoFile: VideoFile,
    gcsPath: string,
    mode: AnalysisMode,
    options: AnalysisOptions = {},
    onProgress?: (progress: AnalysisProgress) => void
  ): Promise<VideoAnalysisResult> {
    const startTime = Date.now();
    
    const progress: AnalysisProgress = {
      step: 'Initializing analysis',
      progress: 0,
      currentFile: videoFile.name,
      stage: 'processing'
    };

    onProgress?.(progress);

    try {
      await this.initializeGeminiClient();

      progress.step = 'Preparing analysis prompts';
      progress.progress = 10;
      onProgress?.(progress);

      // Generate analysis prompts based on options
      const prompts = this.generateAnalysisPrompts(options);

      progress.step = 'Analyzing video content';
      progress.progress = 20;
      progress.stage = 'analysis';
      onProgress?.(progress);

      // Perform comprehensive analysis
      const analysisResults = await this.performComprehensiveAnalysis(
        videoFile,
        gcsPath,
        prompts,
        options,
        onProgress
      );

      progress.step = 'Processing analysis results';
      progress.progress = 90;
      onProgress?.(progress);

      // Build final result
      const result: VideoAnalysisResult = {
        metadata: await this.buildVideoMetadata(videoFile),
        analysisMode: mode,
        scenes: analysisResults.scenes || [],
        objects: analysisResults.objects || [],
        productFeatures: analysisResults.productFeatures,
        summary: analysisResults.summary || this.createDefaultSummary(),
        frameAnalysis: analysisResults.frameAnalysis,
        analyzedAt: new Date(),
        processingTime: Date.now() - startTime,
        qualityMetrics: this.calculateQualityMetrics(analysisResults)
      };

      progress.step = 'Analysis completed';
      progress.progress = 100;
      progress.stage = 'complete';
      onProgress?.(progress);

      return result;

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new VideoAnalyzerError(
        `Analysis failed for ${videoFile.name}: ${errorMessage}`,
        'ANALYSIS_FAILED',
        error
      );
    }
  }

  /**
   * Generate analysis prompts based on options
   */
  private generateAnalysisPrompts(options: AnalysisOptions): string[] {
    const prompts: string[] = [];

    if (options.enableSceneDetection) {
      prompts.push(ANALYSIS_PROMPTS.SCENE_DETECTION);
    }

    if (options.enableObjectDetection) {
      prompts.push(ANALYSIS_PROMPTS.OBJECT_DETECTION);
    }

    if (options.enableProductAnalysis) {
      prompts.push(ANALYSIS_PROMPTS.PRODUCT_FOCUSED);
    }

    if (options.enableSummarization || prompts.length === 0) {
      prompts.push(ANALYSIS_PROMPTS.COMPREHENSIVE);
    }

    // Add custom prompts if provided
    if (options.customPrompts) {
      prompts.push(...options.customPrompts);
    }

    return prompts;
  }

  /**
   * Perform comprehensive analysis using multiple prompts
   */
  private async performComprehensiveAnalysis(
    videoFile: VideoFile,
    gcsPath: string,
    prompts: string[],
    options: AnalysisOptions,
    onProgress?: (progress: AnalysisProgress) => void
  ): Promise<any> {
    const results: any = {
      scenes: [],
      objects: [],
      summary: null,
      productFeatures: null
    };

    for (let i = 0; i < prompts.length; i++) {
      const prompt = prompts[i];
      const progressPercent = 20 + ((i + 1) / prompts.length) * 60;

      onProgress?.({
        step: `Running analysis ${i + 1}/${prompts.length}`,
        progress: progressPercent,
        stage: 'analysis'
      } as AnalysisProgress);

      try {
        const analysisResult = await this.runSingleAnalysis(gcsPath, prompt, options, videoFile.path);
        this.mergeAnalysisResults(results, analysisResult);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.warn(`Analysis prompt ${i + 1} failed:`, errorMessage);
      }
    }

    return results;
  }

  /**
   * Run a single analysis with a specific prompt
   */
  private async runSingleAnalysis(
    gcsPath: string,
    prompt: string,
    options: AnalysisOptions,
    videoPath?: string
  ): Promise<any> {
    try {
      // 检查缓存
      if (videoPath) {
        const cachedResult = await this.checkAnalysisCache(videoPath, gcsPath, prompt, options);
        if (cachedResult) {
          console.log(`🎯 使用缓存的分析结果: ${path.basename(videoPath)}`);
          return cachedResult;
        }
      }

      // Create content array with video reference
      const contents = [
        {
          role: 'user',
          parts: [
            {
              text: prompt
            },
            {
              fileData: {
                mimeType: 'video/mp4', // Adjust based on actual video format
                fileUri: gcsPath
              }
            }
          ]
        }
      ];
      const response = await this.geminiClient.generateContent(
        contents,
        'gemini-2.5-flash',
        {
          temperature: 0.3,
          maxOutputTokens: 4096,
          topP: 0.8
        }
      );

      if (response.statusCode === 200 && response.response?.candidates?.[0]?.content?.parts?.[0]?.text) {
        const responseText = response.response.candidates[0].content.parts[0].text;
        console.log('✅ 分析完成，响应内容:', responseText);

        const parsedResult = this.parseAnalysisResponse(responseText);

        // 保存到缓存
        if (videoPath) {
          await this.saveAnalysisCache(videoPath, gcsPath, prompt, options, parsedResult);
        }

        return parsedResult;
      }

      throw new Error('Invalid response from Gemini API');

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      throw new VideoAnalyzerError(
        `Gemini analysis failed: ${errorMessage}`,
        'GEMINI_ANALYSIS_FAILED',
        error
      );
    }
  }

  /**
   * Parse analysis response from Gemini
   */
  private parseAnalysisResponse(responseText: string): any {
    try {
      // Try to extract JSON from the response
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }

      // If no JSON found, create structured response from text
      return this.parseTextResponse(responseText);

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.warn('Failed to parse JSON response, using text parsing:', errorMessage);
      return this.parseTextResponse(responseText);
    }
  }

  /**
   * Parse text response when JSON parsing fails
   */
  private parseTextResponse(text: string): any {
    const result: any = {
      scenes: [],
      objects: [],
      summary: {
        description: text.substring(0, 500),
        highlights: [],
        topics: [],
        keywords: []
      }
    };

    // Extract key information using regex patterns
    const sceneMatches = text.match(/场景\s*\d+[：:](.*?)(?=场景\s*\d+|$)/g);
    if (sceneMatches) {
      result.scenes = sceneMatches.map((match, index) => ({
        startTime: index * 10, // Estimate timing
        endTime: (index + 1) * 10,
        duration: 10,
        description: match.replace(/场景\s*\d+[：:]/, '').trim(),
        confidence: 0.7
      }));
    }

    // Extract objects/keywords
    const objectMatches = text.match(/(?:物体|对象|元素)[：:]([^。\n]+)/g);
    if (objectMatches) {
      result.objects = objectMatches.map(match => ({
        name: match.replace(/(?:物体|对象|元素)[：:]/, '').trim(),
        category: 'general',
        confidence: 0.6
      }));
    }

    return result;
  }

  /**
   * Merge multiple analysis results
   */
  private mergeAnalysisResults(target: any, source: any): void {
    if (source.scenes && Array.isArray(source.scenes)) {
      target.scenes.push(...source.scenes);
    }

    if (source.objects && Array.isArray(source.objects)) {
      target.objects.push(...source.objects);
    }

    if (source.summary && !target.summary) {
      target.summary = source.summary;
    }

    if (source.productFeatures && !target.productFeatures) {
      target.productFeatures = source.productFeatures;
    }
  }

  /**
   * Build video metadata
   */
  private async buildVideoMetadata(videoFile: VideoFile): Promise<VideoMetadata> {
    return {
      file: videoFile,
      technical: {
        codec: 'unknown',
        container: videoFile.format || 'unknown',
        hasAudio: true, // Assume has audio
        audioCodec: 'unknown'
      },
      content: {
        title: videoFile.name,
        description: `Video analysis for ${videoFile.name}`,
        tags: []
      }
    };
  }

  /**
   * Create default summary when none is provided
   */
  private createDefaultSummary(): ContentSummary {
    return {
      description: 'Video content analysis completed',
      highlights: [],
      topics: [],
      keywords: []
    };
  }

  /**
   * Calculate quality metrics for analysis results
   */
  private calculateQualityMetrics(results: any): {
    overallScore: number;
    detectionAccuracy: number;
    analysisDepth: number;
  } {
    let overallScore = 0.5; // Base score
    let detectionAccuracy = 0.5;
    let analysisDepth = 0.5;

    // Increase scores based on available data
    if (results.scenes && results.scenes.length > 0) {
      overallScore += 0.2;
      detectionAccuracy += 0.2;
    }

    if (results.objects && results.objects.length > 0) {
      overallScore += 0.2;
      detectionAccuracy += 0.2;
    }

    if (results.summary && results.summary.description) {
      overallScore += 0.1;
      analysisDepth += 0.3;
    }

    if (results.productFeatures) {
      analysisDepth += 0.2;
    }

    return {
      overallScore: Math.min(1.0, overallScore),
      detectionAccuracy: Math.min(1.0, detectionAccuracy),
      analysisDepth: Math.min(1.0, analysisDepth)
    };
  }

  /**
   * 确保缓存目录存在
   */
  private async ensureCacheDir(): Promise<void> {
    try {
      await access(this.cacheConfig.cacheDir);
    } catch {
      await fs.promises.mkdir(this.cacheConfig.cacheDir, { recursive: true });
    }
  }

  /**
   * 生成缓存键
   */
  private generateAnalysisCacheKey(
    videoPath: string,
    gcsPath: string,
    prompt: string,
    options: AnalysisOptions
  ): string {
    const crypto = require('crypto');
    const keyData = {
      videoPath,
      gcsPath,
      prompt: prompt.substring(0, 100), // 只取前100个字符避免键过长
      options: JSON.stringify(options)
    };
    return crypto.createHash('md5').update(JSON.stringify(keyData)).digest('hex');
  }

  /**
   * 计算文件校验和
   */
  private async calculateFileChecksum(filePath: string): Promise<string> {
    try {
      const crypto = require('crypto');
      const fileBuffer = await readFile(filePath);
      return crypto.createHash('md5').update(fileBuffer).digest('hex');
    } catch (error) {
      // 如果无法读取文件，使用路径和修改时间作为校验和
      const stats = await fs.promises.stat(filePath);
      const crypto = require('crypto');
      return crypto.createHash('md5').update(`${filePath}-${stats.mtime.getTime()}`).digest('hex');
    }
  }

  /**
   * 检查分析缓存
   */
  private async checkAnalysisCache(
    videoPath: string,
    gcsPath: string,
    prompt: string,
    options: AnalysisOptions
  ): Promise<any | null> {
    if (!this.cacheConfig.enableCache) {
      return null;
    }

    try {
      await this.ensureCacheDir();
      const cacheKey = this.generateAnalysisCacheKey(videoPath, gcsPath, prompt, options);
      const cacheFilePath = path.join(this.cacheConfig.cacheDir, `${cacheKey}.json`);

      // 检查缓存文件是否存在
      try {
        await access(cacheFilePath);
      } catch {
        return null; // 缓存文件不存在
      }

      // 读取缓存内容
      const cacheContent = await readFile(cacheFilePath, 'utf8');
      const cacheEntry: AnalysisCacheEntry = JSON.parse(cacheContent);

      // 检查缓存是否过期
      const now = Date.now();
      if (now - cacheEntry.timestamp > this.cacheConfig.cacheExpiry) {
        // 删除过期缓存
        await fs.promises.unlink(cacheFilePath).catch(() => {});
        return null;
      }

      // 检查文件是否发生变化
      const currentChecksum = await this.calculateFileChecksum(videoPath);
      if (currentChecksum !== cacheEntry.checksum) {
        // 文件已变化，删除缓存
        await fs.promises.unlink(cacheFilePath).catch(() => {});
        return null;
      }

      // 验证缓存条目的完整性
      if (cacheEntry.videoPath === videoPath &&
          cacheEntry.gcsPath === gcsPath &&
          cacheEntry.prompt === prompt) {
        return cacheEntry.result;
      }

      return null;
    } catch (error) {
      console.warn('检查分析缓存失败:', error);
      return null;
    }
  }

  /**
   * 保存分析结果到缓存
   */
  private async saveAnalysisCache(
    videoPath: string,
    gcsPath: string,
    prompt: string,
    options: AnalysisOptions,
    result: any
  ): Promise<void> {
    if (!this.cacheConfig.enableCache) {
      return;
    }

    try {
      await this.ensureCacheDir();
      const cacheKey = this.generateAnalysisCacheKey(videoPath, gcsPath, prompt, options);
      const cacheFilePath = path.join(this.cacheConfig.cacheDir, `${cacheKey}.json`);

      const checksum = await this.calculateFileChecksum(videoPath);
      const cacheEntry: AnalysisCacheEntry = {
        videoPath,
        gcsPath,
        prompt,
        options,
        result,
        timestamp: Date.now(),
        checksum
      };

      await writeFile(cacheFilePath, JSON.stringify(cacheEntry, null, 2), 'utf8');
      console.log(`💾 分析结果已缓存: ${path.basename(videoPath)}`);
    } catch (error) {
      console.warn('保存分析缓存失败:', error);
      // 缓存失败不应该影响主流程
    }
  }

  /**
   * 清理过期的分析缓存
   */
  async cleanExpiredAnalysisCache(): Promise<void> {
    if (!this.cacheConfig.enableCache) {
      return;
    }

    try {
      await this.ensureCacheDir();
      const files = await fs.promises.readdir(this.cacheConfig.cacheDir);
      const now = Date.now();
      let cleanedCount = 0;

      for (const file of files) {
        if (!file.endsWith('.json')) continue;

        const filePath = path.join(this.cacheConfig.cacheDir, file);
        try {
          const content = await readFile(filePath, 'utf8');
          const cacheEntry: AnalysisCacheEntry = JSON.parse(content);

          if (now - cacheEntry.timestamp > this.cacheConfig.cacheExpiry) {
            await fs.promises.unlink(filePath);
            cleanedCount++;
          }
        } catch (error) {
          // 删除损坏的缓存文件
          await fs.promises.unlink(filePath).catch(() => {});
          cleanedCount++;
        }
      }

      if (cleanedCount > 0) {
        console.log(`🧹 清理了 ${cleanedCount} 个过期分析缓存文件`);
      }
    } catch (error) {
      console.warn('清理分析缓存失败:', error);
    }
  }

  /**
   * 获取分析缓存统计信息
   */
  async getAnalysisCacheStats(): Promise<{
    totalFiles: number;
    totalSize: number;
    oldestEntry: Date | null;
    newestEntry: Date | null;
  }> {
    if (!this.cacheConfig.enableCache) {
      return { totalFiles: 0, totalSize: 0, oldestEntry: null, newestEntry: null };
    }

    try {
      await this.ensureCacheDir();
      const files = await fs.promises.readdir(this.cacheConfig.cacheDir);
      let totalFiles = 0;
      let totalSize = 0;
      let oldestTimestamp = Infinity;
      let newestTimestamp = 0;

      for (const file of files) {
        if (!file.endsWith('.json')) continue;

        const filePath = path.join(this.cacheConfig.cacheDir, file);
        try {
          const stats = await fs.promises.stat(filePath);
          const content = await readFile(filePath, 'utf8');
          const cacheEntry: AnalysisCacheEntry = JSON.parse(content);

          totalFiles++;
          totalSize += stats.size;
          oldestTimestamp = Math.min(oldestTimestamp, cacheEntry.timestamp);
          newestTimestamp = Math.max(newestTimestamp, cacheEntry.timestamp);
        } catch (error) {
          // 忽略损坏的文件
        }
      }

      return {
        totalFiles,
        totalSize,
        oldestEntry: oldestTimestamp === Infinity ? null : new Date(oldestTimestamp),
        newestEntry: newestTimestamp === 0 ? null : new Date(newestTimestamp)
      };
    } catch (error) {
      return { totalFiles: 0, totalSize: 0, oldestEntry: null, newestEntry: null };
    }
  }
}

/**
 * Convenience function to analyze a video
 */
export async function analyzeVideoWithGemini(
  videoFile: VideoFile,
  gcsPath: string,
  mode: AnalysisMode,
  options?: AnalysisOptions,
  onProgress?: (progress: AnalysisProgress) => void,
  cacheConfig?: AnalysisCacheConfig
): Promise<VideoAnalysisResult> {
  const engine = new AnalysisEngine(cacheConfig);
  return engine.analyzeVideo(videoFile, gcsPath, mode, options, onProgress);
}
