# Lenovo ThinkCentre M70Q Tiny - EQ12 Cluster Node Setup

## Hardware Specifications

### Processor
- **Options**: Intel 10th/11th Gen Core i3/i5/i7
- **Model**: i3-1220P (12 cores) typical for M70Q
- **TDP**: 15-28W

### Memory
- **Type**: DDR4 SODIMM
- **Max**: 64GB (2 x 32GB)
- **Standard**: 8-16GB typical

### Storage
- **Primary**: M.2 NVMe (up to 1TB, PCIe Gen3)
- **Secondary**: SATA M.2 or 2.5" SSD optional
- **Footprint**: Ultra-compact (143 x 160 x 120mm, 1.3L)

### Power
- **PSU**: 65W internal (fanless)
- **Operating Temp**: 10-40°C
- **Cooling**: Passive (very quiet/silent)

## Physical Ports & Connectors

### Video Output
- 1x HDMI (4K @60Hz)
- 1x DisplayPort (4K @60Hz)
- Optional: Mini-DisplayPort variant

### Networking
- **1x Gigabit Ethernet** (RJ45) - 1 Gbps auto-negotiation
- **Wake-on-LAN**: Supported
- **PXE Boot**: Supported (network install capable)
- NO built-in WiFi (add USB WiFi if needed)

### USB Ports
- 4x USB 3.0 Type-A (rear)
- 2x USB 2.0 Type-A (rear)
- 1x USB 3.0 Type-C (optional variant)

### Audio
- 1x 3.5mm headphone jack
- 1x Mic-in jack

### Power
- 1x USB-C power connector (65W)

## Operating System Compatibility

### Windows
- ✅ Windows 11 Pro (recommended)
- ✅ Windows 10 Pro
- ✅ Windows Server 2019/2022
- ✅ Windows Sandbox support

### Linux
- ✅ Ubuntu 20.04 LTS, 22.04 LTS
- ✅ Debian 11/12
- ✅ CentOS 8/9
- ✅ RHEL 8/9
- ✅ Pop!_OS
- ✅ Fedora

## Network Configuration for EQ12 Cluster

### Current M70Q Status
- **IP**: 192.168.1.11 (WiFi router)
- **MAC**: 98:FA:9B:E9:D6:99
- **Status**: Firewall blocks SSH (all ports filtered)

### Goal: Direct Cluster Connection
Once you get 2.5G USB adapter, connect M70Q this way:

```
M70Q Ethernet Port
        ↓
2.5G USB-to-Ethernet Adapter
        ↓
2.5G Ethernet Switch (new)
        ↓
Pi (192.168.100.80) + EQ12 PC (192.168.100.1/10)
```

### IP Configuration for M70Q
```
Address: 192.168.100.11/24
Gateway: 192.168.100.1
DNS: 8.8.8.8, 8.8.4.4
```

## Headless Setup via HDMI (Recommended Now)

Since you have HDMI, you can set up M70Q with monitor temporarily:

### Step 1: Physical Connection
1. Connect monitor to HDMI port
2. Connect keyboard/mouse to USB
3. Plug in power

### Step 2: Boot to BIOS
1. Power on M70Q
2. Press **F2** or **Del** during boot (Lenovo logo screen)
3. Navigate to **Network Boot** settings

### Step 3: Enable Network Features
**In BIOS → System Settings:**
- Boot Mode: UEFI
- Boot Order: Ethernet first (if network boot needed)
- Wake-on-LAN: Enabled
- Intel ME: Enabled

**In BIOS → Security:**
- Secure Boot: Disable (for Linux/custom boot)
- TPM: Enable (for Windows Server)

### Step 4: Install Ubuntu (Recommended)
1. Create bootable USB on another PC with Ubuntu 22.04 LTS
2. Insert USB into M70Q's USB 3.0 port
3. Boot from USB (F12 or Del during startup)
4. Install Ubuntu with these options:
   - Network: Automatic (DHCP initially)
   - Hostname: `eq12-m70q` or similar
   - User: `eqadmin` (same as Pi: `ricoj100`)
   - Storage: Default

### Step 5: Configure Network (Ubuntu)
Once Ubuntu is running:

