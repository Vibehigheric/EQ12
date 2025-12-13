param([string]$Action = "Test")

$EQ12Root = "C:\EQ12"
$PythonExecutable = "C:\Program Files\Python312\python.exe"
$ChromeScript = "$EQ12Root\chrome_governance_automation.py"

Write-Host "[INFO] EQ12 Chrome Governance Test" -ForegroundColor Cyan
Write-Host ""

# Test Python
if (Test-Path $PythonExecutable) {
    Write-Host "[SUCCESS] Python found: $PythonExecutable" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not found: $PythonExecutable" -ForegroundColor Red
    exit 1
}

# Test Chrome script
if (Test-Path $ChromeScript) {
    Write-Host "[SUCCESS] Chrome script found: $ChromeScript" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Chrome script not found: $ChromeScript" -ForegroundColor Red
    exit 1
}

# Test Chrome executable
$chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
if (Test-Path $chromeExe) {
    Write-Host "[SUCCESS] Chrome executable found" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Chrome executable not found at standard location" -ForegroundColor Yellow
}

# Run validation
Write-Host "[INFO] Running Chrome governance validation..." -ForegroundColor White
try {
    & $PythonExecutable $ChromeScript --validate-profile
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Chrome governance validation successful!" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "[WARNING] Chrome governance validation returned exit code: $LASTEXITCODE" -ForegroundColor Yellow
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "[ERROR] Script execution failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
