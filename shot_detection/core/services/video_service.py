"""
Video Service Module
视频服务模块
"""

from typing import Dict, Any, Optional, Callable, List, Union
from pathlib import Path
import json
import hashlib
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

from ..detection.base import BaseDetector, DetectionResult
from ..processing.processor import VideoProcessor, ProcessingConfig
from ..processing.segmentation import SegmentationService


class VideoService:
    """视频处理服务"""

    def __init__(self, detector: BaseDetector = None,
                 processing_config: ProcessingConfig = None,
                 enable_cache: bool = True,
                 cache_dir: Optional[str] = None,
                 max_workers: int = 4):
        """
        初始化视频服务

        Args:
            detector: 检测器实例
            processing_config: 处理配置
            enable_cache: 是否启用缓存
            cache_dir: 缓存目录
            max_workers: 最大工作线程数
        """
        self.detector = detector
        self.processing_config = processing_config or ProcessingConfig()
        self.processor = VideoProcessor(self.processing_config)
        self.segmentation_service = SegmentationService()
        self.logger = logger.bind(component="VideoService")

        # 缓存配置
        self.enable_cache = enable_cache
        self.cache_dir = Path(cache_dir) if cache_dir else Path.cwd() / ".cache" / "video_service"
        if self.enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 性能监控
        self.performance_stats = {
            "total_processed": 0,
            "total_processing_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }

        # 线程池
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        self.logger.info(f"VideoService initialized with cache={'enabled' if enable_cache else 'disabled'}")

    def _get_cache_key(self, video_path: str, detector_config: Dict[str, Any] = None) -> str:
        """
        生成缓存键

        Args:
            video_path: 视频文件路径
            detector_config: 检测器配置

        Returns:
            缓存键
        """
        # 获取文件信息
        video_path = Path(video_path)
        file_stat = video_path.stat()

        # 创建唯一标识
        cache_data = {
            "file_path": str(video_path),
            "file_size": file_stat.st_size,
            "file_mtime": file_stat.st_mtime,
            "detector_name": self.detector.name if self.detector else "none",
            "detector_config": detector_config or {}
        }

        # 生成MD5哈希
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存结果

        Args:
            cache_key: 缓存键

        Returns:
            缓存的结果或None
        """
        if not self.enable_cache:
            return None

        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)

                self.performance_stats["cache_hits"] += 1
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return cached_data
        except Exception as e:
            self.logger.warning(f"Error reading cache: {e}")

        self.performance_stats["cache_misses"] += 1
        return None

    def _save_to_cache(self, cache_key: str, result: Dict[str, Any]):
        """
        保存结果到缓存

        Args:
            cache_key: 缓存键
            result: 结果数据
        """
        if not self.enable_cache:
            return

        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)

            self.logger.debug(f"Result cached with key: {cache_key}")
        except Exception as e:
            self.logger.warning(f"Error saving to cache: {e}")
    
    def detect_shots(self, video_path: str,
                    output_dir: Optional[str] = None,
                    progress_callback: Optional[Callable[[float, str], None]] = None,
                    force_reprocess: bool = False) -> Dict[str, Any]:
        """
        检测视频镜头边界

        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            progress_callback: 进度回调函数
            force_reprocess: 是否强制重新处理（忽略缓存）

        Returns:
            检测结果字典
        """
        start_time = time.time()

        try:
            self.logger.info(f"Starting shot detection for: {video_path}")

            if progress_callback:
                progress_callback(0.05, "验证输入文件...")

            # 验证输入
            video_path = Path(video_path)
            if not video_path.exists():
                raise FileNotFoundError(f"视频文件不存在: {video_path}")

            if not self.detector:
                raise ValueError("未设置检测器")

            # 检查缓存
            detector_config = getattr(self.detector, 'get_config', lambda: {})()
            cache_key = self._get_cache_key(str(video_path), detector_config)

            if not force_reprocess:
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    if progress_callback:
                        progress_callback(1.0, "从缓存加载结果")

                    self.logger.info(f"Using cached result for: {video_path}")
                    return cached_result

            if progress_callback:
                progress_callback(0.1, "初始化检测器...")

            # 初始化检测器
            if hasattr(self.detector, 'initialize'):
                if not self.detector.initialize():
                    raise RuntimeError("检测器初始化失败")

            if progress_callback:
                progress_callback(0.2, "开始检测镜头边界...")

            # 执行检测
            if hasattr(self.detector, 'detect_shots_fusion'):
                result = self.detector.detect_shots_fusion(str(video_path))
            else:
                result = self.detector.detect_shots(str(video_path))

            if progress_callback:
                progress_callback(0.7, f"检测完成，发现 {len(result.boundaries)} 个边界")

            # 构建返回结果
            detection_result = {
                "success": True,
                "video_path": str(video_path),
                "boundaries": [
                    {
                        "frame_number": b.frame_number,
                        "timestamp": b.timestamp,
                        "confidence": b.confidence,
                        "boundary_type": b.boundary_type,
                        "metadata": b.metadata or {}
                    }
                    for b in result.boundaries
                ],
                "algorithm": result.algorithm_name,
                "processing_time": result.processing_time,
                "frame_count": result.frame_count,
                "confidence_scores": result.confidence_scores,
                "metadata": result.metadata or {},
                "output_dir": output_dir,
                "cache_key": cache_key,
                "from_cache": False
            }

            # 保存到缓存
            self._save_to_cache(cache_key, detection_result)

            # 保存结果文件
            if output_dir:
                self._save_detection_result(result, video_path, output_dir)

            if progress_callback:
                progress_callback(1.0, "检测任务完成")

            # 更新性能统计
            processing_time = time.time() - start_time
            self.performance_stats["total_processed"] += 1
            self.performance_stats["total_processing_time"] += processing_time

            self.logger.info(f"Detection completed: {len(result.boundaries)} boundaries found in {processing_time:.2f}s")

            return detection_result

        except Exception as e:
            self.performance_stats["errors"] += 1
            self.logger.error(f"Shot detection failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": str(video_path) if 'video_path' in locals() else None,
                "processing_time": time.time() - start_time
            }
    
    def process_video_segments(self, video_path: str, detection_result: DetectionResult,
                              output_dir: str,
                              progress_callback: Optional[Callable[[float, str], None]] = None) -> Dict[str, Any]:
        """
        处理视频分段
        
        Args:
            video_path: 视频文件路径
            detection_result: 检测结果
            output_dir: 输出目录
            progress_callback: 进度回调函数
            
        Returns:
            处理结果字典
        """
        try:
            self.logger.info(f"Starting video segmentation for: {video_path}")
            
            if progress_callback:
                progress_callback(0.1, "准备视频分段...")
            
            # 获取视频信息
            video_info = self.processor._get_video_info(video_path)
            
            if progress_callback:
                progress_callback(0.2, "生成分段信息...")
            
            # 创建分段
            segments = self.segmentation_service.create_segments(
                detection_result.boundaries, video_info
            )
            
            if progress_callback:
                progress_callback(0.4, f"开始处理 {len(segments)} 个分段...")
            
            # 处理分段
            self.processing_config.output_dir = Path(output_dir)
            result = self.processor.process_video(
                video_path, detection_result, progress_callback
            )
            
            if progress_callback:
                progress_callback(1.0, "视频分段完成")
            
            self.logger.info(f"Video segmentation completed: {len(segments)} segments")
            
            return {
                "success": True,
                "video_path": video_path,
                "segments": segments,
                "output_dir": output_dir,
                "processing_result": result
            }
            
        except Exception as e:
            self.logger.error(f"Video segmentation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path
            }
    
    def analyze_video(self, video_path: str, 
                     analysis_types: List[str] = None) -> Dict[str, Any]:
        """
        分析视频
        
        Args:
            video_path: 视频文件路径
            analysis_types: 分析类型列表
            
        Returns:
            分析结果字典
        """
        try:
            from ..processing.analysis import AnalysisService
            
            analysis_service = AnalysisService()
            results = analysis_service.analyze_video(video_path, analysis_types)
            
            return {
                "success": True,
                "video_path": video_path,
                "analysis_results": results
            }
            
        except Exception as e:
            self.logger.error(f"Video analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path
            }
    
    def _save_detection_result(self, result: DetectionResult, 
                              video_path: Path, output_dir: str):
        """保存检测结果"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存JSON格式结果
        result_file = output_dir / f"{video_path.stem}_detection_result.json"
        
        result_data = {
            "video_path": str(video_path),
            "algorithm": result.algorithm_name,
            "processing_time": result.processing_time,
            "frame_count": result.frame_count,
            "boundaries": [
                {
                    "frame_number": b.frame_number,
                    "timestamp": b.timestamp,
                    "confidence": b.confidence,
                    "boundary_type": b.boundary_type,
                    "metadata": b.metadata or {}
                }
                for b in result.boundaries
            ],
            "confidence_scores": result.confidence_scores,
            "metadata": result.metadata or {}
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Detection result saved to: {result_file}")
        
        # 保存CSV格式结果（可选）
        self._save_csv_result(result, video_path, output_dir)
    
    def _save_csv_result(self, result: DetectionResult, 
                        video_path: Path, output_dir: Path):
        """保存CSV格式结果"""
        import csv
        
        csv_file = output_dir / f"{video_path.stem}_boundaries.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Frame', 'Timestamp', 'Confidence', 'Type'])
            
            for boundary in result.boundaries:
                writer.writerow([
                    boundary.frame_number,
                    f"{boundary.timestamp:.3f}",
                    f"{boundary.confidence:.3f}",
                    boundary.boundary_type
                ])
        
        self.logger.info(f"CSV result saved to: {csv_file}")
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的视频格式"""
        return ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
    
    def validate_video_file(self, video_path: str) -> bool:
        """验证视频文件"""
        try:
            video_path = Path(video_path)
            
            # 检查文件是否存在
            if not video_path.exists():
                return False
            
            # 检查文件扩展名
            if video_path.suffix.lower() not in self.get_supported_formats():
                return False
            
            # 检查文件大小
            if video_path.stat().st_size == 0:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Video validation failed: {e}")
            return False

    async def detect_shots_async(self, video_path: str,
                                output_dir: Optional[str] = None,
                                progress_callback: Optional[Callable[[float, str], None]] = None,
                                force_reprocess: bool = False) -> Dict[str, Any]:
        """
        异步检测视频镜头边界

        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            progress_callback: 进度回调函数
            force_reprocess: 是否强制重新处理

        Returns:
            检测结果字典
        """
        loop = asyncio.get_event_loop()

        # 在线程池中执行同步检测
        result = await loop.run_in_executor(
            self.executor,
            self.detect_shots,
            video_path,
            output_dir,
            progress_callback,
            force_reprocess
        )

        return result

    def detect_shots_batch(self, video_paths: List[str],
                          output_dir: Optional[str] = None,
                          progress_callback: Optional[Callable[[int, int, str], None]] = None,
                          force_reprocess: bool = False) -> List[Dict[str, Any]]:
        """
        批量检测视频镜头边界

        Args:
            video_paths: 视频文件路径列表
            output_dir: 输出目录
            progress_callback: 进度回调函数 (completed, total, current_file)
            force_reprocess: 是否强制重新处理

        Returns:
            检测结果列表
        """
        results = []
        total_files = len(video_paths)

        self.logger.info(f"Starting batch detection for {total_files} files")

        for i, video_path in enumerate(video_paths):
            try:
                if progress_callback:
                    progress_callback(i, total_files, Path(video_path).name)

                # 为每个文件创建单独的输出目录
                file_output_dir = None
                if output_dir:
                    file_output_dir = Path(output_dir) / Path(video_path).stem
                    file_output_dir.mkdir(parents=True, exist_ok=True)

                result = self.detect_shots(
                    video_path,
                    str(file_output_dir) if file_output_dir else None,
                    force_reprocess=force_reprocess
                )

                results.append(result)

            except Exception as e:
                self.logger.error(f"Error processing {video_path}: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "video_path": video_path
                })

        if progress_callback:
            progress_callback(total_files, total_files, "批量处理完成")

        success_count = sum(1 for r in results if r.get("success", False))
        self.logger.info(f"Batch detection completed: {success_count}/{total_files} successful")

        return results

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        获取性能统计信息

        Returns:
            性能统计字典
        """
        stats = self.performance_stats.copy()

        if stats["total_processed"] > 0:
            stats["avg_processing_time"] = stats["total_processing_time"] / stats["total_processed"]
            stats["cache_hit_rate"] = stats["cache_hits"] / (stats["cache_hits"] + stats["cache_misses"]) if (stats["cache_hits"] + stats["cache_misses"]) > 0 else 0
        else:
            stats["avg_processing_time"] = 0
            stats["cache_hit_rate"] = 0

        return stats

    def clear_cache(self) -> bool:
        """
        清空缓存

        Returns:
            是否成功清空
        """
        try:
            if self.enable_cache and self.cache_dir.exists():
                import shutil
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)

                # 重置缓存统计
                self.performance_stats["cache_hits"] = 0
                self.performance_stats["cache_misses"] = 0

                self.logger.info("Cache cleared successfully")
                return True
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
            return False

        return False

    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存信息

        Returns:
            缓存信息字典
        """
        if not self.enable_cache:
            return {"enabled": False}

        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)

            return {
                "enabled": True,
                "cache_dir": str(self.cache_dir),
                "cache_files_count": len(cache_files),
                "total_size_mb": total_size / (1024 * 1024),
                "cache_hits": self.performance_stats["cache_hits"],
                "cache_misses": self.performance_stats["cache_misses"]
            }
        except Exception as e:
            self.logger.error(f"Error getting cache info: {e}")
            return {"enabled": True, "error": str(e)}

    def cleanup(self):
        """清理资源"""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)

            if hasattr(self.detector, 'cleanup'):
                self.detector.cleanup()

            self.logger.info("VideoService cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.cleanup()

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        获取视频基本信息

        Args:
            video_path: 视频文件路径

        Returns:
            视频信息字典
        """
        try:
            from ..processing import VideoProcessor

            processor = VideoProcessor()
            info = processor.get_video_info(video_path)

            return {
                "success": True,
                "video_path": video_path,
                "info": info
            }

        except Exception as e:
            self.logger.error(f"Get video info failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path
            }

    def extract_frames(self, video_path: str, output_dir: str,
                      frame_interval: int = 30) -> Dict[str, Any]:
        """
        提取视频帧

        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            frame_interval: 帧间隔

        Returns:
            提取结果
        """
        try:
            import cv2
            from pathlib import Path

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            extracted_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    frame_filename = output_path / f"frame_{extracted_count:06d}.jpg"
                    cv2.imwrite(str(frame_filename), frame)
                    extracted_count += 1

                frame_count += 1

            cap.release()

            return {
                "success": True,
                "video_path": video_path,
                "output_dir": output_dir,
                "total_frames": frame_count,
                "extracted_frames": extracted_count,
                "frame_interval": frame_interval
            }

        except Exception as e:
            self.logger.error(f"Extract frames failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path
            }

    def create_video_preview(self, video_path: str, output_path: str,
                           duration: float = 10.0) -> Dict[str, Any]:
        """
        创建视频预览

        Args:
            video_path: 视频文件路径
            output_path: 输出文件路径
            duration: 预览时长

        Returns:
            创建结果
        """
        try:
            import subprocess

            # 使用ffmpeg创建预览
            cmd = [
                'ffmpeg', '-i', video_path,
                '-t', str(duration),
                '-vf', 'scale=640:360',
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-y', output_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "success": True,
                    "video_path": video_path,
                    "preview_path": output_path,
                    "duration": duration
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "video_path": video_path
                }

        except Exception as e:
            self.logger.error(f"Create preview failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "video_path": video_path
            }
