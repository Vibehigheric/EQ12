#Requires -Version 5.1
<#
.SYNOPSIS
    Revert EQ12 rate limits back to production baseline

.DESCRIPTION
    This script reverts rate limits back to production baseline after live events.
    Called automatically by scheduled task or manually when needed.

.PARAMETER Force
    Skip confirmation prompts

.EXAMPLE
    .\eq12_rate_limit_revert.ps1

.EXAMPLE
    .\eq12_rate_limit_revert.ps1 -Force
#>

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Configuration
$EnvFile = "C:\EQ12\.env"
$LogFile = "C:\EQ12\logs\rate_limit_events.log"

# Production baseline limits
$ProductionLimits = @{
    'gpt-4o-mini' = @{tpm = 20000; rpm = 60}
    'gpt-4o' = @{tpm = 3000; rpm = 20}
    'text-embedding-3-small' = @{tpm = 80000; rpm = 60}
    'omni-moderation-latest' = @{tpm = 10000; rpm = 120}
    'whisper-1' = @{tpm = 10000; rpm = 30}
    'gpt-image-1' = @{images_per_min = 2}
    'tts-1' = @{rpm = 30}
    'default' = @{tpm = 0; rpm = 0}
}

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue
}

function Get-EventConfig {
    if (-not (Test-Path $EnvFile)) {
        return $null
    }

    $Content = Get-Content $EnvFile -Raw
    $Config = @{}

    if ($Content -match 'EQ12_LIVE_EVENT_TYPE=([^\r\n]+)') {
        $Config.EventType = $Matches[1]
    }

    if ($Content -match 'EQ12_LIVE_EVENT_EXPIRY=([^\r\n]+)') {
        try {
            $Config.Expiry = [datetime]::Parse($Matches[1])
        } catch {
            Write-Log "Invalid expiry date format: $($Matches[1])" -Level "WARN"
        }
    }

    if ($Content -match 'EQ12_LIVE_EVENT_REASON=([^\r\n]+)') {
        $Config.Reason = $Matches[1]
    }

    if ($Config.EventType) {
        return $Config
    }

    return $null
}

function ConvertTo-RateLimitJson {
    param([hashtable]$Limits)

    $JsonObj = @{}
    foreach ($model in $Limits.Keys) {
        $JsonObj[$model] = $Limits[$model]
    }

    return ($JsonObj | ConvertTo-Json -Compress)
}

function Update-RateLimits {
    param([hashtable]$NewLimits)

    # Convert limits to JSON
    $LimitsJson = ConvertTo-RateLimitJson -Limits $NewLimits

    # Update .env file
    $Content = Get-Content $EnvFile -Raw
    $Content = $Content -replace 'EQ12_RUNTIME_LIMITS_JSON=[^\r\n]+', "EQ12_RUNTIME_LIMITS_JSON=$LimitsJson"

    Set-Content $EnvFile -Value $Content -NoNewline
    Write-Log "Reverted to production rate limits"
}

function Clear-EventConfig {
    $Content = Get-Content $EnvFile -Raw
    $Content = $Content -replace 'EQ12_LIVE_EVENT_TYPE=[^\r\n]*\r?\n?', ''
    $Content = $Content -replace 'EQ12_LIVE_EVENT_EXPIRY=[^\r\n]*\r?\n?', ''
    $Content = $Content -replace 'EQ12_LIVE_EVENT_REASON=[^\r\n]*\r?\n?', ''
    Set-Content $EnvFile -Value $Content -NoNewline
    Write-Log "Cleared live event configuration"
}

# Main execution
try {
    Write-Log "Starting rate limit revert operation"

    # Check if there's an active event
    $EventConfig = Get-EventConfig
    if (-not $EventConfig) {
        Write-Host "✅ No active live event found - system already at production limits" -ForegroundColor Green
        Write-Log "No active event to revert"
        exit 0
    }

    Write-Host "`n🔒 REVERTING RATE LIMITS TO PRODUCTION" -ForegroundColor Yellow
    Write-Host "Event Type: $($EventConfig.EventType)" -ForegroundColor Cyan

    if ($EventConfig.Reason) {
        Write-Host "Original Reason: $($EventConfig.Reason)" -ForegroundColor Gray
    }

    if ($EventConfig.Expiry) {
        $TimeRemaining = $EventConfig.Expiry - (Get-Date)
        if ($TimeRemaining.TotalMinutes -gt 0) {
            $HoursRemaining = [math]::Ceiling($TimeRemaining.TotalHours)
            Write-Host "Time Remaining: $HoursRemaining hours" -ForegroundColor Yellow
        } else {
            $HoursExpired = [math]::Abs([math]::Floor($TimeRemaining.TotalHours))
            Write-Host "Expired: $HoursExpired hours ago" -ForegroundColor Red
        }
    }

    Write-Host "`n📉 PRODUCTION LIMITS:" -ForegroundColor Green
    foreach ($model in $ProductionLimits.Keys) {
        $limits = $ProductionLimits[$model]
        if ($limits.tpm) {
            Write-Host "  $model : TPM=$($limits.tpm), RPM=$($limits.rpm)" -ForegroundColor White
        } elseif ($limits.images_per_min) {
            Write-Host "  $model : $($limits.images_per_min) images/min" -ForegroundColor White
        } else {
            Write-Host "  $model : RPM=$($limits.rpm)" -ForegroundColor White
        }
    }

    # Confirmation
    if (-not $Force) {
        $Confirm = Read-Host "`nRevert to production rate limits? (Y/n)"
        if ($Confirm -eq 'n' -or $Confirm -eq 'N') {
            Write-Host "Operation cancelled by user" -ForegroundColor Yellow
            exit 0
        }
    }

    # Revert to production limits
    Update-RateLimits -NewLimits $ProductionLimits
    Clear-EventConfig

    Write-Host "`n✅ RATE LIMITS REVERTED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "Production baseline restored" -ForegroundColor Green

    # Clean up scheduled tasks
    Get-ScheduledTask -TaskName "EQ12-RateLimitRevert-*" -ErrorAction SilentlyContinue |
        ForEach-Object {
            Unregister-ScheduledTask -TaskName $_.TaskName -Confirm:$false
            Write-Log "Removed scheduled task: $($_.TaskName)"
        }

    # Optional restart reminder
    Write-Host "`n🔄 To apply limits immediately, restart EQ12 services:" -ForegroundColor Yellow
    Write-Host "  pm2 restart eq12-webhook-server" -ForegroundColor Gray
    Write-Host "  # Or restart your application as needed" -ForegroundColor Gray

    Write-Log "Rate limit revert operation completed successfully"
}
catch {
    Write-Log "ERROR: $($_.Exception.Message)" -Level "ERROR"
    Write-Host "`n❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
