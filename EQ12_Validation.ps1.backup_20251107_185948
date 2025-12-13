# EQ12_Validation.ps1 - Simple platform validation

Write-Host "EQ12 PLATFORM VALIDATION" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# Check files
Write-Host "`nFile Structure Check:" -ForegroundColor White

$files = @(
    "eq12_sports_betting_analytics_platform.py",
    "eq12_responsible_gaming_engine.py",
    "eq12_realtime_betting_dashboard.js",
    "EQ12_LLM_Platform_Launcher.ps1",
    "EQ12_LLM_Platform_Job_Postings.md"
)

$fileCount = 0
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
        $fileCount++
    }
    else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
    }
}

# Check Python
Write-Host "`nPython Check:" -ForegroundColor White
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $pythonVersion" -ForegroundColor Green
        $pythonOK = $true
    }
    else {
        Write-Host "  [FAIL] Python not found" -ForegroundColor Red
        $pythonOK = $false
    }
}
catch {
    Write-Host "  [FAIL] Python not available" -ForegroundColor Red
    $pythonOK = $false
}

# Check Node.js
Write-Host "`nNode.js Check:" -ForegroundColor White
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $nodeVersion" -ForegroundColor Green
        $nodeOK = $true
    }
    else {
        Write-Host "  [FAIL] Node.js not found" -ForegroundColor Red
        $nodeOK = $false
    }
}
catch {
    Write-Host "  [FAIL] Node.js not available" -ForegroundColor Red
    $nodeOK = $false
}

# Check environment variables
Write-Host "`nEnvironment Variables:" -ForegroundColor White
$envVars = @("OPENAI_API_KEY", "ODDS_API_KEY", "TELEGRAM_BOT_TOKEN")
$envCount = 0
foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "  [SET] $var" -ForegroundColor Green
        $envCount++
    }
    else {
        Write-Host "  [NOT SET] $var" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`nSUMMARY:" -ForegroundColor Cyan
Write-Host "Files: $fileCount/5 found" -ForegroundColor $(if ($fileCount -eq 5) { "Green" } else { "Yellow" })
Write-Host "Python: $(if ($pythonOK) {"Available"} else {"Missing"})" -ForegroundColor $(if ($pythonOK) { "Green" } else { "Red" })
Write-Host "Node.js: $(if ($nodeOK) {"Available"} else {"Missing"})" -ForegroundColor $(if ($nodeOK) { "Green" } else { "Red" })
Write-Host "Env Vars: $envCount/3 set" -ForegroundColor $(if ($envCount -gt 0) { "Green" } else { "Yellow" })

if ($fileCount -eq 5 -and $pythonOK) {
    Write-Host "`nPLATFORM READY FOR DEPLOYMENT!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor White
    Write-Host "1. Set environment variables (optional)" -ForegroundColor White
    Write-Host "2. Run: .\EQ12_LLM_Platform_Launcher.ps1 -Action start" -ForegroundColor White
    Write-Host "3. Access: http://localhost:3000/dashboard" -ForegroundColor White
}
else {
    Write-Host "`nPLATFORM NEEDS SETUP" -ForegroundColor Yellow
    Write-Host "Install missing components above" -ForegroundColor White
}

Write-Host "`nJob Postings: EQ12_LLM_Platform_Job_Postings.md" -ForegroundColor Magenta
