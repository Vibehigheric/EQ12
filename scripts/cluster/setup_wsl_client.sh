#!/bin/bash
# EQ12 WSL Client Setup
# Purpose: Configure WSL2 instance to act as the Control Plane for the EQ12 Cluster
# Installs: Docker CLI, Python Dependencies, Ansible, SSH Config

set -e

echo "=== EQ12 WSL Control Plane Setup ==="

# 1. Install Dependencies
echo "-> Installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv sshpass jq git ansible

# 2. Install Docker CLI (if not present)
if ! command -v docker &> /dev/null; then
    echo "-> Installing Docker CLI..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
fi

# 3. Setup Python Environment for EQ12
echo "-> Setting up Python environment..."
VENV_DIR=".venv_wsl"

# Remove old .venv if it exists to avoid confusion
if [ -d ".venv" ]; then
    echo "-> Note: Ignoring existing .venv (likely Windows or broken)."
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "-> Creating new virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Install requirements using explicit path to avoid system pip
echo "-> Installing Python packages..."
PIP_CMD="./$VENV_DIR/bin/pip"

if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt
else
    echo "-> No requirements.txt found, installing basic tools..."
    $PIP_CMD install requests pandas plotly ansible
fi

# 4. SSH Key Check
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "-> Generating SSH Key..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
fi

echo "=== Setup Complete ==="
echo "To use the environment, run: source $VENV_DIR/bin/activate"
