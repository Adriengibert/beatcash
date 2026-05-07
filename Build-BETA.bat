@echo off
title Beat Cash - Build BETA
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo ============================================
echo   BUILD BEAT CASH BETA  (.exe + zip)
echo ============================================
echo.

:: ── 1. Build React ────────────────────────────
echo [1/4] Build React (vite)...
pushd beatcash-react
call npm run build
if errorlevel 1 ( echo [ERREUR] vite build a echoue. & popd & pause & exit /b 1 )
popd

:: ── 2. Tuer instances + PyInstaller ──────────
echo.
echo [2/4] PyInstaller (peut prendre 2-3 min)...
powershell -NoProfile -Command "Stop-Process -Name BeatCashReact -Force -ErrorAction SilentlyContinue; Stop-Process -Name BeatCash -Force -ErrorAction SilentlyContinue" > nul 2>&1
call python -m PyInstaller beat_cash_react.spec --noconfirm
if errorlevel 1 ( echo [ERREUR] PyInstaller a echoue. & pause & exit /b 1 )

:: ── 3. Recopier creds + README + bat + BETA.flag ─
echo.
echo [3/4] Copie credentials + docs...
set DIST=dist\BeatCashReact
if exist client_secrets.json     copy /Y client_secrets.json     "%DIST%\" > nul
if exist token.pickle            copy /Y token.pickle            "%DIST%\" > nul
if exist instagram_session.json  copy /Y instagram_session.json  "%DIST%\" > nul
copy /Y assets-beta\LISEZ-MOI.txt    "%DIST%\" > nul 2>&1
copy /Y assets-beta\Lancer-BETA.bat  "%DIST%\" > nul 2>&1
type nul > "%DIST%\BETA.flag"
echo  OK

:: ── 4. Zip ───────────────────────────────────
echo.
echo [4/4] Zip...
if exist dist\BeatCash-BETA.zip del dist\BeatCash-BETA.zip
powershell -NoProfile -Command "Compress-Archive -Path 'dist\BeatCashReact\*' -DestinationPath 'dist\BeatCash-BETA.zip' -Force"
echo  OK

echo.
echo ============================================
echo   BUILD TERMINE
echo ============================================
echo  Exe : dist\BeatCashReact\BeatCashReact.exe
echo  Zip : dist\BeatCash-BETA.zip
echo.
pause
