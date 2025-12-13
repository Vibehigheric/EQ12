# EQ12 Basic Launcher - Simple Working Version
param()

$EQ12Root = "C:\EQ12"

Clear-Host
Write-Host ""
Write-Host "[LAUNCHER] EQ12 GODSTACK - BASIC LAUNCHER" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[OPTIONS] AVAILABLE OPTIONS:" -ForegroundColor Yellow
Write-Host "  1. System Status Check" -ForegroundColor White
Write-Host "  2. Start Dashboard" -ForegroundColor White
Write-Host "  3. AI Assistant" -ForegroundColor White
Write-Host "  4. EQ12 Stack Startup" -ForegroundColor White
Write-Host "  5. Chrome Setup" -ForegroundColor White
Write-Host "  6. API Configuration" -ForegroundColor White
Write-Host "  7. Program Discovery" -ForegroundColor White
Write-Host "  8. System Statistics" -ForegroundColor White
Write-Host ""
Write-Host "  0. Exit" -ForegroundColor Red
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan

$choice = Read-Host "Enter your choice"

if ($choice -eq "1") {
    Write-Host "[STATUS] Running System Status..." -ForegroundColor Green
    & "$EQ12Root\scripts\eq12_status.ps1"
}
elseif ($choice -eq "2") {
    Write-Host "[WEB] Starting Dashboard..." -ForegroundColor Green
    & "$EQ12Root\scripts\build_dashboard.ps1"
}
elseif ($choice -eq "3") {
    Write-Host "[AI] Starting AI Assistant..." -ForegroundColor Green
    python "$EQ12Root\eq12_streaming_assistant.py"
}
elseif ($choice -eq "4") {
    Write-Host "[STARTUP] Starting EQ12 Stack..." -ForegroundColor Green
    if (Test-Path "$EQ12Root\eq12_simple_start.ps1") {
        & "$EQ12Root\eq12_simple_start.ps1"
    }
    else {
        Write-Host "[ERROR] EQ12 startup script not found at: $EQ12Root\eq12_simple_start.ps1" -ForegroundColor Red
        Write-Host "[INFO] Available startup options:" -ForegroundColor Yellow
        Get-ChildItem -Path $EQ12Root -Filter "*start*.ps1" | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
    }
}
elseif ($choice -eq "5") {
    Write-Host "[CHROME] Chrome Setup..." -ForegroundColor Green
    python "$EQ12Root\chrome_governance_automation.py" --setup-profile --verbose
}
elseif ($choice -eq "6") {
    Write-Host "[CONFIG] API Configuration..." -ForegroundColor Green
    & "$EQ12Root\EQ12_API_Config.ps1"
}
elseif ($choice -eq "7") {
    Write-Host ""
    Write-Host "[DISCOVERY] DISCOVERING PROGRAMS..." -ForegroundColor Green
    Write-Host ""

    $pyCount = (Get-ChildItem -Path $EQ12Root -Filter "*.py" -Recurse | Where-Object { $_.Name -notmatch "^test_" }).Count
    $psCount = (Get-ChildItem -Path $EQ12Root -Filter "*.ps1" -Recurse | Where-Object { $_.Name -notmatch "^test_" }).Count

    Write-Host "Python Programs: $pyCount" -ForegroundColor Cyan
    Write-Host "PowerShell Programs: $psCount" -ForegroundColor Magenta
    Write-Host "Total Programs: $($pyCount + $psCount)" -ForegroundColor Yellow

    Write-Host ""
    Write-Host "[URLS] Access Points:" -ForegroundColor Yellow
    Write-Host "Local Dashboard: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "Emergency Server: http://localhost:8081" -ForegroundColor Cyan
}
elseif ($choice -eq "8") {
    Write-Host ""
    Write-Host "[STATS] SYSTEM STATISTICS:" -ForegroundColor Green
    Write-Host ""

    $totalFiles = (Get-ChildItem -Path $EQ12Root -Recurse -File).Count
    $directoriesCount = (Get-ChildItem -Path $EQ12Root -Recurse -Directory).Count
    $totalSize = [math]::Round((Get-ChildItem -Path $EQ12Root -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB, 2)

    Write-Host "Total Files: $totalFiles" -ForegroundColor White
    Write-Host "Directories: $directoriesCount" -ForegroundColor White
    Write-Host "Total Size: $totalSize MB" -ForegroundColor White
    Write-Host "Last Scan: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
}
elseif ($choice -eq "0") {
    Write-Host ""
    Write-Host "[EXIT] Exiting EQ12 Launcher..." -ForegroundColor Green
    exit
}
else {
    Write-Host "❌ Invalid choice" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
