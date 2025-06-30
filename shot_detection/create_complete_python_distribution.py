#!/usr/bin/env python3
"""
创建完整的Python源码分发包
包含所有必要的模块和文件
"""

import os
import shutil
import zipfile
from pathlib import Path
import datetime


def create_complete_python_distribution():
    """创建完整的Python源码分发包"""
    print("🐍 创建完整的Python源码分发包...")
    
    # 创建发布目录
    release_name = f"ShotDetectionGUI_Python_Complete_v1.0.3_{datetime.datetime.now().strftime('%Y%m%d')}"
    release_dir = Path(release_name)
    
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    print(f"📁 创建发布目录: {release_dir}")
    
    # 复制所有Python文件
    print("📋 复制Python源码...")
    
    # 主要Python文件
    python_files = [
        "run_gui.py",
        "gui_app.py",
        "gui_logger.py",  # 重要：包含GUI日志模块
        "config.py",
        "video_segmentation.py",
        "video_processing_with_callbacks.py",
        "font_config.py",
        "build_windows_executable.py",
        "test_tkinter.py",  # tkinter测试工具
        "python313_compatibility_fix.py",  # Python 3.13兼容性修复
        "run_python_fixed.bat",  # 修复的启动脚本
        "__init__.py"
    ]
    
    for file in python_files:
        if Path(file).exists():
            shutil.copy2(file, release_dir / file)
            print(f"✅ {file}")
        else:
            print(f"⚠️ 文件不存在: {file}")
    
    # 复制目录
    directories = ["utils", "detectors", "processors", "exporters"]
    for dir_name in directories:
        if Path(dir_name).exists():
            shutil.copytree(dir_name, release_dir / dir_name)
            print(f"✅ {dir_name}/")
        else:
            print(f"⚠️ 目录不存在: {dir_name}")
    
    # 复制配置文件
    config_files = ["config.yaml", "font_config.ini"]
    for file in config_files:
        if Path(file).exists():
            shutil.copy2(file, release_dir / file)
            print(f"✅ {file}")
    
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
    
    # 创建完整的requirements.txt
    print("📋 创建完整的requirements.txt...")
    requirements = release_dir / "requirements.txt"
    with open(requirements, 'w', encoding='utf-8') as f:
        f.write("""# Smart Shot Detection System - Complete Python Dependencies
# Core video processing
opencv-python>=4.5.0
numpy>=1.20.0

# Logging and utilities
loguru>=0.6.0

# GUI and image processing
Pillow>=8.0.0

# Path handling (for older Python versions)
pathlib2>=2.3.0; python_version<"3.4"

# Data classes (for older Python versions)
dataclasses>=0.6; python_version<"3.7"

# For building executable (optional)
pyinstaller>=5.0.0

# Additional utilities
typing-extensions>=3.7.4; python_version<"3.8"

# GUI framework (usually included with Python)
# tkinter (built-in on most Python installations)

# Note: If you encounter import errors, try installing these additional packages:
# matplotlib>=3.3.0  # For advanced plotting (optional)
# scipy>=1.6.0       # For advanced signal processing (optional)
""")
    print("✅ requirements.txt")
    
    # 创建增强的Windows启动脚本
    print("📋 创建增强的Windows启动脚本...")
    
    run_python_bat = release_dir / "run_python.bat"
    with open(run_python_bat, 'w', encoding='utf-8') as f:
        f.write("""@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Python Version (Complete)
echo ========================================================

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

python --version
echo.

echo Checking tkinter availability...
python -c "import tkinter; print('tkinter: OK')" >nul 2>&1
if errorlevel 1 (
    echo ERROR: tkinter is not available!
    echo.
    echo Solutions:
    echo 1. Reinstall Python with "tcl/tk and IDLE" option checked
    echo 2. Install tkinter separately: sudo apt install python3-tk (Linux)
    echo 3. Use Anaconda Python distribution
    echo.
    pause
    exit /b 1
)

echo tkinter: OK
echo.

echo Installing required packages...
echo This may take a few minutes on first run...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo WARNING: Some packages failed to install.
    echo Trying alternative installation methods...
    echo.
    
    echo Trying with --user flag...
    pip install --user -r requirements.txt
    
    if errorlevel 1 (
        echo.
        echo ERROR: Package installation failed!
        echo.
        echo Troubleshooting steps:
        echo 1. Update pip: python -m pip install --upgrade pip
        echo 2. Check internet connection
        echo 3. Try manual installation: pip install opencv-python numpy loguru pillow
        echo.
        pause
        exit /b 1
    )
)

echo.
echo All dependencies installed successfully!
echo.

echo Starting Smart Shot Detection System...
python run_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start!
    echo.
    echo Common solutions:
    echo 1. Check if all files were extracted properly
    echo 2. Verify Python version is 3.8 or higher
    echo 3. Check error messages above for specific issues
    echo.
    pause
)
""")
    print("✅ run_python.bat")
    
    # 创建Linux启动脚本
    run_linux_sh = release_dir / "run_linux.sh"
    with open(run_linux_sh, 'w', encoding='utf-8') as f:
        f.write("""#!/bin/bash
echo "Smart Shot Detection System - Python Version (Complete)"
echo "========================================================"

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo ""
    echo "Installation commands:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip python3-tk"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip tkinter"
    echo "  Fedora: sudo dnf install python3 python3-pip python3-tkinter"
    echo ""
    exit 1
fi

python3 --version

echo "Checking tkinter availability..."
python3 -c "import tkinter; print('tkinter: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: tkinter is not available!"
    echo ""
    echo "Install tkinter:"
    echo "  Ubuntu/Debian: sudo apt install python3-tk"
    echo "  CentOS/RHEL: sudo yum install tkinter"
    echo "  Fedora: sudo dnf install python3-tkinter"
    echo ""
    exit 1
fi

echo "tkinter: OK"
echo ""

echo "Installing required packages..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "WARNING: Some packages failed to install."
    echo "Trying alternative installation..."
    
    pip3 install --user -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Package installation failed!"
        echo ""
        echo "Try manual installation:"
        echo "pip3 install opencv-python numpy loguru pillow"
        echo ""
        exit 1
    fi
fi

echo ""
echo "All dependencies installed successfully!"
echo ""

echo "Starting Smart Shot Detection System..."
python3 run_gui.py
""")
    os.chmod(run_linux_sh, 0o755)
    print("✅ run_linux.sh")
    
    # 创建依赖检查脚本
    check_deps_py = release_dir / "check_dependencies.py"
    with open(check_deps_py, 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
依赖检查脚本
验证所有必要的模块是否可用
\"\"\"

import sys
import importlib

def check_dependency(module_name, package_name=None):
    \"\"\"检查单个依赖\"\"\"
    try:
        importlib.import_module(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name}: {e}")
        return False

def main():
    \"\"\"主检查函数\"\"\"
    print("🔍 检查Python依赖项...")
    print(f"Python版本: {sys.version}")
    print()
    
    # 必需的依赖
    required_deps = [
        ("tkinter", "tkinter (GUI framework)"),
        ("cv2", "opencv-python (video processing)"),
        ("numpy", "numpy (numerical computing)"),
        ("loguru", "loguru (logging)"),
        ("PIL", "Pillow (image processing)"),
    ]
    
    # 可选的依赖
    optional_deps = [
        ("matplotlib", "matplotlib (plotting)"),
        ("scipy", "scipy (scientific computing)"),
    ]
    
    print("必需依赖:")
    missing_required = []
    for module, desc in required_deps:
        if not check_dependency(module, desc):
            missing_required.append(module)
    
    print("\\n可选依赖:")
    for module, desc in optional_deps:
        check_dependency(module, desc)
    
    print("\\n" + "="*50)
    
    if missing_required:
        print(f"❌ 缺少 {len(missing_required)} 个必需依赖")
        print("请运行以下命令安装:")
        if "cv2" in missing_required:
            print("pip install opencv-python")
        if "numpy" in missing_required:
            print("pip install numpy")
        if "loguru" in missing_required:
            print("pip install loguru")
        if "PIL" in missing_required:
            print("pip install Pillow")
        if "tkinter" in missing_required:
            print("tkinter通常随Python安装，请检查Python安装")
        
        print("\\n或者运行: pip install -r requirements.txt")
        return False
    else:
        print("✅ 所有必需依赖都已安装")
        print("🚀 可以运行应用程序: python run_gui.py")
        return True

if __name__ == "__main__":
    success = main()
    input("\\n按回车键退出...")
    sys.exit(0 if success else 1)
""")
    print("✅ check_dependencies.py")
    
    # 创建详细的安装指南
    print("📖 创建详细的安装指南...")
    guide = release_dir / "INSTALLATION_GUIDE.txt"
    with open(guide, 'w', encoding='utf-8') as f:
        f.write("""Smart Shot Detection System - Complete Installation Guide

=== QUICK START ===

Windows Users:
1. Double-click "run_python.bat"
2. Wait for automatic setup to complete
3. Start using the application!

Linux Users:
1. Run: ./run_linux.sh
2. Wait for automatic setup to complete
3. Start using the application!

=== DETAILED INSTALLATION ===

System Requirements:
- Python 3.8 or higher
- Windows 10/11 (64-bit) OR Linux (64-bit)
- At least 4GB RAM
- At least 2GB free disk space
- Internet connection (for initial setup only)

Step 1: Install Python
----------------------
Windows:
1. Download from https://www.python.org/downloads/
2. Run installer and CHECK "Add Python to PATH"
3. Verify: Open Command Prompt and type "python --version"

Linux:
Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk
CentOS/RHEL: sudo yum install python3 python3-pip tkinter
Fedora: sudo dnf install python3 python3-pip python3-tkinter

Step 2: Verify Dependencies
---------------------------
Run: python check_dependencies.py
This will show you which packages are missing.

Step 3: Install Dependencies
----------------------------
Automatic: Use the provided startup scripts (recommended)
Manual: pip install -r requirements.txt

Step 4: Run Application
-----------------------
python run_gui.py

=== TROUBLESHOOTING ===

Problem: "Python is not recognized"
Solution: Reinstall Python and check "Add to PATH"

Problem: "No module named 'tkinter'"
Solution: 
- Windows: Reinstall Python with "tcl/tk and IDLE" checked
- Linux: sudo apt install python3-tk

Problem: "No module named 'cv2'"
Solution: pip install opencv-python

Problem: Application window is blank or crashes
Solution:
1. Check Python version (must be 3.8+)
2. Verify all dependencies: python check_dependencies.py
3. Try running from command line to see error messages

Problem: Chinese characters show as squares
Solution: The application will auto-detect fonts, but you can:
- Windows: Install additional language packs
- Linux: sudo apt install fonts-noto-cjk

=== FEATURES ===
- Intelligent shot boundary detection
- Automatic video segmentation
- Real-time progress monitoring
- Multiple export formats
- Chinese GUI with font auto-detection
- Comprehensive analysis reports

=== SUPPORT ===
For additional help, check the README.md file or run the dependency checker.

© 2024 Smart Shot Detection System - Complete Edition
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
    
    print(f"\n🎉 完整Python源码分发包创建完成！")
    print(f"📁 目录版本: {release_dir}/")
    print(f"📦 压缩包: {zip_name}")
    print(f"📊 总大小: {size_mb:.1f} MB (压缩后: {zip_size:.1f} MB)")
    
    print(f"\n📋 包含内容:")
    print(f"✅ 完整Python源码（包含gui_logger.py）")
    print(f"✅ 所有必要的模块和目录")
    print(f"✅ 增强的启动脚本（Windows + Linux）")
    print(f"✅ 依赖检查工具")
    print(f"✅ 完整的安装指南")
    print(f"✅ 自动错误诊断和修复")
    
    return release_dir, zip_name


if __name__ == "__main__":
    create_complete_python_distribution()
