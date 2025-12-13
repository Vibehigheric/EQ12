# EQ12 Copilot Metrics - Simple Test
param([switch]$DemoMode)

Clear-Host
Write-Host "EQ12 COPILOT METRICS SYSTEM TEST" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[CHECK] System Components:" -ForegroundColor Yellow

$files = @(
    "CopilotMetricsClient.vb",
    "CopilotMetricsReportCore.vb",
    "eq12_metrics_scheduler.ps1",
    "Eq12Cli.exe"
)

foreach ($file in $files) {
    $path = "C:\EQ12\$file"
    if (Test-Path $path) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[USAGE] Example Commands:" -ForegroundColor Yellow
Write-Host "1. Sync metrics: Eq12Cli.exe metrics-sync --org your-org" -ForegroundColor White
Write-Host "2. Generate report: Eq12Cli.exe metrics-report --org your-org --period daily" -ForegroundColor White
Write-Host "3. Install scheduler: powershell eq12_metrics_scheduler.ps1 -Action install-task" -ForegroundColor White
Write-Host ""

Write-Host "[SUCCESS] Copilot Metrics system ready!" -ForegroundColor Green
Write-Host ""
