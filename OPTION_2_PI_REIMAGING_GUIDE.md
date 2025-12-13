run# OPTION 2: Pi Re-imaging and Pre-Configuration Guide

##  BOOT FAILURE CONFIRMED
**Timestamp:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Issue:** Pi failed to respond after 13+ minutes of monitoring
**EQ12 Status:**  Network fully operational (Ethernet 3: Up, 1 Gbps, 192.168.100.1/24)

##  PRE-IMAGING CHECKLIST

### Hardware Verification
- [ ] Verify USB boot drive is properly connected to Pi
- [ ] Check Pi power LED (red) is solid
- [ ] Check Pi activity LED (green) shows boot activity
- [ ] Verify Ethernet cable connection between Pi and EQ12
- [ ] Confirm USB-Ethernet adapter is connected to EQ12

### Option 2A: Re-flash Existing USB Drive
1. **Remove USB drive from Pi**
2. **Connect to Windows PC**
3. **Download Raspberry Pi Imager:** https://rpi.org/imager
4. **Flash fresh Raspberry Pi OS (64-bit)**
5. **CRITICAL: Pre-configure before first boot**

### Option 2B: Use Different USB Drive
If current drive is corrupted:
1. **Get fresh USB 3.0 drive (32GB+ recommended)**
2. **Follow Option 2A steps**

##  PRE-CONFIGURATION STEPS (CRITICAL)

### Step 1: Enable SSH and Set Credentials
**Before ejecting USB from Windows:**

1. **Navigate to USB drive boot partition**
2. **Create file: `ssh` (no extension)**
   ```
   # This enables SSH on first boot
   ```

3. **Create file: `userconf.txt`**
   ```
   ricoj100:$6$rounds=4096$saltsalt$HASH_HERE
   ```
   
   **Generate password hash:**
   ```bash
   # On any Linux system or WSL:
   echo '102120sRO1!' | openssl passwd -6 -stdin
   ```

### Step 2: Network Pre-Configuration
**Create file: `wpa_supplicant.conf`**
```conf
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

# WiFi networks (if available)
network={
    ssid="YOUR_WIFI_NAME"
    psk="YOUR_WIFI_PASSWORD"
    priority=1
}
```

### Step 3: Static IP Configuration  
**Pi Imager doesn't support static IP in OS customization, so we configure it post-boot.**

**Option A: Via SSH after first boot (DHCP)**
```bash
# Connect via DHCP first, then configure static IP
sudo nano /etc/dhcpcd.conf
# Add to end of file:
interface eth0
static ip_address=192.168.100.2/24
static routers=192.168.100.1
static domain_name_servers=8.8.8.8
```

**Option B: Pre-configure on USB (Advanced)**
**Create file: `cmdline_static.txt`** (backup of cmdline.txt with static IP)
```
# This requires manual post-boot configuration
```

##  POST-FLASH BOOT PROCESS

### Expected Timeline
- **0-30 seconds:** Pi power-on, boot start
- **30-90 seconds:** Kernel loading, services starting  
- **90-120 seconds:** Network configuration, SSH ready
- **2-3 minutes:** Fully operational

### Monitoring Commands
```powershell
# Run this after inserting configured USB and powering Pi:
cd C:\EQ12\scripts
.\eq12_pi_boot_detector.ps1 -MaxMinutes 5
```

##  ALTERNATIVE: HEADLESS SETUP TOOL

### Option 2C: Use EQ12 Auto-Configuration
**If you have monitor/keyboard available:**

1. **Flash basic Raspberry Pi OS**
2. **Boot Pi with monitor connected**
3. **Complete initial setup manually**
4. **Run our auto-config from EQ12:**
   ```powershell
   .\eq12_pi_quicksetup.ps1 -IPAddress 192.168.100.2 -Username ricoj100 -Password '102120sRO1!'
   ```

##  SUPPORT ESCALATION

### If Option 2 Still Fails
1. **Hardware issue:** Pi 5 may be defective
2. **USB drive issue:** Try different USB 3.0 drive
3. **Network issue:** Test with different Ethernet cable
4. **Power issue:** Verify Pi power supply (5V/5A recommended)

### Alternative Configuration Methods
1. **Direct WiFi setup** (if available)
2. **Shared internet connection** through EQ12
3. **USB-to-Serial console** for direct access

---

##  RECOMMENDED NEXT STEPS

1. **Try Option 2A first** (re-flash existing USB)
2. **If that fails, use Option 2B** (different USB drive)  
3. **Monitor boot with our detector script**
4. **Escalate to hardware troubleshooting if needed**

**Remember:** The EQ12 side is confirmed working - the issue is purely Pi-side boot/network configuration.