# EQ12 Pi Quick Fix - Automated Problem Resolution
# Simple one-command solution for common Pi connectivity issues

[CmdletBinding()]
param(
    [switch]$FixAll,
    [switch]$EnableEthernet,
    [switch]$ConfigureIP,
    [switch]$RestartAdapter,
    [switch]$ShowStatus
)

# Require admin for network changes
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host " This script requires Administrator privileges" -ForegroundColor Red
    Write-Host " Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host " EQ12 Pi Quick Fix - Network Repair Tool" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Find Ethernet adapter with 192.168.100.1 IP
$PiAdapter = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -eq "192.168.100.1" } | ForEach-Object { Get-NetAdapter -InterfaceIndex $_.InterfaceIndex }

if (-not $PiAdapter) {
    Write-Host " Cannot find network adapter with IP 192.168.100.1" -ForegroundColor Red
    Write-Host " Looking for disconnected Ethernet adapters..." -ForegroundColor Yellow
    
    $DisconnectedAdapters = Get-NetAdapter | Where-Object { $_.Name -like "*Ethernet*" -and $_.Status -eq "Disconnected" }
    
    if ($DisconnectedAdapters.Count -eq 1) {
        $PiAdapter = $DisconnectedAdapters[0]
        Write-Host " Found potential Pi adapter: $($PiAdapter.Name)" -ForegroundColor Yellow
    }
    else {
        Write-Host " Multiple or no Ethernet adapters found" -ForegroundColor Red
        Write-Host " Please manually identify the adapter connected to Pi" -ForegroundColor Yellow
        Get-NetAdapter | Where-Object { $_.Name -like "*Ethernet*" } | Format-Table Name, Status, LinkSpeed
        exit 1
    }
}

Write-Host " Using adapter: $($PiAdapter.Name) [$($PiAdapter.Status)]" -ForegroundColor Green

# Show current status
if ($ShowStatus -or $FixAll) {
    Write-Host "`n Current Network Status:" -ForegroundColor Cyan
    
    $AdapterStatus = Get-NetAdapter -Name $PiAdapter.Name
    $IPConfig = Get-NetIPAddress -InterfaceAlias $PiAdapter.Name -AddressFamily IPv4 -ErrorAction SilentlyContinue
    
    Write-Host "  Adapter: $($AdapterStatus.Name)" -ForegroundColor White
    Write-Host "  Status: $($AdapterStatus.Status)" -ForegroundColor $(if ($AdapterStatus.Status -eq "Up") { "Green" } else { "Red" })
    Write-Host "  Speed: $($AdapterStatus.LinkSpeed)" -ForegroundColor White
    Write-Host "  IP Addresses: $($IPConfig.IPAddress -join ', ')" -ForegroundColor White
    
    # Test Pi connectivity
    Write-Host "`n Testing Pi connectivity..." -ForegroundColor Cyan
    $PingResult = Test-Connection -ComputerName "192.168.100.2" -Count 1 -Quiet -ErrorAction SilentlyContinue
    Write-Host "  Ping 192.168.100.2: $(if ($PingResult) { ' Success' } else { ' Failed' })" -ForegroundColor $(if ($PingResult) { "Green" } else { "Red" })
    
    if ($PingResult) {
        $SSHTest = Test-NetConnection -ComputerName "192.168.100.2" -Port 22 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        Write-Host "  SSH Port 22: $(if ($SSHTest.TcpTestSucceeded) { ' Open' } else { ' Closed' })" -ForegroundColor $(if ($SSHTest.TcpTestSucceeded) { "Green" } else { "Red" })
    }
}

