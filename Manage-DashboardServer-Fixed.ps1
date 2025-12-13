#requires -Version 5.1
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidateSet('start','stop','restart','status','test')]
  [string]$Action,

  [int]$Port = 3000,

  # If node isn't on PATH, set $env:EQ12_NODE to the full node.exe path
  [string]$NodePath = $(if ($env:EQ12_NODE) { $env:EQ12_NODE } else { (Get-Command node -ErrorAction SilentlyContinue).Source }),

  # Adjust if your server file lives elsewhere
  [string]$ScriptPath = (Join-Path $PSScriptRoot 'eq12_dashboard_server.js'),

  [string]$LogPath = (Join-Path $PSScriptRoot 'logs\dashboard-server.log')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Log {
  param([Parameter(Mandatory)][string]$Message,[ValidateSet('INFO','WARN','ERROR')][string]$Level='INFO')
  $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  $line = "[{0}] [{1}] {2}" -f $ts, $Level, $Message
  Write-Host $line
  try {
    New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null
    Add-Content -LiteralPath $LogPath -Value $line
  } catch {}
}

function Get-ServerProcess {
  try {
    $con = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($con) { return Get-Process -Id $con.OwningProcess -ErrorAction SilentlyContinue }
  } catch {}
  return $null
}

function Show-ServerStatus {
  $proc = Get-ServerProcess
  if ($proc) {
    Write-Log "Dashboard server is LISTENING on port $Port (PID: $($proc.Id))"
  } else {
    Write-Log "Dashboard server is NOT running on port $Port" "WARN"
  }
}

function Start-Server {
  if (-not (Test-Path $ScriptPath)) { throw "Server script not found: $ScriptPath" }
  if (-not $NodePath) { throw "Node.js not found. Install Node or set `$env:EQ12_NODE to node.exe." }

  if (Get-ServerProcess) { Show-ServerStatus; return }

  $env:PORT = "$Port"
  $args = @("$ScriptPath")

  Write-Log "Starting dashboard: `"$NodePath`" $($args -join ' ') (PORT=$Port)"
  $si = New-Object System.Diagnostics.ProcessStartInfo
  $si.FileName = $NodePath
  $si.Arguments = ($args -join ' ')
  $si.WorkingDirectory = Split-Path $ScriptPath
  $si.UseShellExecute = $false
  $si.RedirectStandardOutput = $true
  $si.RedirectStandardError  = $true
  [void][System.Diagnostics.Process]::Start($si)
  Start-Sleep -Milliseconds 400
  Show-ServerStatus
}

function Stop-Server {
  $proc = Get-ServerProcess
  if ($proc) {
    Write-Log "Stopping dashboard PID $($proc.Id) on port $Port"
    Stop-Process -Id $proc.Id -Force
    Start-Sleep -Milliseconds 300
  } else {
    Write-Log "No process found on port $Port" "WARN"
  }
  Show-ServerStatus
}

function Restart-Server { Stop-Server; Start-Server }

function Test-Server {
  Show-ServerStatus

  # Root redirect test (expect 302 to /dashboard)
  try {
    Invoke-WebRequest -Uri ("http://localhost:{0}/" -f $Port) -MaximumRedirection 0 -ErrorAction Stop | Out-Null
    Write-Log "Root redirect: FAIL (no redirect received)" "WARN"
  } catch {
    $resp = $_.Exception.Response
    if ($resp -and ($resp.StatusCode.value__ -eq 302)) {
      Write-Log ("Root redirect: PASS (302 → {0})" -f $resp.Headers.Location)
    } else {
      Write-Log ("Root redirect: FAIL: {0}" -f $_.Exception.Message) "ERROR"
    }
  }

  # /health test
  try {
    $health = Invoke-WebRequest -Uri ("http://localhost:{0}/health" -f $Port) -TimeoutSec 5
    Write-Log ("Health endpoint: PASS ({0}, {1} bytes)" -f $health.StatusCode, $health.RawContentLength)
  } catch {
    Write-Log ("Health endpoint: FAIL: {0}" -f $_.Exception.Message) "ERROR"
  }
}

switch ($Action) {
  'start'   { Start-Server; break }
  'stop'    { Stop-Server; break }
  'restart' { Restart-Server; break }
  'status'  { Show-ServerStatus; break }
  'test'    { Test-Server; break }
  default {
@"
Usage:
  .\Manage-DashboardServer.ps1 -Action [start|stop|restart|status|test] [-Port 3000]

Examples:
  .\Manage-DashboardServer.ps1 -Action start
  .\Manage-DashboardServer.ps1 -Action test -Port 3000
"@ | ForEach-Object { Write-Log $_ }
  }
}
