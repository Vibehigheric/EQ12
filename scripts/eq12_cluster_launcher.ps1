<#
.SYNOPSIS
    EQ12 Cluster Launcher & Status Dashboard
.DESCRIPTION
    Reads the cluster inventory, checks connectivity (Ping + SSH), and displays the status of the distributed AI cluster.
    Run this from the EQ12 Controller (Windows).
#>

param(
    [string]$InventoryPath = "$PSScriptRoot\cluster\inventory.json"
)

$ErrorActionPreference = "Stop"

function Test-SSHConnection {
    param($User, $Ip)
    # Try a simple echo command via SSH. 
    # Requires key-based auth or cached credentials for non-interactive run, 
    # otherwise it might hang prompting for password if not handled carefully.
    # We use BatchMode to fail fast if no auth method is available without interaction.
    $cmd = "ssh -o BatchMode=yes -o ConnectTimeout=3 $User@$Ip echo ok"
    try {
        $res = Invoke-Expression $cmd 2>&1
        if ($LASTEXITCODE -eq 0 -and "$res" -match "ok") { return $true }
    }
    catch {}
    return $false
}

if (-not (Test-Path $InventoryPath)) {
    Write-Error "Inventory file not found at $InventoryPath"
    exit 1
}

$nodes = Get-Content $InventoryPath | ConvertFrom-Json

Write-Host "`n🌐 EQ12 DISTRIBUTED CLUSTER STATUS" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Controller: $env:COMPUTERNAME"
Write-Host "Time:       $(Get-Date)"
Write-Host ""

$results = @()

foreach ($node in $nodes) {
    Write-Host "Checking $($node.name) ($($node.ip))..." -NoNewline

    # 1. Ping Test
    $ping = Test-Connection -ComputerName $node.ip -Count 1 -Quiet
    
    # 2. SSH Test (only if ping works)
    $sshStatus = "N/A"
    if ($ping) {
        if (Test-SSHConnection -User $node.user -Ip $node.ip) {
            $sshStatus = "✅ OK"
        }
        else {
            $sshStatus = "❌ Auth/Conn Fail"
        }
    }
    else {
        $sshStatus = "❌ Unreachable"
    }

    $statusObj = [PSCustomObject]@{
        Node   = $node.name
        IP     = $node.ip
        Role   = $node.role
        OS     = $node.os
        Online = if ($ping) { "✅ Yes" } else { "❌ No" }
        SSH    = $sshStatus
    }
    $results += $statusObj
    
    if ($ping) { Write-Host " Done." -ForegroundColor Green } else { Write-Host " Unreachable." -ForegroundColor Red }
}

Write-Host ""
$results | Format-Table -AutoSize

Write-Host "ACTIONS:" -ForegroundColor Yellow
Write-Host "1. To bootstrap a Linux node (M70q/Pi), SSH in and run the commands in scripts/cluster/bootstrap_ssh_linux.sh"
Write-Host "2. To bootstrap a Windows node, run scripts/cluster/bootstrap_ssh_windows.ps1 on that machine."
Write-Host "3. Once all SSH checks pass, run 'scripts/swarm-admin/scan_and_upgrade_swarm.sh' (via WSL) to deploy Docker Swarm."
