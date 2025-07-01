"""
Base Tab Component
基础Tab组件
"""

import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger

from config import get_config


class BaseTab(ABC):
    """基础Tab组件抽象类"""
    
    def __init__(self, parent: ttk.Notebook, name: str):
        """
        初始化基础Tab
        
        Args:
            parent: 父级Notebook组件
            name: Tab名称
        """
        self.parent = parent
        self.name = name
        self.config = get_config()
        self.logger = logger.bind(component=f"GUI.{name}Tab")
        
        # 创建Tab框架
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text=name)
        
        # 初始化UI
        self.setup_ui()
        
        # 绑定事件
        self.bind_events()
        
        self.logger.debug(f"Initialized {name} tab")
    
    @abstractmethod
    def setup_ui(self):
        """设置UI界面 - 子类必须实现"""
        pass
    
    def bind_events(self):
        """绑定事件 - 子类可以重写"""
        pass
    
    def get_config_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置节
        
        Args:
            section: 配置节名称
            
        Returns:
            配置字典
        """
        return self.config.get(section, {})
    
    def create_labeled_frame(self, parent: tk.Widget, text: str, **kwargs) -> ttk.LabelFrame:
        """
        创建带标签的框架
        
        Args:
            parent: 父组件
            text: 标签文本
            **kwargs: 其他参数
            
        Returns:
            LabelFrame组件
        """
        return ttk.LabelFrame(parent, text=text, **kwargs)
    
    def create_button_frame(self, parent: tk.Widget, **kwargs) -> ttk.Frame:
        """
        创建按钮框架
        
        Args:
            parent: 父组件
            **kwargs: 其他参数
            
        Returns:
            Frame组件
        """
        frame = ttk.Frame(parent, **kwargs)
        return frame
    
    def create_progress_bar(self, parent: tk.Widget, **kwargs) -> ttk.Progressbar:
        """
        创建进度条
        
        Args:
            parent: 父组件
            **kwargs: 其他参数
            
        Returns:
            Progressbar组件
        """
        return ttk.Progressbar(parent, **kwargs)
    
    def create_text_widget(self, parent: tk.Widget, **kwargs) -> tk.Text:
        """
        创建文本组件
        
        Args:
            parent: 父组件
            **kwargs: 其他参数
            
        Returns:
            Text组件
        """
        # 默认配置
        default_config = {
            'wrap': tk.WORD,
            'state': tk.DISABLED,
            'height': 10
        }
        default_config.update(kwargs)
        
        text_widget = tk.Text(parent, **default_config)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        return text_widget
    
    def update_progress(self, value: float, text: str = ""):
        """
        更新进度
        
        Args:
            value: 进度值 (0.0-1.0)
            text: 进度文本
        """
        if hasattr(self, 'progress_var'):
            self.progress_var.set(value * 100)
        
        if hasattr(self, 'status_var') and text:
            self.status_var.set(text)
        
        # 强制更新UI
        self.frame.update_idletasks()
    
    def log_message(self, message: str, level: str = "info"):
        """
        记录日志消息
        
        Args:
            message: 消息内容
            level: 日志级别
        """
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"[{level.upper()}] {message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        # 同时记录到日志系统
        getattr(self.logger, level)(message)
    
    def clear_log(self):
        """清空日志"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    def show_error(self, title: str, message: str):
        """
        显示错误对话框
        
        Args:
            title: 标题
            message: 错误消息
        """
        from tkinter import messagebox
        messagebox.showerror(title, message)
        self.logger.error(f"{title}: {message}")
    
    def show_info(self, title: str, message: str):
        """
        显示信息对话框
        
        Args:
            title: 标题
            message: 信息消息
        """
        from tkinter import messagebox
        messagebox.showinfo(title, message)
        self.logger.info(f"{title}: {message}")
    
    def show_warning(self, title: str, message: str):
        """
        显示警告对话框
        
        Args:
            title: 标题
            message: 警告消息
        """
        from tkinter import messagebox
        messagebox.showwarning(title, message)
        self.logger.warning(f"{title}: {message}")
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """
        显示是/否对话框
        
        Args:
            title: 标题
            message: 询问消息
            
        Returns:
            用户选择结果
        """
        from tkinter import messagebox
        result = messagebox.askyesno(title, message)
        self.logger.debug(f"{title}: {message} -> {result}")
        return result
    
    def on_tab_selected(self):
        """Tab被选中时的回调 - 子类可以重写"""
        self.logger.debug(f"{self.name} tab selected")
    
    def on_tab_deselected(self):
        """Tab被取消选中时的回调 - 子类可以重写"""
        self.logger.debug(f"{self.name} tab deselected")
    
    def cleanup(self):
        """清理资源 - 子类可以重写"""
        self.logger.debug(f"Cleaning up {self.name} tab")
    
    def get_state(self) -> Dict[str, Any]:
        """
        获取Tab状态 - 子类可以重写
        
        Returns:
            状态字典
        """
        return {
            'name': self.name,
            'active': True
        }
    
    def set_state(self, state: Dict[str, Any]):
        """
        设置Tab状态 - 子类可以重写
        
        Args:
            state: 状态字典
        """
        self.logger.debug(f"Setting state for {self.name} tab: {state}")
    
    def validate_inputs(self) -> bool:
        """
        验证输入 - 子类可以重写
        
        Returns:
            验证结果
        """
        return True
