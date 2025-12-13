# EQ12 Daily Sports Betting Operations
# Final Form PowerShell Script for Task Scheduler Integration
param(
    [Parameter()]
    [ValidateSet("Full", "IngestOnly", "ArbScan", "Summary", "LiveWatch", "Health")]
    [string]$Operation = "Full",

    [Parameter()]
    [switch]$Verbose,

    [Parameter()]
    [switch]$NoAlerts
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Configuration
$EQ12_ROOT = "C:\EQ12\visual_studio_projects\EQ12SportsBettingTerminal"
$CLI_PATH = Join-Path $EQ12_ROOT "bin\Debug\Eq12Cli.exe"
$LOG_PATH = "C:\EQ12\logs\daily_operations_$(Get-Date -Format 'yyyyMMdd').log"

# Ensure log directory exists
$logDir = Split-Path $LOG_PATH -Parent
if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory -Force | Out-Null
}

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    Write-Host $logEntry -ForegroundColor $(switch($Level) {
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "SUCCESS" { "Green" }
        default { "White" }
    })

    Add-Content -Path $LOG_PATH -Value $logEntry
}

function Test-Prerequisites {
    Write-Log "🔍 Checking prerequisites..."

    # Check CLI executable
    if (-not (Test-Path $CLI_PATH)) {
        throw "EQ12 CLI not found at: $CLI_PATH"
    }

    # Check config files
    $configPath = Join-Path $EQ12_ROOT "Config\config.json"
    if (-not (Test-Path $configPath)) {
        throw "Config file not found at: $configPath"
    }

    # Check database
    $dbPath = Join-Path $EQ12_ROOT "Data\bankroll.db"
    if (-not (Test-Path $dbPath)) {
        Write-Log "Database not found, will be created automatically" "WARN"
    }

    Write-Log "✅ Prerequisites check completed" "SUCCESS"
}

