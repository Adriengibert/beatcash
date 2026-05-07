@echo off
title BEATCASH - App
cd /d "%~dp0"
echo.
echo  BEATCASH - lancement de l'app (PyWebView)
echo.
if not exist "dist\index.html" (
    echo  [INFO] Pas de build trouvee, je build d'abord...
    call npm run build
    if errorlevel 1 (
        echo  [ERREUR] Build echouee.
        pause & exit /b 1
    )
)
call python launch.py
pause
