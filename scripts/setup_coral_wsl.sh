#!/bin/bash
# Setup Google Coral TPU on WSL/Ubuntu
set -e

echo "=== Installing Google Coral TPU Libraries ==="

# 1. Add Debian package repository
echo "Adding repository..."
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

# 2. Update and Install
echo "Updating package list..."
sudo apt-get update

echo "Installing libedgetpu1-std..."
sudo apt-get install -y libedgetpu1-std

echo "Installing python3-pycoral..."
sudo apt-get install -y python3-pycoral

# 3. Verify
echo "=== Verification ==="
python3 -c "import pycoral.utils.edgetpu; print('PyCoral installed successfully. Devices:', pycoral.utils.edgetpu.list_edge_tpus())"

echo "=== Setup Complete ==="
