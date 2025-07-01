@echo off
chcp 65001 >nul
echo.
echo 🎬 启动视频混剪GUI
echo ==================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    echo 💡 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo 🚀 启动视频混剪GUI...
echo.

python video_mix_gui.py

echo.
echo 📋 GUI应用已关闭
pause
