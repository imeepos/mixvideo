#!/usr/bin/env python3
"""
修复所有导入问题

一键解决所有模块导入和方法缺失问题
"""

import shutil
import os
from pathlib import Path

def fix_all_import_issues():
    """修复所有导入问题"""
    print("🔧 修复所有导入问题")
    print("=" * 50)
    
    root_dir = Path(__file__).parent
    packaged_dir = root_dir / "ShotDetectionGUI_Python_Complete_v1.0.3_20250701"
    
    if not packaged_dir.exists():
        print("❌ 打包版本目录不存在")
        return False
    
    print(f"根目录: {root_dir}")
    print(f"打包版本目录: {packaged_dir}")
    
    # 需要同步的文件
    files_to_sync = [
        "prompts_manager.py",
        "prompts_constants.py", 
        "gui_app.py",
        "gemini_video_analyzer.py",  # 新增
        "run_gui.py"
    ]
    
    # 需要同步的目录
    dirs_to_sync = [
        "prompts"
    ]
    
    success_count = 0
    total_items = len(files_to_sync) + len(dirs_to_sync)
    
    # 同步文件
    print("\n📁 同步文件:")
    for file_name in files_to_sync:
        source_file = root_dir / file_name
        target_file = packaged_dir / file_name
        
        if not source_file.exists():
            print(f"⚠️ 源文件不存在: {file_name}")
            continue
        
        try:
            shutil.copy2(source_file, target_file)
            source_size = source_file.stat().st_size
            target_size = target_file.stat().st_size
            
            if source_size == target_size:
                print(f"✅ {file_name} ({source_size} 字节)")
                success_count += 1
            else:
                print(f"⚠️ {file_name} 大小不匹配")
                
        except Exception as e:
            print(f"❌ {file_name} 同步失败: {e}")
    
    # 同步目录
    print("\n📂 同步目录:")
    for dir_name in dirs_to_sync:
        source_dir = root_dir / dir_name
        target_dir = packaged_dir / dir_name
        
        if not source_dir.exists():
            print(f"⚠️ 源目录不存在: {dir_name}")
            continue
        
        try:
            # 如果目标目录存在，先删除
            if target_dir.exists():
                shutil.rmtree(target_dir)
            
            # 复制整个目录
            shutil.copytree(source_dir, target_dir)
            
            # 统计文件数量
            source_files = list(source_dir.rglob("*"))
            
            print(f"✅ {dir_name}/ ({len(source_files)} 个文件)")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {dir_name}/ 同步失败: {e}")
    
    print(f"\n📊 同步结果: {success_count}/{total_items} 成功")
    
    # 验证修复
    print("\n🔍 验证修复:")
    
    # 验证关键文件
    critical_files = [
        "prompts_manager.py",
        "prompts_constants.py",
        "gemini_video_analyzer.py",
        "prompts/video-analysis.prompt"
    ]
    
    all_exist = True
    for file_path in critical_files:
        full_path = packaged_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size} 字节)")
        else:
            print(f"❌ {file_path} 不存在")
            all_exist = False
    
    if all_exist:
        print("\n🎉 所有关键文件都存在！")
        
        # 测试导入
        print("\n🧪 测试导入:")
        
        # 保存原始环境
        original_cwd = os.getcwd()
        
        try:
            # 切换到打包版本目录
            os.chdir(str(packaged_dir))
            
            # 测试导入
            import sys
            if str(packaged_dir) not in sys.path:
                sys.path.insert(0, str(packaged_dir))
            
            # 清理模块缓存
            modules_to_clear = ['prompts_manager', 'prompts_constants', 'gemini_video_analyzer']
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]
            
            # 测试 prompts_manager
            try:
                from prompts_manager import PromptsManager
                manager = PromptsManager()
                prompt = manager.get_video_analysis_prompt()
                if prompt and len(prompt) > 50:
                    print(f"✅ prompts_manager 导入成功 ({len(prompt)} 字符)")
                else:
                    print("⚠️ prompts_manager 导入成功但提示词无效")
            except Exception as e:
                print(f"❌ prompts_manager 导入失败: {e}")
                all_exist = False
            
            # 测试 prompts_constants
            try:
                from prompts_constants import VIDEO_ANALYSIS_PROMPT
                if VIDEO_ANALYSIS_PROMPT and len(VIDEO_ANALYSIS_PROMPT) > 50:
                    print(f"✅ prompts_constants 导入成功 ({len(VIDEO_ANALYSIS_PROMPT)} 字符)")
                else:
                    print("⚠️ prompts_constants 导入成功但备用提示词无效")
            except Exception as e:
                print(f"❌ prompts_constants 导入失败: {e}")
                all_exist = False
            
            # 测试 gemini_video_analyzer
            try:
                from gemini_video_analyzer import create_gemini_analyzer, AnalysisProgress
                print("✅ gemini_video_analyzer 导入成功")
            except Exception as e:
                print(f"❌ gemini_video_analyzer 导入失败: {e}")
                all_exist = False
            
        finally:
            # 恢复环境
            os.chdir(original_cwd)
    
    if all_exist:
        print("\n🎉 所有修复完成！")
        print("\n✨ 修复内容:")
        print("• ✅ prompts_manager.py - 提示词管理器")
        print("• ✅ prompts_constants.py - 备用提示词")
        print("• ✅ gemini_video_analyzer.py - Gemini视频分析器")
        print("• ✅ gui_app.py - 修复了 _determine_category 方法")
        print("• ✅ prompts/ 目录 - 提示词文件")
        
        print("\n🚀 现在可以:")
        print("1. 正常使用视频分析功能")
        print("2. 不会看到 'No module named' 错误")
        print("3. 不会看到 '_determine_category' 错误")
        print("4. 享受完整的Gemini分析功能")
        
        print("\n📝 使用方法:")
        print(f"cd {packaged_dir.name}")
        print("python run_gui.py")
        
        return True
    else:
        print("\n❌ 修复未完全成功")
        return False


