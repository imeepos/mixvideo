"""
Performance Monitor
性能监控器
"""

import time
import threading
import psutil
from collections import deque
from typing import Dict, List, Any, Optional, Callable
from loguru import logger


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化性能监控器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="PerformanceMonitor")
        
        # 监控配置
        self.monitor_config = self.config.get('performance', {
            'monitor_interval': 1.0,  # 监控间隔(秒)
            'history_size': 300,  # 历史数据大小(5分钟)
            'cpu_threshold': 80.0,  # CPU使用率阈值
            'memory_threshold': 80.0,  # 内存使用率阈值
            'disk_threshold': 90.0,  # 磁盘使用率阈值
            'enable_detailed_monitoring': True  # 启用详细监控
        })
        
        # 监控状态
        self.monitoring = False
        self.monitor_thread = None
        
        # 性能数据历史
        self.history_size = self.monitor_config['history_size']
        self.cpu_history = deque(maxlen=self.history_size)
        self.memory_history = deque(maxlen=self.history_size)
        self.disk_history = deque(maxlen=self.history_size)
        self.network_history = deque(maxlen=self.history_size)
        
        # 性能统计
        self.performance_stats = {
            'start_time': time.time(),
            'total_samples': 0,
            'cpu_peaks': [],
            'memory_peaks': [],
            'alerts_triggered': 0,
            'average_cpu': 0.0,
            'average_memory': 0.0
        }
        
        # 回调函数
        self.alert_callbacks = []
        
        self.logger.info("Performance monitor initialized")
    
    def start_monitoring(self):
        """开始性能监控"""
        if self.monitoring:
            self.logger.warning("Performance monitoring already started")
            return
        
        self.monitoring = True
        self.performance_stats['start_time'] = time.time()
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """停止性能监控"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        
        self.logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                self._collect_performance_data()
                time.sleep(self.monitor_config['monitor_interval'])
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                time.sleep(1.0)
    
    def _collect_performance_data(self):
        """收集性能数据"""
        try:
            timestamp = time.time()
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_history.append((timestamp, cpu_percent))
            
            # 内存使用率
            memory_info = psutil.virtual_memory()
            self.memory_history.append((timestamp, memory_info.percent))
            
            # 磁盘使用率
            disk_info = psutil.disk_usage('/')
            disk_percent = (disk_info.used / disk_info.total) * 100
            self.disk_history.append((timestamp, disk_percent))
            
            # 网络I/O（如果启用详细监控）
            if self.monitor_config['enable_detailed_monitoring']:
                network_info = psutil.net_io_counters()
                self.network_history.append((timestamp, {
                    'bytes_sent': network_info.bytes_sent,
                    'bytes_recv': network_info.bytes_recv
                }))
            
            # 更新统计
            self.performance_stats['total_samples'] += 1
            self._update_statistics(cpu_percent, memory_info.percent)
            
            # 检查阈值
            self._check_thresholds(cpu_percent, memory_info.percent, disk_percent)
            
        except Exception as e:
            self.logger.error(f"Failed to collect performance data: {e}")
    
    def _update_statistics(self, cpu_percent: float, memory_percent: float):
        """更新性能统计"""
        # 计算平均值
        total_samples = self.performance_stats['total_samples']
        
        self.performance_stats['average_cpu'] = (
            (self.performance_stats['average_cpu'] * (total_samples - 1) + cpu_percent) / total_samples
        )
        
        self.performance_stats['average_memory'] = (
            (self.performance_stats['average_memory'] * (total_samples - 1) + memory_percent) / total_samples
        )
        
        # 记录峰值
        if cpu_percent > 90:
            self.performance_stats['cpu_peaks'].append((time.time(), cpu_percent))
            # 只保留最近的峰值
            if len(self.performance_stats['cpu_peaks']) > 50:
                self.performance_stats['cpu_peaks'] = self.performance_stats['cpu_peaks'][-50:]
        
        if memory_percent > 90:
            self.performance_stats['memory_peaks'].append((time.time(), memory_percent))
            if len(self.performance_stats['memory_peaks']) > 50:
                self.performance_stats['memory_peaks'] = self.performance_stats['memory_peaks'][-50:]
    
    def _check_thresholds(self, cpu_percent: float, memory_percent: float, disk_percent: float):
        """检查性能阈值"""
        alerts = []
        
        if cpu_percent > self.monitor_config['cpu_threshold']:
            alerts.append({
                'type': 'cpu',
                'value': cpu_percent,
                'threshold': self.monitor_config['cpu_threshold'],
                'message': f"High CPU usage: {cpu_percent:.1f}%"
            })
        
        if memory_percent > self.monitor_config['memory_threshold']:
            alerts.append({
                'type': 'memory',
                'value': memory_percent,
                'threshold': self.monitor_config['memory_threshold'],
                'message': f"High memory usage: {memory_percent:.1f}%"
            })
        
        if disk_percent > self.monitor_config['disk_threshold']:
            alerts.append({
                'type': 'disk',
                'value': disk_percent,
                'threshold': self.monitor_config['disk_threshold'],
                'message': f"High disk usage: {disk_percent:.1f}%"
            })
        
        if alerts:
            self.performance_stats['alerts_triggered'] += len(alerts)
            self._trigger_alerts(alerts)
    
    def _trigger_alerts(self, alerts: List[Dict[str, Any]]):
        """触发性能警报"""
        for alert in alerts:
            self.logger.warning(alert['message'])
            
            # 调用回调函数
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Alert callback error: {e}")
    
    def get_current_performance(self) -> Dict[str, Any]:
        """获取当前性能数据"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            performance_data = {
                "timestamp": time.time(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": {
                    "percent": memory_info.percent,
                    "total": memory_info.total,
                    "available": memory_info.available,
                    "used": memory_info.used
                },
                "disk": {
                    "percent": (disk_info.used / disk_info.total) * 100,
                    "total": disk_info.total,
                    "used": disk_info.used,
                    "free": disk_info.free
                }
            }
            
            # 添加网络信息（如果启用）
            if self.monitor_config['enable_detailed_monitoring']:
                network_info = psutil.net_io_counters()
                performance_data["network"] = {
                    "bytes_sent": network_info.bytes_sent,
                    "bytes_recv": network_info.bytes_recv,
                    "packets_sent": network_info.packets_sent,
                    "packets_recv": network_info.packets_recv
                }
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Failed to get current performance: {e}")
            return {}
    
    def get_performance_history(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """获取性能历史数据"""
        try:
            current_time = time.time()
            cutoff_time = current_time - (duration_minutes * 60)
            
            # 过滤历史数据
            cpu_data = [(t, v) for t, v in self.cpu_history if t >= cutoff_time]
            memory_data = [(t, v) for t, v in self.memory_history if t >= cutoff_time]
            disk_data = [(t, v) for t, v in self.disk_history if t >= cutoff_time]
            
            return {
                "duration_minutes": duration_minutes,
                "cpu_history": cpu_data,
                "memory_history": memory_data,
                "disk_history": disk_data,
                "sample_count": len(cpu_data)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance history: {e}")
            return {}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        try:
            current_performance = self.get_current_performance()
            
            # 计算历史统计
            cpu_values = [v for _, v in self.cpu_history]
            memory_values = [v for _, v in self.memory_history]
            disk_values = [v for _, v in self.disk_history]
            
            summary = {
                "current": current_performance,
                "statistics": self.performance_stats.copy(),
                "monitoring_duration": time.time() - self.performance_stats['start_time'],
                "monitoring_status": self.monitoring
            }
            
            if cpu_values:
                summary["cpu_stats"] = {
                    "min": min(cpu_values),
                    "max": max(cpu_values),
                    "avg": sum(cpu_values) / len(cpu_values)
                }
            
            if memory_values:
                summary["memory_stats"] = {
                    "min": min(memory_values),
                    "max": max(memory_values),
                    "avg": sum(memory_values) / len(memory_values)
                }
            
            if disk_values:
                summary["disk_stats"] = {
                    "min": min(disk_values),
                    "max": max(disk_values),
                    "avg": sum(disk_values) / len(disk_values)
                }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            return {}
    
    def optimize_performance(self) -> Dict[str, Any]:
        """性能优化建议"""
        try:
            current_perf = self.get_current_performance()
            optimizations = []
            
            # CPU优化建议
            cpu_percent = current_perf.get("cpu", {}).get("percent", 0)
            if cpu_percent > 80:
                optimizations.append({
                    "type": "cpu",
                    "issue": f"High CPU usage: {cpu_percent:.1f}%",
                    "suggestions": [
                        "减少并行处理线程数",
                        "优化算法复杂度",
                        "使用更高效的数据结构"
                    ]
                })
            
            # 内存优化建议
            memory_percent = current_perf.get("memory", {}).get("percent", 0)
            if memory_percent > 80:
                optimizations.append({
                    "type": "memory",
                    "issue": f"High memory usage: {memory_percent:.1f}%",
                    "suggestions": [
                        "启用内存管理器",
                        "减少缓存大小",
                        "优化数据加载策略"
                    ]
                })
            
            # 磁盘优化建议
            disk_percent = current_perf.get("disk", {}).get("percent", 0)
            if disk_percent > 90:
                optimizations.append({
                    "type": "disk",
                    "issue": f"High disk usage: {disk_percent:.1f}%",
                    "suggestions": [
                        "清理临时文件",
                        "压缩或删除旧文件",
                        "使用外部存储"
                    ]
                })
            
            return {
                "success": True,
                "current_performance": current_perf,
                "optimizations": optimizations,
                "overall_health": "good" if not optimizations else "needs_attention"
            }
            
        except Exception as e:
            self.logger.error(f"Performance optimization analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def register_alert_callback(self, callback: Callable):
        """注册警报回调函数"""
        self.alert_callbacks.append(callback)
        self.logger.info("Alert callback registered")
    
    def unregister_alert_callback(self, callback: Callable):
        """取消注册警报回调函数"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
            self.logger.info("Alert callback unregistered")
    
    def reset_statistics(self):
        """重置统计数据"""
        self.performance_stats = {
            'start_time': time.time(),
            'total_samples': 0,
            'cpu_peaks': [],
            'memory_peaks': [],
            'alerts_triggered': 0,
            'average_cpu': 0.0,
            'average_memory': 0.0
        }
        
        # 清空历史数据
        self.cpu_history.clear()
        self.memory_history.clear()
        self.disk_history.clear()
        self.network_history.clear()
        
        self.logger.info("Performance statistics reset")
    
    def cleanup(self):
        """清理资源"""
        self.stop_monitoring()
        self.alert_callbacks.clear()
        self.logger.info("Performance monitor cleanup completed")
