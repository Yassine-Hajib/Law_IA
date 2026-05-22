@echo off
title LegalAssistant - Launcher
color 0A

echo ============================================
echo    LegalAssistant - Moroccan Labor Law AI
echo ============================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] Missing .env file!
    echo.
    echo Please create a file named ".env" in this folder with:
    echo   GROQ_API_KEY=your_api_key_here
    echo   GROQ_MODEL=llama-3.3-70b-versatile
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo [1/3] Checking Python dependencies...
pip install -r requirements.txt --quiet
echo       Done!

echo [2/3] Starting Backend API...
start /min "LegalAssistant - Backend" cmd /k "cd /d %~dp0backend\api && python -m uvicorn main:app --host 127.0.0.1 --port 8000"

echo [3/3] Starting Frontend UI...
start /min "LegalAssistant - Frontend" cmd /k "cd /d %~dp0frontend && npm install --silent && npm run dev"

echo.
echo ============================================
echo    App is starting up, please wait...
echo    It will open automatically in your browser.
echo.
echo    If it does not open, go to:
echo    http://localhost:5173
echo ============================================
echo.

REM Wait 10 seconds then open the browser
timeout /t 10 /nobreak >nul
start http://localhost:5173

echo Press any key to close this window (app will keep running)...
pause >nul
