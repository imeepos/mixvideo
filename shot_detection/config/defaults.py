"""
Default Configuration
默认配置
"""

DEFAULT_CONFIG = {
    # 应用程序信息
    "app": {
        "name": "Shot Detection",
        "version": "2.0.0",
        "author": "Shot Detection Team",
        "description": "Advanced video shot boundary detection tool"
    },
    
    # 检测配置
    "detection": {
        # 默认检测器
        "default_detector": "multi_detector",
        
        # 帧差检测器配置
        "frame_difference": {
            "threshold": 0.3,
            "min_shot_length": 1.0,
            "adaptive_threshold": True,
            "use_edge_detection": False,
            "edge_threshold": 50
        },
        
        # 直方图检测器配置
        "histogram": {
            "threshold": 0.5,
            "bins": 256,
            "method": "correlation",  # correlation, chi_square, intersection
            "color_space": "RGB",  # RGB, HSV, LAB
            "adaptive_threshold": True,
            "window_size": 5
        },
        
        # 多检测器融合配置
        "multi_detector": {
            "enabled_detectors": ["frame_difference", "histogram"],
            "fusion_weights": {
                "frame_difference": 0.6,
                "histogram": 0.4
            },
            "clustering_threshold": 1.0,
            "min_confidence": 0.3
        },
        
        # 通用检测配置
        "common": {
            "sample_rate": 1,  # 采样率（每N帧处理一次）
            "max_frames": None,  # 最大处理帧数
            "enable_gpu": False,  # 是否启用GPU加速
            "num_threads": 4,  # 处理线程数
            "cache_frames": True,  # 是否缓存帧
            "cache_size": 100  # 缓存大小
        }
    },
    
    # 处理配置
    "processing": {
        # 输出配置
        "output": {
            "format": "mp4",
            "quality": "high",  # low, medium, high
            "codec": "h264",
            "audio_codec": "aac",
            "preserve_audio": True
        },
        
        # 分割配置
        "segmentation": {
            "min_segment_duration": 1.0,
            "max_segment_duration": 300.0,
            "enable_smart_split": True,
            "split_on_silence": False,
            "silence_threshold": -40  # dB
        },
        
        # 预览配置
        "preview": {
            "enabled": True,
            "size": [320, 240],
            "fps": 15,
            "format": "mp4"
        }
    },
    
    # GUI配置
    "gui": {
        # 窗口配置
        "window": {
            "width": 1200,
            "height": 800,
            "min_width": 800,
            "min_height": 600,
            "resizable": True,
            "center_on_screen": True
        },
        
        # 主题配置
        "theme": {
            "style": "default",  # default, dark, light
            "font_family": "Arial",
            "font_size": 10,
            "colors": {
                "primary": "#2196F3",
                "secondary": "#FFC107",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "error": "#F44336"
            }
        },
        
        # 界面配置
        "interface": {
            "show_toolbar": True,
            "show_statusbar": True,
            "show_progress": True,
            "auto_save_settings": True,
            "remember_last_directory": True,
            "max_recent_files": 10
        },
        
        # 性能配置
        "performance": {
            "enable_threading": True,
            "max_worker_threads": 4,
            "update_interval": 100,  # ms
            "preview_update_rate": 30  # fps
        }
    },
    
    # 剪映配置
    "jianying": {
        # 项目配置
        "project": {
            "default_template": "default",
            "auto_backup": True,
            "backup_interval": 300,  # seconds
            "max_backups": 5
        },
        
        # 工作流程配置
        "workflow": {
            "auto_scan": True,
            "scan_recursive": True,
            "supported_formats": [".mp4", ".avi", ".mov", ".mkv"],
            "min_video_duration": 1.0,
            "max_video_duration": 3600.0
        },
        
        # 分配算法配置
        "allocation": {
            "algorithm": "smart",  # random, sequential, smart
            "ensure_uniqueness": True,
            "avoid_consecutive": True,
            "max_reuse_count": 2,
            "balance_usage": True
        },
        
        # 输出配置
        "output": {
            "use_original_paths": True,
            "create_backup": True,
            "validate_output": True,
            "auto_open_project": False
        }
    },
    
    # 日志配置
    "logging": {
        "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
        "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
        "file_enabled": True,
        "file_path": "logs/shot_detection.log",
        "file_rotation": "10 MB",
        "file_retention": "30 days",
        "console_enabled": True
    },
    
    # 性能配置
    "performance": {
        "memory_limit": "2GB",
        "cpu_limit": 80,  # percentage
        "io_timeout": 30,  # seconds
        "cache_enabled": True,
        "cache_size": "500MB",
        "parallel_processing": True,
        "max_parallel_jobs": 4
    },
    
    # 高级配置
    "advanced": {
        "debug_mode": False,
        "profiling_enabled": False,
        "experimental_features": False,
        "auto_update_check": True,
        "telemetry_enabled": False,
        "crash_reporting": True
    }
}
