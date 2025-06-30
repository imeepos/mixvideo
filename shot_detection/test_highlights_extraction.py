#!/usr/bin/env python3
"""
测试高光时刻提取功能
验证新的提示词和结果解析是否正常工作
"""

import json
from pathlib import Path


def test_highlights_extraction():
    """测试高光时刻提取功能"""
    print("🧪 测试高光时刻提取功能")
    print("=" * 50)
    
    # 模拟Gemini API返回的结果（新格式）
    mock_result_new_format = {
        "summary": "这是一个展示女装搭配的时尚视频，包含多个精彩的展示瞬间和情感表达。",
        "highlights": [
            {
                "timestamp": "00:15",
                "description": "模特优雅转身展示裙装飘逸效果",
                "type": "动作",
                "confidence": 0.95,
                "duration": "3"
            },
            {
                "timestamp": "00:32",
                "description": "特写镜头展示面料质感和细节工艺",
                "type": "视觉",
                "confidence": 0.88,
                "duration": "2"
            },
            {
                "timestamp": "01:05",
                "description": "音乐高潮配合模特跳跃动作",
                "type": "音乐",
                "confidence": 0.92,
                "duration": "4"
            }
        ],
        "scenes": [
            {
                "timestamp": "00:00",
                "description": "开场介绍，模特站立展示整体造型",
                "objects": ["模特", "连衣裙", "高跟鞋"],
                "actions": ["站立", "微笑"],
                "mood": "自信"
            },
            {
                "timestamp": "00:20",
                "description": "动态展示，模特走动和转身",
                "objects": ["模特", "裙装", "背景"],
                "actions": ["走动", "转身", "摆pose"],
                "mood": "活泼"
            }
        ],
        "emotions": {
            "overall_mood": "积极向上，充满活力",
            "emotion_changes": [
                {
                    "timestamp": "00:10",
                    "emotion": "自信",
                    "intensity": 0.8
                },
                {
                    "timestamp": "00:45",
                    "emotion": "优雅",
                    "intensity": 0.9
                }
            ]
        },
        "quality": {
            "video_quality": 8,
            "audio_quality": 7,
            "lighting": "良好，自然光线充足",
            "stability": "稳定，无明显抖动"
        },
        "technical": {
            "resolution": "1080p",
            "frame_rate": "30fps",
            "color_grading": "暖色调，饱和度适中",
            "camera_movements": ["固定镜头", "跟拍", "特写"]
        }
    }
    
    # 模拟旧格式的结果
    mock_result_old_format = {
        "content_analysis": {
            "summary": "传统格式的视频分析结果",
            "full_text": "这个视频在00:25和01:10有特别精彩的高光时刻，展示了产品的最佳角度。"
        }
    }
    
    # 测试新格式的高光提取
    print("📋 测试新格式高光提取:")
    from gui_app import ShotDetectionGUI
    import tkinter as tk
    
    # 创建临时GUI实例来测试方法
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    app = ShotDetectionGUI(root)
    
    highlights_new = app._extract_highlights(mock_result_new_format)
    print(f"✅ 新格式提取到 {len(highlights_new)} 个高光时刻:")
    for i, highlight in enumerate(highlights_new, 1):
        print(f"  {i}. [{highlight.get('timestamp')}] {highlight.get('description')} "
              f"({highlight.get('type', '未分类')}) [置信度: {highlight.get('confidence', 0):.1%}]")
    
    print("\n📋 测试旧格式高光提取:")
    highlights_old = app._extract_highlights(mock_result_old_format)
    print(f"✅ 旧格式提取到 {len(highlights_old)} 个高光时刻:")
    for i, highlight in enumerate(highlights_old, 1):
        print(f"  {i}. [{highlight.get('timestamp')}] {highlight.get('description')} "
              f"({highlight.get('type', '未分类')}) [置信度: {highlight.get('confidence', 0):.1%}]")
    
    # 测试提示词加载
    print("\n📝 测试提示词加载:")
    try:
        from prompts_manager import PromptsManager
        prompts_manager = PromptsManager()
        analysis_prompt = prompts_manager.get_video_analysis_prompt()
        
        if analysis_prompt:
            print(f"✅ 成功加载提示词，长度: {len(analysis_prompt)} 字符")
            
            # 检查关键词
            keywords = ['highlights', 'timestamp', 'confidence', 'JSON', '高光时刻']
            found_keywords = [kw for kw in keywords if kw in analysis_prompt]
            print(f"📊 包含关键词: {', '.join(found_keywords)}")
            
            if 'JSON' in analysis_prompt and 'highlights' in analysis_prompt:
                print("✅ 提示词包含JSON格式要求和高光时刻指令")
            else:
                print("⚠️ 提示词可能缺少关键指令")
        else:
            print("❌ 提示词加载失败")
            
    except Exception as e:
        print(f"❌ 提示词测试失败: {e}")
    
    # 保存测试结果
    test_results = {
        "new_format_highlights": highlights_new,
        "old_format_highlights": highlights_old,
        "test_time": "2024-01-01 12:00:00"
    }
    
    output_file = "highlights_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 测试结果已保存到: {output_file}")
    
    root.destroy()
    print("\n🎉 高光时刻提取功能测试完成！")


def test_prompt_format():
    """测试提示词格式"""
    print("\n🔍 检查提示词格式:")
    
    prompt_file = Path("prompts/video-analysis.prompt")
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键元素
        checks = {
            "JSON格式要求": "```json" in content,
            "高光时刻字段": "highlights" in content,
            "时间戳要求": "timestamp" in content,
            "置信度要求": "confidence" in content,
            "场景分析": "scenes" in content,
            "情感分析": "emotions" in content,
            "质量评估": "quality" in content
        }
        
        print("📋 提示词检查结果:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        passed_count = sum(checks.values())
        total_count = len(checks)
        print(f"\n📊 检查通过率: {passed_count}/{total_count} ({passed_count/total_count:.1%})")
        
        if passed_count == total_count:
            print("🎉 提示词格式完全符合要求！")
        else:
            print("⚠️ 提示词需要进一步优化")
    else:
        print("❌ 提示词文件不存在")


if __name__ == "__main__":
    test_highlights_extraction()
    test_prompt_format()
