@echo off
chcp 65001 > nul
title Nexus AI Video Studio
cd /d "%~dp0"

echo ============================================================
echo      NEXUS AI VIDEO STUDIO — OTONOM HUKUMET BASLATILIYOR
echo ============================================================
echo.
echo [*] Stüdyo hazırlanıyor...
echo [*] Tarayıcınız açılıyor: http://127.0.0.1:8000
echo.

:: 2 saniye sonra varsayılan tarayıcıda doğrudan 127.0.0.1:8000 adresini aç
start "" powershell -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000'"

:: Sunucuyu 127.0.0.1 üzerinde başlat
python -m web.server
