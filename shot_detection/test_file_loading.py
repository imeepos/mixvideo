#!/usr/bin/env python3
"""
测试提示词文件加载功能
验证从本地文件加载提示词是否正常工作
"""

from prompts_manager import PromptsManager
from prompts_constants import get_video_analysis_prompt, get_folder_matching_prompt


def test_file_loading():
    """测试文件加载功能"""
    print("🧪 测试提示词文件加载功能")
    print("=" * 50)
    
    # 1. 测试管理器从文件加载
    print("\n1. 📁 测试管理器从文件加载:")
    manager = PromptsManager()
    
    # 检查是否成功加载了提示词
    video_config = manager.get_prompt('video_analysis')
    folder_config = manager.get_prompt('folder_matching')
    
    if video_config:
        print(f"   ✅ 视频分析提示词加载成功")
        print(f"      - 长度: {len(video_config.content)} 字符")
        print(f"      - 前50字符: {video_config.content[:50]}...")
    else:
        print(f"   ❌ 视频分析提示词加载失败")
    
    if folder_config:
        print(f"   ✅ 文件夹匹配提示词加载成功")
        print(f"      - 长度: {len(folder_config.content)} 字符")
        print(f"      - 前50字符: {folder_config.content[:50]}...")
        print(f"      - 变量: {folder_config.variables}")
    else:
        print(f"   ❌ 文件夹匹配提示词加载失败")
    
    # 2. 测试常量模块（仍使用写死的内容）
    print("\n2. 📄 测试常量模块:")
    const_video_prompt = get_video_analysis_prompt()
    print(f"   • 常量模块视频提示词长度: {len(const_video_prompt)} 字符")
    
    test_folders = ["产品展示", "模特试穿", "使用场景"]
    const_folder_prompt = get_folder_matching_prompt("测试描述", test_folders)
    print(f"   • 常量模块文件夹提示词长度: {len(const_folder_prompt)} 字符")
    
    # 3. 比较两种方式的内容
    print("\n3. 🔍 比较文件加载 vs 常量模块:")
    if video_config:
        file_content = video_config.content
        const_content = const_video_prompt
        
        print(f"   • 文件加载长度: {len(file_content)} 字符")
        print(f"   • 常量模块长度: {len(const_content)} 字符")
        
        if file_content.strip() == const_content.strip():
            print(f"   ✅ 内容完全一致")
        else:
            print(f"   ⚠️  内容不一致 - 这是正常的，因为文件内容可能已更新")
    
    # 4. 测试文件夹匹配的变量替换
    print("\n4. 🔧 测试文件夹匹配变量替换:")
    if folder_config:
        test_description = "女装连衣裙产品展示视频"
        test_folders = ["产品展示", "模特试穿", "使用场景", "AI素材"]
        
        formatted_prompt = manager.get_folder_matching_prompt(test_description, test_folders)
        
        print(f"   • 原始模板长度: {len(folder_config.content)} 字符")
        print(f"   • 格式化后长度: {len(formatted_prompt)} 字符")
        
        # 检查变量是否被正确替换
        if "{contentDescription}" not in formatted_prompt and "{folderList}" not in formatted_prompt:
            print(f"   ✅ 变量替换成功")
        else:
            print(f"   ❌ 变量替换失败")
        
        # 检查是否包含测试内容
        if test_description in formatted_prompt:
            print(f"   ✅ 内容描述已插入")
        else:
            print(f"   ❌ 内容描述未插入")
        
        if "产品展示" in formatted_prompt:
            print(f"   ✅ 文件夹列表已插入")
        else:
            print(f"   ❌ 文件夹列表未插入")
    
    # 5. 测试重新加载功能
    print("\n5. 🔄 测试重新加载功能:")
    try:
        manager.reload_prompts()
        print(f"   ✅ 重新加载成功")
        
        # 验证重新加载后的内容
        reloaded_config = manager.get_prompt('video_analysis')
        if reloaded_config:
            print(f"   ✅ 重新加载后视频分析提示词仍可用")
        else:
            print(f"   ❌ 重新加载后视频分析提示词不可用")
            
    except Exception as e:
        print(f"   ❌ 重新加载失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")


def test_file_existence():
    """测试提示词文件是否存在"""
    print("\n📂 检查提示词文件是否存在:")
    
    from pathlib import Path
    
    prompts_dir = Path(__file__).parent / "prompts"
    
    files_to_check = [
        "video-analysis.prompt",
        "folder-matching.prompt"
    ]
    
    for filename in files_to_check:
        file_path = prompts_dir / filename
        if file_path.exists():
            print(f"   ✅ {filename} 存在 ({file_path.stat().st_size} 字节)")
        else:
            print(f"   ❌ {filename} 不存在")


if __name__ == "__main__":
    test_file_existence()
    test_file_loading()
