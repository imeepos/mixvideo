#!/usr/bin/env python3
"""
测试进度和日志更新功能
验证GUI界面的实时更新是否正常工作
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from pathlib import Path
import threading
import time

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from video_processing_with_callbacks import process_video_with_gui_callbacks


class ProgressTestGUI:
    """进度测试GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📊 进度和日志更新测试")
        self.root.geometry("800x600")
        
        # 变量
        self.progress_var = tk.DoubleVar()
        self.processing = False
        
        # 创建界面
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="📊 进度和日志更新测试", 
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 控制区域
        control_frame = ttk.LabelFrame(main_frame, text="测试控制", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(button_frame, text="🚀 开始模拟处理", 
                                      command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.video_button = ttk.Button(button_frame, text="🎬 测试视频处理", 
                                      command=self.start_video_processing)
        self.video_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ 清除日志", 
                                      command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT)
        
        # 进度区域
        progress_frame = ttk.LabelFrame(main_frame, text="进度监控", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 进度条
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # 状态标签
        self.status_label = ttk.Label(progress_frame, text="就绪")
        self.status_label.pack()
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="实时日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
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
    
    def update_progress(self, progress: float, description: str):
        """更新进度（线程安全）"""
        def _update_gui():
            self.progress_var.set(progress)
            self.status_label.config(text=f"{progress:.1f}% - {description}")
            # 强制更新界面
            self.root.update_idletasks()
        
        # 确保在主线程中执行GUI更新
        if threading.current_thread() == threading.main_thread():
            _update_gui()
        else:
            self.root.after(0, _update_gui)
    
    def clear_log(self):
        """清除日志"""
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.status_label.config(text="就绪")
    
    def start_simulation(self):
        """开始模拟处理"""
        if self.processing:
            return
        
        self.processing = True
        self.start_button.config(state=tk.DISABLED)
        
        # 在新线程中运行模拟
        thread = threading.Thread(target=self.simulate_processing)
        thread.daemon = True
        thread.start()
    
    def simulate_processing(self):
        """模拟处理过程"""
        try:
            steps = [
                ("验证输入文件", 2),
                ("初始化检测器", 1),
                ("执行镜头检测", 5),
                ("生成分段信息", 1),
                ("切分视频文件", 8),
                ("生成项目文件", 1),
                ("生成分析报告", 2)
            ]
            
            self.log_message("🧪 开始模拟处理", "INFO")
            
            for i, (step_name, duration) in enumerate(steps):
                self.log_message(f"📋 步骤 {i+1}/7: {step_name}", "INFO")
                
                # 模拟步骤进度
                for j in range(duration * 10):
                    step_progress = (j / (duration * 10)) * 100
                    total_progress = (i / len(steps)) * 100 + step_progress / len(steps)
                    
                    self.update_progress(total_progress, f"{step_name}...")
                    time.sleep(0.1)
                
                self.log_message(f"✅ {step_name} 完成", "SUCCESS")
            
            self.update_progress(100, "模拟处理完成")
            self.log_message("🎉 模拟处理完成！", "SUCCESS")
            
        except Exception as e:
            self.log_message(f"❌ 模拟处理失败: {e}", "ERROR")
        finally:
            self.root.after(0, self.on_processing_complete)
    
    def start_video_processing(self):
        """开始真实视频处理"""
        if self.processing:
            return
        
        video_path = "test_video.mp4"
        if not os.path.exists(video_path):
            self.log_message(f"❌ 测试视频不存在: {video_path}", "ERROR")
            return
        
        self.processing = True
        self.video_button.config(state=tk.DISABLED)
        
        # 在新线程中运行视频处理
        thread = threading.Thread(target=self.process_video)
        thread.daemon = True
        thread.start()
    
    def process_video(self):
        """处理视频"""
        try:
            output_dir = "progress_test_output"
            
            self.log_message("🎬 开始真实视频处理", "INFO")
            
            success = process_video_with_gui_callbacks(
                "test_video.mp4",
                output_dir,
                "duration",
                "medium",
                progress_callback=self.update_progress,
                log_callback=self.log_message
            )
            
            if success:
                self.log_message("🎉 视频处理完成！", "SUCCESS")
            else:
                self.log_message("❌ 视频处理失败", "ERROR")
                
        except Exception as e:
            self.log_message(f"❌ 视频处理异常: {e}", "ERROR")
            import traceback
            self.log_message(f"详细错误: {traceback.format_exc()}", "ERROR")
        finally:
            self.root.after(0, self.on_video_processing_complete)
    
    def on_processing_complete(self):
        """模拟处理完成"""
        self.processing = False
        self.start_button.config(state=tk.NORMAL)
    
    def on_video_processing_complete(self):
        """视频处理完成"""
        self.processing = False
        self.video_button.config(state=tk.NORMAL)


def main():
    """主函数"""
    print("📊 启动进度和日志更新测试GUI...")
    
    root = tk.Tk()
    app = ProgressTestGUI(root)
    
    # 居中显示
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    print("✅ 进度测试GUI已启动")
    print("请测试以下功能:")
    print("• 模拟处理 - 测试进度条和日志更新")
    print("• 视频处理 - 测试真实的视频处理回调")
    print("• 清除日志 - 重置界面状态")
    
    root.mainloop()


if __name__ == "__main__":
    main()
