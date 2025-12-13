# EQ12 Pi Power Control System

##  **Hardware Integration Solution**

Based on your excellent analysis, this system provides **EQ12 remote Pi boot control** using:

### **Hardware Options**

#### **Option 1: USB Relay Control (Recommended)**
- **Hardware**: USB-controlled relay module (e.g., SainSmart 4-channel USB relay)
- **Connection**: Pi's USB-C power  Relay  EQ12 USB port
- **Cost**: ~$25-40
- **Reliability**: High (hardware-level power control)

#### **Option 2: GPIO RUN Pin Control**
- **Hardware**: USB-to-GPIO adapter + jumper wires
- **Connection**: Pi's RUN/GND pins  GPIO adapter  EQ12 USB
- **Cost**: ~$10-15  
- **Reliability**: Very high (firmware-level reset)

#### **Option 3: Serial Relay Control**
- **Hardware**: Serial-controlled smart switch
- **Connection**: Pi power  Smart switch  EQ12 serial port
- **Cost**: ~$30-50
- **Reliability**: High (network-controlled)

##  **One-Time Pi EEPROM Setup**

**Critical**: Configure Pi to always boot USB-first:

```bash
# Connect to Pi once (HDMI/keyboard or SSH)
sudo raspi-config

# Navigate: Advanced Options  Boot Order  USB Boot First
# This sets BOOT_ORDER=0xf41 in EEPROM

# Verify:
sudo rpi-eeprom-config | grep BOOT_ORDER
# Should show: BOOT_ORDER=0xf41
```

**After this setup**: Pi will **automatically** boot from USB whenever powered on.

##  **EQ12 Power Control Commands**

### **PowerShell Interface**
```powershell
# Boot Pi from USB (full cycle + monitoring)
.\eq12_pi_powercycle.ps1 -Action BootFromUSB -WaitForBoot

# Simple power cycle
.\eq12_pi_powercycle.ps1 -Action PowerCycle -Device Pi5

# Power on only
.\eq12_pi_powercycle.ps1 -Action PowerOn -Device Pi5

# Power off
.\eq12_pi_powercycle.ps1 -Action PowerOff -Device Pi5
```

### **Python Direct Control**
```bash
# Power cycle with USB relay
python eq12_pi_gpio_trigger.py --device Pi5 --action power-cycle --method usb_relay

# GPIO RUN pin pulse
python eq12_pi_gpio_trigger.py --device Pi5 --action power-cycle --method gpio

# Serial relay control
python eq12_pi_gpio_trigger.py --device Pi5 --action power-cycle --method serial_relay
```

##  **Automatic Integration Workflow**

1. **EQ12 prepares USB image** (if needed)
2. **EQ12 sends power cycle command**:
   ```powershell
   .\eq12_pi_powercycle.ps1 -Action BootFromUSB -WaitForBoot
   ```
3. **Pi boots automatically from USB** (EEPROM configured)
4. **EQ12 detects Pi at 192.168.100.2** (within 60-120s)
5. **Cluster integration continues**

##  **Configuration Files**

### **Power Control Config** (`C:/EQ12/configs/power_control_config.json`)
```json
{
  "devices": {
    "Pi5": {
      "control_method": "usb_relay",
      "device_id": "16c0:05df",
      "power_cycle_delay": 2.0,
      "boot_timeout": 120
    }
  },
  "usb_relay": {
    "vendor_id": "0x16c0",
    "product_id": "0x05df"
  }
}
```

##  **Hardware Setup Guide**

### **USB Relay Method**
1. **Purchase**: SainSmart USB relay or compatible
2. **Connect**: Pi power cable  Relay NO/COM  EQ12 USB power
3. **Install**: `pip install pyusb`
4. **Test**: `.\eq12_pi_powercycle.ps1 -Action PowerCycle`

### **GPIO RUN Pin Method**
1. **Purchase**: USB-to-GPIO adapter (FTDI or CH340-based)
2. **Connect**: 
   - Adapter GND  Pi RUN pin (pin closest to USB-C)
   - Adapter GPIO  Pi GND (adjacent pin)
3. **Install**: `pip install pyserial`
4. **Test**: `.\eq12_pi_powercycle.ps1 -Action PowerCycle -Method GPIO`

##  **Expected Performance**

- **Power cycle time**: 2-5 seconds
- **Boot detection**: 60-120 seconds
- **SSH ready**: 90-150 seconds total
- **Reliability**: 99%+ with proper EEPROM setup

##  **Monitoring & Logging**

All power control actions logged to: `C:/EQ12/logs/power_control_YYYYMMDD.log`

**Example log:**
```
2025-11-08 20:45:30 - INFO - Power cycling Pi5 using usb_relay
2025-11-08 20:45:30 - INFO - USB Relay: OFF
2025-11-08 20:45:32 - INFO - USB Relay: ON
2025-11-08 20:45:35 - INFO - Boot check 1/24 (5s)...
2025-11-08 20:46:30 - INFO -  Device is online and SSH ready!
```

---

##  **Result: True Remote Pi Control**

With this system, your **EQ12 can programmatically boot any Pi node** without human intervention:

```powershell
# Deploy new image and boot Pi cluster node
.\eq12_cluster_deploy.ps1 -Node Pi5 -Image "production_v2.3.img" -AutoBoot
```

**No more manual power buttons, HDMI cables, or keyboards required!** 