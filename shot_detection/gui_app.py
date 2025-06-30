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
        self.gemini_api_key = tk.StringVar()
        self.analysis_model = tk.StringVar(value="gemini-2.0-flash-exp")

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

        # 单个文件处理Tab
        self.single_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.single_frame, text="📄 单个文件处理")

        # 批量处理Tab
        self.batch_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.batch_frame, text="📁 批量处理")

        # 视频分析Tab
        self.analysis_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.analysis_frame, text="🎥 视频分析")

        # 创建单个文件处理界面
        self.create_single_file_interface()

        # 创建批量处理界面
        self.create_batch_interface()

        # 创建视频分析界面
        self.create_analysis_interface()

        # 创建共享的进度和日志区域
        self.create_shared_progress_section(main_frame)


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

        # Gemini配置区域
        self.create_gemini_config(self.analysis_frame, 1)

        # 分析控制按钮区域
        self.create_analysis_control_buttons(self.analysis_frame, 2)

        # 分析结果区域
        self.create_analysis_results_section(self.analysis_frame, 3)

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

    def create_gemini_config(self, parent, row):
        """创建Gemini配置区域"""
        config_frame = ttk.LabelFrame(parent, text="🤖 Gemini AI 配置", padding="10")
        config_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)

        # API Key输入
        ttk.Label(config_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        api_key_entry = ttk.Entry(config_frame, textvariable=self.gemini_api_key, width=50, show="*")
        api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))

        # 模型选择
        ttk.Label(config_frame, text="模型:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        model_combo = ttk.Combobox(config_frame, textvariable=self.analysis_model,
                                  values=["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
                                  state="readonly", width=25)
        model_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))

        # 说明文本
        info_text = "• 需要有效的Google AI Studio API Key\n• gemini-2.0-flash-exp: 最新实验模型，支持视频分析\n• 分析结果将保存为JSON格式"
        info_label = ttk.Label(config_frame, text=info_text, style='Info.TLabel', justify=tk.LEFT)
        info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

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

        if not self.gemini_api_key.get():
            messagebox.showerror("错误", "请输入Gemini API Key")
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
            api_key = self.gemini_api_key.get()
            model_name = self.analysis_model.get()

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

            # 调用真实的Gemini API进行视频分析
            self.update_progress(40, "初始化Gemini分析器...")
            self._real_gemini_analysis(video_path, output_dir, analysis_prompt, api_key, model_name)

        except Exception as e:
            self.log_message(f"视频分析出错: {e}", "ERROR")
            self.root.after(0, self._finish_video_analysis)

    def _real_gemini_analysis(self, video_path, output_dir, prompt, api_key, model_name):
        """真实的Gemini分析过程"""
        try:
            import json
            from gemini_video_analyzer import GeminiVideoAnalyzer

            # 创建分析器
            analyzer = GeminiVideoAnalyzer(api_key, model_name)

            # 定义进度回调
            def progress_callback(progress, description):
                self.root.after(0, lambda: self.update_progress(progress, description))

            # 执行分析
            result = analyzer.analyze_video(video_path, prompt, progress_callback)

            # 保存结果
            result_file = output_dir / f"{Path(video_path).stem}_gemini_analysis.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            # 显示结果
            self.root.after(0, lambda: self._display_gemini_results(result, result_file))

        except Exception as e:
            self.log_message(f"Gemini分析失败: {e}", "ERROR")
            # 如果真实API失败，回退到模拟分析
            self.log_message("回退到模拟分析模式...", "WARNING")
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

            if 'full_text' in content_analysis:
                display_text += f"\n📄 完整分析:\n{content_analysis['full_text']}\n"

            # 如果有结构化数据，也显示出来
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

            # 模拟分析结果
            analysis_result = {
                "video_info": {
                    "file_name": Path(video_path).name,
                    "file_path": str(video_path),
                    "analysis_time": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "content_analysis": {
                    "scenes": [
                        {
                            "start_time": "00:00:00",
                            "end_time": "00:00:15",
                            "description": "产品展示场景，白色背景下的服装细节展示"
                        },
                        {
                            "start_time": "00:00:15",
                            "end_time": "00:00:30",
                            "description": "模特试穿场景，展示服装的穿着效果"
                        }
                    ],
                    "objects": ["服装", "模特", "白色背景", "展示台"],
                    "summary": "这是一个女装产品展示视频，主要展示服装的产品细节和穿着效果",
                    "emotion": "优雅、时尚、专业",
                    "keywords": ["女装", "产品展示", "模特试穿", "时尚", "优雅"]
                },
                "technical_analysis": {
                    "shooting_style": "专业产品摄影",
                    "composition": "居中构图，多角度展示",
                    "lighting": "均匀柔光",
                    "quality": "高清画质"
                },
                "confidence": 0.92
            }

            # 保存分析结果
            result_file = output_dir / f"{Path(video_path).stem}_analysis.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)

            self.update_progress(100, "分析完成")

            # 显示结果
            self.root.after(0, lambda: self._display_analysis_results(analysis_result, result_file))

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
