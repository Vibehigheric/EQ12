#Requires -Version 5.1
<#
.SYNOPSIS
    Temporarily adjust EQ12 rate limits for live events with auto-revert

.DESCRIPTION
    This script temporarily raises rate limits for live events like NFL Sunday,
    then automatically reverts to production limits after the specified duration.
    Prevents accidental long-term usage of higher rate limits.

.PARAMETER EventType
    Type of live event: 'nfl_sunday', 'playoffs', 'championship', 'high_volume', 'demo'

.PARAMETER Duration
    Duration in hours to keep elevated limits (default: 4, max: 12)

.PARAMETER Reason
    Reason for elevation (required for audit trail)

.PARAMETER Force
    Skip confirmation prompts

.EXAMPLE
    .\eq12_rate_limit_boost.ps1 -EventType nfl_sunday -Duration 4 -Reason "NFL Week 6 live betting"

.EXAMPLE
    .\eq12_rate_limit_boost.ps1 -EventType demo -Duration 1 -Reason "Client presentation" -Force
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('nfl_sunday', 'playoffs', 'championship', 'high_volume', 'demo')]
    [string]$EventType,

    [Parameter()]
    [ValidateRange(1, 12)]
    [int]$Duration = 4,

    [Parameter(Mandatory)]
    [string]$Reason,

    [Parameter()]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Rate limit profiles for different event types
$EventProfiles = @{
    'nfl_sunday'   = @{
        'gpt-4o-mini'            = @{tpm = 40000; rpm = 120 }
        'gpt-4o'                 = @{tpm = 6000; rpm = 40 }
        'text-embedding-3-small' = @{tpm = 100000; rpm = 80 }
        'omni-moderation-latest' = @{tpm = 15000; rpm = 150 }
    }
    'playoffs'     = @{
        'gpt-4o-mini'            = @{tpm = 50000; rpm = 150 }
        'gpt-4o'                 = @{tpm = 8000; rpm = 50 }
        'text-embedding-3-small' = @{tpm = 120000; rpm = 100 }
        'omni-moderation-latest' = @{tpm = 20000; rpm = 200 }
    }
    'championship' = @{
        'gpt-4o-mini'            = @{tpm = 60000; rpm = 180 }
        'gpt-4o'                 = @{tpm = 10000; rpm = 60 }
        'text-embedding-3-small' = @{tpm = 150000; rpm = 120 }
        'omni-moderation-latest' = @{tpm = 25000; rpm = 250 }
    }
    'high_volume'  = @{
        'gpt-4o-mini'            = @{tpm = 35000; rpm = 100 }
        'gpt-4o'                 = @{tpm = 5000; rpm = 30 }
        'text-embedding-3-small' = @{tpm = 90000; rpm = 70 }
        'omni-moderation-latest' = @{tpm = 12000; rpm = 120 }
    }
    'demo'         = @{
        'gpt-4o-mini'            = @{tpm = 25000; rpm = 80 }
        'gpt-4o'                 = @{tpm = 4000; rpm = 25 }
        'text-embedding-3-small' = @{tpm = 60000; rpm = 50 }
        'omni-moderation-latest' = @{tpm = 8000; rpm = 100 }
    }
}

# Production baseline (for revert)
$ProductionLimits = @{
    'gpt-4o-mini'            = @{tpm = 20000; rpm = 60 }
    'gpt-4o'                 = @{tpm = 3000; rpm = 20 }
    'text-embedding-3-small' = @{tpm = 80000; rpm = 60 }
    'omni-moderation-latest' = @{tpm = 10000; rpm = 120 }
    'whisper-1'              = @{tpm = 10000; rpm = 30 }
    'gpt-image-1'            = @{images_per_min = 2 }
    'tts-1'                  = @{rpm = 30 }
    'default'                = @{tpm = 0; rpm = 0 }
}

# Configuration
$EnvFile = "C:\EQ12\.env"
$BackupFile = "C:\EQ12\.env.backup.ratelimit.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$LogFile = "C:\EQ12\logs\rate_limit_events.log"

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

    # Backup current .env
    Copy-Item $EnvFile $BackupFile
    Write-Log "Backed up .env to $BackupFile"

    # Convert limits to JSON
    $LimitsJson = ConvertTo-RateLimitJson -Limits $NewLimits

    # Update .env file
    $Content = Get-Content $EnvFile -Raw
    $Content = $Content -replace 'EQ12_RUNTIME_LIMITS_JSON=[^\r\n]+', "EQ12_RUNTIME_LIMITS_JSON=$LimitsJson"

    Set-Content $EnvFile -Value $Content -NoNewline
    Write-Log "Updated rate limits: $($NewLimits.Keys -join ', ')"
}

function Set-EventConfig {
    param([string]$EventName, [datetime]$ExpiryTime, [string]$ReasonText)

    # Add event config to .env
    $Content = Get-Content $EnvFile -Raw
    $ExpiryStr = $ExpiryTime.ToString("yyyy-MM-ddTHH:mm:ssZ")

    # Remove existing event config
    $Content = $Content -replace 'EQ12_LIVE_EVENT_TYPE=[^\r\n]*\r?\n?', ''
    $Content = $Content -replace 'EQ12_LIVE_EVENT_EXPIRY=[^\r\n]*\r?\n?', ''
    $Content = $Content -replace 'EQ12_LIVE_EVENT_REASON=[^\r\n]*\r?\n?', ''

    # Add new event config
    $Content += "`nEQ12_LIVE_EVENT_TYPE=$EventName"
    $Content += "`nEQ12_LIVE_EVENT_EXPIRY=$ExpiryStr"
    $Content += "`nEQ12_LIVE_EVENT_REASON=$ReasonText"

    Set-Content $EnvFile -Value $Content -NoNewline
}

