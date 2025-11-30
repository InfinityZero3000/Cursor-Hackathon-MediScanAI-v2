@echo off
echo ========================================
echo   MediScan AI - Backend Server
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
) else (
    echo [1/4] Virtual environment already exists
)

REM Activate virtual environment
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Install dependencies
echo [3/4] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [WARNING] Some dependencies may have failed to install
    echo Trying to continue anyway...
)

REM Create uploads directory
if not exist uploads mkdir uploads

REM Start Flask server
echo [4/4] Starting Flask server...
echo.
echo ========================================
echo   Server starting at http://localhost:5000
echo   Press Ctrl+C to stop the server
echo ========================================
echo.

python app.py

pause

