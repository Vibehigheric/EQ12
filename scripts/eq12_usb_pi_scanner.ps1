[CmdletBinding()]
param()

<#
.SYNOPSIS
    EQ12 USB Port and Pi Detection Scanner

.DESCRIPTI            # PowerShell 5.1 compatible Test-Connection
            $pingResult = $false
            try {
                $ping = New-Object System.Net.NetworkInformation.Ping
                $reply = $ping.Send($testIP, 1000)
                $pingResult = ($reply.Status -eq 'Success')
                $ping.Dispose()
            } catch {
                $pingResult = $false
            }N
    Scans all USB ports and network adapters to detect Raspberry Pi connection
    and provide detailed hardware analysis.
#>

function Write-ScanLog {
    param(
        [string]$Message,
        [string]$Level = 'INFO'
    )
    
    $colors = @{
        'INFO' = 'Cyan'
        'SUCCESS' = 'Green'
        'WARNING' = 'Yellow'
        'ERROR' = 'Red'
    }
    
    Write-Host "[$Level] $Message" -ForegroundColor $colors[$Level]
}

function Get-USBDeviceDetails {
    Write-ScanLog "=== USB DEVICE SCAN ===" "SUCCESS"
    
    try {
        $usbDevices = Get-WmiObject -Class Win32_USBControllerDevice | ForEach-Object {
            [WMI]$_.Dependent
        } | Where-Object {$_.DeviceID -like "USB\*"}
        
        foreach ($device in $usbDevices) {
            if ($device.Name -like "*Ethernet*" -or $device.Name -like "*Network*" -or $device.Name -like "*Realtek*") {
                Write-ScanLog "NETWORK USB DEVICE FOUND:" "SUCCESS"
                Write-ScanLog "  Name: $($device.Name)"
                Write-ScanLog "  Device ID: $($device.DeviceID)"
                Write-ScanLog "  Status: $($device.Status)"
                Write-ScanLog "  Manufacturer: $($device.Manufacturer)"
                Write-Host ""
            }
        }
    } catch {
        Write-ScanLog "Error scanning USB devices: $($_.Exception.Message)" "ERROR"
    }
}

function Get-EthernetAdapterDetails {
    Write-ScanLog "=== ETHERNET ADAPTER SCAN ===" "SUCCESS"
    
    $adapters = Get-NetAdapter | Where-Object {$_.Name -like "*Ethernet*"}
    
    foreach ($adapter in $adapters) {
        Write-ScanLog "ADAPTER: $($adapter.Name)" "INFO"
        Write-ScanLog "  Status: $($adapter.Status)"
        Write-ScanLog "  Interface: $($adapter.InterfaceDescription)"
        Write-ScanLog "  Link Speed: $($adapter.LinkSpeed)"
        Write-ScanLog "  Media Type: $($adapter.MediaType)"
        
        # Check for physical connection
        if ($adapter.Status -eq "Up") {
            Write-ScanLog "  [CONNECTED] Physical link detected!" "SUCCESS"
        } elseif ($adapter.MediaConnectState -eq "Connected") {
            Write-ScanLog "  [CABLE DETECTED] Cable connected but no link" "WARNING"
        } else {
            Write-ScanLog "  [DISCONNECTED] No cable or device detected" "INFO"
        }
        
        # Get hardware details
        try {
            $adapterStats = Get-NetAdapterStatistics -Name $adapter.Name -ErrorAction SilentlyContinue
            if ($adapterStats) {
                Write-ScanLog "  RX Bytes: $($adapterStats.ReceivedBytes)"
                Write-ScanLog "  TX Bytes: $($adapterStats.SentBytes)"
                Write-ScanLog "  RX Packets: $($adapterStats.ReceivedUnicastPackets)"
                Write-ScanLog "  TX Packets: $($adapterStats.SentUnicastPackets)"
            }
        } catch {
            Write-ScanLog "  Could not get statistics" "WARNING"
        }
        
        Write-Host ""
    }
}