function Clear-EventConfig {
    $Content = Get-Content $EnvFile -Raw
    $Content = $Content -replace 'EQ12_LIVE_EVENT_TYPE=[^\r\n]*\r?\n?', ''
    $Content = $Content -replace 'EQ12_LIVE_EVENT_EXPIRY=[^\r\n]*\r?\n?', ''
    $Content = $Content -replace 'EQ12_LIVE_EVENT_REASON=[^\r\n]*\r?\n?', ''
    Set-Content $EnvFile -Value $Content -NoNewline
}

# Main execution
try {
    Write-Log "Starting rate limit boost: $EventType for $Duration hours"
    Write-Log "Reason: $Reason"

    # Get event profile
    $EventLimits = $EventProfiles[$EventType]
    if (-not $EventLimits) {
        throw "Unknown event type: $EventType"
    }

    # Merge with production baseline
    $NewLimits = $ProductionLimits.Clone()
    foreach ($model in $EventLimits.Keys) {
        $NewLimits[$model] = $EventLimits[$model]
    }

    # Calculate expiry time
    $ExpiryTime = (Get-Date).AddHours($Duration)

    # Show what will change
    Write-Host "`n🚀 RATE LIMIT BOOST: $($EventType.ToUpper())" -ForegroundColor Yellow
    Write-Host "Duration: $Duration hours (until $($ExpiryTime.ToString('yyyy-MM-dd HH:mm:ss')))" -ForegroundColor Yellow
    Write-Host "Reason: $Reason" -ForegroundColor Yellow

    Write-Host "`n📈 LIMIT CHANGES:" -ForegroundColor Cyan
    foreach ($model in $EventLimits.Keys) {
        $prod = $ProductionLimits[$model]
        $event = $EventLimits[$model]

        $prodTpm = $prod.tpm
        $eventTpm = $event.tpm
        $prodRpm = $prod.rpm
        $eventRpm = $event.rpm

        $tpmIncrease = [math]::Round(($eventTpm - $prodTpm) / $prodTpm * 100, 0)
        $rpmIncrease = [math]::Round(($eventRpm - $prodRpm) / $prodRpm * 100, 0)

        Write-Host "  $model" -ForegroundColor White
        Write-Host "    TPM: $prodTpm → $eventTpm (+$tpmIncrease%)" -ForegroundColor Green
        Write-Host "    RPM: $prodRpm → $eventRpm (+$rpmIncrease%)" -ForegroundColor Green
    }

    # Cost impact warning
    Write-Host "`n⚠️  COST IMPACT:" -ForegroundColor Red
    switch ($EventType) {
        'nfl_sunday' { Write-Host "  Moderate increase: 2-3x normal throughput capacity" -ForegroundColor Yellow }
        'playoffs' { Write-Host "  High increase: 3-4x normal throughput capacity" -ForegroundColor Orange }
        'championship' { Write-Host "  Very high increase: 4-5x normal throughput capacity" -ForegroundColor Red }
        'high_volume' { Write-Host "  Moderate increase: 2x normal throughput capacity" -ForegroundColor Yellow }
        'demo' { Write-Host "  Low increase: 1.5x normal throughput capacity" -ForegroundColor Green }
    }

    # Confirmation
    if (-not $Force) {
        $Confirm = Read-Host "`nProceed with rate limit boost? (y/N)"
        if ($Confirm -ne 'y' -and $Confirm -ne 'Y') {
            Write-Host "Operation cancelled by user" -ForegroundColor Yellow
            exit 0
        }
    }

    # Apply changes
    Update-RateLimits -NewLimits $NewLimits
    Set-EventConfig -EventName $EventType -ExpiryTime $ExpiryTime -ReasonText $Reason

    Write-Host "`n✅ RATE LIMITS BOOSTED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "Limits will auto-revert at: $($ExpiryTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Green

    # Schedule auto-revert task
    $TaskName = "EQ12-RateLimitRevert-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    $ScriptPath = "C:\EQ12\eq12_rate_limit_revert.ps1"

    $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`""
    $Trigger = New-ScheduledTaskTrigger -Once -At $ExpiryTime
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U
    $Settings = New-ScheduledTaskSettingsSet -DeleteExpiredTaskAfter (New-TimeSpan -Hours 2)

    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force | Out-Null

    Write-Host "Auto-revert task scheduled: $TaskName" -ForegroundColor Green
    Write-Log "Scheduled auto-revert task: $TaskName for $ExpiryTime"

    # Show current status
    Write-Host "`n📊 CURRENT STATUS:" -ForegroundColor Cyan
    Write-Host "  Event Type: $EventType" -ForegroundColor White
    Write-Host "  Boosted Models: $($EventLimits.Keys.Count)" -ForegroundColor White
    Write-Host "  Duration: $Duration hours" -ForegroundColor White
    Write-Host "  Auto-Revert: Scheduled" -ForegroundColor White

    # Optional: Restart any EQ12 services to pick up new limits
    Write-Host "`n🔄 To apply limits immediately, restart EQ12 services:" -ForegroundColor Yellow
    Write-Host "  pm2 restart eq12-webhook-server" -ForegroundColor Gray
    Write-Host "  # Or restart your application as needed" -ForegroundColor Gray

}
catch {
    Write-Log "ERROR: $($_.Exception.Message)" -Level "ERROR"
    Write-Host "`n❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Log "Rate limit boost operation completed successfully"
