#!/usr/bin/env python3
"""
视频素材智能分配算法

根据提示词要求，将 resources 目录下的视频文件智能分配到 draft_content.json 模板文件的 material.videos 数组中。

主要功能：
1. 扫描 resources 目录获取所有视频文件
2. 分析 templates 目录中的模板文件
3. 智能分配视频到模板的 videos 数组中
4. 确保全局唯一性、避免连续重复、支持1-2个不连续位置占用
5. 保存结果到 outputs 目录，复制使用的视频到 Resources/videoAlg
"""

import os
import json
import shutil
import random

from pathlib import Path
from typing import List, Tuple, Set
from dataclasses import dataclass
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class VideoFile:
    """视频文件信息"""
    path: str
    name: str
    relative_path: str
    size: int = 0

@dataclass
class TemplateInfo:
    """模板信息"""
    name: str
    path: str
    draft_content_path: str
    video_positions: int  # 需要填充的视频位置数量

@dataclass
class AllocationResult:
    """分配结果"""
    template_name: str
    video_assignments: List[Tuple[int, VideoFile]]  # (位置索引, 视频文件)
    total_positions: int
    videos_used: int

class VideoAllocationAlgorithm:
    """视频素材智能分配算法"""

    def __init__(self, workspace_dir: str = "workspace", original_materials_dir: str = None):
        self.workspace_dir = Path(workspace_dir)
        self.resources_dir = self.workspace_dir / "resources"
        self.templates_dir = self.workspace_dir / "templates"
        self.outputs_dir = self.workspace_dir / "outputs"

        # 原始素材目录（用于路径映射）
        self.original_materials_dir = Path(original_materials_dir) if original_materials_dir else None

        # 支持的视频格式
        self.video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}

        # 全局使用的视频集合（确保每个视频只使用一次）
        self.used_videos: Set[str] = set()

        # 分配结果
        self.allocation_results: List[AllocationResult] = []

    def _map_to_original_path(self, temp_path: str) -> str:
        """
        将临时目录路径映射回原始路径

        Args:
            temp_path: 临时目录中的文件路径

        Returns:
            原始路径
        """
        if not self.original_materials_dir:
            return temp_path

        try:
            temp_path_obj = Path(temp_path)

            # 检查是否是临时目录中的路径
            if "resources" in temp_path_obj.parts:
                # 找到 resources 部分的索引
                parts = temp_path_obj.parts
                resources_index = -1
                for i, part in enumerate(parts):
                    if part == "resources":
                        resources_index = i
                        break

                if resources_index >= 0 and resources_index < len(parts) - 1:
                    # 提取 resources 之后的相对路径
                    relative_parts = parts[resources_index + 1:]
                    relative_path = Path(*relative_parts)

                    # 构建原始路径
                    original_path = self.original_materials_dir / relative_path

                    logger.debug(f"路径映射: {temp_path} -> {original_path}")
                    return str(original_path)

            return temp_path

        except Exception as e:
            logger.warning(f"路径映射失败: {temp_path}, {e}")
            return temp_path
    
    def scan_video_resources(self) -> List[VideoFile]:
        """扫描 resources 目录获取所有视频文件"""
        video_files = []
        
        if not self.resources_dir.exists():
            logger.error(f"Resources 目录不存在: {self.resources_dir}")
            return video_files
        
        logger.info(f"扫描视频资源目录: {self.resources_dir}")
        
        for root, _, files in os.walk(self.resources_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.video_extensions:
                    relative_path = file_path.relative_to(self.resources_dir)
                    video_file = VideoFile(
                        path=str(file_path),
                        name=file,
                        relative_path=str(relative_path),
                        size=file_path.stat().st_size if file_path.exists() else 0
                    )
                    video_files.append(video_file)
        
        logger.info(f"找到 {len(video_files)} 个视频文件")
        return video_files
    
    def scan_templates(self) -> List[TemplateInfo]:
        """扫描 templates 目录获取模板信息"""
        templates = []
        
        if not self.templates_dir.exists():
            logger.error(f"Templates 目录不存在: {self.templates_dir}")
            return templates
        
        logger.info(f"扫描模板目录: {self.templates_dir}")
        
        for template_dir in self.templates_dir.iterdir():
            if template_dir.is_dir():
                draft_content_path = template_dir / "draft_content.json"
                if draft_content_path.exists():
                    try:
                        # 分析 draft_content.json 获取视频位置数量
                        video_positions = self._analyze_draft_content(draft_content_path)
                        template_info = TemplateInfo(
                            name=template_dir.name,
                            path=str(template_dir),
                            draft_content_path=str(draft_content_path),
                            video_positions=video_positions
                        )
                        templates.append(template_info)
                        logger.info(f"模板 '{template_dir.name}' 需要 {video_positions} 个视频位置")
                    except Exception as e:
                        logger.error(f"分析模板 {template_dir.name} 失败: {e}")
        
        logger.info(f"找到 {len(templates)} 个有效模板")
        return templates
    
    def _analyze_draft_content(self, draft_path: Path) -> int:
        """分析 draft_content.json 文件，获取需要的视频位置数量 - 只处理 materials.videos"""
        try:
            with open(draft_path, 'r', encoding='utf-8') as f:
                content = json.load(f)

            # 只分析 materials.videos 数组，排除图片文件
            materials = content.get('materials', {})
            videos = materials.get('videos', [])

            if not videos:
                logger.warning(f"未找到 materials.videos 数组: {draft_path}")
                return 0

            # 图片文件扩展名
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg'}

            # 过滤掉图片文件，只计算真正的视频位置
            video_count = 0
            for video in videos:
                path = video.get('path', '')
                if path:
                    # 获取文件扩展名
                    file_ext = Path(path).suffix.lower()
                    # 只计算非图片文件
                    if file_ext not in image_extensions:
                        video_count += 1
                else:
                    # 如果没有路径，也算作视频位置（可能是占位符）
                    video_count += 1

            logger.debug(f"materials.videos 总条目: {len(videos)}, 视频位置: {video_count}")
            return video_count
        except Exception as e:
            logger.error(f"分析 draft_content.json 失败: {e}")
            return 0
    
    def calculate_video_allocation(self, video_positions: int, available_video_count: int = None) -> List[Tuple[int, int]]:
        """
        计算视频分配方案 - 优化版本，尽量使用更多视频

        Args:
            video_positions: 总的视频位置数量
            available_video_count: 可用视频数量（用于优化分配策略）

        Returns:
            List[Tuple[int, int]]: [(起始位置, 占用位置数), ...]
        """
        if video_positions <= 0:
            return []

        allocations = []
        occupied_positions = set()

        # 计算目标视频数量 - 尽量使用更多视频
        if available_video_count:
            # 如果知道可用视频数量，尽量多用视频，但不超过位置数
            target_video_count = min(video_positions, available_video_count)
            # 如果视频很多，可以适当减少每个视频的占用位置数
            max_positions_per_video = 1 if available_video_count > video_positions * 0.8 else 2
        else:
            # 默认策略：使用较多视频
            target_video_count = max(1, int(video_positions * random.uniform(0.7, 0.9)))
            max_positions_per_video = 2

        # 生成随机位置列表
        available_positions = list(range(video_positions))
        random.shuffle(available_positions)

        videos_allocated = 0
        i = 0

        while videos_allocated < target_video_count and i < len(available_positions):
            position = available_positions[i]

            if position in occupied_positions:
                i += 1
                continue

            # 动态调整占用2个位置的概率
            remaining_videos_needed = target_video_count - videos_allocated
            remaining_positions = len([p for p in available_positions[i:] if p not in occupied_positions])

            # 如果剩余位置多于剩余需要的视频，降低占用2个位置的概率
            double_position_probability = 0.2 if remaining_positions > remaining_videos_needed * 1.5 else 0.1

            # 决定是否占用2个位置
            if (max_positions_per_video == 2 and
                random.random() < double_position_probability and
                videos_allocated < target_video_count - 1):  # 确保至少还能分配一个视频

                # 尝试找一个不连续的位置
                second_pos = None
                for j in range(i + 1, len(available_positions)):
                    candidate = available_positions[j]
                    if (candidate not in occupied_positions and
                        abs(candidate - position) > 1):  # 确保不连续
                        second_pos = candidate
                        break

                if second_pos is not None:
                    # 占用2个不连续位置
                    allocations.append((position, 1))
                    allocations.append((second_pos, 1))
                    occupied_positions.add(position)
                    occupied_positions.add(second_pos)
                    # 从可用位置中移除第二个位置
                    available_positions.remove(second_pos)
                else:
                    # 只占用1个位置
                    allocations.append((position, 1))
                    occupied_positions.add(position)
            else:
                # 占用1个位置
                allocations.append((position, 1))
                occupied_positions.add(position)

            videos_allocated += 1
            i += 1

        # 按位置排序
        allocations.sort(key=lambda x: x[0])
        return allocations
    
    def allocate_videos_to_template(self, template: TemplateInfo, available_videos: List[VideoFile]) -> AllocationResult:
        """为单个模板分配视频"""
        logger.info(f"为模板 '{template.name}' 分配视频 (需要 {template.video_positions} 个位置)")

        # 使用优化后的位置数（如果存在）
        effective_positions = getattr(template, 'effective_positions', template.video_positions)

        # 获取当前可用视频数量
        available_videos_copy = [v for v in available_videos if v.path not in self.used_videos]
        current_available_count = len(available_videos_copy)

        # 计算分配方案，传递可用视频数量信息
        allocation_plan = self.calculate_video_allocation(effective_positions, current_available_count)

        # 需要的视频数量
        videos_needed = len(allocation_plan)

        if current_available_count < videos_needed:
            logger.warning(f"可用视频不足！需要 {videos_needed} 个，只有 {current_available_count} 个可用")
            videos_needed = current_available_count

        if videos_needed == 0:
            logger.warning(f"模板 '{template.name}' 没有可用视频进行分配")
            return AllocationResult(
                template_name=template.name,
                video_assignments=[],
                total_positions=template.video_positions,
                videos_used=0
            )

        selected_videos = random.sample(available_videos_copy, videos_needed)

        # 创建分配结果
        video_assignments = []
        for i, (position, _) in enumerate(allocation_plan[:videos_needed]):
            video_assignments.append((position, selected_videos[i]))
            self.used_videos.add(selected_videos[i].path)

        result = AllocationResult(
            template_name=template.name,
            video_assignments=video_assignments,
            total_positions=template.video_positions,
            videos_used=len(selected_videos)
        )

        logger.info(f"模板 '{template.name}' 分配完成: 使用了 {len(selected_videos)} 个视频 (剩余可用: {current_available_count - videos_needed})")
        return result
    
    def execute_allocation(self, video_files=None, templates=None, project_manager=None) -> bool:
        """执行完整的视频分配流程 - 最大化视频生成数量

        Args:
            video_files: 预先扫描的视频文件列表，如果为None则重新扫描
            templates: 预先扫描的模板列表，如果为None则重新扫描
            project_manager: 项目管理器实例，用于处理模板资源变更
        """
        try:
            logger.info("开始执行视频素材智能分配算法 - 目标：最大化视频生成数量")

            # 1. 获取视频资源（复用或重新扫描）
            if video_files is None:
                video_files = self.scan_video_resources()
                if not video_files:
                    logger.error("没有找到视频文件")
                    return False
            else:
                logger.info(f"复用预扫描的视频资源: {len(video_files)} 个")

            # 2. 获取模板（复用或重新扫描）
            if templates is None:
                templates = self.scan_templates()
                if not templates:
                    logger.error("没有找到有效模板")
                    return False
            else:
                logger.info(f"复用预扫描的模板: {len(templates)} 个")

            # 保存project_manager引用，用于后续模板资源更新
            self.project_manager = project_manager

            # 3. 计算最大可生成视频数量
            max_videos = self._calculate_max_video_generation(templates, len(video_files))
            logger.info(f"可用视频素材: {len(video_files)} 个")
            logger.info(f"预计最大可生成视频数量: {max_videos} 个")

            # 4. 执行多轮分配，直到视频用完或无法继续
            round_num = 1
            while len(video_files) > 0 and self._can_continue_allocation(templates, video_files):
                logger.info(f"\n=== 第 {round_num} 轮分配 ===")
                round_results = self._execute_allocation_round(templates, video_files, round_num)

                if not round_results:
                    logger.info("无法继续分配，结束")
                    break

                self.allocation_results.extend(round_results)
                round_num += 1

            # 5. 保存结果
            self._save_results()

            # 6. 生成报告
            self._generate_report()

            total_generated = len(self.allocation_results)
            logger.info(f"视频分配算法执行完成 - 共生成 {total_generated} 个视频")
            return True

        except Exception as e:
            logger.error(f"执行分配算法失败: {e}")
            return False

    def _calculate_max_video_generation(self, templates: List[TemplateInfo], available_videos: int) -> int:
        """计算最大可生成的视频数量 - 基于最小化素材使用策略"""
        # 按模板所需视频数量排序（从少到多）
        template_needs = []
        for template in templates:
            min_videos_needed = max(1, int(template.video_positions * 0.2))  # 最少只需要20%的位置
            template_needs.append((template.name, min_videos_needed))

        template_needs.sort(key=lambda x: x[1])  # 按需求量排序

        # 贪心算法计算最大生成数量
        max_count = 0
        remaining_videos = available_videos

        while remaining_videos > 0:
            allocated_this_round = False
            for _, min_needed in template_needs:
                if remaining_videos >= min_needed:
                    remaining_videos -= min_needed
                    max_count += 1
                    allocated_this_round = True
                    break

            if not allocated_this_round:
                break

        return max_count

    def _can_continue_allocation(self, templates: List[TemplateInfo], video_files: List[VideoFile]) -> bool:
        """检查是否还能继续分配"""
        available_videos = [v for v in video_files if v.path not in self.used_videos]
        if len(available_videos) == 0:
            return False

        # 检查是否至少有一个模板可以用剩余视频完成
        for template in templates:
            min_needed = max(1, int(template.video_positions * 0.3))
            if len(available_videos) >= min_needed:
                return True

        return False

    def _execute_allocation_round(self, templates: List[TemplateInfo], video_files: List[VideoFile], round_num: int) -> List[AllocationResult]:
        """执行一轮分配"""
        round_results = []
        available_videos = [v for v in video_files if v.path not in self.used_videos]

        logger.info(f"第 {round_num} 轮开始，可用视频: {len(available_videos)} 个")

        # 按模板所需视频数量排序（优先分配需求少的模板）
        templates_sorted = sorted(templates, key=lambda t: self._estimate_template_min_videos(t))

        for template in templates_sorted:
            current_available = [v for v in video_files if v.path not in self.used_videos]
            if len(current_available) == 0:
                break

            min_needed = self._estimate_template_min_videos(template)
            if len(current_available) >= min_needed:
                # 为这个模板创建一个视频
                result = self._allocate_single_video(template, video_files, round_num)
                if result and result.videos_used > 0:
                    round_results.append(result)
                    logger.info(f"  ✓ 使用模板 '{template.name}' 生成视频 #{len(self.allocation_results) + len(round_results)}")

        logger.info(f"第 {round_num} 轮完成，生成了 {len(round_results)} 个视频")
        return round_results

    def _estimate_template_min_videos(self, template: TemplateInfo) -> int:
        """估算模板最少需要的视频数量 - 每个视频最多占2个位置"""
        # 计算最少需要的视频数量：向上取整(位置数 / 2)
        # 例如：5个位置 -> ceil(5/2) = 3个视频
        # 例如：8个位置 -> ceil(8/2) = 4个视频
        import math
        return math.ceil(template.video_positions / 2)

    def _allocate_single_video(self, template: TemplateInfo, video_files: List[VideoFile], round_num: int) -> AllocationResult:
        """为单个模板分配视频生成一个视频作品 - 严格按最少视频数量分配"""
        template_name = f"{template.name}_第{round_num}轮_{len(self.allocation_results) + 1}"

        logger.debug(f"为模板 '{template.name}' 分配视频 (第{round_num}轮)")

        # 获取当前可用视频
        available_videos = [v for v in video_files if v.path not in self.used_videos]

        # 计算最少需要的视频数量（严格按数学公式）
        min_videos_needed = self._estimate_template_min_videos(template)

        # 严格使用最少数量的视频
        target_videos = min(min_videos_needed, len(available_videos))

        if target_videos == 0:
            return None

        # 随机选择视频
        selected_videos = random.sample(available_videos, target_videos)

        # 智能分配位置：确保所有位置都被填充，每个视频最多占2个位置
        video_assignments = []
        positions_to_fill = template.video_positions

        for i, video in enumerate(selected_videos):
            # 计算这个视频应该占用多少个位置
            remaining_videos = len(selected_videos) - i
            remaining_positions = positions_to_fill

            if remaining_videos == 1:
                # 最后一个视频，占用所有剩余位置（但不超过2个）
                positions_for_this_video = min(2, remaining_positions)
            else:
                # 不是最后一个视频，计算合理的位置数
                max_positions_for_this_video = min(2, remaining_positions - (remaining_videos - 1))
                positions_for_this_video = max(1, max_positions_for_this_video)

            # 随机选择位置
            available_positions = [p for p in range(template.video_positions)
                                 if not any(p == pos for pos, _ in video_assignments)]
            selected_positions = random.sample(available_positions,
                                             min(positions_for_this_video, len(available_positions)))

            # 添加分配
            for position in selected_positions:
                video_assignments.append((position, video))
                positions_to_fill -= 1

            self.used_videos.add(video.path)

        result = AllocationResult(
            template_name=template_name,
            video_assignments=video_assignments,
            total_positions=template.video_positions,
            videos_used=len(selected_videos)
        )

        return result

    def _estimate_video_needs(self, templates: List[TemplateInfo]) -> int:
        """估算所需的视频数量"""
        total_needed = 0
        for template in templates:
            allocation_plan = self.calculate_video_allocation(template.video_positions)
            total_needed += len(allocation_plan)
        return total_needed

    def _optimize_allocation_strategy(self, templates: List[TemplateInfo], available_count: int):
        """优化分配策略以适应有限的视频资源"""
        # 按模板重要性排序（可以根据需要调整排序逻辑）
        templates.sort(key=lambda t: t.video_positions, reverse=True)

        # 重新计算每个模板的目标视频数量
        total_positions = sum(t.video_positions for t in templates)

        for template in templates:
            # 根据模板的相对重要性分配资源
            ratio = template.video_positions / total_positions
            target_videos = max(1, int(available_count * ratio * 0.8))  # 保留20%缓冲

            # 更新模板的有效视频位置数（用于后续分配）
            template.effective_positions = min(template.video_positions, target_videos * 2)
            logger.info(f"模板 '{template.name}' 优化后目标: {target_videos} 个视频 (原需求: {template.video_positions} 个位置)")

    def _save_results(self):
        """保存分配结果到 outputs 目录 - 使用管理器生成干净的输出"""
        logger.info("保存分配结果...")

        # 创建 outputs 目录
        self.outputs_dir.mkdir(exist_ok=True)

        for result in self.allocation_results:
            try:
                # 使用新的干净保存方法
                success = self._save_clean_template_result(result)
                if success:
                    logger.info(f"模板 '{result.template_name}' 结果保存完成")
                else:
                    logger.error(f"模板 '{result.template_name}' 保存失败")

            except Exception as e:
                logger.error(f"保存模板 '{result.template_name}' 结果失败: {e}")

    def _save_clean_template_result(self, result: AllocationResult) -> bool:
        """
        使用管理器保存干净的模板结果 - 只生成3个JSON文件

        Args:
            result: 分配结果

        Returns:
            是否保存成功
        """
        try:
            # 导入管理器
            from draft_meta_manager import DraftMetaManager
            from draft_content_manager import DraftContentManager

            # 创建输出目录
            output_dir = self.outputs_dir / result.template_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # 获取原始模板路径
            original_template_name = result.template_name.split('_第')[0]
            template_path = self.templates_dir / original_template_name

            if not template_path.exists():
                logger.error(f"模板目录不存在: {template_path}")
                return False

            # 模板文件路径
            template_content_file = template_path / "draft_content.json"
            template_meta_file = template_path / "draft_meta_info.json"
            template_virtual_file = template_path / "draft_virtual_store.json"

            if not template_content_file.exists():
                logger.error(f"模板内容文件不存在: {template_content_file}")
                return False

            # 1. 处理 draft_content.json
            success = self._create_clean_content_file(template_content_file, output_dir, result)
            if not success:
                return False

            # 2. 处理 draft_meta_info.json 和 draft_virtual_store.json
            success = self._create_clean_meta_files(template_meta_file, template_virtual_file, output_dir, result)
            if not success:
                return False

            # 3. 如果有project_manager，使用它来更新模板资源信息
            if hasattr(self, 'project_manager') and self.project_manager is not None:
                try:
                    logger.info(f"使用project_manager更新模板 '{result.template_name}' 的资源信息")
                    # 更新项目管理器中的资源信息
                    self.project_manager.update_project_resources(result.template_name, result.video_assignments)
                    logger.debug(f"模板资源更新完成: {result.template_name}")
                except Exception as e:
                    logger.warning(f"使用project_manager更新模板资源失败: {e}")
                    # 不影响主流程，继续执行

            logger.debug(f"干净输出完成: {output_dir} (仅包含3个JSON文件)")
            return True

        except Exception as e:
            logger.error(f"保存干净模板结果失败: {e}")
            return False

    def _create_clean_content_file(self, template_content_file: Path, output_dir: Path, result: AllocationResult) -> bool:
        """创建干净的 draft_content.json 文件"""
        try:
            # 读取原始模板内容
            with open(template_content_file, 'r', encoding='utf-8') as f:
                content = json.load(f)

            # 更新视频路径
            materials = content.get('materials', {})
            videos = materials.get('videos', [])

            if videos:
                # 图片文件扩展名
                image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg'}

                # 创建视频位置映射（排除图片文件）
                video_positions = []
                for i, video in enumerate(videos):
                    video_path = video.get('path', '')
                    if video_path:
                        file_ext = Path(video_path).suffix.lower()
                        if file_ext not in image_extensions:
                            video_positions.append(i)

                # 从video_assignments中提取视频路径，并映射到原始路径
                allocated_videos = []
                for _, video_file in result.video_assignments:
                    original_path = self._map_to_original_path(video_file.path)
                    allocated_videos.append(original_path)

                # 更新视频路径
                allocated_index = 0
                for pos in video_positions:
                    if allocated_index < len(allocated_videos):
                        videos[pos]['path'] = allocated_videos[allocated_index]
                        logger.debug(f"更新 materials.videos[{pos}]: {allocated_videos[allocated_index]}")
                        allocated_index += 1

                logger.info(f"更新 materials.videos: {allocated_index} 个视频路径 (使用绝对路径，其他位置的视频未处理)")

            # 保存更新后的内容
            output_file = output_dir / "draft_content.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            logger.error(f"创建干净内容文件失败: {e}")
            return False

    def _create_clean_meta_files(self, template_meta_file: Path, template_virtual_file: Path,
                                output_dir: Path, result: AllocationResult) -> bool:
        """创建干净的 draft_meta_info.json 和 draft_virtual_store.json 文件"""
        try:
            # 更新 draft_meta_info.json 中的素材信息
            if template_meta_file.exists():
                with open(template_meta_file, 'r', encoding='utf-8') as f:
                    meta_content = json.load(f)

                # 读取已更新的 draft_content.json 来获取ID到路径的映射关系
                output_content_file = output_dir / "draft_content.json"
                id_to_path_mapping = {}
                if output_content_file.exists():
                    with open(output_content_file, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    id_to_path_mapping = self._extract_id_to_path_mapping_from_content(content)

                # 同步素材信息到 draft_meta_info.json
                updated_count = self._sync_materials_to_meta_info(meta_content, id_to_path_mapping)

                output_meta_file = output_dir / "draft_meta_info.json"
                with open(output_meta_file, 'w', encoding='utf-8') as f:
                    json.dump(meta_content, f, ensure_ascii=False, indent=2)

                logger.info(f"更新 draft_meta_info.json: {updated_count} 个视频路径")

            # 复制 draft_virtual_store.json
            if template_virtual_file.exists():
                with open(template_virtual_file, 'r', encoding='utf-8') as f:
                    virtual_content = json.load(f)

                output_virtual_file = output_dir / "draft_virtual_store.json"
                with open(output_virtual_file, 'w', encoding='utf-8') as f:
                    json.dump(virtual_content, f, ensure_ascii=False, indent=2)
            else:
                # 如果虚拟存储文件不存在，创建一个基本的
                virtual_content = {"store_data": {}}
                output_virtual_file = output_dir / "draft_virtual_store.json"
                with open(output_virtual_file, 'w', encoding='utf-8') as f:
                    json.dump(virtual_content, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            logger.error(f"创建干净元数据文件失败: {e}")
            return False

    def _extract_id_to_path_mapping_from_content(self, content: dict) -> dict:
        """从 draft_content.json 中提取 local_material_id 到 file_path 的映射关系"""
        id_to_path_mapping = {}
        try:
            # 从materials.videos中直接提取ID到路径的映射
            materials = content.get('materials', {})
            videos = materials.get('videos', [])

            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg'}

            for video in videos:
                if 'path' in video and 'local_material_id' in video:
                    video_path = video['path']
                    local_material_id = video.get('local_material_id', '')

                    if video_path and local_material_id and local_material_id.strip():
                        file_ext = Path(video_path).suffix.lower()
                        # 只处理视频文件，跳过图片文件
                        if file_ext not in image_extensions:
                            id_to_path_mapping[local_material_id] = video_path
                            logger.debug(f"ID映射: {local_material_id} -> {video_path}")

            logger.debug(f"从 draft_content.json 提取了 {len(id_to_path_mapping)} 个ID到路径的映射")
            return id_to_path_mapping

        except Exception as e:
            logger.error(f"从 draft_content.json 提取ID到路径映射失败: {e}")
            import traceback
            logger.error(f"详细错误: {traceback.format_exc()}")
            return {}

    def _extract_video_path_id_mapping_from_content(self, content: dict) -> list:
        """从 draft_content.json 中提取视频路径和local_material_id的映射关系"""
        video_path_id_mapping = []
        try:
            # 从materials.videos中提取视频路径
            materials = content.get('materials', {})
            videos = materials.get('videos', [])

            # 图片文件扩展名
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg'}

            video_paths = []
            for video in videos:
                if 'path' in video:
                    video_path = video['path']
                    if video_path:
                        file_ext = Path(video_path).suffix.lower()
                        # 只提取视频文件路径，跳过图片文件
                        if file_ext not in image_extensions:
                            video_paths.append(video_path)

            # 从tracks中提取local_material_id与视频路径的对应关系
            tracks = content.get('tracks', [])
            for track in tracks:
                segments = track.get('segments', [])
                for segment in segments:
                    local_material_id = segment.get('local_material_id', '')
                    material_name = segment.get('material_name', '')

                    if local_material_id and material_name:
                        # 查找对应的视频路径
                        for video_path in video_paths:
                            if Path(video_path).name == material_name:
                                video_path_id_mapping.append({
                                    'path': video_path,
                                    'local_material_id': local_material_id,
                                    'material_name': material_name
                                })
                                break

            logger.debug(f"从 draft_content.json 提取了 {len(video_path_id_mapping)} 个视频路径-ID映射")
            return video_path_id_mapping

        except Exception as e:
            logger.error(f"从 draft_content.json 提取视频路径-ID映射失败: {e}")
            return []

    def _sync_materials_to_meta_info(self, meta_content: dict, id_to_path_mapping: dict) -> int:
        """
        同步素材信息到 draft_meta_info.json

        Args:
            meta_content: draft_meta_info.json 的内容
            id_to_path_mapping: local_material_id 到 file_path 的映射关系

        Returns:
            更新的素材数量
        """
        try:
            updated_count = 0

            # 更新 draft_materials 部分
            if 'draft_materials' in meta_content and id_to_path_mapping:
                draft_materials = meta_content['draft_materials']

                # 查找视频素材类型 (type: 0 表示视频)
                for material_group in draft_materials:
                    if material_group.get('type') == 0 and 'value' in material_group:
                        videos = material_group['value']

                        for video_meta in videos:
                            if 'id' in video_meta and 'file_Path' in video_meta:
                                material_id = video_meta['id']

                                # 如果这个ID在映射中存在，则更新对应的路径
                                if material_id in id_to_path_mapping:
                                    new_video_path = id_to_path_mapping[material_id]
                                    old_path = video_meta['file_Path']

                                    # 更新路径
                                    video_meta['file_Path'] = new_video_path

                                    # 更新文件名相关字段
                                    video_meta['extra_info'] = Path(new_video_path).name

                                    # 更新修改时间为当前时间
                                    import time
                                    current_time = int(time.time())
                                    video_meta['create_time'] = current_time
                                    video_meta['import_time'] = current_time
                                    video_meta['import_time_ms'] = current_time * 1000000  # 微秒

                                    updated_count += 1
                                    logger.debug(f"同步素材ID {material_id}: {Path(old_path).name} -> {Path(new_video_path).name}")
                                else:
                                    logger.debug(f"素材ID {material_id} 在映射中不存在，保持原路径: {video_meta.get('file_Path', 'unknown')}")

            logger.debug(f"draft_meta_info.json 素材同步完成，更新了 {updated_count} 个素材")
            return updated_count

        except Exception as e:
            logger.error(f"同步素材信息到 draft_meta_info.json 失败: {e}")
            return 0

    def _generate_report(self):
        """生成分配报告"""
        logger.info("生成分配报告...")

        report = {
            "allocation_summary": {
                "total_templates": len(self.allocation_results),
                "total_videos_used": len(self.used_videos),
                "timestamp": str(Path().cwd())
            },
            "template_details": [],
            "video_usage": list(self.used_videos)
        }

        for result in self.allocation_results:
            template_detail = {
                "template_name": result.template_name,
                "total_positions": result.total_positions,
                "videos_used": result.videos_used,
                "assignments": [
                    {
                        "position": pos,
                        "video_name": video.name,
                        "video_path": video.relative_path
                    }
                    for pos, video in result.video_assignments
                ]
            }
            report["template_details"].append(template_detail)

        # 保存报告
        report_path = self.outputs_dir / "allocation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"分配报告已保存: {report_path}")

        # 打印摘要
        self._print_summary()

    def _print_summary(self):
        """打印分配摘要"""
        print("\n" + "="*60)
        print("视频素材智能分配算法 - 执行摘要")
        print("="*60)
        print(f"处理模板数量: {len(self.allocation_results)}")
        print(f"使用视频总数: {len(self.used_videos)}")
        print()

        for result in self.allocation_results:
            print(f"模板: {result.template_name}")
            print(f"  - 总位置数: {result.total_positions}")
            print(f"  - 使用视频: {result.videos_used}")
            print(f"  - 分配详情: {len(result.video_assignments)} 个位置已填充")
            print()

        print(f"结果保存位置: {self.outputs_dir}")
        print("="*60)

    def _preview_allocation(self) -> bool:
        """预览分配方案，不实际保存文件"""
        try:
            logger.info("预览视频分配方案...")

            # 1. 扫描视频资源
            video_files = self.scan_video_resources()
            if not video_files:
                logger.error("没有找到视频文件")
                return False

            # 2. 扫描模板
            templates = self.scan_templates()
            if not templates:
                logger.error("没有找到有效模板")
                return False

            # 3. 计算分配方案（不实际分配）
            print("\n" + "="*60)
            print("视频分配预览")
            print("="*60)
            print(f"可用视频总数: {len(video_files)}")
            print(f"模板总数: {len(templates)}")
            print()

            total_videos_needed = 0
            for template in templates:
                # 使用精确的最少视频计算：ceil(位置数/2)
                min_videos_needed = self._estimate_template_min_videos(template)
                total_videos_needed += min_videos_needed

                print(f"模板: {template.name}")
                print(f"  - 视频位置数: {template.video_positions}")
                print(f"  - 最少需要视频数: {min_videos_needed} (ceil({template.video_positions}/2))")
                print(f"  - 每轮固定使用: {min_videos_needed} 个视频")
                print()

            print(f"总计需要视频: {total_videos_needed}")

            if total_videos_needed > len(video_files):
                print("⚠️  警告: 可用视频数量不足！")
            else:
                print("✅ 视频数量充足")

            print("="*60)
            return True

        except Exception as e:
            logger.error(f"预览分配方案失败: {e}")
            return False


def main():
    """主函数"""
    algorithm = VideoAllocationAlgorithm()
    success = algorithm.execute_allocation()

    if success:
        print("✅ 视频分配算法执行成功！")
    else:
        print("❌ 视频分配算法执行失败！")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
