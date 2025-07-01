"""
Plugin Discovery System
插件发现系统
"""

import os
import json
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from loguru import logger


@dataclass
class DiscoveryConfig:
    """插件发现配置"""
    search_paths: List[str]
    file_patterns: List[str]
    manifest_filename: str = "plugin.json"
    auto_discover: bool = True
    recursive_search: bool = True
    max_depth: int = 3
    cache_enabled: bool = True
    cache_file: str = "plugin_cache.json"


class PluginDiscovery:
    """插件发现器"""
    
    def __init__(self, config: Optional[DiscoveryConfig] = None):
        """
        初始化插件发现器
        
        Args:
            config: 发现配置
        """
        self.config = config or DiscoveryConfig(
            search_paths=["./plugins", "~/.shot-detection/plugins"],
            file_patterns=["*.py", "plugin.py", "__init__.py"]
        )
        
        self.logger = logger.bind(component="PluginDiscovery")
        
        # 发现的插件信息
        self._discovered_plugins = {}
        self._plugin_cache = {}
        
        # 加载缓存
        if self.config.cache_enabled:
            self._load_cache()
        
        self.logger.info("Plugin discovery initialized")
    
    def discover_plugins(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        发现插件
        
        Args:
            force_refresh: 是否强制刷新
            
        Returns:
            发现的插件信息
        """
        try:
            self.logger.info("Starting plugin discovery")
            
            if not force_refresh and self._discovered_plugins:
                return self._discovered_plugins
            
            self._discovered_plugins.clear()
            
            # 搜索所有路径
            for search_path in self.config.search_paths:
                self._search_path(search_path)
            
            # 保存缓存
            if self.config.cache_enabled:
                self._save_cache()
            
            self.logger.info(f"Plugin discovery completed: {len(self._discovered_plugins)} plugins found")
            
            return self._discovered_plugins
            
        except Exception as e:
            self.logger.error(f"Plugin discovery failed: {e}")
            return {}
    
    def _search_path(self, search_path: str):
        """搜索指定路径"""
        try:
            # 展开路径
            path = Path(search_path).expanduser().resolve()
            
            if not path.exists():
                self.logger.debug(f"Search path does not exist: {path}")
                return
            
            self.logger.debug(f"Searching path: {path}")
            
            # 递归搜索
            if self.config.recursive_search:
                self._search_recursive(path, 0)
            else:
                self._search_directory(path)
                
        except Exception as e:
            self.logger.error(f"Failed to search path {search_path}: {e}")
    
    def _search_recursive(self, directory: Path, depth: int):
        """递归搜索目录"""
        try:
            if depth > self.config.max_depth:
                return
            
            # 搜索当前目录
            self._search_directory(directory)
            
            # 递归搜索子目录
            for item in directory.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    self._search_recursive(item, depth + 1)
                    
        except Exception as e:
            self.logger.error(f"Failed to search directory recursively: {e}")
    
    def _search_directory(self, directory: Path):
        """搜索单个目录"""
        try:
            # 查找清单文件
            manifest_file = directory / self.config.manifest_filename
            if manifest_file.exists():
                plugin_info = self._parse_manifest(manifest_file)
                if plugin_info:
                    self._discovered_plugins[plugin_info['id']] = plugin_info
                    return
            
            # 查找Python文件
            for pattern in self.config.file_patterns:
                for file_path in directory.glob(pattern):
                    if file_path.is_file():
                        plugin_info = self._analyze_python_file(file_path)
                        if plugin_info:
                            self._discovered_plugins[plugin_info['id']] = plugin_info
                            break
                            
        except Exception as e:
            self.logger.error(f"Failed to search directory {directory}: {e}")
    
    def _parse_manifest(self, manifest_file: Path) -> Optional[Dict[str, Any]]:
        """解析插件清单文件"""
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
            
            # 验证必需字段
            required_fields = ['id', 'name', 'version', 'entry_point']
            for field in required_fields:
                if field not in manifest_data:
                    self.logger.warning(f"Missing required field '{field}' in manifest: {manifest_file}")
                    return None
            
            # 补充路径信息
            manifest_data['manifest_path'] = str(manifest_file)
            manifest_data['plugin_dir'] = str(manifest_file.parent)
            manifest_data['discovery_method'] = 'manifest'
            
            # 验证入口点文件
            entry_point = manifest_file.parent / manifest_data['entry_point']
            if not entry_point.exists():
                self.logger.warning(f"Entry point file not found: {entry_point}")
                return None
            
            manifest_data['entry_point_path'] = str(entry_point)
            
            self.logger.debug(f"Plugin found via manifest: {manifest_data['id']}")
            
            return manifest_data
            
        except Exception as e:
            self.logger.error(f"Failed to parse manifest {manifest_file}: {e}")
            return None
    
    def _analyze_python_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """分析Python文件"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找插件标识
            if not self._is_plugin_file(content):
                return None
            
            # 尝试导入模块获取信息
            plugin_info = self._extract_plugin_info(file_path, content)
            
            if plugin_info:
                plugin_info['discovery_method'] = 'analysis'
                plugin_info['entry_point_path'] = str(file_path)
                plugin_info['plugin_dir'] = str(file_path.parent)
                
                self.logger.debug(f"Plugin found via analysis: {plugin_info['id']}")
            
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze Python file {file_path}: {e}")
            return None
    
    def _is_plugin_file(self, content: str) -> bool:
        """检查是否为插件文件"""
        try:
            # 查找插件标识
            plugin_indicators = [
                'BasePlugin',
                'DetectorPlugin',
                'ProcessorPlugin',
                'class.*Plugin',
                '__plugin_info__',
                'PLUGIN_INFO'
            ]
            
            for indicator in plugin_indicators:
                if indicator in content:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check plugin file: {e}")
            return False
    
    def _extract_plugin_info(self, file_path: Path, content: str) -> Optional[Dict[str, Any]]:
        """提取插件信息"""
        try:
            # 尝试动态导入模块
            spec = importlib.util.spec_from_file_location("temp_plugin", file_path)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件信息
            plugin_info = None
            
            # 方法1: 查找__plugin_info__属性
            if hasattr(module, '__plugin_info__'):
                plugin_info = module.__plugin_info__
            
            # 方法2: 查找PLUGIN_INFO常量
            elif hasattr(module, 'PLUGIN_INFO'):
                plugin_info = module.PLUGIN_INFO
            
            # 方法3: 查找插件类
            else:
                plugin_class = self._find_plugin_class(module)
                if plugin_class:
                    plugin_info = self._extract_class_info(plugin_class)
            
            if plugin_info and isinstance(plugin_info, dict):
                # 验证和补充信息
                if 'id' not in plugin_info:
                    plugin_info['id'] = file_path.stem
                
                if 'name' not in plugin_info:
                    plugin_info['name'] = plugin_info['id']
                
                if 'version' not in plugin_info:
                    plugin_info['version'] = '1.0.0'
                
                return plugin_info
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract plugin info from {file_path}: {e}")
            return None
    
    def _find_plugin_class(self, module) -> Optional[type]:
        """查找插件类"""
        try:
            for name in dir(module):
                obj = getattr(module, name)
                
                if (isinstance(obj, type) and 
                    hasattr(obj, '__bases__') and
                    any('Plugin' in base.__name__ for base in obj.__bases__)):
                    return obj
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find plugin class: {e}")
            return None
    
    def _extract_class_info(self, plugin_class: type) -> Dict[str, Any]:
        """从插件类提取信息"""
        try:
            info = {
                'id': plugin_class.__name__,
                'name': getattr(plugin_class, 'name', plugin_class.__name__),
                'version': getattr(plugin_class, 'version', '1.0.0'),
                'description': getattr(plugin_class, 'description', ''),
                'author': getattr(plugin_class, 'author', ''),
                'class_name': plugin_class.__name__
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to extract class info: {e}")
            return {}
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        获取插件信息
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            插件信息
        """
        return self._discovered_plugins.get(plugin_id)
    
    def get_plugins_by_type(self, plugin_type: str) -> List[Dict[str, Any]]:
        """
        按类型获取插件
        
        Args:
            plugin_type: 插件类型
            
        Returns:
            插件列表
        """
        try:
            plugins = []
            
            for plugin_info in self._discovered_plugins.values():
                if plugin_info.get('type') == plugin_type:
                    plugins.append(plugin_info)
            
            return plugins
            
        except Exception as e:
            self.logger.error(f"Failed to get plugins by type: {e}")
            return []
    
    def search_plugins(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索插件
        
        Args:
            query: 搜索查询
            
        Returns:
            匹配的插件列表
        """
        try:
            results = []
            query_lower = query.lower()
            
            for plugin_info in self._discovered_plugins.values():
                # 搜索名称、描述、标签等
                searchable_fields = [
                    plugin_info.get('name', ''),
                    plugin_info.get('description', ''),
                    plugin_info.get('author', ''),
                    ' '.join(plugin_info.get('tags', []))
                ]
                
                searchable_text = ' '.join(searchable_fields).lower()
                
                if query_lower in searchable_text:
                    results.append(plugin_info)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search plugins: {e}")
            return []
    
    def _load_cache(self):
        """加载缓存"""
        try:
            cache_file = Path(self.config.cache_file)
            
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self._plugin_cache = json.load(f)
                
                self.logger.debug(f"Plugin cache loaded: {len(self._plugin_cache)} entries")
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin cache: {e}")
    
    def _save_cache(self):
        """保存缓存"""
        try:
            cache_data = {
                'timestamp': str(datetime.now()),
                'plugins': self._discovered_plugins
            }
            
            cache_file = Path(self.config.cache_file)
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("Plugin cache saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save plugin cache: {e}")
    
    def clear_cache(self):
        """清理缓存"""
        try:
            cache_file = Path(self.config.cache_file)
            if cache_file.exists():
                cache_file.unlink()
            
            self._plugin_cache.clear()
            self.logger.info("Plugin cache cleared")
            
        except Exception as e:
            self.logger.error(f"Failed to clear plugin cache: {e}")
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """获取发现统计信息"""
        try:
            stats = {
                'total_plugins': len(self._discovered_plugins),
                'discovery_methods': {},
                'plugin_types': {},
                'search_paths': self.config.search_paths
            }
            
            # 统计发现方法
            for plugin_info in self._discovered_plugins.values():
                method = plugin_info.get('discovery_method', 'unknown')
                stats['discovery_methods'][method] = stats['discovery_methods'].get(method, 0) + 1
            
            # 统计插件类型
            for plugin_info in self._discovered_plugins.values():
                plugin_type = plugin_info.get('type', 'unknown')
                stats['plugin_types'][plugin_type] = stats['plugin_types'].get(plugin_type, 0) + 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get discovery stats: {e}")
            return {}
    
    def cleanup(self):
        """清理资源"""
        try:
            self._discovered_plugins.clear()
            self._plugin_cache.clear()
            self.logger.info("Plugin discovery cleanup completed")
        except Exception as e:
            self.logger.error(f"Plugin discovery cleanup failed: {e}")
