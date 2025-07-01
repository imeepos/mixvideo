"""
Translation System
翻译系统
"""

import json
import gettext
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger


class Translator:
    """翻译器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化翻译器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="Translator")
        
        # 翻译配置
        self.translation_config = self.config.get('translation', {
            'default_language': 'zh_CN',
            'fallback_language': 'en_US',
            'translations_dir': './locales',
            'domain': 'shot_detection',
            'auto_detect_language': True,
            'cache_translations': True
        })
        
        # 当前语言
        self.current_language = self.translation_config['default_language']
        
        # 翻译缓存
        self.translation_cache = {}
        
        # 已加载的翻译
        self.translations = {}
        
        # gettext对象
        self.gettext_obj = None
        
        # 初始化翻译
        self._initialize_translations()
        
        self.logger.info("Translator initialized")
    
    def _initialize_translations(self):
        """初始化翻译"""
        try:
            # 自动检测系统语言
            if self.translation_config['auto_detect_language']:
                detected_lang = self._detect_system_language()
                if detected_lang:
                    self.current_language = detected_lang
            
            # 加载翻译文件
            self._load_translations()
            
            # 设置gettext
            self._setup_gettext()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize translations: {e}")
    
    def _detect_system_language(self) -> Optional[str]:
        """检测系统语言"""
        try:
            import locale
            
            # 获取系统语言设置
            system_locale = locale.getdefaultlocale()[0]
            
            if system_locale:
                # 转换为我们支持的语言代码
                if system_locale.startswith('zh'):
                    if 'TW' in system_locale or 'HK' in system_locale:
                        return 'zh_TW'
                    else:
                        return 'zh_CN'
                elif system_locale.startswith('en'):
                    return 'en_US'
                elif system_locale.startswith('ja'):
                    return 'ja_JP'
                elif system_locale.startswith('ko'):
                    return 'ko_KR'
                elif system_locale.startswith('fr'):
                    return 'fr_FR'
                elif system_locale.startswith('de'):
                    return 'de_DE'
                elif system_locale.startswith('es'):
                    return 'es_ES'
                elif system_locale.startswith('ru'):
                    return 'ru_RU'
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to detect system language: {e}")
            return None
    
    def _load_translations(self):
        """加载翻译文件"""
        try:
            translations_dir = Path(self.translation_config['translations_dir'])
            
            if not translations_dir.exists():
                self.logger.warning(f"Translations directory not found: {translations_dir}")
                return
            
            # 加载JSON格式的翻译文件
            for lang_file in translations_dir.glob('*.json'):
                lang_code = lang_file.stem
                
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        translations = json.load(f)
                    
                    self.translations[lang_code] = translations
                    self.logger.info(f"Loaded translations for: {lang_code}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to load translation file {lang_file}: {e}")
            
            # 如果没有找到翻译文件，创建默认翻译
            if not self.translations:
                self._create_default_translations()
            
        except Exception as e:
            self.logger.error(f"Failed to load translations: {e}")
    
    def _create_default_translations(self):
        """创建默认翻译"""
        # 中文翻译
        self.translations['zh_CN'] = {
            # 通用
            'app_name': 'Shot Detection',
            'version': '版本',
            'ok': '确定',
            'cancel': '取消',
            'yes': '是',
            'no': '否',
            'save': '保存',
            'load': '加载',
            'open': '打开',
            'close': '关闭',
            'exit': '退出',
            'help': '帮助',
            'about': '关于',
            'settings': '设置',
            'preferences': '偏好设置',
            
            # 文件操作
            'file': '文件',
            'file_open': '打开文件',
            'file_save': '保存文件',
            'file_save_as': '另存为',
            'file_recent': '最近文件',
            'file_not_found': '文件未找到',
            'file_load_error': '文件加载错误',
            'file_save_error': '文件保存错误',
            
            # 编辑操作
            'edit': '编辑',
            'edit_undo': '撤销',
            'edit_redo': '重做',
            'edit_cut': '剪切',
            'edit_copy': '复制',
            'edit_paste': '粘贴',
            'edit_select_all': '全选',
            'edit_find': '查找',
            'edit_replace': '替换',
            
            # 视图操作
            'view': '视图',
            'view_zoom_in': '放大',
            'view_zoom_out': '缩小',
            'view_zoom_reset': '重置缩放',
            'view_fullscreen': '全屏',
            'view_refresh': '刷新',
            
            # 检测相关
            'detection': '检测',
            'detection_start': '开始检测',
            'detection_stop': '停止检测',
            'detection_pause': '暂停检测',
            'detection_resume': '继续检测',
            'detection_algorithm': '检测算法',
            'detection_threshold': '检测阈值',
            'detection_progress': '检测进度',
            'detection_results': '检测结果',
            'detection_export': '导出结果',
            
            # 算法名称
            'algorithm_frame_difference': '帧差检测',
            'algorithm_histogram': '直方图检测',
            'algorithm_multi': '多算法融合',
            
            # 状态信息
            'status_ready': '就绪',
            'status_processing': '处理中',
            'status_completed': '已完成',
            'status_error': '错误',
            'status_cancelled': '已取消',
            
            # 错误信息
            'error_general': '发生错误',
            'error_file_not_found': '文件未找到',
            'error_invalid_format': '无效的文件格式',
            'error_processing_failed': '处理失败',
            'error_out_of_memory': '内存不足',
            'error_permission_denied': '权限被拒绝',
            
            # 成功信息
            'success_file_saved': '文件保存成功',
            'success_detection_completed': '检测完成',
            'success_export_completed': '导出完成',
            
            # 警告信息
            'warning_unsaved_changes': '有未保存的更改',
            'warning_large_file': '文件较大，处理可能需要较长时间',
            'warning_low_memory': '内存不足，建议关闭其他程序',
            
            # 界面元素
            'menu_file': '文件',
            'menu_edit': '编辑',
            'menu_view': '视图',
            'menu_tools': '工具',
            'menu_help': '帮助',
            'toolbar_main': '主工具栏',
            'statusbar_ready': '就绪',
            
            # 对话框
            'dialog_confirm': '确认',
            'dialog_warning': '警告',
            'dialog_error': '错误',
            'dialog_info': '信息',
            'dialog_question': '问题',
            
            # 进度相关
            'progress_initializing': '初始化中...',
            'progress_loading': '加载中...',
            'progress_processing': '处理中...',
            'progress_saving': '保存中...',
            'progress_exporting': '导出中...',
            'progress_completed': '完成',
            
            # 时间相关
            'time_seconds': '秒',
            'time_minutes': '分钟',
            'time_hours': '小时',
            'time_remaining': '剩余时间',
            'time_elapsed': '已用时间',
            
            # 单位
            'unit_frames': '帧',
            'unit_pixels': '像素',
            'unit_bytes': '字节',
            'unit_kb': 'KB',
            'unit_mb': 'MB',
            'unit_gb': 'GB',
        }
        
        # 英文翻译
        self.translations['en_US'] = {
            # 通用
            'app_name': 'Shot Detection',
            'version': 'Version',
            'ok': 'OK',
            'cancel': 'Cancel',
            'yes': 'Yes',
            'no': 'No',
            'save': 'Save',
            'load': 'Load',
            'open': 'Open',
            'close': 'Close',
            'exit': 'Exit',
            'help': 'Help',
            'about': 'About',
            'settings': 'Settings',
            'preferences': 'Preferences',
            
            # 文件操作
            'file': 'File',
            'file_open': 'Open File',
            'file_save': 'Save File',
            'file_save_as': 'Save As',
            'file_recent': 'Recent Files',
            'file_not_found': 'File Not Found',
            'file_load_error': 'File Load Error',
            'file_save_error': 'File Save Error',
            
            # 编辑操作
            'edit': 'Edit',
            'edit_undo': 'Undo',
            'edit_redo': 'Redo',
            'edit_cut': 'Cut',
            'edit_copy': 'Copy',
            'edit_paste': 'Paste',
            'edit_select_all': 'Select All',
            'edit_find': 'Find',
            'edit_replace': 'Replace',
            
            # 视图操作
            'view': 'View',
            'view_zoom_in': 'Zoom In',
            'view_zoom_out': 'Zoom Out',
            'view_zoom_reset': 'Reset Zoom',
            'view_fullscreen': 'Fullscreen',
            'view_refresh': 'Refresh',
            
            # 检测相关
            'detection': 'Detection',
            'detection_start': 'Start Detection',
            'detection_stop': 'Stop Detection',
            'detection_pause': 'Pause Detection',
            'detection_resume': 'Resume Detection',
            'detection_algorithm': 'Detection Algorithm',
            'detection_threshold': 'Detection Threshold',
            'detection_progress': 'Detection Progress',
            'detection_results': 'Detection Results',
            'detection_export': 'Export Results',
            
            # 算法名称
            'algorithm_frame_difference': 'Frame Difference',
            'algorithm_histogram': 'Histogram',
            'algorithm_multi': 'Multi-Algorithm',
            
            # 状态信息
            'status_ready': 'Ready',
            'status_processing': 'Processing',
            'status_completed': 'Completed',
            'status_error': 'Error',
            'status_cancelled': 'Cancelled',
            
            # 错误信息
            'error_general': 'An error occurred',
            'error_file_not_found': 'File not found',
            'error_invalid_format': 'Invalid file format',
            'error_processing_failed': 'Processing failed',
            'error_out_of_memory': 'Out of memory',
            'error_permission_denied': 'Permission denied',
            
            # 成功信息
            'success_file_saved': 'File saved successfully',
            'success_detection_completed': 'Detection completed',
            'success_export_completed': 'Export completed',
            
            # 警告信息
            'warning_unsaved_changes': 'There are unsaved changes',
            'warning_large_file': 'Large file, processing may take a while',
            'warning_low_memory': 'Low memory, consider closing other programs',
            
            # 界面元素
            'menu_file': 'File',
            'menu_edit': 'Edit',
            'menu_view': 'View',
            'menu_tools': 'Tools',
            'menu_help': 'Help',
            'toolbar_main': 'Main Toolbar',
            'statusbar_ready': 'Ready',
            
            # 对话框
            'dialog_confirm': 'Confirm',
            'dialog_warning': 'Warning',
            'dialog_error': 'Error',
            'dialog_info': 'Information',
            'dialog_question': 'Question',
            
            # 进度相关
            'progress_initializing': 'Initializing...',
            'progress_loading': 'Loading...',
            'progress_processing': 'Processing...',
            'progress_saving': 'Saving...',
            'progress_exporting': 'Exporting...',
            'progress_completed': 'Completed',
            
            # 时间相关
            'time_seconds': 'seconds',
            'time_minutes': 'minutes',
            'time_hours': 'hours',
            'time_remaining': 'Time Remaining',
            'time_elapsed': 'Time Elapsed',
            
            # 单位
            'unit_frames': 'frames',
            'unit_pixels': 'pixels',
            'unit_bytes': 'bytes',
            'unit_kb': 'KB',
            'unit_mb': 'MB',
            'unit_gb': 'GB',
        }
    
    def _setup_gettext(self):
        """设置gettext"""
        try:
            translations_dir = Path(self.translation_config['translations_dir'])
            domain = self.translation_config['domain']
            
            # 尝试设置gettext
            if translations_dir.exists():
                self.gettext_obj = gettext.translation(
                    domain,
                    localedir=str(translations_dir),
                    languages=[self.current_language],
                    fallback=True
                )
                self.gettext_obj.install()
            
        except Exception as e:
            self.logger.error(f"Failed to setup gettext: {e}")
    
    def set_language(self, language_code: str) -> bool:
        """
        设置当前语言
        
        Args:
            language_code: 语言代码
            
        Returns:
            是否设置成功
        """
        try:
            if language_code in self.translations:
                self.current_language = language_code
                self._setup_gettext()
                
                # 清除缓存
                if self.translation_config['cache_translations']:
                    self.translation_cache.clear()
                
                self.logger.info(f"Language set to: {language_code}")
                return True
            else:
                self.logger.warning(f"Language not available: {language_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to set language {language_code}: {e}")
            return False
    
    def get_current_language(self) -> str:
        """获取当前语言"""
        return self.current_language
    
    def get_available_languages(self) -> List[str]:
        """获取可用语言列表"""
        return list(self.translations.keys())
    
    def translate(self, key: str, **kwargs) -> str:
        """
        翻译文本
        
        Args:
            key: 翻译键
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        try:
            # 检查缓存
            cache_key = f"{self.current_language}:{key}"
            if self.translation_config['cache_translations'] and cache_key in self.translation_cache:
                text = self.translation_cache[cache_key]
            else:
                # 获取翻译
                text = self._get_translation(key)
                
                # 缓存翻译
                if self.translation_config['cache_translations']:
                    self.translation_cache[cache_key] = text
            
            # 格式化文本
            if kwargs:
                text = text.format(**kwargs)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Translation failed for key '{key}': {e}")
            return key  # 返回原始键作为后备
    
    def _get_translation(self, key: str) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键
            
        Returns:
            翻译文本
        """
        # 尝试当前语言
        current_translations = self.translations.get(self.current_language, {})
        if key in current_translations:
            return current_translations[key]
        
        # 尝试后备语言
        fallback_language = self.translation_config['fallback_language']
        if fallback_language != self.current_language:
            fallback_translations = self.translations.get(fallback_language, {})
            if key in fallback_translations:
                return fallback_translations[key]
        
        # 返回键本身作为最后的后备
        return key
    
    def translate_plural(self, key_singular: str, key_plural: str, count: int, **kwargs) -> str:
        """
        翻译复数形式
        
        Args:
            key_singular: 单数形式的键
            key_plural: 复数形式的键
            count: 数量
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        try:
            if count == 1:
                text = self.translate(key_singular, **kwargs)
            else:
                text = self.translate(key_plural, **kwargs)
            
            # 添加数量到格式化参数
            kwargs['count'] = count
            
            if kwargs:
                text = text.format(**kwargs)
            
            return text
            
        except Exception as e:
            self.logger.error(f"Plural translation failed: {e}")
            return f"{count} {key_singular if count == 1 else key_plural}"
    
    def add_translation(self, language_code: str, key: str, value: str):
        """
        添加翻译
        
        Args:
            language_code: 语言代码
            key: 翻译键
            value: 翻译值
        """
        try:
            if language_code not in self.translations:
                self.translations[language_code] = {}
            
            self.translations[language_code][key] = value
            
            # 清除相关缓存
            if self.translation_config['cache_translations']:
                cache_key = f"{language_code}:{key}"
                if cache_key in self.translation_cache:
                    del self.translation_cache[cache_key]
            
        except Exception as e:
            self.logger.error(f"Failed to add translation: {e}")
    
    def save_translations(self):
        """保存翻译到文件"""
        try:
            translations_dir = Path(self.translation_config['translations_dir'])
            translations_dir.mkdir(parents=True, exist_ok=True)
            
            for language_code, translations in self.translations.items():
                lang_file = translations_dir / f"{language_code}.json"
                
                with open(lang_file, 'w', encoding='utf-8') as f:
                    json.dump(translations, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Translations saved to files")
            
        except Exception as e:
            self.logger.error(f"Failed to save translations: {e}")
    
    def get_language_info(self, language_code: str) -> Dict[str, str]:
        """
        获取语言信息
        
        Args:
            language_code: 语言代码
            
        Returns:
            语言信息
        """
        language_info = {
            'zh_CN': {'name': '简体中文', 'native_name': '简体中文', 'direction': 'ltr'},
            'zh_TW': {'name': '繁體中文', 'native_name': '繁體中文', 'direction': 'ltr'},
            'en_US': {'name': 'English', 'native_name': 'English', 'direction': 'ltr'},
            'ja_JP': {'name': '日本語', 'native_name': '日本語', 'direction': 'ltr'},
            'ko_KR': {'name': '한국어', 'native_name': '한국어', 'direction': 'ltr'},
            'fr_FR': {'name': 'Français', 'native_name': 'Français', 'direction': 'ltr'},
            'de_DE': {'name': 'Deutsch', 'native_name': 'Deutsch', 'direction': 'ltr'},
            'es_ES': {'name': 'Español', 'native_name': 'Español', 'direction': 'ltr'},
            'ru_RU': {'name': 'Русский', 'native_name': 'Русский', 'direction': 'ltr'},
        }
        
        return language_info.get(language_code, {
            'name': language_code,
            'native_name': language_code,
            'direction': 'ltr'
        })
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.translation_config['cache_translations']:
                self.translation_cache.clear()
            self.logger.info("Translator cleanup completed")
        except Exception as e:
            self.logger.error(f"Translator cleanup failed: {e}")


# 全局翻译函数
_global_translator = None

def init_translator(config: Optional[Dict[str, Any]] = None) -> Translator:
    """初始化全局翻译器"""
    global _global_translator
    _global_translator = Translator(config)
    return _global_translator

def get_translator() -> Optional[Translator]:
    """获取全局翻译器"""
    return _global_translator

def _(key: str, **kwargs) -> str:
    """全局翻译函数"""
    if _global_translator:
        return _global_translator.translate(key, **kwargs)
    return key

def _n(key_singular: str, key_plural: str, count: int, **kwargs) -> str:
    """全局复数翻译函数"""
    if _global_translator:
        return _global_translator.translate_plural(key_singular, key_plural, count, **kwargs)
    return f"{count} {key_singular if count == 1 else key_plural}"
