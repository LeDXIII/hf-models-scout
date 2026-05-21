@echo off
chcp 65001 >nul
echo ============================================
echo  1. HF Models Scout - Быстрый скан (7 дней)
echo ============================================
echo.
hf-scout --days 7 --top-per-category 10 --min-likes 5 --min-downloads 50
echo.
pause
