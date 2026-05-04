@echo off
chcp 65001 > nul
title Beat Cash — Build
color 0F

echo.
echo  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
echo    BEAT CASH  ^|  Build Application Windows
echo  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
echo.

:: ── Vérification Python ─────────────────────────────────────────────
python --version > nul 2>&1
if errorlevel 1 (
    echo  [ERREUR] Python non trouve.
    echo  Telecharge Python sur https://python.org
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  Python : %%v

:: ── Étape 1 : dépendances ──────────────────────────────────────────
echo.
echo  [1/5] Installation des outils de build...
pip install pyinstaller pillow --quiet --upgrade
if errorlevel 1 (
    echo  [ERREUR] Impossible d'installer pyinstaller.
    pause & exit /b 1
)
echo  OK  pyinstaller + pillow

:: ── Étape 2 : icône ─────────────────────────────────────────────────
echo.
echo  [2/5] Generation de l'icone Beat Cash...
python create_icon.py
if errorlevel 1 (
    echo  [AVERT] Icone non creee, on continue sans icone.
    if exist beat_cash.ico del beat_cash.ico
)

:: ── Étape 3 : nettoyage ─────────────────────────────────────────────
echo.
echo  [3/5] Nettoyage des builds precedents...
if exist build      rmdir /s /q build
if exist dist\BeatCash rmdir /s /q dist\BeatCash
echo  OK

:: ── Étape 4 : compilation ───────────────────────────────────────────
echo.
echo  [4/5] Compilation (3-8 minutes selon la machine)...
echo  Ne ferme pas cette fenetre.
echo.
pyinstaller beat_cash.spec --noconfirm --clean
if errorlevel 1 (
    echo.
    echo  [ERREUR] La compilation a echoue.
    echo  Verifie que toutes les dependances sont installees :
    echo    installer.bat
    pause & exit /b 1
)

:: ── Étape 5 : copier client_secrets.json si présent ─────────────────
echo.
echo  [5/5] Finalisation...
if exist client_secrets.json (
    copy client_secrets.json dist\BeatCash\ > nul
    echo  OK  client_secrets.json copie dans dist\BeatCash\
) else (
    echo  INFO : client_secrets.json absent — a copier manuellement dans dist\BeatCash\
)

:: ── Résultat ─────────────────────────────────────────────────────────
echo.
echo  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
echo    Build termine avec succes !
echo  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
echo.
echo  Application   : dist\BeatCash\BeatCash.exe
echo  Dossier complet : dist\BeatCash\
echo.
echo  ─────────────────────────────────────────────
echo  Pour creer un vrai installateur Windows (.exe)
echo  ─────────────────────────────────────────────
echo  1. Telecharge Inno Setup (gratuit) :
echo     https://jrsoftware.org/isdl.php
echo  2. Ouvre  setup.iss  avec Inno Setup Compiler
echo  3. Menu : Build  ^>  Compile   (F9)
echo  4. Resultat : dist_installer\BeatCash_Setup.exe
echo.
echo  Tu peux distribuer BeatCash_Setup.exe comme
echo  n'importe quelle application professionnelle !
echo.
pause
