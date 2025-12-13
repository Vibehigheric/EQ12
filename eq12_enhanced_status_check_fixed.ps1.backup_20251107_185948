#requires -Version 5.1
[CmdletBinding()]
param(
    [switch]$Json,
    [switch]$Detailed
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-EnvValue {
    param([Parameter(Mandatory)][string]$Name)
    # dynamic env lookup
    if (Test-Path "Env:$Name") { return (Get-Item "Env:$Name").Value }
    return $null
}

function Test-Http {
    param([Parameter(Mandatory)][string]$Url, [ValidateSet('GET', 'HEAD')][string]$Method = 'GET', [int]$TimeoutSec = 5)
    try {
        $r = Invoke-WebRequest -Uri $Url -Method $Method -TimeoutSec $TimeoutSec -MaximumRedirection 0 -ErrorAction Stop
        [pscustomobject]@{ ok = $true; code = [int]$r.StatusCode; note = '' }
    }
    catch {
        $resp = $_.Exception.Response
        if ($resp) {
            [pscustomobject]@{ ok = ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 400); code = [int]$resp.StatusCode; note = $_.Exception.Message }
        }
        else {
            [pscustomobject]@{ ok = $false; code = 0; note = $_.Exception.Message }
        }
    }
}

$checks = @()

# 1) OPENAI key present
$openai = Get-EnvValue -Name 'OPENAI_API_KEY'
$checks += [pscustomobject]@{ name = 'OPENAI_API_KEY present'; ok = [bool]$openai; detail = if ($openai) { 'present' } else { 'missing' } }

# 2) LLM switch
$useLLM = Get-EnvValue -Name 'EQ12_USE_LLM'
$checks += [pscustomobject]@{ name = 'EQ12_USE_LLM enabled'; ok = ($useLLM -eq '1'); detail = "EQ12_USE_LLM=$useLLM" }

# 3) Node present
$node = (Get-Command node -ErrorAction SilentlyContinue).Source
$checks += [pscustomobject]@{ name = 'Node on PATH'; ok = [bool]$node; detail = $node }

# 4) Port 3000 listening?
$port = 3000
$tcp = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
$checks += [pscustomobject]@{ name = "Port $port listening"; ok = [bool]$tcp; detail = if ($tcp) { "PID=$($tcp.OwningProcess)" } else { 'not listening' } }

# 5) /health
$h = Test-Http -Url "http://localhost:$port/health" -Method GET
$checks += [pscustomobject]@{ name = '/health 200'; ok = ($h.code -eq 200); detail = "code=$($h.code) $($h.note)" }

# 6) root redirect to /dashboard (302)
$r = Test-Http -Url "http://localhost:$port/" -Method GET
$checks += [pscustomobject]@{ name = 'root redirect'; ok = ($r.code -eq 302); detail = "code=$($r.code) $($r.note)" }

# Score
$total = $checks.Count
$passed = ($checks | Where-Object ok).Count
$score = "{0}/{1}" -f $passed, $total
$percent = if ($total) { [math]::Round(($passed / $total) * 100, 2) } else { 0 }

if ($Json) {
    $obj = [pscustomobject]@{
        timestamp   = (Get-Date).ToString('s')
        totalChecks = $total
        passed      = $passed
        percent     = $percent
        checks      = $checks
    }
    $obj | ConvertTo-Json -Depth 5
    return
}

# Human output (ASCII only)
Write-Host ("=" * 60) -ForegroundColor Cyan
Write-Host " EQ12 Enhanced Status Check" -ForegroundColor Cyan
Write-Host ("=" * 60) -ForegroundColor Cyan

foreach ($c in $checks) {
    $tag = if ($c.ok) { "[OK]      " } else { "[PROBLEM] " }
    $color = if ($c.ok) { 'Green' } else { 'Red' }
    Write-Host ("{0} {1} :: {2}" -f $tag, $c.name, $c.detail) -ForegroundColor $color
}

Write-Host ("-" * 60) -ForegroundColor DarkGray
Write-Host ("Health Score: {0} ({1}%)" -f $score, $percent) -ForegroundColor Yellow

if ($Detailed) {
    Write-Host ("-" * 60) -ForegroundColor DarkGray
    $checks | Format-Table -AutoSize
}