# Restart adapter
if ($RestartAdapter -or $FixAll) {
    Write-Host "`n Restarting network adapter..." -ForegroundColor Cyan
    try {
        Disable-NetAdapter -Name $PiAdapter.Name -Confirm:$false
        Start-Sleep -Seconds 3
        Enable-NetAdapter -Name $PiAdapter.Name -Confirm:$false
        Start-Sleep -Seconds 5
        Write-Host " Adapter restarted successfully" -ForegroundColor Green
    }
    catch {
        Write-Host " Failed to restart adapter: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Configure IP address
if ($ConfigureIP -or $FixAll) {
    Write-Host "`n Configuring IP address..." -ForegroundColor Cyan
    try {
        # Remove existing IP configuration
        Remove-NetIPAddress -InterfaceAlias $PiAdapter.Name -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        Remove-NetRoute -InterfaceAlias $PiAdapter.Name -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue
        
        # Set static IP
        New-NetIPAddress -InterfaceAlias $PiAdapter.Name -IPAddress "192.168.100.1" -PrefixLength 24 -ErrorAction Stop
        Set-NetIPInterface -InterfaceAlias $PiAdapter.Name -Dhcp Disabled -ErrorAction Stop
        
        Write-Host " IP address configured: 192.168.100.1/24" -ForegroundColor Green
        Write-Host " DHCP disabled" -ForegroundColor Green
    }
    catch {
        Write-Host " Failed to configure IP: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Enable Ethernet adapter
if ($EnableEthernet -or $FixAll) {
    Write-Host "`n Enabling Ethernet adapter..." -ForegroundColor Cyan
    try {
        Enable-NetAdapter -Name $PiAdapter.Name -Confirm:$false
        Start-Sleep -Seconds 3
        Write-Host " Ethernet adapter enabled" -ForegroundColor Green
    }
    catch {
        Write-Host " Failed to enable adapter: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Final connectivity test
if ($FixAll) {
    Write-Host "`n Final connectivity test..." -ForegroundColor Cyan
    Start-Sleep -Seconds 5  # Wait for network to stabilize
    
    $FinalPing = Test-Connection -ComputerName "192.168.100.2" -Count 3 -Quiet -ErrorAction SilentlyContinue
    if ($FinalPing) {
        Write-Host " SUCCESS! Pi is now reachable at 192.168.100.2" -ForegroundColor Green
        Write-Host " Next step: Run cluster integration" -ForegroundColor Green
        Write-Host "   python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --action add-node --ip 192.168.100.2 --username ricoj100 --password CLUSTER_PASSWORD_PLACEHOLDER" -ForegroundColor Yellow
    }
    else {
        Write-Host "  Network configured but Pi not responding" -ForegroundColor Yellow
        Write-Host " Possible causes:" -ForegroundColor Yellow
        Write-Host "    Pi is not powered on" -ForegroundColor White
        Write-Host "    Pi needs network configuration (see setup guide)" -ForegroundColor White
        Write-Host "    Ethernet cable not connected" -ForegroundColor White
        Write-Host "    Pi OS not installed with SSH enabled" -ForegroundColor White
        Write-Host "`n Setup guide: C:\EQ12\PI_ETHERNET_SETUP_INSTRUCTIONS.md" -ForegroundColor Cyan
    }
}

# Show usage if no parameters
if (-not ($FixAll -or $EnableEthernet -or $ConfigureIP -or $RestartAdapter -or $ShowStatus)) {
    Write-Host "`n Usage Examples:" -ForegroundColor Yellow
    Write-Host "  .\eq12_pi_quickfix.ps1 -FixAll           # Fix everything automatically" -ForegroundColor White
    Write-Host "  .\eq12_pi_quickfix.ps1 -ShowStatus       # Show current status only" -ForegroundColor White
    Write-Host "  .\eq12_pi_quickfix.ps1 -ConfigureIP      # Just configure IP address" -ForegroundColor White
    Write-Host "  .\eq12_pi_quickfix.ps1 -RestartAdapter   # Restart network adapter" -ForegroundColor White
}

Write-Host "`n For detailed troubleshooting, run:" -ForegroundColor Cyan
Write-Host "   .\eq12_pi_troubleshooter.ps1 -ShowDetailedStatus" -ForegroundColor White