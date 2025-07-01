"""
Release Manager
发布管理器
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from .package_manager import PackageManager, PackageConfig
from .installer import InstallerGenerator, InstallerConfig
from .docker_builder import DockerBuilder, DockerConfig


class ReleaseConfig:
    """发布配置"""
    
    def __init__(self):
        """初始化发布配置"""
        self.version = "2.0.0"
        self.release_name = "Shot Detection v2.0.0"
        self.release_notes = ""
        self.is_prerelease = False
        self.is_draft = False
        self.create_packages = True
        self.create_installers = True
        self.create_docker_images = True
        self.upload_to_github = True
        self.upload_to_pypi = False
        self.upload_to_docker_hub = False
        self.run_tests = True
        self.generate_changelog = True
        self.tag_release = True


class ReleaseManager:
    """发布管理器"""
    
    def __init__(self, config: Optional[ReleaseConfig] = None):
        """
        初始化发布管理器
        
        Args:
            config: 发布配置
        """
        self.config = config or ReleaseConfig()
        self.logger = logger.bind(component="ReleaseManager")
        
        # 项目根目录
        self.project_root = Path(__file__).parent.parent.parent
        
        # 发布目录
        self.release_dir = self.project_root / "releases" / self.config.version
        
        # 组件管理器
        self.package_manager = None
        self.installer_generator = None
        self.docker_builder = None
        
        self.logger.info("Release manager initialized")
    
    def create_release(self) -> bool:
        """
        创建完整发布
        
        Returns:
            是否创建成功
        """
        try:
            self.logger.info(f"Creating release: {self.config.release_name}")
            
            # 准备发布环境
            if not self._prepare_release_environment():
                return False
            
            # 运行测试
            if self.config.run_tests:
                if not self._run_tests():
                    self.logger.error("Tests failed, aborting release")
                    return False
            
            # 生成变更日志
            if self.config.generate_changelog:
                self._generate_changelog()
            
            # 创建包
            if self.config.create_packages:
                if not self._create_packages():
                    self.logger.error("Package creation failed")
                    return False
            
            # 创建安装程序
            if self.config.create_installers:
                if not self._create_installers():
                    self.logger.error("Installer creation failed")
                    return False
            
            # 创建Docker镜像
            if self.config.create_docker_images:
                if not self._create_docker_images():
                    self.logger.error("Docker image creation failed")
                    return False
            
            # 标记发布
            if self.config.tag_release:
                self._tag_release()
            
            # 上传到各个平台
            self._upload_releases()
            
            # 生成发布报告
            self._generate_release_report()
            
            self.logger.info(f"Release created successfully: {self.config.release_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create release: {e}")
            return False
    
    def _prepare_release_environment(self) -> bool:
        """准备发布环境"""
        try:
            # 创建发布目录
            self.release_dir.mkdir(parents=True, exist_ok=True)
            
            # 初始化组件管理器
            package_config = PackageConfig()
            package_config.version = self.config.version
            self.package_manager = PackageManager(package_config)
            
            installer_config = InstallerConfig()
            installer_config.app_version = self.config.version
            self.installer_generator = InstallerGenerator(installer_config)
            
            docker_config = DockerConfig()
            docker_config.image_tag = self.config.version
            self.docker_builder = DockerBuilder(docker_config)
            
            # 验证环境
            if not self._verify_environment():
                return False
            
            self.logger.info("Release environment prepared")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare release environment: {e}")
            return False
    
    def _verify_environment(self) -> bool:
        """验证发布环境"""
        try:
            # 检查Git状态
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout.strip():
                self.logger.warning("Working directory has uncommitted changes")
                # 可以选择是否继续
            
            # 检查版本号
            if not self._verify_version():
                return False
            
            # 检查必要工具
            required_tools = ["git", "python"]
            for tool in required_tools:
                if not self._check_tool_available(tool):
                    self.logger.error(f"Required tool not found: {tool}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Environment verification failed: {e}")
            return False
    
    def _verify_version(self) -> bool:
        """验证版本号"""
        try:
            # 检查版本号格式
            version_parts = self.config.version.split('.')
            if len(version_parts) != 3:
                self.logger.error(f"Invalid version format: {self.config.version}")
                return False
            
            # 检查是否为新版本
            result = subprocess.run(
                ["git", "tag", "-l", f"v{self.config.version}"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout.strip():
                self.logger.error(f"Version {self.config.version} already exists")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Version verification failed: {e}")
            return False
    
    def _check_tool_available(self, tool: str) -> bool:
        """检查工具是否可用"""
        try:
            result = subprocess.run(
                [tool, "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _run_tests(self) -> bool:
        """运行测试"""
        try:
            self.logger.info("Running tests")
            
            # 运行单元测试
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("All tests passed")
                return True
            else:
                self.logger.error(f"Tests failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to run tests: {e}")
            return False
    
    def _generate_changelog(self):
        """生成变更日志"""
        try:
            self.logger.info("Generating changelog")
            
            # 获取上一个版本的标签
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            last_tag = result.stdout.strip() if result.returncode == 0 else ""
            
            # 获取提交历史
            if last_tag:
                git_range = f"{last_tag}..HEAD"
            else:
                git_range = "HEAD"
            
            result = subprocess.run(
                ["git", "log", git_range, "--pretty=format:%h %s", "--no-merges"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # 生成变更日志内容
            changelog_content = f"# Changelog for {self.config.version}\n\n"
            changelog_content += f"Release Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            
            if commits:
                changelog_content += "## Changes\n\n"
                for commit in commits:
                    changelog_content += f"- {commit}\n"
            else:
                changelog_content += "## Changes\n\n- Initial release\n"
            
            # 保存变更日志
            changelog_file = self.release_dir / "CHANGELOG.md"
            with open(changelog_file, 'w', encoding='utf-8') as f:
                f.write(changelog_content)
            
            self.logger.info("Changelog generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate changelog: {e}")
    
    def _create_packages(self) -> bool:
        """创建包"""
        try:
            self.logger.info("Creating packages")
            
            results = self.package_manager.create_all_packages()
            
            # 移动包到发布目录
            dist_dir = self.project_root / "dist"
            if dist_dir.exists():
                packages_dir = self.release_dir / "packages"
                packages_dir.mkdir(exist_ok=True)
                
                for package_file in dist_dir.glob("*"):
                    if package_file.is_file():
                        target_file = packages_dir / package_file.name
                        package_file.rename(target_file)
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            self.logger.info(f"Package creation completed: {successful}/{total} successful")
            return successful > 0
            
        except Exception as e:
            self.logger.error(f"Failed to create packages: {e}")
            return False
    
    def _create_installers(self) -> bool:
        """创建安装程序"""
        try:
            self.logger.info("Creating installers")
            
            results = self.installer_generator.create_all_installers()
            
            # 移动安装程序到发布目录
            installer_build_dir = self.project_root / "installer_build"
            if installer_build_dir.exists():
                installers_dir = self.release_dir / "installers"
                installers_dir.mkdir(exist_ok=True)
                
                # 查找生成的安装程序文件
                for installer_file in installer_build_dir.rglob("*"):
                    if installer_file.is_file() and installer_file.suffix in ['.exe', '.pkg', '.run', '.deb', '.rpm']:
                        target_file = installers_dir / installer_file.name
                        installer_file.rename(target_file)
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            self.logger.info(f"Installer creation completed: {successful}/{total} successful")
            return successful > 0
            
        except Exception as e:
            self.logger.error(f"Failed to create installers: {e}")
            return False
    
    def _create_docker_images(self) -> bool:
        """创建Docker镜像"""
        try:
            self.logger.info("Creating Docker images")
            
            # 构建镜像
            if not self.docker_builder.build_image():
                return False
            
            # 创建Docker Compose配置
            self.docker_builder.create_docker_compose()
            
            # 创建Kubernetes清单
            self.docker_builder.create_kubernetes_manifests()
            
            # 移动Docker相关文件到发布目录
            docker_dir = self.release_dir / "docker"
            docker_dir.mkdir(exist_ok=True)
            
            # 复制Docker Compose文件
            compose_file = self.project_root / "docker-compose.yml"
            if compose_file.exists():
                compose_file.rename(docker_dir / "docker-compose.yml")
            
            # 复制Kubernetes清单
            k8s_dir = self.project_root / "k8s"
            if k8s_dir.exists():
                target_k8s_dir = docker_dir / "k8s"
                k8s_dir.rename(target_k8s_dir)
            
            self.logger.info("Docker images created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create Docker images: {e}")
            return False
    
    def _tag_release(self):
        """标记发布"""
        try:
            tag_name = f"v{self.config.version}"
            
            # 创建标签
            subprocess.run([
                "git", "tag", "-a", tag_name,
                "-m", f"Release {self.config.version}"
            ], cwd=self.project_root, check=True)
            
            self.logger.info(f"Release tagged: {tag_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to tag release: {e}")
    
    def _upload_releases(self):
        """上传发布"""
        try:
            # 上传到GitHub
            if self.config.upload_to_github:
                self._upload_to_github()
            
            # 上传到PyPI
            if self.config.upload_to_pypi:
                self._upload_to_pypi()
            
            # 上传到Docker Hub
            if self.config.upload_to_docker_hub:
                self._upload_to_docker_hub()
                
        except Exception as e:
            self.logger.error(f"Failed to upload releases: {e}")
    
    def _upload_to_github(self):
        """上传到GitHub"""
        try:
            self.logger.info("Uploading to GitHub")
            
            # 推送标签
            subprocess.run([
                "git", "push", "origin", f"v{self.config.version}"
            ], cwd=self.project_root, check=True)
            
            # 使用GitHub CLI创建发布
            release_files = []
            
            # 收集发布文件
            for subdir in ["packages", "installers"]:
                subdir_path = self.release_dir / subdir
                if subdir_path.exists():
                    for file_path in subdir_path.glob("*"):
                        if file_path.is_file():
                            release_files.append(str(file_path))
            
            # 创建GitHub发布
            gh_command = [
                "gh", "release", "create", f"v{self.config.version}",
                "--title", self.config.release_name,
                "--notes-file", str(self.release_dir / "CHANGELOG.md")
            ]
            
            if self.config.is_prerelease:
                gh_command.append("--prerelease")
            
            if self.config.is_draft:
                gh_command.append("--draft")
            
            gh_command.extend(release_files)
            
            result = subprocess.run(gh_command, cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Successfully uploaded to GitHub")
            else:
                self.logger.error(f"GitHub upload failed: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"Failed to upload to GitHub: {e}")
    
    def _upload_to_pypi(self):
        """上传到PyPI"""
        try:
            self.logger.info("Uploading to PyPI")
            
            if self.package_manager:
                success = self.package_manager.upload_to_pypi()
                if success:
                    self.logger.info("Successfully uploaded to PyPI")
                else:
                    self.logger.error("PyPI upload failed")
                    
        except Exception as e:
            self.logger.error(f"Failed to upload to PyPI: {e}")
    
    def _upload_to_docker_hub(self):
        """上传到Docker Hub"""
        try:
            self.logger.info("Uploading to Docker Hub")
            
            if self.docker_builder:
                success = self.docker_builder.push_image("docker.io")
                if success:
                    self.logger.info("Successfully uploaded to Docker Hub")
                else:
                    self.logger.error("Docker Hub upload failed")
                    
        except Exception as e:
            self.logger.error(f"Failed to upload to Docker Hub: {e}")
    
    def _generate_release_report(self):
        """生成发布报告"""
        try:
            report = {
                "version": self.config.version,
                "release_name": self.config.release_name,
                "release_date": datetime.now().isoformat(),
                "is_prerelease": self.config.is_prerelease,
                "components": {
                    "packages": self.config.create_packages,
                    "installers": self.config.create_installers,
                    "docker_images": self.config.create_docker_images
                },
                "uploads": {
                    "github": self.config.upload_to_github,
                    "pypi": self.config.upload_to_pypi,
                    "docker_hub": self.config.upload_to_docker_hub
                },
                "files": []
            }
            
            # 收集发布文件信息
            for file_path in self.release_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.release_dir)
                    report["files"].append({
                        "path": str(relative_path),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
            
            # 保存报告
            report_file = self.release_dir / "release_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Release report generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate release report: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.package_manager:
                self.package_manager.cleanup()
            
            if self.installer_generator:
                self.installer_generator.cleanup()
            
            if self.docker_builder:
                self.docker_builder.cleanup()
            
            self.logger.info("Release manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Release manager cleanup failed: {e}")
