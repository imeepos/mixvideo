/**
 * Basic usage example for @mixvideo/video-analyzer
 */

import { 
  VideoAnalyzer, 
  analyzeVideoQuick, 
  extractVideoHighlights,
  compareVideos,
  AnalysisOptions 
} from '../src';

// Example 1: Basic video analysis
async function basicAnalysis() {
  console.log('🎬 Basic Video Analysis Example');
  
  const analyzer = new VideoAnalyzer({
    apiKey: process.env.GEMINI_API_KEY || 'your-api-key-here'
  });

  // Create a mock video file for demonstration
  const videoFile = new File(['mock video data'], 'sample.mp4', { 
    type: 'video/mp4' 
  });

  try {
    const result = await analyzer.analyzeVideo(
      videoFile,
      {
        enableSceneDetection: true,
        enableObjectDetection: true,
        enableSummarization: true,
        frameSamplingInterval: 2,
        maxFrames: 30,
        quality: 'medium',
        language: 'zh-CN'
      },
      (progress) => {
        console.log(`📊 ${progress.step}: ${progress.progress.toFixed(1)}%`);
      }
    );

    console.log('\n✅ Analysis Complete!');
    console.log(`📹 Video: ${result.metadata.filename}`);
    console.log(`⏱️  Duration: ${result.metadata.duration}s`);
    console.log(`📐 Resolution: ${result.metadata.width}x${result.metadata.height}`);
    console.log(`🎞️  Format: ${result.metadata.format}`);
    
    console.log('\n🎭 Scenes Detected:');
    result.scenes.forEach((scene, index) => {
      console.log(`  ${index + 1}. ${scene.description}`);
      console.log(`     ⏰ ${scene.startTime}s - ${scene.endTime}s`);
      console.log(`     🎯 Type: ${scene.type} (${(scene.confidence * 100).toFixed(1)}%)`);
      console.log(`     🎭 Mood: ${scene.mood || 'N/A'}`);
    });

    console.log('\n🔍 Objects Detected:');
    result.objects.forEach((obj, index) => {
      console.log(`  ${index + 1}. ${obj.name} (${(obj.confidence * 100).toFixed(1)}%)`);
      console.log(`     ⏰ At ${obj.timestamp}s`);
      console.log(`     📦 Category: ${obj.category}`);
    });

    console.log('\n📝 Summary:');
    console.log(`Description: ${result.summary.description}`);
    console.log(`Themes: ${result.summary.themes.join(', ')}`);
    console.log(`Content Rating: ${result.summary.contentRating.category}`);

  } catch (error) {
    console.error('❌ Analysis failed:', error);
  }
}

// Example 2: Quick analysis using utility function
async function quickAnalysisExample() {
  console.log('\n🚀 Quick Analysis Example');
  
  const videoFile = new File(['mock video data'], 'quick-sample.mp4', { 
    type: 'video/mp4' 
  });

  try {
    const result = await analyzeVideoQuick(
      videoFile,
      process.env.GEMINI_API_KEY || 'your-api-key-here',
      {
        quality: 'high',
        maxFrames: 20
      }
    );

    console.log('✅ Quick analysis complete!');
    console.log(`📊 Processing time: ${result.processingTime}ms`);
    console.log(`🎬 Scenes found: ${result.scenes.length}`);
    console.log(`🔍 Objects found: ${result.objects.length}`);

  } catch (error) {
    console.error('❌ Quick analysis failed:', error);
  }
}

// Example 3: Highlight extraction
async function highlightExtractionExample() {
  console.log('\n✨ Highlight Extraction Example');
  
  const videoFile = new File(['mock video data'], 'highlights-sample.mp4', { 
    type: 'video/mp4' 
  });

  try {
    const highlights = await extractVideoHighlights(
      videoFile,
      process.env.GEMINI_API_KEY || 'your-api-key-here',
      {
        language: 'zh-CN'
      }
    );

    console.log(`✅ Found ${highlights.length} highlights!`);
    
    highlights.forEach((highlight, index) => {
      console.log(`\n🌟 Highlight ${index + 1}:`);
      console.log(`   📝 ${highlight.description}`);
      console.log(`   ⏰ ${highlight.startTime}s - ${highlight.endTime}s`);
      console.log(`   🎯 Type: ${highlight.type}`);
      console.log(`   ⭐ Importance: ${(highlight.importance * 100).toFixed(1)}%`);
      console.log(`   📱 Social Media Ready: ${highlight.socialMediaReady ? '✅' : '❌'}`);
    });

    // Filter for social media ready highlights
    const socialHighlights = highlights.filter(h => h.socialMediaReady && h.importance > 0.7);
    console.log(`\n📱 Social Media Ready Highlights: ${socialHighlights.length}`);

  } catch (error) {
    console.error('❌ Highlight extraction failed:', error);
  }
}

