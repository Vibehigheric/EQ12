#Requires -RunAsAdministrator
<#
.SYNOPSIS
EQ12 USB Controller Driver and Network Configuration Script

.DESCRIPTION
Ensures USB controllers have all drivers, configures network adapters,
and establishes Pi connectivity over USB-to-Ethernet

.EXAMPLE
.\eq12_usb_driver_network_setup.ps1
#>

[CmdletBinding()]
param(
    [switch]$UpdateDrivers,
    [switch]$ForceReinstall
)

$ErrorActionPreference = "Continue"
$timestampUtc = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
$logFile = "C:\EQ12\logs\usb_driver_network_setup_$($timestampUtc.Replace(':', '').Replace('-', '')).json"

function Write-LogEntry {
    param([string]$Level, [string]$Message, [hashtable]$Data = @{})
    
    $entry = @{
        timestamp = $timestampUtc
        level = $Level
        message = $Message
        data = $Data
        script = "eq12_usb_driver_network_setup.ps1"
    }
    
    Write-Host "[$Level] $Message" -ForegroundColor $(if($Level -eq "ERROR") {"Red"} elseif($Level -eq "WARNING") {"Yellow"} else {"Green"})
    
    try {
        $entry | ConvertTo-Json -Depth 3 | Out-File -FilePath $logFile -Append -Encoding UTF8
    } catch { }
}

function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-USBControllerStatus {
    Write-LogEntry "INFO" "Checking USB controller status..."
    
    $usbControllers = Get-PnpDevice -Class "USB" | Where-Object {$_.Status -ne "OK"}
    $networkAdapters = Get-PnpDevice -Class "Net" | Where-Object {$_.FriendlyName -like "*USB*"}
    
    $controllerInfo = @{
        problemControllers = $usbControllers.Count
        usbNetworkAdapters = $networkAdapters.Count
        adapters = @()
    }
    
    foreach ($adapter in $networkAdapters) {
        $controllerInfo.adapters += @{
            name = $adapter.FriendlyName
            status = $adapter.Status
            instanceId = $adapter.InstanceId
        }
        
        Write-LogEntry "INFO" "USB Network Adapter Found" @{
            name = $adapter.FriendlyName
            status = $adapter.Status
        }
    }
    
    return $controllerInfo
}

function Update-USBDrivers {
    Write-LogEntry "INFO" "Updating USB drivers..."
    
    try {
        # Check for Windows Update module
        if (-not (Get-Module -ListAvailable -Name PSWindowsUpdate)) {
            Write-LogEntry "INFO" "Installing PSWindowsUpdate module..."
            Install-Module -Name PSWindowsUpdate -Force -Scope CurrentUser -ErrorAction Stop
        }
        
        # Import module
        Import-Module PSWindowsUpdate -ErrorAction Stop
        
        # Get driver updates
        Write-LogEntry "INFO" "Searching for driver updates..."
        $driverUpdates = Get-WUList -UpdateType Driver -Category "USB Controllers"
        
        if ($driverUpdates) {
            Write-LogEntry "INFO" "Found $($driverUpdates.Count) driver updates"
            Install-WindowsUpdate -UpdateType Driver -Category "USB Controllers" -AcceptAll -AutoReboot:$false
            
            return $true
        } else {
            Write-LogEntry "INFO" "No USB driver updates available"
            return $false
        }
    } catch {
        Write-LogEntry "WARNING" "Driver update failed, continuing with manual approach" @{
            error = $_.Exception.Message
        }
        
        # Fallback: Try Device Manager refresh
        try {
            $devcon = "$env:ProgramFiles\Windows Driver Package\devcon.exe"
            if (Test-Path $devcon) {
                Write-LogEntry "INFO" "Refreshing USB devices with devcon..."
                & $devcon rescan
            } else {
                Write-LogEntry "INFO" "Refreshing devices via PowerShell..."
                Get-PnpDevice -Class "USB" | ForEach-Object {
                    Disable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
                    Enable-PnpDevice -InstanceId $_.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
                }
            }
            return $true
        } catch {
            Write-LogEntry "ERROR" "Failed to refresh USB devices" @{
                error = $_.Exception.Message
            }
            return $false
        }
    }
}

