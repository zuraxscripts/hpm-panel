@echo off
title HMP Panel - Stop
cd /d "%~dp0"

echo Stopping HappinessMP Panel...

REM Try to stop the Python processes gracefully
for /f "tokens=2" %%P in ('tasklist /fi "imagename eq python.exe" /fo csv /nh 2^>nul') do (
    taskkill /f /pid %%P >nul 2>&1
)

for /f "tokens=2" %%P in ('tasklist /fi "imagename eq python3.exe" /fo csv /nh 2^>nul') do (
    taskkill /f /pid %%P >nul 2>&1
)

echo [OK] Panel stopped (if it was running)
echo.
pause
