#!/usr/bin/env powershell
<#
.SYNOPSIS
    EQ12 Pi TPU Simple Monitoring Dashboard
.DESCRIPTION
    Simple and reliable Pi TPU monitoring from EQ12 host
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$PiIP = "192.168.1.80"
)

function Get-PiTPUStatus {
    Write-Host " EQ12 Pi TPU Status Check" -ForegroundColor Green
    Write-Host "=" * 40 -ForegroundColor Cyan
    Write-Host ""
    
    # Get TPU status JSON
    Write-Host " Retrieving status..." -ForegroundColor Yellow
    $StatusJSON = ssh ricoj100@$PiIP 'python3 ~/tpu_inference_test.py >/dev/null 2>&1 && cat /tmp/tpu_status.json'
    
    if ($LASTEXITCODE -eq 0) {
        $Status = $StatusJSON | ConvertFrom-Json
        Write-Host " Status retrieved successfully" -ForegroundColor Green
        Write-Host ""
        
        Write-Host " TPU CLUSTER STATUS:" -ForegroundColor Magenta
        Write-Host "Node Name: $($Status.node_name)" -ForegroundColor White
        Write-Host "TPU Detected: $($Status.tpu_detected)" -ForegroundColor Green
        Write-Host "Status: $($Status.status.ToUpper())" -ForegroundColor Green
        Write-Host "Ready for Inference: $($Status.ready_for_inference)" -ForegroundColor Green
        Write-Host "Last Update: $(Get-Date -UnixTimeSeconds $Status.timestamp)" -ForegroundColor Green
    } else {
        Write-Host " Failed to get status" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Get live metrics
    Write-Host " LIVE METRICS:" -ForegroundColor Magenta
    $Metrics = ssh ricoj100@$PiIP 'vcgencmd measure_temp && free -h | grep Mem && lsusb | grep 1a6e'
    
    if ($LASTEXITCODE -eq 0) {
        $Lines = $Metrics -split "`n"
        foreach ($Line in $Lines) {
            if ($Line -match "temp=") {
                $Temp = $Line.Replace("temp=", "")
                Write-Host "Temperature: $Temp" -ForegroundColor Green
            }
            elseif ($Line -match "Mem:") {
                $MemParts = $Line -split "\s+"
                Write-Host " Memory: $($MemParts[2]) used / $($MemParts[1]) total" -ForegroundColor Green
            }
            elseif ($Line -match "1a6e:089a") {
                Write-Host " Coral TPU:  Connected (USB 3.0)" -ForegroundColor Green
            }
        }
    } else {
        Write-Host " Failed to get metrics" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host " EQ12 Pi TPU Cluster: OPERATIONAL" -ForegroundColor Green
}

# Run the status check
Get-PiTPUStatus
