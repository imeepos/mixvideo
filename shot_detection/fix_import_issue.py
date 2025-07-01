#!/usr/bin/env python3
"""
自动修复导入问题
"""

import sys
import os
import shutil
from pathlib import Path

def fix_import_issue():
    """自动修复导入问题"""
    print("🔧 自动修复 prompts_manager 导入问题")
    
    current_dir = Path.cwd()
    
    # 查找打包版本目录
    packaged_dirs = [
        "ShotDetectionGUI_Python_Complete_v1.0.3_20250701",
        "ShotDetectionGUI_Python_Complete_v1.0.3_20250630",
        "ShotDetectionGUI_Python_Complete_v1.0.3_20250629"
    ]
    
    source_dir = None
    for dir_name in packaged_dirs:
        packaged_dir = current_dir / dir_name
        if packaged_dir.exists():
            source_dir = packaged_dir
            break
    
    if not source_dir:
        print("❌ 未找到打包版本目录")
        return False
    
    print(f"✅ 找到源目录: {source_dir}")
    
    # 复制必需文件
    files_to_copy = [
        "prompts_manager.py",
        "prompts_constants.py"
    ]
    
    dirs_to_copy = [
        "prompts"
    ]
    
    success_count = 0
    
    # 复制文件
    for file_name in files_to_copy:
        source_file = source_dir / file_name
        target_file = current_dir / file_name
        
        if source_file.exists():
            try:
                shutil.copy2(source_file, target_file)
                print(f"✅ 复制 {file_name}")
                success_count += 1
            except Exception as e:
                print(f"❌ 复制 {file_name} 失败: {e}")
        else:
            print(f"⚠️ 源文件不存在: {file_name}")
    
    # 复制目录
    for dir_name in dirs_to_copy:
        source_dir_path = source_dir / dir_name
        target_dir_path = current_dir / dir_name
        
        if source_dir_path.exists():
            try:
                if target_dir_path.exists():
                    shutil.rmtree(target_dir_path)
                shutil.copytree(source_dir_path, target_dir_path)
                print(f"✅ 复制 {dir_name}/")
                success_count += 1
            except Exception as e:
                print(f"❌ 复制 {dir_name}/ 失败: {e}")
        else:
            print(f"⚠️ 源目录不存在: {dir_name}")
    
    if success_count > 0:
        print(f"\n🎉 修复完成！复制了 {success_count} 个项目")
        print("现在可以正常运行GUI了")
        return True
    else:
        print("\n❌ 修复失败")
        return False

if __name__ == "__main__":
    fix_import_issue()
