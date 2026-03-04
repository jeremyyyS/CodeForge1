@echo off
title CodeForge - Starting Up

echo =============================
echo   CodeForge - Starting Up
echo =============================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is required but not found. Please install Python 3.8+.
    pause
    exit /b 1
)

echo Python found.

:: Install dependencies
if exist codeforge-frontend\requirements.txt (
    echo Installing dependencies...
    pip install -r codeforge-frontend\requirements.txt --quiet 2>nul
    echo Dependencies ready.
)
echo.

:: Start Backend in a new window
echo Starting Backend (FastAPI) on http://localhost:8000 ...
start "CodeForge Backend" cmd /k "cd backend_new && python jeremy_final.py"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start Frontend in a new window
echo Starting Frontend (Streamlit) on http://localhost:8501 ...
start "CodeForge Frontend" cmd /k "cd codeforge-frontend && streamlit run Login.py"

echo.
echo =============================
echo   CodeForge is running!
echo   Frontend: http://localhost:8501
echo   Backend:  http://localhost:8000
echo   Close the terminal windows to stop.
echo =============================
echo.
pause
