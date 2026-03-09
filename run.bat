@echo off
REM ============================================================
REM CodeForge - One-Click Startup (Windows)
REM Usage: Double-click this file or run: run.bat
REM ============================================================

title CodeForge

echo.
echo   ____          _      _____
echo  / ___^|___   __^| ^| ___^|  ___^|__  _ __ __ _  ___
echo ^| ^|   / _ \ / _` ^|/ _ \ ^|_ / _ \^| '__/ _` ^|/ _ \
echo ^| ^|__^| (_) ^| (_^| ^|  __/  _^| (_) ^| ^| ^| (_^| ^|  __/
echo  \____\___/ \__,_^|\___|_^|  \___/^|_^|  \__, ^|\___|
echo                                       ^|___/
echo.

REM ---- Check Python ----
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Download from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
pip install -q -r codeforge-frontend\requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    echo Run manually: pip install -r codeforge-frontend\requirements.txt
    pause
    exit /b 1
)
echo       Dependencies OK.

REM ---- Setup .env if missing ----
if not exist backend_new\.env (
    echo [2/4] Creating .env from template...
    copy backend_new\.env.example backend_new\.env >nul
    echo       .env created. Edit backend_new\.env to add your GEMINI_API_KEY.
) else (
    echo [2/4] .env already exists.
)

REM ---- Start Backend ----
echo [3/4] Starting backend...
start /b "CodeForge Backend" python backend_new\jeremy_final.py

REM Wait for backend
echo       Waiting for backend...
timeout /t 5 /nobreak >nul

REM ---- Start Frontend ----
echo [4/4] Starting frontend...
echo.
echo =================================================
echo   CodeForge is ready!
echo   Frontend: http://localhost:8501
echo   Backend:  http://localhost:8000
echo   Login:    admin / admin123
echo =================================================
echo.
echo Close this window to stop CodeForge.
echo.

streamlit run codeforge-frontend\Login.py --server.port 8501 --server.headless true

REM ---- Cleanup on close ----
taskkill /f /fi "WINDOWTITLE eq CodeForge Backend" >nul 2>&1
echo CodeForge stopped.
pause
