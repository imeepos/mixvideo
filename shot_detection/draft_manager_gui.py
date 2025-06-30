#!/usr/bin/env python3
"""
剪映草稿管理器GUI

用于测试和管理剪映项目的图形界面，支持：
- 新建草稿项目
- 添加视频、音频、图片素材
- 查看和编辑素材信息
- 保存和加载项目
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
from pathlib import Path
import json

# 添加jianying目录到路径
sys.path.append(str(Path(__file__).parent / "jianying"))

try:
    from jianying.draft_meta_manager import DraftMetaManager, MaterialInfo
except ImportError:
    # 如果导入失败，尝试直接导入
    try:
        from draft_meta_manager import DraftMetaManager, MaterialInfo
    except ImportError:
        print("错误: 无法导入 draft_meta_manager")
        sys.exit(1)


class DraftManagerGUI:
    """剪映草稿管理器GUI主类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("剪映草稿管理器")
        self.root.geometry("1000x700")
        
        # 当前项目管理器
        self.current_manager = None
        self.current_project_path = None
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 项目管理区域
        self.create_project_section(main_frame)
        
        # 素材管理区域
        self.create_material_section(main_frame)
        
        # 信息显示区域
        self.create_info_section(main_frame)
        
    def create_project_section(self, parent):
        """创建项目管理区域"""
        project_frame = ttk.LabelFrame(parent, text="项目管理", padding="5")
        project_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 项目路径
        ttk.Label(project_frame, text="项目路径:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.project_path_var = tk.StringVar()
        self.project_path_entry = ttk.Entry(project_frame, textvariable=self.project_path_var, width=50)
        self.project_path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # 按钮
        ttk.Button(project_frame, text="选择目录", command=self.select_project_directory).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(project_frame, text="新建项目", command=self.create_new_project).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(project_frame, text="加载项目", command=self.load_project).grid(row=0, column=4, padx=(0, 5))
        ttk.Button(project_frame, text="保存项目", command=self.save_project).grid(row=0, column=5)
        
        # 配置网格权重
        project_frame.columnconfigure(1, weight=1)
        
        # 项目信息显示
        info_frame = ttk.Frame(project_frame)
        info_frame.grid(row=1, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.project_info_text = tk.Text(info_frame, height=3, wrap=tk.WORD)
        self.project_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.project_info_text.yview)
        info_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.project_info_text.configure(yscrollcommand=info_scrollbar.set)
        
        info_frame.columnconfigure(0, weight=1)
        
    def create_material_section(self, parent):
        """创建素材管理区域"""
        material_frame = ttk.LabelFrame(parent, text="素材管理", padding="5")
        material_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 添加素材按钮
        button_frame = ttk.Frame(material_frame)
        button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="添加视频", command=lambda: self.add_material("video")).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="添加音频", command=lambda: self.add_material("audio")).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="添加图片", command=lambda: self.add_material("image")).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(button_frame, text="批量添加", command=self.batch_add_materials).grid(row=0, column=3, padx=(0, 5))
        ttk.Button(button_frame, text="删除选中", command=self.remove_selected_material).grid(row=0, column=4, padx=(0, 5))
        ttk.Button(button_frame, text="刷新列表", command=self.refresh_material_list).grid(row=0, column=5)
        
        # 素材列表
        list_frame = ttk.Frame(material_frame)
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建Treeview
        columns = ("类型", "文件名", "尺寸", "时长", "路径")
        self.material_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        # 设置列标题
        for col in columns:
            self.material_tree.heading(col, text=col)
            
        # 设置列宽
        self.material_tree.column("类型", width=60)
        self.material_tree.column("文件名", width=150)
        self.material_tree.column("尺寸", width=100)
        self.material_tree.column("时长", width=80)
        self.material_tree.column("路径", width=300)
        
        self.material_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        tree_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.material_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.material_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # 配置网格权重
        material_frame.columnconfigure(0, weight=1)
        material_frame.rowconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 绑定双击事件
        self.material_tree.bind("<Double-1>", self.on_material_double_click)
        
    def create_info_section(self, parent):
        """创建信息显示区域"""
        info_frame = ttk.LabelFrame(parent, text="详细信息", padding="5")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建滚动文本框
        self.info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, height=15)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        
    def select_project_directory(self):
        """选择项目目录"""
        directory = filedialog.askdirectory(title="选择项目目录")
        if directory:
            self.project_path_var.set(directory)
            
    def create_new_project(self):
        """创建新项目"""
        project_path = self.project_path_var.get().strip()
        if not project_path:
            messagebox.showerror("错误", "请先选择或输入项目路径")
            return
            
        try:
            # 创建项目目录
            project_dir = Path(project_path)
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建管理器
            self.current_manager = DraftMetaManager(project_dir)
            self.current_project_path = project_dir
            
            # 创建默认元数据
            meta_data = self.current_manager.load_meta_data()
            
            # 更新界面
            self.update_project_info()
            self.refresh_material_list()
            
            self.log_info(f"成功创建新项目: {project_path}")
            messagebox.showinfo("成功", f"项目创建成功: {project_dir.name}")
            
        except Exception as e:
            self.log_error(f"创建项目失败: {e}")
            messagebox.showerror("错误", f"创建项目失败: {e}")
            
    def load_project(self):
        """加载现有项目"""
        project_path = self.project_path_var.get().strip()
        if not project_path:
            messagebox.showerror("错误", "请先选择项目路径")
            return
            
        try:
            project_dir = Path(project_path)
            if not project_dir.exists():
                messagebox.showerror("错误", "项目目录不存在")
                return
                
            # 创建管理器并加载
            self.current_manager = DraftMetaManager(project_dir)
            self.current_project_path = project_dir
            
            meta_data = self.current_manager.load_meta_data()
            
            # 更新界面
            self.update_project_info()
            self.refresh_material_list()
            
            self.log_info(f"成功加载项目: {project_path}")
            messagebox.showinfo("成功", f"项目加载成功: {project_dir.name}")
            
        except Exception as e:
            self.log_error(f"加载项目失败: {e}")
            messagebox.showerror("错误", f"加载项目失败: {e}")
            
    def save_project(self):
        """保存项目"""
        if not self.current_manager:
            messagebox.showerror("错误", "没有打开的项目")
            return
            
        try:
            success = self.current_manager.save_meta_data()
            if success:
                self.log_info("项目保存成功")
                messagebox.showinfo("成功", "项目保存成功")
            else:
                messagebox.showerror("错误", "项目保存失败")
                
        except Exception as e:
            self.log_error(f"保存项目失败: {e}")
            messagebox.showerror("错误", f"保存项目失败: {e}")
            
    def add_material(self, material_type):
        """添加素材"""
        if not self.current_manager:
            messagebox.showerror("错误", "请先创建或加载项目")
            return
            
        # 文件类型过滤器
        filetypes = {
            "video": [("视频文件", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"), ("所有文件", "*.*")],
            "audio": [("音频文件", "*.mp3 *.wav *.aac *.flac *.ogg"), ("所有文件", "*.*")],
            "image": [("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"), ("所有文件", "*.*")]
        }
        
        file_path = filedialog.askopenfilename(
            title=f"选择{material_type}文件",
            filetypes=filetypes.get(material_type, [("所有文件", "*.*")])
        )
        
        if file_path:
            self.add_material_file(file_path, material_type)
            
    def add_material_file(self, file_path, material_type):
        """添加单个素材文件"""
        try:
            file_path_obj = Path(file_path)
            
            # 创建素材信息
            material = MaterialInfo(
                file_path=str(file_path_obj),
                name=file_path_obj.name,
                material_type=material_type
            )
            
            # 添加到项目
            material_id = self.current_manager.add_material(material)
            
            # 刷新列表
            self.refresh_material_list()
            
            self.log_info(f"成功添加{material_type}素材: {file_path_obj.name}")
            
        except Exception as e:
            self.log_error(f"添加素材失败: {e}")
            messagebox.showerror("错误", f"添加素材失败: {e}")
            
    def batch_add_materials(self):
        """批量添加素材"""
        if not self.current_manager:
            messagebox.showerror("错误", "请先创建或加载项目")
            return
            
        file_paths = filedialog.askopenfilenames(
            title="批量选择素材文件",
            filetypes=[
                ("媒体文件", "*.mp4 *.avi *.mov *.mp3 *.wav *.jpg *.png"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_paths:
            success_count = 0
            for file_path in file_paths:
                try:
                    # 根据文件扩展名判断类型
                    ext = Path(file_path).suffix.lower()
                    if ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']:
                        material_type = "video"
                    elif ext in ['.mp3', '.wav', '.aac', '.flac', '.ogg']:
                        material_type = "audio"
                    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                        material_type = "image"
                    else:
                        material_type = "video"  # 默认为视频
                        
                    self.add_material_file(file_path, material_type)
                    success_count += 1
                    
                except Exception as e:
                    self.log_error(f"添加文件失败 {file_path}: {e}")
                    
            messagebox.showinfo("完成", f"批量添加完成，成功添加 {success_count} 个文件")
            
    def remove_selected_material(self):
        """删除选中的素材"""
        if not self.current_manager:
            messagebox.showerror("错误", "没有打开的项目")
            return
            
        selected_items = self.material_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的素材")
            return
            
        if messagebox.askyesno("确认", f"确定要删除选中的 {len(selected_items)} 个素材吗？"):
            for item in selected_items:
                try:
                    # 获取素材ID（存储在item的tags中）
                    material_id = self.material_tree.item(item)['tags'][0] if self.material_tree.item(item)['tags'] else None
                    if material_id:
                        self.current_manager.remove_material(material_id)
                        
                except Exception as e:
                    self.log_error(f"删除素材失败: {e}")
                    
            self.refresh_material_list()
            self.log_info(f"删除了 {len(selected_items)} 个素材")
            
    def refresh_material_list(self):
        """刷新素材列表"""
        # 清空现有项目
        for item in self.material_tree.get_children():
            self.material_tree.delete(item)
            
        if not self.current_manager:
            return
            
        try:
            # 获取所有类型的素材
            material_types = ["video", "audio", "image", "text", "other"]
            
            for material_type in material_types:
                materials = self.current_manager.get_materials_by_type(material_type)
                
                for material in materials:
                    # 格式化显示信息
                    file_name = material.get('extra_info', 'N/A')
                    
                    # 尺寸信息
                    width = material.get('width', 0)
                    height = material.get('height', 0)
                    size_str = f"{width}x{height}" if width and height else "N/A"
                    
                    # 时长信息
                    duration = material.get('duration', 0)
                    duration_str = f"{duration/1000000:.2f}s" if duration > 0 else "N/A"
                    
                    # 文件路径
                    file_path = material.get('file_Path', 'N/A')
                    
                    # 插入到树形视图
                    item = self.material_tree.insert('', 'end', values=(
                        material_type,
                        file_name,
                        size_str,
                        duration_str,
                        file_path
                    ), tags=(material.get('id', ''),))
                    
        except Exception as e:
            self.log_error(f"刷新素材列表失败: {e}")
            
    def on_material_double_click(self, event):
        """素材双击事件"""
        selected_item = self.material_tree.selection()[0] if self.material_tree.selection() else None
        if selected_item:
            # 获取素材ID
            material_id = self.material_tree.item(selected_item)['tags'][0] if self.material_tree.item(selected_item)['tags'] else None
            if material_id:
                self.show_material_details(material_id)
                
    def show_material_details(self, material_id):
        """显示素材详细信息"""
        if not self.current_manager:
            return
            
        try:
            # 查找素材
            material_types = ["video", "audio", "image", "text", "other"]
            found_material = None
            
            for material_type in material_types:
                materials = self.current_manager.get_materials_by_type(material_type)
                for material in materials:
                    if material.get('id') == material_id:
                        found_material = material
                        break
                if found_material:
                    break
                    
            if found_material:
                # 格式化显示详细信息
                details = "素材详细信息:\n"
                details += "=" * 50 + "\n"
                
                for key, value in found_material.items():
                    if key == 'duration' and isinstance(value, int):
                        details += f"{key}: {value} 微秒 ({value/1000000:.2f} 秒)\n"
                    elif key in ['create_time', 'import_time']:
                        import datetime
                        dt = datetime.datetime.fromtimestamp(value)
                        details += f"{key}: {value} ({dt.strftime('%Y-%m-%d %H:%M:%S')})\n"
                    else:
                        details += f"{key}: {value}\n"
                        
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(1.0, details)
                
        except Exception as e:
            self.log_error(f"显示素材详情失败: {e}")
            
    def update_project_info(self):
        """更新项目信息显示"""
        if not self.current_manager:
            self.project_info_text.delete(1.0, tk.END)
            return
            
        try:
            project_info = self.current_manager.get_project_info()
            
            info_text = f"项目名称: {project_info.get('project_name', 'N/A')}\n"
            info_text += f"项目ID: {project_info.get('project_id', 'N/A')}\n"
            info_text += f"项目路径: {project_info.get('project_path', 'N/A')}"
            
            self.project_info_text.delete(1.0, tk.END)
            self.project_info_text.insert(1.0, info_text)
            
        except Exception as e:
            self.log_error(f"更新项目信息失败: {e}")
            
    def log_info(self, message):
        """记录信息日志"""
        self.info_text.insert(tk.END, f"[INFO] {message}\n")
        self.info_text.see(tk.END)
        
    def log_error(self, message):
        """记录错误日志"""
        self.info_text.insert(tk.END, f"[ERROR] {message}\n")
        self.info_text.see(tk.END)


def main():
    """主函数"""
    root = tk.Tk()
    app = DraftManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
