#!/usr/bin/env python3
"""
EQ12 Raspberry Pi Setup Assistant
=================================

Comprehensive setup assistant for integrating Raspberry Pi 5 with EQ12 system.
Handles initial configuration, SSH setup, and Coral TPU integration.
"""

import argparse
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
import socket

# Setup logging
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"pi_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RaspberryPiSetupAssistant:
    """Assists with Raspberry Pi setup and integration"""
    
    def __init__(self):
        self.host_ip = self._get_host_ip()
        self.network_base = '.'.join(self.host_ip.split('.')[:-1])
        self.discovered_devices = []
        
        logger.info(" EQ12 Raspberry Pi Setup Assistant")
        logger.info(f"  Host IP: {self.host_ip}")
        logger.info(f" Network base: {self.network_base}")
    
    def _get_host_ip(self):
        """Get host IP address"""
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "192.168.1.144"  # Fallback
    
    def scan_network_devices(self):
        """Comprehensive network device scan"""
        logger.info(" Scanning for network devices...")
        
        # Get ARP table
        try:
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            devices = []
            
            for line in result.stdout.split('\n'):
                if self.network_base in line and 'dynamic' in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        mac = parts[1]
                        devices.append({'ip': ip, 'mac': mac, 'type': 'unknown'})
            
            logger.info(f" Found {len(devices)} network devices:")
            for device in devices:
                logger.info(f"   {device['ip']} - {device['mac']}")
            
            return devices
            
        except Exception as e:
            logger.error(f"Network scan failed: {e}")
            return []
    
    def test_ssh_connectivity(self, ip_address, port=22):
        """Test SSH connectivity to device"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((ip_address, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def identify_raspberry_pi(self, devices):
        """Try to identify Raspberry Pi devices"""
        logger.info(" Identifying Raspberry Pi devices...")
        
        pi_devices = []
        
        for device in devices:
            ip = device['ip']
            mac = device['mac'].lower()
            
            # Check for Raspberry Pi MAC address prefixes
            pi_mac_prefixes = [
                'b8:27:eb',  # Raspberry Pi Foundation
                'dc:a6:32',  # Raspberry Pi Foundation
                'e4:5f:01',  # Raspberry Pi Foundation
                '28:cd:c1',  # Raspberry Pi Foundation (newer)
                'd8:3a:dd',  # Raspberry Pi Foundation (Pi 4+)
            ]
            
            is_pi_mac = any(mac.startswith(prefix) for prefix in pi_mac_prefixes)
            has_ssh = self.test_ssh_connectivity(ip)
            
            if is_pi_mac or has_ssh:
                device_info = {
                    'ip': ip,
                    'mac': mac,
                    'is_pi_mac': is_pi_mac,
                    'ssh_available': has_ssh,
                    'confidence': 'high' if is_pi_mac else 'medium'
                }
                pi_devices.append(device_info)
                
                logger.info(f" Potential Pi found: {ip}")
                logger.info(f"   MAC: {mac}")
                logger.info(f"   SSH: {'' if has_ssh else ''}")
                logger.info(f"   Pi MAC: {'' if is_pi_mac else ''}")
        
        return pi_devices
    
    def generate_pi_setup_guide(self, target_ip=None):
        """Generate setup guide for Raspberry Pi"""
        logger.info(" Generating Raspberry Pi setup guide...")
        
        setup_guide = f"""
#  EQ12 Raspberry Pi 5 Setup Guide
==========================================

## Network Information
- Host PC IP: {self.host_ip}
- Network: {self.network_base}.0/24
- Target Pi IP: {target_ip or 'TBD'}

## Step 1: Enable SSH on Raspberry Pi
1. Connect monitor, keyboard to Pi
2. Boot to desktop
3. Open Terminal and run:
   ```bash
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```
4. Or use GUI: Preferences  Raspberry Pi Configuration  Interfaces  SSH: Enable

## Step 2: Set Static IP (Recommended)
```bash
sudo nano /etc/dhcpcd.conf

# Add these lines:
interface eth0
static ip_address=192.168.1.200/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Save and reboot
sudo reboot
```

## Step 3: Install Coral TPU Support
```bash
# Add Coral repository
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

# Update and install
sudo apt update
sudo apt install -y libedgetpu1-std python3-pycoral python3-pip

# Test Coral detection
python3 -c "from pycoral.utils import edgetpu; print('Coral devices:', edgetpu.list_edge_tpus())"
```

## Step 4: Install EQ12 Dependencies
```bash
# Install Python packages
pip3 install numpy tensorflow-lite requests paramiko psutil

# Create EQ12 workspace
mkdir -p ~/eq12_edge
cd ~/eq12_edge

# Download EQ12 edge scripts (will be transferred from host)
```

