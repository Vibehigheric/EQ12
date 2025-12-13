@echo off
setlocal ENABLEDELAYEDEXPANSION

echo ===============================================
echo EQ12 SAFE-RUN WRAPPER v1.0  (CMD Protected Mode)
echo ===============================================

REM ---- Force working directory ----
cd /d C:\EQ12

REM ---- Force Python 3.12 ----
set PYTHON_EXE=python
if exist "C:\Program Files\Python312\python.exe" (
    set PYTHON_EXE=C:\Program Files\Python312\python.exe
)

REM ---- Ensure UTF-8 everywhere ----
set PYTHONUTF8=1
set PYTHONIOENCODING=UTF-8
chcp 65001 >nul 2>&1

REM ---- Sanitize PATH ----
set PATH=C:\Program Files\Python312;C:\Program Files\Python312\Scripts;C:\EQ12\scripts;%PATH%

REM ---- Log directory ----
set LOGDIR=C:\EQ12\logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM ---- Create safe log filename ----
set TIMESTAMP=%DATE%_%TIME%
set TIMESTAMP=%TIMESTAMP::=-%
set TIMESTAMP=%TIMESTAMP:/=-%
set TIMESTAMP=%TIMESTAMP:.=-%
set TIMESTAMP=%TIMESTAMP: =_%
set LOGFILE=%LOGDIR%\safe_run_%TIMESTAMP%.log

echo Running command: %*
echo Timestamp: %DATE% %TIME%
echo Working Directory: %CD%
echo Python: %PYTHON_EXE%
echo Log: %LOGFILE%
echo.

REM ---- Execute command safely ----
"%PYTHON_EXE%" %* 1>>"%LOGFILE%" 2>&1
set RESULT=%ERRORLEVEL%

if %RESULT% NEQ 0 (
    echo ERROR: Command failed with exit code %RESULT%
    echo See log file: %LOGFILE%
    echo.
    echo Last 10 lines of log:
    echo ----------------------------------------
    powershell -Command "Get-Content '%LOGFILE%' | Select-Object -Last 10"
    echo ----------------------------------------
    exit /b %RESULT%
)

echo SUCCESS: Command completed successfully
echo Log saved to: %LOGFILE%
exit /b 0
