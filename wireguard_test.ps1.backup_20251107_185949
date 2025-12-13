# EQ12 WireGuard VPN Testing Script
# Simple script to test and validate WireGuard VPN connections

param(
    [switch]$ShowStatus,
    [switch]$TestConnection,
    [string]$ConfigName = "eq12-betting"
)

function Write-TestLog {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "White" }
    }
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

function Show-WireGuardStatus {
    Write-TestLog "WireGuard Status Report" -Level "SUCCESS"
    Write-Host "============================================" -ForegroundColor Cyan

    # Check WireGuard installation
    $wgPath = "${env:ProgramFiles}\WireGuard\wireguard.exe"
    $wgToolPath = "${env:ProgramFiles}\WireGuard\wg.exe"

    if (Test-Path $wgPath) {
        Write-Host "[OK] WireGuard installed: $wgPath" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] WireGuard not found" -ForegroundColor Red
    }

    if (Test-Path $wgToolPath) {
        Write-Host "[OK] WG tool available: $wgToolPath" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] WG tool not found" -ForegroundColor Red
    }

    # Check service status
    $serviceName = "WireGuardTunnel`$$ConfigName"
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

    if ($service) {
        Write-Host "[TUNNEL] Tunnel Service: $($service.Status)" -ForegroundColor Green
        Write-Host "   Service Name: $($service.Name)" -ForegroundColor Gray
    } else {
        Write-Host "[ERROR] Tunnel Service: NOT INSTALLED" -ForegroundColor Red
    }

    # Check configuration files
    Write-Host "`n[CONFIG] Configuration Files:" -ForegroundColor Cyan
    $configDir = "C:\EQ12\wireguard"
    if (Test-Path $configDir) {
        Get-ChildItem -Path $configDir -Filter "*.conf" | ForEach-Object {
            Write-Host "   [OK] $($_.Name)" -ForegroundColor Green
        }
    } else {
        Write-Host "   [ERROR] Configuration directory not found" -ForegroundColor Red
    }

    # Show active interfaces
    if (Test-Path $wgToolPath) {
        Write-Host "`n[INTERFACES] Active Interfaces:" -ForegroundColor Cyan
        try {
            $wgShow = & $wgToolPath show 2>&1
            if ($LASTEXITCODE -eq 0 -and $wgShow) {
                Write-Host $wgShow -ForegroundColor Gray
            } else {
                Write-Host "   No active interfaces" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   Error checking interfaces" -ForegroundColor Red
        }
    }

    Write-Host "============================================" -ForegroundColor Cyan
}

function Test-VpnConnection {
    Write-TestLog "Testing VPN connection and IP leak protection" -Level "SUCCESS"

    try {
        Write-Host "`n[IP] Checking current IP address..." -ForegroundColor Cyan
        $currentIP = (Invoke-RestMethod -Uri "https://api.ipify.org" -TimeoutSec 10).Trim()
        Write-Host "   Current IP: $currentIP" -ForegroundColor Gray

        Write-Host "`n[DNS] DNS Server Check:" -ForegroundColor Cyan
        $dnsResult = nslookup google.com 2>$null
        if ($dnsResult) {
            Write-Host "   DNS queries working" -ForegroundColor Green
        }

        Write-Host "`n[INFO] Manual leak tests:" -ForegroundColor Cyan
        Write-Host "   Visit: https://ipleak.net" -ForegroundColor Yellow
        Write-Host "   Visit: https://dnsleaktest.com" -ForegroundColor Yellow

        return $true
    } catch {
        Write-TestLog "Failed to test VPN connection: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

# Main execution
Write-TestLog "EQ12 WireGuard VPN Test Script Started" -Level "SUCCESS"
Write-Host "[EQ12] WireGuard VPN Testing Suite" -ForegroundColor Magenta
Write-Host "Configuration: $ConfigName" -ForegroundColor Gray
Write-Host ""

if ($TestConnection) {
    Test-VpnConnection
}

# Show status by default or if explicitly requested
if ($ShowStatus -or (-not $TestConnection)) {
    Show-WireGuardStatus
}

Write-TestLog "EQ12 WireGuard test script completed" -Level "SUCCESS"
