/**
 * 简化提示词系统使用示例
 * 
 * 展示如何使用新的简化提示词系统进行视频分析
 */

import {
  // 简化的提示词系统（推荐）
  VIDEO_ANALYSIS_PROMPT,
  getVideoAnalysisPrompt,
  formatFolderMatchingPrompt,
  SimplePromptManager,
  defaultPromptManager,

  // 向后兼容的导出
  ANALYSIS_PROMPTS,
  PRODUCT_ANALYSIS_PROMPTS
} from '../src/simple-prompts';

/**
 * 示例1：使用统一的视频分析提示词
 */
function example1_UnifiedVideoAnalysis() {
  console.log('=== 示例1：统一视频分析 ===');
  
  // 直接使用统一的提示词
  console.log('统一提示词长度:', VIDEO_ANALYSIS_PROMPT.length);
  console.log('包含场景检测:', VIDEO_ANALYSIS_PROMPT.includes('场景检测'));
  console.log('包含产品分析:', VIDEO_ANALYSIS_PROMPT.includes('产品分析'));
  
  // 这个提示词包含了所有分析功能：
  // - 基础分析（场景、物体、内容、情感、关键词）
  // - 产品分析（外观、功能、场景、受众、品牌）
  // - 技术分析（拍摄、音频）
}

/**
 * 示例2：文件夹匹配
 */
function example2_FolderMatching() {
  console.log('\n=== 示例2：文件夹匹配 ===');
  
  const videoDescription = '这是一个展示智能手机新功能的产品宣传视频，包含了产品外观展示和功能演示';
  const availableFolders = ['电子产品', '手机配件', '营销视频', '产品展示', '技术演示'];
  
  const folderPrompt = formatFolderMatchingPrompt(videoDescription, availableFolders);
  
  console.log('生成的文件夹匹配提示词:');
  console.log(folderPrompt.substring(0, 200) + '...');
}

/**
 * 示例3：从文件加载提示词
 */
function example3_LoadFromFile() {
  console.log('\n=== 示例3：从文件加载提示词 ===');

  // 提示词现在从独立文件加载
  const videoPrompt = getVideoAnalysisPrompt();

  console.log('从文件加载的视频分析提示词长度:', videoPrompt.length);
  console.log('包含基础分析:', videoPrompt.includes('基础分析'));
  console.log('包含产品分析:', videoPrompt.includes('产品分析'));
  console.log('包含技术分析:', videoPrompt.includes('技术分析'));

  console.log('\n提示词文件位置:');
  console.log('- 视频分析: prompts/video-analysis.prompt');
  console.log('- 文件夹匹配: prompts/folder-matching.prompt');
}

/**
 * 示例4：使用提示词管理器
 */
function example4_PromptManager() {
  console.log('\n=== 示例4：提示词管理器 ===');
  
  // 使用默认管理器
  const videoPrompt = defaultPromptManager.getVideoAnalysisPrompt();
  console.log('默认管理器获取的提示词长度:', videoPrompt.length);
  
  // 创建自定义管理器
  const customManager = new SimplePromptManager();
  
  const folderPrompt = customManager.formatFolderMatchingPrompt(
    '产品演示视频',
    ['产品', '演示', '教程']
  );
  
  console.log('自定义管理器生成的文件夹匹配提示词包含"产品":', folderPrompt.includes('产品'));
}

/**
 * 示例5：向后兼容性
 */
function example5_BackwardCompatibility() {
  console.log('\n=== 示例5：向后兼容性 ===');
  
  // 所有旧的提示词名称现在都指向同一个统一提示词
  console.log('COMPREHENSIVE === PRODUCT_FOCUSED:', 
    ANALYSIS_PROMPTS.COMPREHENSIVE === ANALYSIS_PROMPTS.PRODUCT_FOCUSED);
  
  console.log('APPEARANCE === MATERIALS:', 
    PRODUCT_ANALYSIS_PROMPTS.APPEARANCE === PRODUCT_ANALYSIS_PROMPTS.MATERIALS);
  
  console.log('所有提示词都相同:', 
    ANALYSIS_PROMPTS.COMPREHENSIVE === VIDEO_ANALYSIS_PROMPT);
  
  // 旧代码仍然可以工作，但现在更简单了
  const oldStylePrompt = ANALYSIS_PROMPTS.SCENE_DETECTION;
  const newStylePrompt = VIDEO_ANALYSIS_PROMPT;
  
  console.log('旧式和新式提示词相同:', oldStylePrompt === newStylePrompt);
}

/**
 * 示例6：实际使用场景
 */
function example6_RealWorldUsage() {
  console.log('\n=== 示例6：实际使用场景 ===');
  
  // 场景1：视频分析服务
  class VideoAnalysisService {
    private promptManager = new SimplePromptManager();
    
    async analyzeVideo(videoFile: any) {
      const prompt = this.promptManager.getVideoAnalysisPrompt();
      
      // 这里会调用 AI 服务
      console.log('使用提示词分析视频:', videoFile.name);
      console.log('提示词类型: 统一分析');
      
      return {
        prompt,
        analysis: '模拟分析结果'
      };
    }
    
    async matchFolder(videoDescription: string, folders: string[]) {
      const prompt = this.promptManager.formatFolderMatchingPrompt(videoDescription, folders);
      
      console.log('使用提示词匹配文件夹');
      console.log('候选文件夹数量:', folders.length);
      
      return {
        prompt,
        matches: '模拟匹配结果'
      };
    }
  }
  
  // 使用服务
  const service = new VideoAnalysisService();
  service.analyzeVideo({ name: 'demo.mp4' });
  service.matchFolder('产品视频', ['产品', '营销', '演示']);
}

/**
 * 运行所有示例
 */
function runAllExamples() {
  console.log('🎬 简化提示词系统使用示例\n');
  
  example1_UnifiedVideoAnalysis();
  example2_FolderMatching();
  example3_LoadFromFile();
  example4_PromptManager();
  example5_BackwardCompatibility();
  example6_RealWorldUsage();
  
  console.log('\n✅ 所有示例运行完成！');
  console.log('\n📝 总结：');
  console.log('- 使用 getVideoAnalysisPrompt() 获取统一视频分析提示词');
  console.log('- 提示词从独立文件加载：prompts/video-analysis.prompt');
  console.log('- 使用 formatFolderMatchingPrompt() 进行文件夹匹配');
  console.log('- 文件夹匹配提示词从：prompts/folder-matching.prompt');
  console.log('- 使用 SimplePromptManager 进行统一管理');
  console.log('- 旧的提示词名称仍然可用，保证向后兼容');
  console.log('- 用户可以直接修改 prompts/ 目录下的文件来自定义提示词');
}

// 如果直接运行此文件
if (require.main === module) {
  runAllExamples();
}

export {
  example1_UnifiedVideoAnalysis,
  example2_FolderMatching,
  example3_LoadFromFile,
  example4_PromptManager,
  example5_BackwardCompatibility,
  example6_RealWorldUsage,
  runAllExamples
};
