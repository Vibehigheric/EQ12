# EQ12 Pi Connection Troubleshooter
# Systematic diagnosis and repair of Pi connectivity issues

[CmdletBinding()]
param(
    [string]$PiIP = "192.168.100.2",
    [string]$HostIP = "192.168.100.1",
    [string]$Username = "ricoj100",
    [string]$Password = "102120sRO1!",
    [switch]$FixNetwork,
    [switch]$EnableAdapter,
    [switch]$ShowDetailedStatus
)

$ErrorActionPreference = "Continue"

# Configure logging
$LogPath = "C:\EQ12\logs\pi_troubleshooter_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
New-Item -Path (Split-Path $LogPath) -ItemType Directory -Force | Out-Null

function Write-TroubleshootLog {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    
    $Color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO" { "Cyan" }
        default { "White" }
    }
    
    Write-Host $LogEntry -ForegroundColor $Color
    $LogEntry | Out-File -FilePath $LogPath -Append -Encoding UTF8
}

function Test-AdminRights {
    $CurrentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $CurrentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Get-NetworkAdapterStatus {
    Write-TroubleshootLog " Analyzing network adapter configuration..." "INFO"
    
    $AllAdapters = Get-NetAdapter | Where-Object { $_.Name -like "*Ethernet*" }
    $EthernetAdapters = @()
    
    foreach ($Adapter in $AllAdapters) {
        $IPConfig = Get-NetIPAddress -InterfaceAlias $Adapter.Name -AddressFamily IPv4 -ErrorAction SilentlyContinue
        $AdapterInfo = [PSCustomObject]@{
            Name           = $Adapter.Name
            Status         = $Adapter.Status
            Speed          = $Adapter.LinkSpeed
            IPAddresses    = ($IPConfig | ForEach-Object { "$($_.IPAddress)/$($_.PrefixLength)" }) -join ", "
            HasTargetIP    = ($IPConfig.IPAddress -contains $HostIP)
            InterfaceIndex = $Adapter.InterfaceIndex
        }
        $EthernetAdapters += $AdapterInfo
    }
    
    Write-TroubleshootLog " Network Adapter Analysis:" "INFO"
    foreach ($Adapter in $EthernetAdapters) {
        $StatusIcon = if ($Adapter.Status -eq "Up") { "" } else { "" }
        $IPIcon = if ($Adapter.HasTargetIP) { "" } else { "" }
        Write-TroubleshootLog "  $StatusIcon $IPIcon $($Adapter.Name): $($Adapter.Status) ($($Adapter.Speed)) - $($Adapter.IPAddresses)" "INFO"
    }
    
    return $EthernetAdapters
}

function Find-PiAdapter {
    $Adapters = Get-NetworkAdapterStatus
    
    # Look for adapter with target IP
    $TargetAdapter = $Adapters | Where-Object { $_.HasTargetIP }
    
    if ($TargetAdapter) {
        Write-TroubleshootLog " Found Pi adapter: $($TargetAdapter.Name) with IP $HostIP" "SUCCESS"
        return $TargetAdapter
    }
    
    # Look for disconnected adapters that might be the Pi connection
    $DisconnectedAdapters = $Adapters | Where-Object { $_.Status -eq "Disconnected" }
    
    if ($DisconnectedAdapters.Count -eq 1) {
        Write-TroubleshootLog " Potential Pi adapter (disconnected): $($DisconnectedAdapters[0].Name)" "INFO"
        return $DisconnectedAdapters[0]
    }
    
    Write-TroubleshootLog " Cannot identify Pi network adapter automatically" "ERROR"
    return $null
}

function Set-PiNetworkAdapter {
    param([string]$AdapterName)
    
    if (-not (Test-AdminRights)) {
        Write-TroubleshootLog " Administrator rights required to configure network adapter" "ERROR"
        Write-TroubleshootLog " Please run PowerShell as Administrator and try again" "INFO"
        return $false
    }
    
    Write-TroubleshootLog " Configuring adapter '$AdapterName' for Pi communication..." "INFO"
    
    try {
        # Remove any existing IP configuration
        Remove-NetIPAddress -InterfaceAlias $AdapterName -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        Remove-NetRoute -InterfaceAlias $AdapterName -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        
        # Set static IP
        New-NetIPAddress -InterfaceAlias $AdapterName -IPAddress $HostIP -PrefixLength 24 -ErrorAction Stop
        
        # Disable DHCP
        Set-NetIPInterface -InterfaceAlias $AdapterName -Dhcp Disabled -ErrorAction Stop
        
        Write-TroubleshootLog " Network adapter configured successfully" "SUCCESS"
        Write-TroubleshootLog "   IP Address: $HostIP/24" "INFO"
        Write-TroubleshootLog "   DHCP: Disabled" "INFO"
        
        return $true
    }
    catch {
        Write-TroubleshootLog " Failed to configure network adapter: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Enable-NetworkAdapter {
    param([string]$AdapterName)
    
    if (-not (Test-AdminRights)) {
        Write-TroubleshootLog " Administrator rights required to enable network adapter" "ERROR"
        return $false
    }
    
    try {
        Enable-NetAdapter -Name $AdapterName -Confirm:$false
        Write-TroubleshootLog " Network adapter '$AdapterName' enabled" "SUCCESS"
        Start-Sleep -Seconds 3  # Wait for adapter to come up
        return $true
    }
    catch {
        Write-TroubleshootLog " Failed to enable adapter: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Test-PiConnectivity {
    param([string]$IP, [int]$TimeoutSeconds = 30)
    
    Write-TroubleshootLog " Testing Pi connectivity at $IP..." "INFO"
    
    # Test ping with timeout
    $PingSuccess = $false
    $SSHSuccess = $false
    
    for ($i = 1; $i -le 3; $i++) {
        Write-TroubleshootLog "   Ping attempt $i/3..." "INFO"
        $PingResult = Test-Connection -ComputerName $IP -Count 1 -Quiet -ErrorAction SilentlyContinue
        if ($PingResult) {
            $PingSuccess = $true
            Write-TroubleshootLog "   Ping successful" "SUCCESS"
            break
        }
        Start-Sleep -Seconds 2
    }
    
    if (-not $PingSuccess) {
        Write-TroubleshootLog "   Ping failed after 3 attempts" "ERROR"
    }
    
    # Test SSH port
    if ($PingSuccess) {
        Write-TroubleshootLog "   Testing SSH port 22..." "INFO"
        $SSHTest = Test-NetConnection -ComputerName $IP -Port 22 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        if ($SSHTest.TcpTestSucceeded) {
            $SSHSuccess = $true
            Write-TroubleshootLog "   SSH port accessible" "SUCCESS"
        }
        else {
            Write-TroubleshootLog "   SSH port not accessible" "ERROR"
        }
    }
    
    return @{
        Ping = $PingSuccess
        SSH  = $SSHSuccess
    }
}

function Get-PhysicalConnectionStatus {
    Write-TroubleshootLog " Checking physical connection status..." "INFO"
    
    $PiAdapter = Find-PiAdapter
    if ($PiAdapter) {
        $Adapter = Get-NetAdapter -Name $PiAdapter.Name
        
        Write-TroubleshootLog " Physical Connection Analysis:" "INFO"
        Write-TroubleshootLog "   Adapter: $($Adapter.Name)" "INFO"
        Write-TroubleshootLog "   Status: $($Adapter.Status)" "INFO"
        Write-TroubleshootLog "   Link Speed: $($Adapter.LinkSpeed)" "INFO"
        Write-TroubleshootLog "   Media Type: $($Adapter.MediaType)" "INFO"
        
        if ($Adapter.Status -eq "Disconnected") {
            Write-TroubleshootLog "  Physical Connection Issues Detected:" "WARN"
            Write-TroubleshootLog "   Check Ethernet cable is securely connected" "WARN"
            Write-TroubleshootLog "   Verify Pi is powered on (LED indicators)" "WARN"
            Write-TroubleshootLog "   Try different Ethernet cable" "WARN"
            Write-TroubleshootLog "   Check Pi Ethernet port for damage" "WARN"
        }
    }
}

function Show-PiSetupInstructions {
    Write-TroubleshootLog " Pi Configuration Instructions:" "INFO"
    Write-TroubleshootLog "If Pi is accessible via console/HDMI:" "INFO"
    Write-TroubleshootLog "" "INFO"
    Write-TroubleshootLog "1. Edit network configuration:" "INFO"
    Write-TroubleshootLog "   sudo nano /etc/dhcpcd.conf" "INFO"
    Write-TroubleshootLog "" "INFO"
    Write-TroubleshootLog "2. Add these lines at the end:" "INFO"
    Write-TroubleshootLog "   interface eth0" "INFO"
    Write-TroubleshootLog "   static ip_address=$PiIP/24" "INFO"
    Write-TroubleshootLog "   static routers=$HostIP" "INFO"
    Write-TroubleshootLog "   static domain_name_servers=8.8.8.8" "INFO"
    Write-TroubleshootLog "" "INFO"
    Write-TroubleshootLog "3. Enable SSH (if not already enabled):" "INFO"
    Write-TroubleshootLog "   sudo systemctl enable ssh" "INFO"
    Write-TroubleshootLog "   sudo systemctl start ssh" "INFO"
    Write-TroubleshootLog "" "INFO"
    Write-TroubleshootLog "4. Reboot Pi:" "INFO"
    Write-TroubleshootLog "   sudo reboot" "INFO"
    Write-TroubleshootLog "" "INFO"
    Write-TroubleshootLog " Alternative: Use Raspberry Pi Imager with advanced options" "INFO"
    Write-TroubleshootLog "   to pre-configure static IP during OS installation" "INFO"
}

function Show-DetailedNetworkStatus {
    Write-TroubleshootLog " Detailed Network Status Analysis:" "INFO"
    
    # Show routing table
    Write-TroubleshootLog "  Routing Table:" "INFO"
    $Routes = Get-NetRoute -AddressFamily IPv4 | Where-Object { $_.DestinationPrefix -eq "192.168.100.0/24" -or $_.DestinationPrefix -eq "0.0.0.0/0" }
    foreach ($Route in $Routes) {
        Write-TroubleshootLog "   $($Route.DestinationPrefix) via $($Route.NextHop) [$($Route.InterfaceAlias)]" "INFO"
    }
    
    # Show ARP table for Pi subnet
    Write-TroubleshootLog " ARP Table (Pi Subnet):" "INFO"
    $ARPEntries = Get-NetNeighbor -AddressFamily IPv4 | Where-Object { $_.IPAddress -like "192.168.100.*" }
    if ($ARPEntries) {
        foreach ($Entry in $ARPEntries) {
            Write-TroubleshootLog "   $($Entry.IPAddress) -> $($Entry.LinkLayerAddress) [$($Entry.State)]" "INFO"
        }
    }
    else {
        Write-TroubleshootLog "   No ARP entries found for Pi subnet" "INFO"
    }
    
    # Show active connections
    Write-TroubleshootLog " Active Network Connections:" "INFO"
    $Connections = Get-NetTCPConnection | Where-Object { $_.LocalAddress -eq $HostIP -or $_.RemoteAddress -eq $PiIP }
    if ($Connections) {
        foreach ($Conn in $Connections) {
            Write-TroubleshootLog "   $($Conn.LocalAddress):$($Conn.LocalPort) -> $($Conn.RemoteAddress):$($Conn.RemotePort) [$($Conn.State)]" "INFO"
        }
    }
    else {
        Write-TroubleshootLog "   No active connections to Pi" "INFO"
    }
}

function Repair-NetworkConfiguration {
    Write-TroubleshootLog " Attempting automatic network repair..." "INFO"
    
    if (-not (Test-AdminRights)) {
        Write-TroubleshootLog " Administrator rights required for automatic repair" "ERROR"
        Write-TroubleshootLog " Please run: Right-click PowerShell -> 'Run as Administrator'" "INFO"
        return $false
    }
    
    $PiAdapter = Find-PiAdapter
    if (-not $PiAdapter) {
        Write-TroubleshootLog " Cannot identify Pi network adapter for repair" "ERROR"
        return $false
    }
    
    Write-TroubleshootLog " Repairing adapter: $($PiAdapter.Name)" "INFO"
    
    # Step 1: Reset adapter
    Write-TroubleshootLog "  1 Resetting network adapter..." "INFO"
    Disable-NetAdapter -Name $PiAdapter.Name -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
    Enable-NetAdapter -Name $PiAdapter.Name -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 5
    
    # Step 2: Configure IP address
    Write-TroubleshootLog "  2 Configuring IP address..." "INFO"
    $ConfigResult = Set-PiNetworkAdapter -AdapterName $PiAdapter.Name
    
    if ($ConfigResult) {
        Write-TroubleshootLog "  3 Testing connectivity..." "INFO"
        Start-Sleep -Seconds 3
        $TestResult = Test-PiConnectivity -IP $PiIP
        
        if ($TestResult.Ping) {
            Write-TroubleshootLog " Network repair successful!" "SUCCESS"
            return $true
        }
        else {
            Write-TroubleshootLog "  Network configured but Pi not responding" "WARN"
            Write-TroubleshootLog " Pi may need configuration or may not be powered on" "INFO"
            return $false
        }
    }
    
    return $false
}

# Main execution
Write-TroubleshootLog " EQ12 Pi Connection Troubleshooter" "INFO"
Write-TroubleshootLog "Target Pi: $PiIP | Host: $HostIP" "INFO"
Write-TroubleshootLog "Credentials: $Username | Log: $LogPath" "INFO"
Write-TroubleshootLog "" "INFO"

# Step 1: Check admin rights
if (-not (Test-AdminRights)) {
    Write-TroubleshootLog "  Running without Administrator privileges" "WARN"
    Write-TroubleshootLog " Some repair functions will be limited" "INFO"
}

# Step 2: Analyze network adapters
$AdapterStatus = Get-NetworkAdapterStatus

# Step 3: Find Pi adapter
$PiAdapter = Find-PiAdapter

# Step 4: Test current connectivity
$ConnectivityResult = Test-PiConnectivity -IP $PiIP

# Step 5: Physical connection check
Get-PhysicalConnectionStatus

# Step 6: Show detailed status if requested
if ($ShowDetailedStatus) {
    Show-DetailedNetworkStatus
}

# Step 7: Attempt automatic repair if requested
if ($FixNetwork -and $PiAdapter) {
    $RepairResult = Repair-NetworkConfiguration
}

# Step 8: Enable adapter if requested
if ($EnableAdapter -and $PiAdapter) {
    Enable-NetworkAdapter -AdapterName $PiAdapter.Name
}

# Summary and recommendations
Write-TroubleshootLog "" "INFO"
Write-TroubleshootLog " TROUBLESHOOTING SUMMARY:" "INFO"
Write-TroubleshootLog " Physical Connection: $(if ($PiAdapter -and $PiAdapter.Status -eq 'Up') { ' Connected' } else { ' Disconnected' })" "INFO"
Write-TroubleshootLog " Host IP Configuration: $(if ($PiAdapter -and $PiAdapter.HasTargetIP) { ' Configured' } else { ' Not Configured' })" "INFO"
Write-TroubleshootLog " Pi Connectivity: $(if ($ConnectivityResult.Ping) { ' Responding' } else { ' Not Responding' })" "INFO"
Write-TroubleshootLog " SSH Access: $(if ($ConnectivityResult.SSH) { ' Available' } else { ' Not Available' })" "INFO"

Write-TroubleshootLog "" "INFO"
Write-TroubleshootLog " RECOMMENDED ACTIONS:" "INFO"

if (-not $PiAdapter) {
    Write-TroubleshootLog "1.  Connect Ethernet cable between Pi and EQ12 system" "INFO"
    Write-TroubleshootLog "2.  Ensure Pi is powered on with 5V 5A power supply" "INFO"
    Write-TroubleshootLog "3.  Run script again: .\eq12_pi_troubleshooter.ps1 -FixNetwork" "INFO"
}
elseif ($PiAdapter.Status -eq "Disconnected") {
    Write-TroubleshootLog "1.  Check Ethernet cable connection" "INFO"
    Write-TroubleshootLog "2.  Verify Pi power (check LED indicators)" "INFO"
    Write-TroubleshootLog "3.  Try: .\eq12_pi_troubleshooter.ps1 -EnableAdapter -FixNetwork" "INFO"
}
elseif (-not $PiAdapter.HasTargetIP) {
    Write-TroubleshootLog "1.  Configure network: .\eq12_pi_troubleshooter.ps1 -FixNetwork" "INFO"
    Write-TroubleshootLog "2.  Run as Administrator for automatic configuration" "INFO"
}
elseif (-not $ConnectivityResult.Ping) {
    Write-TroubleshootLog "1.  Configure Pi network settings (see instructions below)" "INFO"
    Write-TroubleshootLog "2.  Use Raspberry Pi Imager with static IP preset" "INFO"
    Write-TroubleshootLog "3.  Follow manual setup guide" "INFO"
    Show-PiSetupInstructions
}

Write-TroubleshootLog "" "INFO"
Write-TroubleshootLog " Full log saved to: $LogPath" "INFO"
Write-TroubleshootLog " Setup guide: C:\EQ12\PI_ETHERNET_SETUP_INSTRUCTIONS.md" "INFO"