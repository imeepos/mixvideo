# 🔧 Shot Detection v2.0 故障排除指南

## 📋 概述

本指南提供 Shot Detection v2.0 常见问题的诊断和解决方案，帮助用户快速解决使用过程中遇到的问题。

## 🚨 常见问题分类

### 🎬 视频处理问题

#### 问题1: 无法打开视频文件
**症状**: 提示"无法打开视频文件"或"VideoLoadError"

**可能原因**:
- 文件路径不正确
- 文件格式不支持
- 文件损坏
- 缺少编解码器

**解决方案**:
```bash
# 1. 检查文件路径
ls -la /path/to/video.mp4

# 2. 检查文件格式
ffprobe -v quiet -print_format json -show_format video.mp4

# 3. 转换文件格式
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4

# 4. 检查文件完整性
ffmpeg -v error -i video.mp4 -f null -
```

**预防措施**:
- 使用支持的格式：MP4, AVI, MOV, MKV, WMV
- 确保文件完整下载
- 定期更新 OpenCV 和 FFmpeg

#### 问题2: 检测结果不准确
**症状**: 镜头边界检测过多、过少或位置不准确

**可能原因**:
- 检测阈值设置不当
- 视频内容特殊（如动画、快速剪辑）
- 算法选择不合适

**解决方案**:
```python
# 1. 调整检测阈值
detector = FrameDifferenceDetector(threshold=0.2)  # 降低阈值，增加敏感度
detector = FrameDifferenceDetector(threshold=0.5)  # 提高阈值，减少误检

# 2. 尝试不同算法
hist_detector = HistogramDetector(threshold=0.4, bins=128)
multi_detector = MultiDetector([fd_detector, hist_detector])

# 3. 使用多算法融合
multi_detector = MultiDetector(
    detectors=[fd_detector, hist_detector],
    fusion_weights={"FrameDifference": 0.7, "Histogram": 0.3}
)
```

**调优建议**:
- 动作片：使用较高阈值 (0.4-0.6)
- 对话片：使用较低阈值 (0.2-0.4)
- 动画片：使用直方图检测器
- 纪录片：使用多算法融合

#### 问题3: 处理速度过慢
**症状**: 视频处理时间过长，系统响应缓慢

**可能原因**:
- 视频文件过大
- 系统资源不足
- 算法复杂度高
- 未启用优化

**解决方案**:
```python
# 1. 启用缓存
video_service = VideoService(detector, enable_cache=True)

# 2. 调整并行处理
batch_service = BatchService(detector, max_workers=4)

# 3. 使用性能监控
from core.performance import PerformanceMonitor
monitor = PerformanceMonitor()
monitor.start_monitoring()

# 4. 优化内存使用
from core.performance import MemoryManager
memory_manager = MemoryManager()
memory_manager.start_monitoring()
```

### 🖥️ GUI界面问题

#### 问题4: 界面无响应或卡死
**症状**: GUI界面冻结，无法点击按钮

**可能原因**:
- 主线程被阻塞
- 内存不足
- 长时间处理任务

**解决方案**:
```python
# 1. 检查后台任务
import psutil
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
    if 'python' in proc.info['name']:
        print(proc.info)

# 2. 强制结束进程
pkill -f "python.*shot_detection"

# 3. 重启应用
python main_v2.py
```

**预防措施**:
- 使用异步处理长时间任务
- 定期检查内存使用
- 实现进度回调和取消机制

#### 问题5: 界面显示异常
**症状**: 按钮错位、文字显示不全、主题异常

**可能原因**:
- 系统DPI设置问题
- 字体缺失
- Tkinter版本兼容性

**解决方案**:
```python
# 1. 设置DPI感知
import tkinter as tk
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

# 2. 调整字体大小
config.set('gui.font_size', 12)

# 3. 重置界面配置
config.reset_gui_config()
```

### ⚙️ 配置问题

#### 问题6: 配置文件错误
**症状**: 启动时提示配置错误或使用默认配置

