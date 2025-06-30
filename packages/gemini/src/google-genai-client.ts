import axios, { type AxiosResponse } from 'axios';

/**
 * TypeScript 版本的 GoogleGenaiClient
 * 对应 Python 版本的 GoogleAuthUtils.GoogleGenaiClient
 */

// 类型定义
export interface GoogleGenaiClientConfig {
  cloudflareProjectId: string;
  cloudflareGatewayId: string;
  googleProjectId: string;
  regions: string[];
  accessToken: string;
}

export interface ContentPart {
  text?: string;
  inlineData?: {
    mimeType: string;
    data: string;
  };
  fileData?: {
    mimeType: string;
    fileUri: string;
  };
}

export interface Content {
  role?: 'user' | 'model';
  parts: ContentPart[];
}

export interface GenerationConfig {
  temperature?: number;
  topP?: number;
  topK?: number;
  maxOutputTokens?: number;
  stopSequences?: string[];
  candidateCount?: number;
}

export interface SafetySetting {
  category: string;
  threshold: string;
}

export interface GenerateContentRequest {
  contents: Content[];
  generationConfig?: GenerationConfig;
  safetySettings?: SafetySetting[];
  systemInstruction?: Content;
}

export interface GenerateContentCandidate {
  content: Content;
  finishReason?: string;
  index?: number;
  safetyRatings?: Array<{
    category: string;
    probability: string;
  }>;
}

export interface GenerateContentResponse {
  candidates?: GenerateContentCandidate[];
  promptFeedback?: {
    safetyRatings?: Array<{
      category: string;
      probability: string;
    }>;
    blockReason?: string;
  };
  usageMetadata?: {
    promptTokenCount?: number;
    candidatesTokenCount?: number;
    totalTokenCount?: number;
  };
}

export interface GenerateContentResult {
  response: GenerateContentResponse | null;
  statusCode: number;
}

/**
 * Google Generative AI 客户端
 * 通过 Cloudflare Gateway 调用 Google Vertex AI API
 */
export class GoogleGenaiClient {
  private config: GoogleGenaiClientConfig;

  constructor(config: GoogleGenaiClientConfig) {
    this.config = config;
  }

  /**
   * 计算属性：通过 Cloudflare Gateway 调用的 URL
   */
  get gatewayUrl(): string {
    // 随机选择一个区域
    const randomRegion = this.config.regions[Math.floor(Math.random() * this.config.regions.length)];

    return `https://gateway.ai.cloudflare.com/v1/${this.config.cloudflareProjectId}/${this.config.cloudflareGatewayId}/google-vertex-ai/v1/projects/${this.config.googleProjectId}/locations/${randomRegion}/publishers/google/models`;
  }

  /**
   * 生成内容
   * @param modelId 模型 ID，如 'gemini-2.5-flash'
   * @param contents 内容数组
   * @param config 生成配置
   * @param timeout 超时时间（秒）
   * @returns 生成结果和状态码
   */
  async generateContent(
    contents: Content[],
    modelId: string = 'gemini-2.5-flash',
    config?: GenerationConfig,
    timeout: number = 30
  ): Promise<GenerateContentResult> {
    try {
      // 构建请求体
      const requestBody: GenerateContentRequest = {
        contents,
        ...(config && { generationConfig: config })
      };

      // 排除空值并转换为 JSON
      const jsonBody = JSON.stringify(requestBody, (key, value) => {
        if (value === null || value === undefined) {
          return undefined;
        }
        return value;
      }, 2);

      const url = `${this.gatewayUrl}/${modelId}:generateContent`;
      const response: AxiosResponse<GenerateContentResponse> = await axios.post(
        url,
        jsonBody,
        {
          timeout: timeout * 1000, // 转换为毫秒
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.config.accessToken}`
          }
        }
      );

      if (response.status !== 200) {
        console.error('❌ Gemini API 非200响应:', {
          status: response.status,
          statusText: response.statusText,
          data: response.data
        });
        return {
          response: null,
          statusCode: response.status
        };
      }

      console.log('✅ Gemini API 200响应，数据结构:', {
        hasCandidates: !!response.data?.candidates,
        candidatesLength: response.data?.candidates?.length || 0,
        firstCandidateStructure: response.data?.candidates?.[0] ? Object.keys(response.data.candidates[0]) : []
      });

      return {
        response: response.data,
        statusCode: response.status
      };

    } catch (error: any) {
      console.error('❌ Gemini API 请求失败:', {
        message: error.message,
        code: error.code,
        hasResponse: !!error.response,
        hasRequest: !!error.request
      });

      if (error.response) {
        console.error('响应错误详情:', {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data
        });
        return {
          response: null,
          statusCode: error.response.status
        };
      } else if (error.request) {
        console.error('网络请求失败，无响应');
        return {
          response: null,
          statusCode: 0
        };
      } else {
        console.error('请求配置错误:', error.message);
        return {
          response: null,
          statusCode: -1
        };
      }
    }
  }

  /**
   * 简化的文本生成方法
   * @param modelId 模型 ID
   * @param prompt 文本提示
   * @param config 生成配置
   * @returns 生成的文本内容
   */
  async generateText(
    prompt: string,
    modelId: string = 'gemini-2.5-flash',
    config?: GenerationConfig
  ): Promise<string | null> {
    const contents: Content[] = [
      {
        role: 'user',
        parts: [{ text: prompt }]
      }
    ];

    const result = await this.generateContent(contents, modelId, config);

    if (result.statusCode === 200 && result.response?.candidates?.[0]?.content?.parts?.[0]?.text) {
      return result.response.candidates[0].content.parts[0].text;
    }

    return null;
  }

  /**
   * 获取配置信息
   */
  getConfig(): GoogleGenaiClientConfig {
    return { ...this.config };
  }

  /**
   * 更新访问令牌
   */
  updateAccessToken(accessToken: string): void {
    this.config.accessToken = accessToken;
  }
}

/**
 * 创建 GoogleGenaiClient 实例的工厂函数
 */
export function createGoogleGenaiClient(config: GoogleGenaiClientConfig): GoogleGenaiClient {
  return new GoogleGenaiClient(config);
}

/**
 * 使用默认配置创建客户端
 */
export function createDefaultGoogleGenaiClient(accessToken: string): GoogleGenaiClient {
  return new GoogleGenaiClient({
    cloudflareProjectId: '67720b647ff2b55cf37ba3ef9e677083',
    cloudflareGatewayId: 'bowong-dev',
    googleProjectId: 'gen-lang-client-0413414134',
    regions: ['us-central1'], // 使用稳定的区域
    accessToken
  });
}
