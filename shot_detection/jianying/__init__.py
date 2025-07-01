"""
JianYing Module - Refactored
剪映模块 - 重构版本

提供剪映项目的创建、编辑和管理功能
采用新的服务导向架构
"""

# 新架构导入
try:
    from .services import JianYingService, VideoMixService, DouyinWorkflowService
    from .managers import ProjectManager, DraftManager, MediaManager
    from .algorithms import VideoAllocationAlgorithm
    from .models import JianYingProject, DraftContent, VideoResource

    # 新架构导出
    __all__ = [
        # Services
        'JianYingService',
        'VideoMixService',
        'DouyinWorkflowService',

        # Managers
        'ProjectManager',
        'DraftManager',
        'MediaManager',

        # Algorithms
        'VideoAllocationAlgorithm',

        # Models
        'JianYingProject',
        'DraftContent',
        'VideoResource',
    ]

    # 向后兼容性导入
    try:
        from .draft_meta_manager import DraftMetaManager, MaterialInfo
        from .draft_content_manager import DraftContentManager, TrackInfo, MaterialRef

        # 添加到导出列表
        __all__.extend([
            'DraftMetaManager',
            'MaterialInfo',
            'DraftContentManager',
            'TrackInfo',
            'MaterialRef'
        ])

    except ImportError as e:
        print(f"警告：旧版剪映模块导入失败: {e}")

except ImportError as e:
    # 如果新架构导入失败，回退到旧版本
    print(f"警告：新架构剪映模块导入失败，回退到旧版本: {e}")

    try:
        from .draft_meta_manager import DraftMetaManager, MaterialInfo
        from .draft_content_manager import DraftContentManager, TrackInfo, MaterialRef

        __all__ = [
            'DraftMetaManager',
            'MaterialInfo',
            'DraftContentManager',
            'TrackInfo',
            'MaterialRef'
        ]

    except ImportError as e2:
        print(f"错误：剪映模块完全导入失败: {e2}")
        __all__ = []

# 版本信息
__version__ = "2.0.0"
__author__ = "Shot Detection Team"
__description__ = "剪映项目管理工具 - 重构版本"
