"""
Plugin Interface Definitions
插件接口定义
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum


class PluginType(Enum):
    """插件类型枚举"""
    DETECTOR = "detector"
    PROCESSOR = "processor"
    EXPORTER = "exporter"
    IMPORTER = "importer"
    FILTER = "filter"
    ANALYZER = "analyzer"
    VISUALIZER = "visualizer"
    UTILITY = "utility"


class PluginStatus(Enum):
    """插件状态枚举"""
    UNKNOWN = "unknown"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"


class PluginInterface(ABC):
    """插件接口基类"""
    
    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """插件唯一标识符"""
        pass
    
    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """插件名称"""
        pass
    
    @property
    @abstractmethod
    def plugin_version(self) -> str:
        """插件版本"""
        pass
    
    @property
    @abstractmethod
    def plugin_type(self) -> PluginType:
        """插件类型"""
        pass
    
    @property
    @abstractmethod
    def plugin_description(self) -> str:
        """插件描述"""
        pass
    
    @property
    @abstractmethod
    def plugin_author(self) -> str:
        """插件作者"""
        pass
    
    @property
    def plugin_dependencies(self) -> List[str]:
        """插件依赖列表"""
        return []
    
    @property
    def plugin_config_schema(self) -> Optional[Dict[str, Any]]:
        """插件配置模式"""
        return None
    
    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        初始化插件
        
        Args:
            config: 插件配置
            
        Returns:
            是否初始化成功
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """
        清理插件资源
        
        Returns:
            是否清理成功
        """
        pass
    
    def get_status(self) -> PluginStatus:
        """获取插件状态"""
        return PluginStatus.UNKNOWN
    
    def get_info(self) -> Dict[str, Any]:
        """获取插件信息"""
        return {
            'id': self.plugin_id,
            'name': self.plugin_name,
            'version': self.plugin_version,
            'type': self.plugin_type.value,
            'description': self.plugin_description,
            'author': self.plugin_author,
            'dependencies': self.plugin_dependencies,
            'status': self.get_status().value
        }


class DetectorInterface(PluginInterface):
    """检测器插件接口"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.DETECTOR
    
    @abstractmethod
    def detect_boundaries(self, video_path: str, **kwargs) -> Dict[str, Any]:
        """
        检测镜头边界
        
        Args:
            video_path: 视频文件路径
            **kwargs: 其他参数
            
        Returns:
            检测结果
        """
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取检测参数"""
        return {}
    
    def set_parameters(self, parameters: Dict[str, Any]) -> bool:
        """设置检测参数"""
        return True


class ProcessorInterface(PluginInterface):
    """处理器插件接口"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.PROCESSOR
    
    @abstractmethod
    def process_video(self, video_path: str, **kwargs) -> Dict[str, Any]:
        """
        处理视频
        
        Args:
            video_path: 视频文件路径
            **kwargs: 其他参数
            
        Returns:
            处理结果
        """
        pass


class ExporterInterface(PluginInterface):
    """导出器插件接口"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.EXPORTER
    
    @abstractmethod
    def export_results(self, results: Dict[str, Any], output_path: str, **kwargs) -> bool:
        """
        导出结果
        
        Args:
            results: 检测结果
            output_path: 输出路径
            **kwargs: 其他参数
            
        Returns:
            是否导出成功
        """
        pass
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的格式"""
        return []


class ImporterInterface(PluginInterface):
    """导入器插件接口"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.IMPORTER
    
    @abstractmethod
    def import_results(self, input_path: str, **kwargs) -> Dict[str, Any]:
        """
        导入结果
        
        Args:
            input_path: 输入路径
            **kwargs: 其他参数
            
        Returns:
            导入的结果
        """
        pass
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的格式"""
        return []


class FilterInterface(PluginInterface):
    """过滤器插件接口"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.FILTER
    
    @abstractmethod
    def filter_results(self, results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        过滤结果
        
        Args:
            results: 原始结果
            **kwargs: 过滤参数
            
        Returns:
            过滤后的结果
        """
        pass


class AnalyzerInterface(PluginInterface):
    """分析器插件接口"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.ANALYZER
    
    @abstractmethod
    def analyze_results(self, results: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        分析结果
        
        Args:
            results: 检测结果
            **kwargs: 分析参数
            
        Returns:
            分析结果
        """
        pass


class VisualizerInterface(PluginInterface):
    """可视化插件接口"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.VISUALIZER
    
    @abstractmethod
    def visualize_results(self, results: Dict[str, Any], **kwargs) -> Any:
        """
        可视化结果
        
        Args:
            results: 检测结果
            **kwargs: 可视化参数
            
        Returns:
            可视化对象
        """
        pass


class UtilityInterface(PluginInterface):
    """工具插件接口"""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.UTILITY
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        执行工具功能
        
        Args:
            **kwargs: 执行参数
            
        Returns:
            执行结果
        """
        pass
