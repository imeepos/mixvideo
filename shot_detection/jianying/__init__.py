"""
剪映项目管理模块

提供剪映项目的创建、编辑和管理功能
"""

# 导入主要的管理器类
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
    
except ImportError as e:
    # 如果导入失败，设置为None，避免整个模块导入失败
    print(f"警告：剪映模块导入失败: {e}")
    DraftMetaManager = None
    MaterialInfo = None
    DraftContentManager = None
    TrackInfo = None
    MaterialRef = None
    
    __all__ = []

# 版本信息
__version__ = "1.0.0"
__author__ = "Shot Detection Team"
__description__ = "剪映项目管理工具"
