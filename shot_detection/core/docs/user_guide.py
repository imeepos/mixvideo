"""
User Guide Generator
用户指南生成器
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class GuideConfig:
    """用户指南配置"""
    
    def __init__(self):
        """初始化用户指南配置"""
        self.output_format = "markdown"  # markdown, html, pdf
        self.include_screenshots = True
        self.include_code_examples = True
        self.include_troubleshooting = True
        self.language = "en"
        self.difficulty_levels = ["beginner", "intermediate", "advanced"]
        self.generate_toc = True
        self.include_glossary = True


class UserGuideGenerator:
    """用户指南生成器"""
    
    def __init__(self, config: Optional[GuideConfig] = None):
        """
        初始化用户指南生成器
        
        Args:
            config: 用户指南配置
        """
        self.config = config or GuideConfig()
        self.logger = logger.bind(component="UserGuideGenerator")
        
        # 指南内容
        self.guide_sections = {}
        self.examples = {}
        self.troubleshooting = {}
        self.glossary = {}
        
        self.logger.info("User guide generator initialized")
    
    def generate_user_guide(self, output_dir: Path) -> bool:
        """
        生成用户指南
        
        Args:
            output_dir: 输出目录
            
        Returns:
            是否生成成功
        """
        try:
            self.logger.info("Generating user guide")
            
            # 创建输出目录
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 准备指南内容
            self._prepare_guide_content()
            
            # 生成各个部分
            self._generate_installation_guide(output_dir)
            self._generate_quickstart_guide(output_dir)
            self._generate_tutorial_guide(output_dir)
            self._generate_configuration_guide(output_dir)
            self._generate_advanced_guide(output_dir)
            
            if self.config.include_troubleshooting:
                self._generate_troubleshooting_guide(output_dir)
            
            if self.config.include_glossary:
                self._generate_glossary(output_dir)
            
            # 生成主索引
            self._generate_guide_index(output_dir)
            
            self.logger.info("User guide generation completed")
            return True
            
        except Exception as e:
            self.logger.error(f"User guide generation failed: {e}")
            return False
    
    def _prepare_guide_content(self):
        """准备指南内容"""
        try:
            # 安装指南内容
            self.guide_sections['installation'] = {
                'title': 'Installation Guide',
                'sections': [
                    'System Requirements',
                    'Installation Methods',
                    'Verification',
                    'Common Issues'
                ]
            }
            
            # 快速开始内容
            self.guide_sections['quickstart'] = {
                'title': 'Quick Start Guide',
                'sections': [
                    'Basic Usage',
                    'First Detection',
                    'Viewing Results',
                    'Next Steps'
                ]
            }
            
            # 教程内容
            self.guide_sections['tutorial'] = {
                'title': 'Tutorial',
                'sections': [
                    'Understanding Shot Detection',
                    'Working with Videos',
                    'Configuring Detection',
                    'Exporting Results',
                    'Batch Processing'
                ]
            }
            
            # 配置指南内容
            self.guide_sections['configuration'] = {
                'title': 'Configuration Guide',
                'sections': [
                    'Configuration Files',
                    'Detection Parameters',
                    'Algorithm Selection',
                    'Performance Tuning',
                    'User Preferences'
                ]
            }
            
            # 高级指南内容
            self.guide_sections['advanced'] = {
                'title': 'Advanced Guide',
                'sections': [
                    'Custom Algorithms',
                    'Plugin Development',
                    'API Integration',
                    'Performance Optimization',
                    'Troubleshooting'
                ]
            }
            
            # 准备示例
            self._prepare_examples()
            
            # 准备故障排除
            self._prepare_troubleshooting()
            
            # 准备术语表
            self._prepare_glossary()
            
        except Exception as e:
            self.logger.error(f"Failed to prepare guide content: {e}")
    
    def _prepare_examples(self):
        """准备代码示例"""
        self.examples = {
            'basic_detection': {
                'title': 'Basic Shot Detection',
                'description': 'Simple example of detecting shots in a video',
                'code': '''from shot_detection import ShotDetector

# Create detector
detector = ShotDetector()

# Detect shots
results = detector.detect_shots('video.mp4')

# Print results
for boundary in results['boundaries']:
    print(f"Shot at {boundary['timestamp']:.2f}s")'''
            },
            'custom_parameters': {
                'title': 'Custom Detection Parameters',
                'description': 'Configuring detection parameters for better results',
                'code': '''from shot_detection import ShotDetector

# Create detector
detector = ShotDetector()

# Configure parameters
detector.set_parameter('threshold', 0.3)
detector.set_parameter('min_shot_duration', 2.0)
detector.set_algorithm('histogram')

# Detect shots
results = detector.detect_shots('video.mp4')'''
            },
            'batch_processing': {
                'title': 'Batch Processing',
                'description': 'Processing multiple videos at once',
                'code': '''import os
from shot_detection import ShotDetector

detector = ShotDetector()

for filename in os.listdir('videos/'):
    if filename.endswith('.mp4'):
        print(f"Processing {filename}...")
        results = detector.detect_shots(f'videos/{filename}')
        print(f"Found {len(results['boundaries'])} shots")'''
            },
            'export_results': {
                'title': 'Exporting Results',
                'description': 'Saving detection results to different formats',
                'code': '''from shot_detection import ShotDetector, JSONExporter, CSVExporter

detector = ShotDetector()
results = detector.detect_shots('video.mp4')

# Export to JSON
json_exporter = JSONExporter()
json_exporter.export(results, 'results.json')

# Export to CSV
csv_exporter = CSVExporter()
csv_exporter.export(results, 'results.csv')'''
            }
        }
    
    def _prepare_troubleshooting(self):
        """准备故障排除内容"""
        self.troubleshooting = {
            'installation_issues': {
                'title': 'Installation Issues',
                'problems': [
                    {
                        'problem': 'ImportError: No module named cv2',
                        'solution': 'Install OpenCV: pip install opencv-python',
                        'details': 'OpenCV is required for video processing. Make sure to install the correct version for your Python environment.'
                    },
                    {
                        'problem': 'Permission denied when installing',
                        'solution': 'Use --user flag: pip install --user shot-detection',
                        'details': 'This installs the package in your user directory instead of system-wide.'
                    }
                ]
            },
            'detection_issues': {
                'title': 'Detection Issues',
                'problems': [
                    {
                        'problem': 'No shots detected in video',
                        'solution': 'Lower the threshold parameter or try a different algorithm',
                        'details': 'Some videos may require different sensitivity settings. Try threshold values between 0.1 and 0.5.'
                    },
                    {
                        'problem': 'Too many false positives',
                        'solution': 'Increase the threshold or minimum shot duration',
                        'details': 'Higher threshold values make detection less sensitive. Increase min_shot_duration to filter out very short segments.'
                    }
                ]
            },
            'performance_issues': {
                'title': 'Performance Issues',
                'problems': [
                    {
                        'problem': 'Detection is very slow',
                        'solution': 'Reduce video resolution or use frame_difference algorithm',
                        'details': 'Large videos take more time to process. Consider preprocessing videos to lower resolution.'
                    },
                    {
                        'problem': 'High memory usage',
                        'solution': 'Process videos in chunks or reduce chunk_size parameter',
                        'details': 'Large videos can consume significant memory. Adjust processing parameters based on available RAM.'
                    }
                ]
            }
        }
    
    def _prepare_glossary(self):
        """准备术语表"""
        self.glossary = {
            'shot': 'A continuous sequence of frames recorded from a single camera position',
            'shot_boundary': 'The transition point between two different shots',
            'cut': 'An instantaneous transition between shots',
            'fade': 'A gradual transition where the image gradually becomes black or white',
            'dissolve': 'A gradual transition where one shot blends into another',
            'threshold': 'A parameter that controls the sensitivity of shot detection',
            'frame_difference': 'An algorithm that detects shots by comparing consecutive frames',
            'histogram': 'An algorithm that uses color distribution to detect shot changes',
            'optical_flow': 'An algorithm that analyzes motion between frames',
            'false_positive': 'A detected shot boundary that is not actually a shot change',
            'false_negative': 'A missed shot boundary that should have been detected'
        }
    
    def _generate_installation_guide(self, output_dir: Path):
        """生成安装指南"""
        try:
            content = []
            
            content.append("# Installation Guide")
            content.append("")
            content.append("This guide will help you install Shot Detection on your system.")
            content.append("")
            
            # 系统要求
            content.append("## System Requirements")
            content.append("")
            content.append("- Python 3.8 or higher")
            content.append("- OpenCV 4.0 or higher")
            content.append("- NumPy 1.19 or higher")
            content.append("- At least 4GB of RAM (8GB recommended)")
            content.append("- 1GB of free disk space")
            content.append("")
            
            # 安装方法
            content.append("## Installation Methods")
            content.append("")
            content.append("### Using pip (Recommended)")
            content.append("")
            content.append("```bash")
            content.append("pip install shot-detection")
            content.append("```")
            content.append("")
            content.append("### Using conda")
            content.append("")
            content.append("```bash")
            content.append("conda install -c conda-forge shot-detection")
            content.append("```")
            content.append("")
            content.append("### From source")
            content.append("")
            content.append("```bash")
            content.append("git clone https://github.com/shot-detection/shot-detection.git")
            content.append("cd shot-detection")
            content.append("pip install -e .")
            content.append("```")
            content.append("")
            
            # 验证安装
            content.append("## Verification")
            content.append("")
            content.append("To verify that Shot Detection is installed correctly:")
            content.append("")
            content.append("```python")
            content.append("import shot_detection")
            content.append("print(shot_detection.__version__)")
            content.append("```")
            content.append("")
            content.append("You should see the version number printed without any errors.")
            content.append("")
            
            # 常见问题
            content.append("## Common Installation Issues")
            content.append("")
            for category, issues in self.troubleshooting.items():
                if 'installation' in category:
                    for problem in issues['problems']:
                        content.append(f"### {problem['problem']}")
                        content.append("")
                        content.append(f"**Solution:** {problem['solution']}")
                        content.append("")
                        content.append(problem['details'])
                        content.append("")
            
            # 保存文件
            output_file = output_dir / "installation.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            self.logger.debug("Installation guide generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate installation guide: {e}")
    
    def _generate_quickstart_guide(self, output_dir: Path):
        """生成快速开始指南"""
        try:
            content = []
            
            content.append("# Quick Start Guide")
            content.append("")
            content.append("Get started with Shot Detection in just a few minutes!")
            content.append("")
            
            # 基本使用
            content.append("## Basic Usage")
            content.append("")
            content.append("Here's how to detect shots in a video:")
            content.append("")
            content.append("```python")
            content.append(self.examples['basic_detection']['code'])
            content.append("```")
            content.append("")
            
            # 第一次检测
            content.append("## Your First Detection")
            content.append("")
            content.append("1. **Prepare a video file**: Make sure you have a video file (MP4, AVI, MOV, etc.)")
            content.append("2. **Run the detection**: Use the code example above")
            content.append("3. **Check the results**: The output will show detected shot boundaries")
            content.append("")
            
            # 查看结果
            content.append("## Understanding Results")
            content.append("")
            content.append("The detection results include:")
            content.append("")
            content.append("- **frame_number**: The frame where the shot boundary occurs")
            content.append("- **timestamp**: The time in seconds where the boundary occurs")
            content.append("- **confidence**: How confident the algorithm is about this boundary")
            content.append("")
            
            # 下一步
            content.append("## Next Steps")
            content.append("")
            content.append("- [Learn about configuration](configuration.md)")
            content.append("- [Try different algorithms](tutorial.md#algorithms)")
            content.append("- [Export your results](tutorial.md#exporting)")
            content.append("- [Process multiple videos](tutorial.md#batch-processing)")
            content.append("")
            
            # 保存文件
            output_file = output_dir / "quickstart.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            self.logger.debug("Quickstart guide generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate quickstart guide: {e}")
    
    def _generate_tutorial_guide(self, output_dir: Path):
        """生成教程指南"""
        try:
            content = []
            
            content.append("# Tutorial")
            content.append("")
            content.append("This comprehensive tutorial covers all aspects of using Shot Detection.")
            content.append("")
            
            # 理解镜头检测
            content.append("## Understanding Shot Detection")
            content.append("")
            content.append("Shot detection is the process of automatically identifying boundaries between different shots in a video. ")
            content.append("A shot is a continuous sequence of frames recorded from a single camera position.")
            content.append("")
            content.append("### Types of Shot Boundaries")
            content.append("")
            content.append("- **Cut**: An instantaneous transition between shots")
            content.append("- **Fade**: A gradual transition through black or white")
            content.append("- **Dissolve**: A gradual blend between two shots")
            content.append("")
            
            # 处理视频
            content.append("## Working with Videos")
            content.append("")
            content.append("### Supported Formats")
            content.append("")
            content.append("Shot Detection supports most common video formats:")
            content.append("")
            content.append("- MP4 (recommended)")
            content.append("- AVI")
            content.append("- MOV")
            content.append("- MKV")
            content.append("- WMV")
            content.append("")
            
            # 配置检测
            content.append("## Configuring Detection")
            content.append("")
            content.append("### Parameters")
            content.append("")
            content.append("```python")
            content.append(self.examples['custom_parameters']['code'])
            content.append("```")
            content.append("")
            
            # 导出结果
            content.append("## Exporting Results")
            content.append("")
            content.append("```python")
            content.append(self.examples['export_results']['code'])
            content.append("```")
            content.append("")
            
            # 批处理
            content.append("## Batch Processing")
            content.append("")
            content.append("```python")
            content.append(self.examples['batch_processing']['code'])
            content.append("```")
            content.append("")
            
            # 保存文件
            output_file = output_dir / "tutorial.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            self.logger.debug("Tutorial guide generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate tutorial guide: {e}")
    
    def _generate_configuration_guide(self, output_dir: Path):
        """生成配置指南"""
        try:
            content = []
            
            content.append("# Configuration Guide")
            content.append("")
            content.append("Learn how to configure Shot Detection for optimal results.")
            content.append("")
            
            # 配置文件
            content.append("## Configuration Files")
            content.append("")
            content.append("Shot Detection uses YAML configuration files:")
            content.append("")
            content.append("```yaml")
            content.append("detection:")
            content.append("  algorithm: frame_difference")
            content.append("  threshold: 0.5")
            content.append("  min_shot_duration: 1.0")
            content.append("")
            content.append("processing:")
            content.append("  max_workers: 4")
            content.append("  chunk_size: 1000")
            content.append("```")
            content.append("")
            
            # 检测参数
            content.append("## Detection Parameters")
            content.append("")
            content.append("### Threshold")
            content.append("Controls the sensitivity of shot detection.")
            content.append("- **Range**: 0.0 - 1.0")
            content.append("- **Default**: 0.5")
            content.append("- **Lower values**: More sensitive, may detect more boundaries")
            content.append("- **Higher values**: Less sensitive, may miss some boundaries")
            content.append("")
            
            content.append("### Minimum Shot Duration")
            content.append("Filters out very short shots.")
            content.append("- **Range**: 0.1 - 10.0 seconds")
            content.append("- **Default**: 1.0 seconds")
            content.append("- **Use case**: Prevents detection of brief camera movements")
            content.append("")
            
            # 算法选择
            content.append("## Algorithm Selection")
            content.append("")
            content.append("### Frame Difference")
            content.append("- **Speed**: Fast")
            content.append("- **Accuracy**: Good")
            content.append("- **Best for**: General purpose, real-time processing")
            content.append("")
            
            content.append("### Histogram")
            content.append("- **Speed**: Medium")
            content.append("- **Accuracy**: Better")
            content.append("- **Best for**: Videos with significant color changes")
            content.append("")
            
            content.append("### Optical Flow")
            content.append("- **Speed**: Slow")
            content.append("- **Accuracy**: Best")
            content.append("- **Best for**: Complex scenes with camera movement")
            content.append("")
            
            # 保存文件
            output_file = output_dir / "configuration.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            self.logger.debug("Configuration guide generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate configuration guide: {e}")
    
    def _generate_advanced_guide(self, output_dir: Path):
        """生成高级指南"""
        try:
            content = []
            
            content.append("# Advanced Guide")
            content.append("")
            content.append("Advanced topics for power users and developers.")
            content.append("")
            
            # 自定义算法
            content.append("## Custom Algorithms")
            content.append("")
            content.append("You can implement custom shot detection algorithms:")
            content.append("")
            content.append("```python")
            content.append("from shot_detection import BaseDetector")
            content.append("")
            content.append("class CustomDetector(BaseDetector):")
            content.append("    def detect_boundaries(self, frames):")
            content.append("        # Your custom logic here")
            content.append("        boundaries = []")
            content.append("        return boundaries")
            content.append("```")
            content.append("")
            
            # 插件开发
            content.append("## Plugin Development")
            content.append("")
            content.append("Extend Shot Detection with plugins:")
            content.append("")
            content.append("```python")
            content.append("from shot_detection.plugins import BasePlugin")
            content.append("")
            content.append("class MyPlugin(BasePlugin):")
            content.append("    def process_results(self, results):")
            content.append("        # Process detection results")
            content.append("        return modified_results")
            content.append("```")
            content.append("")
            
            # API集成
            content.append("## API Integration")
            content.append("")
            content.append("Use Shot Detection in web applications:")
            content.append("")
            content.append("```python")
            content.append("from flask import Flask, request, jsonify")
            content.append("from shot_detection import ShotDetector")
            content.append("")
            content.append("app = Flask(__name__)")
            content.append("detector = ShotDetector()")
            content.append("")
            content.append("@app.route('/detect', methods=['POST'])")
            content.append("def detect_shots():")
            content.append("    video_file = request.files['video']")
            content.append("    results = detector.detect_shots(video_file)")
            content.append("    return jsonify(results)")
            content.append("```")
            content.append("")
            
            # 保存文件
            output_file = output_dir / "advanced.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            self.logger.debug("Advanced guide generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate advanced guide: {e}")
    
    def _generate_troubleshooting_guide(self, output_dir: Path):
        """生成故障排除指南"""
        try:
            content = []
            
            content.append("# Troubleshooting Guide")
            content.append("")
            content.append("Solutions to common problems and issues.")
            content.append("")
            
            for category, issues in self.troubleshooting.items():
                content.append(f"## {issues['title']}")
                content.append("")
                
                for problem in issues['problems']:
                    content.append(f"### {problem['problem']}")
                    content.append("")
                    content.append(f"**Solution:** {problem['solution']}")
                    content.append("")
                    content.append(problem['details'])
                    content.append("")
            
            # 保存文件
            output_file = output_dir / "troubleshooting.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            self.logger.debug("Troubleshooting guide generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate troubleshooting guide: {e}")
    
    def _generate_glossary(self, output_dir: Path):
        """生成术语表"""
        try:
            content = []
            
            content.append("# Glossary")
            content.append("")
            content.append("Definitions of terms used in Shot Detection.")
            content.append("")
            
            for term, definition in sorted(self.glossary.items()):
                content.append(f"## {term.title()}")
                content.append("")
                content.append(definition)
                content.append("")
            
            # 保存文件
            output_file = output_dir / "glossary.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            self.logger.debug("Glossary generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate glossary: {e}")
    
    def _generate_guide_index(self, output_dir: Path):
        """生成指南索引"""
        try:
            content = []
            
            content.append("# User Guide")
            content.append("")
            content.append("Complete documentation for Shot Detection users.")
            content.append("")
            
            content.append("## Getting Started")
            content.append("")
            content.append("- [Installation Guide](installation.md)")
            content.append("- [Quick Start Guide](quickstart.md)")
            content.append("")
            
            content.append("## Learning")
            content.append("")
            content.append("- [Tutorial](tutorial.md)")
            content.append("- [Configuration Guide](configuration.md)")
            content.append("")
            
            content.append("## Advanced Topics")
            content.append("")
            content.append("- [Advanced Guide](advanced.md)")
            content.append("")
            
            content.append("## Reference")
            content.append("")
            if self.config.include_troubleshooting:
                content.append("- [Troubleshooting Guide](troubleshooting.md)")
            if self.config.include_glossary:
                content.append("- [Glossary](glossary.md)")
            content.append("")
            
            # 保存文件
            index_file = output_dir / "index.md"
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            self.logger.debug("Guide index generated")
            
        except Exception as e:
            self.logger.error(f"Failed to generate guide index: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.guide_sections.clear()
            self.examples.clear()
            self.troubleshooting.clear()
            self.glossary.clear()
            self.logger.info("User guide generator cleanup completed")
        except Exception as e:
            self.logger.error(f"User guide generator cleanup failed: {e}")
