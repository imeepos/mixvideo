"""
Code Analysis for Documentation
代码分析文档生成
"""

import ast
import os
import re
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime
from loguru import logger


class AnalysisConfig:
    """代码分析配置"""
    
    def __init__(self):
        """初始化代码分析配置"""
        self.include_private = False
        self.include_tests = False
        self.analyze_complexity = True
        self.analyze_dependencies = True
        self.analyze_coverage = False
        self.generate_metrics = True
        self.include_todos = True
        self.include_fixmes = True


class CodeAnalyzer:
    """代码分析器"""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        """
        初始化代码分析器
        
        Args:
            config: 分析配置
        """
        self.config = config or AnalysisConfig()
        self.logger = logger.bind(component="CodeAnalyzer")
        
        # 分析结果
        self.analysis_results = {
            'modules': {},
            'classes': {},
            'functions': {},
            'dependencies': {},
            'metrics': {},
            'issues': [],
            'todos': [],
            'complexity': {}
        }
        
        self.logger.info("Code analyzer initialized")
    
    def analyze_codebase(self, source_dir: Path) -> Dict[str, Any]:
        """
        分析代码库
        
        Args:
            source_dir: 源代码目录
            
        Returns:
            分析结果
        """
        try:
            self.logger.info(f"Analyzing codebase: {source_dir}")
            
            # 重置结果
            self.analysis_results = {
                'modules': {},
                'classes': {},
                'functions': {},
                'dependencies': {},
                'metrics': {},
                'issues': [],
                'todos': [],
                'complexity': {}
            }
            
            # 分析所有Python文件
            python_files = list(source_dir.rglob("*.py"))
            
            for py_file in python_files:
                if self._should_analyze_file(py_file):
                    self._analyze_file(py_file)
            
            # 分析依赖关系
            if self.config.analyze_dependencies:
                self._analyze_dependencies()
            
            # 计算指标
            if self.config.generate_metrics:
                self._calculate_metrics()
            
            # 分析复杂度
            if self.config.analyze_complexity:
                self._analyze_complexity()
            
            self.logger.info(f"Analyzed {len(self.analysis_results['modules'])} modules")
            
            return self.analysis_results
            
        except Exception as e:
            self.logger.error(f"Codebase analysis failed: {e}")
            return {}
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """检查是否应该分析文件"""
        # 跳过__pycache__目录
        if '__pycache__' in str(file_path):
            return False
        
        # 跳过测试文件（如果配置不包含）
        if not self.config.include_tests and 'test' in str(file_path):
            return False
        
        return True
    
    def _analyze_file(self, file_path: Path):
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 获取模块信息
            module_name = self._get_module_name(file_path)
            
            module_info = {
                'name': module_name,
                'file_path': str(file_path),
                'file_size': len(content),
                'line_count': len(content.split('\n')),
                'docstring': ast.get_docstring(tree),
                'classes': [],
                'functions': [],
                'imports': [],
                'constants': [],
                'todos': [],
                'fixmes': [],
                'complexity_score': 0
            }
            
            # 分析导入
            self._analyze_imports(tree, module_info)
            
            # 分析AST节点
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class_node(node, file_path)
                    module_info['classes'].append(class_info)
                    self.analysis_results['classes'][f"{module_name}.{node.name}"] = class_info
                
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_') or self.config.include_private:
                        function_info = self._analyze_function_node(node, file_path)
                        module_info['functions'].append(function_info)
                        self.analysis_results['functions'][f"{module_name}.{node.name}"] = function_info
                
                elif isinstance(node, ast.Assign):
                    # 分析常量
                    self._analyze_assignment(node, module_info)
            
            # 分析TODO和FIXME注释
            if self.config.include_todos or self.config.include_fixmes:
                self._analyze_comments(content, module_info)
            
            # 计算模块复杂度
            module_info['complexity_score'] = self._calculate_module_complexity(tree)
            
            self.analysis_results['modules'][module_name] = module_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze file {file_path}: {e}")
    
    def _get_module_name(self, file_path: Path) -> str:
        """获取模块名称"""
        try:
            # 假设源代码在shot_detection目录下
            parts = file_path.parts
            
            # 找到shot_detection目录的索引
            shot_detection_idx = -1
            for i, part in enumerate(parts):
                if part == 'shot_detection':
                    shot_detection_idx = i
                    break
            
            if shot_detection_idx >= 0:
                module_parts = parts[shot_detection_idx:]
                
                # 移除文件扩展名
                if module_parts[-1].endswith('.py'):
                    module_parts = module_parts[:-1] + (module_parts[-1][:-3],)
                
                # 如果是__init__.py，移除最后一部分
                if module_parts[-1] == '__init__':
                    module_parts = module_parts[:-1]
                
                return '.'.join(module_parts)
            else:
                return file_path.stem
                
        except Exception:
            return file_path.stem
    
    def _analyze_imports(self, tree: ast.AST, module_info: Dict[str, Any]):
        """分析导入语句"""
        try:
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_info = {
                            'type': 'import',
                            'module': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        }
                        module_info['imports'].append(import_info)
                
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        import_info = {
                            'type': 'from_import',
                            'module': node.module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        }
                        module_info['imports'].append(import_info)
                        
        except Exception as e:
            self.logger.error(f"Failed to analyze imports: {e}")
    
    def _analyze_class_node(self, node: ast.ClassDef, file_path: Path) -> Dict[str, Any]:
        """分析类节点"""
        try:
            class_info = {
                'name': node.name,
                'docstring': ast.get_docstring(node),
                'line_number': node.lineno,
                'end_line': self._get_node_end_line(node),
                'bases': [self._get_node_name(base) for base in node.bases],
                'decorators': [self._get_node_name(dec) for dec in node.decorator_list],
                'methods': [],
                'properties': [],
                'class_variables': [],
                'complexity_score': 0,
                'method_count': 0,
                'property_count': 0
            }
            
            # 分析类成员
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if not item.name.startswith('_') or self.config.include_private:
                        method_info = self._analyze_function_node(item, file_path, is_method=True)
                        
                        if self._is_property(item):
                            class_info['properties'].append(method_info)
                            class_info['property_count'] += 1
                        else:
                            class_info['methods'].append(method_info)
                            class_info['method_count'] += 1
                
                elif isinstance(item, ast.Assign):
                    # 类变量
                    for target in item.targets:
                        if isinstance(target, ast.Name):
                            var_info = {
                                'name': target.id,
                                'line': item.lineno,
                                'value': self._get_node_value(item.value)
                            }
                            class_info['class_variables'].append(var_info)
            
            # 计算类复杂度
            class_info['complexity_score'] = self._calculate_class_complexity(node)
            
            return class_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze class {node.name}: {e}")
            return {'name': node.name, 'error': str(e)}
    
    def _analyze_function_node(self, node: ast.FunctionDef, file_path: Path, 
                              is_method: bool = False) -> Dict[str, Any]:
        """分析函数节点"""
        try:
            function_info = {
                'name': node.name,
                'docstring': ast.get_docstring(node),
                'line_number': node.lineno,
                'end_line': self._get_node_end_line(node),
                'is_method': is_method,
                'is_async': isinstance(node, ast.AsyncFunctionDef),
                'decorators': [self._get_node_name(dec) for dec in node.decorator_list],
                'parameters': [],
                'returns': None,
                'complexity_score': 0,
                'line_count': 0
            }
            
            # 分析参数
            for arg in node.args.args:
                param_info = {
                    'name': arg.arg,
                    'annotation': self._get_node_name(arg.annotation) if arg.annotation else None
                }
                function_info['parameters'].append(param_info)
            
            # 分析返回类型
            if node.returns:
                function_info['returns'] = self._get_node_name(node.returns)
            
            # 计算函数复杂度
            function_info['complexity_score'] = self._calculate_function_complexity(node)
            function_info['line_count'] = function_info['end_line'] - function_info['line_number'] + 1
            
            return function_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze function {node.name}: {e}")
            return {'name': node.name, 'error': str(e)}
    
    def _analyze_assignment(self, node: ast.Assign, module_info: Dict[str, Any]):
        """分析赋值语句"""
        try:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    # 常量
                    constant_info = {
                        'name': target.id,
                        'value': self._get_node_value(node.value),
                        'line': node.lineno,
                        'type': self._infer_type(node.value)
                    }
                    module_info['constants'].append(constant_info)
                    
        except Exception as e:
            self.logger.error(f"Failed to analyze assignment: {e}")
    
    def _analyze_comments(self, content: str, module_info: Dict[str, Any]):
        """分析注释中的TODO和FIXME"""
        try:
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                if self.config.include_todos and 'TODO' in line.upper():
                    todo_info = {
                        'line': line_num,
                        'text': line,
                        'type': 'TODO'
                    }
                    module_info['todos'].append(todo_info)
                    self.analysis_results['todos'].append(todo_info)
                
                if self.config.include_fixmes and 'FIXME' in line.upper():
                    fixme_info = {
                        'line': line_num,
                        'text': line,
                        'type': 'FIXME'
                    }
                    module_info['fixmes'].append(fixme_info)
                    self.analysis_results['todos'].append(fixme_info)
                    
        except Exception as e:
            self.logger.error(f"Failed to analyze comments: {e}")
    
    def _get_node_name(self, node) -> str:
        """获取AST节点名称"""
        if node is None:
            return ""
        
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        else:
            return str(type(node).__name__)
    
    def _get_node_value(self, node) -> str:
        """获取AST节点值"""
        try:
            if isinstance(node, ast.Constant):
                return repr(node.value)
            elif isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.List):
                return f"[{len(node.elts)} items]"
            elif isinstance(node, ast.Dict):
                return f"{{{len(node.keys)} items}}"
            else:
                return "..."
        except Exception:
            return "..."
    
    def _get_node_end_line(self, node) -> int:
        """获取节点结束行号"""
        try:
            if hasattr(node, 'end_lineno') and node.end_lineno:
                return node.end_lineno
            
            # 递归查找最大行号
            max_line = node.lineno
            for child in ast.walk(node):
                if hasattr(child, 'lineno') and child.lineno > max_line:
                    max_line = child.lineno
            
            return max_line
            
        except Exception:
            return node.lineno
    
    def _infer_type(self, node) -> str:
        """推断节点类型"""
        if isinstance(node, ast.Constant):
            return type(node.value).__name__
        elif isinstance(node, ast.List):
            return 'list'
        elif isinstance(node, ast.Dict):
            return 'dict'
        elif isinstance(node, ast.Set):
            return 'set'
        elif isinstance(node, ast.Tuple):
            return 'tuple'
        else:
            return 'unknown'
    
    def _is_property(self, node: ast.FunctionDef) -> bool:
        """检查是否为属性"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'property':
                return True
        return False
    
    def _calculate_module_complexity(self, tree: ast.AST) -> int:
        """计算模块复杂度"""
        try:
            complexity = 1  # 基础复杂度
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(node, (ast.And, ast.Or)):
                    complexity += 1
            
            return complexity
            
        except Exception:
            return 1
    
    def _calculate_class_complexity(self, node: ast.ClassDef) -> int:
        """计算类复杂度"""
        try:
            complexity = 1  # 基础复杂度
            
            # 方法数量增加复杂度
            method_count = len([item for item in node.body if isinstance(item, ast.FunctionDef)])
            complexity += method_count
            
            # 继承增加复杂度
            complexity += len(node.bases)
            
            return complexity
            
        except Exception:
            return 1
    
    def _calculate_function_complexity(self, node: ast.FunctionDef) -> int:
        """计算函数复杂度（循环复杂度）"""
        try:
            complexity = 1  # 基础复杂度
            
            for child in ast.walk(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(child, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(child, (ast.And, ast.Or)):
                    complexity += 1
                elif isinstance(child, ast.comprehension):
                    complexity += 1
            
            return complexity
            
        except Exception:
            return 1
    
    def _analyze_dependencies(self):
        """分析依赖关系"""
        try:
            dependencies = {}
            
            for module_name, module_info in self.analysis_results['modules'].items():
                module_deps = set()
                
                for import_info in module_info.get('imports', []):
                    if import_info['type'] == 'import':
                        module_deps.add(import_info['module'])
                    elif import_info['type'] == 'from_import' and import_info['module']:
                        module_deps.add(import_info['module'])
                
                dependencies[module_name] = list(module_deps)
            
            self.analysis_results['dependencies'] = dependencies
            
        except Exception as e:
            self.logger.error(f"Dependency analysis failed: {e}")
    
    def _calculate_metrics(self):
        """计算代码指标"""
        try:
            metrics = {
                'total_modules': len(self.analysis_results['modules']),
                'total_classes': len(self.analysis_results['classes']),
                'total_functions': len(self.analysis_results['functions']),
                'total_lines': 0,
                'total_todos': len(self.analysis_results['todos']),
                'average_complexity': 0,
                'max_complexity': 0,
                'complexity_distribution': {'low': 0, 'medium': 0, 'high': 0}
            }
            
            # 计算总行数和复杂度
            complexities = []
            
            for module_info in self.analysis_results['modules'].values():
                metrics['total_lines'] += module_info.get('line_count', 0)
                
                module_complexity = module_info.get('complexity_score', 0)
                complexities.append(module_complexity)
                
                # 分类复杂度
                if module_complexity <= 5:
                    metrics['complexity_distribution']['low'] += 1
                elif module_complexity <= 15:
                    metrics['complexity_distribution']['medium'] += 1
                else:
                    metrics['complexity_distribution']['high'] += 1
            
            if complexities:
                metrics['average_complexity'] = sum(complexities) / len(complexities)
                metrics['max_complexity'] = max(complexities)
            
            # 计算函数复杂度
            function_complexities = []
            for function_info in self.analysis_results['functions'].values():
                function_complexities.append(function_info.get('complexity_score', 0))
            
            if function_complexities:
                metrics['average_function_complexity'] = sum(function_complexities) / len(function_complexities)
                metrics['max_function_complexity'] = max(function_complexities)
            
            self.analysis_results['metrics'] = metrics
            
        except Exception as e:
            self.logger.error(f"Metrics calculation failed: {e}")
    
    def _analyze_complexity(self):
        """分析复杂度分布"""
        try:
            complexity_analysis = {
                'modules': {},
                'classes': {},
                'functions': {},
                'hotspots': []
            }
            
            # 模块复杂度
            for module_name, module_info in self.analysis_results['modules'].items():
                complexity = module_info.get('complexity_score', 0)
                complexity_analysis['modules'][module_name] = {
                    'complexity': complexity,
                    'category': self._categorize_complexity(complexity)
                }
            
            # 类复杂度
            for class_name, class_info in self.analysis_results['classes'].items():
                complexity = class_info.get('complexity_score', 0)
                complexity_analysis['classes'][class_name] = {
                    'complexity': complexity,
                    'category': self._categorize_complexity(complexity)
                }
            
            # 函数复杂度
            for function_name, function_info in self.analysis_results['functions'].items():
                complexity = function_info.get('complexity_score', 0)
                complexity_analysis['functions'][function_name] = {
                    'complexity': complexity,
                    'category': self._categorize_complexity(complexity)
                }
                
                # 识别复杂度热点
                if complexity > 10:
                    complexity_analysis['hotspots'].append({
                        'name': function_name,
                        'type': 'function',
                        'complexity': complexity,
                        'line': function_info.get('line_number', 0)
                    })
            
            self.analysis_results['complexity'] = complexity_analysis
            
        except Exception as e:
            self.logger.error(f"Complexity analysis failed: {e}")
    
    def _categorize_complexity(self, complexity: int) -> str:
        """分类复杂度"""
        if complexity <= 5:
            return 'low'
        elif complexity <= 15:
            return 'medium'
        else:
            return 'high'
    
    def generate_analysis_report(self, output_path: Path) -> bool:
        """
        生成分析报告
        
        Args:
            output_path: 输出路径
            
        Returns:
            是否生成成功
        """
        try:
            import json
            
            report = {
                'analysis_date': datetime.now().isoformat(),
                'summary': self.analysis_results.get('metrics', {}),
                'modules': self.analysis_results.get('modules', {}),
                'complexity': self.analysis_results.get('complexity', {}),
                'dependencies': self.analysis_results.get('dependencies', {}),
                'issues': self.analysis_results.get('todos', [])
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Analysis report saved to: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to generate analysis report: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            self.analysis_results.clear()
            self.logger.info("Code analyzer cleanup completed")
        except Exception as e:
            self.logger.error(f"Code analyzer cleanup failed: {e}")
