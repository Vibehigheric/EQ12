# EQ12 Copilot Metrics Automation Scheduler
# Automatically syncs GitHub Copilot metrics, generates reports, and sends alerts
# Features: Task Scheduler integration, Bitly shortening, Telegram notifications

[CmdletBinding()]
param(
    [Parameter(HelpMessage="Organization name for metrics collection")]
    [string]$Organization = "your-org",

    [Parameter(HelpMessage="Action to perform: sync, report, diff, install-task, remove-task, or status")]
    [ValidateSet("sync", "report", "diff", "install-task", "remove-task", "status", "full-cycle")]
    [string]$Action = "full-cycle",

    [Parameter(HelpMessage="Report period: daily, weekly, monthly")]
    [ValidateSet("daily", "weekly", "monthly")]
    [string]$Period = "daily",

    [Parameter(HelpMessage="Number of days for diff analysis")]
    [int]$Days = 30,

    [Parameter(HelpMessage="Run in test mode without actual execution")]
    [switch]$TestMode,

    [Parameter(HelpMessage="Skip Telegram notifications")]
    [switch]$SkipNotifications
)

# Global variables
$EQ12Root = "C:\EQ12"
$LogPath = "C:\EQ12\logs\copilot_metrics_scheduler.log"
$TaskName = "EQ12-CopilotMetrics-Daily"
$Eq12CliPath = Join-Path $EQ12Root "Eq12Cli.exe"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp [$Level] CopilotScheduler: $Message"

    # Ensure log directory exists
    $logDir = Split-Path $LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    # Write to log file
    $logEntry | Out-File -FilePath $LogPath -Append -Encoding UTF8

    # Write to console with colors
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    }
    Write-Host $logEntry -ForegroundColor $color
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..."

    $checks = @{
        "EQ12 CLI Executable" = Test-Path $Eq12CliPath
        "GitHub Token Available" = [System.Environment]::GetEnvironmentVariable("GITHUB_PAT", "User") -ne $null
        "Bitly Token Available" = [System.Environment]::GetEnvironmentVariable("BITLY_TOKEN", "User") -ne $null
        "Telegram Bot Token Available" = [System.Environment]::GetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "User") -ne $null
        "Telegram Chat ID Available" = [System.Environment]::GetEnvironmentVariable("TELEGRAM_CHAT_ID", "User") -ne $null
    }

    $allPassed = $true
    foreach ($check in $checks.GetEnumerator()) {
        if ($check.Value) {
            Write-Log "✅ $($check.Key)" "SUCCESS"
        } else {
            Write-Log "❌ $($check.Key)" "ERROR"
            $allPassed = $false
        }
    }

    if (-not $allPassed) {
        Write-Log "Prerequisites not met. Please configure required environment variables." "ERROR"
        return $false
    }

    Write-Log "All prerequisites met." "SUCCESS"
    return $true
}

