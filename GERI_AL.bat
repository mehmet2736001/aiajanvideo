@echo off
chcp 65001 >nul
title Notebook Video AI - Eski Sürüme Geri Dön (Rollback)
color 0e

echo ========================================================
echo    ⏪ NOTEBOOK VIDEO AI - GERİ ALMA VE SÜRÜM YÖNETİCİSİ
echo ========================================================
echo.

cd /d "E:\aivideoyap"

if not exist ".git" (
    echo [HATA] Bu klasorde bir Git deposu bulunamadi.
    pause
    exit /b 1
)

echo [*] Son 10 Yedekleme Noktasi (Commitler):
echo --------------------------------------------------------
git log --graph --oneline --decorate -n 10
echo --------------------------------------------------------
echo.
echo Ne yapmak istiyorsunuz?
echo.
echo [1] Bir onceki yedeklemeye guvenli sekilde geri don (Undo son islem)
echo [2] Belirli bir commit ID'sine geri don (ID yazarak)
echo [3] En son guncel surume geri don (main branch)
echo [4] Cikis
echo.

set /p CHOICE="Seciminiz [1, 2, 3, 4]: "

if "%CHOICE%"=="1" (
    echo.
    echo [*] Son yapilan degisiklik geri aliniyor...
    git revert HEAD --no-edit
    echo [OK] Son yapilan islem basariyla geri alindi!
)

if "%CHOICE%"=="2" (
    echo.
    set /p COMMIT_ID="Donmek istediginiz 7 haneli Commit ID (ornek: 535a88d): "
    if not "%COMMIT_ID%"=="" (
        echo.
        echo [*] %COMMIT_ID% noktasina geri donuluyor...
        git checkout %COMMIT_ID%
        echo.
        echo [OK] Kodlar %COMMIT_ID% surumune cekildi.
        echo Yeniden en guncel koda donmek icin bu scripti acip 3'e basin.
    )
)

if "%CHOICE%"=="3" (
    echo.
    echo [*] En son ana surume (main) donuluyor...
    git checkout main
    echo [OK] main dali aktif edildi.
)

echo.
pause
