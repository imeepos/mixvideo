"""
Plugin Sandbox System
插件沙箱系统
"""

import os
import sys
import threading
import time
import resource
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from contextlib import contextmanager
from loguru import logger


@dataclass
class SandboxConfig:
    """沙箱配置"""
    max_memory_mb: int = 512
    max_cpu_time: int = 30
    max_execution_time: int = 60
    allowed_modules: List[str] = None
    blocked_modules: List[str] = None
    allow_file_access: bool = False
    allowed_paths: List[str] = None
    allow_network_access: bool = False
    max_threads: int = 5
    enable_resource_limits: bool = True


class PluginSandbox:
    """插件沙箱"""
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        初始化插件沙箱
        
        Args:
            config: 沙箱配置
        """
        self.config = config or SandboxConfig()
        self.logger = logger.bind(component="PluginSandbox")
        
        # 沙箱状态
        self._active_sandboxes = {}
        self._execution_stats = {}
        
        # 默认允许的模块
        if self.config.allowed_modules is None:
            self.config.allowed_modules = [
                'builtins', 'sys', 'os', 'time', 'datetime',
                'json', 'math', 'random', 're', 'collections',
                'itertools', 'functools', 'operator',
                'numpy', 'cv2', 'PIL', 'matplotlib'
            ]
        
        # 默认阻止的模块
        if self.config.blocked_modules is None:
            self.config.blocked_modules = [
                'subprocess', 'multiprocessing', 'threading',
                'socket', 'urllib', 'requests', 'http',
                'ftplib', 'smtplib', 'telnetlib',
                'ctypes', 'importlib', '__import__'
            ]
        
        self.logger.info("Plugin sandbox initialized")
    
    @contextmanager
    def create_sandbox(self, plugin_id: str):
        """
        创建沙箱环境
        
        Args:
            plugin_id: 插件ID
        """
        sandbox_id = f"{plugin_id}_{int(time.time())}"
        
        try:
            self.logger.info(f"Creating sandbox: {sandbox_id}")
            
            # 设置资源限制
            if self.config.enable_resource_limits:
                self._set_resource_limits()
            
            # 设置模块导入限制
            original_import = __builtins__.__import__
            __builtins__.__import__ = self._restricted_import
            
            # 设置文件访问限制
            if not self.config.allow_file_access:
                self._restrict_file_access()
            
            # 记录沙箱
            self._active_sandboxes[sandbox_id] = {
                'plugin_id': plugin_id,
                'start_time': time.time(),
                'thread_id': threading.current_thread().ident
            }
            
            yield sandbox_id
            
        except Exception as e:
            self.logger.error(f"Sandbox execution failed: {e}")
            raise
        
        finally:
            try:
                # 恢复原始导入函数
                __builtins__.__import__ = original_import
                
                # 清理沙箱记录
                if sandbox_id in self._active_sandboxes:
                    sandbox_info = self._active_sandboxes[sandbox_id]
                    execution_time = time.time() - sandbox_info['start_time']
                    
                    self._execution_stats[plugin_id] = {
                        'last_execution_time': execution_time,
                        'total_executions': self._execution_stats.get(plugin_id, {}).get('total_executions', 0) + 1
                    }
                    
                    del self._active_sandboxes[sandbox_id]
                
                self.logger.info(f"Sandbox cleaned up: {sandbox_id}")
                
            except Exception as e:
                self.logger.error(f"Sandbox cleanup failed: {e}")
    
    def _set_resource_limits(self):
        """设置资源限制"""
        try:
            # 设置内存限制
            if self.config.max_memory_mb > 0:
                memory_limit = self.config.max_memory_mb * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
            
            # 设置CPU时间限制
            if self.config.max_cpu_time > 0:
                resource.setrlimit(resource.RLIMIT_CPU, (self.config.max_cpu_time, self.config.max_cpu_time))
            
            self.logger.debug("Resource limits set")
            
        except Exception as e:
            self.logger.error(f"Failed to set resource limits: {e}")
    
    def _restricted_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """受限制的导入函数"""
        try:
            # 检查是否在允许列表中
            if self.config.allowed_modules and name not in self.config.allowed_modules:
                # 检查是否为子模块
                allowed = False
                for allowed_module in self.config.allowed_modules:
                    if name.startswith(f"{allowed_module}."):
                        allowed = True
                        break
                
                if not allowed:
                    raise ImportError(f"Module '{name}' is not allowed in sandbox")
            
            # 检查是否在阻止列表中
            if self.config.blocked_modules and name in self.config.blocked_modules:
                raise ImportError(f"Module '{name}' is blocked in sandbox")
            
            # 执行正常导入
            return __import__(name, globals, locals, fromlist, level)
            
        except Exception as e:
            self.logger.warning(f"Import blocked: {name} - {e}")
            raise
    
    def _restrict_file_access(self):
        """限制文件访问"""
        try:
            # 这里可以实现文件访问限制
            # 例如：重写open函数，检查路径是否在允许列表中
            
            original_open = open
            
            def restricted_open(file, mode='r', **kwargs):
                file_path = Path(file).resolve()
                
                # 检查是否在允许的路径中
                if self.config.allowed_paths:
                    allowed = False
                    for allowed_path in self.config.allowed_paths:
                        allowed_path = Path(allowed_path).resolve()
                        try:
                            file_path.relative_to(allowed_path)
                            allowed = True
                            break
                        except ValueError:
                            continue
                    
                    if not allowed:
                        raise PermissionError(f"File access not allowed: {file}")
                
                return original_open(file, mode, **kwargs)
            
            # 替换内置open函数
            __builtins__['open'] = restricted_open
            
        except Exception as e:
            self.logger.error(f"Failed to restrict file access: {e}")
    
    def execute_in_sandbox(self, plugin_id: str, func: Callable, *args, **kwargs) -> Any:
        """
        在沙箱中执行函数
        
        Args:
            plugin_id: 插件ID
            func: 要执行的函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数返回值
        """
        try:
            with self.create_sandbox(plugin_id) as sandbox_id:
                self.logger.debug(f"Executing function in sandbox: {sandbox_id}")
                
                # 设置执行超时
                if self.config.max_execution_time > 0:
                    result = self._execute_with_timeout(func, self.config.max_execution_time, *args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                return result
                
        except Exception as e:
            self.logger.error(f"Sandbox execution failed for plugin {plugin_id}: {e}")
            raise
    
    def _execute_with_timeout(self, func: Callable, timeout: int, *args, **kwargs) -> Any:
        """带超时的执行"""
        import signal
        
        class TimeoutError(Exception):
            pass
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Execution timeout")
        
        # 设置超时信号
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = func(*args, **kwargs)
            signal.alarm(0)  # 取消超时
            return result
        
        except TimeoutError:
            self.logger.error(f"Function execution timeout: {timeout}s")
            raise
        
        finally:
            signal.signal(signal.SIGALRM, old_handler)
    
    def get_sandbox_stats(self) -> Dict[str, Any]:
        """获取沙箱统计信息"""
        try:
            stats = {
                'active_sandboxes': len(self._active_sandboxes),
                'total_plugins_executed': len(self._execution_stats),
                'execution_stats': self._execution_stats.copy(),
                'config': {
                    'max_memory_mb': self.config.max_memory_mb,
                    'max_cpu_time': self.config.max_cpu_time,
                    'max_execution_time': self.config.max_execution_time,
                    'allow_file_access': self.config.allow_file_access,
                    'allow_network_access': self.config.allow_network_access
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get sandbox stats: {e}")
            return {}
    
    def is_plugin_safe(self, plugin_code: str) -> Dict[str, Any]:
        """
        检查插件代码安全性
        
        Args:
            plugin_code: 插件代码
            
        Returns:
            安全检查结果
        """
        try:
            safety_report = {
                'is_safe': True,
                'warnings': [],
                'errors': [],
                'risk_level': 'low'
            }
            
            # 检查危险函数调用
            dangerous_patterns = [
                'exec(', 'eval(', 'compile(',
                'subprocess.', 'os.system(', 'os.popen(',
                'import subprocess', 'import os',
                '__import__(', 'importlib.',
                'open(', 'file(', 'input(',
                'socket.', 'urllib.', 'requests.',
                'ctypes.', 'multiprocessing.'
            ]
            
            for pattern in dangerous_patterns:
                if pattern in plugin_code:
                    safety_report['warnings'].append(f"Potentially dangerous pattern found: {pattern}")
                    safety_report['risk_level'] = 'medium'
            
            # 检查网络相关代码
            network_patterns = ['http', 'ftp', 'smtp', 'telnet', 'socket']
            for pattern in network_patterns:
                if pattern in plugin_code.lower():
                    safety_report['warnings'].append(f"Network-related code detected: {pattern}")
            
            # 检查文件操作
            file_patterns = ['open(', 'file(', 'with open', 'read(', 'write(']
            for pattern in file_patterns:
                if pattern in plugin_code:
                    safety_report['warnings'].append(f"File operation detected: {pattern}")
            
            # 根据警告数量调整风险级别
            if len(safety_report['warnings']) > 5:
                safety_report['risk_level'] = 'high'
                safety_report['is_safe'] = False
            elif len(safety_report['warnings']) > 2:
                safety_report['risk_level'] = 'medium'
            
            return safety_report
            
        except Exception as e:
            self.logger.error(f"Failed to check plugin safety: {e}")
            return {
                'is_safe': False,
                'errors': [str(e)],
                'risk_level': 'unknown'
            }
    
    def kill_sandbox(self, sandbox_id: str) -> bool:
        """
        强制终止沙箱
        
        Args:
            sandbox_id: 沙箱ID
            
        Returns:
            是否成功终止
        """
        try:
            if sandbox_id in self._active_sandboxes:
                sandbox_info = self._active_sandboxes[sandbox_id]
                
                # 这里可以实现强制终止逻辑
                # 例如：终止相关线程、清理资源等
                
                del self._active_sandboxes[sandbox_id]
                
                self.logger.info(f"Sandbox killed: {sandbox_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to kill sandbox: {e}")
            return False
    
    def cleanup_all_sandboxes(self):
        """清理所有沙箱"""
        try:
            sandbox_ids = list(self._active_sandboxes.keys())
            
            for sandbox_id in sandbox_ids:
                self.kill_sandbox(sandbox_id)
            
            self.logger.info("All sandboxes cleaned up")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup all sandboxes: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.cleanup_all_sandboxes()
            self._execution_stats.clear()
            self.logger.info("Plugin sandbox cleanup completed")
        except Exception as e:
            self.logger.error(f"Plugin sandbox cleanup failed: {e}")
