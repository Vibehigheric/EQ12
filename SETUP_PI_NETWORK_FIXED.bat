@echo off
echo ===========================================
echo EQ12 USB Ethernet Adapter Configuration
echo ===========================================
echo.
echo This script will:
echo 1. Disable DHCP on USB Ethernet adapter
echo 2. Configure static IP (192.168.100.1/24)
echo 3. Test Pi connectivity
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [Step 1] Disabling DHCP on Ethernet 3...
powershell -Command "Set-NetIPInterface -InterfaceAlias 'Ethernet 3' -Dhcp Disabled -ErrorAction SilentlyContinue"

echo [Step 2] Removing existing IP configuration...
powershell -Command "Remove-NetIPAddress -InterfaceAlias 'Ethernet 3' -Confirm:$false -ErrorAction SilentlyContinue"
powershell -Command "Remove-NetRoute -InterfaceAlias 'Ethernet 3' -Confirm:$false -ErrorAction SilentlyContinue"

echo [Step 3] Configuring static IP (192.168.100.1/24)...
powershell -Command "New-NetIPAddress -InterfaceAlias 'Ethernet 3' -IPAddress '192.168.100.1' -PrefixLength 24 -ErrorAction Stop"

if %errorlevel% equ 0 (
    echo [SUCCESS] Static IP configured successfully!
) else (
    echo [ERROR] Failed to configure static IP
    echo Trying alternative method...
    netsh interface ip set address "Ethernet 3" static 192.168.100.1 255.255.255.0
)

echo [Step 4] Enabling adapter...
powershell -Command "Enable-NetAdapter -Name 'Ethernet 3' -ErrorAction SilentlyContinue"

echo [Step 5] Waiting for adapter to initialize...
timeout /t 3 /nobreak >nul

echo [Step 6] Testing configuration...
powershell -Command "Get-NetIPAddress -InterfaceAlias 'Ethernet 3' -AddressFamily IPv4 | Format-Table IPAddress, PrefixLength"

echo [Step 7] Testing Pi connectivity...
ping -n 3 192.168.100.2

echo.
echo ===========================================
echo Configuration Complete!
echo ===========================================
echo.
echo Host IP: 192.168.100.1/24
echo Expected Pi IP: 192.168.100.2/24
echo.
echo If Pi doesn't respond to ping:
echo 1. Ensure Pi is connected via ethernet cable to USB adapter
echo 2. Configure Pi network settings (see PI_ETHERNET_SETUP_INSTRUCTIONS.md)
echo 3. Reboot Pi after network configuration
echo.
echo Next steps:
echo - Test: C:\EQ12\scripts\eq12_pi_connectivity_test.ps1
echo - Add to cluster: python eq12_raspberry_pi_cluster_manager.py --add-node 192.168.100.2
echo.
pause