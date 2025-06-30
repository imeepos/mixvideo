#!/usr/bin/env python3
"""
智能镜头检测与分段系统 - 简化GUI界面
提供简洁易用的图形界面操作
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import webbrowser
import subprocess
from typing import Optional

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from video_segmentation import process_video_segmentation
from utils.video_utils import validate_video_file, get_basic_video_info, format_duration, format_file_size
from gui_logger import setup_gui_logging, ProgressMonitor, ProcessingStatus, ResultsAnalyzer
from font_config import FontManager
from video_processing_with_callbacks import process_video_with_gui_callbacks


class ShotDetectionGUI:
    """智能镜头检测与分段系统 - 简化版GUI"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎬 智能镜头检测与分段系统")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)

        # 设置图标和样式
        self.setup_styles()

        # 核心变量
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.quality_mode = tk.StringVar(value="medium")

        # 简化版本的默认设置
        self.organize_mode = tk.StringVar(value="duration")
        self.enable_classification = tk.BooleanVar(value=False)
        self.move_files = tk.BooleanVar(value=False)
        self.min_confidence = tk.DoubleVar(value=0.6)
        self.naming_mode = tk.StringVar(value="preserve-original")

        # 批量处理变量
        self.batch_input_dir = tk.StringVar()
        self.batch_output_dir = tk.StringVar()
        self.batch_quality_mode = tk.StringVar(value="medium")
        self.batch_recursive = tk.BooleanVar(value=False)

        # 视频分析变量
        self.analysis_video_path = tk.StringVar()
        self.analysis_output_dir = tk.StringVar()

        self.processing = False
        self.current_task = None

        # 处理状态
        self.processing_status = ProcessingStatus()
        self.progress_monitor = None

        # 创建界面
        self.create_widgets()

        # 居中窗口
        self.center_window()

    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()

        # 获取最佳中文字体
        font_manager = FontManager()
        font_manager.detect_system_fonts()
        font_manager.detect_chinese_fonts()
        best_font = font_manager.get_best_font()

        # 设置字体（优先使用中文字体，回退到系统默认）
        if best_font:
            default_font = best_font
            print(f"✅ 使用中文字体: {best_font}")
        else:
            # 回退字体列表
            fallback_fonts = ['DejaVu Sans', 'Liberation Sans', 'Arial', 'Helvetica', 'sans-serif']
            default_font = fallback_fonts[0]
            print(f"⚠️ 使用回退字体: {default_font}")

        # 配置样式
        try:
            # 处理字体名称中的空格问题
            font_tuple_title = (default_font, 16, 'bold')
            font_tuple_heading = (default_font, 12, 'bold')
            font_tuple_info = (default_font, 10)
            font_tuple_success = (default_font, 10, 'bold')
            font_tuple_error = (default_font, 10, 'bold')
            font_tuple_warning = (default_font, 10, 'bold')

            style.configure('Title.TLabel', font=font_tuple_title)
            style.configure('Heading.TLabel', font=font_tuple_heading)
            style.configure('Info.TLabel', font=font_tuple_info)
            style.configure('Success.TLabel', foreground='green', font=font_tuple_success)
            style.configure('Error.TLabel', foreground='red', font=font_tuple_error)
            style.configure('Warning.TLabel', foreground='orange', font=font_tuple_warning)

            # 设置默认字体（使用引号包围字体名称）
            if ' ' in default_font:
                self.root.option_add('*Font', f'"{default_font}" 10')
            else:
                self.root.option_add('*Font', f'{default_font} 10')

        except Exception as e:
            # 如果字体设置失败，使用系统默认
            print(f"⚠️ 字体设置失败，使用系统默认: {e}")
            style.configure('Title.TLabel', font=('TkDefaultFont', 16, 'bold'))
            style.configure('Heading.TLabel', font=('TkDefaultFont', 12, 'bold'))
            style.configure('Info.TLabel', font=('TkDefaultFont', 10))
            style.configure('Success.TLabel', foreground='green', font=('TkDefaultFont', 10, 'bold'))
            style.configure('Error.TLabel', foreground='red', font=('TkDefaultFont', 10, 'bold'))
            style.configure('Warning.TLabel', foreground='orange', font=('TkDefaultFont', 10, 'bold'))

    def center_window(self):
        """居中显示窗口"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """创建带Tab的界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="🎬 智能镜头检测与分段系统", style='Title.TLabel')
        title_label.pack(pady=(0, 15))

        # 创建Tab控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建可滚动的Tab页面
        self.create_scrollable_tabs()

        # 创建共享的进度和日志区域
        self.create_shared_progress_section(main_frame)

    def create_scrollable_tabs(self):
        """创建可滚动的Tab页面"""
        # 单个文件处理Tab
        self.single_canvas, self.single_frame = self.create_scrollable_tab("📄 单个文件处理")
        self.create_single_file_interface()

        # 批量处理Tab
        self.batch_canvas, self.batch_frame = self.create_scrollable_tab("📁 批量处理")
        self.create_batch_interface()

        # 视频分析Tab
        self.analysis_canvas, self.analysis_frame = self.create_scrollable_tab("🎥 视频分析")
        self.create_analysis_interface()

    def create_scrollable_tab(self, tab_name):
        """创建单个可滚动的Tab页面"""
        # 创建Tab的主容器
        tab_container = ttk.Frame(self.notebook)
        self.notebook.add(tab_container, text=tab_name)

        # 创建Canvas和滚动条
        canvas = tk.Canvas(tab_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="15")

        # 配置滚动
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 布局Canvas和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")

        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)

        return canvas, scrollable_frame


    def create_single_file_interface(self):
        """创建单个文件处理界面"""
        # 配置网格权重
        self.single_frame.columnconfigure(1, weight=1)

        # 文件选择区域
        self.create_file_selection(self.single_frame, 0)

        # 简化设置区域
        self.create_simple_settings(self.single_frame, 1)

        # 控制按钮区域
        self.create_control_buttons(self.single_frame, 2)

        # 结果区域
        self.create_results_section(self.single_frame, 3)

    def create_batch_interface(self):
        """创建批量处理界面"""
        # 配置网格权重
        self.batch_frame.columnconfigure(1, weight=1)

        # 批量文件选择区域
        self.create_batch_file_selection(self.batch_frame, 0)

        # 批量设置区域
        self.create_batch_settings(self.batch_frame, 1)

        # 批量控制按钮区域
        self.create_batch_control_buttons(self.batch_frame, 2)

        # 批量结果区域
        self.create_batch_results_section(self.batch_frame, 3)

    def create_shared_progress_section(self, parent):
        """创建共享的进度和日志区域"""
        progress_frame = ttk.LabelFrame(parent, text="📊 处理进度", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(2, weight=1)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # 进度百分比标签
        self.progress_percent_label = ttk.Label(progress_frame, text="0%", style='Info.TLabel')
        self.progress_percent_label.grid(row=0, column=1, padx=(10, 0))

        # 状态标签
        self.status_label = ttk.Label(progress_frame, text="就绪", style='Info.TLabel')
        self.status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))

        # 日志文本框（带滚动条）
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_file_selection(self, parent, row):
        """创建文件选择区域"""
        # 文件选择框架
        file_frame = ttk.LabelFrame(parent, text="📁 文件选择", padding="10")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        # 视频文件选择
        ttk.Label(file_frame, text="视频文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.video_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="浏览", command=self.browse_video_file).grid(row=0, column=2)

        # 输出目录选择
        ttk.Label(file_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(file_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(file_frame, text="浏览", command=self.browse_output_dir).grid(row=1, column=2, pady=(10, 0))

    def create_batch_file_selection(self, parent, row):
        """创建批量文件选择区域"""
        # 文件选择框架
        file_frame = ttk.LabelFrame(parent, text="📁 批量文件选择", padding="10")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        # 输入目录选择
        ttk.Label(file_frame, text="输入目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.batch_input_dir, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="浏览", command=self.browse_batch_input_dir).grid(row=0, column=2)

        # 输出目录选择
        ttk.Label(file_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(file_frame, textvariable=self.batch_output_dir, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(file_frame, text="浏览", command=self.browse_batch_output_dir).grid(row=1, column=2, pady=(10, 0))

        # 递归搜索选项
        ttk.Checkbutton(file_frame, text="包含子目录", variable=self.batch_recursive).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(10, 0))

    def create_simple_settings(self, parent, row):
        """创建简化的设置区域"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ 处理设置", padding="10")
        settings_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        # 质量设置
        ttk.Label(settings_frame, text="输出质量:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        quality_combo = ttk.Combobox(settings_frame, textvariable=self.quality_mode,
                                    values=["low", "medium", "high"], state="readonly", width=15)
        quality_combo.grid(row=0, column=1, sticky=tk.W)

        # 简化说明
        info_text = "• low: 快速处理  • medium: 平衡质量  • high: 高质量"
        info_label = ttk.Label(settings_frame, text=info_text, style='Info.TLabel')
        info_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

    def create_batch_settings(self, parent, row):
        """创建批量设置区域"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ 批量处理设置", padding="10")
        settings_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))

        # 质量设置
        ttk.Label(settings_frame, text="输出质量:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        batch_quality_combo = ttk.Combobox(settings_frame, textvariable=self.batch_quality_mode,
                                          values=["low", "medium", "high"], state="readonly", width=15)
        batch_quality_combo.grid(row=0, column=1, sticky=tk.W)

        # 简化说明
        info_text = "• low: 快速处理  • medium: 平衡质量  • high: 高质量"
        info_label = ttk.Label(settings_frame, text=info_text, style='Info.TLabel')
        info_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

    def create_batch_control_buttons(self, parent, row):
        """创建批量控制按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(0, 15))

        # 开始批量处理按钮
        self.batch_start_button = ttk.Button(button_frame, text="🚀 开始批量处理", command=self.start_batch_processing)
        self.batch_start_button.pack(side=tk.LEFT, padx=(0, 15))

        # 停止按钮
        self.batch_stop_button = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_processing, state=tk.DISABLED)
        self.batch_stop_button.pack(side=tk.LEFT, padx=(0, 15))

        # 打开输出目录按钮
        self.batch_open_output_button = ttk.Button(button_frame, text="📁 打开输出目录",
                                                  command=self.open_batch_output_directory, state=tk.DISABLED)
        self.batch_open_output_button.pack(side=tk.LEFT)

    def create_batch_results_section(self, parent, row):
        """创建批量结果区域"""
        self.batch_results_frame = ttk.LabelFrame(parent, text="📋 批量处理结果", padding="10")
        self.batch_results_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E))

        # 结果统计标签
        self.batch_results_label = ttk.Label(self.batch_results_frame, text="", style='Info.TLabel')
        self.batch_results_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def create_analysis_interface(self):
        """创建视频分析界面"""
        # 配置网格权重
        self.analysis_frame.columnconfigure(1, weight=1)

        # 视频分析文件选择区域
        self.create_analysis_file_selection(self.analysis_frame, 0)

        # 分析控制按钮区域
        self.create_analysis_control_buttons(self.analysis_frame, 1)

        # 分析结果区域
        self.create_analysis_results_section(self.analysis_frame, 2)

    def create_analysis_file_selection(self, parent, row):
        """创建视频分析文件选择区域"""
        file_frame = ttk.LabelFrame(parent, text="📁 视频文件选择", padding="10")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        # 视频文件选择
        ttk.Label(file_frame, text="视频文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.analysis_video_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="浏览", command=self.browse_analysis_video_file).grid(row=0, column=2)

        # 输出目录选择
        ttk.Label(file_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(file_frame, textvariable=self.analysis_output_dir, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(file_frame, text="浏览", command=self.browse_analysis_output_dir).grid(row=1, column=2, pady=(10, 0))



    def create_analysis_control_buttons(self, parent, row):
        """创建分析控制按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(0, 15))

        # 开始分析按钮
        self.analysis_start_button = ttk.Button(button_frame, text="🚀 开始分析", command=self.start_video_analysis)
        self.analysis_start_button.pack(side=tk.LEFT, padx=(0, 15))

        # 停止分析按钮
        self.analysis_stop_button = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_processing, state=tk.DISABLED)
        self.analysis_stop_button.pack(side=tk.LEFT, padx=(0, 15))

        # 打开结果目录按钮
        self.analysis_open_output_button = ttk.Button(button_frame, text="📁 打开结果目录",
                                                     command=self.open_analysis_output_directory, state=tk.DISABLED)
        self.analysis_open_output_button.pack(side=tk.LEFT)

    def create_analysis_results_section(self, parent, row):
        """创建分析结果区域"""
        self.analysis_results_frame = ttk.LabelFrame(parent, text="📊 分析结果", padding="10")
        self.analysis_results_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.analysis_results_frame.columnconfigure(0, weight=1)
        self.analysis_results_frame.rowconfigure(1, weight=1)

        # 结果统计标签
        self.analysis_results_label = ttk.Label(self.analysis_results_frame, text="", style='Info.TLabel')
        self.analysis_results_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 结果显示文本框
        self.analysis_results_text = scrolledtext.ScrolledText(self.analysis_results_frame, height=8, wrap=tk.WORD)
        self.analysis_results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置行权重
        parent.rowconfigure(row, weight=1)


    def create_control_buttons(self, parent, row):
        """创建控制按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(0, 15))

        # 开始处理按钮
        self.start_button = ttk.Button(button_frame, text="🚀 开始处理", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 15))

        # 停止按钮
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 15))

        # 打开输出目录按钮
        self.open_output_button = ttk.Button(button_frame, text="📁 打开输出目录",
                                           command=self.open_output_directory, state=tk.DISABLED)
        self.open_output_button.pack(side=tk.LEFT)



    def create_results_section(self, parent, row):
        """创建结果区域"""
        self.results_frame = ttk.LabelFrame(parent, text="📋 处理结果", padding="10")
        self.results_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E))

        # 结果统计标签
        self.results_label = ttk.Label(self.results_frame, text="", style='Info.TLabel')
        self.results_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def browse_video_file(self):
        """浏览视频文件"""
        filetypes = [
            ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v"),
            ("MP4文件", "*.mp4"),
            ("所有文件", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=filetypes
        )

        if filename:
            self.video_path.set(filename)
            self.update_video_info()

            # 自动设置输出目录
            if not self.output_path.get():
                video_dir = Path(filename).parent
                video_name = Path(filename).stem
                default_output = video_dir / f"{video_name}_segments"
                self.output_path.set(str(default_output))

    def browse_output_dir(self):
        """浏览输出目录"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_path.set(dirname)

    def browse_batch_input_dir(self):
        """浏览批量输入目录"""
        dirname = filedialog.askdirectory(title="选择批量输入目录")
        if dirname:
            self.batch_input_dir.set(dirname)

            # 自动设置输出目录
            if not self.batch_output_dir.get():
                default_output = Path(dirname).parent / f"{Path(dirname).name}_batch_segments"
                self.batch_output_dir.set(str(default_output))

    def browse_batch_output_dir(self):
        """浏览批量输出目录"""
        dirname = filedialog.askdirectory(title="选择批量输出目录")
        if dirname:
            self.batch_output_dir.set(dirname)

    def browse_analysis_video_file(self):
        """浏览分析视频文件"""
        filename = filedialog.askopenfilename(
            title="选择要分析的视频文件",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v"), ("所有文件", "*.*")]
        )
        if filename:
            self.analysis_video_path.set(filename)

            # 自动设置输出目录
            if not self.analysis_output_dir.get():
                video_dir = Path(filename).parent
                video_name = Path(filename).stem
                default_output = video_dir / f"{video_name}_analysis"
                self.analysis_output_dir.set(str(default_output))

    def browse_analysis_output_dir(self):
        """浏览分析输出目录"""
        dirname = filedialog.askdirectory(title="选择分析结果输出目录")
        if dirname:
            self.analysis_output_dir.set(dirname)

    def update_video_info(self):
        """更新视频信息显示（简化版）"""
        video_file = self.video_path.get()

        if video_file and os.path.exists(video_file):
            try:
                if validate_video_file(video_file):
                    info = get_basic_video_info(video_file)
                    self.log_message(f"已选择视频: {Path(video_file).name} ({format_duration(info['duration'])})", "INFO")
                else:
                    self.log_message("无效的视频文件格式", "ERROR")
            except Exception as e:
                self.log_message(f"读取视频信息失败: {e}", "ERROR")

    def log_message(self, message, level="INFO"):
        """添加日志消息（线程安全）"""
        def _update_log():
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            # 插入消息
            self.log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n")

            # 滚动到底部
            self.log_text.see(tk.END)

            # 更新界面
            self.root.update_idletasks()

        # 确保在主线程中执行GUI更新
        if threading.current_thread() == threading.main_thread():
            _update_log()
        else:
            self.root.after(0, _update_log)

    def validate_inputs(self):
        """验证输入参数"""
        if not self.video_path.get():
            messagebox.showerror("错误", "请选择视频文件")
            return False

        if not os.path.exists(self.video_path.get()):
            messagebox.showerror("错误", "视频文件不存在")
            return False

        if not validate_video_file(self.video_path.get()):
            messagebox.showerror("错误", "无效的视频文件格式")
            return False

        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出目录")
            return False

        return True

    def validate_batch_inputs(self):
        """验证批量处理输入参数"""
        if not self.batch_input_dir.get():
            messagebox.showerror("错误", "请选择批量输入目录")
            return False

        if not os.path.exists(self.batch_input_dir.get()):
            messagebox.showerror("错误", "批量输入目录不存在")
            return False

        if not self.batch_output_dir.get():
            messagebox.showerror("错误", "请选择批量输出目录")
            return False

        return True

    def start_processing(self):
        """开始处理"""
        if not self.validate_inputs():
            return

        if self.processing:
            messagebox.showwarning("警告", "正在处理中，请等待完成")
            return

        # 设置处理状态
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.status_label.config(text="处理中...")

        # 清除之前的结果
        self.hide_result_buttons()

        # 在新线程中执行处理
        self.current_task = threading.Thread(target=self.process_video_thread)
        self.current_task.daemon = True
        self.current_task.start()

    def process_video_thread(self):
        """视频处理线程"""
        try:
            # 初始化处理状态
            self.processing_status.start("初始化")

            # 设置进度监控
            self.progress_monitor = ProgressMonitor(self.update_progress)
            self.progress_monitor.set_steps([
                "验证输入文件",
                "初始化检测器",
                "执行镜头检测",
                "生成分段信息",
                "切分视频文件",
                "生成项目文件",
                "生成分析报告"
            ])

            self.log_message("🎬 开始智能镜头检测与分段处理", "INFO")
            self.log_message(f"视频文件: {self.video_path.get()}", "INFO")
            self.log_message(f"输出目录: {self.output_path.get()}", "INFO")
            self.log_message(f"组织方式: {self.organize_mode.get()}", "INFO")
            self.log_message(f"输出质量: {self.quality_mode.get()}", "INFO")

            # 归类功能信息
            if self.enable_classification.get():
                self.log_message("🗂️ 自动归类功能: 启用", "INFO")
                self.log_message(f"文件操作: {'移动' if self.move_files.get() else '复制'}", "INFO")
                self.log_message(f"最小置信度: {self.min_confidence.get():.2f}", "INFO")
                self.log_message(f"命名模式: {self.naming_mode.get()}", "INFO")
            else:
                self.log_message("🗂️ 自动归类功能: 禁用", "INFO")

            # 开始处理步骤
            self.progress_monitor.next_step("开始处理...")

            # 准备归类配置
            classification_config = None
            if self.enable_classification.get():
                classification_config = {
                    'move_files': self.move_files.get(),
                    'min_confidence_for_move': self.min_confidence.get(),
                    'naming_mode': self.naming_mode.get(),
                    'create_directories': True,
                    'conflict_resolution': 'rename',
                    'create_backup': False
                }

            # 执行处理（使用带回调的版本）
            success = process_video_with_gui_callbacks(
                self.video_path.get(),
                self.output_path.get(),
                self.organize_mode.get(),
                self.quality_mode.get(),
                progress_callback=self.update_progress,
                log_callback=self.log_message,
                enable_classification=self.enable_classification.get(),
                classification_config=classification_config
            )

            # 完成进度
            self.progress_monitor.complete()

            if success:
                self.log_message("✅ 处理完成！", "SUCCESS")

                # 分析结果
                results = ResultsAnalyzer.analyze_output_directory(self.output_path.get())
                self.processing_status.complete(results)

                self.root.after(0, self.on_processing_success)
            else:
                self.log_message("❌ 处理失败", "ERROR")
                self.processing_status.set_error("处理失败")
                self.root.after(0, self.on_processing_error)

        except Exception as e:
            error_msg = f"处理过程中出错: {e}"
            self.log_message(f"❌ {error_msg}", "ERROR")
            self.processing_status.set_error(error_msg)
            self.root.after(0, self.on_processing_error)
        finally:
            self.root.after(0, self.on_processing_complete)

    def update_progress(self, progress: float, description: str):
        """更新进度回调（线程安全）"""
        def _update_gui():
            # 确保进度值在有效范围内
            progress_value = max(0, min(100, progress))
            self.progress_var.set(progress_value)

            # 更新百分比标签
            if hasattr(self, 'progress_percent_label'):
                self.progress_percent_label.config(text=f"{progress_value:.1f}%")

            # 更新状态标签
            self.status_label.config(text=description)

            # 更新处理状态（如果存在）
            if hasattr(self, 'processing_status'):
                self.processing_status.update_phase(description)

            # 强制更新界面
            self.root.update_idletasks()

        # 确保在主线程中执行GUI更新
        if threading.current_thread() == threading.main_thread():
            _update_gui()
        else:
            self.root.after(0, _update_gui)

    def update_batch_progress(self, current_file: int, total_files: int, file_name: str, file_progress: float = 0):
        """更新批量处理进度"""
        # 计算总体进度：文件进度 + 当前文件内部进度
        overall_progress = ((current_file - 1) / total_files) * 100 + (file_progress / total_files)
        description = f"处理文件 {current_file}/{total_files}: {file_name}"

        self.update_progress(overall_progress, description)

    def stop_processing(self):
        """停止处理"""
        if self.current_task and self.current_task.is_alive():
            # 注意：Python线程无法强制终止，这里只是设置标志
            self.log_message("⚠️ 正在尝试停止处理...", "WARNING")
            self.processing = False

        self.on_processing_complete()

    def on_processing_success(self):
        """处理成功回调"""
        self.status_label.config(text="处理完成")
        self.show_result_buttons()
        self.open_output_button.config(state=tk.NORMAL)

        # 显示结果统计
        self.show_processing_results()

        messagebox.showinfo("成功", "视频处理完成！\n\n点击下方按钮查看结果。")

    def on_processing_error(self):
        """处理失败回调"""
        self.status_label.config(text="处理失败")
        messagebox.showerror("错误", "视频处理失败，请查看日志了解详情。")

    def on_processing_complete(self):
        """处理完成回调（无论成功失败）"""
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.current_task = None

    def show_result_buttons(self):
        """显示结果按钮（简化版本 - 仅更新标签）"""
        if hasattr(self, 'results_label'):
            self.results_label.config(text="处理完成！请查看输出目录。")

    def hide_result_buttons(self):
        """隐藏结果按钮（简化版本 - 仅清空标签）"""
        if hasattr(self, 'results_label'):
            self.results_label.config(text="")

    def show_processing_results(self):
        """显示处理结果统计"""
        if self.processing_status.results:
            # 使用分析器生成的结果
            summary = ResultsAnalyzer.format_results_summary(self.processing_status.results)
            duration = self.processing_status.get_duration()

            result_text = f"{summary}\n\n⏱️ 处理耗时: {duration:.1f}秒"
            self.results_label.config(text=result_text)
        else:
            # 回退到原有逻辑
            output_dir = Path(self.output_path.get())

            if not output_dir.exists():
                return

            # 统计生成的文件
            video_files = []
            for ext in ['.mp4', '.avi', '.mov']:
                video_files.extend(output_dir.glob(f"**/*{ext}"))

            report_files = list(output_dir.glob("*.html"))
            project_files = list(output_dir.glob("*.xml")) + list(output_dir.glob("*.edl"))

            # 计算总大小
            total_size = sum(f.stat().st_size for f in video_files if f.exists())

            result_text = f"""
处理结果统计:
• 生成视频分段: {len(video_files)} 个
• 分析报告: {len(report_files)} 个
• 项目文件: {len(project_files)} 个
• 总文件大小: {format_file_size(total_size)}
            """.strip()

            self.results_label.config(text=result_text)

    def view_analysis_report(self):
        """查看分析报告"""
        report_file = Path(self.output_path.get()) / "analysis_report.html"

        if report_file.exists():
            try:
                webbrowser.open(f"file://{report_file.absolute()}")
                self.log_message("📊 已在浏览器中打开分析报告", "SUCCESS")
            except Exception as e:
                self.log_message(f"打开分析报告失败: {e}", "ERROR")
                messagebox.showerror("错误", f"无法打开分析报告: {e}")
        else:
            messagebox.showwarning("警告", "分析报告文件不存在")

    def view_video_segments(self):
        """查看视频分段"""
        output_dir = Path(self.output_path.get())

        if not output_dir.exists():
            messagebox.showwarning("警告", "输出目录不存在")
            return

        # 尝试多种方法打开目录
        success = False
        error_messages = []

        try:
            if sys.platform == "win32":
                # Windows
                os.startfile(str(output_dir))
                success = True
            elif sys.platform == "darwin":
                # macOS
                subprocess.run(["open", str(output_dir)], check=True)
                success = True
            else:
                # Linux - 尝试多种方法
                methods = [
                    ["xdg-open", str(output_dir)],
                    ["nautilus", str(output_dir)],
                    ["dolphin", str(output_dir)],
                    ["thunar", str(output_dir)],
                    ["pcmanfm", str(output_dir)],
                    ["caja", str(output_dir)]
                ]

                for method in methods:
                    try:
                        subprocess.run(method, check=True, capture_output=True)
                        success = True
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError) as e:
                        error_messages.append(f"{method[0]}: {e}")
                        continue

        except Exception as e:
            error_messages.append(f"系统调用失败: {e}")

        if success:
            self.log_message("📁 已打开视频分段目录", "SUCCESS")
        else:
            # 如果所有方法都失败，显示目录路径并提供手动选项
            self.log_message("⚠️ 无法自动打开目录，请手动访问", "WARNING")
            self.show_directory_info_dialog(output_dir, error_messages)

    def show_directory_info_dialog(self, output_dir: Path, error_messages: list):
        """显示目录信息对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("📁 输出目录信息")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="无法自动打开目录", style='Heading.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # 目录路径
        path_frame = ttk.LabelFrame(main_frame, text="输出目录路径", padding="10")
        path_frame.pack(fill=tk.X, pady=(0, 10))

        path_text = tk.Text(path_frame, height=2, wrap=tk.WORD)
        path_text.insert(1.0, str(output_dir))
        path_text.config(state=tk.DISABLED)
        path_text.pack(fill=tk.X)

        # 复制路径按钮
        def copy_path():
            dialog.clipboard_clear()
            dialog.clipboard_append(str(output_dir))
            messagebox.showinfo("成功", "路径已复制到剪贴板")

        ttk.Button(path_frame, text="📋 复制路径", command=copy_path).pack(anchor=tk.E, pady=(5, 0))

        # 文件列表
        files_frame = ttk.LabelFrame(main_frame, text="生成的文件", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 创建文件树
        tree = ttk.Treeview(files_frame, columns=('size', 'type'), show='tree headings')
        tree.heading('#0', text='文件名')
        tree.heading('size', text='大小')
        tree.heading('type', text='类型')

        tree.column('#0', width=300)
        tree.column('size', width=100)
        tree.column('type', width=150)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 填充文件信息
        try:
            for item in output_dir.iterdir():
                if item.is_file():
                    size = self.format_file_size(item.stat().st_size)
                    file_type = self.get_file_type_description(item.suffix)
                    tree.insert('', tk.END, text=item.name, values=(size, file_type))
                elif item.is_dir():
                    # 添加目录
                    dir_node = tree.insert('', tk.END, text=f"📁 {item.name}/", values=("目录", "文件夹"))
                    # 添加目录中的文件
                    try:
                        for subitem in item.iterdir():
                            if subitem.is_file():
                                size = self.format_file_size(subitem.stat().st_size)
                                file_type = self.get_file_type_description(subitem.suffix)
                                tree.insert(dir_node, tk.END, text=subitem.name, values=(size, file_type))
                    except PermissionError:
                        tree.insert(dir_node, tk.END, text="(无法访问)", values=("", ""))
        except Exception as e:
            tree.insert('', tk.END, text=f"错误: {e}", values=("", ""))

        # 错误信息（如果有）
        if error_messages:
            error_frame = ttk.LabelFrame(main_frame, text="错误信息", padding="10")
            error_frame.pack(fill=tk.X, pady=(0, 10))

            error_text = tk.Text(error_frame, height=4, wrap=tk.WORD)
            error_text.insert(1.0, "\n".join(error_messages))
            error_text.config(state=tk.DISABLED)
            error_text.pack(fill=tk.X)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        # 尝试终端打开
        def open_in_terminal():
            try:
                if sys.platform.startswith('linux'):
                    # 尝试在终端中打开
                    terminal_commands = [
                        ["gnome-terminal", "--working-directory", str(output_dir)],
                        ["konsole", "--workdir", str(output_dir)],
                        ["xterm", "-e", f"cd '{output_dir}' && bash"],
                        ["x-terminal-emulator", "-e", f"cd '{output_dir}' && bash"]
                    ]

                    for cmd in terminal_commands:
                        try:
                            subprocess.run(cmd, check=True, capture_output=True)
                            messagebox.showinfo("成功", "已在终端中打开目录")
                            return
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            continue

                    messagebox.showwarning("失败", "无法打开终端")
                else:
                    messagebox.showinfo("提示", "此功能仅在Linux系统上可用")
            except Exception as e:
                messagebox.showerror("错误", f"打开终端失败: {e}")

        ttk.Button(button_frame, text="🖥️ 在终端中打开", command=open_in_terminal).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="关闭", command=dialog.destroy).pack(side=tk.RIGHT)

    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f}{size_names[i]}"

    def view_project_files(self):
        """查看项目文件"""
        output_dir = Path(self.output_path.get())
        project_files = []

        if output_dir.exists():
            project_files.extend(output_dir.glob("*.xml"))
            project_files.extend(output_dir.glob("*.edl"))
            project_files.extend(output_dir.glob("*.json"))
            project_files.extend(output_dir.glob("*.csv"))

        if project_files:
            # 创建项目文件查看窗口
            self.show_project_files_window(project_files)
        else:
            messagebox.showwarning("警告", "未找到项目文件")

    def show_project_files_window(self, project_files):
        """显示项目文件窗口"""
        window = tk.Toplevel(self.root)
        window.title("📤 项目文件")
        window.geometry("600x400")
        window.transient(self.root)
        window.grab_set()

        # 文件列表
        frame = ttk.Frame(window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="生成的项目文件:", style='Heading.TLabel').pack(anchor=tk.W, pady=(0, 10))

        # 创建树形视图
        tree = ttk.Treeview(frame, columns=('size', 'type'), show='tree headings')
        tree.heading('#0', text='文件名')
        tree.heading('size', text='大小')
        tree.heading('type', text='类型')

        tree.column('#0', width=300)
        tree.column('size', width=100)
        tree.column('type', width=150)

        # 添加文件
        for file_path in project_files:
            file_size = format_file_size(file_path.stat().st_size)
            file_type = self.get_file_type_description(file_path.suffix)

            tree.insert('', tk.END, text=file_path.name, values=(file_size, file_type))

        tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="打开目录",
                  command=lambda: self.view_video_segments()).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="关闭",
                  command=window.destroy).pack(side=tk.RIGHT)

    def get_file_type_description(self, extension):
        """获取文件类型描述"""
        descriptions = {
            '.html': 'HTML分析报告',
            '.json': 'JSON数据文件',
            '.csv': 'CSV表格文件',
            '.xml': 'XML项目文件',
            '.edl': 'EDL编辑列表',
            '.mp4': 'MP4视频文件',
            '.avi': 'AVI视频文件',
            '.mov': 'MOV视频文件'
        }
        return descriptions.get(extension.lower(), '未知类型')

    def open_output_directory(self):
        """打开输出目录"""
        self.view_video_segments()

    def start_batch_processing(self):
        """开始批量处理"""
        if self.processing:
            messagebox.showwarning("警告", "正在处理中，请等待完成")
            return

        if not self.validate_batch_inputs():
            return

        # 更新界面状态
        self.processing = True
        self.batch_start_button.config(state=tk.DISABLED)
        self.batch_stop_button.config(state=tk.NORMAL)
        self.batch_open_output_button.config(state=tk.DISABLED)
        self.status_label.config(text="正在批量处理...")
        self.progress_var.set(0)

        # 在新线程中执行批量处理
        self.current_task = threading.Thread(target=self._batch_processing_worker, daemon=True)
        self.current_task.start()

    def _batch_processing_worker(self):
        """批量处理工作线程"""
        try:
            input_dir = Path(self.batch_input_dir.get())
            output_dir = Path(self.batch_output_dir.get())
            quality = self.batch_quality_mode.get()
            recursive = self.batch_recursive.get()

            # 查找所有视频文件
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
            video_files = []

            if recursive:
                for ext in video_extensions:
                    video_files.extend(input_dir.rglob(f"*{ext}"))
                    video_files.extend(input_dir.rglob(f"*{ext.upper()}"))
            else:
                for ext in video_extensions:
                    video_files.extend(input_dir.glob(f"*{ext}"))
                    video_files.extend(input_dir.glob(f"*{ext.upper()}"))

            if not video_files:
                self.log_message("未找到视频文件", "WARNING")
                self._finish_batch_processing()
                return

            self.log_message(f"找到 {len(video_files)} 个视频文件，开始批量处理...", "INFO")

            success_count = 0
            total_files = len(video_files)

            for i, video_file in enumerate(video_files):
                if not self.processing:  # 检查是否被停止
                    break

                try:
                    # 更新批量处理进度
                    current_file_num = i + 1
                    self.root.after(0, lambda: self.update_batch_progress(
                        current_file_num, total_files, video_file.name, 0
                    ))

                    # 创建输出目录
                    relative_path = video_file.relative_to(input_dir)
                    video_output_dir = output_dir / relative_path.parent / f"{relative_path.stem}_segments"
                    video_output_dir.mkdir(parents=True, exist_ok=True)

                    self.log_message(f"处理文件 {current_file_num}/{total_files}: {video_file.name}", "INFO")

                    # 创建单个文件的进度回调
                    def file_progress_callback(progress, description):
                        self.root.after(0, lambda: self.update_batch_progress(
                            current_file_num, total_files, video_file.name, progress
                        ))

                    # 处理单个视频文件
                    success = process_video_with_gui_callbacks(
                        str(video_file),
                        str(video_output_dir),
                        "duration",  # 默认按时长组织
                        quality,
                        progress_callback=file_progress_callback,  # 传递进度回调
                        log_callback=self.log_message,
                        enable_classification=False,
                        classification_config=None
                    )

                    if success:
                        success_count += 1
                        self.log_message(f"✅ {video_file.name} 处理完成", "SUCCESS")
                    else:
                        self.log_message(f"❌ {video_file.name} 处理失败", "ERROR")

                except Exception as e:
                    self.log_message(f"❌ {video_file.name} 处理出错: {e}", "ERROR")

            # 完成处理
            self.log_message(f"批量处理完成！成功处理 {success_count}/{total_files} 个文件", "SUCCESS")

            # 更新批量结果显示
            if hasattr(self, 'batch_results_label'):
                result_text = f"批量处理完成！成功: {success_count}, 失败: {total_files - success_count}, 总计: {total_files}"
                self.root.after(0, lambda: self.batch_results_label.config(text=result_text))

        except Exception as e:
            self.log_message(f"批量处理出错: {e}", "ERROR")
        finally:
            self.root.after(0, self._finish_batch_processing)

    def _finish_batch_processing(self):
        """完成批量处理"""
        self.processing = False
        self.batch_start_button.config(state=tk.NORMAL)
        self.batch_stop_button.config(state=tk.DISABLED)
        self.batch_open_output_button.config(state=tk.NORMAL)

        # 更新进度显示
        self.progress_var.set(100)
        if hasattr(self, 'progress_percent_label'):
            self.progress_percent_label.config(text="100.0%")
        self.status_label.config(text="批量处理完成")

        # 显示完成消息
        messagebox.showinfo("完成", "批量处理完成！请查看日志了解详细结果。")

    def open_batch_output_directory(self):
        """打开批量输出目录"""
        output_dir = self.batch_output_dir.get()
        if not output_dir or not os.path.exists(output_dir):
            messagebox.showwarning("警告", "输出目录不存在")
            return

        try:
            if sys.platform == "win32":
                os.startfile(str(output_dir))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(output_dir)], check=True)
            else:
                subprocess.run(["xdg-open", str(output_dir)], check=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开输出目录: {e}")

    def start_video_analysis(self):
        """开始视频分析"""
        if self.processing:
            messagebox.showwarning("警告", "正在处理中，请等待完成")
            return

        if not self.validate_analysis_inputs():
            return

        # 更新界面状态
        self.processing = True
        self.analysis_start_button.config(state=tk.DISABLED)
        self.analysis_stop_button.config(state=tk.NORMAL)
        self.analysis_open_output_button.config(state=tk.DISABLED)
        self.status_label.config(text="正在分析视频...")
        self.progress_var.set(0)

        # 清空结果显示
        self.analysis_results_text.delete(1.0, tk.END)
        self.analysis_results_label.config(text="")

        # 在新线程中执行视频分析
        self.current_task = threading.Thread(target=self._video_analysis_worker, daemon=True)
        self.current_task.start()

    def validate_analysis_inputs(self):
        """验证视频分析输入参数"""
        if not self.analysis_video_path.get():
            messagebox.showerror("错误", "请选择要分析的视频文件")
            return False

        if not os.path.exists(self.analysis_video_path.get()):
            messagebox.showerror("错误", "视频文件不存在")
            return False

        if not self.analysis_output_dir.get():
            messagebox.showerror("错误", "请选择输出目录")
            return False

        return True

    def _video_analysis_worker(self):
        """视频分析工作线程"""
        try:
            video_path = self.analysis_video_path.get()
            output_dir = Path(self.analysis_output_dir.get())

            # 从配置文件加载Gemini配置
            from config import get_config
            config = get_config()
            gemini_config = config.gemini

            # 创建输出目录
            output_dir.mkdir(parents=True, exist_ok=True)

            self.log_message(f"开始分析视频: {Path(video_path).name}", "INFO")
            self.update_progress(10, "初始化Gemini客户端...")

            # 导入并使用提示词
            from prompts_manager import PromptsManager
            prompts_manager = PromptsManager()
            analysis_prompt = prompts_manager.get_video_analysis_prompt()

            if not analysis_prompt:
                self.log_message("无法加载视频分析提示词", "ERROR")
                self._finish_video_analysis()
                return

            self.update_progress(20, "加载分析提示词...")
            self.log_message(f"使用提示词长度: {len(analysis_prompt)} 字符", "INFO")

            # 调用新的Gemini API进行视频分析
            self.update_progress(40, "初始化Gemini分析器...")
            self._real_gemini_analysis(video_path, output_dir, analysis_prompt, gemini_config)

        except Exception as e:
            self.log_message(f"视频分析出错: {e}", "ERROR")
            self.root.after(0, self._finish_video_analysis)

    def _real_gemini_analysis(self, video_path, output_dir, prompt, gemini_config):
        """真实的Gemini分析过程"""
        try:
            import json
            from gemini_video_analyzer import create_gemini_analyzer, AnalysisProgress

            self.log_message("🔧 配置Gemini分析器...", "INFO")
            self.log_message(f"  - Cloudflare项目: {gemini_config.cloudflare_project_id}", "INFO")
            self.log_message(f"  - Google项目: {gemini_config.google_project_id}", "INFO")
            self.log_message(f"  - 模型: {gemini_config.model_name}", "INFO")
            self.log_message(f"  - 区域: {', '.join(gemini_config.regions)}", "INFO")
            self.log_message(f"  - 缓存: {'启用' if gemini_config.enable_cache else '禁用'}", "INFO")

            # 创建分析器
            analyzer = create_gemini_analyzer(
                cloudflare_project_id=gemini_config.cloudflare_project_id,
                cloudflare_gateway_id=gemini_config.cloudflare_gateway_id,
                google_project_id=gemini_config.google_project_id,
                regions=gemini_config.regions,
                model_name=gemini_config.model_name,
                enable_cache=gemini_config.enable_cache,
                cache_dir=gemini_config.cache_dir
            )

            # 显示缓存统计
            cache_stats = analyzer.get_cache_stats()
            if cache_stats.get('enabled'):
                self.log_message(f"📊 缓存统计: {cache_stats.get('total_files', 0)} 个文件", "INFO")

            # 定义进度回调
            def progress_callback(progress: AnalysisProgress):
                self.root.after(0, lambda: self.update_progress(progress.progress, progress.step))
                self.log_message(f"📊 {progress.step} ({progress.progress}%)", "INFO")

            self.update_progress(50, "开始视频分析...")

            # 执行分析
            result = analyzer.analyze_video(video_path, prompt, progress_callback)

            # 保存结果
            result_file = output_dir / f"{Path(video_path).stem}_gemini_analysis.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            self.log_message("✅ Gemini分析完成！", "SUCCESS")

            # 自动归类视频文件
            self._auto_classify_video(video_path, result)

            # 显示简洁的结果摘要
            self.root.after(0, lambda: self._show_analysis_summary(result, result_file))

        except Exception as e:
            self.log_message(f"❌ Gemini分析失败: {e}", "ERROR")
            # 如果真实API失败，回退到模拟分析
            self.log_message("⚠️ 回退到模拟分析模式...", "WARNING")
            self.root.after(0, lambda: self._simulate_gemini_analysis(video_path, output_dir, prompt))

    def _display_gemini_results(self, result, result_file):
        """显示Gemini分析结果"""
        try:
            # 更新结果标签
            video_info = result.get('video_info', {})
            analysis_result = result.get('analysis_result', {})

            self.analysis_results_label.config(
                text=f"Gemini分析完成！模型: {video_info.get('model_used', 'unknown')} | 结果已保存: {result_file.name}"
            )

            # 在文本框中显示详细结果
            self.analysis_results_text.delete(1.0, tk.END)

            # 格式化显示结果
            display_text = f"""🤖 Gemini AI 视频分析结果

