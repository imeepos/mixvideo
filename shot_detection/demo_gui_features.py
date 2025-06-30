#!/usr/bin/env python3
"""
GUI功能演示脚本
在无GUI环境中演示GUI的核心功能
"""

import sys
import os
from pathlib import Path
import time

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from gui_logger import ProgressMonitor, ProcessingStatus, ResultsAnalyzer
from utils.video_utils import validate_video_file, get_basic_video_info, format_duration, format_file_size


class MockGUIDemo:
    """模拟GUI演示类"""
    
    def __init__(self):
        self.processing_status = ProcessingStatus()
        self.progress_monitor = None
        self.log_messages = []
    
    def log_message(self, message, level="INFO"):
        """模拟日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.log_messages.append(log_entry)
        print(log_entry)
    
    def update_progress(self, progress, description):
        """模拟进度更新"""
        bar_length = 30
        filled_length = int(bar_length * progress // 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"\r进度: |{bar}| {progress:.1f}% - {description}", end='', flush=True)
        if progress >= 100:
            print()  # 换行
    
    def demo_file_validation(self, video_path):
        """演示文件验证功能"""
        print("\n" + "="*50)
        print("📁 文件验证演示")
        print("="*50)
        
        self.log_message("开始文件验证", "INFO")
        
        if not os.path.exists(video_path):
            self.log_message(f"文件不存在: {video_path}", "ERROR")
            return False
        
        if not validate_video_file(video_path):
            self.log_message("无效的视频文件格式", "ERROR")
            return False
        
        self.log_message("文件验证通过", "SUCCESS")
        return True
    
    def demo_video_info(self, video_path):
        """演示视频信息获取"""
        print("\n" + "="*50)
        print("📹 视频信息演示")
        print("="*50)
        
        try:
            info = get_basic_video_info(video_path)
            
            print(f"文件名: {Path(video_path).name}")
            print(f"时长: {format_duration(info['duration'])}")
            print(f"分辨率: {info['width']}x{info['height']}")
            print(f"帧率: {info['fps']:.1f} FPS")
            print(f"文件大小: {format_file_size(info['file_size'])}")
            
            self.log_message("视频信息获取成功", "SUCCESS")
            return info
            
        except Exception as e:
            self.log_message(f"获取视频信息失败: {e}", "ERROR")
            return None
    
    def demo_progress_monitoring(self):
        """演示进度监控功能"""
        print("\n" + "="*50)
        print("📊 进度监控演示")
        print("="*50)
        
        # 创建进度监控器
        self.progress_monitor = ProgressMonitor(self.update_progress)
        
        # 设置处理步骤
        steps = [
            "验证输入文件",
            "初始化检测器", 
            "执行镜头检测",
            "生成分段信息",
            "切分视频文件",
            "生成项目文件",
            "生成分析报告"
        ]
        
        self.progress_monitor.set_steps(steps)
        
        # 模拟处理过程
        for i, step in enumerate(steps):
            self.progress_monitor.next_step(step)
            time.sleep(0.5)  # 模拟处理时间
        
        self.progress_monitor.complete()
        self.log_message("进度监控演示完成", "SUCCESS")
    
    def demo_processing_status(self):
        """演示处理状态管理"""
        print("\n" + "="*50)
        print("⚙️ 处理状态演示")
        print("="*50)
        
        # 开始处理
        self.processing_status.start("视频分析")
        print(f"状态: {self.processing_status.get_status_text()}")
        
        time.sleep(1)
        
        # 更新阶段
        self.processing_status.update_phase("镜头检测")
        print(f"状态: {self.processing_status.get_status_text()}")
        
        time.sleep(1)
        
        # 完成处理
        mock_results = {
            'segment_count': 15,
            'total_size': 50 * 1024 * 1024,  # 50MB
            'categories': {
                'short': {'count': 10, 'size': 20 * 1024 * 1024},
                'medium': {'count': 5, 'size': 30 * 1024 * 1024}
            }
        }
        
        self.processing_status.complete(mock_results)
        print(f"状态: {self.processing_status.get_status_text()}")
        
        self.log_message("处理状态演示完成", "SUCCESS")
    
    def demo_results_analysis(self, output_dir):
        """演示结果分析功能"""
        print("\n" + "="*50)
        print("📋 结果分析演示")
        print("="*50)
        
        if not os.path.exists(output_dir):
            self.log_message(f"输出目录不存在: {output_dir}", "WARNING")
            return
        
        # 分析输出目录
        results = ResultsAnalyzer.analyze_output_directory(output_dir)
        
        if results:
            # 显示分析结果
            summary = ResultsAnalyzer.format_results_summary(results)
            print(summary)
            
            # 详细信息
            if results['video_segments']:
                print(f"\n视频分段详情:")
                for segment in results['video_segments'][:5]:  # 只显示前5个
                    print(f"  • {segment['name']} ({format_file_size(segment['size'])})")
                
                if len(results['video_segments']) > 5:
                    print(f"  ... 还有 {len(results['video_segments']) - 5} 个分段")
            
            if results['report_files']:
                print(f"\n分析报告:")
                for report in results['report_files']:
                    print(f"  • {report['name']} ({format_file_size(report['size'])})")
            
            self.log_message("结果分析完成", "SUCCESS")
        else:
            self.log_message("未找到分析结果", "WARNING")
    
    def demo_complete_workflow(self, video_path, output_dir):
        """演示完整工作流程"""
        print("\n" + "🎬" + "="*48 + "🎬")
        print("完整工作流程演示")
        print("🎬" + "="*48 + "🎬")
        
        # 1. 文件验证
        if not self.demo_file_validation(video_path):
            return False
        
        # 2. 视频信息
        video_info = self.demo_video_info(video_path)
        if not video_info:
            return False
        
        # 3. 进度监控
        self.demo_progress_monitoring()
        
        # 4. 处理状态
        self.demo_processing_status()
        
        # 5. 结果分析
        self.demo_results_analysis(output_dir)
        
        print("\n" + "🎉" + "="*48 + "🎉")
        print("GUI功能演示完成！")
        print("🎉" + "="*48 + "🎉")
        
        return True
    
    def show_gui_features_summary(self):
        """显示GUI功能总结"""
        print("\n" + "📋" + "="*48 + "📋")
        print("GUI功能特性总结")
        print("📋" + "="*48 + "📋")
        
        features = [
            "🎯 直观的文件选择界面",
            "⚙️ 灵活的处理参数设置",
            "📹 实时视频信息显示",
            "📊 详细的进度监控",
            "📝 实时日志输出",
            "📋 完整的结果统计",
            "🌐 一键打开分析报告",
            "📁 便捷的文件管理",
            "🎨 美观的用户界面",
            "⚡ 响应式操作体验"
        ]
        
        print("主要功能特性:")
        for feature in features:
            print(f"  {feature}")
        
        print(f"\n操作流程:")
        print("  1. 选择视频文件")
        print("  2. 设置输出目录")
        print("  3. 配置处理参数")
        print("  4. 开始处理")
        print("  5. 查看实时进度")
        print("  6. 查看处理结果")
        print("  7. 打开分析报告")
        
        print(f"\n日志记录: {len(self.log_messages)} 条消息")


def main():
    """主演示函数"""
    print("🎬 智能镜头检测与分段系统 - GUI功能演示")
    print("=" * 60)
    
    # 创建演示实例
    demo = MockGUIDemo()
    
    # 检查测试文件
    video_path = "test_video.mp4"
    output_dir = "timeline_test_output"
    
    if os.path.exists(video_path):
        # 运行完整演示
        demo.demo_complete_workflow(video_path, output_dir)
    else:
        print(f"⚠️ 测试视频文件不存在: {video_path}")
        print("运行部分功能演示...")
        
        # 运行部分演示
        demo.demo_progress_monitoring()
        demo.demo_processing_status()
        
        if os.path.exists(output_dir):
            demo.demo_results_analysis(output_dir)
    
    # 显示功能总结
    demo.show_gui_features_summary()


if __name__ == "__main__":
    main()
