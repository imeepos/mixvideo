"""
直方图检测器
基于色彩直方图分析检测镜头切换
"""

import time
import numpy as np
import cv2
from typing import List, Tuple
from .base import BaseDetector, ShotBoundary, DetectionResult


class HistogramDetector(BaseDetector):
    """直方图检测器"""
    
    def __init__(self, threshold: float = 0.4, bins: int = 256, **kwargs):
        super().__init__("Histogram", **kwargs)
        self.threshold = threshold
        self.bins = bins
        self.min_scene_length = kwargs.get('min_scene_length', 15)
        self.color_space = kwargs.get('color_space', 'RGB')  # RGB, HSV, LAB
        
    def initialize(self) -> bool:
        """初始化检测器"""
        try:
            self.logger.info(f"Initializing Histogram detector with threshold={self.threshold}, bins={self.bins}")
            self.is_initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Histogram detector: {e}")
            return False
    
    def detect_shots(self, video_path: str, **kwargs) -> DetectionResult:
        """检测镜头边界"""
        start_time = time.time()
        boundaries = []
        confidence_scores = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            self.logger.info(f"Processing video: {frame_count} frames at {fps} FPS")
            
            # 读取第一帧
            ret, prev_frame = cap.read()
            if not ret:
                raise ValueError("Cannot read first frame")
            
            prev_frame = self.preprocess_frame(prev_frame)
            prev_hist = self._calculate_histogram(prev_frame)
            frame_number = 0
            
            while True:
                ret, curr_frame = cap.read()
                if not ret:
                    break
                
                frame_number += 1
                curr_frame = self.preprocess_frame(curr_frame)
                curr_hist = self._calculate_histogram(curr_frame)
                
                # 计算直方图差异
                diff_score = self.process_frame_pair(prev_hist, curr_hist)
                confidence_scores.append(diff_score)
                
                # 检查是否超过阈值
                if diff_score > self.threshold:
                    timestamp = frame_number / fps
                    boundary = ShotBoundary(
                        frame_number=frame_number,
                        timestamp=timestamp,
                        confidence=diff_score,
                        boundary_type='cut',
                        metadata={
                            'algorithm': 'histogram',
                            'diff_score': diff_score,
                            'color_space': self.color_space
                        }
                    )
                    boundaries.append(boundary)
                    self.logger.debug(f"Shot boundary detected at frame {frame_number} (score: {diff_score:.3f})")
                
                prev_hist = curr_hist
            
            cap.release()
            
            # 后处理
            boundaries = self.postprocess_boundaries(boundaries, self.min_scene_length)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Histogram detection completed: {len(boundaries)} boundaries found in {processing_time:.2f}s")
            
            return DetectionResult(
                boundaries=boundaries,
                algorithm_name=self.name,
                processing_time=processing_time,
                frame_count=frame_count,
                confidence_scores=confidence_scores
            )
            
        except Exception as e:
            self.logger.error(f"Error in Histogram detection: {e}")
            return DetectionResult([], self.name, time.time() - start_time, 0, [])
    
    def process_frame_pair(self, hist1: np.ndarray, hist2: np.ndarray) -> float:
        """计算两个直方图之间的差异分数"""
        # 使用多种距离度量
        distances = []
        
        # 1. 卡方距离
        chi_square = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
        distances.append(min(chi_square / 1000.0, 1.0))  # 归一化
        
        # 2. 巴氏距离
        bhattacharyya = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
        distances.append(bhattacharyya)
        
        # 3. 相关性（转换为距离）
        correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
        distances.append(1.0 - correlation)
        
        # 4. 交集距离
        intersection = cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT)
        # 归一化交集距离
        hist_sum = np.sum(hist1)
        if hist_sum > 0:
            intersection_dist = 1.0 - (intersection / hist_sum)
        else:
            intersection_dist = 1.0
        distances.append(intersection_dist)
        
        # 加权平均
        weights = [0.3, 0.3, 0.2, 0.2]
        final_distance = sum(w * d for w, d in zip(weights, distances))
        
        return final_distance
    
    def _calculate_histogram(self, frame: np.ndarray) -> np.ndarray:
        """计算帧的直方图"""
        if self.color_space == 'HSV':
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            # 只使用H和S通道
            hist = cv2.calcHist([frame], [0, 1], None, [self.bins//4, self.bins//4], [0, 180, 0, 256])
        elif self.color_space == 'LAB':
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB)
            hist = cv2.calcHist([frame], [0, 1, 2], None, [self.bins//4]*3, [0, 256]*3)
        else:  # RGB
            hist = cv2.calcHist([frame], [0, 1, 2], None, [self.bins//4]*3, [0, 256]*3)
        
        # 归一化直方图
        hist = cv2.normalize(hist, hist).flatten()
        
        return hist
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """预处理帧"""
        # 调整大小以加速处理
        height, width = frame.shape[:2]
        if height > 240:
            scale = 240 / height
            new_width = int(width * scale)
            frame = cv2.resize(frame, (new_width, 240))
        
        return super().preprocess_frame(frame)


class MultiChannelHistogramDetector(HistogramDetector):
    """多通道直方图检测器"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.use_spatial_histogram = kwargs.get('use_spatial_histogram', True)
        self.grid_size = kwargs.get('grid_size', 4)  # 4x4网格
    
    def _calculate_histogram(self, frame: np.ndarray) -> np.ndarray:
        """计算多通道直方图"""
        histograms = []
        
        # 1. 全局直方图
        global_hist = super()._calculate_histogram(frame)
        histograms.append(global_hist)
        
        # 2. 空间直方图（如果启用）
        if self.use_spatial_histogram:
            spatial_hists = self._calculate_spatial_histograms(frame)
            histograms.extend(spatial_hists)
        
        # 3. 边缘直方图
        edge_hist = self._calculate_edge_histogram(frame)
        histograms.append(edge_hist)
        
        # 连接所有直方图
        combined_hist = np.concatenate(histograms)
        
        return combined_hist
    
    def _calculate_spatial_histograms(self, frame: np.ndarray) -> List[np.ndarray]:
        """计算空间分块直方图"""
        height, width = frame.shape[:2]
        block_h = height // self.grid_size
        block_w = width // self.grid_size
        
        spatial_hists = []
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                y1 = i * block_h
                y2 = min((i + 1) * block_h, height)
                x1 = j * block_w
                x2 = min((j + 1) * block_w, width)
                
                block = frame[y1:y2, x1:x2]
                
                if block.size > 0:
                    if len(block.shape) == 3:
                        hist = cv2.calcHist([block], [0, 1, 2], None, 
                                          [self.bins//8]*3, [0, 256]*3)
                    else:
                        hist = cv2.calcHist([block], [0], None, [self.bins//4], [0, 256])
                    
                    hist = cv2.normalize(hist, hist).flatten()
                    spatial_hists.append(hist)
        
        return spatial_hists
    
    def _calculate_edge_histogram(self, frame: np.ndarray) -> np.ndarray:
        """计算边缘直方图"""
        # 转换为灰度图
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        else:
            gray = frame
        
        # 计算边缘
        edges = cv2.Canny(gray, 50, 150)
        
        # 计算边缘方向直方图
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # 计算梯度方向
        angles = np.arctan2(sobel_y, sobel_x)
        angles = (angles + np.pi) / (2 * np.pi) * 180  # 转换为0-180度
        
        # 只考虑边缘像素的方向
        edge_angles = angles[edges > 0]
        
        if len(edge_angles) > 0:
            hist, _ = np.histogram(edge_angles, bins=self.bins//8, range=(0, 180))
            hist = hist.astype(np.float32)
            hist = cv2.normalize(hist, hist).flatten()
        else:
            hist = np.zeros(self.bins//8, dtype=np.float32)
        
        return hist


class AdaptiveHistogramDetector(HistogramDetector):
    """自适应直方图检测器"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptation_window = kwargs.get('adaptation_window', 30)
        self.score_history = []
    
    def detect_shots(self, video_path: str, **kwargs) -> DetectionResult:
        """使用自适应阈值检测镜头边界"""
        # 首先运行基础检测获取所有分数
        result = super().detect_shots(video_path, **kwargs)
        
        # 使用自适应阈值重新处理
        if result.confidence_scores:
            adaptive_boundaries = self._adaptive_threshold_detection(
                result.confidence_scores, video_path
            )
            result.boundaries = adaptive_boundaries
        
        return result
    
    def _adaptive_threshold_detection(self, scores: List[float], video_path: str) -> List[ShotBoundary]:
        """使用自适应阈值检测边界"""
        boundaries = []
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
        
        for i, score in enumerate(scores):
            # 计算局部自适应阈值
            start_idx = max(0, i - self.adaptation_window // 2)
            end_idx = min(len(scores), i + self.adaptation_window // 2)
            local_scores = scores[start_idx:end_idx]
            
            # 使用局部统计计算阈值
            local_mean = np.mean(local_scores)
            local_std = np.std(local_scores)
            adaptive_threshold = local_mean + 2 * local_std
            
            if score > adaptive_threshold and score > self.threshold:
                timestamp = i / fps
                boundary = ShotBoundary(
                    frame_number=i,
                    timestamp=timestamp,
                    confidence=score,
                    boundary_type='cut',
                    metadata={
                        'algorithm': 'adaptive_histogram',
                        'diff_score': score,
                        'adaptive_threshold': adaptive_threshold,
                        'local_mean': local_mean,
                        'local_std': local_std
                    }
                )
                boundaries.append(boundary)
        
        return self.postprocess_boundaries(boundaries, self.min_scene_length)
