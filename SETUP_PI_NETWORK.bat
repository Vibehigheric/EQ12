@echo off
echo.
echo ==========================================
echo   EQ12 Pi Network Configuration
echo ==========================================
echo.
echo This script will configure direct Ethernet networking
echo between your EQ12 system and Raspberry Pi.
echo.
echo You will be prompted for Administrator privileges.
echo.
pause

echo.
echo Launching PowerShell as Administrator...
PowerShell -Command "Start-Process PowerShell -Verb RunAs -ArgumentList '-ExecutionPolicy Bypass -File C:\EQ12\scripts\eq12_direct_ethernet_setup.ps1 -EnableICS -VerboseOutput'"

echo.
echo Configuration launched!
echo Check the Administrator PowerShell window for progress.
echo.
pause