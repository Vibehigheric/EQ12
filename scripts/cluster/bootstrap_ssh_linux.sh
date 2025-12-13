#!/bin/bash
# Bootstrap SSH on Ubuntu/Debian/Raspbian nodes (M70q, Pi)
# Run this on the node itself: curl -sL <url> | bash
# or copy-paste.

set -e

echo "=== EQ12 Cluster Node Bootstrap (Linux) ==="
echo "Target: Enable SSH and Docker for Swarm participation"

# 1. Update and Install SSH
echo "-> Installing OpenSSH Server..."
sudo apt-get update
sudo apt-get install -y openssh-server curl git

# 2. Enable SSH Service
echo "-> Enabling SSH Service..."
sudo systemctl enable --now ssh

# 3. Install Docker (Convenience script)
if ! command -v docker &> /dev/null; then
    echo "-> Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    
    # Add current user to docker group
    echo "-> Adding $USER to docker group..."
    sudo usermod -aG docker "$USER"
    echo "⚠️  You may need to log out and back in for docker group changes to take effect."
else
    echo "-> Docker is already installed."
fi

# 4. Print Status
echo "=== Bootstrap Complete ==="
echo "IP Address: $(hostname -I | awk '{print $1}')"
echo "SSH Status: $(systemctl is-active ssh)"
echo "Docker Version: $(docker --version)"
echo "Ready to be joined to EQ12 Cluster."
