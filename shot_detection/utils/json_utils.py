"""
JSON序列化工具
处理NumPy类型和其他特殊类型的JSON序列化
"""

import json
import numpy as np
from typing import Any, Dict, List, Union
from pathlib import Path


class NumpyJSONEncoder(json.JSONEncoder):
    """支持NumPy类型的JSON编码器"""
    
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, 'item'):  # numpy scalar
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy array
            return obj.tolist()
        return super().default(obj)


def safe_json_dump(data: Any, file_path: str, **kwargs) -> bool:
    """安全的JSON导出，自动处理NumPy类型"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, cls=NumpyJSONEncoder, ensure_ascii=False, indent=2, **kwargs)
        return True
    except Exception as e:
        print(f"JSON导出失败: {e}")
        return False


def safe_json_dumps(data: Any, **kwargs) -> str:
    """安全的JSON字符串转换，自动处理NumPy类型"""
    try:
        return json.dumps(data, cls=NumpyJSONEncoder, ensure_ascii=False, indent=2, **kwargs)
    except Exception as e:
        print(f"JSON字符串转换失败: {e}")
        return "{}"


def sanitize_for_json(obj: Any) -> Any:
    """递归清理对象，确保JSON可序列化"""
    if obj is None:
        return None
    elif isinstance(obj, (bool, int, float, str)):
        return obj
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, Path):
        return str(obj)
    elif hasattr(obj, 'item'):  # numpy scalar
        return obj.item()
    elif hasattr(obj, 'tolist'):  # numpy array
        return obj.tolist()
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {str(key): sanitize_for_json(value) for key, value in obj.items()}
    else:
        # 对于其他类型，尝试转换为字符串
        try:
            return str(obj)
        except:
            return f"<{type(obj).__name__}>"


def create_detection_json(detection_result, segments: List, video_path: str = "") -> Dict:
    """创建完整的检测结果JSON数据"""
    
    # 基础信息
    data = {
        "metadata": {
            "version": "1.0",
            "generated_at": str(Path().cwd()),
            "video_path": str(video_path),
            "processing_timestamp": str(Path().cwd())  # 可以替换为实际时间戳
        },
        "detection_info": {
            "algorithm": str(detection_result.algorithm_name),
            "processing_time": float(detection_result.processing_time),
            "frame_count": int(detection_result.frame_count),
            "boundaries_count": len(detection_result.boundaries)
        }
    }
    
    # 置信度统计
    if detection_result.confidence_scores:
        confidence_scores = [float(score) for score in detection_result.confidence_scores]
        data["detection_info"]["confidence_stats"] = {
            "min": min(confidence_scores),
            "max": max(confidence_scores),
            "mean": sum(confidence_scores) / len(confidence_scores),
            "count": len(confidence_scores)
        }
    else:
        data["detection_info"]["confidence_stats"] = {
            "min": 0.0,
            "max": 0.0,
            "mean": 0.0,
            "count": 0
        }
    
    # 边界信息
    data["boundaries"] = []
    for boundary in detection_result.boundaries:
        boundary_data = {
            "frame_number": int(boundary.frame_number),
            "timestamp": float(boundary.timestamp),
            "confidence": float(boundary.confidence),
            "boundary_type": str(boundary.boundary_type),
            "metadata": sanitize_for_json(boundary.metadata) if boundary.metadata else {}
        }
        data["boundaries"].append(boundary_data)
    
    # 分段信息
    data["segments"] = []
    for segment in segments:
        segment_data = {
            "index": int(segment.index),
            "start_time": float(segment.start_time),
            "end_time": float(segment.end_time),
            "duration": float(segment.duration),
            "start_frame": int(segment.start_frame),
            "end_frame": int(segment.end_frame),
            "file_path": str(segment.file_path),
            "metadata": sanitize_for_json(segment.metadata) if hasattr(segment, 'metadata') and segment.metadata else {}
        }
        data["segments"].append(segment_data)
    
    # 摘要统计
    if segments:
        durations = [float(s.duration) for s in segments]
        data["summary"] = {
            "total_segments": len(segments),
            "total_duration": sum(durations),
            "average_segment_duration": sum(durations) / len(durations),
            "shortest_segment": min(durations),
            "longest_segment": max(durations),
            "segments_by_duration": {
                "short_segments": len([d for d in durations if d <= 5.0]),
                "medium_segments": len([d for d in durations if 5.0 < d <= 30.0]),
                "long_segments": len([d for d in durations if d > 30.0])
            }
        }
    else:
        data["summary"] = {
            "total_segments": 0,
            "total_duration": 0.0,
            "average_segment_duration": 0.0,
            "shortest_segment": 0.0,
            "longest_segment": 0.0,
            "segments_by_duration": {
                "short_segments": 0,
                "medium_segments": 0,
                "long_segments": 0
            }
        }
    
    return data


def create_quality_metrics_json(detection_result, segments: List, config) -> Dict:
    """创建质量指标JSON数据"""
    
    # 计算基础指标
    total_duration = sum(float(s.duration) for s in segments) if segments else 0.0
    avg_segment_duration = total_duration / len(segments) if segments else 0.0
    
    data = {
        "detection_metrics": {
            "algorithm": str(detection_result.algorithm_name),
            "processing_time": float(detection_result.processing_time),
            "boundaries_detected": len(detection_result.boundaries),
            "processing_speed_ratio": float(detection_result.processing_time / total_duration) if total_duration > 0 else 0.0
        },
        "segment_metrics": {
            "total_segments": len(segments),
            "total_duration": total_duration,
            "avg_segment_duration": avg_segment_duration,
            "min_segment_duration": float(min(s.duration for s in segments)) if segments else 0.0,
            "max_segment_duration": float(max(s.duration for s in segments)) if segments else 0.0
        },
        "quality_thresholds": {
            "min_segment_duration": float(config.quality.min_segment_duration),
            "max_segment_duration": float(config.quality.max_segment_duration),
            "max_processing_time_ratio": float(config.quality.max_processing_time_ratio)
        },
        "quality_assessment": {
            "meets_duration_requirements": all(
                config.quality.min_segment_duration <= s.duration <= config.quality.max_segment_duration 
                for s in segments
            ) if segments else True,
            "meets_speed_requirements": (
                detection_result.processing_time / total_duration <= config.quality.max_processing_time_ratio
            ) if total_duration > 0 else True
        }
    }
    
    # 置信度指标
    if detection_result.confidence_scores:
        confidence_scores = [float(score) for score in detection_result.confidence_scores]
        data["detection_metrics"]["confidence_stats"] = {
            "min": min(confidence_scores),
            "max": max(confidence_scores),
            "mean": sum(confidence_scores) / len(confidence_scores),
            "std": float(np.std(confidence_scores)) if len(confidence_scores) > 1 else 0.0
        }
    
    return data


def export_complete_json_report(detection_result, segments: List, config, 
                               output_dir: str, video_path: str = "") -> bool:
    """导出完整的JSON报告"""
    try:
        output_path = Path(output_dir)
        
        # 导出检测结果
        detection_data = create_detection_json(detection_result, segments, video_path)
        detection_file = output_path / "detection_results.json"
        if not safe_json_dump(detection_data, str(detection_file)):
            return False
        
        # 导出质量指标
        quality_data = create_quality_metrics_json(detection_result, segments, config)
        quality_file = output_path / "quality_metrics.json"
        if not safe_json_dump(quality_data, str(quality_file)):
            return False
        
        print(f"✅ JSON报告导出成功: {output_dir}")
        return True
        
    except Exception as e:
        print(f"❌ JSON报告导出失败: {e}")
        return False
