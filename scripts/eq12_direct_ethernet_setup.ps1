[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$EthernetAdapter = "Ethernet",
    
    [Parameter(Mandatory=$false)]
    [string]$HostIP = "192.168.100.1",
    
    [Parameter(Mandatory=$false)]
    [string]$PiIP = "192.168.100.2",
    
    [Parameter(Mandatory=$false)]
    [switch]$EnableICS,
    
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput
)

<#
.SYNOPSIS
    Configure direct Ethernet connection between EQ12 host and Raspberry Pi

.DESCRIPTION
    Sets up point-to-point Ethernet networking for direct Pi connection.
    Configures static IP addresses and optional Internet Connection Sharing.

.PARAMETER EthernetAdapter
    Name of the Ethernet adapter connected to Pi (default: Ethernet)

.PARAMETER HostIP
    IP address for the host PC (default: 192.168.100.1)

.PARAMETER PiIP
    IP address for the Raspberry Pi (default: 192.168.100.2)

.PARAMETER EnableICS
    Enable Internet Connection Sharing to provide Pi with internet access

.PARAMETER VerboseOutput
    Enable verbose logging output

.EXAMPLE
    .\eq12_direct_ethernet_setup.ps1 -EthernetAdapter "Ethernet 2" -EnableICS -VerboseOutput
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
    $logFile = "$script:LogPath\direct_ethernet_setup_$(Get-Date -Format 'yyyyMMdd').log"
    Add-Content -Path $logFile -Value $logMessage
}

function Get-AvailableEthernetAdapters {
    Write-NetworkLog "Scanning for available Ethernet adapters..."
    
    $adapters = Get-NetAdapter -Name "Ethernet*" | Where-Object {$_.Status -ne "Disabled"}
    
    Write-NetworkLog "Found Ethernet adapters:"
    foreach ($adapter in $adapters) {
        $status = if ($adapter.Status -eq "Up") { "[UP]" } else { "[DOWN]" }
        Write-NetworkLog "   $status $($adapter.Name) - $($adapter.InterfaceDescription) - $($adapter.Status)"
    }
    
    return $adapters
}

function Set-StaticIPAddress {
    param(
        [string]$AdapterName,
        [string]$IPAddress,
        [string]$SubnetMask = "255.255.255.0"
    )
    
    Write-NetworkLog "Configuring static IP on adapter: $AdapterName"
    Write-NetworkLog "IP Address: $IPAddress"
    Write-NetworkLog "Subnet Mask: $SubnetMask"
    
    try {
        # Remove existing IP configuration
        Remove-NetIPAddress -InterfaceAlias $AdapterName -Confirm:$false -ErrorAction SilentlyContinue
        Remove-NetRoute -InterfaceAlias $AdapterName -Confirm:$false -ErrorAction SilentlyContinue
        
        # Set new static IP
        New-NetIPAddress -InterfaceAlias $AdapterName -IPAddress $IPAddress -PrefixLength 24 -ErrorAction Stop
        
        Write-NetworkLog "Static IP configured successfully" -Level SUCCESS
        return $true
        
    } catch {
        Write-NetworkLog "Failed to configure static IP: $($_.Exception.Message)" -Level ERROR
        return $false
    }
}

function Enable-InternetConnectionSharing {
    param(
        [string]$PublicConnection,
        [string]$PrivateConnection
    )
    
    Write-NetworkLog "Configuring Internet Connection Sharing..."
    Write-NetworkLog "Public (Internet): $PublicConnection"
    Write-NetworkLog "Private (Pi): $PrivateConnection"
    
    try {
        # Create ICS COM object
        $netShare = New-Object -ComObject HNetCfg.HNetShare
        
        # Get connections
        $publicConn = $netShare.EnumEveryConnection | Where-Object {
            $netShare.NetConnectionProps($_).Name -eq $PublicConnection
        }
        
        $privateConn = $netShare.EnumEveryConnection | Where-Object {
            $netShare.NetConnectionProps($_).Name -eq $PrivateConnection
        }
        
        if ($publicConn -and $privateConn) {
            # Configure ICS
            $publicConfig = $netShare.INetSharingConfigurationForINetConnection($publicConn)
            $privateConfig = $netShare.INetSharingConfigurationForINetConnection($privateConn)
            
            # Enable sharing on public connection
            $publicConfig.EnableSharing(0) # 0 = ICSSHARINGTYPE_PUBLIC
            
            # Enable sharing on private connection  
            $privateConfig.EnableSharing(1) # 1 = ICSSHARINGTYPE_PRIVATE
            
            Write-NetworkLog "Internet Connection Sharing enabled" -Level SUCCESS
            return $true
        } else {
            Write-NetworkLog "Could not find specified network connections" -Level ERROR
            return $false
        }
        
    } catch {
        Write-NetworkLog "ICS configuration failed: $($_.Exception.Message)" -Level ERROR
        Write-NetworkLog "Try enabling ICS manually via Network Connections" -Level INFO
        return $false
    }
}

