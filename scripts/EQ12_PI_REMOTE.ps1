[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$PiUser = "ricoj100",
    
    [Parameter(Mandatory=$false)]
    [string]$PiIP = "192.168.1.80",
    
    [Parameter(Mandatory=$false)]
    [string]$Command = "info"
)

function Invoke-PiCommand {
    param(
        [string]$User,
        [string]$IP,
        [string]$RemoteCommand
    )
    
    try {
        $output = ssh "$User@$IP" $RemoteCommand 2>&1
        return $output
    }
    catch {
        Write-Error "SSH Connection failed: $_"
        return $null
    }
}

Write-Host "EQ12 Raspberry Pi Remote Management" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

switch ($Command.ToLower()) {
    "info" {
        Write-Host "Getting Raspberry Pi Information..." -ForegroundColor Yellow
        Write-Host ""
        
        Write-Host "System Info:" -ForegroundColor Green
        Invoke-PiCommand -User $PiUser -IP $PiIP -RemoteCommand "uname -a"
        Write-Host ""
        
        Write-Host "CPU Info:" -ForegroundColor Green
        Invoke-PiCommand -User $PiUser -IP $PiIP -RemoteCommand "cat /proc/cpuinfo | grep -E 'model name|processor|cores'"
        Write-Host ""
        
        Write-Host "Memory Usage:" -ForegroundColor Green
        Invoke-PiCommand -User $PiUser -IP $PiIP -RemoteCommand "free -h"
        Write-Host ""
        
        Write-Host "Disk Usage:" -ForegroundColor Green
        Invoke-PiCommand -User $PiUser -IP $PiIP -RemoteCommand "df -h"
        Write-Host ""
    }
    
    "usb" {
        Write-Host "USB Devices on Raspberry Pi:" -ForegroundColor Green
        Invoke-PiCommand -User $PiUser -IP $PiIP -RemoteCommand "lsusb"
        Write-Host ""
    }
    
    "storage" {
        Write-Host "Storage Devices:" -ForegroundColor Green
        Invoke-PiCommand -User $PiUser -IP $PiIP -RemoteCommand "lsblk"
        Write-Host ""
    }
    
    "network" {
        Write-Host "Network Interfaces:" -ForegroundColor Green
        Invoke-PiCommand -User $PiUser -IP $PiIP -RemoteCommand "ifconfig"
        Write-Host ""
    }
    
    "services" {
        Write-Host "Running Services:" -ForegroundColor Green
        Invoke-PiCommand -User $PiUser -IP $PiIP -RemoteCommand "systemctl list-units --type=service --state=running"
        Write-Host ""
    }
    
    "scan" {
        Write-Host "Scanning EQ12 Cluster Network (192.168.100.0/24)..." -ForegroundColor Yellow
        Write-Host ""
        Invoke-PiCommand -User $PiUser -IP $PiIP -RemoteCommand "nmap -sn 192.168.100.0/24 | grep -E 'Nmap scan report|Host is up'"
        Write-Host ""
    }
    
    default {
        Write-Host "Usage: .\EQ12_PI_REMOTE.ps1 -Command <command>" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Available commands:" -ForegroundColor Cyan
        Write-Host "  info     - System information (CPU, memory, disk)" -ForegroundColor Green
        Write-Host "  usb      - List USB devices" -ForegroundColor Green
        Write-Host "  storage  - List storage devices" -ForegroundColor Green
        Write-Host "  network  - Network configuration" -ForegroundColor Green
        Write-Host "  services - Running systemd services" -ForegroundColor Green
        Write-Host "  scan     - Scan EQ12 cluster network" -ForegroundColor Green
        Write-Host ""
    }
}

Write-Host "Completed!" -ForegroundColor Cyan
