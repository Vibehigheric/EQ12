# Pi Network Configuration Guide
# Configure Raspberry Pi for EQ12 cluster integration

##  Current Status
 **EQ12 Network**: Ethernet 3 configured correctly (192.168.100.1/24)  
 **Pi Network**: Needs static IP configuration (192.168.100.2/24)

##  Pi Configuration Methods

### Method 1: Raspberry Pi Imager (Easiest - Fresh Install)

If you're installing Pi OS fresh:

1. **Download Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. **Select Options**:
   - Device: Raspberry Pi 5
   - OS: Raspberry Pi OS (64-bit) Lite  
   - Storage: Your USB drive

3. **Press Ctrl + Shift + X** for Advanced Options:
   ```
    Enable SSH
   Authentication: Use password
   Username: ricoj100
   Password: 102120sRO1!
   Hostname: pi-node-1
   
    Configure static IP:
   IP Address: 192.168.100.2
   Gateway: 192.168.100.1
   DNS: 8.8.8.8
   ```

4. **Flash and Boot**: Insert USB drive in Pi, power on, wait 90 seconds

### Method 2: Edit Existing Pi OS (Console/HDMI Access)

If Pi is already running but needs network config:

```bash
# Connect keyboard/monitor to Pi, then run:
sudo nano /etc/dhcpcd.conf

# Add these lines at the end:
interface eth0
static ip_address=192.168.100.2/24
static routers=192.168.100.1
static domain_name_servers=8.8.8.8

# Save file (Ctrl+O, Enter, Ctrl+X)

# Enable SSH
sudo systemctl enable ssh
sudo systemctl start ssh

# Reboot
sudo reboot
```

### Method 3: Edit Boot Partition (No Monitor Needed)

If you can access the Pi's boot partition:

1. **Remove USB drive** from Pi, insert into EQ12
2. **Navigate to boot partition** (usually shows as removable drive)
3. **Edit cmdline.txt**, add at the end:
   ```
   ip=192.168.100.2::192.168.100.1:255.255.255.0::eth0:off
   ```
4. **Create SSH enable file**: Create empty file named `ssh` (no extension)
5. **Create user config**: Create file `userconf.txt` with content:
   ```
   ricoj100:$6$rounds=656000$YQAWmPDxM3aIGF0$uKO1dEGz8RW.8H8g.7Xz5.8B.P5.C2.0J2.K1.5E.3D
   ```
6. **Re-insert in Pi** and power on

##  Testing Connection from EQ12

After Pi configuration, test from EQ12 PowerShell:

```powershell
# Test basic connectivity
ping 192.168.100.2

# Test SSH port
Test-NetConnection -ComputerName 192.168.100.2 -Port 22

# Connect via SSH
ssh ricoj100@192.168.100.2
# Password: 102120sRO1!
```

##  Expected Results

```powershell
PS C:\EQ12> ping 192.168.100.2

Pinging 192.168.100.2 with 32 bytes of data:
Reply from 192.168.100.2: bytes=32 time<1ms TTL=64
Reply from 192.168.100.2: bytes=32 time<1ms TTL=64

PS C:\EQ12> ssh ricoj100@192.168.100.2
ricoj100@pi-node-1:~ $
```

##  Troubleshooting

### If Pi still doesn't respond:
1. **Check power**: Pi 5 needs 5V 5A USB-C power supply
2. **Check boot**: Look for activity LED on Pi
3. **Check cable**: Try different Ethernet cable
4. **Check USB drive**: Ensure it's bootable and properly flashed

### Common Issues:
- **Wrong interface**: Make sure editing `eth0` not `wlan0`
- **Syntax errors**: Check spacing and spelling in config files
- **Boot order**: Pi 5 may need USB boot enabled in firmware
- **File permissions**: SSH key files need correct permissions

##  Quick Test Commands

Run these on EQ12 to verify connection:

```powershell
# Network status
Get-NetAdapter "Ethernet 3" | Format-List Name, Status, LinkSpeed
Get-NetIPAddress -InterfaceAlias "Ethernet 3" -AddressFamily IPv4

# Pi connectivity
ping 192.168.100.2 -n 1
Test-NetConnection 192.168.100.2 -Port 22

# ARP table (should show Pi MAC address after successful ping)
arp -a | findstr "192.168.100"
```

##  Success Criteria

 **Ping responds** from 192.168.100.2  
 **SSH port 22** is accessible  
 **SSH login** works with ricoj100/102120sRO1!  
 **ARP entry** shows Pi MAC address

Once connectivity works, proceed to cluster integration:

```powershell
# Add Pi to EQ12 cluster
python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action add-node --ip 192.168.100.2 --username ricoj100 --password 102120sRO1!
```