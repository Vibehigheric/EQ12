#!/bin/bash
# EQ12 Linux Network Repair Tool (Run on M70q/Ubuntu)

echo -e "\033[0;36m🔧 EQ12 Linux Network Diagnostic Tool\033[0m"
echo "---------------------------------------"

# 1. Check Interface Status
echo -e "\n\033[1;33m1. Checking Network Interfaces...\033[0m"
ip link show

# 2. Check IP Address
echo -e "\n\033[1;33m2. Checking IP Address...\033[0m"
ip addr show | grep "inet " | grep -v "127.0.0.1"

# 3. Restart Network Manager (Common fix)
echo -e "\n\033[1;33m3. Refreshing Network Connection...\033[0m"
if command -v nmcli &> /dev/null; then
    echo "Restarting NetworkManager..."
    sudo systemctl restart NetworkManager
    sleep 5
else
    echo "NetworkManager not found, trying dhclient..."
    sudo dhclient -r
    sudo dhclient -v
fi

# 4. Test Connectivity
echo -e "\n\033[1;33m4. Testing Connectivity...\033[0m"
GATEWAY="192.168.100.1"
echo "Pinging Gateway ($GATEWAY)..."
if ping -c 3 $GATEWAY &> /dev/null; then
    echo -e "\033[0;32m✅ Gateway is REACHABLE!\033[0m"
else
    echo -e "\033[0;31m❌ Gateway is UNREACHABLE.\033[0m"
    echo "👉 Check Ethernet cable and Switch power."
fi

echo -e "\n\033[1;33m5. Testing Internet (Google DNS)...\033[0m"
if ping -c 3 8.8.8.8 &> /dev/null; then
    echo -e "\033[0;32m✅ Internet is REACHABLE!\033[0m"
else
    echo -e "\033[0;31m❌ Internet is UNREACHABLE.\033[0m"
fi

echo -e "\nDone."
