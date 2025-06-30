#!/usr/bin/env python3
"""
tkinter测试脚本
专门用于诊断tkinter相关问题
"""

import sys
import platform

def test_tkinter():
    """测试tkinter可用性"""
    print("🔍 tkinter可用性测试")
    print("=" * 40)
    print(f"Python版本: {sys.version}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print()
    
    # 测试基本导入
    print("1. 测试基本导入...")
    try:
        import tkinter
        print("✅ tkinter导入成功")
    except ImportError as e:
        print(f"❌ tkinter导入失败: {e}")
        print()
        print("解决方案:")
        if platform.system() == "Windows":
            print("- 重新安装Python，确保勾选'tcl/tk and IDLE'")
            print("- 下载Python 3.11.9 (更稳定): https://www.python.org/downloads/release/python-3119/")
            print("- 或安装Anaconda: https://www.anaconda.com/products/distribution")
        else:
            print("- Ubuntu/Debian: sudo apt install python3-tk")
            print("- CentOS/RHEL: sudo yum install tkinter")
            print("- macOS: brew install python-tk")
        return False
    
    # 测试ttk
    print("2. 测试ttk模块...")
    try:
        from tkinter import ttk
        print("✅ tkinter.ttk导入成功")
    except ImportError as e:
        print(f"❌ tkinter.ttk导入失败: {e}")
        return False
    
    # 测试对话框
    print("3. 测试对话框模块...")
    try:
        from tkinter import filedialog, messagebox
        print("✅ 对话框模块导入成功")
    except ImportError as e:
        print(f"❌ 对话框模块导入失败: {e}")
        return False
    
    # 测试创建窗口
    print("4. 测试创建窗口...")
    try:
        root = tkinter.Tk()
        root.title("tkinter测试")
        root.geometry("300x200")
        
        # 添加一些控件
        label = tkinter.Label(root, text="tkinter工作正常！")
        label.pack(pady=20)
        
        button = tkinter.Button(root, text="关闭", command=root.destroy)
        button.pack(pady=10)
        
        print("✅ 窗口创建成功")
        print("📝 将显示测试窗口，请关闭窗口继续...")
        
        # 显示窗口
        root.mainloop()
        
        print("✅ 窗口显示和交互正常")
        
    except Exception as e:
        print(f"❌ 窗口创建失败: {e}")
        return False
    
    print()
    print("🎉 tkinter完全可用！")
    print("✅ 可以运行GUI应用程序")
    return True

def test_other_dependencies():
    """测试其他依赖"""
    print("\n🔍 其他依赖测试")
    print("=" * 40)
    
    dependencies = [
        ("cv2", "OpenCV", "pip install opencv-python"),
        ("numpy", "NumPy", "pip install numpy"),
        ("loguru", "Loguru", "pip install loguru"),
        ("PIL", "Pillow", "pip install Pillow"),
    ]
    
    all_ok = True
    
    for module, name, install_cmd in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - 安装命令: {install_cmd}")
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    print("🧪 Smart Shot Detection System - 依赖测试工具")
    print("=" * 60)
    
    # 测试tkinter
    tkinter_ok = test_tkinter()
    
    # 测试其他依赖
    deps_ok = test_other_dependencies()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    if tkinter_ok and deps_ok:
        print("🎉 所有测试通过！")
        print("✅ 可以运行Smart Shot Detection System")
        print("\n启动命令: python run_gui.py")
    elif tkinter_ok:
        print("⚠️ tkinter可用，但缺少其他依赖")
        print("📝 请安装缺少的依赖包")
    else:
        print("❌ tkinter不可用")
        print("🔧 请先解决tkinter问题")
        
        if sys.version_info >= (3, 13):
            print("\n⚠️ 特别提醒：")
            print("Python 3.13是最新版本，可能存在兼容性问题")
            print("建议使用Python 3.11.9以获得更好的稳定性")
            print("下载地址: https://www.python.org/downloads/release/python-3119/")
    
    print("\n按回车键退出...")
    input()

if __name__ == "__main__":
    main()
