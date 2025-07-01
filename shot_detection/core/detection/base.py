"""
镜头检测算法基类
定义所有检测算法的通用接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import cv2
from dataclasses import dataclass
from loguru import logger


@dataclass
class ShotBoundary:
    """镜头边界信息"""
    frame_number: int
    timestamp: float
    confidence: float
    boundary_type: str = 'cut'  # cut, fade, dissolve
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DetectionResult:
    """检测结果"""
    boundaries: List[ShotBoundary]
    algorithm_name: str
    processing_time: float
    frame_count: int
    confidence_scores: List[float]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseDetector(ABC):
    """镜头检测算法基类"""
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.config = kwargs
        self.is_initialized = False
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        self.logger = logger.bind(detector=self.name)
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化检测器"""
        pass
    
    @abstractmethod
    def detect_shots(self, video_path: str, **kwargs) -> DetectionResult:
        """检测镜头边界"""
        pass
    
    @abstractmethod
    def process_frame_pair(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """处理帧对，返回相似度分数"""
        pass
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """预处理帧"""
        # 默认预处理：转换为RGB并调整大小
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 可以在子类中重写以添加特定的预处理步骤
        return frame
    
    def postprocess_boundaries(self, boundaries: List[ShotBoundary], 
                             min_scene_length: int = 15) -> List[ShotBoundary]:
        """后处理边界，移除过短的镜头"""
        if not boundaries:
            return boundaries
        
        filtered_boundaries = []
        last_boundary = 0
        
        for boundary in boundaries:
            if boundary.frame_number - last_boundary >= min_scene_length:
                filtered_boundaries.append(boundary)
                last_boundary = boundary.frame_number
        
        return filtered_boundaries
    
    def calculate_adaptive_threshold(self, scores: List[float], 
                                   percentile: float = 85) -> float:
        """计算自适应阈值"""
        if not scores:
            return 0.5
        
        return np.percentile(scores, percentile)
    
    def smooth_scores(self, scores: List[float], window_size: int = 5) -> List[float]:
        """平滑置信度分数"""
        if len(scores) < window_size:
            return scores
        
        smoothed = []
        half_window = window_size // 2
        
        for i in range(len(scores)):
            start = max(0, i - half_window)
            end = min(len(scores), i + half_window + 1)
            smoothed.append(np.mean(scores[start:end]))
        
        return smoothed
    
    def find_peaks(self, scores: List[float], threshold: float, 
                   min_distance: int = 15) -> List[int]:
        """找到分数峰值"""
        from scipy.signal import find_peaks
        
        peaks, properties = find_peaks(
            scores, 
            height=threshold, 
            distance=min_distance
        )
        
        return peaks.tolist()
    
    def validate_boundary(self, boundary: ShotBoundary, 
                         frame1: np.ndarray, frame2: np.ndarray) -> bool:
        """验证边界的有效性"""
        # 基础验证：检查置信度
        if boundary.confidence < 0.1:
            return False
        
        # 可以在子类中添加更复杂的验证逻辑
        return True
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            'name': self.name,
            'is_initialized': self.is_initialized,
            'config': self.config
        }
    
    def cleanup(self):
        """清理资源"""
        self.logger.info(f"Cleaning up {self.name} detector")
        self.is_initialized = False


