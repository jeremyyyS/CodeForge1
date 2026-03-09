@echo off
REM ============================================================
REM CodeForge - One-Click Startup (Windows)
REM Usage: Double-click this file or run: run.bat
REM ============================================================

title CodeForge
cd /d "%~dp0"

echo.
echo  ================================================
echo     CodeForge - Python Code Optimizer
echo  ================================================
echo.

REM ---- Check Python ----
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Download from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [1/4] Python found.

REM ---- Install Dependencies ----
echo [2/4] Installing dependencies...
pip install -r codeforge-frontend\requirements.txt
if errorlevel 1 (
    echo [WARNING] Some dependencies may have failed. Trying to continue...
)
echo       Dependencies ready.

REM ---- Setup .env if missing ----
if not exist backend_new\.env (
    echo [INFO] Creating .env from template...
    copy backend_new\.env.example backend_new\.env >nul 2>nul
    echo       Edit backend_new\.env to add your GEMINI_API_KEY for AI mode.
)

REM ---- Start Backend ----
echo [3/4] Starting backend server...
pushd backend_new
start "CodeForge-Backend" /min python jeremy_final.py
popd

REM Wait for backend to be ready
echo       Waiting for backend to start...
timeout /t 5 /nobreak >nul
echo       Backend running on http://localhost:8000

REM ---- Start Frontend ----
echo [4/4] Starting frontend...
echo.
echo  ================================================
echo    CodeForge is ready!
echo    Open:  http://localhost:8501
echo    Login: admin / admin123
echo  ================================================
echo.
echo  Press Ctrl+C or close this window to stop.
echo.

pushd codeforge-frontend
streamlit run Login.py --server.port 8501 --server.headless true
popd

REM ---- Cleanup when frontend stops ----
echo.
echo Stopping backend...
taskkill /f /fi "WINDOWTITLE eq CodeForge-Backend" >nul 2>&1
echo CodeForge stopped.
pause
