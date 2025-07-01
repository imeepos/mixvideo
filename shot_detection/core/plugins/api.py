"""
Plugin API System
插件API系统
"""

import inspect
from typing import Dict, Any, List, Optional, Callable, Type
from abc import ABC, abstractmethod
from loguru import logger


class PluginAPI(ABC):
    """插件API基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        初始化插件API
        
        Args:
            name: API名称
            version: API版本
        """
        self.name = name
        self.version = version
        self.logger = logger.bind(component=f"PluginAPI-{name}")
        
        # API方法注册表
        self._methods = {}
        self._events = {}
        
        # 自动注册API方法
        self._register_api_methods()
    
    def _register_api_methods(self):
        """自动注册API方法"""
        try:
            for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
                if hasattr(method, '_api_method'):
                    method_info = {
                        'name': name,
                        'method': method,
                        'description': getattr(method, '_api_description', ''),
                        'parameters': self._get_method_parameters(method),
                        'returns': getattr(method, '_api_returns', None)
                    }
                    self._methods[name] = method_info
                    
        except Exception as e:
            self.logger.error(f"Failed to register API methods: {e}")
    
    def _get_method_parameters(self, method: Callable) -> Dict[str, Any]:
        """获取方法参数信息"""
        try:
            sig = inspect.signature(method)
            parameters = {}
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                    
                param_info = {
                    'name': param_name,
                    'type': param.annotation if param.annotation != param.empty else None,
                    'default': param.default if param.default != param.empty else None,
                    'required': param.default == param.empty
                }
                parameters[param_name] = param_info
            
            return parameters
            
        except Exception as e:
            self.logger.error(f"Failed to get method parameters: {e}")
            return {}
    
    def get_api_info(self) -> Dict[str, Any]:
        """获取API信息"""
        return {
            'name': self.name,
            'version': self.version,
            'methods': {name: {
                'description': info['description'],
                'parameters': info['parameters'],
                'returns': info['returns']
            } for name, info in self._methods.items()},
            'events': list(self._events.keys())
        }
    
    def call_method(self, method_name: str, **kwargs) -> Any:
        """
        调用API方法
        
        Args:
            method_name: 方法名称
            **kwargs: 方法参数
            
        Returns:
            方法返回值
        """
        try:
            if method_name not in self._methods:
                raise ValueError(f"Unknown API method: {method_name}")
            
            method_info = self._methods[method_name]
            method = method_info['method']
            
            # 验证参数
            self._validate_parameters(method_name, kwargs)
            
            # 调用方法
            return method(**kwargs)
            
        except Exception as e:
            self.logger.error(f"API method call failed: {method_name} - {e}")
            raise
    
    def _validate_parameters(self, method_name: str, kwargs: Dict[str, Any]):
        """验证方法参数"""
        try:
            method_info = self._methods[method_name]
            parameters = method_info['parameters']
            
            # 检查必需参数
            for param_name, param_info in parameters.items():
                if param_info['required'] and param_name not in kwargs:
                    raise ValueError(f"Missing required parameter: {param_name}")
            
            # 检查未知参数
            for param_name in kwargs:
                if param_name not in parameters:
                    raise ValueError(f"Unknown parameter: {param_name}")
                    
        except Exception as e:
            self.logger.error(f"Parameter validation failed: {e}")
            raise
    
    def emit_event(self, event_name: str, data: Any = None):
        """
        发出事件
        
        Args:
            event_name: 事件名称
            data: 事件数据
        """
        try:
            if event_name in self._events:
                for callback in self._events[event_name]:
                    try:
                        callback(data)
                    except Exception as e:
                        self.logger.error(f"Event callback failed: {e}")
                        
        except Exception as e:
            self.logger.error(f"Failed to emit event: {e}")
    
    def register_event_handler(self, event_name: str, callback: Callable):
        """
        注册事件处理器
        
        Args:
            event_name: 事件名称
            callback: 回调函数
        """
        try:
            if event_name not in self._events:
                self._events[event_name] = []
            
            self._events[event_name].append(callback)
            
        except Exception as e:
            self.logger.error(f"Failed to register event handler: {e}")


def api_method(description: str = "", returns: str = None):
    """API方法装饰器"""
    def decorator(func):
        func._api_method = True
        func._api_description = description
        func._api_returns = returns
        return func
    return decorator


class DetectionAPI(PluginAPI):
    """检测API"""
    
    def __init__(self):
        super().__init__("detection", "1.0.0")
        self._detector = None
    
    def set_detector(self, detector):
        """设置检测器"""
        self._detector = detector
    
    @api_method("检测视频中的镜头边界", "检测结果字典")
    def detect_shots(self, video_path: str, algorithm: str = "frame_difference", **params) -> Dict[str, Any]:
        """
        检测镜头边界
        
        Args:
            video_path: 视频路径
            algorithm: 检测算法
            **params: 算法参数
            
        Returns:
            检测结果
        """
        if not self._detector:
            raise RuntimeError("Detector not set")
        
        # 设置算法和参数
        self._detector.set_algorithm(algorithm)
        for key, value in params.items():
            self._detector.set_parameter(key, value)
        
        # 执行检测
        results = self._detector.detect_shots(video_path)
        
        # 发出事件
        self.emit_event("detection_completed", {
            'video_path': video_path,
            'algorithm': algorithm,
            'results': results
        })
        
        return results
    
    @api_method("获取可用的检测算法列表", "算法列表")
    def get_algorithms(self) -> List[str]:
        """获取可用算法"""
        if not self._detector:
            return []
        
        return self._detector.get_available_algorithms()
    
    @api_method("获取算法参数", "参数字典")
    def get_algorithm_parameters(self, algorithm: str) -> Dict[str, Any]:
        """获取算法参数"""
        if not self._detector:
            return {}
        
        return self._detector.get_algorithm_parameters(algorithm)


