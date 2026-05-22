@echo off
title LegalAssistant - Stopping...
color 0C

echo ============================================
echo    Stopping LegalAssistant...
echo ============================================
echo.

echo Closing Backend (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Closing Frontend (port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Closing terminal windows...
taskkill /FI "WINDOWTITLE eq LegalAssistant - Backend" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq LegalAssistant - Frontend" /F >nul 2>&1

echo.
echo All services stopped successfully.
echo.
timeout /t 2 /nobreak >nul
