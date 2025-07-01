"""
Workflow Service Module
工作流服务模块
"""

from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import json
from datetime import datetime
from loguru import logger

from .video_service import VideoService
from .batch_service import BatchService
from .analysis_service import AdvancedAnalysisService
from ..detection import FrameDifferenceDetector, HistogramDetector, MultiDetector
from ..processing import ProcessingConfig
from config import get_config


class WorkflowService:
    """工作流服务 - 整合所有功能的高级服务"""
    
    def __init__(self, config_override: Optional[Dict[str, Any]] = None):
        """
        初始化工作流服务
        
        Args:
            config_override: 配置覆盖
        """
        self.config = get_config()
        if config_override:
            self.config.update(config_override)
        
        self.logger = logger.bind(component="WorkflowService")
        
        # 初始化各种服务
        self._initialize_services()
        
        self.logger.info("WorkflowService initialized")
    
    def _initialize_services(self):
        """初始化各种服务"""
        # 获取配置
        detection_config = self.config.get_detection_config()
        processing_config_dict = self.config.get_processing_config()
        
        # 创建检测器
        self.detector = self._create_detector(detection_config)
        
        # 创建处理配置
        self.processing_config = ProcessingConfig(
            output_format=processing_config_dict.get('output', {}).get('format', 'mp4'),
            quality=processing_config_dict.get('output', {}).get('quality', 'medium'),
            min_segment_duration=processing_config_dict.get('segmentation', {}).get('min_segment_duration', 1.0),
            max_segment_duration=processing_config_dict.get('segmentation', {}).get('max_segment_duration', 300.0)
        )
        
        # 创建服务实例
        self.video_service = VideoService(
            detector=self.detector,
            processing_config=self.processing_config,
            enable_cache=True
        )
        
        self.batch_service = BatchService(
            detector=self.detector,
            processing_config=self.processing_config,
            max_workers=4
        )
        
        self.analysis_service = AdvancedAnalysisService(
            video_service=self.video_service
        )
    
    def _create_detector(self, detection_config: Dict[str, Any]):
        """创建检测器"""
        detector_type = detection_config.get('default_detector', 'multi_detector')
        
        if detector_type == 'frame_difference':
            threshold = detection_config.get('frame_difference', {}).get('threshold', 0.3)
            return FrameDifferenceDetector(threshold=threshold)
        
        elif detector_type == 'histogram':
            threshold = detection_config.get('histogram', {}).get('threshold', 0.5)
            return HistogramDetector(threshold=threshold)
        
        else:  # multi_detector
            # 创建多检测器
            detectors = []
            
            fd_config = detection_config.get('frame_difference', {})
            hist_config = detection_config.get('histogram', {})
            
            detectors.append(FrameDifferenceDetector(threshold=fd_config.get('threshold', 0.3)))
            detectors.append(HistogramDetector(threshold=hist_config.get('threshold', 0.5)))
            
            fusion_weights = detection_config.get('multi_detector', {}).get('fusion_weights', {})
            
            return MultiDetector(detectors, fusion_weights)
    
    def process_single_video(self, video_path: str, output_dir: str,
                           include_analysis: bool = True,
                           progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict[str, Any]:
        """
        处理单个视频的完整工作流
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            include_analysis: 是否包含高级分析
            progress_callback: 进度回调函数
            
        Returns:
            处理结果
        """
        try:
            self.logger.info(f"Starting complete workflow for: {video_path}")
            
            if progress_callback:
                progress_callback(0.1, "开始镜头检测...")
            
            # 步骤1: 镜头检测
            detection_result = self.video_service.detect_shots(
                video_path, output_dir, 
                lambda p, s: progress_callback(0.1 + p * 0.4, s) if progress_callback else None
            )
            
            if not detection_result["success"]:
                return detection_result
            
            # 步骤2: 高级分析（可选）
            analysis_result = None
            if include_analysis:
                if progress_callback:
                    progress_callback(0.5, "进行高级分析...")
                
                # 重构检测结果为DetectionResult对象
                from ..detection.base import DetectionResult, ShotBoundary
                
                boundaries = [
                    ShotBoundary(
                        frame_number=b["frame_number"],
                        timestamp=b["timestamp"],
                        confidence=b["confidence"],
                        boundary_type=b["boundary_type"],
                        metadata=b.get("metadata", {})
                    )
                    for b in detection_result["boundaries"]
                ]
                
                detection_obj = DetectionResult(
                    boundaries=boundaries,
                    algorithm_name=detection_result["algorithm"],
                    processing_time=detection_result["processing_time"],
                    frame_count=detection_result["frame_count"],
                    confidence_scores=detection_result["confidence_scores"]
                )
                
                analysis_result = self.analysis_service.analyze_video_comprehensive(
                    video_path, detection_obj,
                    lambda p, s: progress_callback(0.5 + p * 0.4, s) if progress_callback else None
                )
            
            if progress_callback:
                progress_callback(0.9, "生成最终报告...")
            
            # 步骤3: 生成综合报告
            final_result = self._generate_workflow_report(
                video_path, detection_result, analysis_result, output_dir
            )
            
            if progress_callback:
                progress_callback(1.0, "工作流完成")
            
            self.logger.info(f"Complete workflow finished for: {video_path}")
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path
            }
    
    def process_batch_videos(self, video_paths: List[str], output_dir: str,
                           include_analysis: bool = True,
                           progress_callback: Optional[Callable[[int, int, str], None]] = None) -> Dict[str, Any]:
        """
        批量处理视频的完整工作流
        
        Args:
            video_paths: 视频文件路径列表
            output_dir: 输出目录
            include_analysis: 是否包含高级分析
            progress_callback: 进度回调函数
            
        Returns:
            批量处理结果
        """
        try:
            self.logger.info(f"Starting batch workflow for {len(video_paths)} videos")
            
            results = []
            total_files = len(video_paths)
            
            for i, video_path in enumerate(video_paths):
                if progress_callback:
                    progress_callback(i, total_files, Path(video_path).name)
                
                # 为每个视频创建单独的输出目录
                video_output_dir = Path(output_dir) / Path(video_path).stem
                video_output_dir.mkdir(parents=True, exist_ok=True)
                
                # 处理单个视频
                result = self.process_single_video(
                    video_path, str(video_output_dir), include_analysis
                )
                
                results.append(result)
            
            if progress_callback:
                progress_callback(total_files, total_files, "批量处理完成")
            
            # 生成批量报告
            batch_report = self._generate_batch_report(results, output_dir)
            
            success_count = sum(1 for r in results if r.get("success", False))
            
            return {
                "success": True,
                "total_files": total_files,
                "success_count": success_count,
                "failed_count": total_files - success_count,
                "results": results,
                "batch_report": batch_report,
                "output_dir": output_dir
            }
            
        except Exception as e:
            self.logger.error(f"Batch workflow failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_files": len(video_paths) if 'video_paths' in locals() else 0
            }
    
    def _generate_workflow_report(self, video_path: str, detection_result: Dict[str, Any],
                                 analysis_result: Optional[Dict[str, Any]], output_dir: str) -> Dict[str, Any]:
        """生成工作流报告"""
        report = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "video_path": video_path,
            "output_dir": output_dir,
            "detection_result": detection_result,
            "analysis_result": analysis_result,
            "workflow_summary": {
                "total_shots": len(detection_result.get("boundaries", [])),
                "processing_time": detection_result.get("processing_time", 0),
                "algorithm_used": detection_result.get("algorithm", "unknown"),
                "analysis_included": analysis_result is not None
            }
        }
        
        # 保存报告
        report_file = Path(output_dir) / "workflow_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Workflow report saved to: {report_file}")
        
        return report
    
    def _generate_batch_report(self, results: List[Dict[str, Any]], output_dir: str) -> str:
        """生成批量处理报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = Path(output_dir) / f"batch_workflow_report_{timestamp}.json"
        
        # 统计信息
        total_files = len(results)
        success_count = sum(1 for r in results if r.get("success", False))
        failed_count = total_files - success_count
        
        total_shots = sum(
            len(r.get("detection_result", {}).get("boundaries", []))
            for r in results if r.get("success", False)
        )
        
        total_processing_time = sum(
            r.get("detection_result", {}).get("processing_time", 0)
            for r in results if r.get("success", False)
        )
        
        batch_report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": total_files,
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": success_count / total_files if total_files > 0 else 0,
                "total_shots_detected": total_shots,
                "total_processing_time": total_processing_time,
                "avg_processing_time": total_processing_time / success_count if success_count > 0 else 0
            },
            "results": results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(batch_report, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.info(f"Batch report saved to: {report_file}")
        
        return str(report_file)
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "video_service": {
                "performance_stats": self.video_service.get_performance_stats(),
                "cache_info": self.video_service.get_cache_info()
            },
            "batch_service": {
                "status": self.batch_service.get_processing_status()
            },
            "detector_info": {
                "name": self.detector.name if hasattr(self.detector, 'name') else "unknown",
                "type": type(self.detector).__name__
            },
            "config": {
                "detection": self.config.get_detection_config(),
                "processing": self.config.get_processing_config()
            }
        }
    
    def cleanup(self):
        """清理所有服务资源"""
        try:
            self.video_service.cleanup()
            self.batch_service.stop_processing()
            
            if hasattr(self.detector, 'cleanup'):
                self.detector.cleanup()
            
            self.logger.info("WorkflowService cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.cleanup()
