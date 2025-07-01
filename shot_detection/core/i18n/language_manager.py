"""
Language Management System
语言管理系统
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from loguru import logger

from .translator import Translator


class LanguageManager:
    """语言管理器"""
    
    def __init__(self, translator: Translator, config: Optional[Dict[str, Any]] = None):
        """
        初始化语言管理器
        
        Args:
            translator: 翻译器实例
            config: 配置字典
        """
        self.translator = translator
        self.config = config or {}
        self.logger = logger.bind(component="LanguageManager")
        
        # 语言管理配置
        self.language_config = self.config.get('language_manager', {
            'auto_apply_language': True,
            'save_language_preference': True,
            'language_preference_file': 'language_preference.json',
            'enable_rtl_support': True,
            'font_mapping': {}
        })
        
        # 语言变更回调
        self.language_change_callbacks = []
        
        # 当前应用的语言
        self.applied_language = None
        
        # 字体映射
        self.font_mapping = {
            'zh_CN': {'family': 'Microsoft YaHei UI', 'size': 9},
            'zh_TW': {'family': 'Microsoft JhengHei UI', 'size': 9},
            'en_US': {'family': 'Segoe UI', 'size': 9},
            'ja_JP': {'family': 'Yu Gothic UI', 'size': 9},
            'ko_KR': {'family': 'Malgun Gothic', 'size': 9},
            'fr_FR': {'family': 'Segoe UI', 'size': 9},
            'de_DE': {'family': 'Segoe UI', 'size': 9},
            'es_ES': {'family': 'Segoe UI', 'size': 9},
            'ru_RU': {'family': 'Segoe UI', 'size': 9},
        }
        
        # 更新字体映射
        self.font_mapping.update(self.language_config.get('font_mapping', {}))
        
        # 加载语言偏好
        self._load_language_preference()
        
        self.logger.info("Language manager initialized")
    
    def get_available_languages(self) -> List[Dict[str, str]]:
        """获取可用语言列表"""
        languages = []
        
        for lang_code in self.translator.get_available_languages():
            lang_info = self.translator.get_language_info(lang_code)
            languages.append({
                'code': lang_code,
                'name': lang_info['name'],
                'native_name': lang_info['native_name'],
                'direction': lang_info['direction']
            })
        
        # 按名称排序
        languages.sort(key=lambda x: x['name'])
        
        return languages
    
    def set_language(self, language_code: str, apply_immediately: bool = True) -> bool:
        """
        设置语言
        
        Args:
            language_code: 语言代码
            apply_immediately: 是否立即应用
            
        Returns:
            是否设置成功
        """
        try:
            # 设置翻译器语言
            if not self.translator.set_language(language_code):
                return False
            
            # 立即应用
            if apply_immediately and self.language_config['auto_apply_language']:
                self.apply_language(language_code)
            
            # 保存偏好
            if self.language_config['save_language_preference']:
                self._save_language_preference(language_code)
            
            self.logger.info(f"Language set to: {language_code}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set language {language_code}: {e}")
            return False
    
    def apply_language(self, language_code: str):
        """
        应用语言到界面
        
        Args:
            language_code: 语言代码
        """
        try:
            self.applied_language = language_code
            
            # 通知语言变更
            self._notify_language_change(language_code)
            
            self.logger.info(f"Language applied: {language_code}")
            
        except Exception as e:
            self.logger.error(f"Failed to apply language {language_code}: {e}")
    
    def get_current_language(self) -> str:
        """获取当前语言"""
        return self.translator.get_current_language()
    
    def get_applied_language(self) -> Optional[str]:
        """获取已应用的语言"""
        return self.applied_language
    
    def get_language_font(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        """
        获取语言对应的字体
        
        Args:
            language_code: 语言代码，如果为None则使用当前语言
            
        Returns:
            字体信息
        """
        if not language_code:
            language_code = self.get_current_language()
        
        return self.font_mapping.get(language_code, {
            'family': 'Segoe UI',
            'size': 9
        })
    
    def is_rtl_language(self, language_code: Optional[str] = None) -> bool:
        """
        检查是否为从右到左的语言
        
        Args:
            language_code: 语言代码
            
        Returns:
            是否为RTL语言
        """
        if not language_code:
            language_code = self.get_current_language()
        
        lang_info = self.translator.get_language_info(language_code)
        return lang_info.get('direction', 'ltr') == 'rtl'
    
    def show_language_selector_dialog(self, parent: tk.Widget) -> bool:
        """
        显示语言选择对话框
        
        Args:
            parent: 父控件
            
        Returns:
            是否选择了新语言
        """
        try:
            # 创建语言选择对话框
            dialog = tk.Toplevel(parent)
            dialog.title(self.translator.translate('language_selection'))
            dialog.geometry("400x300")
            dialog.resizable(False, False)
            dialog.transient(parent)
            dialog.grab_set()
            
            # 居中显示
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # 主框架
            main_frame = tk.Frame(dialog, padx=20, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 标题
            title_label = tk.Label(
                main_frame,
                text=self.translator.translate('select_language'),
                font=('Microsoft YaHei UI', 12, 'bold')
            )
            title_label.pack(pady=(0, 15))
            
            # 语言列表框架
            list_frame = tk.Frame(main_frame)
            list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            # 创建Treeview显示语言
            columns = ('code', 'name', 'native_name')
            tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
            
            # 设置列标题
            tree.heading('code', text=self.translator.translate('language_code'))
            tree.heading('name', text=self.translator.translate('language_name'))
            tree.heading('native_name', text=self.translator.translate('native_name'))
            
            # 设置列宽
            tree.column('code', width=80)
            tree.column('name', width=120)
            tree.column('native_name', width=120)
            
            # 添加滚动条
            scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # 填充语言数据
            languages = self.get_available_languages()
            current_language = self.get_current_language()
            
            for lang in languages:
                item_id = tree.insert('', tk.END, values=(
                    lang['code'],
                    lang['name'],
                    lang['native_name']
                ))
                
                # 选中当前语言
                if lang['code'] == current_language:
                    tree.selection_set(item_id)
                    tree.focus(item_id)
            
            # 打包组件
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 预览框架
            preview_frame = tk.LabelFrame(
                main_frame,
                text=self.translator.translate('preview'),
                padx=10,
                pady=10
            )
            preview_frame.pack(fill=tk.X, pady=(0, 15))
            
            preview_label = tk.Label(
                preview_frame,
                text=self.translator.translate('app_name'),
                font=('Microsoft YaHei UI', 10)
            )
            preview_label.pack()
            
            # 按钮框架
            button_frame = tk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            selected_language = [None]  # 使用列表在闭包中修改值
            
            def on_language_select(event):
                """语言选择事件"""
                selection = tree.selection()
                if selection:
                    item = tree.item(selection[0])
                    lang_code = item['values'][0]
                    
                    # 更新预览
                    temp_translator = Translator()
                    temp_translator.set_language(lang_code)
                    preview_text = temp_translator.translate('app_name')
                    
                    # 更新字体
                    font_info = self.get_language_font(lang_code)
                    preview_label.config(
                        text=preview_text,
                        font=(font_info['family'], font_info['size'])
                    )
            
            def apply_language():
                """应用语言"""
                selection = tree.selection()
                if selection:
                    item = tree.item(selection[0])
                    lang_code = item['values'][0]
                    
                    if self.set_language(lang_code):
                        selected_language[0] = lang_code
                        dialog.destroy()
                        messagebox.showinfo(
                            self.translator.translate('success'),
                            self.translator.translate('language_changed')
                        )
                    else:
                        messagebox.showerror(
                            self.translator.translate('error'),
                            self.translator.translate('language_change_failed')
                        )
                else:
                    messagebox.showwarning(
                        self.translator.translate('warning'),
                        self.translator.translate('please_select_language')
                    )
            
            def cancel_selection():
                """取消选择"""
                dialog.destroy()
            
            # 绑定事件
            tree.bind('<<TreeviewSelect>>', on_language_select)
            tree.bind('<Double-1>', lambda e: apply_language())
            
            # 按钮
            tk.Button(
                button_frame,
                text=self.translator.translate('cancel'),
                command=cancel_selection,
                font=('Microsoft YaHei UI', 9),
                padx=20
            ).pack(side=tk.RIGHT)
            
            tk.Button(
                button_frame,
                text=self.translator.translate('apply'),
                command=apply_language,
                font=('Microsoft YaHei UI', 9),
                bg='#2196F3',
                fg='white',
                padx=20
            ).pack(side=tk.RIGHT, padx=(0, 10))
            
            # 等待对话框关闭
            dialog.wait_window()
            
            return selected_language[0] is not None
            
        except Exception as e:
            self.logger.error(f"Failed to show language selector dialog: {e}")
            return False
    
    def create_language_menu(self, parent_menu: tk.Menu) -> tk.Menu:
        """
        创建语言菜单
        
        Args:
            parent_menu: 父菜单
            
        Returns:
            语言菜单
        """
        try:
            language_menu = tk.Menu(parent_menu, tearoff=0)
            
            languages = self.get_available_languages()
            current_language = self.get_current_language()
            
            for lang in languages:
                language_menu.add_radiobutton(
                    label=f"{lang['native_name']} ({lang['name']})",
                    value=lang['code'],
                    variable=tk.StringVar(value=current_language),
                    command=lambda code=lang['code']: self.set_language(code)
                )
            
            return language_menu
            
        except Exception as e:
            self.logger.error(f"Failed to create language menu: {e}")
            return tk.Menu(parent_menu, tearoff=0)
    
    def add_language_change_callback(self, callback: Callable):
        """
        添加语言变更回调
        
        Args:
            callback: 回调函数
        """
        if callback not in self.language_change_callbacks:
            self.language_change_callbacks.append(callback)
    
    def remove_language_change_callback(self, callback: Callable):
        """
        移除语言变更回调
        
        Args:
            callback: 回调函数
        """
        if callback in self.language_change_callbacks:
            self.language_change_callbacks.remove(callback)
    
    def _notify_language_change(self, language_code: str):
        """通知语言变更"""
        for callback in self.language_change_callbacks:
            try:
                callback(language_code)
            except Exception as e:
                self.logger.error(f"Language change callback failed: {e}")
    
    def _load_language_preference(self):
        """加载语言偏好"""
        try:
            if not self.language_config['save_language_preference']:
                return
            
            pref_file = Path(self.language_config['language_preference_file'])
            
            if pref_file.exists():
                with open(pref_file, 'r', encoding='utf-8') as f:
                    preference = json.load(f)
                
                preferred_language = preference.get('language')
                if preferred_language:
                    self.set_language(preferred_language, apply_immediately=False)
                
                self.logger.info(f"Loaded language preference: {preferred_language}")
            
        except Exception as e:
            self.logger.error(f"Failed to load language preference: {e}")
    
    def _save_language_preference(self, language_code: str):
        """保存语言偏好"""
        try:
            if not self.language_config['save_language_preference']:
                return
            
            pref_file = Path(self.language_config['language_preference_file'])
            pref_file.parent.mkdir(parents=True, exist_ok=True)
            
            preference = {
                'language': language_code,
                'saved_at': self._get_current_timestamp()
            }
            
            with open(pref_file, 'w', encoding='utf-8') as f:
                json.dump(preference, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved language preference: {language_code}")
            
        except Exception as e:
            self.logger.error(f"Failed to save language preference: {e}")
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def update_widget_language(self, widget: tk.Widget, text_key: str):
        """
        更新控件的语言文本
        
        Args:
            widget: 控件
            text_key: 文本键
        """
        try:
            translated_text = self.translator.translate(text_key)
            
            if hasattr(widget, 'config'):
                widget.config(text=translated_text)
            
            # 更新字体
            current_language = self.get_current_language()
            font_info = self.get_language_font(current_language)
            
            if hasattr(widget, 'config'):
                try:
                    widget.config(font=(font_info['family'], font_info['size']))
                except:
                    pass  # 某些控件可能不支持字体设置
            
        except Exception as e:
            self.logger.error(f"Failed to update widget language: {e}")
    
    def apply_rtl_layout(self, widget: tk.Widget, language_code: Optional[str] = None):
        """
        应用从右到左布局
        
        Args:
            widget: 控件
            language_code: 语言代码
        """
        try:
            if not self.language_config['enable_rtl_support']:
                return
            
            if self.is_rtl_language(language_code):
                # 应用RTL布局
                if hasattr(widget, 'pack_configure'):
                    widget.pack_configure(side=tk.RIGHT)
                elif hasattr(widget, 'grid_configure'):
                    # 对于grid布局，需要调整列的顺序
                    pass
            
        except Exception as e:
            self.logger.error(f"Failed to apply RTL layout: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.language_change_callbacks.clear()
            self.logger.info("Language manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Language manager cleanup failed: {e}")
