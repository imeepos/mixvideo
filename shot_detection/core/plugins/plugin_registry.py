"""
Plugin Registry
插件注册表
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from .plugin_interface import PluginInterface, PluginType, PluginStatus


class PluginRegistry:
    """插件注册表"""
    
    def __init__(self, registry_file: Optional[str] = None):
        """
        初始化插件注册表
        
        Args:
            registry_file: 注册表文件路径
        """
        self.logger = logger.bind(component="PluginRegistry")
        self.registry_file = Path(registry_file or "./plugins/registry.json")
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 注册表数据
        self.registry_data = {
            'plugins': {},
            'metadata': {
                'version': '1.0',
                'created_at': self._get_current_timestamp(),
                'last_updated': self._get_current_timestamp()
            }
        }
        
        # 加载注册表
        self._load_registry()
        
        self.logger.info("Plugin registry initialized")
    
    def _load_registry(self):
        """加载注册表"""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                
                # 合并数据
                if 'plugins' in loaded_data:
                    self.registry_data['plugins'] = loaded_data['plugins']
                
                if 'metadata' in loaded_data:
                    self.registry_data['metadata'].update(loaded_data['metadata'])
                
                self.logger.info("Plugin registry loaded")
            else:
                self._save_registry()
                
        except Exception as e:
            self.logger.error(f"Failed to load plugin registry: {e}")
    
    def _save_registry(self):
        """保存注册表"""
        try:
            self.registry_data['metadata']['last_updated'] = self._get_current_timestamp()
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("Plugin registry saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save plugin registry: {e}")
    
    def register_plugin(self, plugin: PluginInterface, plugin_path: str = "") -> bool:
        """
        注册插件
        
        Args:
            plugin: 插件实例
            plugin_path: 插件路径
            
        Returns:
            是否注册成功
        """
        try:
            plugin_id = plugin.plugin_id
            
            plugin_info = {
                'id': plugin_id,
                'name': plugin.plugin_name,
                'version': plugin.plugin_version,
                'type': plugin.plugin_type.value,
                'description': plugin.plugin_description,
                'author': plugin.plugin_author,
                'dependencies': plugin.plugin_dependencies,
                'path': plugin_path,
                'status': plugin.get_status().value,
                'config_schema': plugin.plugin_config_schema,
                'registered_at': self._get_current_timestamp(),
                'last_updated': self._get_current_timestamp()
            }
            
            self.registry_data['plugins'][plugin_id] = plugin_info
            self._save_registry()
            
            self.logger.info(f"Plugin registered: {plugin_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register plugin: {e}")
            return False
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """
        注销插件
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            是否注销成功
        """
        try:
            if plugin_id in self.registry_data['plugins']:
                del self.registry_data['plugins'][plugin_id]
                self._save_registry()
                
                self.logger.info(f"Plugin unregistered: {plugin_id}")
                return True
            else:
                self.logger.warning(f"Plugin not found in registry: {plugin_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to unregister plugin {plugin_id}: {e}")
            return False
    
    def update_plugin_status(self, plugin_id: str, status: PluginStatus) -> bool:
        """
        更新插件状态
        
        Args:
            plugin_id: 插件ID
            status: 新状态
            
        Returns:
            是否更新成功
        """
        try:
            if plugin_id in self.registry_data['plugins']:
                self.registry_data['plugins'][plugin_id]['status'] = status.value
                self.registry_data['plugins'][plugin_id]['last_updated'] = self._get_current_timestamp()
                self._save_registry()
                
                self.logger.debug(f"Plugin status updated: {plugin_id} -> {status.value}")
                return True
            else:
                self.logger.warning(f"Plugin not found in registry: {plugin_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update plugin status {plugin_id}: {e}")
            return False
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """
        获取插件信息
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            插件信息
        """
        return self.registry_data['plugins'].get(plugin_id)
    
    def get_all_plugins(self) -> Dict[str, Dict[str, Any]]:
        """获取所有插件信息"""
        return self.registry_data['plugins'].copy()
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> Dict[str, Dict[str, Any]]:
        """
        根据类型获取插件
        
        Args:
            plugin_type: 插件类型
            
        Returns:
            指定类型的插件信息
        """
        return {
            plugin_id: plugin_info
            for plugin_id, plugin_info in self.registry_data['plugins'].items()
            if plugin_info['type'] == plugin_type.value
        }
    
    def get_plugins_by_status(self, status: PluginStatus) -> Dict[str, Dict[str, Any]]:
        """
        根据状态获取插件
        
        Args:
            status: 插件状态
            
        Returns:
            指定状态的插件信息
        """
        return {
            plugin_id: plugin_info
            for plugin_id, plugin_info in self.registry_data['plugins'].items()
            if plugin_info['status'] == status.value
        }
    
    def search_plugins(self, query: str) -> Dict[str, Dict[str, Any]]:
        """
        搜索插件
        
        Args:
            query: 搜索查询
            
        Returns:
            匹配的插件信息
        """
        query_lower = query.lower()
        results = {}
        
        for plugin_id, plugin_info in self.registry_data['plugins'].items():
            # 搜索名称、描述、作者
            searchable_text = f"{plugin_info['name']} {plugin_info['description']} {plugin_info['author']}".lower()
            
            if query_lower in searchable_text or query_lower in plugin_id.lower():
                results[plugin_id] = plugin_info
        
        return results
    
    def get_plugin_dependencies(self, plugin_id: str) -> List[str]:
        """
        获取插件依赖
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            依赖列表
        """
        plugin_info = self.get_plugin_info(plugin_id)
        if plugin_info:
            return plugin_info.get('dependencies', [])
        return []
    
    def get_dependent_plugins(self, plugin_id: str) -> List[str]:
        """
        获取依赖指定插件的插件列表
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            依赖插件的ID列表
        """
        dependent_plugins = []
        
        for pid, plugin_info in self.registry_data['plugins'].items():
            dependencies = plugin_info.get('dependencies', [])
            if plugin_id in dependencies:
                dependent_plugins.append(pid)
        
        return dependent_plugins
    
    def validate_dependencies(self, plugin_id: str) -> tuple[bool, List[str]]:
        """
        验证插件依赖
        
        Args:
            plugin_id: 插件ID
            
        Returns:
            (是否有效, 缺失的依赖列表)
        """
        dependencies = self.get_plugin_dependencies(plugin_id)
        missing_deps = []
        
        for dep in dependencies:
            if dep not in self.registry_data['plugins']:
                missing_deps.append(dep)
        
        return len(missing_deps) == 0, missing_deps
    
    def get_load_order(self, plugin_ids: Optional[List[str]] = None) -> List[str]:
        """
        获取插件加载顺序（基于依赖关系）
        
        Args:
            plugin_ids: 要排序的插件ID列表，如果为None则使用所有插件
            
        Returns:
            排序后的插件ID列表
        """
        if plugin_ids is None:
            plugin_ids = list(self.registry_data['plugins'].keys())
        
        # 拓扑排序
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(plugin_id: str):
            if plugin_id in temp_visited:
                # 检测到循环依赖
                self.logger.warning(f"Circular dependency detected involving: {plugin_id}")
                return
            
            if plugin_id in visited:
                return
            
            temp_visited.add(plugin_id)
            
            # 访问依赖
            dependencies = self.get_plugin_dependencies(plugin_id)
            for dep in dependencies:
                if dep in plugin_ids:
                    visit(dep)
            
            temp_visited.remove(plugin_id)
            visited.add(plugin_id)
            result.append(plugin_id)
        
        for plugin_id in plugin_ids:
            if plugin_id not in visited:
                visit(plugin_id)
        
        return result
    
    def get_registry_statistics(self) -> Dict[str, Any]:
        """获取注册表统计信息"""
        plugins = self.registry_data['plugins']
        
        # 按类型统计
        type_counts = {}
        for plugin_info in plugins.values():
            plugin_type = plugin_info['type']
            type_counts[plugin_type] = type_counts.get(plugin_type, 0) + 1
        
        # 按状态统计
        status_counts = {}
        for plugin_info in plugins.values():
            status = plugin_info['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_plugins': len(plugins),
            'type_distribution': type_counts,
            'status_distribution': status_counts,
            'registry_metadata': self.registry_data['metadata']
        }
    
    def export_registry(self, export_path: str) -> bool:
        """
        导出注册表
        
        Args:
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        try:
            export_data = {
                'registry_data': self.registry_data,
                'statistics': self.get_registry_statistics(),
                'export_timestamp': self._get_current_timestamp()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Registry exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export registry: {e}")
            return False
    
    def import_registry(self, import_path: str, merge: bool = True) -> bool:
        """
        导入注册表
        
        Args:
            import_path: 导入路径
            merge: 是否合并现有数据
            
        Returns:
            是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'registry_data' in import_data:
                imported_registry = import_data['registry_data']
                
                if merge:
                    # 合并插件数据
                    self.registry_data['plugins'].update(imported_registry.get('plugins', {}))
                    
                    # 更新元数据
                    self.registry_data['metadata']['last_updated'] = self._get_current_timestamp()
                else:
                    # 完全替换
                    self.registry_data = imported_registry
                
                self._save_registry()
                
                self.logger.info(f"Registry imported from: {import_path}")
                return True
            else:
                self.logger.error("Invalid registry import file format")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to import registry: {e}")
            return False
    
    def clear_registry(self):
        """清空注册表"""
        try:
            self.registry_data['plugins'].clear()
            self.registry_data['metadata']['last_updated'] = self._get_current_timestamp()
            self._save_registry()
            
            self.logger.info("Registry cleared")
            
        except Exception as e:
            self.logger.error(f"Failed to clear registry: {e}")
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        return datetime.now().isoformat()
    
    def cleanup(self):
        """清理资源"""
        try:
            self._save_registry()
            self.logger.info("Plugin registry cleanup completed")
        except Exception as e:
            self.logger.error(f"Plugin registry cleanup failed: {e}")
