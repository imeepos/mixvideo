#!/usr/bin/env python3
"""
Shot Detection v2.0 Build Script
构建和打包脚本
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"


def run_command(cmd: List[str], cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
    """运行命令"""
    print(f"🔧 Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd or ROOT_DIR, check=check, capture_output=True, text=True)


def clean_build():
    """清理构建目录"""
    print("🧹 Cleaning build directories...")
    
    dirs_to_clean = [BUILD_DIR, DIST_DIR, ROOT_DIR / "shot_detection.egg-info"]
    
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"   Removed: {dir_path}")
    
    # 清理Python缓存
    for cache_dir in ROOT_DIR.rglob("__pycache__"):
        shutil.rmtree(cache_dir)
    
    for pyc_file in ROOT_DIR.rglob("*.pyc"):
        pyc_file.unlink()
    
    print("✅ Build directories cleaned")


def install_dependencies():
    """安装依赖"""
    print("📦 Installing dependencies...")
    
    # 升级pip
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # 安装构建依赖
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel", "build"])
    
    # 安装项目依赖
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("✅ Dependencies installed")


def run_tests():
    """运行测试"""
    print("🧪 Running tests...")
    
    try:
        # 安装测试依赖
        run_command([sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"])
        
        # 运行测试
        result = run_command([sys.executable, "-m", "pytest", "tests/", "-v", "--cov=shot_detection"])
        
        print("✅ All tests passed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def run_linting():
    """运行代码检查"""
    print("🔍 Running code linting...")
    
    try:
        # 安装linting工具
        run_command([sys.executable, "-m", "pip", "install", "black", "flake8", "isort"])
        
        # 格式化代码
        run_command([sys.executable, "-m", "black", "shot_detection/"])
        run_command([sys.executable, "-m", "isort", "shot_detection/"])
        
        # 检查代码风格
        run_command([sys.executable, "-m", "flake8", "shot_detection/"])
        
        print("✅ Code linting passed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Linting failed: {e}")
        return False


def build_package():
    """构建Python包"""
    print("📦 Building Python package...")
    
    try:
        # 使用build模块构建
        run_command([sys.executable, "-m", "build"])
        
        print("✅ Package built successfully")
        
        # 显示构建结果
        if DIST_DIR.exists():
            print("\n📁 Build artifacts:")
            for file in DIST_DIR.iterdir():
                print(f"   {file.name} ({file.stat().st_size} bytes)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Package build failed: {e}")
        return False


def build_executable():
    """构建可执行文件"""
    print("🔨 Building executable...")
    
    try:
        # 安装PyInstaller
        run_command([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # 创建spec文件
        spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_v2.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/*.yaml', 'config'),
        ('templates/*', 'templates'),
        ('assets/*', 'assets'),
    ],
    hiddenimports=[
        'shot_detection.core',
        'shot_detection.gui',
        'shot_detection.jianying',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='shot-detection',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
"""
        
        spec_file = ROOT_DIR / "shot_detection.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        # 构建可执行文件
        run_command([sys.executable, "-m", "PyInstaller", "shot_detection.spec", "--clean"])
        
        print("✅ Executable built successfully")
        
        # 显示构建结果
        exe_dir = ROOT_DIR / "dist"
        if exe_dir.exists():
            print("\n🎯 Executable files:")
            for file in exe_dir.iterdir():
                if file.is_file():
                    print(f"   {file.name} ({file.stat().st_size} bytes)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Executable build failed: {e}")
        return False


def build_docker():
    """构建Docker镜像"""
    print("🐳 Building Docker image...")
    
    try:
        # 构建镜像
        run_command(["docker", "build", "-t", "shot-detection:2.0.0", "."])
        run_command(["docker", "tag", "shot-detection:2.0.0", "shot-detection:latest"])
        
        print("✅ Docker image built successfully")
        
        # 显示镜像信息
        result = run_command(["docker", "images", "shot-detection"])
        print("\n🐳 Docker images:")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Docker build failed: {e}")
        return False


def create_release_package():
    """创建发布包"""
    print("📦 Creating release package...")
    
    release_dir = BUILD_DIR / "release"
    release_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制必要文件
    files_to_copy = [
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        "requirements.txt",
        "config_v2.yaml",
    ]
    
    for file_name in files_to_copy:
        src_file = ROOT_DIR / file_name
        if src_file.exists():
            shutil.copy2(src_file, release_dir)
    
    # 复制文档
    docs_dir = ROOT_DIR / "docs"
    if docs_dir.exists():
        shutil.copytree(docs_dir, release_dir / "docs", dirs_exist_ok=True)
    
    # 复制示例
    examples_dir = ROOT_DIR / "examples"
    if examples_dir.exists():
        shutil.copytree(examples_dir, release_dir / "examples", dirs_exist_ok=True)
    
    # 创建安装脚本
    install_script = release_dir / "install.py"
    with open(install_script, 'w') as f:
        f.write("""#!/usr/bin/env python3
import subprocess
import sys

def main():
    print("Installing Shot Detection v2.0...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "shot-detection"])
    print("Installation completed!")

if __name__ == "__main__":
    main()
""")
    
    print(f"✅ Release package created: {release_dir}")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Shot Detection v2.0 Build Script")
    parser.add_argument("--clean", action="store_true", help="Clean build directories")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument("--package", action="store_true", help="Build Python package")
    parser.add_argument("--executable", action="store_true", help="Build executable")
    parser.add_argument("--docker", action="store_true", help="Build Docker image")
    parser.add_argument("--release", action="store_true", help="Create release package")
    parser.add_argument("--all", action="store_true", help="Run all build steps")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🚀 Shot Detection v2.0 Build Script")
    print("=" * 50)
    
    success = True
    
    try:
        if args.clean or args.all:
            clean_build()
        
        if args.all:
            install_dependencies()
        
        if args.lint or args.all:
            if not run_linting():
                success = False
        
        if args.test or args.all:
            if not run_tests():
                success = False
        
        if args.package or args.all:
            if not build_package():
                success = False
        
        if args.executable or args.all:
            if not build_executable():
                success = False
        
        if args.docker or args.all:
            if not build_docker():
                success = False
        
        if args.release or args.all:
            if not create_release_package():
                success = False
        
        if success:
            print("\n🎉 Build completed successfully!")
        else:
            print("\n❌ Build completed with errors!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Build failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
