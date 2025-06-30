#!/usr/bin/env python3
"""
Gemini视频分析器使用示例
演示如何使用改进后的GeminiVideoAnalyzer
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from gemini_video_analyzer import create_gemini_analyzer, GeminiConfig, AnalysisProgress


def example_basic_usage():
    """基础使用示例"""
    print("🎬 基础视频分析示例")
    
    # 创建分析器（使用默认配置）
    analyzer = create_gemini_analyzer(
        cloudflare_project_id="your_project_id",
        cloudflare_gateway_id="your_gateway_id",
        google_project_id="your_google_project_id",
        enable_cache=True
    )
    
    # 测试视频文件
    video_path = "sample_video.mp4"
    
    if not os.path.exists(video_path):
        print(f"⚠️ 视频文件不存在: {video_path}")
        print("请将视频文件放在当前目录下")
        return
    
    # 分析提示词
    prompt = """请分析这个视频并以JSON格式返回结果，包含以下信息：
{
  "summary": "视频内容总结",
  "scenes": [
    {
      "timestamp": "时间戳",
      "description": "场景描述",
      "objects": ["检测到的物体"],
      "actions": ["动作描述"]
    }
  ],
  "quality": {
    "resolution": "分辨率评估",
    "clarity": "清晰度评分(1-10)",
    "lighting": "光线质量评估"
  },
  "emotions": "情感色调分析"
}"""
    
    # 进度回调函数
    def progress_callback(progress: AnalysisProgress):
        print(f"📊 {progress.step} ({progress.progress}%)")
        if progress.stage == "upload":
            print("   🔄 上传阶段")
        elif progress.stage == "analysis":
            print("   🤖 分析阶段")
        elif progress.stage == "complete":
            print("   ✅ 完成")
    
    try:
        # 执行分析
        result = analyzer.analyze_video(video_path, prompt, progress_callback)
        
        print("\n✅ 分析完成！")
        print(f"📁 文件: {result['video_info']['file_name']}")
        print(f"🤖 模型: {result['video_info']['model_used']}")
        print(f"⏰ 时间: {result['video_info']['analysis_time']}")
        
        # 保存结果
        output_file = f"analysis_{Path(video_path).stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")


def example_custom_config():
    """自定义配置示例"""
    print("⚙️ 自定义配置示例")
    
    # 创建自定义配置
    config = GeminiConfig(
        cloudflare_project_id="your_project_id",
        cloudflare_gateway_id="your_gateway_id",
        google_project_id="your_google_project_id",
        regions=["us-central1", "europe-west1"],  # 自定义区域
        model_name="gemini-2.5-flash",
        enable_cache=True,
        cache_dir="./custom_cache",
        max_retries=5,
        retry_delay=3,
        timeout=180
    )
    
    from gemini_video_analyzer import GeminiVideoAnalyzer
    analyzer = GeminiVideoAnalyzer(config)
    
    # 显示配置信息
    print(f"📋 配置信息:")
    print(f"  - 模型: {config.model_name}")
    print(f"  - 区域: {config.regions}")
    print(f"  - 缓存: {config.enable_cache}")
    print(f"  - 缓存目录: {config.cache_dir}")
    print(f"  - 重试次数: {config.max_retries}")
    print(f"  - 超时时间: {config.timeout}秒")
    
    # 获取缓存统计
    cache_stats = analyzer.get_cache_stats()
    print(f"📊 缓存统计: {cache_stats}")


def example_batch_analysis():
    """批量分析示例"""
    print("📦 批量视频分析示例")
    
    analyzer = create_gemini_analyzer()
    
    # 查找当前目录下的所有视频文件
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    video_files = []
    
    for ext in video_extensions:
        video_files.extend(Path('.').glob(f'*{ext}'))
    
    if not video_files:
        print("⚠️ 当前目录下没有找到视频文件")
        return
    
    print(f"📁 找到 {len(video_files)} 个视频文件")
    
    # 简单的分析提示词
    prompt = "请简要分析这个视频的内容，包括主要场景、物体和活动。"
    
    results = []
    
    for i, video_file in enumerate(video_files):
        print(f"\n🎬 分析视频 {i+1}/{len(video_files)}: {video_file.name}")
        
        try:
            def progress_callback(progress: AnalysisProgress):
                print(f"  📊 {progress.step} ({progress.progress}%)")
            
            result = analyzer.analyze_video(str(video_file), prompt, progress_callback)
            results.append({
                "file": video_file.name,
                "success": True,
                "result": result
            })
            
            print(f"  ✅ 完成: {video_file.name}")
            
        except Exception as e:
            print(f"  ❌ 失败: {video_file.name} - {e}")
            results.append({
                "file": video_file.name,
                "success": False,
                "error": str(e)
            })
    
    # 保存批量结果
    import json
    with open("batch_analysis_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 批量分析完成:")
    success_count = sum(1 for r in results if r['success'])
    print(f"  - 成功: {success_count}/{len(results)}")
    print(f"  - 结果已保存到: batch_analysis_results.json")


def example_cache_management():
    """缓存管理示例"""
    print("🗂️ 缓存管理示例")
    
    analyzer = create_gemini_analyzer()
    
    # 获取缓存统计
    stats = analyzer.get_cache_stats()
    print(f"📊 当前缓存统计:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")
    
    # 清理过期缓存
    clean_result = analyzer.clean_expired_cache()
    print(f"\n🧹 缓存清理结果:")
    print(f"  - 删除文件: {clean_result['removed']}")
    print(f"  - 总文件数: {clean_result['total']}")
    
    # 再次获取统计
    stats = analyzer.get_cache_stats()
    print(f"\n📊 清理后缓存统计:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")


def main():
    """主函数"""
    print("🎬 Gemini视频分析器示例")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "basic":
            example_basic_usage()
        elif command == "config":
            example_custom_config()
        elif command == "batch":
            example_batch_analysis()
        elif command == "cache":
            example_cache_management()
        else:
            print(f"❌ 未知命令: {command}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """打印使用说明"""
    print("使用方法:")
    print("  python example_usage.py basic   # 基础使用示例")
    print("  python example_usage.py config  # 自定义配置示例")
    print("  python example_usage.py batch   # 批量分析示例")
    print("  python example_usage.py cache   # 缓存管理示例")


if __name__ == "__main__":
    main()
