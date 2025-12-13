#Requires -RunAsAdministrator
<#
.SYNOPSIS
EQ12 Raspberry Pi USB-to-Ethernet Configuration Script

.DESCRIPTION
Configures the USB-to-Ethernet adapter for Raspberry Pi communication
Sets up static IP addressing and Internet Connection Sharing (ICS)

.PARAMETER Action
Action to perform: Configure, Test, or Reset

.PARAMETER PiIP
IP address to assign to the Pi (default: 192.168.100.2)

.PARAMETER HostIP
IP address for the host adapter (default: 192.168.100.1)

.EXAMPLE
.\eq12_pi_usb_ethernet_setup.ps1 -Action Configure
.\eq12_pi_usb_ethernet_setup.ps1 -Action Test -PiIP 192.168.100.2
#>

[CmdletBinding()]
param(
    [ValidateSet("Configure", "Test", "Reset")]
    [string]$Action = "Configure",
    
    [string]$PiIP = "192.168.100.2",
    
    [string]$HostIP = "192.168.100.1",
    
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$timestampUtc = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
$logFile = "C:\EQ12\logs\pi_usb_ethernet_setup_$($timestampUtc.Replace(':', '').Replace('-', '')).json"

function Write-LogEntry {
    param([string]$Level, [string]$Message, [hashtable]$Data = @{})
    
    $entry = @{
        timestamp = $timestampUtc
        level = $Level
        message = $Message
        data = $Data
        script = "eq12_pi_usb_ethernet_setup.ps1"
        action = $Action
    }
    
    if ($Verbose -or $Level -eq "ERROR") {
        Write-Host "[$Level] $Message" -ForegroundColor $(if($Level -eq "ERROR") {"Red"} elseif($Level -eq "WARNING") {"Yellow"} else {"Green"})
    }
    
    try {
        $entry | ConvertTo-Json -Depth 3 | Out-File -FilePath $logFile -Append -Encoding UTF8
    } catch { }
}

function Find-USBEthernetAdapter {
    Write-LogEntry "INFO" "Searching for USB Ethernet adapters..."
    
    $usbAdapters = Get-NetAdapter | Where-Object {
        $_.InterfaceDescription -like "*USB*" -and 
        $_.InterfaceDescription -like "*Ethernet*" -or
        $_.InterfaceDescription -like "*Realtek USB*"
    }
    
    if ($usbAdapters) {
        foreach ($adapter in $usbAdapters) {
            Write-LogEntry "INFO" "Found USB Ethernet adapter" @{
                Name = $adapter.Name
                Description = $adapter.InterfaceDescription
                Status = $adapter.Status
                MacAddress = $adapter.MacAddress
            }
        }
        return $usbAdapters[0]  # Return first found
    }
    
    Write-LogEntry "WARNING" "No USB Ethernet adapters found"
    return $null
}

function Configure-USBEthernet {
    param($Adapter)
    
    Write-LogEntry "INFO" "Configuring USB Ethernet adapter: $($Adapter.Name)"
    
    try {
        # Remove existing IP configuration
        Write-LogEntry "INFO" "Removing existing IP configuration..."
        Remove-NetIPAddress -InterfaceIndex $Adapter.ifIndex -Confirm:$false -ErrorAction SilentlyContinue
        Remove-NetRoute -InterfaceIndex $Adapter.ifIndex -Confirm:$false -ErrorAction SilentlyContinue
        
        # Set static IP
        Write-LogEntry "INFO" "Setting static IP: $HostIP/24"
        New-NetIPAddress -InterfaceIndex $Adapter.ifIndex -IPAddress $HostIP -PrefixLength 24 -ErrorAction Stop
        
        # Enable the adapter
        Enable-NetAdapter -Name $Adapter.Name -ErrorAction SilentlyContinue
        
        Write-LogEntry "SUCCESS" "USB Ethernet configured successfully" @{
            adapter = $Adapter.Name
            hostIP = $HostIP
            subnet = "192.168.100.0/24"
        }
        
        return $true
    } catch {
        Write-LogEntry "ERROR" "Failed to configure USB Ethernet" @{
            error = $_.Exception.Message
            adapter = $Adapter.Name
        }
        return $false
    }
}

function Test-PiConnectivity {
    Write-LogEntry "INFO" "Testing Pi connectivity at $PiIP..."
    
    # Test basic ping
    try {
        $ping = New-Object System.Net.NetworkInformation.Ping
        $reply = $ping.Send($PiIP, 3000)
        $pingSuccess = ($reply.Status -eq 'Success')
        $ping.Dispose()
        
        if ($pingSuccess) {
            Write-LogEntry "SUCCESS" "Pi responds to ping" @{
                piIP = $PiIP
                roundTripTime = $reply.RoundtripTime
            }
        } else {
            Write-LogEntry "WARNING" "Pi does not respond to ping" @{
                piIP = $PiIP
                status = $reply.Status
            }
        }
        
        return $pingSuccess
    } catch {
        Write-LogEntry "ERROR" "Ping test failed" @{
            error = $_.Exception.Message
            piIP = $PiIP
        }
        return $false
    }
}

function Test-SSHConnectivity {
    Write-LogEntry "INFO" "Testing SSH connectivity to Pi..."
    
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $connectTask = $tcpClient.ConnectAsync($PiIP, 22)
        $timeout = 5000  # 5 seconds
        
        if ($connectTask.Wait($timeout)) {
            $sshAvailable = $tcpClient.Connected
            $tcpClient.Close()
            
            if ($sshAvailable) {
                Write-LogEntry "SUCCESS" "SSH service available on Pi" @{
                    piIP = $PiIP
                    port = 22
                }
            } else {
                Write-LogEntry "WARNING" "SSH connection failed" @{
                    piIP = $PiIP
                    port = 22
                }
            }
            
            return $sshAvailable
        } else {
            Write-LogEntry "WARNING" "SSH connection timeout" @{
                piIP = $PiIP
                timeout = $timeout
            }
            $tcpClient.Close()
            return $false
        }
    } catch {
        Write-LogEntry "ERROR" "SSH test failed" @{
            error = $_.Exception.Message
            piIP = $PiIP
        }
        return $false
    }
}

