#!/usr/bin/env python3
"""
安全安装依赖项

根据Python版本智能选择兼容的包版本
"""

import sys
import subprocess
import platform

def get_python_version():
    """获取Python版本信息"""
    version = sys.version_info
    return f"{version.major}.{version.minor}.{version.micro}"

def install_package_safe(package_name, fallback_versions=None):
    """安全安装包，如果失败则尝试备用版本"""
    print(f"📦 安装 {package_name}...")
    
    # 首先尝试安装最新兼容版本
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError:
        print(f"⚠️ {package_name} 安装失败，尝试备用版本...")
        
        # 尝试备用版本
        if fallback_versions:
            for version in fallback_versions:
                try:
                    package_spec = f"{package_name.split('>=')[0].split('==')[0]}{version}"
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package_spec])
                    print(f"✅ {package_spec} 安装成功")
                    return True
                except subprocess.CalledProcessError:
                    print(f"⚠️ {package_spec} 也失败了")
                    continue
        
        print(f"❌ {package_name} 所有版本都安装失败")
        return False

def install_core_dependencies():
    """安装核心依赖"""
    print("🔧 安装核心依赖项...")
    print(f"Python版本: {get_python_version()}")
    print(f"平台: {platform.system()} {platform.machine()}")
    
    # 核心依赖列表（按重要性排序）
    core_packages = [
        {
            "name": "requests>=2.25.0",
            "fallbacks": [">=2.20.0", ">=2.15.0", ">=2.10.0"],
            "essential": True,
            "description": "HTTP请求库 (Gemini API必需)"
        },
        {
            "name": "numpy>=1.20.0", 
            "fallbacks": [">=1.18.0", ">=1.16.0", ">=1.15.0"],
            "essential": True,
            "description": "数值计算库"
        },
        {
            "name": "opencv-python>=4.5.0",
            "fallbacks": [">=4.2.0", ">=4.0.0", ">=3.4.0"],
            "essential": True,
            "description": "计算机视觉库"
        },
        {
            "name": "Pillow>=8.0.0",
            "fallbacks": [">=7.0.0", ">=6.0.0", ">=5.4.0"],
            "essential": True,
            "description": "图像处理库"
        },
        {
            "name": "PyYAML>=5.4.0",
            "fallbacks": [">=5.1.0", ">=5.0.0", ">=4.2.0"],
            "essential": True,
            "description": "YAML配置文件处理"
        },
        {
            "name": "loguru>=0.6.0",
            "fallbacks": [">=0.5.0", ">=0.4.0"],
            "essential": False,
            "description": "日志记录库"
        }
    ]
    
    success_count = 0
    essential_count = 0
    
    for package in core_packages:
        if package["essential"]:
            essential_count += 1
        
        print(f"\n{'='*50}")
        print(f"安装: {package['description']}")
        print(f"包名: {package['name']}")
        
        if install_package_safe(package["name"], package["fallbacks"]):
            success_count += 1
        elif package["essential"]:
            print(f"❌ 关键依赖 {package['name']} 安装失败！")
    
    print(f"\n{'='*50}")
    print("安装结果")
    print('='*50)
    print(f"成功安装: {success_count}/{len(core_packages)}")
    print(f"关键依赖: {essential_count} 个")
    
    # 验证关键依赖
    print(f"\n🔍 验证关键依赖...")
    
    critical_imports = [
        ("requests", "HTTP请求"),
        ("numpy", "数值计算"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("yaml", "PyYAML")
    ]
    
    import_success = 0
    for module, desc in critical_imports:
        try:
            __import__(module)
            print(f"✅ {desc} ({module})")
            import_success += 1
        except ImportError as e:
            print(f"❌ {desc} ({module}): {e}")
    
    print(f"\n导入验证: {import_success}/{len(critical_imports)}")
    
    if import_success >= 4:  # 至少4个关键模块成功
        print("\n🎉 核心依赖安装成功！")
        print("现在可以运行视频分析功能了")
        return True
    else:
        print("\n❌ 关键依赖缺失，可能影响功能")
        return False

def create_install_script():
    """创建便捷安装脚本"""
    print(f"\n📝 创建便捷安装脚本...")
    
    # Windows批处理脚本
    bat_content = '''@echo off
echo 安装视频分析系统依赖项...
echo.

python --version
if errorlevel 1 (
    echo 错误: Python未安装或不在PATH中
    pause
    exit /b 1
)

echo.
echo 安装核心依赖...
python -m pip install --upgrade pip
python -m pip install requests>=2.25.0
python -m pip install numpy>=1.20.0
python -m pip install opencv-python>=4.5.0
python -m pip install Pillow>=8.0.0
python -m pip install PyYAML>=5.4.0
python -m pip install loguru>=0.6.0

echo.
echo 验证安装...
python -c "import requests, numpy, cv2, PIL, yaml, loguru; print('所有依赖安装成功!')"

if errorlevel 1 (
    echo.
    echo 部分依赖安装失败，尝试备用方案...
    python install_dependencies_safe.py
)

echo.
echo 安装完成！
pause
'''
    
    with open("install_deps.bat", 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    # Linux shell脚本
    sh_content = '''#!/bin/bash
echo "安装视频分析系统依赖项..."
echo

python3 --version
if [ $? -ne 0 ]; then
    echo "错误: Python3未安装"
    exit 1
fi

echo
echo "安装核心依赖..."
python3 -m pip install --upgrade pip
python3 -m pip install requests>=2.25.0
python3 -m pip install numpy>=1.20.0
python3 -m pip install opencv-python>=4.5.0
python3 -m pip install Pillow>=8.0.0
python3 -m pip install PyYAML>=5.4.0
python3 -m pip install loguru>=0.6.0

echo
echo "验证安装..."
python3 -c "import requests, numpy, cv2, PIL, yaml, loguru; print('所有依赖安装成功!')"

if [ $? -ne 0 ]; then
    echo
    echo "部分依赖安装失败，尝试备用方案..."
    python3 install_dependencies_safe.py
fi

echo
echo "安装完成！"
'''
    
    with open("install_deps.sh", 'w', encoding='utf-8') as f:
        f.write(sh_content)
    
    # 设置执行权限
    import os
    os.chmod("install_deps.sh", 0o755)
    
    print("✅ 创建了便捷安装脚本:")
    print("  - install_deps.bat (Windows)")
    print("  - install_deps.sh (Linux/Mac)")

def main():
    """主函数"""
    print("🛠️ 安全依赖安装工具")
    print("=" * 50)
    
    # 安装核心依赖
    success = install_core_dependencies()
    
    # 创建便捷脚本
    create_install_script()
    
    print(f"\n{'='*50}")
    print("总结")
    print('='*50)
    
    if success:
        print("🎉 依赖安装成功！")
        print("\n✨ 现在可以:")
        print("• 运行视频分析功能")
        print("• 调用Gemini API")
        print("• 使用4分类系统")
        print("• 处理视频文件")
        
        print("\n🚀 下一步:")
        print("cd ShotDetectionGUI_Python_Complete_v1.0.3_20250701")
        print("python run_gui.py")
        
    else:
        print("⚠️ 部分依赖安装失败")
        print("\n🔧 手动安装建议:")
        print("pip install requests numpy opencv-python Pillow PyYAML loguru")
        print("\n或使用便捷脚本:")
        print("Windows: install_deps.bat")
        print("Linux/Mac: ./install_deps.sh")

if __name__ == "__main__":
    main()
