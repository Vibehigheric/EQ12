[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$PiAdapter = "Ethernet 3",  # USB 2.5GbE adapter for Pi
    
    [Parameter(Mandatory=$false)]
    [string]$PrimaryAdapter = "Ethernet",  # Hardwired internet
    
    [Parameter(Mandatory=$false)]
    [string]$BackupAdapter = "Wi-Fi",
    
    [Parameter(Mandatory=$false)]
    [string]$PiIP = "192.168.100.2",
    
    [Parameter(Mandatory=$false)]
    [string]$HostPiIP = "192.168.100.1",
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput
)

<#
.SYNOPSIS
    Configure EQ12 network priorities and Pi USB connection

.DESCRIPTION
    Sets up hardwired ethernet as primary, Wi-Fi as backup, and configures
    Raspberry Pi connection via USB-to-Ethernet adapter.

.PARAMETER PiAdapter
    Network adapter connected to Pi (default: Ethernet 3)

.PARAMETER PrimaryAdapter
    Primary internet connection adapter (default: Ethernet)

.PARAMETER BackupAdapter
    Backup internet connection adapter (default: Wi-Fi)

.PARAMETER PiIP
    IP address for Raspberry Pi (default: 192.168.100.2)

.PARAMETER HostPiIP
    IP address for host on Pi network (default: 192.168.100.1)

.PARAMETER VerboseOutput
    Enable verbose logging

.EXAMPLE
    .\eq12_network_priority_setup.ps1 -VerboseOutput
#>

# Script configuration
$script:WorkspaceRoot = "C:\EQ12"
$script:LogPath = "$WorkspaceRoot\logs"

# Ensure log directory exists
if (-not (Test-Path $script:LogPath)) {
    New-Item -ItemType Directory -Path $script:LogPath -Force | Out-Null
}

