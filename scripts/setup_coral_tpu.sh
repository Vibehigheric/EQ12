#!/bin/bash
# Coral TPU Setup Script for Raspberry Pi
# Installs Google Coral Edge TPU runtime and Python support

set -euo pipefail

echo "=========================================="
echo "Google Coral Edge TPU Setup for Raspberry Pi"
echo "=========================================="
echo ""

# Check if device is already detected
echo "Checking for Coral TPU device..."
if lsusb | grep -q "1a6e:089a"; then
    echo "✓ Google Coral Edge TPU detected!"
else
    echo "⚠ Warning: Coral TPU not detected via lsusb"
    echo "  Please ensure device is connected via USB 3.0"
fi

echo ""
echo "Installing Coral TPU runtime..."
echo ""

# Add Coral repository
echo "Adding Google Coral repository..."
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list > /dev/null

# Add Google's APT key
echo "Adding Google APT key..."
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add - > /dev/null 2>&1 || echo "Note: Key may already be installed"

# Update package list
echo "Updating package list..."
sudo apt-get update -y

# Install Coral runtime
echo "Installing edgetpu-runtime..."
sudo apt-get install -y edgetpu-runtime

# Install Python3 support
echo "Installing Python support..."
sudo apt-get install -y python3-pycoral

# Install additional ML tools
echo "Installing additional ML tools..."
pip3 install --upgrade pip
pip3 install pycoral numpy opencv-python tensorflow-lite

echo ""
echo "=========================================="
echo "Verification"
echo "=========================================="
echo ""

# Verify installation
echo "Device check:"
lsusb | grep -i "coral\|1a6e:089a" || echo "Device not yet visible (may need reboot)"

echo ""
echo "Python check:"
python3 -c "from pycoral.utils.edgetpu import get_edgetpu_model_path; print('✓ pycoral imported successfully')" 2>/dev/null || echo "Python libraries may require additional setup"

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Test with a sample model:"
echo "   mkdir -p ~/coral_models && cd ~/coral_models"
echo "   wget https://dl.google.com/coral/models/mobilenet_v2_1.0_224_inat_bird_quant_edgetpu.tflite"
echo ""
echo "2. Run inference test:"
echo "   python3 test_coral.py"
echo ""
echo "3. For custom models, compile with edgetpu_compiler:"
echo "   pip3 install edgetpu"
echo "   edgetpu_compiler -s your_model.tflite"
echo ""
echo "✓ Coral TPU setup complete!"
echo ""
