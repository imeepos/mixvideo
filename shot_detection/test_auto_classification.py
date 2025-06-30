#!/usr/bin/env python3
"""
测试自动归类和优化的GUI显示功能
"""

import json
import tkinter as tk
from pathlib import Path
import shutil


def test_auto_classification():
    """测试自动归类功能"""
    print("🧪 测试自动归类功能")
    print("=" * 50)
    
    # 创建测试环境
    test_dir = Path("test_classification")
    test_dir.mkdir(exist_ok=True)
    
    # 创建测试视频文件（空文件用于测试）
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
            "name": "优质高光视频",
            "result": {
                "analysis_result": {
                    "summary": "这是一个包含多个精彩高光时刻的优质视频",
                    "highlights": [
                        {"timestamp": "00:05", "description": "精彩转身", "type": "动作", "confidence": 0.95},
                        {"timestamp": "00:15", "description": "完美特写", "type": "视觉", "confidence": 0.92},
                        {"timestamp": "00:25", "description": "情感爆发", "type": "情感", "confidence": 0.88}
                    ],
                    "quality": {"video_quality": 9},
                    "emotions": {"overall_mood": "优雅专业"},
                    "technical": {"resolution": "1080p"}
                }
            },
            "expected_category": "premium_highlights"
        },
        {
            "name": "良好高光视频", 
            "result": {
                "analysis_result": {
                    "summary": "包含一些不错的展示瞬间",
                    "highlights": [
                        {"timestamp": "00:10", "description": "产品展示", "type": "视觉", "confidence": 0.85},
                        {"timestamp": "00:20", "description": "动作展示", "type": "动作", "confidence": 0.80}
                    ],
                    "quality": {"video_quality": 7},
                    "emotions": {"overall_mood": "活泼"},
                    "technical": {"resolution": "720p"}
                }
            },
            "expected_category": "good_highlights"
        },
        {
            "name": "优雅风格视频",
            "result": {
                "analysis_result": {
                    "summary": "展现优雅气质的视频",
                    "highlights": [],
                    "quality": {"video_quality": 6},
                    "emotions": {"overall_mood": "优雅专业"},
                    "technical": {"resolution": "1080p"}
                }
            },
            "expected_category": "elegant_style"
        },
        {
            "name": "标准视频",
            "result": {
                "analysis_result": {
                    "summary": "普通的视频内容",
                    "highlights": [],
                    "quality": {"video_quality": 5},
                    "emotions": {"overall_mood": "普通"},
                    "technical": {"resolution": "720p"}
                }
            },
            "expected_category": "standard"
        }
    ]
    
    print("📋 测试归类逻辑:")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case['name']}")
        
        # 测试归类逻辑
        category = app._determine_category(test_case['result']['analysis_result'])
        expected = test_case['expected_category']
        
        if category == expected:
            print(f"   ✅ 归类正确: {category}")
        else:
            print(f"   ❌ 归类错误: 期望 {expected}, 实际 {category}")
        
        # 测试文件名生成
        filename = app._generate_classified_filename(test_video, test_case['result']['analysis_result'])
        print(f"   📝 生成文件名: {filename}")
        
        # 测试完整归类流程
        try:
            app._auto_classify_video(str(test_video), test_case['result'])
            
            # 检查归类结果
            classified_dir = output_dir / "classified" / category
            if classified_dir.exists():
                files = list(classified_dir.glob("*.mp4"))
                if files:
                    print(f"   ✅ 文件已归类到: {classified_dir.name}")
                    
                    # 检查归类信息文件
                    info_files = list(classified_dir.glob("*.classification.json"))
                    if info_files:
                        print(f"   📄 归类信息已保存")
                    else:
                        print(f"   ⚠️ 归类信息文件缺失")
                else:
                    print(f"   ❌ 归类文件不存在")
            else:
                print(f"   ❌ 归类目录不存在")
                
        except Exception as e:
            print(f"   ❌ 归类测试失败: {e}")
    
    # 清理测试环境
    try:
        shutil.rmtree(test_dir)
        print(f"\n🧹 测试环境已清理")
    except Exception as e:
        print(f"\n⚠️ 清理失败: {e}")
    
    root.destroy()
    print("\n🎉 自动归类功能测试完成！")


def test_gui_display():
    """测试GUI显示优化"""
    print("\n🖥️ 测试GUI显示优化")
    print("=" * 30)
    
    # 模拟分析结果
    mock_result = {
        "video_info": {
            "file_name": "test_video.mp4",
            "model_used": "模拟分析器",
            "analysis_time": "2024-01-01 12:00:00"
        },
        "analysis_result": {
            "summary": "这是一个展示女装搭配的精彩视频，包含多个高光时刻和优质内容。",
            "highlights": [
                {
                    "timestamp": "00:05",
                    "description": "模特优雅转身展示裙装",
                    "type": "动作",
                    "confidence": 0.95
                },
                {
                    "timestamp": "00:18", 
                    "description": "面料质感特写镜头",
                    "type": "视觉",
                    "confidence": 0.88
                }
            ],
            "quality": {
                "video_quality": 8,
                "lighting": "自然光线充足"
            },
            "emotions": {
                "overall_mood": "优雅时尚"
            }
        }
    }
    
    # 创建GUI实例
    from gui_app import ShotDetectionGUI
    
    root = tk.Tk()
    root.withdraw()
    app = ShotDetectionGUI(root)
    
    try:
        # 测试归类逻辑
        category = app._determine_category(mock_result['analysis_result'])
        print(f"📁 归类结果: {category}")
        
        # 测试高光提取
        highlights = app._extract_highlights(mock_result)
        print(f"✨ 提取高光: {len(highlights)} 个")
        
        # 测试文件名生成
        test_file = Path("test.mp4")
        filename = app._generate_classified_filename(test_file, mock_result['analysis_result'])
        print(f"📝 生成文件名: {filename}")
        
        print("✅ GUI显示功能测试通过")
        
    except Exception as e:
        print(f"❌ GUI显示测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        root.destroy()


if __name__ == "__main__":
    test_auto_classification()
    test_gui_display()
