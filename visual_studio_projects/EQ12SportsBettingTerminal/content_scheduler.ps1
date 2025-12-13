# EQ12 Content Engine Task Scheduler Script
# Automated monetization content generation for sports betting terminal

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("daily", "weekly", "monthly")]
    [string]$ContentType = "daily",

    [Parameter(Mandatory = $false)]
    [switch]$Verbose
)

# Configuration
$EQ12Path = "C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal"
$CliPath = Join-Path $EQ12Path "bin\Debug\Eq12Cli.exe"
$LogPath = "C:\EQ12\logs\content_engine_$(Get-Date -Format 'yyyyMMdd').log"

# Ensure log directory exists
$LogDir = Split-Path $LogPath -Parent
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Logging function
function Write-LogMessage {
    param($Message, $Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Output $LogEntry
    Add-Content -Path $LogPath -Value $LogEntry
}

# Main execution
try {
    Write-LogMessage "🚀 Starting EQ12 Content Engine ($ContentType)" "INFO"

    # Verify CLI exists
    if (-not (Test-Path $CliPath)) {
        throw "EQ12 CLI not found at: $CliPath"
    }

    # Set working directory
    Push-Location $EQ12Path

    # Execute content generation
    $Command = "content-$ContentType"
    Write-LogMessage "📝 Executing: $CliPath $Command" "INFO"

    $ProcessArgs = @{
        FilePath               = $CliPath
        ArgumentList           = $Command
        Wait                   = $true
        NoNewWindow            = $true
        RedirectStandardOutput = $true
        RedirectStandardError  = $true
    }

    $Process = Start-Process @ProcessArgs -PassThru
    $Output = $Process.StandardOutput.ReadToEnd()
    $Errors = $Process.StandardError.ReadToEnd()

    # Log output
    if ($Output) {
        Write-LogMessage "CLI Output: $Output" "INFO"
    }

    if ($Errors) {
        Write-LogMessage "CLI Errors: $Errors" "ERROR"
    }

    # Check exit code
    if ($Process.ExitCode -eq 0) {
        Write-LogMessage "✅ Content generation completed successfully" "SUCCESS"

        # Optional: Send success notification
        if ($env:TELEGRAM_BOT_TOKEN -and $env:TELEGRAM_CHAT_ID) {
            $Message = "🎉 EQ12 Content Engine completed $ContentType content generation at $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
            # Note: Would need to implement Telegram notification here
        }
    }
    else {
        throw "Content generation failed with exit code: $($Process.ExitCode)"
    }

}
catch {
    Write-LogMessage "❌ Content generation failed: $($_.Exception.Message)" "ERROR"

    # Optional: Send error notification
    if ($env:TELEGRAM_BOT_TOKEN -and $env:TELEGRAM_CHAT_ID) {
        $Message = "🚨 EQ12 Content Engine failed for $ContentType content: $($_.Exception.Message)"
        # Note: Would need to implement Telegram notification here
    }

    exit 1

}
finally {
    Pop-Location
    Write-LogMessage "📊 Content generation task completed" "INFO"
}

# Task Scheduler XML configurations (commented for reference)
<#

# Create daily content generation task
schtasks /Create /TN "EQ12_Content_Daily" /TR "powershell.exe -File 'C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal\content_scheduler.ps1' -ContentType daily" /SC DAILY /ST 09:20 /F

# Create weekly content generation task
schtasks /Create /TN "EQ12_Content_Weekly" /TR "powershell.exe -File 'C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal\content_scheduler.ps1' -ContentType weekly" /SC WEEKLY /D MON /ST 09:25 /F

# Create monthly content generation task
schtasks /Create /TN "EQ12_Content_Monthly" /TR "powershell.exe -File 'C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal\content_scheduler.ps1' -ContentType monthly" /SC MONTHLY /D 1 /ST 09:30 /F

# List all EQ12 content tasks
schtasks /Query /TN "EQ12_Content*"

# Delete a task (example)
# schtasks /Delete /TN "EQ12_Content_Daily" /F

#>
