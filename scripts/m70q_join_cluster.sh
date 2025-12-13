#!/bin/bash
# EQ12 Cluster Join Script (Run on M70q)
# Forces the M70q to join the 192.168.100.x Cluster Network

# Configuration
INTERFACE="eno1"  # Change if your interface is different (e.g., eth0)
NEW_IP="192.168.100.3"
NETMASK="24"
GATEWAY="192.168.100.1"
TARGET_DESKTOP="192.168.100.2"

echo -e "\033[1;36m🚀 EQ12 Cluster Join Tool\033[0m"
echo "---------------------------------"
echo "Current IP:"
ip -4 addr show $INTERFACE | grep inet

echo -e "\n\033[1;33m1. Releasing old IP (Home Network)...\033[0m"
sudo ip addr flush dev $INTERFACE

echo -e "\n\033[1;33m2. Assigning Cluster IP ($NEW_IP)...\033[0m"
sudo ip addr add $NEW_IP/$NETMASK dev $INTERFACE

echo -e "\n\033[1;33m3. Setting Gateway ($GATEWAY)...\033[0m"
sudo ip route add default via $GATEWAY dev $INTERFACE

echo -e "\n\033[1;33m4. Verifying Connectivity...\033[0m"
echo "Pinging Gateway..."
if ping -c 3 $GATEWAY &> /dev/null; then
    echo -e "\033[0;32m✅ Gateway Reachable!\033[0m"
else
    echo -e "\033[0;31m❌ Gateway Unreachable. (Check cable/switch)\033[0m"
fi

echo "Pinging Desktop ($TARGET_DESKTOP)..."
if ping -c 3 $TARGET_DESKTOP &> /dev/null; then
    echo -e "\033[0;32m✅ Desktop Reachable! Cluster Link Established.\033[0m"
else
    echo -e "\033[0;31m❌ Desktop Unreachable. (Check Desktop Firewall)\033[0m"
fi

echo -e "\n\033[1;35m⚠️  NOTE: This change is temporary (until reboot).\033[0m"
echo "To make it permanent, edit /etc/netplan/00-installer-config.yaml"
