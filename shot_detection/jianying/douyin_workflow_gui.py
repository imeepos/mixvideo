#!/usr/bin/env python3
"""
抖音视频制作工作流程 - 独立GUI应用

这是一个独立的GUI应用，专门用于运行抖音视频制作的完整工作流程。
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading

# 确保当前目录在Python路径中
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

class DouyinWorkflowGUI:
    """抖音视频制作工作流程GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 抖音视频制作工作流程")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 设置样式
        self.setup_styles()
        
        # 变量
        self.douyin_work_dir = tk.StringVar()
        self.douyin_preview_mode = tk.BooleanVar(value=False)
        self.douyin_output_formats = tk.StringVar(value="json,html")
        
        self.create_interface()
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        
        # 配置样式
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Description.TLabel', font=('Arial', 10))
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
        style.configure('Action.TButton', font=('Arial', 10))
    
    def create_interface(self):
        """创建界面"""
        # 主框架（带滚动条）
        main_canvas = tk.Canvas(self.root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas, padding="20")
        
        # 配置滚动
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局Canvas和滚动条
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 标题
        title_label = ttk.Label(scrollable_frame, text="🎵 抖音视频制作完整工作流程", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # 说明
        desc_text = """🎬 4步自动化工作流程：

1️⃣ 扫描 resources/ 目录获取视频资源清单
2️⃣ 管理 templates/ 目录下的抖音项目模板  
3️⃣ 智能分配视频素材到模板中
4️⃣ 将生成的项目输出到 outputs/ 目录

📁 目录结构要求：
  your_project/
  ├── resources/          # 视频素材目录
  │   ├── 素材1/
  │   ├── 素材2/
  │   └── ...
  ├── templates/          # 抖音项目模板目录
  │   ├── 5个镜头/
  │   ├── 6个镜头/
  │   └── ...
  └── outputs/           # 输出目录 (自动创建)
      ├── 生成的项目1/
      ├── 生成的项目2/
      └── ..."""
        
        desc_label = ttk.Label(scrollable_frame, text=desc_text, style='Description.TLabel', justify=tk.LEFT)
        desc_label.pack(pady=(0, 20), anchor='w')
        
        # 工作目录选择
        dir_frame = ttk.LabelFrame(scrollable_frame, text="📁 工作目录设置", padding="15")
        dir_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(dir_frame, text="工作目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        dir_entry = ttk.Entry(dir_frame, textvariable=self.douyin_work_dir, width=60)
        dir_entry.grid(row=0, column=1, padx=(10, 5), pady=5, sticky=tk.EW)
        
        def select_work_directory():
            directory = filedialog.askdirectory(title="选择工作目录")
            if directory:
                self.douyin_work_dir.set(directory)
        
        ttk.Button(dir_frame, text="浏览", command=select_work_directory).grid(row=0, column=2, padx=5, pady=5)
        dir_frame.columnconfigure(1, weight=1)
        
        # 运行选项
        options_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ 运行选项", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 预览模式
        preview_check = ttk.Checkbutton(options_frame, text="预览模式 (只分析，不生成文件)", variable=self.douyin_preview_mode)
        preview_check.pack(anchor=tk.W, pady=5)
        
        # 输出格式选择
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill=tk.X, pady=5)
        ttk.Label(format_frame, text="资源清单格式:").pack(side=tk.LEFT)
        format_combo = ttk.Combobox(format_frame, textvariable=self.douyin_output_formats, 
                                   values=["json", "json,html", "json,csv", "json,html,csv", "json,html,markdown"], 
                                   state="readonly", width=25)
        format_combo.pack(side=tk.LEFT, padx=(10, 0))
        format_combo.set("json,html")
        
        # 操作按钮
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # 预览按钮
        preview_btn = ttk.Button(button_frame, text="🔍 预览分析", 
                               command=self.run_douyin_workflow_preview, style='Action.TButton')
        preview_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # 完整运行按钮
        run_btn = ttk.Button(button_frame, text="🚀 完整运行", 
                           command=self.run_douyin_workflow_full, style='Primary.TButton')
        run_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # 打开输出目录按钮
        open_btn = ttk.Button(button_frame, text="📁 打开输出目录", 
                            command=self.open_douyin_output_directory)
        open_btn.pack(side=tk.LEFT)
        
        # 状态显示
        status_frame = ttk.LabelFrame(scrollable_frame, text="📊 执行状态", padding="15")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.douyin_status_text = scrolledtext.ScrolledText(status_frame, height=15, wrap=tk.WORD, font=('Consolas', 9))
        self.douyin_status_text.pack(fill=tk.BOTH, expand=True)
        
        # 初始状态信息
        self.update_douyin_status("🎬 抖音视频制作工作流程已就绪")
        self.update_douyin_status("📋 请选择包含 resources/ 和 templates/ 目录的工作目录")
        self.update_douyin_status("💡 提示：可以先使用'预览分析'查看资源和模板统计信息")
        self.update_douyin_status("")
    
    def update_douyin_status(self, message):
        """更新状态"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.douyin_status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.douyin_status_text.see(tk.END)
        self.root.update_idletasks()
    
    def run_douyin_workflow_preview(self):
        """运行预览模式"""
        work_dir = self.douyin_work_dir.get().strip()
        if not work_dir:
            messagebox.showerror("错误", "请选择工作目录")
            return
        
        if not Path(work_dir).exists():
            messagebox.showerror("错误", "工作目录不存在")
            return
        
        # 检查必要的子目录
        resources_dir = Path(work_dir) / "resources"
        templates_dir = Path(work_dir) / "templates"
        
        if not resources_dir.exists():
            messagebox.showerror("错误", f"资源目录不存在: {resources_dir}\n\n请确保在工作目录下创建 resources/ 目录并放入视频素材")
            return
        
        if not templates_dir.exists():
            messagebox.showerror("错误", f"模板目录不存在: {templates_dir}\n\n请确保在工作目录下创建 templates/ 目录并放入抖音项目模板")
            return
        
        # 在后台线程中运行预览
        def run_preview():
            try:
                self.update_douyin_status("🔍 开始预览模式...")
                self.update_douyin_status(f"📁 工作目录: {work_dir}")
                
                # 导入工作流程模块
                from run_allocation import DouyinVideoWorkflow
                
                # 创建工作流程实例
                workflow = DouyinVideoWorkflow(work_dir)
                
                # 获取输出格式
                formats = self.douyin_output_formats.get().split(',')
                
                # 步骤1: 扫描资源
                self.update_douyin_status("1️⃣ 扫描resources获取资源清单...")
                inventory = workflow.step1_scan_resources(formats)
                if not inventory:
                    self.update_douyin_status("❌ 无法扫描资源")
                    return
                
                # 步骤2: 管理模板
                self.update_douyin_status("2️⃣ 管理抖音项目模板...")
                project_manager = workflow.step2_manage_templates()
                if not project_manager:
                    self.update_douyin_status("❌ 无法管理模板")
                    return
                
                # 显示预览信息
                stats = inventory['statistics']
                summary = project_manager.get_project_summary()
                
                self.update_douyin_status("")
                self.update_douyin_status("📊 资源统计:")
                self.update_douyin_status(f"  - 视频文件: {stats['video_count']} 个")
                self.update_douyin_status(f"  - 音频文件: {stats['audio_count']} 个")
                self.update_douyin_status(f"  - 图片文件: {stats['image_count']} 个")
                self.update_douyin_status(f"  - 总大小: {stats['total_size_mb']} MB")
                
                self.update_douyin_status("")
                self.update_douyin_status("📋 模板统计:")
                self.update_douyin_status(f"  - 有效模板: {summary['valid_projects']} 个")
                self.update_douyin_status(f"  - 无效模板: {summary['invalid_projects']} 个")
                
                if summary['valid_project_names']:
                    self.update_douyin_status("")
                    self.update_douyin_status("✅ 有效模板列表:")
                    for name in summary['valid_project_names']:
                        self.update_douyin_status(f"  - {name}")
                
                if summary['invalid_project_info']:
                    self.update_douyin_status("")
                    self.update_douyin_status("❌ 无效模板列表:")
                    for info in summary['invalid_project_info']:
                        self.update_douyin_status(f"  - {info['name']}: {info['error']}")
                
                self.update_douyin_status("")
                self.update_douyin_status("🔍 预览完成！如需实际生成视频项目，请点击'完整运行'")
                
            except Exception as e:
                self.update_douyin_status(f"❌ 预览失败: {e}")
                import traceback
                self.update_douyin_status(f"详细错误信息:")
                for line in traceback.format_exc().split('\n'):
                    if line.strip():
                        self.update_douyin_status(f"  {line}")
        
        # 在后台线程中运行
        threading.Thread(target=run_preview, daemon=True).start()
    
    def run_douyin_workflow_full(self):
        """运行完整工作流程"""
        work_dir = self.douyin_work_dir.get().strip()
        if not work_dir:
            messagebox.showerror("错误", "请选择工作目录")
            return
        
        if not Path(work_dir).exists():
            messagebox.showerror("错误", "工作目录不存在")
            return
        
        # 检查必要的子目录
        resources_dir = Path(work_dir) / "resources"
        templates_dir = Path(work_dir) / "templates"
        
        if not resources_dir.exists():
            messagebox.showerror("错误", f"资源目录不存在: {resources_dir}")
            return
        
        if not templates_dir.exists():
            messagebox.showerror("错误", f"模板目录不存在: {templates_dir}")
            return
        
        # 确认对话框
        if not messagebox.askyesno("确认运行", "确定要运行完整的抖音视频制作工作流程吗？\n\n这将：\n• 分析所有视频素材\n• 智能分配到模板中\n• 生成大量视频项目文件\n\n请确保有足够的磁盘空间。"):
            return
        
        # 在后台线程中运行完整工作流程
        def run_full_workflow():
            try:
                self.update_douyin_status("🚀 开始完整工作流程...")
                self.update_douyin_status(f"📁 工作目录: {work_dir}")
                
                # 导入工作流程模块
                from run_allocation import DouyinVideoWorkflow
                
                # 创建工作流程实例
                workflow = DouyinVideoWorkflow(work_dir)
                
                # 获取输出格式
                formats = self.douyin_output_formats.get().split(',')
                
                # 运行完整工作流程
                success = workflow.run_complete_workflow(formats)
                
                if success:
                    self.update_douyin_status("")
                    self.update_douyin_status("🎉 工作流程执行成功！")
                    self.update_douyin_status(f"📁 生成的项目保存在: {Path(work_dir) / 'outputs'}")
                    self.update_douyin_status("💡 可以点击'打开输出目录'查看结果")
                    
                    # 询问是否打开输出目录
                    def ask_open_output():
                        if messagebox.askyesno("完成", "🎉 工作流程执行成功！\n\n是否打开输出目录查看生成的项目？"):
                            self.open_douyin_output_directory()
                    
                    self.root.after(0, ask_open_output)
                else:
                    self.update_douyin_status("")
                    self.update_douyin_status("❌ 工作流程执行失败！请检查上面的错误信息")
                
            except Exception as e:
                self.update_douyin_status(f"❌ 执行失败: {e}")
                import traceback
                self.update_douyin_status(f"详细错误信息:")
                for line in traceback.format_exc().split('\n'):
                    if line.strip():
                        self.update_douyin_status(f"  {line}")
        
        # 在后台线程中运行
        threading.Thread(target=run_full_workflow, daemon=True).start()
    
    def open_douyin_output_directory(self):
        """打开输出目录"""
        work_dir = self.douyin_work_dir.get().strip()
        if not work_dir:
            messagebox.showwarning("警告", "请先选择工作目录")
            return
        
        output_dir = Path(work_dir) / "outputs"
        if not output_dir.exists():
            messagebox.showwarning("警告", "输出目录不存在，请先运行工作流程")
            return
        
        try:
            import subprocess
            import sys
            import os
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
    app = DouyinWorkflowGUI(root)
    
    # 设置关闭事件
    def on_closing():
        if messagebox.askokcancel("退出", "确定要退出抖音视频制作工作流程吗？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动GUI
    root.mainloop()


if __name__ == "__main__":
    main()
