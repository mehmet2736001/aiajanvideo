@echo off
chcp 65001 > nul
title Notebook Video AI - Sunucuyu Durdur
cd /d "%~dp0"

echo ============================================================
echo        🛑 NOTEBOOK VIDEO AI - SUNUCUYU DURDURMA ARACI
echo ============================================================
echo.

echo [*] Port 8080 üzerindeki işlemler aranıyor...
set FOUND=0
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo [*] Port 8080 kullanan işlem sonlandırılıyor (PID: %%a)...
    taskkill /f /pid %%a >nul 2>&1
    set FOUND=1
)

if "%FOUND%"=="1" (
    echo.
    echo [✓] Sunucu başarıyla durduruldu ve port 8080 serbest bırakıldı.
) else (
    echo.
    echo [*] Port 8080 üzerinde çalışan aktif bir sunucu bulunamadı.
)

echo.
timeout /t 3