function Test-DirectConnection {
    param(
        [string]$TargetIP,
        [string]$AdapterName
    )
    
    Write-NetworkLog "Testing direct connection to Pi..."
    
    # Test ping
    try {
        $pingResult = Test-Connection -ComputerName $TargetIP -Count 2 -Quiet
        if ($pingResult) {
            Write-NetworkLog "Ping successful to $TargetIP" -Level SUCCESS
        } else {
            Write-NetworkLog "Ping failed to $TargetIP" -Level WARNING
            Write-NetworkLog "Pi may not be configured yet" -Level INFO
        }
    } catch {
        Write-NetworkLog "Ping test failed: $($_.Exception.Message)" -Level ERROR
    }
    
    # Check adapter status
    try {
        $adapter = Get-NetAdapter -Name $AdapterName
        if ($adapter.Status -eq "Up") {
            Write-NetworkLog "Ethernet adapter is UP" -Level SUCCESS
            
            # Get link speed
            if ($adapter.LinkSpeed -gt 0) {
                Write-NetworkLog "Link Speed: $($adapter.LinkSpeed)" -Level SUCCESS
            }
        } else {
            Write-NetworkLog "Ethernet adapter is $($adapter.Status)" -Level ERROR
        }
    } catch {
        Write-NetworkLog "Adapter check failed: $($_.Exception.Message)" -Level ERROR
    }
}

function New-PiNetworkingGuide {
    param(
        [string]$PiIP,
        [string]$HostIP
    )
    
    Write-NetworkLog "Generating Pi networking configuration guide..."
    
    $piGuide = @"
# Raspberry Pi Direct Ethernet Configuration
================================================

## Network Setup for Direct Connection to EQ12 Host

Your Pi is connected directly to the EQ12 host via Ethernet cable.
Use this configuration to establish communication.

### Step 1: Configure Static IP on Pi
```bash
# Edit network configuration
sudo nano /etc/dhcpcd.conf

# Add these lines at the end:
interface eth0
static ip_address=$PiIP/24
static routers=$HostIP
static domain_name_servers=8.8.8.8 8.8.4.4

# Save and exit (Ctrl+O, Enter, Ctrl+X)
```

### Step 2: Enable SSH
```bash
# Enable SSH service
sudo systemctl enable ssh
sudo systemctl start ssh

# Check SSH status
sudo systemctl status ssh
```

### Step 3: Reboot Pi
```bash
sudo reboot
```

### Step 4: Test Connection from EQ12 Host
From Windows PowerShell:
```powershell
# Test ping
ping $PiIP

# Test SSH
Test-NetConnection -ComputerName $PiIP -Port 22

# SSH into Pi
ssh pi@$PiIP
```

## Network Information
- **Host IP**: $HostIP
- **Pi IP**: $PiIP  
- **Subnet**: 192.168.100.0/24
- **Connection**: Direct Ethernet (point-to-point)

## Troubleshooting

### If Pi not reachable:
1. Check Ethernet cable connection
2. Verify Pi has power and boots properly
3. Check LED indicators on Pi Ethernet port
4. Try different Ethernet cable

### If SSH fails:
1. Enable SSH: `sudo systemctl enable ssh`
2. Start SSH: `sudo systemctl start ssh`
3. Check firewall: `sudo ufw status`

### If internet not working on Pi:
Internet Connection Sharing is configured on host.
Pi should have internet access through the host connection.

## Next Steps
Once networking is working:
1. Install Coral TPU support
2. Add Pi to EQ12 cluster
3. Start distributed processing

"@
    
    # Save guide
    $guidePath = "$script:WorkspaceRoot\PI_DIRECT_ETHERNET_GUIDE.md"
    $piGuide | Out-File -FilePath $guidePath -Encoding UTF8
    
    Write-NetworkLog "Pi networking guide saved: $guidePath" -Level SUCCESS
    return $guidePath
}

