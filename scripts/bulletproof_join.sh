#!/bin/bash
# 🛡️ EQ12 Bulletproof Cluster Join Script
# Target: Ubuntu M70q
# Goal: Switch from Home LAN (192.168.1.x) to Cluster LAN (192.168.100.x)

# --- CONFIGURATION ---
TARGET_IP="192.168.100.3"
GATEWAY="192.168.100.1"
MASTER_NODE="192.168.100.2" # Your Desktop
DNS_SERVER="8.8.8.8"
# ---------------------

echo -e "\033[1;36m🛡️  EQ12 Bulletproof Cluster Joiner\033[0m"
echo "======================================="

# 1. Auto-Detect Interface
echo -e "\n\033[1;33m1. Detecting Network Interface...\033[0m"
INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
if [ -z "$INTERFACE" ]; then
    # Fallback detection
    INTERFACE=$(ip link | grep 'state UP' | awk -F: '{print $2}' | tr -d ' ' | head -n1)
fi

if [ -z "$INTERFACE" ]; then
    echo -e "\033[0;31m❌ Could not detect active interface. Exiting.\033[0m"
    exit 1
fi
echo "✅ Detected Interface: $INTERFACE"

# 2. Backup Existing Netplan
echo -e "\n\033[1;33m2. Backing up Netplan...\033[0m"
sudo mkdir -p /etc/netplan/backup
sudo cp /etc/netplan/*.yaml /etc/netplan/backup/
echo "✅ Backup saved to /etc/netplan/backup/"

# 3. Create New Netplan Configuration
echo -e "\n\033[1;33m3. Writing Cluster Configuration...\033[0m"
cat <<EOF | sudo tee /etc/netplan/99-eq12-cluster.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      dhcp4: no
      addresses:
        - $TARGET_IP/24
      routes:
        - to: default
          via: $GATEWAY
      nameservers:
        addresses: [$DNS_SERVER, 1.1.1.1]
EOF
echo "✅ Configuration written to /etc/netplan/99-eq12-cluster.yaml"

# 4. Apply Changes
echo -e "\n\033[1;33m4. Applying Network Changes (This may disconnect SSH)...\033[0m"
# Remove conflicting configs if necessary (optional, safer to just override priority)
# sudo rm /etc/netplan/00-installer-config.yaml 2>/dev/null

sudo netplan apply
sleep 5

# 5. Verify Routing & IP
echo -e "\n\033[1;33m5. Verifying Configuration...\033[0m"
CURRENT_IP=$(ip addr show $INTERFACE | grep "inet " | awk '{print $2}')
echo "Current IP: $CURRENT_IP"

if [[ "$CURRENT_IP" == *"$TARGET_IP"* ]]; then
    echo -e "\033[0;32m✅ IP Address Assigned Correctly.\033[0m"
else
    echo -e "\033[0;31m❌ IP Address Mismatch. Expected $TARGET_IP\033[0m"
fi

# 6. Connectivity Check
echo -e "\n\033[1;33m6. Testing Connectivity...\033[0m"
echo "Pinging Gateway ($GATEWAY)..."
if ping -c 3 $GATEWAY &> /dev/null; then
    echo -e "\033[0;32m✅ Gateway Reachable.\033[0m"
else
    echo -e "\033[0;31m❌ Gateway Unreachable.\033[0m"
fi

echo "Pinging Master Node ($MASTER_NODE)..."
if ping -c 3 $MASTER_NODE &> /dev/null; then
    echo -e "\033[0;32m✅ Master Node Reachable! Cluster Joined.\033[0m"
else
    echo -e "\033[0;31m❌ Master Node Unreachable.\033[0m"
    echo "   (Check if Desktop Firewall allows ICMP/Ping)"
fi

echo -e "\n\033[1;36m🎉 Setup Complete.\033[0m"
