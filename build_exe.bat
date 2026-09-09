@echo off
REM Build script for CEP Target Analyzer executable
REM This creates a standalone Windows EXE with all dependencies bundled

echo ========================================
echo CEP Target Analyzer - Build EXE
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo.
) else (
    echo WARNING: No virtual environment found at .venv
    echo Please ensure Python and pip are in your PATH
    echo.
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    echo.
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM Build the executable
echo Building executable...
python -m PyInstaller build_exe.spec --clean
echo.

if exist "dist\CEP_Target_Analyzer.exe" (
    echo ========================================
    echo BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Executable location: dist\CEP_Target_Analyzer.exe
    echo.
    echo You can now distribute the entire 'dist' folder
    echo or just the CEP_Target_Analyzer.exe file.
    echo.
) else (
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Please check the error messages above.
    echo.
)

pause
