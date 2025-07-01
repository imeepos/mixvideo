"""
Cache Optimizer
缓存优化器
"""

import os
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from loguru import logger


class CacheOptimizer:
    """缓存优化器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化缓存优化器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="CacheOptimizer")
        
        # 缓存配置
        self.cache_config = self.config.get('cache', {
            'max_cache_size_mb': 1024,  # 最大缓存大小(MB)
            'max_cache_age_hours': 24,  # 最大缓存时间(小时)
            'cleanup_interval_minutes': 30,  # 清理间隔(分钟)
            'auto_cleanup': True,  # 自动清理
            'compression_enabled': True,  # 启用压缩
            'cache_hit_threshold': 0.7  # 缓存命中率阈值
        })
        
        # 缓存统计
        self.cache_stats = {
            'total_size_mb': 0.0,
            'file_count': 0,
            'hit_count': 0,
            'miss_count': 0,
            'cleanup_count': 0,
            'last_cleanup': 0,
            'oldest_file_age': 0,
            'newest_file_age': 0
        }
        
        # 自动清理
        self.auto_cleanup_enabled = False
        self.cleanup_thread = None
        
        self.logger.info("Cache optimizer initialized")
    
    def analyze_cache_directory(self, cache_dir: str) -> Dict[str, Any]:
        """
        分析缓存目录
        
        Args:
            cache_dir: 缓存目录路径
            
        Returns:
            分析结果
        """
        try:
            cache_path = Path(cache_dir)
            if not cache_path.exists():
                return {
                    "success": False,
                    "error": f"Cache directory not found: {cache_dir}"
                }
            
            analysis = {
                "directory": str(cache_path),
                "total_files": 0,
                "total_size_mb": 0.0,
                "file_types": {},
                "age_distribution": {"new": 0, "medium": 0, "old": 0},
                "size_distribution": {"small": 0, "medium": 0, "large": 0},
                "oldest_file": None,
                "newest_file": None,
                "largest_file": None
            }
            
            current_time = time.time()
            oldest_time = current_time
            newest_time = 0
            largest_size = 0
            
            # 遍历缓存文件
            for file_path in cache_path.rglob("*"):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        file_size = stat.st_size
                        file_age = current_time - stat.st_mtime
                        
                        analysis["total_files"] += 1
                        analysis["total_size_mb"] += file_size / (1024 * 1024)
                        
                        # 文件类型统计
                        file_ext = file_path.suffix.lower()
                        analysis["file_types"][file_ext] = analysis["file_types"].get(file_ext, 0) + 1
                        
                        # 年龄分布
                        if file_age < 3600:  # 1小时内
                            analysis["age_distribution"]["new"] += 1
                        elif file_age < 86400:  # 24小时内
                            analysis["age_distribution"]["medium"] += 1
                        else:
                            analysis["age_distribution"]["old"] += 1
                        
                        # 大小分布
                        if file_size < 1024 * 1024:  # < 1MB
                            analysis["size_distribution"]["small"] += 1
                        elif file_size < 10 * 1024 * 1024:  # < 10MB
                            analysis["size_distribution"]["medium"] += 1
                        else:
                            analysis["size_distribution"]["large"] += 1
                        
                        # 记录极值
                        if stat.st_mtime < oldest_time:
                            oldest_time = stat.st_mtime
                            analysis["oldest_file"] = {
                                "path": str(file_path),
                                "age_hours": file_age / 3600,
                                "size_mb": file_size / (1024 * 1024)
                            }
                        
                        if stat.st_mtime > newest_time:
                            newest_time = stat.st_mtime
                            analysis["newest_file"] = {
                                "path": str(file_path),
                                "age_hours": file_age / 3600,
                                "size_mb": file_size / (1024 * 1024)
                            }
                        
                        if file_size > largest_size:
                            largest_size = file_size
                            analysis["largest_file"] = {
                                "path": str(file_path),
                                "size_mb": file_size / (1024 * 1024),
                                "age_hours": file_age / 3600
                            }
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to analyze file {file_path}: {e}")
            
            # 更新统计
            self.cache_stats.update({
                'total_size_mb': analysis["total_size_mb"],
                'file_count': analysis["total_files"],
                'oldest_file_age': (current_time - oldest_time) / 3600 if oldest_time < current_time else 0,
                'newest_file_age': (current_time - newest_time) / 3600 if newest_time > 0 else 0
            })
            
            self.logger.info(f"Cache analysis completed: {analysis['total_files']} files, "
                           f"{analysis['total_size_mb']:.1f}MB")
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            self.logger.error(f"Cache analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def optimize_cache(self, cache_dir: str, 
                      optimization_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        优化缓存
        
        Args:
            cache_dir: 缓存目录路径
            optimization_config: 优化配置
            
        Returns:
            优化结果
        """
        try:
            config = optimization_config or {}
            
            # 分析当前缓存状态
            analysis_result = self.analyze_cache_directory(cache_dir)
            if not analysis_result["success"]:
                return analysis_result
            
            analysis = analysis_result["analysis"]
            optimizations = []
            
            # 1. 大小优化
            max_size_mb = config.get('max_size_mb', self.cache_config['max_cache_size_mb'])
            if analysis["total_size_mb"] > max_size_mb:
                size_optimization = self._optimize_cache_size(cache_dir, max_size_mb)
                optimizations.append(size_optimization)
            
            # 2. 年龄优化
            max_age_hours = config.get('max_age_hours', self.cache_config['max_cache_age_hours'])
            if analysis["age_distribution"]["old"] > 0:
                age_optimization = self._optimize_cache_age(cache_dir, max_age_hours)
                optimizations.append(age_optimization)
            
            # 3. 压缩优化
            if config.get('enable_compression', self.cache_config['compression_enabled']):
                compression_optimization = self._optimize_cache_compression(cache_dir)
                optimizations.append(compression_optimization)
            
            # 4. 重复文件清理
            if config.get('remove_duplicates', True):
                duplicate_optimization = self._remove_duplicate_files(cache_dir)
                optimizations.append(duplicate_optimization)
            
            # 计算总体优化效果
            total_freed_mb = sum(opt.get("freed_mb", 0) for opt in optimizations)
            total_files_removed = sum(opt.get("files_removed", 0) for opt in optimizations)
            
            self.cache_stats['cleanup_count'] += 1
            self.cache_stats['last_cleanup'] = time.time()
            
            self.logger.info(f"Cache optimization completed: freed {total_freed_mb:.1f}MB, "
                           f"removed {total_files_removed} files")
            
            return {
                "success": True,
                "cache_dir": cache_dir,
                "before_analysis": analysis,
                "optimizations": optimizations,
                "total_freed_mb": total_freed_mb,
                "total_files_removed": total_files_removed
            }
            
        except Exception as e:
            self.logger.error(f"Cache optimization failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _optimize_cache_size(self, cache_dir: str, max_size_mb: float) -> Dict[str, Any]:
        """优化缓存大小"""
        try:
            cache_path = Path(cache_dir)
            files_with_stats = []
            
            # 收集文件信息
            for file_path in cache_path.rglob("*"):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        files_with_stats.append({
                            "path": file_path,
                            "size": stat.st_size,
                            "mtime": stat.st_mtime,
                            "atime": stat.st_atime
                        })
                    except Exception:
                        continue
            
            # 按访问时间排序（最久未访问的优先删除）
            files_with_stats.sort(key=lambda x: x["atime"])
            
            current_size_mb = sum(f["size"] for f in files_with_stats) / (1024 * 1024)
            target_size_mb = max_size_mb * 0.9  # 留10%缓冲
            
            freed_mb = 0
            files_removed = 0
            
            for file_info in files_with_stats:
                if current_size_mb <= target_size_mb:
                    break
                
                try:
                    file_size_mb = file_info["size"] / (1024 * 1024)
                    file_info["path"].unlink()
                    
                    current_size_mb -= file_size_mb
                    freed_mb += file_size_mb
                    files_removed += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to remove file {file_info['path']}: {e}")
            
            return {
                "type": "size_optimization",
                "freed_mb": freed_mb,
                "files_removed": files_removed,
                "target_size_mb": target_size_mb
            }
            
        except Exception as e:
            self.logger.error(f"Size optimization failed: {e}")
            return {
                "type": "size_optimization",
                "error": str(e),
                "freed_mb": 0,
                "files_removed": 0
            }
    
    def _optimize_cache_age(self, cache_dir: str, max_age_hours: float) -> Dict[str, Any]:
        """优化缓存年龄"""
        try:
            cache_path = Path(cache_dir)
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            freed_mb = 0
            files_removed = 0
            
            for file_path in cache_path.rglob("*"):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        file_age = current_time - stat.st_mtime
                        
                        if file_age > max_age_seconds:
                            file_size_mb = stat.st_size / (1024 * 1024)
                            file_path.unlink()
                            
                            freed_mb += file_size_mb
                            files_removed += 1
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to remove old file {file_path}: {e}")
            
            return {
                "type": "age_optimization",
                "freed_mb": freed_mb,
                "files_removed": files_removed,
                "max_age_hours": max_age_hours
            }
            
        except Exception as e:
            self.logger.error(f"Age optimization failed: {e}")
            return {
                "type": "age_optimization",
                "error": str(e),
                "freed_mb": 0,
                "files_removed": 0
            }
    
    def _optimize_cache_compression(self, cache_dir: str) -> Dict[str, Any]:
        """优化缓存压缩"""
        try:
            # 这里可以实现文件压缩逻辑
            # 暂时返回模拟结果
            return {
                "type": "compression_optimization",
                "freed_mb": 0,
                "files_compressed": 0,
                "compression_ratio": 0.0
            }
            
        except Exception as e:
            self.logger.error(f"Compression optimization failed: {e}")
            return {
                "type": "compression_optimization",
                "error": str(e),
                "freed_mb": 0,
                "files_compressed": 0
            }
    
    def _remove_duplicate_files(self, cache_dir: str) -> Dict[str, Any]:
        """移除重复文件"""
        try:
            import hashlib
            
            cache_path = Path(cache_dir)
            file_hashes = {}
            freed_mb = 0
            files_removed = 0
            
            for file_path in cache_path.rglob("*"):
                if file_path.is_file():
                    try:
                        # 计算文件哈希
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                        
                        if file_hash in file_hashes:
                            # 发现重复文件，删除较新的
                            existing_file = file_hashes[file_hash]
                            existing_stat = existing_file.stat()
                            current_stat = file_path.stat()
                            
                            if current_stat.st_mtime > existing_stat.st_mtime:
                                # 删除当前文件
                                file_size_mb = current_stat.st_size / (1024 * 1024)
                                file_path.unlink()
                                freed_mb += file_size_mb
                                files_removed += 1
                            else:
                                # 删除已存在的文件，更新记录
                                file_size_mb = existing_stat.st_size / (1024 * 1024)
                                existing_file.unlink()
                                file_hashes[file_hash] = file_path
                                freed_mb += file_size_mb
                                files_removed += 1
                        else:
                            file_hashes[file_hash] = file_path
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to process file {file_path}: {e}")
            
            return {
                "type": "duplicate_removal",
                "freed_mb": freed_mb,
                "files_removed": files_removed,
                "unique_files": len(file_hashes)
            }
            
        except Exception as e:
            self.logger.error(f"Duplicate removal failed: {e}")
            return {
                "type": "duplicate_removal",
                "error": str(e),
                "freed_mb": 0,
                "files_removed": 0
            }
    
    def start_auto_cleanup(self, cache_dir: str):
        """启动自动清理"""
        if self.auto_cleanup_enabled:
            self.logger.warning("Auto cleanup already started")
            return
        
        self.auto_cleanup_enabled = True
        self.cleanup_thread = threading.Thread(
            target=self._auto_cleanup_loop, 
            args=(cache_dir,), 
            daemon=True
        )
        self.cleanup_thread.start()
        
        self.logger.info("Auto cache cleanup started")
    
    def stop_auto_cleanup(self):
        """停止自动清理"""
        if not self.auto_cleanup_enabled:
            return
        
        self.auto_cleanup_enabled = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=2.0)
        
        self.logger.info("Auto cache cleanup stopped")
    
    def _auto_cleanup_loop(self, cache_dir: str):
        """自动清理循环"""
        interval_seconds = self.cache_config['cleanup_interval_minutes'] * 60
        
        while self.auto_cleanup_enabled:
            try:
                time.sleep(interval_seconds)
                if self.auto_cleanup_enabled:
                    self.optimize_cache(cache_dir)
            except Exception as e:
                self.logger.error(f"Auto cleanup error: {e}")
                time.sleep(60)  # 出错时等待1分钟再重试
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        stats = self.cache_stats.copy()
        
        # 计算缓存命中率
        total_requests = stats['hit_count'] + stats['miss_count']
        if total_requests > 0:
            stats['hit_rate'] = stats['hit_count'] / total_requests
        else:
            stats['hit_rate'] = 0.0
        
        # 添加配置信息
        stats['configuration'] = self.cache_config.copy()
        stats['auto_cleanup_enabled'] = self.auto_cleanup_enabled
        
        return stats
    
    def cleanup(self):
        """清理资源"""
        self.stop_auto_cleanup()
        self.logger.info("Cache optimizer cleanup completed")
