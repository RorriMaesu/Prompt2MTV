@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    echo Expected virtual environment python was not found at "%PYTHON_EXE%".
    echo Create the virtual environment first, then install dependencies.
    exit /b 1
)

echo Installing packaging dependency...
"%PYTHON_EXE%" -m pip install pyinstaller
if errorlevel 1 exit /b 1

if exist "dist\Prompt2MTV\_internal\bundled_models" (
    echo Removing obsolete bundled model payload from previous builds...
    rmdir /s /q "dist\Prompt2MTV\_internal\bundled_models"
)

echo Building Prompt2MTV executable...
"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean Prompt2MTV.spec
if errorlevel 1 exit /b 1

if exist "dist\Prompt2MTV\_internal\bundled_models" (
    echo Removing obsolete bundled model payload from build output...
    rmdir /s /q "dist\Prompt2MTV\_internal\bundled_models"
)

echo.
echo Build complete. Launch the app from "dist\Prompt2MTV\Prompt2MTV.exe".
exit /b 0