function Write-NetworkLog {
    param(
        [string]$Message,
        [ValidateSet('INFO', 'WARNING', 'ERROR', 'SUCCESS')]
        [string]$Level = 'INFO'
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # Console output with colors
    switch ($Level) {
        'SUCCESS' { Write-Host $logMessage -ForegroundColor Green }
        'WARNING' { Write-Host $logMessage -ForegroundColor Yellow }
        'ERROR'   { Write-Host $logMessage -ForegroundColor Red }
        default   { Write-Host $logMessage -ForegroundColor Cyan }
    }
    
    # Log to file
    $logFile = "$script:LogPath\network_priority_setup_$(Get-Date -Format 'yyyyMMdd').log"
    Add-Content -Path $logFile -Value $logMessage
}

function Test-AdapterConnectivity {
    param([string]$AdapterName)
    
    try {
        $adapter = Get-NetAdapter -Name $AdapterName -ErrorAction Stop
        return @{
            Exists = $true
            Status = $adapter.Status
            LinkSpeed = $adapter.LinkSpeed
            MediaType = $adapter.MediaType
        }
    } catch {
        return @{
            Exists = $false
            Status = "Not Found"
            LinkSpeed = 0
            MediaType = "Unknown"
        }
    }
}

function Set-NetworkPriority {
    param(
        [string]$AdapterName,
        [int]$Metric
    )
    
    Write-NetworkLog "Setting network priority for $AdapterName (metric: $Metric)"
    
    try {
        # Set IPv4 metric
        Set-NetIPInterface -InterfaceAlias $AdapterName -InterfaceMetric $Metric -AddressFamily IPv4 -ErrorAction Stop
        
        # Set IPv6 metric
        Set-NetIPInterface -InterfaceAlias $AdapterName -InterfaceMetric $Metric -AddressFamily IPv6 -ErrorAction Stop
        
        Write-NetworkLog "Network priority set successfully for $AdapterName" -Level SUCCESS
        return $true
    } catch {
        Write-NetworkLog "Failed to set priority for $AdapterName: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Configure-PiConnection {
    param(
        [string]$AdapterName,
        [string]$HostIP,
        [string]$PiIP
    )
    
    Write-NetworkLog "Configuring Pi connection on $AdapterName"
    Write-NetworkLog "Host IP: $HostIP, Pi IP: $PiIP"
    
    try {
        # Remove existing IP configuration
        Remove-NetIPAddress -InterfaceAlias $AdapterName -Confirm:$false -ErrorAction SilentlyContinue
        Remove-NetRoute -InterfaceAlias $AdapterName -Confirm:$false -ErrorAction SilentlyContinue
        
        # Set static IP for Pi communication
        New-NetIPAddress -InterfaceAlias $AdapterName -IPAddress $HostIP -PrefixLength 24 -ErrorAction Stop
        
        Write-NetworkLog "Pi connection configured successfully" -Level SUCCESS
        return $true
    } catch {
        Write-NetworkLog "Failed to configure Pi connection: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Test-PiConnectivity {
    param([string]$PiIP)
    
    Write-NetworkLog "Testing Pi connectivity to $PiIP"
    
    try {
        $pingResult = Test-Connection -ComputerName $PiIP -Count 2 -Quiet -ErrorAction Stop
        
        if ($pingResult) {
            Write-NetworkLog "Pi is reachable at $PiIP" -Level SUCCESS
            
            # Test SSH connectivity
            try {
                $sshTest = Test-NetConnection -ComputerName $PiIP -Port 22 -WarningAction SilentlyContinue
                if ($sshTest.TcpTestSucceeded) {
                    Write-NetworkLog "SSH is available on Pi" -Level SUCCESS
                } else {
                    Write-NetworkLog "SSH not available on Pi (may need configuration)" -Level WARNING
                }
            } catch {
                Write-NetworkLog "Could not test SSH connectivity" -Level WARNING
            }
            
            return $true
        } else {
            Write-NetworkLog "Pi is not reachable (may need configuration)" -Level WARNING
            return $false
        }
    } catch {
        Write-NetworkLog "Ping test failed: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Show-NetworkStatus {
    Write-NetworkLog "Current Network Status:" -Level INFO
    
    $adapters = Get-NetAdapter | Where-Object {$_.Name -in @($PrimaryAdapter, $BackupAdapter, $PiAdapter)}
    
    foreach ($adapter in $adapters) {
        $status = switch ($adapter.Status) {
            "Up" { "[CONNECTED]" }
            "Disconnected" { "[DISCONNECTED]" }
            default { "[$($adapter.Status)]" }
        }
        
        Write-NetworkLog "  $status $($adapter.Name): $($adapter.InterfaceDescription)"
        
        if ($adapter.Status -eq "Up") {
            # Get IP information
            try {
                $ipConfig = Get-NetIPAddress -InterfaceAlias $adapter.Name -AddressFamily IPv4 -ErrorAction SilentlyContinue
                if ($ipConfig) {
                    Write-NetworkLog "    IP: $($ipConfig.IPAddress)"
                }
                
                # Get metric
                $interface = Get-NetIPInterface -InterfaceAlias $adapter.Name -AddressFamily IPv4 -ErrorAction SilentlyContinue
                if ($interface) {
                    Write-NetworkLog "    Priority Metric: $($interface.InterfaceMetric)"
                }
            } catch {
                # Ignore errors
            }
        }
    }
}

function Enable-InternetConnectionSharing {
    param(
        [string]$PublicAdapter,
        [string]$PrivateAdapter
    )
    
    Write-NetworkLog "Configuring Internet Connection Sharing: $PublicAdapter -> $PrivateAdapter"
    
    try {
        # This requires elevated privileges and COM objects
        $netShare = New-Object -ComObject HNetCfg.HNetShare
        
        # Get connection objects
        $connections = $netShare.EnumEveryConnection
        $publicConn = $null
        $privateConn = $null
        
        foreach ($conn in $connections) {
            $props = $netShare.NetConnectionProps($conn)
            if ($props.Name -eq $PublicAdapter) {
                $publicConn = $conn
            }
            if ($props.Name -eq $PrivateAdapter) {
                $privateConn = $conn
            }
        }
        
        if ($publicConn -and $privateConn) {
            $publicConfig = $netShare.INetSharingConfigurationForINetConnection($publicConn)
            $privateConfig = $netShare.INetSharingConfigurationForINetConnection($privateConn)
            
            # Enable public sharing
            $publicConfig.EnableSharing(0)  # ICSSHARINGTYPE_PUBLIC
            
            # Enable private sharing
            $privateConfig.EnableSharing(1)  # ICSSHARINGTYPE_PRIVATE
            
            Write-NetworkLog "Internet Connection Sharing enabled" -Level SUCCESS
            return $true
        } else {
            Write-NetworkLog "Could not find network connections for ICS" -Level ERROR
            return $false
        }
    } catch {
        Write-NetworkLog "ICS configuration failed: $($_.Exception.Message)" -Level ERROR
        Write-NetworkLog "You may need to configure ICS manually" -Level INFO
        return $false
    }
}

function Show-ConfigurationGuide {
    Write-NetworkLog "Configuration Summary and Next Steps:" -Level INFO
    Write-Host ""
    Write-Host "NETWORK PRIORITY CONFIGURATION" -ForegroundColor Yellow
    Write-Host "==============================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Primary Internet: $PrimaryAdapter (Metric: 5)" -ForegroundColor Green
    Write-Host "2. Backup Internet: $BackupAdapter (Metric: 35)" -ForegroundColor Yellow
    Write-Host "3. Pi Connection: $PiAdapter (IP: $HostPiIP)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "RASPBERRY PI SETUP COMMANDS" -ForegroundColor Yellow
    Write-Host "===========================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "SSH into your Pi and run:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "sudo nano /etc/dhcpcd.conf" -ForegroundColor White
    Write-Host ""
    Write-Host "Add these lines:" -ForegroundColor Cyan
    Write-Host "interface eth0" -ForegroundColor White
    Write-Host "static ip_address=$PiIP/24" -ForegroundColor White
    Write-Host "static routers=$HostPiIP" -ForegroundColor White
    Write-Host "static domain_name_servers=8.8.8.8 8.8.4.4" -ForegroundColor White
    Write-Host ""
    Write-Host "Then reboot:" -ForegroundColor Cyan
    Write-Host "sudo reboot" -ForegroundColor White
    Write-Host ""
    Write-Host "TEST CONNECTIVITY" -ForegroundColor Yellow
    Write-Host "=================" -ForegroundColor Yellow
    Write-Host "ping $PiIP" -ForegroundColor White
    Write-Host "ssh pi@$PiIP" -ForegroundColor White
    Write-Host ""
}

# Main execution
try {
    Write-Host @"
EQ12 Network Priority & Pi Setup
=================================
Configuring hardwired primary, Wi-Fi backup, Pi USB connection
"@ -ForegroundColor Green

    Write-NetworkLog "Starting network configuration..."
    Write-NetworkLog "Primary: $PrimaryAdapter, Backup: $BackupAdapter, Pi: $PiAdapter"

    # Check adapter connectivity
    Write-NetworkLog "Checking adapter connectivity..."
    
    $primaryStatus = Test-AdapterConnectivity -AdapterName $PrimaryAdapter
    $backupStatus = Test-AdapterConnectivity -AdapterName $BackupAdapter
    $piStatus = Test-AdapterConnectivity -AdapterName $PiAdapter
    
    Write-NetworkLog "Primary adapter ($PrimaryAdapter): $($primaryStatus.Status)"
    Write-NetworkLog "Backup adapter ($BackupAdapter): $($backupStatus.Status)"
    Write-NetworkLog "Pi adapter ($PiAdapter): $($piStatus.Status)"

    # Configure network priorities
    Write-NetworkLog "Setting network priorities..."
    
    # Primary internet (lowest metric = highest priority)
    if ($primaryStatus.Exists) {
        Set-NetworkPriority -AdapterName $PrimaryAdapter -Metric 5
    }
    
    # Backup internet (higher metric = lower priority)
    if ($backupStatus.Exists) {
        Set-NetworkPriority -AdapterName $BackupAdapter -Metric 35
    }
    
    # Pi adapter (high metric since it's not for internet)
    if ($piStatus.Exists) {
        Set-NetworkPriority -AdapterName $PiAdapter -Metric 100
    }

    # Configure Pi connection
    if ($piStatus.Exists) {
        Write-NetworkLog "Configuring Pi connection..."
        
        if (Configure-PiConnection -AdapterName $PiAdapter -HostIP $HostPiIP -PiIP $PiIP) {
            # Test Pi connectivity
            Start-Sleep -Seconds 2
            Test-PiConnectivity -PiIP $PiIP
            
            # Try to enable Internet Connection Sharing from primary adapter to Pi
            if ($primaryStatus.Status -eq "Up") {
                Enable-InternetConnectionSharing -PublicAdapter $PrimaryAdapter -PrivateAdapter $PiAdapter
            } elseif ($backupStatus.Status -eq "Up") {
                Enable-InternetConnectionSharing -PublicAdapter $BackupAdapter -PrivateAdapter $PiAdapter
            }
        }
    }

    # Show current status
    Show-NetworkStatus
    
    # Show configuration guide
    Show-ConfigurationGuide

    Write-NetworkLog "Network configuration completed!" -Level SUCCESS

} catch {
    Write-NetworkLog "Configuration failed: $($_.Exception.Message)" -Level ERROR
    Write-NetworkLog "Line: $($_.InvocationInfo.ScriptLineNumber)" -Level ERROR
    exit 1
}