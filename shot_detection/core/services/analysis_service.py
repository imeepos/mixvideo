"""
Advanced Video Analysis Service
高级视频分析服务
"""

from typing import Dict, Any, List, Optional, Callable, Tuple
from pathlib import Path
import json
import cv2
import numpy as np
from loguru import logger
import concurrent.futures
from dataclasses import dataclass, asdict

from ..detection.base import DetectionResult
from .video_service import VideoService


@dataclass
class VideoMetrics:
    """视频指标"""
    duration: float
    frame_count: int
    fps: float
    resolution: Tuple[int, int]
    bitrate: Optional[int] = None
    file_size_mb: float = 0.0
    
    # 质量指标
    avg_brightness: float = 0.0
    avg_contrast: float = 0.0
    sharpness_score: float = 0.0
    noise_level: float = 0.0
    
    # 内容指标
    scene_complexity: float = 0.0
    motion_intensity: float = 0.0
    color_diversity: float = 0.0


@dataclass
class ShotAnalysis:
    """镜头分析结果"""
    shot_index: int
    start_time: float
    end_time: float
    duration: float
    
    # 视觉特征
    dominant_colors: List[Tuple[int, int, int]]
    avg_brightness: float
    motion_score: float
    complexity_score: float
    
    # 内容特征
    scene_type: str = "unknown"
    objects_detected: List[str] = None
    text_detected: List[str] = None
    
    def __post_init__(self):
        if self.objects_detected is None:
            self.objects_detected = []
        if self.text_detected is None:
            self.text_detected = []


