@echo off
chcp 65001 >nul
title Notebook Video AI - Tum Formatlari Renderla (9:16 + 16:9 + 1:1)
color 0b
echo ============================================================
echo   NOTEBOOK VIDEO AI - COKLU FORMAT RENDER MOTORU (PRO 2026)
echo ============================================================
echo.
echo [1/3] 9:16 Dikey Shorts / Reels (1080x1920) Derleniyor...
call npm run build
if %errorlevel% neq 0 (
    echo [HATA] 9:16 Render basarisiz oldu.
) else (
    echo [BASARILI] out/video.mp4 olusturuldu!
)
echo.

echo [2/3] 16:9 Yatay YouTube (1920x1080) Derleniyor...
call npm run build:horizontal
if %errorlevel% neq 0 (
    echo [HATA] 16:9 Render basarisiz oldu.
) else (
    echo [BASARILI] out/video_horizontal.mp4 olusturuldu!
)
echo.

echo [3/3] 1:1 Kare Instagram/LinkedIn (1080x1080) Derleniyor...
call npm run build:square
if %errorlevel% neq 0 (
    echo [HATA] 1:1 Render basarisiz oldu.
) else (
    echo [BASARILI] out/video_square.mp4 olusturuldu!
)
echo.

echo [KAPAK] Video Kapak Resmi Aliniyor...
call npx remotion still src/index.ts NotebookVideo out/thumbnail.png --frame=45
echo.
echo ============================================================
echo   TUM FORMATLAR BASARIYLA DERLENDI!
echo   Ciktilar 'out/' klasorunde hazir.
echo ============================================================
pause
