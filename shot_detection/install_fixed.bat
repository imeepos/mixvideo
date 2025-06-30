@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Installer
echo ========================================

echo Creating installation directory...
if not exist "C:\Program Files\ShotDetectionGUI" (
    mkdir "C:\Program Files\ShotDetectionGUI"
)

echo Copying files...
xcopy /E /I /Y "ShotDetectionGUI_dist\*" "C:\Program Files\ShotDetectionGUI\"

echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\ShotDetectionGUI.lnk'); $Shortcut.TargetPath = 'C:\Program Files\ShotDetectionGUI\ShotDetectionGUI.exe'; $Shortcut.Save()"

echo Creating start menu shortcut...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI" (
    mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI"
)
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI\ShotDetectionGUI.lnk'); $Shortcut.TargetPath = 'C:\Program Files\ShotDetectionGUI\ShotDetectionGUI.exe'; $Shortcut.Save()"

echo Installation completed!
echo You can find "ShotDetectionGUI" shortcut on desktop or start menu
pause
