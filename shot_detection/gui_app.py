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

# 剪映草稿管理相关导入
def import_jianying_modules():
    """导入剪映模块，处理路径问题"""
    import sys
    from pathlib import Path

    # 确保当前脚本目录在Python路径中
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

    try:
        from jianying.draft_meta_manager import DraftMetaManager, MaterialInfo
        from jianying.draft_content_manager import DraftContentManager
        return DraftMetaManager, MaterialInfo, DraftContentManager, None
    except ImportError as e:
        error_msg = f"无法导入 jianying 模块: {e}"
        return None, None, None, error_msg

# 执行导入
DraftMetaManager, MaterialInfo, DraftContentManager, import_error = import_jianying_modules()


class ShotDetectionGUI:
    """智能镜头检测与分段系统 - 简化版GUI"""

    def __init__(self, root):
        self.root = root
        self.root.title("🎬 智能镜头检测与分段系统")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

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

        # 剪映草稿管理变量
        self.draft_project_path = tk.StringVar()
        self.current_draft_manager = None
        self.current_project_path = None

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
        """创建带外层滚动条的界面组件"""
        # 创建主容器和滚动条
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 创建Canvas和滚动条
        self.main_canvas = tk.Canvas(main_container, highlightthickness=0)
        self.main_scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_main_frame = ttk.Frame(self.main_canvas, padding="10")

        # 配置滚动
        self.scrollable_main_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scrollable_main_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)

        # 布局Canvas和滚动条
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件到整个界面
        self.bind_mousewheel_to_main_canvas()

        # 标题
        title_label = ttk.Label(self.scrollable_main_frame, text="🎬 智能镜头检测与分段系统", style='Title.TLabel')
        title_label.pack(pady=(0, 15))

        # 创建Tab控件
        self.notebook = ttk.Notebook(self.scrollable_main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 创建非滚动的Tab页面（因为外层已经有滚动条了）
        self.create_tabs()

        # 创建共享的进度和日志区域
        self.create_shared_progress_section(self.scrollable_main_frame)

    def bind_mousewheel_to_main_canvas(self):
        """绑定鼠标滚轮事件到主Canvas"""
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_to_mousewheel(event):
            self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            self.main_canvas.unbind_all("<MouseWheel>")

        self.main_canvas.bind('<Enter>', _bind_to_mousewheel)
        self.main_canvas.bind('<Leave>', _unbind_from_mousewheel)

        # 也绑定到root窗口，确保在任何地方都能滚动
        self.root.bind_all("<MouseWheel>", _on_mousewheel)

    def create_tabs(self):
        """创建Tab页面（无内部滚动条，使用外层滚动条）"""
        # 单个文件处理Tab
        self.single_frame = self.create_simple_tab("📄 视频分镜")
        self.create_single_file_interface()

        # 批量处理Tab
        self.batch_frame = self.create_simple_tab("📁 批量分镜")
        self.create_batch_interface()

        # 视频分析Tab
        self.analysis_frame = self.create_simple_tab("🎥 视频分类")
        self.create_analysis_interface()

        # 剪映草稿管理Tab
        self.draft_frame = self.create_simple_tab("🎬 剪映草稿")
        self.create_draft_manager_interface()

        # 视频混剪Tab (抖音视频制作)
        self.video_mix_frame = self.create_simple_tab("🎬 视频混剪")
        self.create_video_mix_interface()

    def create_simple_tab(self, tab_name):
        """创建简单的Tab页面（无内部滚动条）"""
        # 创建Tab的主容器
        tab_container = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(tab_container, text=tab_name)

        return tab_container

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

        # 测试Gemini连接按钮
        self.test_gemini_button = ttk.Button(button_frame, text="🔗 测试Gemini", command=self.test_gemini_connection)
        self.test_gemini_button.pack(side=tk.LEFT, padx=(0, 15))

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
            analysis_prompt = None

            # 尝试多种方式获取提示词
            try:
                # 方法1: 直接导入
                from prompts_manager import PromptsManager
                prompts_manager = PromptsManager()
                analysis_prompt = prompts_manager.get_video_analysis_prompt()

                # 检查提示词是否有效
                if analysis_prompt and len(analysis_prompt.strip()) > 50:
                    self.log_message("使用prompts_manager获取提示词", "INFO")
                else:
                    self.log_message("prompts_manager返回的提示词无效或为空", "WARNING")
                    analysis_prompt = None  # 强制进入备用方案

            except ImportError as e:
                self.log_message(f"prompts_manager导入失败: {e}", "WARNING")

                try:
                    # 方法2: 添加路径后导入
                    current_dir = str(Path(__file__).parent)
                    if current_dir not in sys.path:
                        sys.path.insert(0, current_dir)

                    # 清理模块缓存
                    if 'prompts_manager' in sys.modules:
                        del sys.modules['prompts_manager']

                    from prompts_manager import PromptsManager
                    prompts_manager = PromptsManager()
                    analysis_prompt = prompts_manager.get_video_analysis_prompt()

                    # 检查提示词是否有效
                    if analysis_prompt and len(analysis_prompt.strip()) > 50:
                        self.log_message("路径调整后成功获取提示词", "INFO")
                    else:
                        self.log_message("路径调整后prompts_manager仍返回无效提示词", "WARNING")
                        analysis_prompt = None  # 强制进入下一个备用方案

                except Exception as e2:
                    self.log_message(f"路径调整后仍失败: {e2}", "WARNING")

                    try:
                        # 方法3: 使用备用提示词
                        from prompts_constants import VIDEO_ANALYSIS_PROMPT
                        analysis_prompt = VIDEO_ANALYSIS_PROMPT
                        self.log_message("使用备用提示词", "INFO")

                    except Exception as e3:
                        self.log_message(f"备用提示词也失败: {e3}", "ERROR")

                        # 方法4: 直接读取文件
                        try:
                            prompts_file = Path(__file__).parent / "prompts" / "video-analysis.prompt"
                            if prompts_file.exists():
                                with open(prompts_file, 'r', encoding='utf-8') as f:
                                    analysis_prompt = f.read().strip()
                                self.log_message("直接读取提示词文件成功", "INFO")
                            else:
                                self.log_message("提示词文件不存在", "ERROR")
                        except Exception as e4:
                            self.log_message(f"直接读取文件失败: {e4}", "ERROR")

            # 检查是否成功获取提示词
            if not analysis_prompt:
                self.log_message("所有方法都无法获取视频分析提示词", "ERROR")
                self.log_message("请检查以下文件是否存在:", "ERROR")
                self.log_message("1. prompts_manager.py", "ERROR")
                self.log_message("2. prompts_constants.py", "ERROR")
                self.log_message("3. prompts/video-analysis.prompt", "ERROR")
                self._finish_video_analysis()
                return

            self.log_message(f"成功获取提示词，长度: {len(analysis_prompt)} 字符", "INFO")

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
            import traceback
            self.log_message(f"详细错误信息: {traceback.format_exc()}", "ERROR")

            # 询问用户是否使用模拟分析
            from tkinter import messagebox
            use_simulation = messagebox.askyesno(
                "Gemini API失败",
                f"Gemini API调用失败:\n{str(e)}\n\n是否使用模拟分析模式继续？"
            )

            if use_simulation:
                self.log_message("⚠️ 用户选择使用模拟分析模式...", "WARNING")
                self.root.after(0, lambda: self._simulate_gemini_analysis(video_path, output_dir, prompt))
            else:
                self.log_message("❌ 用户取消分析", "INFO")
                self.root.after(0, self._finish_video_analysis)

    def test_gemini_connection(self):
        """测试Gemini API连接"""
        try:
            self.log_message("🔗 开始测试Gemini连接...", "INFO")

            # 从配置文件加载Gemini配置
            from config import get_config
            config = get_config()
            gemini_config = config.gemini

            self.log_message(f"📋 配置信息:", "INFO")
            self.log_message(f"  - Cloudflare项目: {gemini_config.cloudflare_project_id}", "INFO")
            self.log_message(f"  - Google项目: {gemini_config.google_project_id}", "INFO")
            self.log_message(f"  - 模型: {gemini_config.model_name}", "INFO")
            self.log_message(f"  - 基础URL: {gemini_config.base_url}", "INFO")

            # 创建分析器并测试连接
            from gemini_video_analyzer import create_gemini_analyzer

            analyzer = create_gemini_analyzer(
                cloudflare_project_id=gemini_config.cloudflare_project_id,
                cloudflare_gateway_id=gemini_config.cloudflare_gateway_id,
                google_project_id=gemini_config.google_project_id,
                regions=gemini_config.regions,
                model_name=gemini_config.model_name,
                enable_cache=gemini_config.enable_cache,
                cache_dir=gemini_config.cache_dir
            )

            # 测试获取访问令牌
            self.log_message("🔑 测试获取访问令牌...", "INFO")
            import asyncio
            access_token = asyncio.run(analyzer.get_access_token())

            if access_token:
                self.log_message("✅ Gemini连接测试成功！", "SUCCESS")
                self.log_message(f"🔑 访问令牌已获取 (长度: {len(access_token)} 字符)", "INFO")

                from tkinter import messagebox
                messagebox.showinfo("连接测试成功", "Gemini API连接正常，可以进行视频分析！")
            else:
                self.log_message("❌ 获取访问令牌失败", "ERROR")
                from tkinter import messagebox
                messagebox.showerror("连接测试失败", "无法获取访问令牌，请检查配置")

        except Exception as e:
            self.log_message(f"❌ Gemini连接测试失败: {e}", "ERROR")
            import traceback
            self.log_message(f"详细错误: {traceback.format_exc()}", "ERROR")

            from tkinter import messagebox
            messagebox.showerror("连接测试失败", f"Gemini API连接失败:\n{str(e)}")

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
                raise Exception("Gemini归类失败")
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

    def _gemini_classify_video(self, analysis_data):
        """使用Gemini API和folder-matching提示词进行智能归类"""
        try:
            # 加载folder-matching提示词
            try:
                # 确保当前目录在Python路径中
                current_dir = str(Path(__file__).parent)
                if current_dir not in sys.path:
                    sys.path.insert(0, current_dir)

                from prompts_manager import PromptsManager
                prompts_manager = PromptsManager()
            except ImportError as e:
                self.log_message(f"无法导入prompts_manager模块: {e}", "WARNING")
                return None

            # 构建内容描述
            content_description = self._build_content_description(analysis_data)

            # 定义可用的文件夹列表
            folder_list = [
                "product_display (产品展示)",
                "product_usage (产品使用)",
                "model_wearing (模特试穿)",
                "ai_generated (AI素材)"
            ]

            # 获取格式化的提示词
            folder_matching_prompt = prompts_manager.get_folder_matching_prompt(content_description, folder_list)

            if not folder_matching_prompt:
                self.log_message("⚠️ 无法加载folder-matching提示词", "WARNING")
                return None

            # 添加JSON格式要求
            full_prompt = folder_matching_prompt + """

请以JSON格式返回归类结果：
```json
{
  "category": "推荐的文件夹名称",
  "confidence": 0.95,
  "reason": "归类原因说明",
  "quality_level": "S级/A级/B级",
  "features": ["关键特征1", "关键特征2"],
  "recommendations": "优化建议"
}
```

有且只有这四个，请从以下文件夹中选择最合适的：
- product_display (产品展示)
- product_usage (产品使用)
- model_wearing (模特试穿)
- ai_generated (AI素材)
"""

            # 调用Gemini API
            classification_result = self._call_gemini_for_classification(full_prompt)

            if classification_result:
                self.log_message("✅ Gemini智能归类完成", "SUCCESS")
                return classification_result
            else:
                self.log_message("⚠️ Gemini归类返回空结果", "WARNING")
                return None

        except Exception as e:
            self.log_message(f"❌ Gemini归类失败: {e}", "ERROR")
            return None

    def _build_content_description(self, analysis_data):
        """构建用于归类的内容描述"""
        description_parts = []

        # 添加摘要
        summary = analysis_data.get('summary', '')
        if summary:
            description_parts.append(f"内容摘要: {summary}")

        # 添加高光时刻信息
        highlights = analysis_data.get('highlights', [])
        if highlights:
            highlight_desc = f"高光时刻数量: {len(highlights)}个"
            highlight_types = [h.get('type', '') for h in highlights if h.get('type')]
            if highlight_types:
                highlight_desc += f", 类型: {', '.join(set(highlight_types))}"
            description_parts.append(highlight_desc)

        # 添加场景信息
        scenes = analysis_data.get('scenes', [])
        if scenes:
            objects = []
            actions = []
            for scene in scenes:
                objects.extend(scene.get('objects', []))
                actions.extend(scene.get('actions', []))

            if objects:
                description_parts.append(f"检测物体: {', '.join(set(objects))}")
            if actions:
                description_parts.append(f"主要动作: {', '.join(set(actions))}")

        # 添加情感信息
        emotions = analysis_data.get('emotions', {})
        overall_mood = emotions.get('overall_mood', '')
        if overall_mood:
            description_parts.append(f"整体情感: {overall_mood}")

        # 添加质量信息
        quality = analysis_data.get('quality', {})
        video_quality = quality.get('video_quality', 0)
        if video_quality:
            description_parts.append(f"视频质量: {video_quality}/10")

        lighting = quality.get('lighting', '')
        if lighting:
            description_parts.append(f"光线条件: {lighting}")

        # 添加技术信息
        technical = analysis_data.get('technical', {})
        resolution = technical.get('resolution', '')
        if resolution:
            description_parts.append(f"分辨率: {resolution}")

        camera_movements = technical.get('camera_movements', [])
        if camera_movements:
            description_parts.append(f"镜头运动: {', '.join(camera_movements)}")

        return '\n'.join(description_parts)

    def _call_gemini_for_classification(self, prompt):
        """调用Gemini API进行归类分析"""
        try:
            self.log_message("🤖 正在调用Gemini API进行智能归类...", "INFO")

            # 获取配置
            from config import get_config
            config = get_config()
            gemini_config = config.gemini

            # 创建Gemini分析器
            from gemini_video_analyzer import create_gemini_analyzer

            analyzer = create_gemini_analyzer(
                cloudflare_project_id=gemini_config.cloudflare_project_id,
                cloudflare_gateway_id=gemini_config.cloudflare_gateway_id,
                google_project_id=gemini_config.google_project_id,
                regions=gemini_config.regions,
                model_name=gemini_config.model_name,
                enable_cache=False,  # 归类不需要缓存
                cache_dir=gemini_config.cache_dir
            )

            # 调用Gemini进行文本分析（不需要视频文件）
            import asyncio

            async def classify_with_gemini():
                try:
                    # 获取访问令牌
                    access_token = await analyzer.get_access_token()

                    # 创建客户端配置
                    client_config = analyzer._create_gemini_client(access_token)

                    # 构建请求数据
                    request_data = {
                        "contents": [
                            {
                                "role": "user",
                                "parts": [
                                    {
                                        "text": prompt
                                    }
                                ]
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.1,
                            "topK": 32,
                            "topP": 1,
                            "maxOutputTokens": 4096
                        }
                    }

                    # 发送请求
                    import requests
                    generate_url = f"{client_config['gateway_url']}/{gemini_config.model_name}:generateContent"

                    response = requests.post(
                        generate_url,
                        headers=client_config['headers'],
                        json=request_data,
                        timeout=30
                    )

                    self.log_message(f"📡 发送请求到: {generate_url}", "INFO")
                    self.log_message(f"📊 请求状态码: {response.status_code}", "INFO")

                    if response.status_code == 200:
                        result = response.json()
                        self.log_message(f"✅ 获得API响应", "SUCCESS")

                        # 提取响应文本
                        if 'candidates' in result and len(result['candidates']) > 0:
                            candidate = result['candidates'][0]
                            if 'content' in candidate and 'parts' in candidate['content']:
                                response_text = candidate['content']['parts'][0]['text']
                                self.log_message(f"📄 响应文本长度: {len(response_text)} 字符", "INFO")

                                # 解析JSON响应
                                import json
                                import re

                                # 提取JSON部分
                                json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                                if json_match:
                                    json_str = json_match.group(1)
                                    self.log_message(f"✅ 找到JSON格式响应", "SUCCESS")
                                    classification_result = json.loads(json_str)
                                    return classification_result
                                else:
                                    # 尝试直接解析整个响应
                                    try:
                                        classification_result = json.loads(response_text)
                                        self.log_message(f"✅ 直接解析JSON成功", "SUCCESS")
                                        return classification_result
                                    except Exception as parse_error:
                                        self.log_message(f"⚠️ JSON解析失败: {parse_error}", "WARNING")
                                        self.log_message(f"📄 原始响应: {response_text[:200]}...", "INFO")

                                        # 如果无法解析JSON，返回基于文本的分析
                                        return {
                                            "category": "standard",
                                            "confidence": 0.7,
                                            "reason": f"AI分析结果: {response_text[:100]}...",
                                            "quality_level": "B级",
                                            "features": ["AI文本分析"],
                                            "recommendations": "基于AI文本分析的归类建议"
                                        }
                            else:
                                self.log_message(f"❌ 响应格式错误: 缺少content或parts", "ERROR")
                                raise Exception("响应格式错误: 缺少content或parts")
                        else:
                            self.log_message(f"❌ 响应格式错误: 缺少candidates", "ERROR")
                            raise Exception("响应格式错误: 缺少candidates")

                    else:
                        error_msg = f"API请求失败: {response.status_code} - {response.text}"
                        self.log_message(f"❌ {error_msg}", "ERROR")
                        raise Exception(error_msg)

                except Exception as e:
                    raise Exception(f"Gemini归类分析失败: {str(e)}")

            # 执行异步调用
            result = asyncio.run(classify_with_gemini())

            if result:
                category = result.get('category', 'standard')
                confidence = result.get('confidence', 0.7)
                reason = result.get('reason', 'AI智能归类')

                self.log_message(f"🎯 Gemini归类结果: {category} (置信度: {confidence:.1%})", "SUCCESS")
                self.log_message(f"💭 归类原因: {reason}", "INFO")

                return result
            else:
                raise Exception("未获得有效的归类结果")

        except Exception as e:
            self.log_message(f"❌ Gemini归类分析失败: {e}", "ERROR")
            self.log_message("⚠️ 将使用备用归类逻辑", "WARNING")
            raise e

   

    
    def _generate_classified_filename(self, original_file, analysis_data, category_info=None):
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

        # 如果有Gemini归类信息，使用质量等级
        if category_info and 'quality_level' in category_info:
            quality_level = category_info['quality_level']
            if quality_level == "S级":
                prefix_parts.append("S级")
            elif quality_level == "A级":
                prefix_parts.append("A级")
        else:
            # 使用原有逻辑
            if highlight_count >= 3:
                prefix_parts.append("多高光")
            elif highlight_count >= 1:
                prefix_parts.append("有高光")

            if video_quality >= 8:
                prefix_parts.append("优质")
            elif video_quality >= 7:
                prefix_parts.append("良好")

        # 添加置信度信息（如果有）
        if category_info and 'confidence' in category_info:
            confidence = category_info['confidence']
            if confidence >= 0.9:
                prefix_parts.append("高信度")
            elif confidence >= 0.8:
                prefix_parts.append("中信度")

        # 组合文件名
        if prefix_parts:
            prefix = "_".join(prefix_parts)
            new_filename = f"{prefix}_{original_stem}{extension}"
        else:
            new_filename = f"{original_stem}{extension}"

        return new_filename

    def _save_classification_info(self, target_path, analysis_result, original_path, category_info=None):
        """保存归类信息"""
        try:
            info_file = target_path.with_suffix('.classification.json')

            classification_info = {
                "original_path": str(original_path),
                "classified_path": str(target_path),
                "classification_time": __import__('time').strftime("%Y-%m-%d %H:%M:%S"),
                "category": target_path.parent.name,
                "classification_method": "gemini_ai" if category_info else "fallback_logic",
                "analysis_summary": {
                    "highlights_count": len(analysis_result.get('analysis_result', {}).get('highlights', [])),
                    "video_quality": analysis_result.get('analysis_result', {}).get('quality', {}).get('video_quality', 0),
                    "overall_mood": analysis_result.get('analysis_result', {}).get('emotions', {}).get('overall_mood', ''),
                    "summary": analysis_result.get('analysis_result', {}).get('summary', '')
                }
            }

            # 添加Gemini归类信息
            if category_info:
                classification_info["gemini_classification"] = {
                    "confidence": category_info.get('confidence', 0),
                    "reason": category_info.get('reason', ''),
                    "quality_level": category_info.get('quality_level', ''),
                    "features": category_info.get('features', []),
                    "recommendations": category_info.get('recommendations', '')
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


            # 简洁的状态显示
            status_text = f"✅ 分析完成 | {file_name} | {highlight_count}个高光 | 质量:{video_quality}/10"
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

    def create_draft_manager_interface(self):
        """创建剪映草稿管理界面"""
        if DraftMetaManager is None:
            # 如果导入失败，显示错误信息
            error_frame = ttk.Frame(self.draft_frame)
            error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            # 显示详细的错误信息
            error_text = "❌ 剪映草稿管理功能不可用\n\n"
            if import_error:
                error_text += f"导入错误: {import_error}\n\n"

            error_text += "可能的解决方案:\n"
            error_text += "1. 确保 jianying 目录存在\n"
            error_text += "2. 检查 Python 路径设置\n"
            error_text += "3. 安装缺失的依赖包 (如 yaml)\n"
            error_text += "4. 重启应用程序"

            error_label = ttk.Label(error_frame,
                text=error_text,
                font=("Arial", 10), foreground="red", justify=tk.LEFT)
            error_label.pack(expand=True)

            # 添加重试按钮
            retry_button = ttk.Button(error_frame, text="重试导入", command=self.retry_import_jianying)
            retry_button.pack(pady=10)
            return

        # 项目管理区域
        self.create_draft_project_section()

        # 素材管理区域
        self.create_draft_material_section()

        # 信息显示区域
        self.create_draft_info_section()

    def retry_import_jianying(self):
        """重试导入剪映模块"""
        global DraftMetaManager, MaterialInfo, DraftContentManager, import_error

        try:
            # 重新执行导入
            DraftMetaManager, MaterialInfo, DraftContentManager, import_error = import_jianying_modules()

            if DraftMetaManager is not None:
                # 导入成功，重新创建界面
                messagebox.showinfo("成功", "剪映模块导入成功！正在重新加载界面...")

                # 清空当前界面
                for widget in self.draft_frame.winfo_children():
                    widget.destroy()

                # 重新创建界面
                self.create_draft_manager_interface()
            else:
                # 导入仍然失败
                messagebox.showerror("失败", f"重试导入失败:\n{import_error}")

        except Exception as e:
            messagebox.showerror("错误", f"重试导入时发生错误:\n{e}")

    def _is_valid_template_file(self, template_data: dict, template_path: Path) -> bool:
        """验证是否是有效的模板文件"""

        # 对于标准项目文件名，询问用户确认而不是直接拒绝
        if template_path.name in ["draft_content.json", "draft_meta_info.json", "draft_virtual_store.json"]:
            result = messagebox.askyesno(
                "确认文件类型",
                f"您选择的文件名是: {template_path.name}\n\n"
                f"这个文件名通常用于剪映项目文件，但也可能是模板文件。\n\n"
                f"如果这确实是一个模板文件，请点击'是'继续。\n"
                f"如果这是一个项目文件，请点击'否'重新选择。\n\n"
                f"是否继续使用此文件作为模板？"
            )
            if not result:
                return False

        # 检查是否包含项目特有的字段（说明这可能是项目文件而不是模板）
        project_indicators = [
            "source",  # 项目文件通常有source字段
            "static_cover_image_path",  # 项目文件特有
            "retouch_cover"  # 项目文件特有
        ]

        # 检查是否有具体的项目数据（更强的项目文件指示器）
        strong_project_indicators = []

        # 检查是否有具体的素材数据
        materials = template_data.get("materials", {})
        if isinstance(materials, dict):
            for material_type, material_list in materials.items():
                if isinstance(material_list, list) and len(material_list) > 0:
                    # 检查是否包含具体的文件路径
                    for material in material_list:
                        if isinstance(material, dict) and "file_Path" in material:
                            file_path = material.get("file_Path", "")
                            if file_path and not file_path.startswith("template_"):
                                strong_project_indicators.append(f"具体素材路径: {file_path}")
                                break

        # 检查是否有具体的轨道数据
        tracks = template_data.get("tracks", [])
        if isinstance(tracks, list):
            for track in tracks:
                if isinstance(track, dict):
                    segments = track.get("segments", [])
                    if isinstance(segments, list) and len(segments) > 0:
                        strong_project_indicators.append("包含具体的轨道片段数据")
                        break

        # 如果有强项目指示器，询问用户
        if strong_project_indicators:
            indicators_text = "\n".join(f"• {indicator}" for indicator in strong_project_indicators[:3])
            result = messagebox.askyesno(
                "检测到项目数据",
                f"选择的文件包含具体的项目数据：\n\n"
                f"{indicators_text}\n\n"
                f"这通常表示这是一个项目文件而不是模板文件。\n"
                f"模板文件应该包含通用结构，不包含具体数据。\n\n"
                f"是否仍要继续使用此文件作为模板？"
            )
            if not result:
                return False

        # 如果包含多个一般项目字段，轻度提醒
        elif sum(1 for field in project_indicators if field in template_data) >= 2:
            result = messagebox.askyesno(
                "确认使用",
                f"选择的文件包含一些项目特有字段。\n\n"
                f"文件: {template_path.name}\n\n"
                f"这可能是项目文件，也可能是包含完整信息的模板文件。\n\n"
                f"是否继续使用此文件作为模板？"
            )
            if not result:
                return False

        # 检查必需的模板字段
        required_fields = [
            "canvas_config", "config", "keyframes", "materials",
            "platform", "tracks", "version"
        ]

        missing_fields = []
        for field in required_fields:
            if field not in template_data:
                missing_fields.append(field)

        if missing_fields:
            messagebox.showerror(
                "模板格式错误",
                f"选择的文件缺少必需的字段，不是有效的模板文件！\n\n"
                f"缺少字段: {', '.join(missing_fields)}\n\n"
                f"请选择正确的模板文件。"
            )
            return False

        # 检查canvas_config结构
        canvas_config = template_data.get("canvas_config", {})
        if not all(key in canvas_config for key in ["width", "height", "ratio"]):
            messagebox.showerror(
                "模板格式错误",
                f"模板文件的canvas_config结构不完整！\n\n"
                f"需要包含: width, height, ratio\n\n"
                f"请选择正确的模板文件。"
            )
            return False

        return True

    def show_project_creation_dialog(self, template_path: Path, default_parent: Path):
        """显示项目创建对话框"""
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox

        # 创建对话框窗口
        dialog = tk.Toplevel(self.root)
        dialog.title("从模板创建项目")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        result = None

        # 主框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 模板信息
        ttk.Label(main_frame, text="📄 选择的模板:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(main_frame, text=template_path.name, foreground="blue").pack(anchor=tk.W, pady=(0, 15))

        # 项目名称
        ttk.Label(main_frame, text="📝 项目名称:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        name_var = tk.StringVar(value=f"从模板创建_{template_path.stem}")
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=50)
        name_entry.pack(fill=tk.X, pady=(5, 15))
        name_entry.select_range(0, tk.END)
        name_entry.focus()

        # 保存位置
        ttk.Label(main_frame, text="📁 保存位置:", font=("Arial", 10, "bold")).pack(anchor=tk.W)

        location_frame = ttk.Frame(main_frame)
        location_frame.pack(fill=tk.X, pady=(5, 15))

        location_var = tk.StringVar(value=str(default_parent))
        location_entry = ttk.Entry(location_frame, textvariable=location_var, state="readonly")
        location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        def browse_location():
            new_location = filedialog.askdirectory(
                title="选择项目保存位置",
                initialdir=str(default_parent)
            )
            if new_location:
                location_var.set(new_location)

        ttk.Button(location_frame, text="浏览...", command=browse_location).pack(side=tk.RIGHT, padx=(5, 0))

        # 预览信息
        preview_frame = ttk.LabelFrame(main_frame, text="📋 项目预览", padding="10")
        preview_frame.pack(fill=tk.X, pady=(0, 15))

        def update_preview():
            project_name = name_var.get().strip()
            project_location = location_var.get()
            if project_name and project_location:
                full_path = Path(project_location) / project_name
                preview_text.config(state=tk.NORMAL)
                preview_text.delete(1.0, tk.END)
                preview_text.insert(tk.END, f"完整路径: {full_path}\n")
                preview_text.insert(tk.END, f"模板: {template_path.name}\n")
                preview_text.insert(tk.END, f"将创建的文件:\n")
                preview_text.insert(tk.END, f"  • draft_content.json\n")
                preview_text.insert(tk.END, f"  • draft_meta_info.json\n")
                preview_text.insert(tk.END, f"  • draft_virtual_store.json")
                preview_text.config(state=tk.DISABLED)

        preview_text = tk.Text(preview_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        preview_text.pack(fill=tk.X)

        # 绑定更新事件
        name_var.trace('w', lambda *args: update_preview())
        location_var.trace('w', lambda *args: update_preview())
        update_preview()

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        def on_create():
            nonlocal result
            project_name = name_var.get().strip()
            project_location = location_var.get().strip()

            if not project_name:
                messagebox.showerror("错误", "请输入项目名称")
                return

            if not project_location:
                messagebox.showerror("错误", "请选择保存位置")
                return

            # 检查项目是否已存在
            full_path = Path(project_location) / project_name
            if full_path.exists():
                if not messagebox.askyesno("项目已存在",
                    f"项目 '{project_name}' 已存在。\n\n是否覆盖现有项目？"):
                    return

            result = (project_name, Path(project_location))
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        ttk.Button(button_frame, text="创建项目", command=on_create).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT)

        # 等待对话框关闭
        dialog.wait_window()

        return result

    def create_draft_project_section(self):
        """创建项目管理区域"""
        project_frame = ttk.LabelFrame(self.draft_frame, text="📁 项目管理", padding="10")
        project_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # 项目路径选择
        path_frame = ttk.Frame(project_frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(path_frame, text="项目路径:").pack(side=tk.LEFT, padx=(0, 5))

        path_entry = ttk.Entry(path_frame, textvariable=self.draft_project_path, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(path_frame, text="选择目录",
                  command=self.select_draft_directory).pack(side=tk.LEFT, padx=(0, 5))

        # 操作按钮
        button_frame = ttk.Frame(project_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="新建项目",
                  command=self.create_new_draft_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="加载项目",
                  command=self.load_draft_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="保存项目",
                  command=self.save_draft_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="项目另存为",
                  command=self.save_draft_project_as).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="使用模板",
                  command=self.load_from_template).pack(side=tk.LEFT, padx=(0, 5))

        # 项目信息显示
        info_frame = ttk.Frame(project_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))

        self.draft_project_info = tk.Text(info_frame, height=3, wrap=tk.WORD, state=tk.DISABLED)
        self.draft_project_info.pack(fill=tk.X)

    def create_draft_material_section(self):
        """创建素材管理区域"""
        material_frame = ttk.LabelFrame(self.draft_frame, text="🎬 素材管理", padding="10")
        material_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 添加素材按钮
        button_frame = ttk.Frame(material_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="添加视频",
                  command=lambda: self.add_draft_material("video")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="添加音频",
                  command=lambda: self.add_draft_material("audio")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="添加图片",
                  command=lambda: self.add_draft_material("image")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="批量添加",
                  command=self.batch_add_draft_materials).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除选中",
                  command=self.remove_selected_draft_material).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="刷新列表",
                  command=self.refresh_draft_material_list).pack(side=tk.LEFT)

        # 素材列表
        list_frame = ttk.Frame(material_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview
        columns = ("类型", "文件名", "尺寸", "时长", "路径")
        self.draft_material_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)

        # 设置列标题和宽度
        self.draft_material_tree.heading("类型", text="类型")
        self.draft_material_tree.heading("文件名", text="文件名")
        self.draft_material_tree.heading("尺寸", text="尺寸")
        self.draft_material_tree.heading("时长", text="时长")
        self.draft_material_tree.heading("路径", text="路径")

        self.draft_material_tree.column("类型", width=60)
        self.draft_material_tree.column("文件名", width=150)
        self.draft_material_tree.column("尺寸", width=100)
        self.draft_material_tree.column("时长", width=80)
        self.draft_material_tree.column("路径", width=300)

        self.draft_material_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动条
        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                      command=self.draft_material_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.draft_material_tree.configure(yscrollcommand=tree_scrollbar.set)

        # 绑定双击事件
        self.draft_material_tree.bind("<Double-1>", self.on_draft_material_double_click)

    def create_draft_info_section(self):
        """创建信息显示区域"""
        info_frame = ttk.LabelFrame(self.draft_frame, text="📋 详细信息", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        # 创建滚动文本框
        self.draft_info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, height=8)
        self.draft_info_text.pack(fill=tk.BOTH, expand=True)

    # 剪映草稿管理功能方法
    def select_draft_directory(self):
        """选择项目目录"""
        directory = filedialog.askdirectory(title="选择项目目录")
        if directory:
            self.draft_project_path.set(directory)

    def create_new_draft_project(self):
        """创建新项目"""
        project_path = self.draft_project_path.get().strip()
        if not project_path:
            messagebox.showerror("错误", "请先选择或输入项目路径")
            return

        try:
            # 创建项目目录
            project_dir = Path(project_path)
            project_dir.mkdir(parents=True, exist_ok=True)

            # 创建管理器
            self.current_draft_manager = DraftMetaManager(project_dir)
            self.current_project_path = project_dir

            # 创建默认元数据
            meta_data = self.current_draft_manager.load_meta_data()

            # 更新界面
            self.update_draft_project_info()
            self.refresh_draft_material_list()

            self.log_draft_info(f"成功创建新项目: {project_path}")
            messagebox.showinfo("成功", f"项目创建成功: {project_dir.name}")

        except Exception as e:
            self.log_draft_error(f"创建项目失败: {e}")
            messagebox.showerror("错误", f"创建项目失败: {e}")

    def load_draft_project(self):
        """加载现有项目"""
        project_path = self.draft_project_path.get().strip()
        if not project_path:
            messagebox.showerror("错误", "请先选择项目路径")
            return

        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                messagebox.showerror("错误", "项目目录不存在")
                return

            # 创建管理器并加载
            self.current_draft_manager = DraftMetaManager(project_dir)
            self.current_project_path = project_dir

            meta_data = self.current_draft_manager.load_meta_data()

            # 更新界面
            self.update_draft_project_info()
            self.refresh_draft_material_list()

            self.log_draft_info(f"成功加载项目: {project_path}")
            messagebox.showinfo("成功", f"项目加载成功: {project_dir.name}")

        except Exception as e:
            self.log_draft_error(f"加载项目失败: {e}")
            messagebox.showerror("错误", f"加载项目失败: {e}")

    def save_draft_project(self):
        """保存项目"""
        if not self.current_draft_manager:
            messagebox.showerror("错误", "没有打开的项目")
            return

        try:
            success = self.current_draft_manager.save_meta_data()
            if success:
                self.log_draft_info("项目保存成功")
                messagebox.showinfo("成功", "项目保存成功")
            else:
                messagebox.showerror("错误", "项目保存失败")

        except Exception as e:
            self.log_draft_error(f"保存项目失败: {e}")
            messagebox.showerror("错误", f"保存项目失败: {e}")

    def save_draft_project_as(self):
        """项目另存为"""
        if not self.current_draft_manager:
            messagebox.showerror("错误", "没有打开的项目")
            return

        # 选择保存目录
        save_directory = filedialog.askdirectory(title="选择项目另存为的目录")
        if not save_directory:
            return

        # 输入新项目名称
        from tkinter import simpledialog
        new_project_name = simpledialog.askstring(
            "项目另存为",
            "请输入新项目名称:",
            initialvalue=f"{self.current_project_path.name}_副本" if self.current_project_path else "新项目"
        )

        if not new_project_name:
            return

        try:
            # 创建新项目目录
            new_project_path = Path(save_directory) / new_project_name
            new_project_path.mkdir(parents=True, exist_ok=True)

            # 创建新的管理器实例
            new_manager = DraftMetaManager(new_project_path)

            # 复制当前项目的元数据
            if self.current_draft_manager._meta_data:
                # 深拷贝元数据，更新项目相关信息
                import copy
                new_meta_data = copy.deepcopy(self.current_draft_manager._meta_data)

                # 更新项目信息
                import time
                import uuid
                current_time_ms = int(time.time() * 1000000)

                new_meta_data["draft_id"] = str(uuid.uuid4()).upper()
                new_meta_data["draft_name"] = new_project_name
                new_meta_data["draft_fold_path"] = str(new_project_path)
                new_meta_data["draft_root_path"] = str(new_project_path.parent)
                new_meta_data["tm_draft_create"] = current_time_ms
                new_meta_data["tm_draft_modified"] = current_time_ms

                # 设置新管理器的元数据
                new_manager._meta_data = new_meta_data

            # 复制虚拟存储数据
            if self.current_draft_manager._virtual_store_data:
                import copy
                new_manager._virtual_store_data = copy.deepcopy(self.current_draft_manager._virtual_store_data)

            # 保存新项目
            success = new_manager.save_meta_data()

            if success:
                self.log_draft_info(f"项目另存为成功: {new_project_path}")

                # 询问是否切换到新项目
                switch_to_new = messagebox.askyesno(
                    "另存为成功",
                    f"项目已另存为: {new_project_name}\n\n是否切换到新项目？"
                )

                if switch_to_new:
                    # 切换到新项目
                    self.current_draft_manager = new_manager
                    self.current_project_path = new_project_path
                    self.draft_project_path.set(str(new_project_path))

                    # 更新界面
                    self.update_draft_project_info()
                    self.refresh_draft_material_list()

                    self.log_draft_info(f"已切换到新项目: {new_project_name}")

                messagebox.showinfo("成功", f"项目另存为成功!\n\n新项目路径: {new_project_path}")
            else:
                messagebox.showerror("错误", "项目另存为失败")

        except Exception as e:
            self.log_draft_error(f"项目另存为失败: {e}")
            messagebox.showerror("错误", f"项目另存为失败: {e}")

    def load_from_template(self):
        """使用模板创建项目"""
        # 检查剪映模块是否可用
        if DraftContentManager is None or DraftMetaManager is None:
            messagebox.showerror(
                "功能不可用",
                "剪映模块未正确加载，无法使用模板功能。\n\n"
                "请检查:\n"
                "1. jianying 目录是否存在\n"
                "2. 相关模块是否正确安装\n"
                "3. 点击界面上的'重试导入'按钮"
            )
            return

        try:
            # 选择模板文件
            template_file = filedialog.askopenfilename(
                title="选择模板文件 (不是项目文件)",
                filetypes=[
                    ("JSON模板文件", "*.json"),
                    ("所有文件", "*.*")
                ],
                initialdir=str(Path(__file__).parent / "templates")
            )

            if not template_file:
                return

            template_path = Path(template_file)

            # 检查是否选择了项目文件而不是模板文件
            if template_path.name in ["draft_content.json", "draft_meta_info.json", "draft_virtual_store.json"]:
                messagebox.showerror(
                    "文件类型错误",
                    f"您选择的是剪映项目文件，不是模板文件！\n\n"
                    f"选择的文件: {template_path.name}\n\n"
                    f"请选择:\n"
                    f"• 模板文件 (通常在 templates/ 目录下)\n"
                    f"• 文件名不应该是 draft_content.json 等项目文件\n\n"
                    f"如果您想从现有项目创建模板，请:\n"
                    f"1. 先加载该项目\n"
                    f"2. 使用'项目另存为'功能\n"
                    f"3. 或使用专门的'保存为模板'功能"
                )
                return

            # 验证模板文件内容
            try:
                import json
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)

                # 检查是否是有效的模板文件
                if not self._is_valid_template_file(template_data, template_path):
                    return

            except json.JSONDecodeError:
                messagebox.showerror(
                    "文件格式错误",
                    f"选择的文件不是有效的JSON格式！\n\n"
                    f"文件: {template_path.name}\n\n"
                    f"请选择正确的模板文件。"
                )
                return
            except Exception as e:
                messagebox.showerror(
                    "文件读取错误",
                    f"无法读取选择的文件！\n\n"
                    f"文件: {template_path.name}\n"
                    f"错误: {e}\n\n"
                    f"请检查文件是否存在且有读取权限。"
                )
                return

            # 检查是否有当前项目
            if self.current_draft_manager:
                # 询问是否保存当前项目
                save_current = messagebox.askyesnocancel(
                    "使用模板",
                    "当前有打开的项目，是否先保存当前项目？\n\n"
                    "是：保存当前项目后使用模板\n"
                    "否：不保存直接使用模板\n"
                    "取消：取消操作"
                )

                if save_current is None:  # 用户点击取消
                    return
                elif save_current:  # 用户选择保存
                    self.save_draft_project()

            # 智能选择项目目录
            if self.current_project_path:
                # 如果有当前项目，在同级目录创建
                default_parent = self.current_project_path.parent
            else:
                # 否则使用默认的项目目录
                default_parent = Path.home() / "Documents" / "剪映项目"
                default_parent.mkdir(parents=True, exist_ok=True)

            # 简化的项目创建流程
            from tkinter import simpledialog

            # 输入项目名称
            project_name = simpledialog.askstring(
                "使用模板创建项目",
                f"请输入新项目名称:\n\n"
                f"模板: {template_path.name}\n"
                f"保存位置: {default_parent}\n\n"
                f"项目名称:",
                initialvalue=f"从模板创建_{template_path.stem}"
            )

            if not project_name or not project_name.strip():
                return

            project_name = project_name.strip()
            project_parent = default_parent

            # 创建新项目目录
            new_project_path = project_parent / project_name
            new_project_path.mkdir(parents=True, exist_ok=True)

            # 创建内容管理器并从模板加载
            content_manager = DraftContentManager(new_project_path)

            # 添加详细的错误捕获
            self.log_draft_info(f"开始从模板加载: {template_path}")
            success = content_manager.load_from_template(template_path)

            if success:
                self.log_draft_info("模板加载成功，开始保存项目文件")

                # 保存draft_content.json
                save_success = content_manager.save_content_data()

                if save_success:
                    self.log_draft_info("draft_content.json 保存成功")
                else:
                    self.log_draft_error("draft_content.json 保存失败")

                # 创建元数据管理器并保存元数据
                meta_manager = DraftMetaManager(new_project_path)
                meta_manager.load_meta_data()
                meta_success = meta_manager.save_meta_data()

                if meta_success:
                    self.log_draft_info("元数据保存成功")
                else:
                    self.log_draft_error("元数据保存失败")

                save_success = save_success and meta_success

                if save_success:
                    # 切换到新项目
                    self.current_draft_manager = meta_manager
                    self.current_project_path = new_project_path
                    self.draft_project_path.set(str(new_project_path))

                    # 更新界面
                    self.update_draft_project_info()
                    self.refresh_draft_material_list()

                    self.log_draft_info(f"成功从模板创建项目: {project_name}")
                    messagebox.showinfo(
                        "成功",
                        f"成功从模板创建项目！\n\n"
                        f"模板: {template_path.name}\n"
                        f"项目: {project_name}\n"
                        f"路径: {new_project_path}"
                    )
                else:
                    error_msg = "项目保存失败\n\n"
                    if not save_success:
                        error_msg += "- draft_content.json 保存失败\n"
                    if not meta_success:
                        error_msg += "- 元数据保存失败\n"

                    self.log_draft_error(error_msg)
                    messagebox.showerror("错误", error_msg)
            else:
                # 获取更详细的错误信息
                error_msg = f"模板加载失败\n\n模板文件: {template_path}\n\n"
                error_msg += "可能的原因:\n"
                error_msg += "1. 模板文件格式不正确\n"
                error_msg += "2. 模板缺少必需字段\n"
                error_msg += "3. 文件读取权限问题\n"
                error_msg += "4. JSON格式错误\n\n"
                error_msg += "请检查日志获取详细信息"

                self.log_draft_error(f"模板加载失败: {template_path}")
                messagebox.showerror("模板加载失败", error_msg)

        except Exception as e:
            self.log_draft_error(f"使用模板失败: {e}")
            messagebox.showerror("错误", f"使用模板失败: {e}")

    def add_draft_material(self, material_type):
        """添加素材"""
        if not self.current_draft_manager:
            messagebox.showerror("错误", "请先创建或加载项目")
            return

        # 文件类型过滤器
        filetypes = {
            "video": [("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"), ("所有文件", "*.*")],
            "audio": [("音频文件", "*.mp3 *.wav *.aac *.flac *.ogg"), ("所有文件", "*.*")],
            "image": [("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"), ("所有文件", "*.*")]
        }

        file_path = filedialog.askopenfilename(
            title=f"选择{material_type}文件",
            filetypes=filetypes.get(material_type, [("所有文件", "*.*")])
        )

        if file_path:
            self.add_draft_material_file(file_path, material_type)

    def add_draft_material_file(self, file_path, material_type):
        """添加单个素材文件"""
        try:
            file_path_obj = Path(file_path)

            # 创建素材信息
            material = MaterialInfo(
                file_path=str(file_path_obj),
                name=file_path_obj.name,
                material_type=material_type
            )

            # 添加到项目
            material_id = self.current_draft_manager.add_material(material)

            # 刷新列表
            self.refresh_draft_material_list()

            self.log_draft_info(f"成功添加{material_type}素材: {file_path_obj.name}")

        except Exception as e:
            self.log_draft_error(f"添加素材失败: {e}")
            messagebox.showerror("错误", f"添加素材失败: {e}")

    def batch_add_draft_materials(self):
        """批量添加素材"""
        if not self.current_draft_manager:
            messagebox.showerror("错误", "请先创建或加载项目")
            return

        file_paths = filedialog.askopenfilenames(
            title="批量选择素材文件",
            filetypes=[
                ("媒体文件", "*.mp4 *.avi *.mov *.mp3 *.wav *.jpg *.png"),
                ("所有文件", "*.*")
            ]
        )

        if file_paths:
            success_count = 0
            for file_path in file_paths:
                try:
                    # 根据文件扩展名判断类型
                    ext = Path(file_path).suffix.lower()
                    if ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']:
                        material_type = "video"
                    elif ext in ['.mp3', '.wav', '.aac', '.flac', '.ogg']:
                        material_type = "audio"
                    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                        material_type = "image"
                    else:
                        material_type = "video"  # 默认为视频

                    self.add_draft_material_file(file_path, material_type)
                    success_count += 1

                except Exception as e:
                    self.log_draft_error(f"添加文件失败 {file_path}: {e}")

            messagebox.showinfo("完成", f"批量添加完成，成功添加 {success_count} 个文件")

    def remove_selected_draft_material(self):
        """删除选中的素材"""
        if not self.current_draft_manager:
            messagebox.showerror("错误", "没有打开的项目")
            return

        selected_items = self.draft_material_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的素材")
            return

        if messagebox.askyesno("确认", f"确定要删除选中的 {len(selected_items)} 个素材吗？"):
            for item in selected_items:
                try:
                    # 获取素材ID（存储在item的tags中）
                    material_id = self.draft_material_tree.item(item)['tags'][0] if self.draft_material_tree.item(item)['tags'] else None
                    if material_id:
                        self.current_draft_manager.remove_material(material_id)

                except Exception as e:
                    self.log_draft_error(f"删除素材失败: {e}")

            self.refresh_draft_material_list()
            self.log_draft_info(f"删除了 {len(selected_items)} 个素材")

    def refresh_draft_material_list(self):
        """刷新素材列表"""
        # 清空现有项目
        for item in self.draft_material_tree.get_children():
            self.draft_material_tree.delete(item)

        if not self.current_draft_manager:
            return

        try:
            # 直接遍历draft_materials避免重复
            if self.current_draft_manager._meta_data is None:
                return

            draft_materials = self.current_draft_manager._meta_data.get("draft_materials", [])

            for material_group in draft_materials:
                materials = material_group.get("value", [])

                for material in materials:
                    # 根据metetype确定显示的类型
                    metetype = material.get('metetype', 'unknown')
                    if metetype == 'video':
                        display_type = 'video'
                    elif metetype == 'audio':
                        display_type = 'audio'
                    elif metetype == 'photo':
                        display_type = 'image'
                    else:
                        display_type = metetype

                    # 格式化显示信息
                    file_name = material.get('extra_info', 'N/A')

                    # 尺寸信息
                    width = material.get('width', 0)
                    height = material.get('height', 0)
                    size_str = f"{width}x{height}" if width and height else "N/A"

                    # 时长信息
                    duration = material.get('duration', 0)
                    duration_str = f"{duration/1000000:.2f}s" if duration > 0 else "N/A"

                    # 文件路径
                    file_path = material.get('file_Path', 'N/A')

                    # 插入到树形视图
                    item = self.draft_material_tree.insert('', 'end', values=(
                        display_type,
                        file_name,
                        size_str,
                        duration_str,
                        file_path
                    ), tags=(material.get('id', ''),))

        except Exception as e:
            self.log_draft_error(f"刷新素材列表失败: {e}")

    def on_draft_material_double_click(self, event):
        """素材双击事件"""
        selected_item = self.draft_material_tree.selection()[0] if self.draft_material_tree.selection() else None
        if selected_item:
            # 获取素材ID
            material_id = self.draft_material_tree.item(selected_item)['tags'][0] if self.draft_material_tree.item(selected_item)['tags'] else None
            if material_id:
                self.show_draft_material_details(material_id)

    def show_draft_material_details(self, material_id):
        """显示素材详细信息"""
        if not self.current_draft_manager:
            return

        try:
            # 查找素材
            material_types = ["video", "audio", "image", "text", "other"]
            found_material = None

            for material_type in material_types:
                materials = self.current_draft_manager.get_materials_by_type(material_type)
                for material in materials:
                    if material.get('id') == material_id:
                        found_material = material
                        break
                if found_material:
                    break

            if found_material:
                # 格式化显示详细信息
                details = "素材详细信息:\n"
                details += "=" * 50 + "\n"

                for key, value in found_material.items():
                    if key == 'duration' and isinstance(value, int):
                        details += f"{key}: {value} 微秒 ({value/1000000:.2f} 秒)\n"
                    elif key in ['create_time', 'import_time']:
                        import datetime
                        dt = datetime.datetime.fromtimestamp(value)
                        details += f"{key}: {value} ({dt.strftime('%Y-%m-%d %H:%M:%S')})\n"
                    else:
                        details += f"{key}: {value}\n"

                self.draft_info_text.delete(1.0, tk.END)
                self.draft_info_text.insert(1.0, details)

        except Exception as e:
            self.log_draft_error(f"显示素材详情失败: {e}")

    def update_draft_project_info(self):
        """更新项目信息显示"""
        if not self.current_draft_manager:
            self.draft_project_info.config(state=tk.NORMAL)
            self.draft_project_info.delete(1.0, tk.END)
            self.draft_project_info.config(state=tk.DISABLED)
            return

        try:
            project_info = self.current_draft_manager.get_project_info()

            info_text = f"项目名称: {project_info.get('project_name', 'N/A')}\n"
            info_text += f"项目ID: {project_info.get('project_id', 'N/A')}\n"
            info_text += f"项目路径: {project_info.get('project_path', 'N/A')}"

            self.draft_project_info.config(state=tk.NORMAL)
            self.draft_project_info.delete(1.0, tk.END)
            self.draft_project_info.insert(1.0, info_text)
            self.draft_project_info.config(state=tk.DISABLED)

        except Exception as e:
            self.log_draft_error(f"更新项目信息失败: {e}")

    def log_draft_info(self, message):
        """记录信息日志"""
        self.draft_info_text.insert(tk.END, f"[INFO] {message}\n")
        self.draft_info_text.see(tk.END)

    def log_draft_error(self, message):
        """记录错误日志"""
        self.draft_info_text.insert(tk.END, f"[ERROR] {message}\n")
        self.draft_info_text.see(tk.END)

    def create_video_mix_interface(self):
        """创建视频混剪界面"""
        # 添加混剪变量
        self.mix_materials_dir = tk.StringVar()
        self.mix_templates_dir = tk.StringVar()
        self.mix_output_dir = tk.StringVar()

        # 标题
        title_label = ttk.Label(self.video_mix_frame, text="🎬 视频混剪", style='Heading.TLabel')
        title_label.pack(pady=(0, 20))

        # 目录选择区域
        dirs_frame = ttk.Frame(self.video_mix_frame)
        dirs_frame.pack(fill=tk.X, pady=(0, 20))

        # 素材目录
        materials_frame = ttk.LabelFrame(dirs_frame, text="📹 素材目录", padding="15")
        materials_frame.pack(fill=tk.X, pady=(0, 10))

        materials_entry = ttk.Entry(materials_frame, textvariable=self.mix_materials_dir, width=60)
        materials_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        def select_materials_directory():
            directory = filedialog.askdirectory(title="选择素材目录")
            if directory:
                self.mix_materials_dir.set(directory)

        ttk.Button(materials_frame, text="浏览", command=select_materials_directory).pack(side=tk.RIGHT)

        # 模板目录
        templates_frame = ttk.LabelFrame(dirs_frame, text="📋 模板目录", padding="15")
        templates_frame.pack(fill=tk.X, pady=(0, 10))

        templates_entry = ttk.Entry(templates_frame, textvariable=self.mix_templates_dir, width=60)
        templates_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        def select_templates_directory():
            directory = filedialog.askdirectory(title="选择模板目录")
            if directory:
                self.mix_templates_dir.set(directory)

        ttk.Button(templates_frame, text="浏览", command=select_templates_directory).pack(side=tk.RIGHT)

        # 输出目录
        output_frame = ttk.LabelFrame(dirs_frame, text="📤 输出目录", padding="15")
        output_frame.pack(fill=tk.X, pady=(0, 10))

        output_entry = ttk.Entry(output_frame, textvariable=self.mix_output_dir, width=60)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        def select_output_directory():
            directory = filedialog.askdirectory(title="选择输出目录")
            if directory:
                self.mix_output_dir.set(directory)

        ttk.Button(output_frame, text="浏览", command=select_output_directory).pack(side=tk.RIGHT)

        # 操作按钮
        button_frame = ttk.Frame(self.video_mix_frame)
        button_frame.pack(fill=tk.X, pady=20)

        # 预览按钮
        preview_btn = ttk.Button(button_frame, text="🔍 预览",
                               command=self.run_video_mix_preview, style='Action.TButton')
        preview_btn.pack(side=tk.LEFT, padx=(0, 15))

        # 开始混剪按钮
        mix_btn = ttk.Button(button_frame, text="🚀 开始混剪",
                           command=self.run_video_mix, style='Primary.TButton')
        mix_btn.pack(side=tk.LEFT, padx=(0, 15))

        # 打开输出目录按钮
        open_btn = ttk.Button(button_frame, text="📁 打开输出",
                            command=self.open_video_mix_output)
        open_btn.pack(side=tk.LEFT)

        # 状态显示
        status_frame = ttk.LabelFrame(self.video_mix_frame, text="📊 状态", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.mix_status_text = scrolledtext.ScrolledText(status_frame, height=10, wrap=tk.WORD)
        self.mix_status_text.pack(fill=tk.BOTH, expand=True)

        # 初始状态
        self.update_mix_status("等待选择目录...")

    def update_mix_status(self, message):
        """更新视频混剪状态"""
        self.mix_status_text.insert(tk.END, f"{message}\n")
        self.mix_status_text.see(tk.END)
        self.root.update_idletasks()

    def run_video_mix_preview(self):
        """运行视频混剪预览模式"""
        materials_dir = self.mix_materials_dir.get().strip()
        templates_dir = self.mix_templates_dir.get().strip()
        output_dir = self.mix_output_dir.get().strip()

        if not materials_dir:
            messagebox.showerror("错误", "请选择素材目录")
            return

        if not templates_dir:
            messagebox.showerror("错误", "请选择模板目录")
            return

        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return

        if not Path(materials_dir).exists():
            messagebox.showerror("错误", "素材目录不存在")
            return

        if not Path(templates_dir).exists():
            messagebox.showerror("错误", "模板目录不存在")
            return

        # 创建临时工作目录结构
        import tempfile
        temp_work_dir = Path(tempfile.mkdtemp())

        # 创建符合工作流程要求的目录结构
        temp_resources_dir = temp_work_dir / "resources"
        temp_templates_dir = temp_work_dir / "templates"
        temp_output_dir = temp_work_dir / "outputs"

        # 创建符号链接或复制目录
        try:
            import shutil
            shutil.copytree(materials_dir, temp_resources_dir)
            shutil.copytree(templates_dir, temp_templates_dir)
            temp_output_dir.mkdir()
        except Exception as e:
            messagebox.showerror("错误", f"创建临时工作目录失败: {e}")
            return

        # 在后台线程中运行预览
        def run_preview():
            try:
                self.update_mix_status("🔍 开始预览...")
                self.update_mix_status(f"📹 素材目录: {materials_dir}")
                self.update_mix_status(f"📋 模板目录: {templates_dir}")
                self.update_mix_status(f"📤 输出目录: {output_dir}")

                # 导入工作流程模块
                sys.path.insert(0, str(Path(__file__).parent / "jianying"))
                from run_allocation import DouyinVideoWorkflow

                # 创建工作流程实例，传递原始素材目录
                workflow = DouyinVideoWorkflow(str(temp_work_dir), str(materials_dir))

                # 步骤1: 扫描资源
                self.update_mix_status("1️⃣ 扫描素材...")
                inventory = workflow.step1_scan_resources(['json'])
                if not inventory:
                    self.update_mix_status("❌ 无法扫描素材")
                    return

                # 步骤2: 管理模板
                self.update_mix_status("2️⃣ 分析模板...")
                project_manager = workflow.step2_manage_templates()
                if not project_manager:
                    self.update_mix_status("❌ 无法分析模板")
                    return

                # 显示预览信息
                stats = inventory['statistics']
                summary = project_manager.get_project_summary()

                self.update_mix_status("\n📊 素材统计:")
                self.update_mix_status(f"  视频: {stats['video_count']} 个")
                self.update_mix_status(f"  音频: {stats['audio_count']} 个")
                self.update_mix_status(f"  图片: {stats['image_count']} 个")
                self.update_mix_status(f"  总大小: {stats['total_size_mb']} MB")

                self.update_mix_status("\n📋 模板统计:")
                self.update_mix_status(f"  有效模板: {summary['valid_projects']} 个")
                self.update_mix_status(f"  无效模板: {summary['invalid_projects']} 个")

                if summary['valid_project_names']:
                    self.update_mix_status("\n✅ 可用模板:")
                    for name in summary['valid_project_names']:
                        self.update_mix_status(f"  - {name}")

                self.update_mix_status("\n🔍 预览完成！")

            except Exception as e:
                self.update_mix_status(f"❌ 预览失败: {e}")
            finally:
                # 清理临时目录
                try:
                    shutil.rmtree(temp_work_dir)
                except:
                    pass

        # 在后台线程中运行
        threading.Thread(target=run_preview, daemon=True).start()

    def run_video_mix(self):
        """运行完整的视频混剪"""
        materials_dir = self.mix_materials_dir.get().strip()
        templates_dir = self.mix_templates_dir.get().strip()
        output_dir = self.mix_output_dir.get().strip()

        if not materials_dir:
            messagebox.showerror("错误", "请选择素材目录")
            return

        if not templates_dir:
            messagebox.showerror("错误", "请选择模板目录")
            return

        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return

        if not Path(materials_dir).exists():
            messagebox.showerror("错误", "素材目录不存在")
            return

        if not Path(templates_dir).exists():
            messagebox.showerror("错误", "模板目录不存在")
            return

        # 确认对话框
        if not messagebox.askyesno("确认", "确定要开始视频混剪吗？\n这将生成大量视频项目文件。"):
            return

        # 创建工作目录结构
        import tempfile
        temp_work_dir = Path(tempfile.mkdtemp())

        # 创建符合工作流程要求的目录结构
        temp_resources_dir = temp_work_dir / "resources"
        temp_templates_dir = temp_work_dir / "templates"
        temp_output_dir = temp_work_dir / "outputs"

        # 创建符号链接或复制目录
        try:
            import shutil
            shutil.copytree(materials_dir, temp_resources_dir)
            shutil.copytree(templates_dir, temp_templates_dir)
            temp_output_dir.mkdir()
        except Exception as e:
            messagebox.showerror("错误", f"创建工作目录失败: {e}")
            return

        # 在后台线程中运行完整工作流程
        def run_full_workflow():
            try:
                self.update_mix_status("🚀 开始视频混剪...")
                self.update_mix_status(f"📹 素材目录: {materials_dir}")
                self.update_mix_status(f"📋 模板目录: {templates_dir}")
                self.update_mix_status(f"📤 输出目录: {output_dir}")

                # 导入工作流程模块
                sys.path.insert(0, str(Path(__file__).parent / "jianying"))
                from run_allocation import DouyinVideoWorkflow

                # 创建工作流程实例，传递原始素材目录
                workflow = DouyinVideoWorkflow(str(temp_work_dir), str(materials_dir))

                # 运行完整工作流程
                success = workflow.run_complete_workflow(['json'])

                if success:
                    # 复制结果到用户指定的输出目录
                    self.update_mix_status("📁 复制结果到输出目录...")
                    final_output_dir = Path(output_dir)
                    final_output_dir.mkdir(parents=True, exist_ok=True)

                    # 复制生成的项目
                    for item in temp_output_dir.iterdir():
                        if item.is_dir():
                            dest = final_output_dir / item.name
                            if dest.exists():
                                shutil.rmtree(dest)
                            shutil.copytree(item, dest)
                        else:
                            shutil.copy2(item, final_output_dir)

                    self.update_mix_status("\n🎉 视频混剪完成！")
                    self.update_mix_status(f"📁 结果保存在: {output_dir}")

                    # 询问是否打开输出目录
                    def ask_open_output():
                        if messagebox.askyesno("完成", "视频混剪完成！\n是否打开输出目录查看结果？"):
                            self.open_video_mix_output()

                    self.root.after(0, ask_open_output)
                else:
                    self.update_mix_status("\n❌ 视频混剪失败！")

            except Exception as e:
                self.update_mix_status(f"❌ 执行失败: {e}")
                import traceback
                self.update_mix_status(f"详细错误: {traceback.format_exc()}")
            finally:
                # 清理临时目录
                try:
                    shutil.rmtree(temp_work_dir)
                except:
                    pass

        # 在后台线程中运行
        threading.Thread(target=run_full_workflow, daemon=True).start()

    def open_video_mix_output(self):
        """打开视频混剪输出目录"""
        output_dir = self.mix_output_dir.get().strip()
        if not output_dir:
            messagebox.showwarning("警告", "请先选择输出目录")
            return

        if not Path(output_dir).exists():
            messagebox.showwarning("警告", "输出目录不存在，请先运行视频混剪")
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

    def create_video_mix_interface(self):
        """创建视频混剪功能界面"""
        # 添加混剪变量
        self.mix_materials_dir = tk.StringVar()
        self.mix_templates_dir = tk.StringVar()
        self.mix_output_dir = tk.StringVar()

        # 标题
        title_label = ttk.Label(self.video_mix_frame, text="🎬 视频混剪", style='Heading.TLabel')
        title_label.pack(pady=(0, 20))

        # 目录选择区域
        dirs_frame = ttk.Frame(self.video_mix_frame)
        dirs_frame.pack(fill=tk.X, pady=(0, 20))

        # 素材目录
        materials_frame = ttk.LabelFrame(dirs_frame, text="📹 素材目录", padding="15")
        materials_frame.pack(fill=tk.X, pady=(0, 10))

        materials_entry = ttk.Entry(materials_frame, textvariable=self.mix_materials_dir, width=60)
        materials_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        def select_materials_directory():
            directory = filedialog.askdirectory(title="选择素材目录")
            if directory:
                self.mix_materials_dir.set(directory)

        ttk.Button(materials_frame, text="浏览", command=select_materials_directory).pack(side=tk.RIGHT)

        # 模板目录
        templates_frame = ttk.LabelFrame(dirs_frame, text="📋 模板目录", padding="15")
        templates_frame.pack(fill=tk.X, pady=(0, 10))

        templates_entry = ttk.Entry(templates_frame, textvariable=self.mix_templates_dir, width=60)
        templates_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        def select_templates_directory():
            directory = filedialog.askdirectory(title="选择模板目录")
            if directory:
                self.mix_templates_dir.set(directory)

        ttk.Button(templates_frame, text="浏览", command=select_templates_directory).pack(side=tk.RIGHT)

        # 输出目录
        output_frame = ttk.LabelFrame(dirs_frame, text="📤 输出目录", padding="15")
        output_frame.pack(fill=tk.X, pady=(0, 10))

        output_entry = ttk.Entry(output_frame, textvariable=self.mix_output_dir, width=60)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        def select_output_directory():
            directory = filedialog.askdirectory(title="选择输出目录")
            if directory:
                self.mix_output_dir.set(directory)

        ttk.Button(output_frame, text="浏览", command=select_output_directory).pack(side=tk.RIGHT)

        # 操作按钮
        button_frame = ttk.Frame(self.video_mix_frame)
        button_frame.pack(fill=tk.X, pady=20)

        # 预览按钮
        preview_btn = ttk.Button(button_frame, text="🔍 预览",
                               command=self.run_video_mix_preview, style='Action.TButton')
        preview_btn.pack(side=tk.LEFT, padx=(0, 15))

        # 开始混剪按钮
        mix_btn = ttk.Button(button_frame, text="🚀 开始混剪",
                           command=self.run_video_mix, style='Primary.TButton')
        mix_btn.pack(side=tk.LEFT, padx=(0, 15))

        # 打开输出目录按钮
        open_btn = ttk.Button(button_frame, text="📁 打开输出",
                            command=self.open_video_mix_output)
        open_btn.pack(side=tk.LEFT)

        # 状态显示
        status_frame = ttk.LabelFrame(self.video_mix_frame, text="📊 状态", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.mix_status_text = scrolledtext.ScrolledText(status_frame, height=10, wrap=tk.WORD)
        self.mix_status_text.pack(fill=tk.BOTH, expand=True)

        # 初始状态
        self.update_mix_status("等待选择目录...")


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