📹 视频信息:
• 文件名: {video_info.get('file_name', 'unknown')}
• 分析时间: {video_info.get('analysis_time', 'unknown')}
• 使用模型: {video_info.get('model_used', 'unknown')}

📊 分析结果:
"""

            # 显示分析内容
            content_analysis = analysis_result.get('content_analysis', {})

            if 'summary' in content_analysis:
                display_text += f"\n📝 内容摘要:\n{content_analysis['summary']}\n"

            # 显示高光时刻
            highlights = self._extract_highlights(analysis_result)
            if highlights:
                display_text += f"\n✨ 高光时刻:\n"
                for i, highlight in enumerate(highlights, 1):
                    timestamp = highlight.get('timestamp', '未知时间')
                    description = highlight.get('description', '无描述')
                    confidence = highlight.get('confidence', 0)
                    display_text += f"  {i}. [{timestamp}] {description}"
                    if confidence > 0:
                        display_text += f" (置信度: {confidence:.1%})"
                    display_text += "\n"

            # 显示场景分析
            scenes = analysis_result.get('scenes', [])
            if scenes:
                display_text += f"\n🎬 场景分析:\n"
                for i, scene in enumerate(scenes[:5], 1):  # 只显示前5个场景
                    timestamp = scene.get('timestamp', '未知时间')
                    description = scene.get('description', '无描述')
                    display_text += f"  {i}. [{timestamp}] {description}\n"
                if len(scenes) > 5:
                    display_text += f"  ... 还有 {len(scenes) - 5} 个场景\n"

            # 显示情感分析
            emotions = analysis_result.get('emotions', {})
            if emotions:
                display_text += f"\n😊 情感分析:\n"
                if isinstance(emotions, dict):
                    for emotion, score in emotions.items():
                        if isinstance(score, (int, float)):
                            display_text += f"  • {emotion}: {score:.1%}\n"
                        else:
                            display_text += f"  • {emotion}: {score}\n"
                else:
                    display_text += f"  {emotions}\n"

            # 显示质量评估
            quality = analysis_result.get('quality', {})
            if quality:
                display_text += f"\n📊 质量评估:\n"
                if isinstance(quality, dict):
                    for metric, value in quality.items():
                        display_text += f"  • {metric}: {value}\n"
                else:
                    display_text += f"  {quality}\n"

            if 'full_text' in content_analysis:
                display_text += f"\n📄 完整分析:\n{content_analysis['full_text']}\n"

            # 如果有其他结构化数据，也显示出来
            for key, value in content_analysis.items():
                if key not in ['summary', 'full_text'] and isinstance(value, (str, list, dict)):
                    if isinstance(value, list):
                        display_text += f"\n🏷️ {key}: {', '.join(map(str, value))}\n"
                    elif isinstance(value, dict):
                        display_text += f"\n📋 {key}:\n"
                        for sub_key, sub_value in value.items():
                            display_text += f"  • {sub_key}: {sub_value}\n"
                    else:
                        display_text += f"\n📌 {key}: {value}\n"

            display_text += f"\n📁 结果文件: {result_file}"

            self.analysis_results_text.insert(tk.END, display_text)
            self.log_message(f"Gemini分析完成！结果已保存到: {result_file}", "SUCCESS")

        except Exception as e:
            self.log_message(f"结果显示出错: {e}", "ERROR")

    def _simulate_gemini_analysis(self, video_path, output_dir, prompt):
        """模拟Gemini分析过程（实际使用时需要替换为真实的API调用）"""
        import json
        import time

        try:
            # 模拟分析过程
            self.update_progress(60, "分析视频内容...")
            time.sleep(2)  # 模拟处理时间

            self.update_progress(80, "生成分析报告...")

            # 模拟分析结果 - 使用新格式包含高光时刻
            analysis_result = {
                "video_info": {
                    "file_name": Path(video_path).name,
                    "file_path": str(video_path),
                    "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "model_used": "模拟分析器"
                },
                "analysis_result": {
                    "summary": "这是一个女装产品展示视频，主要展示服装的产品细节和穿着效果，包含多个精彩的展示瞬间。",
                    "highlights": [
                        {
                            "timestamp": "00:05",
                            "description": "产品特写镜头，展示面料质感和细节工艺",
                            "type": "视觉",
                            "confidence": 0.88,
                            "duration": "3"
                        },
                        {
                            "timestamp": "00:18",
                            "description": "模特优雅转身，展示服装的整体轮廓",
                            "type": "动作",
                            "confidence": 0.92,
                            "duration": "4"
                        },
                        {
                            "timestamp": "00:25",
                            "description": "服装细节特写，突出设计亮点",
                            "type": "视觉",
                            "confidence": 0.85,
                            "duration": "2"
                        }
                    ],
                    "scenes": [
                        {
                            "timestamp": "00:00",
                            "description": "产品展示场景，白色背景下的服装细节展示",
                            "objects": ["服装", "白色背景", "展示台"],
                            "actions": ["静态展示", "细节特写"],
                            "mood": "专业"
                        },
                        {
                            "timestamp": "00:15",
                            "description": "模特试穿场景，展示服装的穿着效果",
                            "objects": ["模特", "服装", "背景"],
                            "actions": ["试穿", "转身", "摆pose"],
                            "mood": "优雅"
                        }
                    ],
                    "emotions": {
                        "overall_mood": "优雅、时尚、专业",
                        "emotion_changes": [
                            {
                                "timestamp": "00:10",
                                "emotion": "专业",
                                "intensity": 0.8
                            },
                            {
                                "timestamp": "00:20",
                                "emotion": "优雅",
                                "intensity": 0.9
                            }
                        ]
                    },
                    "quality": {
                        "video_quality": 8,
                        "audio_quality": 7,
                        "lighting": "均匀柔光，专业布光",
                        "stability": "稳定，无抖动"
                    },
                    "technical": {
                        "resolution": "1080p",
                        "frame_rate": "30fps",
                        "color_grading": "自然色调，饱和度适中",
                        "camera_movements": ["固定镜头", "特写", "全景"]
                    }
                },
                "metadata": {
                    "response_length": 1200,
                    "candidates_count": 1,
                    "success": True
                },
                "confidence": 0.92
            }

            # 保存分析结果
            result_file = output_dir / f"{Path(video_path).stem}_gemini_analysis.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)

            self.update_progress(100, "分析完成")

            # 自动归类视频文件
            self._auto_classify_video(video_path, analysis_result)

            # 显示简洁的结果摘要
            self.root.after(0, lambda: self._show_analysis_summary(analysis_result, result_file))

        except Exception as e:
            self.log_message(f"分析过程出错: {e}", "ERROR")
        finally:
            self.root.after(0, self._finish_video_analysis)

    def _display_analysis_results(self, result, result_file):
        """显示分析结果"""
        # 更新结果标签
        summary = result.get('content_analysis', {}).get('summary', '无摘要')
        confidence = result.get('confidence', 0)
        self.analysis_results_label.config(text=f"分析完成！置信度: {confidence:.2f} | 结果已保存: {result_file.name}")

        # 在文本框中显示详细结果
        self.analysis_results_text.delete(1.0, tk.END)

        # 格式化显示结果
        display_text = f"""📊 视频分析结果

