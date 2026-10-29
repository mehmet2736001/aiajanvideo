@echo off
chcp 65001 > nul
title Notebook Video AI Studio Pro 4.0
cd /d "%~dp0"

echo ============================================================
echo        🎬 NOTEBOOK VIDEO AI STUDIO PRO 4.0 TITANIUM
echo                  Yerel Başlatıcı Servisi
echo ============================================================
echo.

:: 1. Python Kontrolü
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python sisteminizde bulunamadı veya PATH ortam değişkenine eklenmemiş!
    echo Lütfen Python 3.10 veya 3.11 kurunuz: https://www.python.org/
    echo.
    pause
    exit /b
)

:: 2. Node.js Kontrolü
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Node.js sisteminizde bulunamadı! Remotion video render için gereklidir.
    echo Lütfen Node.js LTS sürümünü kurunuz: https://nodejs.org/
    echo.
    pause
    exit /b
)

:: 3. Port 8080 Kontrolü ve Temizleme (Eski kilitli işlem varsa kapat)
echo [*] Sistem ve port durumu kontrol ediliyor (Port 8080)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do (
    echo [*] Port 8080 üzerinde çalışan önceki işlem kapatılıyor (PID: %%a)...
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo [*] Sunucu başlatılıyor: http://127.0.0.1:8080
echo [*] 2 saniye içinde varsayılan tarayıcınız otomatik açılacak...
echo.

:: 4. Tarayıcıyı Arka Planda Aç
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8080"

:: 5. Python Sunucusunu Başlat
python server.py

echo.
echo [*] Sunucu durduruldu.
pause
