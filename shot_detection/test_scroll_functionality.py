#!/usr/bin/env python3
"""
测试GUI滚动功能
验证Tab页面是否可以正常滚动
"""

import tkinter as tk
from tkinter import ttk


def test_scroll_gui():
    """测试滚动GUI"""
    root = tk.Tk()
    root.title("滚动功能测试")
    root.geometry("800x600")
    
    # 创建Notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 创建可滚动的Tab
    def create_scrollable_tab(tab_name, content_height=2000):
        # Tab容器
        tab_container = ttk.Frame(notebook)
        notebook.add(tab_container, text=tab_name)
        
        # Canvas和滚动条
        canvas = tk.Canvas(tab_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="15")
        
        # 配置滚动
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 鼠标滚轮支持
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # 添加测试内容
        for i in range(50):
            frame = ttk.LabelFrame(scrollable_frame, text=f"测试区域 {i+1}", padding="10")
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"这是第 {i+1} 个测试区域").pack(anchor=tk.W)
            ttk.Entry(frame, width=50).pack(fill=tk.X, pady=2)
            ttk.Button(frame, text=f"按钮 {i+1}").pack(anchor=tk.W, pady=2)
        
        return scrollable_frame
    
    # 创建测试Tab
    create_scrollable_tab("测试Tab 1")
    create_scrollable_tab("测试Tab 2")
    create_scrollable_tab("测试Tab 3")
    
    # 添加说明
    info_frame = ttk.Frame(root)
    info_frame.pack(fill=tk.X, padx=10, pady=5)
    
    info_text = """滚动测试说明:
• 使用鼠标滚轮在Tab内容区域滚动
• 拖拽右侧滚动条
• 内容超出窗口高度时应该可以滚动
• 切换不同Tab测试滚动功能"""
    
    ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
    
    root.mainloop()


if __name__ == "__main__":
    test_scroll_gui()
