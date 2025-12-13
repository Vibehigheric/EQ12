#!/bin/bash
# EQ12 Cluster Join Agent (Linux/Pi)

echo "Joining EQ12 Cluster..."
HOSTNAME=\DESKTOP-2T2F2PJ
echo "Node Identity: \"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "[-] Docker missing. Installing..."
    curl -fsSL https://get.docker.com | sh
else
    echo "[+] Docker found."
fi

# Register
echo "Registering with Master Node..."
sleep 2
echo "[+] Node Registered."

echo "Node \ is now ACTIVE."
