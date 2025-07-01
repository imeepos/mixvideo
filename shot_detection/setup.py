#!/usr/bin/env python3
"""
Shot Detection v2.0 Setup Script
安装和打包脚本
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# 确保Python版本
if sys.version_info < (3, 8):
    print("Error: Shot Detection requires Python 3.8 or higher")
    sys.exit(1)

# 项目根目录
ROOT_DIR = Path(__file__).parent
README_FILE = ROOT_DIR / "README.md"
REQUIREMENTS_FILE = ROOT_DIR / "requirements.txt"

# 读取README
long_description = ""
if README_FILE.exists():
    with open(README_FILE, "r", encoding="utf-8") as f:
        long_description = f.read()

# 读取依赖
install_requires = []
if REQUIREMENTS_FILE.exists():
    with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as f:
        install_requires = [
            line.strip() for line in f.readlines()
            if line.strip() and not line.startswith("#")
        ]

# 版本信息
VERSION = "2.0.0"

# 项目信息
setup(
    name="shot-detection",
    version=VERSION,
    author="Shot Detection Team",
    author_email="team@shotdetection.com",
    description="Advanced video shot boundary detection system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shotdetection/shotdetection",
    project_urls={
        "Bug Reports": "https://github.com/shotdetection/shotdetection/issues",
        "Source": "https://github.com/shotdetection/shotdetection",
        "Documentation": "https://docs.shotdetection.com",
    },
    
    # 包信息
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    include_package_data=True,
    package_data={
        "shot_detection": [
            "config/*.yaml",
            "templates/*.html",
            "assets/*",
            "models/*.h5",
        ],
    },
    
    # 依赖
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "isort>=5.0",
        ],
        "ai": [
            "tensorflow>=2.8.0",
            "torch>=1.10.0",
            "torchvision>=0.11.0",
        ],
        "cloud": [
            "boto3>=1.20.0",
            "azure-storage-blob>=12.0.0",
            "google-cloud-storage>=2.0.0",
        ],
        "gui": [
            "tkinter",  # Usually included with Python
            "pillow>=8.0.0",
        ],
        "all": [
            "tensorflow>=2.8.0",
            "torch>=1.10.0",
            "torchvision>=0.11.0",
            "boto3>=1.20.0",
            "azure-storage-blob>=12.0.0",
            "google-cloud-storage>=2.0.0",
            "pillow>=8.0.0",
        ],
    },
    
    # 入口点
    entry_points={
        "console_scripts": [
            "shot-detection=shot_detection.main_v2:main",
            "shot-detection-cli=shot_detection.cli:main",
            "shot-detection-gui=shot_detection.gui.main_window:main",
        ],
    },
    
    # 分类信息
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # 关键词
    keywords="video, shot detection, boundary detection, computer vision, opencv",
    
    # 许可证
    license="MIT",
    
    # 平台支持
    platforms=["any"],
    
    # Zip安全
    zip_safe=False,
)

# 安装后处理
def post_install():
    """安装后处理"""
    print("\n" + "="*60)
    print("🎉 Shot Detection v2.0 安装完成!")
    print("="*60)
    print("\n📚 快速开始:")
    print("  命令行模式: shot-detection --help")
    print("  GUI模式:   shot-detection-gui")
    print("  Python API: from shot_detection import VideoService")
    print("\n📖 文档:")
    print("  用户手册:   https://docs.shotdetection.com/user-guide")
    print("  API文档:    https://docs.shotdetection.com/api")
    print("  示例代码:   https://docs.shotdetection.com/examples")
    print("\n🔧 配置:")
    print("  配置文件:   ~/.shot_detection/config_v2.yaml")
    print("  日志目录:   ~/.shot_detection/logs/")
    print("  缓存目录:   ~/.shot_detection/cache/")
    print("\n💬 支持:")
    print("  问题报告:   https://github.com/shotdetection/shotdetection/issues")
    print("  社区论坛:   https://community.shotdetection.com")
    print("  邮件支持:   support@shotdetection.com")
    print("\n" + "="*60)

if __name__ == "__main__":
    # 检查是否是安装命令
    if "install" in sys.argv:
        # 执行安装后处理
        import atexit
        atexit.register(post_install)
