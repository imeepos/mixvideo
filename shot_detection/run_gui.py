#!/usr/bin/env python3
"""
智能镜头检测与分段系统 - GUI启动脚本
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def check_dependencies():
    """检查依赖项"""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import loguru
    except ImportError:
        missing_deps.append("loguru")
    
    if missing_deps:
        print("❌ 缺少以下依赖项:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\n请运行以下命令安装:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    return True

def check_ffmpeg():
    """检查FFmpeg"""
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    print("⚠️ 警告: 未找到FFmpeg")
    print("FFmpeg是视频处理的必需工具，请确保已安装并添加到PATH")
    print("下载地址: https://ffmpeg.org/download.html")
    return False

def check_chinese_fonts():
    """检查中文字体"""
    try:
        from font_config import FontManager

        font_manager = FontManager()
        font_manager.detect_system_fonts()
        font_manager.detect_chinese_fonts()

        chinese_fonts = font_manager.chinese_fonts
        best_font = font_manager.get_best_font()

        if chinese_fonts and best_font:
            print(f"✅ 中文字体检查通过，找到 {len(chinese_fonts)} 个中文字体")
            print(f"   最佳字体: {best_font}")
            return True
        else:
            print("⚠️ 警告: 未找到中文字体")
            print("GUI界面可能显示中文乱码")

            # 在Linux上提供安装选项
            if font_manager.system == "Linux":
                print("\n可以运行以下命令安装中文字体:")
                print("sudo apt install fonts-noto-cjk fonts-wqy-zenhei fonts-wqy-microhei")

                response = input("是否现在安装中文字体? (y/N): ")
                if response.lower() == 'y':
                    return font_manager.install_fonts_linux()

            return False

    except Exception as e:
        print(f"⚠️ 字体检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🎬 智能镜头检测与分段系统")
    print("=" * 40)

    # 检查依赖
    print("🔍 检查依赖项...")
    if not check_dependencies():
        sys.exit(1)

    print("✅ Python依赖项检查通过")

    # 检查中文字体
    print("🔍 检查中文字体...")
    font_ok = check_chinese_fonts()
    if not font_ok:
        print("⚠️ 中文字体检查未通过，GUI可能显示乱码")
        response = input("是否继续启动GUI? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)

    # 检查FFmpeg
    print("🔍 检查FFmpeg...")
    ffmpeg_ok = check_ffmpeg()
    if ffmpeg_ok:
        print("✅ FFmpeg检查通过")
    else:
        response = input("是否继续启动GUI? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)

    # 启动GUI
    print("🚀 启动GUI界面...")
    try:
        from gui_app import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ 启动GUI失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
