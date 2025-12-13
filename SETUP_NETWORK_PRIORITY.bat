@echo off
echo.
echo ==========================================
echo   EQ12 Network Priority Configuration
echo ==========================================
echo.
echo This script will configure:
echo - Hardwired ethernet as PRIMARY internet
echo - Wi-Fi as BACKUP internet  
echo - USB-to-Ethernet Pi connection
echo.
echo You will be prompted for Administrator privileges.
echo.
pause

echo.
echo Launching PowerShell as Administrator...
PowerShell -Command "Start-Process PowerShell -Verb RunAs -ArgumentList '-ExecutionPolicy Bypass -File C:\EQ12\scripts\eq12_network_priority_setup.ps1 -VerboseOutput'"

echo.
echo Network configuration launched!
echo Check the Administrator PowerShell window for progress.
echo.
pause