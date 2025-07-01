"""
帧差分析检测器
基于相邻帧之间的像素差异检测镜头切换
"""

import time
import numpy as np
import cv2
from typing import List, Tuple
from .base import BaseDetector, ShotBoundary, DetectionResult


class FrameDifferenceDetector(BaseDetector):
    """帧差分析检测器"""
    
    def __init__(self, threshold: float = 0.3, min_scene_length: int = 15, **kwargs):
        super().__init__("FrameDifference", **kwargs)
        self.threshold = threshold
        self.min_scene_length = min_scene_length
        self.resize_height = kwargs.get('resize_height', 240)  # 降低分辨率加速处理
        
    def initialize(self) -> bool:
        """初始化检测器"""
        try:
            self.logger.info(f"Initializing FrameDifference detector with threshold={self.threshold}")
            self.is_initialized = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize FrameDifference detector: {e}")
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
            frame_number = 0
            
            while True:
                ret, curr_frame = cap.read()
                if not ret:
                    break
                
                frame_number += 1
                curr_frame = self.preprocess_frame(curr_frame)
                
                # 计算帧差
                diff_score = self.process_frame_pair(prev_frame, curr_frame)
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
                            'algorithm': 'frame_difference',
                            'diff_score': diff_score
                        }
                    )
                    boundaries.append(boundary)
                    self.logger.debug(f"Shot boundary detected at frame {frame_number} (score: {diff_score:.3f})")
                
                prev_frame = curr_frame
            
            cap.release()
            
            # 后处理：移除过短的镜头
            boundaries = self.postprocess_boundaries(boundaries, self.min_scene_length)
            
            processing_time = time.time() - start_time
            self.logger.info(f"FrameDifference detection completed: {len(boundaries)} boundaries found in {processing_time:.2f}s")
            
            return DetectionResult(
                boundaries=boundaries,
                algorithm_name=self.name,
                processing_time=processing_time,
                frame_count=frame_count,
                confidence_scores=confidence_scores
            )
            
        except Exception as e:
            self.logger.error(f"Error in FrameDifference detection: {e}")
            return DetectionResult([], self.name, time.time() - start_time, 0, [])
    
    def process_frame_pair(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """计算两帧之间的差异分数"""
        # 调整帧大小以加速处理
        h1, w1 = frame1.shape[:2]
        if h1 > self.resize_height:
            scale = self.resize_height / h1
            new_width = int(w1 * scale)
            frame1 = cv2.resize(frame1, (new_width, self.resize_height))
            frame2 = cv2.resize(frame2, (new_width, self.resize_height))
        
        # 转换为灰度图
        if len(frame1.shape) == 3:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
        else:
            gray1, gray2 = frame1, frame2
        
        # 计算绝对差值
        diff = cv2.absdiff(gray1, gray2)
        
        # 计算差异的均值
        mean_diff = np.mean(diff) / 255.0
        
        return mean_diff
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """预处理帧"""
        # 应用高斯模糊减少噪声
        if len(frame.shape) == 3:
            frame = cv2.GaussianBlur(frame, (5, 5), 0)
        
        return super().preprocess_frame(frame)


class EnhancedFrameDifferenceDetector(FrameDifferenceDetector):
    """增强版帧差检测器"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.adaptive_threshold = kwargs.get('adaptive_threshold', True)
        self.edge_enhancement = kwargs.get('edge_enhancement', True)
        self.motion_compensation = kwargs.get('motion_compensation', True)
    
    def process_frame_pair(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """增强版帧差计算"""
        # 调整帧大小
        h1, w1 = frame1.shape[:2]
        if h1 > self.resize_height:
            scale = self.resize_height / h1
            new_width = int(w1 * scale)
            frame1 = cv2.resize(frame1, (new_width, self.resize_height))
            frame2 = cv2.resize(frame2, (new_width, self.resize_height))
        
        # 转换为灰度图
        if len(frame1.shape) == 3:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
        else:
            gray1, gray2 = frame1, frame2
        
        # 边缘增强
        if self.edge_enhancement:
            gray1 = self._enhance_edges(gray1)
            gray2 = self._enhance_edges(gray2)
        
        # 运动补偿
        if self.motion_compensation:
            gray2 = self._motion_compensation(gray1, gray2)
        
        # 计算多种差异指标
        diff_scores = []
        
        # 1. 像素级差异
        pixel_diff = np.mean(cv2.absdiff(gray1, gray2)) / 255.0
        diff_scores.append(pixel_diff)
        
        # 2. 结构相似性差异
        ssim_score = self._calculate_ssim(gray1, gray2)
        diff_scores.append(1.0 - ssim_score)
        
        # 3. 梯度差异
        gradient_diff = self._calculate_gradient_diff(gray1, gray2)
        diff_scores.append(gradient_diff)
        
        # 加权融合
        weights = [0.4, 0.3, 0.3]
        final_score = sum(w * s for w, s in zip(weights, diff_scores))
        
        return final_score
    
    def _enhance_edges(self, frame: np.ndarray) -> np.ndarray:
        """边缘增强"""
        # 使用Sobel算子增强边缘
        sobel_x = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=3)
        sobel_combined = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # 归一化并与原图融合
        sobel_normalized = cv2.normalize(sobel_combined, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        enhanced = cv2.addWeighted(frame, 0.7, sobel_normalized, 0.3, 0)
        
        return enhanced
    
    def _motion_compensation(self, frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
        """简单的运动补偿"""
        try:
            # 使用光流估计运动
            flow = cv2.calcOpticalFlowPyrLK(
                frame1, frame2, 
                np.array([[frame1.shape[1]//2, frame1.shape[0]//2]], dtype=np.float32),
                None
            )[0]
            
            if flow is not None and len(flow) > 0:
                dx, dy = flow[0][0]
                # 简单的平移补偿
                M = np.float32([[1, 0, -dx], [0, 1, -dy]])
                compensated = cv2.warpAffine(frame2, M, (frame2.shape[1], frame2.shape[0]))
                return compensated
        except:
            pass
        
        return frame2
    
    def _calculate_ssim(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """计算结构相似性指数"""
        # 简化版SSIM计算
        mu1 = cv2.GaussianBlur(frame1.astype(np.float64), (11, 11), 1.5)
        mu2 = cv2.GaussianBlur(frame2.astype(np.float64), (11, 11), 1.5)
        
        mu1_sq = mu1 * mu1
        mu2_sq = mu2 * mu2
        mu1_mu2 = mu1 * mu2
        
        sigma1_sq = cv2.GaussianBlur(frame1.astype(np.float64) * frame1.astype(np.float64), (11, 11), 1.5) - mu1_sq
        sigma2_sq = cv2.GaussianBlur(frame2.astype(np.float64) * frame2.astype(np.float64), (11, 11), 1.5) - mu2_sq
        sigma12 = cv2.GaussianBlur(frame1.astype(np.float64) * frame2.astype(np.float64), (11, 11), 1.5) - mu1_mu2
        
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2
        
        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
        
        return np.mean(ssim_map)
    
    def _calculate_gradient_diff(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """计算梯度差异"""
        # 计算梯度
        grad1_x = cv2.Sobel(frame1, cv2.CV_64F, 1, 0, ksize=3)
        grad1_y = cv2.Sobel(frame1, cv2.CV_64F, 0, 1, ksize=3)
        grad2_x = cv2.Sobel(frame2, cv2.CV_64F, 1, 0, ksize=3)
        grad2_y = cv2.Sobel(frame2, cv2.CV_64F, 0, 1, ksize=3)
        
        # 计算梯度幅值
        mag1 = np.sqrt(grad1_x**2 + grad1_y**2)
        mag2 = np.sqrt(grad2_x**2 + grad2_y**2)
        
        # 计算差异
        diff = np.mean(np.abs(mag1 - mag2)) / 255.0
        
        return diff