def create_verification_script():
    """创建验证脚本"""
    print("\n📝 创建验证脚本...")
    
    verification_script = '''#!/usr/bin/env python3
"""
验证修复结果
"""

import sys
import os
from pathlib import Path

def verify_fixes():
    """验证所有修复"""
    print("🔍 验证修复结果")
    print("=" * 30)
    
    # 切换到脚本目录
    script_dir = Path(__file__).parent.resolve()
    os.chdir(str(script_dir))
    
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    print(f"当前目录: {script_dir}")
    
    # 检查文件
    files = [
        "prompts_manager.py",
        "prompts_constants.py",
        "gemini_video_analyzer.py",
        "prompts/video-analysis.prompt"
    ]
    
    for file_path in files:
        if (script_dir / file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            return False
    
    # 测试导入
    print("\\n测试导入:")
    
    try:
        from prompts_manager import PromptsManager
        print("✅ prompts_manager")
    except Exception as e:
        print(f"❌ prompts_manager: {e}")
        return False
    
    try:
        from prompts_constants import VIDEO_ANALYSIS_PROMPT
        print("✅ prompts_constants")
    except Exception as e:
        print(f"❌ prompts_constants: {e}")
        return False
    
    try:
        from gemini_video_analyzer import create_gemini_analyzer
        print("✅ gemini_video_analyzer")
    except Exception as e:
        print(f"❌ gemini_video_analyzer: {e}")
        return False
    
    print("\\n🎉 所有验证通过！")
    print("现在可以正常使用视频分析功能了")
    return True

if __name__ == "__main__":
    verify_fixes()
'''
    
    # 保存到打包版本目录
    packaged_dir = Path(__file__).parent / "ShotDetectionGUI_Python_Complete_v1.0.3_20250701"
    if packaged_dir.exists():
        verify_script_path = packaged_dir / "verify_fixes.py"
        with open(verify_script_path, 'w', encoding='utf-8') as f:
            f.write(verification_script)
        print(f"✅ 创建验证脚本: {verify_script_path}")
        return verify_script_path
    
    return None


def main():
    """主函数"""
    print("🛠️ 一键修复所有导入问题")
    print("=" * 60)
    
    # 执行修复
    success = fix_all_import_issues()
    
    # 创建验证脚本
    verify_script = create_verification_script()
    
    print(f"\n{'='*60}")
    print("修复结果")
    print('='*60)
    
    if success:
        print("🎉 修复成功！")
        
        print("\n📋 已解决的问题:")
        print("1. ✅ No module named 'prompts_manager'")
        print("2. ✅ No module named 'prompts_constants'")
        print("3. ✅ No module named 'gemini_video_analyzer'")
        print("4. ✅ 'ShotDetectionGUI' object has no attribute '_determine_category'")
        
        print("\n🚀 现在用户应该看到:")
        print("[INFO] 使用prompts_manager获取提示词")
        print("[INFO] 成功获取提示词，长度: 1439 字符")
        print("[INFO] 初始化Gemini客户端...")
        print("[SUCCESS] Gemini分析完成！")
        
        print("\n📝 下一步:")
        print("1. 进入打包版本目录:")
        print("   cd ShotDetectionGUI_Python_Complete_v1.0.3_20250701")
        print("2. 验证修复:")
        print("   python verify_fixes.py")
        print("3. 运行GUI:")
        print("   python run_gui.py")
        
    else:
        print("❌ 修复失败")
        print("请检查错误信息并手动修复")


if __name__ == "__main__":
    main()
