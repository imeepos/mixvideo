@echo off
echo  智能镜头检测与分段系统 - 安装程序
echo ========================================

echo  创建安装目录...
if not exist "C:\Program Files\ShotDetectionGUI" (
    mkdir "C:\Program Files\ShotDetectionGUI"
)

echo  复制文件...
xcopy /E /I /Y "ShotDetectionGUI_dist\*" "C:\Program Files\ShotDetectionGUI\"

echo  创建桌面快捷方式...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\智能镜头检测.lnk'); $Shortcut.TargetPath = 'C:\Program Files\ShotDetectionGUI\ShotDetectionGUI.exe'; $Shortcut.Save()"

echo  创建开始菜单快捷方式...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI" (
    mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI"
)
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI\智能镜头检测.lnk'); $Shortcut.TargetPath = 'C:\Program Files\ShotDetectionGUI\ShotDetectionGUI.exe'; $Shortcut.Save()"

echo  安装完成！
echo  您可以在桌面或开始菜单中找到"智能镜头检测"快捷方式
pause
