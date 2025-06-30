"""
报告生成器
生成分析报告和可视化结果
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from detectors.base import DetectionResult
from processors.video_processor import VideoSegment
from config import ConfigManager
from utils.json_utils import create_quality_metrics_json, safe_json_dump


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logger.bind(component="ReportGenerator")
    
    def generate_report(self, video_path: str, detection_result: DetectionResult,
                       segments: List[VideoSegment], output_dir: str):
        """生成完整的分析报告"""
        self.logger.info("Generating analysis report...")
        
        output_path = Path(output_dir)
        
        # 生成HTML报告
        if self.config.output.generate_html_report:
            self._generate_html_report(video_path, detection_result, segments, 
                                     output_path / "analysis_report.html")
        
        # 生成质量指标报告（使用新的JSON工具）
        quality_data = create_quality_metrics_json(detection_result, segments, self.config)
        safe_json_dump(quality_data, str(output_path / "quality_metrics.json"))
        
        self.logger.info("Analysis report generated successfully")
    
    def _generate_html_report(self, video_path: str, detection_result: DetectionResult,
                            segments: List[VideoSegment], output_path: Path):
        """生成HTML格式的分析报告"""
        try:
            video_name = Path(video_path).name
            total_duration = sum(s.duration for s in segments)
            
            html_content = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>镜头检测分析报告 - {video_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .segments-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .segments-table th, .segments-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        .segments-table th {{ background-color: #f2f2f2; }}
        .timeline {{ margin: 20px 0; padding: 10px; background: #f8f9fa; border-radius: 8px; }}
        .timeline-bar {{ height: 40px; background: linear-gradient(90deg, #007bff, #28a745, #ffc107, #dc3545); border-radius: 6px; position: relative; overflow: hidden; border: 2px solid #dee2e6; }}
        .boundary-marker {{ position: absolute; top: -2px; bottom: -2px; width: 3px; background: #dc3545; border-radius: 1px; box-shadow: 0 0 4px rgba(220, 53, 69, 0.5); z-index: 10; }}
        .timeline-legend {{ display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; color: #666; }}
        .timeline-tick {{ position: absolute; top: 100%; width: 1px; height: 8px; background: #666; }}
        .timeline-label {{ position: absolute; top: 100%; margin-top: 10px; font-size: 10px; color: #666; transform: translateX(-50%); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 镜头检测分析报告</h1>
            <h2>{video_name}</h2>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(segments)}</div>
                <div class="stat-label">检测到的镜头数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(detection_result.boundaries)}</div>
                <div class="stat-label">切换边界数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{total_duration:.1f}s</div>
                <div class="stat-label">总时长</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{detection_result.processing_time:.1f}s</div>
                <div class="stat-label">处理时间</div>
            </div>
        </div>
        
        <h3>📊 检测算法信息</h3>
        <p><strong>算法:</strong> {detection_result.algorithm_name}</p>
        <p><strong>总帧数:</strong> {detection_result.frame_count}</p>
        <p><strong>平均置信度:</strong> {sum(detection_result.confidence_scores)/len(detection_result.confidence_scores):.3f}</p>
        
        <h3>🎞️ 镜头分段详情</h3>
        <table class="segments-table">
            <thead>
                <tr>
                    <th>序号</th>
                    <th>开始时间</th>
                    <th>结束时间</th>
                    <th>时长</th>
                    <th>文件名</th>
                </tr>
            </thead>
            <tbody>
'''
            
            for segment in segments:
                html_content += f'''
                <tr>
                    <td>{segment.index + 1}</td>
                    <td>{segment.start_time:.2f}s</td>
                    <td>{segment.end_time:.2f}s</td>
                    <td>{segment.duration:.2f}s</td>
                    <td>{Path(segment.file_path).name}</td>
                </tr>
'''
            
            html_content += '''
            </tbody>
        </table>
        
        <h3>⏱️ 时间轴可视化</h3>
        <div class="timeline">
            <div class="timeline-bar">
'''

            # 添加时间刻度
            if total_duration > 0:
                # 添加时间刻度（每10%一个刻度）
                for i in range(0, 11):
                    position = i * 10
                    time_at_position = (total_duration * i) / 10
                    html_content += f'<div class="timeline-tick" style="left: {position}%;"></div>'
                    html_content += f'<div class="timeline-label" style="left: {position}%;">{time_at_position:.1f}s</div>'

                # 添加边界标记
                valid_boundaries = []
                for boundary in detection_result.boundaries:
                    # 确保时间戳在有效范围内
                    if 0 <= boundary.timestamp <= total_duration:
                        position = (boundary.timestamp / total_duration) * 100
                        position = min(max(position, 0), 100)  # 确保在0-100%范围内
                        valid_boundaries.append((position, boundary))

                # 按位置排序并添加标记
                valid_boundaries.sort(key=lambda x: x[0])
                for position, boundary in valid_boundaries:
                    html_content += f'<div class="boundary-marker" style="left: {position:.2f}%;" title="时间: {boundary.timestamp:.2f}s, 置信度: {boundary.confidence:.3f}"></div>'

                # 记录有效边界数量用于显示
                valid_boundary_count = len(valid_boundaries)

            # 使用有效边界数量或总边界数量
            displayed_boundary_count = valid_boundary_count if 'valid_boundary_count' in locals() else len(detection_result.boundaries)

            html_content += f'''
            </div>
            <div class="timeline-legend">
                <span>📊 视频时间轴</span>
                <span>🔴 镜头切换点 ({displayed_boundary_count} 个)</span>
                <span>⏱️ 总时长: {total_duration:.1f}s</span>
            </div>
        </div>

        <div style="margin-top: 30px; text-align: center; color: #666;">
            <p>报告生成时间: {str(Path().cwd())}</p>
        </div>
    </div>
</body>
</html>'''
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}")
    
    def _generate_quality_report(self, detection_result: DetectionResult,
                               segments: List[VideoSegment], output_path: Path):
        """生成质量指标报告"""
        try:
            # 计算质量指标
            total_duration = sum(s.duration for s in segments)
            avg_segment_duration = total_duration / len(segments) if segments else 0
            min_segment_duration = min(s.duration for s in segments) if segments else 0
            max_segment_duration = max(s.duration for s in segments) if segments else 0

            # 确保所有数值都是JSON可序列化的
            quality_metrics = {
                "detection_metrics": {
                    "algorithm": str(detection_result.algorithm_name),
                    "processing_time": float(detection_result.processing_time),
                    "boundaries_detected": int(len(detection_result.boundaries)),
                    "avg_confidence": float(sum(detection_result.confidence_scores) / len(detection_result.confidence_scores)) if detection_result.confidence_scores else 0.0,
                    "min_confidence": float(min(detection_result.confidence_scores)) if detection_result.confidence_scores else 0.0,
                    "max_confidence": float(max(detection_result.confidence_scores)) if detection_result.confidence_scores else 0.0,
                    "confidence_std": float(self._calculate_std(detection_result.confidence_scores)) if detection_result.confidence_scores else 0.0
                },
                "segment_metrics": {
                    "total_segments": int(len(segments)),
                    "total_duration": float(total_duration),
                    "avg_segment_duration": float(avg_segment_duration),
                    "min_segment_duration": float(min_segment_duration),
                    "max_segment_duration": float(max_segment_duration),
                    "segment_duration_std": float(self._calculate_std([s.duration for s in segments])) if segments else 0.0,
                    "segments_under_min_threshold": int(sum(1 for s in segments if s.duration < self.config.quality.min_segment_duration)),
                    "segments_over_max_threshold": int(sum(1 for s in segments if s.duration > self.config.quality.max_segment_duration))
                },
                "performance_metrics": {
                    "processing_speed_ratio": float(detection_result.processing_time / total_duration) if total_duration > 0 else 0.0,
                    "meets_speed_requirement": bool((detection_result.processing_time / total_duration) <= self.config.quality.max_processing_time_ratio) if total_duration > 0 else True,
                    "frames_per_second_processed": float(detection_result.frame_count / detection_result.processing_time) if detection_result.processing_time > 0 else 0.0
                },
                "quality_assessment": {
                    "detection_quality_score": self._calculate_detection_quality_score(detection_result, segments),
                    "segmentation_quality_score": self._calculate_segmentation_quality_score(segments),
                    "overall_quality_score": self._calculate_overall_quality_score(detection_result, segments)
                }
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(quality_metrics, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Quality metrics report generated: {output_path}")

        except Exception as e:
            self.logger.error(f"Failed to generate quality report: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def _calculate_std(self, values: List[float]) -> float:
        """计算标准差"""
        if not values or len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5

    def _calculate_detection_quality_score(self, detection_result: DetectionResult, segments: List[VideoSegment]) -> float:
        """计算检测质量分数"""
        try:
            # 基于置信度和分段数量计算质量分数
            if not detection_result.confidence_scores:
                return 0.0

            avg_confidence = sum(detection_result.confidence_scores) / len(detection_result.confidence_scores)
            confidence_consistency = 1.0 - self._calculate_std(detection_result.confidence_scores)
            segment_count_score = min(len(segments) / 10.0, 1.0)  # 假设10个分段为理想数量

            return float((avg_confidence * 0.5 + confidence_consistency * 0.3 + segment_count_score * 0.2))
        except:
            return 0.0

    def _calculate_segmentation_quality_score(self, segments: List[VideoSegment]) -> float:
        """计算分段质量分数"""
        try:
            if not segments:
                return 0.0

            # 基于分段时长分布计算质量分数
            durations = [s.duration for s in segments]
            avg_duration = sum(durations) / len(durations)
            duration_consistency = 1.0 - (self._calculate_std(durations) / avg_duration) if avg_duration > 0 else 0.0

            # 检查分段时长是否在合理范围内
            reasonable_segments = sum(1 for d in durations if 1.0 <= d <= 30.0)
            reasonable_ratio = reasonable_segments / len(segments)

            return float((duration_consistency * 0.6 + reasonable_ratio * 0.4))
        except:
            return 0.0

    def _calculate_overall_quality_score(self, detection_result: DetectionResult, segments: List[VideoSegment]) -> float:
        """计算总体质量分数"""
        try:
            detection_score = self._calculate_detection_quality_score(detection_result, segments)
            segmentation_score = self._calculate_segmentation_quality_score(segments)

            return float((detection_score * 0.6 + segmentation_score * 0.4))
        except:
            return 0.0
