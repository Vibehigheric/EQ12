#!/bin/bash
set -e

echo "=== Installing Google Coral TPU on Raspberry Pi ==="

# 1. Add Debian package repository
echo "Adding repository..."
# Download key to temp file first to avoid pipe issues in non-interactive shells
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg -o /tmp/coral-key.gpg
# Dearmor and install
cat /tmp/coral-key.gpg | sudo gpg --batch --yes --dearmor -o /etc/apt/trusted.gpg.d/coral-edgetpu.gpg
rm /tmp/coral-key.gpg

echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

# 2. Update and Install
echo "Updating package list..."
sudo apt-get update

echo "Installing libedgetpu1-std..."
sudo apt-get install -y libedgetpu1-std

echo "Installing python3-pycoral..."
# sudo apt-get install -y python3-pycoral # Fails on newer Python

# Install via pip in a venv
echo "Setting up Python venv for Coral..."
if [ ! -d "/opt/eq12/coral_venv" ]; then
    sudo python3 -m venv /opt/eq12/coral_venv
fi

# Activate and install
echo "Installing PyCoral via pip..."
sudo /opt/eq12/coral_venv/bin/pip install --upgrade pip
sudo /opt/eq12/coral_venv/bin/pip install "numpy<2.0"
sudo /opt/eq12/coral_venv/bin/pip install --extra-index-url https://google-coral.github.io/py-repo/ pycoral~=2.0

# 3. Verify
echo "=== Verification ==="
sudo /opt/eq12/coral_venv/bin/python3 -c "
import time
from pycoral.utils.edgetpu import list_edge_tpus
print('Scanning for Edge TPU...')
devices = list_edge_tpus()
if devices:
    print(f'SUCCESS: Found {len(devices)} device(s): {devices}')
else:
    print('FAILURE: No devices found.')
"

echo "=== Setup Complete ==="
