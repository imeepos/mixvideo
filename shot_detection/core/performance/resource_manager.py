"""
Resource Manager
资源管理器
"""

import threading
import time
from typing import Dict, List, Any, Optional, Callable
from loguru import logger

from .memory_manager import MemoryManager
from .performance_monitor import PerformanceMonitor
from .cache_optimizer import CacheOptimizer


class ResourceManager:
    """资源管理器 - 统一管理系统资源"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化资源管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="ResourceManager")
        
        # 初始化子管理器
        self.memory_manager = MemoryManager(config)
        self.performance_monitor = PerformanceMonitor(config)
        self.cache_optimizer = CacheOptimizer(config)
        
        # 资源管理配置
        self.resource_config = self.config.get('resource_management', {
            'auto_optimization': True,
            'optimization_interval_minutes': 10,
            'resource_threshold': 80.0,
            'emergency_threshold': 95.0,
            'enable_alerts': True
        })
        
        # 管理状态
        self.managing = False
        self.management_thread = None
        
        # 资源统计
        self.resource_stats = {
            'optimization_count': 0,
            'alert_count': 0,
            'emergency_count': 0,
            'last_optimization': 0,
            'total_freed_mb': 0.0
        }
        
        # 回调函数
        self.optimization_callbacks = []
        self.alert_callbacks = []
        
        self.logger.info("Resource manager initialized")
    
    def start_management(self):
        """开始资源管理"""
        if self.managing:
            self.logger.warning("Resource management already started")
            return
        
        # 启动子管理器
        self.memory_manager.start_monitoring()
        self.performance_monitor.start_monitoring()
        
        # 启动资源管理
        if self.resource_config['auto_optimization']:
            self.managing = True
            self.management_thread = threading.Thread(target=self._management_loop, daemon=True)
            self.management_thread.start()
        
        self.logger.info("Resource management started")
    
    def stop_management(self):
        """停止资源管理"""
        if not self.managing:
            return
        
        self.managing = False
        if self.management_thread:
            self.management_thread.join(timeout=2.0)
        
        # 停止子管理器
        self.memory_manager.stop_monitoring()
        self.performance_monitor.stop_monitoring()
        self.cache_optimizer.stop_auto_cleanup()
        
        self.logger.info("Resource management stopped")
    
    def _management_loop(self):
        """资源管理循环"""
        interval_seconds = self.resource_config['optimization_interval_minutes'] * 60
        
        while self.managing:
            try:
                self._check_and_optimize_resources()
                time.sleep(interval_seconds)
            except Exception as e:
                self.logger.error(f"Resource management error: {e}")
                time.sleep(60)
    
    def _check_and_optimize_resources(self):
        """检查并优化资源"""
        try:
            # 获取当前资源状态
            resource_status = self.get_resource_status()
            
            # 检查是否需要优化
            needs_optimization = self._needs_optimization(resource_status)
            
            if needs_optimization:
                optimization_result = self.optimize_resources()
                
                if optimization_result["success"]:
                    self.resource_stats['optimization_count'] += 1
                    self.resource_stats['last_optimization'] = time.time()
                    
                    # 触发优化回调
                    for callback in self.optimization_callbacks:
                        try:
                            callback(optimization_result)
                        except Exception as e:
                            self.logger.error(f"Optimization callback error: {e}")
            
            # 检查警报条件
            self._check_resource_alerts(resource_status)
            
        except Exception as e:
            self.logger.error(f"Resource check and optimization failed: {e}")
    
    def _needs_optimization(self, resource_status: Dict[str, Any]) -> bool:
        """检查是否需要优化"""
        threshold = self.resource_config['resource_threshold']
        
        # 检查内存使用率
        memory_percent = resource_status.get('memory', {}).get('percent', 0)
        if memory_percent > threshold:
            return True
        
        # 检查CPU使用率
        cpu_percent = resource_status.get('cpu', {}).get('percent', 0)
        if cpu_percent > threshold:
            return True
        
        # 检查缓存大小
        cache_size_mb = resource_status.get('cache', {}).get('total_size_mb', 0)
        max_cache_mb = self.cache_optimizer.cache_config['max_cache_size_mb']
        if cache_size_mb > max_cache_mb * 0.8:  # 80%阈值
            return True
        
        return False
    
    def _check_resource_alerts(self, resource_status: Dict[str, Any]):
        """检查资源警报"""
        if not self.resource_config['enable_alerts']:
            return
        
        emergency_threshold = self.resource_config['emergency_threshold']
        alerts = []
        
        # 检查内存
        memory_percent = resource_status.get('memory', {}).get('percent', 0)
        if memory_percent > emergency_threshold:
            alerts.append({
                'type': 'memory_emergency',
                'value': memory_percent,
                'threshold': emergency_threshold,
                'message': f"Emergency memory usage: {memory_percent:.1f}%"
            })
        
        # 检查CPU
        cpu_percent = resource_status.get('cpu', {}).get('percent', 0)
        if cpu_percent > emergency_threshold:
            alerts.append({
                'type': 'cpu_emergency',
                'value': cpu_percent,
                'threshold': emergency_threshold,
                'message': f"Emergency CPU usage: {cpu_percent:.1f}%"
            })
        
        if alerts:
            self.resource_stats['alert_count'] += len(alerts)
            self.resource_stats['emergency_count'] += 1
            
            # 触发警报回调
            for alert in alerts:
                self.logger.error(alert['message'])
                
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        self.logger.error(f"Alert callback error: {e}")
    
    def get_resource_status(self) -> Dict[str, Any]:
        """获取资源状态"""
        try:
            # 获取性能数据
            performance_data = self.performance_monitor.get_current_performance()
            
            # 获取内存信息
            memory_info = self.memory_manager.get_memory_info()
            
            # 获取缓存统计
            cache_stats = self.cache_optimizer.get_cache_statistics()
            
            return {
                "timestamp": time.time(),
                "cpu": performance_data.get("cpu", {}),
                "memory": performance_data.get("memory", {}),
                "disk": performance_data.get("disk", {}),
                "network": performance_data.get("network", {}),
                "memory_manager": memory_info,
                "cache": cache_stats,
                "management_stats": self.resource_stats.copy()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get resource status: {e}")
            return {}
    
    def optimize_resources(self, optimization_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """优化资源"""
        try:
            config = optimization_config or {}
            optimizations = []
            total_freed_mb = 0.0
            
            # 1. 内存优化
            if config.get('optimize_memory', True):
                memory_result = self.memory_manager.optimize_memory_usage()
                if memory_result["success"]:
                    optimizations.append({
                        "type": "memory",
                        "result": memory_result
                    })
                    total_freed_mb += memory_result.get("freed_mb", 0)
            
            # 2. 缓存优化
            if config.get('optimize_cache', True):
                cache_dir = config.get('cache_dir', './cache')
                cache_result = self.cache_optimizer.optimize_cache(cache_dir)
                if cache_result["success"]:
                    optimizations.append({
                        "type": "cache",
                        "result": cache_result
                    })
                    total_freed_mb += cache_result.get("total_freed_mb", 0)
            
            # 3. 性能优化建议
            if config.get('get_performance_suggestions', True):
                perf_suggestions = self.performance_monitor.optimize_performance()
                optimizations.append({
                    "type": "performance_suggestions",
                    "result": perf_suggestions
                })
            
            # 更新统计
            self.resource_stats['total_freed_mb'] += total_freed_mb
            
            self.logger.info(f"Resource optimization completed: freed {total_freed_mb:.1f}MB")
            
            return {
                "success": True,
                "optimizations": optimizations,
                "total_freed_mb": total_freed_mb,
                "optimization_count": len(optimizations)
            }
            
        except Exception as e:
            self.logger.error(f"Resource optimization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_resource_recommendations(self) -> List[str]:
        """获取资源优化建议"""
        recommendations = []
        
        try:
            # 获取当前状态
            status = self.get_resource_status()
            
            # 内存建议
            memory_percent = status.get('memory', {}).get('percent', 0)
            if memory_percent > 80:
                recommendations.append("内存使用率过高，建议启用自动内存管理")
            
            # CPU建议
            cpu_percent = status.get('cpu', {}).get('percent', 0)
            if cpu_percent > 80:
                recommendations.append("CPU使用率过高，建议减少并行处理任务")
            
            # 缓存建议
            cache_size = status.get('cache', {}).get('total_size_mb', 0)
            max_cache = self.cache_optimizer.cache_config['max_cache_size_mb']
            if cache_size > max_cache * 0.8:
                recommendations.append("缓存使用量接近限制，建议启用自动缓存清理")
            
            # 管理建议
            if not self.managing:
                recommendations.append("建议启用自动资源管理以获得更好的性能")
            
            # 从子管理器获取建议
            memory_recommendations = self.memory_manager.get_memory_recommendations()
            recommendations.extend(memory_recommendations)
            
        except Exception as e:
            self.logger.error(f"Failed to get recommendations: {e}")
            recommendations.append("无法获取资源建议，请检查系统状态")
        
        return recommendations
    
    def create_resource_report(self) -> Dict[str, Any]:
        """创建资源报告"""
        try:
            status = self.get_resource_status()
            recommendations = self.get_resource_recommendations()
            
            # 性能摘要
            performance_summary = self.performance_monitor.get_performance_summary()
            
            # 内存报告
            memory_report = self.memory_manager.create_memory_report()
            
            report = {
                "timestamp": time.time(),
                "resource_status": status,
                "performance_summary": performance_summary,
                "memory_report": memory_report,
                "recommendations": recommendations,
                "management_statistics": self.resource_stats.copy(),
                "configuration": {
                    "resource_config": self.resource_config.copy(),
                    "auto_management": self.managing
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to create resource report: {e}")
            return {
                "error": str(e),
                "timestamp": time.time()
            }
    
    def register_optimization_callback(self, callback: Callable):
        """注册优化回调函数"""
        self.optimization_callbacks.append(callback)
        self.logger.info("Optimization callback registered")
    
    def register_alert_callback(self, callback: Callable):
        """注册警报回调函数"""
        self.alert_callbacks.append(callback)
        self.logger.info("Alert callback registered")
    
    def emergency_cleanup(self) -> Dict[str, Any]:
        """紧急清理"""
        try:
            self.logger.warning("Performing emergency resource cleanup")
            
            # 强制内存优化
            memory_result = self.memory_manager.optimize_memory_usage()
            
            # 强制缓存清理
            cache_result = self.cache_optimizer.optimize_cache('./cache', {
                'max_size_mb': self.cache_optimizer.cache_config['max_cache_size_mb'] * 0.5,
                'max_age_hours': 1.0  # 只保留1小时内的缓存
            })
            
            total_freed = (memory_result.get("freed_mb", 0) + 
                          cache_result.get("total_freed_mb", 0))
            
            self.logger.info(f"Emergency cleanup completed: freed {total_freed:.1f}MB")
            
            return {
                "success": True,
                "memory_cleanup": memory_result,
                "cache_cleanup": cache_result,
                "total_freed_mb": total_freed
            }
            
        except Exception as e:
            self.logger.error(f"Emergency cleanup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup(self):
        """清理资源"""
        self.stop_management()
        
        # 清理子管理器
        self.memory_manager.cleanup()
        self.performance_monitor.cleanup()
        self.cache_optimizer.cleanup()
        
        # 清理回调
        self.optimization_callbacks.clear()
        self.alert_callbacks.clear()
        
        self.logger.info("Resource manager cleanup completed")
