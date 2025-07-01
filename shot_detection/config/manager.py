"""
Configuration Manager
配置管理器
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger

from .defaults import DEFAULT_CONFIG
from .schemas import ConfigSchema


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path) if config_path else self._get_default_config_path()
        self.config = DEFAULT_CONFIG.copy()
        self.logger = logger.bind(component="ConfigManager")
        
        # 加载配置
        self.load_config()
    
    def _get_default_config_path(self) -> Path:
        """获取默认配置文件路径"""
        # 优先级：环境变量 > 当前目录 > 用户目录
        if "SHOT_DETECTION_CONFIG" in os.environ:
            return Path(os.environ["SHOT_DETECTION_CONFIG"])
        
        current_dir_config = Path.cwd() / "config.yaml"
        if current_dir_config.exists():
            return current_dir_config
        
        user_config_dir = Path.home() / ".shot_detection"
        user_config_dir.mkdir(exist_ok=True)
        return user_config_dir / "config.yaml"
    
    def load_config(self) -> bool:
        """
        加载配置文件
        
        Returns:
            是否成功加载
        """
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                
                if user_config:
                    self._merge_config(self.config, user_config)
                    self.logger.info(f"Loaded config from {self.config_path}")
                else:
                    self.logger.warning(f"Empty config file: {self.config_path}")
            else:
                self.logger.info(f"Config file not found: {self.config_path}, using defaults")
                self.save_config()  # 创建默认配置文件
            
            # 验证配置
            self._validate_config()
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        保存配置文件
        
        Returns:
            是否成功保存
        """
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            self.logger.info(f"Saved config to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键（支持点分隔的嵌套键）
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键（支持点分隔的嵌套键）
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        # 导航到目标位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        批量更新配置
        
        Args:
            updates: 更新字典
        """
        self._merge_config(self.config, updates)
    
    def _merge_config(self, base: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """
        递归合并配置
        
        Args:
            base: 基础配置
            updates: 更新配置
        """
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _validate_config(self) -> None:
        """验证配置"""
        try:
            # 使用pydantic验证配置（如果需要）
            # ConfigSchema(**self.config)
            pass
        except Exception as e:
            self.logger.warning(f"Config validation warning: {e}")
    
    def get_detection_config(self) -> Dict[str, Any]:
        """获取检测配置"""
        return self.get('detection', {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """获取处理配置"""
        return self.get('processing', {})
    
    def get_gui_config(self) -> Dict[str, Any]:
        """获取GUI配置"""
        return self.get('gui', {})
    
    def get_jianying_config(self) -> Dict[str, Any]:
        """获取剪映配置"""
        return self.get('jianying', {})
    
    def reset_to_defaults(self) -> None:
        """重置为默认配置"""
        self.config = DEFAULT_CONFIG.copy()
        self.logger.info("Reset config to defaults")
    
    def export_config(self, export_path: str) -> bool:
        """
        导出配置到指定路径
        
        Args:
            export_path: 导出路径
            
        Returns:
            是否成功导出
        """
        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False,
                         allow_unicode=True, indent=2)
            
            self.logger.info(f"Exported config to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting config: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        从指定路径导入配置
        
        Args:
            import_path: 导入路径
            
        Returns:
            是否成功导入
        """
        try:
            import_path = Path(import_path)
            if not import_path.exists():
                self.logger.error(f"Import file not found: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = yaml.safe_load(f)
            
            if imported_config:
                self.config = imported_config
                self._validate_config()
                self.logger.info(f"Imported config from {import_path}")
                return True
            else:
                self.logger.error(f"Empty or invalid config file: {import_path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error importing config: {e}")
            return False


# 全局配置管理器实例
_config_manager = None


def get_config() -> ConfigManager:
    """
    获取全局配置管理器实例
    
    Returns:
        配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def init_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    初始化全局配置管理器
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置管理器实例
    """
    global _config_manager
    _config_manager = ConfigManager(config_path)
    return _config_manager


# 为ConfigManager类添加验证方法
def _add_validation_methods():
    """为ConfigManager类添加验证方法"""

    def validate_config(self) -> tuple[bool, list[str]]:
        """
        验证配置

        Returns:
            (is_valid, errors): 验证结果和错误列表
        """
        errors = []

        try:
            # 验证应用配置
            app_config = self.config.get('app', {})
            if not app_config.get('name'):
                errors.append("应用名称不能为空")

            # 验证检测配置
            detection_config = self.config.get('detection', {})

            # 验证帧差检测配置
            fd_config = detection_config.get('frame_difference', {})
            threshold = fd_config.get('threshold', 0.3)
            if not (0.0 <= threshold <= 1.0):
                errors.append(f"帧差检测阈值必须在0.0-1.0之间，当前值: {threshold}")

            # 验证直方图检测配置
            hist_config = detection_config.get('histogram', {})
            hist_threshold = hist_config.get('threshold', 0.5)
            if not (0.0 <= hist_threshold <= 1.0):
                errors.append(f"直方图检测阈值必须在0.0-1.0之间，当前值: {hist_threshold}")

            bins = hist_config.get('bins', 256)
            if not (1 <= bins <= 1024):
                errors.append(f"直方图bins数量必须在1-1024之间，当前值: {bins}")

            return len(errors) == 0, errors

        except Exception as e:
            errors.append(f"配置验证异常: {e}")
            return False, errors

    # 动态添加方法到ConfigManager类
    ConfigManager.validate_config = validate_config

# 调用函数添加方法
_add_validation_methods()