**可能原因**:
- YAML语法错误
- 配置值类型错误
- 配置文件权限问题

**解决方案**:
```bash
# 1. 验证YAML语法
python -c "import yaml; yaml.safe_load(open('config_v2.yaml'))"

# 2. 检查文件权限
ls -la config_v2.yaml
chmod 644 config_v2.yaml

# 3. 重置配置
python -c "from config import get_config; get_config().reset_to_defaults()"
```

**配置验证**:
```python
from config import get_config

config = get_config()
is_valid, errors = config.validate_config()
if not is_valid:
    for error in errors:
        print(f"配置错误: {error}")
```

#### 问题7: 缓存问题
**症状**: 缓存占用空间过大或缓存失效

**解决方案**:
```python
# 1. 清理缓存
from core.performance import CacheOptimizer
cache_optimizer = CacheOptimizer()
result = cache_optimizer.optimize_cache('./cache')

# 2. 手动清理
import shutil
shutil.rmtree('./cache', ignore_errors=True)

# 3. 调整缓存配置
config.set('cache.max_cache_size_mb', 512)
config.set('cache.max_cache_age_hours', 12)
```

### 🔌 插件问题

#### 问题8: 插件加载失败
**症状**: 插件无法加载或功能不可用

**可能原因**:
- 插件文件错误
- 依赖缺失
- 版本不兼容

**解决方案**:
```python
# 1. 检查插件状态
from core.plugins import PluginManager
plugin_manager = PluginManager()
discovered = plugin_manager.discover_plugins()
print(f"发现插件: {discovered}")

# 2. 查看插件错误
status = plugin_manager.get_plugin_status()
for name, info in status.items():
    if 'error' in info:
        print(f"插件 {name} 错误: {info['error']}")

# 3. 重新加载插件
plugin_manager.reload_plugin('plugin_name')
```

### 💾 内存和性能问题

#### 问题9: 内存使用过高
**症状**: 系统内存占用持续增长，可能导致系统卡顿

**诊断方法**:
```python
# 1. 检查内存使用
import psutil
memory = psutil.virtual_memory()
print(f"内存使用: {memory.percent}%")
print(f"可用内存: {memory.available / 1024**3:.1f} GB")

# 2. 分析内存分布
from core.performance import MemoryManager
memory_manager = MemoryManager()
memory_info = memory_manager.get_memory_info()
print(memory_info)
```

**解决方案**:
```python
# 1. 启用内存管理
memory_manager = MemoryManager()
memory_manager.start_monitoring()

# 2. 手动优化内存
result = memory_manager.optimize_memory_usage()
print(f"释放内存: {result['freed_mb']:.1f} MB")

# 3. 设置内存限制
memory_manager.set_memory_limit(2048)  # 2GB限制
```

#### 问题10: CPU使用率过高
**症状**: CPU使用率持续高于80%，系统响应缓慢

**解决方案**:
```python
# 1. 减少并行线程
batch_service = BatchService(detector, max_workers=2)

# 2. 启用性能监控
from core.performance import PerformanceMonitor
monitor = PerformanceMonitor()
monitor.start_monitoring()

# 3. 获取优化建议
suggestions = monitor.optimize_performance()
for opt in suggestions['optimizations']:
    print(f"建议: {opt}")
```

## 🔍 诊断工具

### 系统诊断脚本
```python
#!/usr/bin/env python3
"""
系统诊断脚本
"""

import sys
import psutil
from pathlib import Path

def diagnose_system():
    """系统诊断"""
    print("=== Shot Detection 系统诊断 ===")
    
    # Python版本
    print(f"Python版本: {sys.version}")
    
    # 系统资源
    memory = psutil.virtual_memory()
    print(f"内存: {memory.total / 1024**3:.1f} GB (使用 {memory.percent}%)")
    
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU: {cpu_count} 核心 (使用 {cpu_percent}%)")
    
    # 磁盘空间
    disk = psutil.disk_usage('.')
    print(f"磁盘: {disk.total / 1024**3:.1f} GB (使用 {disk.percent}%)")
    
    # 检查依赖
    required_packages = ['cv2', 'numpy', 'loguru', 'yaml']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安装")
        except ImportError:
            print(f"❌ {package}: 未安装")
    
    # 检查文件
    important_files = [
        'config_v2.yaml',
        'main_v2.py',
        'core/__init__.py'
    ]
    for file_path in important_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}: 存在")
        else:
            print(f"❌ {file_path}: 缺失")

if __name__ == "__main__":
    diagnose_system()
```

