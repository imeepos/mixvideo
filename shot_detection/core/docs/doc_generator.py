"""
Documentation Generator
文档生成器
"""

import os
import ast
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from loguru import logger


class DocConfig:
    """文档配置"""
    
    def __init__(self):
        """初始化文档配置"""
        self.output_dir = Path("./docs")
        self.source_dir = Path("./shot_detection")
        self.template_dir = Path("./templates")
        self.include_private = False
        self.include_tests = False
        self.format = "markdown"  # markdown, html, rst
        self.language = "en"
        self.theme = "default"
        self.generate_api_docs = True
        self.generate_user_guide = True
        self.generate_examples = True
        self.auto_generate_toc = True


class DocumentationGenerator:
    """文档生成器"""
    
    def __init__(self, config: Optional[DocConfig] = None):
        """
        初始化文档生成器
        
        Args:
            config: 文档配置
        """
        self.config = config or DocConfig()
        self.logger = logger.bind(component="DocumentationGenerator")
        
        # 文档数据
        self.modules_info = {}
        self.classes_info = {}
        self.functions_info = {}
        
        # 模板
        self.templates = {}
        
        # 加载模板
        self._load_templates()
        
        self.logger.info("Documentation generator initialized")
    
    def _load_templates(self):
        """加载文档模板"""
        try:
            template_files = {
                'module': 'module_template.md',
                'class': 'class_template.md',
                'function': 'function_template.md',
                'index': 'index_template.md',
                'api': 'api_template.md'
            }
            
            for template_name, template_file in template_files.items():
                template_path = self.config.template_dir / template_file
                
                if template_path.exists():
                    with open(template_path, 'r', encoding='utf-8') as f:
                        self.templates[template_name] = f.read()
                else:
                    # 使用默认模板
                    self.templates[template_name] = self._get_default_template(template_name)
            
            self.logger.info("Documentation templates loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to load templates: {e}")
            # 使用默认模板
            for template_name in ['module', 'class', 'function', 'index', 'api']:
                self.templates[template_name] = self._get_default_template(template_name)
    
    def _get_default_template(self, template_name: str) -> str:
        """获取默认模板"""
        templates = {
            'module': """# {module_name}

{description}

## Classes

{classes}

## Functions

{functions}

## Constants

{constants}
""",
            'class': """## {class_name}

{description}

### Methods

{methods}

### Properties

{properties}
""",
            'function': """### {function_name}

{description}

**Parameters:**
{parameters}

**Returns:**
{returns}

**Example:**
```python
{example}
```
""",
            'index': """# {project_name} Documentation

{description}

## Table of Contents

{toc}

## Quick Start

{quick_start}
""",
            'api': """# API Reference

{api_content}
"""
        }
        
        return templates.get(template_name, "# {title}\n\n{content}")
    
    def generate_documentation(self) -> bool:
        """
        生成完整文档
        
        Returns:
            是否生成成功
        """
        try:
            self.logger.info("Starting documentation generation")
            
            # 创建输出目录
            self.config.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 分析源代码
            self._analyze_source_code()
            
            # 生成API文档
            if self.config.generate_api_docs:
                self._generate_api_documentation()
            
            # 生成用户指南
            if self.config.generate_user_guide:
                self._generate_user_guide()
            
            # 生成示例
            if self.config.generate_examples:
                self._generate_examples()
            
            # 生成索引
            self._generate_index()
            
            self.logger.info("Documentation generation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Documentation generation failed: {e}")
            return False
    
    def _analyze_source_code(self):
        """分析源代码"""
        try:
            self.logger.info("Analyzing source code")
            
            # 遍历源代码目录
            for py_file in self.config.source_dir.rglob("*.py"):
                if self._should_include_file(py_file):
                    self._analyze_python_file(py_file)
            
            self.logger.info(f"Analyzed {len(self.modules_info)} modules")
            
        except Exception as e:
            self.logger.error(f"Source code analysis failed: {e}")
    
    def _should_include_file(self, file_path: Path) -> bool:
        """检查是否应该包含文件"""
        # 跳过__pycache__目录
        if '__pycache__' in str(file_path):
            return False
        
        # 跳过测试文件（如果配置不包含）
        if not self.config.include_tests and 'test' in str(file_path):
            return False
        
        return True
    
    def _analyze_python_file(self, file_path: Path):
        """分析Python文件"""
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
                'docstring': ast.get_docstring(tree),
                'classes': [],
                'functions': [],
                'constants': []
            }
            
            # 分析AST节点
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node)
                    module_info['classes'].append(class_info)
                    self.classes_info[f"{module_name}.{node.name}"] = class_info
                
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_') or self.config.include_private:
                        function_info = self._analyze_function(node)
                        module_info['functions'].append(function_info)
                        self.functions_info[f"{module_name}.{node.name}"] = function_info
                
                elif isinstance(node, ast.Assign):
                    # 分析常量
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            constant_info = {
                                'name': target.id,
                                'value': self._get_node_value(node.value),
                                'line_number': node.lineno
                            }
                            module_info['constants'].append(constant_info)
            
            self.modules_info[module_name] = module_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze file {file_path}: {e}")
    
    def _get_module_name(self, file_path: Path) -> str:
        """获取模块名称"""
        try:
            relative_path = file_path.relative_to(self.config.source_dir)
            module_parts = list(relative_path.parts[:-1])  # 排除文件名
            
            if relative_path.stem != '__init__':
                module_parts.append(relative_path.stem)
            
            return '.'.join(module_parts) if module_parts else 'root'
            
        except Exception:
            return file_path.stem
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """分析类"""
        try:
            class_info = {
                'name': node.name,
                'docstring': ast.get_docstring(node),
                'line_number': node.lineno,
                'bases': [self._get_node_name(base) for base in node.bases],
                'methods': [],
                'properties': []
            }
            
            # 分析类成员
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if not item.name.startswith('_') or self.config.include_private:
                        method_info = self._analyze_function(item, is_method=True)
                        
                        if self._is_property(item):
                            class_info['properties'].append(method_info)
                        else:
                            class_info['methods'].append(method_info)
            
            return class_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze class {node.name}: {e}")
            return {'name': node.name, 'error': str(e)}
    
    def _analyze_function(self, node: ast.FunctionDef, is_method: bool = False) -> Dict[str, Any]:
        """分析函数"""
        try:
            function_info = {
                'name': node.name,
                'docstring': ast.get_docstring(node),
                'line_number': node.lineno,
                'is_method': is_method,
                'parameters': [],
                'returns': None,
                'decorators': [self._get_node_name(dec) for dec in node.decorator_list]
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
            
            return function_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze function {node.name}: {e}")
            return {'name': node.name, 'error': str(e)}
    
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
            else:
                return "..."
        except Exception:
            return "..."
    
    def _is_property(self, node: ast.FunctionDef) -> bool:
        """检查是否为属性"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'property':
                return True
        return False
    
    def _generate_api_documentation(self):
        """生成API文档"""
        try:
            self.logger.info("Generating API documentation")
            
            api_dir = self.config.output_dir / "api"
            api_dir.mkdir(exist_ok=True)
            
            # 为每个模块生成文档
            for module_name, module_info in self.modules_info.items():
                self._generate_module_doc(module_name, module_info, api_dir)
            
            # 生成API索引
            self._generate_api_index(api_dir)
            
        except Exception as e:
            self.logger.error(f"API documentation generation failed: {e}")
    
    def _generate_module_doc(self, module_name: str, module_info: Dict[str, Any], output_dir: Path):
        """生成模块文档"""
        try:
            # 准备模板数据
            template_data = {
                'module_name': module_name,
                'description': module_info.get('docstring', 'No description available.'),
                'classes': self._format_classes(module_info.get('classes', [])),
                'functions': self._format_functions(module_info.get('functions', [])),
                'constants': self._format_constants(module_info.get('constants', []))
            }
            
            # 渲染模板
            content = self._render_template('module', template_data)
            
            # 保存文件
            output_file = output_dir / f"{module_name.replace('.', '_')}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.debug(f"Generated module doc: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate module doc for {module_name}: {e}")
    
    def _format_classes(self, classes: List[Dict[str, Any]]) -> str:
        """格式化类信息"""
        if not classes:
            return "No classes defined."
        
        formatted = []
        for class_info in classes:
            class_doc = self._render_template('class', {
                'class_name': class_info['name'],
                'description': class_info.get('docstring', 'No description available.'),
                'methods': self._format_methods(class_info.get('methods', [])),
                'properties': self._format_properties(class_info.get('properties', []))
            })
            formatted.append(class_doc)
        
        return '\n\n'.join(formatted)
    
    def _format_functions(self, functions: List[Dict[str, Any]]) -> str:
        """格式化函数信息"""
        if not functions:
            return "No functions defined."
        
        formatted = []
        for func_info in functions:
            func_doc = self._render_template('function', {
                'function_name': func_info['name'],
                'description': func_info.get('docstring', 'No description available.'),
                'parameters': self._format_parameters(func_info.get('parameters', [])),
                'returns': func_info.get('returns', 'None'),
                'example': self._generate_function_example(func_info)
            })
            formatted.append(func_doc)
        
        return '\n\n'.join(formatted)
    
    def _format_methods(self, methods: List[Dict[str, Any]]) -> str:
        """格式化方法信息"""
        return self._format_functions(methods)
    
    def _format_properties(self, properties: List[Dict[str, Any]]) -> str:
        """格式化属性信息"""
        if not properties:
            return "No properties defined."
        
        formatted = []
        for prop_info in properties:
            formatted.append(f"- **{prop_info['name']}**: {prop_info.get('docstring', 'No description')}")
        
        return '\n'.join(formatted)
    
    def _format_constants(self, constants: List[Dict[str, Any]]) -> str:
        """格式化常量信息"""
        if not constants:
            return "No constants defined."
        
        formatted = []
        for const_info in constants:
            formatted.append(f"- **{const_info['name']}** = `{const_info['value']}`")
        
        return '\n'.join(formatted)
    
    def _format_parameters(self, parameters: List[Dict[str, Any]]) -> str:
        """格式化参数信息"""
        if not parameters:
            return "No parameters."
        
        formatted = []
        for param_info in parameters:
            param_line = f"- **{param_info['name']}"
            if param_info.get('annotation'):
                param_line += f" ({param_info['annotation']})"
            param_line += "**: Description needed"
            formatted.append(param_line)
        
        return '\n'.join(formatted)
    
    def _generate_function_example(self, func_info: Dict[str, Any]) -> str:
        """生成函数示例"""
        func_name = func_info['name']
        params = func_info.get('parameters', [])
        
        if not params:
            return f"{func_name}()"
        
        param_names = [p['name'] for p in params if p['name'] != 'self']
        param_str = ', '.join(param_names)
        
        return f"{func_name}({param_str})"
    
    def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """渲染模板"""
        try:
            template = self.templates.get(template_name, "{content}")
            
            # 简单的模板替换
            for key, value in data.items():
                placeholder = f"{{{key}}}"
                template = template.replace(placeholder, str(value))
            
            return template
            
        except Exception as e:
            self.logger.error(f"Template rendering failed: {e}")
            return f"# {data.get('title', 'Documentation')}\n\nError rendering template."
    
    def _generate_api_index(self, api_dir: Path):
        """生成API索引"""
        try:
            index_content = "# API Reference\n\n"
            index_content += "## Modules\n\n"
            
            for module_name in sorted(self.modules_info.keys()):
                file_name = f"{module_name.replace('.', '_')}.md"
                index_content += f"- [{module_name}]({file_name})\n"
            
            index_file = api_dir / "index.md"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            self.logger.info("API index generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate API index: {e}")
    
    def _generate_user_guide(self):
        """生成用户指南"""
        try:
            self.logger.info("Generating user guide")
            
            guide_dir = self.config.output_dir / "guide"
            guide_dir.mkdir(exist_ok=True)
            
            # 生成基本指南页面
            guide_pages = {
                'installation.md': self._generate_installation_guide(),
                'quickstart.md': self._generate_quickstart_guide(),
                'configuration.md': self._generate_configuration_guide(),
                'examples.md': self._generate_examples_guide()
            }
            
            for filename, content in guide_pages.items():
                guide_file = guide_dir / filename
                with open(guide_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            
        except Exception as e:
            self.logger.error(f"User guide generation failed: {e}")
    
    def _generate_installation_guide(self) -> str:
        """生成安装指南"""
        return """# Installation Guide

## Requirements

- Python 3.8 or higher
- OpenCV
- NumPy

## Installation

### Using pip

```bash
pip install shot-detection
```

### From source

```bash
git clone https://github.com/shot-detection/shot-detection.git
cd shot-detection
pip install -e .
```

## Verification

```python
import shot_detection
print(shot_detection.__version__)
```
"""
    
    def _generate_quickstart_guide(self) -> str:
        """生成快速开始指南"""
        return """# Quick Start Guide

## Basic Usage

```python
from shot_detection import ShotDetector

# Create detector
detector = ShotDetector()

# Detect shots in video
results = detector.detect_shots('path/to/video.mp4')

# Print results
for boundary in results['boundaries']:
    print(f"Shot boundary at {boundary['timestamp']}s")
```

## Configuration

```python
# Configure detection parameters
detector.set_parameter('threshold', 0.5)
detector.set_parameter('min_shot_duration', 1.0)

# Use different algorithm
detector.set_algorithm('histogram')
```
"""
    
    def _generate_configuration_guide(self) -> str:
        """生成配置指南"""
        return """# Configuration Guide

## Detection Parameters

### Threshold
Controls sensitivity of shot detection.
- Range: 0.0 - 1.0
- Default: 0.5
- Lower values = more sensitive

### Minimum Shot Duration
Minimum duration for a valid shot.
- Range: 0.1 - 10.0 seconds
- Default: 1.0 seconds

## Algorithms

### Frame Difference
Fast algorithm based on frame-to-frame differences.

### Histogram
More accurate algorithm using color histograms.

### Optical Flow
Advanced algorithm using motion vectors.
"""
    
    def _generate_examples_guide(self) -> str:
        """生成示例指南"""
        return """# Examples

## Basic Detection

```python
from shot_detection import ShotDetector

detector = ShotDetector()
results = detector.detect_shots('video.mp4')
```

## Batch Processing

```python
import os
from shot_detection import ShotDetector

detector = ShotDetector()

for filename in os.listdir('videos/'):
    if filename.endswith('.mp4'):
        results = detector.detect_shots(f'videos/{filename}')
        print(f"{filename}: {len(results['boundaries'])} shots")
```

## Export Results

```python
from shot_detection import ShotDetector, JSONExporter

detector = ShotDetector()
exporter = JSONExporter()

results = detector.detect_shots('video.mp4')
exporter.export(results, 'output.json')
```
"""
    
    def _generate_examples(self):
        """生成示例"""
        try:
            self.logger.info("Generating examples")
            
            examples_dir = self.config.output_dir / "examples"
            examples_dir.mkdir(exist_ok=True)
            
            # 生成示例文件
            examples = {
                'basic_detection.py': self._generate_basic_example(),
                'advanced_detection.py': self._generate_advanced_example(),
                'batch_processing.py': self._generate_batch_example()
            }
            
            for filename, content in examples.items():
                example_file = examples_dir / filename
                with open(example_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            
        except Exception as e:
            self.logger.error(f"Examples generation failed: {e}")
    
    def _generate_basic_example(self) -> str:
        """生成基础示例"""
        return '''#!/usr/bin/env python3
"""
Basic Shot Detection Example
基础镜头检测示例
"""

from shot_detection import ShotDetector

def main():
    # Create detector
    detector = ShotDetector()
    
    # Detect shots
    video_path = 'path/to/your/video.mp4'
    results = detector.detect_shots(video_path)
    
    # Print results
    if results['success']:
        print(f"Detected {len(results['boundaries'])} shot boundaries:")
        for i, boundary in enumerate(results['boundaries']):
            print(f"  {i+1}. Frame {boundary['frame_number']} at {boundary['timestamp']:.2f}s")
    else:
        print("Detection failed:", results.get('error', 'Unknown error'))

if __name__ == '__main__':
    main()
'''
    
    def _generate_advanced_example(self) -> str:
        """生成高级示例"""
        return '''#!/usr/bin/env python3
"""
Advanced Shot Detection Example
高级镜头检测示例
"""

from shot_detection import ShotDetector, JSONExporter

def main():
    # Create detector with custom configuration
    detector = ShotDetector()
    
    # Configure detection parameters
    detector.set_algorithm('histogram')
    detector.set_parameter('threshold', 0.3)
    detector.set_parameter('min_shot_duration', 0.5)
    
    # Detect shots
    video_path = 'path/to/your/video.mp4'
    results = detector.detect_shots(video_path)
    
    if results['success']:
        # Export results
        exporter = JSONExporter()
        exporter.export(results, 'shot_boundaries.json')
        
        # Print statistics
        boundaries = results['boundaries']
        if len(boundaries) > 1:
            durations = []
            for i in range(len(boundaries) - 1):
                duration = boundaries[i+1]['timestamp'] - boundaries[i]['timestamp']
                durations.append(duration)
            
            avg_duration = sum(durations) / len(durations)
            print(f"Average shot duration: {avg_duration:.2f}s")
            print(f"Shortest shot: {min(durations):.2f}s")
            print(f"Longest shot: {max(durations):.2f}s")

if __name__ == '__main__':
    main()
'''
    
    def _generate_batch_example(self) -> str:
        """生成批处理示例"""
        return '''#!/usr/bin/env python3
"""
Batch Processing Example
批处理示例
"""

import os
from pathlib import Path
from shot_detection import ShotDetector, CSVExporter

def main():
    # Setup
    input_dir = Path('input_videos')
    output_dir = Path('output_results')
    output_dir.mkdir(exist_ok=True)
    
    detector = ShotDetector()
    exporter = CSVExporter()
    
    # Process all videos
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    
    for video_file in input_dir.iterdir():
        if video_file.suffix.lower() in video_extensions:
            print(f"Processing: {video_file.name}")
            
            # Detect shots
            results = detector.detect_shots(str(video_file))
            
            if results['success']:
                # Export results
                output_file = output_dir / f"{video_file.stem}_shots.csv"
                exporter.export(results, str(output_file))
                
                print(f"  Found {len(results['boundaries'])} shots")
            else:
                print(f"  Failed: {results.get('error', 'Unknown error')}")

if __name__ == '__main__':
    main()
'''
    
    def _generate_index(self):
        """生成主索引"""
        try:
            self.logger.info("Generating main index")
            
            # 生成目录
            toc_items = []
            
            if self.config.generate_user_guide:
                toc_items.extend([
                    "- [Installation Guide](guide/installation.md)",
                    "- [Quick Start](guide/quickstart.md)",
                    "- [Configuration](guide/configuration.md)",
                    "- [Examples](guide/examples.md)"
                ])
            
            if self.config.generate_api_docs:
                toc_items.append("- [API Reference](api/index.md)")
            
            if self.config.generate_examples:
                toc_items.append("- [Code Examples](examples/)")
            
            # 渲染索引模板
            index_content = self._render_template('index', {
                'project_name': 'Shot Detection',
                'description': 'Advanced video shot detection and analysis toolkit.',
                'toc': '\n'.join(toc_items),
                'quick_start': 'See the [Quick Start Guide](guide/quickstart.md) to get started.'
            })
            
            # 保存索引文件
            index_file = self.config.output_dir / "index.md"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            # 同时创建README.md
            readme_file = self.config.output_dir / "README.md"
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            self.logger.info("Main index generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate main index: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.modules_info.clear()
            self.classes_info.clear()
            self.functions_info.clear()
            self.templates.clear()
            self.logger.info("Documentation generator cleanup completed")
        except Exception as e:
            self.logger.error(f"Documentation generator cleanup failed: {e}")
