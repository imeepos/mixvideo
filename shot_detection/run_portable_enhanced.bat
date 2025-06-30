@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Portable Launcher v1.0.1
echo ======================================================

echo Searching for executable files...

set "FOUND_EXE=0"
set "EXE_PATH="

REM Check for single file version
if exist "ShotDetectionGUI.exe" (
    echo Found: ShotDetectionGUI.exe (single file version)
    set "FOUND_EXE=1"
    set "EXE_PATH=ShotDetectionGUI.exe"
    set "EXE_TYPE=Single File"
    goto :found
)

REM Check for directory version
if exist "ShotDetectionGUI_dist\ShotDetectionGUI.exe" (
    echo Found: ShotDetectionGUI_dist\ShotDetectionGUI.exe (directory version)
    set "FOUND_EXE=1"
    set "EXE_PATH=ShotDetectionGUI_dist\ShotDetectionGUI.exe"
    set "EXE_TYPE=Directory"
    goto :found
)

REM Check for installed version
if exist "C:\Program Files\ShotDetectionGUI\ShotDetectionGUI.exe" (
    echo Found: Installed version in Program Files
    set "FOUND_EXE=1"
    set "EXE_PATH=C:\Program Files\ShotDetectionGUI\ShotDetectionGUI.exe"
    set "EXE_TYPE=Installed"
    goto :found
)

:notfound
echo ERROR: ShotDetectionGUI.exe not found!
echo.
echo Searched locations:
echo 1. .\ShotDetectionGUI.exe (single file version)
echo 2. .\ShotDetectionGUI_dist\ShotDetectionGUI.exe (directory version)
echo 3. C:\Program Files\ShotDetectionGUI\ShotDetectionGUI.exe (installed version)
echo.
echo Current directory: %CD%
echo Directory contents:
dir /b
echo.
echo Solutions:
echo 1. Make sure you extracted all files from the ZIP archive
echo 2. Run this script from the correct directory
echo 3. Try installing using install.bat first
echo.
goto :end

:found
echo.
echo Starting application...
echo Type: %EXE_TYPE%
echo Path: %EXE_PATH%
echo.

REM Start the application
start "" "%EXE_PATH%"

if errorlevel 1 (
    echo ERROR: Failed to start the application!
    echo.
    echo Troubleshooting:
    echo 1. Check if the file exists: %EXE_PATH%
    echo 2. Try running as Administrator
    echo 3. Check antivirus software (may be blocking execution)
    echo 4. Verify file permissions
    echo.
    goto :end
)

echo Application started successfully!
echo.
echo If the application window doesn't appear:
echo 1. Check the taskbar for the application icon
echo 2. Wait a few seconds for the application to load
echo 3. Check if antivirus software blocked the execution
echo.

:end
echo Press any key to close this window...
pause >nul
