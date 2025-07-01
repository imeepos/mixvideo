"""
Theme Management System
主题管理系统
"""

import json
import tkinter as tk
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class ThemeManager:
    """主题管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化主题管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="ThemeManager")
        
        # 主题配置
        self.theme_config = self.config.get('themes', {
            'default_theme': 'light',
            'themes_dir': './themes',
            'auto_detect_system': True,
            'custom_themes_enabled': True
        })
        
        # 当前主题
        self.current_theme = None
        self.theme_data = {}
        
        # 预定义主题
        self.builtin_themes = {
            'light': self._create_light_theme(),
            'dark': self._create_dark_theme(),
            'blue': self._create_blue_theme(),
            'green': self._create_green_theme(),
            'high_contrast': self._create_high_contrast_theme()
        }
        
        # 主题变更回调
        self.theme_change_callbacks = []
        
        self.logger.info("Theme manager initialized")
    
    def _create_light_theme(self) -> Dict[str, Any]:
        """创建浅色主题"""
        return {
            'name': '浅色主题',
            'type': 'light',
            'colors': {
                'primary': '#2196F3',
                'primary_dark': '#1976D2',
                'primary_light': '#BBDEFB',
                'secondary': '#FF9800',
                'background': '#FFFFFF',
                'surface': '#F5F5F5',
                'error': '#F44336',
                'warning': '#FF9800',
                'success': '#4CAF50',
                'info': '#2196F3',
                'text_primary': '#212121',
                'text_secondary': '#757575',
                'text_disabled': '#BDBDBD',
                'border': '#E0E0E0',
                'shadow': '#00000020'
            },
            'fonts': {
                'default_family': 'Microsoft YaHei UI',
                'default_size': 9,
                'title_size': 12,
                'subtitle_size': 10,
                'caption_size': 8,
                'button_size': 9
            },
            'spacing': {
                'small': 4,
                'medium': 8,
                'large': 16,
                'xlarge': 24
            },
            'borders': {
                'radius': 4,
                'width': 1
            }
        }
    
    def _create_dark_theme(self) -> Dict[str, Any]:
        """创建深色主题"""
        return {
            'name': '深色主题',
            'type': 'dark',
            'colors': {
                'primary': '#2196F3',
                'primary_dark': '#1565C0',
                'primary_light': '#42A5F5',
                'secondary': '#FF9800',
                'background': '#121212',
                'surface': '#1E1E1E',
                'error': '#CF6679',
                'warning': '#FFB74D',
                'success': '#81C784',
                'info': '#64B5F6',
                'text_primary': '#FFFFFF',
                'text_secondary': '#B3B3B3',
                'text_disabled': '#666666',
                'border': '#333333',
                'shadow': '#00000040'
            },
            'fonts': {
                'default_family': 'Microsoft YaHei UI',
                'default_size': 9,
                'title_size': 12,
                'subtitle_size': 10,
                'caption_size': 8,
                'button_size': 9
            },
            'spacing': {
                'small': 4,
                'medium': 8,
                'large': 16,
                'xlarge': 24
            },
            'borders': {
                'radius': 4,
                'width': 1
            }
        }
    
    def _create_blue_theme(self) -> Dict[str, Any]:
        """创建蓝色主题"""
        light_theme = self._create_light_theme()
        light_theme.update({
            'name': '蓝色主题',
            'type': 'blue',
            'colors': {
                **light_theme['colors'],
                'primary': '#1976D2',
                'primary_dark': '#0D47A1',
                'primary_light': '#E3F2FD',
                'secondary': '#FFC107',
                'surface': '#E8F4FD'
            }
        })
        return light_theme
    
    def _create_green_theme(self) -> Dict[str, Any]:
        """创建绿色主题"""
        light_theme = self._create_light_theme()
        light_theme.update({
            'name': '绿色主题',
            'type': 'green',
            'colors': {
                **light_theme['colors'],
                'primary': '#4CAF50',
                'primary_dark': '#2E7D32',
                'primary_light': '#E8F5E8',
                'secondary': '#FF9800',
                'surface': '#F1F8E9'
            }
        })
        return light_theme
    
    def _create_high_contrast_theme(self) -> Dict[str, Any]:
        """创建高对比度主题"""
        return {
            'name': '高对比度主题',
            'type': 'high_contrast',
            'colors': {
                'primary': '#0000FF',
                'primary_dark': '#000080',
                'primary_light': '#8080FF',
                'secondary': '#FFFF00',
                'background': '#FFFFFF',
                'surface': '#F0F0F0',
                'error': '#FF0000',
                'warning': '#FF8000',
                'success': '#008000',
                'info': '#0000FF',
                'text_primary': '#000000',
                'text_secondary': '#404040',
                'text_disabled': '#808080',
                'border': '#000000',
                'shadow': '#00000060'
            },
            'fonts': {
                'default_family': 'Microsoft YaHei UI',
                'default_size': 10,  # 稍大字体
                'title_size': 14,
                'subtitle_size': 12,
                'caption_size': 9,
                'button_size': 10
            },
            'spacing': {
                'small': 6,
                'medium': 12,
                'large': 20,
                'xlarge': 28
            },
            'borders': {
                'radius': 2,
                'width': 2  # 更粗边框
            }
        }
    
    def get_available_themes(self) -> Dict[str, str]:
        """获取可用主题列表"""
        themes = {}
        
        # 内置主题
        for theme_id, theme_data in self.builtin_themes.items():
            themes[theme_id] = theme_data['name']
        
        # 自定义主题
        if self.theme_config['custom_themes_enabled']:
            themes_dir = Path(self.theme_config['themes_dir'])
            if themes_dir.exists():
                for theme_file in themes_dir.glob('*.json'):
                    try:
                        with open(theme_file, 'r', encoding='utf-8') as f:
                            theme_data = json.load(f)
                            theme_id = theme_file.stem
                            themes[theme_id] = theme_data.get('name', theme_id)
                    except Exception as e:
                        self.logger.warning(f"Failed to load theme {theme_file}: {e}")
        
        return themes
    
    def load_theme(self, theme_id: str) -> bool:
        """
        加载主题
        
        Args:
            theme_id: 主题ID
            
        Returns:
            是否加载成功
        """
        try:
            # 检查内置主题
            if theme_id in self.builtin_themes:
                self.theme_data = self.builtin_themes[theme_id].copy()
                self.current_theme = theme_id
                self.logger.info(f"Loaded builtin theme: {theme_id}")
                self._notify_theme_change()
                return True
            
            # 检查自定义主题
            if self.theme_config['custom_themes_enabled']:
                themes_dir = Path(self.theme_config['themes_dir'])
                theme_file = themes_dir / f"{theme_id}.json"
                
                if theme_file.exists():
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        self.theme_data = json.load(f)
                        self.current_theme = theme_id
                        self.logger.info(f"Loaded custom theme: {theme_id}")
                        self._notify_theme_change()
                        return True
            
            self.logger.error(f"Theme not found: {theme_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to load theme {theme_id}: {e}")
            return False
    
    def get_current_theme(self) -> Optional[str]:
        """获取当前主题ID"""
        return self.current_theme
    
    def get_theme_data(self) -> Dict[str, Any]:
        """获取当前主题数据"""
        return self.theme_data.copy()
    
    def get_color(self, color_name: str, default: str = '#000000') -> str:
        """
        获取主题颜色
        
        Args:
            color_name: 颜色名称
            default: 默认颜色
            
        Returns:
            颜色值
        """
        return self.theme_data.get('colors', {}).get(color_name, default)
    
    def get_font(self, font_type: str = 'default') -> tuple:
        """
        获取主题字体
        
        Args:
            font_type: 字体类型
            
        Returns:
            字体元组 (family, size)
        """
        fonts = self.theme_data.get('fonts', {})
        family = fonts.get('default_family', 'Microsoft YaHei UI')
        
        size_key = f"{font_type}_size" if font_type != 'default' else 'default_size'
        size = fonts.get(size_key, fonts.get('default_size', 9))
        
        return (family, size)
    
    def get_spacing(self, spacing_type: str = 'medium') -> int:
        """
        获取主题间距
        
        Args:
            spacing_type: 间距类型
            
        Returns:
            间距值
        """
        return self.theme_data.get('spacing', {}).get(spacing_type, 8)
    
    def apply_theme_to_widget(self, widget: tk.Widget, widget_type: str = 'default'):
        """
        将主题应用到控件
        
        Args:
            widget: Tkinter控件
            widget_type: 控件类型
        """
        try:
            colors = self.theme_data.get('colors', {})
            fonts = self.theme_data.get('fonts', {})
            
            # 基础样式
            if hasattr(widget, 'configure'):
                config = {}
                
                # 背景色
                if widget_type in ['frame', 'toplevel', 'window']:
                    config['bg'] = colors.get('background', '#FFFFFF')
                elif widget_type in ['button']:
                    config['bg'] = colors.get('primary', '#2196F3')
                    config['fg'] = '#FFFFFF'
                    config['activebackground'] = colors.get('primary_dark', '#1976D2')
                    config['activeforeground'] = '#FFFFFF'
                elif widget_type in ['entry', 'text', 'listbox']:
                    config['bg'] = colors.get('surface', '#F5F5F5')
                    config['fg'] = colors.get('text_primary', '#212121')
                    config['insertbackground'] = colors.get('text_primary', '#212121')
                else:
                    config['bg'] = colors.get('surface', '#F5F5F5')
                    config['fg'] = colors.get('text_primary', '#212121')
                
                # 字体
                family = fonts.get('default_family', 'Microsoft YaHei UI')
                size = fonts.get('default_size', 9)
                
                if widget_type == 'title':
                    size = fonts.get('title_size', 12)
                elif widget_type == 'button':
                    size = fonts.get('button_size', 9)
                
                config['font'] = (family, size)
                
                # 边框
                if widget_type in ['entry', 'text', 'listbox', 'frame']:
                    config['relief'] = 'solid'
                    config['bd'] = self.theme_data.get('borders', {}).get('width', 1)
                    config['highlightcolor'] = colors.get('primary', '#2196F3')
                
                widget.configure(**config)
                
        except Exception as e:
            self.logger.error(f"Failed to apply theme to widget: {e}")
    
    def save_custom_theme(self, theme_id: str, theme_data: Dict[str, Any]) -> bool:
        """
        保存自定义主题
        
        Args:
            theme_id: 主题ID
            theme_data: 主题数据
            
        Returns:
            是否保存成功
        """
        try:
            if not self.theme_config['custom_themes_enabled']:
                self.logger.warning("Custom themes are disabled")
                return False
            
            themes_dir = Path(self.theme_config['themes_dir'])
            themes_dir.mkdir(parents=True, exist_ok=True)
            
            theme_file = themes_dir / f"{theme_id}.json"
            
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved custom theme: {theme_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save custom theme {theme_id}: {e}")
            return False
    
    def delete_custom_theme(self, theme_id: str) -> bool:
        """
        删除自定义主题
        
        Args:
            theme_id: 主题ID
            
        Returns:
            是否删除成功
        """
        try:
            if theme_id in self.builtin_themes:
                self.logger.warning(f"Cannot delete builtin theme: {theme_id}")
                return False
            
            themes_dir = Path(self.theme_config['themes_dir'])
            theme_file = themes_dir / f"{theme_id}.json"
            
            if theme_file.exists():
                theme_file.unlink()
                self.logger.info(f"Deleted custom theme: {theme_id}")
                return True
            else:
                self.logger.warning(f"Theme file not found: {theme_file}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete custom theme {theme_id}: {e}")
            return False
    
    def auto_detect_system_theme(self) -> str:
        """
        自动检测系统主题
        
        Returns:
            推荐的主题ID
        """
        try:
            import platform
            
            # Windows系统主题检测
            if platform.system() == "Windows":
                try:
                    import winreg
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                    value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    winreg.CloseKey(key)
                    
                    return 'light' if value else 'dark'
                except:
                    pass
            
            # macOS系统主题检测
            elif platform.system() == "Darwin":
                try:
                    import subprocess
                    result = subprocess.run([
                        'defaults', 'read', '-g', 'AppleInterfaceStyle'
                    ], capture_output=True, text=True)
                    
                    return 'dark' if 'Dark' in result.stdout else 'light'
                except:
                    pass
            
            # Linux系统主题检测
            elif platform.system() == "Linux":
                try:
                    import subprocess
                    result = subprocess.run([
                        'gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'
                    ], capture_output=True, text=True)
                    
                    theme_name = result.stdout.strip().lower()
                    return 'dark' if 'dark' in theme_name else 'light'
                except:
                    pass
            
            # 默认返回浅色主题
            return 'light'
            
        except Exception as e:
            self.logger.error(f"Failed to auto-detect system theme: {e}")
            return 'light'
    
    def add_theme_change_callback(self, callback: callable):
        """
        添加主题变更回调
        
        Args:
            callback: 回调函数
        """
        if callback not in self.theme_change_callbacks:
            self.theme_change_callbacks.append(callback)
    
    def remove_theme_change_callback(self, callback: callable):
        """
        移除主题变更回调
        
        Args:
            callback: 回调函数
        """
        if callback in self.theme_change_callbacks:
            self.theme_change_callbacks.remove(callback)
    
    def _notify_theme_change(self):
        """通知主题变更"""
        for callback in self.theme_change_callbacks:
            try:
                callback(self.current_theme, self.theme_data)
            except Exception as e:
                self.logger.error(f"Theme change callback failed: {e}")
    
    def initialize_default_theme(self):
        """初始化默认主题"""
        default_theme = self.theme_config['default_theme']
        
        # 如果启用了系统主题自动检测
        if self.theme_config['auto_detect_system']:
            detected_theme = self.auto_detect_system_theme()
            if detected_theme in self.builtin_themes:
                default_theme = detected_theme
        
        # 加载默认主题
        if not self.load_theme(default_theme):
            # 如果加载失败，使用浅色主题作为后备
            self.load_theme('light')
    
    def cleanup(self):
        """清理资源"""
        self.theme_change_callbacks.clear()
        self.logger.info("Theme manager cleanup completed")
