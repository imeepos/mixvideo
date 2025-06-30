@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Uninstaller
echo =========================================

echo This will remove ShotDetectionGUI from your system.
echo.
set /p "CONFIRM=Are you sure you want to uninstall? (Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo Uninstallation cancelled.
    pause
    exit /b 0
)

echo.
echo Removing installation files...

set "INSTALL_DIR=C:\Program Files\ShotDetectionGUI"

if exist "%INSTALL_DIR%" (
    echo Removing: %INSTALL_DIR%
    rmdir /s /q "%INSTALL_DIR%"
    if exist "%INSTALL_DIR%" (
        echo WARNING: Some files could not be removed. Please remove manually.
    ) else (
        echo Successfully removed installation directory.
    )
) else (
    echo Installation directory not found: %INSTALL_DIR%
)

echo Removing desktop shortcut...
set "DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\ShotDetectionGUI.lnk"
if exist "%DESKTOP_SHORTCUT%" (
    del "%DESKTOP_SHORTCUT%"
    echo Removed: Desktop shortcut
) else (
    echo Desktop shortcut not found
)

echo Removing start menu shortcut...
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI"
if exist "%STARTMENU_DIR%" (
    rmdir /s /q "%STARTMENU_DIR%"
    echo Removed: Start menu shortcuts
) else (
    echo Start menu shortcuts not found
)

echo.
echo Uninstallation completed!
echo.
pause
