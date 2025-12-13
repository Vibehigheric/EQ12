# EQ12 USB Device Scanner

**Complete USB port and device detection system for Windows**

Automatically identifies:
- USB 2.0 / 3.0 / 3.1 / 3.2 / Type-C ports
- Device VID/PID, manufacturer, product name
- Port speed (1.5 Mbps → 20 Gbps)
- Storage devices with drive letters
- Real-time plug/unplug monitoring

---

## Quick Start

### 1. Build the Project

**Visual Studio 2022:**
```
File → New → Project → Console App (.NET 6.0 or .NET 8.0)
Name: Eq12UsbScanner
Language: Visual Basic
```

Add files:
- `UsbDeviceScanner.vb`
- `Program.vb`

Build: `Ctrl+Shift+B`

**Command Line:**
```powershell
cd C:\EQ12_BROKEN_20251122_210342\vb_usb_scanner
dotnet new console -lang VB -n Eq12UsbScanner
# Replace Program.vb with the provided files
dotnet build
```

---

## Usage

### Standard Scan
```powershell
.\Eq12UsbScanner.exe
```

**Output:**
```
=== EQ12 USB DEVICE SCANNER REPORT ===
Scan Time: 2025-11-27 12:30:45

Total USB Devices Detected: 5

----------------------------------------
Device: USB 3.0 SuperSpeed Device
Manufacturer: Generic
VID: 0781  PID: 5583
Class: DiskDrive
Speed: 5 Gbps (USB 3.0/3.1 Gen 1)
Port Type: USB Type-B
Drive Letters: E:\, F:\
Device Path: USB\VID_0781&PID_5583\...
----------------------------------------
```

### Monitor Mode (Real-Time Events)
```powershell
.\Eq12UsbScanner.exe --monitor
```

**Output:**
```
[Monitor Mode] Watching for USB device changes...
Press Ctrl+C to stop.

[12:31:02] Connected
  → SanDisk Ultra USB Device (0781:5583)
[12:32:15] Disconnected
```

### JSON Output (for Automation)
```powershell
.\Eq12UsbScanner.exe --json > usb_devices.json
```

**Output:**
```json
[
  {
    "vendorId": "0781",
    "productId": "5583",
    "devicePath": "USB\\VID_0781&PID_5583\\...",
    "manufacturer": "SanDisk",
    "productName": "Ultra USB Device",
    "deviceClass": "DiskDrive",
    "speed": "5 Gbps (USB 3.0/3.1 Gen 1)",
    "portType": "USB Type-B",
    "isRemovable": true,
    "driveLetters": ["E:\\", "F:\\"]
  }
]
```

---

## Integration with Fetch Engine

### 1. Detect USB Device in VB.NET Fetch Workflow

```vbnet
Imports System.Linq

Sub Main()
    Dim devices = UsbScanner.ScanAllUsbDevices()
    
    ' Find USB 3.0 Type-B device
    Dim targetDevice = devices.FirstOrDefault(
        Function(d) d.PortType.Contains("Type-B") AndAlso 
                   d.Speed.Contains("5 Gbps"))
    
    If targetDevice IsNot Nothing Then
        Console.WriteLine($"Found: {targetDevice.ProductName}")
        Console.WriteLine($"VID:PID = {targetDevice.VendorId}:{targetDevice.ProductId}")
        
        ' Use in fetch engine
        ConnectToDevice(targetDevice.DevicePath)
    End If
End Sub
```

### 2. Automated Drive Detection

```vbnet
Sub AutoMountUsbDrives()
    Dim devices = UsbScanner.ScanAllUsbDevices()
    
    For Each dev In devices
        If dev.IsRemovable AndAlso dev.DriveLetters.Count > 0 Then
            For Each letter In dev.DriveLetters
                Console.WriteLine($"Accessing drive {letter}")
                ProcessDriveData(letter)
            Next
        End If
    Next
End Sub

Sub ProcessDriveData(driveLetter As String)
    Dim files = IO.Directory.GetFiles(driveLetter)
    Console.WriteLine($"Found {files.Length} files on {driveLetter}")
End Sub
```

### 3. Continuous Monitoring Service

```vbnet
Imports System.Threading

Sub StartUsbMonitorService()
    Dim cts As New CancellationTokenSource()
    
    Task.Run(Sub()
        UsbScanner.MonitorUsbEvents(
            Sub(eventType, isConnected)
                If isConnected Then
                    Console.WriteLine("New device connected - triggering fetch workflow")
                    TriggerDataFetch()
                End If
            End Sub
        )
    End Sub, cts.Token)
    
    Console.WriteLine("USB Monitor Service running...")
    Console.ReadKey()
    cts.Cancel()
End Sub
```

