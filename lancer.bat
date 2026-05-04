@echo off
cd /d "%~dp0"
python app.py
if errorlevel 1 (
    echo.
    echo Une erreur s'est produite. As-tu lance installer.bat ?
    pause
)
