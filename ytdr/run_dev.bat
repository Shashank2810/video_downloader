@echo off
:: Check admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting Administrator permission...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

echo Starting development server...
echo.

uvicorn app:app --reload

pause