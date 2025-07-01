"""
Multi-Detector Module
多检测器融合模块
"""

from typing import List, Dict, Any
import numpy as np
from loguru import logger

from .base import BaseDetector, DetectionResult, ShotBoundary


class MultiDetector:
    """多检测器融合类"""
    
    def __init__(self, detectors: List[BaseDetector], fusion_weights: Dict[str, float] = None):
        """
        初始化多检测器
        
        Args:
            detectors: 检测器列表
            fusion_weights: 融合权重字典
        """
        self.detectors = detectors
        self.fusion_weights = fusion_weights or {}
        self.logger = logger.bind(component="MultiDetector")
        
        # 设置默认权重
        if not self.fusion_weights:
            weight = 1.0 / len(detectors)
            self.fusion_weights = {detector.name: weight for detector in detectors}
    
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
    
    def detect_shots_fusion(self, video_path: str, **kwargs) -> DetectionResult:
        """
        使用多检测器融合检测镜头边界
        
        Args:
            video_path: 视频文件路径
            **kwargs: 其他参数
            
        Returns:
            融合后的检测结果
        """
        self.logger.info(f"Starting multi-detector fusion for {video_path}")
        
        # 运行所有检测器
        results = []
        for detector in self.detectors:
            try:
                result = detector.detect_shots(video_path, **kwargs)
                results.append(result)
                self.logger.info(f"{detector.name} detected {len(result.boundaries)} boundaries")
            except Exception as e:
                self.logger.error(f"Error in {detector.name}: {e}")
                continue
        
        if not results:
            self.logger.error("No detector produced valid results")
            return DetectionResult(
                boundaries=[],
                algorithm_name="multi_detector_fusion",
                processing_time=0.0,
                frame_count=0,
                confidence_scores=[]
            )
        
        # 融合结果
        fused_result = self._fuse_results(results)
        
        self.logger.info(f"Fusion complete: {len(fused_result.boundaries)} final boundaries")
        return fused_result
    
    def _fuse_results(self, results: List[DetectionResult]) -> DetectionResult:
        """
        融合多个检测结果
        
        Args:
            results: 检测结果列表
            
        Returns:
            融合后的结果
        """
        if not results:
            return DetectionResult(
                boundaries=[],
                algorithm_name="multi_detector_fusion",
                processing_time=0.0,
                frame_count=0,
                confidence_scores=[]
            )
        
        # 收集所有边界
        all_boundaries = []
        total_processing_time = 0.0
        max_frame_count = 0
        
        for result in results:
            all_boundaries.extend(result.boundaries)
            total_processing_time += result.processing_time
            max_frame_count = max(max_frame_count, result.frame_count)
        
        # 按时间戳排序
        all_boundaries.sort(key=lambda x: x.timestamp)
        
        # 聚类相近的边界
        clustered_boundaries = self._cluster_boundaries(all_boundaries)
        
        # 计算融合置信度
        final_boundaries = self._calculate_fusion_confidence(clustered_boundaries)
        
        return DetectionResult(
            boundaries=final_boundaries,
            algorithm_name="multi_detector_fusion",
            processing_time=total_processing_time,
            frame_count=max_frame_count,
            confidence_scores=[b.confidence for b in final_boundaries],
            metadata={
                'num_detectors': len(results),
                'fusion_weights': self.fusion_weights,
                'original_boundary_count': len(all_boundaries)
            }
        )
    
    def _cluster_boundaries(self, boundaries: List[ShotBoundary], 
                           time_threshold: float = 1.0) -> List[List[ShotBoundary]]:
        """
        聚类相近的边界
        
        Args:
            boundaries: 边界列表
            time_threshold: 时间阈值（秒）
            
        Returns:
            聚类后的边界组
        """
        if not boundaries:
            return []
        
        clusters = []
        current_cluster = [boundaries[0]]
        
        for boundary in boundaries[1:]:
            # 如果与当前聚类的最后一个边界时间差小于阈值，加入当前聚类
            if boundary.timestamp - current_cluster[-1].timestamp <= time_threshold:
                current_cluster.append(boundary)
            else:
                # 否则开始新的聚类
                clusters.append(current_cluster)
                current_cluster = [boundary]
        
        # 添加最后一个聚类
        if current_cluster:
            clusters.append(current_cluster)
        
        return clusters
    
    def _calculate_fusion_confidence(self, clustered_boundaries: List[List[ShotBoundary]]) -> List[ShotBoundary]:
        """
        计算融合置信度
        
        Args:
            clustered_boundaries: 聚类后的边界组
            
        Returns:
            融合后的边界列表
        """
        final_boundaries = []
        
        for cluster in clustered_boundaries:
            if not cluster:
                continue
            
            # 计算聚类中心时间戳
            avg_timestamp = sum(b.timestamp for b in cluster) / len(cluster)
            avg_frame = int(sum(b.frame_number for b in cluster) / len(cluster))
            
            # 计算加权置信度
            weighted_confidence = 0.0
            total_weight = 0.0
            
            for boundary in cluster:
                detector_name = boundary.metadata.get('algorithm', 'unknown')
                weight = self.fusion_weights.get(detector_name, 0.0)
                weighted_confidence += boundary.confidence * weight
                total_weight += weight
            
            if total_weight > 0:
                weighted_confidence /= total_weight
            
            # 创建融合边界
            fused_boundary = ShotBoundary(
                frame_number=avg_frame,
                timestamp=avg_timestamp,
                confidence=weighted_confidence,
                boundary_type='cut',
                metadata={
                    'algorithm': 'multi_detector_fusion',
                    'cluster_size': len(cluster),
                    'contributing_detectors': [b.metadata.get('algorithm', 'unknown') for b in cluster],
                    'original_confidences': [b.confidence for b in cluster]
                }
            )
            
            final_boundaries.append(fused_boundary)
        
        return final_boundaries
    
    def cleanup(self):
        """清理所有检测器"""
        for detector in self.detectors:
            try:
                detector.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up {detector.name}: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        metrics = {
            'num_detectors': len(self.detectors),
            'fusion_weights': self.fusion_weights,
            'detectors': []
        }
        
        for detector in self.detectors:
            try:
                detector_metrics = detector.get_performance_metrics()
                metrics['detectors'].append(detector_metrics)
            except Exception as e:
                self.logger.error(f"Error getting metrics from {detector.name}: {e}")
        
        return metrics
