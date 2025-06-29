/**
 * Specialized product feature analysis for e-commerce and marketing videos
 */

import { useGemini } from '@mixvideo/gemini';
import {
  VideoFile,
  ProductFeatures,
  AnalysisOptions,
  VideoAnalyzerError
} from './types';

// Import prompts from centralized module
import { PRODUCT_ANALYSIS_PROMPTS } from './simple-prompts';

/**
 * Product feature analyzer class
 */
export class ProductAnalyzer {
  private geminiClient: any = null;

  constructor() {
    // Gemini client will be initialized when needed
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
   * Analyze product features in video
   * 简化版本：现在使用统一的视频分析提示词
   */
  async analyzeProductFeatures(
    videoFile: VideoFile,
    gcsPath: string,
    _options: AnalysisOptions = {}
  ): Promise<ProductFeatures> {
    try {
      await this.initializeGeminiClient();

      // 使用统一的产品分析提示词
      const analysisResult = await this.runProductAnalysis(gcsPath, PRODUCT_ANALYSIS_PROMPTS.APPEARANCE);

      // 解析结果为 ProductFeatures 格式
      return this.parseAnalysisResult(analysisResult);

    } catch (error) {
      throw new VideoAnalyzerError(
        `Product analysis failed for ${videoFile.name}: ${this.getErrorMessage(error)}`,
        'PRODUCT_ANALYSIS_FAILED',
        error
      );
    }
  }

  private getErrorMessage(error: unknown){
    return error instanceof Error ? error.message : String(error);
  }

  /**
   * 解析分析结果为 ProductFeatures 格式
   */
  private parseAnalysisResult(analysisResult: any): ProductFeatures {
    // 由于现在使用统一的提示词，直接解析 JSON 结果
    try {
      const parsed = typeof analysisResult === 'string' ? JSON.parse(analysisResult) : analysisResult;

      return {
        appearance: {
          colors: parsed.appearance?.colors || parsed.colors || [],
          shape: parsed.appearance?.shape || parsed.shape || '',
          size: parsed.appearance?.size || parsed.size || '',
          style: parsed.appearance?.style || parsed.style || ''
        },
        materials: parsed.materials || [],
        functionality: parsed.functionality || [],
        usageScenarios: parsed.usageScenarios || parsed.usage_scenarios || [],
        targetAudience: parsed.targetAudience || parsed.target_audience || '',
        brandElements: parsed.brandElements || parsed.brand_elements || []
      };
    } catch (error) {
      // 如果解析失败，返回默认结构
      return {
        appearance: { colors: [], shape: '', size: '', style: '' },
        materials: [],
        functionality: [],
        usageScenarios: [],
        targetAudience: '',
        brandElements: []
      };
    }
  }

  /**
   * Run a single product analysis
   */
  private async runProductAnalysis(gcsPath: string, prompt: string): Promise<any> {
    try {
      const contents = [
        {
          role: 'user',
          parts: [
            {
              text: prompt
            },
            {
              fileData: {
                mimeType: 'video/mp4',
                fileUri: `gs://${gcsPath}`
              }
            }
          ]
        }
      ];

      const response = await this.geminiClient.generateContent(
        contents,
        'gemini-2.5-flash',
        {
          temperature: 0.2, // Lower temperature for more consistent analysis
          maxOutputTokens: 2048,
          topP: 0.8
        }
      );

      if (response.statusCode === 200 && response.response?.candidates?.[0]?.content?.parts?.[0]?.text) {
        const responseText = response.response.candidates[0].content.parts[0].text;
        return this.parseProductAnalysisResponse(responseText);
      }

      return null;

    } catch (error) {
      console.warn('Product analysis step failed:', this.getErrorMessage(error));
      return null;
    }
  }

  /**
   * Parse product analysis response
   */
  private parseProductAnalysisResponse(responseText: string): any {
    try {
      // Try to extract JSON from the response
      const jsonMatch = responseText.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }

      // If no JSON found, parse as text
      return this.parseProductTextResponse(responseText);

    } catch (error) {
      console.warn('Failed to parse product analysis JSON:', this.getErrorMessage(error));
      return this.parseProductTextResponse(responseText);
    }
  }

