"""
GUI日志处理器
为GUI界面提供实时日志显示功能
"""

import logging
import queue
import threading
import time
from typing import Callable, Optional


class GUILogHandler(logging.Handler):
    """GUI日志处理器"""
    
    def __init__(self, log_callback: Callable[[str, str], None]):
        super().__init__()
        self.log_callback = log_callback
        self.log_queue = queue.Queue()
        self.running = True
        
        # 启动日志处理线程
        self.log_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.log_thread.start()
    
    def emit(self, record):
        """发送日志记录"""
        try:
            msg = self.format(record)
            level = record.levelname
            self.log_queue.put((msg, level))
        except Exception:
            self.handleError(record)
    
    def _process_logs(self):
        """处理日志队列"""
        while self.running:
            try:
                msg, level = self.log_queue.get(timeout=1)
                if self.log_callback:
                    self.log_callback(msg, level)
            except queue.Empty:
                continue
            except Exception:
                break
    
    def close(self):
        """关闭处理器"""
        self.running = False
        super().close()


class ProgressMonitor:
    """进度监控器"""
    
    def __init__(self, progress_callback: Callable[[float, str], None]):
        self.progress_callback = progress_callback
        self.current_step = 0
        self.total_steps = 0
        self.step_descriptions = []
    
    def set_steps(self, steps: list):
        """设置处理步骤"""
        self.step_descriptions = steps
        self.total_steps = len(steps)
        self.current_step = 0
    
    def next_step(self, description: Optional[str] = None):
        """进入下一步"""
        if self.current_step < self.total_steps:
            if description:
                step_desc = description
            else:
                step_desc = self.step_descriptions[self.current_step] if self.current_step < len(self.step_descriptions) else f"步骤 {self.current_step + 1}"
            
            progress = (self.current_step / self.total_steps) * 100
            self.progress_callback(progress, step_desc)
            self.current_step += 1
    
    def set_progress(self, progress: float, description: str):
        """设置具体进度"""
        self.progress_callback(progress, description)
    
    def complete(self):
        """完成所有步骤"""
        self.progress_callback(100.0, "处理完成")


def setup_gui_logging(log_callback: Callable[[str, str], None]) -> GUILogHandler:
    """设置GUI日志"""
    # 创建GUI日志处理器
    gui_handler = GUILogHandler(log_callback)
    gui_handler.setLevel(logging.INFO)
    
    # 设置日志格式
    formatter = logging.Formatter('%(message)s')
    gui_handler.setFormatter(formatter)
    
    # 添加到loguru的处理器中
    try:
        from loguru import logger
        
        # 移除默认处理器
        logger.remove()
        
        # 添加GUI处理器
        def gui_sink(message):
            record = message.record
            level_name = record["level"].name
            msg = record["message"]
            log_callback(msg, level_name)
        
        logger.add(gui_sink, level="INFO")
        
    except ImportError:
        # 如果没有loguru，使用标准logging
        root_logger = logging.getLogger()
        root_logger.addHandler(gui_handler)
        root_logger.setLevel(logging.INFO)
    
    return gui_handler


class ProcessingStatus:
    """处理状态管理"""
    
    def __init__(self):
        self.is_running = False
        self.current_phase = ""
        self.start_time = None
        self.end_time = None
        self.error_message = ""
        self.results = {}
    
    def start(self, phase: str = ""):
        """开始处理"""
        import time
        self.is_running = True
        self.current_phase = phase
        self.start_time = time.time()
        self.end_time = None
        self.error_message = ""
        self.results = {}
    
    def update_phase(self, phase: str):
        """更新当前阶段"""
        self.current_phase = phase
    
    def set_error(self, error: str):
        """设置错误信息"""
        self.error_message = error
    
    def complete(self, results: dict = None):
        """完成处理"""
        import time
        self.is_running = False
        self.end_time = time.time()
        if results:
            self.results = results
    
    def get_duration(self) -> float:
        """获取处理时长"""
        if self.start_time:
            end = self.end_time or time.time()
            return end - self.start_time
        return 0.0
    
    def get_status_text(self) -> str:
        """获取状态文本"""
        if self.is_running:
            duration = self.get_duration()
            return f"{self.current_phase} (已运行 {duration:.1f}s)"
        elif self.error_message:
            return f"错误: {self.error_message}"
        elif self.end_time:
            duration = self.get_duration()
            return f"完成 (耗时 {duration:.1f}s)"
        else:
            return "就绪"


