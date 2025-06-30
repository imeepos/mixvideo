#!/usr/bin/env python3
"""
字体测试GUI
测试中文字体在GUI中的显示效果
"""

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from font_config import FontManager


class FontTestGUI:
    """字体测试GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🔤 字体测试 - 中文显示测试")
        self.root.geometry("800x600")
        
        # 字体管理器
        self.font_manager = FontManager()
        self.font_manager.detect_system_fonts()
        self.font_manager.detect_chinese_fonts()
        
        # 当前字体
        self.current_font = tk.StringVar()
        self.current_size = tk.IntVar(value=12)
        
        # 创建界面
        self.create_widgets()
        
        # 设置默认字体
        best_font = self.font_manager.get_best_font()
        if best_font:
            self.current_font.set(best_font)
        else:
            self.current_font.set("TkDefaultFont")
        
        self.update_display()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 控制区域
        control_frame = ttk.LabelFrame(main_frame, text="字体控制", padding="10")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 字体选择
        ttk.Label(control_frame, text="字体:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        font_combo = ttk.Combobox(control_frame, textvariable=self.current_font, width=30)
        font_combo['values'] = self.font_manager.get_recommended_fonts() + ['TkDefaultFont', 'Arial', 'DejaVu Sans']
        font_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        font_combo.bind('<<ComboboxSelected>>', self.on_font_change)
        
        # 字体大小
        ttk.Label(control_frame, text="大小:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        size_spin = ttk.Spinbox(control_frame, from_=8, to=24, textvariable=self.current_size, width=5)
        size_spin.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        size_spin.bind('<KeyRelease>', self.on_size_change)
        size_spin.bind('<<Increment>>', self.on_size_change)
        size_spin.bind('<<Decrement>>', self.on_size_change)
        
        # 刷新按钮
        ttk.Button(control_frame, text="刷新", command=self.update_display).grid(row=0, column=4, padx=(10, 0))
        
        # 配置列权重
        control_frame.columnconfigure(1, weight=1)
        
        # 测试文本区域
        text_frame = ttk.LabelFrame(main_frame, text="中文显示测试", padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建测试标签
        self.test_labels = []
        
        test_texts = [
            ("标题", "🎬 智能镜头检测与分段系统", 16, 'bold'),
            ("副标题", "📁 文件选择和处理设置", 14, 'bold'),
            ("正文", "请选择要处理的视频文件，系统支持MP4、AVI、MOV等格式", 12, 'normal'),
            ("按钮文本", "🚀 开始处理  ⏹️ 停止  📊 查看报告", 10, 'normal'),
            ("状态信息", "处理进度: 85% - 正在生成分析报告...", 10, 'normal'),
            ("错误信息", "❌ 错误：视频文件格式不支持", 10, 'normal'),
            ("成功信息", "✅ 处理完成！生成了22个视频分段", 10, 'normal'),
            ("详细信息", "视频信息: 时长 02:30.500, 分辨率 1920x1080, 帧率 30.0 FPS", 9, 'normal'),
            ("特殊字符", "中文标点：，。！？；：""''（）【】《》", 10, 'normal'),
            ("数字混合", "检测到 25 个镜头边界，平均置信度 0.85，处理耗时 3.2 秒", 10, 'normal')
        ]
        
        for i, (label_text, test_text, size, weight) in enumerate(test_texts):
            # 标签描述
            desc_label = ttk.Label(text_frame, text=f"{label_text}:", font=('TkDefaultFont', 9))
            desc_label.grid(row=i, column=0, sticky=(tk.W, tk.N), padx=(0, 10), pady=2)
            
            # 测试文本
            test_label = ttk.Label(text_frame, text=test_text, font=('TkDefaultFont', size, weight))
            test_label.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2)
            
            self.test_labels.append((test_label, test_text, size, weight))
        
        # 配置列权重
        text_frame.columnconfigure(1, weight=1)
        
        # 信息区域
        info_frame = ttk.LabelFrame(main_frame, text="字体信息", padding="10")
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.info_text = tk.Text(info_frame, height=6, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示字体信息
        self.show_font_info()
    
    def on_font_change(self, event=None):
        """字体改变事件"""
        self.update_display()
    
    def on_size_change(self, event=None):
        """字体大小改变事件"""
        self.root.after(100, self.update_display)  # 延迟更新
    
    def update_display(self):
        """更新显示"""
        font_name = self.current_font.get()
        base_size = self.current_size.get()
        
        try:
            for test_label, test_text, relative_size, weight in self.test_labels:
                actual_size = max(8, base_size + relative_size - 12)  # 基于基础大小调整
                test_label.configure(font=(font_name, actual_size, weight))
            
            # 更新窗口标题
            self.root.title(f"🔤 字体测试 - {font_name} ({base_size}pt)")
            
        except Exception as e:
            print(f"字体更新失败: {e}")
    
    def show_font_info(self):
        """显示字体信息"""
        self.info_text.delete(1.0, tk.END)
        
        # 获取字体信息
        recommended = self.font_manager.get_recommended_fonts()
        chinese_fonts = self.font_manager.chinese_fonts
        
        info = f"""字体检测结果:
• 推荐中文字体: {len(recommended)} 个
• 所有中文字体: {len(chinese_fonts)} 个
• 当前最佳字体: {self.font_manager.get_best_font() or '未找到'}

推荐字体列表:
"""
        
        for i, font in enumerate(recommended, 1):
            info += f"{i}. {font}\n"
        
        if not recommended:
            info += "❌ 未找到推荐的中文字体\n"
        
        info += f"\n使用说明:\n"
        info += f"• 选择不同字体查看中文显示效果\n"
        info += f"• 调整字体大小测试可读性\n"
        info += f"• 如果显示乱码，请安装中文字体包\n"
        
        self.info_text.insert(1.0, info)


def main():
    """主函数"""
    print("🔤 启动字体测试GUI...")
    
    root = tk.Tk()
    app = FontTestGUI(root)
    
    # 居中显示
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    print("✅ 字体测试GUI已启动")
    print("请在GUI中测试不同字体的中文显示效果")
    
    root.mainloop()


if __name__ == "__main__":
    main()
