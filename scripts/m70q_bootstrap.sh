#!/bin/bash
set -e

echo "=== M70q Post-Install Setup ==="

echo "[0/5] Configuring DNS & Routing..."
# Force DNS to Google/Cloudflare
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 1.1.1.1" | sudo tee -a /etc/resolv.conf
# Ensure default route exists (adjust gateway if needed, assuming 192.168.100.1 for cluster)
# sudo ip route add default via 192.168.100.1 || true

echo "[1/5] Checking connectivity..."
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "Internet detected. Updating system..."
    sudo apt update && sudo apt upgrade -y

    echo "[2/5] Installing essential tools..."
    sudo apt install -y curl vim htop net-tools ufw git
else
    echo "WARNING: No internet connection. Skipping updates and tool installation."
fi

echo "[3/5] Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 2377/tcp    # Docker Swarm
sudo ufw allow 7946/tcp    # Swarm overlay
sudo ufw allow 7946/udp    # Swarm overlay  
sudo ufw allow 4789/udp    # VXLAN overlay
sudo ufw allow 9443/tcp    # Portainer
# Enable UFW non-interactively
echo "y" | sudo ufw enable

echo "[4/5] Installing Docker Engine..."
if ! command -v docker &> /dev/null; then
    if ping -c 1 8.8.8.8 &> /dev/null; then
        curl -fsSL https://get.docker.com | sudo sh
        sudo usermod -aG docker $USER
    else
        echo "CRITICAL: Docker not found and no internet to install it. Aborting."
        exit 1
    fi
else
    echo "Docker already installed."
fi

echo "[5/5] Setup complete. Rebooting..."
sudo reboot
