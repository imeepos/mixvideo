"""
视频分段自动归类配置模块
参考video-analyzer实现，为shot_detection添加智能归类功能
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import os


@dataclass
class ClassificationConfig:
    """自动归类配置"""
    
    # 归类开关
    enable_classification: bool = False
    
    # 归类模式
    classification_mode: str = "duration"  # duration, quality, content, custom
    
    # 置信度阈值
    min_confidence_for_move: float = 0.6
    
    # 文件操作配置
    move_files: bool = False  # False=复制，True=移动
    create_directories: bool = True
    conflict_resolution: str = "rename"  # skip, overwrite, rename
    create_backup: bool = False
    
    # 命名模式
    naming_mode: str = "preserve-original"  # smart, content-based, preserve-original, timestamp
    
    # 目录结构配置
    base_output_dir: str = "classified_segments"
    
    # 时长分类配置
    duration_thresholds: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "short": (0.0, 5.0),      # 0-5秒
        "medium": (5.0, 30.0),    # 5-30秒
        "long": (30.0, float('inf'))  # 30秒以上
    })
    
    # 质量分类配置
    quality_thresholds: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "low": (0.0, 0.4),        # 低质量
        "medium": (0.4, 0.7),     # 中等质量
        "high": (0.7, 1.0)        # 高质量
    })
    
    # 内容分类配置
    content_categories: List[str] = field(default_factory=lambda: [
        "action",      # 动作场景
        "dialogue",    # 对话场景
        "landscape",   # 风景场景
        "closeup",     # 特写场景
        "transition",  # 转场场景
        "other"        # 其他
    ])
    
    # 自定义分类规则
    custom_rules: List[Dict] = field(default_factory=list)


@dataclass
class FolderMatchConfig:
    """文件夹匹配配置"""
    
    # 基础目录
    base_directory: str = ""
    
    # 扫描深度
    max_depth: int = 3
    
    # 最小置信度
    min_confidence: float = 0.3
    
    # 最大匹配数量
    max_matches: int = 5
    
    # 启用语义分析
    enable_semantic_analysis: bool = False


@dataclass
class FileOrganizerConfig:
    """文件组织器配置"""
    
    # 文件操作
    move_files: bool = False
    create_directories: bool = True
    conflict_resolution: str = "rename"
    create_backup: bool = False
    backup_directory: str = "./backup"
    
    # 命名模式
    naming_mode: str = "preserve-original"
    
    # 自定义命名函数
    custom_naming_function: Optional[callable] = None


class ClassificationManager:
    """归类管理器"""
    
    def __init__(self, config: ClassificationConfig = None):
        self.config = config or ClassificationConfig()
        self.folder_match_config = FolderMatchConfig()
        self.file_organizer_config = FileOrganizerConfig()
        
        # 同步配置
        self._sync_configs()
    
    def _sync_configs(self):
        """同步各个配置模块"""
        # 同步文件操作配置
        self.file_organizer_config.move_files = self.config.move_files
        self.file_organizer_config.create_directories = self.config.create_directories
        self.file_organizer_config.conflict_resolution = self.config.conflict_resolution
        self.file_organizer_config.create_backup = self.config.create_backup
        self.file_organizer_config.naming_mode = self.config.naming_mode
        
        # 设置基础目录
        self.folder_match_config.base_directory = self.config.base_output_dir
    
    def update_config(self, **kwargs):
        """更新配置"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        self._sync_configs()
    
    def get_classification_categories(self) -> List[str]:
        """获取分类类别"""
        if self.config.classification_mode == "duration":
            return list(self.config.duration_thresholds.keys())
        elif self.config.classification_mode == "quality":
            return list(self.config.quality_thresholds.keys())
        elif self.config.classification_mode == "content":
            return self.config.content_categories
        else:
            return ["default"]
    
    def classify_segment(self, segment_info: Dict) -> str:
        """对分段进行分类"""
        if not self.config.enable_classification:
            return "default"
        
        if self.config.classification_mode == "duration":
            return self._classify_by_duration(segment_info.get('duration', 0))
        elif self.config.classification_mode == "quality":
            return self._classify_by_quality(segment_info.get('confidence', 0))
        elif self.config.classification_mode == "content":
            return self._classify_by_content(segment_info)
        elif self.config.classification_mode == "custom":
            return self._classify_by_custom_rules(segment_info)
        else:
            return "default"
    
    def _classify_by_duration(self, duration: float) -> str:
        """按时长分类"""
        for category, (min_dur, max_dur) in self.config.duration_thresholds.items():
            if min_dur <= duration < max_dur:
                return category
        return "other"
    
    def _classify_by_quality(self, confidence: float) -> str:
        """按质量分类"""
        for category, (min_conf, max_conf) in self.config.quality_thresholds.items():
            if min_conf <= confidence < max_conf:
                return category
        return "other"
    
    def _classify_by_content(self, segment_info: Dict) -> str:
        """按内容分类"""
        # 这里可以集成AI分析结果
        # 暂时返回默认分类
        return "other"
    
    def _classify_by_custom_rules(self, segment_info: Dict) -> str:
        """按自定义规则分类"""
        for rule in self.config.custom_rules:
            if self._match_rule(segment_info, rule):
                return rule.get('category', 'other')
        return "other"
    
    def _match_rule(self, segment_info: Dict, rule: Dict) -> bool:
        """匹配自定义规则"""
        # 实现自定义规则匹配逻辑
        return False
    
    def get_output_directory(self, category: str) -> str:
        """获取输出目录"""
        base_dir = Path(self.config.base_output_dir)
        category_dir = base_dir / category
        
        if self.config.create_directories:
            category_dir.mkdir(parents=True, exist_ok=True)
        
        return str(category_dir)
    
    def should_move_file(self, confidence: float) -> bool:
        """判断是否应该移动文件"""
        return confidence >= self.config.min_confidence_for_move
    
    def generate_filename(self, original_name: str, segment_info: Dict, category: str) -> str:
        """生成文件名"""
        if self.config.naming_mode == "preserve-original":
            return original_name
        elif self.config.naming_mode == "smart":
            return self._generate_smart_filename(original_name, segment_info, category)
        elif self.config.naming_mode == "content-based":
            return self._generate_content_based_filename(original_name, segment_info, category)
        elif self.config.naming_mode == "timestamp":
            return self._generate_timestamp_filename(original_name)
        else:
            return original_name
    
    def _generate_smart_filename(self, original_name: str, segment_info: Dict, category: str) -> str:
        """生成智能文件名"""
        base_name = Path(original_name).stem
        ext = Path(original_name).suffix
        
        # 添加分类信息
        duration = segment_info.get('duration', 0)
        confidence = segment_info.get('confidence', 0)
        
        new_name = f"{base_name}_{category}_d{duration:.1f}s_c{confidence:.2f}{ext}"
        return new_name
    
    def _generate_content_based_filename(self, original_name: str, segment_info: Dict, category: str) -> str:
        """生成基于内容的文件名"""
        base_name = Path(original_name).stem
        ext = Path(original_name).suffix
        
        # 基于内容特征生成名称
        content_desc = segment_info.get('content_description', 'unknown')
        safe_desc = "".join(c for c in content_desc if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_desc = safe_desc.replace(' ', '_')[:20]  # 限制长度
        
        new_name = f"{base_name}_{safe_desc}_{category}{ext}"
        return new_name
    
    def _generate_timestamp_filename(self, original_name: str) -> str:
        """生成时间戳文件名"""
        import datetime
        
        base_name = Path(original_name).stem
        ext = Path(original_name).suffix
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        new_name = f"{base_name}_{timestamp}{ext}"
        return new_name
    
    def load_from_file(self, config_file: str):
        """从文件加载配置"""
        import yaml
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if 'classification' in config_data:
                self._update_config_from_dict(config_data['classification'])
    
    def save_to_file(self, config_file: str):
        """保存配置到文件"""
        import yaml
        
        config_data = {
            'classification': self._config_to_dict()
        }
        
        # 如果文件已存在，合并配置
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_data = yaml.safe_load(f) or {}
            existing_data.update(config_data)
            config_data = existing_data
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    def _update_config_from_dict(self, config_dict: Dict):
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self._sync_configs()
    
    def _config_to_dict(self) -> Dict:
        """将配置转换为字典"""
        return {k: v for k, v in self.config.__dict__.items() if not k.startswith('_')}


# 全局归类管理器实例
classification_manager = ClassificationManager()


def get_classification_manager() -> ClassificationManager:
    """获取归类管理器"""
    return classification_manager


def load_classification_config(config_file: str = None) -> ClassificationManager:
    """加载归类配置"""
    global classification_manager
    classification_manager = ClassificationManager()
    
    if config_file:
        classification_manager.load_from_file(config_file)
    
    return classification_manager
