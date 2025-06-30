#!/usr/bin/env python3
"""
测试真实的Gemini视频分析功能
"""

import asyncio
from pathlib import Path
import json


def test_real_video_analysis():
    """测试真实的视频分析功能"""
    print("🎬 测试真实Gemini视频分析")
    print("=" * 50)
    
    try:
        # 使用真实的测试视频文件
        test_video = Path("test_video.mp4")
        if not test_video.exists():
            print(f"❌ 测试视频文件不存在: {test_video}")
            return False

        print(f"✅ 使用测试视频文件: {test_video}")

        # 检查文件大小
        file_size = test_video.stat().st_size
        print(f"📊 文件大小: {file_size / 1024 / 1024:.2f} MB")

        # 加载配置
        from config import get_config
        config = get_config()
        gemini_config = config.gemini
        
        print(f"📋 使用配置:")
        print(f"  - 模型: {gemini_config.model_name}")
        print(f"  - 缓存: {'启用' if gemini_config.enable_cache else '禁用'}")
        
        # 创建分析器
        from gemini_video_analyzer import create_gemini_analyzer, AnalysisProgress
        
        analyzer = create_gemini_analyzer(
            cloudflare_project_id=gemini_config.cloudflare_project_id,
            cloudflare_gateway_id=gemini_config.cloudflare_gateway_id,
            google_project_id=gemini_config.google_project_id,
            regions=gemini_config.regions,
            model_name=gemini_config.model_name,
            enable_cache=gemini_config.enable_cache,
            cache_dir=gemini_config.cache_dir
        )
        
        print(f"✅ 分析器创建成功")
        
        # 加载提示词
        from prompts_manager import PromptsManager
        prompts_manager = PromptsManager()
        analysis_prompt = prompts_manager.get_video_analysis_prompt()
        
        print(f"📝 提示词长度: {len(analysis_prompt)} 字符")
        
        # 定义进度回调
        def progress_callback(progress: AnalysisProgress):
            print(f"📊 {progress.step} ({progress.progress}%)")
        
        print(f"\n🚀 开始视频分析...")
        
        # 执行分析
        result = analyzer.analyze_video(str(test_video), analysis_prompt, progress_callback)
        
        print(f"✅ 分析完成!")
        
        # 保存结果
        result_file = "test_analysis_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 结果已保存到: {result_file}")
        
        # 显示结果摘要
        print(f"\n📊 分析结果摘要:")
        
        video_info = result.get('video_info', {})
        analysis_result = result.get('analysis_result', {})
        
        print(f"  - 文件名: {video_info.get('file_name', 'unknown')}")
        print(f"  - 模型: {video_info.get('model_used', 'unknown')}")
        print(f"  - 分析时间: {video_info.get('analysis_time', 'unknown')}")
        
        # 检查高光时刻
        if 'highlights' in analysis_result:
            highlights = analysis_result['highlights']
            print(f"  - 高光时刻: {len(highlights)} 个")
            for i, highlight in enumerate(highlights[:3], 1):
                timestamp = highlight.get('timestamp', '未知')
                description = highlight.get('description', '无描述')
                print(f"    {i}. [{timestamp}] {description}")
        
        # 检查场景分析
        if 'scenes' in analysis_result:
            scenes = analysis_result['scenes']
            print(f"  - 场景数量: {len(scenes)} 个")
        
        # 检查质量评估
        if 'quality' in analysis_result:
            quality = analysis_result['quality']
            video_quality = quality.get('video_quality', 0)
            print(f"  - 视频质量: {video_quality}/10")
        
        print(f"\n🎉 真实视频分析测试成功!")
        return True
        
    except Exception as e:
        print(f"❌ 视频分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 不删除真实的测试视频文件
        print(f"📁 保留测试视频文件: {test_video}")


def test_cache_functionality():
    """测试缓存功能"""
    print(f"\n📊 测试缓存功能")
    print("=" * 20)
    
    try:
        from gemini_video_analyzer import create_gemini_analyzer
        from config import get_config
        
        config = get_config()
        gemini_config = config.gemini
        
        analyzer = create_gemini_analyzer(
            cloudflare_project_id=gemini_config.cloudflare_project_id,
            cloudflare_gateway_id=gemini_config.cloudflare_gateway_id,
            google_project_id=gemini_config.google_project_id,
            regions=gemini_config.regions,
            model_name=gemini_config.model_name,
            enable_cache=gemini_config.enable_cache,
            cache_dir=gemini_config.cache_dir
        )
        
        # 获取缓存统计
        cache_stats = analyzer.get_cache_stats()
        
        print(f"✅ 缓存统计:")
        print(f"  - 启用状态: {cache_stats.get('enabled', False)}")
        print(f"  - 缓存目录: {cache_stats.get('cache_dir', 'unknown')}")
        print(f"  - 文件数量: {cache_stats.get('total_files', 0)}")
        print(f"  - 总大小: {cache_stats.get('total_size', 0)} 字节")
        
        # 检查缓存目录
        cache_dir = Path(gemini_config.cache_dir)
        if cache_dir.exists():
            print(f"✅ 缓存目录存在: {cache_dir}")
            cache_files = list(cache_dir.glob("*.json"))
            print(f"  - 缓存文件: {len(cache_files)} 个")
        else:
            print(f"⚠️ 缓存目录不存在: {cache_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ 缓存功能测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 Gemini真实视频分析测试套件")
    print("=" * 60)
    
    tests = [
        ("缓存功能测试", test_cache_functionality),
        ("真实视频分析", test_real_video_analysis)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 运行测试: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
                
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 测试通过 ({passed/total:.1%})")
    
    if passed == total:
        print("🎉 所有测试通过！Gemini视频分析功能正常")
    else:
        print("⚠️ 部分测试失败，请检查配置")


if __name__ == "__main__":
    main()
