"""
Main Window Module
主窗口模块
"""

import tkinter as tk
from tkinter import ttk
from loguru import logger

from config import get_config


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root: tk.Tk):
        """
        初始化主窗口
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.config = get_config()
        self.logger = logger.bind(component="MainWindow")
        
        # 设置窗口
        self.setup_window()
        
        # 创建界面
        self.create_interface()
        
        self.logger.info("Main window initialized")
    
    def setup_window(self):
        """设置窗口属性"""
        gui_config = self.config.get_gui_config()
        window_config = gui_config.get('window', {})
        
        # 设置标题
        app_config = self.config.get('app', {})
        title = f"{app_config.get('name', 'Shot Detection')} v{app_config.get('version', '2.0.0')}"
        self.root.title(title)
        
        # 设置大小
        width = window_config.get('width', 1200)
        height = window_config.get('height', 800)
        self.root.geometry(f"{width}x{height}")
        
        # 设置最小大小
        min_width = window_config.get('min_width', 800)
        min_height = window_config.get('min_height', 600)
        self.root.minsize(min_width, min_height)
        
        # 设置是否可调整大小
        resizable = window_config.get('resizable', True)
        self.root.resizable(resizable, resizable)
    
    def create_interface(self):
        """创建界面"""
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建占位符标签页
        self.create_placeholder_tabs()
        
        # 创建状态栏
        self.create_statusbar()
    
    def create_placeholder_tabs(self):
        """创建功能标签页"""
        try:
            from .components import VideoTab, BatchTab, AnalysisTab, DraftTab, MixTab, ToolsTab

            # 创建各个功能Tab
            self.video_tab = VideoTab(self.notebook, "📄 视频分镜")
            self.batch_tab = BatchTab(self.notebook, "📦 批量处理")
            self.analysis_tab = AnalysisTab(self.notebook, "🔍 视频分析")
            self.draft_tab = DraftTab(self.notebook, "📋 剪映草稿")
            self.mix_tab = MixTab(self.notebook, "🎬 视频混剪")
            self.tools_tab = ToolsTab(self.notebook, "🔧 实用工具")

            # 存储Tab引用
            self.tabs = [
                self.video_tab,
                self.batch_tab,
                self.analysis_tab,
                self.draft_tab,
                self.mix_tab
            ]

            # 绑定Tab选择事件
            self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

            self.logger.info("All tabs created successfully")

        except Exception as e:
            self.logger.error(f"Error creating tabs: {e}")
            # 如果创建失败，使用占位符
            self.create_fallback_tabs()

    def create_fallback_tabs(self):
        """创建备用占位符标签页"""
        tab_names = [
            "📄 视频分镜",
            "📦 批量处理",
            "🔍 视频分析",
            "📋 剪映草稿",
            "🎬 视频混剪"
        ]

        self.tabs = []

        for name in tab_names:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)

            # 添加占位符标签
            label = ttk.Label(frame, text=f"{name} 功能正在开发中...",
                            font=('Arial', 12))
            label.pack(expand=True)

            self.tabs.append(frame)
    
    def create_statusbar(self):
        """创建状态栏"""
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 状态标签
        self.status_label = ttk.Label(self.statusbar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.statusbar, length=200)
        self.progress.pack(side=tk.RIGHT, padx=5)
    
    def update_status(self, message: str):
        """
        更新状态栏
        
        Args:
            message: 状态消息
        """
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_progress(self, value: float):
        """
        更新进度条

        Args:
            value: 进度值 (0.0-1.0)
        """
        self.progress['value'] = value * 100
        self.root.update_idletasks()

    def on_tab_changed(self, event):
        """Tab切换事件处理"""
        try:
            selected_tab = event.widget.select()
            tab_index = event.widget.index(selected_tab)

            # 通知当前Tab被选中
            if hasattr(self.tabs[tab_index], 'on_tab_selected'):
                self.tabs[tab_index].on_tab_selected()

            # 通知其他Tab被取消选中
            for i, tab in enumerate(self.tabs):
                if i != tab_index and hasattr(tab, 'on_tab_deselected'):
                    tab.on_tab_deselected()

        except Exception as e:
            self.logger.error(f"Error handling tab change: {e}")

    def show_about(self):
        """显示关于对话框"""
        from tkinter import messagebox

        app_config = self.config.get('app', {})
        about_text = f"""
{app_config.get('name', 'Shot Detection')} v{app_config.get('version', '2.0.0')}

{app_config.get('description', 'Advanced video shot boundary detection tool')}

作者: {app_config.get('author', 'Shot Detection Team')}

这是一个基于人工智能的视频镜头边界检测工具，
支持多种检测算法和批量处理功能。
        """

        messagebox.showinfo("关于", about_text.strip())

    def show_settings(self):
        """显示设置对话框"""
        try:
            from .dialogs.settings_dialog import SettingsDialog

            dialog = SettingsDialog(self.root, self.config)
            if dialog.result:
                # 用户确认了设置更改
                self.config.save_config()
                self.update_status("设置已保存")

        except ImportError:
            # 如果设置对话框还没实现，显示简单消息
            from tkinter import messagebox
            messagebox.showinfo("设置", "设置功能正在开发中...")

    def on_closing(self):
        """窗口关闭事件处理"""
        try:
            # 清理所有Tab资源
            for tab in self.tabs:
                if hasattr(tab, 'cleanup'):
                    tab.cleanup()

            # 保存配置
            self.config.save_config()

            self.logger.info("Application closing")
            self.root.destroy()

        except Exception as e:
            self.logger.error(f"Error during closing: {e}")
            self.root.destroy()

    def setup_menu(self):
        """设置菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self.on_closing)

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="设置...", command=self.show_settings)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于...", command=self.show_about)

    def setup_keyboard_shortcuts(self):
        """设置键盘快捷键"""
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<F1>', lambda e: self.show_about())
        self.root.bind('<Control-comma>', lambda e: self.show_settings())

    def center_window(self):
        """居中显示窗口"""
        self.root.update_idletasks()

        # 获取窗口大小
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # 获取屏幕大小
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 计算居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"+{x}+{y}")

    def run(self):
        """运行应用程序"""
        try:
            # 设置菜单和快捷键
            self.setup_menu()
            self.setup_keyboard_shortcuts()

            # 居中窗口
            self.center_window()

            # 绑定关闭事件
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            # 设置初始状态
            self.update_status("就绪")

            self.logger.info("Starting main loop")

            # 启动主循环
            self.root.mainloop()

        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