📹 视频信息:
• 文件名: {result['video_info']['file_name']}
• 分析时间: {result['video_info']['analysis_time']}

📝 内容摘要:
{summary}

🎭 情感基调: {result['content_analysis']['emotion']}

🏷️ 关键词: {', '.join(result['content_analysis']['keywords'])}

🎬 场景分析:"""

        for i, scene in enumerate(result['content_analysis']['scenes'], 1):
            display_text += f"\n  {i}. {scene['start_time']} - {scene['end_time']}: {scene['description']}"

        display_text += f"""

🎯 识别对象: {', '.join(result['content_analysis']['objects'])}

📷 技术分析:
• 拍摄风格: {result['technical_analysis']['shooting_style']}
• 构图方式: {result['technical_analysis']['composition']}
• 光线效果: {result['technical_analysis']['lighting']}
• 画质评估: {result['technical_analysis']['quality']}

✅ 置信度: {confidence:.2f}

📁 结果文件: {result_file}
"""

        self.analysis_results_text.insert(tk.END, display_text)
        self.log_message(f"分析完成！结果已保存到: {result_file}", "SUCCESS")

    def _finish_video_analysis(self):
        """完成视频分析"""
        self.processing = False
        self.analysis_start_button.config(state=tk.NORMAL)
        self.analysis_stop_button.config(state=tk.DISABLED)
        self.analysis_open_output_button.config(state=tk.NORMAL)
        self.status_label.config(text="视频分析完成")

    def open_analysis_output_directory(self):
        """打开分析输出目录"""
        output_dir = self.analysis_output_dir.get()
        if not output_dir or not os.path.exists(output_dir):
            messagebox.showwarning("警告", "输出目录不存在")
            return

        try:
            if sys.platform == "win32":
                os.startfile(str(output_dir))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(output_dir)], check=True)
            else:
                subprocess.run(["xdg-open", str(output_dir)], check=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开输出目录: {e}")

    def _auto_classify_video(self, video_path, analysis_result):
        """根据分析结果使用Gemini智能归类视频文件"""
        try:
            video_file = Path(video_path)
            if not video_file.exists():
                self.log_message(f"⚠️ 视频文件不存在，跳过归类: {video_path}", "WARNING")
                return

            # 获取分析结果
            analysis_data = analysis_result.get('analysis_result', analysis_result.get('content_analysis', {}))

            # 使用Gemini进行智能归类
            self.log_message("🤖 正在使用Gemini进行智能归类...", "INFO")
            category_info = self._gemini_classify_video(analysis_data)

            if not category_info:
                # 如果Gemini归类失败，使用备用逻辑
                self.log_message("⚠️ Gemini归类失败，使用备用归类逻辑", "WARNING")
                category_folder = self._determine_category_fallback(analysis_data)
                confidence = 0.5
                reason = "备用逻辑归类"
            else:
                category_folder = category_info.get('category', 'standard')
                confidence = category_info.get('confidence', 0.8)
                reason = category_info.get('reason', '智能分析')

            # 创建归类目录
            output_base = Path(self.analysis_output_dir.get())
            category_path = output_base / "classified" / category_folder
            category_path.mkdir(parents=True, exist_ok=True)

            # 生成新文件名（避免冲突）
            new_filename = self._generate_classified_filename(video_file, analysis_data, category_info)
            target_path = category_path / new_filename

            # 如果目标文件已存在，添加序号
            counter = 1
            original_target = target_path
            while target_path.exists():
                stem = original_target.stem
                suffix = original_target.suffix
                target_path = original_target.parent / f"{stem}_{counter}{suffix}"
                counter += 1

            # 复制文件到归类目录
            import shutil
            shutil.copy2(video_file, target_path)

            self.log_message(f"📁 视频已智能归类到: {category_folder}/{target_path.name} (置信度: {confidence:.1%})", "SUCCESS")
            self.log_message(f"📝 归类原因: {reason}", "INFO")

            # 保存归类信息
            self._save_classification_info(target_path, analysis_result, video_file, category_info)

        except Exception as e:
            self.log_message(f"❌ 视频归类失败: {e}", "ERROR")

    def _determine_category(self, analysis_data):
        """根据分析数据确定归类文件夹"""
        # 获取高光时刻数量
        highlights = analysis_data.get('highlights', [])
        highlight_count = len(highlights)

        # 获取情感分析
        emotions = analysis_data.get('emotions', {})
        overall_mood = emotions.get('overall_mood', '').lower()

        # 获取质量评估
        quality = analysis_data.get('quality', {})
        video_quality = quality.get('video_quality', 0)

        # 获取技术信息
        technical = analysis_data.get('technical', {})
        resolution = technical.get('resolution', '').lower()

        # 归类逻辑
        if highlight_count >= 3 and video_quality >= 8:
            return "premium_highlights"  # 优质高光
        elif highlight_count >= 2:
            return "good_highlights"     # 良好高光
        elif 'elegant' in overall_mood or 'professional' in overall_mood or '优雅' in overall_mood or '专业' in overall_mood:
            return "elegant_style"       # 优雅风格
        elif 'active' in overall_mood or 'energetic' in overall_mood or '活泼' in overall_mood or '活力' in overall_mood:
            return "active_style"        # 活泼风格
        elif '1080p' in resolution or 'hd' in resolution:
            return "hd_quality"          # 高清质量
        elif video_quality >= 7:
            return "good_quality"        # 良好质量
        else:
            return "standard"            # 标准分类

    def _generate_classified_filename(self, original_file, analysis_data):
        """生成归类后的文件名"""
        # 获取原始文件名（不含扩展名）
        original_stem = original_file.stem
        extension = original_file.suffix

        # 获取高光时刻数量
        highlights = analysis_data.get('highlights', [])
        highlight_count = len(highlights)

        # 获取质量评分
        quality = analysis_data.get('quality', {})
        video_quality = quality.get('video_quality', 0)

        # 生成描述性前缀
        prefix_parts = []

        if highlight_count >= 3:
            prefix_parts.append("多高光")
        elif highlight_count >= 1:
            prefix_parts.append("有高光")

        if video_quality >= 8:
            prefix_parts.append("优质")
        elif video_quality >= 7:
            prefix_parts.append("良好")

        # 组合文件名
        if prefix_parts:
            prefix = "_".join(prefix_parts)
            new_filename = f"{prefix}_{original_stem}{extension}"
        else:
            new_filename = f"{original_stem}{extension}"

        return new_filename

    def _save_classification_info(self, target_path, analysis_result, original_path):
        """保存归类信息"""
        try:
            info_file = target_path.with_suffix('.classification.json')

            classification_info = {
                "original_path": str(original_path),
                "classified_path": str(target_path),
                "classification_time": __import__('time').strftime("%Y-%m-%d %H:%M:%S"),
                "category": target_path.parent.name,
                "analysis_summary": {
                    "highlights_count": len(analysis_result.get('analysis_result', {}).get('highlights', [])),
                    "video_quality": analysis_result.get('analysis_result', {}).get('quality', {}).get('video_quality', 0),
                    "overall_mood": analysis_result.get('analysis_result', {}).get('emotions', {}).get('overall_mood', ''),
                    "summary": analysis_result.get('analysis_result', {}).get('summary', '')
                }
            }

            with open(info_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(classification_info, f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.log_message(f"⚠️ 保存归类信息失败: {e}", "WARNING")

    def _show_analysis_summary(self, result, result_file):
        """显示简洁美观的分析结果摘要"""
        try:
            # 获取分析数据
            video_info = result.get('video_info', {})
            analysis_data = result.get('analysis_result', result.get('content_analysis', {}))

            # 提取关键信息
            highlights = self._extract_highlights(result)
            summary = analysis_data.get('summary', '无摘要')
            quality = analysis_data.get('quality', {})
            emotions = analysis_data.get('emotions', {})

            # 更新结果标签 - 简洁版本
            file_name = video_info.get('file_name', 'unknown')
            highlight_count = len(highlights)
            video_quality = quality.get('video_quality', 0)

            # 确定归类信息
            category = self._determine_category(analysis_data)
            category_names = {
                "premium_highlights": "优质高光",
                "good_highlights": "良好高光",
                "elegant_style": "优雅风格",
                "active_style": "活泼风格",
                "hd_quality": "高清质量",
                "good_quality": "良好质量",
                "standard": "标准分类"
            }
            category_display = category_names.get(category, category)

            # 简洁的状态显示
            status_text = f"✅ 分析完成 | {file_name} | {highlight_count}个高光 | 质量:{video_quality}/10 | 归类:{category_display}"
            self.analysis_results_label.config(text=status_text)

            # 在文本框中显示精简的结果
            self.analysis_results_text.delete(1.0, tk.END)

            # 创建精简的显示内容
            display_content = f"""📊 分析摘要
{summary}