```bash
# Open terminal (Ctrl+Alt+T)

# Check current network
ip link show
ip addr show

# Edit netplan config
sudo nano /etc/netplan/01-netcfg.yaml
```

Add configuration:
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp2s0:  # or check your interface name
      addresses:
        - 192.168.100.11/24
      dhcp4: false
      optional: true
```

Apply changes:
```bash
sudo netplan apply
ip addr show  # Verify 192.168.100.11 is assigned
```

### Step 6: Enable SSH
```bash
sudo apt update
sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh

# Allow SSH from cluster network only
sudo ufw allow from 192.168.100.0/24 to any port 22
sudo ufw enable
```

### Step 7: Test from EQ12 System
```powershell
ping 192.168.100.11
ssh ricoj100@192.168.100.11  # Use same user
```

## Alternative: Network Boot (PXE Boot)

If you want to boot M70Q directly from network without USB:

### Prerequisites
- DHCP server on network (your router provides this)
- PXE server ready to serve Ubuntu installer

### Process
1. Set BIOS Boot Order: Ethernet first
2. Power on M70Q
3. Should boot from network automatically
4. Install Ubuntu from network image

## Docker Deployment

Once M70Q is set up with Ubuntu 22.04:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker run hello-world

# Run setup script from EQ12 repo
cd /workspaces/EQ12/scripts
bash setup_10t8_ubuntu.sh
```

## Recommended Configuration for EQ12

| Component | Specification | Rationale |
|-----------|---------------|-----------|
| Processor | i5-1240P minimum | 12 cores for container workloads |
| RAM | 32GB | Sufficient for Docker + databases |
| Storage | 256GB+ NVMe | Fast container boot, local volumes |
| OS | Ubuntu 22.04 LTS | Stability, long support, Docker optimized |
| Network | 1 Gbps Ethernet | Will upgrade to 2.5G adapter |
| Boot | UEFI + SSH enabled | Remote management |

## Troubleshooting M70Q

### Can't connect to network
```bash
# Check cable is connected
ip link show  # Should show "UP" for ethernet

# Try DHCP first
sudo dhclient enp2s0
ip addr show
```

### SSH not working
```bash
# Check SSH is running
sudo systemctl status ssh

# Check firewall
sudo ufw status
sudo ufw allow 22

# Check SSH socket
sudo ss -tln | grep 22
```

### No internet after config
```bash
# Check routing
ip route show

# Add default route if missing
sudo ip route add default via 192.168.100.1

# Make permanent in netplan
# Add to yaml: routes: [{ to: 0.0.0.0/0, via: 192.168.100.1 }]
```

### Can't reach other cluster nodes
```bash
# Ping test
ping 192.168.100.1   # EQ12 PC
ping 192.168.100.80  # Raspberry Pi

# Check network interface is up
ip link show
ip addr show
```

## Next Steps

**Immediate (with HDMI):**
1. ✅ Connect monitor to M70Q HDMI
2. ✅ Boot into BIOS and enable network boot
3. ✅ Create Ubuntu USB installer
4. ✅ Install Ubuntu 22.04 LTS
5. ✅ Configure static IP (192.168.100.11)
6. ✅ Enable SSH access

**Short Term (after basic setup):**
7. ⏳ Test SSH access from EQ12 system
8. ⏳ Install Docker and dependencies
9. ⏳ Run `setup_10t8_ubuntu.sh` for cluster integration

**Medium Term (after 2.5G adapter arrives):**
10. ⏳ Disconnect M70Q from Gigabit Ethernet
11. ⏳ Connect 2.5G USB adapter
12. ⏳ Add to 2.5G switch with Pi
13. ⏳ Update IP config to use 2.5G adapter

## Key Commands Reference

```bash
# Check system info
uname -a
lsb_release -a
free -h
df -h

# Check network
ip addr show
ip route show
netstat -tln | grep 22

# Docker
docker ps
docker-compose up -d
docker logs -f container_name

# SSH from EQ12
ssh eqadmin@192.168.100.11
scp file.txt eqadmin@192.168.100.11:/tmp/
```

---

**Status**: Ready for HDMI-based setup  
**Timeline**: 30-45 minutes for full configuration  
**Priority**: HIGH (primary compute node for cluster)
