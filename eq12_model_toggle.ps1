#Requires -Version 5.1
<#
.SYNOPSIS
    Temporarily enable conditional EQ12 models with auto-revert functionality

.DESCRIPTION
    This script allows temporary activation of expensive or experimental models
    (o1, realtime, high-quality TTS, etc.) with automatic reversion after a
    specified duration. Prevents accidental long-term usage of costly models.

.PARAMETER ModelGroup
    Group of models to enable: 'realtime', 'reasoning', 'audio-hd', 'embeddings-large', 'all-conditional'

.PARAMETER Duration
    Duration in minutes to keep models enabled (default: 60, max: 480)

.PARAMETER Reason
    Reason for enabling (required for audit trail)

.PARAMETER Force
    Skip confirmation prompts

.EXAMPLE
    .\eq12_model_toggle.ps1 -ModelGroup realtime -Duration 30 -Reason "Demo preparation"
    
.EXAMPLE
    .\eq12_model_toggle.ps1 -ModelGroup reasoning -Duration 120 -Reason "Complex analysis project"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('realtime', 'reasoning', 'audio-hd', 'embeddings-large', 'all-conditional')]
    [string],
    
    [Parameter()]
    [ValidateRange(1, 480)]
    [int] = 60,
    
    [Parameter(Mandatory)]
    [string],
    
    [Parameter()]
    [switch]
)

Continue = "Stop"

# Model group definitions
 = @{
    'realtime' = @('gpt-4o-realtime-preview-2024-12-17', 'gpt-4o-mini-realtime-preview-2024-12-17')
    'reasoning' = @('o1', 'o1-mini', 'o1-pro', 'o3', 'o3-mini', 'o4-mini', 'o4-mini-deep-research')
    'audio-hd' = @('tts-1-hd', 'tts-1-1106', 'tts-1-hd-1106')
    'embeddings-large' = @('text-embedding-3-large')
    'all-conditional' = @(
        'tts-1-hd', 'tts-1-1106', 'tts-1-hd-1106', 'gpt-4o-mini-tts', 'gpt-4o-mini-transcribe',
        'gpt-4o-realtime-preview-2024-12-17', 'gpt-4o-mini-realtime-preview-2024-12-17',
        'o1', 'o1-mini', 'o1-pro', 'o3', 'o3-mini', 'o4-mini', 'o4-mini-deep-research',
        'text-embedding-3-large', 'gpt-4o-search-preview', 'gpt-4o-mini-search-preview'
    )
}

# Configuration
 = "C:\EQ12\.env"
 = "C:\EQ12\.env.backup.20251005_192816"
 = "C:\EQ12\logs\model_toggle.log"

function Write-Log {
    param([string], [string] = "INFO")
     = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
     = "[] [] "
    Write-Host 
    Add-Content -Path  -Value  -ErrorAction SilentlyContinue
}

function Get-CurrentAllowedModels {
    if (-not (Test-Path )) {
        throw ".env file not found at "
    }
    
     = Get-Content  -Raw
    if ( -match 'EQ12_ALLOWED_MODELS=([^\r\n]+)') {
        return [1].Split(',').Trim()
    }
    
    throw "EQ12_ALLOWED_MODELS not found in .env file"
}

function Set-AllowedModels {
    param([string[]])
    
    # Backup current .env
    Copy-Item  
    Write-Log "Backed up .env to "
    
    # Update allowed models
     = Get-Content  -Raw
     = ( -join ',')
     =  -replace 'EQ12_ALLOWED_MODELS=[^\r\n]+', "EQ12_ALLOWED_MODELS="
    
    Set-Content  -Value  -NoNewline
    Write-Log "Updated EQ12_ALLOWED_MODELS: "
}

function Set-TempConfig {
    param([string[]], [datetime], [string])
    
    # Add temp config to .env
     = Get-Content  -Raw
     = ( -join ',')
     = .ToString("yyyy-MM-ddTHH:mm:ssZ")
    
    # Remove existing temp config
     =  -replace 'EQ12_TEMP_ENABLED_MODELS=[^\r\n]*\r?\n?', ''
     =  -replace 'EQ12_TEMP_ENABLED_EXPIRY=[^\r\n]*\r?\n?', ''
     =  -replace 'EQ12_TEMP_ENABLED_REASON=[^\r\n]*\r?\n?', ''
    
    # Add new temp config
     += "
EQ12_TEMP_ENABLED_MODELS="
     += "
EQ12_TEMP_ENABLED_EXPIRY="
     += "
EQ12_TEMP_ENABLED_REASON="
    
    Set-Content  -Value  -NoNewline
}

