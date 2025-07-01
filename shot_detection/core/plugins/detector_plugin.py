"""
Detector Plugin Base Class
检测器插件基类
"""

from abc import abstractmethod
from typing import Dict, Any, List, Optional
from .base_plugin import BasePlugin


class DetectorPlugin(BasePlugin):
    """检测器插件基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        初始化检测器插件
        
        Args:
            name: 插件名称
            version: 插件版本
        """
        super().__init__(name, version)
        self.plugin_type = "detector"
        
        # 检测参数
        self.parameters = {}
        
        # 支持的视频格式
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    
    @abstractmethod
    def detect_shots(self, video_path: str) -> Dict[str, Any]:
        """
        检测视频中的镜头边界
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            检测结果字典，包含边界信息
        """
        pass
    
    @abstractmethod
    def get_algorithm_name(self) -> str:
        """
        获取算法名称
        
        Returns:
            算法名称
        """
        pass
    
    def set_parameter(self, name: str, value: Any):
        """
        设置检测参数
        
        Args:
            name: 参数名称
            value: 参数值
        """
        self.parameters[name] = value
        self.logger.debug(f"Parameter set: {name} = {value}")
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """
        获取检测参数
        
        Args:
            name: 参数名称
            default: 默认值
            
        Returns:
            参数值
        """
        return self.parameters.get(name, default)
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        获取所有参数
        
        Returns:
            参数字典
        """
        return self.parameters.copy()
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        """
        获取参数模式定义
        
        Returns:
            参数模式字典
        """
        return {
            'threshold': {
                'type': 'float',
                'default': 0.5,
                'min': 0.0,
                'max': 1.0,
                'description': 'Detection threshold'
            },
            'min_shot_duration': {
                'type': 'float',
                'default': 1.0,
                'min': 0.1,
                'max': 10.0,
                'description': 'Minimum shot duration in seconds'
            }
        }
    
    def validate_parameters(self) -> List[str]:
        """
        验证参数有效性
        
        Returns:
            错误信息列表
        """
        errors = []
        schema = self.get_parameter_schema()
        
        for param_name, param_config in schema.items():
            if param_name in self.parameters:
                value = self.parameters[param_name]
                param_type = param_config.get('type')
                
                # 类型检查
                if param_type == 'float' and not isinstance(value, (int, float)):
                    errors.append(f"Parameter '{param_name}' must be a number")
                elif param_type == 'int' and not isinstance(value, int):
                    errors.append(f"Parameter '{param_name}' must be an integer")
                elif param_type == 'str' and not isinstance(value, str):
                    errors.append(f"Parameter '{param_name}' must be a string")
                
                # 范围检查
                if isinstance(value, (int, float)):
                    if 'min' in param_config and value < param_config['min']:
                        errors.append(f"Parameter '{param_name}' must be >= {param_config['min']}")
                    if 'max' in param_config and value > param_config['max']:
                        errors.append(f"Parameter '{param_name}' must be <= {param_config['max']}")
        
        return errors
    
    def is_video_supported(self, video_path: str) -> bool:
        """
        检查是否支持该视频格式
        
        Args:
            video_path: 视频路径
            
        Returns:
            是否支持
        """
        from pathlib import Path
        
        file_ext = Path(video_path).suffix.lower()
        return file_ext in self.supported_formats
    
    def get_detection_info(self) -> Dict[str, Any]:
        """
        获取检测器信息
        
        Returns:
            检测器信息字典
        """
        return {
            'algorithm_name': self.get_algorithm_name(),
            'supported_formats': self.supported_formats,
            'parameters': self.get_parameters(),
            'parameter_schema': self.get_parameter_schema()
        }
    
    def preprocess_video(self, video_path: str) -> Optional[str]:
        """
        预处理视频（可选实现）
        
        Args:
            video_path: 视频路径
            
        Returns:
            预处理后的视频路径，如果不需要预处理则返回None
        """
        return None
    
    def postprocess_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        后处理检测结果（可选实现）
        
        Args:
            results: 原始检测结果
            
        Returns:
            后处理后的结果
        """
        return results
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        获取性能指标（可选实现）
        
        Returns:
            性能指标字典
        """
        return {
            'processing_time': 0.0,
            'memory_usage': 0,
            'accuracy': 0.0
        }


class FrameDifferenceDetector(DetectorPlugin):
    """帧差检测器示例实现"""
    
    def __init__(self):
        super().__init__("Frame Difference Detector", "1.0.0")
        self.description = "基于帧差的镜头边界检测算法"
        
        # 设置默认参数
        self.set_parameter('threshold', 0.5)
        self.set_parameter('min_shot_duration', 1.0)
    
    def get_algorithm_name(self) -> str:
        return "frame_difference"
    
    def detect_shots(self, video_path: str) -> Dict[str, Any]:
        """实现帧差检测算法"""
        try:
            if not self.is_video_supported(video_path):
                return {
                    'success': False,
                    'error': f'Unsupported video format: {video_path}'
                }
            
            # 验证参数
            errors = self.validate_parameters()
            if errors:
                return {
                    'success': False,
                    'error': f'Parameter validation failed: {", ".join(errors)}'
                }
            
            # 这里实现实际的检测算法
            # 为了示例，返回模拟结果
            boundaries = [
                {'frame_number': 0, 'timestamp': 0.0, 'confidence': 1.0},
                {'frame_number': 300, 'timestamp': 10.0, 'confidence': 0.8},
                {'frame_number': 600, 'timestamp': 20.0, 'confidence': 0.9},
                {'frame_number': 900, 'timestamp': 30.0, 'confidence': 0.7}
            ]
            
            results = {
                'success': True,
                'algorithm': self.get_algorithm_name(),
                'boundaries': boundaries,
                'parameters': self.get_parameters(),
                'video_path': video_path
            }
            
            return self.postprocess_results(results)
            
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class HistogramDetector(DetectorPlugin):
    """直方图检测器示例实现"""
    
    def __init__(self):
        super().__init__("Histogram Detector", "1.0.0")
        self.description = "基于颜色直方图的镜头边界检测算法"
        
        # 设置默认参数
        self.set_parameter('threshold', 0.3)
        self.set_parameter('min_shot_duration', 0.5)
        self.set_parameter('histogram_bins', 256)
    
    def get_algorithm_name(self) -> str:
        return "histogram"
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        schema = super().get_parameter_schema()
        schema['histogram_bins'] = {
            'type': 'int',
            'default': 256,
            'min': 16,
            'max': 512,
            'description': 'Number of histogram bins'
        }
        return schema
    
    def detect_shots(self, video_path: str) -> Dict[str, Any]:
        """实现直方图检测算法"""
        try:
            if not self.is_video_supported(video_path):
                return {
                    'success': False,
                    'error': f'Unsupported video format: {video_path}'
                }
            
            # 验证参数
            errors = self.validate_parameters()
            if errors:
                return {
                    'success': False,
                    'error': f'Parameter validation failed: {", ".join(errors)}'
                }
            
            # 这里实现实际的检测算法
            # 为了示例，返回模拟结果
            boundaries = [
                {'frame_number': 0, 'timestamp': 0.0, 'confidence': 1.0},
                {'frame_number': 450, 'timestamp': 15.0, 'confidence': 0.85},
                {'frame_number': 750, 'timestamp': 25.0, 'confidence': 0.92},
                {'frame_number': 1050, 'timestamp': 35.0, 'confidence': 0.78}
            ]
            
            results = {
                'success': True,
                'algorithm': self.get_algorithm_name(),
                'boundaries': boundaries,
                'parameters': self.get_parameters(),
                'video_path': video_path
            }
            
            return self.postprocess_results(results)
            
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
