"""
Package Manager
包管理器
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class PackageConfig:
    """包配置"""
    
    def __init__(self):
        """初始化包配置"""
        self.package_name = "shot-detection"
        self.version = "2.0.0"
        self.description = "Advanced video shot detection and analysis toolkit"
        self.author = "Shot Detection Team"
        self.author_email = "team@shot-detection.com"
        self.license = "MIT"
        self.url = "https://github.com/shot-detection/shot-detection"
        self.python_requires = ">=3.8"
        self.include_data_files = True
        self.include_docs = True
        self.include_examples = True
        self.platforms = ["any"]
        self.classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Topic :: Multimedia :: Video",
            "Topic :: Scientific/Engineering :: Image Processing"
        ]


class PackageManager:
    """包管理器"""
    
    def __init__(self, config: Optional[PackageConfig] = None):
        """
        初始化包管理器
        
        Args:
            config: 包配置
        """
        self.config = config or PackageConfig()
        self.logger = logger.bind(component="PackageManager")
        
        # 项目根目录
        self.project_root = Path(__file__).parent.parent.parent
        
        # 构建目录
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
        self.logger.info("Package manager initialized")
    
    def create_source_distribution(self) -> bool:
        """
        创建源码分发包
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating source distribution")
            
            # 清理构建目录
            self._clean_build_dirs()
            
            # 生成setup.py
            self._generate_setup_py()
            
            # 生成MANIFEST.in
            self._generate_manifest()
            
            # 生成requirements.txt
            self._generate_requirements()
            
            # 运行setup.py sdist
            result = subprocess.run(
                [self._get_python_executable(), "setup.py", "sdist"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("Source distribution created successfully")
                return True
            else:
                self.logger.error(f"Source distribution failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create source distribution: {e}")
            return False
    
    def create_wheel_distribution(self) -> bool:
        """
        创建wheel分发包
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating wheel distribution")
            
            # 确保wheel已安装
            self._ensure_wheel_installed()
            
            # 运行setup.py bdist_wheel
            result = subprocess.run(
                [self._get_python_executable(), "setup.py", "bdist_wheel"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("Wheel distribution created successfully")
                return True
            else:
                self.logger.error(f"Wheel distribution failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create wheel distribution: {e}")
            return False
    
    def create_conda_package(self) -> bool:
        """
        创建conda包
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating conda package")
            
            # 生成conda配置
            self._generate_conda_recipe()
            
            # 运行conda build
            result = subprocess.run(
                ["conda-build", "conda-recipe"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("Conda package created successfully")
                return True
            else:
                self.logger.error(f"Conda package creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create conda package: {e}")
            return False
    
    def create_app_image(self) -> bool:
        """
        创建AppImage（Linux）

        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating AppImage")

            # 这里可以实现AppImage创建逻辑
            # 需要使用appimage-builder或类似工具

            self.logger.info("AppImage creation not implemented")
            return False

        except Exception as e:
            self.logger.error(f"Failed to create AppImage: {e}")
            return False

    def create_executable(self, platform: str = "current") -> bool:
        """
        创建可执行文件
        
        Args:
            platform: 目标平台
            
        Returns:
            是否创建成功
        """
        try:
            self.logger.info(f"Creating executable for platform: {platform}")
            
            # 确保PyInstaller已安装
            self._ensure_pyinstaller_installed()
            
            # 生成PyInstaller配置
            spec_file = self._generate_pyinstaller_spec()
            
            # 运行PyInstaller
            result = subprocess.run(
                ["pyinstaller", str(spec_file)],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("Executable created successfully")
                return True
            else:
                self.logger.error(f"Executable creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create executable: {e}")
            return False
    
    def _clean_build_dirs(self):
        """清理构建目录"""
        try:
            for dir_path in [self.build_dir, self.dist_dir]:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # 清理egg-info目录
            for egg_info in self.project_root.glob("*.egg-info"):
                if egg_info.is_dir():
                    shutil.rmtree(egg_info)
                    
        except Exception as e:
            self.logger.error(f"Failed to clean build directories: {e}")
    
    def _generate_setup_py(self):
        """生成setup.py文件"""
        try:
            setup_content = f'''#!/usr/bin/env python3
"""
Setup script for {self.config.package_name}
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split("\\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="{self.config.package_name}",
    version="{self.config.version}",
    description="{self.config.description}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="{self.config.author}",
    author_email="{self.config.author_email}",
    url="{self.config.url}",
    license="{self.config.license}",
    packages=find_packages(),
    python_requires="{self.config.python_requires}",
    install_requires=requirements,
    classifiers={self.config.classifiers!r},
    platforms={self.config.platforms!r},
    include_package_data=True,
    zip_safe=False,
    entry_points={{
        "console_scripts": [
            "shot-detection = shot_detection.cli:main",
        ],
    }},
    package_data={{
        "shot_detection": [
            "data/*",
            "templates/*",
            "examples/*",
        ],
    }},
)
'''
            
            setup_file = self.project_root / "setup.py"
            with open(setup_file, 'w', encoding='utf-8') as f:
                f.write(setup_content)
            
            self.logger.debug("setup.py generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate setup.py: {e}")
    
    def _generate_manifest(self):
        """生成MANIFEST.in文件"""
        try:
            manifest_content = """# Include documentation
include README.md
include LICENSE
include CHANGELOG.md
include requirements.txt

# Include data files
recursive-include shot_detection/data *
recursive-include shot_detection/templates *
recursive-include shot_detection/examples *

# Include tests
recursive-include tests *

# Exclude build artifacts
global-exclude *.pyc
global-exclude *.pyo
global-exclude *.pyd
global-exclude __pycache__
global-exclude .git*
global-exclude .DS_Store
"""
            
            manifest_file = self.project_root / "MANIFEST.in"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                f.write(manifest_content)
            
            self.logger.debug("MANIFEST.in generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate MANIFEST.in: {e}")
    
    def _generate_requirements(self):
        """生成requirements.txt文件"""
        try:
            requirements = [
                "numpy>=1.19.0",
                "opencv-python>=4.0.0",
                "pillow>=8.0.0",
                "matplotlib>=3.3.0",
                "loguru>=0.5.0",
                "pyyaml>=5.4.0",
                "toml>=0.10.0",
                "psutil>=5.8.0",
                "tqdm>=4.60.0",
                "click>=8.0.0"
            ]
            
            requirements_file = self.project_root / "requirements.txt"
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(requirements))
            
            self.logger.debug("requirements.txt generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate requirements.txt: {e}")
    
    def _generate_conda_recipe(self):
        """生成conda配置"""
        try:
            recipe_dir = self.project_root / "conda-recipe"
            recipe_dir.mkdir(exist_ok=True)
            
            # meta.yaml
            meta_content = f'''package:
  name: {self.config.package_name}
  version: {self.config.version}

source:
  path: ..

build:
  number: 0
  script: python setup.py install --single-version-externally-managed --record=record.txt
  entry_points:
    - shot-detection = shot_detection.cli:main

requirements:
  build:
    - python
    - setuptools
  run:
    - python
    - numpy >=1.19.0
    - opencv >=4.0.0
    - pillow >=8.0.0
    - matplotlib >=3.3.0
    - loguru >=0.5.0
    - pyyaml >=5.4.0
    - toml >=0.10.0
    - psutil >=5.8.0
    - tqdm >=4.60.0
    - click >=8.0.0

test:
  imports:
    - shot_detection
  commands:
    - shot-detection --help

about:
  home: {self.config.url}
  license: {self.config.license}
  license_file: LICENSE
  summary: {self.config.description}
  description: |
    {self.config.description}
  dev_url: {self.config.url}

extra:
  recipe-maintainers:
    - {self.config.author}
'''
            
            meta_file = recipe_dir / "meta.yaml"
            with open(meta_file, 'w', encoding='utf-8') as f:
                f.write(meta_content)
            
            self.logger.debug("Conda recipe generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate conda recipe: {e}")
    
    def _generate_pyinstaller_spec(self) -> Path:
        """生成PyInstaller配置文件"""
        try:
            spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['shot_detection/cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('shot_detection/data', 'shot_detection/data'),
        ('shot_detection/templates', 'shot_detection/templates'),
    ],
    hiddenimports=[
        'cv2',
        'numpy',
        'matplotlib',
        'loguru',
        'yaml',
        'toml',
        'psutil',
        'tqdm',
        'click',
    ],
    hookspath=[],
    hooksconfig={{}},
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
)
'''
            
            spec_file = self.project_root / "shot-detection.spec"
            with open(spec_file, 'w', encoding='utf-8') as f:
                f.write(spec_content)
            
            self.logger.debug("PyInstaller spec generated")
            return spec_file
            
        except Exception as e:
            self.logger.error(f"Failed to generate PyInstaller spec: {e}")
            return Path("shot-detection.spec")
    
    def _get_python_executable(self) -> str:
        """获取Python可执行文件路径"""
        import sys
        return sys.executable
    
    def _ensure_wheel_installed(self):
        """确保wheel已安装"""
        try:
            import wheel
        except ImportError:
            self.logger.info("Installing wheel...")
            subprocess.run([self._get_python_executable(), "-m", "pip", "install", "wheel"])
    
    def _ensure_pyinstaller_installed(self):
        """确保PyInstaller已安装"""
        try:
            import PyInstaller
        except ImportError:
            self.logger.info("Installing PyInstaller...")
            subprocess.run([self._get_python_executable(), "-m", "pip", "install", "pyinstaller"])
    
    def upload_to_pypi(self, repository: str = "pypi") -> bool:
        """
        上传到PyPI
        
        Args:
            repository: 仓库名称（pypi或testpypi）
            
        Returns:
            是否上传成功
        """
        try:
            self.logger.info(f"Uploading to {repository}")
            
            # 确保twine已安装
            try:
                import twine
            except ImportError:
                self.logger.info("Installing twine...")
                subprocess.run([self._get_python_executable(), "-m", "pip", "install", "twine"])
            
            # 上传
            result = subprocess.run(
                [self._get_python_executable(), "-m", "twine", "upload", "--repository", repository, "dist/*"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully uploaded to {repository}")
                return True
            else:
                self.logger.error(f"Upload failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to upload to PyPI: {e}")
            return False
    
    def create_all_packages(self) -> Dict[str, bool]:
        """
        创建所有包格式
        
        Returns:
            各种包格式的创建结果
        """
        try:
            self.logger.info("Creating all package formats")
            
            results = {}
            
            # 源码分发包
            results['sdist'] = self.create_source_distribution()
            
            # wheel包
            results['wheel'] = self.create_wheel_distribution()
            
            # conda包
            results['conda'] = self.create_conda_package()
            
            # 可执行文件
            results['executable'] = self.create_executable()
            
            # 统计结果
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            self.logger.info(f"Package creation completed: {successful}/{total} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to create all packages: {e}")
            return {}
    
    def cleanup(self):
        """清理资源"""
        try:
            # 清理临时文件
            temp_files = [
                self.project_root / "setup.py",
                self.project_root / "MANIFEST.in",
                self.project_root / "shot-detection.spec"
            ]
            
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
            
            self.logger.info("Package manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Package manager cleanup failed: {e}")
