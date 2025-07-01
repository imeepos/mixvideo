"""
Plugin Manager
插件管理器
"""

import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Type, Any, Optional
import json
from loguru import logger

from .base_plugin import BasePlugin, PluginError


class PluginManager:
    """插件管理器"""
    
    def __init__(self, plugin_dir: Optional[Path] = None):
        """
        初始化插件管理器
        
        Args:
            plugin_dir: 插件目录路径
        """
        self.plugin_dir = plugin_dir or Path("plugins")
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_classes: Dict[str, Type[BasePlugin]] = {}
        self.logger = logger.bind(component="PluginManager")
        
        # 确保插件目录存在
        self.plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置目录
        self.config_dir = self.plugin_dir / "configs"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def discover_plugins(self) -> List[str]:
        """
        发现插件
        
        Returns:
            发现的插件名称列表
        """
        discovered = []
        
        try:
            # 扫描插件目录
            for plugin_file in self.plugin_dir.glob("*.py"):
                if plugin_file.name.startswith("_"):
                    continue
                
                plugin_name = plugin_file.stem
                
                try:
                    # 动态导入插件模块
                    spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # 查找插件类
                        plugin_class = self._find_plugin_class(module)
                        if plugin_class:
                            self.plugin_classes[plugin_name] = plugin_class
                            discovered.append(plugin_name)
                            self.logger.info(f"Discovered plugin: {plugin_name}")
                        
                except Exception as e:
                    self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            
            return discovered
            
        except Exception as e:
            self.logger.error(f"Plugin discovery failed: {e}")
            return []
    
    def _find_plugin_class(self, module) -> Optional[Type[BasePlugin]]:
        """在模块中查找插件类"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            if (isinstance(attr, type) and 
                issubclass(attr, BasePlugin) and 
                attr != BasePlugin):
                return attr
        
        return None
    
    def load_plugin(self, plugin_name: str, **kwargs) -> bool:
        """
        加载插件
        
        Args:
            plugin_name: 插件名称
            **kwargs: 插件初始化参数
            
        Returns:
            是否加载成功
        """
        try:
            if plugin_name in self.plugins:
                self.logger.warning(f"Plugin {plugin_name} already loaded")
                return True
            
            if plugin_name not in self.plugin_classes:
                self.logger.error(f"Plugin class not found: {plugin_name}")
                return False
            
            # 创建插件实例
            plugin_class = self.plugin_classes[plugin_name]
            plugin = plugin_class(name=plugin_name, **kwargs)
            
            # 加载配置
            config_file = self.config_dir / f"{plugin_name}.json"
            plugin.load_config(config_file)
            
            # 验证配置
            if not plugin.validate_config():
                self.logger.error(f"Invalid config for plugin {plugin_name}")
                return False
            
            # 存储插件
            self.plugins[plugin_name] = plugin
            
            self.logger.info(f"Plugin loaded: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否卸载成功
        """
        try:
            if plugin_name not in self.plugins:
                self.logger.warning(f"Plugin not loaded: {plugin_name}")
                return True
            
            plugin = self.plugins[plugin_name]
            
            # 禁用插件
            plugin.disable()
            
            # 保存配置
            config_file = self.config_dir / f"{plugin_name}.json"
            plugin.save_config(config_file)
            
            # 移除插件
            del self.plugins[plugin_name]
            
            self.logger.info(f"Plugin unloaded: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        启用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否启用成功
        """
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin not loaded: {plugin_name}")
            return False
        
        plugin = self.plugins[plugin_name]
        success = plugin.enable()
        
        if success:
            self.logger.info(f"Plugin enabled: {plugin_name}")
        else:
            self.logger.error(f"Failed to enable plugin: {plugin_name}")
        
        return success
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        禁用插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否禁用成功
        """
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin not loaded: {plugin_name}")
            return False
        
        plugin = self.plugins[plugin_name]
        plugin.disable()
        
        self.logger.info(f"Plugin disabled: {plugin_name}")
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        获取插件实例
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            插件实例或None
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """
        列出所有已加载的插件
        
        Returns:
            插件名称列表
        """
        return list(self.plugins.keys())
    
    def list_enabled_plugins(self) -> List[str]:
        """
        列出所有已启用的插件
        
        Returns:
            已启用插件名称列表
        """
        return [name for name, plugin in self.plugins.items() if plugin.enabled]
    
    def get_plugin_status(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有插件状态
        
        Returns:
            插件状态字典
        """
        return {name: plugin.get_status() for name, plugin in self.plugins.items()}
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        重新加载插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否重新加载成功
        """
        # 保存当前状态
        was_enabled = False
        if plugin_name in self.plugins:
            was_enabled = self.plugins[plugin_name].enabled
        
        # 卸载插件
        self.unload_plugin(plugin_name)
        
        # 重新发现插件
        self.discover_plugins()
        
        # 重新加载插件
        success = self.load_plugin(plugin_name)
        
        # 恢复启用状态
        if success and was_enabled:
            self.enable_plugin(plugin_name)
        
        return success
    
    def cleanup_all(self):
        """清理所有插件"""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
        
        self.logger.info("All plugins cleaned up")
    
    def save_plugin_states(self) -> bool:
        """
        保存所有插件状态
        
        Returns:
            是否保存成功
        """
        try:
            states = {}
            for name, plugin in self.plugins.items():
                states[name] = {
                    "enabled": plugin.enabled,
                    "config": plugin.config
                }
            
            state_file = self.config_dir / "plugin_states.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(states, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Plugin states saved")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save plugin states: {e}")
            return False
    
    def load_plugin_states(self) -> bool:
        """
        加载插件状态
        
        Returns:
            是否加载成功
        """
        try:
            state_file = self.config_dir / "plugin_states.json"
            if not state_file.exists():
                return True
            
            with open(state_file, 'r', encoding='utf-8') as f:
                states = json.load(f)
            
            for name, state in states.items():
                if name in self.plugins:
                    plugin = self.plugins[name]
                    plugin.config.update(state.get("config", {}))
                    
                    if state.get("enabled", False):
                        plugin.enable()
            
            self.logger.info("Plugin states loaded")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin states: {e}")
            return False
