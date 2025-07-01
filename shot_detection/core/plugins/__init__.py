"""
Plugin System Module
插件系统模块
"""

from .plugin_manager import PluginManager
from .base_plugin import BasePlugin
from .detector_plugin import DetectorPlugin
from .processor_plugin import ProcessorPlugin

__all__ = [
    "PluginManager",
    "BasePlugin", 
    "DetectorPlugin",
    "ProcessorPlugin",
]
