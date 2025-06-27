/**
 * Smart folder matching system for video categorization
 */

import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import { useGemini } from '@mixvideo/gemini';
import {
  VideoAnalysisResult,
  FolderMatchResult,
  VideoAnalyzerError
} from './types';

const readdir = promisify(fs.readdir);
const stat = promisify(fs.stat);

/**
 * Folder matching configuration
 */
export interface FolderMatchConfig {
  /** Base directory to scan for folders */
  baseDirectory: string;
  /** Maximum depth to scan for folders */
  maxDepth?: number;
  /** Minimum confidence score to include in results */
  minConfidence?: number;
  /** Maximum number of matches to return */
  maxMatches?: number;
  /** Whether to include semantic analysis */
  enableSemanticAnalysis?: boolean;
}

/**
 * Default folder match configuration
 */
export const DEFAULT_FOLDER_MATCH_CONFIG: Required<Omit<FolderMatchConfig, 'baseDirectory'>> = {
  maxDepth: 3,
  minConfidence: 0.3,
  maxMatches: 5,
  enableSemanticAnalysis: true
};

/**
 * Smart folder matcher class
 */
export class FolderMatcher {
  private config: Required<FolderMatchConfig>;
  private geminiClient: any = null;
  private folderCache: Map<string, string[]> = new Map();