---

## Device Type Detection

| Port Type Detected | Cable Required | Typical Use Case |
|-------------------|---------------|------------------|
| USB Type-B 3.0 | USB-A ↔ Type-B | External HDD, RAID enclosure |
| USB Type-C | USB-C ↔ USB-C | Modern laptops, hubs, SSDs |
| USB Type-A | Standard USB | Mouse, keyboard, flash drive |
| USB Micro | USB-A ↔ Micro | Older phones, cameras |

---

## Speed Classification

| Detected Speed | Standard | Max Rate |
|---------------|---------|----------|
| 1.5 Mbps | USB 1.0 Low-Speed | Keyboards, mice |
| 12 Mbps | USB 1.1 Full-Speed | Audio devices |
| 480 Mbps | USB 2.0 High-Speed | Webcams, printers |
| 5 Gbps | USB 3.0 / 3.1 Gen 1 | External drives |
| 10 Gbps | USB 3.1 Gen 2 / 3.2 Gen 2 | NVMe enclosures |
| 20 Gbps | USB 3.2 Gen 2x2 | High-speed RAID |

---

## Troubleshooting

### Issue: "No devices found"
**Fix:**
```powershell
# Run as Administrator
Right-click → Run as administrator
```

### Issue: "Access denied" on monitoring
**Fix:**
```powershell
# Requires elevated permissions for WMI event watchers
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Issue: Wrong drive letters detected
**Fix:**
The simple drive detection uses `DriveInfo.GetDrives()`. For precise matching:

```vbnet
' Add WMI query to match drive serial number to USB device
Dim query = $"ASSOCIATORS OF {{Win32_DiskDrive.DeviceID='\\.\PHYSICALDRIVE0'}} WHERE AssocClass=Win32_DiskDriveToDiskPartition"
' ... parse partition associations
```

---

## Next Steps

### A. Create Windows Service Version
```powershell
# Service that logs all USB events to SQLite
dotnet new worker -lang VB -n Eq12UsbService
# Add UsbDeviceScanner.vb + background service logic
```

### B. Add WinUSB Communication
```vbnet
' NuGet: MadWizard.WinUSB
Imports MadWizard.WinUSB

Dim device As New USBDevice(targetDevice.DevicePath)
Dim reader = device.OpenPipeReader(device.Pipes.InPipe)
Dim buffer(4096) As Byte
Dim bytesRead = reader.Read(buffer, 0, buffer.Length)
```

### C. Integrate with n8n Automation
```powershell
# HTTP webhook when new device detected
Invoke-RestMethod -Uri "http://localhost:5678/webhook/usb-event" `
    -Method POST `
    -Body (@{device=$targetDevice} | ConvertTo-Json) `
    -ContentType "application/json"
```

---

## GitHub Copilot Integration

Paste into VS Code Copilot Chat:
```
@workspace Scan my EQ12 system for all USB devices using the UsbDeviceScanner module.
Generate a report showing:
- All connected USB 3.0/3.1/3.2 devices
- Port types (Type-A, Type-B, Type-C)
- Drive letters for removable storage
- Real-time monitoring of plug/unplug events

Then create a PowerShell wrapper that:
- Runs the scanner hourly via scheduled task
- Logs results to C:\EQ12\logs\usb_scan_YYYYMMDD_HHMMSS.json
- Alerts if any new unknown device is detected
```

---

## PowerShell Wrapper Example

```powershell
# EQ12_USB_SCAN.ps1
param([switch]$Monitor, [switch]$Json)

$scannerPath = "C:\EQ12_BROKEN_20251122_210342\vb_usb_scanner\bin\Release\net8.0\Eq12UsbScanner.exe"

if ($Monitor) {
    & $scannerPath --monitor
} elseif ($Json) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $logFile = "C:\EQ12\logs\usb_scan_$timestamp.json"
    & $scannerPath --json | Out-File -FilePath $logFile -Encoding UTF8
    Write-Host "Saved to $logFile" -ForegroundColor Green
} else {
    & $scannerPath
}
```

---

**Ready to build?**

1. Open Visual Studio 2022
2. Create new VB.NET Console App (.NET 8.0)
3. Copy `UsbDeviceScanner.vb` + `Program.vb`
4. Build → Run
5. See all your USB devices instantly!
