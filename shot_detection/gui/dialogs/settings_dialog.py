"""
Settings Dialog
设置对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any


class SettingsDialog:
    """设置对话框"""
    
    def __init__(self, parent, config):
        """
        初始化设置对话框
        
        Args:
            parent: 父窗口
            config: 配置管理器
        """
        self.parent = parent
        self.config = config
        self.result = None
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("应用设置")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.center_dialog()
        
        # 创建界面
        self.setup_ui()
        
        # 加载当前设置
        self.load_settings()
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def center_dialog(self):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        
        # 获取对话框尺寸
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # 获取父窗口位置和尺寸
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # 计算居中位置
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建Notebook用于分类设置
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # 创建各个设置页面
        self.create_general_tab()
        self.create_detection_tab()
        self.create_processing_tab()
        self.create_gui_tab()
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # 按钮
        ttk.Button(button_frame, text="确定", command=self.apply_settings).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="取消", command=self.cancel_settings).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="应用", command=self.save_settings).pack(side=tk.RIGHT, padx=(0, 10))
        ttk.Button(button_frame, text="重置", command=self.reset_settings).pack(side=tk.LEFT)
    
    def create_general_tab(self):
        """创建常规设置页面"""
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="常规")
        
        # 应用设置
        app_group = ttk.LabelFrame(general_frame, text="应用设置", padding="10")
        app_group.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(app_group, text="应用名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.app_name_var = tk.StringVar()
        ttk.Entry(app_group, textvariable=self.app_name_var, width=30).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(app_group, text="日志级别:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.log_level_var = tk.StringVar()
        log_combo = ttk.Combobox(app_group, textvariable=self.log_level_var, 
                                values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly", width=27)
        log_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # 缓存设置
        cache_group = ttk.LabelFrame(general_frame, text="缓存设置", padding="10")
        cache_group.pack(fill=tk.X, pady=(0, 10))
        
        self.enable_cache_var = tk.BooleanVar()
        ttk.Checkbutton(cache_group, text="启用缓存", variable=self.enable_cache_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(cache_group, text="缓存大小限制(MB):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cache_size_var = tk.StringVar()
        ttk.Entry(cache_group, textvariable=self.cache_size_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
    
    def create_detection_tab(self):
        """创建检测设置页面"""
        detection_frame = ttk.Frame(self.notebook)
        self.notebook.add(detection_frame, text="检测")
        
        # 检测器设置
        detector_group = ttk.LabelFrame(detection_frame, text="检测器设置", padding="10")
        detector_group.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(detector_group, text="默认检测器:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.detector_type_var = tk.StringVar()
        detector_combo = ttk.Combobox(detector_group, textvariable=self.detector_type_var,
                                     values=["frame_difference", "histogram", "multi_detector"], 
                                     state="readonly", width=27)
        detector_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 帧差检测设置
        fd_group = ttk.LabelFrame(detection_frame, text="帧差检测设置", padding="10")
        fd_group.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(fd_group, text="阈值:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.fd_threshold_var = tk.StringVar()
        ttk.Entry(fd_group, textvariable=self.fd_threshold_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # 直方图检测设置
        hist_group = ttk.LabelFrame(detection_frame, text="直方图检测设置", padding="10")
        hist_group.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(hist_group, text="阈值:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.hist_threshold_var = tk.StringVar()
        ttk.Entry(hist_group, textvariable=self.hist_threshold_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(hist_group, text="直方图bins:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.hist_bins_var = tk.StringVar()
        ttk.Entry(hist_group, textvariable=self.hist_bins_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
    
    def create_processing_tab(self):
        """创建处理设置页面"""
        processing_frame = ttk.Frame(self.notebook)
        self.notebook.add(processing_frame, text="处理")
        
        # 输出设置
        output_group = ttk.LabelFrame(processing_frame, text="输出设置", padding="10")
        output_group.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_group, text="输出格式:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.output_format_var = tk.StringVar()
        format_combo = ttk.Combobox(output_group, textvariable=self.output_format_var,
                                   values=["mp4", "avi", "mov", "mkv"], state="readonly", width=27)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(output_group, text="输出质量:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_quality_var = tk.StringVar()
        quality_combo = ttk.Combobox(output_group, textvariable=self.output_quality_var,
                                    values=["low", "medium", "high", "ultra"], state="readonly", width=27)
        quality_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # 分割设置
        segment_group = ttk.LabelFrame(processing_frame, text="分割设置", padding="10")
        segment_group.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(segment_group, text="最小片段时长(秒):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.min_segment_var = tk.StringVar()
        ttk.Entry(segment_group, textvariable=self.min_segment_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(segment_group, text="最大片段时长(秒):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.max_segment_var = tk.StringVar()
        ttk.Entry(segment_group, textvariable=self.max_segment_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
    
    def create_gui_tab(self):
        """创建GUI设置页面"""
        gui_frame = ttk.Frame(self.notebook)
        self.notebook.add(gui_frame, text="界面")
        
        # 界面设置
        ui_group = ttk.LabelFrame(gui_frame, text="界面设置", padding="10")
        ui_group.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ui_group, text="主题:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.theme_var = tk.StringVar()
        theme_combo = ttk.Combobox(ui_group, textvariable=self.theme_var,
                                  values=["default", "clam", "alt", "classic"], state="readonly", width=27)
        theme_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(ui_group, text="字体大小:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.font_size_var = tk.StringVar()
        ttk.Entry(ui_group, textvariable=self.font_size_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))
        
        # 窗口设置
        window_group = ttk.LabelFrame(gui_frame, text="窗口设置", padding="10")
        window_group.pack(fill=tk.X, pady=(0, 10))
        
        self.remember_size_var = tk.BooleanVar()
        ttk.Checkbutton(window_group, text="记住窗口大小", variable=self.remember_size_var).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.remember_position_var = tk.BooleanVar()
        ttk.Checkbutton(window_group, text="记住窗口位置", variable=self.remember_position_var).grid(row=1, column=0, sticky=tk.W, pady=5)
    
    def load_settings(self):
        """加载当前设置"""
        try:
            # 常规设置
            self.app_name_var.set(self.config.get('app.name', 'Shot Detection'))
            self.log_level_var.set(self.config.get('app.log_level', 'INFO'))
            self.enable_cache_var.set(self.config.get('app.enable_cache', True))
            self.cache_size_var.set(str(self.config.get('app.cache_size_mb', 1000)))
            
            # 检测设置
            self.detector_type_var.set(self.config.get('detection.default_detector', 'multi_detector'))
            self.fd_threshold_var.set(str(self.config.get('detection.frame_difference.threshold', 0.3)))
            self.hist_threshold_var.set(str(self.config.get('detection.histogram.threshold', 0.5)))
            self.hist_bins_var.set(str(self.config.get('detection.histogram.bins', 256)))
            
            # 处理设置
            self.output_format_var.set(self.config.get('processing.output.format', 'mp4'))
            self.output_quality_var.set(self.config.get('processing.output.quality', 'high'))
            self.min_segment_var.set(str(self.config.get('processing.segmentation.min_segment_duration', 1.0)))
            self.max_segment_var.set(str(self.config.get('processing.segmentation.max_segment_duration', 300.0)))
            
            # GUI设置
            self.theme_var.set(self.config.get('gui.theme', 'default'))
            self.font_size_var.set(str(self.config.get('gui.font_size', 10)))
            self.remember_size_var.set(self.config.get('gui.remember_window_size', True))
            self.remember_position_var.set(self.config.get('gui.remember_window_position', True))
            
        except Exception as e:
            messagebox.showerror("加载失败", f"无法加载设置: {e}")
    
    def save_settings(self):
        """保存设置"""
        try:
            # 常规设置
            self.config.set('app.name', self.app_name_var.get())
            self.config.set('app.log_level', self.log_level_var.get())
            self.config.set('app.enable_cache', self.enable_cache_var.get())
            self.config.set('app.cache_size_mb', int(self.cache_size_var.get()))
            
            # 检测设置
            self.config.set('detection.default_detector', self.detector_type_var.get())
            self.config.set('detection.frame_difference.threshold', float(self.fd_threshold_var.get()))
            self.config.set('detection.histogram.threshold', float(self.hist_threshold_var.get()))
            self.config.set('detection.histogram.bins', int(self.hist_bins_var.get()))
            
            # 处理设置
            self.config.set('processing.output.format', self.output_format_var.get())
            self.config.set('processing.output.quality', self.output_quality_var.get())
            self.config.set('processing.segmentation.min_segment_duration', float(self.min_segment_var.get()))
            self.config.set('processing.segmentation.max_segment_duration', float(self.max_segment_var.get()))
            
            # GUI设置
            self.config.set('gui.theme', self.theme_var.get())
            self.config.set('gui.font_size', int(self.font_size_var.get()))
            self.config.set('gui.remember_window_size', self.remember_size_var.get())
            self.config.set('gui.remember_window_position', self.remember_position_var.get())
            
            # 保存配置文件
            self.config.save_config()
            
            messagebox.showinfo("保存成功", "设置已保存")
            
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存设置: {e}")
    
    def apply_settings(self):
        """应用设置并关闭对话框"""
        self.save_settings()
        self.result = True
        self.dialog.destroy()
    
    def cancel_settings(self):
        """取消设置"""
        self.result = False
        self.dialog.destroy()
    
    def reset_settings(self):
        """重置设置"""
        if messagebox.askyesno("确认重置", "确定要重置所有设置到默认值吗？"):
            try:
                self.config.reset_to_defaults()
                self.load_settings()
                messagebox.showinfo("重置成功", "设置已重置为默认值")
            except Exception as e:
                messagebox.showerror("重置失败", f"无法重置设置: {e}")