  constructor(config: FolderMatchConfig) {
    this.config = { ...DEFAULT_FOLDER_MATCH_CONFIG, ...config };
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
   * Find matching folders for video analysis result
   */
  async findMatchingFolders(analysisResult: VideoAnalysisResult): Promise<FolderMatchResult[]> {
    try {
      // Get available folders
      const folders = await this.scanFolders();

      // Generate content description for matching
      const contentDescription = this.generateContentDescription(analysisResult);

      // Perform folder matching
      const matches = await this.performFolderMatching(contentDescription, folders);

      // Sort by confidence and return top matches
      return matches
        .filter(match => match.confidence >= this.config.minConfidence)
        .sort((a, b) => b.confidence - a.confidence)
        .slice(0, this.config.maxMatches);

    } catch (error) {
      throw new VideoAnalyzerError(
        `Folder matching failed: ${this.getErrorMessage(error)}`,
        'FOLDER_MATCHING_FAILED',
        error
      );
    }
  }

  /**
   * Scan for available folders
   */
  private async scanFolders(): Promise<string[]> {
    const cacheKey = this.config.baseDirectory;
    
    if (this.folderCache.has(cacheKey)) {
      return this.folderCache.get(cacheKey)!;
    }

    const folders: string[] = [];
    await this.scanFoldersRecursive(this.config.baseDirectory, folders, 0);
    
    this.folderCache.set(cacheKey, folders);
    return folders;
  }

  /**
   * Recursively scan folders
   */
  private async scanFoldersRecursive(
    dirPath: string,
    folders: string[],
    currentDepth: number
  ): Promise<void> {
    if (currentDepth >= this.config.maxDepth) {
      return;
    }

    try {
      const entries = await readdir(dirPath, { withFileTypes: true });

      for (const entry of entries) {
        if (entry.isDirectory()) {
          const fullPath = path.join(dirPath, entry.name);
          folders.push(fullPath);

          // Continue scanning subdirectories
          await this.scanFoldersRecursive(fullPath, folders, currentDepth + 1);
        }
      }
    } catch (error) {
      console.warn(`Failed to scan directory ${dirPath}:`, this.getErrorMessage(error));
    }
  }

  /**
   * Generate content description for matching
   */
  private generateContentDescription(analysisResult: VideoAnalysisResult): string {
    const parts: string[] = [];

    // Add summary description
    if (analysisResult.summary.description) {
      parts.push(`内容描述：${analysisResult.summary.description}`);
    }

    // Add keywords
    if (analysisResult.summary.keywords.length > 0) {
      parts.push(`关键词：${analysisResult.summary.keywords.join('、')}`);
    }

    // Add topics
    if (analysisResult.summary.topics.length > 0) {
      parts.push(`主题：${analysisResult.summary.topics.join('、')}`);
    }

    // Add product features if available
    if (analysisResult.productFeatures) {
      const features = analysisResult.productFeatures;
      
      if (features.appearance.colors.length > 0) {
        parts.push(`颜色：${features.appearance.colors.join('、')}`);
      }
      
      if (features.materials.length > 0) {
        parts.push(`材质：${features.materials.join('、')}`);
      }
      
      if (features.functionality.length > 0) {
        parts.push(`功能：${features.functionality.join('、')}`);
      }
    }

    // Add scene information
    if (analysisResult.scenes.length > 0) {
      const sceneDescriptions = analysisResult.scenes
        .map(scene => scene.description)
        .slice(0, 3); // Take first 3 scenes
      parts.push(`场景：${sceneDescriptions.join('、')}`);
    }

    // Add object information
    if (analysisResult.objects.length > 0) {
      const objectNames = analysisResult.objects
        .map(obj => obj.name)
        .slice(0, 5); // Take first 5 objects
      parts.push(`物体：${objectNames.join('、')}`);
    }

    return parts.join('\n');
  }

  /**
   * Perform folder matching using AI analysis
   */
  private async performFolderMatching(
    contentDescription: string,
    folders: string[]
  ): Promise<FolderMatchResult[]> {
    const matches: FolderMatchResult[] = [];

    // First, perform rule-based matching
    const ruleBasedMatches = this.performRuleBasedMatching(contentDescription, folders);
    matches.push(...ruleBasedMatches);

    // Then, perform semantic matching if enabled
    if (this.config.enableSemanticAnalysis) {
      const semanticMatches = await this.performSemanticMatching(contentDescription, folders);
      matches.push(...semanticMatches);
    }

    // Merge and deduplicate matches
    return this.mergeMatches(matches);
  }

  /**
   * Perform rule-based folder matching
   */
  private performRuleBasedMatching(
    contentDescription: string,
    folders: string[]
  ): FolderMatchResult[] {
    const matches: FolderMatchResult[] = [];
    const contentLower = contentDescription.toLowerCase();

    for (const folderPath of folders) {
      const folderName = path.basename(folderPath).toLowerCase();
      const confidence = this.calculateRuleBasedConfidence(contentLower, folderName);

      if (confidence > 0) {
        matches.push({
          folderPath,
          folderName: path.basename(folderPath),
          confidence,
          reasons: this.generateRuleBasedReasons(contentLower, folderName),
          semanticScore: 0,
          relevanceScore: confidence,
          action: this.determineAction(confidence)
        });
      }
    }

    return matches;
  }

  /**
   * Calculate rule-based confidence score
   */
  private calculateRuleBasedConfidence(content: string, folderName: string): number {
    let confidence = 0;

    // Direct keyword matching
    const keywords = this.extractKeywords(content);
    for (const keyword of keywords) {
      if (folderName.includes(keyword)) {
        confidence += 0.3;
      }
    }

    // Category matching
    const categories = this.extractCategories(content);
    for (const category of categories) {
      if (folderName.includes(category)) {
        confidence += 0.4;
      }
    }

    // Color matching
    const colors = this.extractColors(content);
    for (const color of colors) {
      if (folderName.includes(color)) {
        confidence += 0.2;
      }
    }

    return Math.min(1.0, confidence);
  }

  /**
   * Generate reasons for rule-based matching
   */
  private generateRuleBasedReasons(content: string, folderName: string): string[] {
    const reasons: string[] = [];

    const keywords = this.extractKeywords(content);
    for (const keyword of keywords) {
      if (folderName.includes(keyword)) {
        reasons.push(`关键词匹配：${keyword}`);
      }
    }

    const categories = this.extractCategories(content);
    for (const category of categories) {
      if (folderName.includes(category)) {
        reasons.push(`类别匹配：${category}`);
      }
    }

    return reasons;
  }

  /**
   * Perform semantic matching using Gemini AI
   */
  private async performSemanticMatching(
    contentDescription: string,
    folders: string[]
  ): Promise<FolderMatchResult[]> {
    try {
      await this.initializeGeminiClient();

      const folderNames = folders.map(f => path.basename(f));
      const prompt = `请分析以下视频内容描述，并为其推荐最合适的文件夹：

视频内容描述：
${contentDescription}

可选文件夹：
${folderNames.map((name, index) => `${index + 1}. ${name}`).join('\n')}

请为每个文件夹评分（0-1），并说明匹配原因。返回JSON格式：
{
  "matches": [
    {
      "folderName": "文件夹名称",
      "score": 0.8,
      "reasons": ["匹配原因1", "匹配原因2"]
    }
  ]
}`;

      const response = await this.geminiClient.generateText(
        prompt,
        'gemini-2.5-flash',
        {
          temperature: 0.3,
          maxOutputTokens: 2048
        }
      );

      if (response) {
        return this.parseSemanticMatchingResponse(response, folders);
      }

      return [];

    } catch (error) {
      console.warn('Semantic matching failed:', this.getErrorMessage(error));
      return [];
    }
  }

  /**
   * Parse semantic matching response
   */
  private parseSemanticMatchingResponse(response: string, folders: string[]): FolderMatchResult[] {
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) return [];

      const data = JSON.parse(jsonMatch[0]);
      const matches: FolderMatchResult[] = [];

      if (data.matches && Array.isArray(data.matches)) {
        for (const match of data.matches) {
          const folderPath = folders.find(f => path.basename(f) === match.folderName);
          if (folderPath && match.score > 0) {
            matches.push({
              folderPath,
              folderName: match.folderName,
              confidence: match.score,
              reasons: match.reasons || [],
              semanticScore: match.score,
              relevanceScore: match.score,
              action: this.determineAction(match.score)
            });
          }
        }
      }

      return matches;

    } catch (error) {
      console.warn('Failed to parse semantic matching response:', this.getErrorMessage(error));
      return [];
    }
  }

  private getErrorMessage(error: unknown){
    return error instanceof Error ? error.message : String(error);
  }

  /**
   * Merge and deduplicate matches
   */
  private mergeMatches(matches: FolderMatchResult[]): FolderMatchResult[] {
    const mergedMap = new Map<string, FolderMatchResult>();

    for (const match of matches) {
      const existing = mergedMap.get(match.folderPath);
      
      if (existing) {
        // Merge with existing match
        existing.confidence = Math.max(existing.confidence, match.confidence);
        existing.semanticScore = Math.max(existing.semanticScore, match.semanticScore);
        existing.relevanceScore = Math.max(existing.relevanceScore, match.relevanceScore);
        existing.reasons = [...new Set([...existing.reasons, ...match.reasons])];
        existing.action = this.determineAction(existing.confidence);
      } else {
        mergedMap.set(match.folderPath, { ...match });
      }
    }

    return Array.from(mergedMap.values());
  }

  /**
   * Determine recommended action based on confidence
   */
  private determineAction(confidence: number): 'move' | 'copy' | 'link' | 'ignore' {
    if (confidence >= 0.8) return 'move';
    if (confidence >= 0.6) return 'copy';
    if (confidence >= 0.4) return 'link';
    return 'ignore';
  }

  /**
   * Extract keywords from content
   */
  private extractKeywords(content: string): string[] {
    const keywords: string[] = [];
    
    // Common product keywords
    const productKeywords = ['产品', '商品', '物品', '设备', '工具', '装置'];
    for (const keyword of productKeywords) {
      if (content.includes(keyword)) {
        keywords.push(keyword);
      }
    }

    return keywords;
  }

  /**
   * Extract categories from content
   */
  private extractCategories(content: string): string[] {
    const categories: string[] = [];
    
    // Common categories
    const categoryMap = {
      '电子': ['电子', '数码', '手机', '电脑', '相机'],
      '服装': ['服装', '衣服', '鞋子', '包包', '配饰'],
      '家居': ['家居', '家具', '装饰', '厨具', '床品'],
      '美妆': ['美妆', '化妆品', '护肤', '香水', '彩妆'],
      '食品': ['食品', '零食', '饮料', '茶叶', '咖啡']
    };

    for (const [category, keywords] of Object.entries(categoryMap)) {
      for (const keyword of keywords) {
        if (content.includes(keyword)) {
          categories.push(category);
          break;
        }
      }
    }

    return categories;
  }

  /**
   * Extract colors from content
   */
  private extractColors(content: string): string[] {
    const colors = ['红', '蓝', '绿', '黄', '黑', '白', '灰', '紫', '粉', '橙'];
    return colors.filter(color => content.includes(color));
  }

  /**
   * Clear folder cache
   */
  clearCache(): void {
    this.folderCache.clear();
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<FolderMatchConfig>): void {
    this.config = { ...this.config, ...config };
    this.clearCache(); // Clear cache when config changes
  }
}

/**
 * Convenience function to find matching folders
 */
export async function findMatchingFoldersForVideo(
  analysisResult: VideoAnalysisResult,
  config: FolderMatchConfig
): Promise<FolderMatchResult[]> {
  const matcher = new FolderMatcher(config);
  return matcher.findMatchingFolders(analysisResult);
}
