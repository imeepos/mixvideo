"""
Plugin System Module
插件系统模块
"""

from .plugin_manager import PluginManager
from .base_plugin import BasePlugin
from .detector_plugin import DetectorPlugin
from .processor_plugin import ProcessorPlugin
from .plugin_loader import PluginLoader
from .plugin_registry import PluginRegistry
from .plugin_interface import PluginInterface
from .plugin_config import PluginConfig
from .api import PluginAPI, APIRegistry, DetectionAPI, ProcessingAPI, ExportAPI
from .discovery import PluginDiscovery, DiscoveryConfig
from .sandbox import PluginSandbox, SandboxConfig

__all__ = [
    "PluginManager",
    "BasePlugin",
    "DetectorPlugin",
    "ProcessorPlugin",
    "PluginLoader",
    "PluginRegistry",
    "PluginInterface",
    "PluginConfig",
    "PluginAPI",
    "APIRegistry",
    "DetectionAPI",
    "ProcessingAPI",
    "ExportAPI",
    "PluginDiscovery",
    "DiscoveryConfig",
    "PluginSandbox",
    "SandboxConfig",
]
