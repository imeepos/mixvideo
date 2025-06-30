@echo off
chcp 65001 >nul
echo Smart Shot Detection System - Installer v1.0.1
echo ================================================

echo Checking installation files...

REM Check if we're in the right directory
set "FOUND_FILES=0"

if exist "ShotDetectionGUI.exe" (
    echo Found: ShotDetectionGUI.exe (single file version)
    set "FOUND_FILES=1"
    set "SOURCE_TYPE=single"
    set "SOURCE_FILE=ShotDetectionGUI.exe"
)

if exist "ShotDetectionGUI_dist" (
    echo Found: ShotDetectionGUI_dist directory
    set "FOUND_FILES=1"
    set "SOURCE_TYPE=directory"
    set "SOURCE_DIR=ShotDetectionGUI_dist"
)

if "%FOUND_FILES%"=="0" (
    echo ERROR: No installation files found!
    echo.
    echo Please make sure you are running this script from the directory containing:
    echo - ShotDetectionGUI.exe (single file version)
    echo - OR ShotDetectionGUI_dist folder (directory version)
    echo.
    echo Current directory: %CD%
    echo Directory contents:
    dir /b
    echo.
    pause
    exit /b 1
)

echo Creating installation directory...
set "INSTALL_DIR=C:\Program Files\ShotDetectionGUI"

if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    if errorlevel 1 (
        echo ERROR: Failed to create installation directory!
        echo Please run this script as Administrator.
        pause
        exit /b 1
    )
    echo Created: %INSTALL_DIR%
) else (
    echo Directory already exists: %INSTALL_DIR%
)

echo Copying files...

if "%SOURCE_TYPE%"=="single" (
    echo Copying single file version...
    copy "%SOURCE_FILE%" "%INSTALL_DIR%\ShotDetectionGUI.exe"
    if errorlevel 1 (
        echo ERROR: Failed to copy executable file!
        pause
        exit /b 1
    )
    echo Successfully copied: %SOURCE_FILE%
) else (
    echo Copying directory version...
    xcopy /E /I /Y "%SOURCE_DIR%\*" "%INSTALL_DIR%\"
    if errorlevel 1 (
        echo ERROR: Failed to copy directory contents!
        pause
        exit /b 1
    )
    echo Successfully copied: %SOURCE_DIR%
)

REM Copy additional files if they exist
if exist "test_video.mp4" (
    copy "test_video.mp4" "%INSTALL_DIR%\test_video.mp4"
    echo Copied: test_video.mp4
)

if exist "README.md" (
    copy "README.md" "%INSTALL_DIR%\README.md"
    echo Copied: README.md
)

if exist "QUICK_START.txt" (
    copy "QUICK_START.txt" "%INSTALL_DIR%\QUICK_START.txt"
    echo Copied: QUICK_START.txt
)

echo Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT_PATH=%DESKTOP%\ShotDetectionGUI.lnk"
set "TARGET_PATH=%INSTALL_DIR%\ShotDetectionGUI.exe"

REM Verify target executable exists
if not exist "%TARGET_PATH%" (
    echo ERROR: Target executable not found: %TARGET_PATH%
    pause
    exit /b 1
)

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%TARGET_PATH%'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Smart Shot Detection System'; $Shortcut.Save()"

if exist "%SHORTCUT_PATH%" (
    echo Successfully created desktop shortcut
) else (
    echo WARNING: Failed to create desktop shortcut
)

echo Creating start menu shortcut...
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\ShotDetectionGUI"
if not exist "%STARTMENU%" (
    mkdir "%STARTMENU%"
)

set "STARTMENU_SHORTCUT=%STARTMENU%\ShotDetectionGUI.lnk"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTMENU_SHORTCUT%'); $Shortcut.TargetPath = '%TARGET_PATH%'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Smart Shot Detection System'; $Shortcut.Save()"

if exist "%STARTMENU_SHORTCUT%" (
    echo Successfully created start menu shortcut
) else (
    echo WARNING: Failed to create start menu shortcut
)

echo.
echo ================================================
echo Installation completed successfully!
echo ================================================
echo.
echo Installation details:
echo - Installed to: %INSTALL_DIR%
echo - Desktop shortcut: %SHORTCUT_PATH%
echo - Start menu: %STARTMENU_SHORTCUT%
echo.
echo You can now:
echo 1. Double-click the desktop shortcut
echo 2. Find "ShotDetectionGUI" in the start menu
echo 3. Run directly from: %TARGET_PATH%
echo.
echo Press any key to exit...
pause >nul
