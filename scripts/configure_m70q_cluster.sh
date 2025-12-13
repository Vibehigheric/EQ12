#!/bin/bash
# EQ12 M70Q Network Configuration - Run this on M70Q directly
# Purpose: Configure M70Q for cluster network access

set -e

echo "========================================"
echo "EQ12 M70Q Network Configuration"
echo "========================================"
echo ""

# Get current Ethernet interface
IFACE=$(ip -o link show | grep -v "lo\|docker\|veth\|vir" | awk -F': ' '{print $2}' | grep "^en\|^eth" | head -n1)

if [ -z "$IFACE" ]; then
    echo "ERROR: No Ethernet interface found!"
    echo "Available interfaces:"
    ip link show | grep "^[0-9]"
    exit 1
fi

echo "✓ Detected Ethernet interface: $IFACE"
echo ""

# Check if interface has link
echo "Checking link status..."
if cat /sys/class/net/$IFACE/carrier 2>/dev/null | grep -q 1; then
    echo "✓ Ethernet cable is connected"
else
    echo "⚠ WARNING: Ethernet cable may not be plugged in"
    echo "   Connect M70Q to cluster network switch/router"
fi

echo ""
echo "Current Network Configuration:"
ip addr show $IFACE || echo "Interface not configured"
echo ""

# Configure static IP for cluster network
echo "Configuring cluster network (192.168.100.11)..."

# Backup existing netplan
sudo cp /etc/netplan/*.yaml /etc/netplan/backup_$(date +%Y%m%d_%H%M%S).yaml 2>/dev/null || true

# Create new netplan config for cluster
sudo tee /etc/netplan/02-eq12-cluster.yaml > /dev/null <<'EOF'
network:
  version: 2
  renderer: networkd
  ethernets:
    en0:
      match:
        name: en*
      dhcp4: false
      addresses:
        - 192.168.100.11/24
      routes:
        - to: 0.0.0.0/0
          via: 192.168.100.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
      optional: true
EOF

echo "✓ Netplan configuration created"
echo ""
echo "Applying network configuration..."
sudo netplan apply

# Wait for network to come up
sleep 2

echo ""
echo "New Network Configuration:"
ip addr show $IFACE
echo ""

# Test connectivity
echo "Testing cluster connectivity..."
if ping -c 1 192.168.100.1 > /dev/null 2>&1; then
    echo "✓ Connected to EQ12 system (192.168.100.1)"
else
    echo "✗ Cannot reach EQ12 system"
    echo "  Check: Ethernet cable, switch power, IP configuration"
fi

if ping -c 1 192.168.100.80 > /dev/null 2>&1; then
    echo "✓ Connected to Raspberry Pi (192.168.100.80)"
else
    echo "✗ Cannot reach Raspberry Pi (may be offline)"
fi

echo ""
echo "========================================"
echo "Configuring SSH for Remote Access"
echo "========================================"
echo ""

# Install SSH if not present
if ! command -v ssh &> /dev/null; then
    echo "Installing OpenSSH..."
    sudo apt update
    sudo apt install -y openssh-server openssh-client
fi

# Enable and start SSH
echo "Enabling SSH service..."
sudo systemctl enable ssh
sudo systemctl start ssh

# Configure UFW firewall to allow SSH from cluster network
echo "Configuring firewall..."
sudo ufw allow from 192.168.100.0/24 to any port 22
sudo ufw allow from 192.168.1.0/24 to any port 22 comment "Allow WiFi network SSH"
sudo ufw enable --force

echo "✓ SSH enabled and firewall configured"
echo ""

# Display SSH connection info
LOCAL_USER=$(whoami)
echo "========================================"
echo "SSH Access Information"
echo "========================================"
echo ""
echo "From EQ12 system, connect with:"
echo "  ssh $LOCAL_USER@192.168.100.11"
echo ""
echo "Or from WiFi network:"
echo "  ssh $LOCAL_USER@192.168.1.11"
echo ""

# Show system info
echo "========================================"
echo "System Information"
echo "========================================"
echo ""
uname -a
echo ""
echo "CPU: $(nproc) cores"
echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "Storage: $(df -h / | tail -1 | awk '{print $2}')"
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next Steps:"
echo "1. From EQ12 system, SSH to M70Q:"
echo "   ssh $LOCAL_USER@192.168.100.11"
echo ""
echo "2. Run Docker setup:"
echo "   bash /workspaces/EQ12/scripts/setup_10t8_ubuntu.sh"
echo ""
echo "3. Or manually install Docker:"
echo "   curl -fsSL https://get.docker.com | sh"
echo "   sudo usermod -aG docker $USER"
echo ""
