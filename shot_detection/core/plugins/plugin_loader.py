"""
Plugin Loader
插件加载器
"""

import sys
import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Any, Optional, List, Type
from loguru import logger

from .plugin_interface import PluginInterface, PluginType, PluginStatus
from .plugin_config import PluginConfig


class PluginLoader:
    """插件加载器"""
    
    def __init__(self, config: Optional[PluginConfig] = None):
        """
        初始化插件加载器
        
        Args:
            config: 插件配置管理器
        """
        self.logger = logger.bind(component="PluginLoader")
        self.config = config or PluginConfig()
        
        # 已加载的插件
        self.loaded_plugins = {}
        
        # 插件模块缓存
        self.plugin_modules = {}
        
        # 加载统计
        self.load_stats = {
            'total_attempted': 0,
            'successful_loads': 0,
            'failed_loads': 0,
            'load_errors': []
        }
        
        self.logger.info("Plugin loader initialized")
    
    def discover_plugins(self, directories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        发现插件
        
        Args:
            directories: 搜索目录列表
            
        Returns:
            发现的插件信息列表
        """
        discovered_plugins = []
        
        if not directories:
            directories = self.config.get_plugin_directories()
        
        for directory in directories:
            try:
                plugin_dir = Path(directory)
                if not plugin_dir.exists():
                    self.logger.warning(f"Plugin directory not found: {directory}")
                    continue
                
                # 搜索Python文件
                for plugin_file in plugin_dir.rglob("*.py"):
                    if plugin_file.name.startswith("__"):
                        continue
                    
                    plugin_info = self._analyze_plugin_file(plugin_file)
                    if plugin_info:
                        discovered_plugins.append(plugin_info)
                
                # 搜索插件包
                for plugin_package in plugin_dir.iterdir():
                    if plugin_package.is_dir() and not plugin_package.name.startswith("__"):
                        init_file = plugin_package / "__init__.py"
                        if init_file.exists():
                            plugin_info = self._analyze_plugin_package(plugin_package)
                            if plugin_info:
                                discovered_plugins.append(plugin_info)
                
            except Exception as e:
                self.logger.error(f"Failed to discover plugins in {directory}: {e}")
        
        self.logger.info(f"Discovered {len(discovered_plugins)} plugins")
        return discovered_plugins
    
    def _analyze_plugin_file(self, plugin_file: Path) -> Optional[Dict[str, Any]]:
        """分析插件文件"""
        try:
            # 读取文件内容进行初步分析
            with open(plugin_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含插件接口
            if 'PluginInterface' not in content and 'BasePlugin' not in content:
                return None
            
            return {
                'type': 'file',
                'path': str(plugin_file),
                'name': plugin_file.stem,
                'discovered_at': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze plugin file {plugin_file}: {e}")
            return None
    
    def _analyze_plugin_package(self, plugin_package: Path) -> Optional[Dict[str, Any]]:
        """分析插件包"""
        try:
            init_file = plugin_package / "__init__.py"
            
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含插件接口
            if 'PluginInterface' not in content and 'BasePlugin' not in content:
                return None
            
            return {
                'type': 'package',
                'path': str(plugin_package),
                'name': plugin_package.name,
                'discovered_at': self._get_current_timestamp()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze plugin package {plugin_package}: {e}")
            return None
    
    def load_plugin(self, plugin_path: str, plugin_name: Optional[str] = None) -> Optional[PluginInterface]:
        """
        加载插件
        
        Args:
            plugin_path: 插件路径
            plugin_name: 插件名称
            
        Returns:
            加载的插件实例
        """
        self.load_stats['total_attempted'] += 1
        
        try:
            plugin_path_obj = Path(plugin_path)
            
            if not plugin_name:
                plugin_name = plugin_path_obj.stem
            
            # 检查是否已加载
            if plugin_name in self.loaded_plugins:
                self.logger.warning(f"Plugin already loaded: {plugin_name}")
                return self.loaded_plugins[plugin_name]
            
            # 检查插件是否启用
            if not self.config.is_plugin_enabled(plugin_name):
                self.logger.info(f"Plugin disabled: {plugin_name}")
                return None
            
            # 加载模块
            module = self._load_module(plugin_path, plugin_name)
            if not module:
                return None
            
            # 查找插件类
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                self.logger.error(f"No plugin class found in: {plugin_path}")
                self.load_stats['failed_loads'] += 1
                return None
            
            # 创建插件实例
            plugin_instance = self._create_plugin_instance(plugin_class, plugin_name)
            if not plugin_instance:
                return None
            
            # 初始化插件
            plugin_config = self.config.get_plugin_config(plugin_name)
            if not plugin_instance.initialize(plugin_config):
                self.logger.error(f"Failed to initialize plugin: {plugin_name}")
                self.load_stats['failed_loads'] += 1
                return None
            
            # 注册插件
            self.loaded_plugins[plugin_name] = plugin_instance
            self.plugin_modules[plugin_name] = module
            
            self.load_stats['successful_loads'] += 1
            self.logger.info(f"Successfully loaded plugin: {plugin_name}")
            
            return plugin_instance
            
        except Exception as e:
            error_msg = f"Failed to load plugin {plugin_path}: {e}"
            self.logger.error(error_msg)
            self.load_stats['failed_loads'] += 1
            self.load_stats['load_errors'].append(error_msg)
            return None
    
    def _load_module(self, plugin_path: str, plugin_name: str):
        """加载插件模块"""
        try:
            plugin_path_obj = Path(plugin_path)
            
            if plugin_path_obj.is_file():
                # 加载单个文件
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                
                # 安全检查
                if self.config.is_sandboxing_enabled():
                    if not self._validate_module_safety(plugin_path):
                        self.logger.error(f"Plugin failed safety validation: {plugin_path}")
                        return None
                
                spec.loader.exec_module(module)
                
            elif plugin_path_obj.is_dir():
                # 加载包
                sys.path.insert(0, str(plugin_path_obj.parent))
                try:
                    module = importlib.import_module(plugin_path_obj.name)
                finally:
                    sys.path.pop(0)
            else:
                self.logger.error(f"Invalid plugin path: {plugin_path}")
                return None
            
            return module
            
        except Exception as e:
            self.logger.error(f"Failed to load module {plugin_path}: {e}")
            return None
    
    def _validate_module_safety(self, plugin_path: str) -> bool:
        """验证模块安全性"""
        try:
            with open(plugin_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查禁止的导入
            blocked_imports = self.config.get_blocked_imports()
            for blocked in blocked_imports:
                if f"import {blocked}" in content or f"from {blocked}" in content:
                    self.logger.warning(f"Plugin contains blocked import: {blocked}")
                    return False
            
            # 检查危险操作
            dangerous_patterns = [
                'exec(', 'eval(', '__import__(',
                'open(', 'file(', 'input(',
                'os.system', 'subprocess.',
                'socket.', 'urllib.', 'requests.'
            ]
            
            for pattern in dangerous_patterns:
                if pattern in content:
                    self.logger.warning(f"Plugin contains potentially dangerous code: {pattern}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate module safety: {e}")
            return False
    
    def _find_plugin_class(self, module) -> Optional[Type[PluginInterface]]:
        """查找插件类"""
        try:
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PluginInterface) and 
                    obj != PluginInterface and 
                    not inspect.isabstract(obj)):
                    return obj
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find plugin class: {e}")
            return None
    
    def _create_plugin_instance(self, plugin_class: Type[PluginInterface], 
                               plugin_name: str) -> Optional[PluginInterface]:
        """创建插件实例"""
        try:
            # 检查依赖
            instance = plugin_class()
            dependencies = instance.plugin_dependencies
            
            if dependencies:
                missing_deps = self._check_dependencies(dependencies)
                if missing_deps:
                    self.logger.error(f"Plugin {plugin_name} missing dependencies: {missing_deps}")
                    return None
            
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to create plugin instance: {e}")
            return None
    
    def _check_dependencies(self, dependencies: List[str]) -> List[str]:
        """检查插件依赖"""
        missing_deps = []
        
        for dep in dependencies:
            try:
                importlib.import_module(dep)
            except ImportError:
                missing_deps.append(dep)
        
        return missing_deps
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        卸载插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            是否卸载成功
        """
        try:
            if plugin_name not in self.loaded_plugins:
                self.logger.warning(f"Plugin not loaded: {plugin_name}")
                return False
            
            plugin = self.loaded_plugins[plugin_name]
            
            # 清理插件
            if not plugin.cleanup():
                self.logger.warning(f"Plugin cleanup failed: {plugin_name}")
            
            # 移除引用
            del self.loaded_plugins[plugin_name]
            
            if plugin_name in self.plugin_modules:
                del self.plugin_modules[plugin_name]
            
            self.logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """
        重新加载插件
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            重新加载的插件实例
        """
        try:
            if plugin_name in self.loaded_plugins:
                plugin = self.loaded_plugins[plugin_name]
                plugin_path = getattr(plugin, '_plugin_path', None)
                
                # 卸载现有插件
                self.unload_plugin(plugin_name)
                
                # 重新加载
                if plugin_path:
                    return self.load_plugin(plugin_path, plugin_name)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to reload plugin {plugin_name}: {e}")
            return None
    
    def get_loaded_plugins(self) -> Dict[str, PluginInterface]:
        """获取已加载的插件"""
        return self.loaded_plugins.copy()
    
    def get_plugin_by_type(self, plugin_type: PluginType) -> List[PluginInterface]:
        """
        根据类型获取插件
        
        Args:
            plugin_type: 插件类型
            
        Returns:
            指定类型的插件列表
        """
        return [
            plugin for plugin in self.loaded_plugins.values()
            if plugin.plugin_type == plugin_type
        ]
    
    def get_load_statistics(self) -> Dict[str, Any]:
        """获取加载统计信息"""
        return self.load_stats.copy()
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def cleanup(self):
        """清理资源"""
        try:
            # 卸载所有插件
            plugin_names = list(self.loaded_plugins.keys())
            for plugin_name in plugin_names:
                self.unload_plugin(plugin_name)
            
            self.plugin_modules.clear()
            self.logger.info("Plugin loader cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Plugin loader cleanup failed: {e}")
