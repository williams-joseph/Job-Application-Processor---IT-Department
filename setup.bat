@echo off
REM Quick start script for ECOWAS Application Processor (Windows)

echo ==================================
echo ECOWAS Application Processor Setup
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python found

REM Check if virtual environment exists
if not exist "venv\" (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo To run the application:
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
echo To build executable:
echo   python build.py
echo.
echo IMPORTANT: Install Tesseract OCR
echo Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo.

pause
