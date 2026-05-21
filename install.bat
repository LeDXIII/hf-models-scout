@echo off
chcp 65001 >nul
echo ============================================
echo  HF Models Scout - Установка
echo ============================================
echo.
echo [1/2] Обновление pip...
python -m pip install --upgrade pip
echo.
echo [2/2] Установка зависимостей проекта...
pip install -e .
echo.
echo Готово! Запустите quick-scan.bat для тестового скана.
echo.
pause