function Invoke-MetricsSync {
    param([string]$Org)

    Write-Log "Starting Copilot metrics sync for organization: $Org"

    if ($TestMode) {
        Write-Log "TEST MODE: Would sync metrics for $Org" "WARN"
        return $true
    }

    try {
        $syncArgs = @("metrics-sync", "--org", $Org)
        Write-Log "Executing: $Eq12CliPath $($syncArgs -join ' ')"

        $result = & $Eq12CliPath @syncArgs
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-Log "Metrics sync completed successfully" "SUCCESS"
            return $true
        } else {
            Write-Log "Metrics sync failed with exit code: $exitCode" "ERROR"
            Write-Log "Output: $result" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Error during metrics sync: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Invoke-MetricsReport {
    param([string]$Org, [string]$ReportPeriod)

    Write-Log "Generating Copilot metrics report for $Org ($ReportPeriod)"

    if ($TestMode) {
        Write-Log "TEST MODE: Would generate $ReportPeriod report for $Org" "WARN"
        return "C:\EQ12\Reports\test_report.pdf"
    }

    try {
        $reportArgs = @("metrics-report", "--org", $Org, "--period", $ReportPeriod)
        Write-Log "Executing: $Eq12CliPath $($reportArgs -join ' ')"

        $result = & $Eq12CliPath @reportArgs
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-Log "Report generation completed successfully" "SUCCESS"

            # Find the generated report file
            $reportDir = "C:\EQ12\Reports"
            $reportFiles = Get-ChildItem -Path $reportDir -Filter "*copilot_metrics_$ReportPeriod*.pdf" -ErrorAction SilentlyContinue |
                          Sort-Object LastWriteTime -Descending | Select-Object -First 1

            if ($reportFiles) {
                return $reportFiles.FullName
            } else {
                Write-Log "Report generated but file not found in $reportDir" "WARN"
                return $null
            }
        } else {
            Write-Log "Report generation failed with exit code: $exitCode" "ERROR"
            return $null
        }
    } catch {
        Write-Log "Error during report generation: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

function Invoke-MetricsDiff {
    param([string]$Org, [int]$DiffDays)

    Write-Log "Generating metrics diff analysis for $Org (last $DiffDays days)"

    if ($TestMode) {
        Write-Log "TEST MODE: Would generate diff for $Org ($DiffDays days)" "WARN"
        return $true
    }

    try {
        $diffArgs = @("metrics-diff", "--org", $Org, "--days", $DiffDays.ToString())
        Write-Log "Executing: $Eq12CliPath $($diffArgs -join ' ')"

        $result = & $Eq12CliPath @diffArgs
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-Log "Metrics diff completed successfully" "SUCCESS"
            Write-Log "Diff result: $result"
            return $true
        } else {
            Write-Log "Metrics diff failed with exit code: $exitCode" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Error during metrics diff: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Send-TelegramNotification {
    param([string]$Message, [string]$ReportUrl = "")

    if ($SkipNotifications) {
        Write-Log "Skipping Telegram notification (SkipNotifications flag set)"
        return
    }

    $botToken = [System.Environment]::GetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "User")
    $chatId = [System.Environment]::GetEnvironmentVariable("TELEGRAM_CHAT_ID", "User")

    if (-not $botToken -or -not $chatId) {
        Write-Log "Telegram credentials not configured, skipping notification" "WARN"
        return
    }

    if ($TestMode) {
        Write-Log "TEST MODE: Would send Telegram message: $Message" "WARN"
        return
    }

    try {
        $fullMessage = "📊 EQ12 Copilot Metrics: $Message"
        if ($ReportUrl) {
            $fullMessage += "`n🔗 Report: $ReportUrl"
        }

        $telegramUrl = "https://api.telegram.org/bot$botToken/sendMessage"
        $body = @{
            chat_id = $chatId
            text = $fullMessage
            parse_mode = "Markdown"
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri $telegramUrl -Method Post -ContentType "application/json" -Body $body -TimeoutSec 30
        Write-Log "Telegram notification sent successfully" "SUCCESS"
    } catch {
        Write-Log "Failed to send Telegram notification: $($_.Exception.Message)" "ERROR"
    }
}

function New-BitlyShortUrl {
    param([string]$LongUrl)

    $bitlyToken = [System.Environment]::GetEnvironmentVariable("BITLY_TOKEN", "User")

    if (-not $bitlyToken) {
        Write-Log "Bitly token not configured, returning original URL" "WARN"
        return $LongUrl
    }

    if ($TestMode) {
        Write-Log "TEST MODE: Would shorten URL: $LongUrl" "WARN"
        return "https://bit.ly/test-url"
    }

    try {
        $headers = @{
            "Authorization" = "Bearer $bitlyToken"
            "Content-Type" = "application/json"
        }

        $body = @{
            long_url = $LongUrl
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "https://api-ssl.bitly.com/v4/shorten" -Method Post -Headers $headers -Body $body -TimeoutSec 30

        Write-Log "URL shortened successfully: $($response.link)"
        return $response.link
    } catch {
        Write-Log "Failed to shorten URL: $($_.Exception.Message)" "ERROR"
        return $LongUrl
    }
}

function Install-ScheduledTask {
    Write-Log "Installing scheduled task: $TaskName"

    try {
        # Remove existing task if it exists
        if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-Log "Removed existing scheduled task"
        }

        # Create new task
        $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$PSCommandPath`" -Action full-cycle -Organization $Organization"
        $trigger = New-ScheduledTaskTrigger -Daily -At "09:00AM"
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

        $task = New-ScheduledTask -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "EQ12 Daily Copilot Metrics Collection and Reporting"

        Register-ScheduledTask -TaskName $TaskName -InputObject $task

        Write-Log "Scheduled task installed successfully" "SUCCESS"
        Write-Log "Task will run daily at 9:00 AM for organization: $Organization" "SUCCESS"
    } catch {
        Write-Log "Failed to install scheduled task: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Remove-ScheduledTask {
    Write-Log "Removing scheduled task: $TaskName"

    try {
        if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-Log "Scheduled task removed successfully" "SUCCESS"
        } else {
            Write-Log "Scheduled task not found" "WARN"
        }
    } catch {
        Write-Log "Failed to remove scheduled task: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Show-TaskStatus {
    Write-Log "Checking scheduled task status"

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

        if ($task) {
            Write-Log "Task Status: $($task.State)" "SUCCESS"
            Write-Log "Last Run: $($task.LastRunTime)"
            Write-Log "Next Run: $($task.NextRunTime)"

            $lastResult = Get-ScheduledTaskInfo -TaskName $TaskName
            Write-Log "Last Result: $($lastResult.LastTaskResult)"
        } else {
            Write-Log "Scheduled task not found" "WARN"
        }
    } catch {
        Write-Log "Error checking task status: $($_.Exception.Message)" "ERROR"
    }
}

function Invoke-FullCycle {
    param([string]$Org, [string]$ReportPeriod)

    Write-Log "Starting full Copilot metrics cycle for $Org" "SUCCESS"

    $success = $true

    # Step 1: Sync metrics
    if (-not (Invoke-MetricsSync -Org $Org)) {
        $success = $false
    }

    # Step 2: Generate report
    $reportPath = Invoke-MetricsReport -Org $Org -ReportPeriod $ReportPeriod

    # Step 3: Generate diff analysis
    if (-not (Invoke-MetricsDiff -Org $Org -DiffDays $Days)) {
        $success = $false
    }

    # Step 4: Send notifications
    if ($reportPath -and (Test-Path $reportPath)) {
        # Create a simple web accessible URL (you may need to adjust this)
        $webUrl = "https://your-domain.com/reports/" + (Split-Path $reportPath -Leaf)
        $shortUrl = New-BitlyShortUrl -LongUrl $webUrl

        $message = "Copilot metrics updated for $Org ($ReportPeriod)"
        Send-TelegramNotification -Message $message -ReportUrl $shortUrl

        Write-Log "Report available at: $reportPath" "SUCCESS"
    } else {
        Send-TelegramNotification -Message "Copilot metrics sync completed for $Org, but report generation failed"
    }

    if ($success) {
        Write-Log "Full cycle completed successfully" "SUCCESS"
    } else {
        Write-Log "Full cycle completed with errors" "WARN"
    }

    return $success
}

# Main execution
Write-Log "EQ12 Copilot Metrics Scheduler starting" "SUCCESS"
Write-Log "Action: $Action | Organization: $Organization | Period: $Period"

if ($TestMode) {
    Write-Log "RUNNING IN TEST MODE - No actual operations will be performed" "WARN"
}

# Check prerequisites
if (-not (Test-Prerequisites)) {
    exit 1
}

# Execute requested action
try {
    switch ($Action) {
        "sync" {
            $result = Invoke-MetricsSync -Org $Organization
            exit $(if ($result) { 0 } else { 1 })
        }
        "report" {
            $reportPath = Invoke-MetricsReport -Org $Organization -ReportPeriod $Period
            if ($reportPath) {
                Write-Log "Report generated: $reportPath" "SUCCESS"
                exit 0
            } else {
                exit 1
            }
        }
        "diff" {
            $result = Invoke-MetricsDiff -Org $Organization -DiffDays $Days
            exit $(if ($result) { 0 } else { 1 })
        }
        "install-task" {
            Install-ScheduledTask
            exit 0
        }
        "remove-task" {
            Remove-ScheduledTask
            exit 0
        }
        "status" {
            Show-TaskStatus
            exit 0
        }
        "full-cycle" {
            $result = Invoke-FullCycle -Org $Organization -ReportPeriod $Period
            exit $(if ($result) { 0 } else { 1 })
        }
    }
} catch {
    Write-Log "Fatal error: $($_.Exception.Message)" "ERROR"
    exit 1
}

Write-Log "EQ12 Copilot Metrics Scheduler completed" "SUCCESS"