## Step 5: Configure SSH Key Authentication (Recommended)
On Windows host:
```powershell
# Generate SSH key
ssh-keygen -t rsa -b 4096 -f C:\\EQ12\\ssh_keys\\eq12_pi_key

# Copy public key to Pi (replace IP)
scp C:\\EQ12\\ssh_keys\\eq12_pi_key.pub pi@192.168.1.200:~/.ssh/authorized_keys
```

## Step 6: Add Pi to EQ12 Cluster
```powershell
# From EQ12 host
cd C:\\EQ12\\scripts
python eq12_raspberry_pi_cluster_manager.py --action add-node --ip 192.168.1.200 --username pi --ssh-key "C:\\EQ12\\ssh_keys\\eq12_pi_key"
```

## Troubleshooting

### SSH Connection Issues
- Check SSH is enabled: `sudo systemctl status ssh`
- Check firewall: `sudo ufw status`
- Verify IP: `ip addr show eth0`

### Coral TPU Issues
- Check USB connection: `lsusb | grep Google`
- Verify permissions: `ls -l /dev/apex_0`
- Test with example: `python3 /usr/share/doc/python3-pycoral/examples/classify_image.py`

### Network Issues
- Check ethernet connection: `ethtool eth0`
- Ping host: `ping {self.host_ip}`
- Check routing: `ip route show`

"""
        
        # Save setup guide
        guide_path = Path("C:/EQ12/RASPBERRY_PI_SETUP_GUIDE.md")
        with open(guide_path, 'w') as f:
            f.write(setup_guide)
        
        logger.info(f" Setup guide saved: {guide_path}")
        return guide_path
    
    def create_pi_configuration_script(self):
        """Create automated Pi configuration script"""
        logger.info(" Creating Pi configuration script...")
        
        config_script = f"""#!/bin/bash
# EQ12 Raspberry Pi Auto-Configuration Script
# Run this script on the Raspberry Pi after basic setup

set -e

echo " EQ12 Raspberry Pi Configuration Starting..."

# Update system
echo " Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
echo " Installing essential packages..."
sudo apt install -y python3-pip python3-venv git curl wget htop iotop

# Install Coral TPU support
echo " Installing Coral TPU support..."
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt update
sudo apt install -y libedgetpu1-std python3-pycoral

# Install Python dependencies
echo " Installing Python dependencies..."
pip3 install --user numpy tensorflow-lite requests paramiko psutil

# Create EQ12 workspace
echo " Creating EQ12 workspace..."
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
        mem_total = int(mem_info.split('\\n')[1].split()[1]) / 1024  # GB
        
        # Check Coral
        coral_check = subprocess.run(['lsusb'], capture_output=True, text=True).stdout
        has_coral = 'coral' in coral_check.lower() or 'google' in coral_check.lower()
        
        # Temperature
        try:
            temp_result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True)
            temperature = float(temp_result.stdout.strip().split('=')[1].replace("'C", ""))
        except:
            temperature = None
        
        info = {{
            'hostname': hostname,
            'ip_address': ip_address,
            'cpu_cores': cpu_cores,
            'memory_gb': round(mem_total, 1),
            'coral_connected': has_coral,
            'temperature_c': temperature,
            'timestamp': datetime.now().isoformat(),
            'status': 'ready'
        }}
        
        print(" Raspberry Pi EQ12 Node Information:")
        print(json.dumps(info, indent=2))
        
        # Save to file for host to retrieve
        with open('/tmp/eq12_node_info.json', 'w') as f:
            json.dump(info, f, indent=2)
        
        return info
        
    except Exception as e:
        print(f"Error getting system info: {{e}}")
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
echo " Testing Coral TPU..."
python3 -c "
try:
    from pycoral.utils import edgetpu
    devices = edgetpu.list_edge_tpus()
    print(f'Coral TPU devices found: {{len(devices)}}')
    for i, device in enumerate(devices):
        print(f'  Device {{i}}: {{device}}')
    if devices:
        print(' Coral TPU is working!')
    else:
        print('  No Coral TPU detected. Check USB connection.')
except Exception as e:
    print(f' Coral TPU test failed: {{e}}')
    print('Install with: sudo apt install python3-pycoral')
"

# Set static IP configuration
echo " Configuring static IP..."
sudo tee -a /etc/dhcpcd.conf > /dev/null << 'EOF'

# EQ12 Static IP Configuration
interface eth0
static ip_address=192.168.1.200/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8
EOF

# Enable SSH
echo " Enabling SSH..."
sudo systemctl enable ssh
sudo systemctl start ssh

# Create SSH directory
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Configure firewall
echo "  Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow from {self.network_base}.0/24
sudo ufw --force enable