class MultiDetector:
    """多算法检测器管理器"""
    
    def __init__(self):
        self.detectors: List[BaseDetector] = []
        self.weights: Dict[str, float] = {}
        self.logger = logger.bind(component="MultiDetector")
    
    def add_detector(self, detector: BaseDetector, weight: float = 1.0):
        """添加检测器"""
        self.detectors.append(detector)
        self.weights[detector.name] = weight
        self.logger.info(f"Added detector: {detector.name} with weight {weight}")
    
    def initialize_all(self) -> bool:
        """初始化所有检测器"""
        success_count = 0
        
        for detector in self.detectors:
            try:
                if detector.initialize():
                    success_count += 1
                    self.logger.info(f"Successfully initialized {detector.name}")
                else:
                    self.logger.error(f"Failed to initialize {detector.name}")
            except Exception as e:
                self.logger.error(f"Error initializing {detector.name}: {e}")
        
        return success_count > 0
    
    def detect_shots_ensemble(self, video_path: str, **kwargs) -> DetectionResult:
        """使用集成方法检测镜头"""
        all_results = []
        
        # 运行所有检测器
        for detector in self.detectors:
            if not detector.is_initialized:
                continue
            
            try:
                result = detector.detect_shots(video_path, **kwargs)
                all_results.append(result)
                self.logger.info(f"{detector.name} found {len(result.boundaries)} boundaries")
            except Exception as e:
                self.logger.error(f"Error in {detector.name}: {e}")
        
        if not all_results:
            return DetectionResult([], "ensemble", 0.0, 0, [])
        
        # 融合结果
        fused_boundaries = self._fuse_boundaries(all_results)
        
        # 计算总处理时间
        total_time = sum(result.processing_time for result in all_results)
        
        # 获取帧数（假设所有结果的帧数相同）
        frame_count = all_results[0].frame_count if all_results else 0
        
        return DetectionResult(
            boundaries=fused_boundaries,
            algorithm_name="ensemble",
            processing_time=total_time,
            frame_count=frame_count,
            confidence_scores=[b.confidence for b in fused_boundaries]
        )
    
    def _fuse_boundaries(self, results: List[DetectionResult]) -> List[ShotBoundary]:
        """融合多个检测结果"""
        # 收集所有边界
        all_boundaries = []
        for result in results:
            weight = self.weights.get(result.algorithm_name, 1.0)
            for boundary in result.boundaries:
                # 调整置信度权重
                weighted_boundary = ShotBoundary(
                    frame_number=boundary.frame_number,
                    timestamp=boundary.timestamp,
                    confidence=boundary.confidence * weight,
                    boundary_type=boundary.boundary_type,
                    metadata={**boundary.metadata, 'source': result.algorithm_name}
                )
                all_boundaries.append(weighted_boundary)
        
        # 按帧号排序
        all_boundaries.sort(key=lambda x: x.frame_number)
        
        # 聚合相近的边界
        fused_boundaries = self._cluster_boundaries(all_boundaries)
        
        return fused_boundaries
    
    def _cluster_boundaries(self, boundaries: List[ShotBoundary], 
                          tolerance: int = 5) -> List[ShotBoundary]:
        """聚合相近的边界"""
        if not boundaries:
            return []
        
        clustered = []
        current_cluster = [boundaries[0]]
        
        for boundary in boundaries[1:]:
            # 如果当前边界与聚类中心距离小于容忍度，加入聚类
            cluster_center = current_cluster[0].frame_number
            if abs(boundary.frame_number - cluster_center) <= tolerance:
                current_cluster.append(boundary)
            else:
                # 完成当前聚类，开始新聚类
                clustered.append(self._merge_cluster(current_cluster))
                current_cluster = [boundary]
        
        # 处理最后一个聚类
        if current_cluster:
            clustered.append(self._merge_cluster(current_cluster))
        
        return clustered
    
    def _merge_cluster(self, cluster: List[ShotBoundary]) -> ShotBoundary:
        """合并聚类中的边界"""
        if len(cluster) == 1:
            return cluster[0]
        
        # 使用加权平均计算最终位置和置信度
        total_weight = sum(b.confidence for b in cluster)
        
        if total_weight == 0:
            # 如果所有置信度都是0，使用简单平均
            avg_frame = int(np.mean([b.frame_number for b in cluster]))
            avg_timestamp = np.mean([b.timestamp for b in cluster])
            avg_confidence = np.mean([b.confidence for b in cluster])
        else:
            # 加权平均
            avg_frame = int(sum(b.frame_number * b.confidence for b in cluster) / total_weight)
            avg_timestamp = sum(b.timestamp * b.confidence for b in cluster) / total_weight
            avg_confidence = total_weight / len(cluster)
        
        # 合并元数据
        merged_metadata = {
            'sources': [b.metadata.get('source', 'unknown') for b in cluster],
            'cluster_size': len(cluster)
        }
        
        return ShotBoundary(
            frame_number=avg_frame,
            timestamp=avg_timestamp,
            confidence=avg_confidence,
            boundary_type=cluster[0].boundary_type,
            metadata=merged_metadata
        )
    
    def cleanup_all(self):
        """清理所有检测器"""
        for detector in self.detectors:
            detector.cleanup()
        
        self.detectors.clear()
        self.weights.clear()
        self.logger.info("All detectors cleaned up")
