@echo off
chcp 65001 >nul
echo ============================================
echo  2. HF Models Scout - Полный скан (30 дней)
echo ============================================
echo.
hf-scout --days 30 --top-per-category 30 --min-likes 3 --min-downloads 30
echo.
pause
