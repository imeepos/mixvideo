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

/**
 * Product analysis prompts for different aspects
 */
export const PRODUCT_ANALYSIS_PROMPTS = {
  APPEARANCE: `请详细分析视频中产品的外观特征：
1. 颜色：主要颜色、配色方案、颜色搭配
2. 形状：整体形状、设计风格、几何特征
3. 尺寸：相对大小、比例关系
4. 风格：设计风格（现代、经典、简约等）
5. 表面处理：光泽度、纹理、图案

请以JSON格式返回详细的外观分析结果。`,

  MATERIALS: `请分析视频中产品使用的材料：
1. 主要材料：金属、塑料、布料、皮革、玻璃等
2. 材料质感：光滑、粗糙、柔软、坚硬等
3. 材料质量：高端、中端、经济型
4. 特殊材料：环保材料、高科技材料等
5. 材料组合：多种材料的搭配使用

请以JSON格式返回材料分析结果。`,

  FUNCTIONALITY: `请分析产品展示的功能特征：
1. 主要功能：产品的核心功能和用途
2. 特色功能：独特的功能特点
3. 操作方式：如何使用和操作
4. 技术特征：涉及的技术和创新点
5. 性能表现：速度、效率、精度等

请以JSON格式返回功能分析结果。`,

  USAGE_SCENARIOS: `请分析产品的使用场景和环境：
1. 使用环境：室内、户外、办公室、家庭等
2. 使用时机：日常、特殊场合、季节性等
3. 用户行为：如何使用、使用频率
4. 搭配使用：与其他产品的配合
5. 适用人群：年龄、性别、职业等

请以JSON格式返回使用场景分析结果。`,

  BRAND_ELEMENTS: `请识别视频中的品牌元素：
1. Logo标识：品牌logo的位置和展示
2. 品牌色彩：品牌专用色彩
3. 包装设计：产品包装的品牌特征
4. 品牌文字：品牌名称、标语等
5. 品牌风格：整体品牌调性和风格

请以JSON格式返回品牌元素分析结果。`,

  ATMOSPHERE: `请分析视频的整体氛围和情感表达：
1. 视觉氛围：明亮、温馨、专业、时尚等
2. 情感基调：快乐、严肃、轻松、高端等
3. 音乐风格：背景音乐的风格和情感
4. 拍摄风格：镜头语言、构图风格
5. 目标情感：想要传达的情感和感受

请以JSON格式返回氛围分析结果。`
};

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
   */
  async analyzeProductFeatures(
    videoFile: VideoFile,
    gcsPath: string,
    options: AnalysisOptions = {}
  ): Promise<ProductFeatures> {
    try {
      await this.initializeGeminiClient();

      // Run comprehensive product analysis
      const analysisResults = await Promise.allSettled([
        this.analyzeAppearance(gcsPath),
        this.analyzeMaterials(gcsPath),
        this.analyzeFunctionality(gcsPath),
        this.analyzeUsageScenarios(gcsPath),
        this.analyzeBrandElements(gcsPath),
        this.analyzeAtmosphere(gcsPath)
      ]);

      // Combine results
      return this.combineProductAnalysis(analysisResults);

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
   * Analyze product appearance
   */
  private async analyzeAppearance(gcsPath: string): Promise<any> {
    return this.runProductAnalysis(gcsPath, PRODUCT_ANALYSIS_PROMPTS.APPEARANCE);
  }

  /**
   * Analyze product materials
   */
  private async analyzeMaterials(gcsPath: string): Promise<any> {
    return this.runProductAnalysis(gcsPath, PRODUCT_ANALYSIS_PROMPTS.MATERIALS);
  }

  /**
   * Analyze product functionality
   */
  private async analyzeFunctionality(gcsPath: string): Promise<any> {
    return this.runProductAnalysis(gcsPath, PRODUCT_ANALYSIS_PROMPTS.FUNCTIONALITY);
  }

  /**
   * Analyze usage scenarios
   */
  private async analyzeUsageScenarios(gcsPath: string): Promise<any> {
    return this.runProductAnalysis(gcsPath, PRODUCT_ANALYSIS_PROMPTS.USAGE_SCENARIOS);
  }

  /**
   * Analyze brand elements
   */
  private async analyzeBrandElements(gcsPath: string): Promise<any> {
    return this.runProductAnalysis(gcsPath, PRODUCT_ANALYSIS_PROMPTS.BRAND_ELEMENTS);
  }

  /**
   * Analyze video atmosphere
   */
  private async analyzeAtmosphere(gcsPath: string): Promise<any> {
    return this.runProductAnalysis(gcsPath, PRODUCT_ANALYSIS_PROMPTS.ATMOSPHERE);
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
   */
  async analyzeForEcommerce(
    videoFile: VideoFile,
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
