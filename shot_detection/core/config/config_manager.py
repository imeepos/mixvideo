"""
Configuration Manager
配置管理器
"""

import os
import json
import yaml
import toml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from loguru import logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: Optional[str] = None, 
                 default_config_file: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置目录
            default_config_file: 默认配置文件
        """
        self.logger = logger.bind(component="ConfigManager")
        
        # 配置目录
        self.config_dir = Path(config_dir or "./config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 默认配置文件
        self.default_config_file = default_config_file or "config.yaml"
        self.config_file_path = self.config_dir / self.default_config_file
        
        # 配置数据
        self.config_data = {}
        
        # 配置验证器
        self.validator = ConfigValidator()
        
        # 配置变更监听器
        self.change_listeners = []
        
        # 配置历史
        self.config_history = []
        
        # 加载配置
        self._load_config()
        
        self.logger.info(f"Config manager initialized with config dir: {self.config_dir}")
    
    def _load_config(self):
        """加载配置"""
        try:
            if self.config_file_path.exists():
                self.config_data = self._load_config_file(self.config_file_path)
            else:
                # 创建默认配置
                self.config_data = self._create_default_config()
                self._save_config()
            
            # 验证配置
            validation_result = self.validator.validate_config(self.config_data)
            if not validation_result['valid']:
                self.logger.warning(f"Config validation warnings: {validation_result['errors']}")
            
            self.logger.info("Configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            self.config_data = self._create_default_config()
    
    def _load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_ext = file_path.suffix.lower()
                
                if file_ext in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif file_ext == '.json':
                    return json.load(f) or {}
                elif file_ext == '.toml':
                    return toml.load(f) or {}
                else:
                    raise ValueError(f"Unsupported config file format: {file_ext}")
            
        except Exception as e:
            self.logger.error(f"Failed to load config file {file_path}: {e}")
            return {}
    
    def _save_config(self):
        """保存配置"""
        try:
            # 备份当前配置到历史
            self._backup_config()
            
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                file_ext = self.config_file_path.suffix.lower()
                
                if file_ext in ['.yaml', '.yml']:
                    yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
                elif file_ext == '.json':
                    json.dump(self.config_data, f, indent=2, ensure_ascii=False)
                elif file_ext == '.toml':
                    toml.dump(self.config_data, f)
                else:
                    raise ValueError(f"Unsupported config file format: {file_ext}")
            
            self.logger.info("Configuration saved successfully")
            
            # 通知监听器
            self._notify_change_listeners()
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
    
    def _backup_config(self):
        """备份配置到历史"""
        try:
            backup_entry = {
                'timestamp': datetime.now().isoformat(),
                'config': self.config_data.copy()
            }
            
            self.config_history.append(backup_entry)
            
            # 限制历史记录数量
            max_history = 50
            if len(self.config_history) > max_history:
                self.config_history = self.config_history[-max_history:]
            
        except Exception as e:
            self.logger.error(f"Failed to backup config: {e}")
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        return {
            'app': {
                'name': 'Shot Detection',
                'version': '2.0.0',
                'debug': False,
                'log_level': 'INFO'
            },
            'detection': {
                'default_algorithm': 'frame_difference',
                'threshold': 0.5,
                'min_shot_duration': 1.0,
                'max_shot_duration': 300.0,
                'output_format': 'json'
            },
            'processing': {
                'max_workers': 4,
                'chunk_size': 1000,
                'memory_limit_mb': 1024,
                'temp_dir': './temp'
            },
            'export': {
                'default_format': 'json',
                'include_metadata': True,
                'compress_output': False
            },
            'ui': {
                'theme': 'default',
                'language': 'en_US',
                'auto_save': True,
                'recent_files_count': 10
            },
            'security': {
                'enable_authentication': False,
                'session_timeout_minutes': 30,
                'max_login_attempts': 5
            },
            'performance': {
                'enable_caching': True,
                'cache_size_mb': 256,
                'enable_gpu': False
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键（支持点号分隔的嵌套键）
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
            self.logger.error(f"Failed to get config value for key '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键（支持点号分隔的嵌套键）
            value: 配置值
            
        Returns:
            是否设置成功
        """
        try:
            keys = key.split('.')
            config = self.config_data
            
            # 导航到父级字典
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                elif not isinstance(config[k], dict):
                    # 如果中间路径不是字典，创建新字典
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            
            # 验证配置
            validation_result = self.validator.validate_config(self.config_data)
            if not validation_result['valid']:
                self.logger.warning(f"Config validation warnings after setting '{key}': {validation_result['errors']}")
            
            # 保存配置
            self._save_config()
            
            self.logger.info(f"Config value set: {key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set config value for key '{key}': {e}")
            return False
    
    def update(self, config_dict: Dict[str, Any]) -> bool:
        """
        批量更新配置
        
        Args:
            config_dict: 配置字典
            
        Returns:
            是否更新成功
        """
        try:
            # 深度合并配置
            self._deep_merge(self.config_data, config_dict)
            
            # 验证配置
            validation_result = self.validator.validate_config(self.config_data)
            if not validation_result['valid']:
                self.logger.warning(f"Config validation warnings after update: {validation_result['errors']}")
            
            # 保存配置
            self._save_config()
            
            self.logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return False
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """深度合并字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def delete(self, key: str) -> bool:
        """
        删除配置项
        
        Args:
            key: 配置键
            
        Returns:
            是否删除成功
        """
        try:
            keys = key.split('.')
            config = self.config_data
            
            # 导航到父级字典
            for k in keys[:-1]:
                if k not in config or not isinstance(config[k], dict):
                    return False  # 路径不存在
                config = config[k]
            
            # 删除键
            if keys[-1] in config:
                del config[keys[-1]]
                self._save_config()
                self.logger.info(f"Config key deleted: {key}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete config key '{key}': {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config_data.copy()
    
    def reset_to_default(self) -> bool:
        """重置为默认配置"""
        try:
            self.config_data = self._create_default_config()
            self._save_config()
            self.logger.info("Configuration reset to default")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset configuration: {e}")
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        """
        从文件加载配置
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            是否加载成功
        """
        try:
            config_data = self._load_config_file(Path(file_path))
            
            if config_data:
                self.config_data = config_data
                self._save_config()
                self.logger.info(f"Configuration loaded from file: {file_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to load config from file '{file_path}': {e}")
            return False
    
    def save_to_file(self, file_path: str) -> bool:
        """
        保存配置到文件
        
        Args:
            file_path: 目标文件路径
            
        Returns:
            是否保存成功
        """
        try:
            target_path = Path(file_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                file_ext = target_path.suffix.lower()
                
                if file_ext in ['.yaml', '.yml']:
                    yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
                elif file_ext == '.json':
                    json.dump(self.config_data, f, indent=2, ensure_ascii=False)
                elif file_ext == '.toml':
                    toml.dump(self.config_data, f)
                else:
                    raise ValueError(f"Unsupported file format: {file_ext}")
            
            self.logger.info(f"Configuration saved to file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save config to file '{file_path}': {e}")
            return False
    
    def add_change_listener(self, listener: callable):
        """
        添加配置变更监听器
        
        Args:
            listener: 监听器函数
        """
        if listener not in self.change_listeners:
            self.change_listeners.append(listener)
    
    def remove_change_listener(self, listener: callable):
        """
        移除配置变更监听器
        
        Args:
            listener: 监听器函数
        """
        if listener in self.change_listeners:
            self.change_listeners.remove(listener)
    
    def _notify_change_listeners(self):
        """通知配置变更监听器"""
        try:
            for listener in self.change_listeners:
                try:
                    listener(self.config_data.copy())
                except Exception as e:
                    self.logger.error(f"Config change listener error: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to notify change listeners: {e}")
    
    def get_config_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取配置历史
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            配置历史列表
        """
        return self.config_history[-limit:] if self.config_history else []
    
    def restore_from_history(self, index: int) -> bool:
        """
        从历史恢复配置
        
        Args:
            index: 历史记录索引（-1为最新）
            
        Returns:
            是否恢复成功
        """
        try:
            if not self.config_history:
                return False
            
            if index < 0:
                index = len(self.config_history) + index
            
            if 0 <= index < len(self.config_history):
                self.config_data = self.config_history[index]['config'].copy()
                self._save_config()
                self.logger.info(f"Configuration restored from history index: {index}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to restore config from history: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            self.change_listeners.clear()
            self.config_history.clear()
            self.logger.info("Config manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Config manager cleanup failed: {e}")


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        """初始化配置验证器"""
        self.logger = logger.bind(component="ConfigValidator")
        
        # 配置模式定义
        self.config_schema = {
            'app': {
                'name': {'type': str, 'required': True},
                'version': {'type': str, 'required': True},
                'debug': {'type': bool, 'default': False},
                'log_level': {'type': str, 'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR'], 'default': 'INFO'}
            },
            'detection': {
                'default_algorithm': {'type': str, 'required': True},
                'threshold': {'type': float, 'min': 0.0, 'max': 1.0, 'default': 0.5},
                'min_shot_duration': {'type': float, 'min': 0.1, 'default': 1.0},
                'max_shot_duration': {'type': float, 'min': 1.0, 'default': 300.0}
            },
            'processing': {
                'max_workers': {'type': int, 'min': 1, 'max': 32, 'default': 4},
                'chunk_size': {'type': int, 'min': 100, 'default': 1000},
                'memory_limit_mb': {'type': int, 'min': 256, 'default': 1024}
            }
        }
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证配置
        
        Args:
            config: 配置字典
            
        Returns:
            验证结果
        """
        try:
            errors = []
            warnings = []
            
            # 验证每个配置段
            for section_name, section_schema in self.config_schema.items():
                if section_name in config:
                    section_errors, section_warnings = self._validate_section(
                        config[section_name], section_schema, section_name
                    )
                    errors.extend(section_errors)
                    warnings.extend(section_warnings)
                else:
                    warnings.append(f"Missing configuration section: {section_name}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            self.logger.error(f"Config validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': []
            }
    
    def _validate_section(self, section: Dict[str, Any], schema: Dict[str, Any], 
                         section_name: str) -> tuple[List[str], List[str]]:
        """验证配置段"""
        errors = []
        warnings = []
        
        try:
            for key, rules in schema.items():
                if key in section:
                    # 验证值
                    value = section[key]
                    key_errors = self._validate_value(value, rules, f"{section_name}.{key}")
                    errors.extend(key_errors)
                elif rules.get('required', False):
                    errors.append(f"Required configuration missing: {section_name}.{key}")
                else:
                    warnings.append(f"Optional configuration missing: {section_name}.{key}")
            
            return errors, warnings
            
        except Exception as e:
            errors.append(f"Section validation error for {section_name}: {str(e)}")
            return errors, warnings
    
    def _validate_value(self, value: Any, rules: Dict[str, Any], key_path: str) -> List[str]:
        """验证配置值"""
        errors = []
        
        try:
            # 类型检查
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                errors.append(f"Invalid type for {key_path}: expected {expected_type.__name__}, got {type(value).__name__}")
                return errors
            
            # 选择检查
            choices = rules.get('choices')
            if choices and value not in choices:
                errors.append(f"Invalid value for {key_path}: must be one of {choices}")
            
            # 数值范围检查
            if isinstance(value, (int, float)):
                min_val = rules.get('min')
                max_val = rules.get('max')
                
                if min_val is not None and value < min_val:
                    errors.append(f"Value for {key_path} is below minimum: {value} < {min_val}")
                
                if max_val is not None and value > max_val:
                    errors.append(f"Value for {key_path} is above maximum: {value} > {max_val}")
            
            # 字符串长度检查
            if isinstance(value, str):
                min_length = rules.get('min_length')
                max_length = rules.get('max_length')
                
                if min_length is not None and len(value) < min_length:
                    errors.append(f"String length for {key_path} is below minimum: {len(value)} < {min_length}")
                
                if max_length is not None and len(value) > max_length:
                    errors.append(f"String length for {key_path} is above maximum: {len(value)} > {max_length}")
            
            return errors
            
        except Exception as e:
            errors.append(f"Value validation error for {key_path}: {str(e)}")
            return errors
