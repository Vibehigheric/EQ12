@echo off
REM EQ12 Buffalo Stack Combo Runner
REM Batch wrapper for eq12_godmode_runner_plus.py
REM This allows Task Scheduler to run the Python script reliably

setlocal EnableDelayedExpansion

REM Set base paths
set BASE_DIR=C:\EQ12\buffalo_stack
set LOG_DIR=%BASE_DIR%\logs
set PYTHON_SCRIPT=%BASE_DIR%\eq12_godmode_runner_plus.py

REM Create logs directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Set log file with timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%-%MM%-%DD%_%HH%-%Min%-%Sec%"

set BATCH_LOG=%LOG_DIR%\eq12_combo_%timestamp%.log

REM Change to base directory
cd /d "%BASE_DIR%"

echo [%date% %time%] EQ12 Buffalo Stack Combo Runner Started >> "%BATCH_LOG%"
echo [%date% %time%] Base Directory: %BASE_DIR% >> "%BATCH_LOG%"
echo [%date% %time%] Python Script: %PYTHON_SCRIPT% >> "%BATCH_LOG%"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [%date% %time%] ERROR: Python not found in PATH >> "%BATCH_LOG%"
    echo Python not found. Please ensure Python is installed and in your PATH.
    exit /b 1
)

REM Check if script exists
if not exist "%PYTHON_SCRIPT%" (
    echo [%date% %time%] ERROR: Script not found: %PYTHON_SCRIPT% >> "%BATCH_LOG%"
    echo Script not found: %PYTHON_SCRIPT%
    exit /b 1
)

REM Load environment variables from .env file if it exists
if exist "%BASE_DIR%\.env" (
    echo [%date% %time%] Loading environment from .env file >> "%BATCH_LOG%"
    for /f "usebackq tokens=1,2 delims==" %%i in ("%BASE_DIR%\.env") do (
        if "%%i" neq "" if "%%j" neq "" (
            set "%%i=%%j"
        )
    )
)

REM Run the Python script with appropriate arguments for automated execution
echo [%date% %time%] Executing Python script with --skip-api-prompts flag >> "%BATCH_LOG%"

python "%PYTHON_SCRIPT%" --skip-api-prompts >> "%BATCH_LOG%" 2>&1

set EXIT_CODE=%errorlevel%
echo [%date% %time%] Python script completed with exit code: %EXIT_CODE% >> "%BATCH_LOG%"

if %EXIT_CODE% equ 0 (
    echo [%date% %time%] EQ12 Buffalo Stack Combo Runner completed successfully >> "%BATCH_LOG%"
) else (
    echo [%date% %time%] EQ12 Buffalo Stack Combo Runner failed with code %EXIT_CODE% >> "%BATCH_LOG%"
)

REM Keep the last 10 log files to prevent disk space issues
for /f "skip=10 delims=" %%F in ('dir "%LOG_DIR%\eq12_combo_*.log" /b /o:-d 2^>nul') do (
    echo [%date% %time%] Cleaning old log: %%F >> "%BATCH_LOG%"
    del "%LOG_DIR%\%%F" >nul 2>&1
)

echo [%date% %time%] EQ12 Buffalo Stack Combo Runner batch script finished >> "%BATCH_LOG%"
exit /b %EXIT_CODE%