import { config } from 'dotenv';
import { GeminiConfig } from '@mixvideo/video-analyzer';

// 加载环境变量
config();

export const getGeminiConfig = (): GeminiConfig => {
  const apiKey = process.env.GEMINI_API_KEY;
  
  if (!apiKey) {
    throw new Error('GEMINI_API_KEY 环境变量未设置。请在 .env 文件中设置您的 Gemini API Key。');
  }

  return {
    apiKey,
    model: process.env.GEMINI_MODEL || 'gemini-2.0-flash-exp',
    maxRetries: parseInt(process.env.MAX_RETRIES || '3'),
    timeout: parseInt(process.env.TIMEOUT || '30000'),
  };
};

export const checkEnvironment = (): boolean => {
  try {
    getGeminiConfig();
    return true;
  } catch (error) {
    console.error('❌ 环境配置错误:', (error as Error).message);
    console.log('');
    console.log('📝 请按照以下步骤配置环境:');
    console.log('1. 复制 .env.example 到 .env');
    console.log('2. 在 .env 文件中设置您的 GEMINI_API_KEY');
    console.log('3. 从 https://makersuite.google.com/app/apikey 获取 API Key');
    return false;
  }
};
