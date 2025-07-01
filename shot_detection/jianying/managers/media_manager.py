"""
Media Manager
媒体管理器
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from loguru import logger

from ..media_scanner import MediaScanner as LegacyMediaScanner


class MediaManager:
    """媒体管理器 - 新架构版本"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化媒体管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="MediaManager")
        
        # 保持与旧版本的兼容性
        self.legacy_scanner = LegacyMediaScanner()
        
        # 媒体配置
        self.media_config = self.config.get('media', {
            'supported_video_formats': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
            'supported_audio_formats': ['.mp3', '.wav', '.aac', '.m4a'],
            'supported_image_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.gif'],
            'min_file_size': 1024,  # 1KB
            'max_file_size': 1024 * 1024 * 1024 * 2,  # 2GB
            'scan_recursively': True
        })
        
        self.logger.info("Media manager initialized")
    
    def scan_media_directory(self, directory_path: str, 
                           scan_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        扫描媒体目录
        
        Args:
            directory_path: 目录路径
            scan_config: 扫描配置
            
        Returns:
            扫描结果
        """
        try:
            self.logger.info(f"Scanning media directory: {directory_path}")
            
            config = scan_config or {}
            
            # 使用旧版扫描器进行基础扫描
            try:
                legacy_result = self.legacy_scanner.scan_directory(directory_path)
                if legacy_result.get("success", False):
                    # 增强扫描结果
                    enhanced_result = self._enhance_scan_result(legacy_result, config)
                    return enhanced_result
            except Exception as e:
                self.logger.warning(f"Legacy scanner failed, using fallback: {e}")
            
            # 使用新的扫描逻辑
            scan_result = self._scan_directory_new(directory_path, config)
            
            self.logger.info(f"Media scan completed: {scan_result['statistics']['total_files']} files found")
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Media scan failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _scan_directory_new(self, directory_path: str, 
                           config: Dict[str, Any]) -> Dict[str, Any]:
        """新的目录扫描逻辑"""
        directory = Path(directory_path)
        if not directory.exists():
            return {
                "success": False,
                "error": f"Directory not found: {directory_path}"
            }
        
        media_files = {
            "videos": [],
            "audios": [],
            "images": []
        }
        
        statistics = {
            "total_files": 0,
            "video_files": 0,
            "audio_files": 0,
            "image_files": 0,
            "skipped_files": 0,
            "total_size": 0
        }
        
        # 扫描文件
        recursive = config.get('recursive', self.media_config['scan_recursively'])
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                file_info = self._analyze_media_file(file_path)
                
                if file_info["valid"]:
                    media_type = file_info["type"]
                    if media_type in media_files:
                        media_files[media_type].append(file_info)
                        statistics[f"{media_type[:-1]}_files"] += 1
                        statistics["total_size"] += file_info["size"]
                    
                    statistics["total_files"] += 1
                else:
                    statistics["skipped_files"] += 1
        
        return {
            "success": True,
            "directory_path": directory_path,
            "media_files": media_files,
            "statistics": statistics,
            "scan_config": config,
            "scanned_at": self._get_current_timestamp()
        }
    
    def _analyze_media_file(self, file_path: Path) -> Dict[str, Any]:
        """分析媒体文件"""
        file_info = {
            "path": str(file_path),
            "name": file_path.name,
            "size": 0,
            "type": "unknown",
            "valid": False,
            "metadata": {}
        }
        
        try:
            # 获取文件大小
            file_info["size"] = file_path.stat().st_size
            
            # 检查文件大小限制
            min_size = self.media_config["min_file_size"]
            max_size = self.media_config["max_file_size"]
            
            if not (min_size <= file_info["size"] <= max_size):
                return file_info
            
            # 根据扩展名确定文件类型
            suffix = file_path.suffix.lower()
            
            if suffix in self.media_config["supported_video_formats"]:
                file_info["type"] = "videos"
                file_info["valid"] = True
                file_info["metadata"] = self._get_video_metadata(file_path)
            elif suffix in self.media_config["supported_audio_formats"]:
                file_info["type"] = "audios"
                file_info["valid"] = True
                file_info["metadata"] = self._get_audio_metadata(file_path)
            elif suffix in self.media_config["supported_image_formats"]:
                file_info["type"] = "images"
                file_info["valid"] = True
                file_info["metadata"] = self._get_image_metadata(file_path)
            
        except Exception as e:
            self.logger.warning(f"Failed to analyze file {file_path}: {e}")
        
        return file_info
    
    def _get_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """获取视频元数据"""
        metadata = {
            "duration": 0.0,
            "resolution": (0, 0),
            "fps": 0.0,
            "codec": "unknown"
        }
        
        try:
            # 这里应该使用实际的视频分析工具
            # 暂时返回模拟数据
            metadata.update({
                "duration": 30.0,
                "resolution": (1920, 1080),
                "fps": 30.0,
                "codec": "h264"
            })
        except Exception as e:
            self.logger.warning(f"Failed to get video metadata for {file_path}: {e}")
        
        return metadata
    
    def _get_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """获取音频元数据"""
        metadata = {
            "duration": 0.0,
            "sample_rate": 0,
            "channels": 0,
            "bitrate": 0
        }
        
        try:
            # 这里应该使用实际的音频分析工具
            # 暂时返回模拟数据
            metadata.update({
                "duration": 180.0,
                "sample_rate": 44100,
                "channels": 2,
                "bitrate": 320
            })
        except Exception as e:
            self.logger.warning(f"Failed to get audio metadata for {file_path}: {e}")
        
        return metadata
    
    def _get_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """获取图片元数据"""
        metadata = {
            "resolution": (0, 0),
            "format": "unknown",
            "color_mode": "unknown"
        }
        
        try:
            # 这里应该使用实际的图片分析工具
            # 暂时返回模拟数据
            metadata.update({
                "resolution": (1920, 1080),
                "format": "JPEG",
                "color_mode": "RGB"
            })
        except Exception as e:
            self.logger.warning(f"Failed to get image metadata for {file_path}: {e}")
        
        return metadata
    
    def _enhance_scan_result(self, legacy_result: Dict[str, Any], 
                            config: Dict[str, Any]) -> Dict[str, Any]:
        """增强扫描结果"""
        enhanced = legacy_result.copy()
        
        # 添加新功能
        enhanced["version"] = "2.0"
        enhanced["enhanced_by"] = "Shot Detection v2.0"
        enhanced["scan_config"] = config
        enhanced["enhanced_at"] = self._get_current_timestamp()
        
        # 添加额外的统计信息
        if "media_files" in enhanced:
            enhanced["enhanced_statistics"] = self._calculate_enhanced_statistics(
                enhanced["media_files"]
            )
        
        return enhanced
    
    def _calculate_enhanced_statistics(self, media_files: Dict[str, List]) -> Dict[str, Any]:
        """计算增强统计信息"""
        stats = {
            "file_type_distribution": {},
            "size_distribution": {"small": 0, "medium": 0, "large": 0},
            "quality_distribution": {"high": 0, "medium": 0, "low": 0}
        }
        
        for media_type, files in media_files.items():
            stats["file_type_distribution"][media_type] = len(files)
            
            for file_info in files:
                # 大小分布
                size = file_info.get("size", 0)
                if size < 10 * 1024 * 1024:  # < 10MB
                    stats["size_distribution"]["small"] += 1
                elif size < 100 * 1024 * 1024:  # < 100MB
                    stats["size_distribution"]["medium"] += 1
                else:
                    stats["size_distribution"]["large"] += 1
                
                # 质量分布（基于分辨率等）
                metadata = file_info.get("metadata", {})
                resolution = metadata.get("resolution", (0, 0))
                if isinstance(resolution, (list, tuple)) and len(resolution) >= 2:
                    width, height = resolution[0], resolution[1]
                    if width >= 1920 and height >= 1080:
                        stats["quality_distribution"]["high"] += 1
                    elif width >= 1280 and height >= 720:
                        stats["quality_distribution"]["medium"] += 1
                    else:
                        stats["quality_distribution"]["low"] += 1
        
        return stats
    
    def create_media_inventory(self, scan_result: Dict[str, Any], 
                              output_path: Optional[str] = None) -> Dict[str, Any]:
        """创建媒体清单"""
        try:
            if not scan_result.get("success", False):
                return {
                    "success": False,
                    "error": "Invalid scan result"
                }
            
            inventory = {
                "version": "2.0",
                "created_at": self._get_current_timestamp(),
                "source_directory": scan_result.get("directory_path", ""),
                "media_files": scan_result.get("media_files", {}),
                "statistics": scan_result.get("statistics", {}),
                "enhanced_statistics": scan_result.get("enhanced_statistics", {})
            }
            
            # 保存清单文件
            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(inventory, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Media inventory saved: {output_file}")
                
                return {
                    "success": True,
                    "inventory": inventory,
                    "output_file": str(output_file)
                }
            else:
                return {
                    "success": True,
                    "inventory": inventory
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create media inventory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def filter_media_files(self, media_files: Dict[str, List], 
                          filters: Dict[str, Any]) -> Dict[str, Any]:
        """过滤媒体文件"""
        try:
            filtered_files = {
                "videos": [],
                "audios": [],
                "images": []
            }
            
            for media_type, files in media_files.items():
                for file_info in files:
                    if self._file_matches_filters(file_info, filters):
                        filtered_files[media_type].append(file_info)
            
            return {
                "success": True,
                "filtered_files": filtered_files,
                "filters_applied": filters
            }
            
        except Exception as e:
            self.logger.error(f"Failed to filter media files: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _file_matches_filters(self, file_info: Dict[str, Any], 
                             filters: Dict[str, Any]) -> bool:
        """检查文件是否匹配过滤条件"""
        # 大小过滤
        if "min_size" in filters:
            if file_info.get("size", 0) < filters["min_size"]:
                return False
        
        if "max_size" in filters:
            if file_info.get("size", 0) > filters["max_size"]:
                return False
        
        # 时长过滤（对于视频和音频）
        metadata = file_info.get("metadata", {})
        duration = metadata.get("duration", 0)
        
        if "min_duration" in filters:
            if duration < filters["min_duration"]:
                return False
        
        if "max_duration" in filters:
            if duration > filters["max_duration"]:
                return False
        
        # 分辨率过滤（对于视频和图片）
        resolution = metadata.get("resolution", (0, 0))
        if isinstance(resolution, (list, tuple)) and len(resolution) >= 2:
            width, height = resolution[0], resolution[1]
            
            if "min_resolution" in filters:
                min_w, min_h = filters["min_resolution"]
                if width < min_w or height < min_h:
                    return False
        
        return True
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("Media manager cleanup completed")
