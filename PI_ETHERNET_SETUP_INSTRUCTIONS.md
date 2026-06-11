#  Raspberry Pi Direct Ethernet Setup Guide

## Current Status
 **USB-to-Ethernet Adapter**: Detected and configured (Realtek USB 2.5GbE)  
 **Host Network Configuration**: Static IP 192.168.100.1/24 configured  
 **Pi Credentials Confirmed**: Username: ricoj100, Password: CLUSTER_PASSWORD_PLACEHOLDER  
 **Ready for USB Boot**: Pi OS Lite 64-bit with SSH pre-configured  
 **Target IP**: Pi will use 192.168.100.2/24 static IP

##  Phase 1: Raspberry Pi Imager Configuration (EQ12 Host)

### Prerequisites Check
- [ ] Raspberry Pi Imager installed on EQ12
- [ ] USB 3.0 drive (32GB+) or NVMe HAT + SSD
- [ ] Ethernet cable connected between Pi and EQ12
- [ ] 5V 5A USB-C power supply for Pi

### Automated Pi OS Flashing
```powershell
# Run the automated installer (recommended)
cd C:\EQ12\cluster
.\eq12_pi_installer.ps1 -NodeId 1 -DriveType USB -AutoDeploy

# Or use the GUI installer
.\eq12_pi_installer_gui.ps1
```

### Manual Raspberry Pi Imager Setup
If using Imager directly:

1. **Launch Raspberry Pi Imager** on your EQ12 system
2. **Choose Device**: Raspberry Pi 5
3. **Choose OS**: Raspberry Pi OS (64-bit) Lite
4. **Choose Storage**: Your USB drive

5. **Press Ctrl + Shift + X**  Advanced Options:
   ```
    Enable SSH
   Authentication: Use password
   Username: ricoj100
   Password: CLUSTER_PASSWORD_PLACEHOLDER
   Hostname: pi-node-1
   
    Configure wireless LAN (optional backup)
    Set locale settings
   
    Configure static IP:
   IP Address: 192.168.100.2
   Gateway: 192.168.100.1
   DNS: 8.8.8.8
   
    Configure wireless LAN (optional - for Internet access):
   SSID: <your_wifi_network>
   Password: <your_wifi_password>
   Country: US
   
     IMPORTANT: Leave WiFi IP as DHCP (don't set static IP for WiFi)
   This creates optimal dual-network setup:
    Ethernet: 192.168.100.x (dedicated EQ12 cluster)
    WiFi: DHCP (Internet access for updates/cloud services)
   ```

6. **Click Save  Write  Verify**

##  Phase 2: Pi Boot and First Connection

### Physical Setup
1. **Safely eject** the USB drive from EQ12
2. **Insert USB drive** into blue USB 3.0 port on Pi 5
3. **Connect Ethernet cable** from Pi to EQ12 USB-Ethernet adapter
4. **Connect USB-C power** (5V 5A) to Pi 5
5. **Wait 60-90 seconds** for first boot and SSH initialization

### Connection Verification (EQ12 PowerShell)
```powershell
# Test network connectivity
ping 192.168.100.2

# Test SSH port
Test-NetConnection -ComputerName 192.168.100.2 -Port 22

# Connect via SSH
ssh ricoj100@192.168.100.2
# Password: CLUSTER_PASSWORD_PLACEHOLDER
# Accept host key when prompted (type 'yes')
```

### Expected Results
```bash
# Successful connection shows:
ricoj100@pi-node-1:~ $
```

##  Phase 4: WiFi Configuration (Optional but Recommended)

### Why Configure WiFi?
- **Ethernet (192.168.100.x)**: Dedicated high-speed EQ12 cluster communication
- **WiFi**: Internet access for Pi OS updates, package installs, cloud API sync
- **Security**: Keeps cluster traffic isolated from Internet

### Automatic WiFi Setup (After Ethernet Works)
```powershell
# Configure WiFi automatically via SSH over Ethernet
cd C:\EQ12\cluster
.\eq12_pi_wifi_config.ps1 -WiFiSSID "YourNetworkName" -WiFiPassword "YourPassword" -VerifyDualNetwork

# Verify both networks are working
.\eq12_pi_wifi_config.ps1 -WiFiSSID "YourNetworkName" -WiFiPassword "YourPassword" -VerifyDualNetwork -SetRoutePriority
```

### Manual WiFi Configuration (On Pi Console)
```bash
# If using Pi console/HDMI
sudo raspi-config
# Navigate to: System Options  S1 Wireless LAN
# Enter SSID and password

# Verify dual network setup
ip a show eth0  # Should show 192.168.100.2/24
ip a show wlan0 # Should show DHCP IP (e.g., 192.168.0.105/24)
ping -c 3 8.8.8.8  # Test Internet via WiFi
```

