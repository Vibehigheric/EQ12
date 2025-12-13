<#
  EQ12 WireGuard health check
  - Logs status to C:\EQ12\logs\wg.log
  - Exits 0 when tunnel is up and peer is reachable, otherwise non-zero
#>
Param()

$ErrorActionPreference = 'Stop'

$logdir = 'C:\EQ12\logs'
if (-not (Test-Path $logdir)) { New-Item -ItemType Directory -Path $logdir | Out-Null }
$logfile = Join-Path $logdir 'wg.log'

function Log($msg) {
    $ts = (Get-Date).ToString('s')
    "$ts - $msg" | Out-File -FilePath $logfile -Append -Encoding utf8
}

try {
    Log 'Checking WireGuard status...'
    # On Windows, the wireguard.exe or wg show can provide status if installed
    $wgExe = Get-Command wg -ErrorAction SilentlyContinue
    if ($null -eq $wgExe) {
        Log 'wg tool not found; ensure WireGuard is installed.'
        Write-Error 'wg tool not found'
        exit 2
    }

    $out = & wg show 2>&1
    Log "wg show output: $out"

    # simple check: look for interface and peers
    if ($out -match 'interface:') {
        Log 'WireGuard interface present.'
    } else {
        Log 'No WireGuard interface reported.'
        exit 3
    }

    # Ping peer internal IP (example address)
    $peer = '10.0.0.1'
    $ping = Test-Connection -ComputerName $peer -Count 2 -Quiet
    if ($ping) {
        Log "Peer $peer reachable"
        exit 0
    } else {
        Log "Peer $peer unreachable"
        exit 4
    }
} catch {
    Log "Error checking WireGuard: $_"
    exit 10
}
