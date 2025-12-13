#Requires -Version 5.1

[CmdletBinding()]
param(
    [ValidateSet("Scan", "Test", "Status")]
    [string]$Action = "Scan",
    
    [string]$IP = "192.168.100.2",
    [string]$Username = "ricoj100", 
    [string]$Password = "102120sRO1!",
    [int]$Timeout = 30
)

# Logging setup
$LogPath = "C:\EQ12\logs"
$LogFile = Join-Path $LogPath "tpu_scanner_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
if (-not (Test-Path $LogPath)) { New-Item -Path $LogPath -ItemType Directory -Force }

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

function Test-PiConnection {
    param([string]$TargetIP)
    
    Write-Log "Testing connection to Pi at $TargetIP..."
    
    # Test ping
    $PingTest = Test-NetConnection -ComputerName $TargetIP -InformationLevel Quiet
    if (-not $PingTest) {
        Write-Log "Ping failed to $TargetIP" "ERROR"
        return $false
    }
    
    Write-Log "Ping successful to $TargetIP"
    
    # Test SSH port
    $SSHTest = Test-NetConnection -ComputerName $TargetIP -Port 22 -InformationLevel Quiet
    if (-not $SSHTest) {
        Write-Log "SSH port 22 not accessible on $TargetIP" "ERROR"
        return $false
    }
    
    Write-Log "SSH port accessible on $TargetIP"
    return $true
}

function Invoke-PiSSHCommand {
    param([string]$TargetIP, [string]$Command, [string]$Description)
    
    Write-Log "SSH Command [$TargetIP]: $Description"
    
    try {
        $Result = echo $Password | ssh -o StrictHostKeyChecking=no -o ConnectTimeout=$Timeout $Username@$TargetIP "$Command" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "SSH command successful" "DEBUG"
            return $Result
        }
        else {
            Write-Log "SSH command returned exit code: $LASTEXITCODE" "WARNING"
            return $Result
        }
    }
    catch {
        Write-Log "SSH command failed: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Get-PiSystemInfo {
    param([string]$TargetIP)
    
    Write-Log "Gathering Pi system information..."
    
    $InfoCommand = "echo 'HOSTNAME:'`$(hostname); echo 'ARCH:'`$(uname -m); echo 'MEMORY:'`$(free -m | grep '^Mem:' | awk '{print `$2}'); echo 'CPU:'`$(nproc); echo 'TEMP:'`$(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 || echo 'N/A')"
    
    $Result = Invoke-PiSSHCommand -TargetIP $TargetIP -Command $InfoCommand -Description "System info collection"
    
    $SystemInfo = @{}
    if ($Result) {
        $Lines = $Result -split "`n"
        foreach ($Line in $Lines) {
            if ($Line -match "^([^:]+):(.+)$") {
                $Key = $Matches[1].Trim()
                $Value = $Matches[2].Trim()
                $SystemInfo[$Key] = $Value
            }
        }
    }
    
    return $SystemInfo
}

function Get-PiTPUDevices {
    param([string]$TargetIP)
    
    Write-Log "Scanning for TPU devices on Pi..."
    
    $TPUCommand = "lsusb | grep -i 'Google\|Coral' || echo 'NO_TPU_FOUND'"
    $Result = Invoke-PiSSHCommand -TargetIP $TargetIP -Command $TPUCommand -Description "TPU device scan"
    
    $TPUDevices = @()
    if ($Result -and $Result -ne "NO_TPU_FOUND") {
        $Lines = $Result -split "`n"
        foreach ($Line in $Lines) {
            if ($Line -match "Bus (\d+) Device (\d+): ID ([a-f0-9:]+) (.+)" -and $Line -match "Google|Coral") {
                $TPUDevices += @{
                    Bus = $Matches[1]
                    Device = $Matches[2]
                    VendorProduct = $Matches[3]
                    Description = $Matches[4].Trim()
                }
            }
        }
    }
    
    if ($TPUDevices.Count -gt 0) {
        Write-Log "Found $($TPUDevices.Count) TPU device(s)"
    }
    else {
        Write-Log "No TPU devices detected"
    }
    
    return $TPUDevices
}

function Show-PiStatus {
    param([hashtable]$SystemInfo, [array]$TPUDevices)
    
    Write-Host ""
    Write-Host "EQ12 PI NODE STATUS" -ForegroundColor Green
    Write-Host "=" * 40 -ForegroundColor Cyan
    Write-Host "IP Address:    $IP" -ForegroundColor White
    Write-Host "Hostname:      $($SystemInfo.HOSTNAME)" -ForegroundColor White
    Write-Host "Architecture:  $($SystemInfo.ARCH)" -ForegroundColor White
    Write-Host "Memory:        $($SystemInfo.MEMORY) MB" -ForegroundColor White
    Write-Host "CPU Cores:     $($SystemInfo.CPU)" -ForegroundColor White
    Write-Host "Temperature:   $($SystemInfo.TEMP)" -ForegroundColor White
    Write-Host ""
    
    if ($TPUDevices.Count -gt 0) {
        Write-Host "TPU DEVICES ($($TPUDevices.Count))" -ForegroundColor Yellow
        Write-Host "-" * 40 -ForegroundColor Cyan
        foreach ($TPU in $TPUDevices) {
            Write-Host "Device: $($TPU.Description)" -ForegroundColor Green
            Write-Host "  Bus: $($TPU.Bus), Device: $($TPU.Device)" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "NO TPU DEVICES DETECTED" -ForegroundColor Yellow
        Write-Host "Connect a Coral USB TPU to enable AI acceleration" -ForegroundColor Gray
    }
    
    Write-Host ""
}

# Main execution
Write-Log "EQ12 TPU Scanner Starting - Action: $Action, Target: $IP"

switch ($Action) {
    "Scan" {
        if (-not (Test-PiConnection -TargetIP $IP)) {
            Write-Log "Cannot connect to Pi at $IP" "ERROR"
            exit 1
        }
        
        $SystemInfo = Get-PiSystemInfo -TargetIP $IP
        $TPUDevices = Get-PiTPUDevices -TargetIP $IP
        
        Show-PiStatus -SystemInfo $SystemInfo -TPUDevices $TPUDevices
    }
    
    "Test" {
        Write-Host "TPU performance testing will be implemented after basic scan works" -ForegroundColor Yellow
    }
    
    "Status" {
        Write-Host "Quick Pi Status Check" -ForegroundColor Cyan
        
        if (Test-PiConnection -TargetIP $IP) {
            Write-Host "Pi is online at $IP" -ForegroundColor Green
        }
        else {
            Write-Host "Pi is offline or unreachable at $IP" -ForegroundColor Red
        }
    }
}

Write-Log "EQ12 TPU Scanner Complete"
Write-Log "Log saved to: $LogFile"