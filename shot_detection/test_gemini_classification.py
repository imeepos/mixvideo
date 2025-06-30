#!/usr/bin/env python3
"""
测试Gemini智能归类功能
"""

import json
import tkinter as tk
from pathlib import Path
import shutil


def test_gemini_classification():
    """测试Gemini智能归类功能"""
    print("🧪 测试Gemini智能归类功能")
    print("=" * 50)
    
    # 创建测试环境
    test_dir = Path("test_gemini_classification")
    test_dir.mkdir(exist_ok=True)
    
    # 创建测试视频文件
    test_video = test_dir / "test_video.mp4"
    test_video.touch()
    
    # 创建输出目录
    output_dir = test_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    # 创建GUI实例
    from gui_app import ShotDetectionGUI
    
    root = tk.Tk()
    root.withdraw()
    app = ShotDetectionGUI(root)
    
    # 设置输出目录
    app.analysis_output_dir.set(str(output_dir))
    
    # 测试不同类型的分析结果
    test_cases = [
        {
            "name": "产品展示视频",
            "analysis_data": {
                "summary": "这是一个白底背景下的女装产品展示视频，展示了一件红色连衣裙的细节特写",
                "highlights": [
                    {"timestamp": "00:05", "description": "产品360度旋转展示", "type": "视觉", "confidence": 0.95}
                ],
                "scenes": [
                    {
                        "timestamp": "00:00",
                        "description": "白底背景产品展示",
                        "objects": ["连衣裙", "白色背景", "展示台"],
                        "actions": ["静态展示", "旋转"],
                        "mood": "专业"
                    }
                ],
                "emotions": {"overall_mood": "专业展示"},
                "quality": {"video_quality": 9, "lighting": "均匀柔光"},
                "technical": {"resolution": "4K", "camera_movements": ["固定镜头", "旋转"]}
            },
            "expected_category": "product_display"
        },
        {
            "name": "模特试穿视频",
            "analysis_data": {
                "summary": "模特试穿展示视频，展现了服装的穿着效果和动态美感",
                "highlights": [
                    {"timestamp": "00:10", "description": "模特优雅转身", "type": "动作", "confidence": 0.92},
                    {"timestamp": "00:20", "description": "完美走位展示", "type": "动作", "confidence": 0.88}
                ],
                "scenes": [
                    {
                        "timestamp": "00:00",
                        "description": "模特试穿展示场景",
                        "objects": ["模特", "服装", "T台"],
                        "actions": ["试穿", "转身", "走位"],
                        "mood": "优雅"
                    }
                ],
                "emotions": {"overall_mood": "优雅时尚"},
                "quality": {"video_quality": 8, "lighting": "自然光线"},
                "technical": {"resolution": "1080p", "camera_movements": ["跟拍", "特写"]}
            },
            "expected_category": "model_wearing"
        },
        {
            "name": "优质高光视频",
            "analysis_data": {
                "summary": "包含多个精彩高光时刻的优质视频内容",
                "highlights": [
                    {"timestamp": "00:05", "description": "精彩动作瞬间", "type": "动作", "confidence": 0.95},
                    {"timestamp": "00:15", "description": "情感爆发时刻", "type": "情感", "confidence": 0.92},
                    {"timestamp": "00:25", "description": "视觉冲击画面", "type": "视觉", "confidence": 0.88},
                    {"timestamp": "00:35", "description": "完美转场效果", "type": "转场", "confidence": 0.90}
                ],
                "scenes": [
                    {
                        "timestamp": "00:00",
                        "description": "多元素综合展示",
                        "objects": ["模特", "产品", "场景"],
                        "actions": ["展示", "互动", "表演"],
                        "mood": "活力"
                    }
                ],
                "emotions": {"overall_mood": "活力四射"},
                "quality": {"video_quality": 9, "lighting": "专业布光"},
                "technical": {"resolution": "4K", "camera_movements": ["多角度", "动态跟拍"]}
            },
            "expected_category": "premium_highlights"
        }
    ]
    
    print("📋 测试Gemini智能归类:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case['name']}")
        
        try:
            # 测试内容描述构建
            content_description = app._build_content_description(test_case['analysis_data'])
            print(f"   📝 内容描述长度: {len(content_description)} 字符")
            print(f"   📄 内容描述: {content_description[:100]}...")
            
            # 测试Gemini归类
            classification_result = app._gemini_classify_video(test_case['analysis_data'])
            
            if classification_result:
                category = classification_result.get('category', 'unknown')
                confidence = classification_result.get('confidence', 0)
                reason = classification_result.get('reason', '无原因')
                
                print(f"   🎯 归类结果: {category}")
                print(f"   📊 置信度: {confidence:.1%}")
                print(f"   💭 归类原因: {reason}")
                
                # 检查是否符合预期
                expected = test_case.get('expected_category', '')
                if category == expected:
                    print(f"   ✅ 归类正确")
                else:
                    print(f"   ⚠️ 归类结果与预期不同 (预期: {expected})")
            else:
                print(f"   ❌ Gemini归类失败")
            
            # 测试完整归类流程
            print(f"   🔄 测试完整归类流程...")
            app._auto_classify_video(str(test_video), {"analysis_result": test_case['analysis_data']})
            
            # 检查归类结果
            classified_dir = output_dir / "classified"
            if classified_dir.exists():
                categories = [d.name for d in classified_dir.iterdir() if d.is_dir()]
                if categories:
                    print(f"   📁 已创建归类目录: {', '.join(categories)}")
                    
                    # 检查文件是否被正确归类
                    for cat_dir in classified_dir.iterdir():
                        if cat_dir.is_dir():
                            files = list(cat_dir.glob("*.mp4"))
                            if files:
                                print(f"   📄 {cat_dir.name} 目录下有 {len(files)} 个文件")
                else:
                    print(f"   ⚠️ 未创建归类目录")
            else:
                print(f"   ❌ 归类目录不存在")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 测试提示词加载
    print(f"\n📝 测试提示词加载:")
    try:
        from prompts_manager import PromptsManager
        prompts_manager = PromptsManager()
        
        # 测试folder-matching提示词
        folder_prompt = prompts_manager.get_folder_matching_prompt(
            "测试内容描述", 
            ["产品展示", "模特试穿"]
        )
        
        if folder_prompt:
            print(f"✅ folder-matching提示词加载成功，长度: {len(folder_prompt)} 字符")
            
            # 检查关键内容
            key_checks = {
                "包含内容描述": "测试内容描述" in folder_prompt,
                "包含文件夹列表": "产品展示" in folder_prompt,
                "包含分类标准": "分类" in folder_prompt or "归类" in folder_prompt
            }
            
            for check, passed in key_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}")
        else:
            print("❌ folder-matching提示词加载失败")
            
    except Exception as e:
        print(f"❌ 提示词测试失败: {e}")
    
    # 清理测试环境
    try:
        shutil.rmtree(test_dir)
        print(f"\n🧹 测试环境已清理")
    except Exception as e:
        print(f"\n⚠️ 清理失败: {e}")
    
    root.destroy()
    print("\n🎉 Gemini智能归类功能测试完成！")


def test_prompt_integration():
    """测试提示词集成"""
    print("\n🔗 测试提示词集成:")
    
    try:
        from prompts_manager import PromptsManager
        
        prompts_manager = PromptsManager()
        
        # 测试可用提示词列表
        available_prompts = prompts_manager.list_prompts()
        print(f"📋 可用提示词: {list(available_prompts.keys())}")
        
        # 测试video-analysis提示词
        video_prompt = prompts_manager.get_video_analysis_prompt()
        print(f"📄 video-analysis提示词长度: {len(video_prompt)} 字符")
        
        # 测试folder-matching提示词（原始版本）
        folder_config = prompts_manager.get_prompt('folder_matching')
        if folder_config:
            print(f"📄 folder-matching原始提示词长度: {len(folder_config.content)} 字符")
            print(f"📋 变量列表: {folder_config.variables}")
        
        print("✅ 提示词集成测试通过")
        
    except Exception as e:
        print(f"❌ 提示词集成测试失败: {e}")


if __name__ == "__main__":
    test_gemini_classification()
    test_prompt_integration()
