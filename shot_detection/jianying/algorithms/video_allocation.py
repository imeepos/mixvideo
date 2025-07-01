"""
Video Allocation Algorithm
视频分配算法 - 重构版本
"""

import random
from typing import Dict, List, Any, Optional
from loguru import logger

from ..video_allocation_algorithm import VideoAllocationAlgorithm as LegacyAlgorithm


class VideoAllocationAlgorithm:
    """视频分配算法 - 新架构版本"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化视频分配算法
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="VideoAllocationAlgorithm")
        
        # 保持与旧版本的兼容性
        self.legacy_algorithm = LegacyAlgorithm()
        
        # 算法配置
        self.algorithm_config = self.config.get('allocation', {
            'strategy': 'smart',  # smart, random, sequential
            'max_videos_per_position': 2,
            'min_video_usage': 1,
            'avoid_consecutive_duplicates': True,
            'quality_weight': 0.3,
            'diversity_weight': 0.4,
            'randomness_weight': 0.3
        })
        
        self.logger.info("Video allocation algorithm initialized")
    
    def allocate_videos(self, video_inventory: List[Dict[str, Any]],
                       template_positions: List[Dict[str, Any]],
                       strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        分配视频到模板位置
        
        Args:
            video_inventory: 视频库存列表
            template_positions: 模板位置列表
            strategy: 分配策略
            
        Returns:
            分配结果
        """
        try:
            strategy = strategy or self.algorithm_config['strategy']
            self.logger.info(f"Starting video allocation with strategy: {strategy}")
            
            # 预处理数据
            processed_inventory = self._preprocess_inventory(video_inventory)
            processed_positions = self._preprocess_positions(template_positions)
            
            # 根据策略选择分配方法
            if strategy == 'smart':
                allocation_result = self._smart_allocation(processed_inventory, processed_positions)
            elif strategy == 'random':
                allocation_result = self._random_allocation(processed_inventory, processed_positions)
            elif strategy == 'sequential':
                allocation_result = self._sequential_allocation(processed_inventory, processed_positions)
            elif strategy == 'legacy':
                # 使用旧版算法
                return self._use_legacy_algorithm(video_inventory, template_positions)
            else:
                raise ValueError(f"Unknown allocation strategy: {strategy}")
            
            # 后处理和验证
            validated_result = self._validate_allocation(allocation_result)
            
            # 生成分配统计
            statistics = self._generate_allocation_statistics(validated_result)
            
            self.logger.info(f"Video allocation completed: {statistics['total_allocations']} allocations")
            
            return {
                "success": True,
                "strategy": strategy,
                "allocations": validated_result,
                "statistics": statistics,
                "quality_score": statistics.get('quality_score', 0.0)
            }
            
        except Exception as e:
            self.logger.error(f"Video allocation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "strategy": strategy
            }
    
    def _preprocess_inventory(self, video_inventory: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """预处理视频库存"""
        processed = []
        
        for i, video in enumerate(video_inventory):
            processed_video = {
                "id": i,
                "path": video.get("path", ""),
                "name": video.get("name", f"video_{i}"),
                "duration": video.get("duration", 0.0),
                "quality_score": video.get("quality_score", 0.5),
                "usage_count": 0,
                "last_used_position": -1,
                "metadata": video.get("metadata", {})
            }
            processed.append(processed_video)
        
        return processed
    
    def _preprocess_positions(self, template_positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """预处理模板位置"""
        processed = []
        
        for i, position in enumerate(template_positions):
            processed_position = {
                "id": i,
                "template_id": position.get("template_id", ""),
                "position_index": position.get("position_index", i),
                "required_duration": position.get("duration", 0.0),
                "preferences": position.get("preferences", {}),
                "constraints": position.get("constraints", {})
            }
            processed.append(processed_position)
        
        return processed
    
    def _smart_allocation(self, inventory: List[Dict[str, Any]], 
                         positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """智能分配算法"""
        allocations = []
        
        # 计算每个视频的综合分数
        for video in inventory:
            video['composite_score'] = self._calculate_composite_score(video)
        
        # 按综合分数排序
        sorted_inventory = sorted(inventory, key=lambda x: x['composite_score'], reverse=True)
        
        for position in positions:
            # 为每个位置选择最佳视频
            best_video = self._select_best_video_for_position(
                sorted_inventory, position, allocations
            )
            
            if best_video:
                allocation = {
                    "position_id": position["id"],
                    "video_id": best_video["id"],
                    "video_path": best_video["path"],
                    "allocation_score": best_video['composite_score'],
                    "allocation_reason": "smart_selection"
                }
                allocations.append(allocation)
                
                # 更新视频使用状态
                best_video['usage_count'] += 1
                best_video['last_used_position'] = position["id"]
        
        return allocations
    
    def _random_allocation(self, inventory: List[Dict[str, Any]], 
                          positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """随机分配算法"""
        allocations = []
        available_videos = inventory.copy()
        
        for position in positions:
            if not available_videos:
                # 如果视频用完了，重新开始
                available_videos = inventory.copy()
                for video in available_videos:
                    video['usage_count'] = 0
            
            # 随机选择视频
            selected_video = random.choice(available_videos)
            
            allocation = {
                "position_id": position["id"],
                "video_id": selected_video["id"],
                "video_path": selected_video["path"],
                "allocation_score": random.random(),
                "allocation_reason": "random_selection"
            }
            allocations.append(allocation)
            
            # 更新使用状态
            selected_video['usage_count'] += 1
            
            # 如果达到最大使用次数，移除该视频
            max_usage = self.algorithm_config.get('max_videos_per_position', 2)
            if selected_video['usage_count'] >= max_usage:
                available_videos.remove(selected_video)
        
        return allocations
    
    def _sequential_allocation(self, inventory: List[Dict[str, Any]], 
                              positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """顺序分配算法"""
        allocations = []
        video_index = 0
        
        for position in positions:
            # 循环使用视频
            if video_index >= len(inventory):
                video_index = 0
            
            selected_video = inventory[video_index]
            
            allocation = {
                "position_id": position["id"],
                "video_id": selected_video["id"],
                "video_path": selected_video["path"],
                "allocation_score": 1.0 - (video_index / len(inventory)),
                "allocation_reason": "sequential_selection"
            }
            allocations.append(allocation)
            
            # 更新使用状态
            selected_video['usage_count'] += 1
            video_index += 1
        
        return allocations
    
    def _calculate_composite_score(self, video: Dict[str, Any]) -> float:
        """计算视频的综合分数"""
        quality_score = video.get('quality_score', 0.5)
        usage_penalty = video.get('usage_count', 0) * 0.1
        
        # 综合分数计算
        composite_score = (
            quality_score * self.algorithm_config['quality_weight'] +
            (1.0 - usage_penalty) * self.algorithm_config['diversity_weight'] +
            random.random() * self.algorithm_config['randomness_weight']
        )
        
        return max(0.0, min(1.0, composite_score))
    
    def _select_best_video_for_position(self, inventory: List[Dict[str, Any]],
                                       position: Dict[str, Any],
                                       existing_allocations: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """为位置选择最佳视频"""
        # 过滤可用视频
        available_videos = []
        max_usage = self.algorithm_config.get('max_videos_per_position', 2)
        
        for video in inventory:
            if video['usage_count'] < max_usage:
                # 检查是否避免连续重复
                if self.algorithm_config.get('avoid_consecutive_duplicates', True):
                    if self._is_consecutive_duplicate(video, position, existing_allocations):
                        continue
                
                available_videos.append(video)
        
        if not available_videos:
            return None
        
        # 选择分数最高的视频
        return max(available_videos, key=lambda x: x['composite_score'])
    
    def _is_consecutive_duplicate(self, video: Dict[str, Any], 
                                 position: Dict[str, Any],
                                 existing_allocations: List[Dict[str, Any]]) -> bool:
        """检查是否为连续重复"""
        position_id = position["id"]
        
        # 检查前一个位置是否使用了同一个视频
        if position_id > 0:
            for allocation in existing_allocations:
                if (allocation["position_id"] == position_id - 1 and 
                    allocation["video_id"] == video["id"]):
                    return True
        
        return False
    
    def _use_legacy_algorithm(self, video_inventory: List[Dict[str, Any]],
                             template_positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用旧版算法"""
        try:
            # 转换数据格式以适配旧版算法
            legacy_result = self.legacy_algorithm.allocate_videos(
                video_inventory, template_positions
            )
            
            return {
                "success": legacy_result.get("success", False),
                "strategy": "legacy",
                "allocations": legacy_result.get("allocations", []),
                "statistics": legacy_result.get("statistics", {}),
                "legacy_result": True
            }
            
        except Exception as e:
            self.logger.error(f"Legacy algorithm failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "strategy": "legacy"
            }
    
    def _validate_allocation(self, allocations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """验证分配结果"""
        validated = []
        
        for allocation in allocations:
            # 基本验证
            if all(key in allocation for key in ["position_id", "video_id", "video_path"]):
                validated.append(allocation)
            else:
                self.logger.warning(f"Invalid allocation skipped: {allocation}")
        
        return validated
    
    def _generate_allocation_statistics(self, allocations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成分配统计"""
        if not allocations:
            return {
                "total_allocations": 0,
                "unique_videos_used": 0,
                "average_score": 0.0,
                "quality_score": 0.0
            }
        
        video_ids = [alloc["video_id"] for alloc in allocations]
        unique_videos = len(set(video_ids))
        
        scores = [alloc.get("allocation_score", 0.0) for alloc in allocations]
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        # 计算质量分数（基于分配的均匀性和分数）
        quality_score = min(1.0, average_score * (unique_videos / len(allocations)))
        
        return {
            "total_allocations": len(allocations),
            "unique_videos_used": unique_videos,
            "average_score": average_score,
            "quality_score": quality_score,
            "video_usage_distribution": self._calculate_usage_distribution(video_ids)
        }
    
    def _calculate_usage_distribution(self, video_ids: List[int]) -> Dict[str, int]:
        """计算视频使用分布"""
        from collections import Counter
        usage_count = Counter(video_ids)
        
        distribution = {}
        for video_id, count in usage_count.items():
            distribution[f"video_{video_id}"] = count
        
        return distribution
    
    def get_allocation_strategies(self) -> List[Dict[str, Any]]:
        """获取可用的分配策略"""
        strategies = [
            {
                "name": "smart",
                "display_name": "智能分配",
                "description": "基于视频质量和多样性的智能分配",
                "recommended_for": ["高质量内容", "多样化需求"]
            },
            {
                "name": "random",
                "display_name": "随机分配", 
                "description": "随机选择视频进行分配",
                "recommended_for": ["快速生成", "实验性内容"]
            },
            {
                "name": "sequential",
                "display_name": "顺序分配",
                "description": "按顺序循环使用视频",
                "recommended_for": ["均匀分布", "简单需求"]
            },
            {
                "name": "legacy",
                "display_name": "兼容模式",
                "description": "使用旧版分配算法",
                "recommended_for": ["向后兼容", "已有配置"]
            }
        ]
        
        return strategies
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("Video allocation algorithm cleanup completed")