function Invoke-CliCommand {
    param(
        [string]$Command,
        [string]$Description,
        [int]$TimeoutMinutes = 10
    )

    Write-Log "🔄 $Description..."

    try {
        $startTime = Get-Date

        # Build full command
        $arguments = @($Command)
        if ($Verbose) { $arguments += "--verbose" }

        $processInfo = New-Object System.Diagnostics.ProcessStartInfo
        $processInfo.FileName = $CLI_PATH
        $processInfo.Arguments = $arguments -join " "
        $processInfo.WorkingDirectory = $EQ12_ROOT
        $processInfo.RedirectStandardOutput = $true
        $processInfo.RedirectStandardError = $true
        $processInfo.UseShellExecute = $false
        $processInfo.CreateNoWindow = $true

        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $processInfo

        # Start process
        $process.Start() | Out-Null

        # Read output
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()

        # Wait for completion with timeout
        $completed = $process.WaitForExit($TimeoutMinutes * 60000)

        if (-not $completed) {
            $process.Kill()
            throw "Command timed out after $TimeoutMinutes minutes"
        }

        $duration = (Get-Date) - $startTime

        if ($process.ExitCode -eq 0) {
            Write-Log "✅ $Description completed successfully (${duration})" "SUCCESS"
            if ($stdout -and $Verbose) {
                Write-Log "Output: $stdout"
            }
            return $stdout
        } else {
            throw "Exit code: $($process.ExitCode). Error: $stderr"
        }

    } catch {
        Write-Log "❌ $Description failed: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Send-AlertNotification {
    param(
        [string]$Message,
        [string]$Type = "INFO"
    )

    if ($NoAlerts) {
        Write-Log "Alert skipped (NoAlerts flag): $Message"
        return
    }

    try {
        # Send via Telegram using PowerShell
        $configPath = Join-Path $EQ12_ROOT "Config\config.json"
        $config = Get-Content $configPath | ConvertFrom-Json

        $telegramToken = $config.telegram.token
        $chatId = $config.telegram.chat_id

        if ($telegramToken -and $chatId) {
            $emoji = switch($Type) {
                "ERROR" { "❌" }
                "SUCCESS" { "✅" }
                "WARN" { "⚠️" }
                default { "ℹ️" }
            }

            $fullMessage = "$emoji EQ12 Daily Operations`n$Message`n🕐 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

            $uri = "https://api.telegram.org/bot$telegramToken/sendMessage"
            $body = @{
                chat_id = $chatId
                text = $fullMessage
                parse_mode = "Markdown"
            } | ConvertTo-Json

            Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json" | Out-Null
            Write-Log "📤 Alert sent via Telegram" "SUCCESS"
        }

    } catch {
        Write-Log "Failed to send alert: $($_.Exception.Message)" "WARN"
    }
}

function Start-DailyOperations {
    Write-Log "🚀 Starting EQ12 Daily Operations - $Operation mode" "SUCCESS"

    try {
        Test-Prerequisites

        $startTime = Get-Date
        $results = @{}

        switch ($Operation) {
            "Full" {
                Write-Log "📊 Running full daily operations suite..."

                # 1. Health check
                $results["health"] = Invoke-CliCommand "health" "System health check" 2

                # 2. Ingest latest odds
                $results["ingest"] = Invoke-CliCommand "ingest-odds" "Ingesting latest odds" 15

                # 3. Scan for arbitrage
                $results["scan"] = Invoke-CliCommand "scan-arb" "Scanning arbitrage opportunities" 5

                # 4. Generate and push summary
                $results["summary"] = Invoke-CliCommand "push-summary" "Generating daily summary" 5

                # 5. Show arbitrage history
                $results["history"] = Invoke-CliCommand "arb-history" "Retrieving arbitrage history" 2
            }

            "IngestOnly" {
                $results["ingest"] = Invoke-CliCommand "ingest-odds" "Ingesting latest odds" 15
            }

            "ArbScan" {
                $results["scan"] = Invoke-CliCommand "scan-arb" "Scanning arbitrage opportunities" 5
            }

            "Summary" {
                $results["summary"] = Invoke-CliCommand "push-summary" "Generating daily summary" 5
            }

            "LiveWatch" {
                Write-Log "🔄 Starting live arbitrage watch (runs until stopped)..."
                $results["watch"] = Invoke-CliCommand "live-watch" "Live arbitrage monitoring" 1440 # 24 hours
            }

            "Health" {
                $results["health"] = Invoke-CliCommand "health" "System health check" 2
            }
        }

        $duration = (Get-Date) - $startTime
        $successMessage = "🎯 EQ12 Daily Operations completed successfully!`nOperation: $Operation`nDuration: $duration`nTimestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

        Write-Log $successMessage "SUCCESS"
        Send-AlertNotification $successMessage "SUCCESS"

        # Output results summary
        Write-Log "📋 Operation Results Summary:"
        foreach ($key in $results.Keys) {
            Write-Log "  ✅ $key : Completed"
        }

    } catch {
        $errorMessage = "EQ12 Daily Operations failed!`nOperation: $Operation`nError: $($_.Exception.Message)`nTimestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

        Write-Log $errorMessage "ERROR"
        Send-AlertNotification $errorMessage "ERROR"

        # Exit with error code for Task Scheduler
        exit 1
    }
}

function Show-Usage {
    Write-Host @"
🎯 EQ12 Daily Sports Betting Operations Script

Usage: .\daily_operations.ps1 [Parameters]

Parameters:
  -Operation [Full|IngestOnly|ArbScan|Summary|LiveWatch|Health]
             Default: Full

  -Verbose   Enable verbose output

  -NoAlerts  Skip Telegram notifications

Operations:
  Full       - Complete daily suite (health, ingest, scan, summary)
  IngestOnly - Only pull latest odds from API
  ArbScan    - Only scan for arbitrage opportunities
  Summary    - Only generate and push daily summary
  LiveWatch  - Start continuous arbitrage monitoring
  Health     - Only perform system health check

Examples:
  .\daily_operations.ps1
  .\daily_operations.ps1 -Operation ArbScan -Verbose
  .\daily_operations.ps1 -Operation LiveWatch -NoAlerts

Task Scheduler Integration:
  schtasks /create /tn "EQ12DailyOps" /tr "powershell -ExecutionPolicy Bypass -File C:\EQ12\daily_operations.ps1" /sc daily /st 09:00

"@
}

# Main execution
if ($args.Count -eq 0 -or $args[0] -eq "-help" -or $args[0] -eq "--help") {
    Show-Usage
    exit 0
}

try {
    Start-DailyOperations
} catch {
    Write-Log "Fatal error in main execution: $($_.Exception.Message)" "ERROR"
    exit 1
}
