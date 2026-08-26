@echo off
chcp 65001 > nul
cd /d "%~dp0.."
if not exist output mkdir output

echo [%date% %time%] Starting Automated Market Digest...

:: Prefer the known Python installation, then use PATH as a fallback.
if exist "C:\ProgramData\miniconda3\python.exe" (
    "C:\ProgramData\miniconda3\python.exe" main.py --mail >> output\task_scheduler_log.txt 2>&1
) else (
    python main.py --mail >> output\task_scheduler_log.txt 2>&1
)

set "TASK_EXIT_CODE=%errorlevel%"
if not "%TASK_EXIT_CODE%"=="0" (
    echo [%date% %time%] Task failed with exit code %TASK_EXIT_CODE%.>> output\task_scheduler_log.txt
) else (
    echo [%date% %time%] Task completed successfully.>> output\task_scheduler_log.txt
)
exit /b %TASK_EXIT_CODE%
