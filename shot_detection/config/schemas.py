"""
Configuration Schemas
配置模式定义
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class DetectionConfig:
    """检测配置"""
    default_detector: str = "multi_detector"
    frame_difference: Dict[str, Any] = None
    histogram: Dict[str, Any] = None
    multi_detector: Dict[str, Any] = None
    common: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.frame_difference is None:
            self.frame_difference = {}
        if self.histogram is None:
            self.histogram = {}
        if self.multi_detector is None:
            self.multi_detector = {}
        if self.common is None:
            self.common = {}


@dataclass
class ProcessingConfig:
    """处理配置"""
    output: Dict[str, Any] = None
    segmentation: Dict[str, Any] = None
    preview: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.output is None:
            self.output = {}
        if self.segmentation is None:
            self.segmentation = {}
        if self.preview is None:
            self.preview = {}


@dataclass
class GUIConfig:
    """GUI配置"""
    window: Dict[str, Any] = None
    theme: Dict[str, Any] = None
    interface: Dict[str, Any] = None
    performance: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.window is None:
            self.window = {}
        if self.theme is None:
            self.theme = {}
        if self.interface is None:
            self.interface = {}
        if self.performance is None:
            self.performance = {}


@dataclass
class ConfigSchema:
    """完整配置模式"""
    app: Dict[str, Any] = None
    detection: DetectionConfig = None
    processing: ProcessingConfig = None
    gui: GUIConfig = None
    jianying: Dict[str, Any] = None
    logging: Dict[str, Any] = None
    performance: Dict[str, Any] = None
    advanced: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.app is None:
            self.app = {}
        if self.detection is None:
            self.detection = DetectionConfig()
        if self.processing is None:
            self.processing = ProcessingConfig()
        if self.gui is None:
            self.gui = GUIConfig()
        if self.jianying is None:
            self.jianying = {}
        if self.logging is None:
            self.logging = {}
        if self.performance is None:
            self.performance = {}
        if self.advanced is None:
            self.advanced = {}
