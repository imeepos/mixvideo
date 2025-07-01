"""
Plugin Configuration Management
插件配置管理
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger


class PluginConfig:
    """插件配置管理器"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化插件配置管理器
        
        Args:
            config_dir: 配置目录路径
        """
        self.logger = logger.bind(component="PluginConfig")
        self.config_dir = Path(config_dir or "./plugins/config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 全局插件配置
        self.global_config = {}
        
        # 插件特定配置
        self.plugin_configs = {}
        
        # 加载配置
        self._load_global_config()
        self._load_plugin_configs()
        
        self.logger.info("Plugin config manager initialized")
    
    def _load_global_config(self):
        """加载全局插件配置"""
        try:
            global_config_file = self.config_dir / "plugins.yaml"
            
            if global_config_file.exists():
                with open(global_config_file, 'r', encoding='utf-8') as f:
                    self.global_config = yaml.safe_load(f) or {}
            else:
                # 创建默认全局配置
                self.global_config = {
                    'enabled': True,
                    'auto_load': True,
                    'plugin_directories': ['./plugins'],
                    'max_load_time': 30,
                    'enable_sandboxing': True,
                    'allowed_imports': [
                        'os', 'sys', 'json', 'yaml', 'pathlib',
                        'numpy', 'cv2', 'PIL', 'matplotlib'
                    ],
                    'blocked_imports': [
                        'subprocess', 'socket', 'urllib', 'requests'
                    ],
                    'resource_limits': {
                        'max_memory_mb': 512,
                        'max_cpu_percent': 50,
                        'max_execution_time': 300
                    }
                }
                self._save_global_config()
            
            self.logger.info("Global plugin config loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to load global plugin config: {e}")
    
    def _save_global_config(self):
        """保存全局插件配置"""
        try:
            global_config_file = self.config_dir / "plugins.yaml"
            
            with open(global_config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.global_config, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info("Global plugin config saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save global plugin config: {e}")
    
    def _load_plugin_configs(self):
        """加载所有插件配置"""
        try:
            for config_file in self.config_dir.glob("*.json"):
                if config_file.name == "plugins.json":
                    continue
                
                plugin_id = config_file.stem
                
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    
                    self.plugin_configs[plugin_id] = config
                    self.logger.info(f"Loaded config for plugin: {plugin_id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load config for plugin {plugin_id}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin configs: {e}")
    
    def get_global_config(self) -> Dict[str, Any]:
        """获取全局插件配置"""
        return self.global_config.copy()
    
    def set_global_config(self, config: Dict[str, Any]):
        """设置全局插件配置"""
        self.global_config.update(config)
        self._save_global_config()
    
    def get_plugin_config(self, plugin_id: str) -> Dict[str, Any]:
        """
        获取插件配置
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            插件配置
        """
        return self.plugin_configs.get(plugin_id, {})
    
    def set_plugin_config(self, plugin_id: str, config: Dict[str, Any]):
        """
        设置插件配置
        
        Args:
            plugin_id: 插件ID
            config: 插件配置
        """
        self.plugin_configs[plugin_id] = config
        self._save_plugin_config(plugin_id)
    
    def _save_plugin_config(self, plugin_id: str):
        """保存插件配置"""
        try:
            config_file = self.config_dir / f"{plugin_id}.json"
            config = self.plugin_configs.get(plugin_id, {})
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved config for plugin: {plugin_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to save config for plugin {plugin_id}: {e}")
    
    def update_plugin_config(self, plugin_id: str, updates: Dict[str, Any]):
        """
        更新插件配置
        
        Args:
            plugin_id: 插件ID
            updates: 配置更新
        """
        if plugin_id not in self.plugin_configs:
            self.plugin_configs[plugin_id] = {}
        
        self.plugin_configs[plugin_id].update(updates)
        self._save_plugin_config(plugin_id)
    
    def delete_plugin_config(self, plugin_id: str):
        """
        删除插件配置
        
        Args:
            plugin_id: 插件ID
        """
        try:
            if plugin_id in self.plugin_configs:
                del self.plugin_configs[plugin_id]
            
            config_file = self.config_dir / f"{plugin_id}.json"
            if config_file.exists():
                config_file.unlink()
            
            self.logger.info(f"Deleted config for plugin: {plugin_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to delete config for plugin {plugin_id}: {e}")
    
    def get_plugin_directories(self) -> List[str]:
        """获取插件目录列表"""
        return self.global_config.get('plugin_directories', ['./plugins'])
    
    def add_plugin_directory(self, directory: str):
        """
        添加插件目录
        
        Args:
            directory: 目录路径
        """
        directories = self.get_plugin_directories()
        if directory not in directories:
            directories.append(directory)
            self.global_config['plugin_directories'] = directories
            self._save_global_config()
    
    def remove_plugin_directory(self, directory: str):
        """
        移除插件目录
        
        Args:
            directory: 目录路径
        """
        directories = self.get_plugin_directories()
        if directory in directories:
            directories.remove(directory)
            self.global_config['plugin_directories'] = directories
            self._save_global_config()
    
    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """
        检查插件是否启用
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            是否启用
        """
        plugin_config = self.get_plugin_config(plugin_id)
        return plugin_config.get('enabled', True)
    
    def enable_plugin(self, plugin_id: str):
        """
        启用插件
        
        Args:
            plugin_id: 插件ID
        """
        self.update_plugin_config(plugin_id, {'enabled': True})
    
    def disable_plugin(self, plugin_id: str):
        """
        禁用插件
        
        Args:
            plugin_id: 插件ID
        """
        self.update_plugin_config(plugin_id, {'enabled': False})
    
    def get_resource_limits(self) -> Dict[str, Any]:
        """获取资源限制"""
        return self.global_config.get('resource_limits', {})
    
    def get_allowed_imports(self) -> List[str]:
        """获取允许的导入模块"""
        return self.global_config.get('allowed_imports', [])
    
    def get_blocked_imports(self) -> List[str]:
        """获取禁止的导入模块"""
        return self.global_config.get('blocked_imports', [])
    
    def is_sandboxing_enabled(self) -> bool:
        """检查是否启用沙箱"""
        return self.global_config.get('enable_sandboxing', True)
    
    def validate_plugin_config(self, plugin_id: str, config: Dict[str, Any], 
                              schema: Optional[Dict[str, Any]] = None) -> tuple[bool, List[str]]:
        """
        验证插件配置
        
        Args:
            plugin_id: 插件ID
            config: 配置数据
            schema: 配置模式
            
        Returns:
            (是否有效, 错误列表)
        """
        errors = []
        
        try:
            # 基本验证
            if not isinstance(config, dict):
                errors.append("Configuration must be a dictionary")
                return False, errors
            
            # 如果有模式，进行模式验证
            if schema:
                errors.extend(self._validate_against_schema(config, schema))
            
            # 检查必需字段
            required_fields = ['enabled']
            for field in required_fields:
                if field not in config:
                    errors.append(f"Missing required field: {field}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
            return False, errors
    
    def _validate_against_schema(self, config: Dict[str, Any], 
                                schema: Dict[str, Any]) -> List[str]:
        """根据模式验证配置"""
        errors = []
        
        try:
            # 简单的模式验证实现
            for field, field_schema in schema.items():
                if field in config:
                    value = config[field]
                    field_type = field_schema.get('type')
                    
                    if field_type and not isinstance(value, eval(field_type)):
                        errors.append(f"Field '{field}' must be of type {field_type}")
                    
                    # 检查范围
                    if 'min' in field_schema and isinstance(value, (int, float)):
                        if value < field_schema['min']:
                            errors.append(f"Field '{field}' must be >= {field_schema['min']}")
                    
                    if 'max' in field_schema and isinstance(value, (int, float)):
                        if value > field_schema['max']:
                            errors.append(f"Field '{field}' must be <= {field_schema['max']}")
                
                elif field_schema.get('required', False):
                    errors.append(f"Required field '{field}' is missing")
            
        except Exception as e:
            errors.append(f"Schema validation error: {e}")
        
        return errors
    
    def export_configs(self, export_path: str) -> bool:
        """
        导出所有配置
        
        Args:
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        try:
            export_data = {
                'global_config': self.global_config,
                'plugin_configs': self.plugin_configs,
                'export_timestamp': self._get_current_timestamp()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configs exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configs: {e}")
            return False
    
    def import_configs(self, import_path: str) -> bool:
        """
        导入配置
        
        Args:
            import_path: 导入路径
            
        Returns:
            是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # 导入全局配置
            if 'global_config' in import_data:
                self.global_config.update(import_data['global_config'])
                self._save_global_config()
            
            # 导入插件配置
            if 'plugin_configs' in import_data:
                for plugin_id, config in import_data['plugin_configs'].items():
                    self.set_plugin_config(plugin_id, config)
            
            self.logger.info(f"Configs imported from: {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import configs: {e}")
            return False
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def cleanup(self):
        """清理资源"""
        try:
            # 保存所有配置
            self._save_global_config()
            for plugin_id in self.plugin_configs:
                self._save_plugin_config(plugin_id)
            
            self.logger.info("Plugin config cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Plugin config cleanup failed: {e}")
