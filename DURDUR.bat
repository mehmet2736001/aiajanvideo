@echo off
chcp 65001 > nul
title Notebook Video AI - Sunucuyu Durdur
cd /d "%~dp0"

echo ============================================================
echo        NOTEBOOK VIDEO AI - SUNUCUYU DURDURMA ARACI
echo ============================================================
echo.

echo [*] Port 8080 uzerindeki islemler araniyor...
set FOUND=0
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo [*] Port 8080 kullanan islem sonlandiriliyor - PID: %%a
    taskkill /f /pid %%a >nul 2>&1
    set FOUND=1
)

if "%FOUND%"=="1" (
    echo.
    echo [OK] Sunucu basariyla durduruldu ve port 8080 serbest birakildi.
) else (
    echo.
    echo [*] Port 8080 uzerinde calisan aktif bir sunucu bulunamadi.
)

echo.
ping 127.0.0.1 -n 3 >nul
