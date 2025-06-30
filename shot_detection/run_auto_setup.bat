@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Auto Setup Version
echo ================================================

echo 🔍 系统环境自动检查和配置...
echo.

echo 检查Python安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    echo.
    echo 请先安装Python 3.8或更高版本:
    echo https://www.python.org/downloads/
    echo.
    echo 安装时请确保勾选 "Add Python to PATH"
    pause
    exit /b 1
)

python --version
echo ✅ Python已安装
echo.

echo 🚀 启动自动环境检查...
echo 这将自动检查并安装所有必要的依赖项
echo.

REM 设置本地FFmpeg路径（如果存在）
if exist "bin\ffmpeg.exe" (
    echo 🔧 配置本地FFmpeg环境...
    set PATH=%~dp0bin;%PATH%
    echo ✅ 本地FFmpeg已配置
    echo.
)

echo 启动应用程序...
python run_gui.py

if errorlevel 1 (
    echo.
    echo ❌ 应用程序启动失败
    echo.
    echo 故障排除建议:
    echo 1. 检查Python版本: python --version
    echo 2. 运行依赖检查: python check_dependencies.py
    echo 3. 运行tkinter测试: python test_tkinter.py
    echo 4. 检查FFmpeg: python check_ffmpeg.py
    echo.
    echo 如果问题持续，请尝试:
    echo - 重新安装Python 3.11.9 (推荐版本)
    echo - 运行: python install_ffmpeg.py
    echo.
)

echo.
echo 应用程序会话结束
pause
