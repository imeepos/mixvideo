#!/usr/bin/env python3
"""
剪映项目管理GUI

提供图形界面来管理剪映项目，包括：
1. 扫描和显示项目列表
2. 查看项目详情
3. 创建新项目
4. 管理项目文件
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
from pathlib import Path
import threading
import logging

# 导入剪映管理器
from jianying.jianying_project_manager import JianyingProjectManager


class JianyingManagerGUI:
    """剪映项目管理GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("剪映项目管理器")
        self.root.geometry("1200x800")
        
        # 初始化变量
        self.manager = None
        self.current_directory = tk.StringVar()
        
        # 设置日志
        self.setup_logging()
        
        # 创建界面
        self.create_widgets()
        
        # 绑定事件
        self.bind_events()
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(main_frame, text="项目目录", padding="5")
        dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="目录:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.current_directory, width=60)
        self.dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dir_frame, text="浏览", command=self.browse_directory).grid(row=0, column=2)
        ttk.Button(dir_frame, text="扫描", command=self.scan_projects).grid(row=0, column=3, padx=(5, 0))
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(control_frame, text="创建新项目", command=self.create_new_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="刷新列表", command=self.refresh_projects).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="导出摘要", command=self.export_summary).pack(side=tk.LEFT, padx=(0, 5))
        
        # 主内容区域 - 使用Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 项目列表标签页
        self.create_projects_tab()
        
        # 项目详情标签页
        self.create_details_tab()
        
        # 日志标签页
        self.create_log_tab()
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def create_projects_tab(self):
        """创建项目列表标签页"""
        projects_frame = ttk.Frame(self.notebook)
        self.notebook.add(projects_frame, text="项目列表")
        
        # 配置网格
        projects_frame.columnconfigure(0, weight=1)
        projects_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ("名称", "状态", "路径", "错误信息")
        self.projects_tree = ttk.Treeview(projects_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        for col in columns:
            self.projects_tree.heading(col, text=col)
            self.projects_tree.column(col, width=200)
        
        # 调整列宽
        self.projects_tree.column("名称", width=200)
        self.projects_tree.column("状态", width=80)
        self.projects_tree.column("路径", width=300)
        self.projects_tree.column("错误信息", width=300)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(projects_frame, orient=tk.VERTICAL, command=self.projects_tree.yview)
        self.projects_tree.configure(yscrollcommand=tree_scroll.set)
        
        # 布局
        self.projects_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 右键菜单
        self.create_context_menu()
    
    def create_details_tab(self):
        """创建项目详情标签页"""
        details_frame = ttk.Frame(self.notebook)
        self.notebook.add(details_frame, text="项目详情")
        
        # 配置网格
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(1, weight=1)
        
        # 项目选择
        select_frame = ttk.Frame(details_frame)
        select_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        select_frame.columnconfigure(1, weight=1)
        
        ttk.Label(select_frame, text="选择项目:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.project_combo = ttk.Combobox(select_frame, state="readonly")
        self.project_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.project_combo.bind("<<ComboboxSelected>>", self.on_project_selected)
        
        ttk.Button(select_frame, text="查看详情", command=self.show_project_details).grid(row=0, column=2)
        
        # 详情显示区域
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, height=20)
        self.details_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_log_tab(self):
        """创建日志标签页"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="日志")
        
        # 配置网格
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志显示区域
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=20)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志控制按钮
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(log_control_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT)
        ttk.Button(log_control_frame, text="保存日志", command=self.save_log).pack(side=tk.LEFT, padx=(5, 0))
    
    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="查看详情", command=self.view_selected_project)
        self.context_menu.add_command(label="打开目录", command=self.open_project_directory)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="删除项目", command=self.delete_selected_project)
        
        # 绑定右键事件
        self.projects_tree.bind("<Button-3>", self.show_context_menu)
    
    def bind_events(self):
        """绑定事件"""
        # 双击查看详情
        self.projects_tree.bind("<Double-1>", lambda e: self.view_selected_project())
    
    def browse_directory(self):
        """浏览目录"""
        directory = filedialog.askdirectory(title="选择剪映项目目录")
        if directory:
            self.current_directory.set(directory)
    
    def scan_projects(self):
        """扫描项目"""
        directory = self.current_directory.get()
        if not directory:
            messagebox.showerror("错误", "请先选择项目目录")
            return
        
        if not os.path.exists(directory):
            messagebox.showerror("错误", "目录不存在")
            return
        
        # 在后台线程中扫描
        def scan_thread():
            try:
                self.status_var.set("正在扫描项目...")
                self.manager = JianyingProjectManager(directory)
                projects = self.manager.scan_projects()
                
                # 在主线程中更新界面
                self.root.after(0, lambda: self.update_projects_list(projects))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("错误", f"扫描失败: {e}"))
                self.root.after(0, lambda: self.status_var.set("扫描失败"))
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def update_projects_list(self, projects):
        """更新项目列表"""
        # 清空现有项目
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
        
        # 添加项目
        for project in projects:
            status = "有效" if project.is_valid else "无效"
            error_msg = project.error_message if not project.is_valid else ""
            
            self.projects_tree.insert("", tk.END, values=(
                project.name,
                status,
                str(project.path),
                error_msg
            ))
        
        # 更新项目下拉列表
        valid_projects = [p.name for p in projects if p.is_valid]
        self.project_combo['values'] = valid_projects
        
        # 更新状态
        valid_count = len([p for p in projects if p.is_valid])
        self.status_var.set(f"扫描完成: 发现 {len(projects)} 个项目，{valid_count} 个有效")
        
        # 记录日志
        self.log_message(f"扫描完成: {len(projects)} 个项目，{valid_count} 个有效")
    
    def refresh_projects(self):
        """刷新项目列表"""
        if self.manager:
            self.scan_projects()
        else:
            messagebox.showwarning("警告", "请先扫描项目目录")
    
    def create_new_project(self):
        """创建新项目"""
        if not self.manager:
            messagebox.showerror("错误", "请先扫描项目目录")
            return
        
        # 弹出对话框获取项目名称
        import tkinter.simpledialog
        project_name = tkinter.simpledialog.askstring("创建项目", "请输入项目名称:")
        if not project_name:
            return
        
        # 验证项目名称
        if not project_name.strip():
            messagebox.showerror("错误", "项目名称不能为空")
            return
        
        # 创建项目
        try:
            if self.manager.create_new_project(project_name.strip()):
                messagebox.showinfo("成功", f"项目 '{project_name}' 创建成功")
                self.refresh_projects()
            else:
                messagebox.showerror("错误", "项目创建失败")
        except Exception as e:
            messagebox.showerror("错误", f"创建项目时出错: {e}")
    
    def view_selected_project(self):
        """查看选中的项目"""
        selection = self.projects_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        item = self.projects_tree.item(selection[0])
        project_name = item['values'][0]
        
        # 切换到详情标签页并显示项目
        self.notebook.select(1)  # 选择详情标签页
        self.project_combo.set(project_name)
        self.show_project_details()
    
    def show_project_details(self):
        """显示项目详情"""
        project_name = self.project_combo.get()
        if not project_name or not self.manager:
            return
        
        project = self.manager.get_project(project_name)
        if not project:
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, "项目不存在")
            return
        
        # 获取项目详细信息
        details = self.get_project_details(project)
        
        # 显示详情
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, details)
    
    def get_project_details(self, project):
        """获取项目详细信息"""
        details = f"项目名称: {project.name}\n"
        details += f"项目路径: {project.path}\n"
        details += f"状态: {'有效' if project.is_valid else '无效'}\n"
        
        if not project.is_valid:
            details += f"错误信息: {project.error_message}\n"
            return details
        
        details += "\n=== 文件信息 ===\n"
        
        # 检查文件大小
        for file_path, name in [
            (project.draft_content_path, "draft_content.json"),
            (project.draft_meta_info_path, "draft_meta_info.json"),
            (project.draft_virtual_store_path, "draft_virtual_store.json")
        ]:
            if file_path.exists():
                size = file_path.stat().st_size
                details += f"{name}: {size:,} 字节\n"
            else:
                details += f"{name}: 文件不存在\n"
        
        # 尝试获取更多信息
        try:
            content_mgr = self.manager.get_project_content_manager(project.name)
            meta_mgr = self.manager.get_project_meta_manager(project.name)
            
            if content_mgr:
                details += "\n=== 内容信息 ===\n"
                content_info = content_mgr.get_project_info()
                details += f"时长: {content_info.get('duration', 0) / 1000000:.2f} 秒\n"
                details += f"轨道数: {len(content_info.get('tracks', []))}\n"
                details += f"素材数: {len(content_info.get('materials', []))}\n"
            
            if meta_mgr:
                details += "\n=== 元数据信息 ===\n"
                meta_info = meta_mgr.get_project_info()
                details += f"创建时间: {meta_info.get('create_time', 'N/A')}\n"
                details += f"修改时间: {meta_info.get('update_time', 'N/A')}\n"
                
                materials = meta_mgr.get_all_materials()
                details += f"素材总数: {len(materials)}\n"
                
                # 按类型统计素材
                material_types = {}
                for material in materials:
                    mat_type = material.get('metetype', 'unknown')
                    material_types[mat_type] = material_types.get(mat_type, 0) + 1
                
                for mat_type, count in material_types.items():
                    details += f"  {mat_type}: {count} 个\n"
        
        except Exception as e:
            details += f"\n获取详细信息时出错: {e}\n"
        
        return details
    
    def on_project_selected(self, event):
        """项目选择事件"""
        # 可以在这里添加自动显示详情的逻辑
        pass
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 选择右键点击的项目
        item = self.projects_tree.identify_row(event.y)
        if item:
            self.projects_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def open_project_directory(self):
        """打开项目目录"""
        selection = self.projects_tree.selection()
        if not selection:
            return
        
        item = self.projects_tree.item(selection[0])
        project_path = item['values'][2]
        
        try:
            import subprocess
            import sys
            
            if sys.platform == "win32":
                os.startfile(project_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", project_path])
            else:
                subprocess.run(["xdg-open", project_path])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开目录: {e}")
    
    def delete_selected_project(self):
        """删除选中的项目"""
        selection = self.projects_tree.selection()
        if not selection:
            return
        
        item = self.projects_tree.item(selection[0])
        project_name = item['values'][0]
        
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除项目 '{project_name}' 吗？\n\n这将永久删除项目文件夹及其所有内容！"):
            try:
                if self.manager.delete_project(project_name):
                    messagebox.showinfo("成功", f"项目 '{project_name}' 已删除")
                    self.refresh_projects()
                else:
                    messagebox.showerror("错误", "删除项目失败")
            except Exception as e:
                messagebox.showerror("错误", f"删除项目时出错: {e}")
    
    def export_summary(self):
        """导出项目摘要"""
        if not self.manager:
            messagebox.showerror("错误", "请先扫描项目目录")
            return
        
        # 选择保存文件
        file_path = filedialog.asksaveasfilename(
            title="保存项目摘要",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                summary = self.manager.get_project_summary()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", f"项目摘要已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存摘要失败: {e}")
    
    def log_message(self, message):
        """记录日志消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """保存日志"""
        file_path = filedialog.asksaveasfilename(
            title="保存日志",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("成功", f"日志已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存日志失败: {e}")


def main():
    """主函数"""
    root = tk.Tk()
    app = JianyingManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
