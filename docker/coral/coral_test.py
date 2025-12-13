import time
import subprocess
from pycoral.utils.edgetpu import list_edge_tpus

print("=== USB Devices (lsusb) ===")
try:
    subprocess.run(["lsusb"], check=True)
except Exception as e:
    print(f"lsusb failed: {e}")

print("\nScanning for Edge TPU devices...")
try:
    devices = list_edge_tpus()
    if devices:
        print(f"SUCCESS: Found {len(devices)} Edge TPU device(s):")
        for device in devices:
            print(f" - {device}")
    else:
        print("FAILURE: No Edge TPU devices found.")
except Exception as e:
    print(f"Error during scan: {e}")
