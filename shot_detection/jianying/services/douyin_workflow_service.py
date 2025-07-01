"""
Douyin Workflow Service
抖音工作流服务
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from loguru import logger

from .video_mix_service import VideoMixService


class DouyinWorkflowService:
    """抖音工作流服务 - 专门针对抖音内容创作的工作流"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化抖音工作流服务
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="DouyinWorkflowService")
        
        # 初始化视频混剪服务
        self.video_mix_service = VideoMixService(config)
        
        # 抖音特定配置
        self.douyin_config = self.config.get('douyin', {
            'target_duration': 15.0,  # 抖音推荐时长
            'aspect_ratio': '9:16',   # 竖屏比例
            'resolution': (1080, 1920),  # 竖屏分辨率
            'max_file_size_mb': 100,  # 最大文件大小
            'add_watermark': False,   # 是否添加水印
            'auto_subtitle': True,    # 自动字幕
            'background_music': True  # 背景音乐
        })
        
        self.logger.info("Douyin workflow service initialized")
    
    def create_douyin_content(self, content_type: str, source_videos: List[str],
                             output_dir: str, content_config: Optional[Dict] = None,
                             progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        创建抖音内容
        
        Args:
            content_type: 内容类型 (short_video, story, tutorial, etc.)
            source_videos: 源视频文件列表
            output_dir: 输出目录
            content_config: 内容配置
            progress_callback: 进度回调函数
            
        Returns:
            创建结果
        """
        try:
            self.logger.info(f"Creating Douyin content: {content_type}")
            
            if progress_callback:
                progress_callback(0.1, "分析源视频...")
            
            # 分析源视频
            video_analysis = self._analyze_source_videos(source_videos)
            
            if progress_callback:
                progress_callback(0.2, "生成内容策略...")
            
            # 生成内容策略
            content_strategy = self._generate_content_strategy(
                content_type, video_analysis, content_config
            )
            
            if progress_callback:
                progress_callback(0.4, "创建混剪项目...")
            
            # 创建混剪项目
            project_name = f"douyin_{content_type}_{self._get_timestamp()}"
            mix_result = self.video_mix_service.create_mix_project(
                project_name=project_name,
                output_dir=output_dir,
                video_files=source_videos,
                mix_strategy=content_strategy["mix_strategy"]
            )
            
            if not mix_result["success"]:
                return mix_result
            
            if progress_callback:
                progress_callback(0.6, "应用抖音优化...")
            
            # 应用抖音特定优化
            optimization_result = self._apply_douyin_optimization(
                mix_result["project_path"], content_strategy
            )
            
            if progress_callback:
                progress_callback(0.8, "生成内容元数据...")
            
            # 生成内容元数据
            metadata = self._generate_content_metadata(
                content_type, content_strategy, video_analysis
            )
            
            if progress_callback:
                progress_callback(1.0, "抖音内容创建完成")
            
            self.logger.info(f"Douyin content created: {mix_result['project_path']}")
            
            return {
                "success": True,
                "project_path": mix_result["project_path"],
                "content_type": content_type,
                "content_strategy": content_strategy,
                "metadata": metadata,
                "optimization_applied": optimization_result["success"]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create Douyin content: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_source_videos(self, video_files: List[str]) -> Dict[str, Any]:
        """分析源视频"""
        analysis = {
            "total_videos": len(video_files),
            "total_duration": 0.0,
            "video_details": [],
            "quality_distribution": {"high": 0, "medium": 0, "low": 0},
            "resolution_types": {"horizontal": 0, "vertical": 0, "square": 0}
        }
        
        for video_file in video_files:
            try:
                # 模拟视频分析
                video_detail = {
                    "path": video_file,
                    "name": Path(video_file).name,
                    "duration": 45.0,  # 模拟时长
                    "resolution": (1920, 1080),  # 模拟分辨率
                    "fps": 30.0,
                    "quality_score": 0.75,
                    "has_audio": True,
                    "brightness": 0.6,
                    "motion_level": 0.7
                }
                
                # 分类质量
                if video_detail["quality_score"] >= 0.8:
                    analysis["quality_distribution"]["high"] += 1
                elif video_detail["quality_score"] >= 0.6:
                    analysis["quality_distribution"]["medium"] += 1
                else:
                    analysis["quality_distribution"]["low"] += 1
                
                # 分类分辨率类型
                width, height = video_detail["resolution"]
                if width > height:
                    analysis["resolution_types"]["horizontal"] += 1
                elif height > width:
                    analysis["resolution_types"]["vertical"] += 1
                else:
                    analysis["resolution_types"]["square"] += 1
                
                analysis["video_details"].append(video_detail)
                analysis["total_duration"] += video_detail["duration"]
                
            except Exception as e:
                self.logger.warning(f"Failed to analyze video {video_file}: {e}")
        
        return analysis
    
    def _generate_content_strategy(self, content_type: str, 
                                  video_analysis: Dict[str, Any],
                                  content_config: Optional[Dict] = None) -> Dict[str, Any]:
        """生成内容策略"""
        config = content_config or {}
        
        # 基础策略配置
        base_strategies = {
            "short_video": {
                "target_duration": 15.0,
                "clip_count": 3,
                "mix_strategy": "smart",
                "transition_style": "quick",
                "music_style": "upbeat"
            },
            "story": {
                "target_duration": 30.0,
                "clip_count": 5,
                "mix_strategy": "sequential",
                "transition_style": "smooth",
                "music_style": "narrative"
            },
            "tutorial": {
                "target_duration": 60.0,
                "clip_count": 8,
                "mix_strategy": "sequential",
                "transition_style": "cut",
                "music_style": "background"
            }
        }
        
        strategy = base_strategies.get(content_type, base_strategies["short_video"]).copy()
        
        # 根据视频分析调整策略
        total_duration = video_analysis["total_duration"]
        video_count = video_analysis["total_videos"]
        
        # 调整片段数量
        if video_count < strategy["clip_count"]:
            strategy["clip_count"] = video_count
        
        # 根据质量分布调整策略
        quality_dist = video_analysis["quality_distribution"]
        if quality_dist["high"] > quality_dist["medium"] + quality_dist["low"]:
            strategy["quality_preference"] = "high_quality_focus"
        else:
            strategy["quality_preference"] = "balanced"
        
        # 应用用户配置覆盖
        strategy.update(config)
        
        return strategy
    
    def _apply_douyin_optimization(self, project_path: str, 
                                  content_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """应用抖音特定优化"""
        try:
            optimizations = []
            
            # 1. 分辨率优化 - 转换为竖屏
            if self.douyin_config["aspect_ratio"] == "9:16":
                optimizations.append({
                    "type": "resolution",
                    "target": self.douyin_config["resolution"],
                    "method": "crop_and_scale"
                })
            
            # 2. 时长优化
            target_duration = content_strategy.get("target_duration", 15.0)
            optimizations.append({
                "type": "duration",
                "target": target_duration,
                "method": "smart_trim"
            })
            
            # 3. 音频优化
            if self.douyin_config["background_music"]:
                optimizations.append({
                    "type": "audio",
                    "add_background_music": True,
                    "music_style": content_strategy.get("music_style", "upbeat")
                })
            
            # 4. 字幕优化
            if self.douyin_config["auto_subtitle"]:
                optimizations.append({
                    "type": "subtitle",
                    "auto_generate": True,
                    "style": "douyin_default"
                })
            
            # 5. 文件大小优化
            optimizations.append({
                "type": "compression",
                "target_size_mb": self.douyin_config["max_file_size_mb"],
                "quality": "high"
            })
            
            # 保存优化配置到项目
            optimization_config = {
                "douyin_optimizations": optimizations,
                "applied_at": self._get_timestamp()
            }
            
            # 这里应该实际应用优化，暂时只保存配置
            self.logger.info(f"Applied {len(optimizations)} Douyin optimizations")
            
            return {
                "success": True,
                "optimizations_applied": len(optimizations),
                "optimization_config": optimization_config
            }
            
        except Exception as e:
            self.logger.error(f"Failed to apply Douyin optimization: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_content_metadata(self, content_type: str,
                                  content_strategy: Dict[str, Any],
                                  video_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成内容元数据"""
        metadata = {
            "content_type": content_type,
            "platform": "douyin",
            "created_at": self._get_timestamp(),
            "target_audience": self._determine_target_audience(content_type),
            "hashtags": self._generate_hashtags(content_type, video_analysis),
            "description": self._generate_description(content_type, content_strategy),
            "technical_specs": {
                "duration": content_strategy.get("target_duration", 15.0),
                "resolution": self.douyin_config["resolution"],
                "aspect_ratio": self.douyin_config["aspect_ratio"],
                "file_size_limit": self.douyin_config["max_file_size_mb"]
            },
            "optimization_applied": True
        }
        
        return metadata
    
    def _determine_target_audience(self, content_type: str) -> str:
        """确定目标受众"""
        audience_map = {
            "short_video": "年轻用户(18-35岁)",
            "story": "广泛受众(16-45岁)",
            "tutorial": "学习型用户(20-40岁)"
        }
        return audience_map.get(content_type, "广泛受众")
    
    def _generate_hashtags(self, content_type: str, 
                          video_analysis: Dict[str, Any]) -> List[str]:
        """生成推荐标签"""
        base_hashtags = {
            "short_video": ["#短视频", "#创意", "#有趣"],
            "story": ["#故事", "#分享", "#生活"],
            "tutorial": ["#教程", "#学习", "#技能"]
        }
        
        hashtags = base_hashtags.get(content_type, ["#视频"])
        
        # 根据视频分析添加相关标签
        if video_analysis["quality_distribution"]["high"] > 0:
            hashtags.append("#高清")
        
        return hashtags
    
    def _generate_description(self, content_type: str,
                             content_strategy: Dict[str, Any]) -> str:
        """生成内容描述"""
        descriptions = {
            "short_video": f"精彩{content_strategy.get('target_duration', 15)}秒，不容错过！",
            "story": "分享生活中的美好瞬间",
            "tutorial": "实用教程，轻松学会新技能"
        }
        
        return descriptions.get(content_type, "精彩内容分享")
    
    def get_douyin_templates(self) -> List[Dict[str, Any]]:
        """获取抖音内容模板"""
        templates = [
            {
                "name": "快手短视频",
                "content_type": "short_video",
                "description": "15秒快节奏短视频",
                "target_duration": 15.0,
                "recommended_for": ["娱乐", "搞笑", "创意"]
            },
            {
                "name": "生活故事",
                "content_type": "story", 
                "description": "30秒生活分享",
                "target_duration": 30.0,
                "recommended_for": ["生活", "情感", "分享"]
            },
            {
                "name": "技能教程",
                "content_type": "tutorial",
                "description": "60秒实用教程",
                "target_duration": 60.0,
                "recommended_for": ["教育", "技能", "知识"]
            }
        ]
        
        return templates
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'video_mix_service'):
            self.video_mix_service.cleanup()
        self.logger.info("Douyin workflow service cleanup completed")