function Configure-EthernetAdapter {
    Write-LogEntry "INFO" "Configuring Ethernet 3 adapter..."
    
    try {
        # Check if adapter exists
        $adapter = Get-NetAdapter -Name "Ethernet 3" -ErrorAction SilentlyContinue
        if (-not $adapter) {
            Write-LogEntry "ERROR" "Ethernet 3 adapter not found"
            return $false
        }
        
        Write-LogEntry "INFO" "Found adapter" @{
            name = $adapter.Name
            status = $adapter.Status
            linkSpeed = $adapter.LinkSpeed
            macAddress = $adapter.MacAddress
        }
        
        # Disable DHCP on IPv4
        Write-LogEntry "INFO" "Disabling DHCP on IPv4 interface..."
        Set-NetIPInterface -InterfaceAlias "Ethernet 3" -AddressFamily IPv4 -Dhcp Disabled -ErrorAction Stop
        
        # Remove existing IP configuration
        Write-LogEntry "INFO" "Removing existing IP configuration..."
        Remove-NetIPAddress -InterfaceAlias "Ethernet 3" -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        Remove-NetRoute -InterfaceAlias "Ethernet 3" -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        
        # Set static IP
        Write-LogEntry "INFO" "Configuring static IP: 192.168.100.1/24"
        $ipResult = New-NetIPAddress -InterfaceAlias "Ethernet 3" -IPAddress "192.168.100.1" -PrefixLength 24 -ErrorAction Stop
        
        # Enable adapter
        Enable-NetAdapter -Name "Ethernet 3" -ErrorAction SilentlyContinue
        
        Write-LogEntry "SUCCESS" "Ethernet adapter configured successfully" @{
            ipAddress = "192.168.100.1"
            prefixLength = 24
            adapterStatus = "Configured"
        }
        
        return $true
    } catch {
        Write-LogEntry "ERROR" "Failed to configure Ethernet adapter" @{
            error = $_.Exception.Message
        }
        
        # Try netsh as fallback
        try {
            Write-LogEntry "INFO" "Trying netsh fallback configuration..."
            $netshResult = netsh interface ip set address "Ethernet 3" static 192.168.100.1 255.255.255.0
            if ($LASTEXITCODE -eq 0) {
                Write-LogEntry "SUCCESS" "Netsh configuration successful"
                return $true
            } else {
                Write-LogEntry "ERROR" "Netsh configuration failed"
                return $false
            }
        } catch {
            Write-LogEntry "ERROR" "Netsh fallback failed" @{
                error = $_.Exception.Message
            }
            return $false
        }
    }
}

function Test-NetworkConfiguration {
    Write-LogEntry "INFO" "Testing network configuration..."
    
    # Check IP configuration
    $ipConfig = Get-NetIPAddress -InterfaceAlias "Ethernet 3" -AddressFamily IPv4 -ErrorAction SilentlyContinue
    if ($ipConfig) {
        Write-LogEntry "SUCCESS" "IP configuration verified" @{
            ipAddress = $ipConfig.IPAddress
            prefixLength = $ipConfig.PrefixLength
        }
    } else {
        Write-LogEntry "ERROR" "No IP configuration found"
        return $false
    }
    
    # Test Pi connectivity
    Write-LogEntry "INFO" "Testing Pi connectivity at 192.168.100.2..."
    try {
        $ping = New-Object System.Net.NetworkInformation.Ping
        $reply = $ping.Send("192.168.100.2", 3000)
        
        if ($reply.Status -eq 'Success') {
            Write-LogEntry "SUCCESS" "Pi connectivity confirmed" @{
                roundTripTime = $reply.RoundtripTime
                status = $reply.Status.ToString()
            }
            return $true
        } else {
            Write-LogEntry "WARNING" "Pi not responding" @{
                status = $reply.Status.ToString()
                message = "Pi may need network configuration"
            }
            return $false
        }
        $ping.Dispose()
    } catch {
        Write-LogEntry "WARNING" "Pi connectivity test failed" @{
            error = $_.Exception.Message
        }
        return $false
    }
}

# Main execution
if (-not (Test-AdminRights)) {
    Write-LogEntry "ERROR" "Administrator rights required"
    Write-Host "Please run this script as Administrator!" -ForegroundColor Red
    exit 1
}

Write-LogEntry "INFO" "Starting USB driver and network configuration"

# Step 1: Check USB controller status
$usbStatus = Get-USBControllerStatus

# Step 2: Update drivers if requested
if ($UpdateDrivers) {
    $driverResult = Update-USBDrivers
    if ($driverResult) {
        Write-LogEntry "INFO" "Driver update completed, waiting for system to stabilize..."
        Start-Sleep -Seconds 5
    }
}

# Step 3: Configure network adapter
$networkResult = Configure-EthernetAdapter

# Step 4: Test configuration
if ($networkResult) {
    Start-Sleep -Seconds 3  # Allow adapter to initialize
    $testResult = Test-NetworkConfiguration
    
    if ($testResult) {
        Write-LogEntry "SUCCESS" "Complete setup successful - Pi responding!"
    } else {
        Write-LogEntry "INFO" "Network configured, Pi setup needed"
    }
} else {
    Write-LogEntry "ERROR" "Network configuration failed"
}

# Final summary
Write-LogEntry "SUCCESS" "Setup completed" @{
    usbControllersOK = ($usbStatus.problemControllers -eq 0)
    networkConfigured = $networkResult
    piResponding = $testResult
    logFile = $logFile
}

Write-Host "`n=== SETUP SUMMARY ===" -ForegroundColor Cyan
Write-Host "USB Controllers: $(if($usbStatus.problemControllers -eq 0) {' OK'} else {' Issues'})" -ForegroundColor $(if($usbStatus.problemControllers -eq 0) {'Green'} else {'Red'})
Write-Host "Network Config: $(if($networkResult) {' Configured'} else {' Failed'})" -ForegroundColor $(if($networkResult) {'Green'} else {'Red'})
Write-Host "Pi Connectivity: $(if($testResult) {' Connected'} else {' Pending Pi Setup'})" -ForegroundColor $(if($testResult) {'Green'} else {'Yellow'})

if (-not $testResult) {
    Write-Host "`nNEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Configure Pi network: C:\EQ12\PI_ETHERNET_SETUP_INSTRUCTIONS.md" -ForegroundColor White
    Write-Host "2. Test connectivity: .\eq12_pi_connectivity_test.ps1" -ForegroundColor White
    Write-Host "3. Add to cluster: python eq12_raspberry_pi_cluster_manager.py --add-node 192.168.100.2" -ForegroundColor White
}

Write-Host "`nLog file: $logFile" -ForegroundColor Cyan
