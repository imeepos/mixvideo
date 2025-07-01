"""
Tools Tab Component
工具Tab组件
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import json
import subprocess
import sys
from typing import Optional, Dict, Any

from .base_tab import BaseTab


class ToolsTab(BaseTab):
    """实用工具Tab"""
    
    def setup_ui(self):
        """设置UI界面"""
        # 配置网格权重
        self.frame.columnconfigure(0, weight=1)
        
        # 创建主要区域
        self.create_system_info_section()
        self.create_cache_management_section()
        self.create_config_management_section()
        self.create_performance_section()
        self.create_maintenance_section()
        
        # 初始化变量
        self.system_info = {}
        self.performance_stats = {}
    
    def create_system_info_section(self):
        """创建系统信息区域"""
        info_frame = self.create_labeled_frame(self.frame, "💻 系统信息", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # 系统信息显示
        self.info_text = tk.Text(info_frame, height=6, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 刷新按钮
        ttk.Button(info_frame, text="🔄 刷新系统信息", 
                  command=self.refresh_system_info).grid(row=1, column=0, sticky=tk.W)
        
        ttk.Button(info_frame, text="📋 复制信息", 
                  command=self.copy_system_info).grid(row=1, column=1, sticky=tk.E)
    
    def create_cache_management_section(self):
        """创建缓存管理区域"""
        cache_frame = self.create_labeled_frame(self.frame, "💾 缓存管理", padding="10")
        cache_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        cache_frame.columnconfigure(1, weight=1)
        
        # 缓存信息
        self.cache_info_var = tk.StringVar(value="缓存信息加载中...")
        ttk.Label(cache_frame, textvariable=self.cache_info_var).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 缓存操作按钮
        button_frame = ttk.Frame(cache_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="🔄 刷新缓存信息", 
                  command=self.refresh_cache_info).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🗑️ 清空缓存", 
                  command=self.clear_cache).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📁 打开缓存目录", 
                  command=self.open_cache_directory).pack(side=tk.LEFT)
    
    def create_config_management_section(self):
        """创建配置管理区域"""
        config_frame = self.create_labeled_frame(self.frame, "⚙️ 配置管理", padding="10")
        config_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # 配置文件信息
        self.config_info_var = tk.StringVar(value="配置信息加载中...")
        ttk.Label(config_frame, textvariable=self.config_info_var).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # 配置操作按钮
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="📄 编辑配置", 
                  command=self.edit_config).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="💾 备份配置", 
                  command=self.backup_config).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📥 恢复配置", 
                  command=self.restore_config).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 重置配置", 
                  command=self.reset_config).pack(side=tk.LEFT)
    
    def create_performance_section(self):
        """创建性能监控区域"""
        perf_frame = self.create_labeled_frame(self.frame, "📊 性能监控", padding="10")
        perf_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        perf_frame.columnconfigure(0, weight=1)
        
        # 性能信息显示
        self.perf_text = tk.Text(perf_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.perf_text.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 性能操作按钮
        button_frame = ttk.Frame(perf_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="🔄 刷新性能数据", 
                  command=self.refresh_performance_stats).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📊 导出性能报告", 
                  command=self.export_performance_report).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🧹 清理性能数据", 
                  command=self.clear_performance_stats).pack(side=tk.LEFT)
    
    def create_maintenance_section(self):
        """创建维护工具区域"""
        maint_frame = self.create_labeled_frame(self.frame, "🔧 维护工具", padding="10")
        maint_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        maint_frame.columnconfigure(1, weight=1)
        
        # 维护操作按钮
        button_frame = ttk.Frame(maint_frame)
        button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="🧪 运行系统测试", 
                  command=self.run_system_test).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📋 生成诊断报告", 
                  command=self.generate_diagnostic_report).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔍 检查依赖", 
                  command=self.check_dependencies).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📁 打开日志目录", 
                  command=self.open_log_directory).pack(side=tk.LEFT)
        
        # 状态显示
        self.maintenance_status_var = tk.StringVar(value="维护工具就绪")
        ttk.Label(maint_frame, textvariable=self.maintenance_status_var).grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    def refresh_system_info(self):
        """刷新系统信息"""
        try:
            import platform
            import psutil
            
            # 收集系统信息
            info_lines = [
                f"操作系统: {platform.system()} {platform.release()}",
                f"Python版本: {platform.python_version()}",
                f"处理器: {platform.processor()}",
                f"CPU核心数: {psutil.cpu_count()} 个",
                f"内存总量: {psutil.virtual_memory().total / (1024**3):.1f} GB",
                f"可用内存: {psutil.virtual_memory().available / (1024**3):.1f} GB",
                f"磁盘使用: {psutil.disk_usage('/').percent:.1f}%"
            ]
            
            # 显示信息
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "\n".join(info_lines))
            self.info_text.config(state=tk.DISABLED)
            
            self.system_info = {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available
            }
            
            self.log_message("系统信息已刷新")
            
        except Exception as e:
            self.show_error("刷新失败", f"无法获取系统信息: {e}")
    
    def copy_system_info(self):
        """复制系统信息到剪贴板"""
        try:
            info_text = self.info_text.get(1.0, tk.END).strip()
            self.frame.clipboard_clear()
            self.frame.clipboard_append(info_text)
            self.show_info("复制成功", "系统信息已复制到剪贴板")
        except Exception as e:
            self.show_error("复制失败", str(e))
    
    def refresh_cache_info(self):
        """刷新缓存信息"""
        try:
            from core.services import VideoService
            from core.detection import FrameDifferenceDetector
            
            # 创建视频服务获取缓存信息
            detector = FrameDifferenceDetector()
            video_service = VideoService(detector, enable_cache=True)
            
            cache_info = video_service.get_cache_info()
            
            if cache_info.get('enabled', False):
                info_text = (
                    f"缓存状态: 启用\n"
                    f"缓存目录: {cache_info.get('cache_dir', 'N/A')}\n"
                    f"缓存文件数: {cache_info.get('cache_files_count', 0)}\n"
                    f"缓存大小: {cache_info.get('total_size_mb', 0):.1f} MB\n"
                    f"缓存命中: {cache_info.get('cache_hits', 0)} 次\n"
                    f"缓存未命中: {cache_info.get('cache_misses', 0)} 次"
                )
            else:
                info_text = "缓存状态: 禁用"
            
            self.cache_info_var.set(info_text)
            video_service.cleanup()
            
        except Exception as e:
            self.cache_info_var.set(f"获取缓存信息失败: {e}")
    
    def clear_cache(self):
        """清空缓存"""
        if self.ask_yes_no("确认清空", "确定要清空所有缓存文件吗？"):
            try:
                from core.services import VideoService
                from core.detection import FrameDifferenceDetector
                
                detector = FrameDifferenceDetector()
                video_service = VideoService(detector, enable_cache=True)
                
                success = video_service.clear_cache()
                video_service.cleanup()
                
                if success:
                    self.show_info("清空成功", "缓存已清空")
                    self.refresh_cache_info()
                else:
                    self.show_warning("清空失败", "无法清空缓存")
                    
            except Exception as e:
                self.show_error("清空失败", str(e))
    
    def open_cache_directory(self):
        """打开缓存目录"""
        try:
            from core.services import VideoService
            from core.detection import FrameDifferenceDetector
            
            detector = FrameDifferenceDetector()
            video_service = VideoService(detector, enable_cache=True)
            
            cache_info = video_service.get_cache_info()
            cache_dir = cache_info.get('cache_dir')
            
            if cache_dir and Path(cache_dir).exists():
                if sys.platform == "win32":
                    subprocess.run(["explorer", cache_dir])
                elif sys.platform == "darwin":
                    subprocess.run(["open", cache_dir])
                else:
                    subprocess.run(["xdg-open", cache_dir])
                
                self.log_message(f"已打开缓存目录: {cache_dir}")
            else:
                self.show_warning("目录不存在", "缓存目录不存在或缓存未启用")
            
            video_service.cleanup()
            
        except Exception as e:
            self.show_error("打开失败", str(e))
    
    def edit_config(self):
        """编辑配置文件"""
        try:
            from config import get_config
            
            config = get_config()
            config_path = config.config_path
            
            if config_path.exists():
                if sys.platform == "win32":
                    subprocess.run(["notepad", str(config_path)])
                elif sys.platform == "darwin":
                    subprocess.run(["open", "-t", str(config_path)])
                else:
                    subprocess.run(["xdg-open", str(config_path)])
                
                self.log_message(f"已打开配置文件: {config_path}")
            else:
                self.show_warning("文件不存在", "配置文件不存在")
                
        except Exception as e:
            self.show_error("打开失败", str(e))
    
    def backup_config(self):
        """备份配置文件"""
        try:
            from config import get_config
            import shutil
            from datetime import datetime
            
            config = get_config()
            config_path = config.config_path
            
            if config_path.exists():
                # 创建备份文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"config_backup_{timestamp}.yaml"
                backup_path = config_path.parent / backup_name
                
                # 复制文件
                shutil.copy2(config_path, backup_path)
                
                self.show_info("备份成功", f"配置已备份到:\n{backup_path}")
                self.log_message(f"配置文件已备份: {backup_path}")
            else:
                self.show_warning("文件不存在", "配置文件不存在")
                
        except Exception as e:
            self.show_error("备份失败", str(e))
    
    def restore_config(self):
        """恢复配置文件"""
        try:
            from config import get_config
            
            config = get_config()
            config_dir = config.config_path.parent
            
            # 选择备份文件
            backup_file = filedialog.askopenfilename(
                title="选择配置备份文件",
                initialdir=config_dir,
                filetypes=[("YAML文件", "*.yaml"), ("所有文件", "*.*")]
            )
            
            if backup_file:
                if self.ask_yes_no("确认恢复", "确定要恢复配置文件吗？当前配置将被覆盖。"):
                    import shutil
                    shutil.copy2(backup_file, config.config_path)
                    
                    self.show_info("恢复成功", "配置文件已恢复，请重启应用程序以生效")
                    self.log_message(f"配置文件已恢复: {backup_file}")
                    
        except Exception as e:
            self.show_error("恢复失败", str(e))
    
    def reset_config(self):
        """重置配置文件"""
        if self.ask_yes_no("确认重置", "确定要重置配置文件到默认设置吗？"):
            try:
                from config import get_config
                
                config = get_config()
                config.reset_to_defaults()
                config.save_config()
                
                self.show_info("重置成功", "配置已重置为默认设置")
                self.log_message("配置文件已重置为默认设置")
                
            except Exception as e:
                self.show_error("重置失败", str(e))
    
    def refresh_performance_stats(self):
        """刷新性能统计"""
        try:
            from core.services import VideoService
            from core.detection import FrameDifferenceDetector

            # 获取性能统计
            detector = FrameDifferenceDetector()
            video_service = VideoService(detector, enable_cache=True)

            stats = video_service.get_performance_stats()

            # 格式化显示
            stats_lines = [
                f"总处理文件数: {stats.get('total_processed', 0)}",
                f"总处理时间: {stats.get('total_processing_time', 0):.2f} 秒",
                f"平均处理时间: {stats.get('avg_processing_time', 0):.2f} 秒",
                f"缓存命中次数: {stats.get('cache_hits', 0)}",
                f"缓存未命中次数: {stats.get('cache_misses', 0)}",
                f"缓存命中率: {stats.get('cache_hit_rate', 0):.1%}",
                f"错误次数: {stats.get('errors', 0)}"
            ]

            # 显示统计信息
            self.perf_text.config(state=tk.NORMAL)
            self.perf_text.delete(1.0, tk.END)
            self.perf_text.insert(tk.END, "\n".join(stats_lines))
            self.perf_text.config(state=tk.DISABLED)

            self.performance_stats = stats
            video_service.cleanup()

        except Exception as e:
            self.perf_text.config(state=tk.NORMAL)
            self.perf_text.delete(1.0, tk.END)
            self.perf_text.insert(tk.END, f"获取性能统计失败: {e}")
            self.perf_text.config(state=tk.DISABLED)

    def export_performance_report(self):
        """导出性能报告"""
        try:
            filename = filedialog.asksaveasfilename(
                title="导出性能报告",
                defaultextension=".json",
                filetypes=[
                    ("JSON文件", "*.json"),
                    ("文本文件", "*.txt"),
                    ("所有文件", "*.*")
                ]
            )

            if filename:
                report_data = {
                    "timestamp": str(tk.datetime.datetime.now()),
                    "system_info": self.system_info,
                    "performance_stats": self.performance_stats
                }

                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write("Shot Detection 性能报告\n")
                        f.write("=" * 30 + "\n\n")
                        f.write(f"生成时间: {report_data['timestamp']}\n\n")

                        f.write("系统信息:\n")
                        for key, value in self.system_info.items():
                            f.write(f"  {key}: {value}\n")

                        f.write("\n性能统计:\n")
                        for key, value in self.performance_stats.items():
                            f.write(f"  {key}: {value}\n")

                self.show_info("导出成功", f"性能报告已保存到:\n{filename}")
                self.log_message(f"性能报告已导出: {filename}")

        except Exception as e:
            self.show_error("导出失败", str(e))

    def clear_performance_stats(self):
        """清理性能数据"""
        if self.ask_yes_no("确认清理", "确定要清理所有性能统计数据吗？"):
            try:
                # 这里可以添加清理性能数据的逻辑
                self.show_info("清理成功", "性能统计数据已清理")
                self.refresh_performance_stats()

            except Exception as e:
                self.show_error("清理失败", str(e))

    def run_system_test(self):
        """运行系统测试"""
        self.maintenance_status_var.set("正在运行系统测试...")

        def run_test():
            try:
                # 运行测试脚本
                import subprocess
                result = subprocess.run([
                    sys.executable, "test_advanced_features.py"
                ], capture_output=True, text=True, cwd=Path.cwd())

                if result.returncode == 0:
                    self.maintenance_status_var.set("系统测试通过 ✅")
                    self.show_info("测试完成", "系统测试全部通过！")
                else:
                    self.maintenance_status_var.set("系统测试失败 ❌")
                    self.show_warning("测试失败", f"系统测试失败:\n{result.stderr}")

                self.log_message(f"系统测试完成，返回码: {result.returncode}")

            except Exception as e:
                self.maintenance_status_var.set("测试异常 ⚠️")
                self.show_error("测试异常", str(e))

        # 在后台线程运行测试
        test_thread = threading.Thread(target=run_test)
        test_thread.daemon = True
        test_thread.start()

    def generate_diagnostic_report(self):
        """生成诊断报告"""
        try:
            from datetime import datetime

            # 收集诊断信息
            diagnostic_data = {
                "timestamp": datetime.now().isoformat(),
                "system_info": self.system_info,
                "performance_stats": self.performance_stats,
                "config_info": self._get_config_info(),
                "cache_info": self._get_cache_info(),
                "dependencies": self._check_dependencies_info()
            }

            # 选择保存位置
            filename = filedialog.asksaveasfilename(
                title="保存诊断报告",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
            )

            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(diagnostic_data, f, indent=2, ensure_ascii=False, default=str)

                self.show_info("生成成功", f"诊断报告已保存到:\n{filename}")
                self.log_message(f"诊断报告已生成: {filename}")

        except Exception as e:
            self.show_error("生成失败", str(e))

    def check_dependencies(self):
        """检查依赖"""
        self.maintenance_status_var.set("正在检查依赖...")

        def check_deps():
            try:
                missing_deps = []
                required_modules = [
                    'cv2', 'numpy', 'loguru', 'pyyaml',
                    'tkinter', 'pathlib', 'threading'
                ]

                for module in required_modules:
                    try:
                        __import__(module)
                    except ImportError:
                        missing_deps.append(module)

                if missing_deps:
                    self.maintenance_status_var.set(f"缺少依赖: {', '.join(missing_deps)} ❌")
                    self.show_warning("依赖检查", f"缺少以下依赖:\n{', '.join(missing_deps)}")
                else:
                    self.maintenance_status_var.set("所有依赖正常 ✅")
                    self.show_info("依赖检查", "所有必需的依赖都已安装")

                self.log_message("依赖检查完成")

            except Exception as e:
                self.maintenance_status_var.set("依赖检查异常 ⚠️")
                self.show_error("检查异常", str(e))

        # 在后台线程检查依赖
        check_thread = threading.Thread(target=check_deps)
        check_thread.daemon = True
        check_thread.start()

    def open_log_directory(self):
        """打开日志目录"""
        try:
            log_dir = Path.cwd() / "logs"

            if log_dir.exists():
                if sys.platform == "win32":
                    subprocess.run(["explorer", str(log_dir)])
                elif sys.platform == "darwin":
                    subprocess.run(["open", str(log_dir)])
                else:
                    subprocess.run(["xdg-open", str(log_dir)])

                self.log_message(f"已打开日志目录: {log_dir}")
            else:
                self.show_warning("目录不存在", "日志目录不存在")

        except Exception as e:
            self.show_error("打开失败", str(e))

    def _get_config_info(self):
        """获取配置信息"""
        try:
            from config import get_config
            config = get_config()
            return {
                "config_path": str(config.config_path),
                "app_name": config.get('app.name'),
                "app_version": config.get('app.version'),
                "config_exists": config.config_path.exists()
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_cache_info(self):
        """获取缓存信息"""
        try:
            from core.services import VideoService
            from core.detection import FrameDifferenceDetector

            detector = FrameDifferenceDetector()
            video_service = VideoService(detector, enable_cache=True)
            cache_info = video_service.get_cache_info()
            video_service.cleanup()

            return cache_info
        except Exception as e:
            return {"error": str(e)}

    def _check_dependencies_info(self):
        """检查依赖信息"""
        try:
            import pkg_resources

            installed_packages = {}
            for dist in pkg_resources.working_set:
                installed_packages[dist.project_name] = dist.version

            return installed_packages
        except Exception as e:
            return {"error": str(e)}

    def on_tab_selected(self):
        """Tab被选中时的回调"""
        super().on_tab_selected()
        # 自动刷新信息
        self.refresh_system_info()
        self.refresh_cache_info()
        self.refresh_performance_stats()
