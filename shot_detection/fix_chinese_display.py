#!/usr/bin/env python3
"""
修复中文显示问题
设置正确的环境变量和字体配置
"""

import os
import sys
import locale
import subprocess
from pathlib import Path


def set_locale_environment():
    """设置本地化环境变量"""
    print("🌐 设置本地化环境...")
    
    # 设置环境变量
    env_vars = {
        'LANG': 'en_US.UTF-8',
        'LC_ALL': 'en_US.UTF-8',
        'LC_CTYPE': 'en_US.UTF-8',
        'PYTHONIOENCODING': 'utf-8'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  {key}={value}")
    
    # 设置Python默认编码
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf-8')
    
    # 设置locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        print("✅ 本地化设置成功")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
            print("✅ 使用C.UTF-8本地化")
        except locale.Error:
            print("⚠️ 本地化设置失败，使用默认设置")


def install_chinese_fonts():
    """安装中文字体"""
    print("📦 安装中文字体...")
    
    try:
        # 检查是否为Linux系统
        if sys.platform.startswith('linux'):
            # 更新包列表
            print("更新包列表...")
            subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
            
            # 安装字体包
            font_packages = [
                'fonts-noto-cjk',           # Google Noto CJK字体
                'fonts-noto-cjk-extra',     # 额外的CJK字体
                'fonts-wqy-zenhei',         # 文泉驿正黑
                'fonts-wqy-microhei',       # 文泉驿微米黑
                'fonts-arphic-ukai',        # 文鼎PL楷书
                'fonts-arphic-uming',       # 文鼎PL明体
                'language-pack-zh-hans',    # 简体中文语言包
                'language-pack-zh-hans-base'
            ]
            
            for package in font_packages:
                try:
                    print(f"安装 {package}...")
                    result = subprocess.run(['sudo', 'apt', 'install', '-y', package],
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"✅ {package} 安装成功")
                    else:
                        print(f"⚠️ {package} 安装失败: {result.stderr}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ {package} 安装出错: {e}")
            
            # 更新字体缓存
            print("更新字体缓存...")
            subprocess.run(['fc-cache', '-fv'], capture_output=True)
            print("✅ 字体缓存更新完成")
            
            return True
            
        else:
            print(f"⚠️ 当前系统 {sys.platform} 不支持自动字体安装")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 字体安装失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 字体安装过程中出错: {e}")
        return False


def configure_tkinter_fonts():
    """配置Tkinter字体"""
    print("🎨 配置Tkinter字体...")
    
    try:
        import tkinter as tk
        from tkinter import font
        
        # 创建临时根窗口
        root = tk.Tk()
        root.withdraw()
        
        # 获取系统字体
        available_fonts = font.families()
        
        # 查找中文字体
        chinese_fonts = []
        for font_name in available_fonts:
            font_lower = font_name.lower()
            if any(keyword in font_lower for keyword in ['noto', 'cjk', 'han', 'wqy', 'chinese']):
                chinese_fonts.append(font_name)
        
        if chinese_fonts:
            best_font = chinese_fonts[0]
            print(f"✅ 找到中文字体: {best_font}")
            
            # 设置默认字体
            default_font = font.nametofont("TkDefaultFont")
            default_font.configure(family=best_font)
            
            text_font = font.nametofont("TkTextFont")
            text_font.configure(family=best_font)
            
            print("✅ Tkinter字体配置完成")
        else:
            print("⚠️ 未找到合适的中文字体")
        
        root.destroy()
        return len(chinese_fonts) > 0
        
    except Exception as e:
        print(f"❌ Tkinter字体配置失败: {e}")
        return False


def test_chinese_display():
    """测试中文显示"""
    print("🧪 测试中文显示...")
    
    try:
        import tkinter as tk
        from tkinter import ttk
        
        # 创建测试窗口
        root = tk.Tk()
        root.title("中文显示测试")
        root.geometry("400x200")
        
        # 测试文本
        test_text = "🎬 智能镜头检测与分段系统\n中文显示测试成功！"
        
        # 创建标签
        label = ttk.Label(root, text=test_text, font=('TkDefaultFont', 12))
        label.pack(expand=True)
        
        # 创建按钮
        button = ttk.Button(root, text="关闭测试", command=root.destroy)
        button.pack(pady=10)
        
        print("✅ 中文显示测试窗口已打开")
        print("如果看到正确的中文显示，说明修复成功")
        
        # 显示窗口
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ 中文显示测试失败: {e}")
        return False


def create_font_config_file():
    """创建字体配置文件"""
    print("📝 创建字体配置文件...")
    
    config_content = """# 字体配置文件
# 用于GUI应用的中文字体设置

[fonts]
# 推荐的中文字体（按优先级排序）
chinese_fonts = [
    "Noto Sans CJK SC",
    "Noto Sans CJK TC", 
    "Source Han Sans",
    "WenQuanYi Zen Hei",
    "WenQuanYi Micro Hei",
    "Microsoft YaHei",
    "SimHei",
    "SimSun"
]

# 回退字体
fallback_fonts = [
    "DejaVu Sans",
    "Liberation Sans", 
    "Arial",
    "Helvetica"
]

[display]
# 显示设置
encoding = "utf-8"
locale = "en_US.UTF-8"

[tkinter]
# Tkinter特定设置
default_font_size = 10
title_font_size = 16
heading_font_size = 12
"""
    
    try:
        config_file = Path("font_config.ini")
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"✅ 字体配置文件已创建: {config_file}")
        return True
        
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")
        return False


def main():
    """主修复函数"""
    print("🔧 中文显示问题修复工具")
    print("=" * 40)
    
    # 1. 设置环境变量
    set_locale_environment()
    
    # 2. 检查是否需要安装字体
    print("\n🔍 检查字体安装状态...")
    
    try:
        from font_config import FontManager
        font_manager = FontManager()
        font_manager.detect_system_fonts()
        font_manager.detect_chinese_fonts()
        
        if not font_manager.chinese_fonts:
            print("❌ 未检测到中文字体")
            response = input("是否安装中文字体? (y/N): ")
            if response.lower() == 'y':
                install_chinese_fonts()
        else:
            print(f"✅ 检测到 {len(font_manager.chinese_fonts)} 个中文字体")
            
    except ImportError:
        print("⚠️ 无法导入字体管理器，尝试安装字体...")
        response = input("是否安装中文字体? (y/N): ")
        if response.lower() == 'y':
            install_chinese_fonts()
    
    # 3. 配置Tkinter字体
    print("\n🎨 配置GUI字体...")
    configure_tkinter_fonts()
    
    # 4. 创建配置文件
    print("\n📝 创建配置文件...")
    create_font_config_file()
    
    # 5. 测试中文显示
    print("\n🧪 测试中文显示...")
    response = input("是否打开测试窗口? (y/N): ")
    if response.lower() == 'y':
        test_chinese_display()
    
    print("\n🎉 中文显示修复完成！")
    print("现在可以启动GUI应用测试中文显示效果")
    print("运行命令: python run_gui.py")


if __name__ == "__main__":
    main()
