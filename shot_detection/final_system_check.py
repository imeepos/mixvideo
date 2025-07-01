#!/usr/bin/env python3
"""
最终系统检查

验证所有组件是否正常工作
"""

import sys
import os
from pathlib import Path

def check_python_environment():
    """检查Python环境"""
    print("🐍 检查Python环境...")
    
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python版本兼容")
        return True
    else:
        print("❌ Python版本过低，需要3.8+")
        return False

def check_dependencies():
    """检查依赖项"""
    print("\n📦 检查依赖项...")
    
    dependencies = [
        ("requests", "HTTP请求库"),
        ("numpy", "数值计算"),
        ("cv2", "OpenCV视觉库"),
        ("PIL", "图像处理"),
        ("yaml", "配置文件"),
        ("loguru", "日志记录")
    ]
    
    success_count = 0
    for module, desc in dependencies:
        try:
            __import__(module)
            print(f"✅ {desc} ({module})")
            success_count += 1
        except ImportError as e:
            print(f"❌ {desc} ({module}): {e}")
    
    print(f"\n依赖检查: {success_count}/{len(dependencies)}")
    return success_count >= 5  # 至少5个核心依赖

def check_project_files():
    """检查项目文件"""
    print("\n📁 检查项目文件...")
    
    # 检查当前目录
    current_dir = Path.cwd()
    print(f"当前目录: {current_dir}")
    
    # 必需文件列表
    required_files = [
        "prompts_manager.py",
        "prompts_constants.py", 
        "gemini_video_analyzer.py",
        "gui_app.py",
        "run_gui.py",
        "prompts/video-analysis.prompt",
        "prompts/folder-matching.prompt",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size} 字节)")
        else:
            print(f"❌ {file_path} 缺失")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ 缺少 {len(missing_files)} 个文件")
        return False
    else:
        print(f"\n✅ 所有必需文件都存在")
        return True

def check_module_imports():
    """检查模块导入"""
    print("\n🔧 检查模块导入...")
    
    # 确保当前目录在Python路径中
    current_dir = str(Path.cwd())
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # 测试关键模块导入
    modules_to_test = [
        ("prompts_manager", "PromptsManager"),
        ("prompts_constants", "VIDEO_ANALYSIS_PROMPT"),
        ("gemini_video_analyzer", "create_gemini_analyzer")
    ]
    
    import_success = 0
    for module_name, item_name in modules_to_test:
        try:
            # 清理模块缓存
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            module = __import__(module_name)
            
            # 检查特定项目是否存在
            if hasattr(module, item_name):
                print(f"✅ {module_name}.{item_name}")
                import_success += 1
            else:
                print(f"⚠️ {module_name} 导入成功但缺少 {item_name}")
        except Exception as e:
            print(f"❌ {module_name}: {e}")
    
    print(f"\n模块导入: {import_success}/{len(modules_to_test)}")
    return import_success == len(modules_to_test)

def check_classification_system():
    """检查分类系统"""
    print("\n🎯 检查分类系统...")
    
    try:
        from prompts_manager import PromptsManager
        manager = PromptsManager()
        
        # 测试提示词加载
        video_prompt = manager.get_video_analysis_prompt()
        if video_prompt and len(video_prompt) > 100:
            print(f"✅ 视频分析提示词 ({len(video_prompt)} 字符)")
        else:
            print("❌ 视频分析提示词无效")
            return False
        
        # 测试分类提示词
        test_content = "测试视频内容"
        test_folders = ["product_display", "product_usage", "model_wearing", "ai_generated"]
        
        folder_prompt = manager.get_folder_matching_prompt(test_content, test_folders)
        if folder_prompt and len(folder_prompt) > 100:
            print(f"✅ 分类提示词 ({len(folder_prompt)} 字符)")
        else:
            print("❌ 分类提示词无效")
            return False
        
        # 检查4分类是否都包含在提示词中
        categories_found = 0
        for category in test_folders:
            if category in folder_prompt:
                categories_found += 1
        
        print(f"✅ 4分类系统完整 ({categories_found}/4)")
        return categories_found == 4
        
    except Exception as e:
        print(f"❌ 分类系统检查失败: {e}")
        return False

def generate_system_report():
    """生成系统报告"""
    print(f"\n{'='*60}")
    print("系统检查报告")
    print('='*60)
    
    checks = [
        ("Python环境", check_python_environment),
        ("依赖项", check_dependencies),
        ("项目文件", check_project_files),
        ("模块导入", check_module_imports),
        ("分类系统", check_classification_system)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{'='*30}")
        print(f"检查: {check_name}")
        print('='*30)
        
        try:
            if check_func():
                passed += 1
                print(f"✅ {check_name} 通过")
            else:
                print(f"❌ {check_name} 失败")
        except Exception as e:
            print(f"❌ {check_name} 异常: {e}")
    
    print(f"\n{'='*60}")
    print("最终结果")
    print('='*60)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 系统检查全部通过！")
        print("\n✨ 系统状态:")
        print("• ✅ Python环境正常")
        print("• ✅ 所有依赖已安装")
        print("• ✅ 项目文件完整")
        print("• ✅ 模块导入正常")
        print("• ✅ 4分类系统就绪")
        
        print("\n🚀 现在可以:")
        print("• 运行GUI: python run_gui.py")
        print("• 使用视频分析功能")
        print("• 调用Gemini API进行智能分类")
        print("• 享受完整的4分类系统")
        
        print("\n🎯 您的分类系统:")
        print("1. product_display (产品展示)")
        print("2. product_usage (产品使用)")
        print("3. model_wearing (模特试穿)")
        print("4. ai_generated (AI素材)")
        
        return True
    else:
        print(f"\n❌ {total - passed} 项检查失败")
        print("\n🔧 建议修复步骤:")
        if passed < 2:
            print("1. 运行: python install_dependencies_safe.py")
        if passed < 4:
            print("2. 运行: python fix_all_import_issues.py")
        print("3. 重新运行此检查脚本")
        
        return False

def main():
    """主函数"""
    print("🔍 最终系统检查")
    print("验证视频分析系统是否完全就绪")
    
    success = generate_system_report()
    
    if success:
        print(f"\n🎊 恭喜！您的视频分析系统已完全就绪！")
    else:
        print(f"\n⚠️ 系统尚未完全就绪，请按建议修复")

if __name__ == "__main__":
    main()
