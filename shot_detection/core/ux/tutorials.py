"""
Tutorial and Onboarding System
教程和引导系统
"""

import json
import tkinter as tk
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from loguru import logger


class TutorialManager:
    """教程管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化教程管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="TutorialManager")
        
        # 教程配置
        self.tutorial_config = self.config.get('tutorials', {
            'enable_tutorials': True,
            'show_welcome_tutorial': True,
            'tutorials_dir': './tutorials',
            'auto_start_tutorial': False,
            'tutorial_progress_file': 'tutorial_progress.json'
        })
        
        # 教程数据
        self.tutorials = {}
        self.current_tutorial = None
        self.current_step = 0
        self.tutorial_progress = {}
        
        # UI组件
        self.tutorial_overlay = None
        self.tutorial_dialog = None
        
        # 初始化内置教程
        self._initialize_builtin_tutorials()
        
        # 加载教程进度
        self._load_tutorial_progress()
        
        self.logger.info("Tutorial manager initialized")
    
    def _initialize_builtin_tutorials(self):
        """初始化内置教程"""
        # 欢迎教程
        self.tutorials['welcome'] = {
            'id': 'welcome',
            'title': '欢迎使用 Shot Detection',
            'description': '快速了解 Shot Detection 的基本功能',
            'steps': [
                {
                    'title': '欢迎',
                    'content': '欢迎使用 Shot Detection v2.0！这是一个强大的视频镜头边界检测工具。',
                    'target': None,
                    'position': 'center',
                    'action': None
                },
                {
                    'title': '打开视频文件',
                    'content': '点击"打开文件"按钮或使用快捷键 Ctrl+O 来选择要分析的视频文件。',
                    'target': 'open_button',
                    'position': 'bottom',
                    'action': 'highlight'
                },
                {
                    'title': '选择检测算法',
                    'content': '在算法选择区域，您可以选择不同的检测算法，如帧差检测、直方图检测等。',
                    'target': 'algorithm_selector',
                    'position': 'right',
                    'action': 'highlight'
                },
                {
                    'title': '调整参数',
                    'content': '根据视频特点调整检测阈值和其他参数，以获得最佳检测效果。',
                    'target': 'parameters_panel',
                    'position': 'left',
                    'action': 'highlight'
                },
                {
                    'title': '开始检测',
                    'content': '点击"开始检测"按钮开始分析视频。检测过程中可以查看实时进度。',
                    'target': 'start_button',
                    'position': 'top',
                    'action': 'highlight'
                },
                {
                    'title': '查看结果',
                    'content': '检测完成后，您可以在结果面板中查看检测到的镜头边界，并导出结果。',
                    'target': 'results_panel',
                    'position': 'top',
                    'action': 'highlight'
                },
                {
                    'title': '完成',
                    'content': '教程完成！您现在可以开始使用 Shot Detection 分析您的视频了。如需更多帮助，请查看帮助文档。',
                    'target': None,
                    'position': 'center',
                    'action': None
                }
            ]
        }
        
        # 高级功能教程
        self.tutorials['advanced'] = {
            'id': 'advanced',
            'title': '高级功能教程',
            'description': '学习使用 Shot Detection 的高级功能',
            'steps': [
                {
                    'title': '批量处理',
                    'content': '使用批量处理功能可以同时处理多个视频文件，提高工作效率。',
                    'target': 'batch_tab',
                    'position': 'bottom',
                    'action': 'highlight'
                },
                {
                    'title': '性能监控',
                    'content': '在性能面板中可以监控系统资源使用情况，优化处理性能。',
                    'target': 'performance_tab',
                    'position': 'bottom',
                    'action': 'highlight'
                },
                {
                    'title': '剪映集成',
                    'content': '可以直接将检测结果导出为剪映项目，方便后续编辑。',
                    'target': 'jianying_tab',
                    'position': 'bottom',
                    'action': 'highlight'
                }
            ]
        }
        
        # 快捷键教程
        self.tutorials['shortcuts'] = {
            'id': 'shortcuts',
            'title': '键盘快捷键',
            'description': '学习常用的键盘快捷键',
            'steps': [
                {
                    'title': '文件操作',
                    'content': 'Ctrl+O: 打开文件\nCtrl+S: 保存结果\nCtrl+Q: 退出程序',
                    'target': None,
                    'position': 'center',
                    'action': None
                },
                {
                    'title': '检测操作',
                    'content': 'Ctrl+D: 开始检测\nCtrl+Shift+D: 停止检测\nCtrl+E: 导出结果',
                    'target': None,
                    'position': 'center',
                    'action': None
                },
                {
                    'title': '视图操作',
                    'content': 'F5: 刷新\nF11: 全屏\nCtrl+Plus: 放大\nCtrl+Minus: 缩小',
                    'target': None,
                    'position': 'center',
                    'action': None
                }
            ]
        }
    
    def start_tutorial(self, tutorial_id: str, parent_widget: tk.Widget) -> bool:
        """
        开始教程
        
        Args:
            tutorial_id: 教程ID
            parent_widget: 父控件
            
        Returns:
            是否成功开始
        """
        try:
            if not self.tutorial_config['enable_tutorials']:
                return False
            
            if tutorial_id not in self.tutorials:
                self.logger.error(f"Tutorial not found: {tutorial_id}")
                return False
            
            self.current_tutorial = tutorial_id
            self.current_step = 0
            
            # 创建教程界面
            self._create_tutorial_ui(parent_widget)
            
            # 显示第一步
            self._show_current_step()
            
            self.logger.info(f"Started tutorial: {tutorial_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start tutorial {tutorial_id}: {e}")
            return False
    
    def _create_tutorial_ui(self, parent_widget: tk.Widget):
        """
        创建教程UI
        
        Args:
            parent_widget: 父控件
        """
        try:
            # 创建覆盖层
            self.tutorial_overlay = tk.Toplevel(parent_widget)
            self.tutorial_overlay.title("教程")
            self.tutorial_overlay.attributes('-topmost', True)
            self.tutorial_overlay.attributes('-alpha', 0.9)
            self.tutorial_overlay.configure(bg='black')
            
            # 设置全屏覆盖
            self.tutorial_overlay.geometry(f"{parent_widget.winfo_screenwidth()}x{parent_widget.winfo_screenheight()}+0+0")
            self.tutorial_overlay.overrideredirect(True)
            
            # 创建教程对话框
            self.tutorial_dialog = tk.Toplevel(self.tutorial_overlay)
            self.tutorial_dialog.title("教程")
            self.tutorial_dialog.configure(bg='white')
            self.tutorial_dialog.attributes('-topmost', True)
            
            # 对话框内容框架
            content_frame = tk.Frame(self.tutorial_dialog, bg='white', padx=20, pady=20)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            self.title_label = tk.Label(
                content_frame,
                text="",
                font=('Microsoft YaHei UI', 14, 'bold'),
                bg='white',
                fg='#2196F3'
            )
            self.title_label.pack(pady=(0, 10))
            
            # 内容
            self.content_label = tk.Label(
                content_frame,
                text="",
                font=('Microsoft YaHei UI', 10),
                bg='white',
                fg='#333333',
                wraplength=400,
                justify=tk.LEFT
            )
            self.content_label.pack(pady=(0, 20))
            
            # 按钮框架
            button_frame = tk.Frame(content_frame, bg='white')
            button_frame.pack(fill=tk.X)
            
            # 上一步按钮
            self.prev_button = tk.Button(
                button_frame,
                text="上一步",
                command=self._previous_step,
                font=('Microsoft YaHei UI', 9),
                state=tk.DISABLED
            )
            self.prev_button.pack(side=tk.LEFT)
            
            # 跳过按钮
            skip_button = tk.Button(
                button_frame,
                text="跳过教程",
                command=self._skip_tutorial,
                font=('Microsoft YaHei UI', 9)
            )
            skip_button.pack(side=tk.LEFT, padx=(10, 0))
            
            # 下一步/完成按钮
            self.next_button = tk.Button(
                button_frame,
                text="下一步",
                command=self._next_step,
                font=('Microsoft YaHei UI', 9),
                bg='#2196F3',
                fg='white'
            )
            self.next_button.pack(side=tk.RIGHT)
            
            # 进度指示器
            self.progress_label = tk.Label(
                content_frame,
                text="",
                font=('Microsoft YaHei UI', 8),
                bg='white',
                fg='#666666'
            )
            self.progress_label.pack(pady=(10, 0))
            
        except Exception as e:
            self.logger.error(f"Failed to create tutorial UI: {e}")
    
    def _show_current_step(self):
        """显示当前步骤"""
        try:
            if not self.current_tutorial or not self.tutorial_dialog:
                return
            
            tutorial = self.tutorials[self.current_tutorial]
            steps = tutorial['steps']
            
            if self.current_step >= len(steps):
                self._finish_tutorial()
                return
            
            step = steps[self.current_step]
            
            # 更新内容
            self.title_label.config(text=step['title'])
            self.content_label.config(text=step['content'])
            
            # 更新进度
            progress_text = f"第 {self.current_step + 1} 步，共 {len(steps)} 步"
            self.progress_label.config(text=progress_text)
            
            # 更新按钮状态
            self.prev_button.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
            
            if self.current_step == len(steps) - 1:
                self.next_button.config(text="完成")
            else:
                self.next_button.config(text="下一步")
            
            # 定位对话框
            self._position_dialog(step)
            
            # 执行步骤动作
            self._execute_step_action(step)
            
        except Exception as e:
            self.logger.error(f"Failed to show current step: {e}")
    
    def _position_dialog(self, step: Dict[str, Any]):
        """
        定位对话框
        
        Args:
            step: 步骤数据
        """
        try:
            position = step.get('position', 'center')
            
            # 更新对话框大小
            self.tutorial_dialog.update_idletasks()
            dialog_width = self.tutorial_dialog.winfo_reqwidth()
            dialog_height = self.tutorial_dialog.winfo_reqheight()
            
            screen_width = self.tutorial_dialog.winfo_screenwidth()
            screen_height = self.tutorial_dialog.winfo_screenheight()
            
            if position == 'center':
                x = (screen_width - dialog_width) // 2
                y = (screen_height - dialog_height) // 2
            elif position == 'top':
                x = (screen_width - dialog_width) // 2
                y = 50
            elif position == 'bottom':
                x = (screen_width - dialog_width) // 2
                y = screen_height - dialog_height - 50
            elif position == 'left':
                x = 50
                y = (screen_height - dialog_height) // 2
            elif position == 'right':
                x = screen_width - dialog_width - 50
                y = (screen_height - dialog_height) // 2
            else:
                x = (screen_width - dialog_width) // 2
                y = (screen_height - dialog_height) // 2
            
            self.tutorial_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            
        except Exception as e:
            self.logger.error(f"Failed to position dialog: {e}")
    
    def _execute_step_action(self, step: Dict[str, Any]):
        """
        执行步骤动作
        
        Args:
            step: 步骤数据
        """
        try:
            action = step.get('action')
            target = step.get('target')
            
            if action == 'highlight' and target:
                # 这里可以实现高亮目标控件的逻辑
                self.logger.info(f"Highlighting target: {target}")
            
        except Exception as e:
            self.logger.error(f"Failed to execute step action: {e}")
    
    def _next_step(self):
        """下一步"""
        try:
            tutorial = self.tutorials[self.current_tutorial]
            steps = tutorial['steps']
            
            if self.current_step >= len(steps) - 1:
                self._finish_tutorial()
            else:
                self.current_step += 1
                self._show_current_step()
                
        except Exception as e:
            self.logger.error(f"Failed to go to next step: {e}")
    
    def _previous_step(self):
        """上一步"""
        try:
            if self.current_step > 0:
                self.current_step -= 1
                self._show_current_step()
                
        except Exception as e:
            self.logger.error(f"Failed to go to previous step: {e}")
    
    def _skip_tutorial(self):
        """跳过教程"""
        try:
            self._finish_tutorial(skipped=True)
        except Exception as e:
            self.logger.error(f"Failed to skip tutorial: {e}")
    
    def _finish_tutorial(self, skipped: bool = False):
        """
        完成教程
        
        Args:
            skipped: 是否跳过
        """
        try:
            if self.current_tutorial:
                # 记录教程完成状态
                self.tutorial_progress[self.current_tutorial] = {
                    'completed': not skipped,
                    'skipped': skipped,
                    'completed_at': self._get_current_timestamp()
                }
                
                # 保存进度
                self._save_tutorial_progress()
                
                self.logger.info(f"Tutorial {'skipped' if skipped else 'completed'}: {self.current_tutorial}")
            
            # 清理UI
            self._cleanup_tutorial_ui()
            
            # 重置状态
            self.current_tutorial = None
            self.current_step = 0
            
        except Exception as e:
            self.logger.error(f"Failed to finish tutorial: {e}")
    
    def _cleanup_tutorial_ui(self):
        """清理教程UI"""
        try:
            if self.tutorial_dialog:
                self.tutorial_dialog.destroy()
                self.tutorial_dialog = None
            
            if self.tutorial_overlay:
                self.tutorial_overlay.destroy()
                self.tutorial_overlay = None
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup tutorial UI: {e}")
    
    def _load_tutorial_progress(self):
        """加载教程进度"""
        try:
            progress_file = Path(self.tutorial_config['tutorial_progress_file'])
            
            if progress_file.exists():
                with open(progress_file, 'r', encoding='utf-8') as f:
                    self.tutorial_progress = json.load(f)
                
                self.logger.info("Tutorial progress loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to load tutorial progress: {e}")
    
    def _save_tutorial_progress(self):
        """保存教程进度"""
        try:
            progress_file = Path(self.tutorial_config['tutorial_progress_file'])
            progress_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.tutorial_progress, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Tutorial progress saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save tutorial progress: {e}")
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def get_available_tutorials(self) -> List[Dict[str, Any]]:
        """获取可用教程列表"""
        tutorials = []
        
        for tutorial_id, tutorial_data in self.tutorials.items():
            progress = self.tutorial_progress.get(tutorial_id, {})
            
            tutorials.append({
                'id': tutorial_id,
                'title': tutorial_data['title'],
                'description': tutorial_data['description'],
                'steps_count': len(tutorial_data['steps']),
                'completed': progress.get('completed', False),
                'skipped': progress.get('skipped', False)
            })
        
        return tutorials
    
    def is_tutorial_completed(self, tutorial_id: str) -> bool:
        """
        检查教程是否已完成
        
        Args:
            tutorial_id: 教程ID
            
        Returns:
            是否已完成
        """
        return self.tutorial_progress.get(tutorial_id, {}).get('completed', False)
    
    def should_show_welcome_tutorial(self) -> bool:
        """是否应该显示欢迎教程"""
        if not self.tutorial_config['show_welcome_tutorial']:
            return False
        
        return not self.is_tutorial_completed('welcome')
    
    def reset_tutorial_progress(self, tutorial_id: Optional[str] = None):
        """
        重置教程进度
        
        Args:
            tutorial_id: 教程ID，如果为None则重置所有
        """
        try:
            if tutorial_id:
                if tutorial_id in self.tutorial_progress:
                    del self.tutorial_progress[tutorial_id]
            else:
                self.tutorial_progress.clear()
            
            self._save_tutorial_progress()
            self.logger.info(f"Reset tutorial progress: {tutorial_id or 'all'}")
            
        except Exception as e:
            self.logger.error(f"Failed to reset tutorial progress: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self._cleanup_tutorial_ui()
            self.logger.info("Tutorial manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Tutorial cleanup failed: {e}")