class AdvancedAnalysisService:
    """高级视频分析服务"""
    
    def __init__(self, video_service: VideoService = None):
        """
        初始化高级分析服务
        
        Args:
            video_service: 视频服务实例
        """
        self.video_service = video_service
        self.logger = logger.bind(component="AdvancedAnalysisService")
        
        # 分析配置
        self.analysis_config = {
            "sample_rate": 30,  # 每30帧采样一次
            "max_samples": 100,  # 最大采样数
            "enable_object_detection": False,  # 是否启用对象检测
            "enable_text_detection": False,   # 是否启用文本检测
            "enable_face_detection": False,   # 是否启用人脸检测
        }
    
    def analyze_video_comprehensive(self, video_path: str,
                                   detection_result: Optional[DetectionResult] = None,
                                   progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict[str, Any]:
        """
        综合视频分析
        
        Args:
            video_path: 视频文件路径
            detection_result: 镜头检测结果
            progress_callback: 进度回调函数
            
        Returns:
            综合分析结果
        """
        try:
            self.logger.info(f"Starting comprehensive analysis for: {video_path}")
            
            if progress_callback:
                progress_callback(0.1, "获取视频基本信息...")
            
            # 获取基本视频指标
            video_metrics = self._extract_video_metrics(video_path)
            
            if progress_callback:
                progress_callback(0.3, "分析视频质量...")
            
            # 分析视频质量
            quality_analysis = self._analyze_video_quality(video_path)
            
            if progress_callback:
                progress_callback(0.5, "分析镜头内容...")
            
            # 分析镜头内容
            shot_analyses = []
            if detection_result:
                shot_analyses = self._analyze_shots(video_path, detection_result, progress_callback)
            
            if progress_callback:
                progress_callback(0.8, "生成分析报告...")
            
            # 生成综合报告
            analysis_report = self._generate_analysis_report(
                video_metrics, quality_analysis, shot_analyses
            )
            
            if progress_callback:
                progress_callback(1.0, "分析完成")
            
            return {
                "success": True,
                "video_path": video_path,
                "video_metrics": asdict(video_metrics),
                "quality_analysis": quality_analysis,
                "shot_analyses": [asdict(shot) for shot in shot_analyses],
                "analysis_report": analysis_report
            }
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path
            }
    
    def _extract_video_metrics(self, video_path: str) -> VideoMetrics:
        """提取视频基本指标"""
        cap = cv2.VideoCapture(video_path)
        
        try:
            # 基本信息
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # 文件大小
            file_size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            
            return VideoMetrics(
                duration=duration,
                frame_count=frame_count,
                fps=fps,
                resolution=(width, height),
                file_size_mb=file_size_mb
            )
            
        finally:
            cap.release()
    
    def _analyze_video_quality(self, video_path: str) -> Dict[str, Any]:
        """分析视频质量"""
        cap = cv2.VideoCapture(video_path)
        
        try:
            brightness_values = []
            contrast_values = []
            sharpness_values = []
            
            # 采样分析
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            sample_interval = max(1, total_frames // self.analysis_config["max_samples"])
            
            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_interval == 0:
                    # 转换为灰度图
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # 计算亮度
                    brightness = np.mean(gray)
                    brightness_values.append(brightness)
                    
                    # 计算对比度
                    contrast = np.std(gray)
                    contrast_values.append(contrast)
                    
                    # 计算清晰度（拉普拉斯方差）
                    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                    sharpness = laplacian.var()
                    sharpness_values.append(sharpness)
                
                frame_idx += 1
            
            return {
                "avg_brightness": np.mean(brightness_values) if brightness_values else 0,
                "brightness_std": np.std(brightness_values) if brightness_values else 0,
                "avg_contrast": np.mean(contrast_values) if contrast_values else 0,
                "contrast_std": np.std(contrast_values) if contrast_values else 0,
                "avg_sharpness": np.mean(sharpness_values) if sharpness_values else 0,
                "sharpness_std": np.std(sharpness_values) if sharpness_values else 0,
                "quality_score": self._calculate_quality_score(
                    brightness_values, contrast_values, sharpness_values
                )
            }
            
        finally:
            cap.release()
    
    def _calculate_quality_score(self, brightness_values: List[float],
                                contrast_values: List[float],
                                sharpness_values: List[float]) -> float:
        """计算综合质量分数"""
        if not brightness_values or not contrast_values or not sharpness_values:
            return 0.0
        
        # 归一化各项指标
        brightness_score = min(1.0, np.mean(brightness_values) / 255.0)
        contrast_score = min(1.0, np.mean(contrast_values) / 100.0)
        sharpness_score = min(1.0, np.mean(sharpness_values) / 1000.0)
        
        # 加权平均
        quality_score = (brightness_score * 0.3 + contrast_score * 0.3 + sharpness_score * 0.4)
        
        return quality_score
    
    def _analyze_shots(self, video_path: str, detection_result: DetectionResult,
                      progress_callback: Optional[Callable[[float, str], None]] = None) -> List[ShotAnalysis]:
        """分析各个镜头"""
        shot_analyses = []
        boundaries = detection_result.boundaries
        
        if len(boundaries) < 2:
            return shot_analyses
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        try:
            for i in range(len(boundaries) - 1):
                start_boundary = boundaries[i]
                end_boundary = boundaries[i + 1]
                
                if progress_callback:
                    progress = 0.5 + (i / len(boundaries)) * 0.3
                    progress_callback(progress, f"分析镜头 {i+1}/{len(boundaries)-1}")
                
                # 分析单个镜头
                shot_analysis = self._analyze_single_shot(
                    cap, start_boundary.frame_number, end_boundary.frame_number, fps, i
                )
                
                shot_analyses.append(shot_analysis)
            
        finally:
            cap.release()
        
        return shot_analyses
    
    def _analyze_single_shot(self, cap: cv2.VideoCapture, start_frame: int,
                           end_frame: int, fps: float, shot_index: int) -> ShotAnalysis:
        """分析单个镜头"""
        # 设置到起始帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        frames = []
        brightness_values = []
        
        # 采样帧
        frame_count = end_frame - start_frame
        sample_interval = max(1, frame_count // 10)  # 最多采样10帧
        
        for frame_idx in range(start_frame, end_frame, sample_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                frames.append(frame)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness_values.append(np.mean(gray))
        
        # 分析主要颜色
        dominant_colors = self._extract_dominant_colors(frames)
        
        # 计算运动强度
        motion_score = self._calculate_motion_score(frames)
        
        # 计算复杂度
        complexity_score = self._calculate_complexity_score(frames)
        
        return ShotAnalysis(
            shot_index=shot_index,
            start_time=start_frame / fps,
            end_time=end_frame / fps,
            duration=(end_frame - start_frame) / fps,
            dominant_colors=dominant_colors,
            avg_brightness=np.mean(brightness_values) if brightness_values else 0,
            motion_score=motion_score,
            complexity_score=complexity_score
        )
    
    def _extract_dominant_colors(self, frames: List[np.ndarray]) -> List[Tuple[int, int, int]]:
        """提取主要颜色"""
        if not frames:
            return []
        
        # 合并所有帧的像素
        all_pixels = []
        for frame in frames[:3]:  # 只使用前3帧
            resized = cv2.resize(frame, (50, 50))  # 缩小以提高速度
            pixels = resized.reshape(-1, 3)
            all_pixels.extend(pixels)
        
        if not all_pixels:
            return []
        
        # 使用K-means聚类找到主要颜色
        try:
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            kmeans.fit(all_pixels)
            
            colors = []
            for center in kmeans.cluster_centers_:
                colors.append((int(center[2]), int(center[1]), int(center[0])))  # BGR to RGB
            
            return colors
            
        except ImportError:
            # 如果没有sklearn，使用简单的平均颜色
            avg_color = np.mean(all_pixels, axis=0)
            return [(int(avg_color[2]), int(avg_color[1]), int(avg_color[0]))]
    
    def _calculate_motion_score(self, frames: List[np.ndarray]) -> float:
        """计算运动强度分数"""
        if len(frames) < 2:
            return 0.0
        
        motion_scores = []
        
        for i in range(1, len(frames)):
            prev_gray = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            
            # 计算帧差
            diff = cv2.absdiff(prev_gray, curr_gray)
            motion_score = np.mean(diff)
            motion_scores.append(motion_score)
        
        return np.mean(motion_scores) if motion_scores else 0.0
    
    def _calculate_complexity_score(self, frames: List[np.ndarray]) -> float:
        """计算场景复杂度分数"""
        if not frames:
            return 0.0
        
        complexity_scores = []
        
        for frame in frames[:3]:  # 只分析前3帧
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 使用Canny边缘检测计算复杂度
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            complexity_scores.append(edge_density)
        
        return np.mean(complexity_scores) if complexity_scores else 0.0
    
    def _generate_analysis_report(self, video_metrics: VideoMetrics,
                                 quality_analysis: Dict[str, Any],
                                 shot_analyses: List[ShotAnalysis]) -> Dict[str, Any]:
        """生成分析报告"""
        report = {
            "summary": {
                "total_duration": video_metrics.duration,
                "total_shots": len(shot_analyses),
                "avg_shot_duration": np.mean([shot.duration for shot in shot_analyses]) if shot_analyses else 0,
                "quality_score": quality_analysis.get("quality_score", 0),
                "file_size_mb": video_metrics.file_size_mb
            },
            "quality_assessment": {
                "brightness": "good" if 50 <= quality_analysis.get("avg_brightness", 0) <= 200 else "poor",
                "contrast": "good" if quality_analysis.get("avg_contrast", 0) > 30 else "poor",
                "sharpness": "good" if quality_analysis.get("avg_sharpness", 0) > 100 else "poor"
            },
            "content_analysis": {
                "avg_motion_intensity": np.mean([shot.motion_score for shot in shot_analyses]) if shot_analyses else 0,
                "avg_scene_complexity": np.mean([shot.complexity_score for shot in shot_analyses]) if shot_analyses else 0,
                "shot_duration_variance": np.var([shot.duration for shot in shot_analyses]) if shot_analyses else 0
            },
            "recommendations": self._generate_recommendations(video_metrics, quality_analysis, shot_analyses)
        }
        
        return report
    
    def _generate_recommendations(self, video_metrics: VideoMetrics,
                                 quality_analysis: Dict[str, Any],
                                 shot_analyses: List[ShotAnalysis]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 质量建议
        if quality_analysis.get("avg_brightness", 0) < 50:
            recommendations.append("视频亮度偏低，建议增加曝光")
        elif quality_analysis.get("avg_brightness", 0) > 200:
            recommendations.append("视频亮度偏高，建议减少曝光")
        
        if quality_analysis.get("avg_contrast", 0) < 30:
            recommendations.append("视频对比度偏低，建议增强对比度")
        
        if quality_analysis.get("avg_sharpness", 0) < 100:
            recommendations.append("视频清晰度偏低，建议检查对焦或增强锐化")
        
        # 内容建议
        if shot_analyses:
            avg_shot_duration = np.mean([shot.duration for shot in shot_analyses])
            if avg_shot_duration < 1.0:
                recommendations.append("镜头切换过于频繁，建议适当延长镜头时长")
            elif avg_shot_duration > 10.0:
                recommendations.append("镜头时长过长，建议增加镜头切换")
        
        # 文件大小建议
        if video_metrics.file_size_mb > 500:
            recommendations.append("文件大小较大，建议压缩以便分享")
        
        return recommendations
