#!/bin/bash
# EQ12 Swarm Join Helper
# Usage: ./join_swarm.sh <manager_ip> <token>
# Or interactive mode

MANAGER_IP=$1
TOKEN=$2

if [ -z "$MANAGER_IP" ]; then
    read -p "Enter Swarm Manager IP (e.g., 192.168.1.52): " MANAGER_IP
fi

if [ -z "$TOKEN" ]; then
    read -p "Enter Swarm Join Token: " TOKEN
fi

if [ -z "$MANAGER_IP" ] || [ -z "$TOKEN" ]; then
    echo "Error: Manager IP and Token are required."
    exit 1
fi

echo "Joining Swarm at $MANAGER_IP..."
sudo docker swarm join --token "$TOKEN" "$MANAGER_IP":2377

if [ $? -eq 0 ]; then
    echo "Successfully joined the swarm!"
else
    echo "Failed to join swarm. Check firewall and connectivity."
fi
