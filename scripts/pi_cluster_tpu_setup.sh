#!/bin/bash
# ==========================================================
# EQ12 Raspberry Pi 5 Complete Cluster + TPU Setup Script
# Configures:
#   • Static IP 192.168.100.2/24 on eth0
#   • Gateway/DNS → 192.168.100.1 / 8.8.8.8
#   • Enables systemd-networkd
#   • Enables full SSH access on all interfaces
#   • Installs Coral TPU runtime and dependencies
#   • Downloads and tests TPU inference capability
# ==========================================================

echo "=== EQ12 Raspberry Pi Cluster + TPU Setup Starting ==="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}🔧${NC} $1"
}

# 1️⃣ System update and preparation
print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2️⃣ Backup any old network configurations
print_info "Backing up existing network configurations..."
sudo mkdir -p /etc/backup/eq12_network
sudo cp -r /etc/network* /etc/backup/eq12_network/ 2>/dev/null || true
sudo cp /etc/dhcpcd.conf /etc/backup/eq12_network/dhcpcd.conf.bak 2>/dev/null || true

# 3️⃣ Create systemd-networkd config for eth0
print_info "Configuring static IP for cluster network..."
sudo mkdir -p /etc/systemd/network
cat << 'EOF' | sudo tee /etc/systemd/network/10-eth0.network >/dev/null
[Match]
Name=eth0

[Network]
Address=192.168.100.2/24
Gateway=192.168.100.1
DNS=8.8.8.8
EOF

# 4️⃣ Enable & restart network services
print_info "Enabling systemd-networkd..."
sudo systemctl enable systemd-networkd
sudo systemctl restart systemd-networkd

# 5️⃣ Configure SSH for cluster access
print_info "Configuring SSH for cluster access..."
sudo systemctl enable ssh
sudo sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^#\?ListenAddress.*/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# 6️⃣ Install Coral TPU dependencies
print_info "Installing Coral TPU runtime and dependencies..."
sudo apt install -y libedgetpu1-std python3-pip python3-venv python3-tflite-runtime usbutils curl wget

# 7️⃣ Install additional Python packages for TPU
print_info "Installing Python packages for TPU inference..."
pip3 install --user Pillow numpy

# 8️⃣ Create TPU test environment
print_info "Setting up TPU test environment..."
mkdir -p ~/coral_test && cd ~/coral_test

# 9️⃣ Download TPU test files
print_info "Downloading TPU test models and images..."
wget -q https://github.com/google-coral/test_data/raw/master/mobilenet_v1_1.0_224_quant_edgetpu.tflite -O mobilenet_edgetpu.tflite
wget -q https://github.com/google-coral/test_data/raw/master/cat.bmp -O cat.bmp

if [ -f mobilenet_edgetpu.tflite ] && [ -f cat.bmp ]; then
    print_status "TPU test files downloaded successfully"
else
    print_error "Failed to download TPU test files"
fi

# 🔟 Create TPU benchmark script
print_info "Creating TPU benchmark script..."
cat << 'EOF' > ~/coral_test/tpu_benchmark.py
#!/usr/bin/env python3
import time
import sys
from PIL import Image
import numpy as np

try:
    import tflite_runtime.interpreter as tflite
    
    print("🔍 Initializing Coral TPU benchmark...")
    
    # Initialize interpreter with TPU delegate
    interpreter = tflite.Interpreter(
        model_path="mobilenet_edgetpu.tflite", 
        experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')]
    )
    interpreter.allocate_tensors()
    
    # Get input/output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_shape = input_details[0]['shape']
    
    # Load and prepare image
    image = Image.open("cat.bmp").resize((224, 224))
    input_data = np.expand_dims(image, axis=0)
    
    # Warm-up run
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    
    # Benchmark runs
    print("🏁 Running TPU performance benchmark (10 iterations)...")
    times = []
    for i in range(10):
        interpreter.set_tensor(input_details[0]['index'], input_data)
        start = time.time()
        interpreter.invoke()
        end = time.time()
        times.append(end - start)
        
        if i == 0:
            # Get first inference result for validation
            output_data = interpreter.get_tensor(output_details[0]['index'])
            top_prediction = np.argmax(output_data)
            confidence = np.max(output_data)
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    inferences_per_sec = 1 / avg_time
    
    print(f"")
    print(f"🎯 TPU Benchmark Results:")
    print(f"   Average inference time: {avg_time:.4f}s")
    print(f"   Minimum inference time: {min_time:.4f}s")
    print(f"   Maximum inference time: {max_time:.4f}s")
    print(f"   Inferences per second: {inferences_per_sec:.2f}")
    print(f"   Top prediction class: {top_prediction}")
    print(f"   Confidence: {confidence:.4f}")
    print(f"")
    print(f"BENCHMARK_RESULT:avg={avg_time:.4f},min={min_time:.4f},max={max_time:.4f},iterations=10,ips={inferences_per_sec:.2f}")
    
