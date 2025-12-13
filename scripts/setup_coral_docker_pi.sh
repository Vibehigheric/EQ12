#!/bin/bash
set -e

echo "=== Setting up Coral TPU in Docker on Raspberry Pi ==="

WORK_DIR="$HOME/coral-docker"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# 1. Create Verify Script
cat > verify_coral.py <<EOF
import time
from pycoral.utils.edgetpu import list_edge_tpus

print('Scanning for Edge TPU...')
devices = list_edge_tpus()
if devices:
    print(f'SUCCESS: Found {len(devices)} device(s): {devices}')
else:
    print('FAILURE: No devices found.')
EOF

# 2. Create Dockerfile
cat > Dockerfile <<EOF
FROM python:3.9-slim-bullseye

RUN apt-get update && apt-get install -y \\
    curl \\
    gnupg \\
    usbutils \\
    && rm -rf /var/lib/apt/lists/*

# Add Coral Repo
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | tee /etc/apt/sources.list.d/coral-edgetpu.list \\
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \\
    && apt-get update \\
    && apt-get install -y libedgetpu1-std python3-pycoral

# Fix for apt-installed packages in python image
ENV PYTHONPATH=/usr/lib/python3/dist-packages:\$PYTHONPATH

WORKDIR /app
COPY verify_coral.py .

CMD ["python3", "verify_coral.py"]
EOF

# 3. Build Image
echo "Building Docker image 'eq12-coral'..."
sudo docker build -t eq12-coral .

# 4. Run Verification
echo "Running verification container..."
# We need --privileged or specific device mapping for USB
sudo docker run --rm --privileged -v /dev/bus/usb:/dev/bus/usb eq12-coral

echo "=== Docker Setup Complete ==="
