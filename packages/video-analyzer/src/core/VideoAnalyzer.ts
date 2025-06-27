import { GoogleGenerativeAI } from '@google/generative-ai';
import {
  VideoAnalysisResult,
  VideoMetadata,
  AnalysisOptions,
  GeminiConfig,
  ProgressCallback,
  VideoAnalyzerError,
  VideoFrame,
  SceneDetection,
  ObjectDetection,
  VideoSummary,
  HighlightDetection
} from '../types';
import { FrameExtractor } from '../utils/FrameExtractor';
import { VideoProcessor } from '../utils/VideoProcessor';
import { PromptBuilder } from '../utils/PromptBuilder';

/**
 * Main video analyzer class using Gemini 2.0 Flash
 */
export class VideoAnalyzer {
  private genAI: GoogleGenerativeAI;
  private config: Required<GeminiConfig>;
  private frameExtractor: FrameExtractor;
  private videoProcessor: VideoProcessor;
  private promptBuilder: PromptBuilder;

  constructor(config: GeminiConfig) {
    this.config = {
      model: 'gemini-2.0-flash-exp',
      endpoint: 'https://generativelanguage.googleapis.com',
      timeout: 60000,
      maxRetries: 3,
      ...config
    };

    this.genAI = new GoogleGenerativeAI(this.config.apiKey);
    this.frameExtractor = new FrameExtractor();
    this.videoProcessor = new VideoProcessor();
    this.promptBuilder = new PromptBuilder();
  }

  /**
   * Analyze a video file or URL
   */
  async analyzeVideo(
    videoInput: File | string | ArrayBuffer,
    options: AnalysisOptions = {},
    progressCallback?: ProgressCallback
  ): Promise<VideoAnalysisResult> {
    const startTime = Date.now();
    
    try {
      // Step 1: Extract metadata
      progressCallback?.({
        step: 'Extracting video metadata',
        progress: 10
      });

      const metadata = await this.videoProcessor.extractMetadata(videoInput);

      // Step 2: Extract frames
      progressCallback?.({
        step: 'Extracting video frames',
        progress: 20
      });

      const frames = await this.frameExtractor.extractFrames(
        videoInput,
        {
          interval: options.frameSamplingInterval || 2,
          maxFrames: options.maxFrames || 30,
          quality: options.quality === 'high' ? 90 : options.quality === 'low' ? 60 : 75
        }
      );

      // Step 3: Analyze with Gemini
      progressCallback?.({
        step: 'Analyzing video content with AI',
        progress: 40
      });

      const analysisResult = await this.performGeminiAnalysis(
        frames,
        metadata,
        options,
        progressCallback
      );

      const processingTime = Date.now() - startTime;

      return {
        ...analysisResult,
        metadata,
        analyzedAt: new Date(),
        processingTime,
        modelVersion: this.config.model
      };

    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      throw this.createError('ANALYSIS_FAILED', `Video analysis failed: ${message}`, error);
    }
  }

  /**
   * Analyze multiple videos in batch
   */
  async analyzeBatch(
    videos: Array<{ input: File | string | ArrayBuffer; id: string }>,
    options: AnalysisOptions = {},
    progressCallback?: ProgressCallback
  ): Promise<Map<string, VideoAnalysisResult>> {
    const results = new Map<string, VideoAnalysisResult>();
    const total = videos.length;

    for (let i = 0; i < total; i++) {
      const video = videos[i];
      
      progressCallback?.({
        step: `Analyzing video ${i + 1} of ${total}`,
        progress: (i / total) * 100
      });

      try {
        const result = await this.analyzeVideo(video.input, options);
        results.set(video.id, result);
      } catch (error) {
        console.error(`Failed to analyze video ${video.id}:`, error);
      }
    }

    progressCallback?.({
      step: 'Batch analysis complete',
      progress: 100
    });

    return results;
  }

  /**
   * Extract highlights from video
   */
  async extractHighlights(
    videoInput: File | string | ArrayBuffer,
    options: AnalysisOptions = {}
  ): Promise<HighlightDetection[]> {
    const frames = await this.frameExtractor.extractFrames(videoInput, {
      interval: 1,
      maxFrames: 60
    });

    const prompt = this.promptBuilder.buildHighlightPrompt(options.language || 'zh-CN');
    const model = this.genAI.getGenerativeModel({ model: this.config.model });

    const result = await model.generateContent([
      prompt,
      ...frames.map(frame => ({
        inlineData: {
          data: frame.imageData.split(',')[1],
          mimeType: 'image/jpeg'
        }
      }))
    ]);

    return this.parseHighlightResponse(result.response.text());
  }

