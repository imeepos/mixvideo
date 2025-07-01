#!/usr/bin/env python3
"""
剪映项目管理系统演示

展示如何使用剪映项目管理系统的各种功能
"""

import os
import tempfile
import shutil
from pathlib import Path

# 导入剪映管理器
from jianying.jianying_project_manager import JianyingProjectManager


def demo_basic_usage():
    """演示基本用法"""
    print("🎬 剪映项目管理系统演示")
    print("=" * 50)
    
    # 创建临时演示目录
    demo_dir = Path(tempfile.mkdtemp(prefix="jianying_demo_"))
    print(f"演示目录: {demo_dir}")
    
    try:
        # 1. 创建项目管理器
        print("\n1. 创建项目管理器...")
        manager = JianyingProjectManager(demo_dir)
        
        # 2. 创建几个测试项目
        print("\n2. 创建测试项目...")
        projects_to_create = [
            "我的第一个视频",
            "产品展示视频",
            "旅行记录",
            "教学视频"
        ]
        
        for project_name in projects_to_create:
            success = manager.create_new_project(project_name)
            status = "✅ 成功" if success else "❌ 失败"
            print(f"   创建 '{project_name}': {status}")
        
        # 3. 扫描项目
        print("\n3. 扫描项目...")
        projects = manager.scan_projects()
        print(f"   发现 {len(projects)} 个项目")
        
        # 4. 显示项目列表
        print("\n4. 项目列表:")
        for project in projects:
            status = "✅ 有效" if project.is_valid else "❌ 无效"
            print(f"   - {project.name}: {status}")
            if not project.is_valid:
                print(f"     错误: {project.error_message}")
        
        # 5. 获取项目详情
        print("\n5. 项目详情:")
        valid_projects = manager.get_valid_projects()
        
        if valid_projects:
            project = valid_projects[0]
            print(f"   项目名称: {project.name}")
            print(f"   项目路径: {project.path}")
            
            # 获取管理器
            content_mgr = manager.get_project_content_manager(project.name)
            meta_mgr = manager.get_project_meta_manager(project.name)
            
            if content_mgr:
                info = content_mgr.get_project_info()
                print(f"   项目时长: {info.get('duration', 0) / 1000000:.2f} 秒")
                print(f"   轨道数量: {len(info.get('tracks', []))}")
            
            if meta_mgr:
                materials = meta_mgr.get_all_materials()
                print(f"   素材数量: {len(materials)}")
        
        # 6. 项目摘要
        print("\n6. 项目摘要:")
        summary = manager.get_project_summary()
        print(f"   基础目录: {summary['base_directory']}")
        print(f"   总项目数: {summary['total_projects']}")
        print(f"   有效项目: {summary['valid_projects']}")
        print(f"   无效项目: {summary['invalid_projects']}")
        
        # 7. 演示删除项目
        print("\n7. 删除项目演示...")
        if valid_projects:
            project_to_delete = valid_projects[-1].name
            print(f"   删除项目: {project_to_delete}")
            success = manager.delete_project(project_to_delete)
            status = "✅ 成功" if success else "❌ 失败"
            print(f"   删除结果: {status}")
            
            # 重新扫描验证
            projects = manager.scan_projects()
            print(f"   删除后剩余项目: {len(projects)} 个")
        
        print("\n✅ 演示完成！")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理演示目录
        if demo_dir.exists():
            shutil.rmtree(demo_dir)
        print(f"\n🧹 已清理演示目录: {demo_dir}")


