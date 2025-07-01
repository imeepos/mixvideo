@echo off
echo 安装视频分析系统依赖项...
echo.

python --version
if errorlevel 1 (
    echo 错误: Python未安装或不在PATH中
    pause
    exit /b 1
)

echo.
echo 安装核心依赖...
python -m pip install --upgrade pip
python -m pip install requests>=2.25.0
python -m pip install numpy>=1.20.0
python -m pip install opencv-python>=4.5.0
python -m pip install Pillow>=8.0.0
python -m pip install PyYAML>=5.4.0
python -m pip install loguru>=0.6.0

echo.
echo 验证安装...
python -c "import requests, numpy, cv2, PIL, yaml, loguru; print('所有依赖安装成功!')"

if errorlevel 1 (
    echo.
    echo 部分依赖安装失败，尝试备用方案...
    python install_dependencies_safe.py
)

echo.
echo 安装完成！
pause
