"""
Memory Manager
内存管理器
"""

import gc
import psutil
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from loguru import logger


class MemoryManager:
    """内存管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化内存管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="MemoryManager")
        
        # 内存配置
        self.memory_config = self.config.get('memory', {
            'max_memory_usage_percent': 80.0,  # 最大内存使用百分比
            'gc_threshold': 70.0,  # 垃圾回收阈值
            'monitor_interval': 5.0,  # 监控间隔(秒)
            'auto_cleanup': True,  # 自动清理
            'warning_threshold': 85.0,  # 警告阈值
            'emergency_threshold': 95.0  # 紧急阈值
        })
        
        # 监控状态
        self.monitoring = False
        self.monitor_thread = None
        self.memory_stats = {
            'peak_usage': 0.0,
            'current_usage': 0.0,
            'gc_count': 0,
            'cleanup_count': 0,
            'warnings': 0
        }
        
        # 回调函数
        self.callbacks = {
            'warning': [],
            'emergency': [],
            'cleanup': []
        }
        
        self.logger.info("Memory manager initialized")
    
    def start_monitoring(self):
        """开始内存监控"""
        if self.monitoring:
            self.logger.warning("Memory monitoring already started")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """停止内存监控"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        self.logger.info("Memory monitoring stopped")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                self._check_memory_usage()
                time.sleep(self.memory_config['monitor_interval'])
            except Exception as e:
                self.logger.error(f"Memory monitoring error: {e}")
                time.sleep(1.0)
    
    def _check_memory_usage(self):
        """检查内存使用情况"""
        try:
            # 获取内存信息
            memory_info = psutil.virtual_memory()
            usage_percent = memory_info.percent
            
            # 更新统计
            self.memory_stats['current_usage'] = usage_percent
            if usage_percent > self.memory_stats['peak_usage']:
                self.memory_stats['peak_usage'] = usage_percent
            
            # 检查阈值
            if usage_percent >= self.memory_config['emergency_threshold']:
                self._handle_emergency_memory()
            elif usage_percent >= self.memory_config['warning_threshold']:
                self._handle_warning_memory()
            elif usage_percent >= self.memory_config['gc_threshold']:
                if self.memory_config['auto_cleanup']:
                    self._perform_garbage_collection()
            
        except Exception as e:
            self.logger.error(f"Failed to check memory usage: {e}")
    
    def _handle_warning_memory(self):
        """处理内存警告"""
        self.memory_stats['warnings'] += 1
        self.logger.warning(f"High memory usage: {self.memory_stats['current_usage']:.1f}%")
        
        # 触发警告回调
        for callback in self.callbacks['warning']:
            try:
                callback(self.memory_stats['current_usage'])
            except Exception as e:
                self.logger.error(f"Warning callback error: {e}")
    
    def _handle_emergency_memory(self):
        """处理紧急内存情况"""
        self.logger.error(f"Emergency memory usage: {self.memory_stats['current_usage']:.1f}%")
        
        # 强制垃圾回收
        self._perform_garbage_collection()
        
        # 触发紧急回调
        for callback in self.callbacks['emergency']:
            try:
                callback(self.memory_stats['current_usage'])
            except Exception as e:
                self.logger.error(f"Emergency callback error: {e}")
    
    def _perform_garbage_collection(self):
        """执行垃圾回收"""
        try:
            before_usage = psutil.virtual_memory().percent
            
            # 执行垃圾回收
            collected = gc.collect()
            
            after_usage = psutil.virtual_memory().percent
            freed_percent = before_usage - after_usage
            
            self.memory_stats['gc_count'] += 1
            
            self.logger.info(f"Garbage collection: collected {collected} objects, "
                           f"freed {freed_percent:.1f}% memory")
            
            # 触发清理回调
            for callback in self.callbacks['cleanup']:
                try:
                    callback(collected, freed_percent)
                except Exception as e:
                    self.logger.error(f"Cleanup callback error: {e}")
                    
        except Exception as e:
            self.logger.error(f"Garbage collection failed: {e}")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        try:
            memory_info = psutil.virtual_memory()
            swap_info = psutil.swap_memory()
            
            return {
                "virtual_memory": {
                    "total": memory_info.total,
                    "available": memory_info.available,
                    "used": memory_info.used,
                    "percent": memory_info.percent
                },
                "swap_memory": {
                    "total": swap_info.total,
                    "used": swap_info.used,
                    "percent": swap_info.percent
                },
                "statistics": self.memory_stats.copy(),
                "thresholds": {
                    "gc_threshold": self.memory_config['gc_threshold'],
                    "warning_threshold": self.memory_config['warning_threshold'],
                    "emergency_threshold": self.memory_config['emergency_threshold']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get memory info: {e}")
            return {}
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """优化内存使用"""
        try:
            before_info = psutil.virtual_memory()
            optimizations = []
            
            # 1. 强制垃圾回收
            collected = gc.collect()
            optimizations.append(f"Garbage collection: {collected} objects")
            
            # 2. 清理缓存（如果有的话）
            # 这里可以添加具体的缓存清理逻辑
            
            # 3. 优化垃圾回收阈值
            gc.set_threshold(700, 10, 10)  # 更激进的垃圾回收
            optimizations.append("Adjusted GC thresholds")
            
            after_info = psutil.virtual_memory()
            freed_mb = (before_info.used - after_info.used) / (1024 * 1024)
            
            self.memory_stats['cleanup_count'] += 1
            
            self.logger.info(f"Memory optimization completed: freed {freed_mb:.1f}MB")
            
            return {
                "success": True,
                "freed_mb": freed_mb,
                "before_usage": before_info.percent,
                "after_usage": after_info.percent,
                "optimizations": optimizations
            }
            
        except Exception as e:
            self.logger.error(f"Memory optimization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def set_memory_limit(self, limit_mb: int):
        """设置内存限制"""
        try:
            import resource
            
            # 设置内存限制（仅在Unix系统上有效）
            limit_bytes = limit_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))
            
            self.logger.info(f"Memory limit set to {limit_mb}MB")
            
        except Exception as e:
            self.logger.warning(f"Failed to set memory limit: {e}")
    
    def register_callback(self, event_type: str, callback: Callable):
        """注册回调函数"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
            self.logger.info(f"Registered {event_type} callback")
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    def unregister_callback(self, event_type: str, callback: Callable):
        """取消注册回调函数"""
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            self.logger.info(f"Unregistered {event_type} callback")
    
    def get_memory_recommendations(self) -> List[str]:
        """获取内存优化建议"""
        recommendations = []
        current_usage = self.memory_stats['current_usage']
        
        if current_usage > 80:
            recommendations.append("考虑增加系统内存或关闭其他应用程序")
        
        if self.memory_stats['gc_count'] > 100:
            recommendations.append("频繁的垃圾回收可能影响性能，考虑优化代码")
        
        if self.memory_stats['warnings'] > 10:
            recommendations.append("内存使用经常超过警告阈值，建议调整处理策略")
        
        if not self.monitoring:
            recommendations.append("启用内存监控以获得更好的内存管理")
        
        return recommendations
    
    def create_memory_report(self) -> Dict[str, Any]:
        """创建内存报告"""
        memory_info = self.get_memory_info()
        recommendations = self.get_memory_recommendations()
        
        report = {
            "timestamp": time.time(),
            "memory_info": memory_info,
            "statistics": self.memory_stats.copy(),
            "recommendations": recommendations,
            "monitoring_status": self.monitoring,
            "configuration": self.memory_config.copy()
        }
        
        return report
    
    def cleanup(self):
        """清理资源"""
        self.stop_monitoring()
        
        # 最后一次垃圾回收
        gc.collect()
        
        self.logger.info("Memory manager cleanup completed")
