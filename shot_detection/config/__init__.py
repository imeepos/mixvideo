"""
Configuration Management Module
配置管理模块
"""

from .manager import ConfigManager, get_config, init_config
from .defaults import DEFAULT_CONFIG
from .schemas import ConfigSchema, DetectionConfig, ProcessingConfig, GUIConfig

__all__ = [
    "ConfigManager",
    "get_config",
    "init_config",
    "DEFAULT_CONFIG",
    "ConfigSchema",
    "DetectionConfig",
    "ProcessingConfig",
    "GUIConfig",
]
