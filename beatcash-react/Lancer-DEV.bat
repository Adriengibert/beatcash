@echo off
title BEATCASH React - DEV
cd /d "%~dp0"
echo.
echo  BEATCASH - dev server (Vite)
echo  → http://127.0.0.1:5174
echo  Ctrl+C pour arreter
echo.
call npm run dev -- --port 5174 --host 127.0.0.1
pause
