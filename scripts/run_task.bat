@echo off
chcp 65001 > nul
cd /d "%~dp0.."
if not exist output mkdir output

echo [%date% %time%] Starting Automated News Market Digest...

:: Try to use the full path to the python version we know works
if exist "C:\ProgramData\miniconda3\python.exe" (
    "C:\ProgramData\miniconda3\python.exe" main.py --all --mail >> output\task_scheduler_log.txt 2>&1
) else (
    python main.py --all --mail >> output\task_scheduler_log.txt 2>&1
)

echo [%date% %time%] Task Completed.
exit
