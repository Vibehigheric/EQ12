#!/bin/bash
# EQ12 M70q Network Diagnostic & Fix Tool
# Based on the analysis provided.

LOG_FILE="network_fix.log"
exec > >(tee -a $LOG_FILE) 2>&1

echo -e "\033[1;36m🔧 EQ12 M70q Network Fixer\033[0m"
echo "========================================"

# 1. Check Physical Link
echo -e "\n\033[1;33m1. Checking Physical Link (ethtool)...\033[0m"
if command -v ethtool &> /dev/null; then
    sudo ethtool eno1 | grep -E "Speed|Duplex|Link detected"
else
    echo "ethtool not installed. Checking carrier state:"
    cat /sys/class/net/eno1/carrier 2>/dev/null && echo "Carrier: Detected" || echo "Carrier: Not Detected"
fi

# 2. Check Routing Table
echo -e "\n\033[1;33m2. Checking Routing Table...\033[0m"
ip route show
if ! ip route | grep -q "default via"; then
    echo -e "\033[0;31m❌ NO DEFAULT GATEWAY FOUND!\033[0m"
    echo "Attempting to add default gateway (192.168.1.1)..."
    sudo ip route add default via 192.168.1.1 dev eno1
else
    echo -e "\033[0;32m✅ Default gateway exists.\033[0m"
fi

# 3. Test Gateway Connectivity
echo -e "\n\033[1;33m3. Pinging Gateway (192.168.1.1)...\033[0m"
if ping -c 4 192.168.1.1; then
    echo -e "\033[0;32m✅ Gateway Reachable!\033[0m"
else
    echo -e "\033[0;31m❌ Gateway Unreachable.\033[0m"
    echo "⚠️  Possible causes: Bad cable, VLAN mismatch, or IP conflict."
fi

# 4. Restart Networking
echo -e "\n\033[1;33m4. Restarting Network Stack...\033[0m"
if command -v nmcli &> /dev/null; then
    sudo systemctl restart NetworkManager
    echo "NetworkManager restarted."
else
    echo "Restarting networking service..."
    sudo systemctl restart networking
fi

# 5. Renew DHCP
echo -e "\n\033[1;33m5. Renewing IP Address...\033[0m"
sudo dhclient -r eno1
sudo dhclient -v eno1

# 6. CLUSTER CHECK (The Real Fix?)
echo -e "\n\033[1;35m6. EQ12 Cluster Check\033[0m"
echo "Your Desktop is on 192.168.100.x (The Cluster Network)."
echo "This M70q is on 192.168.1.x (The Home Network)."
echo "---------------------------------------------------"
echo "❓ Should this device be on the Cluster Network (192.168.100.x)?"
echo "   If yes, run this command to set a static IP:"
echo "   sudo ip addr add 192.168.100.3/24 dev eno1"
echo "========================================"
