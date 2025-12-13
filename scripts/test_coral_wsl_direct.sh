#!/bin/bash
set -e

echo "=== Testing Coral TPU in WSL (Direct) ==="

# Create venv
cd ~
if [ ! -d "coral_venv" ]; then
    echo "Creating venv..."
    python3 -m venv coral_venv
fi

source coral_venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install "numpy<2.0"
pip install --extra-index-url https://google-coral.github.io/py-repo/ pycoral~=2.0

# Run test
echo "Running test..."
python3 -c "
import time
from pycoral.utils.edgetpu import list_edge_tpus
print('Scanning...')
devices = list_edge_tpus()
if devices:
    print(f'SUCCESS: Found {len(devices)} device(s): {devices}')
else:
    print('FAILURE: No devices found.')
"

echo "=== Done ==="
