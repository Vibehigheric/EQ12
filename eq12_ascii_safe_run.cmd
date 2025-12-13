@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ================================================================
echo EQ12 ASCII-SAFE COMMAND WRAPPER v2.0 - CORRUPTION IMMUNE
echo ================================================================

REM Force working directory and validate
cd /d C:\EQ12
if not exist "C:\EQ12" (
    echo ERROR: EQ12 directory not found
    exit /b 1
)

REM Set ASCII-safe environment
set PYTHONUTF8=1
set PYTHONIOENCODING=ascii
set LC_ALL=C
set LANG=C

REM Force UTF-8 codepage for Windows console
chcp 65001 >nul 2>&1

REM Clean PATH to prevent conflicts
set PATH=C:\Program Files\Python312;C:\Program Files\Python312\Scripts;C:\EQ12\scripts;%SystemRoot%\System32;%SystemRoot%

REM Find Python executable
set PYTHON_EXE=python
if exist "C:\Program Files\Python312\python.exe" (
    set PYTHON_EXE="C:\Program Files\Python312\python.exe"
)

REM Create log directory and filename
set LOGDIR=C:\EQ12\logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM Safe timestamp for filename
for /f "tokens=1-3 delims=/" %%a in ("%date%") do set DATE_SAFE=%%c%%a%%b
for /f "tokens=1-3 delims=:." %%a in ("%time%") do set TIME_SAFE=%%a%%b%%c
set TIME_SAFE=%TIME_SAFE: =0%
set LOGFILE=%LOGDIR%\safe_run_%DATE_SAFE%_%TIME_SAFE%.log

echo Command: %*
echo Python: %PYTHON_EXE%
echo Working Directory: %CD%
echo Log File: %LOGFILE%
echo.

REM Execute command with full error capture
%PYTHON_EXE% %* 1>>"%LOGFILE%" 2>&1
set RESULT=%ERRORLEVEL%

REM Display results
if %RESULT% EQU 0 (
    echo SUCCESS: Command completed successfully
    echo Output logged to: %LOGFILE%
) else (
    echo ERROR: Command failed with exit code %RESULT%
    echo.
    echo Last 5 lines from log:
    echo ----------------------------------------
    powershell -NoProfile -Command "if (Test-Path '%LOGFILE%') { Get-Content '%LOGFILE%' | Select-Object -Last 5 | ForEach-Object { Write-Host $_ } }"
    echo ----------------------------------------
)

exit /b %RESULT%
