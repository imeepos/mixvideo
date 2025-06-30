#!/usr/bin/env python3
"""
自动安装所有必要工具
静默安装版本，用于自动化部署
"""

import sys
import subprocess
import platform
from pathlib import Path


def install_python_packages():
    """自动安装Python包"""
    print("📦 检查和安装Python包...")
    
    required_packages = [
        "opencv-python",
        "numpy", 
        "loguru",
        "Pillow"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_').split('.')[0])
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"📥 安装 {package}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", package], 
                             check=True, capture_output=True)
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安装失败: {e}")
                return False
    
    return True


def install_ffmpeg_silent():
    """静默安装FFmpeg"""
    print("🎬 检查和安装FFmpeg...")
    
    # 检查是否已安装
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ 系统FFmpeg已安装")
            return True
    except:
        pass
    
    # 检查本地FFmpeg
    local_paths = [Path("bin/ffmpeg.exe"), Path("ffmpeg.exe")]
    for path in local_paths:
        if path.exists():
            try:
                result = subprocess.run([str(path), '-version'], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ 本地FFmpeg已安装: {path}")
                    return True
            except:
                continue
    
    # 尝试自动安装
    if platform.system() == "Windows":
        print("📥 自动下载和安装FFmpeg...")
        try:
            import install_ffmpeg
            
            # 下载
            zip_file = install_ffmpeg.download_ffmpeg_windows()
            if not zip_file:
                return False
            
            # 解压
            ffmpeg_exe = install_ffmpeg.extract_ffmpeg(zip_file)
            if not ffmpeg_exe:
                return False
            
            # 安装
            local_ffmpeg = install_ffmpeg.install_ffmpeg_locally(ffmpeg_exe)
            if not local_ffmpeg:
                return False
            
            # 清理
            install_ffmpeg.cleanup_download()
            
            print("✅ FFmpeg自动安装完成")
            return True
            
        except Exception as e:
            print(f"❌ FFmpeg自动安装失败: {e}")
            return False
    
    return False


def check_tkinter():
    """检查tkinter"""
    print("🖼️ 检查tkinter...")
    
    try:
        import tkinter
        print("✅ tkinter可用")
        return True
    except ImportError:
        print("❌ tkinter不可用")
        
        if sys.version_info >= (3, 13):
            print("⚠️ Python 3.13可能存在tkinter兼容性问题")
            print("建议使用Python 3.11.9")
        
        return False


def create_launcher():
    """创建启动器"""
    print("🚀 创建启动器...")
    
    # 检查本地FFmpeg
    has_local_ffmpeg = Path("bin/ffmpeg.exe").exists()
    
    launcher_content = f'''@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Ready to Run
echo ==========================================

'''
    
    if has_local_ffmpeg:
        launcher_content += '''echo 🔧 配置FFmpeg环境...
set PATH=%~dp0bin;%PATH%
echo ✅ FFmpeg环境已配置

'''
    
    launcher_content += '''echo 🚀 启动应用程序...
python run_gui.py

if errorlevel 1 (
    echo.
    echo ❌ 启动失败，请检查错误信息
    pause
)
'''
    
    with open("run_ready.bat", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print("✅ 创建启动器: run_ready.bat")


def main():
    """主函数"""
    print("🔧 Smart Shot Detection System - 自动工具安装器")
    print("=" * 60)
    
    success_count = 0
    total_checks = 4
    
    # 1. 检查tkinter
    if check_tkinter():
        success_count += 1
    
    # 2. 安装Python包
    if install_python_packages():
        success_count += 1
    
    # 3. 安装FFmpeg
    if install_ffmpeg_silent():
        success_count += 1
    
    # 4. 创建启动器
    try:
        create_launcher()
        success_count += 1
    except Exception as e:
        print(f"❌ 创建启动器失败: {e}")
    
    print("\n" + "=" * 60)
    print("📊 安装结果总结")
    print("=" * 60)
    
    print(f"成功: {success_count}/{total_checks}")
    
    if success_count == total_checks:
        print("🎉 所有工具安装完成！")
        print("✅ 可以使用以下方式启动应用:")
        print("  1. 双击: run_ready.bat")
        print("  2. 运行: python run_gui.py")
    elif success_count >= 2:
        print("⚠️ 部分工具安装成功")
        print("应用程序可能可以运行，但某些功能可能受限")
        print("建议手动解决剩余问题")
    else:
        print("❌ 大部分工具安装失败")
        print("请手动安装必要的依赖项")
    
    print("\n详细帮助:")
    print("  - 依赖检查: python check_dependencies.py")
    print("  - tkinter测试: python test_tkinter.py") 
    print("  - FFmpeg检查: python check_ffmpeg.py")
    
    return success_count >= 2


if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n按回车键退出...")
        input()
    
    sys.exit(0 if success else 1)
