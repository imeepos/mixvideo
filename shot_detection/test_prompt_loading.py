#!/usr/bin/env python3
"""
测试提示词是否正确从本地文件加载
"""

import os
from pathlib import Path


def test_prompt_loading():
    """测试提示词加载功能"""
    print("🧪 测试提示词加载功能")
    print("=" * 50)
    
    # 测试直接文件读取
    print("📁 测试直接文件读取:")
    prompt_file = Path("prompts/video-analysis.prompt")
    
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ 文件存在，大小: {len(content)} 字符")
        print(f"📄 文件路径: {prompt_file.absolute()}")
        
        # 检查关键内容
        key_checks = {
            "JSON格式要求": "```json" in content,
            "高光时刻字段": "highlights" in content,
            "时间戳要求": "timestamp" in content,
            "置信度要求": "confidence" in content,
            "分析深度要求": "分析深度要求" in content,
            "高光识别标准": "高光时刻识别标准" in content
        }
        
        print("\n📋 内容检查:")
        for check, passed in key_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
        
        # 显示前几行内容
        lines = content.split('\n')
        print(f"\n📝 文件前10行内容:")
        for i, line in enumerate(lines[:10], 1):
            print(f"  {i:2d}: {line}")
        
    else:
        print("❌ 提示词文件不存在")
        return False
    
    # 测试PromptsManager加载
    print(f"\n🔧 测试PromptsManager加载:")
    try:
        from prompts_manager import PromptsManager
        
        prompts_manager = PromptsManager()
        loaded_prompt = prompts_manager.get_video_analysis_prompt()
        
        if loaded_prompt:
            print(f"✅ PromptsManager加载成功，大小: {len(loaded_prompt)} 字符")
            
            # 比较内容是否一致
            if loaded_prompt.strip() == content.strip():
                print("✅ 加载内容与文件内容完全一致")
            else:
                print("⚠️ 加载内容与文件内容不一致")
                print(f"  文件内容长度: {len(content)}")
                print(f"  加载内容长度: {len(loaded_prompt)}")
                
                # 找出差异
                file_lines = content.strip().split('\n')
                loaded_lines = loaded_prompt.strip().split('\n')
                
                print(f"  文件行数: {len(file_lines)}")
                print(f"  加载行数: {len(loaded_lines)}")
                
                # 显示前几行差异
                max_lines = min(5, len(file_lines), len(loaded_lines))
                for i in range(max_lines):
                    if i < len(file_lines) and i < len(loaded_lines):
                        if file_lines[i] != loaded_lines[i]:
                            print(f"  差异行 {i+1}:")
                            print(f"    文件: {file_lines[i][:50]}...")
                            print(f"    加载: {loaded_lines[i][:50]}...")
            
            # 检查关键内容
            loaded_checks = {
                "JSON格式要求": "```json" in loaded_prompt,
                "高光时刻字段": "highlights" in loaded_prompt,
                "时间戳要求": "timestamp" in loaded_prompt,
                "置信度要求": "confidence" in loaded_prompt
            }
            
            print("\n📋 加载内容检查:")
            for check, passed in loaded_checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}")
                
        else:
            print("❌ PromptsManager加载失败，返回空内容")
            return False
            
    except Exception as e:
        print(f"❌ PromptsManager测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试GUI中的使用
    print(f"\n🖥️ 测试GUI中的使用:")
    try:
        import tkinter as tk
        from gui_app import ShotDetectionGUI
        
        root = tk.Tk()
        root.withdraw()
        app = ShotDetectionGUI(root)
        
        # 模拟获取提示词的过程
        try:
            from prompts_manager import PromptsManager
            prompts_manager = PromptsManager()
            gui_prompt = prompts_manager.get_video_analysis_prompt()
            
            if gui_prompt:
                print(f"✅ GUI中提示词加载成功，大小: {len(gui_prompt)} 字符")
                
                # 检查是否包含高光时刻相关内容
                if "highlights" in gui_prompt and "confidence" in gui_prompt:
                    print("✅ GUI加载的提示词包含高光时刻相关内容")
                else:
                    print("❌ GUI加载的提示词缺少高光时刻相关内容")
            else:
                print("❌ GUI中提示词加载失败")
                
        except Exception as e:
            print(f"❌ GUI提示词测试失败: {e}")
        
        root.destroy()
        
    except Exception as e:
        print(f"❌ GUI测试失败: {e}")
    
    print("\n🎉 提示词加载测试完成！")
    return True


def test_prompt_modification():
    """测试提示词修改是否生效"""
    print("\n🔄 测试提示词修改生效:")
    
    # 在提示词末尾添加测试标记
    test_marker = "\n# 测试标记 - 本地修改生效验证"
    prompt_file = Path("prompts/video-analysis.prompt")
    
    try:
        # 读取原始内容
        with open(prompt_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 添加测试标记
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(original_content + test_marker)
        
        print("✅ 已添加测试标记到提示词文件")
        
        # 重新加载并检查
        from prompts_manager import PromptsManager
        prompts_manager = PromptsManager()
        modified_prompt = prompts_manager.get_video_analysis_prompt()
        
        if test_marker in modified_prompt:
            print("✅ 提示词修改生效！本地文件修改已被正确加载")
        else:
            print("❌ 提示词修改未生效，可能存在缓存或其他问题")
        
        # 恢复原始内容
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        print("✅ 已恢复原始提示词内容")
        
    except Exception as e:
        print(f"❌ 提示词修改测试失败: {e}")


if __name__ == "__main__":
    test_prompt_loading()
    test_prompt_modification()
