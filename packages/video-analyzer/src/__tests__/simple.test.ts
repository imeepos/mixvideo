/**
 * Simple test to verify the package builds correctly
 */

describe('VideoAnalyzer Package', () => {
  it('should export main classes', () => {
    const { VideoAnalyzer } = require('../core/VideoAnalyzer');
    expect(VideoAnalyzer).toBeDefined();
  });

  it('should export utility classes', () => {
    const { FrameExtractor } = require('../utils/FrameExtractor');
    const { VideoProcessor } = require('../utils/VideoProcessor');
    const { PromptBuilder } = require('../utils/PromptBuilder');
    
    expect(FrameExtractor).toBeDefined();
    expect(VideoProcessor).toBeDefined();
    expect(PromptBuilder).toBeDefined();
  });

  it('should export types', () => {
    const types = require('../types');
    expect(types).toBeDefined();
  });

  it('should create VideoAnalyzer instance', () => {
    const { VideoAnalyzer } = require('../core/VideoAnalyzer');
    const analyzer = new VideoAnalyzer({ apiKey: 'test-key' });
    expect(analyzer).toBeInstanceOf(VideoAnalyzer);
  });
});
