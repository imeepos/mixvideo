"""
JianYing Service
剪映服务 - 统一的剪映项目管理服务
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

from ..draft_content_manager import DraftContentManager
from ..draft_meta_manager import DraftMetaManager
from ..jianying_project_manager import JianYingProjectManager


class JianYingService:
    """剪映服务 - 提供统一的剪映项目管理接口"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化剪映服务
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="JianYingService")
        
        # 初始化管理器
        self.project_manager = JianYingProjectManager()
        self.content_manager = DraftContentManager()
        self.meta_manager = DraftMetaManager()
        
        self.logger.info("JianYing service initialized")
    
    def create_project(self, project_name: str, output_dir: str, 
                      video_files: List[str], **kwargs) -> Dict[str, Any]:
        """
        创建剪映项目
        
        Args:
            project_name: 项目名称
            output_dir: 输出目录
            video_files: 视频文件列表
            **kwargs: 其他参数
            
        Returns:
            创建结果
        """
        try:
            self.logger.info(f"Creating JianYing project: {project_name}")
            
            # 创建项目目录
            project_path = Path(output_dir) / project_name
            project_path.mkdir(parents=True, exist_ok=True)
            
            # 创建项目配置
            project_config = {
                "name": project_name,
                "output_dir": str(project_path),
                "video_files": video_files,
                "created_at": self._get_current_timestamp(),
                **kwargs
            }
            
            # 使用项目管理器创建项目
            result = self.project_manager.create_project(
                project_name=project_name,
                project_path=str(project_path),
                video_files=video_files
            )
            
            if result.get("success", False):
                self.logger.info(f"JianYing project created successfully: {project_path}")
                return {
                    "success": True,
                    "project_path": str(project_path),
                    "project_config": project_config,
                    "files_created": result.get("files_created", [])
                }
            else:
                error_msg = result.get("error", "Unknown error")
                self.logger.error(f"Failed to create JianYing project: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            self.logger.error(f"Exception in create_project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_project(self, project_path: str) -> Dict[str, Any]:
        """
        加载剪映项目
        
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
            
            # 检查必要的文件
            required_files = [
                "draft_content.json",
                "draft_meta_info.json",
                "draft_virtual_store.json"
            ]
            
            missing_files = []
            for file_name in required_files:
                if not (project_dir / file_name).exists():
                    missing_files.append(file_name)
            
            if missing_files:
                return {
                    "success": False,
                    "error": f"Missing required files: {missing_files}"
                }
            
            # 加载项目数据
            project_data = {}
            for file_name in required_files:
                file_path = project_dir / file_name
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data[file_name.replace('.json', '')] = json.load(f)
            
            self.logger.info(f"JianYing project loaded: {project_path}")
            return {
                "success": True,
                "project_path": project_path,
                "project_data": project_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_project(self, project_path: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新剪映项目
        
        Args:
            project_path: 项目路径
            updates: 更新内容
            
        Returns:
            更新结果
        """
        try:
            # 先加载项目
            load_result = self.load_project(project_path)
            if not load_result["success"]:
                return load_result
            
            project_data = load_result["project_data"]
            
            # 应用更新
            for key, value in updates.items():
                if key in project_data:
                    if isinstance(project_data[key], dict) and isinstance(value, dict):
                        project_data[key].update(value)
                    else:
                        project_data[key] = value
            
            # 保存更新后的数据
            project_dir = Path(project_path)
            for file_key, data in project_data.items():
                file_path = project_dir / f"{file_key}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JianYing project updated: {project_path}")
            return {
                "success": True,
                "project_path": project_path,
                "updated_files": list(project_data.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_project(self, project_path: str, export_format: str = "json") -> Dict[str, Any]:
        """
        导出剪映项目
        
        Args:
            project_path: 项目路径
            export_format: 导出格式
            
        Returns:
            导出结果
        """
        try:
            # 加载项目
            load_result = self.load_project(project_path)
            if not load_result["success"]:
                return load_result
            
            project_data = load_result["project_data"]
            
            # 创建导出文件
            export_file = Path(project_path) / f"export.{export_format}"
            
            if export_format == "json":
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2, ensure_ascii=False)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported export format: {export_format}"
                }
            
            self.logger.info(f"Project exported: {export_file}")
            return {
                "success": True,
                "export_file": str(export_file),
                "format": export_format
            }
            
        except Exception as e:
            self.logger.error(f"Failed to export project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_project_info(self, project_path: str) -> Dict[str, Any]:
        """
        获取项目信息
        
        Args:
            project_path: 项目路径
            
        Returns:
            项目信息
        """
        try:
            load_result = self.load_project(project_path)
            if not load_result["success"]:
                return load_result
            
            project_data = load_result["project_data"]
            
            # 提取关键信息
            meta_info = project_data.get("draft_meta_info", {})
            content_info = project_data.get("draft_content", {})
            
            # 统计信息
            materials = meta_info.get("materials", {})
            video_count = len(materials.get("videos", []))
            audio_count = len(materials.get("audios", []))
            image_count = len(materials.get("images", []))
            
            tracks = content_info.get("tracks", [])
            track_count = len(tracks)
            
            info = {
                "project_path": project_path,
                "project_name": Path(project_path).name,
                "material_counts": {
                    "videos": video_count,
                    "audios": audio_count,
                    "images": image_count,
                    "total": video_count + audio_count + image_count
                },
                "track_count": track_count,
                "created_at": meta_info.get("create_time"),
                "duration": meta_info.get("duration", 0)
            }
            
            return {
                "success": True,
                "project_info": info
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get project info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_current_timestamp(self) -> int:
        """获取当前时间戳"""
        import time
        return int(time.time() * 1000)
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("JianYing service cleanup completed")
