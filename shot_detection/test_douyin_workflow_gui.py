#!/usr/bin/env python3
"""
测试抖音视频制作工作流程GUI集成
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading

# 添加jianying目录到路径
sys.path.insert(0, str(Path(__file__).parent / "jianying"))

class DouyinWorkflowTestGUI:
    """抖音视频制作工作流程测试GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎵 抖音视频制作工作流程 - 测试版")
        self.root.geometry("800x600")
        
        # 变量
        self.douyin_work_dir = tk.StringVar()
        self.douyin_preview_mode = tk.BooleanVar(value=False)
        self.douyin_output_formats = tk.StringVar(value="json,html")
        
        self.create_interface()
    
    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🎵 抖音视频制作完整工作流程", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 说明
        desc_text = """🎬 4步自动化工作流程：
1️⃣ 扫描 resources/ 目录获取视频资源清单
2️⃣ 管理 templates/ 目录下的抖音项目模板  
3️⃣ 智能分配视频素材到模板中
4️⃣ 将生成的项目输出到 outputs/ 目录

📁 目录结构要求：
  your_project/
  ├── resources/          # 视频素材目录
  ├── templates/          # 抖音项目模板目录
  └── outputs/           # 输出目录 (自动创建)"""
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=(0, 15), anchor='w')
        
        # 工作目录选择
        dir_frame = ttk.LabelFrame(main_frame, text="📁 工作目录设置", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(dir_frame, text="工作目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        dir_entry = ttk.Entry(dir_frame, textvariable=self.douyin_work_dir, width=50)
        dir_entry.grid(row=0, column=1, padx=(10, 5), pady=5, sticky=tk.EW)
        
        def select_work_directory():
            directory = filedialog.askdirectory(title="选择工作目录")
            if directory:
                self.douyin_work_dir.set(directory)
        
        ttk.Button(dir_frame, text="浏览", command=select_work_directory).grid(row=0, column=2, padx=5, pady=5)
        dir_frame.columnconfigure(1, weight=1)
        
        # 运行选项
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ 运行选项", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 预览模式
        preview_check = ttk.Checkbutton(options_frame, text="预览模式 (只分析，不生成文件)", variable=self.douyin_preview_mode)
        preview_check.pack(anchor=tk.W, pady=5)
        
        # 输出格式选择
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill=tk.X, pady=5)
        ttk.Label(format_frame, text="资源清单格式:").pack(side=tk.LEFT)
        format_combo = ttk.Combobox(format_frame, textvariable=self.douyin_output_formats, 
                                   values=["json", "json,html", "json,csv", "json,html,csv", "json,html,markdown"], 
                                   state="readonly", width=20)
        format_combo.pack(side=tk.LEFT, padx=(10, 0))
        format_combo.set("json,html")
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        # 预览按钮
        preview_btn = ttk.Button(button_frame, text="🔍 预览分析", command=self.run_douyin_workflow_preview)
        preview_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 完整运行按钮
        run_btn = ttk.Button(button_frame, text="🚀 完整运行", command=self.run_douyin_workflow_full)
        run_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 打开输出目录按钮
        open_btn = ttk.Button(button_frame, text="📁 打开输出目录", command=self.open_douyin_output_directory)
        open_btn.pack(side=tk.LEFT)
        
        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="📊 状态信息", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.douyin_status_text = scrolledtext.ScrolledText(status_frame, height=12, wrap=tk.WORD)
        self.douyin_status_text.pack(fill=tk.BOTH, expand=True)
        
        # 初始状态信息
        self.update_douyin_status("等待开始工作流程...")
        self.update_douyin_status("请选择包含 resources/ 和 templates/ 目录的工作目录")
    
    def update_douyin_status(self, message):
        """更新状态"""
        self.douyin_status_text.insert(tk.END, f"{message}\n")
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
            messagebox.showerror("错误", f"资源目录不存在: {resources_dir}\n请确保在工作目录下创建 resources/ 目录并放入视频素材")
            return
        
        if not templates_dir.exists():
            messagebox.showerror("错误", f"模板目录不存在: {templates_dir}\n请确保在工作目录下创建 templates/ 目录并放入抖音项目模板")
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
                
                self.update_douyin_status("\n📊 资源统计:")
                self.update_douyin_status(f"  - 视频文件: {stats['video_count']} 个")
                self.update_douyin_status(f"  - 音频文件: {stats['audio_count']} 个")
                self.update_douyin_status(f"  - 图片文件: {stats['image_count']} 个")
                self.update_douyin_status(f"  - 总大小: {stats['total_size_mb']} MB")
                
                self.update_douyin_status("\n📋 模板统计:")
                self.update_douyin_status(f"  - 有效模板: {summary['valid_projects']} 个")
                self.update_douyin_status(f"  - 无效模板: {summary['invalid_projects']} 个")
                
                if summary['valid_project_names']:
                    self.update_douyin_status("\n✅ 有效模板列表:")
                    for name in summary['valid_project_names']:
                        self.update_douyin_status(f"  - {name}")
                
                if summary['invalid_project_info']:
                    self.update_douyin_status("\n❌ 无效模板列表:")
                    for info in summary['invalid_project_info']:
                        self.update_douyin_status(f"  - {info['name']}: {info['error']}")
                
                self.update_douyin_status("\n🔍 预览完成！如需实际生成，请点击'完整运行'")
                
            except Exception as e:
                self.update_douyin_status(f"❌ 预览失败: {e}")
                import traceback
                self.update_douyin_status(f"详细错误: {traceback.format_exc()}")
        
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
        if not messagebox.askyesno("确认", "确定要运行完整的抖音视频制作工作流程吗？\n这将生成大量视频项目文件。"):
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
                    self.update_douyin_status("\n🎉 工作流程执行成功！")
                    self.update_douyin_status(f"📁 查看生成的项目: {Path(work_dir) / 'outputs'}")
                    
                    # 询问是否打开输出目录
                    def ask_open_output():
                        if messagebox.askyesno("完成", "工作流程执行成功！\n是否打开输出目录查看结果？"):
                            self.open_douyin_output_directory()
                    
                    self.root.after(0, ask_open_output)
                else:
                    self.update_douyin_status("\n❌ 工作流程执行失败！")
                
            except Exception as e:
                self.update_douyin_status(f"❌ 执行失败: {e}")
                import traceback
                self.update_douyin_status(f"详细错误: {traceback.format_exc()}")
        
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
            if sys.platform == "win32":
                import os
                os.startfile(str(output_dir))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(output_dir)], check=True)
            else:
                subprocess.run(["xdg-open", str(output_dir)], check=True)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开输出目录: {e}")


def main():
    root = tk.Tk()
    app = DouyinWorkflowTestGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
