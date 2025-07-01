"""
API Documentation Generator
API文档生成器
"""

import json
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Type, Callable
from datetime import datetime
from loguru import logger


class APIDocConfig:
    """API文档配置"""
    
    def __init__(self):
        """初始化API文档配置"""
        self.output_format = "markdown"  # markdown, json, html
        self.include_private = False
        self.include_inherited = True
        self.include_source_links = True
        self.group_by_module = True
        self.generate_search_index = True
        self.include_examples = True
        self.include_type_hints = True


class APIDocumentationGenerator:
    """API文档生成器"""
    
    def __init__(self, config: Optional[APIDocConfig] = None):
        """
        初始化API文档生成器
        
        Args:
            config: API文档配置
        """
        self.config = config or APIDocConfig()
        self.logger = logger.bind(component="APIDocumentationGenerator")
        
        # API信息
        self.api_info = {
            'modules': {},
            'classes': {},
            'functions': {},
            'constants': {}
        }
        
        # 搜索索引
        self.search_index = []
        
        self.logger.info("API documentation generator initialized")
    
    def generate_api_docs(self, modules: List[Any], output_dir: Path) -> bool:
        """
        生成API文档
        
        Args:
            modules: 要文档化的模块列表
            output_dir: 输出目录
            
        Returns:
            是否生成成功
        """
        try:
            self.logger.info("Generating API documentation")
            
            # 创建输出目录
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 分析模块
            for module in modules:
                self._analyze_module(module)
            
            # 生成文档
            if self.config.output_format == "markdown":
                self._generate_markdown_docs(output_dir)
            elif self.config.output_format == "json":
                self._generate_json_docs(output_dir)
            elif self.config.output_format == "html":
                self._generate_html_docs(output_dir)
            
            # 生成搜索索引
            if self.config.generate_search_index:
                self._generate_search_index(output_dir)
            
            self.logger.info("API documentation generation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"API documentation generation failed: {e}")
            return False
    
    def _analyze_module(self, module: Any):
        """分析模块"""
        try:
            module_name = module.__name__
            
            module_info = {
                'name': module_name,
                'docstring': inspect.getdoc(module),
                'file': inspect.getfile(module) if hasattr(module, '__file__') else None,
                'classes': [],
                'functions': [],
                'constants': [],
                'submodules': []
            }
            
            # 获取模块成员
            for name, obj in inspect.getmembers(module):
                if name.startswith('_') and not self.config.include_private:
                    continue
                
                if inspect.isclass(obj) and obj.__module__ == module_name:
                    class_info = self._analyze_class(obj)
                    module_info['classes'].append(class_info)
                    self.api_info['classes'][f"{module_name}.{name}"] = class_info
                
                elif inspect.isfunction(obj) and obj.__module__ == module_name:
                    function_info = self._analyze_function(obj)
                    module_info['functions'].append(function_info)
                    self.api_info['functions'][f"{module_name}.{name}"] = function_info
                
                elif not inspect.ismodule(obj) and not inspect.isclass(obj) and not inspect.isfunction(obj):
                    # 常量或变量
                    constant_info = {
                        'name': name,
                        'value': repr(obj),
                        'type': type(obj).__name__,
                        'module': module_name
                    }
                    module_info['constants'].append(constant_info)
                    self.api_info['constants'][f"{module_name}.{name}"] = constant_info
            
            self.api_info['modules'][module_name] = module_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze module {module}: {e}")
    
    def _analyze_class(self, cls: Type) -> Dict[str, Any]:
        """分析类"""
        try:
            class_info = {
                'name': cls.__name__,
                'qualname': cls.__qualname__,
                'module': cls.__module__,
                'docstring': inspect.getdoc(cls),
                'bases': [base.__name__ for base in cls.__bases__ if base != object],
                'methods': [],
                'properties': [],
                'class_variables': [],
                'source_file': None,
                'source_lines': None
            }
            
            # 获取源文件信息
            try:
                class_info['source_file'] = inspect.getfile(cls)
                class_info['source_lines'] = inspect.getsourcelines(cls)[1]
            except (OSError, TypeError):
                pass
            
            # 分析类成员
            for name, obj in inspect.getmembers(cls):
                if name.startswith('_') and not self.config.include_private:
                    continue
                
                if inspect.ismethod(obj) or inspect.isfunction(obj):
                    # 检查是否为类的直接成员
                    if (not self.config.include_inherited and 
                        name not in cls.__dict__):
                        continue
                    
                    method_info = self._analyze_method(obj, cls)
                    class_info['methods'].append(method_info)
                
                elif isinstance(obj, property):
                    property_info = self._analyze_property(obj, name)
                    class_info['properties'].append(property_info)
                
                elif (not callable(obj) and not name.startswith('_') and 
                      name in cls.__dict__):
                    # 类变量
                    var_info = {
                        'name': name,
                        'value': repr(obj),
                        'type': type(obj).__name__
                    }
                    class_info['class_variables'].append(var_info)
            
            return class_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze class {cls}: {e}")
            return {'name': cls.__name__, 'error': str(e)}
    
    def _analyze_method(self, method: Callable, cls: Type) -> Dict[str, Any]:
        """分析方法"""
        try:
            method_info = {
                'name': method.__name__,
                'docstring': inspect.getdoc(method),
                'signature': str(inspect.signature(method)),
                'is_classmethod': isinstance(inspect.getattr_static(cls, method.__name__), classmethod),
                'is_staticmethod': isinstance(inspect.getattr_static(cls, method.__name__), staticmethod),
                'is_property': isinstance(inspect.getattr_static(cls, method.__name__), property),
                'parameters': [],
                'returns': None,
                'raises': [],
                'examples': []
            }
            
            # 分析签名
            try:
                sig = inspect.signature(method)
                for param_name, param in sig.parameters.items():
                    param_info = {
                        'name': param_name,
                        'annotation': str(param.annotation) if param.annotation != param.empty else None,
                        'default': str(param.default) if param.default != param.empty else None,
                        'kind': param.kind.name
                    }
                    method_info['parameters'].append(param_info)
                
                if sig.return_annotation != sig.empty:
                    method_info['returns'] = str(sig.return_annotation)
            
            except (ValueError, TypeError):
                pass
            
            # 解析文档字符串中的信息
            if method_info['docstring']:
                parsed_doc = self._parse_docstring(method_info['docstring'])
                method_info.update(parsed_doc)
            
            return method_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze method {method}: {e}")
            return {'name': method.__name__, 'error': str(e)}
    
    def _analyze_function(self, func: Callable) -> Dict[str, Any]:
        """分析函数"""
        try:
            function_info = {
                'name': func.__name__,
                'qualname': func.__qualname__,
                'module': func.__module__,
                'docstring': inspect.getdoc(func),
                'signature': str(inspect.signature(func)),
                'parameters': [],
                'returns': None,
                'raises': [],
                'examples': [],
                'source_file': None,
                'source_lines': None
            }
            
            # 获取源文件信息
            try:
                function_info['source_file'] = inspect.getfile(func)
                function_info['source_lines'] = inspect.getsourcelines(func)[1]
            except (OSError, TypeError):
                pass
            
            # 分析签名
            try:
                sig = inspect.signature(func)
                for param_name, param in sig.parameters.items():
                    param_info = {
                        'name': param_name,
                        'annotation': str(param.annotation) if param.annotation != param.empty else None,
                        'default': str(param.default) if param.default != param.empty else None,
                        'kind': param.kind.name
                    }
                    function_info['parameters'].append(param_info)
                
                if sig.return_annotation != sig.empty:
                    function_info['returns'] = str(sig.return_annotation)
            
            except (ValueError, TypeError):
                pass
            
            # 解析文档字符串
            if function_info['docstring']:
                parsed_doc = self._parse_docstring(function_info['docstring'])
                function_info.update(parsed_doc)
            
            return function_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze function {func}: {e}")
            return {'name': func.__name__, 'error': str(e)}
    
    def _analyze_property(self, prop: property, name: str) -> Dict[str, Any]:
        """分析属性"""
        try:
            property_info = {
                'name': name,
                'docstring': inspect.getdoc(prop),
                'getter': prop.fget is not None,
                'setter': prop.fset is not None,
                'deleter': prop.fdel is not None,
                'type': None
            }
            
            # 尝试获取类型注解
            if prop.fget:
                try:
                    sig = inspect.signature(prop.fget)
                    if sig.return_annotation != sig.empty:
                        property_info['type'] = str(sig.return_annotation)
                except (ValueError, TypeError):
                    pass
            
            return property_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze property {name}: {e}")
            return {'name': name, 'error': str(e)}
    
    def _parse_docstring(self, docstring: str) -> Dict[str, Any]:
        """解析文档字符串"""
        try:
            parsed = {
                'description': '',
                'parameters_doc': {},
                'returns_doc': '',
                'raises_doc': [],
                'examples_doc': []
            }
            
            lines = docstring.split('\n')
            current_section = 'description'
            current_content = []
            
            for line in lines:
                line = line.strip()
                
                if line.lower().startswith('args:') or line.lower().startswith('parameters:'):
                    if current_content:
                        parsed[current_section] = '\n'.join(current_content).strip()
                        current_content = []
                    current_section = 'parameters_doc'
                    continue
                
                elif line.lower().startswith('returns:'):
                    if current_content:
                        parsed[current_section] = '\n'.join(current_content).strip()
                        current_content = []
                    current_section = 'returns_doc'
                    continue
                
                elif line.lower().startswith('raises:') or line.lower().startswith('throws:'):
                    if current_content:
                        parsed[current_section] = '\n'.join(current_content).strip()
                        current_content = []
                    current_section = 'raises_doc'
                    continue
                
                elif line.lower().startswith('example:') or line.lower().startswith('examples:'):
                    if current_content:
                        parsed[current_section] = '\n'.join(current_content).strip()
                        current_content = []
                    current_section = 'examples_doc'
                    continue
                
                current_content.append(line)
            
            # 处理最后一个部分
            if current_content:
                parsed[current_section] = '\n'.join(current_content).strip()
            
            return parsed
            
        except Exception as e:
            self.logger.error(f"Failed to parse docstring: {e}")
            return {}
    
    def _generate_markdown_docs(self, output_dir: Path):
        """生成Markdown文档"""
        try:
            # 为每个模块生成文档
            for module_name, module_info in self.api_info['modules'].items():
                self._generate_module_markdown(module_name, module_info, output_dir)
            
            # 生成索引
            self._generate_markdown_index(output_dir)
            
        except Exception as e:
            self.logger.error(f"Markdown documentation generation failed: {e}")
    
    def _generate_module_markdown(self, module_name: str, module_info: Dict[str, Any], output_dir: Path):
        """生成模块Markdown文档"""
        try:
            content = []
            
            # 模块标题
            content.append(f"# {module_name}")
            content.append("")
            
            # 模块描述
            if module_info.get('docstring'):
                content.append(module_info['docstring'])
                content.append("")
            
            # 类
            if module_info.get('classes'):
                content.append("## Classes")
                content.append("")
                
                for class_info in module_info['classes']:
                    content.extend(self._format_class_markdown(class_info))
                    content.append("")
            
            # 函数
            if module_info.get('functions'):
                content.append("## Functions")
                content.append("")
                
                for function_info in module_info['functions']:
                    content.extend(self._format_function_markdown(function_info))
                    content.append("")
            
            # 常量
            if module_info.get('constants'):
                content.append("## Constants")
                content.append("")
                
                for constant_info in module_info['constants']:
                    content.append(f"### {constant_info['name']}")
                    content.append(f"**Type:** `{constant_info['type']}`")
                    content.append(f"**Value:** `{constant_info['value']}`")
                    content.append("")
            
            # 保存文件
            filename = f"{module_name.replace('.', '_')}.md"
            output_file = output_dir / filename
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            self.logger.debug(f"Generated markdown doc: {output_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate module markdown for {module_name}: {e}")
    
    def _format_class_markdown(self, class_info: Dict[str, Any]) -> List[str]:
        """格式化类的Markdown"""
        content = []
        
        # 类标题
        content.append(f"### {class_info['name']}")
        content.append("")
        
        # 继承信息
        if class_info.get('bases'):
            bases_str = ', '.join(class_info['bases'])
            content.append(f"**Inherits from:** {bases_str}")
            content.append("")
        
        # 类描述
        if class_info.get('docstring'):
            content.append(class_info['docstring'])
            content.append("")
        
        # 方法
        if class_info.get('methods'):
            content.append("#### Methods")
            content.append("")
            
            for method_info in class_info['methods']:
                content.extend(self._format_method_markdown(method_info))
                content.append("")
        
        # 属性
        if class_info.get('properties'):
            content.append("#### Properties")
            content.append("")
            
            for prop_info in class_info['properties']:
                content.append(f"##### {prop_info['name']}")
                if prop_info.get('type'):
                    content.append(f"**Type:** `{prop_info['type']}`")
                if prop_info.get('docstring'):
                    content.append(prop_info['docstring'])
                content.append("")
        
        return content
    
    def _format_function_markdown(self, function_info: Dict[str, Any]) -> List[str]:
        """格式化函数的Markdown"""
        content = []
        
        # 函数标题
        content.append(f"### {function_info['name']}")
        content.append("")
        
        # 签名
        content.append("```python")
        content.append(f"{function_info['name']}{function_info['signature']}")
        content.append("```")
        content.append("")
        
        # 描述
        if function_info.get('docstring'):
            content.append(function_info['docstring'])
            content.append("")
        
        # 参数
        if function_info.get('parameters'):
            content.append("**Parameters:**")
            content.append("")
            for param in function_info['parameters']:
                param_line = f"- **{param['name']}"
                if param.get('annotation'):
                    param_line += f" ({param['annotation']})"
                param_line += "**"
                if param.get('default'):
                    param_line += f" = `{param['default']}`"
                content.append(param_line)
            content.append("")
        
        # 返回值
        if function_info.get('returns'):
            content.append(f"**Returns:** `{function_info['returns']}`")
            content.append("")
        
        return content
    
    def _format_method_markdown(self, method_info: Dict[str, Any]) -> List[str]:
        """格式化方法的Markdown"""
        content = []
        
        # 方法标题
        method_title = f"##### {method_info['name']}"
        if method_info.get('is_classmethod'):
            method_title += " (classmethod)"
        elif method_info.get('is_staticmethod'):
            method_title += " (staticmethod)"
        elif method_info.get('is_property'):
            method_title += " (property)"
        
        content.append(method_title)
        content.append("")
        
        # 签名
        content.append("```python")
        content.append(f"{method_info['name']}{method_info['signature']}")
        content.append("```")
        content.append("")
        
        # 描述
        if method_info.get('docstring'):
            content.append(method_info['docstring'])
            content.append("")
        
        return content
    
    def _generate_markdown_index(self, output_dir: Path):
        """生成Markdown索引"""
        try:
            content = []
            content.append("# API Reference")
            content.append("")
            content.append("## Modules")
            content.append("")
            
            for module_name in sorted(self.api_info['modules'].keys()):
                filename = f"{module_name.replace('.', '_')}.md"
                content.append(f"- [{module_name}]({filename})")
            
            content.append("")
            
            # 保存索引
            index_file = output_dir / "index.md"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
        except Exception as e:
            self.logger.error(f"Failed to generate markdown index: {e}")
    
    def _generate_json_docs(self, output_dir: Path):
        """生成JSON文档"""
        try:
            # 保存完整API信息
            api_file = output_dir / "api.json"
            with open(api_file, 'w', encoding='utf-8') as f:
                json.dump(self.api_info, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info("JSON API documentation generated")
            
        except Exception as e:
            self.logger.error(f"JSON documentation generation failed: {e}")
    
    def _generate_html_docs(self, output_dir: Path):
        """生成HTML文档"""
        try:
            # 这里可以实现HTML文档生成
            # 可以使用模板引擎如Jinja2
            self.logger.info("HTML documentation generation not implemented")
            
        except Exception as e:
            self.logger.error(f"HTML documentation generation failed: {e}")
    
    def _generate_search_index(self, output_dir: Path):
        """生成搜索索引"""
        try:
            search_index = []
            
            # 为所有API项目创建搜索条目
            for module_name, module_info in self.api_info['modules'].items():
                # 模块条目
                search_index.append({
                    'type': 'module',
                    'name': module_name,
                    'title': module_name,
                    'description': module_info.get('docstring', ''),
                    'url': f"{module_name.replace('.', '_')}.md"
                })
                
                # 类条目
                for class_info in module_info.get('classes', []):
                    search_index.append({
                        'type': 'class',
                        'name': class_info['name'],
                        'title': f"{module_name}.{class_info['name']}",
                        'description': class_info.get('docstring', ''),
                        'url': f"{module_name.replace('.', '_')}.md#{class_info['name'].lower()}"
                    })
                
                # 函数条目
                for function_info in module_info.get('functions', []):
                    search_index.append({
                        'type': 'function',
                        'name': function_info['name'],
                        'title': f"{module_name}.{function_info['name']}",
                        'description': function_info.get('docstring', ''),
                        'url': f"{module_name.replace('.', '_')}.md#{function_info['name'].lower()}"
                    })
            
            # 保存搜索索引
            search_file = output_dir / "search_index.json"
            with open(search_file, 'w', encoding='utf-8') as f:
                json.dump(search_index, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Search index generated")
            
        except Exception as e:
            self.logger.error(f"Search index generation failed: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.api_info.clear()
            self.search_index.clear()
            self.logger.info("API documentation generator cleanup completed")
        except Exception as e:
            self.logger.error(f"API documentation generator cleanup failed: {e}")
