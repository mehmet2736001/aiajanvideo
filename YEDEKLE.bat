@echo off
chcp 65001 >nul
title Notebook Video AI - GitHub Anlık Yedekleyici
color 0b

echo ========================================================
echo    🚀 NOTEBOOK VIDEO AI - GITHUB ANLIK YEDEKLEME
echo ========================================================
echo.

cd /d "E:\aivideoyap"

:: 1. Git kurulu mu kontrol et
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [HATA] Sisteminizde Git yuklu degil veya PATH'e eklenmemis.
    echo Lutfen https://git-scm.com/ adresinden Git'i yukleyin.
    pause
    exit /b 1
)

:: 2. Git repo başlatılmış mı
if not exist ".git" (
    echo [*] Git deposu baslatiliyor...
    git init
    git branch -M main
)

:: 3. Remote Origin kontrolü
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Henuz bir GitHub deposu baglanmamis.
    echo.
    echo GitHub'da olusturdugunuz deponun linkini yapistirin:
    echo (Ornek: https://github.com/kullaniciadi/proje-adi.git)
    echo.
    set /p REPO_URL="GitHub Repo URL: "
    if not "%REPO_URL%"=="" (
        git remote add origin %REPO_URL%
        echo [OK] GitHub deposu baglandi: %REPO_URL%
    ) else (
        echo [UYARI] URL girilmedi. Sadece yerel commit aliniyor...
    )
)

echo.
echo [*] Degisiklikler taranıyor ve paketleniyor...
git add .

:: 4. Commit Açıklaması
echo.
set "TIMESTAMP=%date:~6,4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%"
echo Varsayilan Aciklama: "Yedekleme: %TIMESTAMP%"
echo Farkli bir not yazmak isterseniz yazip Enter'a basin (veya bos birakin):
set /p USER_MSG="Yedekleme Notu: "

if "%USER_MSG%"=="" (
    set "COMMIT_MSG=Yedekleme: %TIMESTAMP%"
) else (
    set "COMMIT_MSG=%USER_MSG% (%TIMESTAMP%)"
)

git commit -m "%COMMIT_MSG%"

echo.
echo [*] GitHub'a gonderiliyor (git push origin main)...
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo    ✅ YEDEKLEME BASARIYLA TAMAMLANDI!
    echo    Son Surum: %COMMIT_MSG%
    echo ========================================================
) else (
    echo.
    echo [!] Push sirasinda bir uyari veya yetkilendirme istegi olustu.
    echo Eger ilk defa push yapiyorsaniz, GitHub oturum acma penceresi acilmis olabilir.
    echo Ayrica GitHub'da 'Personal Access Token' gerekebilir.
)

echo.
pause
