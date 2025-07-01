"""
Shot Detection Core Module
核心业务逻辑模块
"""

from .detection import *
from .processing import *
from .export import *
from .services import *
from .performance import *
from .advanced import *
from .ux import *
from .i18n import *
from .plugins import *
from .security import *
from .config import *
from .docs import *
from .deployment import *

__version__ = "2.0.0"
__all__ = [
    # Detection
    "BaseDetector",
    "FrameDifferenceDetector", 
    "HistogramDetector",
    "MultiDetector",
    "ShotBoundary",
    "DetectionResult",
    
    # Processing
    "VideoProcessor",
    "VideoSegment",
    "SegmentationService",
    "AnalysisService",
    
    # Export
    "ProjectExporter",
    "FormatHandler",
    
    # Services
    "VideoService",
    "BatchService",
    "AnalysisService",

    # Performance
    "MemoryManager",
    "PerformanceMonitor",
    "CacheOptimizer",
    "ResourceManager",

    # Advanced Features
    "AIDetector",
    "ModelManager",
    "CloudProcessor",
    "CloudStorage",
    "WorkflowAutomation",
    "TaskScheduler",
    "AdvancedAnalytics",
    "ReportGenerator",

    # User Experience
    "AccessibilityManager",
    "ThemeManager",
    "ShortcutManager",
    "TutorialManager",
    "FeedbackCollector",
    "UserPreferences",

    # Internationalization
    "Translator",
    "LanguageManager",
    "LocaleUtils",

    # Plugin System
    "PluginManager",
    "BasePlugin",
    "DetectorPlugin",
    "ProcessorPlugin",
    "PluginLoader",
    "PluginRegistry",
    "PluginInterface",
    "PluginConfig",

    # Security
    "AuthenticationManager",
    "UserManager",
    "AuthorizationManager",
    "PermissionManager",
    "EncryptionManager",
    "SecureStorage",
    "AuditLogger",
    "SecurityMonitor",
    "InputValidator",
    "SecurityValidator",

    # Configuration Management
    "ConfigManager",
    "ConfigValidator",
    "SettingsManager",
    "UserSettings",
    "EnvironmentManager",
    "EnvironmentConfig",
    "ProfileManager",
    "ConfigProfile",

    # Documentation Generation
    "DocumentationGenerator",
    "DocConfig",
    "APIDocumentationGenerator",
    "APIDocConfig",
    "UserGuideGenerator",
    "GuideConfig",
    "CodeAnalyzer",
    "AnalysisConfig",

    # Deployment and Distribution
    "PackageManager",
    "PackageConfig",
    "InstallerGenerator",
    "InstallerConfig",
    "DockerBuilder",
    "DockerConfig",
    "ReleaseManager",
    "ReleaseConfig",
]