def create_enhanced_video_processor():
    """创建增强的视频处理器，支持进度回调"""
    
    def enhanced_process_video_segmentation(video_path: str, output_dir: str, 
                                          organize_by: str, quality: str,
                                          progress_callback: Optional[Callable] = None,
                                          log_callback: Optional[Callable] = None):
        """增强的视频处理函数，支持进度和日志回调"""
        
        # 设置进度监控
        if progress_callback:
            monitor = ProgressMonitor(progress_callback)
            monitor.set_steps([
                "验证输入文件",
                "初始化检测器", 
                "执行镜头检测",
                "生成分段信息",
                "切分视频文件",
                "生成项目文件",
                "生成分析报告"
            ])
        
        # 设置日志
        if log_callback:
            setup_gui_logging(log_callback)
        
        try:
            # 导入处理函数
            from video_segmentation import process_video_segmentation
            
            # 执行处理（这里可以添加更详细的进度回调）
            if progress_callback:
                monitor.next_step("开始处理...")
            
            success = process_video_segmentation(video_path, output_dir, organize_by, quality)
            
            if progress_callback:
                monitor.complete()
            
            return success
            
        except Exception as e:
            if log_callback:
                log_callback(f"处理失败: {e}", "ERROR")
            return False
    
    return enhanced_process_video_segmentation


class ResultsAnalyzer:
    """结果分析器"""
    
    @staticmethod
    def analyze_output_directory(output_dir: str) -> dict:
        """分析输出目录，生成统计信息"""
        from pathlib import Path
        
        output_path = Path(output_dir)
        if not output_path.exists():
            return {}
        
        results = {
            'video_segments': [],
            'report_files': [],
            'project_files': [],
            'total_size': 0,
            'segment_count': 0,
            'categories': {}
        }
        
        # 统计视频分段
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        for ext in video_extensions:
            for video_file in output_path.glob(f"**/*{ext}"):
                if video_file.is_file():
                    size = video_file.stat().st_size
                    results['video_segments'].append({
                        'name': video_file.name,
                        'path': str(video_file),
                        'size': size,
                        'category': video_file.parent.name
                    })
                    results['total_size'] += size
        
        results['segment_count'] = len(results['video_segments'])
        
        # 统计报告文件
        for report_file in output_path.glob("*.html"):
            results['report_files'].append({
                'name': report_file.name,
                'path': str(report_file),
                'size': report_file.stat().st_size
            })
        
        # 统计项目文件
        project_extensions = ['.xml', '.edl', '.json', '.csv']
        for ext in project_extensions:
            for project_file in output_path.glob(f"*{ext}"):
                results['project_files'].append({
                    'name': project_file.name,
                    'path': str(project_file),
                    'size': project_file.stat().st_size,
                    'type': ext[1:]  # 去掉点号
                })
        
        # 统计分类
        categories = {}
        for segment in results['video_segments']:
            category = segment['category']
            if category not in categories:
                categories[category] = {'count': 0, 'size': 0}
            categories[category]['count'] += 1
            categories[category]['size'] += segment['size']
        
        results['categories'] = categories
        
        return results
    
    @staticmethod
    def format_results_summary(results: dict) -> str:
        """格式化结果摘要"""
        if not results:
            return "无结果数据"
        
        from utils.video_utils import format_file_size
        
        summary = f"""处理结果统计:
• 视频分段: {results['segment_count']} 个
• 分析报告: {len(results['report_files'])} 个  
• 项目文件: {len(results['project_files'])} 个
• 总文件大小: {format_file_size(results['total_size'])}"""
        
        if results['categories']:
            summary += "\n\n分类统计:"
            for category, stats in results['categories'].items():
                summary += f"\n• {category}: {stats['count']} 个 ({format_file_size(stats['size'])})"
        
        return summary
