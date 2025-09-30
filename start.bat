@echo off
echo 🤖 ZyraX Bot Startup Script
echo ========================================

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python 3.11 or higher.
    pause
    exit /b 1
)

echo Installing/checking requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install requirements!
    pause
    exit /b 1
)

echo Starting ZyraX Bot...
echo ========================================
python bot.py

pause
