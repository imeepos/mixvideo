"""
检测算法模块
"""

from .base import BaseDetector, MultiDetector, ShotBoundary, DetectionResult
from .frame_diff import FrameDifferenceDetector, EnhancedFrameDifferenceDetector
from .histogram import HistogramDetector, MultiChannelHistogramDetector, AdaptiveHistogramDetector

__all__ = [
    'BaseDetector',
    'MultiDetector', 
    'ShotBoundary',
    'DetectionResult',
    'FrameDifferenceDetector',
    'EnhancedFrameDifferenceDetector',
    'HistogramDetector',
    'MultiChannelHistogramDetector',
    'AdaptiveHistogramDetector'
]