### 日志分析工具
```bash
#!/bin/bash
# 日志分析脚本

echo "=== Shot Detection 日志分析 ==="

# 检查日志文件
if [ -f "logs/shot_detection.log" ]; then
    echo "📄 日志文件存在"
    
    # 统计错误数量
    error_count=$(grep -c "ERROR" logs/shot_detection.log)
    warning_count=$(grep -c "WARNING" logs/shot_detection.log)
    
    echo "❌ 错误数量: $error_count"
    echo "⚠️ 警告数量: $warning_count"
    
    # 显示最近的错误
    echo "🔍 最近的错误:"
    grep "ERROR" logs/shot_detection.log | tail -5
    
else
    echo "❌ 日志文件不存在"
fi
```

## 🆘 紧急恢复

### 完全重置
```bash
#!/bin/bash
# 紧急重置脚本

echo "🚨 执行紧急重置..."

# 1. 停止所有相关进程
pkill -f "python.*shot_detection"

# 2. 清理缓存
rm -rf ./cache/*
rm -rf ./temp/*

# 3. 重置配置
cp config_v2.yaml.backup config_v2.yaml

# 4. 清理日志
> logs/shot_detection.log

# 5. 重新安装依赖
pip install -r requirements.txt --force-reinstall

echo "✅ 重置完成，请重新启动应用"
```

### 数据恢复
```python
def recover_data():
    """数据恢复"""
    import shutil
    from datetime import datetime
    
    # 创建备份
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".git", "venv"
    ))
    
    print(f"数据已备份到: {backup_dir}")
    
    # 恢复默认配置
    from config import get_config
    config = get_config()
    config.reset_to_defaults()
    config.save_config()
    
    print("配置已重置为默认值")
```

## 📞 获取帮助

### 自助诊断
1. 运行系统诊断脚本
2. 检查日志文件
3. 查看配置文件
4. 测试基本功能

### 问题报告
提交问题时请包含：

1. **系统信息**
   ```bash
   python --version
   pip list | grep -E "(opencv|numpy|loguru)"
   uname -a  # Linux/macOS
   systeminfo  # Windows
   ```

2. **错误信息**
   ```bash
   # 完整的错误堆栈
   tail -50 logs/shot_detection.log
   ```

3. **重现步骤**
   - 详细的操作步骤
   - 使用的配置参数
   - 输入文件信息

4. **环境配置**
   ```bash
   # 配置文件内容
   cat config_v2.yaml
   ```

### 联系方式
- 📧 邮箱: support@shotdetection.com
- 🐛 问题追踪: GitHub Issues
- 💬 社区论坛: 用户交流群
- 📚 文档: 在线帮助文档

## 🔄 版本兼容性

### 升级指南
从 v1.x 升级到 v2.0:

1. **备份数据**
   ```bash
   cp -r shot_detection shot_detection_backup
   ```

2. **迁移配置**
   ```python
   from config import migrate_config
   migrate_config("config.yaml", "config_v2.yaml")
   ```

3. **更新代码**
   ```python
   # 旧版本
   from shot_detection import ShotDetector
   
   # 新版本
   from core.detection import FrameDifferenceDetector
   from core.services import VideoService
   ```

### 向后兼容
v2.0 提供向后兼容支持：

```python
# 兼容模式
from core.detection import LegacyDetectorAdapter
legacy_detector = LegacyDetectorAdapter(old_detector)
```

---

**📝 文档版本**: v2.0.0  
**📅 最后更新**: 2025-07-01  
**🆘 紧急联系**: support@shotdetection.com
