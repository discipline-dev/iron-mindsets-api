@echo off
cd /d %~dp0

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Starting ExistentialBot...
python existential_bot.py

if %errorlevel% neq 0 (
    echo [ERROR] Bot crashed with exit code %errorlevel%.
) else (
    echo [INFO] Bot exited normally.
)

echo.
echo Press any key to close this window...
pause >nul
