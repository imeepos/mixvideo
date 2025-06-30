#!/usr/bin/env python3
"""
测试滚动布局GUI
验证主界面的滚动功能和目录打开修复
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import subprocess

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))


class ScrollTestGUI:
    """滚动测试GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔄 滚动布局测试")
        self.root.geometry("800x600")
        
        # 创建滚动界面
        self.create_scrollable_interface()
    
    def create_scrollable_interface(self):
        """创建可滚动界面"""
        # 创建主画布和滚动条
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # 配置滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # 创建画布窗口
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 布局画布和滚动条
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        self.bind_mousewheel()
        
        # 绑定画布大小变化事件
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # 创建测试内容
        self.create_test_content()
    
    def bind_mousewheel(self):
        """绑定鼠标滚轮事件"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # 绑定鼠标进入和离开事件
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # Linux系统的滚轮事件
        def _on_mousewheel_linux(event):
            self.canvas.yview_scroll(-1, "units")
        
        def _on_mousewheel_linux_up(event):
            self.canvas.yview_scroll(1, "units")
        
        self.canvas.bind("<Button-4>", _on_mousewheel_linux_up)
        self.canvas.bind("<Button-5>", _on_mousewheel_linux)
    
    def on_canvas_configure(self, event):
        """画布大小变化事件"""
        # 更新滚动区域的宽度以匹配画布宽度
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def create_test_content(self):
        """创建测试内容"""
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🔄 滚动布局测试", font=('TkDefaultFont', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 创建多个测试区域
        for i in range(10):
            self.create_test_section(main_frame, i + 1)
        
        # 目录打开测试
        self.create_directory_test_section(main_frame)
    
    def create_test_section(self, parent, section_num):
        """创建测试区域"""
        frame = ttk.LabelFrame(parent, text=f"📋 测试区域 {section_num}", padding="15")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        # 添加一些测试内容
        content_text = f"""这是第 {section_num} 个测试区域。
这里包含了一些测试文本来验证滚动功能是否正常工作。
您可以使用鼠标滚轮或滚动条来滚动界面。

功能测试项目：
• 鼠标滚轮滚动
• 滚动条拖拽
• 键盘方向键滚动
• 界面响应式调整"""
        
        text_label = ttk.Label(frame, text=content_text, justify=tk.LEFT)
        text_label.pack(anchor=tk.W)
        
        # 添加一些按钮
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text=f"测试按钮 {section_num}-1", 
                  command=lambda: messagebox.showinfo("测试", f"点击了区域 {section_num} 的按钮 1")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text=f"测试按钮 {section_num}-2", 
                  command=lambda: messagebox.showinfo("测试", f"点击了区域 {section_num} 的按钮 2")).pack(side=tk.LEFT)
    
    def create_directory_test_section(self, parent):
        """创建目录打开测试区域"""
        frame = ttk.LabelFrame(parent, text="📁 目录打开测试", padding="15")
        frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = """测试目录打开功能的修复效果：
• 支持多种文件管理器
• 提供错误处理和回退方案
• 显示详细的目录信息对话框"""
        
        ttk.Label(frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 10))
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        # 测试目录打开
        def test_open_current_dir():
            self.test_directory_open(Path.cwd())
        
        def test_open_home_dir():
            self.test_directory_open(Path.home())
        
        def test_open_nonexistent_dir():
            self.test_directory_open(Path("/nonexistent/directory"))
        
        ttk.Button(button_frame, text="📂 打开当前目录", command=test_open_current_dir).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🏠 打开用户目录", command=test_open_home_dir).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ 测试不存在目录", command=test_open_nonexistent_dir).pack(side=tk.LEFT)
    
    def test_directory_open(self, directory_path):
        """测试目录打开功能"""
        if not directory_path.exists():
            messagebox.showwarning("警告", f"目录不存在: {directory_path}")
            return
        
        # 尝试多种方法打开目录
        success = False
        error_messages = []
        
        try:
            if sys.platform == "win32":
                # Windows
                os.startfile(str(directory_path))
                success = True
            elif sys.platform == "darwin":
                # macOS
                subprocess.run(["open", str(directory_path)], check=True)
                success = True
            else:
                # Linux - 尝试多种方法
                methods = [
                    ["xdg-open", str(directory_path)],
                    ["nautilus", str(directory_path)],
                    ["dolphin", str(directory_path)],
                    ["thunar", str(directory_path)],
                    ["pcmanfm", str(directory_path)],
                    ["caja", str(directory_path)]
                ]
                
                for method in methods:
                    try:
                        subprocess.run(method, check=True, capture_output=True)
                        success = True
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError) as e:
                        error_messages.append(f"{method[0]}: {e}")
                        continue
        
        except Exception as e:
            error_messages.append(f"系统调用失败: {e}")
        
        if success:
            messagebox.showinfo("成功", f"已打开目录: {directory_path}")
        else:
            # 显示详细错误信息
            error_text = f"无法打开目录: {directory_path}\n\n错误信息:\n" + "\n".join(error_messages)
            messagebox.showerror("失败", error_text)


def main():
    """主函数"""
    print("🔄 启动滚动布局测试GUI...")
    
    root = tk.Tk()
    app = ScrollTestGUI(root)
    
    # 居中显示
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    print("✅ 滚动布局测试GUI已启动")
    print("请测试以下功能:")
    print("• 鼠标滚轮滚动")
    print("• 滚动条拖拽")
    print("• 目录打开功能")
    print("• 界面响应性")
    
    root.mainloop()


if __name__ == "__main__":
    main()
