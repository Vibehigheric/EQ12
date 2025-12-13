<#
.SYNOPSIS
    EQ12 Control System Toolkit
.DESCRIPTION
    Provides utilities for control technicians to validate PLC/microcontroller deployments, convert configuration
    files, and run quick diagnostics using PowerShell automation.
#>
[CmdletBinding(DefaultParameterSetName = 'Menu')]
param(
    [Parameter(ParameterSetName = 'Diagnostics')]
    [switch]$Diagnostics,

    [Parameter(ParameterSetName = 'Package')]
    [switch]$Package,

    [Parameter(ParameterSetName = 'Convert')]
    [string]$Config,

    [Parameter(ParameterSetName = 'Convert')]
    [ValidateSet('json-to-csv', 'csv-to-json', 'yaml-to-json')]
    [string]$Mode
)

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot '..' '..')
$logDir = Join-Path $repoRoot 'logs/control'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logFile = Join-Path $logDir "control_toolkit_$timestamp.log"

function Write-Log {
    param([string]$Message)
    $stamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $entry = "[$stamp] $Message"
    Add-Content -Path $logFile -Value $entry
    Write-Host $entry
}

function Invoke-ControlDiagnostics {
    Write-Log 'Starting control diagnostics suite.'
    $report = [ordered]@{}

    $report.Python = if (Get-Command python -ErrorAction SilentlyContinue) { 'Detected' } else { 'Missing' }
    $report.PowerShellVersion = $PSVersionTable.PSVersion.ToString()
    $report.DotNet = if (Get-Command dotnet -ErrorAction SilentlyContinue) { 'Detected' } else { 'Missing' }
    $report.Git = if (Get-Command git -ErrorAction SilentlyContinue) { 'Detected' } else { 'Missing' }

    $plcConfigDir = Join-Path $repoRoot 'control_configs'
    if (Test-Path $plcConfigDir) {
        $report.PLCConfigs = (Get-ChildItem -Path $plcConfigDir -Filter '*.json' -Recurse).Count
    } else {
        $report.PLCConfigs = 0
        Write-Log "PLC config directory not found: $plcConfigDir"
    }

    Write-Log (ConvertTo-Json $report -Depth 4)
}

function Invoke-ControlPackage {
    Write-Log 'Packaging control deployment bundle.'
    $outputDir = Join-Path $repoRoot 'artifacts'
    if (-not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir | Out-Null }
    $bundle = Join-Path $outputDir "eq12_control_bundle_$timestamp.zip"
    $paths = @(
        Join-Path $repoRoot 'control_configs',
        Join-Path $repoRoot 'scripts/control'
    )
    $existing = $paths | Where-Object { Test-Path $_ }
    if ($existing.Count -eq 0) {
        Write-Log 'Nothing to package; ensure control_configs/ exists.'
        return
    }
    Compress-Archive -Path $existing -DestinationPath $bundle -Force
    Write-Log "Created bundle: $bundle"
}

function Invoke-ConfigConversion {
    param([string]$Path, [string]$Mode)
    if (-not (Test-Path $Path)) {
        Write-Log "Config file not found: $Path"
        return
    }
    switch ($Mode) {
        'json-to-csv' {
            $json = Get-Content -Path $Path -Raw | ConvertFrom-Json
            $csvPath = [System.IO.Path]::ChangeExtension($Path, '.csv')
            $json | ConvertTo-Csv -NoTypeInformation | Set-Content -Path $csvPath -Encoding UTF8
            Write-Log "Converted $Path -> $csvPath"
        }
        'csv-to-json' {
            $table = Import-Csv -Path $Path
            $jsonPath = [System.IO.Path]::ChangeExtension($Path, '.json')
            $table | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath -Encoding UTF8
            Write-Log "Converted $Path -> $jsonPath"
        }
        'yaml-to-json' {
            if (-not (Get-Module -ListAvailable -Name powershell-yaml)) {
                Install-Module powershell-yaml -Scope CurrentUser -Force -ErrorAction Stop
            }
            Import-Module powershell-yaml
            $yaml = Get-Content -Path $Path -Raw | ConvertFrom-Yaml
            $jsonPath = [System.IO.Path]::ChangeExtension($Path, '.json')
            $yaml | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonPath -Encoding UTF8
            Write-Log "Converted $Path -> $jsonPath"
        }
    }
}

switch ($PSCmdlet.ParameterSetName) {
    'Diagnostics' { Invoke-ControlDiagnostics }
    'Package' { Invoke-ControlPackage }
    'Convert' { Invoke-ConfigConversion -Path $Config -Mode $Mode }
    default {
        Write-Host 'EQ12 CONTROL TOOLKIT' -ForegroundColor Cyan
        Write-Host '  powershell -File control_system_toolkit.ps1 -Diagnostics' -ForegroundColor Yellow
        Write-Host '  powershell -File control_system_toolkit.ps1 -Package' -ForegroundColor Yellow
        Write-Host '  powershell -File control_system_toolkit.ps1 -Config config.json -Mode json-to-csv' -ForegroundColor Yellow
    }
}
