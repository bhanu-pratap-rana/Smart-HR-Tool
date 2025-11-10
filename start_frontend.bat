@echo off
echo ================================================
echo Starting Smart HR Tool - Frontend UI
echo ================================================
echo.
echo Frontend will open automatically in your browser
echo URL: http://localhost:8501
echo.
echo Make sure the backend is running first!
echo.
cd /d "%~dp0"
call venv\Scripts\activate.bat
streamlit run frontend/app.py
