@echo off
echo  ���ܾ�ͷ�����ֶ�ϵͳ - ��װ����
echo ========================================

echo  ������װĿ¼...
if not exist "C:\Program Files\ShotDetectionGUI" (
    mkdir "C:\Program Files\ShotDetectionGUI"
)

echo  �����ļ�...
xcopy /E /I /Y "ShotDetectionGUI_dist\*" "C:\Program Files\ShotDetectionGUI\"

echo  ���������ݷ�ʽ...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\���ܾ�ͷ���.lnk'); $Shortcut.TargetPath = 'C:\Program Files\ShotDetectionGUI\ShotDetectionGUI.exe'; $Shortcut.Save()"

echo  ������ʼ�˵���ݷ�ʽ...
if not exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI" (
    mkdir "%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI"
)
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI\���ܾ�ͷ���.lnk'); $Shortcut.TargetPath = 'C:\Program Files\ShotDetectionGUI\ShotDetectionGUI.exe'; $Shortcut.Save()"

echo  ��װ��ɣ�
echo  �������������ʼ�˵����ҵ�"���ܾ�ͷ���"��ݷ�ʽ
pause
