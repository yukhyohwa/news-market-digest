@echo off
chcp 65001 > nul
cd /d "%~dp0.."

echo ===========================================
echo === Market Digest: Manual Run           ===
echo ===========================================
echo.

:: Prefer the known Python installation, then use PATH as a fallback.
if exist "C:\ProgramData\miniconda3\python.exe" (
    "C:\ProgramData\miniconda3\python.exe" main.py --mail
) else (
    python main.py --mail
)

if errorlevel 1 (
    echo.
    echo [FAILED] Market Digest exited with code %errorlevel%.
    pause
    exit /b %errorlevel%
)

echo.
echo Process completed at %date% %time%
pause
