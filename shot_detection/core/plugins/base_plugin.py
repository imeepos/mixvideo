"""
Base Plugin Class
基础插件类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
import json


class BasePlugin(ABC):
    """插件基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        初始化插件
        
        Args:
            name: 插件名称
            version: 插件版本
        """
        self.name = name
        self.version = version
        self.enabled = False
        self.config = {}
        self.metadata = {}
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化插件
        
        Returns:
            是否初始化成功
        """
        pass
    
    @abstractmethod
    def cleanup(self):
        """清理插件资源"""
        pass
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """
        获取插件信息
        
        Returns:
            插件信息字典
        """
        pass
    
    def enable(self) -> bool:
        """
        启用插件
        
        Returns:
            是否启用成功
        """
        try:
            if not self.enabled:
                success = self.initialize()
                if success:
                    self.enabled = True
                return success
            return True
        except Exception as e:
            print(f"Failed to enable plugin {self.name}: {e}")
            return False
    
    def disable(self):
        """禁用插件"""
        try:
            if self.enabled:
                self.cleanup()
                self.enabled = False
        except Exception as e:
            print(f"Failed to disable plugin {self.name}: {e}")
    
    def load_config(self, config_path: Path) -> bool:
        """
        加载插件配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            是否加载成功
        """
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                return True
            return False
        except Exception as e:
            print(f"Failed to load config for plugin {self.name}: {e}")
            return False
    
    def save_config(self, config_path: Path) -> bool:
        """
        保存插件配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            是否保存成功
        """
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to save config for plugin {self.name}: {e}")
            return False
    
    def set_config(self, key: str, value: Any):
        """设置配置项"""
        self.config[key] = value
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def validate_config(self) -> bool:
        """
        验证配置
        
        Returns:
            配置是否有效
        """
        return True  # 默认实现，子类可以重写
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取插件状态
        
        Returns:
            状态信息
        """
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "config_valid": self.validate_config()
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.name} v{self.version} ({'enabled' if self.enabled else 'disabled'})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return f"<{self.__class__.__name__}(name='{self.name}', version='{self.version}', enabled={self.enabled})>"


class PluginError(Exception):
    """插件异常"""
    pass


class PluginInitializationError(PluginError):
    """插件初始化异常"""
    pass


class PluginConfigurationError(PluginError):
    """插件配置异常"""
    pass
