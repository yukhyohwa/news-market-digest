@echo off
chcp 65001 > nul
cd /d "%~dp0.."

echo ===========================================
echo === News Market Digest: Manual Run      ===
echo ===========================================
echo.

:: Try to use the full path to the python version we know works
if exist "C:\ProgramData\miniconda3\python.exe" (
    "C:\ProgramData\miniconda3\python.exe" main.py --all --mail
) else (
    python main.py --all --mail
)

echo.
echo Process completed at %date% %time%
pause
