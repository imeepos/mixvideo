"""
Advanced Analytics Module
高级分析模块
"""

import json
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger


class AdvancedAnalytics:
    """高级分析器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化高级分析器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="AdvancedAnalytics")
        
        # 分析配置
        self.analytics_config = self.config.get('analytics', {
            'enable_quality_analysis': True,
            'enable_content_analysis': True,
            'enable_temporal_analysis': True,
            'enable_statistical_analysis': True,
            'quality_metrics': ['sharpness', 'brightness', 'contrast', 'noise'],
            'content_metrics': ['motion', 'scene_complexity', 'color_distribution'],
            'temporal_metrics': ['shot_duration', 'transition_types', 'rhythm']
        })
        
        self.logger.info("Advanced analytics initialized")
    
    def analyze_video_comprehensive(self, video_path: str, 
                                   detection_result: Dict[str, Any],
                                   progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        综合视频分析
        
        Args:
            video_path: 视频文件路径
            detection_result: 检测结果
            progress_callback: 进度回调函数
            
        Returns:
            综合分析结果
        """
        try:
            start_time = time.time()
            analysis_result = {
                "video_path": video_path,
                "analysis_timestamp": start_time,
                "quality_analysis": {},
                "content_analysis": {},
                "temporal_analysis": {},
                "statistical_analysis": {},
                "recommendations": []
            }
            
            # 1. 质量分析
            if self.analytics_config['enable_quality_analysis']:
                if progress_callback:
                    progress_callback(0.2, "分析视频质量...")
                
                quality_result = self._analyze_video_quality(video_path, detection_result)
                analysis_result["quality_analysis"] = quality_result
            
            # 2. 内容分析
            if self.analytics_config['enable_content_analysis']:
                if progress_callback:
                    progress_callback(0.4, "分析视频内容...")
                
                content_result = self._analyze_video_content(video_path, detection_result)
                analysis_result["content_analysis"] = content_result
            
            # 3. 时序分析
            if self.analytics_config['enable_temporal_analysis']:
                if progress_callback:
                    progress_callback(0.6, "分析时序特征...")
                
                temporal_result = self._analyze_temporal_features(detection_result)
                analysis_result["temporal_analysis"] = temporal_result
            
            # 4. 统计分析
            if self.analytics_config['enable_statistical_analysis']:
                if progress_callback:
                    progress_callback(0.8, "生成统计分析...")
                
                statistical_result = self._analyze_statistics(detection_result)
                analysis_result["statistical_analysis"] = statistical_result
            
            # 5. 生成建议
            if progress_callback:
                progress_callback(0.9, "生成优化建议...")
            
            recommendations = self._generate_recommendations(analysis_result)
            analysis_result["recommendations"] = recommendations
            
            # 计算总体评分
            overall_score = self._calculate_overall_score(analysis_result)
            analysis_result["overall_score"] = overall_score
            
            analysis_result["processing_time"] = time.time() - start_time
            
            if progress_callback:
                progress_callback(1.0, "分析完成")
            
            self.logger.info(f"Comprehensive analysis completed for {video_path}")
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {e}")
            raise
    
    def _analyze_video_quality(self, video_path: str, 
                              detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析视频质量"""
        try:
            import cv2
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception(f"Cannot open video: {video_path}")
            
            quality_metrics = {
                "resolution": {
                    "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                },
                "fps": cap.get(cv2.CAP_PROP_FPS),
                "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "duration": 0.0,
                "sharpness": {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0},
                "brightness": {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0},
                "contrast": {"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0},
                "noise_level": {"mean": 0.0, "std": 0.0}
            }
            
            # 计算时长
            if quality_metrics["fps"] > 0:
                quality_metrics["duration"] = quality_metrics["frame_count"] / quality_metrics["fps"]
            
            # 采样分析帧质量
            sample_frames = min(50, quality_metrics["frame_count"])
            frame_interval = max(1, quality_metrics["frame_count"] // sample_frames)
            
            sharpness_values = []
            brightness_values = []
            contrast_values = []
            noise_values = []
            
            for i in range(0, quality_metrics["frame_count"], frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if ret:
                    # 转换为灰度图
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # 计算清晰度（拉普拉斯方差）
                    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                    sharpness_values.append(sharpness)
                    
                    # 计算亮度
                    brightness = np.mean(gray)
                    brightness_values.append(brightness)
                    
                    # 计算对比度
                    contrast = np.std(gray)
                    contrast_values.append(contrast)
                    
                    # 估算噪声水平
                    noise = self._estimate_noise_level(gray)
                    noise_values.append(noise)
            
            cap.release()
            
            # 统计质量指标
            if sharpness_values:
                quality_metrics["sharpness"] = {
                    "mean": float(np.mean(sharpness_values)),
                    "std": float(np.std(sharpness_values)),
                    "min": float(np.min(sharpness_values)),
                    "max": float(np.max(sharpness_values))
                }
            
            if brightness_values:
                quality_metrics["brightness"] = {
                    "mean": float(np.mean(brightness_values)),
                    "std": float(np.std(brightness_values)),
                    "min": float(np.min(brightness_values)),
                    "max": float(np.max(brightness_values))
                }
            
            if contrast_values:
                quality_metrics["contrast"] = {
                    "mean": float(np.mean(contrast_values)),
                    "std": float(np.std(contrast_values)),
                    "min": float(np.min(contrast_values)),
                    "max": float(np.max(contrast_values))
                }
            
            if noise_values:
                quality_metrics["noise_level"] = {
                    "mean": float(np.mean(noise_values)),
                    "std": float(np.std(noise_values))
                }
            
            # 质量评级
            quality_metrics["quality_score"] = self._calculate_quality_score(quality_metrics)
            quality_metrics["quality_grade"] = self._get_quality_grade(quality_metrics["quality_score"])
            
            return quality_metrics
            
        except Exception as e:
            self.logger.error(f"Video quality analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_video_content(self, video_path: str, 
                              detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析视频内容"""
        try:
            content_metrics = {
                "shot_count": len(detection_result.get("boundaries", [])),
                "average_shot_duration": 0.0,
                "motion_analysis": {"high_motion_shots": 0, "low_motion_shots": 0},
                "scene_complexity": {"simple": 0, "moderate": 0, "complex": 0},
                "color_analysis": {
                    "dominant_colors": [],
                    "color_diversity": 0.0,
                    "brightness_distribution": {}
                },
                "content_type": "unknown"
            }
            
            boundaries = detection_result.get("boundaries", [])
            
            if boundaries:
                # 计算平均镜头时长
                durations = []
                for i in range(len(boundaries) - 1):
                    duration = boundaries[i + 1]["timestamp"] - boundaries[i]["timestamp"]
                    durations.append(duration)
                
                if durations:
                    content_metrics["average_shot_duration"] = float(np.mean(durations))
            
            # 内容类型推断
            content_metrics["content_type"] = self._infer_content_type(content_metrics)
            
            return content_metrics
            
        except Exception as e:
            self.logger.error(f"Video content analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_temporal_features(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """分析时序特征"""
        try:
            boundaries = detection_result.get("boundaries", [])
            
            temporal_metrics = {
                "shot_duration_stats": {},
                "rhythm_analysis": {},
                "transition_patterns": {},
                "temporal_consistency": 0.0
            }
            
            if len(boundaries) < 2:
                return temporal_metrics
            
            # 计算镜头时长统计
            durations = []
            for i in range(len(boundaries) - 1):
                duration = boundaries[i + 1]["timestamp"] - boundaries[i]["timestamp"]
                durations.append(duration)
            
            if durations:
                temporal_metrics["shot_duration_stats"] = {
                    "mean": float(np.mean(durations)),
                    "std": float(np.std(durations)),
                    "min": float(np.min(durations)),
                    "max": float(np.max(durations)),
                    "median": float(np.median(durations)),
                    "percentile_25": float(np.percentile(durations, 25)),
                    "percentile_75": float(np.percentile(durations, 75))
                }
                
                # 节奏分析
                temporal_metrics["rhythm_analysis"] = self._analyze_rhythm(durations)
                
                # 时序一致性
                temporal_metrics["temporal_consistency"] = self._calculate_temporal_consistency(durations)
            
            return temporal_metrics
            
        except Exception as e:
            self.logger.error(f"Temporal analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_statistics(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """统计分析"""
        try:
            boundaries = detection_result.get("boundaries", [])
            
            statistical_metrics = {
                "boundary_count": len(boundaries),
                "confidence_stats": {},
                "distribution_analysis": {},
                "outlier_detection": {}
            }
            
            if boundaries:
                # 置信度统计
                confidences = [b.get("confidence", 0.0) for b in boundaries]
                if confidences:
                    statistical_metrics["confidence_stats"] = {
                        "mean": float(np.mean(confidences)),
                        "std": float(np.std(confidences)),
                        "min": float(np.min(confidences)),
                        "max": float(np.max(confidences))
                    }
                
                # 分布分析
                timestamps = [b.get("timestamp", 0.0) for b in boundaries]
                if timestamps:
                    statistical_metrics["distribution_analysis"] = self._analyze_distribution(timestamps)
            
            return statistical_metrics
            
        except Exception as e:
            self.logger.error(f"Statistical analysis failed: {e}")
            return {"error": str(e)}
    
    def _estimate_noise_level(self, gray_image: np.ndarray) -> float:
        """估算图像噪声水平"""
        try:
            # 使用高斯拉普拉斯算子估算噪声
            kernel = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]])
            convolved = cv2.filter2D(gray_image, cv2.CV_64F, kernel)
            noise_level = np.std(convolved)
            return float(noise_level)
        except:
            return 0.0
    
    def _calculate_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """计算质量评分"""
        try:
            score = 0.0
            weight_sum = 0.0
            
            # 分辨率评分
            resolution = quality_metrics.get("resolution", {})
            width = resolution.get("width", 0)
            height = resolution.get("height", 0)
            
            if width > 0 and height > 0:
                resolution_score = min(1.0, (width * height) / (1920 * 1080))
                score += resolution_score * 0.3
                weight_sum += 0.3
            
            # 清晰度评分
            sharpness = quality_metrics.get("sharpness", {})
            sharpness_mean = sharpness.get("mean", 0)
            if sharpness_mean > 0:
                sharpness_score = min(1.0, sharpness_mean / 1000)  # 归一化
                score += sharpness_score * 0.4
                weight_sum += 0.4
            
            # 对比度评分
            contrast = quality_metrics.get("contrast", {})
            contrast_mean = contrast.get("mean", 0)
            if contrast_mean > 0:
                contrast_score = min(1.0, contrast_mean / 100)  # 归一化
                score += contrast_score * 0.3
                weight_sum += 0.3
            
            if weight_sum > 0:
                return score / weight_sum
            else:
                return 0.5  # 默认评分
                
        except Exception:
            return 0.5
    
    def _get_quality_grade(self, score: float) -> str:
        """获取质量等级"""
        if score >= 0.9:
            return "优秀"
        elif score >= 0.8:
            return "良好"
        elif score >= 0.6:
            return "一般"
        elif score >= 0.4:
            return "较差"
        else:
            return "很差"
    
    def _infer_content_type(self, content_metrics: Dict[str, Any]) -> str:
        """推断内容类型"""
        avg_duration = content_metrics.get("average_shot_duration", 0)
        shot_count = content_metrics.get("shot_count", 0)
        
        if avg_duration < 2.0:
            return "快节奏/音乐视频"
        elif avg_duration > 10.0:
            return "纪录片/对话"
        elif shot_count > 100:
            return "动作片/快剪"
        else:
            return "常规视频"
    
    def _analyze_rhythm(self, durations: List[float]) -> Dict[str, Any]:
        """分析视频节奏"""
        try:
            rhythm_metrics = {
                "rhythm_type": "unknown",
                "tempo_changes": 0,
                "rhythm_score": 0.0
            }
            
            if len(durations) < 3:
                return rhythm_metrics
            
            # 计算节奏变化
            tempo_changes = 0
            for i in range(1, len(durations) - 1):
                if (durations[i] > durations[i-1] and durations[i] > durations[i+1]) or \
                   (durations[i] < durations[i-1] and durations[i] < durations[i+1]):
                    tempo_changes += 1
            
            rhythm_metrics["tempo_changes"] = tempo_changes
            
            # 节奏类型判断
            avg_duration = np.mean(durations)
            std_duration = np.std(durations)
            
            if std_duration / avg_duration < 0.3:
                rhythm_metrics["rhythm_type"] = "稳定节奏"
            elif std_duration / avg_duration > 0.8:
                rhythm_metrics["rhythm_type"] = "变化节奏"
            else:
                rhythm_metrics["rhythm_type"] = "中等节奏"
            
            # 节奏评分
            rhythm_metrics["rhythm_score"] = min(1.0, 1.0 - (std_duration / avg_duration))
            
            return rhythm_metrics
            
        except Exception:
            return {"rhythm_type": "unknown", "tempo_changes": 0, "rhythm_score": 0.0}
    
    def _calculate_temporal_consistency(self, durations: List[float]) -> float:
        """计算时序一致性"""
        try:
            if len(durations) < 2:
                return 1.0
            
            # 计算变异系数
            mean_duration = np.mean(durations)
            std_duration = np.std(durations)
            
            if mean_duration > 0:
                cv = std_duration / mean_duration
                consistency = max(0.0, 1.0 - cv)
                return float(consistency)
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def _analyze_distribution(self, timestamps: List[float]) -> Dict[str, Any]:
        """分析时间戳分布"""
        try:
            if len(timestamps) < 2:
                return {}
            
            # 计算间隔
            intervals = []
            for i in range(1, len(timestamps)):
                intervals.append(timestamps[i] - timestamps[i-1])
            
            return {
                "uniform_distribution": self._test_uniformity(intervals),
                "clustering_detected": self._detect_clustering(intervals),
                "distribution_type": self._classify_distribution(intervals)
            }
            
        except Exception:
            return {}
    
    def _test_uniformity(self, intervals: List[float]) -> bool:
        """测试分布均匀性"""
        try:
            if len(intervals) < 3:
                return True
            
            mean_interval = np.mean(intervals)
            std_interval = np.std(intervals)
            
            # 变异系数小于0.5认为是均匀分布
            cv = std_interval / mean_interval if mean_interval > 0 else 1.0
            return cv < 0.5
            
        except Exception:
            return False
    
    def _detect_clustering(self, intervals: List[float]) -> bool:
        """检测聚类"""
        try:
            if len(intervals) < 5:
                return False
            
            # 简单的聚类检测：检查是否有明显的间隔差异
            sorted_intervals = sorted(intervals)
            median_interval = np.median(sorted_intervals)
            
            # 检查是否有显著大于中位数的间隔
            large_intervals = [x for x in intervals if x > median_interval * 3]
            return len(large_intervals) > len(intervals) * 0.1
            
        except Exception:
            return False
    
    def _classify_distribution(self, intervals: List[float]) -> str:
        """分类分布类型"""
        try:
            if self._test_uniformity(intervals):
                return "均匀分布"
            elif self._detect_clustering(intervals):
                return "聚类分布"
            else:
                return "随机分布"
                
        except Exception:
            return "未知分布"
    
    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        try:
            # 质量建议
            quality_analysis = analysis_result.get("quality_analysis", {})
            quality_score = quality_analysis.get("quality_score", 0.5)
            
            if quality_score < 0.6:
                recommendations.append("视频质量较低，建议提高录制质量或进行后期增强")
            
            # 内容建议
            content_analysis = analysis_result.get("content_analysis", {})
            avg_shot_duration = content_analysis.get("average_shot_duration", 0)
            
            if avg_shot_duration < 1.0:
                recommendations.append("镜头切换过于频繁，可能影响观看体验")
            elif avg_shot_duration > 15.0:
                recommendations.append("镜头时长过长，建议增加剪辑点以提高节奏感")
            
            # 时序建议
            temporal_analysis = analysis_result.get("temporal_analysis", {})
            temporal_consistency = temporal_analysis.get("temporal_consistency", 1.0)
            
            if temporal_consistency < 0.5:
                recommendations.append("镜头时长变化较大，建议优化剪辑节奏")
            
            # 统计建议
            statistical_analysis = analysis_result.get("statistical_analysis", {})
            boundary_count = statistical_analysis.get("boundary_count", 0)
            
            if boundary_count < 5:
                recommendations.append("检测到的镜头边界较少，可能需要调整检测参数")
            elif boundary_count > 200:
                recommendations.append("检测到的镜头边界过多，建议提高检测阈值")
            
            if not recommendations:
                recommendations.append("视频分析结果良好，无需特别优化")
            
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {e}")
            recommendations.append("无法生成建议，请检查分析结果")
        
        return recommendations
    
    def _calculate_overall_score(self, analysis_result: Dict[str, Any]) -> float:
        """计算总体评分"""
        try:
            scores = []
            weights = []
            
            # 质量评分
            quality_analysis = analysis_result.get("quality_analysis", {})
            quality_score = quality_analysis.get("quality_score")
            if quality_score is not None:
                scores.append(quality_score)
                weights.append(0.4)
            
            # 时序一致性评分
            temporal_analysis = analysis_result.get("temporal_analysis", {})
            temporal_consistency = temporal_analysis.get("temporal_consistency")
            if temporal_consistency is not None:
                scores.append(temporal_consistency)
                weights.append(0.3)
            
            # 节奏评分
            rhythm_analysis = temporal_analysis.get("rhythm_analysis", {})
            rhythm_score = rhythm_analysis.get("rhythm_score")
            if rhythm_score is not None:
                scores.append(rhythm_score)
                weights.append(0.3)
            
            if scores and weights:
                weighted_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
                return float(weighted_score)
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("Advanced analytics cleanup completed")


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化报告生成器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="ReportGenerator")
        
        # 报告配置
        self.report_config = self.config.get('report', {
            'include_charts': True,
            'include_statistics': True,
            'include_recommendations': True,
            'output_format': 'json',  # json, html, pdf
            'template_dir': './templates',
            'output_dir': './reports'
        })
        
        self.logger.info("Report generator initialized")
    
    def generate_analysis_report(self, analysis_result: Dict[str, Any], 
                               output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        生成分析报告
        
        Args:
            analysis_result: 分析结果
            output_path: 输出路径
            
        Returns:
            报告生成结果
        """
        try:
            # 生成报告内容
            report_content = self._create_report_content(analysis_result)
            
            # 确定输出路径
            if not output_path:
                timestamp = int(time.time())
                output_path = f"{self.report_config['output_dir']}/analysis_report_{timestamp}.json"
            
            # 创建输出目录
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存报告
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_content, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Analysis report generated: {output_path}")
            
            return {
                "success": True,
                "report_path": str(output_file),
                "report_size": output_file.stat().st_size,
                "format": self.report_config['output_format']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate analysis report: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_report_content(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """创建报告内容"""
        report = {
            "report_metadata": {
                "generated_at": time.time(),
                "generator_version": "2.0.0",
                "report_type": "video_analysis"
            },
            "executive_summary": self._create_executive_summary(analysis_result),
            "detailed_analysis": analysis_result,
            "visualizations": self._create_visualizations(analysis_result),
            "conclusions": self._create_conclusions(analysis_result)
        }
        
        return report
    
    def _create_executive_summary(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """创建执行摘要"""
        summary = {
            "overall_score": analysis_result.get("overall_score", 0.0),
            "key_findings": [],
            "main_recommendations": analysis_result.get("recommendations", [])[:3]
        }
        
        # 提取关键发现
        quality_analysis = analysis_result.get("quality_analysis", {})
        if quality_analysis:
            quality_grade = quality_analysis.get("quality_grade", "未知")
            summary["key_findings"].append(f"视频质量等级: {quality_grade}")
        
        content_analysis = analysis_result.get("content_analysis", {})
        if content_analysis:
            shot_count = content_analysis.get("shot_count", 0)
            content_type = content_analysis.get("content_type", "未知")
            summary["key_findings"].append(f"检测到 {shot_count} 个镜头，内容类型: {content_type}")
        
        return summary
    
    def _create_visualizations(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """创建可视化数据"""
        visualizations = {
            "charts": [],
            "graphs": [],
            "statistics": {}
        }
        
        # 这里可以添加图表数据
        # 实际实现中可以生成matplotlib图表或其他可视化
        
        return visualizations
    
    def _create_conclusions(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """创建结论"""
        conclusions = {
            "summary": "视频分析已完成",
            "strengths": [],
            "areas_for_improvement": [],
            "next_steps": []
        }
        
        overall_score = analysis_result.get("overall_score", 0.0)
        
        if overall_score > 0.8:
            conclusions["strengths"].append("整体视频质量优秀")
        elif overall_score > 0.6:
            conclusions["strengths"].append("视频质量良好")
        else:
            conclusions["areas_for_improvement"].append("视频质量需要改进")
        
        recommendations = analysis_result.get("recommendations", [])
        if recommendations:
            conclusions["next_steps"] = recommendations[:2]
        
        return conclusions
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("Report generator cleanup completed")
