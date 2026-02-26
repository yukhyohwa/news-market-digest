@echo off
:: Set character set to UTF-8
chcp 65001 > nul

:: Move to project directory
cd /d "%~dp0.."

:: Ensure output directory exists (optional but safe)
if not exist output mkdir output

echo [%date% %time%] Starting Automated News & Market Digest...

:: Run program with arguments and log output
:: --all: Run News + Market 
:: --mail: Send email report
python main.py --all --mail >> output\task_scheduler_log.txt 2>&1

echo [%date% %time%] Task Completed.
exit