echo " EQ12 Raspberry Pi configuration complete!"
echo " Next steps:"
echo "   1. Reboot Pi: sudo reboot"
echo "   2. Verify IP: ip addr show eth0"
echo "   3. Test from host: ping 192.168.1.200"
echo "   4. Add to cluster from host PC"

echo " Rebooting in 10 seconds... (Ctrl+C to cancel)"
sleep 10
sudo reboot
"""
        
        # Save configuration script
        script_path = Path("C:/EQ12/scripts/pi_auto_config.sh")
        with open(script_path, 'w', newline='\n') as f:
            f.write(config_script)
        
        logger.info(f" Configuration script saved: {script_path}")
        return script_path
    
    def generate_host_integration_commands(self):
        """Generate commands to run on host after Pi setup"""
        logger.info(" Generating host integration commands...")
        
        commands = f"""
# EQ12 Host Integration Commands
# Run these commands on Windows host after Pi is configured

# 1. Test Pi connectivity
ping -n 4 192.168.1.200

# 2. Test SSH connectivity  
ssh pi@192.168.1.200 "echo 'SSH connection successful'"

# 3. Generate SSH key for automated access
ssh-keygen -t rsa -b 4096 -f C:\\EQ12\\ssh_keys\\eq12_pi_key -N ""

# 4. Copy SSH key to Pi
scp C:\\EQ12\\ssh_keys\\eq12_pi_key.pub pi@192.168.1.200:~/.ssh/authorized_keys

# 5. Test key-based SSH
ssh -i C:\\EQ12\\ssh_keys\\eq12_pi_key pi@192.168.1.200 "echo 'Key-based SSH working'"

# 6. Add Pi to EQ12 cluster
cd C:\\EQ12\\scripts
python eq12_raspberry_pi_cluster_manager.py --action add-node --ip 192.168.1.200 --username pi --ssh-key "C:\\EQ12\\ssh_keys\\eq12_pi_key"

# 7. Start cluster
python eq12_raspberry_pi_cluster_manager.py --action start

# 8. Monitor cluster status
python eq12_raspberry_pi_cluster_manager.py --action status

# 9. Generate dashboard
python eq12_raspberry_pi_cluster_manager.py --action dashboard

# 10. Test with sample tasks
python eq12_raspberry_pi_cluster_manager.py --action test-task
"""
        
        # Save commands
        commands_path = Path("C:/EQ12/PI_HOST_INTEGRATION_COMMANDS.md")
        with open(commands_path, 'w') as f:
            f.write(commands)
        
        logger.info(f" Host commands saved: {commands_path}")
        return commands_path

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 Raspberry Pi Setup Assistant")
    parser.add_argument("--action", choices=['scan', 'setup-guide', 'config-script', 'full-setup'], 
                       default='full-setup', help="Setup action to perform")
    parser.add_argument("--target-ip", help="Target IP address for Pi")
    
    args = parser.parse_args()
    
    assistant = RaspberryPiSetupAssistant()
    
    try:
        if args.action == 'scan':
            devices = assistant.scan_network_devices()
            pi_devices = assistant.identify_raspberry_pi(devices)
            
            if pi_devices:
                logger.info(f" Found {len(pi_devices)} potential Pi devices")
                for device in pi_devices:
                    print(f" Pi candidate: {device['ip']} (confidence: {device['confidence']})")
            else:
                logger.warning("  No Raspberry Pi devices detected")
                logger.info(" If Pi is connected, try enabling SSH first")
        
        elif args.action == 'setup-guide':
            guide_path = assistant.generate_pi_setup_guide(args.target_ip)
            print(f" Setup guide created: {guide_path}")
        
        elif args.action == 'config-script':
            script_path = assistant.create_pi_configuration_script()
            print(f" Configuration script created: {script_path}")
        
        elif args.action == 'full-setup':
            logger.info(" Starting full Pi setup process...")
            
            # Scan for devices
            devices = assistant.scan_network_devices()
            pi_devices = assistant.identify_raspberry_pi(devices)
            
            # Generate all setup files
            guide_path = assistant.generate_pi_setup_guide(args.target_ip)
            script_path = assistant.create_pi_configuration_script()
            commands_path = assistant.generate_host_integration_commands()
            
            logger.info(" Full setup package created!")
            logger.info(f" Setup guide: {guide_path}")
            logger.info(f" Pi config script: {script_path}")
            logger.info(f" Host commands: {commands_path}")
            
            if pi_devices:
                logger.info(f" Detected {len(pi_devices)} potential Pi devices:")
                for device in pi_devices:
                    logger.info(f"   {device['ip']} - {device['confidence']} confidence")
            else:
                logger.warning("  No Pi devices detected automatically")
                logger.info(" Follow the setup guide to enable SSH and configure your Pi")
    
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())