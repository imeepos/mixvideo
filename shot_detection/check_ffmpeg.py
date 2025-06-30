#!/usr/bin/env python3
"""
FFmpeg检查和诊断脚本
"""

import subprocess
import sys
import platform
from pathlib import Path


def check_ffmpeg_system():
    """检查系统FFmpeg"""
    print("🔍 检查系统FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ 系统FFmpeg: {version_line}")
            return True
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 系统未安装FFmpeg")
    
    return False


def check_ffmpeg_local():
    """检查本地FFmpeg"""
    print("🔍 检查本地FFmpeg...")
    
    local_paths = [
        Path("bin/ffmpeg.exe"),
        Path("ffmpeg.exe"),
        Path("ffmpeg/bin/ffmpeg.exe")
    ]
    
    for path in local_paths:
        if path.exists():
            try:
                result = subprocess.run([str(path), '-version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_line = result.stdout.split('\n')[0]
                    print(f"✅ 本地FFmpeg: {path} - {version_line}")
                    return path
            except Exception:
                continue
    
    print("❌ 本地未找到FFmpeg")
    return None


def test_ffmpeg_functionality(ffmpeg_path=None):
    """测试FFmpeg功能"""
    print("🧪 测试FFmpeg功能...")
    
    cmd = ['ffmpeg'] if ffmpeg_path is None else [str(ffmpeg_path)]
    
    # 测试基本命令
    try:
        result = subprocess.run(cmd + ['-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1', 
                                     '-t', '1', '-f', 'null', '-'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ FFmpeg功能测试通过")
            return True
        else:
            print(f"❌ FFmpeg功能测试失败: {result.stderr}")
    except Exception as e:
        print(f"❌ FFmpeg功能测试异常: {e}")
    
    return False


def provide_installation_guide():
    """提供安装指南"""
    print("\n📋 FFmpeg安装指南")
    print("=" * 40)
    
    if platform.system() == "Windows":
        print("Windows用户:")
        print("1. 自动安装: python install_ffmpeg.py")
        print("2. 手动安装:")
        print("   - 访问: https://ffmpeg.org/download.html")
        print("   - 下载Windows版本")
        print("   - 解压并添加到PATH")
        print("3. 使用包管理器:")
        print("   - Chocolatey: choco install ffmpeg")
        print("   - Scoop: scoop install ffmpeg")
    
    elif platform.system() == "Darwin":  # macOS
        print("macOS用户:")
        print("1. 使用Homebrew: brew install ffmpeg")
        print("2. 使用MacPorts: sudo port install ffmpeg")
        print("3. 手动下载: https://ffmpeg.org/download.html")
    
    else:  # Linux
        print("Linux用户:")
        print("1. Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg")
        print("2. CentOS/RHEL: sudo yum install ffmpeg")
        print("3. Fedora: sudo dnf install ffmpeg")
        print("4. Arch: sudo pacman -S ffmpeg")


def create_ffmpeg_wrapper():
    """创建FFmpeg包装脚本"""
    print("📝 创建FFmpeg包装脚本...")
    
    # 检查本地FFmpeg
    local_ffmpeg = check_ffmpeg_local()
    
    if local_ffmpeg:
        # 创建Python包装器
        wrapper_content = f'''#!/usr/bin/env python3
"""
FFmpeg包装器
自动使用本地FFmpeg
"""

import subprocess
import sys
from pathlib import Path

def main():
    ffmpeg_path = Path("{local_ffmpeg}")
    if ffmpeg_path.exists():
        # 使用本地FFmpeg
        cmd = [str(ffmpeg_path)] + sys.argv[1:]
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    else:
        # 尝试系统FFmpeg
        cmd = ["ffmpeg"] + sys.argv[1:]
        result = subprocess.run(cmd)
        sys.exit(result.returncode)

if __name__ == "__main__":
    main()
'''
        
        with open("ffmpeg_wrapper.py", "w", encoding="utf-8") as f:
            f.write(wrapper_content)
        
        print("✅ 创建了FFmpeg包装器: ffmpeg_wrapper.py")
        return True
    
    return False


def main():
    """主函数"""
    print("🎬 Smart Shot Detection System - FFmpeg检查工具")
    print("=" * 60)
    
    # 检查系统FFmpeg
    system_ffmpeg = check_ffmpeg_system()
    
    # 检查本地FFmpeg
    local_ffmpeg = check_ffmpeg_local()
    
    # 测试功能
    if system_ffmpeg:
        print("\n🧪 测试系统FFmpeg...")
        test_ffmpeg_functionality()
    elif local_ffmpeg:
        print("\n🧪 测试本地FFmpeg...")
        test_ffmpeg_functionality(local_ffmpeg)
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 检查结果总结")
    print("=" * 60)
    
    if system_ffmpeg:
        print("✅ 系统FFmpeg可用")
        print("🚀 可以直接运行应用程序")
    elif local_ffmpeg:
        print("✅ 本地FFmpeg可用")
        print("🚀 使用 run_with_ffmpeg.bat 启动应用")
        
        # 创建包装器
        create_ffmpeg_wrapper()
    else:
        print("❌ 未找到可用的FFmpeg")
        print("🔧 需要安装FFmpeg")
        
        # 提供安装指南
        provide_installation_guide()
        
        if platform.system() == "Windows":
            print("\n💡 推荐操作:")
            print("1. 运行: python install_ffmpeg.py")
            print("2. 然后使用: run_with_ffmpeg.bat")
    
    print("\n按回车键退出...")
    input()


if __name__ == "__main__":
    main()
