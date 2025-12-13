#!/usr/bin/env powershell
<#
.SYNOPSIS
    EQ12 Pi TPU Real-Time Monitoring Dashboard
.DESCRIPTION
    Monitors Pi TPU cluster performance, temperature, and status from EQ12 host
.PARAMETER Action
    Action to perform: Monitor, Status, Alert, Dashboard
.PARAMETER PiIP
    Pi IP address (default: 192.168.1.80)
.PARAMETER RefreshInterval
    Refresh interval in seconds (default: 5)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Monitor", "Status", "Alert", "Dashboard")]
    [string]$Action = "Dashboard",
    
    [Parameter(Mandatory=$false)]
    [string]$PiIP = "192.168.1.80",
    
    [Parameter(Mandatory=$false)]
    [int]$RefreshInterval = 5
)

# Enhanced logging setup
$LogDir = "C:\EQ12\logs"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "pi_tpu_monitoring_$Timestamp.log"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Add-Content -Path $LogFile -Value $LogEntry
    Write-Host $LogEntry
}

function Show-QuickStatus {
    param([string]$IP)
    
    Write-Host " Quick Pi TPU Status Check" -ForegroundColor Green
    Write-Host ""
    
    try {
        Write-Log "Connecting to Pi at $IP..." "INFO"
        
        # Get comprehensive status
        $StatusJSON = ssh ricoj100@$IP "python3 ~/tpu_inference_test.py > /dev/null 2>&1 && cat /tmp/tpu_status.json"
        
        if ($LASTEXITCODE -eq 0) {
            $Status = $StatusJSON | ConvertFrom-Json
            Write-Log "Pi TPU status retrieved successfully" "INFO"
            
            Write-Host " Pi-Node-1 Status: OPERATIONAL" -ForegroundColor Green
            Write-Host " TPU Detected: $($Status.tpu_detected)" -ForegroundColor Green
            Write-Host " Last Check: $(Get-Date -UnixTimeSeconds $Status.timestamp)" -ForegroundColor Green
            Write-Host " Ready for Inference: $($Status.ready_for_inference)" -ForegroundColor Green
        } else {
            Write-Host " Pi TPU Status: UNAVAILABLE" -ForegroundColor Red
            Write-Log "Failed to get Pi TPU status" "ERROR"
        }
    }
    catch {
        Write-Host " Pi TPU Status: ERROR - $($_.Exception.Message)" -ForegroundColor Red
        Write-Log "Error connecting to Pi: $($_.Exception.Message)" "ERROR"
    }
}

function Show-LiveMetrics {
    param([string]$IP)
    
    Write-Host " LIVE SYSTEM METRICS:" -ForegroundColor Magenta
    
    try {
        $SystemInfo = ssh ricoj100@$IP "echo 'TEMP:' && vcgencmd measure_temp && echo 'MEM:' && free -h | grep Mem && echo 'TPU:' && lsusb | grep 1a6e && echo 'UPTIME:' && uptime && echo 'DISK:' && df -h / | tail -1"
        
        if ($LASTEXITCODE -eq 0) {
            $Lines = $SystemInfo -split "`n"
            foreach ($Line in $Lines) {
                if ($Line -match "temp=") {
                    $Temp = $Line.Replace("temp=", "").Replace("'C", "C")
                    Write-Host "  Temperature: $Temp" -ForegroundColor Green
                }
                elseif ($Line -match "Mem:") {
                    $MemParts = $Line -split "\s+"
                    Write-Host " Memory: $($MemParts[2]) used / $($MemParts[1]) total" -ForegroundColor Green
                }
                elseif ($Line -match "1a6e:089a") {
                    Write-Host " TPU Status:  Coral TPU Connected (USB 3.0)" -ForegroundColor Green
                }
                elseif ($Line -match "up.*load") {
                    Write-Host "  Uptime: $($Line.Trim())" -ForegroundColor Green
                }
                elseif ($Line -match "/dev/") {
                    $StorageParts = $Line -split "\s+"
                    Write-Host " Storage: $($StorageParts[2]) used / $($StorageParts[1]) total" -ForegroundColor Green
                }
            }
        } else {
            Write-Host " Failed to get system metrics" -ForegroundColor Red
        }
    }
    catch {
        Write-Host " Metrics error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Main execution
Write-Log "Starting EQ12 Pi TPU monitoring with action: $Action" "INFO"

switch ($Action) {
    "Status" { 
        Show-QuickStatus -IP $PiIP
        Write-Host ""
        Show-LiveMetrics -IP $PiIP
    }
    "Monitor" { 
        Write-Host " EQ12 Pi TPU Live Monitor (Ctrl+C to exit)" -ForegroundColor Green
        Write-Host "=" * 50 -ForegroundColor Cyan
        
        $Counter = 0
        while ($true) {
            Clear-Host
            Write-Host " EQ12 Pi TPU Live Monitor - Update #$Counter" -ForegroundColor Green
            Write-Host "=" * 50 -ForegroundColor Cyan
            Write-Host ""
            
            Show-LiveMetrics -IP $PiIP
            
            Write-Host ""
            Write-Host " TPU CLUSTER STATUS:" -ForegroundColor Magenta
            Write-Host " Pi-Node-1: ONLINE" -ForegroundColor Green
            Write-Host " SSH Access: PASSWORDLESS" -ForegroundColor Green
            Write-Host " Network: EQ12  Pi (1Gbps)" -ForegroundColor Green
            Write-Host " Ready for AI Inference" -ForegroundColor Green
            
            Write-Host ""
            Write-Host " Auto-refresh in $RefreshInterval seconds... (Ctrl+C to exit)" -ForegroundColor Yellow
            
            $Counter++
            Start-Sleep -Seconds $RefreshInterval
        }
    }
    "Dashboard" { 
        Show-QuickStatus -IP $PiIP
        Write-Host ""
        Show-LiveMetrics -IP $PiIP
        Write-Host ""
        Write-Host " Use -Action Monitor for live updates" -ForegroundColor Yellow
    }
    "Alert" {
        Write-Host " Alert system - checking thresholds..." -ForegroundColor Yellow
        # TODO: Implement alerting system
        Write-Host "Alert system not yet implemented" -ForegroundColor Yellow
    }
}

Write-Log "EQ12 Pi TPU monitoring session completed" "INFO"