function Enable-InternetSharing {
    param($USBAdapter)
    
    Write-LogEntry "INFO" "Attempting to enable Internet Connection Sharing..."
    
    try {
        # Get the primary internet adapter (usually Wi-Fi with highest metric)
        $internetAdapter = Get-NetAdapter | Where-Object {
            $_.Status -eq "Up" -and 
            $_.InterfaceDescription -like "*Wi-Fi*"
        } | Select-Object -First 1
        
        if (-not $internetAdapter) {
            Write-LogEntry "WARNING" "No active internet adapter found for sharing"
            return $false
        }
        
        Write-LogEntry "INFO" "Setting up ICS" @{
            sourceAdapter = $internetAdapter.Name
            targetAdapter = $USBAdapter.Name
        }
        
        # This requires additional COM setup which is complex
        # For now, just document the manual steps
        Write-LogEntry "INFO" "Manual ICS setup required" @{
            instructions = @(
                "1. Open Network and Sharing Center",
                "2. Click 'Change adapter settings'",
                "3. Right-click '$($internetAdapter.Name)' adapter",
                "4. Select Properties > Sharing tab",
                "5. Check 'Allow other network users to connect'",
                "6. Select '$($USBAdapter.Name)' from dropdown",
                "7. Click OK"
            )
        }
        
        return $true
    } catch {
        Write-LogEntry "ERROR" "ICS setup failed" @{
            error = $_.Exception.Message
        }
        return $false
    }
}

# Main execution
Write-LogEntry "INFO" "Starting Pi USB Ethernet setup" @{
    action = $Action
    piIP = $PiIP
    hostIP = $HostIP
}

switch ($Action) {
    "Configure" {
        $adapter = Find-USBEthernetAdapter
        if ($adapter) {
            $success = Configure-USBEthernet -Adapter $adapter
            if ($success) {
                Enable-InternetSharing -USBAdapter $adapter
                
                Write-LogEntry "INFO" "Configuration complete, testing connectivity..."
                Start-Sleep -Seconds 3
                
                $pingSuccess = Test-PiConnectivity
                $sshSuccess = Test-SSHConnectivity
                
                Write-LogEntry "SUCCESS" "Setup completed" @{
                    pingWorking = $pingSuccess
                    sshWorking = $sshSuccess
                    adapterConfigured = $true
                }
                
                if (-not $pingSuccess) {
                    Write-LogEntry "INFO" "Pi setup instructions" @{
                        message = "Pi may need manual network configuration"
                        piCommands = @(
                            "sudo nano /etc/dhcpcd.conf",
                            "Add: interface eth0",
                            "Add: static ip_address=$PiIP/24",
                            "Add: static routers=$HostIP",
                            "Add: static domain_name_servers=$HostIP 8.8.8.8",
                            "sudo reboot"
                        )
                    }
                }
            }
        } else {
            Write-LogEntry "ERROR" "No USB Ethernet adapter found"
        }
    }
    
    "Test" {
        $pingSuccess = Test-PiConnectivity
        $sshSuccess = Test-SSHConnectivity
        
        Write-LogEntry "SUCCESS" "Connectivity test completed" @{
            pingWorking = $pingSuccess
            sshWorking = $sshSuccess
        }
    }
    
    "Reset" {
        $adapter = Find-USBEthernetAdapter
        if ($adapter) {
            Write-LogEntry "INFO" "Resetting adapter configuration..."
            Remove-NetIPAddress -InterfaceIndex $adapter.ifIndex -Confirm:$false -ErrorAction SilentlyContinue
            Remove-NetRoute -InterfaceIndex $adapter.ifIndex -Confirm:$false -ErrorAction SilentlyContinue
            Disable-NetAdapter -Name $adapter.Name -Confirm:$false -ErrorAction SilentlyContinue
            
            Write-LogEntry "SUCCESS" "Adapter reset completed"
        }
    }
}

Write-LogEntry "SUCCESS" "Script execution completed" @{
    logFile = $logFile
    action = $Action
}

Write-Host "`n=== Pi USB Ethernet Setup Complete ===" -ForegroundColor Green
Write-Host "Log file: $logFile" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Test connectivity: .\eq12_pi_usb_ethernet_setup.ps1 -Action Test" -ForegroundColor White
Write-Host "2. Add to cluster: python eq12_raspberry_pi_cluster_manager.py --add-node $PiIP" -ForegroundColor White