  /**
   * Compare two videos for similarity
   */
  async compareVideos(
    video1: File | string | ArrayBuffer,
    video2: File | string | ArrayBuffer,
    options: AnalysisOptions = {}
  ): Promise<{ similarity: number; analysis: string }> {
    const [frames1, frames2] = await Promise.all([
      this.frameExtractor.extractFrames(video1, { maxFrames: 20 }),
      this.frameExtractor.extractFrames(video2, { maxFrames: 20 })
    ]);

    const prompt = this.promptBuilder.buildComparisonPrompt(options.language || 'zh-CN');
    const model = this.genAI.getGenerativeModel({ model: this.config.model });

    const allFrames = [
      ...frames1.map(f => ({ ...f, source: 'video1' })),
      ...frames2.map(f => ({ ...f, source: 'video2' }))
    ];

    const result = await model.generateContent([
      prompt,
      ...allFrames.map(frame => ({
        inlineData: {
          data: frame.imageData.split(',')[1],
          mimeType: 'image/jpeg'
        }
      }))
    ]);

    return this.parseComparisonResponse(result.response.text());
  }

  /**
   * Perform Gemini analysis on extracted frames
   */
  private async performGeminiAnalysis(
    frames: VideoFrame[],
    metadata: VideoMetadata,
    options: AnalysisOptions,
    progressCallback?: ProgressCallback
  ): Promise<Omit<VideoAnalysisResult, 'metadata' | 'analyzedAt' | 'processingTime' | 'modelVersion'>> {
    const model = this.genAI.getGenerativeModel({ 
      model: this.config.model,
      generationConfig: {
        temperature: 0.4,
        topK: 32,
        topP: 1,
        maxOutputTokens: 8192,
      }
    });

    // Build comprehensive analysis prompt
    const prompt = this.promptBuilder.buildAnalysisPrompt(metadata, options);

    progressCallback?.({
      step: 'Sending frames to Gemini for analysis',
      progress: 60
    });

    // Prepare content for Gemini
    const content = [
      prompt,
      ...frames.map(frame => ({
        inlineData: {
          data: frame.imageData.split(',')[1], // Remove data:image/jpeg;base64, prefix
          mimeType: 'image/jpeg'
        }
      }))
    ];

    const result = await model.generateContent(content);
    const responseText = result.response.text();

    progressCallback?.({
      step: 'Processing AI analysis results',
      progress: 80
    });

    // Parse the response
    return this.parseGeminiResponse(responseText, frames);
  }

  /**
   * Parse Gemini response into structured data
   */
  private parseGeminiResponse(
    responseText: string,
    frames: VideoFrame[]
  ): Omit<VideoAnalysisResult, 'metadata' | 'analyzedAt' | 'processingTime' | 'modelVersion'> {
    try {
      // Try to extract JSON from response
      const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[1]);
        return this.validateAndNormalizeResponse(parsed);
      }

      // Fallback: parse structured text response
      return this.parseTextResponse(responseText, frames);
    } catch (error) {
      throw this.createError('PARSE_ERROR', 'Failed to parse Gemini response', error);
    }
  }

  private parseHighlightResponse(responseText: string): HighlightDetection[] {
    // Implementation for parsing highlight detection response
    try {
      const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[1]);
        return parsed.highlights || [];
      }
      return [];
    } catch (error) {
      console.error('Failed to parse highlight response:', error);
      return [];
    }
  }

  private parseComparisonResponse(responseText: string): { similarity: number; analysis: string } {
    try {
      const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[1]);
        return {
          similarity: parsed.similarity || 0,
          analysis: parsed.analysis || responseText
        };
      }
      return { similarity: 0, analysis: responseText };
    } catch (error) {
      return { similarity: 0, analysis: responseText };
    }
  }

  private validateAndNormalizeResponse(parsed: any): Omit<VideoAnalysisResult, 'metadata' | 'analyzedAt' | 'processingTime' | 'modelVersion'> {
    return {
      scenes: parsed.scenes || [],
      objects: parsed.objects || [],
      summary: parsed.summary || {
        description: '',
        themes: [],
        keyMoments: [],
        emotions: [],
        contentRating: { category: 'unknown', reasons: [], confidence: 0 }
      }
    };
  }

  private parseTextResponse(
    responseText: string,
    frames: VideoFrame[]
  ): Omit<VideoAnalysisResult, 'metadata' | 'analyzedAt' | 'processingTime' | 'modelVersion'> {
    // Fallback text parsing implementation
    return {
      scenes: [],
      objects: [],
      summary: {
        description: responseText.substring(0, 500),
        themes: [],
        keyMoments: [],
        emotions: [],
        contentRating: { category: 'unknown', reasons: [], confidence: 0 }
      }
    };
  }

  private createError(code: string, message: string, originalError?: any): VideoAnalyzerError {
    const error = new Error(message) as VideoAnalyzerError;
    error.code = code;
    error.details = originalError;
    return error;
  }
}
