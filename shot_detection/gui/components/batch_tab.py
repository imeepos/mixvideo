"""
Batch Tab Component
批量处理Tab组件
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from typing import List
import os

from .base_tab import BaseTab


class BatchTab(BaseTab):
    """批量处理Tab"""

    def setup_ui(self):
        """设置UI界面"""
        # 配置网格权重
        self.frame.columnconfigure(1, weight=1)

        # 创建主要区域
        self.create_input_section()
        self.create_settings_section()
        self.create_file_list_section()
        self.create_control_section()
        self.create_progress_section()
        self.create_results_section()

        # 初始化变量
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.recursive = tk.BooleanVar(value=True)
        self.quality_mode = tk.StringVar(value="medium")
        self.detector_type = tk.StringVar(value="multi_detector")
        self.processing = False
        self.video_files = []
        self.processed_count = 0
        self.total_count = 0

    def create_input_section(self):
        """创建输入目录区域"""
        input_frame = self.create_labeled_frame(self.frame, "📁 输入输出目录", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)

        # 输入目录
        ttk.Label(input_frame, text="输入目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_dir, width=50)
        self.input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(input_frame, text="浏览...",
                  command=self.browse_input_dir).grid(row=0, column=2, sticky=tk.W)

        # 输出目录
        ttk.Label(input_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.output_entry = ttk.Entry(input_frame, textvariable=self.output_dir, width=50)
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(input_frame, text="浏览...",
                  command=self.browse_output_dir).grid(row=1, column=2, sticky=tk.W, pady=(10, 0))

        # 递归搜索选项
        ttk.Checkbutton(input_frame, text="递归搜索子目录",
                       variable=self.recursive).grid(row=2, column=0, columnspan=2,
                                                     sticky=tk.W, pady=(10, 0))

    def create_settings_section(self):
        """创建设置区域"""
        settings_frame = self.create_labeled_frame(self.frame, "⚙️ 批量处理设置", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)

        # 检测器类型
        ttk.Label(settings_frame, text="检测算法:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        detector_combo = ttk.Combobox(settings_frame, textvariable=self.detector_type,
                                     values=["multi_detector", "frame_difference", "histogram"],
                                     state="readonly", width=20)
        detector_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        # 质量模式
        ttk.Label(settings_frame, text="输出质量:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        quality_combo = ttk.Combobox(settings_frame, textvariable=self.quality_mode,
                                    values=["low", "medium", "high"],
                                    state="readonly", width=15)
        quality_combo.grid(row=0, column=3, sticky=tk.W)

        # 文件过滤
        filter_frame = ttk.LabelFrame(settings_frame, text="文件过滤", padding="5")
        filter_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))

        self.min_size_var = tk.StringVar(value="1")
        self.max_size_var = tk.StringVar(value="1000")

        ttk.Label(filter_frame, text="文件大小范围 (MB):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(filter_frame, textvariable=self.min_size_var, width=8).grid(row=0, column=1, padx=(0, 5))
        ttk.Label(filter_frame, text="到").grid(row=0, column=2, padx=5)
        ttk.Entry(filter_frame, textvariable=self.max_size_var, width=8).grid(row=0, column=3, padx=(5, 0))

    def create_file_list_section(self):
        """创建文件列表区域"""
        list_frame = self.create_labeled_frame(self.frame, "📋 待处理文件列表", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # 创建Treeview
        columns = ("文件名", "大小", "时长", "状态")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=8)

        # 设置列
        self.file_tree.heading("#0", text="路径")
        self.file_tree.column("#0", width=300)

        for i, col in enumerate(columns):
            self.file_tree.heading(f"#{i+1}", text=col)
            self.file_tree.column(f"#{i+1}", width=100)

        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 滚动条
        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_tree.configure(yscrollcommand=tree_scrollbar.set)

        # 按钮框架
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(button_frame, text="🔍 扫描文件",
                  command=self.scan_files).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🗑️ 清空列表",
                  command=self.clear_file_list).pack(side=tk.LEFT, padx=(0, 10))

        # 文件统计标签
        self.file_count_label = ttk.Label(button_frame, text="文件数量: 0")
        self.file_count_label.pack(side=tk.RIGHT)

        # 配置网格权重
        self.frame.rowconfigure(2, weight=1)

    def create_control_section(self):
        """创建控制按钮区域"""
        control_frame = self.create_button_frame(self.frame, padding="10")
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 主要按钮
        self.start_button = ttk.Button(control_frame, text="🚀 开始批量处理",
                                      command=self.start_batch_processing, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(control_frame, text="⏹️ 停止处理",
                                     command=self.stop_batch_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))

        self.export_button = ttk.Button(control_frame, text="📊 导出报告",
                                       command=self.export_report, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))

        # 右侧按钮
        self.clear_button = ttk.Button(control_frame, text="🗑️ 清空日志",
                                      command=self.clear_log)
        self.clear_button.pack(side=tk.RIGHT, padx=(10, 0))

        self.settings_button = ttk.Button(control_frame, text="⚙️ 高级设置",
                                         command=self.show_advanced_settings)
        self.settings_button.pack(side=tk.RIGHT, padx=(10, 0))

    def create_progress_section(self):
        """创建进度显示区域"""
        progress_frame = self.create_labeled_frame(self.frame, "📊 批量处理进度", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        # 总体进度
        ttk.Label(progress_frame, text="总体进度:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.overall_progress_var = tk.DoubleVar()
        self.overall_progress = ttk.Progressbar(progress_frame, variable=self.overall_progress_var,
                                               maximum=100, length=400)
        self.overall_progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 当前文件进度
        ttk.Label(progress_frame, text="当前文件:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.current_progress_var = tk.DoubleVar()
        self.current_progress = ttk.Progressbar(progress_frame, variable=self.current_progress_var,
                                               maximum=100, length=400)
        self.current_progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 状态信息
        self.status_frame = ttk.Frame(progress_frame)
        self.status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.status_frame.columnconfigure(1, weight=1)

        ttk.Label(self.status_frame, text="当前文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.current_file_var = tk.StringVar(value="无")
        ttk.Label(self.status_frame, textvariable=self.current_file_var).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(self.status_frame, text="处理状态:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self.status_frame, textvariable=self.status_var).grid(row=1, column=1, sticky=tk.W)

        ttk.Label(self.status_frame, text="完成数量:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.completed_var = tk.StringVar(value="0/0")
        ttk.Label(self.status_frame, textvariable=self.completed_var).grid(row=2, column=1, sticky=tk.W)

    def create_results_section(self):
        """创建结果显示区域"""
        results_frame = self.create_labeled_frame(self.frame, "📋 处理日志", padding="10")
        results_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # 日志文本框
        self.log_text = tk.Text(results_frame, height=12, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 滚动条
        log_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        # 配置网格权重
        self.frame.rowconfigure(5, weight=1)

    def browse_input_dir(self):
        """浏览输入目录"""
        dirname = filedialog.askdirectory(title="选择输入目录")
        if dirname:
            self.input_dir.set(dirname)
            # 自动设置输出目录
            if not self.output_dir.get():
                output_dir = Path(dirname).parent / "batch_output"
                self.output_dir.set(str(output_dir))
            self.log_message(f"选择输入目录: {dirname}")

    def browse_output_dir(self):
        """浏览输出目录"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_dir.set(dirname)
            self.log_message(f"设置输出目录: {dirname}")

    def scan_files(self):
        """扫描文件"""
        input_dir = self.input_dir.get().strip()
        if not input_dir:
            self.show_error("输入错误", "请先选择输入目录")
            return

        if not Path(input_dir).exists():
            self.show_error("目录错误", "输入目录不存在")
            return

        try:
            self.log_message("开始扫描视频文件...")

            # 使用批量服务扫描文件
            from core.services import BatchService
            from core.detection import FrameDifferenceDetector

            detector = FrameDifferenceDetector()
            batch_service = BatchService(detector)

            # 获取过滤参数
            min_size = float(self.min_size_var.get() or 1)
            max_size = float(self.max_size_var.get() or 1000)

            video_files = batch_service.scan_video_files(
                input_dir,
                recursive=self.recursive.get(),
                min_size_mb=min_size,
                max_size_mb=max_size
            )

            # 清空现有列表
            self.clear_file_list()

            # 添加到列表
            for file_info in video_files:
                self.add_file_to_list(file_info)

            self.log_message(f"扫描完成，找到 {len(video_files)} 个视频文件")
            self.file_count_label.config(text=f"文件数量: {len(video_files)}")

            # 保存文件列表
            self.video_files = video_files

        except Exception as e:
            self.show_error("扫描失败", str(e))
            self.log_message(f"扫描失败: {e}", "error")

    def add_file_to_list(self, file_info):
        """添加文件到列表"""
        # 格式化文件大小
        size_mb = file_info.get('size_mb', 0)
        size_str = f"{size_mb:.1f} MB"

        # 格式化时长
        duration = file_info.get('duration', 0)
        duration_str = f"{duration:.1f}s" if duration > 0 else "未知"

        # 插入到树形视图
        item = self.file_tree.insert("", tk.END,
                                     text=file_info.get('relative_path', ''),
                                     values=(
                                         file_info.get('name', ''),
                                         size_str,
                                         duration_str,
                                         file_info.get('status', '待处理')
                                     ))

        # 保存文件信息到item
        self.file_tree.set(item, "file_info", file_info)

    def clear_file_list(self):
        """清空文件列表"""
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        self.file_count_label.config(text="文件数量: 0")
        self.video_files = []

    def start_batch_processing(self):
        """开始批量处理"""
        if not self.validate_batch_inputs():
            return

        self.processing = True
        self.update_ui_state()

        # 在后台线程中运行批量处理
        processing_thread = threading.Thread(target=self.run_batch_processing)
        processing_thread.daemon = True
        processing_thread.start()

    def stop_batch_processing(self):
        """停止批量处理"""
        self.processing = False
        self.update_ui_state()
        self.log_message("用户取消了批量处理任务", "warning")

    def run_batch_processing(self):
        """运行批量处理任务"""
        try:
            self.log_message("开始批量处理...")

            # 创建批量服务
            from core.services import BatchService
            from core.detection import FrameDifferenceDetector, HistogramDetector, MultiDetector

            # 根据设置创建检测器
            detector_type = self.detector_type.get()
            if detector_type == "frame_difference":
                detector = FrameDifferenceDetector()
            elif detector_type == "histogram":
                detector = HistogramDetector()
            else:  # multi_detector
                detectors = [FrameDifferenceDetector(), HistogramDetector()]
                detector = MultiDetector(detectors)

            batch_service = BatchService(detector, max_workers=4)

            # 准备文件路径列表
            video_paths = [file_info['path'] for file_info in self.video_files]
            output_dir = self.output_dir.get()

            # 执行批量处理
            results = batch_service.process_batch(
                self.video_files,
                output_dir,
                progress_callback=self.update_batch_progress
            )

            if results['success']:
                self.log_message(f"✅ 批量处理完成！")
                self.log_message(f"   成功处理: {results['success_count']}/{results['total_files']}")
                self.log_message(f"   报告文件: {results.get('report_file', 'N/A')}")

                # 启用导出按钮
                self.export_button.config(state=tk.NORMAL)

                # 保存结果
                self.batch_results = results
            else:
                self.log_message(f"❌ 批量处理失败: {results.get('error', '未知错误')}", "error")

        except Exception as e:
            self.log_message(f"❌ 批量处理异常: {str(e)}", "error")
            self.show_error("处理失败", str(e))
        finally:
            self.processing = False
            self.update_ui_state()

    def update_batch_progress(self, completed, total, current_file):
        """更新批量处理进度"""
        # 更新总体进度
        overall_progress = (completed / total * 100) if total > 0 else 0
        self.overall_progress_var.set(overall_progress)

        # 更新状态信息
        self.current_file_var.set(current_file)
        self.completed_var.set(f"{completed}/{total}")

        if completed < total:
            self.status_var.set(f"正在处理 ({completed+1}/{total})")
        else:
            self.status_var.set("处理完成")

        # 强制更新UI
        self.frame.update_idletasks()

    def export_report(self):
        """导出处理报告"""
        if not hasattr(self, 'batch_results'):
            self.show_warning("导出失败", "没有可导出的处理结果")
            return

        try:
            # 选择导出文件
            filename = filedialog.asksaveasfilename(
                title="导出处理报告",
                defaultextension=".json",
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("CSV文件", "*.csv"),
                    ("所有文件", "*.*")
                ]
            )

            if filename:
                import json

                # 导出JSON格式
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.batch_results, f, indent=2, ensure_ascii=False, default=str)

                # 导出CSV格式
                elif filename.endswith('.csv'):
                    import csv
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['文件名', '状态', '处理时间', '检测边界数', '错误信息'])

                        for result in self.batch_results.get('results', []):
                            file_info = result.get('file_info', {})
                            detection_result = result.get('detection_result', {})

                            writer.writerow([
                                file_info.get('name', ''),
                                '成功' if result.get('success', False) else '失败',
                                f"{detection_result.get('processing_time', 0):.2f}s",
                                len(detection_result.get('boundaries', [])),
                                result.get('error', '')
                            ])

                self.log_message(f"报告已导出到: {filename}")
                self.show_info("导出成功", f"处理报告已保存到:\n{filename}")

        except Exception as e:
            self.show_error("导出失败", str(e))
            self.log_message(f"导出报告失败: {e}", "error")

    def show_advanced_settings(self):
        """显示高级设置对话框"""
        # 创建设置窗口
        settings_window = tk.Toplevel(self.frame)
        settings_window.title("批量处理高级设置")
        settings_window.geometry("400x300")
        settings_window.transient(self.frame.winfo_toplevel())
        settings_window.grab_set()

        # 设置内容
        main_frame = ttk.Frame(settings_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 线程数设置
        ttk.Label(main_frame, text="最大工作线程数:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        thread_var = tk.IntVar(value=4)
        thread_spin = ttk.Spinbox(main_frame, from_=1, to=16, textvariable=thread_var, width=10)
        thread_spin.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))

        # 超时设置
        ttk.Label(main_frame, text="处理超时(秒):").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        timeout_var = tk.IntVar(value=300)
        timeout_spin = ttk.Spinbox(main_frame, from_=60, to=3600, textvariable=timeout_var, width=10)
        timeout_spin.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))

        # 重试次数
        ttk.Label(main_frame, text="失败重试次数:").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        retry_var = tk.IntVar(value=1)
        retry_spin = ttk.Spinbox(main_frame, from_=0, to=5, textvariable=retry_var, width=10)
        retry_spin.grid(row=2, column=1, sticky=tk.W, pady=(0, 10))

        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))

        def apply_settings():
            # 这里可以保存设置到配置文件
            self.log_message(f"应用高级设置: 线程数={thread_var.get()}, 超时={timeout_var.get()}s")
            settings_window.destroy()

        ttk.Button(button_frame, text="应用", command=apply_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=settings_window.destroy).pack(side=tk.LEFT)

    def update_ui_state(self):
        """更新UI状态"""
        if self.processing:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.input_entry.config(state=tk.DISABLED)
            self.output_entry.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.input_entry.config(state=tk.NORMAL)
            self.output_entry.config(state=tk.NORMAL)

    def validate_batch_inputs(self) -> bool:
        """验证批量处理输入"""
        input_dir = self.input_dir.get().strip()
        if not input_dir:
            self.show_error("输入错误", "请选择输入目录")
            return False

        if not Path(input_dir).exists():
            self.show_error("目录错误", "输入目录不存在")
            return False

        output_dir = self.output_dir.get().strip()
        if not output_dir:
            self.show_error("输入错误", "请选择输出目录")
            return False

        if not self.video_files:
            self.show_error("文件错误", "没有找到可处理的视频文件，请先扫描文件")
            return False

        return True

    def bind_events(self):
        """绑定事件"""
        # 绑定回车键到扫描按钮
        self.frame.bind('<Return>', lambda e: self.scan_files())

        # 绑定文件列表双击事件
        self.file_tree.bind('<Double-1>', self.on_file_double_click)

    def on_file_double_click(self, event):
        """文件列表双击事件"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            file_path = self.file_tree.item(item, "text")
            self.log_message(f"双击文件: {file_path}")

            # 这里可以添加预览功能
            # self.preview_file(file_path)

    def on_tab_selected(self):
        """Tab被选中时的回调"""
        super().on_tab_selected()
        # 设置焦点到输入目录
        self.input_entry.focus_set()

    def cleanup(self):
        """清理资源"""
        super().cleanup()
        if self.processing:
            self.processing = False
