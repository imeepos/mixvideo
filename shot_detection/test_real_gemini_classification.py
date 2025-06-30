#!/usr/bin/env python3
"""
测试真实的Gemini智能归类功能
"""

import tkinter as tk
from pathlib import Path
import json


def test_real_gemini_classification():
    """测试真实的Gemini智能归类功能"""
    print("🤖 测试真实Gemini智能归类功能")
    print("=" * 50)
    
    # 创建GUI实例
    root = tk.Tk()
    root.withdraw()
    
    from gui_app import ShotDetectionGUI
    app = ShotDetectionGUI(root)
    
    # 测试不同类型的视频内容描述
    test_cases = [
        {
            "name": "产品展示视频",
            "content_description": """内容摘要: 这是一个白底背景下的女装产品展示视频，展示了一件红色连衣裙的细节特写
高光时刻数量: 1个, 类型: 视觉
检测物体: 展示台, 连衣裙, 白色背景
主要动作: 静态展示, 旋转
整体情感: 专业展示
视频质量: 9/10
技术参数: 4K分辨率, 固定镜头"""
        },
        {
            "name": "模特试穿视频", 
            "content_description": """内容摘要: 模特试穿展示视频，展现了服装的穿着效果和动态美感
高光时刻数量: 2个, 类型: 动作
检测物体: T台, 服装, 模特
主要动作: 走位, 转身, 试穿
整体情感: 优雅时尚
视频质量: 8/10
技术参数: 1080p分辨率, 跟拍镜头"""
        },
        {
            "name": "优质高光视频",
            "content_description": """内容摘要: 包含多个精彩高光时刻的优质视频内容
高光时刻数量: 4个, 类型: 动作, 情感, 转场, 视觉
检测物体: 产品, 场景, 模特
主要动作: 互动, 展示, 表演
整体情感: 活力四射
视频质量: 9/10
技术参数: 4K分辨率, 多角度拍摄"""
        },
        {
            "name": "穿搭教程视频",
            "content_description": """内容摘要: 本视频为男性提供了五大穿衣口诀，旨在帮助他们提升穿搭品味和个人形象。内容涵盖了从服装版型、色彩搭配到裤装选择的实用建议。
高光时刻数量: 18个, 类型: 视觉, 转场, 动作
检测物体: 服装, 模特, 文字标题
主要动作: 展示, 对比, 说明
整体情感: 教育性, 实用性
视频质量: 9/10
技术参数: 高清分辨率, 多场景切换"""
        }
    ]
    
    print("📋 测试真实Gemini归类:")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case['name']}")
        print("-" * 30)
        
        try:
            # 构建完整的提示词
            from prompts_manager import PromptsManager
            prompts_manager = PromptsManager()
            
            # 定义可用的文件夹列表
            folder_list = [
                "product_display (产品展示)",
                "product_usage (产品使用)", 
                "model_wearing (模特试穿)",
                "ai_generated (AI素材)",
                "premium_highlights (优质高光)",
                "good_highlights (良好高光)",
                "elegant_style (优雅风格)",
                "active_style (活泼风格)",
                "standard (标准分类)"
            ]
            
            # 获取格式化的提示词
            folder_matching_prompt = prompts_manager.get_folder_matching_prompt(
                test_case['content_description'], 
                folder_list
            )
            
            # 添加JSON格式要求
            full_prompt = folder_matching_prompt + """

请以JSON格式返回归类结果：
```json
{
  "category": "推荐的文件夹名称",
  "confidence": 0.95,
  "reason": "归类原因说明",
  "quality_level": "S级/A级/B级",
  "features": ["关键特征1", "关键特征2"],
  "recommendations": "优化建议"
}
```

请从以下文件夹中选择最合适的：
- product_display (产品展示)
- product_usage (产品使用)
- model_wearing (模特试穿)
- ai_generated (AI素材)
- premium_highlights (优质高光)
- good_highlights (良好高光)
- elegant_style (优雅风格)
- active_style (活泼风格)
- standard (标准分类)
"""
            
            print(f"📝 提示词长度: {len(full_prompt)} 字符")
            
            # 调用真实的Gemini归类
            print(f"🤖 调用真实Gemini API...")
            classification_result = app._call_gemini_for_classification(full_prompt)
            
            if classification_result:
                category = classification_result.get('category', 'unknown')
                confidence = classification_result.get('confidence', 0)
                reason = classification_result.get('reason', '无原因')
                quality_level = classification_result.get('quality_level', '未知')
                features = classification_result.get('features', [])
                recommendations = classification_result.get('recommendations', '无建议')
                
                print(f"✅ Gemini归类成功!")
                print(f"  🎯 归类结果: {category}")
                print(f"  📊 置信度: {confidence:.1%}")
                print(f"  💭 归类原因: {reason}")
                print(f"  🏆 质量等级: {quality_level}")
                print(f"  🔍 关键特征: {', '.join(features)}")
                print(f"  💡 建议: {recommendations}")
                
                # 保存结果
                result_file = f"gemini_classification_result_{i}.json"
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "test_case": test_case,
                        "classification_result": classification_result,
                        "prompt_used": full_prompt
                    }, f, ensure_ascii=False, indent=2)
                
                print(f"  💾 结果已保存: {result_file}")
                
            else:
                print(f"❌ Gemini归类失败")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    root.destroy()
    print("\n🎉 真实Gemini归类功能测试完成！")


def test_prompt_construction():
    """测试提示词构建"""
    print(f"\n📝 测试提示词构建")
    print("=" * 20)
    
    try:
        from prompts_manager import PromptsManager
        
        prompts_manager = PromptsManager()
        
        # 测试内容描述
        test_content = "这是一个测试视频，包含产品展示和模特试穿的内容"
        
        # 测试文件夹列表
        test_folders = ["产品展示", "模特试穿", "使用场景"]
        
        # 获取格式化提示词
        formatted_prompt = prompts_manager.get_folder_matching_prompt(test_content, test_folders)
        
        print(f"✅ 提示词构建成功")
        print(f"📊 提示词长度: {len(formatted_prompt)} 字符")
        print(f"📄 包含内容描述: {'测试视频' in formatted_prompt}")
        print(f"📄 包含文件夹列表: {'产品展示' in formatted_prompt}")
        
        # 保存提示词示例
        with open("prompt_example.txt", 'w', encoding='utf-8') as f:
            f.write(formatted_prompt)
        
        print(f"💾 提示词示例已保存: prompt_example.txt")
        
    except Exception as e:
        print(f"❌ 提示词构建测试失败: {e}")


def main():
    """主测试函数"""
    print("🧪 真实Gemini智能归类测试套件")
    print("=" * 60)
    
    try:
        # 测试提示词构建
        test_prompt_construction()
        
        # 测试真实Gemini归类
        test_real_gemini_classification()
        
        print(f"\n🎯 测试完成")
        print(f"📋 检查生成的文件:")
        print(f"  - gemini_classification_result_*.json (归类结果)")
        print(f"  - prompt_example.txt (提示词示例)")
        
    except Exception as e:
        print(f"❌ 测试套件失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
