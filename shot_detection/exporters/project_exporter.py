"""
项目文件导出器
负责生成各种剪辑软件的项目文件
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from detectors.base import DetectionResult
from processors.video_processor import VideoSegment
from config import ConfigManager
from utils.json_utils import export_complete_json_report


class ProjectExporter:
    """项目文件导出器"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logger.bind(component="ProjectExporter")
    
    def export_all_formats(self, video_path: str, detection_result: DetectionResult,
                          segments: List[VideoSegment], output_dir: str):
        """导出所有格式的项目文件"""
        self.logger.info("Exporting project files...")

        output_path = Path(output_dir)

        # 使用新的JSON工具导出完整报告
        export_complete_json_report(detection_result, segments, self.config, str(output_path), video_path)

        # 导出CSV格式的分段信息
        self._export_csv_segments(segments, output_path / "segments_info.csv")

        # 导出EDL文件
        if self.config.output.generate_edl:
            self._export_edl(segments, output_path / "edit_decision_list.edl")

        # 导出Premiere Pro XML（简化版）
        if self.config.output.generate_premiere_xml:
            self._export_premiere_xml(segments, output_path / "premiere_project.xml")

        self.logger.info("Project files exported successfully")
    
    def _export_json_results(self, detection_result: DetectionResult,
                           segments: List[VideoSegment], output_path: Path):
        """导出JSON格式的检测结果"""
        try:
            # 转换数据，确保所有数值都是JSON可序列化的
            data = {
                "detection_info": {
                    "algorithm": str(detection_result.algorithm_name),
                    "processing_time": float(detection_result.processing_time),
                    "frame_count": int(detection_result.frame_count),
                    "boundaries_count": len(detection_result.boundaries),
                    "confidence_stats": {
                        "min": float(min(detection_result.confidence_scores)) if detection_result.confidence_scores else 0.0,
                        "max": float(max(detection_result.confidence_scores)) if detection_result.confidence_scores else 0.0,
                        "mean": float(sum(detection_result.confidence_scores) / len(detection_result.confidence_scores)) if detection_result.confidence_scores else 0.0
                    }
                },
                "boundaries": [
                    {
                        "frame_number": int(b.frame_number),
                        "timestamp": float(b.timestamp),
                        "confidence": float(b.confidence),
                        "boundary_type": str(b.boundary_type),
                        "metadata": self._sanitize_metadata(b.metadata)
                    }
                    for b in detection_result.boundaries
                ],
                "segments": [
                    {
                        "index": int(s.index),
                        "start_time": float(s.start_time),
                        "end_time": float(s.end_time),
                        "duration": float(s.duration),
                        "start_frame": int(s.start_frame),
                        "end_frame": int(s.end_frame),
                        "file_path": str(s.file_path),
                        "metadata": self._sanitize_metadata(s.metadata) if s.metadata else {}
                    }
                    for s in segments
                ],
                "summary": {
                    "total_segments": len(segments),
                    "total_duration": float(sum(s.duration for s in segments)),
                    "average_segment_duration": float(sum(s.duration for s in segments) / len(segments)) if segments else 0.0,
                    "shortest_segment": float(min(s.duration for s in segments)) if segments else 0.0,
                    "longest_segment": float(max(s.duration for s in segments)) if segments else 0.0
                }
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"JSON results exported to {output_path}")

        except Exception as e:
            self.logger.error(f"Failed to export JSON results: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def _sanitize_metadata(self, metadata: Dict) -> Dict:
        """清理元数据，确保JSON可序列化"""
        if not metadata:
            return {}

        sanitized = {}
        for key, value in metadata.items():
            try:
                # 转换numpy类型为Python原生类型
                if hasattr(value, 'item'):  # numpy scalar
                    sanitized[str(key)] = value.item()
                elif hasattr(value, 'tolist'):  # numpy array
                    sanitized[str(key)] = value.tolist()
                elif isinstance(value, (int, float, str, bool, type(None))):
                    sanitized[str(key)] = value
                elif isinstance(value, (list, tuple)):
                    sanitized[str(key)] = [self._sanitize_value(v) for v in value]
                elif isinstance(value, dict):
                    sanitized[str(key)] = self._sanitize_metadata(value)
                else:
                    sanitized[str(key)] = str(value)
            except Exception:
                sanitized[str(key)] = str(value)

        return sanitized

    def _sanitize_value(self, value):
        """清理单个值"""
        if hasattr(value, 'item'):  # numpy scalar
            return value.item()
        elif hasattr(value, 'tolist'):  # numpy array
            return value.tolist()
        elif isinstance(value, (int, float, str, bool, type(None))):
            return value
        else:
            return str(value)
    
    def _export_csv_segments(self, segments: List[VideoSegment], output_path: Path):
        """导出CSV格式的分段信息"""
        try:
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入标题行
                writer.writerow([
                    'Index', 'Start Time', 'End Time', 'Duration', 
                    'Start Frame', 'End Frame', 'File Path'
                ])
                
                # 写入数据行
                for segment in segments:
                    writer.writerow([
                        segment.index,
                        f"{segment.start_time:.3f}",
                        f"{segment.end_time:.3f}",
                        f"{segment.duration:.3f}",
                        segment.start_frame,
                        segment.end_frame,
                        segment.file_path
                    ])
            
            self.logger.info(f"CSV segments exported to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV segments: {e}")
    
    def _export_edl(self, segments: List[VideoSegment], output_path: Path):
        """导出EDL文件"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("TITLE: Shot Detection EDL\n")
                f.write("FCM: NON-DROP FRAME\n\n")
                
                for i, segment in enumerate(segments, 1):
                    # EDL格式：事件号 源卷 轨道 转场类型 源入点 源出点 记录入点 记录出点
                    f.write(f"{i:03d}  001      V     C        ")
                    f.write(f"{self._seconds_to_timecode(segment.start_time)} ")
                    f.write(f"{self._seconds_to_timecode(segment.end_time)} ")
                    f.write(f"{self._seconds_to_timecode(0 if i == 1 else sum(s.duration for s in segments[:i-1]))} ")
                    f.write(f"{self._seconds_to_timecode(sum(s.duration for s in segments[:i]))}\n")
                    f.write(f"* FROM CLIP NAME: {Path(segment.file_path).name}\n\n")
            
            self.logger.info(f"EDL exported to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export EDL: {e}")
    
    def _export_premiere_xml(self, segments: List[VideoSegment], output_path: Path):
        """导出Premiere Pro XML文件（简化版）"""
        try:
            xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xmeml version="5">
<project>
<name>Shot Detection Project</name>
<children>
<sequence>
<name>Main Sequence</name>
<rate>
<timebase>25</timebase>
<ntsc>FALSE</ntsc>
</rate>
<media>
<video>
<track>
'''
            
            current_time = 0
            for segment in segments:
                duration_frames = int(segment.duration * 25)  # 假设25fps
                
                xml_content += f'''
<clipitem>
<name>{Path(segment.file_path).name}</name>
<start>{current_time}</start>
<end>{current_time + duration_frames}</end>
<in>0</in>
<out>{duration_frames}</out>
<file>
<name>{Path(segment.file_path).name}</name>
<pathurl>file://{segment.file_path}</pathurl>
</file>
</clipitem>
'''
                current_time += duration_frames
            
            xml_content += '''
</track>
</video>
</media>
</sequence>
</children>
</project>
</xmeml>'''
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            self.logger.info(f"Premiere XML exported to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export Premiere XML: {e}")
    
    def _seconds_to_timecode(self, seconds: float) -> str:
        """将秒数转换为时间码格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        frames = int((seconds % 1) * 25)  # 假设25fps
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"
