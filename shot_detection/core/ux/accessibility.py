"""
Accessibility Manager
无障碍访问管理器
"""

import tkinter as tk
from typing import Dict, Any, Optional, List
from loguru import logger


class AccessibilityManager:
    """无障碍访问管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化无障碍访问管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="AccessibilityManager")
        
        # 无障碍配置
        self.accessibility_config = self.config.get('accessibility', {
            'enable_screen_reader': False,
            'enable_high_contrast': False,
            'enable_large_fonts': False,
            'enable_keyboard_navigation': True,
            'enable_focus_indicators': True,
            'enable_tooltips': True,
            'font_scale_factor': 1.0,
            'animation_duration': 200,
            'reduce_motion': False
        })
        
        # 当前设置
        self.current_settings = self.accessibility_config.copy()
        
        # 焦点管理
        self.focus_ring_widgets = []
        self.current_focus_index = -1
        
        # 屏幕阅读器支持
        self.screen_reader_enabled = False
        
        self.logger.info("Accessibility manager initialized")
    
    def enable_screen_reader_support(self, root_widget: tk.Widget):
        """
        启用屏幕阅读器支持
        
        Args:
            root_widget: 根控件
        """
        try:
            self.screen_reader_enabled = True
            
            # 设置窗口属性
            if hasattr(root_widget, 'wm_attributes'):
                # 设置窗口为可访问
                root_widget.wm_attributes('-toolwindow', False)
            
            # 添加ARIA标签支持
            self._add_aria_labels(root_widget)
            
            # 设置键盘导航
            self._setup_keyboard_navigation(root_widget)
            
            self.logger.info("Screen reader support enabled")
            
        except Exception as e:
            self.logger.error(f"Failed to enable screen reader support: {e}")
    
    def _add_aria_labels(self, widget: tk.Widget):
        """
        添加ARIA标签
        
        Args:
            widget: 控件
        """
        try:
            # 为不同类型的控件添加适当的标签
            widget_class = widget.__class__.__name__
            
            if widget_class == 'Button':
                if not hasattr(widget, 'aria_label'):
                    text = widget.cget('text') if hasattr(widget, 'cget') else ''
                    widget.aria_label = f"按钮: {text}"
            
            elif widget_class == 'Entry':
                if not hasattr(widget, 'aria_label'):
                    widget.aria_label = "文本输入框"
            
            elif widget_class == 'Text':
                if not hasattr(widget, 'aria_label'):
                    widget.aria_label = "文本编辑区域"
            
            elif widget_class == 'Listbox':
                if not hasattr(widget, 'aria_label'):
                    widget.aria_label = "列表框"
            
            elif widget_class == 'Label':
                if not hasattr(widget, 'aria_label'):
                    text = widget.cget('text') if hasattr(widget, 'cget') else ''
                    widget.aria_label = f"标签: {text}"
            
            # 递归处理子控件
            for child in widget.winfo_children():
                self._add_aria_labels(child)
                
        except Exception as e:
            self.logger.error(f"Failed to add ARIA labels: {e}")
    
    def _setup_keyboard_navigation(self, root_widget: tk.Widget):
        """
        设置键盘导航
        
        Args:
            root_widget: 根控件
        """
        try:
            # 收集可聚焦的控件
            self._collect_focusable_widgets(root_widget)
            
            # 绑定键盘事件
            root_widget.bind('<Tab>', self._handle_tab_navigation)
            root_widget.bind('<Shift-Tab>', self._handle_shift_tab_navigation)
            root_widget.bind('<Return>', self._handle_enter_key)
            root_widget.bind('<space>', self._handle_space_key)
            root_widget.bind('<Escape>', self._handle_escape_key)
            
            # 设置初始焦点
            if self.focus_ring_widgets:
                self.current_focus_index = 0
                self._set_focus(0)
            
            self.logger.info("Keyboard navigation setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup keyboard navigation: {e}")
    
    def _collect_focusable_widgets(self, widget: tk.Widget):
        """
        收集可聚焦的控件
        
        Args:
            widget: 控件
        """
        try:
            # 检查控件是否可聚焦
            if self._is_focusable(widget):
                self.focus_ring_widgets.append(widget)
            
            # 递归处理子控件
            for child in widget.winfo_children():
                self._collect_focusable_widgets(child)
                
        except Exception as e:
            self.logger.error(f"Failed to collect focusable widgets: {e}")
    
    def _is_focusable(self, widget: tk.Widget) -> bool:
        """
        检查控件是否可聚焦
        
        Args:
            widget: 控件
            
        Returns:
            是否可聚焦
        """
        try:
            widget_class = widget.__class__.__name__
            
            # 可聚焦的控件类型
            focusable_types = [
                'Button', 'Entry', 'Text', 'Listbox', 'Checkbutton', 
                'Radiobutton', 'Scale', 'Spinbox', 'Combobox'
            ]
            
            if widget_class not in focusable_types:
                return False
            
            # 检查控件状态
            try:
                state = widget.cget('state')
                if state in ['disabled', 'readonly']:
                    return False
            except:
                pass
            
            # 检查控件是否可见
            try:
                if not widget.winfo_viewable():
                    return False
            except:
                pass
            
            return True
            
        except Exception:
            return False
    
    def _handle_tab_navigation(self, event):
        """处理Tab键导航"""
        try:
            if self.focus_ring_widgets:
                self.current_focus_index = (self.current_focus_index + 1) % len(self.focus_ring_widgets)
                self._set_focus(self.current_focus_index)
            return 'break'
        except Exception as e:
            self.logger.error(f"Tab navigation failed: {e}")
    
    def _handle_shift_tab_navigation(self, event):
        """处理Shift+Tab键导航"""
        try:
            if self.focus_ring_widgets:
                self.current_focus_index = (self.current_focus_index - 1) % len(self.focus_ring_widgets)
                self._set_focus(self.current_focus_index)
            return 'break'
        except Exception as e:
            self.logger.error(f"Shift+Tab navigation failed: {e}")
    
    def _handle_enter_key(self, event):
        """处理回车键"""
        try:
            if 0 <= self.current_focus_index < len(self.focus_ring_widgets):
                widget = self.focus_ring_widgets[self.current_focus_index]
                if widget.__class__.__name__ == 'Button':
                    widget.invoke()
            return 'break'
        except Exception as e:
            self.logger.error(f"Enter key handling failed: {e}")
    
    def _handle_space_key(self, event):
        """处理空格键"""
        try:
            if 0 <= self.current_focus_index < len(self.focus_ring_widgets):
                widget = self.focus_ring_widgets[self.current_focus_index]
                widget_class = widget.__class__.__name__
                
                if widget_class in ['Button', 'Checkbutton', 'Radiobutton']:
                    widget.invoke()
            return 'break'
        except Exception as e:
            self.logger.error(f"Space key handling failed: {e}")
    
    def _handle_escape_key(self, event):
        """处理Escape键"""
        try:
            # 可以用于关闭对话框或取消操作
            widget = event.widget
            
            # 查找最近的Toplevel窗口
            while widget and not isinstance(widget, tk.Toplevel):
                widget = widget.master
            
            if widget and isinstance(widget, tk.Toplevel):
                widget.destroy()
            
        except Exception as e:
            self.logger.error(f"Escape key handling failed: {e}")
    
    def _set_focus(self, index: int):
        """
        设置焦点到指定控件
        
        Args:
            index: 控件索引
        """
        try:
            if 0 <= index < len(self.focus_ring_widgets):
                widget = self.focus_ring_widgets[index]
                widget.focus_set()
                
                # 添加焦点指示器
                if self.current_settings['enable_focus_indicators']:
                    self._add_focus_indicator(widget)
                
                # 屏幕阅读器支持
                if self.screen_reader_enabled:
                    self._announce_widget(widget)
                    
        except Exception as e:
            self.logger.error(f"Failed to set focus: {e}")
    
    def _add_focus_indicator(self, widget: tk.Widget):
        """
        添加焦点指示器
        
        Args:
            widget: 控件
        """
        try:
            # 移除之前的焦点指示器
            self._remove_focus_indicators()
            
            # 添加高亮边框
            original_relief = widget.cget('relief') if hasattr(widget, 'cget') else 'flat'
            original_bd = widget.cget('bd') if hasattr(widget, 'cget') else 1
            
            widget.configure(relief='solid', bd=2, highlightthickness=2, highlightcolor='#2196F3')
            
            # 保存原始样式以便恢复
            widget._original_relief = original_relief
            widget._original_bd = original_bd
            widget._has_focus_indicator = True
            
        except Exception as e:
            self.logger.error(f"Failed to add focus indicator: {e}")
    
    def _remove_focus_indicators(self):
        """移除所有焦点指示器"""
        try:
            for widget in self.focus_ring_widgets:
                if hasattr(widget, '_has_focus_indicator') and widget._has_focus_indicator:
                    original_relief = getattr(widget, '_original_relief', 'flat')
                    original_bd = getattr(widget, '_original_bd', 1)
                    
                    widget.configure(relief=original_relief, bd=original_bd, highlightthickness=0)
                    widget._has_focus_indicator = False
                    
        except Exception as e:
            self.logger.error(f"Failed to remove focus indicators: {e}")
    
    def _announce_widget(self, widget: tk.Widget):
        """
        为屏幕阅读器朗读控件信息
        
        Args:
            widget: 控件
        """
        try:
            if hasattr(widget, 'aria_label'):
                announcement = widget.aria_label
            else:
                widget_class = widget.__class__.__name__
                text = ''
                
                try:
                    text = widget.cget('text')
                except:
                    pass
                
                announcement = f"{widget_class}: {text}"
            
            # 这里可以集成实际的屏幕阅读器API
            self.logger.info(f"Screen reader: {announcement}")
            
        except Exception as e:
            self.logger.error(f"Failed to announce widget: {e}")
    
    def enable_high_contrast_mode(self, theme_manager=None):
        """
        启用高对比度模式
        
        Args:
            theme_manager: 主题管理器
        """
        try:
            self.current_settings['enable_high_contrast'] = True
            
            if theme_manager:
                theme_manager.load_theme('high_contrast')
            
            self.logger.info("High contrast mode enabled")
            
        except Exception as e:
            self.logger.error(f"Failed to enable high contrast mode: {e}")
    
    def set_font_scale(self, scale_factor: float, theme_manager=None):
        """
        设置字体缩放
        
        Args:
            scale_factor: 缩放因子
            theme_manager: 主题管理器
        """
        try:
            self.current_settings['font_scale_factor'] = scale_factor
            self.current_settings['enable_large_fonts'] = scale_factor > 1.0
            
            # 这里可以通知主题管理器更新字体大小
            if theme_manager:
                theme_data = theme_manager.get_theme_data()
                if 'fonts' in theme_data:
                    for font_key in theme_data['fonts']:
                        if font_key.endswith('_size'):
                            original_size = theme_data['fonts'][font_key]
                            theme_data['fonts'][font_key] = int(original_size * scale_factor)
            
            self.logger.info(f"Font scale set to: {scale_factor}")
            
        except Exception as e:
            self.logger.error(f"Failed to set font scale: {e}")
    
    def add_tooltip(self, widget: tk.Widget, text: str):
        """
        添加工具提示
        
        Args:
            widget: 控件
            text: 提示文本
        """
        try:
            if not self.current_settings['enable_tooltips']:
                return
            
            def show_tooltip(event):
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                
                label = tk.Label(
                    tooltip,
                    text=text,
                    background='#FFFFDD',
                    relief='solid',
                    borderwidth=1,
                    font=('Microsoft YaHei UI', 8)
                )
                label.pack()
                
                def hide_tooltip():
                    tooltip.destroy()
                
                tooltip.after(3000, hide_tooltip)  # 3秒后自动隐藏
                widget.tooltip = tooltip
            
            def hide_tooltip(event):
                if hasattr(widget, 'tooltip'):
                    widget.tooltip.destroy()
                    delattr(widget, 'tooltip')
            
            widget.bind('<Enter>', show_tooltip)
            widget.bind('<Leave>', hide_tooltip)
            
        except Exception as e:
            self.logger.error(f"Failed to add tooltip: {e}")
    
    def get_accessibility_settings(self) -> Dict[str, Any]:
        """获取当前无障碍设置"""
        return self.current_settings.copy()
    
    def update_accessibility_settings(self, settings: Dict[str, Any]):
        """
        更新无障碍设置
        
        Args:
            settings: 新设置
        """
        try:
            self.current_settings.update(settings)
            self.logger.info("Accessibility settings updated")
        except Exception as e:
            self.logger.error(f"Failed to update accessibility settings: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self._remove_focus_indicators()
            self.focus_ring_widgets.clear()
            self.logger.info("Accessibility manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Accessibility cleanup failed: {e}")
