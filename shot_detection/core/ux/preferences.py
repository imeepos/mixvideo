"""
User Preferences Management
用户偏好设置管理
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from loguru import logger


class UserPreferences:
    """用户偏好设置管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化用户偏好设置管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="UserPreferences")
        
        # 偏好设置配置
        self.preferences_config = self.config.get('preferences', {
            'preferences_file': 'user_preferences.json',
            'auto_save': True,
            'backup_preferences': True,
            'sync_with_config': True
        })
        
        # 默认偏好设置
        self.default_preferences = {
            # 界面设置
            'ui': {
                'theme': 'light',
                'language': 'zh_CN',
                'font_size': 9,
                'window_size': '1200x800',
                'window_position': 'center',
                'show_toolbar': True,
                'show_statusbar': True,
                'show_sidebar': True
            },
            
            # 检测设置
            'detection': {
                'default_algorithm': 'frame_difference',
                'default_threshold': 0.3,
                'auto_start_detection': False,
                'show_progress_details': True,
                'auto_export_results': False,
                'default_output_format': 'json'
            },
            
            # 性能设置
            'performance': {
                'max_workers': 4,
                'enable_cache': True,
                'cache_size_mb': 512,
                'enable_gpu': False,
                'memory_limit_mb': 2048
            },
            
            # 文件设置
            'files': {
                'default_input_dir': '',
                'default_output_dir': '',
                'recent_files': [],
                'max_recent_files': 10,
                'auto_backup': True,
                'backup_interval_minutes': 30
            },
            
            # 高级设置
            'advanced': {
                'enable_debug_mode': False,
                'log_level': 'INFO',
                'enable_telemetry': True,
                'check_updates': True,
                'beta_features': False
            },
            
            # 无障碍设置
            'accessibility': {
                'enable_screen_reader': False,
                'enable_high_contrast': False,
                'enable_large_fonts': False,
                'font_scale_factor': 1.0,
                'enable_keyboard_navigation': True,
                'reduce_motion': False
            },
            
            # 快捷键设置
            'shortcuts': {
                'enable_shortcuts': True,
                'custom_shortcuts': {}
            }
        }
        
        # 当前偏好设置
        self.preferences = self.default_preferences.copy()
        
        # 偏好设置变更回调
        self.change_callbacks = []
        
        # 加载偏好设置
        self._load_preferences()
        
        self.logger.info("User preferences initialized")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        获取偏好设置值
        
        Args:
            key: 设置键（支持点分隔的路径，如 'ui.theme'）
            default: 默认值
            
        Returns:
            设置值
        """
        try:
            keys = key.split('.')
            value = self.preferences
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Failed to get preference {key}: {e}")
            return default
    
    def set_preference(self, key: str, value: Any, save: bool = True):
        """
        设置偏好设置值
        
        Args:
            key: 设置键
            value: 设置值
            save: 是否立即保存
        """
        try:
            keys = key.split('.')
            target = self.preferences
            
            # 导航到目标位置
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            
            # 设置值
            old_value = target.get(keys[-1])
            target[keys[-1]] = value
            
            # 通知变更
            self._notify_preference_change(key, old_value, value)
            
            # 保存
            if save and self.preferences_config['auto_save']:
                self._save_preferences()
            
            self.logger.info(f"Set preference {key} = {value}")
            
        except Exception as e:
            self.logger.error(f"Failed to set preference {key}: {e}")
    
    def reset_preferences(self, category: Optional[str] = None):
        """
        重置偏好设置
        
        Args:
            category: 类别名称，如果为None则重置所有
        """
        try:
            if category:
                if category in self.default_preferences:
                    self.preferences[category] = self.default_preferences[category].copy()
                    self.logger.info(f"Reset preferences category: {category}")
            else:
                self.preferences = self.default_preferences.copy()
                self.logger.info("Reset all preferences to defaults")
            
            # 保存
            self._save_preferences()
            
            # 通知变更
            self._notify_preference_change('reset', None, category)
            
        except Exception as e:
            self.logger.error(f"Failed to reset preferences: {e}")
    
    def show_preferences_dialog(self, parent: tk.Widget) -> bool:
        """
        显示偏好设置对话框
        
        Args:
            parent: 父控件
            
        Returns:
            是否保存了设置
        """
        try:
            # 创建偏好设置对话框
            dialog = tk.Toplevel(parent)
            dialog.title("偏好设置")
            dialog.geometry("700x600")
            dialog.resizable(True, True)
            dialog.transient(parent)
            dialog.grab_set()
            
            # 居中显示
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # 创建主框架
            main_frame = tk.Frame(dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 创建笔记本控件
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # 临时存储设置
            temp_preferences = self._deep_copy_dict(self.preferences)
            
            # 创建各个设置页面
            self._create_ui_preferences_tab(notebook, temp_preferences)
            self._create_detection_preferences_tab(notebook, temp_preferences)
            self._create_performance_preferences_tab(notebook, temp_preferences)
            self._create_files_preferences_tab(notebook, temp_preferences)
            self._create_accessibility_preferences_tab(notebook, temp_preferences)
            self._create_advanced_preferences_tab(notebook, temp_preferences)
            
            # 按钮框架
            button_frame = tk.Frame(main_frame)
            button_frame.pack(fill=tk.X)
            
            saved = [False]  # 使用列表在闭包中修改值
            
            def save_preferences():
                try:
                    # 应用临时设置
                    self.preferences = temp_preferences
                    self._save_preferences()
                    
                    # 通知所有变更
                    self._notify_preference_change('bulk_update', None, None)
                    
                    saved[0] = True
                    dialog.destroy()
                    messagebox.showinfo("成功", "偏好设置已保存")
                    
                except Exception as e:
                    messagebox.showerror("错误", f"保存设置失败: {e}")
            
            def cancel_preferences():
                dialog.destroy()
            
            def reset_all():
                if messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？"):
                    temp_preferences.clear()
                    temp_preferences.update(self._deep_copy_dict(self.default_preferences))
                    # 刷新界面
                    dialog.destroy()
                    self.show_preferences_dialog(parent)
            
            # 按钮
            tk.Button(
                button_frame,
                text="重置全部",
                command=reset_all,
                font=('Microsoft YaHei UI', 9)
            ).pack(side=tk.LEFT)
            
            tk.Button(
                button_frame,
                text="取消",
                command=cancel_preferences,
                font=('Microsoft YaHei UI', 9),
                padx=20
            ).pack(side=tk.RIGHT)
            
            tk.Button(
                button_frame,
                text="保存",
                command=save_preferences,
                font=('Microsoft YaHei UI', 9),
                bg='#2196F3',
                fg='white',
                padx=20
            ).pack(side=tk.RIGHT, padx=(0, 10))
            
            # 等待对话框关闭
            dialog.wait_window()
            
            return saved[0]
            
        except Exception as e:
            self.logger.error(f"Failed to show preferences dialog: {e}")
            return False
    
    def _create_ui_preferences_tab(self, notebook: ttk.Notebook, temp_prefs: Dict[str, Any]):
        """创建界面设置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="界面")
        
        # 滚动框架
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 主题设置
        theme_frame = ttk.LabelFrame(scrollable_frame, text="主题", padding=10)
        theme_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(theme_frame, text="主题:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        theme_var = tk.StringVar(value=temp_prefs['ui']['theme'])
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=theme_var,
            values=['light', 'dark', 'blue', 'green', 'high_contrast'],
            state='readonly'
        )
        theme_combo.grid(row=0, column=1, sticky=tk.W)
        theme_combo.bind('<<ComboboxSelected>>', 
                        lambda e: temp_prefs['ui'].update({'theme': theme_var.get()}))
        
        # 字体设置
        font_frame = ttk.LabelFrame(scrollable_frame, text="字体", padding=10)
        font_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(font_frame, text="字体大小:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        font_size_var = tk.IntVar(value=temp_prefs['ui']['font_size'])
        font_size_spin = tk.Spinbox(
            font_frame,
            from_=8, to=16,
            textvariable=font_size_var,
            width=10
        )
        font_size_spin.grid(row=0, column=1, sticky=tk.W)
        font_size_spin.bind('<FocusOut>', 
                           lambda e: temp_prefs['ui'].update({'font_size': font_size_var.get()}))
        
        # 窗口设置
        window_frame = ttk.LabelFrame(scrollable_frame, text="窗口", padding=10)
        window_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 显示选项
        display_frame = ttk.LabelFrame(scrollable_frame, text="显示选项", padding=10)
        display_frame.pack(fill=tk.X, padx=10, pady=5)
        
        show_toolbar_var = tk.BooleanVar(value=temp_prefs['ui']['show_toolbar'])
        tk.Checkbutton(
            display_frame,
            text="显示工具栏",
            variable=show_toolbar_var,
            command=lambda: temp_prefs['ui'].update({'show_toolbar': show_toolbar_var.get()})
        ).pack(anchor=tk.W)
        
        show_statusbar_var = tk.BooleanVar(value=temp_prefs['ui']['show_statusbar'])
        tk.Checkbutton(
            display_frame,
            text="显示状态栏",
            variable=show_statusbar_var,
            command=lambda: temp_prefs['ui'].update({'show_statusbar': show_statusbar_var.get()})
        ).pack(anchor=tk.W)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_detection_preferences_tab(self, notebook: ttk.Notebook, temp_prefs: Dict[str, Any]):
        """创建检测设置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="检测")
        
        # 算法设置
        algo_frame = ttk.LabelFrame(frame, text="默认算法", padding=10)
        algo_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(algo_frame, text="检测算法:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        algo_var = tk.StringVar(value=temp_prefs['detection']['default_algorithm'])
        algo_combo = ttk.Combobox(
            algo_frame,
            textvariable=algo_var,
            values=['frame_difference', 'histogram', 'multi'],
            state='readonly'
        )
        algo_combo.grid(row=0, column=1, sticky=tk.W)
        algo_combo.bind('<<ComboboxSelected>>', 
                       lambda e: temp_prefs['detection'].update({'default_algorithm': algo_var.get()}))
        
        tk.Label(algo_frame, text="默认阈值:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        threshold_var = tk.DoubleVar(value=temp_prefs['detection']['default_threshold'])
        threshold_scale = tk.Scale(
            algo_frame,
            from_=0.1, to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=threshold_var
        )
        threshold_scale.grid(row=1, column=1, sticky=tk.W)
        threshold_scale.bind('<ButtonRelease-1>', 
                            lambda e: temp_prefs['detection'].update({'default_threshold': threshold_var.get()}))
    
    def _create_performance_preferences_tab(self, notebook: ttk.Notebook, temp_prefs: Dict[str, Any]):
        """创建性能设置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="性能")
        
        # 处理设置
        proc_frame = ttk.LabelFrame(frame, text="处理设置", padding=10)
        proc_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(proc_frame, text="最大工作线程:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        workers_var = tk.IntVar(value=temp_prefs['performance']['max_workers'])
        workers_spin = tk.Spinbox(
            proc_frame,
            from_=1, to=16,
            textvariable=workers_var,
            width=10
        )
        workers_spin.grid(row=0, column=1, sticky=tk.W)
        workers_spin.bind('<FocusOut>', 
                         lambda e: temp_prefs['performance'].update({'max_workers': workers_var.get()}))
        
        # 缓存设置
        cache_frame = ttk.LabelFrame(frame, text="缓存设置", padding=10)
        cache_frame.pack(fill=tk.X, padx=10, pady=5)
        
        enable_cache_var = tk.BooleanVar(value=temp_prefs['performance']['enable_cache'])
        tk.Checkbutton(
            cache_frame,
            text="启用缓存",
            variable=enable_cache_var,
            command=lambda: temp_prefs['performance'].update({'enable_cache': enable_cache_var.get()})
        ).pack(anchor=tk.W)
    
    def _create_files_preferences_tab(self, notebook: ttk.Notebook, temp_prefs: Dict[str, Any]):
        """创建文件设置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="文件")
        
        # 默认目录
        dir_frame = ttk.LabelFrame(frame, text="默认目录", padding=10)
        dir_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 输入目录
        tk.Label(dir_frame, text="默认输入目录:").grid(row=0, column=0, sticky=tk.W)
        input_dir_var = tk.StringVar(value=temp_prefs['files']['default_input_dir'])
        input_dir_entry = tk.Entry(dir_frame, textvariable=input_dir_var, width=40)
        input_dir_entry.grid(row=0, column=1, padx=(10, 5))
        
        def browse_input_dir():
            dir_path = filedialog.askdirectory()
            if dir_path:
                input_dir_var.set(dir_path)
                temp_prefs['files']['default_input_dir'] = dir_path
        
        tk.Button(dir_frame, text="浏览", command=browse_input_dir).grid(row=0, column=2)
    
    def _create_accessibility_preferences_tab(self, notebook: ttk.Notebook, temp_prefs: Dict[str, Any]):
        """创建无障碍设置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="无障碍")
        
        # 无障碍选项
        access_frame = ttk.LabelFrame(frame, text="无障碍选项", padding=10)
        access_frame.pack(fill=tk.X, padx=10, pady=5)
        
        high_contrast_var = tk.BooleanVar(value=temp_prefs['accessibility']['enable_high_contrast'])
        tk.Checkbutton(
            access_frame,
            text="启用高对比度",
            variable=high_contrast_var,
            command=lambda: temp_prefs['accessibility'].update({'enable_high_contrast': high_contrast_var.get()})
        ).pack(anchor=tk.W)
        
        large_fonts_var = tk.BooleanVar(value=temp_prefs['accessibility']['enable_large_fonts'])
        tk.Checkbutton(
            access_frame,
            text="启用大字体",
            variable=large_fonts_var,
            command=lambda: temp_prefs['accessibility'].update({'enable_large_fonts': large_fonts_var.get()})
        ).pack(anchor=tk.W)
    
    def _create_advanced_preferences_tab(self, notebook: ttk.Notebook, temp_prefs: Dict[str, Any]):
        """创建高级设置标签页"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="高级")
        
        # 调试设置
        debug_frame = ttk.LabelFrame(frame, text="调试设置", padding=10)
        debug_frame.pack(fill=tk.X, padx=10, pady=5)
        
        debug_var = tk.BooleanVar(value=temp_prefs['advanced']['enable_debug_mode'])
        tk.Checkbutton(
            debug_frame,
            text="启用调试模式",
            variable=debug_var,
            command=lambda: temp_prefs['advanced'].update({'enable_debug_mode': debug_var.get()})
        ).pack(anchor=tk.W)
        
        # 更新设置
        update_frame = ttk.LabelFrame(frame, text="更新设置", padding=10)
        update_frame.pack(fill=tk.X, padx=10, pady=5)
        
        check_updates_var = tk.BooleanVar(value=temp_prefs['advanced']['check_updates'])
        tk.Checkbutton(
            update_frame,
            text="自动检查更新",
            variable=check_updates_var,
            command=lambda: temp_prefs['advanced'].update({'check_updates': check_updates_var.get()})
        ).pack(anchor=tk.W)
    
    def _deep_copy_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """深拷贝字典"""
        import copy
        return copy.deepcopy(d)
    
    def _load_preferences(self):
        """加载偏好设置"""
        try:
            prefs_file = Path(self.preferences_config['preferences_file'])
            
            if prefs_file.exists():
                with open(prefs_file, 'r', encoding='utf-8') as f:
                    loaded_prefs = json.load(f)
                
                # 合并设置（保留默认值）
                self._merge_preferences(self.preferences, loaded_prefs)
                
                self.logger.info("User preferences loaded")
            
        except Exception as e:
            self.logger.error(f"Failed to load preferences: {e}")
    
    def _save_preferences(self):
        """保存偏好设置"""
        try:
            prefs_file = Path(self.preferences_config['preferences_file'])
            prefs_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 备份现有文件
            if self.preferences_config['backup_preferences'] and prefs_file.exists():
                backup_file = prefs_file.with_suffix('.bak')
                prefs_file.replace(backup_file)
            
            with open(prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            
            self.logger.info("User preferences saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save preferences: {e}")
    
    def _merge_preferences(self, target: Dict[str, Any], source: Dict[str, Any]):
        """合并偏好设置"""
        for key, value in source.items():
            if key in target:
                if isinstance(target[key], dict) and isinstance(value, dict):
                    self._merge_preferences(target[key], value)
                else:
                    target[key] = value
    
    def add_change_callback(self, callback: Callable):
        """
        添加偏好设置变更回调
        
        Args:
            callback: 回调函数
        """
        if callback not in self.change_callbacks:
            self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable):
        """
        移除偏好设置变更回调
        
        Args:
            callback: 回调函数
        """
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    def _notify_preference_change(self, key: str, old_value: Any, new_value: Any):
        """通知偏好设置变更"""
        for callback in self.change_callbacks:
            try:
                callback(key, old_value, new_value)
            except Exception as e:
                self.logger.error(f"Preference change callback failed: {e}")
    
    def export_preferences(self, export_path: str) -> bool:
        """
        导出偏好设置
        
        Args:
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Preferences exported to: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export preferences: {e}")
            return False
    
    def import_preferences(self, import_path: str) -> bool:
        """
        导入偏好设置
        
        Args:
            import_path: 导入路径
            
        Returns:
            是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_prefs = json.load(f)
            
            # 合并设置
            self._merge_preferences(self.preferences, imported_prefs)
            
            # 保存
            self._save_preferences()
            
            # 通知变更
            self._notify_preference_change('import', None, None)
            
            self.logger.info(f"Preferences imported from: {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import preferences: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            # 保存最终设置
            self._save_preferences()
            self.change_callbacks.clear()
            self.logger.info("User preferences cleanup completed")
        except Exception as e:
            self.logger.error(f"Preferences cleanup failed: {e}")
