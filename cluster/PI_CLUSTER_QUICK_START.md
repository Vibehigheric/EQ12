# EQ12 Pi Cluster Quick Start Guide
# Automated deployment for Raspberry Pi 5 cluster integration

##  ONE-CLICK DEPLOYMENT

### Method 1: PowerShell Command Line
```powershell
# Flash single Pi node (USB boot)
.\eq12_pi_installer.ps1 -NodeId 1 -DriveType USB -AutoDeploy

# Flash Pi node with NVMe boot (performance mode)
.\eq12_pi_installer.ps1 -NodeId 2 -DriveType NVMe -AutoDeploy

# Deploy to existing Pi (skip OS flashing)
.\eq12_pi_installer.ps1 -NodeId 3 -SkipFlashing -AutoDeploy
```

### Method 2: GUI Installer
```powershell
# Launch graphical installer
.\eq12_pi_installer_gui.ps1
```

##  PREREQUISITES CHECKLIST

### Hardware Requirements
- [ ] EQ12 master system configured (192.168.100.1)
- [ ] Raspberry Pi 5 (8GB recommended)
- [ ] USB 3.0 drive (32GB+) OR NVMe HAT + SSD
- [ ] Coral USB Accelerator for each Pi
- [ ] Ethernet cable for initial setup
- [ ] Power supply (5V 5A USB-C)

### Software Prerequisites
- [ ] Raspberry Pi Imager installed
- [ ] PowerShell 5.0+ (Windows)
- [ ] Network connectivity to Pi subnet
- [ ] Admin privileges on EQ12 system

### Network Configuration
- [ ] EQ12 system IP: 192.168.100.1
- [ ] Pi cluster subnet: 192.168.100.0/24
- [ ] Pi nodes: 192.168.100.11-22
- [ ] Internet gateway configured
- [ ] SSH enabled for cluster management

##  INSTALLATION PROCESS

### Phase 1: Single Pi Setup (Testing)
1. **Connect Pi via USB-Ethernet**
   ```powershell
   # Verify network adapter
   Get-NetAdapter | Where-Object {$_.InterfaceDescription -like "*USB*Ethernet*"}
   ```

2. **Flash and Deploy First Node**
   ```powershell
   .\eq12_pi_installer.ps1 -NodeId 1 -DriveType USB -AutoDeploy -Verbose
   ```

3. **Verify Node Registration**
   ```powershell
   # Check cluster status
   Invoke-RestMethod -Uri "http://192.168.100.1:8000/cluster/status"
   ```

### Phase 2: Multi-Pi Expansion (Production)
1. **Hardware Setup**
   - Install PoE+ switch (NETGEAR GS108PP)
   - Connect additional Pi nodes
   - Verify power delivery

2. **Batch Node Deployment**
   ```powershell
   # Deploy nodes 2-4 (Phase 2 expansion)
   2..4 | ForEach-Object {
       .\eq12_pi_installer.ps1 -NodeId $_ -DriveType NVMe -AutoDeploy
       Start-Sleep -Seconds 30  # Wait between deployments
   }
   ```

3. **Cluster Validation**
   ```powershell
   # Verify all nodes online
   .\cluster\validate_cluster.ps1 -ExpectedNodes 4
   ```

### Phase 3: Full Cluster (12 Nodes)
1. **Complete Hardware Installation**
   - All 12 Pi nodes connected
   - Coral TPUs distributed
   - Network switch management

2. **Full Deployment**
   ```powershell
   # Deploy remaining nodes 5-12
   5..12 | ForEach-Object {
       .\eq12_pi_installer.ps1 -NodeId $_ -DriveType NVMe -AutoDeploy
   }
   ```

##  NODE SPECIALIZATION

### Node Allocation Strategy
- **Nodes 01-03**: AI Inference (High-priority TPU tasks)
- **Nodes 04-06**: Cross-listing Automation
- **Nodes 07-09**: Web Scraping & Data Collection  
- **Nodes 10-12**: General Purpose & Load Balancing

