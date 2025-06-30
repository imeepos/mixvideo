#!/usr/bin/env python3
"""
创建发布包脚本
将所有必要文件打包成用户友好的发布包
"""

import os
import shutil
import zipfile
from pathlib import Path
import datetime


def create_release_package():
    """创建发布包"""
    print("📦 创建智能镜头检测与分段系统发布包...")
    
    # 创建发布目录
    release_name = f"ShotDetectionGUI_v1.0.0_{datetime.datetime.now().strftime('%Y%m%d')}"
    release_dir = Path(release_name)
    
    if release_dir.exists():
        shutil.rmtree(release_dir)
    
    release_dir.mkdir()
    print(f"📁 创建发布目录: {release_dir}")
    
    # 复制可执行文件
    print("📋 复制可执行文件...")
    
    # 单文件版本
    if Path("dist/ShotDetectionGUI").exists():
        shutil.copy2("dist/ShotDetectionGUI", release_dir / "ShotDetectionGUI")
        print("✅ 单文件版本: ShotDetectionGUI")
    
    # 目录版本
    if Path("dist/ShotDetectionGUI_dist").exists():
        shutil.copytree("dist/ShotDetectionGUI_dist", release_dir / "ShotDetectionGUI_dist")
        print("✅ 目录版本: ShotDetectionGUI_dist/")
    
    # 复制安装脚本
    print("📋 复制安装脚本...")
    for script in ["install.bat", "install.sh"]:
        if Path(script).exists():
            shutil.copy2(script, release_dir / script)
            print(f"✅ {script}")
    
    # 复制文档
    print("📋 复制文档...")
    docs = ["RELEASE_README.md", "README.md"]
    for doc in docs:
        if Path(doc).exists():
            shutil.copy2(doc, release_dir / doc)
            print(f"✅ {doc}")
    
    # 复制图标
    if Path("icon.ico").exists():
        shutil.copy2("icon.ico", release_dir / "icon.ico")
        print("✅ icon.ico")
    
    # 复制示例视频（如果存在且不太大）
    if Path("test_video.mp4").exists():
        size_mb = Path("test_video.mp4").stat().st_size / (1024 * 1024)
        if size_mb < 50:  # 小于50MB才复制
            shutil.copy2("test_video.mp4", release_dir / "test_video.mp4")
            print(f"✅ test_video.mp4 ({size_mb:.1f}MB)")
        else:
            print(f"⚠️ test_video.mp4 太大 ({size_mb:.1f}MB)，跳过")
    
    # 创建快速开始指南
    print("📖 创建快速开始指南...")
    quick_start = release_dir / "QUICK_START.txt"
    with open(quick_start, 'w', encoding='utf-8') as f:
        f.write("""🎬 智能镜头检测与分段系统 - 快速开始

=== Windows 用户 ===
1. 双击运行 ShotDetectionGUI.exe
   或
   右键点击 install.bat，选择"以管理员身份运行"进行安装

=== Linux 用户 ===
1. 在终端中运行: ./ShotDetectionGUI
   或
   运行安装脚本: sudo ./install.sh

=== 使用步骤 ===
1. 选择视频文件 (推荐MP4格式)
2. 设置输出目录
3. 选择组织方式和质量设置
4. 点击"开始处理"
5. 等待处理完成
6. 查看生成的分段视频和分析报告

=== 系统要求 ===
- 64位操作系统
- 至少4GB内存
- 至少2GB可用磁盘空间

=== 技术支持 ===
如遇问题，请查看 RELEASE_README.md 中的故障排除部分。

© 2024 智能镜头检测与分段系统
""")
    print("✅ QUICK_START.txt")
    
    # 创建版本信息文件
    version_info = release_dir / "VERSION_INFO.txt"
    with open(version_info, 'w', encoding='utf-8') as f:
        f.write(f"""智能镜头检测与分段系统
版本: v1.0.0
构建日期: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
平台: Linux x86_64

功能特性:
- 智能镜头检测算法
- 自动视频分段
- 多格式项目文件导出
- 详细分析报告生成
- 中文GUI界面
- 实时进度显示

包含文件:
- ShotDetectionGUI (单文件可执行版本)
- ShotDetectionGUI_dist/ (目录版本)
- install.bat (Windows安装脚本)
- install.sh (Linux安装脚本)
- RELEASE_README.md (详细说明文档)
- QUICK_START.txt (快速开始指南)
- icon.ico (应用图标)
""")
    print("✅ VERSION_INFO.txt")
    
    # 计算发布包大小
    total_size = 0
    for root, dirs, files in os.walk(release_dir):
        for file in files:
            total_size += os.path.getsize(os.path.join(root, file))
    
    size_mb = total_size / (1024 * 1024)
    print(f"📊 发布包大小: {size_mb:.1f} MB")
    
    # 创建压缩包
    print("🗜️ 创建压缩包...")
    zip_name = f"{release_name}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, release_dir.parent)
                zipf.write(file_path, arc_name)
    
    zip_size = os.path.getsize(zip_name) / (1024 * 1024)
    print(f"✅ 压缩包创建完成: {zip_name} ({zip_size:.1f} MB)")
    
    # 显示发布包内容
    print(f"\n📦 发布包内容 ({release_dir}):")
    for item in sorted(release_dir.rglob("*")):
        if item.is_file():
            size = item.stat().st_size / (1024 * 1024)
            rel_path = item.relative_to(release_dir)
            if size > 1:
                print(f"   📄 {rel_path} ({size:.1f} MB)")
            else:
                print(f"   📄 {rel_path}")
        elif item.is_dir() and item != release_dir:
            rel_path = item.relative_to(release_dir)
            print(f"   📁 {rel_path}/")
    
    print(f"\n🎉 发布包创建完成！")
    print(f"📁 目录版本: {release_dir}/")
    print(f"📦 压缩包: {zip_name}")
    print(f"📊 总大小: {size_mb:.1f} MB (压缩后: {zip_size:.1f} MB)")
    
    print(f"\n📋 发布清单:")
    print(f"✅ 可执行文件 (单文件 + 目录版本)")
    print(f"✅ 安装脚本 (Windows + Linux)")
    print(f"✅ 用户文档 (详细说明 + 快速开始)")
    print(f"✅ 应用图标")
    print(f"✅ 版本信息")
    
    return release_dir, zip_name


if __name__ == "__main__":
    create_release_package()
