#!/usr/bin/env python3
"""
视频混剪GUI - 简洁版本

用户选择：素材目录、模板目录、输出目录
功能：预览、开始混剪、打开输出
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import tempfile
import shutil

# 确保当前目录在Python路径中
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

class VideoMixGUI:
    """视频混剪GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 视频混剪")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # 设置样式
        self.setup_styles()
        
        # 变量
        self.materials_dir = tk.StringVar()
        self.templates_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        self.create_interface()
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
    
    def create_interface(self):
        """创建界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🎬 视频混剪", style='Title.TLabel')
        title_label.pack(pady=(0, 30))
        
        # 目录选择区域
        dirs_frame = ttk.Frame(main_frame)
        dirs_frame.pack(fill=tk.X, pady=(0, 30))
        
        # 素材目录
        materials_frame = ttk.LabelFrame(dirs_frame, text="📹 素材目录", padding="15")
        materials_frame.pack(fill=tk.X, pady=(0, 15))
        
        materials_entry = ttk.Entry(materials_frame, textvariable=self.materials_dir, width=60)
        materials_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def select_materials_directory():
            directory = filedialog.askdirectory(title="选择素材目录")
            if directory:
                self.materials_dir.set(directory)
        
        ttk.Button(materials_frame, text="浏览", command=select_materials_directory).pack(side=tk.RIGHT)
        
        # 模板目录
        templates_frame = ttk.LabelFrame(dirs_frame, text="📋 模板目录", padding="15")
        templates_frame.pack(fill=tk.X, pady=(0, 15))
        
        templates_entry = ttk.Entry(templates_frame, textvariable=self.templates_dir, width=60)
        templates_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def select_templates_directory():
            directory = filedialog.askdirectory(title="选择模板目录")
            if directory:
                self.templates_dir.set(directory)
        
        ttk.Button(templates_frame, text="浏览", command=select_templates_directory).pack(side=tk.RIGHT)
        
        # 输出目录
        output_frame = ttk.LabelFrame(dirs_frame, text="📤 输出目录", padding="15")
        output_frame.pack(fill=tk.X, pady=(0, 15))
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=60)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        def select_output_directory():
            directory = filedialog.askdirectory(title="选择输出目录")
            if directory:
                self.output_dir.set(directory)
        
        ttk.Button(output_frame, text="浏览", command=select_output_directory).pack(side=tk.RIGHT)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # 预览按钮
        preview_btn = ttk.Button(button_frame, text="🔍 预览", command=self.run_preview)
        preview_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # 开始混剪按钮
        mix_btn = ttk.Button(button_frame, text="🚀 开始混剪", command=self.run_mix, style='Primary.TButton')
        mix_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        # 打开输出目录按钮
        open_btn = ttk.Button(button_frame, text="📁 打开输出", command=self.open_output)
        open_btn.pack(side=tk.LEFT)
        
        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="📊 状态", padding="15")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=12, wrap=tk.WORD, font=('Consolas', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # 初始状态
        self.update_status("等待选择目录...")
    
    def update_status(self, message):
        """更新状态"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def validate_directories(self):
        """验证目录"""
        materials_dir = self.materials_dir.get().strip()
        templates_dir = self.templates_dir.get().strip()
        output_dir = self.output_dir.get().strip()
        
        if not materials_dir:
            messagebox.showerror("错误", "请选择素材目录")
            return None
        
        if not templates_dir:
            messagebox.showerror("错误", "请选择模板目录")
            return None
        
        if not output_dir:
            messagebox.showerror("错误", "请选择输出目录")
            return None
        
        if not Path(materials_dir).exists():
            messagebox.showerror("错误", "素材目录不存在")
            return None
        
        if not Path(templates_dir).exists():
            messagebox.showerror("错误", "模板目录不存在")
            return None
        
        return materials_dir, templates_dir, output_dir
    
    def run_preview(self):
        """运行预览"""
        dirs = self.validate_directories()
        if not dirs:
            return
        
        materials_dir, templates_dir, output_dir = dirs
        
        def preview_task():
            try:
                self.update_status("🔍 开始预览...")
                self.update_status(f"📹 素材目录: {materials_dir}")
                self.update_status(f"📋 模板目录: {templates_dir}")
                self.update_status(f"📤 输出目录: {output_dir}")
                
                # 创建临时工作目录
                temp_work_dir = Path(tempfile.mkdtemp())
                temp_resources_dir = temp_work_dir / "resources"
                temp_templates_dir = temp_work_dir / "templates"
                temp_output_dir = temp_work_dir / "outputs"
                
                # 复制目录
                shutil.copytree(materials_dir, temp_resources_dir)
                shutil.copytree(templates_dir, temp_templates_dir)
                temp_output_dir.mkdir()
                
                # 导入工作流程模块
                from run_allocation import DouyinVideoWorkflow

                # 创建工作流程实例，传递原始素材目录
                workflow = DouyinVideoWorkflow(str(temp_work_dir), str(materials_dir))
                
                # 扫描资源
                self.update_status("1️⃣ 扫描素材...")
                inventory = workflow.step1_scan_resources(['json'])
                if not inventory:
                    self.update_status("❌ 无法扫描素材")
                    return
                
                # 分析模板
                self.update_status("2️⃣ 分析模板...")
                project_manager = workflow.step2_manage_templates()
                if not project_manager:
                    self.update_status("❌ 无法分析模板")
                    return
                
                # 显示统计信息
                stats = inventory['statistics']
                summary = project_manager.get_project_summary()
                
                self.update_status("")
                self.update_status("📊 素材统计:")
                self.update_status(f"  视频: {stats['video_count']} 个")
                self.update_status(f"  音频: {stats['audio_count']} 个")
                self.update_status(f"  图片: {stats['image_count']} 个")
                self.update_status(f"  总大小: {stats['total_size_mb']} MB")
                
                self.update_status("")
                self.update_status("📋 模板统计:")
                self.update_status(f"  有效模板: {summary['valid_projects']} 个")
                self.update_status(f"  无效模板: {summary['invalid_projects']} 个")
                
                if summary['valid_project_names']:
                    self.update_status("")
                    self.update_status("✅ 可用模板:")
                    for name in summary['valid_project_names']:
                        self.update_status(f"  - {name}")
                
                self.update_status("")
                self.update_status("🔍 预览完成！")
                
            except Exception as e:
                self.update_status(f"❌ 预览失败: {e}")
            finally:
                # 清理临时目录
                try:
                    shutil.rmtree(temp_work_dir)
                except:
                    pass
        
        threading.Thread(target=preview_task, daemon=True).start()
    
    def run_mix(self):
        """运行混剪"""
        dirs = self.validate_directories()
        if not dirs:
            return
        
        materials_dir, templates_dir, output_dir = dirs
        
        # 确认对话框
        if not messagebox.askyesno("确认", "确定要开始视频混剪吗？\n这将生成大量视频项目文件。"):
            return
        
        def mix_task():
            try:
                self.update_status("🚀 开始视频混剪...")
                self.update_status(f"📹 素材目录: {materials_dir}")
                self.update_status(f"📋 模板目录: {templates_dir}")
                self.update_status(f"📤 输出目录: {output_dir}")
                
                # 创建临时工作目录
                temp_work_dir = Path(tempfile.mkdtemp())
                temp_resources_dir = temp_work_dir / "resources"
                temp_templates_dir = temp_work_dir / "templates"
                temp_output_dir = temp_work_dir / "outputs"
                
                # 复制目录
                shutil.copytree(materials_dir, temp_resources_dir)
                shutil.copytree(templates_dir, temp_templates_dir)
                temp_output_dir.mkdir()
                
                # 导入工作流程模块
                from run_allocation import DouyinVideoWorkflow

                # 创建工作流程实例，传递原始素材目录
                workflow = DouyinVideoWorkflow(str(temp_work_dir), str(materials_dir))
                
                # 运行完整工作流程
                success = workflow.run_complete_workflow(['json'])
                
                if success:
                    # 复制结果到用户指定的输出目录
                    self.update_status("📁 复制结果到输出目录...")
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
                    
                    self.update_status("")
                    self.update_status("🎉 视频混剪完成！")
                    self.update_status(f"📁 结果保存在: {output_dir}")
                    
                    # 询问是否打开输出目录
                    def ask_open():
                        if messagebox.askyesno("完成", "视频混剪完成！\n是否打开输出目录查看结果？"):
                            self.open_output()
                    
                    self.root.after(0, ask_open)
                else:
                    self.update_status("")
                    self.update_status("❌ 视频混剪失败！")
                
            except Exception as e:
                self.update_status(f"❌ 执行失败: {e}")
                import traceback
                for line in traceback.format_exc().split('\n'):
                    if line.strip():
                        self.update_status(f"  {line}")
            finally:
                # 清理临时目录
                try:
                    shutil.rmtree(temp_work_dir)
                except:
                    pass
        
        threading.Thread(target=mix_task, daemon=True).start()
    
    def open_output(self):
        """打开输出目录"""
        output_dir = self.output_dir.get().strip()
        if not output_dir:
            messagebox.showwarning("警告", "请先选择输出目录")
            return
        
        if not Path(output_dir).exists():
            messagebox.showwarning("警告", "输出目录不存在，请先运行视频混剪")
            return
        
        try:
            import subprocess
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
    app = VideoMixGUI(root)
    
    # 设置关闭事件
    def on_closing():
        if messagebox.askokcancel("退出", "确定要退出视频混剪吗？"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动GUI
    root.mainloop()


if __name__ == "__main__":
    main()
