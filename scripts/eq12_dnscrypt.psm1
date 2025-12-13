<#
EQ12 DNSCrypt helper module

Functions:
- Get-EQ12DNSCryptStatus: returns JSON object {ok, status, resolver, ts}
- Restart-EQ12DNSCrypt: restart the dnscrypt service if present
#>

using namespace System

function Get-EQ12LogsPath { # lightweight reimplementation to avoid dependency
    $path = $env:EQ12_LOGS
    if ([string]::IsNullOrWhiteSpace($path)) { $path = 'C:\EQ12\logs' }
    if (-not (Test-Path $path)) { New-Item -Path $path -ItemType Directory -Force | Out-Null }
    return $path
}

function Get-EQ12DNSCryptStatus {
    [CmdletBinding()]
    param()

    $out = @{ ok = $false; status = 'unknown'; resolver = $null; ts = (Get-Date).ToString('o') }
    try {
        # Check for a Windows service named 'dnscrypt-proxy' or 'dnscrypt'
        $svc = Get-Service -Name 'dnscrypt-proxy' -ErrorAction SilentlyContinue
        if (-not $svc) { $svc = Get-Service -Name 'dnscrypt' -ErrorAction SilentlyContinue }
        if ($svc) {
            $out.status = $svc.Status.ToString()
            $out.ok = ($svc.Status -eq 'Running')
            # Optional: try query resolver via nslookup
            try {
                $r = nslookup -timeout=2 1.1.1.1 2>&1 | Out-String
                $out.resolver = $r -replace '\r?\n',' | '
            } catch { $out.resolver = $null }
        } else {
            $out.status = 'not-installed'
            $out.ok = $false
        }
    } catch {
        $out.status = "error: $_"
        $out.ok = $false
    }

    # write to logs
    $logPath = Join-Path (Get-EQ12LogsPath) 'dnscrypt.json'
    try { $out | ConvertTo-Json -Depth 5 | Out-File -FilePath $logPath -Encoding utf8 -Force } catch {}
    return $out
}

function Restart-EQ12DNSCrypt {
    [CmdletBinding()]
    param()

    try {
        $svc = Get-Service -Name 'dnscrypt-proxy' -ErrorAction SilentlyContinue
        if (-not $svc) { $svc = Get-Service -Name 'dnscrypt' -ErrorAction SilentlyContinue }
        if (-not $svc) { Write-Warning 'DNSCrypt service not found'; return $false }
        Restart-Service -InputObject $svc -Force -ErrorAction Stop
        Start-Sleep -Seconds 2
        return $true
    } catch {
        Write-Warning "Failed to restart DNSCrypt service: $_"
        return $false
    }
}

Export-ModuleMember -Function Get-EQ12DNSCryptStatus, Restart-EQ12DNSCrypt
