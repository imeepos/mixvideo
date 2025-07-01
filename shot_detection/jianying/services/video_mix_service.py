"""
Video Mix Service
视频混剪服务
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from loguru import logger

from .jianying_service import JianYingService


class VideoMixService:
    """视频混剪服务"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化视频混剪服务
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="VideoMixService")
        
        # 初始化剪映服务
        self.jianying_service = JianYingService(config)
        
        # 混剪配置
        self.mix_config = self.config.get('video_mix', {
            'min_clip_duration': 2.0,
            'max_clip_duration': 10.0,
            'transition_duration': 0.5,
            'auto_adjust_volume': True,
            'add_background_music': False
        })
        
        self.logger.info("Video mix service initialized")
    
    def create_mix_project(self, project_name: str, output_dir: str,
                          video_files: List[str], mix_strategy: str = "random",
                          progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        创建混剪项目
        
        Args:
            project_name: 项目名称
            output_dir: 输出目录
            video_files: 视频文件列表
            mix_strategy: 混剪策略 (random, sequential, smart)
            progress_callback: 进度回调函数
            
        Returns:
            创建结果
        """
        try:
            self.logger.info(f"Creating video mix project: {project_name}")
            
            if progress_callback:
                progress_callback(0.1, "分析视频文件...")
            
            # 分析视频文件
            video_analysis = self._analyze_videos(video_files)
            
            if progress_callback:
                progress_callback(0.3, "生成混剪方案...")
            
            # 生成混剪方案
            mix_plan = self._generate_mix_plan(video_analysis, mix_strategy)
            
            if progress_callback:
                progress_callback(0.5, "创建剪映项目...")
            
            # 创建剪映项目
            jianying_result = self.jianying_service.create_project(
                project_name=project_name,
                output_dir=output_dir,
                video_files=video_files,
                mix_plan=mix_plan,
                project_type="video_mix"
            )
            
            if not jianying_result["success"]:
                return jianying_result
            
            if progress_callback:
                progress_callback(0.7, "应用混剪配置...")
            
            # 应用混剪配置
            mix_result = self._apply_mix_configuration(
                jianying_result["project_path"], 
                mix_plan
            )
            
            if progress_callback:
                progress_callback(1.0, "混剪项目创建完成")
            
            self.logger.info(f"Video mix project created: {jianying_result['project_path']}")
            
            return {
                "success": True,
                "project_path": jianying_result["project_path"],
                "mix_plan": mix_plan,
                "video_analysis": video_analysis,
                "configuration_applied": mix_result["success"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create mix project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_videos(self, video_files: List[str]) -> Dict[str, Any]:
        """分析视频文件"""
        analysis = {
            "total_videos": len(video_files),
            "total_duration": 0.0,
            "video_info": []
        }
        
        for video_file in video_files:
            try:
                # 这里应该使用实际的视频分析工具
                # 暂时使用模拟数据
                video_info = {
                    "path": video_file,
                    "name": Path(video_file).name,
                    "duration": 30.0,  # 模拟时长
                    "resolution": (1920, 1080),  # 模拟分辨率
                    "fps": 30.0,  # 模拟帧率
                    "quality_score": 0.8  # 模拟质量分数
                }
                
                analysis["video_info"].append(video_info)
                analysis["total_duration"] += video_info["duration"]
                
            except Exception as e:
                self.logger.warning(f"Failed to analyze video {video_file}: {e}")
        
        return analysis
    
    def _generate_mix_plan(self, video_analysis: Dict[str, Any], 
                          strategy: str) -> Dict[str, Any]:
        """生成混剪方案"""
        video_info = video_analysis["video_info"]
        
        if strategy == "random":
            return self._generate_random_mix_plan(video_info)
        elif strategy == "sequential":
            return self._generate_sequential_mix_plan(video_info)
        elif strategy == "smart":
            return self._generate_smart_mix_plan(video_info)
        else:
            raise ValueError(f"Unknown mix strategy: {strategy}")
    
    def _generate_random_mix_plan(self, video_info: List[Dict]) -> Dict[str, Any]:
        """生成随机混剪方案"""
        import random
        
        clips = []
        for i, video in enumerate(video_info):
            # 随机选择片段
            clip_duration = random.uniform(
                self.mix_config['min_clip_duration'],
                min(self.mix_config['max_clip_duration'], video['duration'])
            )
            
            start_time = random.uniform(0, max(0, video['duration'] - clip_duration))
            
            clips.append({
                "video_index": i,
                "video_path": video["path"],
                "start_time": start_time,
                "duration": clip_duration,
                "transition": "fade" if i > 0 else "none"
            })
        
        # 随机打乱顺序
        random.shuffle(clips)
        
        return {
            "strategy": "random",
            "clips": clips,
            "total_clips": len(clips),
            "estimated_duration": sum(clip["duration"] for clip in clips)
        }
    
    def _generate_sequential_mix_plan(self, video_info: List[Dict]) -> Dict[str, Any]:
        """生成顺序混剪方案"""
        clips = []
        for i, video in enumerate(video_info):
            # 顺序选择片段
            clip_duration = min(
                self.mix_config['max_clip_duration'],
                video['duration']
            )
            
            clips.append({
                "video_index": i,
                "video_path": video["path"],
                "start_time": 0,
                "duration": clip_duration,
                "transition": "cut" if i > 0 else "none"
            })
        
        return {
            "strategy": "sequential",
            "clips": clips,
            "total_clips": len(clips),
            "estimated_duration": sum(clip["duration"] for clip in clips)
        }
    
    def _generate_smart_mix_plan(self, video_info: List[Dict]) -> Dict[str, Any]:
        """生成智能混剪方案"""
        # 根据视频质量分数排序
        sorted_videos = sorted(video_info, key=lambda x: x.get('quality_score', 0), reverse=True)
        
        clips = []
        for i, video in enumerate(sorted_videos):
            # 根据质量调整片段时长
            quality_factor = video.get('quality_score', 0.5)
            base_duration = self.mix_config['min_clip_duration']
            max_duration = self.mix_config['max_clip_duration']
            
            clip_duration = base_duration + (max_duration - base_duration) * quality_factor
            clip_duration = min(clip_duration, video['duration'])
            
            clips.append({
                "video_index": video_info.index(video),
                "video_path": video["path"],
                "start_time": 0,
                "duration": clip_duration,
                "transition": "fade" if i > 0 else "none",
                "quality_score": quality_factor
            })
        
        return {
            "strategy": "smart",
            "clips": clips,
            "total_clips": len(clips),
            "estimated_duration": sum(clip["duration"] for clip in clips)
        }
    
    def _apply_mix_configuration(self, project_path: str, 
                                mix_plan: Dict[str, Any]) -> Dict[str, Any]:
        """应用混剪配置到剪映项目"""
        try:
            # 加载项目
            load_result = self.jianying_service.load_project(project_path)
            if not load_result["success"]:
                return load_result
            
            project_data = load_result["project_data"]
            
            # 修改项目数据以应用混剪配置
            # 这里需要根据剪映的具体格式来修改
            # 暂时保存混剪方案到项目中
            if "draft_content" in project_data:
                project_data["draft_content"]["mix_plan"] = mix_plan
            
            # 更新项目
            update_result = self.jianying_service.update_project(
                project_path, 
                {"draft_content": project_data["draft_content"]}
            )
            
            return update_result
            
        except Exception as e:
            self.logger.error(f"Failed to apply mix configuration: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_mix_templates(self) -> List[Dict[str, Any]]:
        """获取混剪模板"""
        templates = [
            {
                "name": "快节奏混剪",
                "description": "适合音乐视频和宣传片",
                "strategy": "random",
                "config": {
                    "min_clip_duration": 1.0,
                    "max_clip_duration": 3.0,
                    "transition_duration": 0.2
                }
            },
            {
                "name": "故事性混剪", 
                "description": "保持视频的连贯性",
                "strategy": "sequential",
                "config": {
                    "min_clip_duration": 3.0,
                    "max_clip_duration": 8.0,
                    "transition_duration": 0.5
                }
            },
            {
                "name": "智能混剪",
                "description": "根据视频质量智能选择",
                "strategy": "smart",
                "config": {
                    "min_clip_duration": 2.0,
                    "max_clip_duration": 6.0,
                    "transition_duration": 0.3
                }
            }
        ]
        
        return templates
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'jianying_service'):
            self.jianying_service.cleanup()
        self.logger.info("Video mix service cleanup completed")
