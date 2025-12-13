<#
EQ12 patch
Builds dashboard HTML from JSON snapshots. Produces table-based panels for Crypto/Stocks/Sports/Jobs/Recycle.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$JsonPath,

    [Parameter()]
    [string]$OutHtml
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot

function Get-DefaultPath {
    param(
        [string]$EnvValue,
        [string]$FallbackRelative
    )

    if (-not [string]::IsNullOrWhiteSpace($EnvValue)) {
        return $EnvValue
    }

    return Join-Path -Path $repoRoot -ChildPath $FallbackRelative
}

$logsRoot = Get-DefaultPath -EnvValue $env:EQ12_LOGS -FallbackRelative 'logs'
if (-not $OutHtml) {
    $dashboardRoot = Get-DefaultPath -EnvValue $env:EQ12_DASHBOARD -FallbackRelative 'dashboard'
    if (-not (Test-Path -LiteralPath $dashboardRoot)) {
        New-Item -ItemType Directory -Path $dashboardRoot -Force | Out-Null
    }
    $OutHtml = Join-Path -Path $dashboardRoot -ChildPath 'dashboard.html'
}

Write-Host "Building dashboard from $JsonPath"

if (-not (Test-Path -LiteralPath $JsonPath)) {
    throw "Missing JSON snapshot at $JsonPath"
}

if (Test-Path -LiteralPath $JsonPath -PathType Container) {
    $candidate = Get-ChildItem -Path $JsonPath -Filter '*.json' -File | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $candidate) {
        throw "No JSON files found under $JsonPath"
    }
    Write-Host "JsonPath points to a directory; using latest JSON file $($candidate.FullName)" -ForegroundColor Yellow
    $JsonPath = $candidate.FullName
}

if (-not (Test-Path -LiteralPath (Split-Path -Parent $OutHtml))) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $OutHtml) -Force | Out-Null
}

$jsonText = Get-Content -Path $JsonPath -Raw -Encoding UTF8
try {
    $json = $jsonText | ConvertFrom-Json
} catch {
    throw "Failed to parse JSON from ${JsonPath}: $($_.Exception.Message)"
}

function Get-Eq12TableHtml {
    param(
        [object[]]$items,
        [string]$title
    )

    $html = "<h2>$title</h2><table border=1><thead><tr>"
    if ($items -and $items.Count -gt 0) {
        $cols = $items[0].psobject.properties.name
        foreach ($c in $cols) { $html += "<th>$c</th>" }
        $html += "</tr></thead><tbody>"
        foreach ($r in $items) {
            $html += "<tr>"
            foreach ($c in $cols) {
                $value = $r.$c
                if ($value -is [System.Collections.IEnumerable] -and -not ($value -is [string])) {
                    $value = ($value | Out-String).Trim()
                }
                $html += "<td>$value</td>"
            }
            $html += "</tr>"
        }
        $html += "</tbody></table>"
    } else {
        $html += "</tr></thead><tbody><tr><td>No data</td></tr></tbody></table>"
    }
    return $html
}

$panels = @('crypto', 'stocks', 'sports', 'jobs', 'recycle')
$html = "<html><head><title>EQ12 Dashboard</title></head><body>"
foreach ($panel in $panels) {
    $items = @()
    if ($json.data) {
        $items = @($json.data | Where-Object { $_.panel -eq $panel })
    }
    $html += Get-Eq12TableHtml -items $items -title $panel
}
$html += "</body></html>"

Set-Content -Path $OutHtml -Value $html -Encoding UTF8
Write-Host "Wrote dashboard HTML to $OutHtml"
