"""
Project Manager
项目管理器 - 重构版本
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

from ..jianying_project_manager import JianYingProjectManager as LegacyProjectManager


class ProjectManager:
    """项目管理器 - 新架构版本"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化项目管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="ProjectManager")
        
        # 保持与旧版本的兼容性
        self.legacy_manager = LegacyProjectManager()
        
        # 项目配置
        self.project_config = self.config.get('project', {
            'default_resolution': (1920, 1080),
            'default_fps': 30.0,
            'auto_backup': True,
            'backup_interval': 300  # 5分钟
        })
        
        self.logger.info("Project manager initialized")
    
    def create_project(self, project_name: str, project_path: str,
                      video_files: List[str], **kwargs) -> Dict[str, Any]:
        """
        创建新项目
        
        Args:
            project_name: 项目名称
            project_path: 项目路径
            video_files: 视频文件列表
            **kwargs: 其他参数
            
        Returns:
            创建结果
        """
        try:
            self.logger.info(f"Creating project: {project_name}")
            
            # 创建项目目录
            project_dir = Path(project_path)
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # 使用旧版管理器创建基础项目
            legacy_result = self.legacy_manager.create_project(
                project_name=project_name,
                project_path=project_path,
                video_files=video_files
            )
            
            if not legacy_result.get("success", False):
                return legacy_result
            
            # 添加新架构的增强功能
            enhancements = self._add_project_enhancements(project_dir, kwargs)
            
            # 创建项目元数据
            metadata = self._create_project_metadata(
                project_name, project_path, video_files, kwargs
            )
            
            # 保存项目元数据
            metadata_file = project_dir / "project_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Project created successfully: {project_path}")
            
            return {
                "success": True,
                "project_path": project_path,
                "project_name": project_name,
                "files_created": legacy_result.get("files_created", []) + [str(metadata_file)],
                "metadata": metadata,
                "enhancements": enhancements
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_project(self, project_path: str) -> Dict[str, Any]:
        """
        加载项目
        
        Args:
            project_path: 项目路径
            
        Returns:
            加载结果
        """
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                return {
                    "success": False,
                    "error": f"Project directory not found: {project_path}"
                }
            
            # 加载项目元数据
            metadata_file = project_dir / "project_metadata.json"
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            # 检查项目文件完整性
            integrity_check = self._check_project_integrity(project_dir)
            
            # 加载项目数据
            project_data = self._load_project_data(project_dir)
            
            self.logger.info(f"Project loaded: {project_path}")
            
            return {
                "success": True,
                "project_path": project_path,
                "metadata": metadata,
                "project_data": project_data,
                "integrity_check": integrity_check
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_project(self, project_path: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存项目
        
        Args:
            project_path: 项目路径
            project_data: 项目数据
            
        Returns:
            保存结果
        """
        try:
            project_dir = Path(project_path)
            
            # 创建备份（如果启用）
            backup_result = None
            if self.project_config.get('auto_backup', True):
                backup_result = self._create_backup(project_dir)
            
            # 保存项目文件
            saved_files = []
            
            for file_key, data in project_data.items():
                if file_key.endswith('_data'):
                    file_name = file_key.replace('_data', '.json')
                    file_path = project_dir / file_name
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    
                    saved_files.append(str(file_path))
            
            # 更新元数据
            self._update_project_metadata(project_dir)
            
            self.logger.info(f"Project saved: {project_path}")
            
            return {
                "success": True,
                "project_path": project_path,
                "saved_files": saved_files,
                "backup_created": backup_result is not None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to save project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _add_project_enhancements(self, project_dir: Path, 
                                 kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """添加项目增强功能"""
        enhancements = {}
        
        try:
            # 1. 创建项目配置文件
            project_config = {
                "version": "2.0",
                "created_with": "Shot Detection v2.0",
                "features": {
                    "auto_backup": self.project_config.get('auto_backup', True),
                    "version_control": True,
                    "collaboration": False
                }
            }
            
            config_file = project_dir / "project_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(project_config, f, indent=2, ensure_ascii=False)
            
            enhancements["config_file"] = str(config_file)
            
            # 2. 创建资源目录结构
            directories = ["assets", "exports", "backups", "temp"]
            for dir_name in directories:
                dir_path = project_dir / dir_name
                dir_path.mkdir(exist_ok=True)
                enhancements[f"{dir_name}_dir"] = str(dir_path)
            
            # 3. 创建版本控制
            if kwargs.get('enable_version_control', True):
                version_file = project_dir / "version_history.json"
                version_data = {
                    "current_version": 1,
                    "history": [{
                        "version": 1,
                        "created_at": self._get_current_timestamp(),
                        "description": "Initial project creation"
                    }]
                }
                
                with open(version_file, 'w', encoding='utf-8') as f:
                    json.dump(version_data, f, indent=2, ensure_ascii=False)
                
                enhancements["version_control"] = str(version_file)
            
        except Exception as e:
            self.logger.warning(f"Failed to add some enhancements: {e}")
        
        return enhancements
    
    def _create_project_metadata(self, project_name: str, project_path: str,
                               video_files: List[str], kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """创建项目元数据"""
        metadata = {
            "project_name": project_name,
            "project_path": project_path,
            "created_at": self._get_current_timestamp(),
            "last_modified": self._get_current_timestamp(),
            "version": "2.0",
            "source_videos": {
                "count": len(video_files),
                "files": video_files
            },
            "project_settings": {
                "resolution": kwargs.get('resolution', self.project_config['default_resolution']),
                "fps": kwargs.get('fps', self.project_config['default_fps']),
                "project_type": kwargs.get('project_type', 'standard')
            },
            "statistics": {
                "total_edits": 0,
                "export_count": 0,
                "last_export": None
            }
        }
        
        return metadata
    
    def _check_project_integrity(self, project_dir: Path) -> Dict[str, Any]:
        """检查项目完整性"""
        integrity = {
            "valid": True,
            "missing_files": [],
            "corrupted_files": [],
            "warnings": []
        }
        
        # 检查必需文件
        required_files = [
            "draft_content.json",
            "draft_meta_info.json", 
            "draft_virtual_store.json"
        ]
        
        for file_name in required_files:
            file_path = project_dir / file_name
            if not file_path.exists():
                integrity["missing_files"].append(file_name)
                integrity["valid"] = False
            else:
                # 检查文件是否可以正常解析
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    integrity["corrupted_files"].append(file_name)
                    integrity["valid"] = False
        
        return integrity
    
    def _load_project_data(self, project_dir: Path) -> Dict[str, Any]:
        """加载项目数据"""
        project_data = {}
        
        json_files = list(project_dir.glob("*.json"))
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    key = json_file.stem + "_data"
                    project_data[key] = data
            except Exception as e:
                self.logger.warning(f"Failed to load {json_file}: {e}")
        
        return project_data
    
    def _create_backup(self, project_dir: Path) -> Optional[str]:
        """创建项目备份"""
        try:
            import shutil
            from datetime import datetime
            
            backup_dir = project_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = backup_dir / backup_name
            
            # 复制项目文件到备份目录
            shutil.copytree(project_dir, backup_path, 
                          ignore=shutil.ignore_patterns("backups", "temp", "__pycache__"))
            
            self.logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")
            return None
    
    def _update_project_metadata(self, project_dir: Path):
        """更新项目元数据"""
        try:
            metadata_file = project_dir / "project_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                metadata["last_modified"] = self._get_current_timestamp()
                metadata["statistics"]["total_edits"] += 1
                
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
        except Exception as e:
            self.logger.warning(f"Failed to update metadata: {e}")
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("Project manager cleanup completed")
