"""
Workflow Automation Module
工作流自动化模块
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from loguru import logger


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化任务调度器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="TaskScheduler")
        
        # 调度器配置
        self.scheduler_config = self.config.get('scheduler', {
            'max_concurrent_tasks': 5,
            'task_timeout': 3600,  # 1小时
            'retry_attempts': 3,
            'retry_delay': 60,  # 1分钟
            'cleanup_interval': 300  # 5分钟
        })
        
        # 任务队列和状态
        self.pending_tasks = []
        self.running_tasks = {}
        self.completed_tasks = []
        self.failed_tasks = []
        
        # 调度器状态
        self.running = False
        self.scheduler_thread = None
        self.cleanup_thread = None
        
        self.logger.info("Task scheduler initialized")
    
    def start(self):
        """启动任务调度器"""
        if self.running:
            self.logger.warning("Task scheduler already running")
            return
        
        self.running = True
        
        # 启动调度线程
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        # 启动清理线程
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        
        self.logger.info("Task scheduler started")
    
    def stop(self):
        """停止任务调度器"""
        if not self.running:
            return
        
        self.running = False
        
        # 等待线程结束
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5.0)
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5.0)
        
        # 取消所有运行中的任务
        for task_id in list(self.running_tasks.keys()):
            self.cancel_task(task_id)
        
        self.logger.info("Task scheduler stopped")
    
    def schedule_task(self, task_config: Dict[str, Any]) -> str:
        """
        调度任务
        
        Args:
            task_config: 任务配置
            
        Returns:
            任务ID
        """
        try:
            task_id = f"task_{int(time.time() * 1000)}"
            
            task = {
                "id": task_id,
                "type": task_config.get("type", "unknown"),
                "config": task_config,
                "created_at": datetime.now(),
                "scheduled_at": task_config.get("scheduled_at"),
                "priority": task_config.get("priority", 5),  # 1-10, 1最高
                "retry_count": 0,
                "max_retries": task_config.get("max_retries", self.scheduler_config["retry_attempts"])
            }
            
            # 添加到待处理队列
            self.pending_tasks.append(task)
            
            # 按优先级排序
            self.pending_tasks.sort(key=lambda x: x["priority"])
            
            self.logger.info(f"Task scheduled: {task_id} ({task['type']})")
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"Failed to schedule task: {e}")
            raise
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        try:
            # 从待处理队列中移除
            self.pending_tasks = [t for t in self.pending_tasks if t["id"] != task_id]
            
            # 取消运行中的任务
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task["cancelled"] = True
                
                # 如果有取消回调，调用它
                if "cancel_callback" in task:
                    try:
                        task["cancel_callback"]()
                    except Exception as e:
                        self.logger.error(f"Cancel callback failed: {e}")
                
                # 移动到失败队列
                task["status"] = "cancelled"
                task["completed_at"] = datetime.now()
                self.failed_tasks.append(task)
                del self.running_tasks[task_id]
                
                self.logger.info(f"Task cancelled: {task_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        # 检查运行中的任务
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            return {
                "id": task_id,
                "status": "running",
                "progress": task.get("progress", 0.0),
                "started_at": task.get("started_at"),
                "message": task.get("message", "")
            }
        
        # 检查待处理任务
        for task in self.pending_tasks:
            if task["id"] == task_id:
                return {
                    "id": task_id,
                    "status": "pending",
                    "scheduled_at": task.get("scheduled_at"),
                    "priority": task["priority"]
                }
        
        # 检查已完成任务
        for task in self.completed_tasks:
            if task["id"] == task_id:
                return {
                    "id": task_id,
                    "status": "completed",
                    "completed_at": task.get("completed_at"),
                    "result": task.get("result")
                }
        
        # 检查失败任务
        for task in self.failed_tasks:
            if task["id"] == task_id:
                return {
                    "id": task_id,
                    "status": "failed",
                    "error": task.get("error"),
                    "retry_count": task.get("retry_count", 0)
                }
        
        return None
    
    def _scheduler_loop(self):
        """调度器主循环"""
        while self.running:
            try:
                self._process_pending_tasks()
                time.sleep(1.0)
            except Exception as e:
                self.logger.error(f"Scheduler loop error: {e}")
                time.sleep(5.0)
    
    def _process_pending_tasks(self):
        """处理待处理任务"""
        max_concurrent = self.scheduler_config["max_concurrent_tasks"]
        
        # 检查是否可以启动新任务
        if len(self.running_tasks) >= max_concurrent:
            return
        
        # 获取下一个可执行的任务
        current_time = datetime.now()
        
        for i, task in enumerate(self.pending_tasks):
            # 检查调度时间
            scheduled_at = task.get("scheduled_at")
            if scheduled_at and current_time < scheduled_at:
                continue
            
            # 启动任务
            if self._start_task(task):
                self.pending_tasks.pop(i)
                break
    
    def _start_task(self, task: Dict[str, Any]) -> bool:
        """启动任务"""
        try:
            task_id = task["id"]
            task["started_at"] = datetime.now()
            task["status"] = "running"
            task["progress"] = 0.0
            task["cancelled"] = False
            
            # 添加到运行队列
            self.running_tasks[task_id] = task
            
            # 在新线程中执行任务
            task_thread = threading.Thread(
                target=self._execute_task,
                args=(task,),
                daemon=True
            )
            task["thread"] = task_thread
            task_thread.start()
            
            self.logger.info(f"Task started: {task_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start task {task['id']}: {e}")
            return False
    
    def _execute_task(self, task: Dict[str, Any]):
        """执行任务"""
        task_id = task["id"]
        
        try:
            # 获取任务执行器
            executor = self._get_task_executor(task["type"])
            if not executor:
                raise Exception(f"No executor found for task type: {task['type']}")
            
            # 执行任务
            result = executor(task)
            
            # 检查是否被取消
            if task.get("cancelled", False):
                return
            
            # 任务完成
            task["status"] = "completed"
            task["completed_at"] = datetime.now()
            task["result"] = result
            
            # 移动到完成队列
            self.completed_tasks.append(task)
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            self.logger.info(f"Task completed: {task_id}")
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {task_id} - {e}")
            
            # 检查是否需要重试
            task["retry_count"] += 1
            if task["retry_count"] < task["max_retries"]:
                # 重新调度
                task["scheduled_at"] = datetime.now() + timedelta(
                    seconds=self.scheduler_config["retry_delay"]
                )
                self.pending_tasks.append(task)
                self.pending_tasks.sort(key=lambda x: x["priority"])
            else:
                # 任务失败
                task["status"] = "failed"
                task["error"] = str(e)
                task["completed_at"] = datetime.now()
                self.failed_tasks.append(task)
            
            # 从运行队列移除
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    def _get_task_executor(self, task_type: str) -> Optional[Callable]:
        """获取任务执行器"""
        executors = {
            "video_detection": self._execute_video_detection,
            "batch_processing": self._execute_batch_processing,
            "cloud_upload": self._execute_cloud_upload,
            "report_generation": self._execute_report_generation
        }
        
        return executors.get(task_type)
    
    def _execute_video_detection(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行视频检测任务"""
        config = task["config"]
        video_path = config["video_path"]
        
        # 模拟视频检测过程
        for i in range(10):
            if task.get("cancelled", False):
                raise Exception("Task cancelled")
            
            task["progress"] = (i + 1) / 10
            task["message"] = f"处理帧 {i+1}/10"
            time.sleep(1)
        
        return {
            "boundaries": [{"frame": 100, "timestamp": 3.33}],
            "processing_time": 10.0
        }
    
    def _execute_batch_processing(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行批量处理任务"""
        config = task["config"]
        video_files = config["video_files"]
        
        results = []
        for i, video_file in enumerate(video_files):
            if task.get("cancelled", False):
                raise Exception("Task cancelled")
            
            task["progress"] = (i + 1) / len(video_files)
            task["message"] = f"处理视频 {i+1}/{len(video_files)}"
            
            # 模拟处理
            time.sleep(2)
            results.append({"video": video_file, "boundaries": 5})
        
        return {"results": results}
    
    def _execute_cloud_upload(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行云上传任务"""
        config = task["config"]
        file_path = config["file_path"]
        
        # 模拟上传过程
        for i in range(5):
            if task.get("cancelled", False):
                raise Exception("Task cancelled")
            
            task["progress"] = (i + 1) / 5
            task["message"] = f"上传进度 {(i+1)*20}%"
            time.sleep(1)
        
        return {"upload_url": f"https://cloud.example.com/{file_path}"}
    
    def _execute_report_generation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行报告生成任务"""
        config = task["config"]
        
        # 模拟报告生成
        for i in range(3):
            if task.get("cancelled", False):
                raise Exception("Task cancelled")
            
            task["progress"] = (i + 1) / 3
            task["message"] = f"生成报告 {i+1}/3"
            time.sleep(1)
        
        return {"report_path": "reports/analysis_report.pdf"}
    
    def _cleanup_loop(self):
        """清理循环"""
        while self.running:
            try:
                self._cleanup_old_tasks()
                time.sleep(self.scheduler_config["cleanup_interval"])
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
    
    def _cleanup_old_tasks(self):
        """清理旧任务"""
        cutoff_time = datetime.now() - timedelta(hours=24)  # 保留24小时
        
        # 清理完成的任务
        self.completed_tasks = [
            t for t in self.completed_tasks
            if t.get("completed_at", datetime.now()) > cutoff_time
        ]
        
        # 清理失败的任务
        self.failed_tasks = [
            t for t in self.failed_tasks
            if t.get("completed_at", datetime.now()) > cutoff_time
        ]
    
    def get_scheduler_stats(self) -> Dict[str, Any]:
        """获取调度器统计信息"""
        return {
            "running": self.running,
            "pending_tasks": len(self.pending_tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "max_concurrent": self.scheduler_config["max_concurrent_tasks"]
        }
    
    def cleanup(self):
        """清理资源"""
        self.stop()
        self.logger.info("Task scheduler cleanup completed")


class WorkflowAutomation:
    """工作流自动化"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化工作流自动化
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="WorkflowAutomation")
        
        # 初始化任务调度器
        self.task_scheduler = TaskScheduler(config)
        
        # 工作流配置
        self.workflow_config = self.config.get('workflow', {
            'auto_start': True,
            'default_priority': 5,
            'notification_enabled': True,
            'save_results': True
        })
        
        # 预定义工作流
        self.workflows = {
            "video_analysis": self._create_video_analysis_workflow,
            "batch_processing": self._create_batch_processing_workflow,
            "cloud_backup": self._create_cloud_backup_workflow
        }
        
        self.logger.info("Workflow automation initialized")
    
    def start(self):
        """启动工作流自动化"""
        self.task_scheduler.start()
        self.logger.info("Workflow automation started")
    
    def stop(self):
        """停止工作流自动化"""
        self.task_scheduler.stop()
        self.logger.info("Workflow automation stopped")
    
    def execute_workflow(self, workflow_name: str, 
                        workflow_config: Dict[str, Any]) -> str:
        """
        执行工作流
        
        Args:
            workflow_name: 工作流名称
            workflow_config: 工作流配置
            
        Returns:
            工作流ID
        """
        try:
            if workflow_name not in self.workflows:
                raise ValueError(f"Unknown workflow: {workflow_name}")
            
            # 创建工作流
            workflow_creator = self.workflows[workflow_name]
            tasks = workflow_creator(workflow_config)
            
            # 调度所有任务
            workflow_id = f"workflow_{int(time.time() * 1000)}"
            task_ids = []
            
            for task_config in tasks:
                task_config["workflow_id"] = workflow_id
                task_id = self.task_scheduler.schedule_task(task_config)
                task_ids.append(task_id)
            
            self.logger.info(f"Workflow executed: {workflow_id} ({len(task_ids)} tasks)")
            
            return workflow_id
            
        except Exception as e:
            self.logger.error(f"Failed to execute workflow {workflow_name}: {e}")
            raise
    
    def _create_video_analysis_workflow(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建视频分析工作流"""
        video_path = config["video_path"]
        
        tasks = [
            {
                "type": "video_detection",
                "video_path": video_path,
                "algorithm": config.get("algorithm", "frame_difference"),
                "threshold": config.get("threshold", 0.3),
                "priority": 3
            },
            {
                "type": "report_generation",
                "video_path": video_path,
                "include_charts": config.get("include_charts", True),
                "priority": 5,
                "scheduled_at": datetime.now() + timedelta(minutes=5)  # 5分钟后执行
            }
        ]
        
        return tasks
    
    def _create_batch_processing_workflow(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建批量处理工作流"""
        video_files = config["video_files"]
        
        tasks = [
            {
                "type": "batch_processing",
                "video_files": video_files,
                "algorithm": config.get("algorithm", "frame_difference"),
                "priority": 4
            }
        ]
        
        return tasks
    
    def _create_cloud_backup_workflow(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建云备份工作流"""
        files_to_backup = config["files"]
        
        tasks = []
        for file_path in files_to_backup:
            tasks.append({
                "type": "cloud_upload",
                "file_path": file_path,
                "priority": 6
            })
        
        return tasks
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        # 这里需要跟踪工作流中的所有任务
        # 简化实现，返回基本状态
        return {
            "workflow_id": workflow_id,
            "status": "running",
            "progress": 0.5,
            "tasks": []
        }
    
    def cleanup(self):
        """清理资源"""
        self.task_scheduler.cleanup()
        self.logger.info("Workflow automation cleanup completed")