### Service Distribution
```yaml
ai_inference:
  nodes: [01, 02, 03]
  resources: "High TPU, 4GB RAM each"
  
cross_listing:
  nodes: [04, 05, 06] 
  resources: "Moderate CPU, Network intensive"
  
web_scraping:
  nodes: [07, 08, 09]
  resources: "Browser automation, Storage"
  
load_balancing:
  nodes: [10, 11, 12]
  resources: "Flexible allocation, Backup services"
```

##  MONITORING & MANAGEMENT

### Cluster Dashboard
```powershell
# Open web dashboard
Start-Process "http://192.168.100.1:3000"

# CLI status check
.\eq12_tpu_monitor.py --cluster-overview
```

### Performance Monitoring
```powershell
# Real-time TPU utilization
.\eq12_tpu_monitor.py --live-metrics

# Node health check
.\cluster\health_check.ps1 -AllNodes
```

### Maintenance Commands
```powershell
# Restart all cluster services
.\cluster\restart_services.ps1

# Update Pi OS on all nodes
.\cluster\update_nodes.ps1 -SecurityUpdates

# Backup cluster configuration
.\cluster\backup_config.ps1 -Destination "C:\EQ12\backups"
```

##  TROUBLESHOOTING

### Common Issues
1. **Pi not booting from USB/NVMe**
   ```bash
   # On Pi: Update bootloader
   sudo rpi-eeprom-update -a
   sudo reboot
   ```

2. **Network connectivity issues**
   ```powershell
   # Reset network configuration
   .\cluster\reset_network.ps1 -NodeId 1
   ```

3. **TPU not detected**
   ```bash
   # On Pi: Verify USB device
   lsusb | grep "Google"
   
   # Reinstall drivers
   sudo apt update && sudo apt install -y gasket-dkms libedgetpu1-std
   ```

### Log Locations
- **EQ12 Master**: `C:\EQ12\logs\cluster_*.log`
- **Pi Nodes**: `/home/eq12/logs/node_*.log`
- **Service Logs**: `docker logs eq12-cluster-service`

### Support Commands
```powershell
# Generate diagnostic report
.\cluster\diagnostic_report.ps1 -FullReport

# Export cluster configuration
.\cluster\export_config.ps1 -Format JSON

# Test all network connections
.\cluster\network_test.ps1 -Comprehensive
```

##  PERFORMANCE EXPECTATIONS

### Baseline Metrics (12-Node Cluster)
- **Total TPU Power**: ~12 TOPS aggregate
- **Inference Throughput**: 2000+ inferences/hour
- **Network Latency**: <5ms intra-cluster
- **Power Consumption**: ~180W total (15W per Pi)
- **Uptime Target**: 99.9% availability

### Scaling Characteristics
- **Linear TPU scaling**: Each Pi adds ~1 TOPS
- **Network bottleneck**: PoE+ switch at 1Gbps shared
- **Thermal management**: Auto-throttling at 80C
- **Load balancing**: Automatic task distribution

##  SUCCESS CRITERIA

### Phase 1 Complete 
- [ ] Single Pi node online and registered
- [ ] TPU detection and basic inference working
- [ ] Network connectivity established
- [ ] Cluster services responding

### Phase 2 Complete   
- [ ] 4 Pi nodes operational
- [ ] Load balancing active across nodes
- [ ] Cross-listing automation distributed
- [ ] Performance monitoring dashboard live

### Phase 3 Complete 
- [ ] All 12 nodes online and stable
- [ ] Full specialization roles assigned
- [ ] Automatic failover tested
- [ ] Enterprise monitoring implemented
- [ ] ROI targets achieved (>300% efficiency gain)

---

** Ready to deploy your Pi cluster? Start with Phase 1 using the GUI installer!**

```powershell
# Launch the installer now
.\eq12_pi_installer_gui.ps1
```