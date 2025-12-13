# Adding Lenovo M70Q to EQ12 Cluster Network

## Current Network Status

### Verified Working Connections
- **EQ12 System (Windows PC)**
  - Realtek USB 2.5GbE adapter: `192.168.100.1`, `192.168.100.10`
  - MAC: `6C-1F-F7-1A-02-FD`
  
- **Raspberry Pi**
  - eth0: `192.168.100.80/24`
  - MAC: `2C:CF:67:8E:13:58`
  - Connection: <1ms latency (excellent)

### M70Q Current Status
- **IP (WiFi/Router network)**: `192.168.1.11`
- **MAC**: `98:FA:9B:E9:D6:99`
- **Status**: Online but all ports filtered (firewall active)
- **OS**: Likely Ubuntu/Linux (Lenovo M70Q Tiny)

## Physical Setup Required

### Option 1: Direct Ethernet Connection (Recommended)
1. **Connect M70Q to Realtek USB adapter**:
   - Use Ethernet cable from M70Q to spare port on your network switch/router
   - Or use second USB-Ethernet adapter to create dedicated link

2. **Configure static IP on M70Q**:
   ```bash
   # On M70Q (requires console/monitor access initially)
   sudo ip addr add 192.168.100.11/24 dev <ethernet_interface>
   sudo ip link set <ethernet_interface> up
   
   # Test connectivity
   ping 192.168.100.1
   ping 192.168.100.80
   ```

3. **Make permanent** (Ubuntu/Debian):
   ```bash
   # Edit netplan configuration
   sudo nano /etc/netplan/01-netcfg.yaml
   ```
   
   Add:
   ```yaml
   network:
     version: 2
     ethernets:
       <interface_name>:
         addresses:
           - 192.168.100.11/24
         dhcp4: false
   ```
   
   Apply:
   ```bash
   sudo netplan apply
   ```

### Option 2: USB-Ethernet Adapter on M70Q
If M70Q doesn't have built-in Ethernet or you need additional network interface:

1. **Connect USB-Ethernet adapter** to M70Q
2. **Configure as above** using the new USB network interface

## Post-Connection Steps

### 1. Enable SSH on M70Q
```bash
# On M70Q
sudo apt update
sudo apt install openssh-server -y
sudo systemctl enable ssh
sudo systemctl start ssh

# Configure firewall
sudo ufw allow from 192.168.100.0/24 to any port 22
sudo ufw enable
```

### 2. Test from EQ12 System
```powershell
# From Windows PowerShell
ping 192.168.100.11
ssh <username>@192.168.100.11
```

### 3. Install Docker and Dependencies
```bash
# On M70Q via SSH
cd /workspaces/EQ12/scripts
bash setup_10t8_ubuntu.sh
```

### 4. Configure Cluster Services

**On M70Q (Primary Compute)**:
- Docker containers for main services
- PostgreSQL database
- Redis cache
- API services

**On Raspberry Pi (ML Inference)**:
- Coral TPU runtime
- ML model serving
- Edge inference tasks

**On Windows (Management)**:
- Monitoring dashboards
- Development environment
- Orchestration scripts

## Network Topology

```
┌──────────────────────────────────────────────────────┐
│         192.168.1.0/24 (Router WiFi Network)         │
│  - Router: 192.168.1.1                               │
│  - EQ12 PC WiFi: 192.168.1.144                       │
│  - M70Q WiFi: 192.168.1.11 (backup/management)       │
│  - Pi WiFi: 192.168.1.80 (backup/management)         │
└──────────────────────────────────────────────────────┘
                          │
                          │
┌──────────────────────────────────────────────────────┐
│      192.168.100.0/24 (EQ12 Cluster Network)         │
│      via Realtek USB 2.5GbE Adapter                  │
│                                                       │
│  ┌─────────────────┐      ┌──────────────────┐      │
│  │  EQ12 PC        │      │  Raspberry Pi    │      │
│  │  192.168.100.1  │──────│  192.168.100.80  │      │
│  │  192.168.100.10 │      │  (Coral TPU)     │      │
│  └─────────────────┘      └──────────────────┘      │
│           │                                          │
│           │                                          │
│  ┌─────────────────┐                                │
│  │  Lenovo M70Q    │                                │
│  │  192.168.100.11 │  ← NEEDS CONFIGURATION         │
│  │  (Ubuntu)       │                                │
│  └─────────────────┘                                │
└──────────────────────────────────────────────────────┘
```

## Verification Commands

### From EQ12 System (PowerShell)
```powershell
# Check cluster network
Get-NetIPAddress -InterfaceAlias "Ethernet 3"

# Test all nodes
ping 192.168.100.1   # Self
ping 192.168.100.80  # Raspberry Pi
ping 192.168.100.11  # M70Q (after configuration)

# SSH to nodes
ssh ricoj100@192.168.100.80   # Pi
ssh <user>@192.168.100.11     # M70Q
```

### From Raspberry Pi
```bash
# Test cluster connectivity
ping 192.168.100.1   # EQ12 PC
ping 192.168.100.11  # M70Q
ip addr show eth0
```

### From M70Q (after setup)
```bash
# Test cluster connectivity  
ping 192.168.100.1   # EQ12 PC
ping 192.168.100.80  # Raspberry Pi
ip addr show
docker ps
```

## Next Steps After M70Q Added

1. ✅ **Physical connection** - Connect M70Q to cluster network
2. ✅ **IP configuration** - Assign 192.168.100.11/24
3. ✅ **SSH access** - Enable and test remote access
4. ✅ **Run setup script** - Execute `setup_10t8_ubuntu.sh`
5. ✅ **Deploy services** - Start Docker containers
6. ✅ **Install Coral TPU** on Pi - Run `setup_coral_tpu.sh`
7. ✅ **Test inter-node** - Verify all nodes can communicate
8. ✅ **Deploy EQ12 apps** - Start main services

## Troubleshooting

### M70Q not accessible
- Check physical Ethernet cable connection
- Verify network interface is UP: `ip link show`
- Check firewall rules: `sudo ufw status`
- Verify IP configuration: `ip addr show`

### Slow performance
- Test bandwidth: `iperf3 -s` on one node, `iperf3 -c 192.168.100.X` on another
- Check adapter speed: Should be 1-2.5 Gbps
- Monitor with: `nload` or `iftop`

### Connectivity issues
- Ensure all devices on same subnet (192.168.100.0/24)
- Check routing table: `ip route show`
- Verify no IP conflicts: `arp -a` on Windows
