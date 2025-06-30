"""
文件组织器模块
参考video-analyzer实现，负责视频分段的自动归类和文件管理
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import datetime
from loguru import logger

from classification_config import ClassificationManager, get_classification_manager


@dataclass
class FileOperationResult:
    """文件操作结果"""
    success: bool
    original_path: str
    new_path: Optional[str] = None
    operation: str = "skip"  # move, copy, skip
    error: Optional[str] = None
    backup_path: Optional[str] = None
    category: Optional[str] = None
    confidence: float = 0.0


class FileOrganizer:
    """文件组织器"""
    
    def __init__(self, classification_manager: ClassificationManager = None):
        self.classification_manager = classification_manager or get_classification_manager()
        self.operation_history: List[FileOperationResult] = []
    
    def organize_segment(self, 
                        segment_file: str, 
                        segment_info: Dict,
                        target_base_dir: str = None) -> FileOperationResult:
        """组织单个视频分段"""
        try:
            # 检查是否启用归类
            if not self.classification_manager.config.enable_classification:
                return FileOperationResult(
                    success=True,
                    original_path=segment_file,
                    operation="skip",
                    error="Classification disabled"
                )
            
            # 分类分段
            category = self.classification_manager.classify_segment(segment_info)
            confidence = segment_info.get('confidence', 1.0)
            
            # 检查置信度阈值
            if not self.classification_manager.should_move_file(confidence):
                return FileOperationResult(
                    success=True,
                    original_path=segment_file,
                    operation="skip",
                    category=category,
                    confidence=confidence,
                    error=f"Confidence {confidence:.2f} below threshold {self.classification_manager.config.min_confidence_for_move}"
                )
            
            # 确定目标目录
            if target_base_dir:
                target_dir = os.path.join(target_base_dir, category)
            else:
                target_dir = self.classification_manager.get_output_directory(category)
            
            # 确保目标目录存在
            if self.classification_manager.config.create_directories:
                Path(target_dir).mkdir(parents=True, exist_ok=True)
            
            # 生成新文件名
            original_name = os.path.basename(segment_file)
            new_filename = self.classification_manager.generate_filename(
                original_name, segment_info, category
            )
            new_path = os.path.join(target_dir, new_filename)
            
            # 处理文件名冲突
            new_path = self._resolve_file_conflict(new_path)
            
            # 执行文件操作
            operation = "move" if self.classification_manager.config.move_files else "copy"
            backup_path = None
            
            if operation == "move":
                # 创建备份（如果需要）
                if self.classification_manager.config.create_backup:
                    backup_path = self._create_backup(segment_file)
                
                shutil.move(segment_file, new_path)
                logger.info(f"📦 移动文件: {segment_file} -> {new_path}")
            else:
                shutil.copy2(segment_file, new_path)
                logger.info(f"📋 复制文件: {segment_file} -> {new_path}")
            
            result = FileOperationResult(
                success=True,
                original_path=segment_file,
                new_path=new_path,
                operation=operation,
                backup_path=backup_path,
                category=category,
                confidence=confidence
            )
            
            self.operation_history.append(result)
            return result
            
        except Exception as e:
            error_msg = f"文件组织失败: {str(e)}"
            logger.error(error_msg)
            
            result = FileOperationResult(
                success=False,
                original_path=segment_file,
                operation="error",
                error=error_msg,
                category=category if 'category' in locals() else None,
                confidence=confidence if 'confidence' in locals() else 0.0
            )
            
            self.operation_history.append(result)
            return result
    
    def organize_segments_batch(self, 
                               segments: List[Tuple[str, Dict]], 
                               target_base_dir: str = None) -> List[FileOperationResult]:
        """批量组织视频分段"""
        results = []
        
        logger.info(f"🗂️ 开始批量组织 {len(segments)} 个视频分段")
        
        for i, (segment_file, segment_info) in enumerate(segments):
            logger.info(f"处理分段 {i+1}/{len(segments)}: {os.path.basename(segment_file)}")
            
            result = self.organize_segment(segment_file, segment_info, target_base_dir)
            results.append(result)
            
            # 记录进度
            if (i + 1) % 10 == 0:
                success_count = sum(1 for r in results if r.success)
                logger.info(f"已处理 {i+1}/{len(segments)} 个分段，成功 {success_count} 个")
        
        # 生成总结报告
        self._generate_batch_summary(results)
        
        return results
    
    def _resolve_file_conflict(self, file_path: str) -> str:
        """解决文件名冲突"""
        if not os.path.exists(file_path):
            return file_path
        
        conflict_resolution = self.classification_manager.config.conflict_resolution
        
        if conflict_resolution == "skip":
            return file_path
        elif conflict_resolution == "overwrite":
            return file_path
        elif conflict_resolution == "rename":
            return self._generate_unique_filename(file_path)
        else:
            return file_path
    
    def _generate_unique_filename(self, file_path: str) -> str:
        """生成唯一文件名"""
        path = Path(file_path)
        base_name = path.stem
        suffix = path.suffix
        parent = path.parent
        
        counter = 1
        while True:
            new_name = f"{base_name}_{counter:03d}{suffix}"
            new_path = parent / new_name
            
            if not new_path.exists():
                return str(new_path)
            
            counter += 1
            
            # 防止无限循环
            if counter > 999:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{base_name}_{timestamp}{suffix}"
                return str(parent / new_name)
    
    def _create_backup(self, file_path: str) -> str:
        """创建文件备份"""
        backup_dir = Path(self.classification_manager.config.base_output_dir) / "backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        file_name = os.path.basename(file_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{Path(file_name).stem}_{timestamp}{Path(file_name).suffix}"
        backup_path = backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"💾 创建备份: {backup_path}")
        
        return str(backup_path)
    
    def _generate_batch_summary(self, results: List[FileOperationResult]):
        """生成批量操作总结"""
        total = len(results)
        success = sum(1 for r in results if r.success)
        failed = total - success
        
        # 按操作类型统计
        operations = {}
        categories = {}
        
        for result in results:
            if result.success:
                operations[result.operation] = operations.get(result.operation, 0) + 1
                if result.category:
                    categories[result.category] = categories.get(result.category, 0) + 1
        
        logger.info("📊 批量组织操作总结:")
        logger.info(f"  总计: {total} 个分段")
        logger.info(f"  成功: {success} 个")
        logger.info(f"  失败: {failed} 个")
        
        if operations:
            logger.info("  操作统计:")
            for op, count in operations.items():
                logger.info(f"    {op}: {count} 个")
        
        if categories:
            logger.info("  分类统计:")
            for cat, count in categories.items():
                logger.info(f"    {cat}: {count} 个")
    
    def get_operation_summary(self) -> Dict:
        """获取操作总结"""
        total = len(self.operation_history)
        success = sum(1 for r in self.operation_history if r.success)
        
        operations = {}
        categories = {}
        errors = []
        
        for result in self.operation_history:
            if result.success:
                operations[result.operation] = operations.get(result.operation, 0) + 1
                if result.category:
                    categories[result.category] = categories.get(result.category, 0) + 1
            else:
                errors.append(result.error)
        
        return {
            'total': total,
            'success': success,
            'failed': total - success,
            'operations': operations,
            'categories': categories,
            'errors': errors
        }
    
    def undo_last_operation(self) -> bool:
        """撤销最后一次操作"""
        if not self.operation_history:
            logger.warning("没有可撤销的操作")
            return False
        
        last_operation = self.operation_history[-1]
        
        if not last_operation.success or not last_operation.new_path:
            logger.warning("最后一次操作无法撤销")
            return False
        
        try:
            if last_operation.operation == "move":
                # 移动回原位置
                shutil.move(last_operation.new_path, last_operation.original_path)
                logger.info(f"🔄 撤销移动: {last_operation.new_path} -> {last_operation.original_path}")
            elif last_operation.operation == "copy":
                # 删除复制的文件
                os.remove(last_operation.new_path)
                logger.info(f"🗑️ 删除复制文件: {last_operation.new_path}")
            
            # 从历史记录中移除
            self.operation_history.pop()
            return True
            
        except Exception as e:
            logger.error(f"撤销操作失败: {str(e)}")
            return False
    
    def clear_history(self):
        """清空操作历史"""
        self.operation_history.clear()
        logger.info("🧹 已清空操作历史")


def create_file_organizer(classification_manager: ClassificationManager = None) -> FileOrganizer:
    """创建文件组织器实例"""
    return FileOrganizer(classification_manager)
