"""
Processor Plugin Base Class
处理器插件基类
"""

from abc import abstractmethod
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from .base_plugin import BasePlugin


class ProcessorPlugin(BasePlugin):
    """处理器插件基类"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        初始化处理器插件
        
        Args:
            name: 插件名称
            version: 插件版本
        """
        super().__init__(name, version)
        self.plugin_type = "processor"
        
        # 处理参数
        self.parameters = {}
        
        # 支持的输入格式
        self.supported_input_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        
        # 支持的输出格式
        self.supported_output_formats = ['.mp4', '.avi', '.mov']
    
    @abstractmethod
    def process(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        处理数据
        
        Args:
            input_data: 输入数据
            **kwargs: 处理参数
            
        Returns:
            处理结果字典
        """
        pass
    
    @abstractmethod
    def get_processor_type(self) -> str:
        """
        获取处理器类型
        
        Returns:
            处理器类型
        """
        pass
    
    def set_parameter(self, name: str, value: Any):
        """
        设置处理参数
        
        Args:
            name: 参数名称
            value: 参数值
        """
        self.parameters[name] = value
        self.logger.debug(f"Parameter set: {name} = {value}")
    
    def get_parameter(self, name: str, default: Any = None) -> Any:
        """
        获取处理参数
        
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
            'quality': {
                'type': 'str',
                'default': 'medium',
                'choices': ['low', 'medium', 'high'],
                'description': 'Processing quality'
            },
            'output_format': {
                'type': 'str',
                'default': 'mp4',
                'choices': ['mp4', 'avi', 'mov'],
                'description': 'Output format'
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
                
                # 选择检查
                if 'choices' in param_config and value not in param_config['choices']:
                    errors.append(f"Parameter '{param_name}' must be one of {param_config['choices']}")
                
                # 范围检查
                if isinstance(value, (int, float)):
                    if 'min' in param_config and value < param_config['min']:
                        errors.append(f"Parameter '{param_name}' must be >= {param_config['min']}")
                    if 'max' in param_config and value > param_config['max']:
                        errors.append(f"Parameter '{param_name}' must be <= {param_config['max']}")
        
        return errors
    
    def is_input_supported(self, input_path: str) -> bool:
        """
        检查是否支持该输入格式
        
        Args:
            input_path: 输入路径
            
        Returns:
            是否支持
        """
        file_ext = Path(input_path).suffix.lower()
        return file_ext in self.supported_input_formats
    
    def is_output_supported(self, output_format: str) -> bool:
        """
        检查是否支持该输出格式
        
        Args:
            output_format: 输出格式
            
        Returns:
            是否支持
        """
        if not output_format.startswith('.'):
            output_format = f'.{output_format}'
        return output_format.lower() in self.supported_output_formats
    
    def get_processor_info(self) -> Dict[str, Any]:
        """
        获取处理器信息
        
        Returns:
            处理器信息字典
        """
        return {
            'processor_type': self.get_processor_type(),
            'supported_input_formats': self.supported_input_formats,
            'supported_output_formats': self.supported_output_formats,
            'parameters': self.get_parameters(),
            'parameter_schema': self.get_parameter_schema()
        }
    
    def preprocess_input(self, input_data: Any) -> Any:
        """
        预处理输入数据（可选实现）
        
        Args:
            input_data: 输入数据
            
        Returns:
            预处理后的数据
        """
        return input_data
    
    def postprocess_output(self, output_data: Any) -> Any:
        """
        后处理输出数据（可选实现）
        
        Args:
            output_data: 输出数据
            
        Returns:
            后处理后的数据
        """
        return output_data
    
    def get_processing_progress(self) -> float:
        """
        获取处理进度（可选实现）
        
        Returns:
            进度百分比 (0.0-1.0)
        """
        return 0.0
    
    def cancel_processing(self):
        """
        取消处理（可选实现）
        """
        pass


class VideoProcessor(ProcessorPlugin):
    """视频处理器示例实现"""
    
    def __init__(self):
        super().__init__("Video Processor", "1.0.0")
        self.description = "通用视频处理器"
        
        # 设置默认参数
        self.set_parameter('quality', 'medium')
        self.set_parameter('output_format', 'mp4')
        self.set_parameter('resolution', 'original')
        self.set_parameter('fps', 'original')
    
    def get_processor_type(self) -> str:
        return "video"
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        schema = super().get_parameter_schema()
        schema.update({
            'resolution': {
                'type': 'str',
                'default': 'original',
                'choices': ['original', '720p', '1080p', '4k'],
                'description': 'Output resolution'
            },
            'fps': {
                'type': 'str',
                'default': 'original',
                'choices': ['original', '24', '30', '60'],
                'description': 'Output frame rate'
            }
        })
        return schema
    
    def process(self, input_data: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """处理视频文件"""
        try:
            input_path = str(input_data)
            
            if not self.is_input_supported(input_path):
                return {
                    'success': False,
                    'error': f'Unsupported input format: {input_path}'
                }
            
            # 验证参数
            errors = self.validate_parameters()
            if errors:
                return {
                    'success': False,
                    'error': f'Parameter validation failed: {", ".join(errors)}'
                }
            
            # 获取输出路径
            output_path = kwargs.get('output_path')
            if not output_path:
                input_file = Path(input_path)
                output_format = self.get_parameter('output_format', 'mp4')
                output_path = input_file.with_suffix(f'.processed.{output_format}')
            
            # 这里实现实际的视频处理逻辑
            # 为了示例，返回模拟结果
            
            results = {
                'success': True,
                'processor_type': self.get_processor_type(),
                'input_path': input_path,
                'output_path': str(output_path),
                'parameters': self.get_parameters(),
                'processing_time': 10.5,
                'file_size_reduction': 0.25
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Video processing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class AudioProcessor(ProcessorPlugin):
    """音频处理器示例实现"""
    
    def __init__(self):
        super().__init__("Audio Processor", "1.0.0")
        self.description = "音频提取和处理器"
        
        # 支持的输入格式（视频文件）
        self.supported_input_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        
        # 支持的输出格式（音频文件）
        self.supported_output_formats = ['.mp3', '.wav', '.aac', '.flac']
        
        # 设置默认参数
        self.set_parameter('quality', 'high')
        self.set_parameter('output_format', 'mp3')
        self.set_parameter('bitrate', '192k')
        self.set_parameter('sample_rate', '44100')
    
    def get_processor_type(self) -> str:
        return "audio"
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            'quality': {
                'type': 'str',
                'default': 'high',
                'choices': ['low', 'medium', 'high'],
                'description': 'Audio quality'
            },
            'output_format': {
                'type': 'str',
                'default': 'mp3',
                'choices': ['mp3', 'wav', 'aac', 'flac'],
                'description': 'Output audio format'
            },
            'bitrate': {
                'type': 'str',
                'default': '192k',
                'choices': ['128k', '192k', '256k', '320k'],
                'description': 'Audio bitrate'
            },
            'sample_rate': {
                'type': 'str',
                'default': '44100',
                'choices': ['22050', '44100', '48000', '96000'],
                'description': 'Audio sample rate'
            }
        }
    
    def process(self, input_data: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """从视频中提取音频"""
        try:
            input_path = str(input_data)
            
            if not self.is_input_supported(input_path):
                return {
                    'success': False,
                    'error': f'Unsupported input format: {input_path}'
                }
            
            # 验证参数
            errors = self.validate_parameters()
            if errors:
                return {
                    'success': False,
                    'error': f'Parameter validation failed: {", ".join(errors)}'
                }
            
            # 获取输出路径
            output_path = kwargs.get('output_path')
            if not output_path:
                input_file = Path(input_path)
                output_format = self.get_parameter('output_format', 'mp3')
                output_path = input_file.with_suffix(f'.{output_format}')
            
            # 这里实现实际的音频提取逻辑
            # 为了示例，返回模拟结果
            
            results = {
                'success': True,
                'processor_type': self.get_processor_type(),
                'input_path': input_path,
                'output_path': str(output_path),
                'parameters': self.get_parameters(),
                'processing_time': 5.2,
                'audio_duration': 120.5,
                'audio_channels': 2
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Audio processing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class ImageProcessor(ProcessorPlugin):
    """图像处理器示例实现"""
    
    def __init__(self):
        super().__init__("Image Processor", "1.0.0")
        self.description = "视频帧提取和图像处理器"
        
        # 支持的输入格式（视频文件）
        self.supported_input_formats = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
        
        # 支持的输出格式（图像文件）
        self.supported_output_formats = ['.jpg', '.png', '.bmp', '.tiff']
        
        # 设置默认参数
        self.set_parameter('output_format', 'jpg')
        self.set_parameter('quality', 'high')
        self.set_parameter('frame_interval', 1.0)
        self.set_parameter('max_frames', 100)
    
    def get_processor_type(self) -> str:
        return "image"
    
    def get_parameter_schema(self) -> Dict[str, Any]:
        return {
            'output_format': {
                'type': 'str',
                'default': 'jpg',
                'choices': ['jpg', 'png', 'bmp', 'tiff'],
                'description': 'Output image format'
            },
            'quality': {
                'type': 'str',
                'default': 'high',
                'choices': ['low', 'medium', 'high'],
                'description': 'Image quality'
            },
            'frame_interval': {
                'type': 'float',
                'default': 1.0,
                'min': 0.1,
                'max': 10.0,
                'description': 'Interval between extracted frames (seconds)'
            },
            'max_frames': {
                'type': 'int',
                'default': 100,
                'min': 1,
                'max': 1000,
                'description': 'Maximum number of frames to extract'
            }
        }
    
    def process(self, input_data: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """从视频中提取帧"""
        try:
            input_path = str(input_data)
            
            if not self.is_input_supported(input_path):
                return {
                    'success': False,
                    'error': f'Unsupported input format: {input_path}'
                }
            
            # 验证参数
            errors = self.validate_parameters()
            if errors:
                return {
                    'success': False,
                    'error': f'Parameter validation failed: {", ".join(errors)}'
                }
            
            # 获取输出目录
            output_dir = kwargs.get('output_dir')
            if not output_dir:
                input_file = Path(input_path)
                output_dir = input_file.parent / f"{input_file.stem}_frames"
            
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            
            # 这里实现实际的帧提取逻辑
            # 为了示例，返回模拟结果
            
            frame_interval = self.get_parameter('frame_interval', 1.0)
            max_frames = self.get_parameter('max_frames', 100)
            output_format = self.get_parameter('output_format', 'jpg')
            
            # 模拟提取的帧文件
            extracted_frames = []
            for i in range(min(max_frames, 50)):  # 模拟提取50帧
                frame_file = output_dir / f"frame_{i:06d}.{output_format}"
                extracted_frames.append(str(frame_file))
            
            results = {
                'success': True,
                'processor_type': self.get_processor_type(),
                'input_path': input_path,
                'output_dir': str(output_dir),
                'parameters': self.get_parameters(),
                'processing_time': 8.3,
                'frames_extracted': len(extracted_frames),
                'frame_files': extracted_frames
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Image processing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