✨ 高光时刻 ({len(highlights)}个):"""

            if highlights:
                for i, highlight in enumerate(highlights[:5], 1):  # 只显示前5个
                    timestamp = highlight.get('timestamp', '未知')
                    description = highlight.get('description', '无描述')
                    highlight_type = highlight.get('type', '')
                    confidence = highlight.get('confidence', 0)

                    display_content += f"\n  {i}. [{timestamp}] {description}"
                    if highlight_type:
                        display_content += f" ({highlight_type})"
                    if confidence > 0:
                        display_content += f" [{confidence:.0%}]"

                if len(highlights) > 5:
                    display_content += f"\n  ... 还有 {len(highlights) - 5} 个高光时刻"
            else:
                display_content += "\n  暂无高光时刻"

            # 添加质量和情感信息
            if quality:
                display_content += f"\n\n📊 质量评估: {video_quality}/10"
                if quality.get('lighting'):
                    display_content += f" | 光线: {quality['lighting']}"

            if emotions and emotions.get('overall_mood'):
                display_content += f"\n😊 整体情感: {emotions['overall_mood']}"

            # 添加归类信息
            display_content += f"\n\n📁 自动归类: {category_display}"
            display_content += f"\n💾 结果文件: {result_file.name}"

            # 显示内容
            self.analysis_results_text.insert(tk.END, display_content)

            # 添加操作按钮区域
            self._add_result_action_buttons(result_file)

            self.log_message("✅ 分析结果显示完成", "SUCCESS")

        except Exception as e:
            self.log_message(f"❌ 结果显示失败: {e}", "ERROR")
            # 回退到原始显示方法
            self._display_gemini_results(result, result_file)

    def _add_result_action_buttons(self, result_file):
        """添加结果操作按钮"""
        try:
            # 检查是否已经有按钮框架
            if hasattr(self, 'result_buttons_frame'):
                self.result_buttons_frame.destroy()

            # 创建按钮框架
            self.result_buttons_frame = ttk.Frame(self.analysis_frame)
            self.result_buttons_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

            # 添加操作按钮
            ttk.Button(
                self.result_buttons_frame,
                text="📂 打开结果文件",
                command=lambda: self._open_file(result_file)
            ).pack(side=tk.LEFT, padx=(0, 10))

            ttk.Button(
                self.result_buttons_frame,
                text="📁 打开归类目录",
                command=lambda: self._open_classified_directory()
            ).pack(side=tk.LEFT, padx=(0, 10))

            ttk.Button(
                self.result_buttons_frame,
                text="📋 复制摘要",
                command=lambda: self._copy_summary_to_clipboard()
            ).pack(side=tk.LEFT)

        except Exception as e:
            self.log_message(f"⚠️ 添加操作按钮失败: {e}", "WARNING")

    def _open_file(self, file_path):
        """打开文件"""
        try:
            import subprocess
            import sys

            if sys.platform == "win32":
                os.startfile(str(file_path))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(file_path)], check=True)
            else:
                subprocess.run(["xdg-open", str(file_path)], check=True)

        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件: {e}")

    def _open_classified_directory(self):
        """打开归类目录"""
        try:
            classified_dir = Path(self.analysis_output_dir.get()) / "classified"
            if classified_dir.exists():
                self.open_output_directory_with_path(classified_dir)
            else:
                messagebox.showinfo("提示", "归类目录不存在")
        except Exception as e:
            messagebox.showerror("错误", f"无法打开归类目录: {e}")

    def _copy_summary_to_clipboard(self):
        """复制摘要到剪贴板"""
        try:
            content = self.analysis_results_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("成功", "分析摘要已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {e}")

    def _extract_highlights(self, analysis_result):
        """从分析结果中提取高光时刻"""
        highlights = []

        # 直接从结果中获取highlights字段
        if 'highlights' in analysis_result:
            return analysis_result['highlights']

        # 从analysis_result子字段中获取（新格式）
        analysis_data = analysis_result.get('analysis_result', {})
        if 'highlights' in analysis_data:
            return analysis_data['highlights']

        # 从content_analysis中获取（旧格式）
        content_analysis = analysis_result.get('content_analysis', {})
        if 'highlights' in content_analysis:
            return content_analysis['highlights']

        # 如果没有直接的highlights字段，尝试从其他字段推断
        # 从场景中提取可能的高光时刻
        scenes = analysis_result.get('scenes', [])
        for scene in scenes:
            # 如果场景有特殊标记或高置信度，可能是高光时刻
            if scene.get('confidence', 0) > 0.8 or 'highlight' in scene.get('description', '').lower():
                highlights.append({
                    'timestamp': scene.get('timestamp', '未知'),
                    'description': scene.get('description', '高光场景'),
                    'type': 'scene',
                    'confidence': scene.get('confidence', 0.8)
                })

        # 从情感变化中提取高光时刻
        emotions = analysis_result.get('emotions', {})
        emotion_changes = emotions.get('emotion_changes', [])
        for change in emotion_changes:
            if change.get('intensity', 0) > 0.7:  # 高强度情感变化
                highlights.append({
                    'timestamp': change.get('timestamp', '未知'),
                    'description': f"情感高光: {change.get('emotion', '未知情感')}",
                    'type': 'emotion',
                    'confidence': change.get('intensity', 0.7)
                })

        # 从文本中尝试提取高光信息
        full_text = content_analysis.get('full_text', '')
        if '高光' in full_text or 'highlight' in full_text.lower():
            # 简单的文本解析，寻找时间戳模式
            import re
            time_patterns = re.findall(r'(\d{1,2}:\d{2}(?::\d{2})?)', full_text)
            for i, timestamp in enumerate(time_patterns[:3]):  # 最多提取3个
                highlights.append({
                    'timestamp': timestamp,
                    'description': f"文本提及的高光时刻 {i+1}",
                    'type': 'text_extracted',
                    'confidence': 0.6
                })

        return highlights[:10]  # 最多返回10个高光时刻





def main():
    """主函数"""
    root = tk.Tk()
    app = ShotDetectionGUI(root)

    # 设置关闭事件
    def on_closing():
        if app.processing:
            if messagebox.askokcancel("退出", "正在处理中，确定要退出吗？"):
                app.processing = False
                root.destroy()
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 启动GUI
    root.mainloop()


if __name__ == "__main__":
    main()
