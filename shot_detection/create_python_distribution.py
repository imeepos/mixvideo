#!/usr/bin/env python3
"""
创建Python源码分发包
让用户在Windows上自行构建或直接运行Python版本
"""

import os
import shutil
import zipfile
from pathlib import Path
import datetime


def create_python_distribution():
    """创建Python源码分发包"""
    print("🐍 创建Python源码分发包...")
    
    # 创建发布目录
    release_name = f"ShotDetectionGUI_Python_Source_v1.0.2_{datetime.datetime.now().strftime('%Y%m%d')}"
    release_dir = Path(release_name)
    
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    print(f"📁 创建发布目录: {release_dir}")
    
    # 复制Python源码
    print("📋 复制Python源码...")
    
    # 主要Python文件
    python_files = [
        "run_gui.py",
        "gui_app.py",
        "gui_logger.py",  # 添加缺失的模块
        "config.py",
        "video_segmentation.py",
        "video_processing_with_callbacks.py",
        "font_config.py",
        "build_windows_executable.py"
    ]
    
    for file in python_files:
        if Path(file).exists():
            shutil.copy2(file, release_dir / file)
            print(f"✅ {file}")
    
    # 复制目录
    directories = ["utils", "detectors", "processors", "exporters"]
    for dir_name in directories:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, release_dir / dir_name)
            print(f"✅ {dir_name}/")
    
    # 复制其他文件
    other_files = ["README.md", "icon.ico", "test_video.mp4"]
    for file in other_files:
        if Path(file).exists():
            size_mb = Path(file).stat().st_size / (1024 * 1024)
            if file.endswith('.mp4') and size_mb > 50:
                print(f"⚠️ {file} 太大 ({size_mb:.1f}MB)，跳过")
                continue
            shutil.copy2(file, release_dir / file)
            print(f"✅ {file}")
    
    # 创建requirements.txt
    print("📋 创建requirements.txt...")
    requirements = release_dir / "requirements.txt"
    with open(requirements, 'w', encoding='utf-8') as f:
        f.write("""# Smart Shot Detection System - Python Dependencies
opencv-python>=4.5.0
numpy>=1.20.0
loguru>=0.6.0
Pillow>=8.0.0
pathlib2>=2.3.0
dataclasses>=0.6; python_version<"3.7"

# For building executable (optional)
pyinstaller>=5.0.0

# For GUI (usually included with Python)
# tkinter (built-in on most Python installations)
""")
    print("✅ requirements.txt")
    
    # 创建Windows批处理启动脚本
    print("📋 创建Windows启动脚本...")
    
    # Python直接运行脚本
    run_python_bat = release_dir / "run_python.bat"
    with open(run_python_bat, 'w', encoding='utf-8') as f:
        f.write("""@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Python Version
echo ============================================

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

python --version
echo.

echo Checking dependencies...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ERROR: tkinter is not available!
    echo Please install tkinter or use a complete Python distribution.
    pause
    exit /b 1
)

echo Installing required packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo WARNING: Some packages failed to install.
    echo The application may not work correctly.
    echo.
)

echo Starting application...
python run_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start!
    echo Please check the error messages above.
    pause
)
""")
    print("✅ run_python.bat")
    
    # 构建可执行文件脚本
    build_exe_bat = release_dir / "build_executable.bat"
    with open(build_exe_bat, 'w', encoding='utf-8') as f:
        f.write("""@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Build Executable
echo ==============================================

echo This script will build a Windows executable file.
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo Installing build dependencies...
pip install pyinstaller pillow

echo Building executable...
python build_windows_executable.py

if errorlevel 1 (
    echo.
    echo Build failed! Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Check the 'dist' folder for the executable files.
pause
""")
    print("✅ build_executable.bat")
    
    # 创建Linux启动脚本
    run_linux_sh = release_dir / "run_linux.sh"
    with open(run_linux_sh, 'w', encoding='utf-8') as f:
        f.write("""#!/bin/bash
echo "Smart Shot Detection System - Python Version (Linux)"
echo "===================================================="

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.8 or higher:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip tkinter"
    exit 1
fi

python3 --version

echo "Installing required packages..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "WARNING: Some packages failed to install."
    echo "The application may not work correctly."
fi

echo "Starting application..."
python3 run_gui.py
""")
    os.chmod(run_linux_sh, 0o755)
    print("✅ run_linux.sh")
    
    # 创建详细的安装和使用指南
    print("📖 创建安装和使用指南...")
    guide = release_dir / "INSTALLATION_GUIDE.txt"
    with open(guide, 'w', encoding='utf-8') as f:
        f.write("""Smart Shot Detection System - Installation and Usage Guide

=== OVERVIEW ===
This is the Python source code distribution of the Smart Shot Detection System.
You can either run it directly with Python or build your own executable.

=== SYSTEM REQUIREMENTS ===
- Python 3.8 or higher
- Windows 10/11 (64-bit) OR Linux (64-bit)
- At least 4GB RAM
- At least 2GB free disk space

=== INSTALLATION OPTIONS ===

Option 1: Direct Python Execution (Recommended for developers)
----------------------------------------------------------
Windows:
1. Install Python from https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH"
2. Double-click "run_python.bat"
   - This will install dependencies and start the application

Linux:
1. Install Python and dependencies:
   Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk
   CentOS/RHEL: sudo yum install python3 python3-pip tkinter
2. Run: ./run_linux.sh

Option 2: Build Your Own Executable (Windows only)
------------------------------------------------
1. Follow Option 1 to set up Python
2. Double-click "build_executable.bat"
3. Wait for the build to complete
4. Find the executable in the "dist" folder

Option 3: Manual Installation
---------------------------
1. Install Python 3.8+
2. Install dependencies: pip install -r requirements.txt
3. Run the application: python run_gui.py

=== USAGE ===
1. Select a video file (MP4 format recommended)
2. Choose output directory for video segments
3. Configure processing options:
   - Organization method (by duration or quality)
   - Output quality setting
4. Click "Start Processing"
5. Monitor progress in real-time
6. View results in the output directory

=== FEATURES ===
- Intelligent shot boundary detection
- Automatic video segmentation
- Real-time progress monitoring
- Multiple export formats (MP4, CSV, EDL, XML, HTML)
- Chinese GUI with automatic font detection
- Scrollable interface for different screen sizes

=== TROUBLESHOOTING ===

Problem: "Python is not installed or not in PATH"
Solution: Install Python from python.org and ensure "Add to PATH" is checked

Problem: "tkinter is not available"
Solution: 
- Windows: Reinstall Python with "tcl/tk and IDLE" option checked
- Linux: sudo apt install python3-tk

Problem: "pip install failed"
Solution: 
- Update pip: python -m pip install --upgrade pip
- Try with --user flag: pip install --user -r requirements.txt

Problem: Application doesn't start
Solution:
- Check Python version: python --version (should be 3.8+)
- Check error messages in the console
- Try running: python -c "import tkinter; print('tkinter OK')"

Problem: Video processing fails
Solution:
- Ensure video file is not corrupted
- Check available disk space
- Try with a smaller video file first

=== BUILDING EXECUTABLE ===
If you want to create your own executable:

1. Use the provided build_executable.bat (Windows)
2. Or manually run: python build_windows_executable.py
3. The executable will be created in the "dist" folder
4. You can then distribute the entire "dist" folder

=== SUPPORT ===
For technical support and bug reports, please refer to the README.md file
or check the project documentation.

© 2024 Smart Shot Detection System
""")
    print("✅ INSTALLATION_GUIDE.txt")
    
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
    
    print(f"\n🎉 Python源码分发包创建完成！")
    print(f"📁 目录版本: {release_dir}/")
    print(f"📦 压缩包: {zip_name}")
    print(f"📊 总大小: {size_mb:.1f} MB (压缩后: {zip_size:.1f} MB)")
    
    print(f"\n📋 包含内容:")
    print(f"✅ 完整Python源码")
    print(f"✅ Windows启动脚本 (run_python.bat)")
    print(f"✅ Linux启动脚本 (run_linux.sh)")
    print(f"✅ 可执行文件构建脚本 (build_executable.bat)")
    print(f"✅ 依赖列表 (requirements.txt)")
    print(f"✅ 详细安装指南 (INSTALLATION_GUIDE.txt)")
    
    return release_dir, zip_name


if __name__ == "__main__":
    create_python_distribution()