// Example 4: Video comparison
async function videoComparisonExample() {
  console.log('\n🔄 Video Comparison Example');
  
  const video1 = new File(['mock video 1'], 'video1.mp4', { type: 'video/mp4' });
  const video2 = new File(['mock video 2'], 'video2.mp4', { type: 'video/mp4' });

  try {
    const comparison = await compareVideos(
      video1,
      video2,
      process.env.GEMINI_API_KEY || 'your-api-key-here',
      {
        language: 'zh-CN'
      }
    );

    console.log('✅ Comparison complete!');
    console.log(`🎯 Similarity Score: ${(comparison.similarity * 100).toFixed(1)}%`);
    console.log(`📝 Analysis: ${comparison.analysis}`);

  } catch (error) {
    console.error('❌ Video comparison failed:', error);
  }
}

// Example 5: Batch processing
async function batchProcessingExample() {
  console.log('\n📦 Batch Processing Example');
  
  const analyzer = new VideoAnalyzer({
    apiKey: process.env.GEMINI_API_KEY || 'your-api-key-here'
  });

  const videos = [
    { 
      input: new File(['mock video 1'], 'batch1.mp4', { type: 'video/mp4' }), 
      id: 'video1' 
    },
    { 
      input: new File(['mock video 2'], 'batch2.mp4', { type: 'video/mp4' }), 
      id: 'video2' 
    },
    { 
      input: new File(['mock video 3'], 'batch3.mp4', { type: 'video/mp4' }), 
      id: 'video3' 
    }
  ];

  try {
    const results = await analyzer.analyzeBatch(
      videos,
      {
        quality: 'medium',
        maxFrames: 15
      },
      (progress) => {
        console.log(`📊 Batch Progress: ${progress.step} (${progress.progress.toFixed(1)}%)`);
      }
    );

    console.log(`✅ Batch processing complete! Analyzed ${results.size} videos.`);
    
    for (const [videoId, result] of results) {
      console.log(`\n🎬 ${videoId}:`);
      console.log(`   📝 ${result.summary.description.substring(0, 100)}...`);
      console.log(`   🎭 Scenes: ${result.scenes.length}`);
      console.log(`   🔍 Objects: ${result.objects.length}`);
      console.log(`   ⏱️  Processing: ${result.processingTime}ms`);
    }

  } catch (error) {
    console.error('❌ Batch processing failed:', error);
  }
}

// Example 6: Custom analysis with specific prompts
async function customAnalysisExample() {
  console.log('\n🎯 Custom Analysis Example');
  
  const analyzer = new VideoAnalyzer({
    apiKey: process.env.GEMINI_API_KEY || 'your-api-key-here'
  });

  const videoFile = new File(['mock video data'], 'custom-sample.mp4', { 
    type: 'video/mp4' 
  });

  const customOptions: AnalysisOptions = {
    customPrompt: `
      请专门分析这个视频的以下方面：
      1. 营销潜力和商业价值
      2. 品牌安全性评估
      3. 观众参与度因素
      4. 推荐的社交媒体平台
      5. 最佳发布时间建议
      
      请为每个方面提供详细的见解和建议。
    `,
    language: 'zh-CN',
    quality: 'high'
  };

  try {
    const result = await analyzer.analyzeVideo(videoFile, customOptions);
    
    console.log('✅ Custom analysis complete!');
    console.log(`📝 Custom Analysis Result:`);
    console.log(result.summary.description);

  } catch (error) {
    console.error('❌ Custom analysis failed:', error);
  }
}

// Run all examples
async function runAllExamples() {
  console.log('🎬 @mixvideo/video-analyzer Examples\n');
  console.log('=' .repeat(50));
  
  await basicAnalysis();
  await quickAnalysisExample();
  await highlightExtractionExample();
  await videoComparisonExample();
  await batchProcessingExample();
  await customAnalysisExample();
  
  console.log('\n' + '='.repeat(50));
  console.log('🎉 All examples completed!');
}

// Export for use in other files
export {
  basicAnalysis,
  quickAnalysisExample,
  highlightExtractionExample,
  videoComparisonExample,
  batchProcessingExample,
  customAnalysisExample,
  runAllExamples
};

// Run examples if this file is executed directly
if (require.main === module) {
  runAllExamples().catch(console.error);
}
