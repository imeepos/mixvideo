"""
Authorization Management
授权管理
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from loguru import logger


class AuthorizationManager:
    """授权管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化授权管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="AuthorizationManager")
        
        # 权限管理器
        self.permission_manager = PermissionManager(config)
        
        # 角色权限映射
        self.role_permissions = {}
        
        # 用户角色映射
        self.user_roles = {}
        
        # 资源权限要求
        self.resource_permissions = {}
        
        # 加载配置
        self._load_authorization_config()
        
        self.logger.info("Authorization manager initialized")
    
    def _load_authorization_config(self):
        """加载授权配置"""
        try:
            # 默认角色权限配置
            self.role_permissions = {
                'admin': ['*'],  # 管理员拥有所有权限
                'user': [
                    'video.view',
                    'video.upload',
                    'detection.run',
                    'detection.view_results',
                    'export.basic'
                ],
                'viewer': [
                    'video.view',
                    'detection.view_results'
                ],
                'operator': [
                    'video.view',
                    'video.upload',
                    'video.delete',
                    'detection.run',
                    'detection.view_results',
                    'detection.manage',
                    'export.basic',
                    'export.advanced'
                ]
            }
            
            # 默认资源权限要求
            self.resource_permissions = {
                '/api/videos': ['video.view'],
                '/api/videos/upload': ['video.upload'],
                '/api/videos/delete': ['video.delete'],
                '/api/detection/run': ['detection.run'],
                '/api/detection/results': ['detection.view_results'],
                '/api/detection/manage': ['detection.manage'],
                '/api/export/basic': ['export.basic'],
                '/api/export/advanced': ['export.advanced'],
                '/api/admin/*': ['admin.*'],
                '/api/system/*': ['system.*']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to load authorization config: {e}")
    
    def check_permission(self, user: Dict[str, Any], permission: str) -> bool:
        """
        检查用户权限
        
        Args:
            user: 用户信息
            permission: 权限名称
            
        Returns:
            是否有权限
        """
        try:
            # 检查用户是否活跃
            if not user.get('active', True):
                return False
            
            # 获取用户权限
            user_permissions = self._get_user_permissions(user)
            
            # 检查通配符权限
            if '*' in user_permissions:
                return True
            
            # 检查精确匹配
            if permission in user_permissions:
                return True
            
            # 检查通配符匹配
            for perm in user_permissions:
                if perm.endswith('*'):
                    prefix = perm[:-1]
                    if permission.startswith(prefix):
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Permission check failed: {e}")
            return False
    
    def check_resource_access(self, user: Dict[str, Any], resource: str, 
                            method: str = 'GET') -> bool:
        """
        检查资源访问权限
        
        Args:
            user: 用户信息
            resource: 资源路径
            method: HTTP方法
            
        Returns:
            是否有访问权限
        """
        try:
            # 获取资源所需权限
            required_permissions = self._get_resource_permissions(resource, method)
            
            if not required_permissions:
                # 如果没有配置权限要求，默认允许
                return True
            
            # 检查用户是否拥有所需权限
            for permission in required_permissions:
                if not self.check_permission(user, permission):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Resource access check failed: {e}")
            return False
    
    def _get_user_permissions(self, user: Dict[str, Any]) -> Set[str]:
        """获取用户所有权限"""
        permissions = set()
        
        # 添加直接权限
        user_permissions = user.get('permissions', [])
        permissions.update(user_permissions)
        
        # 添加角色权限
        user_roles = user.get('roles', [])
        for role in user_roles:
            role_permissions = self.role_permissions.get(role, [])
            permissions.update(role_permissions)
        
        return permissions
    
    def _get_resource_permissions(self, resource: str, method: str) -> List[str]:
        """获取资源所需权限"""
        # 精确匹配
        if resource in self.resource_permissions:
            return self.resource_permissions[resource]
        
        # 通配符匹配
        for pattern, permissions in self.resource_permissions.items():
            if pattern.endswith('*'):
                prefix = pattern[:-1]
                if resource.startswith(prefix):
                    return permissions
        
        return []
    
    def add_role_permission(self, role: str, permission: str) -> bool:
        """
        为角色添加权限
        
        Args:
            role: 角色名称
            permission: 权限名称
            
        Returns:
            是否添加成功
        """
        try:
            if role not in self.role_permissions:
                self.role_permissions[role] = []
            
            if permission not in self.role_permissions[role]:
                self.role_permissions[role].append(permission)
                self.logger.info(f"Added permission {permission} to role {role}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to add role permission: {e}")
            return False
    
    def remove_role_permission(self, role: str, permission: str) -> bool:
        """
        从角色移除权限
        
        Args:
            role: 角色名称
            permission: 权限名称
            
        Returns:
            是否移除成功
        """
        try:
            if role in self.role_permissions and permission in self.role_permissions[role]:
                self.role_permissions[role].remove(permission)
                self.logger.info(f"Removed permission {permission} from role {role}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove role permission: {e}")
            return False
    
    def get_role_permissions(self, role: str) -> List[str]:
        """获取角色权限"""
        return self.role_permissions.get(role, [])
    
    def get_user_effective_permissions(self, user: Dict[str, Any]) -> List[str]:
        """获取用户有效权限"""
        return list(self._get_user_permissions(user))
    
    def create_role(self, role: str, permissions: List[str] = None) -> bool:
        """
        创建角色
        
        Args:
            role: 角色名称
            permissions: 权限列表
            
        Returns:
            是否创建成功
        """
        try:
            if role in self.role_permissions:
                self.logger.warning(f"Role already exists: {role}")
                return False
            
            self.role_permissions[role] = permissions or []
            self.logger.info(f"Created role: {role}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create role {role}: {e}")
            return False
    
    def delete_role(self, role: str) -> bool:
        """
        删除角色
        
        Args:
            role: 角色名称
            
        Returns:
            是否删除成功
        """
        try:
            if role in self.role_permissions:
                del self.role_permissions[role]
                self.logger.info(f"Deleted role: {role}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete role {role}: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            self.permission_manager.cleanup()
            self.logger.info("Authorization manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Authorization cleanup failed: {e}")


class PermissionManager:
    """权限管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化权限管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="PermissionManager")
        
        # 权限定义文件
        self.permissions_file = Path(self.config.get('permissions_file', './data/permissions.json'))
        self.permissions_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 权限定义
        self.permissions = {}
        
        # 权限组
        self.permission_groups = {}
        
        # 加载权限定义
        self._load_permissions()
        
        self.logger.info("Permission manager initialized")
    
    def _load_permissions(self):
        """加载权限定义"""
        try:
            if self.permissions_file.exists():
                with open(self.permissions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.permissions = data.get('permissions', {})
                    self.permission_groups = data.get('groups', {})
            else:
                self._create_default_permissions()
                
        except Exception as e:
            self.logger.error(f"Failed to load permissions: {e}")
            self._create_default_permissions()
    
    def _save_permissions(self):
        """保存权限定义"""
        try:
            data = {
                'permissions': self.permissions,
                'groups': self.permission_groups,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.permissions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save permissions: {e}")
    
    def _create_default_permissions(self):
        """创建默认权限定义"""
        try:
            self.permissions = {
                'video.view': {
                    'name': 'View Videos',
                    'description': 'View video files and metadata',
                    'category': 'video'
                },
                'video.upload': {
                    'name': 'Upload Videos',
                    'description': 'Upload new video files',
                    'category': 'video'
                },
                'video.delete': {
                    'name': 'Delete Videos',
                    'description': 'Delete video files',
                    'category': 'video'
                },
                'detection.run': {
                    'name': 'Run Detection',
                    'description': 'Execute shot detection algorithms',
                    'category': 'detection'
                },
                'detection.view_results': {
                    'name': 'View Detection Results',
                    'description': 'View shot detection results',
                    'category': 'detection'
                },
                'detection.manage': {
                    'name': 'Manage Detection',
                    'description': 'Manage detection settings and algorithms',
                    'category': 'detection'
                },
                'export.basic': {
                    'name': 'Basic Export',
                    'description': 'Export results in basic formats',
                    'category': 'export'
                },
                'export.advanced': {
                    'name': 'Advanced Export',
                    'description': 'Export results in advanced formats',
                    'category': 'export'
                },
                'admin.*': {
                    'name': 'Admin Access',
                    'description': 'Full administrative access',
                    'category': 'admin'
                },
                'system.*': {
                    'name': 'System Access',
                    'description': 'System-level operations',
                    'category': 'system'
                }
            }
            
            self.permission_groups = {
                'video': {
                    'name': 'Video Management',
                    'description': 'Permissions related to video file management',
                    'permissions': ['video.view', 'video.upload', 'video.delete']
                },
                'detection': {
                    'name': 'Detection Operations',
                    'description': 'Permissions related to shot detection',
                    'permissions': ['detection.run', 'detection.view_results', 'detection.manage']
                },
                'export': {
                    'name': 'Export Operations',
                    'description': 'Permissions related to result export',
                    'permissions': ['export.basic', 'export.advanced']
                },
                'admin': {
                    'name': 'Administration',
                    'description': 'Administrative permissions',
                    'permissions': ['admin.*', 'system.*']
                }
            }
            
            self._save_permissions()
            
        except Exception as e:
            self.logger.error(f"Failed to create default permissions: {e}")
    
    def get_permission(self, permission: str) -> Optional[Dict[str, Any]]:
        """获取权限定义"""
        return self.permissions.get(permission)
    
    def get_all_permissions(self) -> Dict[str, Dict[str, Any]]:
        """获取所有权限定义"""
        return self.permissions.copy()
    
    def get_permissions_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """根据类别获取权限"""
        return {
            perm: info for perm, info in self.permissions.items()
            if info.get('category') == category
        }
    
    def add_permission(self, permission: str, name: str, description: str, 
                      category: str = 'custom') -> bool:
        """
        添加权限定义
        
        Args:
            permission: 权限标识
            name: 权限名称
            description: 权限描述
            category: 权限类别
            
        Returns:
            是否添加成功
        """
        try:
            if permission in self.permissions:
                self.logger.warning(f"Permission already exists: {permission}")
                return False
            
            self.permissions[permission] = {
                'name': name,
                'description': description,
                'category': category,
                'created_at': datetime.now().isoformat()
            }
            
            self._save_permissions()
            self.logger.info(f"Added permission: {permission}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add permission {permission}: {e}")
            return False
    
    def remove_permission(self, permission: str) -> bool:
        """
        移除权限定义
        
        Args:
            permission: 权限标识
            
        Returns:
            是否移除成功
        """
        try:
            if permission in self.permissions:
                del self.permissions[permission]
                self._save_permissions()
                self.logger.info(f"Removed permission: {permission}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to remove permission {permission}: {e}")
            return False
    
    def get_permission_group(self, group: str) -> Optional[Dict[str, Any]]:
        """获取权限组"""
        return self.permission_groups.get(group)
    
    def get_all_permission_groups(self) -> Dict[str, Dict[str, Any]]:
        """获取所有权限组"""
        return self.permission_groups.copy()
    
    def cleanup(self):
        """清理资源"""
        try:
            self._save_permissions()
            self.logger.info("Permission manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Permission manager cleanup failed: {e}")
