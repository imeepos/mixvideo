"""
Test Runner
测试运行器
"""

import unittest
import time
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from loguru import logger


class TestRunner:
    """测试运行器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化测试运行器
        
        Args:
            config: 测试配置
        """
        self.config = config or {}
        self.logger = logger.bind(component="TestRunner")
        
        # 测试结果
        self.test_results = []
        
        # 测试统计
        self.stats = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'error_tests': 0,
            'start_time': None,
            'end_time': None,
            'duration': 0
        }
        
        # 测试套件
        self.test_suites = []
        
        self.logger.info("Test runner initialized")
    
    def add_test_suite(self, test_suite: 'TestSuite'):
        """
        添加测试套件
        
        Args:
            test_suite: 测试套件
        """
        self.test_suites.append(test_suite)
        self.logger.info(f"Added test suite: {test_suite.name}")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        运行所有测试
        
        Returns:
            测试结果
        """
        try:
            self.logger.info("Starting test execution")
            self.stats['start_time'] = datetime.now()
            
            # 重置统计
            self.test_results.clear()
            self.stats.update({
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'error_tests': 0
            })
            
            # 运行所有测试套件
            for test_suite in self.test_suites:
                suite_results = self._run_test_suite(test_suite)
                self.test_results.extend(suite_results)
            
            # 计算统计信息
            self._calculate_stats()
            
            self.stats['end_time'] = datetime.now()
            self.stats['duration'] = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
            
            self.logger.info(f"Test execution completed in {self.stats['duration']:.2f}s")
            
            return self._generate_test_report()
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }
    
    def _run_test_suite(self, test_suite: 'TestSuite') -> List[Dict[str, Any]]:
        """运行测试套件"""
        try:
            self.logger.info(f"Running test suite: {test_suite.name}")
            
            suite_results = []
            
            for test_case in test_suite.test_cases:
                result = self._run_test_case(test_case, test_suite.name)
                suite_results.append(result)
            
            return suite_results
            
        except Exception as e:
            self.logger.error(f"Test suite execution failed: {e}")
            return [{
                'test_name': f"{test_suite.name}_error",
                'suite_name': test_suite.name,
                'status': 'error',
                'error': str(e),
                'duration': 0
            }]
    
    def _run_test_case(self, test_case: Callable, suite_name: str) -> Dict[str, Any]:
        """运行单个测试用例"""
        test_name = getattr(test_case, '__name__', str(test_case))
        
        try:
            self.logger.debug(f"Running test: {test_name}")
            
            start_time = time.time()
            
            # 运行测试
            test_case()
            
            duration = time.time() - start_time
            
            result = {
                'test_name': test_name,
                'suite_name': suite_name,
                'status': 'passed',
                'duration': duration,
                'message': 'Test passed successfully'
            }
            
            self.logger.debug(f"Test passed: {test_name} ({duration:.3f}s)")
            
            return result
            
        except unittest.SkipTest as e:
            duration = time.time() - start_time
            
            result = {
                'test_name': test_name,
                'suite_name': suite_name,
                'status': 'skipped',
                'duration': duration,
                'message': str(e)
            }
            
            self.logger.debug(f"Test skipped: {test_name}")
            
            return result
            
        except AssertionError as e:
            duration = time.time() - start_time
            
            result = {
                'test_name': test_name,
                'suite_name': suite_name,
                'status': 'failed',
                'duration': duration,
                'message': str(e),
                'traceback': traceback.format_exc()
            }
            
            self.logger.warning(f"Test failed: {test_name} - {str(e)}")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            result = {
                'test_name': test_name,
                'suite_name': suite_name,
                'status': 'error',
                'duration': duration,
                'message': str(e),
                'traceback': traceback.format_exc()
            }
            
            self.logger.error(f"Test error: {test_name} - {str(e)}")
            
            return result
    
    def _calculate_stats(self):
        """计算测试统计信息"""
        try:
            self.stats['total_tests'] = len(self.test_results)
            
            for result in self.test_results:
                status = result['status']
                if status == 'passed':
                    self.stats['passed_tests'] += 1
                elif status == 'failed':
                    self.stats['failed_tests'] += 1
                elif status == 'skipped':
                    self.stats['skipped_tests'] += 1
                elif status == 'error':
                    self.stats['error_tests'] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to calculate stats: {e}")
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        try:
            # 按套件分组结果
            suite_results = {}
            for result in self.test_results:
                suite_name = result['suite_name']
                if suite_name not in suite_results:
                    suite_results[suite_name] = []
                suite_results[suite_name].append(result)
            
            # 计算成功率
            success_rate = 0
            if self.stats['total_tests'] > 0:
                success_rate = (self.stats['passed_tests'] / self.stats['total_tests']) * 100
            
            report = {
                'success': self.stats['failed_tests'] == 0 and self.stats['error_tests'] == 0,
                'stats': self.stats.copy(),
                'success_rate': success_rate,
                'suite_results': suite_results,
                'failed_tests': [r for r in self.test_results if r['status'] in ['failed', 'error']],
                'report_generated_at': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate test report: {e}")
            return {
                'success': False,
                'error': f"Report generation failed: {str(e)}",
                'stats': self.stats
            }
    
    def run_specific_tests(self, test_patterns: List[str]) -> Dict[str, Any]:
        """
        运行特定的测试
        
        Args:
            test_patterns: 测试模式列表
            
        Returns:
            测试结果
        """
        try:
            self.logger.info(f"Running specific tests: {test_patterns}")
            
            # 过滤测试用例
            filtered_suites = []
            
            for test_suite in self.test_suites:
                filtered_cases = []
                
                for test_case in test_suite.test_cases:
                    test_name = getattr(test_case, '__name__', str(test_case))
                    
                    # 检查是否匹配模式
                    for pattern in test_patterns:
                        if pattern in test_name or pattern in test_suite.name:
                            filtered_cases.append(test_case)
                            break
                
                if filtered_cases:
                    filtered_suite = TestSuite(test_suite.name, test_suite.description)
                    filtered_suite.test_cases = filtered_cases
                    filtered_suites.append(filtered_suite)
            
            # 临时替换测试套件
            original_suites = self.test_suites
            self.test_suites = filtered_suites
            
            try:
                result = self.run_all_tests()
                return result
            finally:
                self.test_suites = original_suites
            
        except Exception as e:
            self.logger.error(f"Failed to run specific tests: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }
    
    def save_report(self, report: Dict[str, Any], output_path: str) -> bool:
        """
        保存测试报告
        
        Args:
            report: 测试报告
            output_path: 输出路径
            
        Returns:
            是否保存成功
        """
        try:
            import json
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Test report saved to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save test report: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            self.test_results.clear()
            self.test_suites.clear()
            self.logger.info("Test runner cleanup completed")
        except Exception as e:
            self.logger.error(f"Test runner cleanup failed: {e}")


class TestSuite:
    """测试套件"""
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化测试套件
        
        Args:
            name: 套件名称
            description: 套件描述
        """
        self.name = name
        self.description = description
        self.test_cases = []
        self.setup_func = None
        self.teardown_func = None
        
        self.logger = logger.bind(component="TestSuite")
    
    def add_test(self, test_func: Callable):
        """
        添加测试用例
        
        Args:
            test_func: 测试函数
        """
        self.test_cases.append(test_func)
        self.logger.debug(f"Added test: {getattr(test_func, '__name__', str(test_func))}")
    
    def set_setup(self, setup_func: Callable):
        """
        设置初始化函数
        
        Args:
            setup_func: 初始化函数
        """
        self.setup_func = setup_func
    
    def set_teardown(self, teardown_func: Callable):
        """
        设置清理函数
        
        Args:
            teardown_func: 清理函数
        """
        self.teardown_func = teardown_func
    
    def run_setup(self):
        """运行初始化"""
        if self.setup_func:
            try:
                self.setup_func()
                self.logger.debug(f"Setup completed for suite: {self.name}")
            except Exception as e:
                self.logger.error(f"Setup failed for suite {self.name}: {e}")
                raise
    
    def run_teardown(self):
        """运行清理"""
        if self.teardown_func:
            try:
                self.teardown_func()
                self.logger.debug(f"Teardown completed for suite: {self.name}")
            except Exception as e:
                self.logger.error(f"Teardown failed for suite {self.name}: {e}")
    
    def get_test_count(self) -> int:
        """获取测试用例数量"""
        return len(self.test_cases)
    
    def get_info(self) -> Dict[str, Any]:
        """获取套件信息"""
        return {
            'name': self.name,
            'description': self.description,
            'test_count': self.get_test_count(),
            'has_setup': self.setup_func is not None,
            'has_teardown': self.teardown_func is not None
        }
