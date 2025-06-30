"""
智能镜头检测与分段系统 - 配置模块
提供系统的核心配置参数和设置管理
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from pathlib import Path


@dataclass
class DetectionConfig:
    """镜头检测算法配置"""
    
    # 帧差分析配置
    frame_diff_threshold: float = 0.3
    frame_diff_min_scene_len: int = 15  # 最小镜头长度（帧数）
    
    # 直方图检测配置
    histogram_threshold: float = 0.4
    histogram_bins: int = 256
    
    # 光流分析配置
    optical_flow_threshold: float = 0.5
    optical_flow_max_features: int = 1000
    
    # 深度学习检测配置
    dl_model_path: str = "models/shot_detection_model.pth"
    dl_confidence_threshold: float = 0.8
    dl_batch_size: int = 32
    
    # 融合算法配置
    fusion_weights: Dict[str, float] = field(default_factory=lambda: {
        'frame_diff': 0.25,
        'histogram': 0.25,
        'optical_flow': 0.25,
        'deep_learning': 0.25
    })
    fusion_threshold: float = 0.6


@dataclass
class ProcessingConfig:
    """视频处理配置"""
    
    # 输入输出配置
    input_formats: List[str] = field(default_factory=lambda: [
        '.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'
    ])
    output_format: str = 'mp4'
    
    # 处理参数配置
    target_fps: Optional[int] = None  # None表示保持原始帧率
    target_resolution: Optional[Tuple[int, int]] = None  # None表示保持原始分辨率
    quality_preset: str = 'medium'  # low, medium, high, lossless
    
    # 性能配置
    max_workers: int = 8
    chunk_size: int = 1000  # 每次处理的帧数
    memory_limit_gb: float = 4.0
    use_gpu: bool = True
    gpu_device: str = 'cuda:0'
    
    # 缓存配置
    enable_cache: bool = True
    cache_dir: str = '.cache'
    cache_max_size_gb: float = 10.0


@dataclass
class OutputConfig:
    """输出格式配置"""
    
    # 分段输出配置
    segment_naming_pattern: str = "{basename}_segment_{index:03d}.{ext}"
    include_metadata: bool = True
    preserve_audio: bool = True
    
    # 项目文件生成
    generate_premiere_xml: bool = True
    generate_final_cut_xml: bool = True
    generate_edl: bool = True
    generate_aaf: bool = False
    
    # 报告生成
    generate_html_report: bool = True
    generate_json_report: bool = True
    generate_csv_report: bool = True
    
    # 时间码格式
    timecode_format: str = 'SMPTE'  # SMPTE, frames, seconds
    timecode_fps: int = 25


@dataclass
class QualityConfig:
    """质量控制配置"""
    
    # 检测质量指标
    min_accuracy: float = 0.95
    max_false_positive_rate: float = 0.05
    max_false_negative_rate: float = 0.03
    
    # 处理质量指标
    max_processing_time_ratio: float = 0.1  # 处理时间/视频时长
    min_segment_duration: float = 1.0  # 最小分段时长（秒）
    max_segment_duration: float = 300.0  # 最大分段时长（秒）
    
    # 输出质量指标
    min_metadata_accuracy: float = 0.98
    required_format_compatibility: float = 1.0


@dataclass
class SystemConfig:
    """系统配置"""

    # 日志配置
    log_level: str = 'INFO'
    log_file: str = 'shot_detection.log'
    log_rotation: str = '10 MB'
    log_retention: str = '30 days'

    # 调试配置
    debug_mode: bool = False
    save_debug_frames: bool = False
    debug_output_dir: str = 'debug'

    # 监控配置
    enable_monitoring: bool = True
    metrics_port: int = 8080
    health_check_interval: int = 30


@dataclass
class GeminiConfig:
    """Gemini AI 视频分析配置"""

    # Cloudflare Gateway 配置
    cloudflare_project_id: str = "your_cloudflare_project_id_here"
    cloudflare_gateway_id: str = "your_cloudflare_gateway_id_here"

    # Google 项目配置
    google_project_id: str = "your_google_project_id_here"

    # 模型配置
    model_name: str = "gemini-2.5-flash"

    # 区域配置（支持多区域负载均衡）
    regions: List[str] = field(default_factory=lambda: [
        "us-central1", "us-east1", "europe-west1"
    ])

    # 缓存配置
    enable_cache: bool = True
    cache_dir: str = ".cache/gemini_analysis"
    cache_expiry_days: int = 7

    # API 配置
    timeout_seconds: int = 120
    max_retries: int = 3
    retry_delay_seconds: int = 5

    # 文件上传配置
    max_file_size_mb: int = 100
    supported_formats: List[str] = field(default_factory=lambda: [
        ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm"
    ])


@dataclass
class ClassificationIntegrationConfig:
    """归类功能集成配置"""

    # 归类功能开关
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
    naming_mode: str = "preserve-original"  # preserve-original, smart, content-based, timestamp

    # 目录结构
    base_output_dir: str = "classified_segments"

    # 时长分类阈值（秒）
    duration_thresholds: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "short": (0.0, 5.0),
        "medium": (5.0, 30.0),
        "long": (30.0, float('inf'))
    })

    # 质量分类阈值（置信度）
    quality_thresholds: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "low": (0.0, 0.4),
        "medium": (0.4, 0.7),
        "high": (0.7, 1.0)
    })

    # 内容分类类别
    content_categories: List[str] = field(default_factory=lambda: [
        "action", "dialogue", "landscape", "closeup", "transition", "other"
    ])

    # 性能配置
    max_concurrent_operations: int = 4
    enable_parallel_processing: bool = True

    # 报告配置
    generate_classification_report: bool = True
    include_confidence_scores: bool = True
    save_operation_history: bool = True


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_file: Optional[str] = None):
        self.detection = DetectionConfig()
        self.processing = ProcessingConfig()
        self.output = OutputConfig()
        self.quality = QualityConfig()
        self.system = SystemConfig()
        self.classification = ClassificationIntegrationConfig()  # 归类配置
        self.gemini = GeminiConfig()  # 新增Gemini配置

        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file: str):
        """从配置文件加载配置"""
        import yaml
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # 更新各个配置模块
        if 'detection' in config_data:
            self._update_config(self.detection, config_data['detection'])
        if 'processing' in config_data:
            self._update_config(self.processing, config_data['processing'])
        if 'output' in config_data:
            self._update_config(self.output, config_data['output'])
        if 'quality' in config_data:
            self._update_config(self.quality, config_data['quality'])
        if 'system' in config_data:
            self._update_config(self.system, config_data['system'])
        if 'gemini' in config_data:
            self._update_config(self.gemini, config_data['gemini'])
    
    def save_to_file(self, config_file: str):
        """保存配置到文件"""
        import yaml
        
        config_data = {
            'detection': self._config_to_dict(self.detection),
            'processing': self._config_to_dict(self.processing),
            'output': self._config_to_dict(self.output),
            'quality': self._config_to_dict(self.quality),
            'system': self._config_to_dict(self.system),
            'gemini': self._config_to_dict(self.gemini)
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    def _update_config(self, config_obj, config_dict):
        """更新配置对象"""
        for key, value in config_dict.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
    
    def _config_to_dict(self, config_obj):
        """将配置对象转换为字典"""
        return {k: v for k, v in config_obj.__dict__.items() if not k.startswith('_')}
    
    def validate(self) -> List[str]:
        """验证配置的有效性"""
        errors = []
        
        # 验证检测配置
        if not 0 < self.detection.frame_diff_threshold < 1:
            errors.append("frame_diff_threshold must be between 0 and 1")
        
        # 验证处理配置
        if self.processing.max_workers < 1:
            errors.append("max_workers must be at least 1")
        
        # 验证质量配置
        if not 0 < self.quality.min_accuracy <= 1:
            errors.append("min_accuracy must be between 0 and 1")
        
        return errors


# 全局配置实例
config = ConfigManager()


def load_config(config_file: str = None) -> ConfigManager:
    """加载配置"""
    global config
    config = ConfigManager(config_file)
    return config


def get_config() -> ConfigManager:
    """获取当前配置"""
    return config
