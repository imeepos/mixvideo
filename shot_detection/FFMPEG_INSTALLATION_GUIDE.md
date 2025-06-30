# 🎬 FFmpeg安装和配置指南

## 📋 问题说明

**错误信息：**
```
[WinError 2] 系统找不到指定的文件。
```

**原因分析：**
- Windows系统默认不包含FFmpeg
- 应用程序需要FFmpeg来处理视频分段
- 需要下载并配置FFmpeg

## 🚀 快速解决方案

### **方法1：自动安装（推荐）**

```batch
# 1. 运行FFmpeg自动安装工具
python install_ffmpeg.py

# 2. 使用FFmpeg启动器
run_with_ffmpeg.bat
```

### **方法2：检查和诊断**

```batch
# 检查FFmpeg状态
python check_ffmpeg.py
```

## 📦 完整解决流程

### **步骤1：检查FFmpeg状态**

运行检查工具：
```batch
python check_ffmpeg.py
```

输出示例：
```
🔍 检查系统FFmpeg...
❌ 系统未安装FFmpeg

🔍 检查本地FFmpeg...
❌ 本地未找到FFmpeg

📊 检查结果总结
❌ 未找到可用的FFmpeg
🔧 需要安装FFmpeg
```

### **步骤2：自动安装FFmpeg**

运行安装工具：
```batch
python install_ffmpeg.py
```

安装过程：
```
📥 下载FFmpeg for Windows...
正在下载: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
这可能需要几分钟时间...
✅ 下载完成

📦 解压FFmpeg...
✅ 解压完成
找到FFmpeg: ffmpeg_download\ffmpeg-6.0-essentials_build\bin\ffmpeg.exe

📁 安装FFmpeg到本地目录...
✅ FFmpeg安装到: D:\YourApp\bin\ffmpeg.exe
✅ FFmpeg安装验证成功

🚀 创建应用启动器...
✅ 创建了FFmpeg启动器: run_with_ffmpeg.bat

🎉 FFmpeg安装完成！
```

### **步骤3：使用FFmpeg启动器**

双击运行：
```batch
run_with_ffmpeg.bat
```

启动器会：
1. ✅ 设置FFmpeg路径
2. ✅ 验证FFmpeg可用性
3. ✅ 启动应用程序

## 🔧 手动安装方法

### **Windows用户**

#### **方法A：官方下载**
1. 访问：https://ffmpeg.org/download.html
2. 选择"Windows"
3. 下载"release builds"
4. 解压到任意目录
5. 将`bin`目录添加到系统PATH

#### **方法B：包管理器**

**使用Chocolatey：**
```batch
# 安装Chocolatey (如果未安装)
# 访问: https://chocolatey.org/install

# 安装FFmpeg
choco install ffmpeg
```

**使用Scoop：**
```batch
# 安装Scoop (如果未安装)
# 访问: https://scoop.sh/

# 安装FFmpeg
scoop install ffmpeg
```

### **Linux用户**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

### **macOS用户**

```bash
# 使用Homebrew
brew install ffmpeg

# 使用MacPorts
sudo port install ffmpeg
```

## 📁 文件结构说明

### **安装后的目录结构**
```
YourApp/
├── bin/
│   └── ffmpeg.exe          # 本地FFmpeg可执行文件
├── run_with_ffmpeg.bat     # FFmpeg启动器
├── setup_ffmpeg_path.bat   # 环境变量设置
├── install_ffmpeg.py       # 自动安装工具
├── check_ffmpeg.py         # 检查工具
└── run_gui.py              # 主程序
```

### **启动器工作原理**
```batch
# run_with_ffmpeg.bat 内容
@echo off
set PATH=%~dp0bin;%PATH%    # 添加本地bin到PATH
bin\ffmpeg.exe -version     # 验证FFmpeg
python run_gui.py           # 启动应用
```

## 🔍 故障排除

### **问题1：下载失败**
```
❌ 下载失败: HTTP Error 403: Forbidden
```

**解决方案：**
1. 检查网络连接
2. 尝试手动下载
3. 使用VPN或代理
4. 使用包管理器安装

### **问题2：解压失败**
```
❌ 解压失败: Bad zipfile
```

**解决方案：**
1. 重新下载ZIP文件
2. 检查磁盘空间
3. 使用管理员权限运行
4. 手动解压ZIP文件

### **问题3：权限问题**
```
❌ 安装失败: Permission denied
```

**解决方案：**
1. 以管理员身份运行
2. 更改安装目录权限
3. 安装到用户目录

### **问题4：PATH问题**
```
❌ FFmpeg not found in PATH
```

**解决方案：**
1. 使用`run_with_ffmpeg.bat`启动
2. 运行`setup_ffmpeg_path.bat`
3. 手动添加到系统PATH

## 🎯 验证安装

### **验证命令**
```batch
# 检查FFmpeg版本
ffmpeg -version

# 或使用本地路径
bin\ffmpeg.exe -version

# 或使用检查工具
python check_ffmpeg.py
```

### **成功输出示例**
```
ffmpeg version 6.0 Copyright (c) 2000-2023 the FFmpeg developers
built with gcc 12.2.0 (Rev10, Built by MSYS2 project)
configuration: --enable-gpl --enable-version3 ...
```

## 📊 性能说明

### **FFmpeg版本选择**
- **Essentials版本**：基本功能，文件较小（~50MB）
- **Full版本**：完整功能，文件较大（~100MB）
- **推荐**：Essentials版本足够使用

### **处理性能**
- **编码速度**：取决于视频分辨率和质量设置
- **内存使用**：通常50-200MB
- **磁盘空间**：输出文件约为输入文件的50-80%

## 🎉 最终验证

安装完成后，运行完整测试：

```batch
# 1. 检查FFmpeg
python check_ffmpeg.py

# 2. 启动应用
run_with_ffmpeg.bat

# 3. 测试视频处理
# 在应用中选择test_video.mp4进行处理
```

**成功标志：**
- ✅ FFmpeg检查通过
- ✅ 应用正常启动
- ✅ 视频分段处理成功
- ✅ 生成输出文件

---

© 2024 Smart Shot Detection System - FFmpeg安装指南
