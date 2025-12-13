#!/bin/bash
# Configure M70Q network for EQ12 cluster
# Run this script ON THE M70Q via console or temporary network access

set -e

echo "======================================"
echo "M70Q Network Configuration for EQ12"
echo "======================================"
echo ""

# Detect primary Ethernet interface
INTERFACE=$(ip -o link show | grep -v "lo\|vir\|docker\|br-" | awk -F': ' '{print $2}' | grep "^en" | head -n1)

if [ -z "$INTERFACE" ]; then
    echo "ERROR: No Ethernet interface found!"
    echo "Available interfaces:"
    ip link show
    exit 1
fi

echo "Detected Ethernet interface: $INTERFACE"
echo ""

# Backup existing netplan config
sudo cp /etc/netplan/*.yaml /etc/netplan/backup_$(date +%Y%m%d_%H%M%S).yaml 2>/dev/null || true

# Create new netplan configuration
echo "Creating netplan configuration..."
sudo tee /etc/netplan/01-eq12-cluster.yaml > /dev/null <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    $INTERFACE:
      addresses:
        - 192.168.100.11/24
      dhcp4: false
      optional: true
EOF

echo "Configuration created:"
cat /etc/netplan/01-eq12-cluster.yaml
echo ""

# Apply configuration
echo "Applying network configuration..."
sudo netplan apply

echo ""
echo "Waiting for network to stabilize..."
sleep 3

# Verify configuration
echo ""
echo "Current network status:"
ip addr show $INTERFACE
echo ""

# Test connectivity
echo "Testing connectivity to EQ12 system..."
if ping -c 2 192.168.100.2 > /dev/null 2>&1; then
    echo "✓ Successfully connected to EQ12 system (192.168.100.2)"
else
    echo "✗ Cannot reach EQ12 system - check cable connection"
fi

if ping -c 2 192.168.100.80 > /dev/null 2>&1; then
    echo "✓ Successfully connected to Raspberry Pi (192.168.100.80)"
else
    echo "✗ Cannot reach Raspberry Pi"
fi

echo ""
echo "======================================"
echo "M70Q is now configured for EQ12 cluster"
echo "IP Address: 192.168.100.11/24"
echo "======================================"
echo ""
echo "From EQ12 system, you can now SSH:"
echo "  ssh <username>@192.168.100.11"
