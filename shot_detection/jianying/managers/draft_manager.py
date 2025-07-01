"""
Draft Manager
草稿管理器
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

from ..draft_content_manager import DraftContentManager as LegacyDraftContentManager
from ..draft_meta_manager import DraftMetaManager as LegacyDraftMetaManager


class DraftManager:
    """草稿管理器 - 新架构版本"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化草稿管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="DraftManager")
        
        # 保持与旧版本的兼容性
        self.legacy_content_manager = LegacyDraftContentManager()
        self.legacy_meta_manager = LegacyDraftMetaManager()
        
        self.logger.info("Draft manager initialized")
    
    def create_draft(self, project_path: str, video_files: List[str], 
                    draft_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        创建草稿
        
        Args:
            project_path: 项目路径
            video_files: 视频文件列表
            draft_config: 草稿配置
            
        Returns:
            创建结果
        """
        try:
            self.logger.info(f"Creating draft for project: {project_path}")
            
            config = draft_config or {}
            
            # 创建草稿内容
            content_result = self._create_draft_content(video_files, config)
            
            # 创建草稿元信息
            meta_result = self._create_draft_meta(video_files, config)
            
            # 创建虚拟存储
            virtual_store_result = self._create_virtual_store(config)
            
            # 保存草稿文件
            save_result = self._save_draft_files(
                project_path, content_result, meta_result, virtual_store_result
            )
            
            if save_result["success"]:
                self.logger.info(f"Draft created successfully: {project_path}")
                return {
                    "success": True,
                    "project_path": project_path,
                    "files_created": save_result["files_created"],
                    "draft_content": content_result,
                    "draft_meta": meta_result
                }
            else:
                return save_result
                
        except Exception as e:
            self.logger.error(f"Failed to create draft: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def load_draft(self, project_path: str) -> Dict[str, Any]:
        """
        加载草稿
        
        Args:
            project_path: 项目路径
            
        Returns:
            加载结果
        """
        try:
            project_dir = Path(project_path)
            
            # 检查必要文件
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
                    "error": f"Missing draft files: {missing_files}"
                }
            
            # 加载草稿数据
            draft_data = {}
            for file_name in required_files:
                file_path = project_dir / file_name
                with open(file_path, 'r', encoding='utf-8') as f:
                    key = file_name.replace('.json', '')
                    draft_data[key] = json.load(f)
            
            self.logger.info(f"Draft loaded: {project_path}")
            return {
                "success": True,
                "project_path": project_path,
                "draft_data": draft_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load draft: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_draft(self, project_path: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新草稿
        
        Args:
            project_path: 项目路径
            updates: 更新内容
            
        Returns:
            更新结果
        """
        try:
            # 先加载现有草稿
            load_result = self.load_draft(project_path)
            if not load_result["success"]:
                return load_result
            
            draft_data = load_result["draft_data"]
            
            # 应用更新
            for key, value in updates.items():
                if key in draft_data:
                    if isinstance(draft_data[key], dict) and isinstance(value, dict):
                        draft_data[key].update(value)
                    else:
                        draft_data[key] = value
            
            # 保存更新后的数据
            project_dir = Path(project_path)
            updated_files = []
            
            for key, data in draft_data.items():
                file_path = project_dir / f"{key}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                updated_files.append(str(file_path))
            
            self.logger.info(f"Draft updated: {project_path}")
            return {
                "success": True,
                "project_path": project_path,
                "updated_files": updated_files
            }
            
        except Exception as e:
            self.logger.error(f"Failed to update draft: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_draft_content(self, video_files: List[str], 
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """创建草稿内容"""
        # 使用旧版管理器创建基础内容
        try:
            legacy_content = self.legacy_content_manager.create_content(video_files)
            
            # 添加新功能增强
            enhanced_content = self._enhance_draft_content(legacy_content, config)
            
            return enhanced_content
            
        except Exception as e:
            self.logger.warning(f"Legacy content creation failed, using fallback: {e}")
            return self._create_fallback_content(video_files, config)
    
    def _create_draft_meta(self, video_files: List[str], 
                          config: Dict[str, Any]) -> Dict[str, Any]:
        """创建草稿元信息"""
        try:
            legacy_meta = self.legacy_meta_manager.create_meta_info(video_files)
            
            # 添加新功能增强
            enhanced_meta = self._enhance_draft_meta(legacy_meta, config)
            
            return enhanced_meta
            
        except Exception as e:
            self.logger.warning(f"Legacy meta creation failed, using fallback: {e}")
            return self._create_fallback_meta(video_files, config)
    
    def _create_virtual_store(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建虚拟存储"""
        return {
            "version": "2.0",
            "store_data": {},
            "created_at": self._get_current_timestamp()
        }
    
    def _enhance_draft_content(self, legacy_content: Dict[str, Any], 
                              config: Dict[str, Any]) -> Dict[str, Any]:
        """增强草稿内容"""
        enhanced = legacy_content.copy()
        
        # 添加版本信息
        enhanced["version"] = "2.0"
        enhanced["created_with"] = "Shot Detection v2.0"
        
        # 添加配置信息
        if config:
            enhanced["config"] = config
        
        # 添加时间戳
        enhanced["created_at"] = self._get_current_timestamp()
        enhanced["last_modified"] = enhanced["created_at"]
        
        return enhanced
    
    def _enhance_draft_meta(self, legacy_meta: Dict[str, Any], 
                           config: Dict[str, Any]) -> Dict[str, Any]:
        """增强草稿元信息"""
        enhanced = legacy_meta.copy()
        
        # 添加版本信息
        enhanced["version"] = "2.0"
        enhanced["created_with"] = "Shot Detection v2.0"
        
        # 添加配置信息
        if config:
            enhanced["config"] = config
        
        return enhanced
    
    def _create_fallback_content(self, video_files: List[str], 
                                config: Dict[str, Any]) -> Dict[str, Any]:
        """创建备用草稿内容"""
        return {
            "version": "2.0",
            "tracks": [],
            "materials": [{"path": video, "type": "video"} for video in video_files],
            "canvas_config": config.get("canvas_config", {}),
            "created_at": self._get_current_timestamp()
        }
    
    def _create_fallback_meta(self, video_files: List[str], 
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """创建备用草稿元信息"""
        return {
            "version": "2.0",
            "create_time": self._get_current_timestamp(),
            "materials": {
                "videos": [{"path": video, "name": Path(video).name} for video in video_files],
                "audios": [],
                "images": []
            },
            "config": config
        }
    
    def _save_draft_files(self, project_path: str, content: Dict[str, Any],
                         meta: Dict[str, Any], virtual_store: Dict[str, Any]) -> Dict[str, Any]:
        """保存草稿文件"""
        try:
            project_dir = Path(project_path)
            project_dir.mkdir(parents=True, exist_ok=True)
            
            files_created = []
            
            # 保存草稿内容
            content_file = project_dir / "draft_content.json"
            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            files_created.append(str(content_file))
            
            # 保存草稿元信息
            meta_file = project_dir / "draft_meta_info.json"
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
            files_created.append(str(meta_file))
            
            # 保存虚拟存储
            store_file = project_dir / "draft_virtual_store.json"
            with open(store_file, 'w', encoding='utf-8') as f:
                json.dump(virtual_store, f, indent=2, ensure_ascii=False)
            files_created.append(str(store_file))
            
            return {
                "success": True,
                "files_created": files_created
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("Draft manager cleanup completed")
