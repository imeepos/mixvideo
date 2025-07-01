"""
Performance Tests
性能测试
"""

import time
import psutil
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from loguru import logger

from .test_base import BaseTestCase
from .test_utils import TestUtils, MockDataGenerator


class PerformanceTestRunner:
    """性能测试运行器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化性能测试运行器
        
        Args:
            config: 测试配置
        """
        self.config = config or {}
        self.logger = logger.bind(component="PerformanceTestRunner")
        
        # 性能测试结果
        self.performance_results = []
        
        # 系统监控
        self.system_monitor = SystemMonitor()
        
        self.logger.info("Performance test runner initialized")
    
    def run_benchmark_suite(self, benchmark_suite: 'BenchmarkSuite') -> Dict[str, Any]:
        """
        运行基准测试套件
        
        Args:
            benchmark_suite: 基准测试套件
            
        Returns:
            测试结果
        """
        try:
            self.logger.info(f"Running benchmark suite: {benchmark_suite.name}")
            
            suite_results = {
                'suite_name': benchmark_suite.name,
                'description': benchmark_suite.description,
                'start_time': datetime.now().isoformat(),
                'benchmarks': [],
                'system_info': self._get_system_info()
            }
            
            # 运行每个基准测试
            for benchmark in benchmark_suite.benchmarks:
                result = self._run_single_benchmark(benchmark)
                suite_results['benchmarks'].append(result)
            
            suite_results['end_time'] = datetime.now().isoformat()
            suite_results['total_duration'] = sum(b['duration'] for b in suite_results['benchmarks'])
            
            # 计算统计信息
            suite_results['statistics'] = self._calculate_suite_statistics(suite_results['benchmarks'])
            
            self.performance_results.append(suite_results)
            
            self.logger.info(f"Benchmark suite completed: {benchmark_suite.name}")
            
            return suite_results
            
        except Exception as e:
            self.logger.error(f"Benchmark suite failed: {e}")
            return {
                'suite_name': benchmark_suite.name,
                'error': str(e),
                'success': False
            }
    
    def _run_single_benchmark(self, benchmark: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个基准测试"""
        try:
            benchmark_name = benchmark['name']
            benchmark_func = benchmark['function']
            iterations = benchmark.get('iterations', 1)
            warmup_iterations = benchmark.get('warmup_iterations', 0)
            
            self.logger.debug(f"Running benchmark: {benchmark_name}")
            
            # 预热
            for _ in range(warmup_iterations):
                benchmark_func()
            
            # 开始监控
            self.system_monitor.start_monitoring()
            
            # 运行基准测试
            times = []
            memory_usage = []
            
            for i in range(iterations):
                # 记录内存使用
                memory_before = psutil.Process().memory_info().rss
                
                # 运行测试
                start_time = time.perf_counter()
                result = benchmark_func()
                end_time = time.perf_counter()
                
                duration = end_time - start_time
                times.append(duration)
                
                # 记录内存使用
                memory_after = psutil.Process().memory_info().rss
                memory_usage.append(memory_after - memory_before)
                
                self.logger.debug(f"Iteration {i + 1}: {duration:.4f}s")
            
            # 停止监控
            monitoring_data = self.system_monitor.stop_monitoring()
            
            # 计算统计信息
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            avg_memory = sum(memory_usage) / len(memory_usage) if memory_usage else 0
            max_memory = max(memory_usage) if memory_usage else 0
            
            benchmark_result = {
                'name': benchmark_name,
                'iterations': iterations,
                'times': times,
                'duration': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'memory_usage': {
                    'avg_bytes': avg_memory,
                    'max_bytes': max_memory,
                    'all_measurements': memory_usage
                },
                'system_monitoring': monitoring_data,
                'success': True
            }
            
            return benchmark_result
            
        except Exception as e:
            self.logger.error(f"Benchmark failed: {benchmark_name} - {e}")
            return {
                'name': benchmark_name,
                'error': str(e),
                'success': False,
                'duration': 0
            }
    
    def _calculate_suite_statistics(self, benchmarks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算套件统计信息"""
        try:
            successful_benchmarks = [b for b in benchmarks if b.get('success', False)]
            
            if not successful_benchmarks:
                return {'error': 'No successful benchmarks'}
            
            total_time = sum(b['duration'] for b in successful_benchmarks)
            avg_time = total_time / len(successful_benchmarks)
            
            fastest_benchmark = min(successful_benchmarks, key=lambda x: x['duration'])
            slowest_benchmark = max(successful_benchmarks, key=lambda x: x['duration'])
            
            total_memory = sum(b['memory_usage']['avg_bytes'] for b in successful_benchmarks)
            avg_memory = total_memory / len(successful_benchmarks)
            
            return {
                'total_benchmarks': len(benchmarks),
                'successful_benchmarks': len(successful_benchmarks),
                'failed_benchmarks': len(benchmarks) - len(successful_benchmarks),
                'total_time': total_time,
                'average_time': avg_time,
                'fastest_benchmark': {
                    'name': fastest_benchmark['name'],
                    'time': fastest_benchmark['duration']
                },
                'slowest_benchmark': {
                    'name': slowest_benchmark['name'],
                    'time': slowest_benchmark['duration']
                },
                'average_memory_usage': avg_memory
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate statistics: {e}")
            return {'error': str(e)}
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'platform': self._get_platform_info()
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {}
    
    def _get_platform_info(self) -> Dict[str, str]:
        """获取平台信息"""
        import platform
        
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor()
        }
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        try:
            if not self.performance_results:
                return {'error': 'No performance results available'}
            
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'total_suites': len(self.performance_results),
                'suites': self.performance_results,
                'summary': self._generate_summary()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            return {'error': str(e)}
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成摘要"""
        try:
            all_benchmarks = []
            for suite in self.performance_results:
                all_benchmarks.extend(suite.get('benchmarks', []))
            
            successful_benchmarks = [b for b in all_benchmarks if b.get('success', False)]
            
            if not successful_benchmarks:
                return {'error': 'No successful benchmarks'}
            
            total_time = sum(b['duration'] for b in successful_benchmarks)
            avg_time = total_time / len(successful_benchmarks)
            
            return {
                'total_benchmarks': len(all_benchmarks),
                'successful_benchmarks': len(successful_benchmarks),
                'total_execution_time': total_time,
                'average_execution_time': avg_time,
                'performance_score': self._calculate_performance_score(successful_benchmarks)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")
            return {'error': str(e)}
    
    def _calculate_performance_score(self, benchmarks: List[Dict[str, Any]]) -> float:
        """计算性能分数"""
        try:
            # 简单的性能分数计算
            # 基于执行时间和内存使用的综合评分
            
            time_scores = []
            memory_scores = []
            
            for benchmark in benchmarks:
                # 时间分数（越快越好）
                time_score = 1.0 / (benchmark['duration'] + 0.001)  # 避免除零
                time_scores.append(time_score)
                
                # 内存分数（越少越好）
                memory_usage = benchmark['memory_usage']['avg_bytes']
                memory_score = 1.0 / (memory_usage / 1024 / 1024 + 1)  # 转换为MB
                memory_scores.append(memory_score)
            
            avg_time_score = sum(time_scores) / len(time_scores)
            avg_memory_score = sum(memory_scores) / len(memory_scores)
            
            # 综合分数（时间权重70%，内存权重30%）
            performance_score = (avg_time_score * 0.7 + avg_memory_score * 0.3) * 100
            
            return round(performance_score, 2)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate performance score: {e}")
            return 0.0
    
    def save_performance_report(self, report: Dict[str, Any], output_path: str) -> bool:
        """保存性能报告"""
        try:
            import json
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Performance report saved to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save performance report: {e}")
            return False


class BenchmarkSuite:
    """基准测试套件"""
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化基准测试套件
        
        Args:
            name: 套件名称
            description: 套件描述
        """
        self.name = name
        self.description = description
        self.benchmarks = []
        
        self.logger = logger.bind(component="BenchmarkSuite")
    
    def add_benchmark(self, name: str, function: Callable, 
                     iterations: int = 1, warmup_iterations: int = 0):
        """
        添加基准测试
        
        Args:
            name: 基准测试名称
            function: 测试函数
            iterations: 迭代次数
            warmup_iterations: 预热迭代次数
        """
        benchmark = {
            'name': name,
            'function': function,
            'iterations': iterations,
            'warmup_iterations': warmup_iterations
        }
        
        self.benchmarks.append(benchmark)
        self.logger.debug(f"Added benchmark: {name}")
    
    def get_benchmark_count(self) -> int:
        """获取基准测试数量"""
        return len(self.benchmarks)


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        """初始化系统监控器"""
        self.logger = logger.bind(component="SystemMonitor")
        self.monitoring = False
        self.monitoring_data = []
        self.monitor_thread = None
    
    def start_monitoring(self, interval: float = 0.1):
        """开始监控"""
        try:
            self.monitoring = True
            self.monitoring_data.clear()
            
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                args=(interval,),
                daemon=True
            )
            self.monitor_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """停止监控并返回数据"""
        try:
            self.monitoring = False
            
            if self.monitor_thread:
                self.monitor_thread.join(timeout=1.0)
            
            return self._process_monitoring_data()
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
            return {}
    
    def _monitor_loop(self, interval: float):
        """监控循环"""
        while self.monitoring:
            try:
                data_point = {
                    'timestamp': time.time(),
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'memory_used': psutil.virtual_memory().used,
                    'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None,
                    'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None
                }
                
                self.monitoring_data.append(data_point)
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                break
    
    def _process_monitoring_data(self) -> Dict[str, Any]:
        """处理监控数据"""
        try:
            if not self.monitoring_data:
                return {}
            
            cpu_values = [d['cpu_percent'] for d in self.monitoring_data]
            memory_values = [d['memory_percent'] for d in self.monitoring_data]
            
            return {
                'duration': self.monitoring_data[-1]['timestamp'] - self.monitoring_data[0]['timestamp'],
                'data_points': len(self.monitoring_data),
                'cpu_usage': {
                    'avg': sum(cpu_values) / len(cpu_values),
                    'max': max(cpu_values),
                    'min': min(cpu_values)
                },
                'memory_usage': {
                    'avg': sum(memory_values) / len(memory_values),
                    'max': max(memory_values),
                    'min': min(memory_values)
                },
                'raw_data': self.monitoring_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process monitoring data: {e}")
            return {}
