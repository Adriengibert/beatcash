@echo off
echo ============================================
echo   YouTube Bot - Installation
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe!
    echo Telecharge Python sur https://python.org
    echo Coche "Add Python to PATH" pendant l'installation!
    pause
    exit /b 1
)

echo [1/2] Installation des packages Python...
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client tkinterdnd2 imageio-ffmpeg instagrapi anthropic

echo.
echo [2/2] Installation terminee!
echo.
echo Double-clique sur "lancer.bat" pour demarrer le bot.
echo.
pause
