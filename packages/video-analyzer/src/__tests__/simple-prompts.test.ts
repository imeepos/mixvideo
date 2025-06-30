/**
 * Tests for the simplified prompts system
 */

import {
  VIDEO_ANALYSIS_PROMPT,
  getVideoAnalysisPrompt,
  getFolderMatchingTemplate,
  formatFolderMatchingPrompt,
  reloadPrompts,
  SimplePromptManager,
  defaultPromptManager,
  ANALYSIS_PROMPTS,
  PRODUCT_ANALYSIS_PROMPTS
} from '../simple-prompts';

describe('Simple Prompts System', () => {
  describe('Basic prompts', () => {
    it('should provide a unified video analysis prompt', () => {
      expect(VIDEO_ANALYSIS_PROMPT).toBeDefined();
      expect(typeof VIDEO_ANALYSIS_PROMPT).toBe('string');
      expect(VIDEO_ANALYSIS_PROMPT.length).toBeGreaterThan(0);
      // 适应用户自定义的提示词内容
      expect(VIDEO_ANALYSIS_PROMPT).toMatch(/视频|分析|内容/);
    });

    it('should load video analysis prompt from function', () => {
      const prompt = getVideoAnalysisPrompt();
      expect(prompt).toBeDefined();
      expect(typeof prompt).toBe('string');
      expect(prompt.length).toBeGreaterThan(0);
    });

    it('should provide folder matching template', () => {
      const template = getFolderMatchingTemplate();
      expect(template).toBeDefined();
      expect(template).toContain('{contentDescription}');
      expect(template).toContain('{folderList}');
    });
  });

  describe('formatFolderMatchingPrompt', () => {
    it('should format folder matching prompt correctly', () => {
      const contentDescription = '这是一个产品展示视频';
      const folderNames = ['电子产品', '数码设备'];
      
      const result = formatFolderMatchingPrompt(contentDescription, folderNames);
      
      expect(result).toContain(contentDescription);
      expect(result).toContain('1. 电子产品');
      expect(result).toContain('2. 数码设备');
      expect(result).toContain('JSON格式');
    });

    it('should handle empty folder list', () => {
      const result = formatFolderMatchingPrompt('测试视频', []);
      expect(result).toContain('测试视频');
      expect(result).toBeDefined();
    });
  });

  describe('getVideoAnalysisPrompt', () => {
    it('should return video analysis prompt', () => {
      const result = getVideoAnalysisPrompt();
      expect(result).toBeDefined();
      expect(typeof result).toBe('string');
      expect(result.length).toBeGreaterThan(0);
    });

    it('should return consistent results', () => {
      const result1 = getVideoAnalysisPrompt();
      const result2 = getVideoAnalysisPrompt();
      expect(result1).toEqual(result2);
    });
  });

  describe('reloadPrompts', () => {
    it('should reload prompts without error', () => {
      expect(() => reloadPrompts()).not.toThrow();
    });
  });

  describe('SimplePromptManager', () => {
    it('should create manager with default config', () => {
      const manager = new SimplePromptManager();
      expect(manager).toBeDefined();
    });

    it('should provide video analysis prompt', () => {
      const manager = new SimplePromptManager();
      const prompt = manager.getVideoAnalysisPrompt();
      expect(prompt).toEqual(VIDEO_ANALYSIS_PROMPT);
    });

    it('should format folder matching prompt', () => {
      const manager = new SimplePromptManager();
      const result = manager.formatFolderMatchingPrompt('测试', ['文件夹1']);
      expect(result).toContain('测试');
      expect(result).toContain('文件夹1');
    });

    it('should reload prompts', () => {
      const manager = new SimplePromptManager();
      expect(() => manager.reloadPrompts()).not.toThrow();
    });
  });

  describe('Default prompt manager', () => {
    it('should provide a default instance', () => {
      expect(defaultPromptManager).toBeDefined();
      expect(defaultPromptManager instanceof SimplePromptManager).toBe(true);
    });
  });

  describe('Backward compatibility', () => {
    it('should provide all legacy ANALYSIS_PROMPTS', () => {
      expect(ANALYSIS_PROMPTS.COMPREHENSIVE).toEqual(VIDEO_ANALYSIS_PROMPT);
      expect(ANALYSIS_PROMPTS.PRODUCT_FOCUSED).toEqual(VIDEO_ANALYSIS_PROMPT);
      expect(ANALYSIS_PROMPTS.SCENE_DETECTION).toEqual(VIDEO_ANALYSIS_PROMPT);
      expect(ANALYSIS_PROMPTS.OBJECT_DETECTION).toEqual(VIDEO_ANALYSIS_PROMPT);
    });

    it('should provide all legacy PRODUCT_ANALYSIS_PROMPTS', () => {
      expect(PRODUCT_ANALYSIS_PROMPTS.APPEARANCE).toEqual(VIDEO_ANALYSIS_PROMPT);
      expect(PRODUCT_ANALYSIS_PROMPTS.MATERIALS).toEqual(VIDEO_ANALYSIS_PROMPT);
      expect(PRODUCT_ANALYSIS_PROMPTS.FUNCTIONALITY).toEqual(VIDEO_ANALYSIS_PROMPT);
      expect(PRODUCT_ANALYSIS_PROMPTS.USAGE_SCENARIOS).toEqual(VIDEO_ANALYSIS_PROMPT);
      expect(PRODUCT_ANALYSIS_PROMPTS.BRAND_ELEMENTS).toEqual(VIDEO_ANALYSIS_PROMPT);
      expect(PRODUCT_ANALYSIS_PROMPTS.ATMOSPHERE).toEqual(VIDEO_ANALYSIS_PROMPT);
    });
  });

  describe('Content validation', () => {
    it('should contain analysis instructions', () => {
      // 适应用户自定义的提示词内容，检查基本的分析相关词汇
      const prompt = VIDEO_ANALYSIS_PROMPT.toLowerCase();
      const hasAnalysisTerms = prompt.includes('分析') ||
                              prompt.includes('识别') ||
                              prompt.includes('检测') ||
                              prompt.includes('管理') ||
                              prompt.includes('分类');
      expect(hasAnalysisTerms).toBe(true);
    });

    it('should be in Chinese', () => {
      expect(VIDEO_ANALYSIS_PROMPT).toMatch(/[\u4e00-\u9fff]/);
      expect(getFolderMatchingTemplate()).toMatch(/[\u4e00-\u9fff]/);
    });

    it('should be suitable for video analysis', () => {
      // 检查是否包含视频相关内容
      const prompt = VIDEO_ANALYSIS_PROMPT.toLowerCase();
      const hasVideoTerms = prompt.includes('视频') ||
                           prompt.includes('素材') ||
                           prompt.includes('资源') ||
                           prompt.includes('内容');
      expect(hasVideoTerms).toBe(true);
    });
  });
});
