#!/usr/bin/env python3
"""
Windows专用可执行文件构建脚本
解决跨平台兼容性问题
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_windows_build_environment():
    """检查Windows构建环境"""
    print("🔍 检查Windows构建环境...")
    
    # 检查是否在Windows上运行
    if sys.platform != "win32":
        print("❌ 此脚本需要在Windows系统上运行")
        print("当前系统:", sys.platform)
        return False
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print(f"❌ 需要Python 3.8或更高版本，当前版本: {python_version.major}.{python_version.minor}")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller安装完成")
    
    return True


def create_windows_spec_file():
    """创建Windows专用规格文件"""
    print("📝 创建Windows专用PyInstaller规格文件...")
    
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
    
    # 示例文件（如果存在）
    ('test_video.mp4', '.') if Path('test_video.mp4').exists() else None,
]

# 过滤None值
datas = [d for d in datas if d is not None]

# 隐藏导入 - Windows专用
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
    # Windows特定
    'win32api',
    'win32con',
    'win32gui',
    'msvcrt',
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
    # Linux特定模块
    'termios',
    'fcntl',
    'pwd',
    'grp',
]

# Windows特定的二进制文件
binaries = []

a = Analysis(
    ['run_gui.py'],
    pathex=[str(project_root)],
    binaries=binaries,
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
    version='version_info.txt' if Path('version_info.txt').exists() else None,
)

# 创建目录分发版本
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ShotDetectionGUI_Windows',
)
'''
    
    with open('ShotDetectionGUI_Windows.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Windows规格文件创建完成: ShotDetectionGUI_Windows.spec")


def create_version_info():
    """创建Windows版本信息文件"""
    print("📋 创建Windows版本信息...")
    
    version_info_content = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1, 0, 2, 0),
    prodvers=(1, 0, 2, 0),
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Smart Shot Detection Team'),
        StringStruct(u'FileDescription', u'Smart Shot Detection System'),
        StringStruct(u'FileVersion', u'1.0.2.0'),
        StringStruct(u'InternalName', u'ShotDetectionGUI'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024'),
        StringStruct(u'OriginalFilename', u'ShotDetectionGUI.exe'),
        StringStruct(u'ProductName', u'Smart Shot Detection System'),
        StringStruct(u'ProductVersion', u'1.0.2.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info_content)
    
    print("✅ 版本信息文件创建完成: version_info.txt")


def build_windows_executable():
    """构建Windows可执行文件"""
    print("🔨 开始构建Windows可执行文件...")
    
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
        '--log-level=INFO',
        'ShotDetectionGUI_Windows.spec'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Windows可执行文件构建成功！")
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
                    # 显示目录中的主要文件
                    for subitem in item.iterdir():
                        if subitem.name.endswith('.exe'):
                            size = subitem.stat().st_size / (1024 * 1024)
                            print(f"      📄 {subitem.name} ({size:.1f} MB)")
        
        return True
    else:
        print("❌ 构建失败！")
        print("错误输出:")
        print(result.stderr)
        return False


def create_windows_installer():
    """创建Windows安装包"""
    print("📦 创建Windows安装包...")
    
    # 检查是否有NSIS或Inno Setup
    try:
        # 尝试使用auto-py-to-exe的安装包功能
        subprocess.run(['pip', 'install', 'auto-py-to-exe'], check=True)
        print("✅ 安装包工具准备完成")
    except:
        print("⚠️ 无法安装打包工具，将创建ZIP分发包")
    
    # 创建简单的ZIP分发包
    import zipfile
    import datetime
    
    release_name = f"ShotDetectionGUI_Windows_v1.0.2_{datetime.datetime.now().strftime('%Y%m%d')}"
    
    with zipfile.ZipFile(f"{release_name}.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
        dist_dir = Path('dist')
        if dist_dir.exists():
            for root, dirs, files in os.walk(dist_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, dist_dir)
                    zipf.write(file_path, arc_name)
    
    print(f"✅ Windows分发包创建完成: {release_name}.zip")


def main():
    """主函数"""
    print("🪟 智能镜头检测与分段系统 - Windows专用构建工具")
    print("=" * 60)
    
    # 检查构建环境
    if not check_windows_build_environment():
        print("\n❌ 构建环境检查失败")
        print("请在Windows系统上运行此脚本，并确保Python环境正确配置")
        return False
    
    # 创建版本信息
    create_version_info()
    
    # 创建规格文件
    create_windows_spec_file()
    
    # 构建可执行文件
    if not build_windows_executable():
        return False
    
    # 创建安装包
    create_windows_installer()
    
    print("\n🎉 Windows构建完成！")
    print("📦 Windows发布包内容:")
    print("   📁 dist/ShotDetectionGUI_Windows/ - 程序文件")
    print("   📄 dist/ShotDetectionGUI.exe - 单文件版本")
    print("   📦 ShotDetectionGUI_Windows_v1.0.2_*.zip - 分发包")
    
    print("\n📋 使用说明:")
    print("1. 将生成的文件复制到Windows系统")
    print("2. 解压ZIP文件")
    print("3. 双击ShotDetectionGUI.exe运行")
    print("4. 或使用提供的安装脚本进行系统安装")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        input("按回车键退出...")
    sys.exit(0 if success else 1)
