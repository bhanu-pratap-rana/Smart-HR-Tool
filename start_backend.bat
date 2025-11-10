@echo off
echo ================================================
echo Starting Smart HR Tool - Refactored Backend
echo ================================================
echo.
echo Backend API will run on: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
cd /d "%~dp0"
call venv\Scripts\activate.bat
python -m backend.app.main
