#!/usr/bin/env python3
"""
剪映项目管理器

遍历指定目录下的所有子目录，管理剪映草稿项目。
每个项目包含3个JSON文件：
- draft_content.json (由 draft_content_manager.py 管理)
- draft_meta_info.json (由 draft_meta_manager.py 管理)
- draft_virtual_store.json (由 draft_meta_manager.py 管理)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging

# 导入本地管理器
from draft_meta_manager import DraftMetaManager
from draft_content_manager import DraftContentManager


@dataclass
class JianyingProject:
    """剪映项目信息"""
    name: str
    path: Path
    draft_content_path: Path
    draft_meta_info_path: Path
    draft_virtual_store_path: Path
    is_valid: bool = False
    error_message: str = ""


class JianyingProjectManager:
    """剪映项目管理器"""
    
    def __init__(self, base_directory: Union[str, Path]):
        """
        初始化项目管理器
        
        Args:
            base_directory: 包含剪映项目的基础目录
        """
        self.base_directory = Path(base_directory)
        self.projects: Dict[str, JianyingProject] = {}
        self.logger = logging.getLogger(__name__)
        
    def scan_projects(self) -> List[JianyingProject]:
        """
        扫描基础目录下的所有剪映项目
        
        Returns:
            发现的项目列表
        """
        self.projects.clear()
        
        if not self.base_directory.exists():
            self.logger.error(f"基础目录不存在: {self.base_directory}")
            return []
        
        self.logger.info(f"开始扫描剪映项目: {self.base_directory}")
        
        for item in self.base_directory.iterdir():
            if item.is_dir():
                project = self._analyze_project_directory(item)
                if project:
                    self.projects[project.name] = project
                    if project.is_valid:
                        self.logger.info(f"发现有效项目: {project.name}")
                    else:
                        self.logger.warning(f"发现无效项目: {project.name} - {project.error_message}")
        
        valid_count = sum(1 for p in self.projects.values() if p.is_valid)
        self.logger.info(f"扫描完成，发现 {len(self.projects)} 个项目，其中 {valid_count} 个有效")
        
        return list(self.projects.values())
    
    def _analyze_project_directory(self, project_dir: Path) -> Optional[JianyingProject]:
        """
        分析单个项目目录
        
        Args:
            project_dir: 项目目录路径
            
        Returns:
            项目信息，如果不是有效项目则返回None
        """
        project_name = project_dir.name
        
        # 检查必需的JSON文件
        draft_content_path = project_dir / "draft_content.json"
        draft_meta_info_path = project_dir / "draft_meta_info.json"
        draft_virtual_store_path = project_dir / "draft_virtual_store.json"
        
        project = JianyingProject(
            name=project_name,
            path=project_dir,
            draft_content_path=draft_content_path,
            draft_meta_info_path=draft_meta_info_path,
            draft_virtual_store_path=draft_virtual_store_path
        )
        
        # 验证文件存在性
        missing_files = []
        if not draft_content_path.exists():
            missing_files.append("draft_content.json")
        if not draft_meta_info_path.exists():
            missing_files.append("draft_meta_info.json")
        if not draft_virtual_store_path.exists():
            missing_files.append("draft_virtual_store.json")
        
        if missing_files:
            project.error_message = f"缺少文件: {', '.join(missing_files)}"
            return project
        
        # 验证JSON文件格式
        try:
            # 验证 draft_content.json
            with open(draft_content_path, 'r', encoding='utf-8') as f:
                content_data = json.load(f)
                if not isinstance(content_data, dict):
                    project.error_message = "draft_content.json 格式无效"
                    return project
            
            # 验证 draft_meta_info.json
            with open(draft_meta_info_path, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
                if not isinstance(meta_data, dict):
                    project.error_message = "draft_meta_info.json 格式无效"
                    return project
            
            # 验证 draft_virtual_store.json
            with open(draft_virtual_store_path, 'r', encoding='utf-8') as f:
                store_data = json.load(f)
                if not isinstance(store_data, dict):
                    project.error_message = "draft_virtual_store.json 格式无效"
                    return project
            
            project.is_valid = True
            
        except json.JSONDecodeError as e:
            project.error_message = f"JSON解析错误: {e}"
        except Exception as e:
            project.error_message = f"文件读取错误: {e}"
        
        return project
    
    def get_project(self, project_name: str) -> Optional[JianyingProject]:
        """
        获取指定名称的项目
        
        Args:
            project_name: 项目名称
            
        Returns:
            项目信息，如果不存在则返回None
        """
        return self.projects.get(project_name)
    
    def get_valid_projects(self) -> List[JianyingProject]:
        """
        获取所有有效的项目
        
        Returns:
            有效项目列表
        """
        return [p for p in self.projects.values() if p.is_valid]
    
    def get_project_content_manager(self, project_name: str) -> Optional[DraftContentManager]:
        """
        获取项目的内容管理器
        
        Args:
            project_name: 项目名称
            
        Returns:
            内容管理器实例，如果项目不存在或无效则返回None
        """
        project = self.get_project(project_name)
        if not project or not project.is_valid:
            return None
        
        try:
            return DraftContentManager(project.path)
        except Exception as e:
            self.logger.error(f"创建内容管理器失败: {e}")
            return None
    
    def get_project_meta_manager(self, project_name: str) -> Optional[DraftMetaManager]:
        """
        获取项目的元数据管理器
        
        Args:
            project_name: 项目名称
            
        Returns:
            元数据管理器实例，如果项目不存在或无效则返回None
        """
        project = self.get_project(project_name)
        if not project or not project.is_valid:
            return None
        
        try:
            return DraftMetaManager(project.path)
        except Exception as e:
            self.logger.error(f"创建元数据管理器失败: {e}")
            return None
    
    def create_new_project(self, project_name: str, template_data: Optional[Dict] = None) -> bool:
        """
        创建新的剪映项目
        
        Args:
            project_name: 项目名称
            template_data: 模板数据（可选）
            
        Returns:
            创建是否成功
        """
        project_dir = self.base_directory / project_name
        
        if project_dir.exists():
            self.logger.error(f"项目已存在: {project_name}")
            return False
        
        try:
            # 创建项目目录
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建元数据管理器并初始化
            meta_manager = DraftMetaManager(project_dir)
            meta_manager.create_new_project()
            
            # 创建内容管理器并初始化
            content_manager = DraftContentManager(project_dir)
            content_manager.create_new_project(template_data)
            
            # 重新扫描以更新项目列表
            self.scan_projects()
            
            self.logger.info(f"成功创建项目: {project_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"创建项目失败: {e}")
            # 清理失败的项目目录
            if project_dir.exists():
                import shutil
                shutil.rmtree(project_dir, ignore_errors=True)
            return False
    
    def delete_project(self, project_name: str) -> bool:
        """
        删除项目
        
        Args:
            project_name: 项目名称
            
        Returns:
            删除是否成功
        """
        project = self.get_project(project_name)
        if not project:
            self.logger.error(f"项目不存在: {project_name}")
            return False
        
        try:
            import shutil
            shutil.rmtree(project.path)
            
            # 从项目列表中移除
            if project_name in self.projects:
                del self.projects[project_name]
            
            self.logger.info(f"成功删除项目: {project_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"删除项目失败: {e}")
            return False
    
    def get_project_summary(self) -> Dict[str, Any]:
        """
        获取项目摘要信息
        
        Returns:
            包含项目统计信息的字典
        """
        valid_projects = self.get_valid_projects()
        invalid_projects = [p for p in self.projects.values() if not p.is_valid]
        
        return {
            "base_directory": str(self.base_directory),
            "total_projects": len(self.projects),
            "valid_projects": len(valid_projects),
            "invalid_projects": len(invalid_projects),
            "valid_project_names": [p.name for p in valid_projects],
            "invalid_project_info": [
                {"name": p.name, "error": p.error_message}
                for p in invalid_projects
            ]
        }

    def update_project_resources(self, project_name: str, video_assignments: list):
        """
        更新项目的资源信息

        Args:
            project_name: 项目名称
            video_assignments: 视频分配列表 [(位置索引, VideoFile), ...]
        """
        try:
            # 从项目名称中提取原始模板名称
            original_name = project_name.split('_第')[0]

            if original_name in self.projects:
                project = self.projects[original_name]

                # 记录资源更新信息
                self.logger.info(f"更新项目 '{original_name}' 的资源信息:")
                self.logger.info(f"  - 分配的视频数量: {len(video_assignments)}")

                for position, video_file in video_assignments:
                    self.logger.debug(f"  - 位置 {position}: {video_file.name}")

                # 这里可以添加更多的资源更新逻辑
                # 比如更新项目的元数据、统计信息等

                self.logger.info(f"项目 '{original_name}' 资源更新完成")
                return True
            else:
                self.logger.warning(f"项目 '{original_name}' 不存在，无法更新资源")
                return False

        except Exception as e:
            self.logger.error(f"更新项目资源失败: {e}")
            return False

    def get_valid_projects_dict(self):
        """获取所有有效项目的字典"""
        valid_projects = {}
        for name, project in self.projects.items():
            if project.is_valid:
                valid_projects[name] = {
                    'path': str(project.path),
                    'draft_content_path': str(project.draft_content_path),
                    'draft_meta_info_path': str(project.draft_meta_info_path),
                    'draft_virtual_store_path': str(project.draft_virtual_store_path)
                }
        return valid_projects


def main():
    """主函数 - 用于测试"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # 示例用法
    manager = JianyingProjectManager("./test_projects")
    
    # 扫描项目
    manager.scan_projects()

    # 打印摘要
    summary = manager.get_project_summary()
    print("项目摘要:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # 遍历有效项目
    for project in manager.get_valid_projects():
        print(f"\n处理项目: {project.name}")
        
        # 获取管理器
        content_mgr = manager.get_project_content_manager(project.name)
        meta_mgr = manager.get_project_meta_manager(project.name)
        
        if content_mgr and meta_mgr:
            print(f"  - 内容管理器: 可用")
            print(f"  - 元数据管理器: 可用")


if __name__ == "__main__":
    main()
