"""
Draft Tab Component
草稿Tab组件
"""

import tkinter as tk
from tkinter import ttk

from .base_tab import BaseTab


class DraftTab(BaseTab):
    """剪映草稿Tab"""
    
    def setup_ui(self):
        """设置UI界面"""
        # 创建占位符标签
        label = ttk.Label(self.frame, text="剪映草稿功能正在开发中...", 
                         font=('Arial', 12))
        label.pack(expand=True)
