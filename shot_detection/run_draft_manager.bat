@echo off
echo 启动剪映草稿管理器...
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 运行草稿管理器
python run_draft_manager.py

REM 如果出错，暂停以查看错误信息
if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)
