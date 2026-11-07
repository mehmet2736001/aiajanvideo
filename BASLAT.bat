@echo off
chcp 65001 > nul
title Nexus AI Video Studio
cd /d "%~dp0"

:menu
cls
echo ============================================================
echo      NEXUS AI VIDEO STUDIO
echo ============================================================
echo.
echo   [1] Web Studyo Panelini Baslat  (http://127.0.0.1:8000)
echo   [2] Remotion Canli Onizleme     (npm start)
echo   [3] Kurulum: Python + Node bagimliliklarini yukle
echo   [4] Testleri calistir
echo   [5] Cikis
echo.
set /p secim=Seciminiz (1-5): 

if "%secim%"=="1" goto studio
if "%secim%"=="2" goto preview
if "%secim%"=="3" goto kurulum
if "%secim%"=="4" goto test
if "%secim%"=="5" exit /b 0
goto menu

:studio
where python >nul 2>nul || (echo [HATA] Python bulunamadi. https://www.python.org adresinden kurun. & pause & goto menu)
where ffmpeg >nul 2>nul || echo [UYARI] ffmpeg PATH'te degil; ses ve render adimlari calismaz.
if not exist node_modules echo [UYARI] node_modules yok; once [3] ile kurulum yapin.
echo.
echo Sunucu baslatiliyor... Durdurmak icin Ctrl+C
start "" powershell -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:8000'"
python -m web.server
pause
goto menu

:preview
call npm start
pause
goto menu

:kurulum
python -m pip install -r requirements.txt
call npm install
echo.
echo Kurulum tamam. ffmpeg'in kurulu ve PATH'te oldugundan emin olun.
pause
goto menu

:test
python -m pip install -q -r requirements-dev.txt
python -m pytest -q
call npm run typecheck
pause
goto menu
