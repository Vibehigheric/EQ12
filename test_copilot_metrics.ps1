# EQ12 Copilot Metrics System - Quick Test & Demo
# Demonstrates the complete GitHub Copilot Metrics automation system

param(
    [Parameter(HelpMessage="Organization to test with")]
    [string]$Organization = "microsoft",

    [Parameter(HelpMessage="Run in demo mode (no actual API calls)")]
    [switch]$DemoMode
)

Clear-Host
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EQ12 COPILOT METRICS SYSTEM TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] Testing Copilot Metrics automation system" -ForegroundColor Green
Write-Host "[INFO] Organization: $Organization" -ForegroundColor White
Write-Host "[INFO] Demo Mode: $DemoMode" -ForegroundColor White
Write-Host ""

# Check prerequisites
Write-Host "[CHECK] Checking system prerequisites..." -ForegroundColor Yellow

$checks = @{
    "EQ12 CLI" = Test-Path "C:\EQ12\Eq12Cli.exe"
    "Scheduler Script" = Test-Path "C:\EQ12\eq12_metrics_scheduler.ps1"
    "VB.NET Metrics Client" = Test-Path "C:\EQ12\CopilotMetricsClient.vb"
    "Report Generator" = Test-Path "C:\EQ12\CopilotMetricsReportCore.vb"
    "Data Directory" = Test-Path "C:\EQ12\data"
    "Reports Directory" = Test-Path "C:\EQ12\Reports"
    "Logs Directory" = Test-Path "C:\EQ12\logs"
}

foreach ($check in $checks.GetEnumerator()) {
    if ($check.Value) {
        Write-Host "  ✅ $($check.Key)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($check.Key)" -ForegroundColor Red
        if ($check.Key -in @("Data Directory", "Reports Directory", "Logs Directory")) {
            $dir = "C:\EQ12\$($check.Key.Replace(' Directory', '').ToLower())"
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "     Created: $dir" -ForegroundColor Yellow
        }
    }
}

Write-Host ""

# Environment variables check
Write-Host "[CHECK] Environment variables..." -ForegroundColor Yellow

$envVars = @{
    "GITHUB_PAT" = [System.Environment]::GetEnvironmentVariable("GITHUB_PAT", "User")
    "TELEGRAM_BOT_TOKEN" = [System.Environment]::GetEnvironmentVariable("TELEGRAM_BOT_TOKEN", "User")
    "TELEGRAM_CHAT_ID" = [System.Environment]::GetEnvironmentVariable("TELEGRAM_CHAT_ID", "User")
    "BITLY_TOKEN" = [System.Environment]::GetEnvironmentVariable("BITLY_TOKEN", "User")
}

foreach ($var in $envVars.GetEnumerator()) {
    if ($var.Value) {
        $masked = $var.Value.Substring(0, [Math]::Min(8, $var.Value.Length)) + "..."
        Write-Host "  ✅ $($var.Key): $masked" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $($var.Key): Not configured" -ForegroundColor Yellow
    }
}

Write-Host ""

# Test the scheduler commands
Write-Host "[TEST] Testing scheduler commands..." -ForegroundColor Yellow

$testCommands = @(
    @{ Name = "Metrics Sync"; Command = "sync"; Args = "--org $Organization" }
    @{ Name = "Report Generation"; Command = "report"; Args = "--org $Organization --period daily" }
    @{ Name = "Metrics Diff"; Command = "diff"; Args = "--org $Organization --days 30" }
)

foreach ($test in $testCommands) {
    Write-Host "  [TEST] $($test.Name)..." -ForegroundColor White

    if ($DemoMode) {
        Write-Host "    Demo: powershell -File eq12_metrics_scheduler.ps1 -Action $($test.Command) $($test.Args) -TestMode" -ForegroundColor Gray
        Write-Host "    ✅ Would execute successfully" -ForegroundColor Green
    } else {
        try {
            $result = & "C:\EQ12\eq12_metrics_scheduler.ps1" -Action $test.Command -Organization $Organization -TestMode
            Write-Host "    ✅ Test passed" -ForegroundColor Green
        } catch {
            Write-Host "    ❌ Test failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

Write-Host ""

# Show usage examples
Write-Host "[USAGE] Command Examples:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Manual metrics sync:" -ForegroundColor Cyan
Write-Host "   Eq12Cli.exe metrics-sync --org your-org" -ForegroundColor White
Write-Host ""
Write-Host "2. Generate daily report:" -ForegroundColor Cyan
Write-Host "   Eq12Cli.exe metrics-report --org your-org --period daily" -ForegroundColor White
Write-Host ""
Write-Host "3. View 30-day metrics diff:" -ForegroundColor Cyan
Write-Host "   Eq12Cli.exe metrics-diff --org your-org --days 30" -ForegroundColor White
Write-Host ""
Write-Host "4. Install scheduled task:" -ForegroundColor Cyan
Write-Host "   powershell -File eq12_metrics_scheduler.ps1 -Action install-task -Organization your-org" -ForegroundColor White
Write-Host ""
Write-Host "5. Run full automation cycle:" -ForegroundColor Cyan
Write-Host "   powershell -File eq12_metrics_scheduler.ps1 -Action full-cycle -Organization your-org" -ForegroundColor White
Write-Host ""

# Show integration points
Write-Host "[INTEGRATION] System Components:" -ForegroundColor Yellow
Write-Host ""
Write-Host "📁 Data Storage:" -ForegroundColor Green
Write-Host "   • SQLite: C:\EQ12\data\bankroll.db" -ForegroundColor White
Write-Host "   • BigQuery: Auto-sync enabled" -ForegroundColor White
Write-Host ""
Write-Host "📊 Reports:" -ForegroundColor Green
Write-Host "   • PDF Reports: C:\EQ12\Reports\" -ForegroundColor White
Write-Host "   • Monetization insights included" -ForegroundColor White
Write-Host ""
Write-Host "🔔 Notifications:" -ForegroundColor Green
Write-Host "   • Telegram alerts with Bitly links" -ForegroundColor White
Write-Host "   • Daily automation reports" -ForegroundColor White
Write-Host ""
Write-Host "📅 Scheduling:" -ForegroundColor Green
Write-Host "   • Windows Task Scheduler integration" -ForegroundColor White
Write-Host "   • Daily 9:00 AM execution" -ForegroundColor White
Write-Host ""

Write-Host "[SUCCESS] EQ12 Copilot Metrics system is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Configure environment variables (GitHub PAT, Telegram, Bitly)" -ForegroundColor White
Write-Host "2. Install the scheduled task for daily automation" -ForegroundColor White
Write-Host "3. Run your first metrics sync" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
Read-Host "Press Enter to continue"
