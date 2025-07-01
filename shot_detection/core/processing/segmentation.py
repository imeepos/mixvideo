"""
Video Segmentation Module
视频分割模块
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from loguru import logger

from ..detection.base import ShotBoundary


@dataclass
class VideoSegment:
    """视频片段"""
    index: int
    start_time: float
    end_time: float
    start_frame: int
    end_frame: int
    duration: float
    confidence: float
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.duration == 0:
            self.duration = self.end_time - self.start_time


class SegmentationService:
    """分割服务"""
    
    def __init__(self):
        """初始化分割服务"""
        self.logger = logger.bind(component="SegmentationService")
    
    def create_segments(self, boundaries: List[ShotBoundary], 
                       video_info: Dict[str, Any]) -> List[VideoSegment]:
        """
        根据边界创建视频片段
        
        Args:
            boundaries: 镜头边界列表
            video_info: 视频信息
            
        Returns:
            视频片段列表
        """
        segments = []
        
        if not boundaries:
            # 如果没有边界，返回整个视频作为一个片段
            segment = VideoSegment(
                index=0,
                start_time=0.0,
                end_time=video_info.get('duration', 0.0),
                start_frame=0,
                end_frame=video_info.get('frame_count', 0) - 1,
                duration=video_info.get('duration', 0.0),
                confidence=1.0
            )
            segments.append(segment)
            return segments
        
        # 确保边界按时间排序
        sorted_boundaries = sorted(boundaries, key=lambda x: x.timestamp)
        
        # 添加开始和结束边界
        if sorted_boundaries[0].timestamp > 0:
            start_boundary = ShotBoundary(
                frame_number=0,
                timestamp=0.0,
                confidence=1.0,
                boundary_type='start'
            )
            sorted_boundaries.insert(0, start_boundary)
        
        video_duration = video_info.get('duration', 0.0)
        if sorted_boundaries[-1].timestamp < video_duration:
            end_boundary = ShotBoundary(
                frame_number=video_info.get('frame_count', 0) - 1,
                timestamp=video_duration,
                confidence=1.0,
                boundary_type='end'
            )
            sorted_boundaries.append(end_boundary)
        
        # 创建片段
        for i in range(len(sorted_boundaries) - 1):
            start_boundary = sorted_boundaries[i]
            end_boundary = sorted_boundaries[i + 1]
            
            segment = VideoSegment(
                index=i,
                start_time=start_boundary.timestamp,
                end_time=end_boundary.timestamp,
                start_frame=start_boundary.frame_number,
                end_frame=end_boundary.frame_number,
                duration=end_boundary.timestamp - start_boundary.timestamp,
                confidence=min(start_boundary.confidence, end_boundary.confidence),
                metadata={
                    'start_boundary_type': start_boundary.boundary_type,
                    'end_boundary_type': end_boundary.boundary_type
                }
            )
            
            segments.append(segment)
        
        self.logger.info(f"Created {len(segments)} segments from {len(boundaries)} boundaries")
        return segments
    
    def filter_segments(self, segments: List[VideoSegment], 
                       min_duration: float = 1.0,
                       max_duration: float = 300.0) -> List[VideoSegment]:
        """
        过滤片段
        
        Args:
            segments: 原始片段列表
            min_duration: 最小时长
            max_duration: 最大时长
            
        Returns:
            过滤后的片段列表
        """
        filtered_segments = []
        
        for segment in segments:
            if min_duration <= segment.duration <= max_duration:
                filtered_segments.append(segment)
            else:
                self.logger.debug(f"Filtered out segment {segment.index}: "
                                f"duration={segment.duration:.2f}s")
        
        self.logger.info(f"Filtered segments: {len(filtered_segments)}/{len(segments)} kept")
        return filtered_segments
    
    def merge_short_segments(self, segments: List[VideoSegment],
                           min_duration: float = 1.0) -> List[VideoSegment]:
        """
        合并短片段
        
        Args:
            segments: 原始片段列表
            min_duration: 最小时长阈值
            
        Returns:
            合并后的片段列表
        """
        if not segments:
            return []
        
        merged_segments = []
        current_segment = segments[0]
        
        for next_segment in segments[1:]:
            if current_segment.duration < min_duration:
                # 合并短片段
                merged_segment = VideoSegment(
                    index=current_segment.index,
                    start_time=current_segment.start_time,
                    end_time=next_segment.end_time,
                    start_frame=current_segment.start_frame,
                    end_frame=next_segment.end_frame,
                    duration=next_segment.end_time - current_segment.start_time,
                    confidence=min(current_segment.confidence, next_segment.confidence),
                    metadata={
                        'merged': True,
                        'original_segments': [current_segment.index, next_segment.index]
                    }
                )
                current_segment = merged_segment
            else:
                merged_segments.append(current_segment)
                current_segment = next_segment
        
        # 添加最后一个片段
        merged_segments.append(current_segment)
        
        self.logger.info(f"Merged segments: {len(segments)} -> {len(merged_segments)}")
        return merged_segments
    
    def get_segment_statistics(self, segments: List[VideoSegment]) -> Dict[str, Any]:
        """
        获取片段统计信息
        
        Args:
            segments: 片段列表
            
        Returns:
            统计信息字典
        """
        if not segments:
            return {
                'count': 0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'min_duration': 0.0,
                'max_duration': 0.0
            }
        
        durations = [s.duration for s in segments]
        total_duration = sum(durations)
        
        return {
            'count': len(segments),
            'total_duration': total_duration,
            'avg_duration': total_duration / len(segments),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'confidence_avg': sum(s.confidence for s in segments) / len(segments)
        }
