@echo off
chcp 65001 >nul
echo ============================================
echo  3. HF Models Scout - Глубокий скан (90 дней)
echo ============================================
echo.
hf-scout --days 90 --top-per-category 50 --min-likes 10 --min-downloads 100
echo.
pause
