@echo off
title HMP Panel - Windows Installer
cd /d "%~dp0"

echo =======================================================
echo   HappinessMP Panel - Windows Installation
echo =======================================================
echo.

REM Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.9 or newer from: https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
python --version
echo [OK]   Python found
echo.

REM Check Python version
for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYVER=%%V
echo [INFO] Python version: %PYVER%
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist ".venv" (
    echo [INFO] Virtual environment already exists, skipping...
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK]   Virtual environment created
)
echo.

REM Activate and upgrade pip
echo [3/5] Setting up pip...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)
python -m pip install --upgrade pip --quiet
echo [OK]   Pip is ready
echo.

REM Install dependencies
echo [4/5] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARN] Some dependencies may have failed to install.
    echo [INFO] The panel might still work with limited functionality.
) else (
    echo [OK]   Dependencies installed
)
echo.

REM Create data directory
if not exist "data" mkdir data

REM Create start scripts
echo [5/5] Creating start scripts...

if not exist "start.bat" (
    echo @echo off > start.bat
    echo title HMP Panel >> start.bat
    echo cd /d "%%~dp0" >> start.bat
    echo echo Starting HappinessMP Panel... >> start.bat
    echo echo. >> start.bat
    echo call .venv\Scripts\activate.bat >> start.bat
    echo python main.py %%* >> start.bat
    echo pause >> start.bat
)

echo [OK]   Installation complete!
echo.
echo =======================================================
echo   How to start:
echo.
echo   Run:  start.bat
echo.
echo   Or with custom port:  start.bat --port 20000
echo.
echo   Then open your browser to:
echo     http://localhost:20000
echo.
echo   For background running, use:  start_hidden.vbs
echo =======================================================
echo.

pause
