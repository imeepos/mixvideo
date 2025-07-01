#!/usr/bin/env python3
"""
抖音视频制作工作流程 - 简化命令行工具

这是一个简化的命令行工具，用于快速运行抖音视频制作的完整工作流程。
"""

import sys
import argparse
from pathlib import Path

# 导入主工作流程
from run_allocation import DouyinVideoWorkflow


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="抖音视频制作工作流程 - 一键运行",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎬 抖音视频制作完整工作流程:

  1️⃣  扫描 resources/ 目录获取视频资源清单
  2️⃣  管理 templates/ 目录下的抖音项目模板  
  3️⃣  智能分配视频素材到模板中
  4️⃣  将生成的项目输出到 outputs/ 目录

📁 目录结构要求:
  your_project/
  ├── resources/          # 视频素材目录
  │   ├── 素材1/
  │   ├── 素材2/
  │   └── ...
  ├── templates/          # 抖音项目模板目录
  │   ├── 5个镜头/
  │   ├── 6个镜头/
  │   └── ...
  └── outputs/           # 输出目录 (自动创建)
      ├── 生成的项目1/
      ├── 生成的项目2/
      └── ...

🚀 使用示例:
  python douyin_workflow.py                    # 在当前目录运行
  python douyin_workflow.py -d /path/to/work   # 指定工作目录
  python douyin_workflow.py --preview          # 预览模式，不实际生成
  python douyin_workflow.py -v                 # 显示详细日志
        """
    )
    
    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='工作目录路径 (默认: 当前目录)'
    )
    
    parser.add_argument(
        '--preview',
        action='store_true',
        help='预览模式：只分析不生成文件'
    )
    
    parser.add_argument(
        '--formats',
        nargs='+',
        default=['json', 'html'],
        choices=['json', 'csv', 'html', 'markdown', 'excel'],
        help='资源清单输出格式 (默认: json html)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 检查工作目录
    work_dir = Path(args.directory).resolve()
    if not work_dir.exists():
        print(f"❌ 工作目录不存在: {work_dir}")
        return 1
    
    # 检查必要的子目录
    resources_dir = work_dir / "resources"
    templates_dir = work_dir / "templates"
    
    if not resources_dir.exists():
        print(f"❌ 资源目录不存在: {resources_dir}")
        print("💡 请确保在工作目录下创建 resources/ 目录并放入视频素材")
        return 1
    
    if not templates_dir.exists():
        print(f"❌ 模板目录不存在: {templates_dir}")
        print("💡 请确保在工作目录下创建 templates/ 目录并放入抖音项目模板")
        return 1
    
    print("🎬 抖音视频制作工作流程")
    print("=" * 50)
    print(f"📁 工作目录: {work_dir}")
    print(f"📹 资源目录: {resources_dir}")
    print(f"📋 模板目录: {templates_dir}")
    print(f"📤 输出目录: {work_dir / 'outputs'}")
    
    if args.preview:
        print("🔍 预览模式 - 不会实际生成文件")
    
    print("=" * 50)
    
    try:
        # 创建工作流程实例
        workflow = DouyinVideoWorkflow(str(work_dir))
        
        if args.preview:
            # 预览模式：只运行前两个步骤
            print("🔍 预览模式：分析资源和模板...")
            
            # 步骤1: 扫描资源
            inventory = workflow.step1_scan_resources(args.formats)
            if not inventory:
                print("❌ 无法扫描资源")
                return 1
            
            # 步骤2: 管理模板
            project_manager = workflow.step2_manage_templates()
            if not project_manager:
                print("❌ 无法管理模板")
                return 1
            
            # 显示预览信息
            stats = inventory['statistics']
            summary = project_manager.get_project_summary()
            
            print("\n📊 资源统计:")
            print(f"  - 视频文件: {stats['video_count']} 个")
            print(f"  - 音频文件: {stats['audio_count']} 个")
            print(f"  - 图片文件: {stats['image_count']} 个")
            print(f"  - 总大小: {stats['total_size_mb']} MB")
            
            print("\n📋 模板统计:")
            print(f"  - 有效模板: {summary['valid_projects']} 个")
            print(f"  - 无效模板: {summary['invalid_projects']} 个")
            
            if summary['valid_project_names']:
                print("\n✅ 有效模板列表:")
                for name in summary['valid_project_names']:
                    print(f"  - {name}")
            
            if summary['invalid_project_info']:
                print("\n❌ 无效模板列表:")
                for info in summary['invalid_project_info']:
                    print(f"  - {info['name']}: {info['error']}")
            
            print("\n🔍 预览完成！如需实际生成，请去掉 --preview 参数")
            
        else:
            # 正常模式：运行完整工作流程
            success = workflow.run_complete_workflow(args.formats)
            
            if success:
                print("\n🎉 工作流程执行成功！")
                print(f"📁 查看生成的项目: {work_dir / 'outputs'}")
                return 0
            else:
                print("\n❌ 工作流程执行失败！")
                return 1
    
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
        return 1
    except Exception as e:
        print(f"\n💥 执行过程中发生错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
