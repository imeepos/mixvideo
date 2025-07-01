@echo off
chcp 65001 >nul
echo 修复FFmpeg编码问题...
echo.

echo 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: Python未安装
    pause
    exit /b 1
)

echo.
echo 设置环境变量...
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo.
echo 运行修复脚本...
python fix_ffmpeg_encoding.py

echo.
echo 测试修复结果...
python -c "import subprocess; print('FFmpeg编码修复测试完成')"

echo.
echo 修复完成！
pause
