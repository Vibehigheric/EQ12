#!/bin/bash
# EQ12 WSL Cluster Expert Setup
# Configures Ubuntu WSL to manage the Raspberry Pi Cluster seamlessly.

PI_USER="ricoj100"
PI_IP="192.168.1.80"
PI_PASS="CLUSTER_PASSWORD_PLACEHOLDER"

echo "========================================"
echo "   EQ12 WSL CLUSTER EXPERT SETUP"
echo "========================================"

# 1. Install Dependencies
echo "[*] Installing dependencies..."
sudo apt-get update -qq
sudo apt-get install -y sshpass ansible docker.io python3-pip -qq

# 2. Configure SSH Key-Based Access
echo "[*] Configuring Passwordless SSH..."
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "    Generating SSH Key..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
fi

# Copy ID to Pi using sshpass
echo "    Copying SSH Key to Pi ($PI_IP)..."
sshpass -p "$PI_PASS" ssh-copy-id -o StrictHostKeyChecking=no "$PI_USER@$PI_IP"

# 3. Configure SSH Config
echo "[*] Updating ~/.ssh/config..."
CONFIG_ENTRY="
Host eq12-pi
    HostName $PI_IP
    User $PI_USER
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking no
"

if ! grep -q "Host eq12-pi" ~/.ssh/config 2>/dev/null; then
    echo "$CONFIG_ENTRY" >> ~/.ssh/config
    chmod 600 ~/.ssh/config
    echo "    Added 'eq12-pi' alias."
else
    echo "    'eq12-pi' alias already exists."
fi

# 4. Configure Docker Remote Context
echo "[*] Setting up Docker Remote Context..."
if ! docker context inspect eq12-edge >/dev/null 2>&1; then
    docker context create eq12-edge --docker "host=ssh://$PI_USER@$PI_IP"
    echo "    Created Docker context 'eq12-edge'."
else
    echo "    Docker context 'eq12-edge' already exists."
fi

# 5. Create Ansible Inventory
echo "[*] Creating Ansible Inventory..."
mkdir -p ~/eq12_cluster
cat > ~/eq12_cluster/inventory.ini <<EOF
[edge]
eq12-pi ansible_host=$PI_IP ansible_user=$PI_USER

[brain]
localhost ansible_connection=local
EOF

echo "========================================"
echo "   SETUP COMPLETE"
echo "========================================"
echo "You can now:"
echo "  1. SSH to Pi:      ssh eq12-pi"
echo "  2. Manage Docker:  docker --context eq12-edge ps"
echo "  3. Run Ansible:    ansible -i ~/eq12_cluster/inventory.ini edge -m ping"
