@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Python Version (Fixed)
echo =====================================================

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

python --version
echo.

echo Checking tkinter availability...
python -c "import tkinter; print('tkinter: Available')" 2>nul
if errorlevel 1 (
    echo ERROR: tkinter is not available!
    echo.
    echo This is a common issue with Python 3.13 on Windows.
    echo.
    echo Solutions:
    echo 1. Reinstall Python from python.org with "tcl/tk and IDLE" option checked
    echo 2. Install Python 3.11 or 3.12 instead (more stable for GUI applications)
    echo 3. Use Anaconda Python distribution (includes tkinter by default)
    echo 4. Try: pip install tk (may work on some systems)
    echo.
    echo Recommended: Download Python 3.11.9 from python.org
    echo Direct link: https://www.python.org/downloads/release/python-3119/
    echo.
    set /p "continue=Try to continue anyway? (y/N): "
    if /i not "%continue%"=="y" (
        echo.
        echo Installation cancelled. Please install tkinter first.
        pause
        exit /b 1
    )
    echo.
    echo WARNING: Continuing without tkinter verification...
) else (
    echo tkinter: Available
)

echo.

echo Checking other dependencies...
python -c "import sys; print(f'Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"

echo.
echo Installing required packages...
echo This may take a few minutes on first run...

pip install --upgrade pip >nul 2>&1

echo Installing opencv-python...
pip install opencv-python
if errorlevel 1 (
    echo WARNING: opencv-python installation failed, trying alternative...
    pip install opencv-python-headless
)

echo Installing numpy...
pip install numpy
if errorlevel 1 (
    echo ERROR: numpy installation failed!
    echo This is required for the application to work.
    pause
    exit /b 1
)

echo Installing loguru...
pip install loguru

echo Installing Pillow...
pip install Pillow

echo Installing additional dependencies...
pip install pathlib2 dataclasses typing-extensions

echo.
echo Verifying installations...
python -c "import cv2; print('OpenCV: OK')" 2>nul || echo "OpenCV: FAILED"
python -c "import numpy; print('NumPy: OK')" 2>nul || echo "NumPy: FAILED"
python -c "import loguru; print('Loguru: OK')" 2>nul || echo "Loguru: FAILED"
python -c "from PIL import Image; print('Pillow: OK')" 2>nul || echo "Pillow: FAILED"

echo.
echo All dependencies processed!
echo.

echo Starting Smart Shot Detection System...
echo If the application doesn't start, check the error messages above.
echo.

python run_gui.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start!
    echo.
    echo Common solutions:
    echo 1. Check if all files were extracted properly
    echo 2. Verify Python version is 3.8-3.12 (3.13 may have compatibility issues)
    echo 3. Install tkinter: pip install tk
    echo 4. Try running: python check_dependencies.py
    echo 5. Consider using Python 3.11 instead of 3.13
    echo.
    echo For Python 3.13 users:
    echo - This version is very new and may have compatibility issues
    echo - Consider downgrading to Python 3.11.9 for better stability
    echo.
    pause
)

echo.
echo Application session ended.
pause
