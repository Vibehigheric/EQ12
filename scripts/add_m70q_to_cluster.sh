#!/bin/bash
# Run this on M70Q (192.168.1.52) to join EQ12 cluster

set -e

echo "============================================"
echo "EQ12 Cluster - Adding M70Q Node"
echo "IP: 192.168.1.52"
echo "============================================"
echo ""

# Install SSH if needed
echo "Installing OpenSSH Server..."
sudo apt update
sudo apt install -y openssh-server

# Enable SSH
echo "Enabling SSH..."
sudo systemctl enable ssh
sudo systemctl start ssh

# Configure firewall
echo "Configuring firewall..."
sudo ufw allow from 192.168.1.0/24 to any port 22
sudo ufw enable --force

echo "✓ SSH enabled"
echo ""

# Create cluster user if needed (ricoj100)
if ! id ricoj100 &>/dev/null; then
    echo "Creating cluster user: ricoj100"
    sudo adduser --gecos "" ricoj100
    sudo usermod -aG sudo ricoj100
    echo "Set password for ricoj100:"
    sudo passwd ricoj100
fi

# Install Docker
if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo sh /tmp/get-docker.sh
    sudo usermod -aG docker $USER
    sudo usermod -aG docker ricoj100
    echo "✓ Docker installed"
fi

# System info
echo ""
echo "============================================"
echo "System Information"
echo "============================================"
hostname
uname -a
echo "CPU cores: $(nproc)"
echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "Storage: $(df -h / | tail -1 | awk '{print $4}' | awk '{print $1}')"
ip addr show | grep "inet "

echo ""
echo "============================================"
echo "M70Q ready for cluster!"
echo "============================================"
echo ""
echo "From EQ12 system, connect with:"
echo "  ssh ricoj100@192.168.1.52"
echo ""
