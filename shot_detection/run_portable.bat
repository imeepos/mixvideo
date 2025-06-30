@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Portable Version
echo =============================================

echo Starting application...
if exist "ShotDetectionGUI.exe" (
    start "" "ShotDetectionGUI.exe"
    echo Application started successfully!
) else if exist "ShotDetectionGUI_dist\ShotDetectionGUI.exe" (
    start "" "ShotDetectionGUI_dist\ShotDetectionGUI.exe"
    echo Application started successfully!
) else (
    echo ERROR: ShotDetectionGUI.exe not found!
    echo Please make sure you are running this script from the correct directory.
    echo.
    echo Expected files:
    echo - ShotDetectionGUI.exe (single file version)
    echo - OR ShotDetectionGUI_dist\ShotDetectionGUI.exe (directory version)
)

echo.
echo Press any key to close this window...
pause >nul