function Test-PiAutoDetection {
    Write-ScanLog "=== PI AUTO-DETECTION TEST ===" "SUCCESS"
    
    # Test common Pi IP ranges
    $piRanges = @("192.168.1.", "192.168.0.", "10.0.0.", "172.16.0.")
    $found = $false
    
    foreach ($range in $piRanges) {
        for ($i = 1; $i -le 254; $i++) {
            $testIP = "$range$i"
            
            # PowerShell 5.1 compatible ping test
            $ping = $false
            try {
                $pingObj = New-Object System.Net.NetworkInformation.Ping
                $reply = $pingObj.Send($testIP, 1000)
                $ping = ($reply.Status -eq 'Success')
                $pingObj.Dispose()
            } catch {
                $ping = $false
            }
            
            if ($ping) {
                Write-ScanLog "POTENTIAL PI FOUND: $testIP" "SUCCESS"
                
                # Test for SSH (Pi usually has SSH on port 22)
                try {
                    $sshTest = Test-NetConnection -ComputerName $testIP -Port 22 -WarningAction SilentlyContinue -InformationLevel Quiet
                    if ($sshTest.TcpTestSucceeded) {
                        Write-ScanLog "  SSH PORT OPEN - Likely Raspberry Pi!" "SUCCESS"
                        
                        # Try to get hostname
                        try {
                            $hostname = [System.Net.Dns]::GetHostEntry($testIP).HostName
                            Write-ScanLog "  Hostname: $hostname"
                            if ($hostname -like "*raspberrypi*" -or $hostname -like "*rpi*") {
                                Write-ScanLog "  CONFIRMED: Raspberry Pi detected!" "SUCCESS"
                            }
                        } catch {
                            Write-ScanLog "  Could not resolve hostname" "INFO"
                        }
                        
                        $found = $true
                    }
                } catch {
                    Write-ScanLog "  SSH test failed" "INFO"
                }
            }
        }
        
        if ($found) { break }
    }
    
    if (-not $found) {
        Write-ScanLog "No Raspberry Pi detected on common networks" "WARNING"
        Write-ScanLog "Pi may need network configuration first" "INFO"
    }
}

function Get-NetworkPriorityStatus {
    Write-ScanLog "=== NETWORK PRIORITY STATUS ===" "SUCCESS"
    
    $interfaces = Get-NetIPInterface | Where-Object {$_.AddressFamily -eq "IPv4" -and $_.ConnectionState -eq "Connected"} | Sort-Object InterfaceMetric
    
    Write-ScanLog "Current Network Priority (lower metric = higher priority):"
    foreach ($interface in $interfaces) {
        $adapter = Get-NetAdapter -InterfaceIndex $interface.InterfaceIndex
        $ipConfig = Get-NetIPAddress -InterfaceIndex $interface.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
        
        $priority = switch ($interface.InterfaceMetric) {
            {$_ -le 10} { "PRIMARY" }
            {$_ -le 30} { "SECONDARY" }
            default { "BACKUP" }
        }
        
        Write-ScanLog "  [$priority] $($adapter.Name) (Metric: $($interface.InterfaceMetric))"
        if ($ipConfig) {
            Write-ScanLog "    IP: $($ipConfig.IPAddress)"
        }
    }
}

function Show-RecommendedActions {
    Write-ScanLog "=== RECOMMENDED ACTIONS ===" "SUCCESS"
    
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Run network priority setup:" -ForegroundColor White
    Write-Host "   C:\EQ12\SETUP_NETWORK_PRIORITY.bat" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. If Pi not detected, configure Pi networking:" -ForegroundColor White
    Write-Host "   Follow: C:\EQ12\PI_ETHERNET_SETUP_INSTRUCTIONS.md" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Test Pi connection:" -ForegroundColor White
    Write-Host "   .\eq12_pi_connectivity_test.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. Add Pi to EQ12 cluster:" -ForegroundColor White
    Write-Host "   python eq12_raspberry_pi_cluster_manager.py --add-node <pi_ip>" -ForegroundColor Cyan
    Write-Host ""
}

# Main execution
Clear-Host
Write-Host @"
EQ12 USB & Network Detection Scanner
===================================
Scanning for Raspberry Pi and network configuration
"@ -ForegroundColor Green

Write-Host ""

# Run all scans
Get-USBDeviceDetails
Get-EthernetAdapterDetails
Get-NetworkPriorityStatus
Test-PiAutoDetection
Show-RecommendedActions

Write-ScanLog "Scan completed!" "SUCCESS"