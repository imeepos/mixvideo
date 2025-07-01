"""
Shot Detection Core Module
核心业务逻辑模块
"""

from .detection import *
from .processing import *
from .export import *
from .services import *
from .performance import *

__version__ = "2.0.0"
__all__ = [
    # Detection
    "BaseDetector",
    "FrameDifferenceDetector", 
    "HistogramDetector",
    "MultiDetector",
    "ShotBoundary",
    "DetectionResult",
    
    # Processing
    "VideoProcessor",
    "VideoSegment",
    "SegmentationService",
    "AnalysisService",
    
    # Export
    "ProjectExporter",
    "FormatHandler",
    
    # Services
    "VideoService",
    "BatchService",
    "AnalysisService",

    # Performance
    "MemoryManager",
    "PerformanceMonitor",
    "CacheOptimizer",
    "ResourceManager",
]
