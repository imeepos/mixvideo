"""
Installer Generator
安装程序生成器
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class InstallerConfig:
    """安装程序配置"""
    
    def __init__(self):
        """初始化安装程序配置"""
        self.app_name = "Shot Detection"
        self.app_version = "2.0.0"
        self.app_description = "Advanced video shot detection and analysis toolkit"
        self.app_publisher = "Shot Detection Team"
        self.app_url = "https://github.com/shot-detection/shot-detection"
        self.app_icon = "icon.ico"
        self.license_file = "LICENSE"
        self.install_dir = "Shot Detection"
        self.create_desktop_shortcut = True
        self.create_start_menu_shortcut = True
        self.add_to_path = True
        self.require_admin = False
        self.compression_level = 9


class InstallerGenerator:
    """安装程序生成器"""
    
    def __init__(self, config: Optional[InstallerConfig] = None):
        """
        初始化安装程序生成器
        
        Args:
            config: 安装程序配置
        """
        self.config = config or InstallerConfig()
        self.logger = logger.bind(component="InstallerGenerator")
        
        # 项目根目录
        self.project_root = Path(__file__).parent.parent.parent
        
        # 构建目录
        self.build_dir = self.project_root / "installer_build"
        
        self.logger.info("Installer generator initialized")
    
    def create_windows_installer(self) -> bool:
        """
        创建Windows安装程序（使用NSIS）
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating Windows installer")
            
            # 准备构建目录
            self._prepare_build_dir()
            
            # 生成NSIS脚本
            nsis_script = self._generate_nsis_script()
            
            # 编译NSIS脚本
            return self._compile_nsis_script(nsis_script)
            
        except Exception as e:
            self.logger.error(f"Failed to create Windows installer: {e}")
            return False
    
    def create_macos_installer(self) -> bool:
        """
        创建macOS安装程序（使用pkgbuild）
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating macOS installer")
            
            # 准备构建目录
            self._prepare_build_dir()
            
            # 创建应用包结构
            app_bundle = self._create_app_bundle()
            
            # 创建PKG安装包
            return self._create_pkg_installer(app_bundle)
            
        except Exception as e:
            self.logger.error(f"Failed to create macOS installer: {e}")
            return False
    
    def create_linux_installer(self) -> bool:
        """
        创建Linux安装程序（使用makeself）
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating Linux installer")
            
            # 准备构建目录
            self._prepare_build_dir()
            
            # 创建安装脚本
            install_script = self._create_install_script()
            
            # 创建自解压安装包
            return self._create_makeself_installer(install_script)
            
        except Exception as e:
            self.logger.error(f"Failed to create Linux installer: {e}")
            return False
    
    def create_deb_package(self) -> bool:
        """
        创建Debian包
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating Debian package")
            
            # 准备构建目录
            self._prepare_build_dir()
            
            # 创建Debian包结构
            self._create_debian_structure()
            
            # 构建包
            return self._build_debian_package()
            
        except Exception as e:
            self.logger.error(f"Failed to create Debian package: {e}")
            return False
    
    def create_rpm_package(self) -> bool:
        """
        创建RPM包
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info("Creating RPM package")
            
            # 准备构建目录
            self._prepare_build_dir()
            
            # 创建RPM spec文件
            spec_file = self._create_rpm_spec()
            
            # 构建RPM包
            return self._build_rpm_package(spec_file)
            
        except Exception as e:
            self.logger.error(f"Failed to create RPM package: {e}")
            return False
    
    def _prepare_build_dir(self):
        """准备构建目录"""
        try:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            
            self.build_dir.mkdir(parents=True)
            
            # 复制应用文件
            app_dir = self.build_dir / "app"
            app_dir.mkdir()
            
            # 复制主要文件
            source_dir = self.project_root / "shot_detection"
            if source_dir.exists():
                shutil.copytree(source_dir, app_dir / "shot_detection")
            
            # 复制其他必要文件
            for file_name in ["README.md", "LICENSE", "requirements.txt"]:
                source_file = self.project_root / file_name
                if source_file.exists():
                    shutil.copy2(source_file, app_dir)
            
            self.logger.debug("Build directory prepared")
            
        except Exception as e:
            self.logger.error(f"Failed to prepare build directory: {e}")
    
    def _generate_nsis_script(self) -> Path:
        """生成NSIS脚本"""
        try:
            nsis_content = f'''!define APP_NAME "{self.config.app_name}"
!define APP_VERSION "{self.config.app_version}"
!define APP_PUBLISHER "{self.config.app_publisher}"
!define APP_URL "{self.config.app_url}"
!define APP_DESCRIPTION "{self.config.app_description}"

; 包含现代UI
!include "MUI2.nsh"

; 基本设置
Name "${{APP_NAME}}"
OutFile "Shot-Detection-${{APP_VERSION}}-Setup.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""
RequestExecutionLevel {"admin" if self.config.require_admin else "user"}

; 界面设置
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

; 页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 语言
!insertmacro MUI_LANGUAGE "English"

; 安装部分
Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    SetOverwrite ifnewer
    
    ; 复制文件
    File /r "app\\*"
    
    ; 创建卸载程序
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    ; 注册表项
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "" $INSTDIR
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "URLInfoAbout" "${{APP_URL}}"
    
    ; 快捷方式
    {"CreateShortCut \\"$DESKTOP\\\\Shot Detection.lnk\\" \\"$INSTDIR\\\\shot-detection.exe\\"" if self.config.create_desktop_shortcut else ""}
    {"CreateDirectory \\"$SMPROGRAMS\\\\${{APP_NAME}}\\"" if self.config.create_start_menu_shortcut else ""}
    {"CreateShortCut \\"$SMPROGRAMS\\\\${{APP_NAME}}\\\\Shot Detection.lnk\\" \\"$INSTDIR\\\\shot-detection.exe\\"" if self.config.create_start_menu_shortcut else ""}
    
    ; 添加到PATH
    {"EnvVarUpdate $0 \\"PATH\\" \\"A\\" \\"HKLM\\" \\"$INSTDIR\\"" if self.config.add_to_path else ""}
SectionEnd

; 卸载部分
Section "Uninstall"
    ; 删除文件
    RMDir /r "$INSTDIR"
    
    ; 删除快捷方式
    Delete "$DESKTOP\\Shot Detection.lnk"
    RMDir /r "$SMPROGRAMS\\${{APP_NAME}}"
    
    ; 删除注册表项
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
    DeleteRegKey HKCU "Software\\${{APP_NAME}}"
    
    ; 从PATH移除
    {"EnvVarUpdate $0 \\"PATH\\" \\"R\\" \\"HKLM\\" \\"$INSTDIR\\"" if self.config.add_to_path else ""}
SectionEnd
'''
            
            nsis_file = self.build_dir / "installer.nsi"
            with open(nsis_file, 'w', encoding='utf-8') as f:
                f.write(nsis_content)
            
            self.logger.debug("NSIS script generated")
            return nsis_file
            
        except Exception as e:
            self.logger.error(f"Failed to generate NSIS script: {e}")
            return Path("installer.nsi")
    
    def _compile_nsis_script(self, nsis_script: Path) -> bool:
        """编译NSIS脚本"""
        try:
            import subprocess
            
            # 查找NSIS编译器
            nsis_paths = [
                "C:\\Program Files (x86)\\NSIS\\makensis.exe",
                "C:\\Program Files\\NSIS\\makensis.exe",
                "makensis"
            ]
            
            makensis = None
            for path in nsis_paths:
                if shutil.which(path):
                    makensis = path
                    break
            
            if not makensis:
                self.logger.error("NSIS compiler not found")
                return False
            
            # 编译
            result = subprocess.run(
                [makensis, str(nsis_script)],
                cwd=self.build_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("Windows installer created successfully")
                return True
            else:
                self.logger.error(f"NSIS compilation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to compile NSIS script: {e}")
            return False
    
    def _create_app_bundle(self) -> Path:
        """创建macOS应用包"""
        try:
            app_name = f"{self.config.app_name}.app"
            app_bundle = self.build_dir / app_name
            
            # 创建应用包结构
            contents_dir = app_bundle / "Contents"
            macos_dir = contents_dir / "MacOS"
            resources_dir = contents_dir / "Resources"
            
            for dir_path in [contents_dir, macos_dir, resources_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # 创建Info.plist
            info_plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>{self.config.app_name}</string>
    <key>CFBundleDisplayName</key>
    <string>{self.config.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.shotdetection.app</string>
    <key>CFBundleVersion</key>
    <string>{self.config.app_version}</string>
    <key>CFBundleShortVersionString</key>
    <string>{self.config.app_version}</string>
    <key>CFBundleExecutable</key>
    <string>shot-detection</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
</dict>
</plist>'''
            
            with open(contents_dir / "Info.plist", 'w') as f:
                f.write(info_plist)
            
            # 复制应用文件
            app_files = self.build_dir / "app"
            if app_files.exists():
                shutil.copytree(app_files, resources_dir / "app")
            
            self.logger.debug("macOS app bundle created")
            return app_bundle
            
        except Exception as e:
            self.logger.error(f"Failed to create app bundle: {e}")
            return Path("app.bundle")
    
    def _create_pkg_installer(self, app_bundle: Path) -> bool:
        """创建PKG安装包"""
        try:
            import subprocess
            
            pkg_file = self.build_dir / f"{self.config.app_name}-{self.config.app_version}.pkg"
            
            result = subprocess.run([
                "pkgbuild",
                "--root", str(app_bundle.parent),
                "--identifier", "com.shotdetection.pkg",
                "--version", self.config.app_version,
                "--install-location", "/Applications",
                str(pkg_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("macOS installer created successfully")
                return True
            else:
                self.logger.error(f"PKG creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create PKG installer: {e}")
            return False
    
    def _create_install_script(self) -> Path:
        """创建Linux安装脚本"""
        try:
            install_script_content = f'''#!/bin/bash

APP_NAME="{self.config.app_name}"
APP_VERSION="{self.config.app_version}"
INSTALL_DIR="/opt/shot-detection"

echo "Installing $APP_NAME $APP_VERSION..."

# 创建安装目录
sudo mkdir -p "$INSTALL_DIR"

# 复制文件
sudo cp -r app/* "$INSTALL_DIR/"

# 创建符号链接
sudo ln -sf "$INSTALL_DIR/shot-detection" "/usr/local/bin/shot-detection"

# 创建桌面文件
cat > /tmp/shot-detection.desktop << EOF
[Desktop Entry]
Name={self.config.app_name}
Comment={self.config.app_description}
Exec=/usr/local/bin/shot-detection
Icon=$INSTALL_DIR/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Video;
EOF

sudo mv /tmp/shot-detection.desktop /usr/share/applications/

echo "Installation completed successfully!"
'''
            
            install_script = self.build_dir / "install.sh"
            with open(install_script, 'w') as f:
                f.write(install_script_content)
            
            # 设置执行权限
            install_script.chmod(0o755)
            
            self.logger.debug("Linux install script created")
            return install_script
            
        except Exception as e:
            self.logger.error(f"Failed to create install script: {e}")
            return Path("install.sh")
    
    def _create_makeself_installer(self, install_script: Path) -> bool:
        """创建makeself自解压安装包"""
        try:
            import subprocess
            
            installer_file = self.build_dir / f"shot-detection-{self.config.app_version}-installer.run"
            
            result = subprocess.run([
                "makeself",
                str(self.build_dir),
                str(installer_file),
                f"{self.config.app_name} {self.config.app_version} Installer",
                "./install.sh"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Linux installer created successfully")
                return True
            else:
                self.logger.error(f"makeself creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create makeself installer: {e}")
            return False
    
    def _create_debian_structure(self):
        """创建Debian包结构"""
        try:
            debian_dir = self.build_dir / "debian"
            debian_dir.mkdir(exist_ok=True)
            
            # 创建control文件
            control_content = f'''Package: shot-detection
Version: {self.config.app_version}
Section: video
Priority: optional
Architecture: all
Depends: python3, python3-pip, python3-opencv, python3-numpy
Maintainer: {self.config.app_publisher} <team@shot-detection.com>
Description: {self.config.app_description}
 Advanced video shot detection and analysis toolkit for automatic
 identification of shot boundaries in video content.
'''
            
            with open(debian_dir / "control", 'w') as f:
                f.write(control_content)
            
            # 创建postinst脚本
            postinst_content = '''#!/bin/bash
set -e

# 安装Python依赖
pip3 install -r /opt/shot-detection/requirements.txt

# 创建符号链接
ln -sf /opt/shot-detection/shot-detection /usr/local/bin/shot-detection

exit 0
'''
            
            postinst_file = debian_dir / "postinst"
            with open(postinst_file, 'w') as f:
                f.write(postinst_content)
            postinst_file.chmod(0o755)
            
            self.logger.debug("Debian package structure created")
            
        except Exception as e:
            self.logger.error(f"Failed to create Debian structure: {e}")
    
    def _build_debian_package(self) -> bool:
        """构建Debian包"""
        try:
            import subprocess
            
            result = subprocess.run([
                "dpkg-deb",
                "--build",
                str(self.build_dir),
                f"shot-detection_{self.config.app_version}_all.deb"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Debian package created successfully")
                return True
            else:
                self.logger.error(f"Debian package build failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to build Debian package: {e}")
            return False
    
    def _create_rpm_spec(self) -> Path:
        """创建RPM spec文件"""
        try:
            spec_content = f'''Name: shot-detection
Version: {self.config.app_version}
Release: 1%{{?dist}}
Summary: {self.config.app_description}

License: MIT
URL: {self.config.app_url}
Source0: %{{name}}-%{{version}}.tar.gz

BuildArch: noarch
Requires: python3, python3-pip, python3-opencv, python3-numpy

%description
{self.config.app_description}

%prep
%setup -q

%build
# 无需构建

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/opt/shot-detection
cp -r * $RPM_BUILD_ROOT/opt/shot-detection/

mkdir -p $RPM_BUILD_ROOT/usr/local/bin
ln -s /opt/shot-detection/shot-detection $RPM_BUILD_ROOT/usr/local/bin/shot-detection

%files
/opt/shot-detection/*
/usr/local/bin/shot-detection

%post
pip3 install -r /opt/shot-detection/requirements.txt

%changelog
* {datetime.now().strftime("%a %b %d %Y")} {self.config.app_publisher} <team@shot-detection.com> - {self.config.app_version}-1
- Initial package
'''
            
            spec_file = self.build_dir / "shot-detection.spec"
            with open(spec_file, 'w') as f:
                f.write(spec_content)
            
            self.logger.debug("RPM spec file created")
            return spec_file
            
        except Exception as e:
            self.logger.error(f"Failed to create RPM spec: {e}")
            return Path("shot-detection.spec")
    
    def _build_rpm_package(self, spec_file: Path) -> bool:
        """构建RPM包"""
        try:
            import subprocess
            
            result = subprocess.run([
                "rpmbuild",
                "-bb",
                str(spec_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("RPM package created successfully")
                return True
            else:
                self.logger.error(f"RPM package build failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to build RPM package: {e}")
            return False
    
    def create_all_installers(self) -> Dict[str, bool]:
        """
        创建所有平台的安装程序
        
        Returns:
            各平台安装程序的创建结果
        """
        try:
            self.logger.info("Creating all installers")
            
            results = {}
            
            # Windows安装程序
            results['windows'] = self.create_windows_installer()
            
            # macOS安装程序
            results['macos'] = self.create_macos_installer()
            
            # Linux安装程序
            results['linux'] = self.create_linux_installer()
            
            # Debian包
            results['deb'] = self.create_deb_package()
            
            # RPM包
            results['rpm'] = self.create_rpm_package()
            
            # 统计结果
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            self.logger.info(f"Installer creation completed: {successful}/{total} successful")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to create all installers: {e}")
            return {}
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            
            self.logger.info("Installer generator cleanup completed")
        except Exception as e:
            self.logger.error(f"Installer generator cleanup failed: {e}")
