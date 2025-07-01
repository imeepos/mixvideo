"""
Environment Management
环境管理
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger


class EnvironmentManager:
    """环境管理器"""
    
    def __init__(self):
        """初始化环境管理器"""
        self.logger = logger.bind(component="EnvironmentManager")
        
        # 环境信息
        self.env_info = {}
        
        # 环境配置
        self.env_config = EnvironmentConfig()
        
        # 收集环境信息
        self._collect_environment_info()
        
        self.logger.info("Environment manager initialized")
    
    def _collect_environment_info(self):
        """收集环境信息"""
        try:
            self.env_info = {
                'system': self._get_system_info(),
                'python': self._get_python_info(),
                'hardware': self._get_hardware_info(),
                'paths': self._get_path_info(),
                'environment_variables': self._get_env_variables(),
                'dependencies': self._get_dependency_info()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to collect environment info: {e}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            return {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture(),
                'hostname': platform.node(),
                'username': os.getenv('USERNAME') or os.getenv('USER', 'unknown')
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {}
    
    def _get_python_info(self) -> Dict[str, Any]:
        """获取Python信息"""
        try:
            return {
                'version': sys.version,
                'version_info': {
                    'major': sys.version_info.major,
                    'minor': sys.version_info.minor,
                    'micro': sys.version_info.micro,
                    'releaselevel': sys.version_info.releaselevel,
                    'serial': sys.version_info.serial
                },
                'executable': sys.executable,
                'prefix': sys.prefix,
                'path': sys.path[:5],  # 只显示前5个路径
                'platform': sys.platform,
                'maxsize': sys.maxsize,
                'encoding': sys.getdefaultencoding()
            }
        except Exception as e:
            self.logger.error(f"Failed to get Python info: {e}")
            return {}
    
    def _get_hardware_info(self) -> Dict[str, Any]:
        """获取硬件信息"""
        try:
            hardware_info = {
                'cpu_count': os.cpu_count(),
                'architecture': platform.machine()
            }
            
            # 尝试获取更详细的硬件信息
            try:
                import psutil
                
                # CPU信息
                hardware_info.update({
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                    'cpu_count_logical': psutil.cpu_count(logical=True),
                    'cpu_count_physical': psutil.cpu_count(logical=False)
                })
                
                # 内存信息
                memory = psutil.virtual_memory()
                hardware_info.update({
                    'memory_total': memory.total,
                    'memory_available': memory.available,
                    'memory_percent': memory.percent
                })
                
                # 磁盘信息
                disk = psutil.disk_usage('/')
                hardware_info.update({
                    'disk_total': disk.total,
                    'disk_used': disk.used,
                    'disk_free': disk.free,
                    'disk_percent': (disk.used / disk.total) * 100
                })
                
            except ImportError:
                self.logger.warning("psutil not available, limited hardware info")
            
            return hardware_info
            
        except Exception as e:
            self.logger.error(f"Failed to get hardware info: {e}")
            return {}
    
    def _get_path_info(self) -> Dict[str, Any]:
        """获取路径信息"""
        try:
            return {
                'current_working_directory': str(Path.cwd()),
                'home_directory': str(Path.home()),
                'temp_directory': str(Path.cwd() / 'temp'),
                'config_directory': str(Path.cwd() / 'config'),
                'data_directory': str(Path.cwd() / 'data'),
                'logs_directory': str(Path.cwd() / 'logs'),
                'cache_directory': str(Path.cwd() / 'cache')
            }
        except Exception as e:
            self.logger.error(f"Failed to get path info: {e}")
            return {}
    
    def _get_env_variables(self) -> Dict[str, str]:
        """获取环境变量"""
        try:
            # 只获取相关的环境变量
            relevant_vars = [
                'PATH', 'PYTHONPATH', 'HOME', 'USER', 'USERNAME',
                'TEMP', 'TMP', 'APPDATA', 'LOCALAPPDATA',
                'CUDA_VISIBLE_DEVICES', 'OPENCV_LOG_LEVEL'
            ]
            
            env_vars = {}
            for var in relevant_vars:
                value = os.getenv(var)
                if value:
                    env_vars[var] = value
            
            return env_vars
            
        except Exception as e:
            self.logger.error(f"Failed to get environment variables: {e}")
            return {}
    
    def _get_dependency_info(self) -> Dict[str, Any]:
        """获取依赖信息"""
        try:
            dependencies = {}
            
            # 检查关键依赖
            key_packages = [
                'numpy', 'opencv-python', 'pillow', 'matplotlib',
                'loguru', 'pyyaml', 'toml', 'psutil'
            ]
            
            for package in key_packages:
                try:
                    module = __import__(package.replace('-', '_'))
                    version = getattr(module, '__version__', 'unknown')
                    dependencies[package] = {
                        'installed': True,
                        'version': version,
                        'location': getattr(module, '__file__', 'unknown')
                    }
                except ImportError:
                    dependencies[package] = {
                        'installed': False,
                        'version': None,
                        'location': None
                    }
            
            return dependencies
            
        except Exception as e:
            self.logger.error(f"Failed to get dependency info: {e}")
            return {}
    
    def get_environment_info(self) -> Dict[str, Any]:
        """获取完整环境信息"""
        return self.env_info.copy()
    
    def get_system_capabilities(self) -> Dict[str, bool]:
        """获取系统能力"""
        try:
            capabilities = {
                'gpu_available': self._check_gpu_availability(),
                'opencv_available': self._check_opencv_availability(),
                'ffmpeg_available': self._check_ffmpeg_availability(),
                'multiprocessing_available': True,  # Python内置
                'threading_available': True,  # Python内置
                'large_memory_available': self._check_large_memory_availability(),
                'fast_storage_available': self._check_fast_storage_availability()
            }
            
            return capabilities
            
        except Exception as e:
            self.logger.error(f"Failed to get system capabilities: {e}")
            return {}
    
    def _check_gpu_availability(self) -> bool:
        """检查GPU可用性"""
        try:
            # 检查CUDA
            try:
                import torch
                return torch.cuda.is_available()
            except ImportError:
                pass
            
            # 检查OpenCL
            try:
                import pyopencl
                platforms = pyopencl.get_platforms()
                return len(platforms) > 0
            except ImportError:
                pass
            
            return False
            
        except Exception:
            return False
    
    def _check_opencv_availability(self) -> bool:
        """检查OpenCV可用性"""
        try:
            import cv2
            return True
        except ImportError:
            return False
    
    def _check_ffmpeg_availability(self) -> bool:
        """检查FFmpeg可用性"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def _check_large_memory_availability(self) -> bool:
        """检查大内存可用性（>= 8GB）"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.total >= 8 * 1024 * 1024 * 1024  # 8GB
        except ImportError:
            return False
    
    def _check_fast_storage_availability(self) -> bool:
        """检查快速存储可用性（SSD）"""
        try:
            # 简单的启发式检查
            # 实际实现可能需要更复杂的检测逻辑
            import psutil
            
            # 检查磁盘IO统计
            disk_io = psutil.disk_io_counters()
            if disk_io:
                # 如果读写速度较快，可能是SSD
                return True
            
            return False
            
        except ImportError:
            return False
    
    def get_recommended_settings(self) -> Dict[str, Any]:
        """获取推荐设置"""
        try:
            capabilities = self.get_system_capabilities()
            hardware_info = self.env_info.get('hardware', {})
            
            recommendations = {
                'processing': {
                    'max_workers': min(os.cpu_count() or 4, 8),
                    'use_gpu': capabilities.get('gpu_available', False),
                    'memory_limit_mb': self._get_recommended_memory_limit(hardware_info),
                    'chunk_size': self._get_recommended_chunk_size(hardware_info)
                },
                'performance': {
                    'enable_caching': capabilities.get('fast_storage_available', True),
                    'cache_size_mb': self._get_recommended_cache_size(hardware_info),
                    'enable_parallel_processing': capabilities.get('multiprocessing_available', True)
                },
                'quality': {
                    'use_high_quality_algorithms': hardware_info.get('memory_total', 0) > 4 * 1024**3,
                    'enable_preview': True,
                    'save_intermediate_results': capabilities.get('fast_storage_available', False)
                }
            }
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get recommended settings: {e}")
            return {}
    
    def _get_recommended_memory_limit(self, hardware_info: Dict[str, Any]) -> int:
        """获取推荐内存限制"""
        try:
            total_memory = hardware_info.get('memory_total', 4 * 1024**3)
            
            # 使用总内存的50%作为限制
            recommended_mb = int((total_memory * 0.5) / (1024**2))
            
            # 最小256MB，最大4GB
            return max(256, min(recommended_mb, 4096))
            
        except Exception:
            return 1024  # 默认1GB
    
    def _get_recommended_chunk_size(self, hardware_info: Dict[str, Any]) -> int:
        """获取推荐块大小"""
        try:
            memory_total = hardware_info.get('memory_total', 4 * 1024**3)
            
            if memory_total >= 16 * 1024**3:  # >= 16GB
                return 2000
            elif memory_total >= 8 * 1024**3:  # >= 8GB
                return 1500
            elif memory_total >= 4 * 1024**3:  # >= 4GB
                return 1000
            else:
                return 500
                
        except Exception:
            return 1000  # 默认
    
    def _get_recommended_cache_size(self, hardware_info: Dict[str, Any]) -> int:
        """获取推荐缓存大小"""
        try:
            memory_total = hardware_info.get('memory_total', 4 * 1024**3)
            
            # 使用总内存的10%作为缓存
            recommended_mb = int((memory_total * 0.1) / (1024**2))
            
            # 最小64MB，最大1GB
            return max(64, min(recommended_mb, 1024))
            
        except Exception:
            return 256  # 默认256MB
    
    def validate_environment(self) -> Dict[str, Any]:
        """验证环境"""
        try:
            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'recommendations': []
            }
            
            # 检查Python版本
            if sys.version_info < (3, 8):
                validation_results['errors'].append("Python 3.8 or higher is required")
                validation_results['valid'] = False
            
            # 检查关键依赖
            dependencies = self.env_info.get('dependencies', {})
            
            required_packages = ['numpy', 'opencv-python']
            for package in required_packages:
                if not dependencies.get(package, {}).get('installed', False):
                    validation_results['errors'].append(f"Required package not installed: {package}")
                    validation_results['valid'] = False
            
            # 检查内存
            hardware_info = self.env_info.get('hardware', {})
            memory_total = hardware_info.get('memory_total', 0)
            
            if memory_total < 2 * 1024**3:  # < 2GB
                validation_results['warnings'].append("Low memory detected, performance may be affected")
            
            # 检查磁盘空间
            disk_free = hardware_info.get('disk_free', 0)
            if disk_free < 1 * 1024**3:  # < 1GB
                validation_results['warnings'].append("Low disk space detected")
            
            # 性能建议
            capabilities = self.get_system_capabilities()
            
            if not capabilities.get('gpu_available', False):
                validation_results['recommendations'].append("Consider installing GPU support for better performance")
            
            if not capabilities.get('ffmpeg_available', False):
                validation_results['recommendations'].append("Install FFmpeg for enhanced video processing capabilities")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Environment validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'recommendations': []
            }
    
    def cleanup(self):
        """清理资源"""
        try:
            self.env_info.clear()
            self.logger.info("Environment manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Environment manager cleanup failed: {e}")


class EnvironmentConfig:
    """环境配置"""
    
    def __init__(self):
        """初始化环境配置"""
        self.logger = logger.bind(component="EnvironmentConfig")
        
        # 环境变量配置
        self.env_vars = {
            'SHOT_DETECTION_DEBUG': 'false',
            'SHOT_DETECTION_LOG_LEVEL': 'INFO',
            'SHOT_DETECTION_CACHE_DIR': './cache',
            'SHOT_DETECTION_TEMP_DIR': './temp',
            'SHOT_DETECTION_MAX_WORKERS': str(os.cpu_count() or 4),
            'SHOT_DETECTION_MEMORY_LIMIT_MB': '1024',
            'SHOT_DETECTION_ENABLE_GPU': 'auto',
            'SHOT_DETECTION_OPENCV_LOG_LEVEL': 'ERROR'
        }
        
        # 应用环境变量
        self._apply_environment_variables()
    
    def _apply_environment_variables(self):
        """应用环境变量"""
        try:
            for key, default_value in self.env_vars.items():
                if key not in os.environ:
                    os.environ[key] = default_value
            
            # 设置OpenCV日志级别
            opencv_log_level = os.getenv('SHOT_DETECTION_OPENCV_LOG_LEVEL', 'ERROR')
            if opencv_log_level == 'ERROR':
                os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
            
            self.logger.info("Environment variables applied")
            
        except Exception as e:
            self.logger.error(f"Failed to apply environment variables: {e}")
    
    def get_env_var(self, key: str, default: str = "") -> str:
        """获取环境变量"""
        return os.getenv(key, default)
    
    def set_env_var(self, key: str, value: str):
        """设置环境变量"""
        os.environ[key] = value
    
    def is_debug_mode(self) -> bool:
        """检查是否为调试模式"""
        return self.get_env_var('SHOT_DETECTION_DEBUG', 'false').lower() == 'true'
    
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.get_env_var('SHOT_DETECTION_LOG_LEVEL', 'INFO')
    
    def get_cache_dir(self) -> str:
        """获取缓存目录"""
        return self.get_env_var('SHOT_DETECTION_CACHE_DIR', './cache')
    
    def get_temp_dir(self) -> str:
        """获取临时目录"""
        return self.get_env_var('SHOT_DETECTION_TEMP_DIR', './temp')
    
    def get_max_workers(self) -> int:
        """获取最大工作线程数"""
        try:
            return int(self.get_env_var('SHOT_DETECTION_MAX_WORKERS', str(os.cpu_count() or 4)))
        except ValueError:
            return os.cpu_count() or 4
    
    def get_memory_limit_mb(self) -> int:
        """获取内存限制（MB）"""
        try:
            return int(self.get_env_var('SHOT_DETECTION_MEMORY_LIMIT_MB', '1024'))
        except ValueError:
            return 1024
    
    def is_gpu_enabled(self) -> bool:
        """检查是否启用GPU"""
        gpu_setting = self.get_env_var('SHOT_DETECTION_ENABLE_GPU', 'auto').lower()
        
        if gpu_setting == 'true':
            return True
        elif gpu_setting == 'false':
            return False
        else:  # auto
            # 自动检测GPU可用性
            try:
                import torch
                return torch.cuda.is_available()
            except ImportError:
                return False
