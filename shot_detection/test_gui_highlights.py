#!/usr/bin/env python3
"""
测试GUI中的高光时刻显示功能
模拟点击分析按钮的过程
"""

import tkinter as tk
import json
from pathlib import Path
import time


def test_gui_highlights():
    """测试GUI中的高光时刻功能"""
    print("🧪 测试GUI高光时刻显示功能")
    print("=" * 50)
    
    # 创建GUI实例
    from gui_app import ShotDetectionGUI
    
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    app = ShotDetectionGUI(root)
    
    # 模拟设置视频路径和输出目录
    app.analysis_video_path.set("test_video.mp4")
    app.analysis_output_dir.set("test_output")
    
    # 创建测试输出目录
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    print("📋 测试模拟分析功能...")
    
    # 直接调用模拟分析方法
    try:
        app._simulate_gemini_analysis("test_video.mp4", output_dir, "测试提示词")
        
        # 检查生成的结果文件
        result_files = list(output_dir.glob("*_gemini_analysis.json"))
        if result_files:
            result_file = result_files[0]
            print(f"✅ 找到结果文件: {result_file}")
            
            # 读取并检查结果
            with open(result_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            print("📊 检查结果结构:")
            
            # 检查是否包含高光时刻
            analysis_result = result.get('analysis_result', {})
            highlights = analysis_result.get('highlights', [])
            
            if highlights:
                print(f"✅ 包含 {len(highlights)} 个高光时刻:")
                for i, highlight in enumerate(highlights, 1):
                    timestamp = highlight.get('timestamp', '未知')
                    description = highlight.get('description', '无描述')
                    highlight_type = highlight.get('type', '未分类')
                    confidence = highlight.get('confidence', 0)
                    print(f"  {i}. [{timestamp}] {description} ({highlight_type}) [置信度: {confidence:.1%}]")
            else:
                print("❌ 未找到高光时刻")
            
            # 检查其他字段
            scenes = analysis_result.get('scenes', [])
            emotions = analysis_result.get('emotions', {})
            quality = analysis_result.get('quality', {})
            
            print(f"📋 场景数量: {len(scenes)}")
            print(f"😊 情感分析: {'有' if emotions else '无'}")
            print(f"📊 质量评估: {'有' if quality else '无'}")
            
            # 测试高光时刻提取
            print("\n🔍 测试高光时刻提取方法:")
            extracted_highlights = app._extract_highlights(result)
            print(f"✅ 提取到 {len(extracted_highlights)} 个高光时刻")
            
            # 保存测试结果
            test_summary = {
                "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "highlights_count": len(highlights),
                "extracted_highlights_count": len(extracted_highlights),
                "has_scenes": len(scenes) > 0,
                "has_emotions": bool(emotions),
                "has_quality": bool(quality),
                "test_passed": len(highlights) > 0
            }
            
            with open("gui_highlights_test_summary.json", 'w', encoding='utf-8') as f:
                json.dump(test_summary, f, ensure_ascii=False, indent=2)
            
            print(f"\n📊 测试总结:")
            print(f"  - 高光时刻: {test_summary['highlights_count']} 个")
            print(f"  - 提取成功: {test_summary['extracted_highlights_count']} 个")
            print(f"  - 测试结果: {'✅ 通过' if test_summary['test_passed'] else '❌ 失败'}")
            
        else:
            print("❌ 未找到结果文件")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        root.destroy()
    
    print("\n🎉 GUI高光时刻测试完成！")


def test_display_method():
    """测试显示方法"""
    print("\n🖥️ 测试显示方法...")
    
    # 模拟结果数据
    mock_result = {
        "video_info": {
            "file_name": "test.mp4",
            "model_used": "模拟分析器",
            "analysis_time": "2024-01-01 12:00:00"
        },
        "analysis_result": {
            "summary": "测试视频分析",
            "highlights": [
                {
                    "timestamp": "00:10",
                    "description": "测试高光时刻",
                    "type": "测试",
                    "confidence": 0.9
                }
            ]
        }
    }
    
    from gui_app import ShotDetectionGUI
    import tkinter as tk
    
    root = tk.Tk()
    root.withdraw()
    app = ShotDetectionGUI(root)
    
    try:
        # 测试高光提取
        highlights = app._extract_highlights(mock_result)
        print(f"✅ 显示方法提取到 {len(highlights)} 个高光时刻")
        
        if highlights:
            for highlight in highlights:
                print(f"  - [{highlight.get('timestamp')}] {highlight.get('description')}")
        
    except Exception as e:
        print(f"❌ 显示方法测试失败: {e}")
    
    finally:
        root.destroy()


if __name__ == "__main__":
    test_gui_highlights()
    test_display_method()
