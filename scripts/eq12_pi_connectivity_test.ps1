[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$PiIP = "192.168.100.2"
)

<#
.SYNOPSIS
    Quick test to check Pi connectivity and network status

.DESCRIPTION
    Tests if Raspberry Pi is reachable and provides setup guidance
#>

function Test-PiConnectivity {
    param([string]$IPAddress)
    
    Write-Host "`nTesting Pi Connectivity..." -ForegroundColor Cyan
    
    # Test ping
    Write-Host "Testing ping to $IPAddress..." -NoNewline
    try {
        $ping = Test-Connection -ComputerName $IPAddress -Count 2 -Quiet
        if ($ping) {
            Write-Host " [SUCCESS]" -ForegroundColor Green
            return $true
        } else {
            Write-Host " [FAILED]" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host " [ERROR]: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-SSHConnectivity {
    param([string]$IPAddress)
    
    Write-Host "Testing SSH port (22) on $IPAddress..." -NoNewline
    try {
        $ssh = Test-NetConnection -ComputerName $IPAddress -Port 22 -WarningAction SilentlyContinue
        if ($ssh.TcpTestSucceeded) {
            Write-Host " [SSH READY]" -ForegroundColor Green
            return $true
        } else {
            Write-Host " [SSH NOT READY]" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host " [ERROR]" -ForegroundColor Red
        return $false
    }
}

function Show-NetworkAdapterStatus {
    Write-Host "`nNetwork Adapter Status:" -ForegroundColor Cyan
    
    $adapters = Get-NetAdapter | Where-Object {$_.Name -like "*Ethernet*"}
    
    foreach ($adapter in $adapters) {
        $status = if ($adapter.Status -eq "Up") { "[UP]" } else { "[DOWN]" }
        $speed = if ($adapter.LinkSpeed -gt 0) { " ($($adapter.LinkSpeed))" } else { "" }
        
        Write-Host "  $status $($adapter.Name): $($adapter.Status)$speed"
        
        # Check if adapter has IP configured
        try {
            $ipConfig = Get-NetIPAddress -InterfaceAlias $adapter.Name -AddressFamily IPv4 -ErrorAction SilentlyContinue
            if ($ipConfig) {
                Write-Host "    IP: $($ipConfig.IPAddress)"
            }
        } catch {
            # Ignore errors
        }
    }
}

function Show-SetupGuidance {
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
    Write-Host "1. Configure network adapters (requires Administrator):"
    Write-Host "    Run: C:\EQ12\SETUP_PI_NETWORK.bat"
    Write-Host "    Or manually configure Ethernet adapter with IP 192.168.100.1"
    Write-Host ""
    Write-Host "2. Configure Pi with IP 192.168.100.2:"
    Write-Host "    Follow guide: C:\EQ12\PI_ETHERNET_SETUP_INSTRUCTIONS.md"
    Write-Host ""
    Write-Host "3. Test connection:"
    Write-Host "    Run this script again: .\eq12_pi_connectivity_test.ps1"
    Write-Host ""
    Write-Host "4. Add Pi to cluster:"
    Write-Host "    python eq12_raspberry_pi_cluster_manager.py --add-node 192.168.100.2"
}

# Main execution
Clear-Host
Write-Host @"
Raspberry Pi Connectivity Test
====================================
Testing direct Ethernet connection to Pi
"@ -ForegroundColor Green

# Show current network status
Show-NetworkAdapterStatus

# Test Pi connectivity
$pingSuccess = Test-PiConnectivity -IPAddress $PiIP

if ($pingSuccess) {
    # Pi is reachable, test SSH
    $sshReady = Test-SSHConnectivity -IPAddress $PiIP
    
    if ($sshReady) {
        Write-Host "`nPi is ready for cluster integration!" -ForegroundColor Green
        Write-Host "Run cluster manager:" -ForegroundColor Cyan
        Write-Host "python C:\EQ12\scripts\eq12_raspberry_pi_cluster_manager.py --add-node $PiIP"
    } else {
        Write-Host "`nPi reachable but SSH not ready" -ForegroundColor Yellow
        Write-Host "Configure SSH on Pi first (see setup guide)"
    }
} else {
    Write-Host "`nPi not reachable" -ForegroundColor Red
    Show-SetupGuidance
}

Write-Host "`nFull setup guide: C:\EQ12\PI_ETHERNET_SETUP_INSTRUCTIONS.md" -ForegroundColor Cyan
