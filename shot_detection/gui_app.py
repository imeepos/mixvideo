#!/usr/bin/env python3
"""
智能镜头检测与分段系统 - GUI界面
提供用户友好的图形界面操作
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
    """智能镜头检测与分段系统GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 智能镜头检测与分段系统")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 设置图标和样式
        self.setup_styles()
        
        # 变量
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.organize_mode = tk.StringVar(value="duration")
        self.quality_mode = tk.StringVar(value="medium")
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
        """创建界面组件"""
        # 创建主画布和滚动条
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # 配置滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # 创建画布窗口
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 布局画布和滚动条
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮事件
        self.bind_mousewheel()

        # 绑定画布大小变化事件
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # 主容器（在可滚动框架内）
        main_frame = ttk.Frame(self.scrollable_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🎬 智能镜头检测与分段系统", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        self.create_file_selection(main_frame, 1)
        
        # 设置区域
        self.create_settings_section(main_frame, 2)
        
        # 视频信息区域
        self.create_video_info_section(main_frame, 3)
        
        # 控制按钮区域
        self.create_control_buttons(main_frame, 4)
        
        # 进度和日志区域
        self.create_progress_section(main_frame, 5)
        
        # 结果区域
        self.create_results_section(main_frame, 6)

    def bind_mousewheel(self):
        """绑定鼠标滚轮事件"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")

        # 绑定鼠标进入和离开事件
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)

        # Linux系统的滚轮事件
        def _on_mousewheel_linux(event):
            self.canvas.yview_scroll(-1, "units")

        def _on_mousewheel_linux_up(event):
            self.canvas.yview_scroll(1, "units")

        self.canvas.bind("<Button-4>", _on_mousewheel_linux_up)
        self.canvas.bind("<Button-5>", _on_mousewheel_linux)

    def on_canvas_configure(self, event):
        """画布大小变化事件"""
        # 更新滚动区域的宽度以匹配画布宽度
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
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
    
    def create_settings_section(self, parent, row):
        """创建设置区域"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ 处理设置", padding="10")
        settings_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 组织方式
        ttk.Label(settings_frame, text="分段组织方式:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        organize_combo = ttk.Combobox(settings_frame, textvariable=self.organize_mode, 
                                     values=["duration", "quality", "none"], state="readonly", width=15)
        organize_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # 质量设置
        ttk.Label(settings_frame, text="输出质量:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        quality_combo = ttk.Combobox(settings_frame, textvariable=self.quality_mode,
                                    values=["low", "medium", "high", "lossless"], state="readonly", width=15)
        quality_combo.grid(row=0, column=3, sticky=tk.W)
        
        # 说明文本
        info_text = """
组织方式说明:
• duration: 按时长分类 (短片段≤5s, 中等5-30s, 长片段>30s)
• quality: 按检测质量分类 (高/中/低置信度)
• none: 所有分段放在同一目录

质量设置说明:
• low: 快速处理，文件较小
• medium: 平衡质量和大小
• high: 高质量，文件较大
• lossless: 无损质量，文件最大
        """
        info_label = ttk.Label(settings_frame, text=info_text.strip(), style='Info.TLabel', justify=tk.LEFT)
        info_label.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_video_info_section(self, parent, row):
        """创建视频信息区域"""
        self.info_frame = ttk.LabelFrame(parent, text="📹 视频信息", padding="10")
        self.info_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.video_info_label = ttk.Label(self.info_frame, text="请选择视频文件", style='Info.TLabel')
        self.video_info_label.grid(row=0, column=0, sticky=tk.W)
    
    def create_control_buttons(self, parent, row):
        """创建控制按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        
        # 开始处理按钮
        self.start_button = ttk.Button(button_frame, text="🚀 开始处理", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止按钮
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清除日志按钮
        self.clear_button = ttk.Button(button_frame, text="🗑️ 清除日志", command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 打开输出目录按钮
        self.open_output_button = ttk.Button(button_frame, text="📁 打开输出目录", 
                                           command=self.open_output_directory, state=tk.DISABLED)
        self.open_output_button.pack(side=tk.LEFT)
    
    def create_progress_section(self, parent, row):
        """创建进度和日志区域"""
        progress_frame = ttk.LabelFrame(parent, text="📊 处理进度", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(1, weight=1)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态标签
        self.status_label = ttk.Label(progress_frame, text="就绪", style='Info.TLabel')
        self.status_label.grid(row=0, column=1, padx=(10, 0))
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=12, wrap=tk.WORD)
        self.log_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行权重
        parent.rowconfigure(row, weight=1)
    
    def create_results_section(self, parent, row):
        """创建结果区域"""
        self.results_frame = ttk.LabelFrame(parent, text="📋 处理结果", padding="10")
        self.results_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        self.results_frame.columnconfigure(1, weight=1)
        
        # 结果按钮（初始隐藏）
        self.view_report_button = ttk.Button(self.results_frame, text="📊 查看分析报告", 
                                           command=self.view_analysis_report)
        self.view_segments_button = ttk.Button(self.results_frame, text="🎬 查看视频分段", 
                                             command=self.view_video_segments)
        self.view_projects_button = ttk.Button(self.results_frame, text="📤 查看项目文件", 
                                             command=self.view_project_files)
        
        # 结果统计标签
        self.results_label = ttk.Label(self.results_frame, text="", style='Info.TLabel')
        self.results_label.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
    
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
    
    def update_video_info(self):
        """更新视频信息显示"""
        video_file = self.video_path.get()
        
        if not video_file or not os.path.exists(video_file):
            self.video_info_label.config(text="请选择有效的视频文件")
            return
        
        try:
            if validate_video_file(video_file):
                info = get_basic_video_info(video_file)
                
                info_text = f"""
文件名: {Path(video_file).name}
时长: {format_duration(info['duration'])}
分辨率: {info['width']}x{info['height']}
帧率: {info['fps']:.1f} FPS
文件大小: {format_file_size(info['file_size'])}
                """.strip()
                
                self.video_info_label.config(text=info_text)
            else:
                self.video_info_label.config(text="无效的视频文件格式")
                
        except Exception as e:
            self.video_info_label.config(text=f"读取视频信息失败: {e}")
    
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
    
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)
    
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

            # 开始处理步骤
            self.progress_monitor.next_step("开始处理...")

            # 执行处理（使用带回调的版本）
            success = process_video_with_gui_callbacks(
                self.video_path.get(),
                self.output_path.get(),
                self.organize_mode.get(),
                self.quality_mode.get(),
                progress_callback=self.update_progress,
                log_callback=self.log_message
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
            self.progress_var.set(progress)
            self.status_label.config(text=description)
            self.processing_status.update_phase(description)
            # 强制更新界面
            self.root.update_idletasks()

        # 确保在主线程中执行GUI更新
        if threading.current_thread() == threading.main_thread():
            _update_gui()
        else:
            self.root.after(0, _update_gui)

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
        """显示结果按钮"""
        self.view_report_button.grid(row=1, column=0, padx=(0, 10), pady=(10, 0))
        self.view_segments_button.grid(row=1, column=1, padx=(0, 10), pady=(10, 0))
        self.view_projects_button.grid(row=1, column=2, pady=(10, 0))

    def hide_result_buttons(self):
        """隐藏结果按钮"""
        self.view_report_button.grid_remove()
        self.view_segments_button.grid_remove()
        self.view_projects_button.grid_remove()
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
