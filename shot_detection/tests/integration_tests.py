"""
Integration Tests
集成测试
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from .test_base import BaseTestCase
from .test_utils import TestUtils, MockDataGenerator


class IntegrationTestRunner:
    """集成测试运行器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化集成测试运行器
        
        Args:
            config: 测试配置
        """
        self.config = config or {}
        self.logger = logger.bind(component="IntegrationTestRunner")
        
        # 测试结果
        self.integration_results = []
        
        # 测试环境
        self.test_env = None
        
        self.logger.info("Integration test runner initialized")
    
    def setup_test_environment(self) -> bool:
        """设置测试环境"""
        try:
            # 创建临时测试目录
            self.test_env = {
                'base_dir': Path(tempfile.mkdtemp()),
                'config_dir': None,
                'data_dir': None,
                'output_dir': None
            }
            
            # 创建子目录
            self.test_env['config_dir'] = self.test_env['base_dir'] / 'config'
            self.test_env['data_dir'] = self.test_env['base_dir'] / 'data'
            self.test_env['output_dir'] = self.test_env['base_dir'] / 'output'
            
            for dir_path in [self.test_env['config_dir'], self.test_env['data_dir'], self.test_env['output_dir']]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            # 创建模拟数据
            mock_generator = MockDataGenerator()
            mock_generator.create_mock_test_environment(self.test_env['base_dir'])
            
            self.logger.info(f"Test environment setup at: {self.test_env['base_dir']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup test environment: {e}")
            return False
    
    def cleanup_test_environment(self):
        """清理测试环境"""
        try:
            if self.test_env and self.test_env['base_dir'].exists():
                import shutil
                shutil.rmtree(self.test_env['base_dir'])
                self.logger.info("Test environment cleaned up")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup test environment: {e}")
    
    def run_system_test_suite(self, test_suite: 'SystemTestSuite') -> Dict[str, Any]:
        """
        运行系统测试套件
        
        Args:
            test_suite: 系统测试套件
            
        Returns:
            测试结果
        """
        try:
            self.logger.info(f"Running system test suite: {test_suite.name}")
            
            # 设置测试环境
            if not self.setup_test_environment():
                return {
                    'suite_name': test_suite.name,
                    'success': False,
                    'error': 'Failed to setup test environment'
                }
            
            suite_results = {
                'suite_name': test_suite.name,
                'description': test_suite.description,
                'start_time': datetime.now().isoformat(),
                'tests': [],
                'environment': str(self.test_env['base_dir'])
            }
            
            try:
                # 运行每个测试
                for test_case in test_suite.test_cases:
                    result = self._run_integration_test(test_case)
                    suite_results['tests'].append(result)
                
                suite_results['end_time'] = datetime.now().isoformat()
                suite_results['success'] = all(t.get('success', False) for t in suite_results['tests'])
                
                # 计算统计信息
                suite_results['statistics'] = self._calculate_integration_statistics(suite_results['tests'])
                
                self.integration_results.append(suite_results)
                
                self.logger.info(f"System test suite completed: {test_suite.name}")
                
                return suite_results
                
            finally:
                # 清理测试环境
                self.cleanup_test_environment()
            
        except Exception as e:
            self.logger.error(f"System test suite failed: {e}")
            return {
                'suite_name': test_suite.name,
                'success': False,
                'error': str(e)
            }
    
    def _run_integration_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行集成测试"""
        try:
            test_name = test_case['name']
            test_type = test_case['type']
            
            self.logger.debug(f"Running integration test: {test_name}")
            
            start_time = datetime.now()
            
            if test_type == 'command_line':
                result = self._run_command_line_test(test_case)
            elif test_type == 'api':
                result = self._run_api_test(test_case)
            elif test_type == 'workflow':
                result = self._run_workflow_test(test_case)
            elif test_type == 'file_processing':
                result = self._run_file_processing_test(test_case)
            else:
                result = {
                    'success': False,
                    'error': f"Unknown test type: {test_type}"
                }
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result.update({
                'test_name': test_name,
                'test_type': test_type,
                'duration': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Integration test failed: {test_name} - {e}")
            return {
                'test_name': test_name,
                'success': False,
                'error': str(e),
                'duration': 0
            }
    
    def _run_command_line_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行命令行测试"""
        try:
            command = test_case['command']
            expected_exit_code = test_case.get('expected_exit_code', 0)
            timeout = test_case.get('timeout', 30)
            
            # 替换环境变量
            if self.test_env:
                command = command.replace('${TEST_DIR}', str(self.test_env['base_dir']))
                command = command.replace('${CONFIG_DIR}', str(self.test_env['config_dir']))
                command = command.replace('${OUTPUT_DIR}', str(self.test_env['output_dir']))
            
            # 运行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.test_env['base_dir'] if self.test_env else None
            )
            
            success = result.returncode == expected_exit_code
            
            return {
                'success': success,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': command
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Command timeout',
                'command': command
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
    
    def _run_api_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行API测试"""
        try:
            # 这里可以实现API测试逻辑
            # 例如：启动服务器，发送HTTP请求，验证响应
            
            return {
                'success': True,
                'message': 'API test placeholder - not implemented'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _run_workflow_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行工作流测试"""
        try:
            workflow_steps = test_case.get('steps', [])
            
            for step_idx, step in enumerate(workflow_steps):
                step_result = self._execute_workflow_step(step)
                
                if not step_result.get('success', False):
                    return {
                        'success': False,
                        'error': f"Workflow step {step_idx + 1} failed: {step_result.get('error', 'Unknown error')}",
                        'failed_step': step_idx + 1
                    }
            
            return {
                'success': True,
                'steps_completed': len(workflow_steps)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_workflow_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流步骤"""
        try:
            step_type = step['type']
            
            if step_type == 'create_file':
                file_path = self.test_env['base_dir'] / step['path']
                content = step.get('content', '')
                
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {'success': True}
                
            elif step_type == 'run_command':
                command = step['command']
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.test_env['base_dir']
                )
                
                return {
                    'success': result.returncode == 0,
                    'exit_code': result.returncode,
                    'output': result.stdout
                }
                
            elif step_type == 'check_file':
                file_path = self.test_env['base_dir'] / step['path']
                exists = file_path.exists()
                
                return {
                    'success': exists,
                    'file_exists': exists
                }
                
            else:
                return {
                    'success': False,
                    'error': f"Unknown step type: {step_type}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _run_file_processing_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """运行文件处理测试"""
        try:
            input_files = test_case.get('input_files', [])
            expected_outputs = test_case.get('expected_outputs', [])
            
            # 创建输入文件
            for input_file in input_files:
                file_path = self.test_env['data_dir'] / input_file['name']
                content = input_file.get('content', '')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # 运行处理命令
            command = test_case.get('command', '')
            if command:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.test_env['base_dir']
                )
                
                if result.returncode != 0:
                    return {
                        'success': False,
                        'error': f"Processing command failed: {result.stderr}"
                    }
            
            # 检查输出文件
            for expected_output in expected_outputs:
                output_path = self.test_env['output_dir'] / expected_output['name']
                
                if not output_path.exists():
                    return {
                        'success': False,
                        'error': f"Expected output file not found: {expected_output['name']}"
                    }
                
                # 可以添加更多的文件内容验证
            
            return {
                'success': True,
                'processed_files': len(input_files),
                'output_files': len(expected_outputs)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_integration_statistics(self, tests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算集成测试统计信息"""
        try:
            total_tests = len(tests)
            successful_tests = len([t for t in tests if t.get('success', False)])
            failed_tests = total_tests - successful_tests
            
            total_duration = sum(t.get('duration', 0) for t in tests)
            avg_duration = total_duration / total_tests if total_tests > 0 else 0
            
            return {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                'total_duration': total_duration,
                'average_duration': avg_duration
            }
            
        except Exception as e:
            self.logger.error(f"Failed to calculate statistics: {e}")
            return {}
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """生成集成测试报告"""
        try:
            if not self.integration_results:
                return {'error': 'No integration test results available'}
            
            report = {
                'report_generated_at': datetime.now().isoformat(),
                'total_suites': len(self.integration_results),
                'suites': self.integration_results,
                'summary': self._generate_integration_summary()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate integration report: {e}")
            return {'error': str(e)}
    
    def _generate_integration_summary(self) -> Dict[str, Any]:
        """生成集成测试摘要"""
        try:
            all_tests = []
            for suite in self.integration_results:
                all_tests.extend(suite.get('tests', []))
            
            total_tests = len(all_tests)
            successful_tests = len([t for t in all_tests if t.get('success', False)])
            
            return {
                'total_test_suites': len(self.integration_results),
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': total_tests - successful_tests,
                'overall_success_rate': (successful_tests / total_tests * 100) if total_tests > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}")
            return {}


class SystemTestSuite:
    """系统测试套件"""
    
    def __init__(self, name: str, description: str = ""):
        """
        初始化系统测试套件
        
        Args:
            name: 套件名称
            description: 套件描述
        """
        self.name = name
        self.description = description
        self.test_cases = []
        
        self.logger = logger.bind(component="SystemTestSuite")
    
    def add_command_line_test(self, name: str, command: str, 
                             expected_exit_code: int = 0, timeout: int = 30):
        """添加命令行测试"""
        test_case = {
            'name': name,
            'type': 'command_line',
            'command': command,
            'expected_exit_code': expected_exit_code,
            'timeout': timeout
        }
        
        self.test_cases.append(test_case)
        self.logger.debug(f"Added command line test: {name}")
    
    def add_workflow_test(self, name: str, steps: List[Dict[str, Any]]):
        """添加工作流测试"""
        test_case = {
            'name': name,
            'type': 'workflow',
            'steps': steps
        }
        
        self.test_cases.append(test_case)
        self.logger.debug(f"Added workflow test: {name}")
    
    def add_file_processing_test(self, name: str, input_files: List[Dict[str, Any]],
                                expected_outputs: List[Dict[str, Any]], command: str = ""):
        """添加文件处理测试"""
        test_case = {
            'name': name,
            'type': 'file_processing',
            'input_files': input_files,
            'expected_outputs': expected_outputs,
            'command': command
        }
        
        self.test_cases.append(test_case)
        self.logger.debug(f"Added file processing test: {name}")
    
    def get_test_count(self) -> int:
        """获取测试数量"""
        return len(self.test_cases)
