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
import { formatFolderMatchingPrompt } from './simple-prompts';

const readdir = promisify(fs.readdir);

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
      const prompt = formatFolderMatchingPrompt(contentDescription, folderNames);

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
      console.log('📝 解析文件夹匹配响应，长度:', response.length);

      // 清理响应文本
      const cleanedResponse = this.cleanJsonResponse(response);
      const jsonMatch = cleanedResponse.match(/\{[\s\S]*\}/);

      if (!jsonMatch) {
        console.warn('⚠️ 未找到JSON结构，使用降级匹配');
        return this.fallbackMatching(response, folders);
      }

      const jsonStr = this.fixJsonString(jsonMatch[0]);
      console.log('🔍 尝试解析JSON:', jsonStr.substring(0, 200) + '...');

      const data = JSON.parse(jsonStr);
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
      console.warn('❌ 解析文件夹匹配响应失败:', this.getErrorMessage(error));
      console.warn('原始响应:', response.substring(0, 500) + '...');
      return this.fallbackMatching(response, folders);
    }
  }

  /**
   * Clean JSON response text
   */
  private cleanJsonResponse(text: string): string {
    return text
      .replace(/```json\s*/g, '') // 移除 ```json
      .replace(/```\s*/g, '')     // 移除 ```
      .replace(/^\s*[\r\n]+/gm, '') // 移除空行
      .trim();
  }

  /**
   * Fix common JSON string issues
   */
  private fixJsonString(jsonStr: string): string {
    let fixed = jsonStr
      .replace(/,(\s*[}\]])/g, '$1')  // 移除尾随逗号
      .replace(/([{,]\s*)(\w+):/g, '$1"$2":') // 给属性名加引号
      .replace(/:\s*'([^']*)'/g, ': "$1"')    // 单引号改双引号
      .replace(/\n/g, ' ')                    // 移除换行符
      .replace(/\s+/g, ' ')                   // 合并多个空格
      .trim();

    // 处理截断的 JSON（如果以逗号结尾但没有闭合）
    if (fixed.endsWith(',')) {
      fixed = fixed.slice(0, -1); // 移除末尾逗号
    }

    // 确保 JSON 结构完整
    const openBraces = (fixed.match(/\{/g) || []).length;
    const closeBraces = (fixed.match(/\}/g) || []).length;
    const openBrackets = (fixed.match(/\[/g) || []).length;
    const closeBrackets = (fixed.match(/\]/g) || []).length;

    // 补充缺失的闭合符号
    for (let i = 0; i < openBrackets - closeBrackets; i++) {
      fixed += ']';
    }
    for (let i = 0; i < openBraces - closeBraces; i++) {
      fixed += '}';
    }

    return fixed;
  }

  /**
   * Fallback matching when JSON parsing fails
   */
  private fallbackMatching(response: string, folders: string[]): FolderMatchResult[] {
    console.log('🔄 使用降级匹配策略');

    const results: FolderMatchResult[] = [];

    // 简单的关键词匹配
    for (const folder of folders) {
      const folderName = path.basename(folder);
      const lowerResponse = response.toLowerCase();
      const lowerFolderName = folderName.toLowerCase();

      let confidence = 0;
      const reasons: string[] = [];

      // 检查文件夹名称是否在响应中出现
      if (lowerResponse.includes(lowerFolderName)) {
        confidence += 0.6; // 提高直接匹配的权重
        reasons.push(`文件夹名称匹配: ${folderName}`);
      }

      // 检查相关关键词
      const keywords = this.extractKeywords(lowerResponse);
      const folderKeywords = this.getFolderKeywords(lowerFolderName);

      for (const keyword of keywords) {
        if (folderKeywords.includes(keyword)) {
          confidence += 0.3; // 提高关键词匹配权重
          reasons.push(`关键词匹配: ${keyword}`);
        }
      }

      // 检查内容相关性
      const contentScore = this.calculateContentRelevance(lowerResponse, lowerFolderName);
      if (contentScore > 0) {
        confidence += contentScore;
        reasons.push(`内容相关性: ${(contentScore * 100).toFixed(0)}%`);
      }

      if (confidence > 0.2) { // 降低阈值
        // 提高降级匹配的置信度
        const adjustedConfidence = Math.min(confidence + 0.3, 0.9); // 提升置信度
        results.push({
          folderPath: folder,
          folderName,
          confidence: adjustedConfidence,
          reasons,
          semanticScore: confidence,
          relevanceScore: confidence,
          action: this.determineAction(adjustedConfidence)
        });
      }
    }

    return results.sort((a, b) => b.confidence - a.confidence);
  }

  /**
   * Extract keywords from text
   */
  private extractKeywords(text: string): string[] {
    const commonWords = ['的', '是', '在', '有', '和', '与', '或', '但', '这', '那', '一个', '一些'];
    return text
      .split(/[\s,，。！？；：]+/)
      .filter(word => word.length > 1 && !commonWords.includes(word))
      .slice(0, 10); // 取前10个关键词
  }

  /**
   * Get keywords for folder name
   */
  private getFolderKeywords(folderName: string): string[] {
    const keywordMap: Record<string, string[]> = {
      '产品展示': ['产品', '展示', '商品', '物品'],
      '产品使用': ['使用', '操作', '演示', '教程'],
      '生活场景': ['生活', '日常', '场景', '环境'],
      '模特实拍': ['模特', '实拍', '人物', '拍摄'],
      '服装配饰': ['服装', '配饰', '衣服', '饰品'],
      '美妆护肤': ['美妆', '护肤', '化妆', '保养'],
      '其他': ['其他', '未分类', '杂项']
    };

    return keywordMap[folderName] || [folderName];
  }

  /**
   * 计算内容相关性
   */
  private calculateContentRelevance(response: string, folderName: string): number {
    let score = 0;

    // 定义文件夹相关的内容模式
    const contentPatterns: Record<string, string[]> = {
      '产品展示': ['展示', '介绍', '外观', '细节', '特色', '卖点'],
      '产品使用': ['使用', '演示', '操作', '功能', '教程', '方法'],
      '生活场景': ['生活', '日常', '场景', '环境', '氛围', '情境'],
      '模特实拍': ['模特', '实拍', '人物', '穿着', '试穿', '搭配'],
      '服装配饰': ['服装', '衣服', '配饰', '穿搭', '时尚', '款式'],
      '美妆护肤': ['美妆', '化妆', '护肤', '保养', '美容', '肌肤'],
      '其他': ['其他', '杂项', '未分类']
    };

    const patterns = contentPatterns[folderName] || [];

    for (const pattern of patterns) {
      if (response.includes(pattern)) {
        score += 0.1; // 每个匹配的模式增加0.1分
      }
    }

    // 检查特定的产品类型
    if (folderName === '服装配饰') {
      const clothingTerms = ['外套', '夹克', '上衣', '裤子', '裙子', '连帽', '防晒衣'];
      for (const term of clothingTerms) {
        if (response.includes(term)) {
          score += 0.15;
        }
      }
    }

    return Math.min(score, 0.5); // 最高0.5分
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
