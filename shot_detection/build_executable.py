#!/usr/bin/env python3
"""
可执行文件构建脚本
使用PyInstaller将智能镜头检测与分段系统打包成可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_dependencies():
    """检查构建依赖"""
    print("🔍 检查构建依赖...")
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller已安装: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller安装完成")
    
    # 检查其他必要依赖
    required_packages = [
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
        ("loguru", "loguru"),
        ("pathlib", "pathlib"),
        ("tkinter", "tkinter"),
        ("pillow", "PIL"),
        ("matplotlib", "matplotlib")
    ]

    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name}")
    
    if missing_packages:
        print(f"⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        print("请先安装缺少的依赖包")
        return False
    
    return True


def create_spec_file():
    """创建PyInstaller规格文件"""
    print("📝 创建PyInstaller规格文件...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# 获取项目根目录
project_root = Path.cwd()

# 数据文件和目录
datas = [
    # 配置文件
    ('config.py', '.'),
    
    # 工具模块
    ('utils', 'utils'),
    ('detectors', 'detectors'),
    ('processors', 'processors'),
    ('exporters', 'exporters'),
    
    # 字体配置
    ('font_config.py', '.'),
    ('font_config.ini', '.'),
    
    # 示例文件
    ('test_video.mp4', '.'),
    
    # 文档
    ('README.md', '.'),
    ('*.md', '.'),
]

# 隐藏导入
hiddenimports = [
    'cv2',
    'numpy',
    'loguru',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'matplotlib',
    'matplotlib.pyplot',
    'pathlib',
    'threading',
    'subprocess',
    'webbrowser',
    'datetime',
    'json',
    'csv',
    'xml.etree.ElementTree',
    'configparser',
    'dataclasses',
    'typing',
    'collections',
    'itertools',
    'functools',
    'operator',
    'math',
    'statistics',
    'time',
    'os',
    'sys',
    'shutil',
    'tempfile',
    'platform',
    'socket',
    'urllib',
    'http',
    'email',
    'base64',
    'hashlib',
    'uuid',
    'random',
    'string',
    're',
    'glob',
    'fnmatch',
]

# 排除的模块
excludes = [
    'test_*',
    'pytest',
    'unittest',
    'doctest',
    'pdb',
    'pydoc',
    'IPython',
    'jupyter',
    'notebook',
]

a = Analysis(
    ['run_gui.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ShotDetectionGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
)

# 创建目录分发版本
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ShotDetectionGUI_dist',
)
'''
    
    with open('ShotDetectionGUI.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 规格文件创建完成: ShotDetectionGUI.spec")


def create_icon():
    """创建应用图标"""
    print("🎨 创建应用图标...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建64x64的图标
        size = 64
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制简单的摄像机图标
        # 主体
        draw.rectangle([8, 20, 48, 44], fill=(70, 130, 180), outline=(50, 100, 150), width=2)
        # 镜头
        draw.ellipse([50, 26, 58, 38], fill=(50, 50, 50), outline=(30, 30, 30), width=1)
        # 取景器
        draw.rectangle([16, 12, 40, 20], fill=(100, 100, 100), outline=(80, 80, 80), width=1)
        # 胶片条
        draw.rectangle([4, 48, 60, 52], fill=(255, 215, 0), outline=(200, 170, 0), width=1)
        for i in range(6, 58, 8):
            draw.rectangle([i, 49, i+4, 51], fill=(200, 170, 0))
        
        # 保存为ICO格式
        img.save('icon.ico', format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
        print("✅ 图标创建完成: icon.ico")
        
    except ImportError:
        print("⚠️ PIL未安装，跳过图标创建")
    except Exception as e:
        print(f"⚠️ 图标创建失败: {e}")


def build_executable():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    # 清理之前的构建
    for path in ['build', 'dist', '__pycache__']:
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"🗑️ 清理: {path}")
    
    # 使用PyInstaller构建
    cmd = [
        'pyinstaller',
        '--clean',
        '--noconfirm',
        'ShotDetectionGUI.spec'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 可执行文件构建成功！")
        print(f"📁 输出目录: {Path.cwd() / 'dist'}")
        
        # 检查生成的文件
        dist_dir = Path('dist')
        if dist_dir.exists():
            print("\n📦 生成的文件:")
            for item in dist_dir.iterdir():
                if item.is_file():
                    size = item.stat().st_size / (1024 * 1024)  # MB
                    print(f"   📄 {item.name} ({size:.1f} MB)")
                elif item.is_dir():
                    print(f"   📁 {item.name}/")
        
        return True
    else:
        print("❌ 构建失败！")
        print("错误输出:")
        print(result.stderr)
        return False


def create_installer_script():
    """创建安装脚本"""
    print("📜 创建安装脚本...")
    
    # Windows批处理脚本（避免中文字符）
    batch_script = '''@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Installer
echo ========================================

echo Creating installation directory...
if not exist "C:\\Program Files\\ShotDetectionGUI" (
    mkdir "C:\\Program Files\\ShotDetectionGUI"
)

echo Copying files...
xcopy /E /I /Y "ShotDetectionGUI_dist\\*" "C:\\Program Files\\ShotDetectionGUI\\"

echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\ShotDetectionGUI.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\ShotDetectionGUI\\ShotDetectionGUI.exe'; $Shortcut.Save()"

echo Creating start menu shortcut...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ShotDetectionGUI" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ShotDetectionGUI"
)
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\ShotDetectionGUI\\ShotDetectionGUI.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\ShotDetectionGUI\\ShotDetectionGUI.exe'; $Shortcut.Save()"

echo Installation completed!
echo You can find "ShotDetectionGUI" shortcut on desktop or start menu
pause
'''
    
    with open('install.bat', 'w', encoding='utf-8') as f:
        f.write(batch_script)
    
    # Linux shell脚本
    shell_script = '''#!/bin/bash
echo "🎬 智能镜头检测与分段系统 - 安装程序"
echo "========================================"

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用sudo运行此脚本"
    exit 1
fi

echo "📁 创建安装目录..."
mkdir -p /opt/ShotDetectionGUI

echo "📋 复制文件..."
cp -r ShotDetectionGUI_dist/* /opt/ShotDetectionGUI/

echo "🔗 创建可执行链接..."
ln -sf /opt/ShotDetectionGUI/ShotDetectionGUI /usr/local/bin/shot-detection-gui

echo "📋 创建桌面文件..."
cat > /usr/share/applications/shot-detection-gui.desktop << EOF
[Desktop Entry]
Name=智能镜头检测
Name[en]=Shot Detection GUI
Comment=智能视频镜头检测与分段系统
Comment[en]=Intelligent Video Shot Detection and Segmentation System
Exec=/opt/ShotDetectionGUI/ShotDetectionGUI
Icon=/opt/ShotDetectionGUI/icon.ico
Terminal=false
Type=Application
Categories=AudioVideo;Video;
EOF

echo "🔧 设置权限..."
chmod +x /opt/ShotDetectionGUI/ShotDetectionGUI
chmod +x /usr/share/applications/shot-detection-gui.desktop

echo "✅ 安装完成！"
echo "📱 您可以在应用程序菜单中找到'智能镜头检测'"
'''
    
    with open('install.sh', 'w', encoding='utf-8') as f:
        f.write(shell_script)
    
    os.chmod('install.sh', 0o755)
    
    print("✅ 安装脚本创建完成:")
    print("   📄 install.bat (Windows)")
    print("   📄 install.sh (Linux)")


def create_readme():
    """创建发布说明"""
    print("📖 创建发布说明...")
    
    readme_content = '''# 🎬 智能镜头检测与分段系统 - 可执行版本

## 📋 系统要求

### Windows
- Windows 10 或更高版本
- 64位操作系统
- 至少 4GB 内存
- 至少 2GB 可用磁盘空间

### Linux
- Ubuntu 18.04 或更高版本 / CentOS 7 或更高版本
- 64位操作系统
- 至少 4GB 内存
- 至少 2GB 可用磁盘空间

## 🚀 安装方法

### Windows 安装
1. 解压下载的压缩包
2. 右键点击 `install.bat`，选择"以管理员身份运行"
3. 按照提示完成安装
4. 在桌面或开始菜单中找到"智能镜头检测"快捷方式

### Linux 安装
1. 解压下载的压缩包
2. 打开终端，进入解压目录
3. 运行安装脚本：`sudo ./install.sh`
4. 在应用程序菜单中找到"智能镜头检测"

### 便携版使用
如果不想安装，可以直接运行：
- Windows: 双击 `ShotDetectionGUI.exe`
- Linux: 在终端中运行 `./ShotDetectionGUI`

## 📖 使用说明

### 基本操作
1. **选择视频文件**：点击"浏览"按钮选择要处理的MP4视频文件
2. **设置输出目录**：选择分段视频的保存位置
3. **配置参数**：
   - 组织方式：按时长或质量组织分段
   - 输出质量：选择视频压缩质量
4. **开始处理**：点击"开始处理"按钮
5. **查看结果**：处理完成后可以查看分段视频和分析报告

### 高级功能
- **实时进度显示**：处理过程中可以看到详细的进度信息
- **日志监控**：实时查看处理日志和错误信息
- **分析报告**：生成详细的HTML分析报告
- **多格式导出**：支持CSV、EDL、XML等格式的项目文件

## 🔧 故障排除

### 常见问题

**Q: 程序无法启动**
A: 请确保：
- 系统满足最低要求
- 已安装必要的系统组件
- 杀毒软件没有阻止程序运行

**Q: 视频处理失败**
A: 请检查：
- 视频文件格式是否支持（推荐MP4）
- 视频文件是否损坏
- 输出目录是否有写入权限
- 磁盘空间是否充足

**Q: 中文显示乱码**
A: 程序会自动检测和安装中文字体，如果仍有问题：
- Windows: 确保系统已安装中文语言包
- Linux: 运行 `sudo apt install fonts-noto-cjk`

**Q: FFmpeg相关错误**
A: 程序内置了FFmpeg，如果出现问题：
- 确保程序有执行权限
- 检查系统是否缺少必要的编解码器

### 获取帮助
如果遇到其他问题，请：
1. 查看程序日志文件
2. 截图错误信息
3. 联系技术支持

## 📄 许可证
本软件遵循 MIT 许可证。

## 🔄 更新日志
- v1.0.0: 初始发布版本
  - 智能镜头检测
  - 视频自动分段
  - 多格式导出
  - GUI界面
  - 中文支持

---
© 2024 智能镜头检测与分段系统
'''
    
    with open('RELEASE_README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ 发布说明创建完成: RELEASE_README.md")


def main():
    """主函数"""
    print("📦 智能镜头检测与分段系统 - 可执行文件构建工具")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 创建图标
    create_icon()
    
    # 创建规格文件
    create_spec_file()
    
    # 构建可执行文件
    if not build_executable():
        return False
    
    # 创建安装脚本
    create_installer_script()
    
    # 创建发布说明
    create_readme()
    
    print("\n🎉 构建完成！")
    print("📦 发布包内容:")
    print("   📁 dist/ShotDetectionGUI_dist/ - 程序文件")
    print("   📄 dist/ShotDetectionGUI.exe - 单文件版本")
    print("   📄 install.bat - Windows安装脚本")
    print("   📄 install.sh - Linux安装脚本")
    print("   📄 RELEASE_README.md - 发布说明")
    print("   🎨 icon.ico - 应用图标")
    
    print("\n📋 下一步:")
    print("1. 测试生成的可执行文件")
    print("2. 创建发布压缩包")
    print("3. 编写用户文档")
    print("4. 发布到目标平台")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