def demo_advanced_usage():
    """演示高级用法"""
    print("\n🚀 高级功能演示")
    print("=" * 50)
    
    demo_dir = Path(tempfile.mkdtemp(prefix="jianying_advanced_"))
    print(f"演示目录: {demo_dir}")
    
    try:
        manager = JianyingProjectManager(demo_dir)
        
        # 1. 使用模板创建项目
        print("\n1. 使用模板创建项目...")
        template_data = {
            "duration": 60000000,  # 60秒
            "resolution": {"width": 1080, "height": 1920},
            "fps": 30
        }
        
        success = manager.create_new_project("模板项目", template_data)
        print(f"   模板项目创建: {'✅ 成功' if success else '❌ 失败'}")
        
        # 2. 项目内容管理
        print("\n2. 项目内容管理...")
        projects = manager.scan_projects()
        
        if projects:
            project = projects[0]
            content_mgr = manager.get_project_content_manager(project.name)
            
            if content_mgr:
                # 获取项目信息
                info = content_mgr.get_project_info()
                print(f"   项目ID: {info.get('id', 'N/A')}")
                print(f"   项目时长: {info.get('duration', 0) / 1000000:.2f} 秒")
                
                # 获取轨道摘要
                track_summary = content_mgr.get_tracks_summary()
                print(f"   轨道摘要:")
                for track_type, data in track_summary.get('track_types', {}).items():
                    print(f"     {track_type}: {data['count']} 个轨道")
        
        # 3. 元数据管理
        print("\n3. 元数据管理...")
        if projects:
            project = projects[0]
            meta_mgr = manager.get_project_meta_manager(project.name)
            
            if meta_mgr:
                # 获取项目信息
                project_info = meta_mgr.get_project_info()
                print(f"   项目名称: {project_info.get('project_name', 'N/A')}")
                print(f"   创建时间: {project_info.get('create_time', 'N/A')}")
                print(f"   修改时间: {project_info.get('modified_time', 'N/A')}")
                
                # 获取素材信息
                materials = meta_mgr.get_all_materials()
                print(f"   素材总数: {len(materials)}")
        
        print("\n✅ 高级功能演示完成！")
        
    except Exception as e:
        print(f"\n❌ 高级演示过程中出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if demo_dir.exists():
            shutil.rmtree(demo_dir)
        print(f"\n🧹 已清理演示目录: {demo_dir}")


def demo_cli_usage():
    """演示命令行用法"""
    print("\n💻 命令行工具演示")
    print("=" * 50)
    
    print("剪映项目管理命令行工具支持以下操作:")
    print()
    
    print("📁 扫描项目:")
    print("   python jianying_cli.py scan /path/to/projects")
    print("   python jianying_cli.py scan /path/to/projects -v -o summary.json")
    print()
    
    print("📋 列出项目:")
    print("   python jianying_cli.py list /path/to/projects")
    print("   python jianying_cli.py list /path/to/projects --valid-only")
    print("   python jianying_cli.py list /path/to/projects --invalid-only -v")
    print()
    
    print("ℹ️ 查看项目信息:")
    print("   python jianying_cli.py info /path/to/projects project_name")
    print("   python jianying_cli.py info /path/to/projects project_name --detailed")
    print()
    
    print("➕ 创建新项目:")
    print("   python jianying_cli.py create /path/to/projects new_project_name")
    print()
    
    print("🗑️ 删除项目:")
    print("   python jianying_cli.py delete /path/to/projects project_name")
    print("   python jianying_cli.py delete /path/to/projects project_name --force")
    print()
    
    print("📤 导出项目:")
    print("   python jianying_cli.py export /path/to/projects project_name /export/path")
    print()


def demo_gui_usage():
    """演示GUI用法"""
    print("\n🖥️ GUI界面演示")
    print("=" * 50)
    
    print("剪映项目管理GUI提供以下功能:")
    print()
    
    print("🎯 主要功能:")
    print("   • 直观的项目列表显示")
    print("   • 项目有效性验证")
    print("   • 项目详情查看")
    print("   • 创建和删除项目")
    print("   • 导出项目摘要")
    print("   • 实时日志显示")
    print()
    
    print("📱 界面布局:")
    print("   • 项目列表标签页 - 显示所有项目")
    print("   • 项目详情标签页 - 查看项目详细信息")
    print("   • 日志标签页 - 显示操作日志")
    print()
    
    print("🚀 启动方式:")
    print("   python jianying_manager_gui.py")
    print()
    
    print("💡 使用提示:")
    print("   1. 点击'浏览'选择剪映项目目录")
    print("   2. 点击'扫描'扫描项目")
    print("   3. 在项目列表中查看所有项目")
    print("   4. 双击项目查看详情")
    print("   5. 右键菜单进行项目操作")
    print()


def main():
    """主演示函数"""
    print("🎬 剪映项目管理系统完整演示")
    print("=" * 60)
    
    # 基本用法演示
    demo_basic_usage()
    
    # 高级用法演示
    demo_advanced_usage()
    
    # 命令行用法演示
    demo_cli_usage()
    
    # GUI用法演示
    demo_gui_usage()
    
    print("\n🎉 演示完成！")
    print("\n📚 更多信息请查看:")
    print("   • JIANYING_MANAGER_README.md - 详细文档")
    print("   • jianying_cli.py --help - 命令行帮助")
    print("   • jianying_manager_gui.py - GUI界面")
    print("\n✨ 剪映项目管理系统让您轻松管理大量剪映项目！")


if __name__ == "__main__":
    main()
