@echo off
echo EQ12 Pi USB Ethernet Configuration
echo ===================================

echo Configuring USB Ethernet adapter for Pi communication...

REM Configure Ethernet 3 (USB adapter) with static IP
powershell -Command "Remove-NetIPAddress -InterfaceAlias 'Ethernet 3' -Confirm:$false -ErrorAction SilentlyContinue"
powershell -Command "New-NetIPAddress -InterfaceAlias 'Ethernet 3' -IPAddress '192.168.100.1' -PrefixLength 24"

echo.
echo Testing Pi connectivity...
ping -n 3 192.168.100.2

echo.
echo Configuration complete!
echo Host IP: 192.168.100.1
echo Pi IP: 192.168.100.2 (expected)
echo.
echo If Pi doesn't respond:
echo 1. Check Pi network configuration (/etc/dhcpcd.conf)
echo 2. Ensure Pi ethernet is connected to USB adapter
echo 3. Run: python eq12_raspberry_pi_cluster_manager.py --discover
echo.
pause