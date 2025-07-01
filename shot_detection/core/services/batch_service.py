"""
Batch Service Module
批量处理服务模块
"""

from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import concurrent.futures
from loguru import logger

from .video_service import VideoService
from ..detection.base import BaseDetector
from ..processing.processor import ProcessingConfig


class BatchService:
    """批量处理服务"""
    
    def __init__(self, detector: BaseDetector = None,
                 processing_config: ProcessingConfig = None,
                 max_workers: int = 4):
        """
        初始化批量处理服务
        
        Args:
            detector: 检测器实例
            processing_config: 处理配置
            max_workers: 最大工作线程数
        """
        self.video_service = VideoService(detector, processing_config)
        self.max_workers = max_workers
        self.logger = logger.bind(component="BatchService")
        self._stop_requested = False
    
    def scan_video_files(self, input_dir: str, recursive: bool = True,
                        min_size_mb: float = 1.0, max_size_mb: float = 1000.0) -> List[Dict[str, Any]]:
        """
        扫描视频文件
        
        Args:
            input_dir: 输入目录
            recursive: 是否递归搜索
            min_size_mb: 最小文件大小(MB)
            max_size_mb: 最大文件大小(MB)
            
        Returns:
            视频文件信息列表
        """
        try:
            input_dir = Path(input_dir)
            if not input_dir.exists():
                raise FileNotFoundError(f"输入目录不存在: {input_dir}")
            
            video_files = []
            supported_formats = self.video_service.get_supported_formats()
            
            # 搜索模式
            pattern = "**/*" if recursive else "*"
            
            for file_path in input_dir.glob(pattern):
                if not file_path.is_file():
                    continue
                
                # 检查文件扩展名
                if file_path.suffix.lower() not in supported_formats:
                    continue
                
                # 检查文件大小
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                if not (min_size_mb <= file_size_mb <= max_size_mb):
                    continue
                
                # 验证视频文件
                if not self.video_service.validate_video_file(str(file_path)):
                    continue
                
                # 获取基本信息
                file_info = {
                    "path": str(file_path),
                    "name": file_path.name,
                    "size_mb": file_size_mb,
                    "relative_path": str(file_path.relative_to(input_dir)),
                    "status": "待处理"
                }
                
                # 尝试获取视频时长（可选）
                try:
                    video_info = self.video_service.processor._get_video_info(str(file_path))
                    file_info["duration"] = video_info.get("duration", 0.0)
                    file_info["fps"] = video_info.get("fps", 0.0)
                    file_info["resolution"] = f"{video_info.get('width', 0)}x{video_info.get('height', 0)}"
                except Exception:
                    file_info["duration"] = 0.0
                    file_info["fps"] = 0.0
                    file_info["resolution"] = "未知"
                
                video_files.append(file_info)
            
            self.logger.info(f"Found {len(video_files)} video files in {input_dir}")
            return video_files
            
        except Exception as e:
            self.logger.error(f"Error scanning video files: {e}")
            return []
    
    def process_batch(self, video_files: List[Dict[str, Any]], output_dir: str,
                     progress_callback: Optional[Callable[[int, int, str], None]] = None) -> Dict[str, Any]:
        """
        批量处理视频文件
        
        Args:
            video_files: 视频文件信息列表
            output_dir: 输出目录
            progress_callback: 进度回调函数 (processed_count, total_count, current_file)
            
        Returns:
            批量处理结果
        """
        try:
            self.logger.info(f"Starting batch processing of {len(video_files)} files")
            
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            results = []
            self._stop_requested = False
            
            # 使用线程池进行并行处理
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # 提交所有任务
                future_to_file = {
                    executor.submit(self._process_single_file, file_info, output_dir): file_info
                    for file_info in video_files
                }
                
                processed_count = 0
                total_count = len(video_files)
                
                # 处理完成的任务
                for future in concurrent.futures.as_completed(future_to_file):
                    if self._stop_requested:
                        # 取消剩余任务
                        for f in future_to_file:
                            f.cancel()
                        break
                    
                    file_info = future_to_file[future]
                    
                    try:
                        result = future.result()
                        results.append(result)
                        
                        processed_count += 1
                        
                        if progress_callback:
                            progress_callback(processed_count, total_count, file_info["name"])
                        
                        status = "成功" if result["success"] else "失败"
                        self.logger.info(f"Processed {file_info['name']}: {status}")
                        
                    except Exception as e:
                        self.logger.error(f"Error processing {file_info['name']}: {e}")
                        results.append({
                            "success": False,
                            "file_info": file_info,
                            "error": str(e)
                        })
                        processed_count += 1
                        
                        if progress_callback:
                            progress_callback(processed_count, total_count, file_info["name"])
            
            # 生成批量处理报告
            report = self._generate_batch_report(results, output_dir)
            
            success_count = sum(1 for r in results if r["success"])
            self.logger.info(f"Batch processing completed: {success_count}/{len(results)} successful")
            
            return {
                "success": True,
                "total_files": len(video_files),
                "processed_files": len(results),
                "success_count": success_count,
                "failed_count": len(results) - success_count,
                "results": results,
                "report_file": report,
                "output_dir": str(output_dir)
            }
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "total_files": len(video_files) if 'video_files' in locals() else 0
            }
    
    def _process_single_file(self, file_info: Dict[str, Any], output_dir: Path) -> Dict[str, Any]:
        """处理单个文件"""
        try:
            video_path = file_info["path"]
            file_output_dir = output_dir / Path(video_path).stem
            
            # 执行检测
            result = self.video_service.detect_shots(
                video_path, str(file_output_dir)
            )
            
            return {
                "success": result["success"],
                "file_info": file_info,
                "detection_result": result,
                "output_dir": str(file_output_dir)
            }
            
        except Exception as e:
            return {
                "success": False,
                "file_info": file_info,
                "error": str(e)
            }
    
    def _generate_batch_report(self, results: List[Dict[str, Any]], output_dir: Path) -> str:
        """生成批量处理报告"""
        import json
        from datetime import datetime
        
        report_file = output_dir / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 统计信息
        total_files = len(results)
        success_count = sum(1 for r in results if r["success"])
        failed_count = total_files - success_count
        
        # 处理时间统计
        processing_times = []
        boundary_counts = []
        
        for result in results:
            if result["success"] and "detection_result" in result:
                detection_result = result["detection_result"]
                if "processing_time" in detection_result:
                    processing_times.append(detection_result["processing_time"])
                if "boundaries" in detection_result:
                    boundary_counts.append(len(detection_result["boundaries"]))
        
        # 生成报告
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": total_files,
                "success_count": success_count,
                "failed_count": failed_count,
                "success_rate": success_count / total_files if total_files > 0 else 0
            },
            "statistics": {
                "avg_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0,
                "total_processing_time": sum(processing_times),
                "avg_boundaries_per_video": sum(boundary_counts) / len(boundary_counts) if boundary_counts else 0,
                "total_boundaries": sum(boundary_counts)
            },
            "results": results
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Batch report saved to: {report_file}")
        return str(report_file)
    
    def stop_processing(self):
        """停止批量处理"""
        self._stop_requested = True
        self.logger.info("Batch processing stop requested")
    
    def get_processing_status(self) -> Dict[str, Any]:
        """获取处理状态"""
        return {
            "is_processing": not self._stop_requested,
            "max_workers": self.max_workers
        }

    def create_batch_report(self, results: List[Dict[str, Any]],
                           output_dir: str) -> str:
        """
        创建批量处理报告

        Args:
            results: 处理结果列表
            output_dir: 输出目录

        Returns:
            报告文件路径
        """
        try:
            from datetime import datetime
            import json

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 生成报告数据
            timestamp = datetime.now()
            report_data = {
                "timestamp": timestamp.isoformat(),
                "summary": {
                    "total_files": len(results),
                    "success_count": sum(1 for r in results if r.get("success", False)),
                    "failed_count": sum(1 for r in results if not r.get("success", False)),
                    "total_processing_time": sum(r.get("processing_time", 0) for r in results),
                    "total_boundaries": sum(len(r.get("boundaries", [])) for r in results if r.get("success", False))
                },
                "results": results
            }

            # 保存JSON报告
            json_file = output_path / f"batch_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)

            # 保存CSV报告
            csv_file = output_path / f"batch_summary_{timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
            self._create_csv_report(results, csv_file)

            self.logger.info(f"Batch report created: {json_file}")
            return str(json_file)

        except Exception as e:
            self.logger.error(f"Create batch report failed: {e}")
            return ""

    def _create_csv_report(self, results: List[Dict[str, Any]], csv_file: Path):
        """创建CSV报告"""
        try:
            import csv

            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # 写入标题行
                writer.writerow([
                    '文件名', '状态', '处理时间(秒)', '检测边界数',
                    '文件大小(MB)', '时长(秒)', '错误信息'
                ])

                # 写入数据行
                for result in results:
                    file_info = result.get('file_info', {})

                    writer.writerow([
                        file_info.get('name', ''),
                        '成功' if result.get('success', False) else '失败',
                        f"{result.get('processing_time', 0):.2f}",
                        len(result.get('boundaries', [])),
                        f"{file_info.get('size_mb', 0):.1f}",
                        f"{file_info.get('duration', 0):.1f}",
                        result.get('error', '')
                    ])

        except Exception as e:
            self.logger.error(f"Create CSV report failed: {e}")

    def get_batch_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取批量处理统计信息

        Args:
            results: 处理结果列表

        Returns:
            统计信息字典
        """
        try:
            total_files = len(results)
            success_results = [r for r in results if r.get("success", False)]
            failed_results = [r for r in results if not r.get("success", False)]

            # 基本统计
            stats = {
                "total_files": total_files,
                "success_count": len(success_results),
                "failed_count": len(failed_results),
                "success_rate": len(success_results) / total_files if total_files > 0 else 0
            }

            if success_results:
                # 处理时间统计
                processing_times = [r.get("processing_time", 0) for r in success_results]
                stats.update({
                    "total_processing_time": sum(processing_times),
                    "avg_processing_time": sum(processing_times) / len(processing_times),
                    "min_processing_time": min(processing_times),
                    "max_processing_time": max(processing_times)
                })

                # 边界检测统计
                boundary_counts = [len(r.get("boundaries", [])) for r in success_results]
                stats.update({
                    "total_boundaries": sum(boundary_counts),
                    "avg_boundaries_per_file": sum(boundary_counts) / len(boundary_counts),
                    "min_boundaries": min(boundary_counts),
                    "max_boundaries": max(boundary_counts)
                })

                # 文件大小统计
                file_sizes = [r.get("file_info", {}).get("size_mb", 0) for r in success_results]
                if file_sizes:
                    stats.update({
                        "total_file_size_mb": sum(file_sizes),
                        "avg_file_size_mb": sum(file_sizes) / len(file_sizes),
                        "min_file_size_mb": min(file_sizes),
                        "max_file_size_mb": max(file_sizes)
                    })

            # 错误统计
            if failed_results:
                error_types = {}
                for result in failed_results:
                    error = result.get("error", "Unknown error")
                    error_type = error.split(":")[0] if ":" in error else error
                    error_types[error_type] = error_types.get(error_type, 0) + 1

                stats["error_types"] = error_types

            return stats

        except Exception as e:
            self.logger.error(f"Get batch statistics failed: {e}")
            return {"error": str(e)}
