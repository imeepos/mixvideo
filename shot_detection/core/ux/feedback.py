"""
User Feedback Collection System
用户反馈收集系统
"""

import json
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger


class FeedbackCollector:
    """反馈收集器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化反馈收集器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="FeedbackCollector")
        
        # 反馈配置
        self.feedback_config = self.config.get('feedback', {
            'enable_feedback': True,
            'feedback_file': 'feedback.json',
            'auto_collect_usage': True,
            'collect_performance_data': True,
            'collect_error_reports': True,
            'feedback_server_url': '',
            'anonymous_feedback': True
        })
        
        # 反馈数据
        self.feedback_data = []
        self.usage_statistics = {}
        self.error_reports = []
        
        # 加载现有反馈
        self._load_feedback_data()
        
        self.logger.info("Feedback collector initialized")
    
    def show_feedback_dialog(self, parent: tk.Widget, feedback_type: str = 'general') -> bool:
        """
        显示反馈对话框
        
        Args:
            parent: 父控件
            feedback_type: 反馈类型
            
        Returns:
            是否提交了反馈
        """
        try:
            if not self.feedback_config['enable_feedback']:
                return False
            
            # 创建反馈对话框
            dialog = tk.Toplevel(parent)
            dialog.title("用户反馈")
            dialog.geometry("500x400")
            dialog.resizable(True, True)
            dialog.transient(parent)
            dialog.grab_set()
            
            # 居中显示
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # 主框架
            main_frame = tk.Frame(dialog, padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            title_label = tk.Label(
                main_frame,
                text="我们重视您的反馈",
                font=('Microsoft YaHei UI', 14, 'bold'),
                fg='#2196F3'
            )
            title_label.pack(pady=(0, 10))
            
            # 反馈类型
            type_frame = tk.Frame(main_frame)
            type_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(type_frame, text="反馈类型:", font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT)
            
            feedback_type_var = tk.StringVar(value=feedback_type)
            type_combo = tk.OptionMenu(
                type_frame,
                feedback_type_var,
                'general', 'bug_report', 'feature_request', 'performance', 'ui_ux'
            )
            type_combo.pack(side=tk.LEFT, padx=(10, 0))
            
            # 反馈内容
            content_label = tk.Label(
                main_frame,
                text="请详细描述您的反馈:",
                font=('Microsoft YaHei UI', 9)
            )
            content_label.pack(anchor=tk.W, pady=(10, 5))
            
            content_text = tk.Text(
                main_frame,
                height=10,
                font=('Microsoft YaHei UI', 9),
                wrap=tk.WORD
            )
            content_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # 联系信息（可选）
            contact_frame = tk.Frame(main_frame)
            contact_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(contact_frame, text="联系方式（可选）:", font=('Microsoft YaHei UI', 9)).pack(anchor=tk.W)
            
            contact_entry = tk.Entry(
                contact_frame,
                font=('Microsoft YaHei UI', 9)
            )
            contact_entry.pack(fill=tk.X, pady=(5, 0))
            
            # 匿名反馈选项
            anonymous_var = tk.BooleanVar(value=self.feedback_config['anonymous_feedback'])
            anonymous_check = tk.Checkbutton(
                main_frame,
                text="匿名反馈",
                variable=anonymous_var,
                font=('Microsoft YaHei UI', 9)
            )
            anonymous_check.pack(anchor=tk.W, pady=(0, 10))
            
            # 按钮框架
            button_frame = tk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            submitted = [False]  # 使用列表来在闭包中修改值
            
            def submit_feedback():
                content = content_text.get("1.0", tk.END).strip()
                if not content:
                    messagebox.showwarning("警告", "请输入反馈内容")
                    return
                
                feedback_data = {
                    'type': feedback_type_var.get(),
                    'content': content,
                    'contact': contact_entry.get() if not anonymous_var.get() else '',
                    'anonymous': anonymous_var.get(),
                    'timestamp': datetime.now().isoformat(),
                    'version': '2.0.0'
                }
                
                if self.collect_feedback(feedback_data):
                    messagebox.showinfo("感谢", "感谢您的反馈！我们会认真考虑您的建议。")
                    submitted[0] = True
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", "反馈提交失败，请稍后重试。")
            
            def cancel_feedback():
                dialog.destroy()
            
            # 提交按钮
            submit_button = tk.Button(
                button_frame,
                text="提交反馈",
                command=submit_feedback,
                font=('Microsoft YaHei UI', 9),
                bg='#2196F3',
                fg='white',
                padx=20
            )
            submit_button.pack(side=tk.RIGHT)
            
            # 取消按钮
            cancel_button = tk.Button(
                button_frame,
                text="取消",
                command=cancel_feedback,
                font=('Microsoft YaHei UI', 9),
                padx=20
            )
            cancel_button.pack(side=tk.RIGHT, padx=(0, 10))
            
            # 等待对话框关闭
            dialog.wait_window()
            
            return submitted[0]
            
        except Exception as e:
            self.logger.error(f"Failed to show feedback dialog: {e}")
            return False
    
    def collect_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """
        收集反馈数据
        
        Args:
            feedback_data: 反馈数据
            
        Returns:
            是否收集成功
        """
        try:
            # 添加系统信息
            feedback_data.update(self._get_system_info())
            
            # 添加到反馈列表
            self.feedback_data.append(feedback_data)
            
            # 保存到文件
            self._save_feedback_data()
            
            # 如果配置了服务器，尝试上传
            if self.feedback_config.get('feedback_server_url'):
                self._upload_feedback(feedback_data)
            
            self.logger.info(f"Collected feedback: {feedback_data['type']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to collect feedback: {e}")
            return False
    
    def collect_usage_statistics(self, action: str, details: Optional[Dict[str, Any]] = None):
        """
        收集使用统计
        
        Args:
            action: 操作名称
            details: 详细信息
        """
        try:
            if not self.feedback_config['auto_collect_usage']:
                return
            
            timestamp = datetime.now().isoformat()
            
            if action not in self.usage_statistics:
                self.usage_statistics[action] = {
                    'count': 0,
                    'first_used': timestamp,
                    'last_used': timestamp,
                    'details': []
                }
            
            stats = self.usage_statistics[action]
            stats['count'] += 1
            stats['last_used'] = timestamp
            
            if details:
                stats['details'].append({
                    'timestamp': timestamp,
                    'data': details
                })
                
                # 只保留最近100条详细记录
                if len(stats['details']) > 100:
                    stats['details'] = stats['details'][-100:]
            
            # 定期保存统计数据
            if stats['count'] % 10 == 0:
                self._save_feedback_data()
            
        except Exception as e:
            self.logger.error(f"Failed to collect usage statistics: {e}")
    
    def collect_error_report(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        收集错误报告
        
        Args:
            error: 异常对象
            context: 上下文信息
        """
        try:
            if not self.feedback_config['collect_error_reports']:
                return
            
            import traceback
            
            error_report = {
                'timestamp': datetime.now().isoformat(),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'traceback': traceback.format_exc(),
                'context': context or {},
                'system_info': self._get_system_info()
            }
            
            self.error_reports.append(error_report)
            
            # 只保留最近50个错误报告
            if len(self.error_reports) > 50:
                self.error_reports = self.error_reports[-50:]
            
            # 保存错误报告
            self._save_feedback_data()
            
            self.logger.info(f"Collected error report: {type(error).__name__}")
            
        except Exception as e:
            self.logger.error(f"Failed to collect error report: {e}")
    
    def collect_performance_data(self, operation: str, duration: float, 
                                details: Optional[Dict[str, Any]] = None):
        """
        收集性能数据
        
        Args:
            operation: 操作名称
            duration: 持续时间（秒）
            details: 详细信息
        """
        try:
            if not self.feedback_config['collect_performance_data']:
                return
            
            performance_data = {
                'operation': operation,
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'details': details or {}
            }
            
            # 添加到使用统计中
            self.collect_usage_statistics('performance', performance_data)
            
        except Exception as e:
            self.logger.error(f"Failed to collect performance data: {e}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            import platform
            import psutil
            
            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'app_version': '2.0.0'
            }
        except Exception:
            return {'app_version': '2.0.0'}
    
    def _load_feedback_data(self):
        """加载反馈数据"""
        try:
            feedback_file = Path(self.feedback_config['feedback_file'])
            
            if feedback_file.exists():
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.feedback_data = data.get('feedback', [])
                self.usage_statistics = data.get('usage_statistics', {})
                self.error_reports = data.get('error_reports', [])
                
                self.logger.info("Feedback data loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to load feedback data: {e}")
    
    def _save_feedback_data(self):
        """保存反馈数据"""
        try:
            feedback_file = Path(self.feedback_config['feedback_file'])
            feedback_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'feedback': self.feedback_data,
                'usage_statistics': self.usage_statistics,
                'error_reports': self.error_reports,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Failed to save feedback data: {e}")
    
    def _upload_feedback(self, feedback_data: Dict[str, Any]):
        """
        上传反馈到服务器
        
        Args:
            feedback_data: 反馈数据
        """
        try:
            import requests
            
            server_url = self.feedback_config['feedback_server_url']
            
            response = requests.post(
                f"{server_url}/feedback",
                json=feedback_data,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info("Feedback uploaded successfully")
            else:
                self.logger.warning(f"Failed to upload feedback: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to upload feedback: {e}")
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """获取反馈摘要"""
        try:
            # 统计反馈类型
            feedback_types = {}
            for feedback in self.feedback_data:
                feedback_type = feedback.get('type', 'unknown')
                feedback_types[feedback_type] = feedback_types.get(feedback_type, 0) + 1
            
            # 统计使用情况
            total_actions = sum(stats['count'] for stats in self.usage_statistics.values())
            most_used_actions = sorted(
                self.usage_statistics.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:5]
            
            return {
                'total_feedback': len(self.feedback_data),
                'feedback_types': feedback_types,
                'total_error_reports': len(self.error_reports),
                'total_actions': total_actions,
                'most_used_actions': [
                    {'action': action, 'count': stats['count']}
                    for action, stats in most_used_actions
                ],
                'last_feedback': self.feedback_data[-1]['timestamp'] if self.feedback_data else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get feedback summary: {e}")
            return {}
    
    def export_feedback_data(self, export_path: str) -> bool:
        """
        导出反馈数据
        
        Args:
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'summary': self.get_feedback_summary(),
                'feedback': self.feedback_data,
                'usage_statistics': self.usage_statistics,
                'error_reports': self.error_reports
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Feedback data exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export feedback data: {e}")
            return False
    
    def clear_feedback_data(self, data_type: str = 'all'):
        """
        清理反馈数据
        
        Args:
            data_type: 数据类型 ('all', 'feedback', 'usage', 'errors')
        """
        try:
            if data_type in ['all', 'feedback']:
                self.feedback_data.clear()
            
            if data_type in ['all', 'usage']:
                self.usage_statistics.clear()
            
            if data_type in ['all', 'errors']:
                self.error_reports.clear()
            
            self._save_feedback_data()
            self.logger.info(f"Cleared feedback data: {data_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to clear feedback data: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            # 保存最终数据
            self._save_feedback_data()
            self.logger.info("Feedback collector cleanup completed")
        except Exception as e:
            self.logger.error(f"Feedback cleanup failed: {e}")
