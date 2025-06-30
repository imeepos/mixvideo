#!/usr/bin/env python3
"""
智能镜头检测与分段系统 - GUI测试版本
用于测试Tab界面和批量处理功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import os
import threading
import time


class ShotDetectionGUITest:
    """智能镜头检测与分段系统 - 测试版GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 智能镜头检测与分段系统 - 测试版")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)
        
        # 核心变量
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.quality_mode = tk.StringVar(value="medium")

        # 批量处理变量
        self.batch_input_dir = tk.StringVar()
        self.batch_output_dir = tk.StringVar()
        self.batch_quality_mode = tk.StringVar(value="medium")
        self.batch_recursive = tk.BooleanVar(value=False)

        self.processing = False
        
        # 创建界面
        self.create_widgets()
        
        # 居中窗口
        self.center_window()

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
        title_label = ttk.Label(main_frame, text="🎬 智能镜头检测与分段系统", font=('Arial', 16, 'bold'))
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
        
        # 创建单个文件处理界面
        self.create_single_file_interface()
        
        # 创建批量处理界面
        self.create_batch_interface()
        
        # 创建共享的状态区域
        self.create_status_section(main_frame)

    def create_single_file_interface(self):
        """创建单个文件处理界面"""
        # 配置网格权重
        self.single_frame.columnconfigure(1, weight=1)
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(self.single_frame, text="📁 文件选择", padding="10")
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # 视频文件选择
        ttk.Label(file_frame, text="视频文件:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(file_frame, textvariable=self.video_path, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(file_frame, text="浏览", command=self.browse_video_file).grid(row=0, column=2)
        
        # 输出目录选择
        ttk.Label(file_frame, text="输出目录:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        ttk.Entry(file_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        ttk.Button(file_frame, text="浏览", command=self.browse_output_dir).grid(row=1, column=2, pady=(10, 0))

        # 设置区域
        settings_frame = ttk.LabelFrame(self.single_frame, text="⚙️ 处理设置", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(settings_frame, text="输出质量:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        quality_combo = ttk.Combobox(settings_frame, textvariable=self.quality_mode,
                                    values=["low", "medium", "high"], state="readonly", width=15)
        quality_combo.grid(row=0, column=1, sticky=tk.W)
        
        # 控制按钮
        button_frame = ttk.Frame(self.single_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15))
        
        self.start_button = ttk.Button(button_frame, text="🚀 开始处理", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)

    def create_batch_interface(self):
        """创建批量处理界面"""
        # 配置网格权重
        self.batch_frame.columnconfigure(1, weight=1)
        
        # 批量文件选择区域
        file_frame = ttk.LabelFrame(self.batch_frame, text="📁 批量文件选择", padding="10")
        file_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
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

        # 批量设置区域
        settings_frame = ttk.LabelFrame(self.batch_frame, text="⚙️ 批量处理设置", padding="10")
        settings_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(settings_frame, text="输出质量:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        batch_quality_combo = ttk.Combobox(settings_frame, textvariable=self.batch_quality_mode,
                                          values=["low", "medium", "high"], state="readonly", width=15)
        batch_quality_combo.grid(row=0, column=1, sticky=tk.W)

        # 批量控制按钮
        button_frame = ttk.Frame(self.batch_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15))
        
        self.batch_start_button = ttk.Button(button_frame, text="🚀 开始批量处理", command=self.start_batch_processing)
        self.batch_start_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.batch_stop_button = ttk.Button(button_frame, text="⏹️ 停止", command=self.stop_processing, state=tk.DISABLED)
        self.batch_stop_button.pack(side=tk.LEFT)

    def create_status_section(self, parent):
        """创建状态区域"""
        status_frame = ttk.LabelFrame(parent, text="📊 处理进度", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(2, weight=1)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # 进度百分比标签
        self.progress_percent_label = ttk.Label(status_frame, text="0%", font=('Arial', 10))
        self.progress_percent_label.grid(row=0, column=1, padx=(10, 0))

        # 状态标签
        self.status_label = ttk.Label(status_frame, text="就绪", font=('Arial', 10))
        self.status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))

        # 日志文本框（带滚动条）
        self.log_text = scrolledtext.ScrolledText(status_frame, height=6, wrap=tk.WORD)
        self.log_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

    # 文件浏览方法
    def browse_video_file(self):
        filename = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv"), ("所有文件", "*.*")]
        )
        if filename:
            self.video_path.set(filename)
            if not self.output_path.get():
                video_dir = Path(filename).parent
                video_name = Path(filename).stem
                default_output = video_dir / f"{video_name}_segments"
                self.output_path.set(str(default_output))

    def browse_output_dir(self):
        dirname = filedialog.askdirectory(title="选择输出目录")
        if dirname:
            self.output_path.set(dirname)

    def browse_batch_input_dir(self):
        dirname = filedialog.askdirectory(title="选择批量输入目录")
        if dirname:
            self.batch_input_dir.set(dirname)
            if not self.batch_output_dir.get():
                default_output = Path(dirname).parent / f"{Path(dirname).name}_batch_segments"
                self.batch_output_dir.set(str(default_output))

    def browse_batch_output_dir(self):
        dirname = filedialog.askdirectory(title="选择批量输出目录")
        if dirname:
            self.batch_output_dir.set(dirname)

    # 日志方法
    def log_message(self, message, level="INFO"):
        """添加日志消息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # 插入消息
        self.log_text.insert(tk.END, f"[{timestamp}] {level}: {message}\n")

        # 滚动到底部
        self.log_text.see(tk.END)

        # 更新界面
        self.root.update_idletasks()

    def update_progress(self, progress, description):
        """更新进度显示"""
        # 确保进度值在有效范围内
        progress_value = max(0, min(100, progress))
        self.progress_var.set(progress_value)
        self.progress_percent_label.config(text=f"{progress_value:.1f}%")
        self.status_label.config(text=description)
        self.root.update_idletasks()

    # 处理方法（测试版本）
    def start_processing(self):
        if not self.video_path.get():
            messagebox.showerror("错误", "请选择视频文件")
            return

        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.progress_percent_label.config(text="0%")

        self.log_message("开始处理单个文件...", "INFO")

        # 模拟处理进度
        self.simulate_single_processing()

    def start_batch_processing(self):
        if not self.batch_input_dir.get():
            messagebox.showerror("错误", "请选择批量输入目录")
            return

        self.processing = True
        self.batch_start_button.config(state=tk.DISABLED)
        self.batch_stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.progress_percent_label.config(text="0%")

        self.log_message("开始批量处理...", "INFO")
        self.log_message("找到 3 个视频文件", "INFO")

        # 模拟批量处理进度
        self.simulate_batch_processing()

    def simulate_single_processing(self):
        """模拟单个文件处理进度"""
        def progress_step(step):
            if not self.processing:
                return

            progress_steps = [
                (10, "初始化检测器..."),
                (25, "分析视频帧..."),
                (50, "检测镜头边界..."),
                (75, "生成视频分段..."),
                (90, "创建分析报告..."),
                (100, "处理完成")
            ]

            if step < len(progress_steps):
                progress, description = progress_steps[step]
                self.update_progress(progress, description)
                self.log_message(description, "INFO")

                if step < len(progress_steps) - 1:
                    self.root.after(500, lambda: progress_step(step + 1))
                else:
                    self.finish_processing()

        progress_step(0)

    def simulate_batch_processing(self):
        """模拟批量处理进度"""
        def progress_step(file_num, file_progress):
            if not self.processing:
                return

            files = ["video1.mp4", "video2.mp4", "video3.mp4"]
            total_files = len(files)

            if file_num <= total_files:
                # 计算总体进度
                overall_progress = ((file_num - 1) / total_files) * 100 + (file_progress / total_files)
                description = f"处理文件 {file_num}/{total_files}: {files[file_num-1]}"

                self.update_progress(overall_progress, description)

                if file_progress == 0:
                    self.log_message(f"开始处理 {files[file_num-1]}", "INFO")
                elif file_progress == 100:
                    self.log_message(f"✅ {files[file_num-1]} 处理完成", "SUCCESS")

                # 继续下一步
                if file_progress < 100:
                    next_progress = file_progress + 25
                    self.root.after(300, lambda: progress_step(file_num, next_progress))
                elif file_num < total_files:
                    self.root.after(300, lambda: progress_step(file_num + 1, 0))
                else:
                    self.log_message("批量处理完成！成功: 3, 失败: 0, 总计: 3", "SUCCESS")
                    self.finish_processing()

        progress_step(1, 0)

    def stop_processing(self):
        self.processing = False
        self.log_message("用户停止处理", "WARNING")
        self.finish_processing()

    def finish_processing(self):
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.batch_start_button.config(state=tk.NORMAL)
        self.batch_stop_button.config(state=tk.DISABLED)

        if self.progress_var.get() < 100:
            self.update_progress(100, "处理完成")

        messagebox.showinfo("完成", "处理完成！")


def main():
    """主函数"""
    root = tk.Tk()
    app = ShotDetectionGUITest(root)
    
    # 设置关闭事件
    def on_closing():
        if app.processing:
            if messagebox.askokcancel("退出", "正在处理中，确定要退出吗？"):
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动GUI
    root.mainloop()


if __name__ == "__main__":
    main()
