#!/usr/bin/env python3
"""
Comprehensive Verification Script
综合验证脚本
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class ComprehensiveVerification:
    """综合验证类"""
    
    def __init__(self):
        self.total_checks = 0
        self.passed_checks = 0
        self.failed_checks = 0
        self.warnings = 0
        self.errors = []
        self.warnings_list = []
    
    def check_pass(self, message: str):
        """检查通过"""
        self.total_checks += 1
        self.passed_checks += 1
        print(f"✅ {message}")
    
    def check_fail(self, message: str, error: str = ""):
        """检查失败"""
        self.total_checks += 1
        self.failed_checks += 1
        self.errors.append(f"{message}: {error}")
        print(f"❌ {message}")
        if error:
            print(f"   错误: {error}")
    
    def check_warning(self, message: str):
        """检查警告"""
        self.warnings += 1
        self.warnings_list.append(message)
        print(f"⚠️ {message}")
    
    def verify_all(self):
        """执行所有验证"""
        print("🔍 Shot Detection v2.0 综合验证")
        print("=" * 60)
        
        start_time = time.time()
        
        # 执行各项验证
        self.verify_project_structure()
        self.verify_core_modules()
        self.verify_services()
        self.verify_gui_system()
        self.verify_configuration()
        self.verify_documentation()
        self.verify_tests()
        self.verify_deployment_readiness()
        
        end_time = time.time()
        
        # 生成报告
        self.generate_final_report(end_time - start_time)
    
    def verify_project_structure(self):
        """验证项目结构"""
        print("\n📁 验证项目结构...")
        
        # 核心目录
        core_dirs = [
            "core", "core/detection", "core/processing", 
            "core/services", "core/plugins"
        ]
        
        for dir_path in core_dirs:
            if (project_root / dir_path).exists():
                self.check_pass(f"核心目录: {dir_path}")
            else:
                self.check_fail(f"核心目录缺失: {dir_path}")
        
        # GUI目录
        gui_dirs = ["gui", "gui/components", "gui/dialogs"]
        for dir_path in gui_dirs:
            if (project_root / dir_path).exists():
                self.check_pass(f"GUI目录: {dir_path}")
            else:
                self.check_fail(f"GUI目录缺失: {dir_path}")
        
        # 其他重要目录
        other_dirs = ["config", "jianying", "tests", "examples"]
        for dir_path in other_dirs:
            if (project_root / dir_path).exists():
                self.check_pass(f"目录: {dir_path}")
            else:
                self.check_warning(f"目录缺失: {dir_path}")
    
    def verify_core_modules(self):
        """验证核心模块"""
        print("\n🔍 验证核心模块...")
        
        try:
            # 检测模块
            from core.detection import FrameDifferenceDetector, HistogramDetector, MultiDetector
            self.check_pass("检测模块导入成功")
            
            # 创建检测器实例
            fd_detector = FrameDifferenceDetector(threshold=0.3)
            hist_detector = HistogramDetector(threshold=0.5)
            multi_detector = MultiDetector([fd_detector, hist_detector])
            
            self.check_pass("检测器实例创建成功")
            
            # 测试初始化
            if fd_detector.initialize():
                self.check_pass("检测器初始化成功")
            else:
                self.check_fail("检测器初始化失败")
            
            # 清理
            fd_detector.cleanup()
            hist_detector.cleanup()
            multi_detector.cleanup()
            
        except Exception as e:
            self.check_fail("核心检测模块验证失败", str(e))
        
        try:
            # 处理模块
            from core.processing import VideoProcessor, ProcessingConfig
            self.check_pass("处理模块导入成功")
            
        except Exception as e:
            self.check_fail("处理模块验证失败", str(e))
    
    def verify_services(self):
        """验证服务层"""
        print("\n🎬 验证服务层...")
        
        try:
            from core.services import VideoService, BatchService, WorkflowService, AdvancedAnalysisService
            from core.detection import FrameDifferenceDetector
            
            self.check_pass("服务模块导入成功")
            
            # 创建服务实例
            detector = FrameDifferenceDetector()
            
            video_service = VideoService(detector, enable_cache=True)
            self.check_pass("视频服务创建成功")
            
            batch_service = BatchService(detector, max_workers=2)
            self.check_pass("批量服务创建成功")
            
            analysis_service = AdvancedAnalysisService()
            self.check_pass("分析服务创建成功")
            
            # 测试服务功能
            stats = video_service.get_performance_stats()
            if isinstance(stats, dict):
                self.check_pass("性能统计功能正常")
            else:
                self.check_fail("性能统计功能异常")
            
            cache_info = video_service.get_cache_info()
            if isinstance(cache_info, dict):
                self.check_pass("缓存信息功能正常")
            else:
                self.check_fail("缓存信息功能异常")
            
            # 清理
            video_service.cleanup()
            batch_service.stop_processing()
            
        except Exception as e:
            self.check_fail("服务层验证失败", str(e))
    
    def verify_gui_system(self):
        """验证GUI系统"""
        print("\n🖥️ 验证GUI系统...")
        
        try:
            # 检查tkinter可用性
            import tkinter as tk
            self.check_pass("Tkinter可用")
            
            # 导入GUI组件
            from gui.components import BaseTab, VideoTab, BatchTab, AnalysisTab, ToolsTab
            self.check_pass("GUI组件导入成功")
            
            from gui.main_window import MainWindow
            self.check_pass("主窗口导入成功")
            
            from gui.dialogs import SettingsDialog
            self.check_pass("对话框导入成功")
            
        except ImportError as e:
            self.check_fail("GUI系统导入失败", str(e))
        except Exception as e:
            self.check_warning(f"GUI系统验证异常: {e}")
    
    def verify_configuration(self):
        """验证配置系统"""
        print("\n⚙️ 验证配置系统...")
        
        try:
            from config import get_config, ConfigManager
            
            config = get_config()
            self.check_pass("配置管理器创建成功")
            
            # 测试配置获取
            app_name = config.get('app.name')
            if app_name:
                self.check_pass(f"应用配置正常: {app_name}")
            else:
                self.check_warning("应用名称配置为空")
            
            # 测试各种配置
            detection_config = config.get_detection_config()
            processing_config = config.get_processing_config()
            gui_config = config.get_gui_config()
            
            if isinstance(detection_config, dict):
                self.check_pass("检测配置正常")
            else:
                self.check_fail("检测配置异常")
            
            # 测试配置验证
            is_valid, errors = config.validate_config()
            if is_valid:
                self.check_pass("配置验证通过")
            else:
                self.check_fail("配置验证失败", "; ".join(errors))
            
        except Exception as e:
            self.check_fail("配置系统验证失败", str(e))
    
    def verify_documentation(self):
        """验证文档"""
        print("\n📖 验证文档...")
        
        doc_files = [
            ("USER_MANUAL.md", "用户手册"),
            ("API_REFERENCE.md", "API参考"),
            ("FINAL_REPORT.md", "最终报告"),
            ("REFACTOR_COMPLETE.md", "重构报告"),
            ("FUNCTIONALITY_CHECK_REPORT.md", "功能检查报告")
        ]
        
        for doc_file, description in doc_files:
            path = project_root / doc_file
            if path.exists():
                size_kb = path.stat().st_size / 1024
                if size_kb > 1:
                    self.check_pass(f"{description}: {size_kb:.1f}KB")
                else:
                    self.check_warning(f"{description}文件过小: {size_kb:.1f}KB")
            else:
                self.check_fail(f"{description}缺失")
    
    def verify_tests(self):
        """验证测试系统"""
        print("\n🧪 验证测试系统...")
        
        # 检查测试文件
        test_files = [
            "tests/test_core/test_detection.py",
            "tests/test_core/test_services.py", 
            "tests/test_config.py",
            "run_tests.py"
        ]
        
        for test_file in test_files:
            if (project_root / test_file).exists():
                self.check_pass(f"测试文件: {test_file}")
            else:
                self.check_warning(f"测试文件缺失: {test_file}")
        
        # 尝试运行快速测试
        try:
            result = subprocess.run([
                sys.executable, "test_refactor.py"
            ], capture_output=True, text=True, timeout=30, cwd=project_root)
            
            if result.returncode == 0:
                self.check_pass("基础测试通过")
            else:
                self.check_warning("基础测试失败")
        except Exception as e:
            self.check_warning(f"无法运行测试: {e}")
    
    def verify_deployment_readiness(self):
        """验证部署就绪状态"""
        print("\n🚀 验证部署就绪状态...")
        
        # 检查依赖
        required_deps = ["cv2", "numpy", "loguru", "yaml"]
        for dep in required_deps:
            try:
                __import__(dep)
                self.check_pass(f"依赖可用: {dep}")
            except ImportError:
                self.check_fail(f"依赖缺失: {dep}")
        
        # 检查主程序
        main_files = ["main_v2.py", "main.py"]
        for main_file in main_files:
            if (project_root / main_file).exists():
                self.check_pass(f"主程序: {main_file}")
            else:
                self.check_warning(f"主程序缺失: {main_file}")
        
        # 检查配置文件
        config_files = ["config_v2.yaml"]
        for config_file in config_files:
            if (project_root / config_file).exists():
                self.check_pass(f"配置文件: {config_file}")
            else:
                self.check_fail(f"配置文件缺失: {config_file}")
    
    def generate_final_report(self, duration: float):
        """生成最终报告"""
        print("\n" + "=" * 60)
        print("📊 综合验证报告")
        print("=" * 60)
        
        success_rate = self.passed_checks / self.total_checks if self.total_checks > 0 else 0
        
        print(f"⏱️ 验证时间: {duration:.2f} 秒")
        print(f"📋 总检查项: {self.total_checks}")
        print(f"✅ 通过检查: {self.passed_checks}")
        print(f"❌ 失败检查: {self.failed_checks}")
        print(f"⚠️ 警告数量: {self.warnings}")
        print(f"🎯 成功率: {success_rate:.1%}")
        
        # 评估状态
        if success_rate >= 0.95:
            status = "🎉 优秀 - 系统完全就绪"
            deployment_ready = True
        elif success_rate >= 0.85:
            status = "👍 良好 - 系统基本就绪"
            deployment_ready = True
        elif success_rate >= 0.70:
            status = "⚠️ 一般 - 需要修复部分问题"
            deployment_ready = False
        else:
            status = "❌ 较差 - 需要大量修复"
            deployment_ready = False
        
        print(f"📈 系统状态: {status}")
        print(f"🚀 部署就绪: {'是' if deployment_ready else '否'}")
        
        # 显示关键问题
        if self.errors:
            print(f"\n❌ 关键问题 ({len(self.errors)}):")
            for i, error in enumerate(self.errors[:5], 1):
                print(f"   {i}. {error}")
            if len(self.errors) > 5:
                print(f"   ... 还有 {len(self.errors) - 5} 个问题")
        
        if self.warnings_list:
            print(f"\n⚠️ 警告信息 ({len(self.warnings_list)}):")
            for i, warning in enumerate(self.warnings_list[:3], 1):
                print(f"   {i}. {warning}")
            if len(self.warnings_list) > 3:
                print(f"   ... 还有 {len(self.warnings_list) - 3} 个警告")
        
        # 生成建议
        print(f"\n💡 改进建议:")
        if success_rate < 0.85:
            print("   1. 优先修复失败的检查项")
            print("   2. 确保所有核心模块正常工作")
            print("   3. 完善缺失的文档和测试")
        else:
            print("   1. 处理剩余的警告信息")
            print("   2. 完善可选功能和文档")
            print("   3. 准备用户培训材料")
        
        print(f"\n🎊 Shot Detection v2.0 综合验证完成！")
        
        return deployment_ready


def main():
    """主函数"""
    verification = ComprehensiveVerification()
    deployment_ready = verification.verify_all()
    
    return 0 if deployment_ready else 1


if __name__ == "__main__":
    sys.exit(main())
