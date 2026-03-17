@echo off
setlocal

cd /d "%~dp0"

call .\build_exe.bat
if errorlevel 1 exit /b 1

if exist "dist\Prompt2MTV\_internal\bundled_models" (
    echo Removing obsolete bundled model payload before installer packaging...
    rmdir /s /q "dist\Prompt2MTV\_internal\bundled_models"
)

if exist "dist_installer" rmdir /s /q "dist_installer"

set "ISCC_EXE=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_EXE%" set "ISCC_EXE=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC_EXE%" set "ISCC_EXE=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"

if not exist "%ISCC_EXE%" (
    echo Inno Setup 6 was not found.
    echo Install Inno Setup 6 and rerun this script, or compile Prompt2MTV.iss manually.
    exit /b 1
)

echo Building Prompt2MTV installer...
"%ISCC_EXE%" "Prompt2MTV.iss"
if errorlevel 1 exit /b 1

echo.
echo Installer build complete. Check the "dist_installer" folder.
exit /b 0