@echo off
chcp 65001 > nul
cd /d "%~dp0.."
echo ===========================================
echo === News & Market Digest: Manual Run    ===
echo ===========================================
echo.
python main.py --all --mail
echo.
echo Process completed at %date% %time%
pause
