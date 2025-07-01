"""
Input Validation and Security Validation
输入验证和安全验证
"""

import re
import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urlparse
from loguru import logger


class InputValidator:
    """输入验证器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化输入验证器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="InputValidator")
        
        # 验证配置
        self.validation_config = self.config.get('validation', {
            'max_string_length': 1000,
            'max_file_size_mb': 100,
            'allowed_file_extensions': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
            'allowed_mime_types': ['video/mp4', 'video/avi', 'video/quicktime'],
            'blocked_patterns': ['<script', 'javascript:', 'vbscript:', 'onload='],
            'sql_injection_patterns': ['union', 'select', 'insert', 'update', 'delete', 'drop'],
            'path_traversal_patterns': ['../', '..\\', '/etc/', '/proc/', 'c:\\'],
            'enable_strict_mode': True
        })
        
        # 编译正则表达式
        self._compile_patterns()
        
        self.logger.info("Input validator initialized")
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        try:
            # 邮箱验证
            self.email_pattern = re.compile(
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            )
            
            # 用户名验证（字母数字下划线，3-20位）
            self.username_pattern = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
            
            # 密码验证（至少8位，包含字母和数字）
            self.password_pattern = re.compile(
                r'^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$'
            )
            
            # IP地址验证
            self.ip_pattern = re.compile(
                r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            )
            
            # URL验证
            self.url_pattern = re.compile(
                r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
            )
            
            # 文件名验证（不包含特殊字符）
            self.filename_pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
            
        except Exception as e:
            self.logger.error(f"Pattern compilation failed: {e}")
    
    def validate_string(self, value: str, field_name: str = "field", 
                       max_length: Optional[int] = None,
                       min_length: int = 0,
                       pattern: Optional[str] = None,
                       allow_empty: bool = True) -> Dict[str, Any]:
        """
        验证字符串
        
        Args:
            value: 要验证的字符串
            field_name: 字段名称
            max_length: 最大长度
            min_length: 最小长度
            pattern: 正则表达式模式
            allow_empty: 是否允许空值
            
        Returns:
            验证结果
        """
        try:
            errors = []
            
            # 类型检查
            if not isinstance(value, str):
                return {
                    'valid': False,
                    'errors': [f"{field_name} must be a string"],
                    'sanitized_value': str(value) if value is not None else ""
                }
            
            # 空值检查
            if not value.strip():
                if not allow_empty:
                    errors.append(f"{field_name} cannot be empty")
                return {
                    'valid': len(errors) == 0,
                    'errors': errors,
                    'sanitized_value': value.strip()
                }
            
            # 长度检查
            if len(value) < min_length:
                errors.append(f"{field_name} must be at least {min_length} characters")
            
            max_len = max_length or self.validation_config['max_string_length']
            if len(value) > max_len:
                errors.append(f"{field_name} must not exceed {max_len} characters")
            
            # 模式检查
            if pattern:
                if not re.match(pattern, value):
                    errors.append(f"{field_name} format is invalid")
            
            # 安全检查
            security_errors = self._check_security_patterns(value, field_name)
            errors.extend(security_errors)
            
            # 清理值
            sanitized_value = self._sanitize_string(value)
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'sanitized_value': sanitized_value
            }
            
        except Exception as e:
            self.logger.error(f"String validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'sanitized_value': ""
            }
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """验证邮箱地址"""
        try:
            if not email:
                return {
                    'valid': False,
                    'errors': ["Email is required"],
                    'sanitized_value': ""
                }
            
            # 基本格式检查
            if not self.email_pattern.match(email):
                return {
                    'valid': False,
                    'errors': ["Invalid email format"],
                    'sanitized_value': email.lower().strip()
                }
            
            # 长度检查
            if len(email) > 254:  # RFC 5321 限制
                return {
                    'valid': False,
                    'errors': ["Email address too long"],
                    'sanitized_value': email.lower().strip()
                }
            
            return {
                'valid': True,
                'errors': [],
                'sanitized_value': email.lower().strip()
            }
            
        except Exception as e:
            self.logger.error(f"Email validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Email validation error: {str(e)}"],
                'sanitized_value': ""
            }
    
    def validate_username(self, username: str) -> Dict[str, Any]:
        """验证用户名"""
        try:
            if not username:
                return {
                    'valid': False,
                    'errors': ["Username is required"],
                    'sanitized_value': ""
                }
            
            # 格式检查
            if not self.username_pattern.match(username):
                return {
                    'valid': False,
                    'errors': ["Username must be 3-20 characters, letters, numbers, and underscores only"],
                    'sanitized_value': username.lower().strip()
                }
            
            # 保留字检查
            reserved_usernames = ['admin', 'root', 'system', 'user', 'test', 'guest']
            if username.lower() in reserved_usernames:
                return {
                    'valid': False,
                    'errors': ["Username is reserved"],
                    'sanitized_value': username.lower().strip()
                }
            
            return {
                'valid': True,
                'errors': [],
                'sanitized_value': username.lower().strip()
            }
            
        except Exception as e:
            self.logger.error(f"Username validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Username validation error: {str(e)}"],
                'sanitized_value': ""
            }
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """验证密码"""
        try:
            errors = []
            
            if not password:
                return {
                    'valid': False,
                    'errors': ["Password is required"],
                    'strength': 'none'
                }
            
            # 长度检查
            if len(password) < 8:
                errors.append("Password must be at least 8 characters")
            
            if len(password) > 128:
                errors.append("Password must not exceed 128 characters")
            
            # 复杂度检查
            strength_score = 0
            
            if re.search(r'[a-z]', password):
                strength_score += 1
            else:
                errors.append("Password must contain lowercase letters")
            
            if re.search(r'[A-Z]', password):
                strength_score += 1
            else:
                errors.append("Password must contain uppercase letters")
            
            if re.search(r'\d', password):
                strength_score += 1
            else:
                errors.append("Password must contain numbers")
            
            if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                strength_score += 1
            
            # 强度评估
            if strength_score < 3:
                strength = 'weak'
            elif strength_score == 3:
                strength = 'medium'
            else:
                strength = 'strong'
            
            # 常见密码检查
            common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
            if password.lower() in common_passwords:
                errors.append("Password is too common")
                strength = 'weak'
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'strength': strength,
                'score': strength_score
            }
            
        except Exception as e:
            self.logger.error(f"Password validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Password validation error: {str(e)}"],
                'strength': 'none'
            }
    
    def validate_file_path(self, file_path: str) -> Dict[str, Any]:
        """验证文件路径"""
        try:
            errors = []
            
            if not file_path:
                return {
                    'valid': False,
                    'errors': ["File path is required"],
                    'sanitized_path': ""
                }
            
            # 路径遍历检查
            for pattern in self.validation_config['path_traversal_patterns']:
                if pattern.lower() in file_path.lower():
                    errors.append("Path traversal attempt detected")
                    break
            
            # 路径长度检查
            if len(file_path) > 260:  # Windows路径限制
                errors.append("File path too long")
            
            # 文件名检查
            path_obj = Path(file_path)
            filename = path_obj.name
            
            if not self.filename_pattern.match(filename):
                errors.append("Invalid characters in filename")
            
            # 扩展名检查
            file_ext = path_obj.suffix.lower()
            allowed_extensions = self.validation_config['allowed_file_extensions']
            
            if file_ext not in allowed_extensions:
                errors.append(f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}")
            
            # 清理路径
            sanitized_path = str(path_obj.resolve())
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'sanitized_path': sanitized_path,
                'filename': filename,
                'extension': file_ext
            }
            
        except Exception as e:
            self.logger.error(f"File path validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"File path validation error: {str(e)}"],
                'sanitized_path': ""
            }
    
    def validate_file_upload(self, file_path: str, max_size_mb: Optional[int] = None) -> Dict[str, Any]:
        """验证文件上传"""
        try:
            errors = []
            
            # 路径验证
            path_result = self.validate_file_path(file_path)
            if not path_result['valid']:
                return path_result
            
            # 文件存在检查
            if not os.path.exists(file_path):
                return {
                    'valid': False,
                    'errors': ["File does not exist"],
                    'sanitized_path': path_result['sanitized_path']
                }
            
            # 文件大小检查
            file_size = os.path.getsize(file_path)
            max_size = (max_size_mb or self.validation_config['max_file_size_mb']) * 1024 * 1024
            
            if file_size > max_size:
                errors.append(f"File size exceeds limit ({max_size_mb or self.validation_config['max_file_size_mb']}MB)")
            
            # MIME类型检查
            mime_type, _ = mimetypes.guess_type(file_path)
            allowed_mime_types = self.validation_config['allowed_mime_types']
            
            if mime_type and mime_type not in allowed_mime_types:
                errors.append(f"MIME type not allowed: {mime_type}")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'sanitized_path': path_result['sanitized_path'],
                'file_size': file_size,
                'mime_type': mime_type,
                'filename': path_result['filename'],
                'extension': path_result['extension']
            }
            
        except Exception as e:
            self.logger.error(f"File upload validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"File upload validation error: {str(e)}"],
                'sanitized_path': ""
            }
    
    def validate_url(self, url: str) -> Dict[str, Any]:
        """验证URL"""
        try:
            if not url:
                return {
                    'valid': False,
                    'errors': ["URL is required"],
                    'sanitized_url': ""
                }
            
            # 基本格式检查
            if not self.url_pattern.match(url):
                return {
                    'valid': False,
                    'errors': ["Invalid URL format"],
                    'sanitized_url': url.strip()
                }
            
            # 解析URL
            parsed = urlparse(url)
            
            # 协议检查
            if parsed.scheme not in ['http', 'https']:
                return {
                    'valid': False,
                    'errors': ["Only HTTP and HTTPS protocols are allowed"],
                    'sanitized_url': url.strip()
                }
            
            # 主机名检查
            if not parsed.netloc:
                return {
                    'valid': False,
                    'errors': ["Invalid hostname"],
                    'sanitized_url': url.strip()
                }
            
            return {
                'valid': True,
                'errors': [],
                'sanitized_url': url.strip(),
                'parsed': {
                    'scheme': parsed.scheme,
                    'netloc': parsed.netloc,
                    'path': parsed.path,
                    'query': parsed.query
                }
            }
            
        except Exception as e:
            self.logger.error(f"URL validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"URL validation error: {str(e)}"],
                'sanitized_url': ""
            }
    
    def _check_security_patterns(self, value: str, field_name: str) -> List[str]:
        """检查安全模式"""
        errors = []
        
        try:
            value_lower = value.lower()
            
            # XSS检查
            for pattern in self.validation_config['blocked_patterns']:
                if pattern.lower() in value_lower:
                    errors.append(f"{field_name} contains potentially dangerous content")
                    break
            
            # SQL注入检查
            for pattern in self.validation_config['sql_injection_patterns']:
                if pattern.lower() in value_lower:
                    errors.append(f"{field_name} contains potentially dangerous SQL content")
                    break
            
            # 路径遍历检查
            for pattern in self.validation_config['path_traversal_patterns']:
                if pattern.lower() in value_lower:
                    errors.append(f"{field_name} contains path traversal attempt")
                    break
            
        except Exception as e:
            self.logger.error(f"Security pattern check failed: {e}")
            errors.append(f"{field_name} security check failed")
        
        return errors
    
    def _sanitize_string(self, value: str) -> str:
        """清理字符串"""
        try:
            # 移除前后空白
            sanitized = value.strip()
            
            # 移除控制字符
            sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
            
            # HTML实体编码（基本）
            sanitized = sanitized.replace('&', '&amp;')
            sanitized = sanitized.replace('<', '&lt;')
            sanitized = sanitized.replace('>', '&gt;')
            sanitized = sanitized.replace('"', '&quot;')
            sanitized = sanitized.replace("'", '&#x27;')
            
            return sanitized
            
        except Exception as e:
            self.logger.error(f"String sanitization failed: {e}")
            return value


class SecurityValidator:
    """安全验证器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化安全验证器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="SecurityValidator")
        
        # 输入验证器
        self.input_validator = InputValidator(config)
        
        # 安全配置
        self.security_config = self.config.get('security_validation', {
            'enable_csrf_protection': True,
            'enable_rate_limiting': True,
            'max_requests_per_minute': 60,
            'enable_ip_whitelist': False,
            'ip_whitelist': [],
            'enable_ip_blacklist': True,
            'ip_blacklist': [],
            'session_timeout_minutes': 30
        })
        
        # 请求计数器（用于速率限制）
        self.request_counters = {}
        
        self.logger.info("Security validator initialized")
    
    def validate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证请求
        
        Args:
            request_data: 请求数据
            
        Returns:
            验证结果
        """
        try:
            errors = []
            
            # IP地址验证
            client_ip = request_data.get('client_ip')
            if client_ip:
                ip_check = self._validate_client_ip(client_ip)
                if not ip_check['valid']:
                    errors.extend(ip_check['errors'])
            
            # 速率限制检查
            if self.security_config['enable_rate_limiting']:
                rate_check = self._check_rate_limit(client_ip)
                if not rate_check['valid']:
                    errors.extend(rate_check['errors'])
            
            # CSRF令牌验证
            if self.security_config['enable_csrf_protection']:
                csrf_token = request_data.get('csrf_token')
                csrf_check = self._validate_csrf_token(csrf_token)
                if not csrf_check['valid']:
                    errors.extend(csrf_check['errors'])
            
            # 会话验证
            session_id = request_data.get('session_id')
            if session_id:
                session_check = self._validate_session(session_id)
                if not session_check['valid']:
                    errors.extend(session_check['errors'])
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'client_ip': client_ip
            }
            
        except Exception as e:
            self.logger.error(f"Request validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Request validation error: {str(e)}"]
            }
    
    def _validate_client_ip(self, client_ip: str) -> Dict[str, Any]:
        """验证客户端IP地址"""
        try:
            errors = []
            
            # IP格式验证
            if not self.input_validator.ip_pattern.match(client_ip):
                errors.append("Invalid IP address format")
                return {'valid': False, 'errors': errors}
            
            # 黑名单检查
            if (self.security_config['enable_ip_blacklist'] and 
                client_ip in self.security_config['ip_blacklist']):
                errors.append("IP address is blacklisted")
            
            # 白名单检查
            if (self.security_config['enable_ip_whitelist'] and 
                client_ip not in self.security_config['ip_whitelist']):
                errors.append("IP address not in whitelist")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors
            }
            
        except Exception as e:
            self.logger.error(f"IP validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"IP validation error: {str(e)}"]
            }
    
    def _check_rate_limit(self, client_ip: str) -> Dict[str, Any]:
        """检查速率限制"""
        try:
            if not client_ip:
                return {'valid': True, 'errors': []}
            
            current_time = int(time.time())
            minute_window = current_time // 60
            
            # 初始化计数器
            if client_ip not in self.request_counters:
                self.request_counters[client_ip] = {}
            
            # 清理旧的计数器
            old_windows = [w for w in self.request_counters[client_ip].keys() if w < minute_window - 1]
            for old_window in old_windows:
                del self.request_counters[client_ip][old_window]
            
            # 增加当前窗口计数
            if minute_window not in self.request_counters[client_ip]:
                self.request_counters[client_ip][minute_window] = 0
            
            self.request_counters[client_ip][minute_window] += 1
            
            # 检查速率限制
            total_requests = sum(self.request_counters[client_ip].values())
            max_requests = self.security_config['max_requests_per_minute']
            
            if total_requests > max_requests:
                return {
                    'valid': False,
                    'errors': [f"Rate limit exceeded: {total_requests}/{max_requests} requests per minute"]
                }
            
            return {'valid': True, 'errors': []}
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {e}")
            return {
                'valid': False,
                'errors': [f"Rate limit check error: {str(e)}"]
            }
    
    def _validate_csrf_token(self, csrf_token: str) -> Dict[str, Any]:
        """验证CSRF令牌"""
        try:
            if not csrf_token:
                return {
                    'valid': False,
                    'errors': ["CSRF token is required"]
                }
            
            # 这里应该实现实际的CSRF令牌验证逻辑
            # 例如：检查令牌是否在有效期内，是否与会话匹配等
            
            # 简单示例：检查令牌格式
            if len(csrf_token) < 32:
                return {
                    'valid': False,
                    'errors': ["Invalid CSRF token format"]
                }
            
            return {'valid': True, 'errors': []}
            
        except Exception as e:
            self.logger.error(f"CSRF token validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"CSRF token validation error: {str(e)}"]
            }
    
    def _validate_session(self, session_id: str) -> Dict[str, Any]:
        """验证会话"""
        try:
            if not session_id:
                return {
                    'valid': False,
                    'errors': ["Session ID is required"]
                }
            
            # 这里应该实现实际的会话验证逻辑
            # 例如：检查会话是否存在，是否过期等
            
            # 简单示例：检查会话ID格式
            if len(session_id) < 32:
                return {
                    'valid': False,
                    'errors': ["Invalid session ID format"]
                }
            
            return {'valid': True, 'errors': []}
            
        except Exception as e:
            self.logger.error(f"Session validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Session validation error: {str(e)}"]
            }
    
    def cleanup(self):
        """清理资源"""
        try:
            self.request_counters.clear()
            self.logger.info("Security validator cleanup completed")
        except Exception as e:
            self.logger.error(f"Security validator cleanup failed: {e}")
