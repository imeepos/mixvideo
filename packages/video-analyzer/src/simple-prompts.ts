/**
 * Simplified Video Analyzer Prompts
 *
 * 统一的提示词管理系统，从独立文件加载提示词
 */

import * as fs from 'fs';
import * as path from 'path';

/**
 * 默认的视频分析提示词（如果文件加载失败时使用）
 */
const DEFAULT_VIDEO_ANALYSIS_PROMPT = `请对这个视频进行全面分析，根据视频内容自动识别并分析以下相关方面：

**基础分析：**
1. 场景检测：识别视频中的不同场景，包括开始时间、结束时间和场景描述
2. 物体识别：识别视频中出现的主要物体、人物和元素
3. 内容总结：提供视频的整体描述、关键亮点和主要主题
4. 情感基调：分析视频的情感氛围和风格
5. 关键词提取：提取最相关的关键词

**产品分析（如适用）：**
6. 产品外观：颜色、形状、尺寸、风格、材质
7. 功能特征：产品展示的功能和特性
8. 使用场景：产品的使用环境和场景
9. 目标受众：分析产品的目标用户群体
10. 品牌元素：识别品牌标识、logo等元素

**技术分析：**
11. 拍摄风格：镜头语言、构图风格、视觉效果
12. 音频分析：背景音乐、音效、语音内容（如有）

请以JSON格式返回结果，包含所有相关字段。如果某些方面不适用于当前视频，可以省略或标注为"不适用"。`;

/**
 * 默认的文件夹匹配提示词模板（如果文件加载失败时使用）
 */
const DEFAULT_FOLDER_MATCHING_TEMPLATE = `请分析以下视频内容描述，并为其推荐最合适的文件夹：

视频内容描述：
{contentDescription}

可选文件夹：
{folderList}

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

/**
 * 缓存的提示词
 */
let cachedVideoAnalysisPrompt: string | null = null;
let cachedFolderMatchingTemplate: string | null = null;

/**
 * 从文件加载提示词
 */
function loadPromptFromFile(filePath: string): string | null {
  try {
    const fullPath = path.resolve(filePath);
    if (fs.existsSync(fullPath)) {
      return fs.readFileSync(fullPath, 'utf-8').trim();
    }
    return null;
  } catch (error) {
    console.warn(`Failed to load prompt from file ${filePath}:`, error);
    return null;
  }
}

/**
 * 获取视频分析提示词（从文件加载或使用默认）
 */
export function getVideoAnalysisPrompt(): string {
  if (!cachedVideoAnalysisPrompt) {
    const promptsDir = path.join(__dirname, '..', 'prompts');
    const promptFile = path.join(promptsDir, 'video-analysis.prompt');

    cachedVideoAnalysisPrompt = loadPromptFromFile(promptFile) || DEFAULT_VIDEO_ANALYSIS_PROMPT;
  }

  return cachedVideoAnalysisPrompt;
}

/**
 * 获取文件夹匹配提示词模板（从文件加载或使用默认）
 */
export function getFolderMatchingTemplate(): string {
  if (!cachedFolderMatchingTemplate) {
    const promptsDir = path.join(__dirname, '..', 'prompts');
    const promptFile = path.join(promptsDir, 'folder-matching.prompt');

    cachedFolderMatchingTemplate = loadPromptFromFile(promptFile) || DEFAULT_FOLDER_MATCHING_TEMPLATE;
  }

  return cachedFolderMatchingTemplate;
}

/**
 * 格式化文件夹匹配提示词
 */
export function formatFolderMatchingPrompt(
  contentDescription: string,
  folderNames: string[]
): string {
  const template = getFolderMatchingTemplate();
  const folderList = folderNames.map((name, index) => `${index + 1}. ${name}`).join('\n');

  return template
    .replace('{contentDescription}', contentDescription)
    .replace('{folderList}', folderList);
}

/**
 * 重新加载提示词（用于开发时更新）
 */
export function reloadPrompts(): void {
  cachedVideoAnalysisPrompt = null;
  cachedFolderMatchingTemplate = null;
}

// 向后兼容性导出
// 所有旧的提示词名称都指向统一的视频分析提示词
export const ANALYSIS_PROMPTS = {
  get COMPREHENSIVE() { return getVideoAnalysisPrompt(); },
  get PRODUCT_FOCUSED() { return getVideoAnalysisPrompt(); },
  get SCENE_DETECTION() { return getVideoAnalysisPrompt(); },
  get OBJECT_DETECTION() { return getVideoAnalysisPrompt(); }
};

export const PRODUCT_ANALYSIS_PROMPTS = {
  get APPEARANCE() { return getVideoAnalysisPrompt(); },
  get MATERIALS() { return getVideoAnalysisPrompt(); },
  get FUNCTIONALITY() { return getVideoAnalysisPrompt(); },
  get USAGE_SCENARIOS() { return getVideoAnalysisPrompt(); },
  get BRAND_ELEMENTS() { return getVideoAnalysisPrompt(); },
  get ATMOSPHERE() { return getVideoAnalysisPrompt(); }
};

/**
 * 简化的提示词管理器
 */
export class SimplePromptManager {
  /**
   * 获取视频分析提示词
   */
  getVideoAnalysisPrompt(): string {
    return getVideoAnalysisPrompt();
  }

  /**
   * 格式化文件夹匹配提示词
   */
  formatFolderMatchingPrompt(contentDescription: string, folderNames: string[]): string {
    return formatFolderMatchingPrompt(contentDescription, folderNames);
  }

  /**
   * 重新加载提示词
   */
  reloadPrompts(): void {
    reloadPrompts();
  }
}

/**
 * 默认的提示词管理器实例
 */
export const defaultPromptManager = new SimplePromptManager();

/**
 * 导出主要的提示词（兼容旧的导出方式）
 */
export const VIDEO_ANALYSIS_PROMPT = getVideoAnalysisPrompt();
