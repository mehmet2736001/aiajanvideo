@echo off
chcp 65001 > nul
title Notebook Video AI Studio Pro 4.0
cd /d "%~dp0"

echo ============================================================
echo        NOTEBOOK VIDEO AI STUDIO PRO 4.0 TITANIUM
echo                  Yerel Baslatici Servisi
echo ============================================================
echo.

:: 1. Python Kontrolu
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python sisteminizde bulunamadi veya PATH ortamina eklenmemis!
    echo Lutfen Python kurunuz: https://www.python.org/
    echo.
    pause
    exit /b 1
)

:: 2. Node.js Kontrolu
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Node.js sisteminizde bulunamadi! Remotion render icin gereklidir.
    echo Lutfen Node.js LTS kurunuz: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

:: 3. Port 8080 Kontrolu ve Temizleme
echo [*] Sistem ve port durumu kontrol ediliyor (Port 8080)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo [*] Port 8080 uzerindeki eski islem kapatiliyor - PID: %%a
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo [*] Sunucu baslatiliyor: http://127.0.0.1:8080
echo [*] 2 saniye icinde varsayilan tarayiciniz otomatik acilacak...
echo.

:: 4. Tarayiciyi Ac
start "" powershell -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8080'"

:: 5. Python Sunucusunu Baslat
python server.py

echo.
echo [*] Sunucu durduruldu.
pause
