"""
Analysis Tab Component
分析Tab组件
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import json
from typing import Optional, Dict, Any, List

from .base_tab import BaseTab


class AnalysisTab(BaseTab):
    """视频分析Tab"""

    def setup_ui(self):
        """设置UI界面"""
        # 配置网格权重
        self.frame.columnconfigure(1, weight=1)

        # 创建主要区域
        self.create_input_section()
        self.create_analysis_options_section()
        self.create_control_section()
        self.create_progress_section()
        self.create_results_section()

        # 初始化变量
        self.video_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.analysis_types = {
            'basic': tk.BooleanVar(value=True),
            'quality': tk.BooleanVar(value=True),
            'content': tk.BooleanVar(value=False),
            'motion': tk.BooleanVar(value=True),
            'color': tk.BooleanVar(value=True)
        }
        self.processing = False
        self.analysis_results = None

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
        self.output_entry = ttk.Entry(input_frame, textvariable=self.output_dir, width=50)
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(input_frame, text="浏览...",
                  command=self.browse_output_dir).grid(row=1, column=2, sticky=tk.W, pady=(10, 0))

    def create_analysis_options_section(self):
        """创建分析选项区域"""
        options_frame = self.create_labeled_frame(self.frame, "🔍 分析选项", padding="10")
        options_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 分析类型选择
        ttk.Label(options_frame, text="选择分析类型:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        # 基础分析
        ttk.Checkbutton(options_frame, text="📊 基础信息分析",
                       variable=self.analysis_types['basic']).grid(
                           row=1, column=0, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Label(options_frame, text="(时长、分辨率、帧率等)",
                 foreground='gray').grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        # 质量分析
        ttk.Checkbutton(options_frame, text="🎯 视频质量分析",
                       variable=self.analysis_types['quality']).grid(
                           row=2, column=0, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Label(options_frame, text="(亮度、对比度、清晰度等)",
                 foreground='gray').grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

        # 运动分析
        ttk.Checkbutton(options_frame, text="🏃 运动强度分析",
                       variable=self.analysis_types['motion']).grid(
                           row=3, column=0, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Label(options_frame, text="(场景变化、运动检测等)",
                 foreground='gray').grid(row=3, column=1, sticky=tk.W, padx=(10, 0))

        # 颜色分析
        ttk.Checkbutton(options_frame, text="🎨 颜色特征分析",
                       variable=self.analysis_types['color']).grid(
                           row=4, column=0, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Label(options_frame, text="(主要颜色、色彩分布等)",
                 foreground='gray').grid(row=4, column=1, sticky=tk.W, padx=(10, 0))

        # 内容分析（高级功能）
        ttk.Checkbutton(options_frame, text="🧠 内容识别分析 (实验性)",
                       variable=self.analysis_types['content']).grid(
                           row=5, column=0, sticky=tk.W, padx=(20, 0), pady=2)
        ttk.Label(options_frame, text="(对象检测、场景识别等)",
                 foreground='gray').grid(row=5, column=1, sticky=tk.W, padx=(10, 0))

    def create_control_section(self):
        """创建控制按钮区域"""
        control_frame = self.create_button_frame(self.frame, padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # 按钮
        self.start_button = ttk.Button(control_frame, text="🚀 开始分析",
                                      command=self.start_analysis, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_button = ttk.Button(control_frame, text="⏹️ 停止",
                                     command=self.stop_analysis, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))

        self.export_button = ttk.Button(control_frame, text="📊 导出报告",
                                       command=self.export_analysis_report, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = ttk.Button(control_frame, text="🗑️ 清空日志",
                                      command=self.clear_log)
        self.clear_button.pack(side=tk.RIGHT)

    def create_progress_section(self):
        """创建进度显示区域"""
        progress_frame = self.create_labeled_frame(self.frame, "📊 分析进度", padding="10")
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
        results_frame = self.create_labeled_frame(self.frame, "📋 分析结果", padding="10")
        results_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # 创建Notebook用于显示不同类型的结果
        self.results_notebook = ttk.Notebook(results_frame)
        self.results_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 日志Tab
        self.log_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.log_frame, text="📋 处理日志")

        self.log_text = tk.Text(self.log_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        log_scrollbar = ttk.Scrollbar(self.log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        # 结果Tab（动态创建）
        self.result_tabs = {}

        # 配置网格权重
        self.frame.rowconfigure(4, weight=1)

    def browse_video_file(self):
        """浏览视频文件"""
        filename = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("MP4文件", "*.mp4"),
                ("AVI文件", "*.avi"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.video_path.set(filename)
            # 自动设置输出目录
            if not self.output_dir.get():
                output_dir = Path(filename).parent / "analysis_output"
                self.output_dir.set(str(output_dir))
            self.log_message(f"选择视频文件: {filename}")

    def browse_output_dir(self):
        """浏览输出目录"""
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_dir.set(dirname)
            self.log_message(f"设置输出目录: {dirname}")

    def start_analysis(self):
        """开始分析"""
        if not self.validate_inputs():
            return

        self.processing = True
        self.update_ui_state()

        # 在后台线程中运行分析
        analysis_thread = threading.Thread(target=self.run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()

    def stop_analysis(self):
        """停止分析"""
        self.processing = False
        self.update_ui_state()
        self.log_message("用户取消了分析任务", "warning")

    def run_analysis(self):
        """运行分析任务"""
        try:
            self.log_message("开始视频分析...")

            video_path = self.video_path.get()
            output_dir = self.output_dir.get()

            # 更新进度
            self.update_progress(0.1, "初始化分析服务...")

            # 创建分析服务
            from core.services import AdvancedAnalysisService
            analysis_service = AdvancedAnalysisService()

            # 执行分析
            self.update_progress(0.2, "开始综合分析...")

            result = analysis_service.analyze_video_comprehensive(
                video_path,
                progress_callback=self.update_analysis_progress
            )

            if result['success']:
                self.log_message("✅ 视频分析完成！")
                self.analysis_results = result

                # 显示结果
                self.display_analysis_results(result)

                # 启用导出按钮
                self.export_button.config(state=tk.NORMAL)

                # 保存结果到文件
                self.save_analysis_results(result, output_dir)

            else:
                self.log_message(f"❌ 视频分析失败: {result.get('error', '未知错误')}", "error")

        except Exception as e:
            self.log_message(f"❌ 分析异常: {str(e)}", "error")
            self.show_error("分析失败", str(e))
        finally:
            self.processing = False
            self.update_ui_state()
            self.update_progress(1.0, "分析完成")

    def update_analysis_progress(self, progress: float, status: str):
        """更新分析进度"""
        # 将分析进度映射到总进度的20%-90%区间
        total_progress = 0.2 + progress * 0.7
        self.update_progress(total_progress, status)

    def update_progress(self, progress: float, status: str):
        """更新进度"""
        self.progress_var.set(progress * 100)
        self.status_var.set(status)
        self.frame.update_idletasks()

    def display_analysis_results(self, result: Dict[str, Any]):
        """显示分析结果"""
        try:
            # 清除现有的结果Tab
            for tab_name in list(self.result_tabs.keys()):
                self.results_notebook.forget(self.result_tabs[tab_name])
                del self.result_tabs[tab_name]

            # 基础信息Tab
            if 'video_metrics' in result:
                self.create_metrics_tab(result['video_metrics'])

            # 质量分析Tab
            if 'quality_analysis' in result:
                self.create_quality_tab(result['quality_analysis'])

            # 镜头分析Tab
            if 'shot_analyses' in result and result['shot_analyses']:
                self.create_shots_tab(result['shot_analyses'])

            # 分析报告Tab
            if 'analysis_report' in result:
                self.create_report_tab(result['analysis_report'])

        except Exception as e:
            self.log_message(f"显示结果失败: {e}", "error")

    def create_metrics_tab(self, metrics: Dict[str, Any]):
        """创建基础指标Tab"""
        metrics_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(metrics_frame, text="📊 基础信息")
        self.result_tabs['metrics'] = metrics_frame

        # 创建滚动文本框
        text_widget = tk.Text(metrics_frame, wrap=tk.WORD, state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 格式化显示指标
        info_lines = [
            f"视频时长: {metrics.get('duration', 0):.2f} 秒",
            f"总帧数: {metrics.get('frame_count', 0)}",
            f"帧率: {metrics.get('fps', 0):.2f} fps",
            f"分辨率: {metrics.get('resolution', (0, 0))[0]}x{metrics.get('resolution', (0, 0))[1]}",
            f"文件大小: {metrics.get('file_size_mb', 0):.1f} MB",
            "",
            "质量指标:",
            f"  平均亮度: {metrics.get('avg_brightness', 0):.1f}",
            f"  平均对比度: {metrics.get('avg_contrast', 0):.1f}",
            f"  清晰度分数: {metrics.get('sharpness_score', 0):.1f}",
            f"  噪声水平: {metrics.get('noise_level', 0):.1f}",
            "",
            "内容指标:",
            f"  场景复杂度: {metrics.get('scene_complexity', 0):.1f}",
            f"  运动强度: {metrics.get('motion_intensity', 0):.1f}",
            f"  颜色多样性: {metrics.get('color_diversity', 0):.1f}"
        ]

        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, "\n".join(info_lines))
        text_widget.config(state=tk.DISABLED)

    def create_quality_tab(self, quality: Dict[str, Any]):
        """创建质量分析Tab"""
        quality_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(quality_frame, text="🎯 质量分析")
        self.result_tabs['quality'] = quality_frame

        # 创建滚动文本框
        text_widget = tk.Text(quality_frame, wrap=tk.WORD, state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 格式化显示质量信息
        quality_lines = [
            f"平均亮度: {quality.get('avg_brightness', 0):.1f} (标准差: {quality.get('brightness_std', 0):.1f})",
            f"平均对比度: {quality.get('avg_contrast', 0):.1f} (标准差: {quality.get('contrast_std', 0):.1f})",
            f"平均清晰度: {quality.get('avg_sharpness', 0):.1f} (标准差: {quality.get('sharpness_std', 0):.1f})",
            f"综合质量分数: {quality.get('quality_score', 0):.2f}",
            "",
            "质量评估:",
        ]

        # 添加质量评估
        score = quality.get('quality_score', 0)
        if score >= 0.8:
            quality_lines.append("  ✅ 优秀 - 视频质量很好")
        elif score >= 0.6:
            quality_lines.append("  👍 良好 - 视频质量不错")
        elif score >= 0.4:
            quality_lines.append("  ⚠️ 一般 - 视频质量有待改善")
        else:
            quality_lines.append("  ❌ 较差 - 视频质量需要提升")

        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, "\n".join(quality_lines))
        text_widget.config(state=tk.DISABLED)

    def create_shots_tab(self, shots: List[Dict[str, Any]]):
        """创建镜头分析Tab"""
        shots_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(shots_frame, text="🎬 镜头分析")
        self.result_tabs['shots'] = shots_frame

        # 创建树形视图显示镜头信息
        columns = ('镜头', '开始时间', '时长', '亮度', '运动强度', '复杂度')
        tree = ttk.Treeview(shots_frame, columns=columns, show='headings', height=15)

        # 设置列标题
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(shots_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # 布局
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # 填充数据
        for shot in shots:
            tree.insert('', tk.END, values=(
                f"镜头 {shot.get('shot_index', 0) + 1}",
                f"{shot.get('start_time', 0):.1f}s",
                f"{shot.get('duration', 0):.1f}s",
                f"{shot.get('avg_brightness', 0):.1f}",
                f"{shot.get('motion_score', 0):.2f}",
                f"{shot.get('complexity_score', 0):.2f}"
            ))

    def create_report_tab(self, report: Dict[str, Any]):
        """创建分析报告Tab"""
        report_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(report_frame, text="📋 分析报告")
        self.result_tabs['report'] = report_frame

        # 创建滚动文本框
        text_widget = tk.Text(report_frame, wrap=tk.WORD, state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 格式化显示报告
        report_lines = []

        # 摘要信息
        summary = report.get('summary', {})
        report_lines.extend([
            "📊 分析摘要",
            "=" * 30,
            f"总时长: {summary.get('total_duration', 0):.2f} 秒",
            f"总镜头数: {summary.get('total_shots', 0)}",
            f"平均镜头时长: {summary.get('avg_shot_duration', 0):.2f} 秒",
            f"质量分数: {summary.get('quality_score', 0):.2f}",
            f"文件大小: {summary.get('file_size_mb', 0):.1f} MB",
            ""
        ])

        # 质量评估
        quality = report.get('quality_assessment', {})
        report_lines.extend([
            "🎯 质量评估",
            "=" * 30,
            f"亮度: {quality.get('brightness', 'unknown')}",
            f"对比度: {quality.get('contrast', 'unknown')}",
            f"清晰度: {quality.get('sharpness', 'unknown')}",
            ""
        ])

        # 内容分析
        content = report.get('content_analysis', {})
        report_lines.extend([
            "📈 内容分析",
            "=" * 30,
            f"平均运动强度: {content.get('avg_motion_intensity', 0):.2f}",
            f"平均场景复杂度: {content.get('avg_scene_complexity', 0):.2f}",
            f"镜头时长方差: {content.get('shot_duration_variance', 0):.2f}",
            ""
        ])

        # 改进建议
        recommendations = report.get('recommendations', [])
        if recommendations:
            report_lines.extend([
                "💡 改进建议",
                "=" * 30
            ])
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")

        text_widget.config(state=tk.NORMAL)
        text_widget.insert(tk.END, "\n".join(report_lines))
        text_widget.config(state=tk.DISABLED)

    def save_analysis_results(self, result: Dict[str, Any], output_dir: str):
        """保存分析结果"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 保存完整结果
            result_file = output_path / "analysis_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)

            self.log_message(f"分析结果已保存到: {result_file}")

        except Exception as e:
            self.log_message(f"保存结果失败: {e}", "error")

    def export_analysis_report(self):
        """导出分析报告"""
        if not hasattr(self, 'analysis_results') or not self.analysis_results:
            self.show_warning("导出失败", "没有可导出的分析结果")
            return

        try:
            filename = filedialog.asksaveasfilename(
                title="导出分析报告",
                defaultextension=".json",
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("文本文件", "*.txt"),
                    ("所有文件", "*.*")
                ]
            )

            if filename:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.analysis_results, f, indent=2, ensure_ascii=False, default=str)
                else:
                    # 导出为文本格式
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("Shot Detection 视频分析报告\n")
                        f.write("=" * 40 + "\n\n")

                        # 写入基本信息
                        metrics = self.analysis_results.get('video_metrics', {})
                        f.write(f"视频文件: {self.analysis_results.get('video_path', 'N/A')}\n")
                        f.write(f"分析时间: {self.analysis_results.get('timestamp', 'N/A')}\n")
                        f.write(f"视频时长: {metrics.get('duration', 0):.2f} 秒\n")
                        f.write(f"分辨率: {metrics.get('resolution', (0, 0))[0]}x{metrics.get('resolution', (0, 0))[1]}\n\n")

                        # 写入分析报告
                        report = self.analysis_results.get('analysis_report', {})
                        if report:
                            f.write("分析报告:\n")
                            f.write("-" * 20 + "\n")

                            summary = report.get('summary', {})
                            for key, value in summary.items():
                                f.write(f"{key}: {value}\n")

                self.show_info("导出成功", f"分析报告已保存到:\n{filename}")
                self.log_message(f"分析报告已导出: {filename}")

        except Exception as e:
            self.show_error("导出失败", str(e))
            self.log_message(f"导出报告失败: {e}", "error")

    def validate_inputs(self) -> bool:
        """验证输入"""
        video_path = self.video_path.get().strip()
        if not video_path:
            self.show_error("输入错误", "请选择视频文件")
            return False

        if not Path(video_path).exists():
            self.show_error("文件错误", "视频文件不存在")
            return False

        output_dir = self.output_dir.get().strip()
        if not output_dir:
            self.show_error("输入错误", "请选择输出目录")
            return False

        # 检查选择的分析类型
        selected_types = [name for name, var in self.analysis_types.items() if var.get()]
        if not selected_types:
            self.show_error("选择错误", "请至少选择一种分析类型")
            return False

        return True

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
