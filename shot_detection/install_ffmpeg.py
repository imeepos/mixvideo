#!/usr/bin/env python3
"""
FFmpeg自动安装脚本
为Windows用户自动下载和配置FFmpeg
"""

import os
import sys
import urllib.request
import zipfile
import shutil
import subprocess
from pathlib import Path
import platform


def check_ffmpeg_installed():
    """检查FFmpeg是否已安装"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
            print(f"版本信息: {result.stdout.split()[2]}")
            return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    print("❌ FFmpeg未安装或不在PATH中")
    return False


def download_ffmpeg_windows():
    """下载Windows版FFmpeg"""
    print("📥 下载FFmpeg for Windows...")
    
    # FFmpeg下载URL (使用官方构建)
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    
    # 创建下载目录
    download_dir = Path("ffmpeg_download")
    download_dir.mkdir(exist_ok=True)
    
    zip_file = download_dir / "ffmpeg.zip"
    
    try:
        print(f"正在下载: {ffmpeg_url}")
        print("这可能需要几分钟时间...")
        
        # 下载文件
        urllib.request.urlretrieve(ffmpeg_url, zip_file)
        print(f"✅ 下载完成: {zip_file}")
        
        return zip_file
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None


def extract_ffmpeg(zip_file):
    """解压FFmpeg"""
    print("📦 解压FFmpeg...")
    
    extract_dir = Path("ffmpeg_download")
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print("✅ 解压完成")
        
        # 查找ffmpeg.exe
        for root, dirs, files in os.walk(extract_dir):
            if "ffmpeg.exe" in files:
                ffmpeg_path = Path(root) / "ffmpeg.exe"
                print(f"找到FFmpeg: {ffmpeg_path}")
                return ffmpeg_path
        
        print("❌ 在解压文件中找不到ffmpeg.exe")
        return None
        
    except Exception as e:
        print(f"❌ 解压失败: {e}")
        return None


def install_ffmpeg_locally(ffmpeg_exe):
    """在本地安装FFmpeg"""
    print("📁 安装FFmpeg到本地目录...")
    
    # 创建本地bin目录
    local_bin = Path("bin")
    local_bin.mkdir(exist_ok=True)
    
    # 复制ffmpeg.exe到本地bin目录
    local_ffmpeg = local_bin / "ffmpeg.exe"
    
    try:
        shutil.copy2(ffmpeg_exe, local_ffmpeg)
        print(f"✅ FFmpeg安装到: {local_ffmpeg.absolute()}")
        
        # 测试安装
        result = subprocess.run([str(local_ffmpeg), '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg安装验证成功")
            return local_ffmpeg
        else:
            print("❌ FFmpeg安装验证失败")
            return None
            
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return None


def add_to_path(ffmpeg_dir):
    """添加FFmpeg到PATH环境变量"""
    print("🔧 配置环境变量...")
    
    if platform.system() == "Windows":
        # 创建批处理文件来设置PATH
        bat_content = f'''@echo off
set PATH={ffmpeg_dir.absolute()};%PATH%
echo FFmpeg已添加到PATH
echo 当前会话中可以直接使用ffmpeg命令
'''
        
        with open("setup_ffmpeg_path.bat", "w") as f:
            f.write(bat_content)
        
        print("✅ 创建了环境变量设置脚本: setup_ffmpeg_path.bat")
        print("💡 运行此脚本可在当前会话中使用ffmpeg命令")


def create_ffmpeg_launcher():
    """创建FFmpeg启动器"""
    print("🚀 创建应用启动器...")
    
    launcher_content = '''@echo off
chcp 65001 >nul
echo Smart Shot Detection System - FFmpeg Ready Version
echo ==================================================

echo Setting up FFmpeg...
set PATH=%~dp0bin;%PATH%

echo Checking FFmpeg...
bin\\ffmpeg.exe -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: FFmpeg not found in bin directory!
    echo Please run: python install_ffmpeg.py
    pause
    exit /b 1
)

echo FFmpeg: Ready
echo.

echo Starting application...
python run_gui.py

pause
'''
    
    with open("run_with_ffmpeg.bat", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print("✅ 创建了FFmpeg启动器: run_with_ffmpeg.bat")


def cleanup_download():
    """清理下载文件"""
    download_dir = Path("ffmpeg_download")
    if download_dir.exists():
        try:
            shutil.rmtree(download_dir)
            print("🗑️ 清理下载文件")
        except Exception as e:
            print(f"⚠️ 清理失败: {e}")


def install_ffmpeg_alternative():
    """提供FFmpeg替代安装方法"""
    print("\n📋 FFmpeg替代安装方法")
    print("=" * 40)
    
    print("方法1: 手动下载安装")
    print("1. 访问: https://ffmpeg.org/download.html")
    print("2. 下载Windows版本")
    print("3. 解压到任意目录")
    print("4. 将ffmpeg.exe所在目录添加到系统PATH")
    
    print("\n方法2: 使用包管理器")
    print("1. 安装Chocolatey: https://chocolatey.org/")
    print("2. 运行: choco install ffmpeg")
    
    print("\n方法3: 使用便携版")
    print("1. 下载便携版FFmpeg")
    print("2. 放在应用程序同一目录")
    print("3. 使用run_with_ffmpeg.bat启动")


def main():
    """主函数"""
    print("🎬 Smart Shot Detection System - FFmpeg安装工具")
    print("=" * 60)
    
    # 检查操作系统
    if platform.system() != "Windows":
        print("此脚本专为Windows设计")
        print("Linux/macOS用户请使用包管理器安装FFmpeg:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        return
    
    # 检查是否已安装
    if check_ffmpeg_installed():
        print("✅ FFmpeg已可用，无需安装")
        return
    
    print("\n🔧 开始安装FFmpeg...")
    
    # 下载FFmpeg
    zip_file = download_ffmpeg_windows()
    if not zip_file:
        print("\n❌ 自动下载失败")
        install_ffmpeg_alternative()
        return
    
    # 解压FFmpeg
    ffmpeg_exe = extract_ffmpeg(zip_file)
    if not ffmpeg_exe:
        print("\n❌ 解压失败")
        install_ffmpeg_alternative()
        return
    
    # 安装到本地
    local_ffmpeg = install_ffmpeg_locally(ffmpeg_exe)
    if not local_ffmpeg:
        print("\n❌ 本地安装失败")
        install_ffmpeg_alternative()
        return
    
    # 配置环境
    add_to_path(local_ffmpeg.parent)
    
    # 创建启动器
    create_ffmpeg_launcher()
    
    # 清理下载文件
    cleanup_download()
    
    print("\n🎉 FFmpeg安装完成！")
    print("=" * 60)
    print("✅ FFmpeg已安装到本地bin目录")
    print("✅ 创建了专用启动器: run_with_ffmpeg.bat")
    print("\n🚀 使用方法:")
    print("1. 双击 run_with_ffmpeg.bat 启动应用")
    print("2. 或运行 setup_ffmpeg_path.bat 后使用普通启动方式")
    
    print("\n按回车键退出...")
    input()


if __name__ == "__main__":
    main()
