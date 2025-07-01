"""
Detection Module
镜头检测算法模块
"""

from .base import BaseDetector, ShotBoundary, DetectionResult
from .frame_diff import FrameDifferenceDetector, EnhancedFrameDifferenceDetector
from .histogram import HistogramDetector, MultiChannelHistogramDetector, AdaptiveHistogramDetector
from .multi_detector import MultiDetector

__all__ = [
    "BaseDetector",
    "ShotBoundary", 
    "DetectionResult",
    "FrameDifferenceDetector",
    "EnhancedFrameDifferenceDetector",
    "HistogramDetector",
    "MultiChannelHistogramDetector", 
    "AdaptiveHistogramDetector",
    "MultiDetector",
]
