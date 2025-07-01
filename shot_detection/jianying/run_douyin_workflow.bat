@echo off
chcp 65001 >nul
echo.
echo 🎬 抖音视频制作工作流程 - Windows 启动脚本
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    echo 💡 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查当前目录结构
if not exist "resources" (
    echo ❌ 错误: 当前目录下没有找到 resources 文件夹
    echo 💡 请确保在包含 resources 和 templates 文件夹的目录中运行此脚本
    echo.
    echo 📁 期望的目录结构:
    echo    your_project/
    echo    ├── resources/     ^(视频素材目录^)
    echo    ├── templates/     ^(抖音项目模板目录^)
    echo    └── outputs/       ^(输出目录，自动创建^)
    echo.
    pause
    exit /b 1
)

if not exist "templates" (
    echo ❌ 错误: 当前目录下没有找到 templates 文件夹
    echo 💡 请确保在包含 resources 和 templates 文件夹的目录中运行此脚本
    pause
    exit /b 1
)

echo ✅ 目录结构检查通过
echo.

REM 询问用户运行模式
echo 请选择运行模式:
echo 1. 预览模式 (只分析，不生成文件)
echo 2. 完整运行 (生成所有项目)
echo.
set /p choice="请输入选择 (1 或 2): "

if "%choice%"=="1" (
    echo.
    echo 🔍 启动预览模式...
    python douyin_workflow.py --preview -v
) else if "%choice%"=="2" (
    echo.
    echo 🚀 启动完整工作流程...
    python douyin_workflow.py -v
) else (
    echo ❌ 无效选择，默认使用预览模式
    echo.
    python douyin_workflow.py --preview -v
)

echo.
echo 📋 工作流程完成！
pause
