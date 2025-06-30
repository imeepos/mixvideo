#!/usr/bin/env python3
"""
Python 3.13兼容性修复脚本
解决新版本Python的兼容性问题
"""

import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"当前Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 13):
        print("⚠️ 检测到Python 3.13+")
        print("这是最新版本，可能存在兼容性问题")
        return True
    
    return False

def fix_tkinter_python313():
    """修复Python 3.13的tkinter问题"""
    print("\n🔧 尝试修复Python 3.13的tkinter问题...")
    
    # 方法1: 尝试安装tk包
    print("方法1: 安装tk包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "tk"], 
                      check=True, capture_output=True)
        print("✅ tk包安装成功")
    except subprocess.CalledProcessError:
        print("❌ tk包安装失败")
    
    # 方法2: 尝试安装tkinter包
    print("方法2: 安装tkinter包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "tkinter"], 
                      check=True, capture_output=True)
        print("✅ tkinter包安装成功")
    except subprocess.CalledProcessError:
        print("❌ tkinter包安装失败")
    
    # 方法3: 检查系统tkinter
    print("方法3: 检查系统tkinter...")
    try:
        import tkinter
        print("✅ tkinter现在可用")
        return True
    except ImportError:
        print("❌ tkinter仍然不可用")
    
    return False

def install_alternative_python():
    """提供安装替代Python版本的指导"""
    print("\n📥 推荐安装Python 3.11.9")
    print("=" * 40)
    
    if platform.system() == "Windows":
        print("Windows用户:")
        print("1. 访问: https://www.python.org/downloads/release/python-3119/")
        print("2. 下载: Windows installer (64-bit)")
        print("3. 安装时确保勾选:")
        print("   - Add Python to PATH")
        print("   - tcl/tk and IDLE")
        print("   - pip")
        print("4. 重新运行此应用程序")
    
    elif platform.system() == "Darwin":  # macOS
        print("macOS用户:")
        print("1. 使用Homebrew: brew install python@3.11")
        print("2. 或从python.org下载安装包")
        print("3. 安装后运行: python3.11 run_gui.py")
    
    else:  # Linux
        print("Linux用户:")
        print("1. Ubuntu/Debian:")
        print("   sudo apt update")
        print("   sudo apt install python3.11 python3.11-tk python3.11-pip")
        print("2. CentOS/RHEL:")
        print("   sudo yum install python311 python311-tkinter")
        print("3. 使用pyenv安装特定版本")

def create_compatibility_launcher():
    """创建兼容性启动器"""
    print("\n📝 创建兼容性启动器...")
    
    launcher_content = '''@echo off
echo Smart Shot Detection System - Python 3.13 Compatibility Launcher
echo ================================================================

echo Checking Python version...
python -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"

echo.
echo Attempting tkinter fix for Python 3.13...
python -c "import sys; exec('import subprocess; subprocess.run([sys.executable, \"-m\", \"pip\", \"install\", \"tk\"], capture_output=True)') if sys.version_info >= (3, 13) else None"

echo.
echo Testing tkinter...
python -c "import tkinter; print('tkinter: OK')" 2>nul
if errorlevel 1 (
    echo tkinter: FAILED
    echo.
    echo SOLUTION: Install Python 3.11.9 instead
    echo Download: https://www.python.org/downloads/release/python-3119/
    echo.
    pause
    exit /b 1
) else (
    echo tkinter: OK
)

echo.
echo Installing dependencies...
pip install opencv-python numpy loguru Pillow

echo.
echo Starting application...
python run_gui.py

pause
'''
    
    with open("run_python313_compatible.bat", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print("✅ 创建了兼容性启动器: run_python313_compatible.bat")

def main():
    """主函数"""
    print("🔧 Python 3.13兼容性修复工具")
    print("=" * 50)
    
    is_python313 = check_python_version()
    
    if is_python313:
        print("\n🎯 针对Python 3.13的特殊处理...")
        
        # 尝试修复tkinter
        if fix_tkinter_python313():
            print("\n✅ tkinter修复成功！")
            print("现在可以尝试运行应用程序")
        else:
            print("\n❌ 无法修复tkinter问题")
            install_alternative_python()
        
        # 创建兼容性启动器
        create_compatibility_launcher()
        
    else:
        print("\n✅ Python版本兼容性良好")
        print("如果遇到问题，请运行: python test_tkinter.py")
    
    print("\n" + "=" * 50)
    print("🎯 建议:")
    print("1. 如果问题持续，建议使用Python 3.11.9")
    print("2. 运行 test_tkinter.py 进行详细诊断")
    print("3. 使用 run_python_fixed.bat 启动应用")
    
    print("\n按回车键退出...")
    input()

if __name__ == "__main__":
    main()
