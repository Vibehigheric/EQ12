#!/usr/bin/env python3
"""
Coral TPU Device Detection and Setup
Generated: 2025-11-07T13:02:24.457486
"""

import sys
import subprocess
import logging
from pathlib import Path

def detect_coral_device():
    """Detect and configure Coral TPU device"""
    
    print(" Detecting Google Coral TPU device...")
    
    try:
        # Try importing Coral libraries
        from pycoral.utils.edgetpu import make_interpreter
        from pycoral.utils.edgetpu import list_edge_tpus
        
        # List available Edge TPU devices
        devices = list_edge_tpus()
        
        if devices:
            print(f" Found {len(devices)} Coral device(s):")
            for i, device in enumerate(devices):
                print(f"   {i+1}. {device}")
            
            # Test basic inference
            try:
                interpreter = make_interpreter(model_path=None, device=devices[0])
                print(" Coral TPU ready for inference")
                return True
            except Exception as e:
                print(f" Coral device found but not ready: {e}")
                return False
        else:
            print(" No Coral TPU devices detected")
            print(" Troubleshooting:")
            print("   1. Ensure Coral USB Accelerator is connected")
            print("   2. Check USB cable and port")
            print("   3. Install Coral drivers if needed")
            print("   4. Try different USB port (USB 3.0 recommended)")
            return False
            
    except ImportError as e:
        print(f" Coral libraries not available: {e}")
        print(" Install with: pip install pycoral tflite-runtime")
        return False
    
    except Exception as e:
        print(f" Error detecting Coral device: {e}")
        return False

def install_coral_drivers():
    """Install Coral TPU drivers on Windows"""
    
    print(" Installing Coral TPU drivers...")
    
    try:
        # Download Coral drivers
        import requests
        
        driver_url = "https://github.com/google-coral/libedgetpu/releases/download/release-frogfish/edgetpu_runtime_20221024.zip"
        driver_file = Path("coral_drivers.zip")
        
        print(f" Downloading drivers from {driver_url}...")
        response = requests.get(driver_url, stream=True)
        
        with open(driver_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(" Drivers downloaded successfully")
        print(" Extract and run install.bat as Administrator")
        
        return True
        
    except Exception as e:
        print(f" Driver download failed: {e}")
        return False

if __name__ == "__main__":
    print(" Coral TPU Detection and Setup")
    print("=" * 40)
    
    # Detect device
    device_ready = detect_coral_device()
    
    if not device_ready:
        # Try to install drivers
        install_coral_drivers()
    
    print("=" * 40)
