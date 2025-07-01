#!/usr/bin/env python3
"""
剪映项目管理命令行工具

提供命令行界面来管理剪映项目
"""

import argparse
import json
import sys
import os
from pathlib import Path
import logging

# 导入剪映管理器
from jianying.jianying_project_manager import JianyingProjectManager


def setup_logging(verbose=False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def scan_command(args):
    """扫描项目命令"""
    print(f"扫描目录: {args.directory}")
    
    manager = JianyingProjectManager(args.directory)
    projects = manager.scan_projects()
    
    if not projects:
        print("未发现任何项目")
        return
    
    # 显示项目列表
    valid_projects = [p for p in projects if p.is_valid]
    invalid_projects = [p for p in projects if not p.is_valid]
    
    print(f"\n发现 {len(projects)} 个项目:")
    print(f"  有效项目: {len(valid_projects)}")
    print(f"  无效项目: {len(invalid_projects)}")
    
    if args.verbose:
        print("\n=== 有效项目 ===")
        for project in valid_projects:
            print(f"  {project.name} -> {project.path}")
        
        if invalid_projects:
            print("\n=== 无效项目 ===")
            for project in invalid_projects:
                print(f"  {project.name} -> {project.error_message}")
    
    # 保存摘要
    if args.output:
        summary = manager.get_project_summary()
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"\n项目摘要已保存到: {args.output}")


def list_command(args):
    """列出项目命令"""
    manager = JianyingProjectManager(args.directory)
    projects = manager.scan_projects()
    
    if not projects:
        print("未发现任何项目")
        return
    
    # 根据参数过滤项目
    if args.valid_only:
        projects = [p for p in projects if p.is_valid]
    elif args.invalid_only:
        projects = [p for p in projects if not p.is_valid]
    
    # 显示项目
    for project in projects:
        status = "✓" if project.is_valid else "✗"
        print(f"{status} {project.name}")
        
        if args.verbose:
            print(f"    路径: {project.path}")
            if not project.is_valid:
                print(f"    错误: {project.error_message}")
            print()


def info_command(args):
    """显示项目信息命令"""
    manager = JianyingProjectManager(args.directory)
    manager.scan_projects()
    
    project = manager.get_project(args.project_name)
    if not project:
        print(f"项目不存在: {args.project_name}")
        return
    
    print(f"项目名称: {project.name}")
    print(f"项目路径: {project.path}")
    print(f"状态: {'有效' if project.is_valid else '无效'}")
    
    if not project.is_valid:
        print(f"错误信息: {project.error_message}")
        return
    
    # 显示文件信息
    print("\n文件信息:")
    for file_path, name in [
        (project.draft_content_path, "draft_content.json"),
        (project.draft_meta_info_path, "draft_meta_info.json"),
        (project.draft_virtual_store_path, "draft_virtual_store.json")
    ]:
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  {name}: {size:,} 字节")
        else:
            print(f"  {name}: 文件不存在")
    
    # 显示详细信息
    if args.detailed:
        try:
            content_mgr = manager.get_project_content_manager(project.name)
            meta_mgr = manager.get_project_meta_manager(project.name)
            
            if content_mgr:
                print("\n内容信息:")
                content_info = content_mgr.get_project_info()
                print(f"  时长: {content_info.get('duration', 0) / 1000000:.2f} 秒")
                print(f"  轨道数: {len(content_info.get('tracks', []))}")
                print(f"  素材数: {len(content_info.get('materials', []))}")
            
            if meta_mgr:
                print("\n元数据信息:")
                meta_info = meta_mgr.get_project_info()
                print(f"  创建时间: {meta_info.get('create_time', 'N/A')}")
                print(f"  修改时间: {meta_info.get('update_time', 'N/A')}")
                
                materials = meta_mgr.get_all_materials()
                print(f"  素材总数: {len(materials)}")
                
                # 按类型统计素材
                material_types = {}
                for material in materials:
                    mat_type = material.get('metetype', 'unknown')
                    material_types[mat_type] = material_types.get(mat_type, 0) + 1
                
                for mat_type, count in material_types.items():
                    print(f"    {mat_type}: {count} 个")
        
        except Exception as e:
            print(f"\n获取详细信息时出错: {e}")