class ProcessingAPI(PluginAPI):
    """处理API"""
    
    def __init__(self):
        super().__init__("processing", "1.0.0")
        self._processor = None
    
    def set_processor(self, processor):
        """设置处理器"""
        self._processor = processor
    
    @api_method("处理视频文件", "处理结果")
    def process_video(self, video_path: str, output_path: str = None, **options) -> Dict[str, Any]:
        """
        处理视频文件
        
        Args:
            video_path: 输入视频路径
            output_path: 输出路径
            **options: 处理选项
            
        Returns:
            处理结果
        """
        if not self._processor:
            raise RuntimeError("Processor not set")
        
        results = self._processor.process_video(video_path, output_path, **options)
        
        self.emit_event("processing_completed", {
            'video_path': video_path,
            'output_path': output_path,
            'results': results
        })
        
        return results
    
    @api_method("获取视频信息", "视频信息字典")
    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """获取视频信息"""
        if not self._processor:
            raise RuntimeError("Processor not set")
        
        return self._processor.get_video_info(video_path)


class ExportAPI(PluginAPI):
    """导出API"""
    
    def __init__(self):
        super().__init__("export", "1.0.0")
        self._exporters = {}
    
    def register_exporter(self, format_name: str, exporter):
        """注册导出器"""
        self._exporters[format_name] = exporter
    
    @api_method("导出检测结果", "导出结果")
    def export_results(self, results: Dict[str, Any], output_path: str, format_name: str = "json") -> bool:
        """
        导出检测结果
        
        Args:
            results: 检测结果
            output_path: 输出路径
            format_name: 导出格式
            
        Returns:
            是否导出成功
        """
        if format_name not in self._exporters:
            raise ValueError(f"Unknown export format: {format_name}")
        
        exporter = self._exporters[format_name]
        success = exporter.export(results, output_path)
        
        self.emit_event("export_completed", {
            'format': format_name,
            'output_path': output_path,
            'success': success
        })
        
        return success
    
    @api_method("获取支持的导出格式", "格式列表")
    def get_supported_formats(self) -> List[str]:
        """获取支持的导出格式"""
        return list(self._exporters.keys())


class APIRegistry:
    """API注册表"""
    
    def __init__(self):
        """初始化API注册表"""
        self.logger = logger.bind(component="APIRegistry")
        self._apis = {}
        
        # 注册默认API
        self._register_default_apis()
    
    def _register_default_apis(self):
        """注册默认API"""
        try:
            self.register_api(DetectionAPI())
            self.register_api(ProcessingAPI())
            self.register_api(ExportAPI())
            
        except Exception as e:
            self.logger.error(f"Failed to register default APIs: {e}")
    
    def register_api(self, api: PluginAPI):
        """
        注册API
        
        Args:
            api: API实例
        """
        try:
            self._apis[api.name] = api
            self.logger.info(f"API registered: {api.name} v{api.version}")
            
        except Exception as e:
            self.logger.error(f"Failed to register API: {e}")
    
    def unregister_api(self, api_name: str):
        """
        注销API
        
        Args:
            api_name: API名称
        """
        try:
            if api_name in self._apis:
                del self._apis[api_name]
                self.logger.info(f"API unregistered: {api_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to unregister API: {e}")
    
    def get_api(self, api_name: str) -> Optional[PluginAPI]:
        """
        获取API
        
        Args:
            api_name: API名称
            
        Returns:
            API实例
        """
        return self._apis.get(api_name)
    
    def get_all_apis(self) -> Dict[str, PluginAPI]:
        """获取所有API"""
        return self._apis.copy()
    
    def call_api_method(self, api_name: str, method_name: str, **kwargs) -> Any:
        """
        调用API方法
        
        Args:
            api_name: API名称
            method_name: 方法名称
            **kwargs: 方法参数
            
        Returns:
            方法返回值
        """
        try:
            api = self.get_api(api_name)
            if not api:
                raise ValueError(f"Unknown API: {api_name}")
            
            return api.call_method(method_name, **kwargs)
            
        except Exception as e:
            self.logger.error(f"API method call failed: {api_name}.{method_name} - {e}")
            raise
    
    def get_api_documentation(self) -> Dict[str, Any]:
        """获取API文档"""
        try:
            documentation = {}
            
            for api_name, api in self._apis.items():
                documentation[api_name] = api.get_api_info()
            
            return documentation
            
        except Exception as e:
            self.logger.error(f"Failed to get API documentation: {e}")
            return {}
    
    def cleanup(self):
        """清理资源"""
        try:
            self._apis.clear()
            self.logger.info("API registry cleanup completed")
        except Exception as e:
            self.logger.error(f"API registry cleanup failed: {e}")
