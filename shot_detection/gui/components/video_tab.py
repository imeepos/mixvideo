"""
Video Tab Component
视频Tab组件
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from typing import Optional

from .base_tab import BaseTab


class VideoTab(BaseTab):
    """视频处理Tab"""

    def setup_ui(self):
        """设置UI界面"""
        # 配置网格权重
        self.frame.columnconfigure(1, weight=1)

        # 创建主要区域
        self.create_input_section()
        self.create_settings_section()
        self.create_control_section()
        self.create_progress_section()
        self.create_results_section()

        # 初始化变量
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.quality_mode = tk.StringVar(value="medium")
        self.detector_type = tk.StringVar(value="multi_detector")
        self.processing = False

    def create_input_section(self):
        """创建输入文件区域"""
        input_frame = self.create_labeled_frame(self.frame, "📁 输入文件", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)

        # 视频文件选择
        ttk.Label(input_frame, text="视频文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.video_entry = ttk.Entry(input_frame, textvariable=self.video_path, width=50)
        self.video_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(input_frame, text="浏览...",
                  command=self.browse_video_file).grid(row=0, column=2, sticky=tk.W)

        # 输出目录选择
        ttk.Label(input_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.output_entry = ttk.Entry(input_frame, textvariable=self.output_path, width=50)
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(input_frame, text="浏览...",
                  command=self.browse_output_dir).grid(row=1, column=2, sticky=tk.W, pady=(10, 0))

    def create_settings_section(self):
        """创建设置区域"""
        settings_frame = self.create_labeled_frame(self.frame, "⚙️ 检测设置", padding="10")
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

        # 高级设置
        advanced_frame = ttk.LabelFrame(settings_frame, text="高级设置", padding="5")
        advanced_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        advanced_frame.columnconfigure(1, weight=1)

        # 阈值设置
        ttk.Label(advanced_frame, text="检测阈值:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.threshold_var = tk.DoubleVar(value=0.3)
        threshold_scale = ttk.Scale(advanced_frame, from_=0.1, to=1.0,
                                   variable=self.threshold_var, orient=tk.HORIZONTAL)
        threshold_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.threshold_label = ttk.Label(advanced_frame, text="0.30")
        self.threshold_label.grid(row=0, column=2, sticky=tk.W)

        # 绑定阈值更新
        threshold_scale.configure(command=self.update_threshold_label)

    def create_control_section(self):
        """创建控制按钮区域"""
        control_frame = self.create_button_frame(self.frame, padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 按钮
        self.start_button = ttk.Button(control_frame, text="🚀 开始检测",
                                      command=self.start_detection, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(control_frame, text="⏹️ 停止",
                                     command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))

        self.preview_button = ttk.Button(control_frame, text="👁️ 预览结果",
                                        command=self.preview_results, state=tk.DISABLED)
        self.preview_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = ttk.Button(control_frame, text="🗑️ 清空日志",
                                      command=self.clear_log)
        self.clear_button.pack(side=tk.RIGHT)

    def create_progress_section(self):
        """创建进度显示区域"""
        progress_frame = self.create_labeled_frame(self.frame, "📊 处理进度", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W)

    def create_results_section(self):
        """创建结果显示区域"""
        results_frame = self.create_labeled_frame(self.frame, "📋 处理日志", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
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
        self.frame.rowconfigure(4, weight=1)

    def browse_video_file(self):
        """浏览视频文件"""
        filetypes = [
            ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
            ("所有文件", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=filetypes
        )
        if filename:
            self.video_path.set(filename)
            # 自动设置输出目录
            if not self.output_path.get():
                output_dir = Path(filename).parent / "segments"
                self.output_path.set(str(output_dir))
            self.log_message(f"选择视频文件: {filename}")

    def browse_output_dir(self):
        """浏览输出目录"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_path.set(dirname)
            self.log_message(f"设置输出目录: {dirname}")

    def update_threshold_label(self, value):
        """更新阈值标签"""
        self.threshold_label.config(text=f"{float(value):.2f}")

    def start_detection(self):
        """开始检测"""
        if not self.validate_inputs():
            return

        self.processing = True
        self.update_ui_state()

        # 在后台线程中运行检测
        detection_thread = threading.Thread(target=self.run_detection)
        detection_thread.daemon = True
        detection_thread.start()

    def stop_detection(self):
        """停止检测"""
        self.processing = False
        self.update_ui_state()
        self.log_message("用户取消了检测任务", "warning")

    def run_detection(self):
        """运行检测任务"""
        try:
            self.log_message("开始视频镜头检测...")
            self.update_progress(0.1, "初始化检测器...")

            # 导入检测模块
            from core.detection import FrameDifferenceDetector, HistogramDetector, MultiDetector

            # 创建检测器
            detector_type = self.detector_type.get()
            if detector_type == "frame_difference":
                detector = FrameDifferenceDetector(threshold=self.threshold_var.get())
            elif detector_type == "histogram":
                detector = HistogramDetector(threshold=self.threshold_var.get())
            else:  # multi_detector
                detectors = [
                    FrameDifferenceDetector(threshold=self.threshold_var.get()),
                    HistogramDetector(threshold=self.threshold_var.get())
                ]
                detector = MultiDetector(detectors)

            self.update_progress(0.2, "初始化检测器完成")

            # 初始化检测器
            if hasattr(detector, 'initialize'):
                if not detector.initialize():
                    raise Exception("检测器初始化失败")

            self.update_progress(0.3, "开始分析视频...")

            # 执行检测
            video_path = self.video_path.get()
            result = detector.detect_shots(video_path) if hasattr(detector, 'detect_shots') else \
                     detector.detect_shots_fusion(video_path)

            self.update_progress(0.7, f"检测完成，发现 {len(result.boundaries)} 个镜头边界")

            # 处理结果
            self.process_detection_result(result)

            self.update_progress(1.0, "检测任务完成")
            self.log_message(f"✅ 检测完成！共发现 {len(result.boundaries)} 个镜头边界")

            # 启用预览按钮
            self.preview_button.config(state=tk.NORMAL)

        except Exception as e:
            self.log_message(f"❌ 检测失败: {str(e)}", "error")
            self.show_error("检测失败", str(e))
        finally:
            self.processing = False
            self.update_ui_state()

    def process_detection_result(self, result):
        """处理检测结果"""
        try:
            # 创建输出目录
            output_dir = Path(self.output_path.get())
            output_dir.mkdir(parents=True, exist_ok=True)

            # 保存检测结果
            import json
            result_file = output_dir / "detection_result.json"

            # 转换结果为可序列化格式
            result_data = {
                "algorithm": result.algorithm_name,
                "processing_time": result.processing_time,
                "frame_count": result.frame_count,
                "boundaries": [
                    {
                        "frame_number": b.frame_number,
                        "timestamp": b.timestamp,
                        "confidence": b.confidence,
                        "boundary_type": b.boundary_type,
                        "metadata": b.metadata or {}
                    }
                    for b in result.boundaries
                ],
                "confidence_scores": result.confidence_scores,
                "metadata": result.metadata or {}
            }

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)

            self.log_message(f"检测结果已保存到: {result_file}")

            # 生成统计信息
            self.generate_statistics(result)

        except Exception as e:
            self.log_message(f"保存结果时出错: {str(e)}", "error")

    def generate_statistics(self, result):
        """生成统计信息"""
        boundaries = result.boundaries
        if not boundaries:
            self.log_message("未检测到镜头边界")
            return

        # 计算统计信息
        durations = []
        for i in range(len(boundaries) - 1):
            duration = boundaries[i + 1].timestamp - boundaries[i].timestamp
            durations.append(duration)

        if durations:
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)

            self.log_message("📊 统计信息:")
            self.log_message(f"   镜头数量: {len(boundaries)}")
            self.log_message(f"   平均时长: {avg_duration:.2f}秒")
            self.log_message(f"   最短时长: {min_duration:.2f}秒")
            self.log_message(f"   最长时长: {max_duration:.2f}秒")
            self.log_message(f"   处理时间: {result.processing_time:.2f}秒")

    def preview_results(self):
        """预览结果"""
        output_dir = Path(self.output_path.get())
        result_file = output_dir / "detection_result.json"

        if not result_file.exists():
            self.show_warning("预览失败", "未找到检测结果文件")
            return

        try:
            # 打开结果文件所在目录
            import subprocess
            import sys

            if sys.platform == "win32":
                subprocess.run(["explorer", str(output_dir)])
            elif sys.platform == "darwin":
                subprocess.run(["open", str(output_dir)])
            else:
                subprocess.run(["xdg-open", str(output_dir)])

            self.log_message(f"已打开结果目录: {output_dir}")

        except Exception as e:
            self.show_error("打开目录失败", str(e))

    def update_ui_state(self):
        """更新UI状态"""
        if self.processing:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.video_entry.config(state=tk.DISABLED)
            self.output_entry.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.video_entry.config(state=tk.NORMAL)
            self.output_entry.config(state=tk.NORMAL)

    def validate_inputs(self) -> bool:
        """验证输入"""
        video_path = self.video_path.get().strip()
        if not video_path:
            self.show_error("输入错误", "请选择视频文件")
            return False

        if not Path(video_path).exists():
            self.show_error("文件错误", "视频文件不存在")
            return False

        output_path = self.output_path.get().strip()
        if not output_path:
            self.show_error("输入错误", "请选择输出目录")
            return False

        return True

    def bind_events(self):
        """绑定事件"""
        # 绑定回车键到开始按钮
        self.frame.bind('<Return>', lambda e: self.start_detection())

        # 绑定文件拖放（如果需要的话）
        # self.video_entry.drop_target_register(DND_FILES)
        # self.video_entry.dnd_bind('<<Drop>>', self.on_file_drop)

    def on_tab_selected(self):
        """Tab被选中时的回调"""
        super().on_tab_selected()
        # 设置焦点到视频文件输入框
        self.video_entry.focus_set()

    def cleanup(self):
        """清理资源"""
        super().cleanup()
        if self.processing:
            self.processing = False
