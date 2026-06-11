# SIMPLIFIED PI SETUP - Pi Imager Method

##  PRACTICAL APPROACH (No Advanced Configuration Needed)

### **Step 1: Use Pi Imager OS Customization**
1. **Download Raspberry Pi Imager**: https://rpi.org/imager
2. **Select Raspberry Pi OS (64-bit)**
3. **Click  (Advanced Options)**
4. **Configure ONLY these settings:**
   -  **Enable SSH**  Use password authentication
   -  **Set username:** `ricoj100`
   -  **Set password:** `CLUSTER_PASSWORD_PLACEHOLDER`
   -  **Configure WiFi** (optional, for initial setup)
   -  **Skip static IP** (Pi Imager doesn't support it properly)

### **Step 2: First Boot Process**
**Pi will boot with DHCP initially - this is NORMAL and EXPECTED**

1. **Flash and insert USB**
2. **Power on Pi**  
3. **Pi gets automatic IP from router/DHCP**
4. **We'll find it and configure static IP via SSH**

### **Step 3: Find Pi and Configure Static IP**

**Option A: Scan for Pi on network**
```powershell
# Run this to find your Pi
.\eq12_pi_network_scanner.ps1
```

**Option B: Connect via router's DHCP**
```powershell
# If Pi gets IP from your main router (e.g., 192.168.1.x)
ssh ricoj100@192.168.1.XXX  # Replace XXX with actual IP
```

**Option C: Direct connection troubleshooting**
```powershell
# Check if EQ12 can be DHCP server temporarily
.\eq12_pi_dhcp_helper.ps1
```

### **Step 4: Set Static IP via SSH**
Once connected to Pi:
```bash
# Configure static IP for EQ12 cluster
sudo nano /etc/dhcpcd.conf

# Add these lines to the end:
interface eth0
static ip_address=192.168.100.2/24
static routers=192.168.100.1
static domain_name_servers=8.8.8.8 8.8.4.4

# Save and reboot
sudo reboot
```

##  **This is the REAL-WORLD method that actually works!**

**Why this approach works:**
-  Uses Pi Imager's actual capabilities
-  No complex USB file editing
-  Standard networking approach
-  Easy troubleshooting
-  Reliable and tested

**Expected timeline:**
- Flash: 5-10 minutes
- First boot: 2-3 minutes  
- Find Pi: 1-2 minutes
- Configure static IP: 2 minutes
- **Total: ~15 minutes**