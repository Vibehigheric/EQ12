<#
Exports Windows Reliability Monitor events to JSON and manages logman perf counters.

Usage:
  .\eq12_syshealth.ps1 -OutDir C:\EQ12\logs -StartCollector -StopCollector -Verify

Dry-run by default; use -Apply to perform actions that change system state.
#>

[CmdletBinding()]
param(
    [string]$OutDir = 'C:\EQ12\logs',
    [string]$PerfName = 'EQ12Perf',
    [switch]$StartCollector,
    [switch]$StopCollector,
    [int]$DurationSeconds = 60,
    [switch]$Verify,
    [switch]$Apply
)

function Write-JsonFile {
    param($Path, $Object)
    $dir = Split-Path $Path -Parent
    if (-not (Test-Path $dir)) { New-Item -Path $dir -ItemType Directory -Force | Out-Null }
    $Object | ConvertTo-Json -Depth 5 | Out-File -FilePath $Path -Encoding UTF8 -Force
}

function Export-ReliabilityJson {
    param($OutPath)
    Write-Host "Exporting Reliability Monitor to $OutPath"
    try {
        $events = Get-WinEvent -LogName Microsoft-Windows-ReliabilityMonitor/Operational -ErrorAction Stop |
            Select-Object TimeCreated, Id, LevelDisplayName, Message
        Write-JsonFile -Path $OutPath -Object $events
    } catch {
        Write-Warning "Failed to read Reliability Monitor: $_"
        return $false
    }
    return $true
}

function Start-PerfCollector {
    param($Name, $OutPath)
    Write-Host "Creating perf collector $Name -> $OutPath"
    $counters = @(
        '\Processor(_Total)\% Processor Time',
        '\Memory\Available MBytes'
    )

    if (-not $Apply) { Write-Host "Dry-run: would create and start collector $Name"; return $null }

    # Create and start
    logman create counter $Name -c $counters -f csv -o $OutPath -y | Out-Null
    logman start $Name | Out-Null
    return $true
}

function Stop-PerfCollector {
    param($Name)
    Write-Host "Stopping perf collector $Name"
    if (-not $Apply) { Write-Host "Dry-run: would stop collector $Name"; return $null }
    logman stop $Name | Out-Null
    logman delete $Name | Out-Null
    return $true
}

# Main
$outDir = $OutDir
if (-not (Test-Path $outDir)) { New-Item -Path $outDir -ItemType Directory -Force | Out-Null }

$reliabilityPath = Join-Path $outDir 'reliability.json'
$perfOut = Join-Path $outDir 'eq12_perf'

if ($Verify) {
    # Export reliability monitor and confirm file
    $ok = Export-ReliabilityJson -OutPath $reliabilityPath
    if ($ok) { Write-Host "Reliability exported to $reliabilityPath" } else { Write-Warning "Reliability export failed" }
    exit 0
}

if ($StartCollector) {
    Start-PerfCollector -Name $PerfName -OutPath $perfOut
}

if ($StopCollector) {
    Stop-PerfCollector -Name $PerfName
}

if (-not ($StartCollector -or $StopCollector -or $Verify)) {
    # default: export reliability only
    Export-ReliabilityJson -OutPath $reliabilityPath | Out-Null
    Write-Host "Wrote reliability JSON to $reliabilityPath"
}