except ImportError as e:
    print(f"❌ TensorFlow Lite runtime not available: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ TPU benchmark failed: {e}")
    print(f"BENCHMARK_ERROR:{str(e)}")
    sys.exit(1)
EOF

chmod +x ~/coral_test/tpu_benchmark.py

# 1️⃣1️⃣ Test for TPU devices
print_info "Checking for connected Coral TPU devices..."
echo ""
echo "🔍 USB Device Scan:"
lsusb | grep -i "Google\|Coral" || print_warning "No Coral TPU devices detected via USB"

echo ""
echo "🔍 TPU Device Files:"
ls /dev/apex_* 2>/dev/null || print_warning "No TPU device files found in /dev/"

# 1️⃣2️⃣ Run initial TPU test if devices found
if lsusb | grep -q -i "Google\|Coral"; then
    print_status "Coral TPU device detected! Running initial test..."
    cd ~/coral_test
    python3 tpu_benchmark.py
else
    print_warning "No Coral TPU devices detected. Connect your TPU and run: cd ~/coral_test && python3 tpu_benchmark.py"
fi

# 1️⃣3️⃣ Verify network configuration
print_info "Verifying network configuration..."
echo ""
echo "🌐 Network Interfaces:"
ip addr show eth0
echo ""
echo "🌐 Routing Table:"
ip route show | grep eth0

# 1️⃣4️⃣ Create monitoring script
print_info "Creating system monitoring script..."
cat << 'EOF' > ~/eq12_node_status.sh
#!/bin/bash
echo "=== EQ12 Pi Node Status ==="
echo "Hostname: $(hostname)"
echo "IP Address: $(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)"
echo "Uptime: $(uptime -p)"
echo "Temperature: $(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 || echo 'N/A')"
echo "Memory: $(free -h | grep '^Mem:' | awk '{print $3"/"$2}')"
echo "Load: $(uptime | awk -F'load average:' '{print $2}')"
echo ""
echo "🚀 TPU Devices:"
lsusb | grep -i "Google\|Coral" || echo "No TPU devices detected"
echo ""
echo "🔗 Network Connectivity:"
ping -c 3 192.168.100.1 > /dev/null 2>&1 && echo "✅ EQ12 host reachable" || echo "❌ Cannot reach EQ12 host"
ping -c 3 8.8.8.8 > /dev/null 2>&1 && echo "✅ Internet connectivity" || echo "❌ No internet connectivity"
EOF

chmod +x ~/eq12_node_status.sh

# 1️⃣5️⃣ Final status check
echo ""
echo "==============================================="
print_status "EQ12 Raspberry Pi Cluster + TPU Setup Complete!"
echo "==============================================="
echo ""
echo "📋 Configuration Summary:"
echo "   • Static IP: 192.168.100.2/24"
echo "   • Gateway: 192.168.100.1"
echo "   • SSH: Enabled on all interfaces"
echo "   • TPU Runtime: Installed"
echo "   • Test Environment: ~/coral_test/"
echo ""
echo "🚀 Next Steps:"
echo "   1. Connect your Coral TPU via USB"
echo "   2. Run: cd ~/coral_test && python3 tpu_benchmark.py"
echo "   3. Check status: ~/eq12_node_status.sh"
echo ""
echo "📞 EQ12 Cluster Commands:"
echo "   • Node status: ~/eq12_node_status.sh"
echo "   • TPU benchmark: cd ~/coral_test && python3 tpu_benchmark.py"
echo "   • Network test: ping 192.168.100.1"
echo ""
print_info "Rebooting to finalize configuration..."
sleep 5
sudo reboot