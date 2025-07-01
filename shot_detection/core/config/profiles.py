"""
Configuration Profiles Management
配置文件管理
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger


class ProfileManager:
    """配置文件管理器"""
    
    def __init__(self, profiles_dir: Optional[str] = None):
        """
        初始化配置文件管理器
        
        Args:
            profiles_dir: 配置文件目录
        """
        self.logger = logger.bind(component="ProfileManager")
        
        # 配置文件目录
        self.profiles_dir = Path(profiles_dir or "./profiles")
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置文件索引
        self.profiles_index_file = self.profiles_dir / "index.json"
        
        # 配置文件数据
        self.profiles = {}
        
        # 当前活动配置文件
        self.active_profile = None
        
        # 加载配置文件
        self._load_profiles()
        
        self.logger.info("Profile manager initialized")
    
    def _load_profiles(self):
        """加载配置文件"""
        try:
            if self.profiles_index_file.exists():
                with open(self.profiles_index_file, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
                
                self.active_profile = index_data.get('active_profile')
                profile_list = index_data.get('profiles', [])
                
                # 加载每个配置文件
                for profile_info in profile_list:
                    profile_id = profile_info['id']
                    profile_file = self.profiles_dir / f"{profile_id}.json"
                    
                    if profile_file.exists():
                        profile = ConfigProfile.load_from_file(str(profile_file))
                        if profile:
                            self.profiles[profile_id] = profile
            else:
                # 创建默认配置文件
                self._create_default_profiles()
            
            self.logger.info(f"Loaded {len(self.profiles)} profiles")
            
        except Exception as e:
            self.logger.error(f"Failed to load profiles: {e}")
            self._create_default_profiles()
    
    def _save_profiles_index(self):
        """保存配置文件索引"""
        try:
            index_data = {
                'active_profile': self.active_profile,
                'profiles': [
                    {
                        'id': profile.profile_id,
                        'name': profile.name,
                        'description': profile.description,
                        'created_at': profile.created_at,
                        'updated_at': profile.updated_at
                    }
                    for profile in self.profiles.values()
                ],
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.profiles_index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Failed to save profiles index: {e}")
    
    def _create_default_profiles(self):
        """创建默认配置文件"""
        try:
            # 默认配置文件
            default_profile = ConfigProfile(
                profile_id="default",
                name="Default",
                description="Default configuration profile",
                config_data={
                    'detection': {
                        'algorithm': 'frame_difference',
                        'threshold': 0.5,
                        'min_shot_duration': 1.0
                    },
                    'processing': {
                        'max_workers': 4,
                        'chunk_size': 1000
                    },
                    'export': {
                        'format': 'json',
                        'include_metadata': True
                    }
                }
            )
            
            # 高性能配置文件
            performance_profile = ConfigProfile(
                profile_id="performance",
                name="High Performance",
                description="Optimized for high performance processing",
                config_data={
                    'detection': {
                        'algorithm': 'multi_algorithm',
                        'threshold': 0.3,
                        'min_shot_duration': 0.5
                    },
                    'processing': {
                        'max_workers': 8,
                        'chunk_size': 2000,
                        'enable_gpu': True,
                        'memory_limit_mb': 2048
                    },
                    'export': {
                        'format': 'json',
                        'include_metadata': True,
                        'compress_output': True
                    }
                }
            )
            
            # 高质量配置文件
            quality_profile = ConfigProfile(
                profile_id="quality",
                name="High Quality",
                description="Optimized for high quality detection",
                config_data={
                    'detection': {
                        'algorithm': 'histogram',
                        'threshold': 0.7,
                        'min_shot_duration': 2.0,
                        'enable_preprocessing': True
                    },
                    'processing': {
                        'max_workers': 2,
                        'chunk_size': 500,
                        'memory_limit_mb': 1024
                    },
                    'export': {
                        'format': 'json',
                        'include_metadata': True,
                        'include_thumbnails': True
                    }
                }
            )
            
            # 保存配置文件
            self.profiles['default'] = default_profile
            self.profiles['performance'] = performance_profile
            self.profiles['quality'] = quality_profile
            
            # 设置默认为活动配置文件
            self.active_profile = 'default'
            
            # 保存到文件
            for profile in self.profiles.values():
                self._save_profile(profile)
            
            self._save_profiles_index()
            
            self.logger.info("Default profiles created")
            
        except Exception as e:
            self.logger.error(f"Failed to create default profiles: {e}")
    
    def _save_profile(self, profile: 'ConfigProfile'):
        """保存配置文件"""
        try:
            profile_file = self.profiles_dir / f"{profile.profile_id}.json"
            profile.save_to_file(str(profile_file))
            
        except Exception as e:
            self.logger.error(f"Failed to save profile {profile.profile_id}: {e}")
    
    def create_profile(self, profile_id: str, name: str, description: str = "",
                      config_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        创建配置文件
        
        Args:
            profile_id: 配置文件ID
            name: 配置文件名称
            description: 配置文件描述
            config_data: 配置数据
            
        Returns:
            是否创建成功
        """
        try:
            if profile_id in self.profiles:
                self.logger.warning(f"Profile already exists: {profile_id}")
                return False
            
            profile = ConfigProfile(
                profile_id=profile_id,
                name=name,
                description=description,
                config_data=config_data or {}
            )
            
            self.profiles[profile_id] = profile
            self._save_profile(profile)
            self._save_profiles_index()
            
            self.logger.info(f"Profile created: {profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create profile {profile_id}: {e}")
            return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        删除配置文件
        
        Args:
            profile_id: 配置文件ID
            
        Returns:
            是否删除成功
        """
        try:
            if profile_id not in self.profiles:
                self.logger.warning(f"Profile not found: {profile_id}")
                return False
            
            if profile_id == 'default':
                self.logger.warning("Cannot delete default profile")
                return False
            
            # 如果是活动配置文件，切换到默认
            if self.active_profile == profile_id:
                self.active_profile = 'default'
            
            # 删除文件
            profile_file = self.profiles_dir / f"{profile_id}.json"
            if profile_file.exists():
                profile_file.unlink()
            
            # 从内存中移除
            del self.profiles[profile_id]
            
            self._save_profiles_index()
            
            self.logger.info(f"Profile deleted: {profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete profile {profile_id}: {e}")
            return False
    
    def get_profile(self, profile_id: str) -> Optional['ConfigProfile']:
        """
        获取配置文件
        
        Args:
            profile_id: 配置文件ID
            
        Returns:
            配置文件对象
        """
        return self.profiles.get(profile_id)
    
    def get_active_profile(self) -> Optional['ConfigProfile']:
        """获取活动配置文件"""
        if self.active_profile:
            return self.profiles.get(self.active_profile)
        return None
    
    def set_active_profile(self, profile_id: str) -> bool:
        """
        设置活动配置文件
        
        Args:
            profile_id: 配置文件ID
            
        Returns:
            是否设置成功
        """
        try:
            if profile_id not in self.profiles:
                self.logger.warning(f"Profile not found: {profile_id}")
                return False
            
            self.active_profile = profile_id
            self._save_profiles_index()
            
            self.logger.info(f"Active profile set to: {profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set active profile {profile_id}: {e}")
            return False
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """列出所有配置文件"""
        try:
            return [
                {
                    'id': profile.profile_id,
                    'name': profile.name,
                    'description': profile.description,
                    'created_at': profile.created_at,
                    'updated_at': profile.updated_at,
                    'is_active': profile.profile_id == self.active_profile
                }
                for profile in self.profiles.values()
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to list profiles: {e}")
            return []
    
    def duplicate_profile(self, source_profile_id: str, new_profile_id: str,
                         new_name: str, new_description: str = "") -> bool:
        """
        复制配置文件
        
        Args:
            source_profile_id: 源配置文件ID
            new_profile_id: 新配置文件ID
            new_name: 新配置文件名称
            new_description: 新配置文件描述
            
        Returns:
            是否复制成功
        """
        try:
            source_profile = self.get_profile(source_profile_id)
            if not source_profile:
                self.logger.warning(f"Source profile not found: {source_profile_id}")
                return False
            
            if new_profile_id in self.profiles:
                self.logger.warning(f"Target profile already exists: {new_profile_id}")
                return False
            
            # 创建新配置文件
            new_profile = ConfigProfile(
                profile_id=new_profile_id,
                name=new_name,
                description=new_description,
                config_data=source_profile.config_data.copy()
            )
            
            self.profiles[new_profile_id] = new_profile
            self._save_profile(new_profile)
            self._save_profiles_index()
            
            self.logger.info(f"Profile duplicated: {source_profile_id} -> {new_profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to duplicate profile: {e}")
            return False
    
    def export_profile(self, profile_id: str, export_path: str) -> bool:
        """
        导出配置文件
        
        Args:
            profile_id: 配置文件ID
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        try:
            profile = self.get_profile(profile_id)
            if not profile:
                self.logger.warning(f"Profile not found: {profile_id}")
                return False
            
            return profile.save_to_file(export_path)
            
        except Exception as e:
            self.logger.error(f"Failed to export profile {profile_id}: {e}")
            return False
    
    def import_profile(self, import_path: str, profile_id: Optional[str] = None) -> bool:
        """
        导入配置文件
        
        Args:
            import_path: 导入路径
            profile_id: 新配置文件ID（如果为None则使用文件中的ID）
            
        Returns:
            是否导入成功
        """
        try:
            profile = ConfigProfile.load_from_file(import_path)
            if not profile:
                return False
            
            # 如果指定了新ID，更新配置文件ID
            if profile_id:
                profile.profile_id = profile_id
            
            # 检查ID冲突
            if profile.profile_id in self.profiles:
                self.logger.warning(f"Profile ID already exists: {profile.profile_id}")
                return False
            
            self.profiles[profile.profile_id] = profile
            self._save_profile(profile)
            self._save_profiles_index()
            
            self.logger.info(f"Profile imported: {profile.profile_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import profile: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            self.profiles.clear()
            self.logger.info("Profile manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Profile manager cleanup failed: {e}")


class ConfigProfile:
    """配置文件"""
    
    def __init__(self, profile_id: str, name: str, description: str = "",
                 config_data: Optional[Dict[str, Any]] = None):
        """
        初始化配置文件
        
        Args:
            profile_id: 配置文件ID
            name: 配置文件名称
            description: 配置文件描述
            config_data: 配置数据
        """
        self.profile_id = profile_id
        self.name = name
        self.description = description
        self.config_data = config_data or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        self.logger = logger.bind(component="ConfigProfile")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键（支持点号分隔）
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            keys = key.split('.')
            value = self.config_data
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to get config '{key}': {e}")
            return default
    
    def set_config(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键（支持点号分隔）
            value: 配置值
        """
        try:
            keys = key.split('.')
            config = self.config_data
            
            # 导航到父级字典
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                elif not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            self.updated_at = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Failed to set config '{key}': {e}")
    
    def update_config(self, config_dict: Dict[str, Any]):
        """
        批量更新配置
        
        Args:
            config_dict: 配置字典
        """
        try:
            self._deep_merge(self.config_data, config_dict)
            self.updated_at = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Failed to update config: {e}")
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """深度合并字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config_data.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'profile_id': self.profile_id,
            'name': self.name,
            'description': self.description,
            'config_data': self.config_data,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigProfile':
        """从字典创建配置文件"""
        profile = cls(
            profile_id=data['profile_id'],
            name=data['name'],
            description=data.get('description', ''),
            config_data=data.get('config_data', {})
        )
        
        profile.created_at = data.get('created_at', profile.created_at)
        profile.updated_at = data.get('updated_at', profile.updated_at)
        
        return profile
    
    def save_to_file(self, file_path: str) -> bool:
        """
        保存到文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否保存成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save profile to file: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['ConfigProfile']:
        """
        从文件加载
        
        Args:
            file_path: 文件路径
            
        Returns:
            配置文件对象
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return cls.from_dict(data)
            
        except Exception as e:
            logger.error(f"Failed to load profile from file: {e}")
            return None
