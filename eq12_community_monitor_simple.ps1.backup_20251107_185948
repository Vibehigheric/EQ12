param(
    [string]$Action = "single",
    [int]$Interval = 15,
    [int]$ReportDays = 7
)

$ErrorActionPreference = "Stop"
$PythonScript = "C:\EQ12\eq12_community_monitor_clean.py"

Write-Host "EQ12 Community Monitor - Action: $Action" -ForegroundColor Green

if ($Action -eq "install-deps") {
    Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
    python -m pip install feedparser requests PyGithub
    Write-Host "Dependencies installed!" -ForegroundColor Green
}
elseif ($Action -eq "single") {
    Write-Host "Running single monitoring cycle..." -ForegroundColor Cyan
    python $PythonScript --single
}
elseif ($Action -eq "continuous") {
    Write-Host "Starting continuous monitoring..." -ForegroundColor Cyan
    python $PythonScript --continuous --interval $Interval
}
elseif ($Action -eq "report") {
    Write-Host "Generating report..." -ForegroundColor Cyan
    python $PythonScript --report $ReportDays
}
else {
    Write-Host "Usage: .\script.ps1 -Action [install-deps|single|continuous|report]" -ForegroundColor Yellow
}