  /**
   * Parse text response for product analysis
   */
  private parseProductTextResponse(text: string): any {
    const result: any = {};

    // Extract colors
    const colorMatches = text.match(/颜色[：:]([^。\n]+)/g);
    if (colorMatches) {
      result.colors = colorMatches.map(match => 
        match.replace(/颜色[：:]/, '').trim()
      );
    }

    // Extract materials
    const materialMatches = text.match(/材料[：:]([^。\n]+)/g);
    if (materialMatches) {
      result.materials = materialMatches.map(match => 
        match.replace(/材料[：:]/, '').trim()
      );
    }

    // Extract functionality
    const functionMatches = text.match(/功能[：:]([^。\n]+)/g);
    if (functionMatches) {
      result.functionality = functionMatches.map(match => 
        match.replace(/功能[：:]/, '').trim()
      );
    }

    return result;
  }

  /**
   * Combine all product analysis results
   */
  private combineProductAnalysis(results: PromiseSettledResult<any>[]): ProductFeatures {
    const productFeatures: ProductFeatures = {
      appearance: {
        colors: [],
        shape: '',
        size: '',
        style: ''
      },
      materials: [],
      functionality: [],
      usageScenarios: [],
      targetAudience: '',
      brandElements: []
    };

    results.forEach((result, index) => {
      if (result.status === 'fulfilled' && result.value) {
        const data = result.value;

        switch (index) {
          case 0: // Appearance
            if (data.colors) productFeatures.appearance.colors = data.colors;
            if (data.shape) productFeatures.appearance.shape = data.shape;
            if (data.size) productFeatures.appearance.size = data.size;
            if (data.style) productFeatures.appearance.style = data.style;
            break;

          case 1: // Materials
            if (data.materials) productFeatures.materials = data.materials;
            break;

          case 2: // Functionality
            if (data.functionality) productFeatures.functionality = data.functionality;
            break;

          case 3: // Usage scenarios
            if (data.usageScenarios) productFeatures.usageScenarios = data.usageScenarios;
            if (data.targetAudience) productFeatures.targetAudience = data.targetAudience;
            break;

          case 4: // Brand elements
            if (data.brandElements) productFeatures.brandElements = data.brandElements;
            break;

          case 5: // Atmosphere
            // Atmosphere data can be used to enhance other fields
            break;
        }
      }
    });

    return productFeatures;
  }

  /**
   * Analyze product for e-commerce categorization
   * 简化版本：使用统一的提示词
   */
  async analyzeForEcommerce(
    _videoFile: VideoFile,
    gcsPath: string
  ): Promise<{
    category: string;
    subcategory: string;
    tags: string[];
    priceRange: string;
    targetMarket: string;
  }> {
    const prompt = `请分析这个产品视频，为电商平台分类：
1. 产品类别：确定主要产品类别
2. 子类别：更具体的产品分类
3. 标签：相关的产品标签和关键词
4. 价格范围：根据产品特征推测价格档次
5. 目标市场：目标消费群体和市场定位

请以JSON格式返回电商分类结果。`;

    try {
      const result = await this.runProductAnalysis(gcsPath, prompt);
      
      return {
        category: result?.category || 'unknown',
        subcategory: result?.subcategory || 'unknown',
        tags: result?.tags || [],
        priceRange: result?.priceRange || 'unknown',
        targetMarket: result?.targetMarket || 'unknown'
      };

    } catch (error) {
      throw new VideoAnalyzerError(
        `E-commerce analysis failed: ${this.getErrorMessage(error)}`,
        'ECOMMERCE_ANALYSIS_FAILED',
        error
      );
    }
  }

  /**
   * Generate product description from analysis
   */
  generateProductDescription(features: ProductFeatures): string {
    const parts: string[] = [];

    // Add appearance description
    if (features.appearance.colors.length > 0) {
      parts.push(`颜色：${features.appearance.colors.join('、')}`);
    }

    if (features.appearance.style) {
      parts.push(`风格：${features.appearance.style}`);
    }

    // Add materials
    if (features.materials.length > 0) {
      parts.push(`材质：${features.materials.join('、')}`);
    }

    // Add functionality
    if (features.functionality.length > 0) {
      parts.push(`功能：${features.functionality.join('、')}`);
    }

    // Add usage scenarios
    if (features.usageScenarios.length > 0) {
      parts.push(`适用场景：${features.usageScenarios.join('、')}`);
    }

    return parts.join('；');
  }
}

/**
 * Convenience function to analyze product features
 */
export async function analyzeProductInVideo(
  videoFile: VideoFile,
  gcsPath: string,
  options?: AnalysisOptions
): Promise<ProductFeatures> {
  const analyzer = new ProductAnalyzer();
  return analyzer.analyzeProductFeatures(videoFile, gcsPath, options);
}
