"""
Authentication Management
身份认证管理
"""

import hashlib
import secrets
import jwt
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from loguru import logger


class AuthenticationManager:
    """身份认证管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化身份认证管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="AuthenticationManager")
        
        # 认证配置
        self.auth_config = self.config.get('authentication', {
            'jwt_secret': secrets.token_urlsafe(32),
            'jwt_algorithm': 'HS256',
            'token_expiry_hours': 24,
            'refresh_token_expiry_days': 30,
            'max_login_attempts': 5,
            'lockout_duration_minutes': 30,
            'password_min_length': 8,
            'password_require_special': True,
            'password_require_numbers': True,
            'password_require_uppercase': True,
            'enable_2fa': False,
            'session_timeout_minutes': 60
        })
        
        # 用户管理器
        self.user_manager = UserManager(config)
        
        # 活动会话
        self.active_sessions = {}
        
        # 登录尝试跟踪
        self.login_attempts = {}
        
        self.logger.info("Authentication manager initialized")
    
    def authenticate_user(self, username: str, password: str, 
                         totp_code: Optional[str] = None) -> Dict[str, Any]:
        """
        用户身份认证
        
        Args:
            username: 用户名
            password: 密码
            totp_code: TOTP验证码（如果启用2FA）
            
        Returns:
            认证结果
        """
        try:
            # 检查账户锁定
            if self._is_account_locked(username):
                return {
                    'success': False,
                    'error': 'account_locked',
                    'message': 'Account is temporarily locked due to too many failed attempts'
                }
            
            # 验证用户凭据
            user = self.user_manager.get_user(username)
            if not user:
                self._record_failed_attempt(username)
                return {
                    'success': False,
                    'error': 'invalid_credentials',
                    'message': 'Invalid username or password'
                }
            
            # 验证密码
            if not self._verify_password(password, user['password_hash']):
                self._record_failed_attempt(username)
                return {
                    'success': False,
                    'error': 'invalid_credentials',
                    'message': 'Invalid username or password'
                }
            
            # 检查账户状态
            if not user.get('active', True):
                return {
                    'success': False,
                    'error': 'account_disabled',
                    'message': 'Account is disabled'
                }
            
            # 2FA验证
            if self.auth_config['enable_2fa'] and user.get('totp_secret'):
                if not totp_code:
                    return {
                        'success': False,
                        'error': 'totp_required',
                        'message': 'TOTP code required'
                    }
                
                if not self._verify_totp(user['totp_secret'], totp_code):
                    self._record_failed_attempt(username)
                    return {
                        'success': False,
                        'error': 'invalid_totp',
                        'message': 'Invalid TOTP code'
                    }
            
            # 清除失败尝试记录
            self._clear_failed_attempts(username)
            
            # 生成访问令牌
            access_token = self._generate_access_token(user)
            refresh_token = self._generate_refresh_token(user)
            
            # 创建会话
            session_id = self._create_session(user, access_token)
            
            # 更新最后登录时间
            self.user_manager.update_last_login(username)
            
            self.logger.info(f"User authenticated successfully: {username}")
            
            return {
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user.get('email', ''),
                    'roles': user.get('roles', []),
                    'permissions': user.get('permissions', [])
                },
                'tokens': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': self.auth_config['token_expiry_hours'] * 3600
                },
                'session_id': session_id
            }
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return {
                'success': False,
                'error': 'authentication_error',
                'message': 'Authentication failed due to internal error'
            }
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        try:
            # 提取盐值和哈希
            parts = password_hash.split('$')
            if len(parts) != 3:
                return False
            
            algorithm, salt, stored_hash = parts
            
            # 计算密码哈希
            computed_hash = hashlib.pbkdf2_hmac(
                algorithm, 
                password.encode('utf-8'), 
                salt.encode('utf-8'), 
                100000
            ).hex()
            
            return secrets.compare_digest(computed_hash, stored_hash)
            
        except Exception as e:
            self.logger.error(f"Password verification failed: {e}")
            return False
    
    def _generate_access_token(self, user: Dict[str, Any]) -> str:
        """生成访问令牌"""
        try:
            payload = {
                'user_id': user['id'],
                'username': user['username'],
                'roles': user.get('roles', []),
                'permissions': user.get('permissions', []),
                'iat': int(time.time()),
                'exp': int(time.time()) + (self.auth_config['token_expiry_hours'] * 3600),
                'type': 'access'
            }
            
            token = jwt.encode(
                payload,
                self.auth_config['jwt_secret'],
                algorithm=self.auth_config['jwt_algorithm']
            )
            
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to generate access token: {e}")
            raise
    
    def _generate_refresh_token(self, user: Dict[str, Any]) -> str:
        """生成刷新令牌"""
        try:
            payload = {
                'user_id': user['id'],
                'username': user['username'],
                'iat': int(time.time()),
                'exp': int(time.time()) + (self.auth_config['refresh_token_expiry_days'] * 24 * 3600),
                'type': 'refresh'
            }
            
            token = jwt.encode(
                payload,
                self.auth_config['jwt_secret'],
                algorithm=self.auth_config['jwt_algorithm']
            )
            
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to generate refresh token: {e}")
            raise
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        验证令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            验证结果
        """
        try:
            payload = jwt.decode(
                token,
                self.auth_config['jwt_secret'],
                algorithms=[self.auth_config['jwt_algorithm']]
            )
            
            # 检查令牌类型
            if payload.get('type') != 'access':
                return {
                    'valid': False,
                    'error': 'invalid_token_type'
                }
            
            # 检查用户是否仍然存在且活跃
            user = self.user_manager.get_user_by_id(payload['user_id'])
            if not user or not user.get('active', True):
                return {
                    'valid': False,
                    'error': 'user_inactive'
                }
            
            return {
                'valid': True,
                'payload': payload,
                'user': user
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'error': 'token_expired'
            }
        except jwt.InvalidTokenError:
            return {
                'valid': False,
                'error': 'invalid_token'
            }
        except Exception as e:
            self.logger.error(f"Token verification failed: {e}")
            return {
                'valid': False,
                'error': 'verification_error'
            }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        刷新访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            新的令牌
        """
        try:
            payload = jwt.decode(
                refresh_token,
                self.auth_config['jwt_secret'],
                algorithms=[self.auth_config['jwt_algorithm']]
            )
            
            # 检查令牌类型
            if payload.get('type') != 'refresh':
                return {
                    'success': False,
                    'error': 'invalid_token_type'
                }
            
            # 获取用户信息
            user = self.user_manager.get_user_by_id(payload['user_id'])
            if not user or not user.get('active', True):
                return {
                    'success': False,
                    'error': 'user_inactive'
                }
            
            # 生成新的访问令牌
            new_access_token = self._generate_access_token(user)
            
            return {
                'success': True,
                'access_token': new_access_token,
                'expires_in': self.auth_config['token_expiry_hours'] * 3600
            }
            
        except jwt.ExpiredSignatureError:
            return {
                'success': False,
                'error': 'refresh_token_expired'
            }
        except jwt.InvalidTokenError:
            return {
                'success': False,
                'error': 'invalid_refresh_token'
            }
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
            return {
                'success': False,
                'error': 'refresh_error'
            }
    
    def _create_session(self, user: Dict[str, Any], access_token: str) -> str:
        """创建会话"""
        session_id = secrets.token_urlsafe(32)
        
        self.active_sessions[session_id] = {
            'user_id': user['id'],
            'username': user['username'],
            'access_token': access_token,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'ip_address': None,  # 可以从请求中获取
            'user_agent': None   # 可以从请求中获取
        }
        
        return session_id
    
    def logout(self, session_id: str) -> bool:
        """
        用户登出
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否登出成功
        """
        try:
            if session_id in self.active_sessions:
                username = self.active_sessions[session_id]['username']
                del self.active_sessions[session_id]
                self.logger.info(f"User logged out: {username}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Logout failed: {e}")
            return False
    
    def _is_account_locked(self, username: str) -> bool:
        """检查账户是否被锁定"""
        if username not in self.login_attempts:
            return False
        
        attempts = self.login_attempts[username]
        
        # 检查尝试次数
        if attempts['count'] < self.auth_config['max_login_attempts']:
            return False
        
        # 检查锁定时间
        lockout_duration = timedelta(minutes=self.auth_config['lockout_duration_minutes'])
        if datetime.now() - attempts['last_attempt'] > lockout_duration:
            # 锁定时间已过，清除记录
            del self.login_attempts[username]
            return False
        
        return True
    
    def _record_failed_attempt(self, username: str):
        """记录失败的登录尝试"""
        if username not in self.login_attempts:
            self.login_attempts[username] = {
                'count': 0,
                'first_attempt': datetime.now(),
                'last_attempt': datetime.now()
            }
        
        self.login_attempts[username]['count'] += 1
        self.login_attempts[username]['last_attempt'] = datetime.now()
    
    def _clear_failed_attempts(self, username: str):
        """清除失败的登录尝试记录"""
        if username in self.login_attempts:
            del self.login_attempts[username]
    
    def _verify_totp(self, secret: str, code: str) -> bool:
        """验证TOTP代码"""
        try:
            import pyotp
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=1)
        except ImportError:
            self.logger.warning("pyotp not installed, TOTP verification disabled")
            return True
        except Exception as e:
            self.logger.error(f"TOTP verification failed: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            self.active_sessions.clear()
            self.login_attempts.clear()
            self.logger.info("Authentication manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Authentication cleanup failed: {e}")


class UserManager:
    """用户管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化用户管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="UserManager")
        
        # 用户数据文件
        self.users_file = Path(self.config.get('users_file', './data/users.json'))
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 用户数据
        self.users = {}
        
        # 加载用户数据
        self._load_users()
        
        self.logger.info("User manager initialized")
    
    def _load_users(self):
        """加载用户数据"""
        try:
            if self.users_file.exists():
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            else:
                # 创建默认管理员用户
                self._create_default_admin()
                
        except Exception as e:
            self.logger.error(f"Failed to load users: {e}")
            self._create_default_admin()
    
    def _save_users(self):
        """保存用户数据"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save users: {e}")
    
    def _create_default_admin(self):
        """创建默认管理员用户"""
        try:
            admin_user = {
                'id': 'admin',
                'username': 'admin',
                'email': 'admin@shotdetection.local',
                'password_hash': self._hash_password('admin123'),
                'roles': ['admin'],
                'permissions': ['*'],
                'active': True,
                'created_at': datetime.now().isoformat(),
                'last_login': None
            }
            
            self.users['admin'] = admin_user
            self._save_users()
            
            self.logger.info("Default admin user created (username: admin, password: admin123)")
            
        except Exception as e:
            self.logger.error(f"Failed to create default admin: {e}")
    
    def _hash_password(self, password: str) -> str:
        """哈希密码"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        
        return f"sha256${salt}${password_hash}"
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        return self.users.get(username)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取用户信息"""
        for user in self.users.values():
            if user['id'] == user_id:
                return user
        return None
    
    def create_user(self, username: str, password: str, email: str = "", 
                   roles: List[str] = None, permissions: List[str] = None) -> bool:
        """
        创建用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            roles: 角色列表
            permissions: 权限列表
            
        Returns:
            是否创建成功
        """
        try:
            if username in self.users:
                self.logger.warning(f"User already exists: {username}")
                return False
            
            user = {
                'id': secrets.token_urlsafe(16),
                'username': username,
                'email': email,
                'password_hash': self._hash_password(password),
                'roles': roles or [],
                'permissions': permissions or [],
                'active': True,
                'created_at': datetime.now().isoformat(),
                'last_login': None
            }
            
            self.users[username] = user
            self._save_users()
            
            self.logger.info(f"User created: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create user {username}: {e}")
            return False
    
    def update_last_login(self, username: str):
        """更新最后登录时间"""
        try:
            if username in self.users:
                self.users[username]['last_login'] = datetime.now().isoformat()
                self._save_users()
                
        except Exception as e:
            self.logger.error(f"Failed to update last login for {username}: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self._save_users()
            self.logger.info("User manager cleanup completed")
        except Exception as e:
            self.logger.error(f"User manager cleanup failed: {e}")
