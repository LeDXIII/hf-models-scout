@echo off
chcp 65001 >nul
echo ============================================
echo  4. HF Models Scout - Тестовый скан (3 дня)
echo ============================================
echo.
hf-scout --days 3 --top-per-category 5 --min-likes 1 --min-downloads 10
echo.
pause