### Expected Dual-Network Result
```bash
eth0: inet 192.168.100.2/24    # EQ12 cluster (static)
wlan0: inet 192.168.0.105/24   # Internet access (DHCP)
```

### Automatic Cluster Registration
```powershell
# Add Pi to EQ12 cluster with confirmed credentials
python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action add-node --ip 192.168.100.2 --username ricoj100 --password CLUSTER_PASSWORD_PLACEHOLDER

# Verify cluster status
python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action status
```

### Setup SSH Key Authentication (Recommended)
```powershell
# Generate SSH key for passwordless authentication
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\eq12_pi_key"

# Copy key to Pi (enter password once more)
ssh-copy-id -i "$env:USERPROFILE\.ssh\eq12_pi_key.pub" ricoj100@192.168.100.2

# Test passwordless login
ssh -i "$env:USERPROFILE\.ssh\eq12_pi_key" ricoj100@192.168.100.2
```

##  Phase 5: EQ12 Cluster Integration

### Deploy EQ12 Services to Pi
```powershell
# Run post-installation setup
cd C:\EQ12\cluster
.\deploy_eq12_cluster.ps1 -TargetNode 192.168.100.2 -Username ricoj100

# Or use the automated deployment
python C:\EQ12\scripts\eq12_pi_setup_assistant.py --target-ip 192.168.100.2 --deploy-services
```

##  Troubleshooting

### Pi Not Responding to Ping
1. **Check USB boot order**: Pi 5 may need bootloader update
   ```bash
   # On Pi with working OS:
   sudo rpi-eeprom-update -a
   sudo reboot
   ```
2. **Verify USB drive compatibility**: Use USB 3.0 drive, avoid old USB 2.0
3. **Check power supply**: Pi 5 requires 5V 5A, inadequate power causes boot issues
4. **Try different USB port**: Use blue USB 3.0 ports on Pi

### SSH Connection Failed
1. **Wait longer**: First boot can take 2-3 minutes
2. **Check SSH service**:
   ```bash
   # On Pi console (if available):
   sudo systemctl status ssh
   sudo systemctl restart ssh
   ```
3. **Verify credentials**: Username `ricoj100`, Password `CLUSTER_PASSWORD_PLACEHOLDER`
4. **Check SSH key conflicts**: Clear known_hosts if previous Pi connected
   ```powershell
   ssh-keygen -R 192.168.100.2
   ```

### Network Configuration Issues
- **EQ12 Adapter**: Ensure 192.168.100.1/24 is set on USB-Ethernet adapter
- **Pi Static IP**: Should auto-configure to 192.168.100.2 during imaging
- **Gateway Setting**: Pi gateway must be 192.168.100.1 (EQ12 system)
- **DNS Resolution**: Use 8.8.8.8 for internet access through EQ12

### USB Boot Not Working
1. **Update Pi bootloader** (requires working SD card first):
   ```bash
   sudo rpi-eeprom-update -a
   ```
2. **Check USB drive format**: Must be FAT32 for boot partition
3. **Use recommended drives**: SanDisk Extreme, Samsung T7, or Pi-specific drives
4. **Enable USB boot**: Recent Pi 5 firmware supports USB boot by default

##  Network Configuration Summary

### Confirmed Network Setup
- **EQ12 Host IP**: 192.168.100.1/24 (USB-Ethernet adapter)
- **Pi Node IP**: 192.168.100.2/24 (static, configured during imaging)
- **Subnet**: 192.168.100.0/24 
- **Gateway**: 192.168.100.1 (EQ12 provides internet access)
- **DNS**: 8.8.8.8, 8.8.4.4
- **Connection**: Direct Ethernet (point-to-point)

### SSH Credentials
- **Username**: ricoj100
- **Password**: CLUSTER_PASSWORD_PLACEHOLDER
- **Hostname**: pi-node-1
- **SSH Port**: 22 (default)

##  Next Steps After Connection Works

### Immediate Actions
1. **Coral TPU Setup**: Install TPU drivers and test AI inference
2. **Docker Services**: Deploy EQ12 cluster services via containers
3. **Performance Testing**: Benchmark network and compute performance
4. **Monitoring Setup**: Configure Grafana dashboard for Pi metrics

### Scale to Multi-Pi Cluster
1. **Add More Nodes**: Use NodeId 2-12 for additional Pi units
2. **PoE+ Switch**: Install NETGEAR GS108PP for centralized power/networking
3. **Load Balancing**: Distribute workloads across Pi cluster
4. **Specialization**: Assign specific roles (AI, scraping, cross-listing)

### Automation Commands
```powershell
# Quick status check
python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action discover

# Deploy services to Pi
cd C:\EQ12\cluster
.\deploy_eq12_cluster.ps1 -AllNodes

# Monitor cluster performance  
python C:\EQ12\scripts\eq12_tpu_monitor.py --cluster-overview

# Launch cluster dashboard
Start-Process "http://192.168.100.1:3000"
```