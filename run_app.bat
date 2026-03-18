@echo off
REM ===============================================
REM ONLUYEN Batch - Flask Web Application
REM ===============================================

echo.
echo ========================================
echo.  ONLUYEN Batch Application
echo.  Flask Web Server
echo.
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install requirements if needed
echo [*] Checking dependencies...
python -m pip list | find /i "Flask" >nul
if %errorlevel% neq 0 (
    echo [*] Installing Flask...
    python -m pip install -r requirements.txt
)

REM Run the Flask app
echo.
echo [*] Starting Flask Application...
echo [*] Server will run at: http://localhost:5000
echo [*] Press Ctrl+C to stop the server
echo.
python app.py

pause
