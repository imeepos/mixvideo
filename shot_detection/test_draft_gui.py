#!/usr/bin/env python3
"""
测试剪映草稿管理器GUI功能

验证GUI组件是否正常工作
"""

import sys
import tempfile
from pathlib import Path

# 添加路径
sys.path.append(str(Path(__file__).parent / "jianying"))

try:
    from jianying.draft_meta_manager import DraftMetaManager, MaterialInfo
    print("✓ 成功导入 draft_meta_manager")
except ImportError:
    try:
        from draft_meta_manager import DraftMetaManager, MaterialInfo
        print("✓ 成功导入 draft_meta_manager (直接导入)")
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        sys.exit(1)

def test_basic_functionality():
    """测试基本功能"""
    print("\n=== 测试基本功能 ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_gui_project"
        
        # 创建管理器
        manager = DraftMetaManager(project_path)
        meta_data = manager.load_meta_data()
        
        print(f"✓ 创建项目: {project_path.name}")
        
        # 获取项目信息
        project_info = manager.get_project_info()
        print(f"✓ 项目ID: {project_info['project_id']}")
        print(f"✓ 项目名称: {project_info['project_name']}")
        
        # 添加测试素材
        test_video_path = "/home/imeep/mixvideo/workspace/resources/0630-交付素材1/背景2/1751271193442.mp4"
        
        if Path(test_video_path).exists():
            material = MaterialInfo(
                file_path=test_video_path,
                name="test_video.mp4",
                material_type="video"
            )
            
            material_id = manager.add_material(material)
            print(f"✓ 添加视频素材: {material_id}")
            
            # 获取素材列表
            videos = manager.get_materials_by_type("video")
            print(f"✓ 视频素材数量: {len(videos)}")
            
            if videos:
                video = videos[0]
                print(f"  - 文件名: {video.get('extra_info')}")
                print(f"  - 尺寸: {video.get('width')}x{video.get('height')}")
                print(f"  - 时长: {video.get('duration', 0)/1000000:.2f}秒")
        else:
            print("⚠ 测试视频文件不存在，跳过素材测试")
        
        # 保存项目
        if manager.save_meta_data():
            print("✓ 项目保存成功")
        else:
            print("✗ 项目保存失败")

def test_gui_imports():
    """测试GUI相关导入"""
    print("\n=== 测试GUI导入 ===")
    
    try:
        import tkinter as tk
        print("✓ tkinter 可用")
        
        # 测试创建根窗口（不显示）
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        from tkinter import ttk, filedialog, messagebox, scrolledtext
        print("✓ tkinter 子模块可用")
        
        root.destroy()
        
    except ImportError as e:
        print(f"✗ tkinter 导入失败: {e}")
        return False
    
    try:
        from draft_manager_gui import DraftManagerGUI
        print("✓ DraftManagerGUI 类导入成功")
        return True
    except ImportError as e:
        print(f"✗ DraftManagerGUI 导入失败: {e}")
        return False

def test_file_operations():
    """测试文件操作"""
    print("\n=== 测试文件操作 ===")
    
    # 查找测试文件
    resource_dir = Path("/home/imeep/mixvideo/workspace/resources")
    
    if resource_dir.exists():
        video_files = list(resource_dir.rglob("*.mp4"))[:3]
        print(f"✓ 找到 {len(video_files)} 个视频文件")
        
        for video_file in video_files:
            print(f"  - {video_file.name}: {video_file.stat().st_size} bytes")
    else:
        print("⚠ 资源目录不存在")
    
    # 测试临时目录创建
    with tempfile.TemporaryDirectory() as temp_dir:
        test_project = Path(temp_dir) / "gui_test_project"
        test_project.mkdir(parents=True, exist_ok=True)
        print(f"✓ 创建测试目录: {test_project}")

def main():
    """主测试函数"""
    print("=== 剪映草稿管理器GUI测试 ===")
    
    # 测试基本导入
    if not test_gui_imports():
        print("\n❌ GUI导入测试失败，无法继续")
        return
    
    # 测试基本功能
    test_basic_functionality()
    
    # 测试文件操作
    test_file_operations()
    
    print("\n=== 测试完成 ===")
    print("如果所有测试都通过，GUI应该可以正常使用")
    print("运行 'python run_draft_manager.py' 启动GUI界面")

if __name__ == "__main__":
    main()
