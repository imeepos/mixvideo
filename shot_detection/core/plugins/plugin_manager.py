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
from .plugin_interface import PluginInterface, PluginType, PluginStatus
from .plugin_loader import PluginLoader
from .plugin_registry import PluginRegistry
from .plugin_config import PluginConfig


class PluginManager:
    """增强的插件管理器"""

    def __init__(self, plugin_dir: Optional[Path] = None, config: Optional[Dict[str, Any]] = None):
        """
        初始化插件管理器

        Args:
            plugin_dir: 插件目录路径
            config: 插件管理器配置
        """
        self.plugin_dir = plugin_dir or Path("plugins")
        self.config = config or {}
        self.logger = logger.bind(component="PluginManager")

        # 确保插件目录存在
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        # 初始化组件
        self.plugin_config = PluginConfig(str(self.plugin_dir / "config"))
        self.plugin_loader = PluginLoader(self.plugin_config)
        self.plugin_registry = PluginRegistry(str(self.plugin_dir / "registry.json"))

        # 兼容性：保留原有接口
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_classes: Dict[str, Type[BasePlugin]] = {}

        # 新接口：插件实例
        self.plugin_instances: Dict[str, PluginInterface] = {}

        # 配置目录
        self.config_dir = self.plugin_dir / "configs"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("Enhanced plugin manager initialized")
    
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

    # 新的增强方法
    def discover_plugins_enhanced(self, directories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        增强的插件发现功能

        Args:
            directories: 搜索目录列表

        Returns:
            发现的插件信息列表
        """
        return self.plugin_loader.discover_plugins(directories)

    def load_plugin_enhanced(self, plugin_path: str, plugin_name: Optional[str] = None) -> Optional[PluginInterface]:
        """
        增强的插件加载功能

        Args:
            plugin_path: 插件路径
            plugin_name: 插件名称

        Returns:
            加载的插件实例
        """
        plugin = self.plugin_loader.load_plugin(plugin_path, plugin_name)

        if plugin:
            # 注册到注册表
            self.plugin_registry.register_plugin(plugin, plugin_path)

            # 存储实例
            self.plugin_instances[plugin.plugin_id] = plugin

            self.logger.info(f"Enhanced plugin loaded: {plugin.plugin_id}")

        return plugin

    def unload_plugin_enhanced(self, plugin_id: str) -> bool:
        """
        增强的插件卸载功能

        Args:
            plugin_id: 插件ID

        Returns:
            是否卸载成功
        """
        success = self.plugin_loader.unload_plugin(plugin_id)

        if success:
            # 从注册表移除
            self.plugin_registry.unregister_plugin(plugin_id)

            # 移除实例
            if plugin_id in self.plugin_instances:
                del self.plugin_instances[plugin_id]

        return success

    def get_plugins_by_type_enhanced(self, plugin_type: PluginType) -> List[PluginInterface]:
        """
        根据类型获取插件

        Args:
            plugin_type: 插件类型

        Returns:
            指定类型的插件列表
        """
        return self.plugin_loader.get_plugin_by_type(plugin_type)

    def get_plugin_info_enhanced(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        获取插件信息

        Args:
            plugin_id: 插件ID

        Returns:
            插件信息
        """
        return self.plugin_registry.get_plugin_info(plugin_id)

    def search_plugins_enhanced(self, query: str) -> Dict[str, Dict[str, Any]]:
        """
        搜索插件

        Args:
            query: 搜索查询

        Returns:
            匹配的插件信息
        """
        return self.plugin_registry.search_plugins(query)

    def get_plugin_dependencies_enhanced(self, plugin_id: str) -> List[str]:
        """
        获取插件依赖

        Args:
            plugin_id: 插件ID

        Returns:
            依赖列表
        """
        return self.plugin_registry.get_plugin_dependencies(plugin_id)

    def validate_plugin_dependencies_enhanced(self, plugin_id: str) -> tuple[bool, List[str]]:
        """
        验证插件依赖

        Args:
            plugin_id: 插件ID

        Returns:
            (是否有效, 缺失的依赖列表)
        """
        return self.plugin_registry.validate_dependencies(plugin_id)

    def get_load_order_enhanced(self, plugin_ids: Optional[List[str]] = None) -> List[str]:
        """
        获取插件加载顺序

        Args:
            plugin_ids: 要排序的插件ID列表

        Returns:
            排序后的插件ID列表
        """
        return self.plugin_registry.get_load_order(plugin_ids)

    def load_plugins_in_order(self, plugin_paths: Dict[str, str]) -> Dict[str, bool]:
        """
        按依赖顺序加载插件

        Args:
            plugin_paths: 插件ID到路径的映射

        Returns:
            加载结果
        """
        results = {}

        # 首先发现所有插件
        for plugin_id, plugin_path in plugin_paths.items():
            plugin = self.load_plugin_enhanced(plugin_path, plugin_id)
            results[plugin_id] = plugin is not None

        # 获取加载顺序
        load_order = self.get_load_order_enhanced(list(plugin_paths.keys()))

        # 按顺序初始化插件
        for plugin_id in load_order:
            if plugin_id in self.plugin_instances:
                plugin = self.plugin_instances[plugin_id]
                config = self.plugin_config.get_plugin_config(plugin_id)

                try:
                    if not plugin.initialize(config):
                        self.logger.error(f"Failed to initialize plugin: {plugin_id}")
                        results[plugin_id] = False
                    else:
                        self.plugin_registry.update_plugin_status(plugin_id, PluginStatus.ACTIVE)
                except Exception as e:
                    self.logger.error(f"Plugin initialization error {plugin_id}: {e}")
                    results[plugin_id] = False
                    self.plugin_registry.update_plugin_status(plugin_id, PluginStatus.ERROR)

        return results

    def auto_discover_and_load(self) -> Dict[str, bool]:
        """
        自动发现并加载插件

        Returns:
            加载结果
        """
        # 发现插件
        discovered = self.discover_plugins_enhanced()

        # 构建路径映射
        plugin_paths = {}
        for plugin_info in discovered:
            plugin_paths[plugin_info['name']] = plugin_info['path']

        # 按顺序加载
        return self.load_plugins_in_order(plugin_paths)

    def get_plugin_statistics(self) -> Dict[str, Any]:
        """获取插件统计信息"""
        registry_stats = self.plugin_registry.get_registry_statistics()
        loader_stats = self.plugin_loader.get_load_statistics()

        return {
            'registry': registry_stats,
            'loader': loader_stats,
            'loaded_plugins': len(self.plugin_instances),
            'legacy_plugins': len(self.plugins)
        }

    def export_plugin_data(self, export_path: str) -> bool:
        """
        导出插件数据

        Args:
            export_path: 导出路径

        Returns:
            是否导出成功
        """
        try:
            export_data = {
                'statistics': self.get_plugin_statistics(),
                'registry': self.plugin_registry.get_all_plugins(),
                'config': self.plugin_config.get_global_config(),
                'export_timestamp': self._get_current_timestamp()
            }

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Plugin data exported to: {export_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export plugin data: {e}")
            return False

    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()

    def cleanup_enhanced(self):
        """增强的清理功能"""
        try:
            # 清理新组件
            self.plugin_loader.cleanup()
            self.plugin_registry.cleanup()
            self.plugin_config.cleanup()

            # 清理实例
            self.plugin_instances.clear()

            # 调用原有清理
            self.cleanup_all()

            self.logger.info("Enhanced plugin manager cleanup completed")

        except Exception as e:
            self.logger.error(f"Enhanced cleanup failed: {e}")
