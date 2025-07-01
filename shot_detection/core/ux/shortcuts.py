"""
Keyboard Shortcuts Manager
键盘快捷键管理器
"""

import tkinter as tk
from typing import Dict, Any, Optional, Callable, List
from loguru import logger


class ShortcutManager:
    """快捷键管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化快捷键管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="ShortcutManager")
        
        # 快捷键配置
        self.shortcut_config = self.config.get('shortcuts', {
            'enable_shortcuts': True,
            'enable_custom_shortcuts': True,
            'show_shortcuts_in_tooltips': True,
            'shortcuts_file': 'shortcuts.json'
        })
        
        # 快捷键注册表
        self.shortcuts = {}
        self.widget_bindings = {}
        
        # 默认快捷键
        self.default_shortcuts = {
            # 文件操作
            'file_open': {'key': 'Ctrl+o', 'description': '打开文件'},
            'file_save': {'key': 'Ctrl+s', 'description': '保存文件'},
            'file_save_as': {'key': 'Ctrl+Shift+s', 'description': '另存为'},
            'file_exit': {'key': 'Ctrl+q', 'description': '退出程序'},
            
            # 编辑操作
            'edit_undo': {'key': 'Ctrl+z', 'description': '撤销'},
            'edit_redo': {'key': 'Ctrl+y', 'description': '重做'},
            'edit_cut': {'key': 'Ctrl+x', 'description': '剪切'},
            'edit_copy': {'key': 'Ctrl+c', 'description': '复制'},
            'edit_paste': {'key': 'Ctrl+v', 'description': '粘贴'},
            'edit_select_all': {'key': 'Ctrl+a', 'description': '全选'},
            'edit_find': {'key': 'Ctrl+f', 'description': '查找'},
            'edit_replace': {'key': 'Ctrl+h', 'description': '替换'},
            
            # 视图操作
            'view_zoom_in': {'key': 'Ctrl+plus', 'description': '放大'},
            'view_zoom_out': {'key': 'Ctrl+minus', 'description': '缩小'},
            'view_zoom_reset': {'key': 'Ctrl+0', 'description': '重置缩放'},
            'view_fullscreen': {'key': 'F11', 'description': '全屏'},
            'view_refresh': {'key': 'F5', 'description': '刷新'},
            
            # 视频操作
            'video_play_pause': {'key': 'space', 'description': '播放/暂停'},
            'video_stop': {'key': 'Ctrl+space', 'description': '停止'},
            'video_previous': {'key': 'Left', 'description': '上一帧'},
            'video_next': {'key': 'Right', 'description': '下一帧'},
            'video_jump_backward': {'key': 'Ctrl+Left', 'description': '快退'},
            'video_jump_forward': {'key': 'Ctrl+Right', 'description': '快进'},
            
            # 检测操作
            'detection_start': {'key': 'Ctrl+d', 'description': '开始检测'},
            'detection_stop': {'key': 'Ctrl+Shift+d', 'description': '停止检测'},
            'detection_export': {'key': 'Ctrl+e', 'description': '导出结果'},
            
            # 窗口操作
            'window_new': {'key': 'Ctrl+n', 'description': '新建窗口'},
            'window_close': {'key': 'Ctrl+w', 'description': '关闭窗口'},
            'window_minimize': {'key': 'Ctrl+m', 'description': '最小化'},
            'window_maximize': {'key': 'Ctrl+Shift+m', 'description': '最大化'},
            
            # 帮助操作
            'help_about': {'key': 'F1', 'description': '关于'},
            'help_shortcuts': {'key': 'Ctrl+Shift+slash', 'description': '快捷键帮助'},
            'help_documentation': {'key': 'Ctrl+F1', 'description': '文档'},
            
            # 开发调试
            'debug_console': {'key': 'F12', 'description': '调试控制台'},
            'debug_reload': {'key': 'Ctrl+F5', 'description': '重新加载'},
        }
        
        # 初始化默认快捷键
        self.shortcuts = self.default_shortcuts.copy()
        
        self.logger.info("Shortcut manager initialized")
    
    def register_shortcut(self, shortcut_id: str, key_combination: str, 
                         callback: Callable, description: str = ""):
        """
        注册快捷键
        
        Args:
            shortcut_id: 快捷键ID
            key_combination: 键组合
            callback: 回调函数
            description: 描述
        """
        try:
            if not self.shortcut_config['enable_shortcuts']:
                return
            
            self.shortcuts[shortcut_id] = {
                'key': key_combination,
                'callback': callback,
                'description': description
            }
            
            self.logger.info(f"Registered shortcut: {shortcut_id} ({key_combination})")
            
        except Exception as e:
            self.logger.error(f"Failed to register shortcut {shortcut_id}: {e}")
    
    def unregister_shortcut(self, shortcut_id: str):
        """
        注销快捷键
        
        Args:
            shortcut_id: 快捷键ID
        """
        try:
            if shortcut_id in self.shortcuts:
                del self.shortcuts[shortcut_id]
                self.logger.info(f"Unregistered shortcut: {shortcut_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to unregister shortcut {shortcut_id}: {e}")
    
    def bind_shortcuts_to_widget(self, widget: tk.Widget):
        """
        将快捷键绑定到控件
        
        Args:
            widget: 控件
        """
        try:
            if not self.shortcut_config['enable_shortcuts']:
                return
            
            widget_id = id(widget)
            self.widget_bindings[widget_id] = []
            
            for shortcut_id, shortcut_data in self.shortcuts.items():
                if 'callback' in shortcut_data:
                    key = shortcut_data['key']
                    callback = shortcut_data['callback']
                    
                    # 转换键组合格式
                    tk_key = self._convert_key_format(key)
                    
                    # 绑定事件
                    widget.bind(f'<{tk_key}>', lambda e, cb=callback: self._handle_shortcut(e, cb))
                    
                    # 记录绑定
                    self.widget_bindings[widget_id].append((tk_key, callback))
            
            self.logger.info(f"Bound {len(self.shortcuts)} shortcuts to widget")
            
        except Exception as e:
            self.logger.error(f"Failed to bind shortcuts to widget: {e}")
    
    def unbind_shortcuts_from_widget(self, widget: tk.Widget):
        """
        从控件解绑快捷键
        
        Args:
            widget: 控件
        """
        try:
            widget_id = id(widget)
            
            if widget_id in self.widget_bindings:
                for tk_key, callback in self.widget_bindings[widget_id]:
                    widget.unbind(f'<{tk_key}>')
                
                del self.widget_bindings[widget_id]
                self.logger.info("Unbound shortcuts from widget")
            
        except Exception as e:
            self.logger.error(f"Failed to unbind shortcuts from widget: {e}")
    
    def _convert_key_format(self, key: str) -> str:
        """
        转换键格式为Tkinter格式
        
        Args:
            key: 键组合字符串
            
        Returns:
            Tkinter格式的键组合
        """
        try:
            # 替换常见的键名
            key_mapping = {
                'ctrl': 'Control',
                'alt': 'Alt',
                'shift': 'Shift',
                'cmd': 'Command',
                'meta': 'Meta',
                'plus': 'plus',
                'minus': 'minus',
                'slash': 'slash',
                'space': 'space',
                'enter': 'Return',
                'return': 'Return',
                'tab': 'Tab',
                'escape': 'Escape',
                'esc': 'Escape',
                'backspace': 'BackSpace',
                'delete': 'Delete',
                'home': 'Home',
                'end': 'End',
                'pageup': 'Page_Up',
                'pagedown': 'Page_Down',
                'up': 'Up',
                'down': 'Down',
                'left': 'Left',
                'right': 'Right',
            }
            
            # 处理功能键
            for i in range(1, 13):
                key_mapping[f'f{i}'] = f'F{i}'
            
            # 分割键组合
            parts = key.lower().split('+')
            converted_parts = []
            
            for part in parts:
                if part in key_mapping:
                    converted_parts.append(key_mapping[part])
                else:
                    # 保持原样（如字母、数字）
                    converted_parts.append(part)
            
            return '-'.join(converted_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to convert key format: {e}")
            return key
    
    def _handle_shortcut(self, event, callback: Callable):
        """
        处理快捷键事件
        
        Args:
            event: 事件对象
            callback: 回调函数
        """
        try:
            # 调用回调函数
            if callable(callback):
                result = callback()
                
                # 如果回调返回'break'，阻止事件传播
                if result == 'break':
                    return 'break'
            
        except Exception as e:
            self.logger.error(f"Shortcut callback failed: {e}")
    
    def get_shortcut_list(self) -> List[Dict[str, str]]:
        """
        获取快捷键列表
        
        Returns:
            快捷键列表
        """
        shortcut_list = []
        
        for shortcut_id, shortcut_data in self.shortcuts.items():
            shortcut_list.append({
                'id': shortcut_id,
                'key': shortcut_data['key'],
                'description': shortcut_data.get('description', ''),
                'category': self._get_shortcut_category(shortcut_id)
            })
        
        # 按类别排序
        shortcut_list.sort(key=lambda x: (x['category'], x['description']))
        
        return shortcut_list
    
    def _get_shortcut_category(self, shortcut_id: str) -> str:
        """
        获取快捷键类别
        
        Args:
            shortcut_id: 快捷键ID
            
        Returns:
            类别名称
        """
        if shortcut_id.startswith('file_'):
            return '文件'
        elif shortcut_id.startswith('edit_'):
            return '编辑'
        elif shortcut_id.startswith('view_'):
            return '视图'
        elif shortcut_id.startswith('video_'):
            return '视频'
        elif shortcut_id.startswith('detection_'):
            return '检测'
        elif shortcut_id.startswith('window_'):
            return '窗口'
        elif shortcut_id.startswith('help_'):
            return '帮助'
        elif shortcut_id.startswith('debug_'):
            return '调试'
        else:
            return '其他'
    
    def create_shortcuts_help_dialog(self, parent: tk.Widget) -> tk.Toplevel:
        """
        创建快捷键帮助对话框
        
        Args:
            parent: 父控件
            
        Returns:
            帮助对话框
        """
        try:
            dialog = tk.Toplevel(parent)
            dialog.title("快捷键帮助")
            dialog.geometry("600x500")
            dialog.resizable(True, True)
            
            # 创建主框架
            main_frame = tk.Frame(dialog)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # 标题
            title_label = tk.Label(
                main_frame,
                text="键盘快捷键",
                font=('Microsoft YaHei UI', 14, 'bold')
            )
            title_label.pack(pady=(0, 10))
            
            # 创建滚动框架
            canvas = tk.Canvas(main_frame)
            scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # 获取快捷键列表
            shortcuts = self.get_shortcut_list()
            
            # 按类别分组
            categories = {}
            for shortcut in shortcuts:
                category = shortcut['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(shortcut)
            
            # 显示快捷键
            for category, category_shortcuts in categories.items():
                # 类别标题
                category_label = tk.Label(
                    scrollable_frame,
                    text=category,
                    font=('Microsoft YaHei UI', 11, 'bold'),
                    fg='#2196F3'
                )
                category_label.pack(anchor='w', pady=(10, 5))
                
                # 快捷键列表
                for shortcut in category_shortcuts:
                    shortcut_frame = tk.Frame(scrollable_frame)
                    shortcut_frame.pack(fill=tk.X, pady=2)
                    
                    # 键组合
                    key_label = tk.Label(
                        shortcut_frame,
                        text=shortcut['key'],
                        font=('Consolas', 9),
                        bg='#F0F0F0',
                        relief='solid',
                        bd=1,
                        padx=5,
                        pady=2
                    )
                    key_label.pack(side=tk.LEFT, padx=(0, 10))
                    
                    # 描述
                    desc_label = tk.Label(
                        shortcut_frame,
                        text=shortcut['description'],
                        font=('Microsoft YaHei UI', 9),
                        anchor='w'
                    )
                    desc_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # 打包滚动组件
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # 关闭按钮
            close_button = tk.Button(
                main_frame,
                text="关闭",
                command=dialog.destroy,
                font=('Microsoft YaHei UI', 9)
            )
            close_button.pack(pady=(10, 0))
            
            # 设置对话框属性
            dialog.transient(parent)
            dialog.grab_set()
            
            # 居中显示
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            return dialog
            
        except Exception as e:
            self.logger.error(f"Failed to create shortcuts help dialog: {e}")
            return None
    
    def update_shortcut_key(self, shortcut_id: str, new_key: str) -> bool:
        """
        更新快捷键
        
        Args:
            shortcut_id: 快捷键ID
            new_key: 新的键组合
            
        Returns:
            是否更新成功
        """
        try:
            if shortcut_id in self.shortcuts:
                self.shortcuts[shortcut_id]['key'] = new_key
                self.logger.info(f"Updated shortcut {shortcut_id} to {new_key}")
                return True
            else:
                self.logger.warning(f"Shortcut not found: {shortcut_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to update shortcut {shortcut_id}: {e}")
            return False
    
    def reset_to_defaults(self):
        """重置为默认快捷键"""
        try:
            # 保留有回调函数的快捷键的回调
            callbacks = {}
            for shortcut_id, shortcut_data in self.shortcuts.items():
                if 'callback' in shortcut_data:
                    callbacks[shortcut_id] = shortcut_data['callback']
            
            # 重置为默认
            self.shortcuts = self.default_shortcuts.copy()
            
            # 恢复回调函数
            for shortcut_id, callback in callbacks.items():
                if shortcut_id in self.shortcuts:
                    self.shortcuts[shortcut_id]['callback'] = callback
            
            self.logger.info("Reset shortcuts to defaults")
            
        except Exception as e:
            self.logger.error(f"Failed to reset shortcuts: {e}")
    
    def save_custom_shortcuts(self, file_path: Optional[str] = None):
        """
        保存自定义快捷键
        
        Args:
            file_path: 保存路径
        """
        try:
            import json
            
            if not file_path:
                file_path = self.shortcut_config['shortcuts_file']
            
            # 准备保存数据（排除回调函数）
            save_data = {}
            for shortcut_id, shortcut_data in self.shortcuts.items():
                save_data[shortcut_id] = {
                    'key': shortcut_data['key'],
                    'description': shortcut_data.get('description', '')
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved custom shortcuts to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save custom shortcuts: {e}")
    
    def load_custom_shortcuts(self, file_path: Optional[str] = None):
        """
        加载自定义快捷键
        
        Args:
            file_path: 加载路径
        """
        try:
            import json
            from pathlib import Path
            
            if not file_path:
                file_path = self.shortcut_config['shortcuts_file']
            
            if not Path(file_path).exists():
                self.logger.info("No custom shortcuts file found")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                custom_shortcuts = json.load(f)
            
            # 更新快捷键
            for shortcut_id, shortcut_data in custom_shortcuts.items():
                if shortcut_id in self.shortcuts:
                    self.shortcuts[shortcut_id]['key'] = shortcut_data['key']
                    if 'description' in shortcut_data:
                        self.shortcuts[shortcut_id]['description'] = shortcut_data['description']
            
            self.logger.info(f"Loaded custom shortcuts from {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to load custom shortcuts: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.widget_bindings.clear()
            self.logger.info("Shortcut manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Shortcut cleanup failed: {e}")
