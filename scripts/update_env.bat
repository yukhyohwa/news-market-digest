@echo off
chcp 65001 > nul
cd /d "%~dp0.."

echo "==========================================="
echo "=== Updating Project Dependencies       ==="
echo "==========================================="
echo.

:: Define the python command to use
set PYTHON_EXE=python
if exist "C:\ProgramData\miniconda3\python.exe" (
    set PYTHON_EXE="C:\ProgramData\miniconda3\python.exe"
)

echo Using Python: %PYTHON_EXE%
%PYTHON_EXE% --version

echo.
echo Upgrading pip...
%PYTHON_EXE% -m pip install --upgrade pip

echo.
echo Installing requirements...
%PYTHON_EXE% -m pip install -r requirements.txt

echo.
echo Checking deep-translator...
%PYTHON_EXE% -m pip list | findstr "deep-translator"

echo.
echo "Update completed."
pause
