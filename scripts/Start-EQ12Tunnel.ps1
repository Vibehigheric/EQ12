<#
.SYNOPSIS
  Start and manage ngrok tunnels for EQ12 services.

.DESCRIPTION
  Conservative dry-run-first wrapper. Reads NGROK_AUTHTOKEN from environment.
  Provides Start-EQ12Tunnel, Stop-EQ12Tunnel, Get-EQ12TunnelStatus functions.

.TODO
  - add Pester tests
#>
[CmdletBinding()]
param()

function Get-NgrokPath {
    $paths = @(
        "$env:ProgramFiles\ngrok\ngrok.exe",
        "$env:LOCALAPPDATA\ngrok\ngrok.exe",
        "C:\\ngrok\\ngrok.exe"
    )
    foreach ($p in $paths) { if (Test-Path $p) { return $p } }
    return $null
}

function Start-EQ12Tunnel {
    [CmdletBinding()]
    param(
        [string]$Service = 'dashboard',
        [int]$LocalPort = 8080,
        [switch]$DryRun
    )

    # TODO: add Pester test
    if (-not $env:NGROK_AUTHTOKEN) {
        Write-Error "NGROK_AUTHTOKEN is not set in environment."
        return
    }

    $ngrok = Get-NgrokPath
    if (-not $ngrok) { Write-Error "ngrok executable not found. Install ngrok or set NGROK_PATH."; return }

    $logdir = 'C:\EQ12\logs'
    if (-not (Test-Path $logdir)) { New-Item -Path $logdir -ItemType Directory -Force | Out-Null }
    $logfile = Join-Path $logdir 'ngrok_tunnels.log'

    $cmd = "$ngrok http $LocalPort --log=stdout --log-format=logfmt"
    Write-Output "Starting ngrok for $Service on port $LocalPort (DryRun=$DryRun)"
    if ($DryRun) {
        Write-Output "Dry-run: would run: $cmd"
        return
    }

    # Start ngrok in background and capture output to get the public URL
    $startInfo = New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName = $ngrok
    $startInfo.Arguments = "http $LocalPort --log=stdout --log-format=logfmt"
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $startInfo
    $proc.Start() | Out-Null

    Start-Sleep -Seconds 2
    $out = $proc.StandardOutput.ReadToEnd()
    $err = $proc.StandardError.ReadToEnd()

    # Try to extract the public URL from logs (ngrok writes lines like "url=http://..."
    $url = $null
    foreach ($line in $out -split "`n") {
        if ($line -match 'url=(https?://[\w\.-:%/]+)') { $url = $Matches[1]; break }
    }

    if ($url) {
        "$((Get-Date).ToString('s'))`t$Service`t$url" | Out-File -FilePath $logfile -Append -Encoding utf8
        Write-Output "Started ngrok for $Service -> $url"
        # Also write structured JSON record
        $jsonLog = Join-Path $logdir 'ngrok.json'
        $record = @{ service = $Service; url = $url; timestamp = (Get-Date).ToString('o') }
        $existing = @()
        if (Test-Path $jsonLog) {
            try { $existing = Get-Content $jsonLog -Raw | ConvertFrom-Json -ErrorAction Stop } catch { $existing = @() }
        }
        $all = $existing + ,$record
        $all | ConvertTo-Json -Depth 3 | Out-File -FilePath $jsonLog -Encoding utf8
    } else {
        Write-Warning "Could not parse ngrok public URL from output. See $logfile for raw logs."
        $out | Out-File -FilePath $logfile -Append -Encoding utf8
        $err | Out-File -FilePath $logfile -Append -Encoding utf8
    }
}

function Stop-EQ12Tunnel {
    [CmdletBinding()]
    param(
        [string]$Service = 'dashboard'
    )
    # Simple stop: try to kill ngrok processes (conservative)
    Get-Process -Name ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Output "Stopped ngrok processes for service $Service"
}

function Get-EQ12TunnelStatus {
    [CmdletBinding()]
    param()
    $logfile = 'C:\EQ12\logs\ngrok_tunnels.log'
    if (Test-Path $logfile) { Get-Content $logfile -Tail 50 } else { Write-Output "No ngrok tunnels log found." }
}

# Note: This script is intended to be dot-sourced to import functions into the caller's scope.
# Do not call Export-ModuleMember here because this file may be dot-sourced or executed directly.