function Clear-TempConfig {
     = Get-Content  -Raw
     =  -replace 'EQ12_TEMP_ENABLED_MODELS=[^\r\n]*\r?\n?', ''
     =  -replace 'EQ12_TEMP_ENABLED_EXPIRY=[^\r\n]*\r?\n?', ''
     =  -replace 'EQ12_TEMP_ENABLED_REASON=[^\r\n]*\r?\n?', ''
    Set-Content  -Value  -NoNewline
}

# Main execution
try {
    Write-Log "Starting model toggle operation:  for  minutes"
    Write-Log "Reason: "
    
    # Get models to enable
     = []
    if (-not ) {
        throw "Unknown model group: "
    }
    
    # Calculate expiry time
     = (Get-Date).AddMinutes()
    
    # Show what will be enabled
    Write-Host "
ðŸ”“ MODELS TO ENABLE:" -ForegroundColor Yellow
     | ForEach-Object { Write-Host "  - " -ForegroundColor Cyan }
    Write-Host "
â° DURATION:  minutes (until )" -ForegroundColor Yellow
    Write-Host "ðŸ“ REASON: " -ForegroundColor Yellow
    
    # Cost warning
    Write-Host "
âš ï¸  COST WARNING:" -ForegroundColor Red
    switch () {
        'reasoning' { Write-Host "  O1/O3 models are 15-60x more expensive than gpt-4o-mini" -ForegroundColor Red }
        'realtime' { Write-Host "  Realtime models have additional streaming costs" -ForegroundColor Red }
        'audio-hd' { Write-Host "  HD audio models are 2-4x more expensive than standard" -ForegroundColor Red }
        'embeddings-large' { Write-Host "  Large embeddings are 5x more expensive than small" -ForegroundColor Red }
    }
    
    # Confirmation
    if (-not ) {
         = Read-Host "
Proceed with temporary model enablement? (y/N)"
        if ( -ne 'y' -and  -ne 'Y') {
            Write-Host "Operation cancelled by user" -ForegroundColor Yellow
            exit 0
        }
    }
    
    # Get current models
     = Get-CurrentAllowedModels
    Write-Log "Current allowed models: "
    
    # Combine current + temp models
     =  +  | Sort-Object | Get-Unique
    
    # Update configuration
    Set-AllowedModels -Models 
    Set-TempConfig -TempModels  -ExpiryTime  -Reason 
    
    Write-Host "
âœ… MODELS ENABLED SUCCESSFULLY" -ForegroundColor Green
    Write-Host "Models will auto-revert at: " -ForegroundColor Green
    
    # Schedule auto-revert task
     = "EQ12-ModelRevert-20251005-192816"
     = "C:\EQ12\eq12_model_revert.ps1"
    
     = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File """
     = New-ScheduledTaskTrigger -Once -At 
     = New-ScheduledTaskPrincipal -UserId Ricoj100 -LogonType S4U
     = New-ScheduledTaskSettingsSet -DeleteExpiredTaskAfter (New-TimeSpan -Hours 1)
    
    Register-ScheduledTask -TaskName  -Action  -Trigger  -Principal  -Settings  -Force | Out-Null
    
    Write-Host "Auto-revert task scheduled: " -ForegroundColor Green
    Write-Log "Scheduled auto-revert task:  for "
    
    # Show current status
    Write-Host "
ðŸ“Š CURRENT STATUS:" -ForegroundColor Cyan
    Write-Host "  Enabled Models: 0" -ForegroundColor White
    Write-Host "  Temp Models: 0" -ForegroundColor White
    Write-Host "  Expires:  minutes" -ForegroundColor White
    
}
catch {
    Write-Log "ERROR: " -Level "ERROR"
    Write-Host "
âŒ ERROR: " -ForegroundColor Red
    exit 1
}

Write-Log "Model toggle operation completed successfully"
