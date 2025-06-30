#!/usr/bin/env python3
"""
创建修复版发布包
解决Windows批处理文件编码问题
"""

import os
import shutil
import zipfile
from pathlib import Path
import datetime


def create_fixed_release():
    """创建修复版发布包"""
    print("📦 创建修复版发布包...")
    
    # 创建发布目录
    release_name = f"ShotDetectionGUI_v1.0.1_Fixed_{datetime.datetime.now().strftime('%Y%m%d')}"
    release_dir = Path(release_name)
    
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    print(f"📁 创建发布目录: {release_dir}")
    
    # 复制可执行文件
    print("📋 复制可执行文件...")
    
    # 单文件版本
    if Path("dist/ShotDetectionGUI").exists():
        shutil.copy2("dist/ShotDetectionGUI", release_dir / "ShotDetectionGUI")
        print("✅ 单文件版本: ShotDetectionGUI")
    
    # 目录版本
    if Path("dist/ShotDetectionGUI_dist").exists():
        shutil.copytree("dist/ShotDetectionGUI_dist", release_dir / "ShotDetectionGUI_dist")
        print("✅ 目录版本: ShotDetectionGUI_dist/")
    
    # 复制修复的安装脚本
    print("📋 复制修复的安装脚本...")
    scripts = [
        ("install_fixed.bat", "install.bat"),
        ("run_portable.bat", "run_portable.bat"),
        ("install.sh", "install.sh")
    ]
    
    for src, dst in scripts:
        if Path(src).exists():
            shutil.copy2(src, release_dir / dst)
            print(f"✅ {dst}")
    
    # 复制文档
    print("📋 复制文档...")
    docs = ["RELEASE_README.md", "README.md"]
    for doc in docs:
        if Path(doc).exists():
            shutil.copy2(doc, release_dir / doc)
            print(f"✅ {doc}")
    
    # 复制图标
    if Path("icon.ico").exists():
        shutil.copy2("icon.ico", release_dir / "icon.ico")
        print("✅ icon.ico")
    
    # 复制示例视频
    if Path("test_video.mp4").exists():
        size_mb = Path("test_video.mp4").stat().st_size / (1024 * 1024)
        if size_mb < 50:
            shutil.copy2("test_video.mp4", release_dir / "test_video.mp4")
            print(f"✅ test_video.mp4 ({size_mb:.1f}MB)")
    
    # 创建修复版快速开始指南
    print("📖 创建修复版快速开始指南...")
    quick_start = release_dir / "QUICK_START.txt"
    with open(quick_start, 'w', encoding='utf-8') as f:
        f.write("""Smart Shot Detection System - Quick Start Guide

=== Windows Users ===
Method 1: Portable Version (Recommended)
1. Double-click "run_portable.bat" to start the application directly
   OR
2. Double-click "ShotDetectionGUI.exe" (single file version)
   OR
3. Navigate to "ShotDetectionGUI_dist" folder and double-click "ShotDetectionGUI.exe"

Method 2: System Installation
1. Right-click "install.bat" and select "Run as administrator"
2. Follow the installation prompts
3. Find "ShotDetectionGUI" shortcut on desktop or start menu

=== Linux Users ===
Method 1: Direct Run
1. Open terminal in the application directory
2. Run: ./ShotDetectionGUI

Method 2: System Installation
1. Open terminal in the application directory
2. Run: sudo ./install.sh

=== Usage Steps ===
1. Select video file (MP4 format recommended)
2. Set output directory
3. Choose organization method and quality settings
4. Click "Start Processing"
5. Wait for processing to complete
6. View generated video segments and analysis report

=== System Requirements ===
- 64-bit operating system
- At least 4GB RAM
- At least 2GB free disk space

=== Troubleshooting ===
- If you see encoding errors, use "run_portable.bat" instead of direct execution
- If Chinese characters don't display correctly, the system will auto-detect fonts
- For other issues, check RELEASE_README.md

=== Technical Support ===
If you encounter problems, please refer to the troubleshooting section in RELEASE_README.md.

© 2024 Smart Shot Detection System
""")
    print("✅ QUICK_START.txt")
    
    # 创建修复版本信息
    version_info = release_dir / "VERSION_INFO.txt"
    with open(version_info, 'w', encoding='utf-8') as f:
        f.write(f"""Smart Shot Detection System
Version: v1.0.1 (Fixed Release)
Build Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Platform: Linux x86_64

FIXES IN THIS VERSION:
- Fixed Windows batch file encoding issues
- Added portable run script for Windows
- Improved installation process
- Better error handling for directory operations

Features:
- Intelligent shot detection algorithms
- Automatic video segmentation
- Multi-format project file export
- Detailed analysis report generation
- Chinese GUI interface with font auto-detection
- Real-time progress display
- Scrollable interface layout

Package Contents:
- ShotDetectionGUI (single file executable version)
- ShotDetectionGUI_dist/ (directory version with dependencies)
- install.bat (Windows installation script - FIXED)
- run_portable.bat (Windows portable launcher - NEW)
- install.sh (Linux installation script)
- RELEASE_README.md (detailed documentation)
- QUICK_START.txt (quick start guide - UPDATED)
- icon.ico (application icon)
- test_video.mp4 (sample video for testing)

INSTALLATION NOTES:
- Windows users: Use "run_portable.bat" for easiest startup
- If installation fails, try running as administrator
- For portable use, no installation required
""")
    print("✅ VERSION_INFO.txt")
    
    # 计算发布包大小
    total_size = 0
    for root, dirs, files in os.walk(release_dir):
        for file in files:
            total_size += os.path.getsize(os.path.join(root, file))
    
    size_mb = total_size / (1024 * 1024)
    print(f"📊 发布包大小: {size_mb:.1f} MB")
    
    # 创建压缩包
    print("🗜️ 创建压缩包...")
    zip_name = f"{release_name}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, release_dir.parent)
                zipf.write(file_path, arc_name)
    
    zip_size = os.path.getsize(zip_name) / (1024 * 1024)
    print(f"✅ 压缩包创建完成: {zip_name} ({zip_size:.1f} MB)")
    
    print(f"\n🎉 修复版发布包创建完成！")
    print(f"📁 目录版本: {release_dir}/")
    print(f"📦 压缩包: {zip_name}")
    print(f"📊 总大小: {size_mb:.1f} MB (压缩后: {zip_size:.1f} MB)")
    
    print(f"\n🔧 修复内容:")
    print(f"✅ Windows批处理文件编码问题")
    print(f"✅ 添加便携版启动脚本")
    print(f"✅ 改进安装过程")
    print(f"✅ 更新用户文档")
    
    return release_dir, zip_name


if __name__ == "__main__":
    create_fixed_release()
