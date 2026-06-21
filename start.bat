@echo off
title HMP Panel
cd /d "%~dp0"

echo =======================================================
echo   HappinessMP Panel
echo =======================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

echo [INFO] Starting panel...
echo [INFO] Open http://localhost:20000 in your browser
echo [INFO] Press Ctrl+C to stop the panel
echo.

call .venv\Scripts\activate.bat
python main.py %*

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Panel exited with code %errorlevel%
    pause
)
