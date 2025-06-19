@echo off
echo ========================================
echo   Employee Management System
echo   Auto-Deploy Script
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

:: Run the auto-deploy script
echo Starting auto-deployment...
echo.
python auto_deploy.py

:: Check if deployment was successful
if errorlevel 1 (
    echo.
    echo ========================================
    echo   Deployment Failed!
    echo ========================================
    echo Please check the error messages above
    pause
    exit /b 1
) else (
    echo.
    echo ========================================
    echo   Deployment Successful!
    echo ========================================
    echo Your application will be updated on Render
    echo Check your Render dashboard for status
    echo.
    timeout /t 5 /nobreak >nul
)

exit /b 0