#Requires -Version 5.1
<#
.SYNOPSIS
    Revert temporarily enabled EQ12 models back to default allowlist

.DESCRIPTION
    This script reverts conditional models back to the default allowlist.
    Called automatically by scheduled task or manually when needed.

.PARAMETER Force
    Skip confirmation prompts

.EXAMPLE
    .\eq12_model_revert.ps1

.EXAMPLE
    .\eq12_model_revert.ps1 -Force
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Configuration
$EnvFile = "C:\EQ12\.env"
$LogFile = "C:\EQ12\logs\model_toggle.log"

# Default production allowlist
$DefaultAllowedModels = @(
    'gpt-4o-mini',
    'gpt-4o',
    'chatgpt-4o-latest',
    'text-embedding-3-small',
    'omni-moderation-latest',
    'whisper-1',
    'gpt-image-1',
    'tts-1'
)

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue
}

function Get-TempConfig {
    if (-not (Test-Path $EnvFile)) {
        return $null
    }

    $Content = Get-Content $EnvFile -Raw
    $Config = @{}

    if ($Content -match 'EQ12_TEMP_ENABLED_MODELS=([^\r\n]+)') {
        $Config.Models = $Matches[1].Split(',').Trim()
    }

    if ($Content -match 'EQ12_TEMP_ENABLED_EXPIRY=([^\r\n]+)') {
        try {
            $Config.Expiry = [datetime]::Parse($Matches[1])
        }
        catch {
            Write-Log "Invalid expiry date format: $($Matches[1])" -Level "WARN"
        }
    }

    if ($Content -match 'EQ12_TEMP_ENABLED_REASON=([^\r\n]+)') {
        $Config.Reason = $Matches[1]
    }

    if ($Config.Models -and $Config.Models.Count -gt 0) {
        return $Config
    }

    return $null
}

function Set-AllowedModels {
    param([string[]]$Models)

    $Content = Get-Content $EnvFile -Raw
    $NewModels = ($Models -join ',')
    $Content = $Content -replace 'EQ12_ALLOWED_MODELS=[^\r\n]+', "EQ12_ALLOWED_MODELS=$NewModels"

    Set-Content $EnvFile -Value $Content -NoNewline
    Write-Log "Reverted EQ12_ALLOWED_MODELS to: $NewModels"
}

function Clear-TempConfig {
    $Content = Get-Content $EnvFile -Raw
    $Content = $Content -replace 'EQ12_TEMP_ENABLED_MODELS=[^\r\n]*\r?\n?', ''
    $Content = $Content -replace 'EQ12_TEMP_ENABLED_EXPIRY=[^\r\n]*\r?\n?', ''
    $Content = $Content -replace 'EQ12_TEMP_ENABLED_REASON=[^\r\n]*\r?\n?', ''
    Set-Content $EnvFile -Value $Content -NoNewline
    Write-Log "Cleared temporary model configuration"
}

# Main execution
try {
    Write-Log "Starting model revert operation"

    # Check if there are temp models to revert
    $TempConfig = Get-TempConfig
    if (-not $TempConfig) {
        Write-Host "✅ No temporary models found - system already in default state" -ForegroundColor Green
        Write-Log "No temporary models to revert"
        exit 0
    }

    Write-Host "`n🔒 REVERTING TEMPORARY MODELS" -ForegroundColor Yellow
    Write-Host "Models to remove:" -ForegroundColor Cyan
    $TempConfig.Models | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }

    if ($TempConfig.Reason) {
        Write-Host "Original reason: $($TempConfig.Reason)" -ForegroundColor Gray
    }

    if ($TempConfig.Expiry) {
        $TimeRemaining = $TempConfig.Expiry - (Get-Date)
        if ($TimeRemaining.TotalMinutes -gt 0) {
            Write-Host "Time remaining: $([math]::Ceiling($TimeRemaining.TotalMinutes)) minutes" -ForegroundColor Yellow
        }
        else {
            Write-Host "Expired $([math]::Abs([math]::Floor($TimeRemaining.TotalMinutes))) minutes ago" -ForegroundColor Red
        }
    }

    # Confirmation
    if (-not $Force) {
        $Confirm = Read-Host "`nRevert to default model policy? (Y/n)"
        if ($Confirm -eq 'n' -or $Confirm -eq 'N') {
            Write-Host "Operation cancelled by user" -ForegroundColor Yellow
            exit 0
        }
    }

    # Revert to default models
    Set-AllowedModels -Models $DefaultAllowedModels
    Clear-TempConfig

    Write-Host "`n✅ MODELS REVERTED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "Default allowlist restored:" -ForegroundColor Green
    $DefaultAllowedModels | ForEach-Object { Write-Host "  - $_" -ForegroundColor Green }

    # Clean up scheduled tasks
    Get-ScheduledTask -TaskName "EQ12-ModelRevert-*" -ErrorAction SilentlyContinue |
    ForEach-Object {
        Unregister-ScheduledTask -TaskName $_.TaskName -Confirm:$false
        Write-Log "Removed scheduled task: $($_.TaskName)"
    }

    Write-Log "Model revert operation completed successfully"
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)" -Level "ERROR"
    Write-Host "`n❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
