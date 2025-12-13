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
echo "✅ New Netplan config written to /etc/netplan/99-eq12-cluster.yaml"

# 4. Disable NetworkManager for this interface (Optional but recommended for servers)
# echo -e "\n\033[1;33m4. Disabling NetworkManager for $INTERFACE...\033[0m"
# nmcli device set $INTERFACE managed no

# 5. Apply Netplan
echo -e "\n\033[1;33m5. Applying Netplan Configuration...\033[0m"
sudo netplan apply
if [ $? -eq 0 ]; then
    echo "✅ Netplan applied successfully."
else
    echo -e "\033[0;31m❌ Netplan apply failed. Restoring backup...\033[0m"
    sudo cp /etc/netplan/backup/*.yaml /etc/netplan/
    sudo netplan apply
    exit 1
fi

# 6. Verify Connectivity
echo -e "\n\033[1;33m6. Verifying Connectivity...\033[0m"
sleep 5
ping -c 3 $MASTER_NODE
if [ $? -eq 0 ]; then
    echo -e "\033[1;32m✅ SUCCESS: Connected to Cluster Master ($MASTER_NODE)!\033[0m"
else
    echo -e "\033[0;31m⚠️  WARNING: Could not ping Master Node. Check firewall or switch.\033[0m"
fi

echo -e "\n\033[1;36m🚀 Cluster Join Complete. IP is now $TARGET_IP\033[0m"
