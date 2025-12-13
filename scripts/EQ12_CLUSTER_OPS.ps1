<#
.SYNOPSIS
    EQ12 Cluster Operations Manager
    Manages the distributed system: Windows (Brain) + Raspberry Pi (Edge/TPU).

.DESCRIPTION
    Performs health checks (Scan) and code deployment (Update) across the cluster.
    
.PARAMETER Task
    "Scan" or "Update". Defaults to "Scan".
#>

param(
    [ValidateSet("Scan", "Update")]
    [string]$Task = "Scan"
)

$PiIP = "192.168.1.80"
$PiUser = "ricoj100"
$PiPass = "102120sRO1!"
# WSL wrapper for sshpass
$SSHCmd = "wsl -e sshpass -p '$PiPass' ssh -o StrictHostKeyChecking=no $PiUser@$PiIP"
$SCPCmd = "wsl -e sshpass -p '$PiPass' scp -o StrictHostKeyChecking=no"

function Scan-Cluster {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "   EQ12 CLUSTER STATUS: $Task" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Cyan

    # --- 1. Local Windows Node ---
    Write-Host "`n[LOCAL] Windows Node (The Brain)" -ForegroundColor Magenta
    $BettingScript = "src\eq12_betting_cluster.py"
    if (Test-Path $BettingScript) {
        Write-Host "  [+] Strategy Engine Script: FOUND" -ForegroundColor Green
    }
    else {
        Write-Host "  [-] Strategy Engine Script: MISSING ($BettingScript)" -ForegroundColor Red
    }
    
    # Check Python
    try {
        $PyVer = python --version 2>&1
        Write-Host "  [+] Python Environment: $PyVer" -ForegroundColor Green
    }
    catch {
        Write-Host "  [-] Python Environment: ERROR" -ForegroundColor Red
    }

    # --- 2. Remote Raspberry Pi Node ---
    Write-Host "`n[REMOTE] Raspberry Pi Node (The Edge)" -ForegroundColor Magenta
    Write-Host "  Connecting to $PiIP..."
    
    if (Test-Connection -ComputerName $PiIP -Count 1 -Quiet) {
        Write-Host "  [+] Network Ping: ONLINE" -ForegroundColor Green
        
        # Check Docker
        $DockerVer = Invoke-Expression "$SSHCmd 'docker --version'"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [+] Docker: $DockerVer" -ForegroundColor Green
        }
        else {
            Write-Host "  [-] Docker: NOT FOUND or ERROR" -ForegroundColor Red
        }

        # Check TPU
        # 1a6e:089a is Global Unichip Corp. (Google Coral)
        $USBCheck = Invoke-Expression "$SSHCmd 'lsusb'"
        if ($USBCheck -match "Google" -or $USBCheck -match "Global Unichip") {
            Write-Host "  [+] Coral TPU: DETECTED (USB)" -ForegroundColor Green
        }
        else {
            Write-Host "  [-] Coral TPU: NOT DETECTED" -ForegroundColor Red
            Write-Host "      Raw USB List:"
            $USBCheck | ForEach-Object { Write-Host "      $_" -ForegroundColor Gray }
        }

        # Check Templates
        $RemoteFiles = Invoke-Expression "$SSHCmd 'ls ~/coral_templates'"
        if ($RemoteFiles -match "run_sports_demo.sh") {
            Write-Host "  [+] Sports Templates: DEPLOYED" -ForegroundColor Green
        }
        else {
            Write-Host "  [-] Sports Templates: MISSING" -ForegroundColor Yellow
        }

    }
    else {
        Write-Host "  [-] Network Ping: OFFLINE" -ForegroundColor Red
    }
    Write-Host "`n==========================================" -ForegroundColor Cyan
}

function Update-Cluster {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "   EQ12 CLUSTER UPDATE" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Cyan

    # --- 1. Deploy to Pi ---
    Write-Host "`n[UPDATE] Deploying Code to Raspberry Pi..." -ForegroundColor Magenta
    
    # Convert Windows path to WSL path for SCP
    # Assuming script is run from repo root
    $RepoRoot = Get-Location
    # Simple conversion for C: drive
    $WSLPath = "/mnt/c" + $RepoRoot.Path.Substring(2).Replace("\", "/") + "/scripts/coral_templates/"
    $RemotePath = "~/coral_templates/"
    
    Write-Host "  Source: $WSLPath"
    Write-Host "  Dest:   $RemotePath"

    # Ensure remote dir exists
    Invoke-Expression "$SSHCmd 'mkdir -p $RemotePath'"
    
    # Copy files
    Write-Host "  Copying files..."
    # Remove trailing slash from source to copy the folder itself
    $WSLPathClean = $WSLPath.TrimEnd("/")
    $CopyCmd = "$SCPCmd -r $WSLPathClean $PiUser@$PiIP`:~/"
    Invoke-Expression $CopyCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] File Transfer: SUCCESS" -ForegroundColor Green
        
        # Make executable
        Invoke-Expression "$SSHCmd 'chmod +x $RemotePath*.sh'"
        Write-Host "  [+] Permissions: UPDATED (+x)" -ForegroundColor Green
    }
    else {
        Write-Host "  [-] File Transfer: FAILED" -ForegroundColor Red
    }

    Write-Host "`n[UPDATE] Cluster Sync Complete." -ForegroundColor Green
}

if ($Task -eq "Scan") { Scan-Cluster }
if ($Task -eq "Update") { Update-Cluster }
