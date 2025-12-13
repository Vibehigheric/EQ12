#!/bin/bash
set -e

echo "=== Setting up Python 3.9 for Coral in WSL ==="

# 1. Add PPA
echo "Adding deadsnakes PPA..."
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update

# 2. Install Python 3.9
echo "Installing Python 3.9..."
sudo apt-get install -y python3.9 python3.9-venv python3.9-dev

# 3. Create venv
echo "Creating venv..."
cd ~
rm -rf coral_venv_39
python3.9 -m venv coral_venv_39
source coral_venv_39/bin/activate

# 4. Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install "numpy<2.0"
pip install --extra-index-url https://google-coral.github.io/py-repo/ pycoral~=2.0

# 5. Run Test
echo "Running Coral Test..."
python3 -c "
import time
from pycoral.utils.edgetpu import list_edge_tpus
print('Scanning for Edge TPU...')
devices = list_edge_tpus()
if devices:
    print(f'SUCCESS: Found {len(devices)} device(s): {devices}')
else:
    print('FAILURE: No devices found.')
"

echo "=== Done ==="
