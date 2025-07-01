#!/usr/bin/env python3
"""
智能镜头检测与分段系统 - GUI启动脚本
"""

import sys
import os
from pathlib import Path

# 强健的路径设置 - 确保能找到所有模块
def setup_python_path():
    """设置Python模块搜索路径"""
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.resolve()

    # 确保脚本目录在Python路径中
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    # 切换工作目录到脚本目录
    os.chdir(str(script_dir))

    print(f"[DEBUG] 脚本目录: {script_dir}")
    print(f"[DEBUG] 工作目录: {Path.cwd()}")
    print(f"[DEBUG] Python路径第一项: {sys.path[0]}")

    # 验证关键文件是否存在
    critical_files = [
        "prompts_manager.py",
        "prompts_constants.py",
        "prompts/video-analysis.prompt"
    ]

    missing_files = []
    for file_path in critical_files:
        if not (script_dir / file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"[ERROR] 缺少关键文件: {missing_files}")
        print(f"[ERROR] 请确保从正确的目录运行，或运行修复脚本")
        return False

    print(f"[DEBUG] 所有关键文件都存在")
    return True

# 设置路径
if not setup_python_path():
    print("路径设置失败，退出...")
    sys.exit(1)

def check_python_dependencies():
    """检查Python依赖项"""
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
        print("❌ 缺少以下Python依赖项:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\n正在尝试自动安装...")

        # 尝试自动安装
        import subprocess
        import sys

        for dep in missing_deps:
            if dep == "tkinter":
                print("⚠️ tkinter需要重新安装Python或使用完整Python发行版")
                continue

            try:
                print(f"安装 {dep}...")
                subprocess.run([sys.executable, "-m", "pip", "install", dep],
                             check=True, capture_output=True)
                print(f"✅ {dep} 安装成功")
            except subprocess.CalledProcessError:
                print(f"❌ {dep} 安装失败")
                return False

        # 重新检查
        return check_python_dependencies()

    return True


def check_ffmpeg():
    """检查FFmpeg是否可用"""
    import subprocess

    # 可能的FFmpeg路径
    possible_paths = [
        'ffmpeg',
        'bin/ffmpeg.exe',
        'ffmpeg.exe',
        'ffmpeg/bin/ffmpeg.exe',
    ]

    for path in possible_paths:
        try:
            result = subprocess.run([path, '-version'],
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ FFmpeg可用: {path}")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            continue

    print("❌ FFmpeg未找到")
    return False


def auto_install_ffmpeg():
    """自动安装FFmpeg"""
    print("🔧 正在自动安装FFmpeg...")

    try:
        # 导入并运行FFmpeg安装脚本
        import install_ffmpeg

        # 检查是否已安装
        if install_ffmpeg.check_ffmpeg_installed():
            return True

        print("开始下载和安装FFmpeg...")

        # 下载FFmpeg
        zip_file = install_ffmpeg.download_ffmpeg_windows()
        if not zip_file:
            return False

        # 解压FFmpeg
        ffmpeg_exe = install_ffmpeg.extract_ffmpeg(zip_file)
        if not ffmpeg_exe:
            return False

        # 安装到本地
        local_ffmpeg = install_ffmpeg.install_ffmpeg_locally(ffmpeg_exe)
        if not local_ffmpeg:
            return False

        # 创建启动器
        install_ffmpeg.create_ffmpeg_launcher()

        # 清理下载文件
        install_ffmpeg.cleanup_download()

        print("✅ FFmpeg自动安装完成")
        return True

    except Exception as e:
        print(f"❌ FFmpeg自动安装失败: {e}")
        return False


def check_and_install_tools():
    """检查并自动安装所有必要工具"""
    print("🔍 检查系统依赖...")
    print("=" * 50)

    all_ok = True

    # 检查Python依赖
    print("1. 检查Python依赖...")
    if not check_python_dependencies():
        print("❌ Python依赖检查失败")
        all_ok = False
    else:
        print("✅ Python依赖检查通过")

    print()

    # 检查FFmpeg
    print("2. 检查FFmpeg...")
    if not check_ffmpeg():
        print("🔧 FFmpeg未安装，尝试自动安装...")

        # 询问用户是否自动安装
        try:
            response = input("是否自动下载并安装FFmpeg? (Y/n): ").strip().lower()
            if response in ['', 'y', 'yes', '是']:
                if auto_install_ffmpeg():
                    print("✅ FFmpeg自动安装成功")
                else:
                    print("❌ FFmpeg自动安装失败")
                    print("请手动运行: python install_ffmpeg.py")
                    all_ok = False
            else:
                print("⚠️ 跳过FFmpeg安装，视频处理功能将不可用")
                all_ok = False
        except KeyboardInterrupt:
            print("\n⚠️ 用户取消安装")
            all_ok = False
    else:
        print("✅ FFmpeg检查通过")

    print()
    print("=" * 50)

    if all_ok:
        print("🎉 所有依赖检查通过，可以启动应用程序")
    else:
        print("⚠️ 部分依赖缺失，应用程序可能无法正常工作")
        print("建议运行以下命令解决问题:")
        print("  - python check_dependencies.py")
        print("  - python install_ffmpeg.py")

    return all_ok

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

    # 检查并自动安装所有必要工具
    print("🔍 系统环境检查...")
    if not check_and_install_tools():
        print("\n⚠️ 系统环境检查未完全通过")
        response = input("是否继续启动应用程序? (y/N): ").strip().lower()
        if response not in ['y', 'yes', '是']:
            print("应用程序启动已取消")
            sys.exit(1)

    # 检查中文字体
    print("\n🔍 检查中文字体...")
    font_ok = check_chinese_fonts()
    if not font_ok:
        print("⚠️ 中文字体检查未通过，GUI可能显示乱码")
        response = input("是否继续启动GUI? (y/N): ")
        if response.lower() != 'y':
            print("应用程序启动已取消")
            sys.exit(1)

    print("\n🚀 启动应用程序...")
    print("=" * 40)

    # 启动GUI
    try:
        from gui_app import main as gui_main
        print("✅ 启动GUI界面...")
        gui_main()
    except ImportError as e:
        print(f"❌ 导入GUI模块失败: {e}")
        print("请确保所有文件都已正确安装")
        print("建议运行: python check_dependencies.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动GUI失败: {e}")
        print("详细错误信息:")
        import traceback
        traceback.print_exc()
        print("\n建议:")
        print("1. 检查所有依赖是否正确安装")
        print("2. 运行: python check_dependencies.py")
        print("3. 运行: python test_tkinter.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
