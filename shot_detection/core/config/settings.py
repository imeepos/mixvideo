"""
Settings Management
设置管理
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from loguru import logger


class SettingsManager:
    """设置管理器"""
    
    def __init__(self, settings_dir: Optional[str] = None):
        """
        初始化设置管理器
        
        Args:
            settings_dir: 设置目录
        """
        self.logger = logger.bind(component="SettingsManager")
        
        # 设置目录
        self.settings_dir = Path(settings_dir or "./settings")
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        
        # 全局设置文件
        self.global_settings_file = self.settings_dir / "global.json"
        
        # 用户设置文件
        self.user_settings_file = self.settings_dir / "user.json"
        
        # 设置数据
        self.global_settings = {}
        self.user_settings = {}
        
        # 设置变更监听器
        self.change_listeners = []
        
        # 加载设置
        self._load_settings()
        
        self.logger.info("Settings manager initialized")
    
    def _load_settings(self):
        """加载设置"""
        try:
            # 加载全局设置
            if self.global_settings_file.exists():
                with open(self.global_settings_file, 'r', encoding='utf-8') as f:
                    self.global_settings = json.load(f)
            else:
                self.global_settings = self._create_default_global_settings()
                self._save_global_settings()
            
            # 加载用户设置
            if self.user_settings_file.exists():
                with open(self.user_settings_file, 'r', encoding='utf-8') as f:
                    self.user_settings = json.load(f)
            else:
                self.user_settings = self._create_default_user_settings()
                self._save_user_settings()
            
            self.logger.info("Settings loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            self.global_settings = self._create_default_global_settings()
            self.user_settings = self._create_default_user_settings()
    
    def _create_default_global_settings(self) -> Dict[str, Any]:
        """创建默认全局设置"""
        return {
            'app': {
                'name': 'Shot Detection',
                'version': '2.0.0',
                'build': '20240101',
                'copyright': '© 2024 Shot Detection Team'
            },
            'system': {
                'max_memory_usage_mb': 2048,
                'max_cpu_cores': 8,
                'temp_cleanup_interval_hours': 24,
                'log_retention_days': 30
            },
            'defaults': {
                'detection_algorithm': 'frame_difference',
                'export_format': 'json',
                'video_formats': ['.mp4', '.avi', '.mov', '.mkv'],
                'max_file_size_mb': 1024
            },
            'features': {
                'enable_gpu_acceleration': True,
                'enable_cloud_processing': False,
                'enable_plugins': True,
                'enable_analytics': True
            }
        }
    
    def _create_default_user_settings(self) -> Dict[str, Any]:
        """创建默认用户设置"""
        return {
            'ui': {
                'theme': 'default',
                'language': 'en_US',
                'font_size': 12,
                'window_size': [1200, 800],
                'window_position': [100, 100],
                'show_toolbar': True,
                'show_statusbar': True,
                'auto_save': True,
                'auto_save_interval_minutes': 5
            },
            'detection': {
                'default_threshold': 0.5,
                'preview_enabled': True,
                'auto_detect_on_load': False,
                'save_intermediate_results': False
            },
            'export': {
                'default_format': 'json',
                'include_metadata': True,
                'include_thumbnails': False,
                'compress_output': False,
                'output_directory': './output'
            },
            'recent': {
                'files': [],
                'projects': [],
                'max_recent_items': 10
            },
            'preferences': {
                'check_updates': True,
                'send_analytics': False,
                'show_tips': True,
                'confirm_delete': True
            }
        }
    
    def _save_global_settings(self):
        """保存全局设置"""
        try:
            with open(self.global_settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.global_settings, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("Global settings saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save global settings: {e}")
    
    def _save_user_settings(self):
        """保存用户设置"""
        try:
            with open(self.user_settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_settings, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("User settings saved")
            
            # 通知监听器
            self._notify_change_listeners('user')
            
        except Exception as e:
            self.logger.error(f"Failed to save user settings: {e}")
    
    def get_global_setting(self, key: str, default: Any = None) -> Any:
        """
        获取全局设置
        
        Args:
            key: 设置键（支持点号分隔）
            default: 默认值
            
        Returns:
            设置值
        """
        return self._get_setting(self.global_settings, key, default)
    
    def get_user_setting(self, key: str, default: Any = None) -> Any:
        """
        获取用户设置
        
        Args:
            key: 设置键（支持点号分隔）
            default: 默认值
            
        Returns:
            设置值
        """
        return self._get_setting(self.user_settings, key, default)
    
    def _get_setting(self, settings: Dict[str, Any], key: str, default: Any) -> Any:
        """获取设置值"""
        try:
            keys = key.split('.')
            value = settings
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to get setting '{key}': {e}")
            return default
    
    def set_global_setting(self, key: str, value: Any) -> bool:
        """
        设置全局设置
        
        Args:
            key: 设置键
            value: 设置值
            
        Returns:
            是否设置成功
        """
        try:
            if self._set_setting(self.global_settings, key, value):
                self._save_global_settings()
                self._notify_change_listeners('global')
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to set global setting '{key}': {e}")
            return False
    
    def set_user_setting(self, key: str, value: Any) -> bool:
        """
        设置用户设置
        
        Args:
            key: 设置键
            value: 设置值
            
        Returns:
            是否设置成功
        """
        try:
            if self._set_setting(self.user_settings, key, value):
                self._save_user_settings()
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to set user setting '{key}': {e}")
            return False
    
    def _set_setting(self, settings: Dict[str, Any], key: str, value: Any) -> bool:
        """设置值"""
        try:
            keys = key.split('.')
            current = settings
            
            # 导航到父级字典
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                elif not isinstance(current[k], dict):
                    current[k] = {}
                current = current[k]
            
            # 设置值
            current[keys[-1]] = value
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set setting '{key}': {e}")
            return False
    
    def add_recent_file(self, file_path: str) -> bool:
        """
        添加最近文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否添加成功
        """
        try:
            recent_files = self.get_user_setting('recent.files', [])
            
            # 移除已存在的项
            if file_path in recent_files:
                recent_files.remove(file_path)
            
            # 添加到开头
            recent_files.insert(0, file_path)
            
            # 限制数量
            max_items = self.get_user_setting('recent.max_recent_items', 10)
            recent_files = recent_files[:max_items]
            
            return self.set_user_setting('recent.files', recent_files)
            
        except Exception as e:
            self.logger.error(f"Failed to add recent file: {e}")
            return False
    
    def get_recent_files(self) -> List[str]:
        """获取最近文件列表"""
        return self.get_user_setting('recent.files', [])
    
    def clear_recent_files(self) -> bool:
        """清空最近文件列表"""
        return self.set_user_setting('recent.files', [])
    
    def add_recent_project(self, project_path: str) -> bool:
        """
        添加最近项目
        
        Args:
            project_path: 项目路径
            
        Returns:
            是否添加成功
        """
        try:
            recent_projects = self.get_user_setting('recent.projects', [])
            
            # 移除已存在的项
            if project_path in recent_projects:
                recent_projects.remove(project_path)
            
            # 添加到开头
            recent_projects.insert(0, project_path)
            
            # 限制数量
            max_items = self.get_user_setting('recent.max_recent_items', 10)
            recent_projects = recent_projects[:max_items]
            
            return self.set_user_setting('recent.projects', recent_projects)
            
        except Exception as e:
            self.logger.error(f"Failed to add recent project: {e}")
            return False
    
    def get_recent_projects(self) -> List[str]:
        """获取最近项目列表"""
        return self.get_user_setting('recent.projects', [])
    
    def clear_recent_projects(self) -> bool:
        """清空最近项目列表"""
        return self.set_user_setting('recent.projects', [])
    
    def export_settings(self, export_path: str, include_global: bool = True, 
                       include_user: bool = True) -> bool:
        """
        导出设置
        
        Args:
            export_path: 导出路径
            include_global: 是否包含全局设置
            include_user: 是否包含用户设置
            
        Returns:
            是否导出成功
        """
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'app_version': self.get_global_setting('app.version', '2.0.0')
            }
            
            if include_global:
                export_data['global_settings'] = self.global_settings
            
            if include_user:
                export_data['user_settings'] = self.user_settings
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Settings exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_settings(self, import_path: str, import_global: bool = True,
                       import_user: bool = True) -> bool:
        """
        导入设置
        
        Args:
            import_path: 导入路径
            import_global: 是否导入全局设置
            import_user: 是否导入用户设置
            
        Returns:
            是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if import_global and 'global_settings' in import_data:
                self.global_settings.update(import_data['global_settings'])
                self._save_global_settings()
            
            if import_user and 'user_settings' in import_data:
                self.user_settings.update(import_data['user_settings'])
                self._save_user_settings()
            
            self.logger.info(f"Settings imported from: {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")
            return False
    
    def reset_user_settings(self) -> bool:
        """重置用户设置为默认值"""
        try:
            self.user_settings = self._create_default_user_settings()
            self._save_user_settings()
            self.logger.info("User settings reset to default")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset user settings: {e}")
            return False
    
    def add_change_listener(self, listener: callable):
        """添加设置变更监听器"""
        if listener not in self.change_listeners:
            self.change_listeners.append(listener)
    
    def remove_change_listener(self, listener: callable):
        """移除设置变更监听器"""
        if listener in self.change_listeners:
            self.change_listeners.remove(listener)
    
    def _notify_change_listeners(self, settings_type: str):
        """通知设置变更监听器"""
        try:
            for listener in self.change_listeners:
                try:
                    listener(settings_type, self.get_all_settings())
                except Exception as e:
                    self.logger.error(f"Settings change listener error: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to notify change listeners: {e}")
    
    def get_all_settings(self) -> Dict[str, Any]:
        """获取所有设置"""
        return {
            'global': self.global_settings.copy(),
            'user': self.user_settings.copy()
        }
    
    def cleanup(self):
        """清理资源"""
        try:
            self.change_listeners.clear()
            self.logger.info("Settings manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Settings manager cleanup failed: {e}")


