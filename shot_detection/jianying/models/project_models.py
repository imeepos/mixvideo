"""
Project Models
项目数据模型
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path


@dataclass
class VideoResource:
    """视频资源模型"""
    path: str
    name: str
    duration: float = 0.0
    resolution: tuple = (1920, 1080)
    fps: float = 30.0
    file_size: int = 0
    format: str = "mp4"
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.name:
            self.name = Path(self.path).name
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "path": self.path,
            "name": self.name,
            "duration": self.duration,
            "resolution": self.resolution,
            "fps": self.fps,
            "file_size": self.file_size,
            "format": self.format,
            "quality_score": self.quality_score,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoResource':
        """从字典创建"""
        return cls(**data)


@dataclass
class DraftContent:
    """草稿内容模型"""
    tracks: List[Dict[str, Any]] = field(default_factory=list)
    materials: List[Dict[str, Any]] = field(default_factory=list)
    canvas_config: Dict[str, Any] = field(default_factory=dict)
    version: str = "2.0"
    
    def add_track(self, track_type: str, track_data: Dict[str, Any]):
        """添加轨道"""
        track = {
            "id": len(self.tracks),
            "type": track_type,
            "data": track_data,
            "created_at": self._get_timestamp()
        }
        self.tracks.append(track)
    
    def add_material(self, material_type: str, material_data: Dict[str, Any]):
        """添加素材"""
        material = {
            "id": len(self.materials),
            "type": material_type,
            "data": material_data,
            "created_at": self._get_timestamp()
        }
        self.materials.append(material)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "tracks": self.tracks,
            "materials": self.materials,
            "canvas_config": self.canvas_config,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DraftContent':
        """从字典创建"""
        return cls(
            tracks=data.get("tracks", []),
            materials=data.get("materials", []),
            canvas_config=data.get("canvas_config", {}),
            version=data.get("version", "2.0")
        )
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()


@dataclass
class JianYingProject:
    """剪映项目模型"""
    name: str
    path: str
    draft_content: DraftContent = field(default_factory=DraftContent)
    video_resources: List[VideoResource] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    last_modified: Optional[str] = None
    version: str = "2.0"
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.created_at:
            self.created_at = self._get_timestamp()
        if not self.last_modified:
            self.last_modified = self.created_at
    
    def add_video_resource(self, video_path: str, **kwargs) -> VideoResource:
        """添加视频资源"""
        video_resource = VideoResource(path=video_path, **kwargs)
        self.video_resources.append(video_resource)
        self._update_modified_time()
        return video_resource
    
    def remove_video_resource(self, video_path: str) -> bool:
        """移除视频资源"""
        for i, resource in enumerate(self.video_resources):
            if resource.path == video_path:
                del self.video_resources[i]
                self._update_modified_time()
                return True
        return False
    
    def get_video_resource(self, video_path: str) -> Optional[VideoResource]:
        """获取视频资源"""
        for resource in self.video_resources:
            if resource.path == video_path:
                return resource
        return None
    
    def get_project_statistics(self) -> Dict[str, Any]:
        """获取项目统计信息"""
        total_duration = sum(resource.duration for resource in self.video_resources)
        total_size = sum(resource.file_size for resource in self.video_resources)
        
        return {
            "video_count": len(self.video_resources),
            "total_duration": total_duration,
            "total_size": total_size,
            "track_count": len(self.draft_content.tracks),
            "material_count": len(self.draft_content.materials),
            "created_at": self.created_at,
            "last_modified": self.last_modified
        }
    
    def export_to_jianying_format(self) -> Dict[str, Any]:
        """导出为剪映格式"""
        # 这里需要根据剪映的具体格式要求来实现
        # 暂时返回基本结构
        return {
            "draft_content": self.draft_content.to_dict(),
            "draft_meta_info": self._generate_meta_info(),
            "draft_virtual_store": self._generate_virtual_store()
        }
    
    def _generate_meta_info(self) -> Dict[str, Any]:
        """生成元信息"""
        materials = {
            "videos": [resource.to_dict() for resource in self.video_resources],
            "audios": [],
            "images": []
        }
        
        return {
            "create_time": self.created_at,
            "last_modify_time": self.last_modified,
            "materials": materials,
            "version": self.version
        }
    
    def _generate_virtual_store(self) -> Dict[str, Any]:
        """生成虚拟存储信息"""
        return {
            "version": self.version,
            "store_data": {}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "path": self.path,
            "draft_content": self.draft_content.to_dict(),
            "video_resources": [resource.to_dict() for resource in self.video_resources],
            "metadata": self.metadata,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JianYingProject':
        """从字典创建"""
        project = cls(
            name=data["name"],
            path=data["path"],
            draft_content=DraftContent.from_dict(data.get("draft_content", {})),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            last_modified=data.get("last_modified"),
            version=data.get("version", "2.0")
        )
        
        # 添加视频资源
        for resource_data in data.get("video_resources", []):
            resource = VideoResource.from_dict(resource_data)
            project.video_resources.append(resource)
        
        return project
    
    def _update_modified_time(self):
        """更新修改时间"""
        self.last_modified = self._get_timestamp()
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()


# 工厂函数
def create_project(name: str, path: str, video_files: List[str]) -> JianYingProject:
    """创建项目的工厂函数"""
    project = JianYingProject(name=name, path=path)
    
    for video_file in video_files:
        project.add_video_resource(video_file)
    
    return project


def load_project_from_path(project_path: str) -> Optional[JianYingProject]:
    """从路径加载项目"""
    try:
        import json
        
        project_dir = Path(project_path)
        metadata_file = project_dir / "project_metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return JianYingProject.from_dict(data)
        
        return None
        
    except Exception:
        return None
