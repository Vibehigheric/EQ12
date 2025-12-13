#!/bin/bash
# EQ12 Raspberry Pi Auto-Configuration Script
# Run this script on the Raspberry Pi after basic setup

set -e

echo "🍓 EQ12 Raspberry Pi Configuration Starting..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo "🔧 Installing essential packages..."
sudo apt install -y python3-pip python3-venv git curl wget htop iotop

# Install Coral TPU support
echo "🧠 Installing Coral TPU support..."
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt update
sudo apt install -y libedgetpu1-std python3-pycoral

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install --user numpy tensorflow-lite requests paramiko psutil

# Create EQ12 workspace
echo "📁 Creating EQ12 workspace..."
mkdir -p ~/eq12_edge
cd ~/eq12_edge

# Create Python virtual environment
python3 -m venv eq12_env
source eq12_env/bin/activate
pip install numpy tensorflow-lite pycoral requests paramiko psutil

# Create startup script
cat > ~/eq12_edge/startup.py << 'EOF'
#!/usr/bin/env python3
import socket
import json
import time
import subprocess
from datetime import datetime

def get_system_info():
    try:
        # Get system information
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(socket.gethostname())
        
        # CPU info
        cpu_cores = int(subprocess.run(['nproc'], capture_output=True, text=True).stdout.strip())
        
        # Memory info
        mem_info = subprocess.run(['free', '-m'], capture_output=True, text=True).stdout
        mem_total = int(mem_info.split('\n')[1].split()[1]) / 1024  # GB
        
        # Check Coral
        coral_check = subprocess.run(['lsusb'], capture_output=True, text=True).stdout
        has_coral = 'coral' in coral_check.lower() or 'google' in coral_check.lower()
        
        # Temperature
        try:
            temp_result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
            temperature = float(temp_result.stdout.strip().split('=')[1].replace("'C", ""))
        except:
            temperature = None
        
        info = {
            'hostname': hostname,
            'ip_address': ip_address,
            'cpu_cores': cpu_cores,
            'memory_gb': round(mem_total, 1),
            'coral_connected': has_coral,
            'temperature_c': temperature,
            'timestamp': datetime.now().isoformat(),
            'status': 'ready'
        }
        
        print("🍓 Raspberry Pi EQ12 Node Information:")
        print(json.dumps(info, indent=2))
        
        # Save to file for host to retrieve
        with open('/tmp/eq12_node_info.json', 'w') as f:
            json.dump(info, f, indent=2)
        
        return info
        
    except Exception as e:
        print(f"Error getting system info: {e}")
        return None

if __name__ == "__main__":
    get_system_info()
EOF

chmod +x ~/eq12_edge/startup.py

# Create service for auto-start
sudo tee /etc/systemd/system/eq12-node.service > /dev/null << 'EOF'
[Unit]
Description=EQ12 Edge Processing Node
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/eq12_edge
ExecStart=/home/pi/eq12_edge/eq12_env/bin/python /home/pi/eq12_edge/startup.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl enable eq12-node.service

# Test Coral TPU
echo "🧠 Testing Coral TPU..."
python3 -c "
try:
    from pycoral.utils import edgetpu
    devices = edgetpu.list_edge_tpus()
    print(f'Coral TPU devices found: {len(devices)}')
    for i, device in enumerate(devices):
        print(f'  Device {i}: {device}')
    if devices:
        print('✅ Coral TPU is working!')
    else:
        print('⚠️  No Coral TPU detected. Check USB connection.')
except Exception as e:
    print(f'❌ Coral TPU test failed: {e}')
    print('Install with: sudo apt install python3-pycoral')
"

# Set static IP configuration
echo "📡 Configuring static IP..."
sudo tee -a /etc/dhcpcd.conf > /dev/null << 'EOF'

# EQ12 Static IP Configuration
interface eth0
static ip_address=192.168.1.200/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
EOF

# Enable SSH
echo "🔑 Enabling SSH..."
sudo systemctl enable ssh
sudo systemctl start ssh

# Create SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Configure firewall
echo "🛡️  Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow from 192.168.1.0/24
sudo ufw --force enable

echo "✅ EQ12 Raspberry Pi configuration complete!"
echo "📝 Next steps:"
echo "   1. Reboot Pi: sudo reboot"
echo "   2. Verify IP: ip addr show eth0"
echo "   3. Test from host: ping 192.168.1.200"
echo "   4. Add to cluster from host PC"

echo "🔄 Rebooting in 10 seconds... (Ctrl+C to cancel)"
sleep 10
sudo reboot
