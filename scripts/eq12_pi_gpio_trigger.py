#!/usr/bin/env python3
"""
EQ12 Raspberry Pi GPIO Power Controller
Provides USB relay and GPIO-based power control for Pi 5 nodes
"""

import argparse
import json
import logging
import time
import sys
from datetime import datetime
from pathlib import Path

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False

class EQ12PowerController:
    def __init__(self, config_path="C:/EQ12/configs/power_control_config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.setup_logging()
        
    def load_config(self):
        """Load power control configuration"""
        default_config = {
            "devices": {
                "Pi5": {
                    "control_method": "usb_relay",
                    "device_id": "16c0:05df",  # Generic USB relay
                    "gpio_pin": 17,
                    "power_cycle_delay": 2.0,
                    "boot_timeout": 120
                }
            },
            "usb_relay": {
                "vendor_id": "0x16c0",
                "product_id": "0x05df",
                "on_command": b'\xA0\x01\x01\xA2',
                "off_command": b'\xA0\x01\x00\xA1'
            },
            "serial_relay": {
                "port": "COM3",
                "baudrate": 9600,
                "timeout": 1.0
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"Warning: Could not load config: {e}")
                return default_config
        else:
            # Create default config
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def setup_logging(self):
        """Setup logging to EQ12 logs directory"""
        log_dir = Path("C:/EQ12/logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"power_control_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def find_usb_relay(self):
        """Find USB relay device"""
        if not USB_AVAILABLE:
            raise ImportError("pyusb not available. Install with: pip install pyusb")
        
        vendor_id = int(self.config["usb_relay"]["vendor_id"], 16)
        product_id = int(self.config["usb_relay"]["product_id"], 16)
        
        device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
        if device is None:
            self.logger.error(f"USB relay not found (VID: {vendor_id:04x}, PID: {product_id:04x})")
            return None
        
        # Detach kernel driver if necessary
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)
        
        device.set_configuration()
        return device
    
    def control_usb_relay(self, device, state):
        """Control USB relay state"""
        if state:
            command = self.config["usb_relay"]["on_command"]
            self.logger.info("USB Relay: ON")
        else:
            command = self.config["usb_relay"]["off_command"]
            self.logger.info("USB Relay: OFF")
        
        try:
            device.write(0x02, command)
            return True
        except Exception as e:
            self.logger.error(f"USB relay control failed: {e}")
            return False
    
    def find_serial_relay(self):
        """Find serial relay device"""
        if not SERIAL_AVAILABLE:
            raise ImportError("pyserial not available. Install with: pip install pyserial")
        
        port = self.config["serial_relay"]["port"]
        
        # Auto-detect if port is "AUTO"
        if port == "AUTO":
            ports = serial.tools.list_ports.comports()
            for p in ports:
                if "USB" in p.description or "Serial" in p.description:
                    port = p.device
                    break
            
            if port == "AUTO":
                self.logger.error("No suitable serial port found")
                return None
        
        try:
            ser = serial.Serial(
                port=port,
                baudrate=self.config["serial_relay"]["baudrate"],
                timeout=self.config["serial_relay"]["timeout"]
            )
            return ser
        except Exception as e:
            self.logger.error(f"Serial connection failed: {e}")
            return None
    
    def control_serial_relay(self, ser, state):
        """Control serial relay state"""
        if state:
            command = b'relay on\r\n'
            self.logger.info("Serial Relay: ON")
        else:
            command = b'relay off\r\n'
            self.logger.info("Serial Relay: OFF")
        
        try:
            ser.write(command)
            response = ser.readline()
            return b'OK' in response
        except Exception as e:
            self.logger.error(f"Serial relay control failed: {e}")
            return False
    
    def gpio_pulse(self, pin, duration=0.5):
        """Send GPIO pulse (simulated for Windows)"""
        self.logger.info(f"GPIO pulse on pin {pin} for {duration}s (simulated)")
        # In real implementation, this would control actual GPIO
        # For now, we simulate the timing
        time.sleep(duration)
        return True
    
    def power_cycle_device(self, device_name, method="auto"):
        """Power cycle a device"""
        if device_name not in self.config["devices"]:
            self.logger.error(f"Device {device_name} not configured")
            return False
        
        device_config = self.config["devices"][device_name]
        
        if method == "auto":
            method = device_config["control_method"]
        
        self.logger.info(f"Power cycling {device_name} using {method}")
        
        success = False
        
        if method == "usb_relay":
            relay = self.find_usb_relay()
            if relay:
                # Power off
                self.control_usb_relay(relay, False)
                time.sleep(device_config["power_cycle_delay"])
                # Power on
                success = self.control_usb_relay(relay, True)
        
        elif method == "serial_relay":
            ser = self.find_serial_relay()
            if ser:
                # Power off
                self.control_serial_relay(ser, False)
                time.sleep(device_config["power_cycle_delay"])
                # Power on
                success = self.control_serial_relay(ser, True)
                ser.close()
        
        elif method == "gpio":
            pin = device_config["gpio_pin"]
            success = self.gpio_pulse(pin, 0.5)
        
        if success:
            self.logger.info(f"{device_name} power cycle initiated")
            return True
        else:
            self.logger.error(f"{device_name} power cycle failed")
            return False
    
    def power_on_device(self, device_name):
        """Power on a device"""
        if device_name not in self.config["devices"]:
            self.logger.error(f"Device {device_name} not configured")
            return False
        
        device_config = self.config["devices"][device_name]
        method = device_config["control_method"]
        
        self.logger.info(f"Powering on {device_name} using {method}")
        
        if method == "usb_relay":
            relay = self.find_usb_relay()
            if relay:
                return self.control_usb_relay(relay, True)
        
        elif method == "serial_relay":
            ser = self.find_serial_relay()
            if ser:
                success = self.control_serial_relay(ser, True)
                ser.close()
                return success
        
        return False
    
    def power_off_device(self, device_name):
        """Power off a device"""
        if device_name not in self.config["devices"]:
            self.logger.error(f"Device {device_name} not configured")
            return False
        
        device_config = self.config["devices"][device_name]
        method = device_config["control_method"]
        
        self.logger.info(f"Powering off {device_name} using {method}")
        
        if method == "usb_relay":
            relay = self.find_usb_relay()
            if relay:
                return self.control_usb_relay(relay, False)
        
        elif method == "serial_relay":
            ser = self.find_serial_relay()
            if ser:
                success = self.control_serial_relay(ser, False)
                ser.close()
                return success
        
        return False

def main():
    parser = argparse.ArgumentParser(description="EQ12 Pi Power Controller")
    parser.add_argument("--device", default="Pi5", help="Target device name")
    parser.add_argument("--action", choices=["power-on", "power-off", "power-cycle"], 
                       default="power-cycle", help="Power action")
    parser.add_argument("--method", choices=["usb_relay", "serial_relay", "gpio", "auto"], 
                       default="auto", help="Control method")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    controller = EQ12PowerController()
    
    if args.action == "power-on":
        success = controller.power_on_device(args.device)
    elif args.action == "power-off":
        success = controller.power_off_device(args.device)
    elif args.action == "power-cycle":
        success = controller.power_cycle_device(args.device, args.method)
    
    if success:
        print(f" {args.action} successful for {args.device}")
        sys.exit(0)
    else:
        print(f" {args.action} failed for {args.device}")
        sys.exit(1)

if __name__ == "__main__":
    main()