def create_command(args):
    """创建项目命令"""
    manager = JianyingProjectManager(args.directory)
    
    print(f"创建项目: {args.project_name}")
    
    try:
        if manager.create_new_project(args.project_name):
            print("项目创建成功")
        else:
            print("项目创建失败")
            sys.exit(1)
    except Exception as e:
        print(f"创建项目时出错: {e}")
        sys.exit(1)


def delete_command(args):
    """删除项目命令"""
    manager = JianyingProjectManager(args.directory)
    manager.scan_projects()
    
    project = manager.get_project(args.project_name)
    if not project:
        print(f"项目不存在: {args.project_name}")
        return
    
    # 确认删除
    if not args.force:
        response = input(f"确定要删除项目 '{args.project_name}' 吗？这将永久删除项目文件夹及其所有内容！(y/N): ")
        if response.lower() != 'y':
            print("取消删除")
            return
    
    try:
        if manager.delete_project(args.project_name):
            print("项目删除成功")
        else:
            print("项目删除失败")
            sys.exit(1)
    except Exception as e:
        print(f"删除项目时出错: {e}")
        sys.exit(1)


def export_command(args):
    """导出项目命令"""
    manager = JianyingProjectManager(args.directory)
    manager.scan_projects()
    
    project = manager.get_project(args.project_name)
    if not project:
        print(f"项目不存在: {args.project_name}")
        return
    
    if not project.is_valid:
        print(f"项目无效: {project.error_message}")
        return
    
    # 导出项目文件
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        import shutil
        
        # 复制项目文件
        for file_path, name in [
            (project.draft_content_path, "draft_content.json"),
            (project.draft_meta_info_path, "draft_meta_info.json"),
            (project.draft_virtual_store_path, "draft_virtual_store.json")
        ]:
            if file_path.exists():
                shutil.copy2(file_path, output_dir / name)
                print(f"导出: {name}")
        
        print(f"项目已导出到: {output_dir}")
        
    except Exception as e:
        print(f"导出项目时出错: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="剪映项目管理命令行工具")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 扫描命令
    scan_parser = subparsers.add_parser("scan", help="扫描项目目录")
    scan_parser.add_argument("directory", help="项目目录路径")
    scan_parser.add_argument("-o", "--output", help="保存摘要到文件")
    scan_parser.set_defaults(func=scan_command)
    
    # 列出命令
    list_parser = subparsers.add_parser("list", help="列出项目")
    list_parser.add_argument("directory", help="项目目录路径")
    list_parser.add_argument("--valid-only", action="store_true", help="只显示有效项目")
    list_parser.add_argument("--invalid-only", action="store_true", help="只显示无效项目")
    list_parser.set_defaults(func=list_command)
    
    # 信息命令
    info_parser = subparsers.add_parser("info", help="显示项目信息")
    info_parser.add_argument("directory", help="项目目录路径")
    info_parser.add_argument("project_name", help="项目名称")
    info_parser.add_argument("-d", "--detailed", action="store_true", help="显示详细信息")
    info_parser.set_defaults(func=info_command)
    
    # 创建命令
    create_parser = subparsers.add_parser("create", help="创建新项目")
    create_parser.add_argument("directory", help="项目目录路径")
    create_parser.add_argument("project_name", help="项目名称")
    create_parser.set_defaults(func=create_command)
    
    # 删除命令
    delete_parser = subparsers.add_parser("delete", help="删除项目")
    delete_parser.add_argument("directory", help="项目目录路径")
    delete_parser.add_argument("project_name", help="项目名称")
    delete_parser.add_argument("-f", "--force", action="store_true", help="强制删除，不询问确认")
    delete_parser.set_defaults(func=delete_command)
    
    # 导出命令
    export_parser = subparsers.add_parser("export", help="导出项目")
    export_parser.add_argument("directory", help="项目目录路径")
    export_parser.add_argument("project_name", help="项目名称")
    export_parser.add_argument("output", help="导出目录")
    export_parser.set_defaults(func=export_command)
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 设置日志
    setup_logging(args.verbose)
    
    # 执行命令
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"执行命令时出错: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
