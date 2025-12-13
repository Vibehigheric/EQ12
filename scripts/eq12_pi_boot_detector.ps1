#Requires -Version 5.0
<#
.SYNOPSIS
    EQ12 Raspberry Pi Boot Detection and Connection Verification
.DESCRIPTION
    Monitors Pi boot process with real-time feedback and automatic SSH detection
.PARAMETER MaxMinutes
    Maximum minutes to monitor (default: 10)
.PARAMETER IPAddress
    Pi IP address to monitor (default: 192.168.100.2)
#>

[CmdletBinding()]
param(
    [int]$MaxMinutes = 10,
    [string]$IPAddress = "192.168.100.2"
)

function Write-TimestampLog {
    param([string]$Message, [string]$Color = "White")
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $Color
}

function Test-PiConnection {
    param([string]$IP)
    
    try {
        $ping = Test-Connection -ComputerName $IP -Count 1 -Quiet -ErrorAction SilentlyContinue
        return $ping
    }
    catch {
        return $false
    }
}

function Test-SSHPort {
    param([string]$IP)
    
    try {
        $ssh = Test-NetConnection -ComputerName $IP -Port 22 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        return $ssh.TcpTestSucceeded
    }
    catch {
        return $false
    }
}

# Main monitoring loop
Write-Host ""
Write-Host " EQ12 PI BOOT DETECTOR STARTING" -ForegroundColor Green
Write-Host "Target: $IPAddress" -ForegroundColor Cyan
Write-Host "Timeout: $MaxMinutes minutes" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
$maxAttempts = $MaxMinutes * 12  # 5-second intervals
$attempt = 1

while ($attempt -le $maxAttempts) {
    $elapsed = [math]::Round(((Get-Date) - $startTime).TotalMinutes, 1)
    
    Write-TimestampLog "Check $attempt/$maxAttempts (${elapsed}m): Testing Pi connection..." "Gray"
    
    if (Test-PiConnection -IP $IPAddress) {
        Write-TimestampLog " Pi is responding to ping!" "Green"
        
        Write-TimestampLog "Testing SSH port 22..." "Yellow"
        if (Test-SSHPort -IP $IPAddress) {
            Write-TimestampLog " SSH port is open!" "Green"
            Write-Host ""
            Write-Host " PI BOOT COMPLETE!" -ForegroundColor Green
            Write-Host "Pi is fully online and ready for cluster integration!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next step: ssh ricoj100@$IPAddress" -ForegroundColor Cyan
            Write-Host "Password: 102120sRO1!" -ForegroundColor Cyan
            exit 0
        }
        else {
            Write-TimestampLog " SSH not ready yet, continuing monitoring..." "Yellow"
        }
    }
    else {
        if ($attempt % 6 -eq 0) {  # Every 30 seconds
            Write-TimestampLog " Pi still booting (${elapsed} minutes elapsed)..." "Gray"
        }
    }
    
    $attempt++
    Start-Sleep -Seconds 5
}

# Timeout reached
Write-Host ""
Write-Host " BOOT TIMEOUT REACHED" -ForegroundColor Red
Write-Host "Pi did not respond within $MaxMinutes minutes." -ForegroundColor Red
Write-Host ""
Write-Host "Troubleshooting options:" -ForegroundColor Yellow
Write-Host "1. Run: .\eq12_pi_troubleshooter.ps1" -ForegroundColor Cyan
Write-Host "2. Check USB boot drive and restart Pi" -ForegroundColor Cyan
Write-Host "3. Proceed with Option 2 (re-imaging)" -ForegroundColor Cyan
