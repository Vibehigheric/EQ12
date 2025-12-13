#!/bin/bash
# Wrapper to run coral_runner.py inside the eq12-coral Docker container
# Usage: ./run_coral.sh [args passed to python script]

# Ensure we are in the directory of the script or handle paths correctly
# For simplicity, we mount the current directory to /workspace

echo "Starting Coral Container..."

sudo docker run --rm \
    --privileged \
    -v /dev/bus/usb:/dev/bus/usb \
    -v "$(pwd)":/workspace \
    -w /workspace \
    eq12-coral \
    python3 coral_runner.py "$@"
