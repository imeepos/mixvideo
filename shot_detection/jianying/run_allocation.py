#!/usr/bin/env python3
"""
抖音视频制作完整工作流程

整合以下功能的主工作流脚本：
1. 扫描resources获取资源清单 (media_scanner.py)
2. 创建抖音项目管理根目录是templates (jianying_project_manager.py)
3. 利用video_allocation_algorithm.py算法替换模板里的视频
4. 将结果输出到outputs目录
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any

# 导入本地模块
from media_scanner import MediaScanner
from jianying_project_manager import JianyingProjectManager
from video_allocation_algorithm import VideoAllocationAlgorithm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('douyin_workflow.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class DouyinVideoWorkflow:
    """抖音视频制作完整工作流程"""

    def __init__(self, base_dir: str = ".", original_materials_dir: str = None):
        """
        初始化工作流程

        Args:
            base_dir: 基础工作目录，默认为当前目录
            original_materials_dir: 原始素材目录（用于路径映射）
        """
        self.base_dir = Path(base_dir).resolve()
        self.resources_dir = self.base_dir / "resources"
        self.templates_dir = self.base_dir / "templates"
        self.outputs_dir = self.base_dir / "outputs"
        self.original_materials_dir = original_materials_dir

        # 确保必要目录存在
        self.outputs_dir.mkdir(exist_ok=True)

        logger.info(f"初始化抖音视频工作流程")
        logger.info(f"基础目录: {self.base_dir}")
        logger.info(f"资源目录: {self.resources_dir}")
        logger.info(f"模板目录: {self.templates_dir}")
        logger.info(f"输出目录: {self.outputs_dir}")

    def _detect_scan_directory(self) -> Path:
        """
        智能检测扫描目录

        优先级：
        1. 如果 base_dir/resources 存在，使用它
        2. 如果 base_dir 本身包含视频文件，使用 base_dir
        3. 否则返回 None

        Returns:
            扫描目录路径或None
        """
        # 检查标准的 resources 目录
        if self.resources_dir.exists():
            logger.info(f"使用标准资源目录: {self.resources_dir}")
            return self.resources_dir

        # 检查 base_dir 是否直接包含视频文件
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        has_videos = False

        try:
            for item in self.base_dir.iterdir():
                if item.is_file() and item.suffix.lower() in video_extensions:
                    has_videos = True
                    break
                elif item.is_dir():
                    # 检查子目录是否包含视频文件
                    for sub_item in item.iterdir():
                        if sub_item.is_file() and sub_item.suffix.lower() in video_extensions:
                            has_videos = True
                            break
                    if has_videos:
                        break
        except Exception as e:
            logger.warning(f"检查目录时出错: {e}")

        if has_videos:
            logger.info(f"检测到用户直接选择了素材目录: {self.base_dir}")
            logger.info("将直接扫描该目录而不是 resources 子目录")
            return self.base_dir

        logger.error(f"在 {self.base_dir} 和 {self.resources_dir} 中都未找到视频文件")
        return None

    def step1_scan_resources(self, output_formats: list = None) -> Dict[str, Any]:
        """
        步骤1: 扫描resources获取资源清单

        Args:
            output_formats: 输出格式列表，默认为 ['json', 'html']

        Returns:
            资源清单字典
        """
        logger.info("=" * 60)
        logger.info("步骤1: 扫描resources获取资源清单")
        logger.info("=" * 60)

        # 智能检测扫描目录
        scan_dir = self._detect_scan_directory()
        if not scan_dir:
            logger.error("无法找到有效的扫描目录")
            return {}

        if output_formats is None:
            output_formats = ['json', 'html']

        try:
            # 使用媒体扫描器扫描资源
            scanner = MediaScanner(include_hash=False, include_metadata=True)
            media_files = scanner.scan_directory(scan_dir, recursive=True)
            inventory = scanner.generate_inventory(media_files)

            # 保存多种格式的清单
            for format_type in output_formats:
                output_file = self.outputs_dir / f"media_inventory.{format_type}"
                scanner.save_inventory(inventory, output_file, format_type)
                logger.info(f"资源清单已保存: {output_file}")

            # 打印统计信息
            stats = inventory['statistics']
            logger.info(f"扫描完成:")
            logger.info(f"  - 总文件数: {stats['total_files']}")
            logger.info(f"  - 视频文件: {stats['video_count']}")
            logger.info(f"  - 音频文件: {stats['audio_count']}")
            logger.info(f"  - 图片文件: {stats['image_count']}")
            logger.info(f"  - 总大小: {stats['total_size_mb']} MB")

            return inventory

        except Exception as e:
            logger.error(f"扫描资源失败: {e}")
            return {}

    def step2_manage_templates(self) -> JianyingProjectManager:
        """
        步骤2: 创建抖音项目管理根目录是templates

        Returns:
            项目管理器实例
        """
        logger.info("=" * 60)
        logger.info("步骤2: 管理抖音项目模板")
        logger.info("=" * 60)

        if not self.templates_dir.exists():
            logger.error(f"模板目录不存在: {self.templates_dir}")
            return None

        try:
            # 创建项目管理器
            project_manager = JianyingProjectManager(self.templates_dir)

            # 扫描项目
            project_manager.scan_projects()

            # 获取项目摘要
            summary = project_manager.get_project_summary()

            logger.info(f"项目扫描完成:")
            logger.info(f"  - 总项目数: {summary['total_projects']}")
            logger.info(f"  - 有效项目: {summary['valid_projects']}")
            logger.info(f"  - 无效项目: {summary['invalid_projects']}")

            # 保存项目摘要
            summary_file = self.outputs_dir / "project_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            logger.info(f"项目摘要已保存: {summary_file}")

            # 列出有效项目
            for project_name in summary['valid_project_names']:
                logger.info(f"  ✓ 有效项目: {project_name}")

            # 列出无效项目
            for invalid_info in summary['invalid_project_info']:
                logger.warning(f"  ✗ 无效项目: {invalid_info['name']} - {invalid_info['error']}")

            return project_manager

        except Exception as e:
            logger.error(f"管理模板失败: {e}")
            return None

    def step3_allocate_videos(self, inventory=None, project_manager=None) -> bool:
        """
        步骤3: 利用video_allocation_algorithm.py算法替换模板里的视频

        Args:
            inventory: 步骤1的资源清单结果，如果为None则重新扫描
            project_manager: 步骤2的项目管理器结果，如果为None则重新创建

        Returns:
            分配是否成功
        """
        logger.info("=" * 60)
        logger.info("步骤3: 智能分配视频到模板")
        logger.info("=" * 60)

        try:
            # 创建视频分配算法实例，使用当前目录作为workspace，传递原始素材目录
            algorithm = VideoAllocationAlgorithm(str(self.base_dir), self.original_materials_dir)

            # 如果提供了前面步骤的结果，则记录复用信息
            if inventory is not None:
                logger.info("复用步骤1的资源清单结果")
                stats = inventory.get('statistics', {})
                logger.info(f"  - 已知视频文件: {stats.get('video_count', 0)} 个")
                logger.info(f"  - 已知总大小: {stats.get('total_size_mb', 0)} MB")

            if project_manager is not None:
                logger.info("复用步骤2的项目管理器结果")
                summary = project_manager.get_project_summary()
                logger.info(f"  - 已知有效模板: {summary.get('valid_projects', 0)} 个")
                logger.info(f"  - 已知无效模板: {summary.get('invalid_projects', 0)} 个")

            # 准备传递给算法的参数
            video_files = None
            templates = None

            # 如果有inventory，从中提取视频文件信息
            if inventory is not None:
                try:
                    # 从inventory中重建video_files列表
                    video_files = self._extract_video_files_from_inventory(inventory)
                    logger.info(f"从inventory提取了 {len(video_files)} 个视频文件")
                except Exception as e:
                    logger.warning(f"从inventory提取视频文件失败: {e}，将重新扫描")
                    video_files = None

            # 如果有project_manager，从中提取模板信息
            if project_manager is not None:
                try:
                    # 从project_manager中重建templates列表
                    templates = self._extract_templates_from_project_manager(project_manager)
                    logger.info(f"从project_manager提取了 {len(templates)} 个模板")
                except Exception as e:
                    logger.warning(f"从project_manager提取模板失败: {e}，将重新扫描")
                    templates = None

            # 执行分配，传递预扫描的资源和模板信息
            logger.info("开始执行视频素材智能分配算法 - 目标：最大化视频生成数量")
            success = algorithm.execute_allocation(video_files, templates, project_manager)

            if success:
                logger.info("视频分配算法执行成功")

                # 生成分配报告
                total_generated = len(algorithm.allocation_results)
                total_videos_used = len(algorithm.used_videos)

                logger.info(f"分配结果:")
                logger.info(f"  - 生成视频数量: {total_generated}")
                logger.info(f"  - 使用视频素材: {total_videos_used}")

                return True
            else:
                logger.error("视频分配算法执行失败")
                return False

        except Exception as e:
            logger.error(f"视频分配失败: {e}")
            return False

    def _extract_video_files_from_inventory(self, inventory):
        """从inventory中提取VideoFile对象列表"""
        from video_allocation_algorithm import VideoFile

        video_files = []
        files_data = inventory.get('files', [])

        for file_data in files_data:
            if file_data.get('type') == 'video':
                try:
                    video_file = VideoFile(
                        path=file_data['path'],
                        name=file_data['name'],
                        size=file_data['size'],
                        duration=file_data.get('duration', 0.0),
                        resolution=file_data.get('resolution', ''),
                        format=file_data.get('format', '')
                    )
                    video_files.append(video_file)
                except Exception as e:
                    logger.warning(f"创建VideoFile对象失败: {file_data.get('path', 'unknown')}, {e}")

        return video_files

    def _extract_templates_from_project_manager(self, project_manager):
        """从project_manager中提取Template对象列表"""
        from video_allocation_algorithm import Template

        templates = []
        projects = project_manager.get_valid_projects_dict()

        for project_name, project_info in projects.items():
            try:
                # 计算模板需要的视频位置数
                video_positions = self._count_video_positions_in_template(project_info)

                template = Template(
                    name=project_name,
                    path=project_info.get('path', ''),
                    video_positions=video_positions,
                    effective_positions=video_positions
                )
                templates.append(template)
                logger.debug(f"从project_manager提取模板: {project_name}, 需要 {video_positions} 个视频位置")
            except Exception as e:
                logger.warning(f"创建Template对象失败: {project_name}, {e}")

        return templates

    def _count_video_positions_in_template(self, project_info):
        """计算模板中的视频位置数"""
        try:
            # 读取draft_content.json来计算视频位置
            content_file = Path(project_info['path']) / 'draft_content.json'
            if content_file.exists():
                import json
                with open(content_file, 'r', encoding='utf-8') as f:
                    content = json.load(f)

                # 计算materials.videos中的视频位置数（排除图片）
                materials = content.get('materials', {})
                videos = materials.get('videos', [])

                image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg'}
                video_positions = 0

                for video in videos:
                    video_path = video.get('path', '')
                    if video_path:
                        file_ext = Path(video_path).suffix.lower()
                        if file_ext not in image_extensions:
                            video_positions += 1

                return video_positions
            else:
                logger.warning(f"模板内容文件不存在: {content_file}")
                return 0
        except Exception as e:
            logger.warning(f"计算模板视频位置数失败: {e}")
            return 0

    def step4_finalize_outputs(self) -> bool:
        """
        步骤4: 整理和验证输出结果

        Returns:
            整理是否成功
        """
        logger.info("=" * 60)
        logger.info("步骤4: 整理输出结果")
        logger.info("=" * 60)

        try:
            # 检查outputs目录内容
            if not self.outputs_dir.exists():
                logger.error("输出目录不存在")
                return False

            output_items = list(self.outputs_dir.iterdir())
            logger.info(f"输出目录包含 {len(output_items)} 个项目:")

            # 统计不同类型的输出
            directories = []
            json_files = []
            other_files = []

            for item in output_items:
                if item.is_dir():
                    directories.append(item.name)
                elif item.suffix.lower() == '.json':
                    json_files.append(item.name)
                else:
                    other_files.append(item.name)

            logger.info(f"  - 生成的项目目录: {len(directories)} 个")
            for dir_name in directories:
                logger.info(f"    ✓ {dir_name}")

            logger.info(f"  - JSON报告文件: {len(json_files)} 个")
            for json_file in json_files:
                logger.info(f"    ✓ {json_file}")

            logger.info(f"  - 其他文件: {len(other_files)} 个")
            for other_file in other_files:
                logger.info(f"    ✓ {other_file}")

            # 生成最终报告
            final_report = {
                "workflow_summary": {
                    "timestamp": str(Path().cwd()),
                    "base_directory": str(self.base_dir),
                    "total_output_items": len(output_items),
                    "generated_projects": len(directories),
                    "report_files": len(json_files),
                    "other_files": len(other_files)
                },
                "generated_projects": directories,
                "report_files": json_files,
                "other_files": other_files
            }

            final_report_file = self.outputs_dir / "workflow_final_report.json"
            with open(final_report_file, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, ensure_ascii=False, indent=2)

            logger.info(f"最终报告已保存: {final_report_file}")
            return True

        except Exception as e:
            logger.error(f"整理输出失败: {e}")
            return False

    def run_complete_workflow(self, output_formats: list = None) -> bool:
        """
        运行完整的工作流程

        Args:
            output_formats: 资源清单输出格式

        Returns:
            工作流程是否成功完成
        """
        logger.info("🚀 开始执行抖音视频制作完整工作流程")
        logger.info("=" * 80)

        try:
            # 步骤1: 扫描资源
            inventory = self.step1_scan_resources(output_formats)
            if not inventory:
                logger.error("步骤1失败: 无法扫描资源")
                return False

            # 步骤2: 管理模板
            project_manager = self.step2_manage_templates()
            if not project_manager:
                logger.error("步骤2失败: 无法管理模板")
                return False
            
            # 步骤3: 分配视频 (复用前面步骤的结果)
            allocation_success = self.step3_allocate_videos(inventory, project_manager)
            if not allocation_success:
                logger.error("步骤3失败: 视频分配失败")
                return False

            # 步骤4: 整理输出
            finalize_success = self.step4_finalize_outputs()
            if not finalize_success:
                logger.error("步骤4失败: 整理输出失败")
                return False

            logger.info("=" * 80)
            logger.info("🎉 抖音视频制作完整工作流程执行成功！")
            logger.info(f"📁 查看结果: {self.outputs_dir}")
            logger.info("=" * 80)

            return True

        except Exception as e:
            logger.error(f"工作流程执行失败: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="抖音视频制作完整工作流程",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
工作流程步骤:
  1. 扫描resources获取资源清单
  2. 管理templates目录下的抖音项目模板
  3. 智能分配视频到模板
  4. 将结果输出到outputs目录

示例用法:
  python run_allocation.py                    # 使用当前目录
  python run_allocation.py -d /path/to/work   # 指定工作目录
  python run_allocation.py --formats json html csv  # 指定输出格式
  python run_allocation.py -v                 # 显示详细日志
        """
    )

    parser.add_argument(
        '-d', '--directory',
        default='.',
        help='工作目录路径 (默认: 当前目录)'
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
        logging.getLogger().setLevel(logging.DEBUG)

    # 检查工作目录
    work_dir = Path(args.directory).resolve()
    if not work_dir.exists():
        print(f"❌ 工作目录不存在: {work_dir}")
        return 1

    print(f"🚀 启动抖音视频制作工作流程")
    print(f"📁 工作目录: {work_dir}")
    print(f"📋 输出格式: {', '.join(args.formats)}")

    # 创建工作流程实例
    workflow = DouyinVideoWorkflow(str(work_dir))

    # 运行完整工作流程
    success = workflow.run_complete_workflow(args.formats)

    if success:
        print("✅ 工作流程执行成功！")
        return 0
    else:
        print("❌ 工作流程执行失败！")
        return 1


if __name__ == "__main__":
    sys.exit(main())