class UserSettings:
    """用户设置助手类"""
    
    def __init__(self, settings_manager: SettingsManager):
        """
        初始化用户设置助手
        
        Args:
            settings_manager: 设置管理器
        """
        self.settings_manager = settings_manager
        self.logger = logger.bind(component="UserSettings")
    
    @property
    def theme(self) -> str:
        """获取主题"""
        return self.settings_manager.get_user_setting('ui.theme', 'default')
    
    @theme.setter
    def theme(self, value: str):
        """设置主题"""
        self.settings_manager.set_user_setting('ui.theme', value)
    
    @property
    def language(self) -> str:
        """获取语言"""
        return self.settings_manager.get_user_setting('ui.language', 'en_US')
    
    @language.setter
    def language(self, value: str):
        """设置语言"""
        self.settings_manager.set_user_setting('ui.language', value)
    
    @property
    def font_size(self) -> int:
        """获取字体大小"""
        return self.settings_manager.get_user_setting('ui.font_size', 12)
    
    @font_size.setter
    def font_size(self, value: int):
        """设置字体大小"""
        self.settings_manager.set_user_setting('ui.font_size', value)
    
    @property
    def auto_save(self) -> bool:
        """获取自动保存设置"""
        return self.settings_manager.get_user_setting('ui.auto_save', True)
    
    @auto_save.setter
    def auto_save(self, value: bool):
        """设置自动保存"""
        self.settings_manager.set_user_setting('ui.auto_save', value)
    
    @property
    def auto_save_interval(self) -> int:
        """获取自动保存间隔（分钟）"""
        return self.settings_manager.get_user_setting('ui.auto_save_interval_minutes', 5)
    
    @auto_save_interval.setter
    def auto_save_interval(self, value: int):
        """设置自动保存间隔"""
        self.settings_manager.set_user_setting('ui.auto_save_interval_minutes', value)
    
    @property
    def default_threshold(self) -> float:
        """获取默认检测阈值"""
        return self.settings_manager.get_user_setting('detection.default_threshold', 0.5)
    
    @default_threshold.setter
    def default_threshold(self, value: float):
        """设置默认检测阈值"""
        self.settings_manager.set_user_setting('detection.default_threshold', value)
    
    @property
    def preview_enabled(self) -> bool:
        """获取预览启用状态"""
        return self.settings_manager.get_user_setting('detection.preview_enabled', True)
    
    @preview_enabled.setter
    def preview_enabled(self, value: bool):
        """设置预览启用状态"""
        self.settings_manager.set_user_setting('detection.preview_enabled', value)
    
    @property
    def output_directory(self) -> str:
        """获取输出目录"""
        return self.settings_manager.get_user_setting('export.output_directory', './output')
    
    @output_directory.setter
    def output_directory(self, value: str):
        """设置输出目录"""
        self.settings_manager.set_user_setting('export.output_directory', value)
    
    @property
    def default_export_format(self) -> str:
        """获取默认导出格式"""
        return self.settings_manager.get_user_setting('export.default_format', 'json')
    
    @default_export_format.setter
    def default_export_format(self, value: str):
        """设置默认导出格式"""
        self.settings_manager.set_user_setting('export.default_format', value)
    
    def get_window_geometry(self) -> Dict[str, Any]:
        """获取窗口几何信息"""
        return {
            'size': self.settings_manager.get_user_setting('ui.window_size', [1200, 800]),
            'position': self.settings_manager.get_user_setting('ui.window_position', [100, 100])
        }
    
    def set_window_geometry(self, size: List[int], position: List[int]):
        """设置窗口几何信息"""
        self.settings_manager.set_user_setting('ui.window_size', size)
        self.settings_manager.set_user_setting('ui.window_position', position)
    
    def get_ui_state(self) -> Dict[str, bool]:
        """获取UI状态"""
        return {
            'show_toolbar': self.settings_manager.get_user_setting('ui.show_toolbar', True),
            'show_statusbar': self.settings_manager.get_user_setting('ui.show_statusbar', True)
        }
    
    def set_ui_state(self, show_toolbar: bool, show_statusbar: bool):
        """设置UI状态"""
        self.settings_manager.set_user_setting('ui.show_toolbar', show_toolbar)
        self.settings_manager.set_user_setting('ui.show_statusbar', show_statusbar)