# Main execution
try {
    Write-Host @"
EQ12 Direct Ethernet Configuration
===================================
Configuring point-to-point connection between EQ12 host and Raspberry Pi
"@ -ForegroundColor Green

    Write-NetworkLog "Starting direct Ethernet configuration..."
    Write-NetworkLog "Host IP: $HostIP"
    Write-NetworkLog "Pi IP: $PiIP"
    Write-NetworkLog "Ethernet Adapter: $EthernetAdapter"

    # Check available adapters
    $adapters = Get-AvailableEthernetAdapters
    
    if (-not $adapters) {
        Write-NetworkLog "No Ethernet adapters found" -Level ERROR
        exit 1
    }

    # Find the specified adapter or ask user to choose
    $targetAdapter = $adapters | Where-Object {$_.Name -eq $EthernetAdapter}
    
    if (-not $targetAdapter) {
        Write-NetworkLog "Adapter '$EthernetAdapter' not found" -Level WARNING
        Write-NetworkLog "Available adapters:" -Level INFO
        
        for ($i = 0; $i -lt $adapters.Count; $i++) {
            Write-Host "   [$i] $($adapters[$i].Name) - $($adapters[$i].Status)"
        }
        
        $choice = Read-Host "Select adapter number (0-$($adapters.Count-1))"
        
        if ([int]$choice -ge 0 -and [int]$choice -lt $adapters.Count) {
            $targetAdapter = $adapters[[int]$choice]
            $EthernetAdapter = $targetAdapter.Name
        } else {
            Write-NetworkLog "Invalid selection" -Level ERROR
            exit 1
        }
    }

    Write-NetworkLog "Using adapter: $($targetAdapter.Name)" -Level SUCCESS

    # Configure static IP on host adapter
    if (-not (Set-StaticIPAddress -AdapterName $EthernetAdapter -IPAddress $HostIP)) {
        Write-NetworkLog "Failed to configure host IP address" -Level ERROR
        exit 1
    }

    # Enable Internet Connection Sharing if requested
    if ($EnableICS) {
        $wifiAdapter = Get-NetAdapter | Where-Object {$_.Name -like "*Wi-Fi*" -and $_.Status -eq "Up"} | Select-Object -First 1
        
        if ($wifiAdapter) {
            Write-NetworkLog "Enabling ICS from $($wifiAdapter.Name) to $EthernetAdapter"
            Enable-InternetConnectionSharing -PublicConnection $wifiAdapter.Name -PrivateConnection $EthernetAdapter
        } else {
            Write-NetworkLog "No Wi-Fi adapter found for ICS" -Level WARNING
        }
    }

    # Test the connection
    Start-Sleep -Seconds 2
    Test-DirectConnection -TargetIP $PiIP -AdapterName $EthernetAdapter

    # Generate Pi configuration guide
    $guidePath = New-PiNetworkingGuide -PiIP $PiIP -HostIP $HostIP

    Write-NetworkLog "Direct Ethernet configuration completed!" -Level SUCCESS
    
    Write-Host @"

Configuration Complete!
=========================

Host Configuration:
[SUCCESS] Ethernet adapter configured with IP: $HostIP
[SUCCESS] Ready for Pi connection
$(if ($EnableICS) { "[SUCCESS] Internet Connection Sharing enabled" } else { "[WARNING] ICS not enabled (use -EnableICS to enable)" })

Next Steps:
1. Follow Pi setup guide: $guidePath
2. Configure Pi with IP: $PiIP
3. Enable SSH on Pi
4. Test connection: ping $PiIP
5. Add Pi to EQ12 cluster

"@ -ForegroundColor Green

    # Open the guide
    if (Test-Path $guidePath) {
        Start-Process $guidePath
    }

} catch {
    Write-NetworkLog "Configuration failed: $($_.Exception.Message)" -Level ERROR
    Write-NetworkLog "Line: $($_.InvocationInfo.ScriptLineNumber)" -Level ERROR
    exit 1
}