
#  EQ12 Raspberry Pi 5 Setup Guide
==========================================

## Network Information
- Host PC IP: 192.168.1.144
- Network: 192.168.1.0/24
- Target Pi IP: TBD

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
ssh-keygen -t rsa -b 4096 -f C:\EQ12\ssh_keys\eq12_pi_key

# Copy public key to Pi (replace IP)
scp C:\EQ12\ssh_keys\eq12_pi_key.pub pi@192.168.1.200:~/.ssh/authorized_keys
```

## Step 6: Add Pi to EQ12 Cluster
```powershell
# From EQ12 host
cd C:\EQ12\scripts
python eq12_raspberry_pi_cluster_manager.py --action add-node --ip 192.168.1.200 --username pi --ssh-key "C:\EQ12\ssh_keys\eq12_pi_key"
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
- Ping host: `ping 192.168.1.144`
- Check routing: `ip route show`

