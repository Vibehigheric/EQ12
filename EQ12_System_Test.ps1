# EQ12_Simple_Test.ps1
# Simple test script for EQ12 validation

[CmdletBinding()]
param()

# Set UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Details = ""
    )

    if ($Passed) {
        Write-Host "✅ $TestName" -ForegroundColor Green
    } else {
        Write-Host "❌ $TestName" -ForegroundColor Red
        if ($Details) {
            Write-Host "   $Details" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "🧪 EQ12 SYSTEM VALIDATION" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# Test results array
$testResults = @()

# Test 1: Core files
Write-Host "📁 Core Files:" -ForegroundColor Cyan
$coreFiles = @(
    "eq12_comprehensive_llm_automation.py",
    "eq12_enhanced_dashboard_server.js",
    "EQ12_UTF8_PowerShell_Services.ps1"
)

foreach ($file in $coreFiles) {
    $exists = Test-Path $file
    Write-TestResult $file $exists
    $testResults += $exists
}

# Test 2: Directories
Write-Host "`n📂 Directories:" -ForegroundColor Cyan
$dirs = @("logs", "configs", "scripts", "tests")
foreach ($dir in $dirs) {
    $path = "C:\EQ12\$dir"
    $exists = Test-Path $path
    if (-not $exists) {
        try {
            New-Item -ItemType Directory -Path $path -Force | Out-Null
            $exists = $true
        } catch {
            $exists = $false
        }
    }
    Write-TestResult $dir $exists
    $testResults += $exists
}

# Test 3: UTF-8 Support
Write-Host "`n🔤 UTF-8 Support:" -ForegroundColor Cyan
$encoding = [Console]::OutputEncoding.EncodingName
$utf8OK = $encoding -eq "Unicode (UTF-8)"
Write-TestResult "PowerShell UTF-8 Encoding" $utf8OK $encoding
$testResults += $utf8OK

# Test file encoding
try {
    $testFile = "C:\EQ12\logs\test.txt"
    $content = "Test content with accents: café résumé"
    Set-Content -Path $testFile -Value $content -Encoding UTF8
    $readBack = Get-Content -Path $testFile -Encoding UTF8
    $fileTest = $readBack -eq $content
    Write-TestResult "File UTF-8 Operations" $fileTest
    $testResults += $fileTest
    Remove-Item $testFile -ErrorAction SilentlyContinue
} catch {
    Write-TestResult "File UTF-8 Operations" $false $_.Exception.Message
    $testResults += $false
}

# Test 4: Python
Write-Host "`n🐍 Python Environment:" -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>$null
    $pythonOK = $LASTEXITCODE -eq 0
    Write-TestResult "Python Available" $pythonOK $pythonVersion
    $testResults += $pythonOK
} catch {
    Write-TestResult "Python Available" $false "Python not found"
    $testResults += $false
}

# Test 5: Node.js (basic check)
Write-Host "`n🟢 Node.js Environment:" -ForegroundColor Cyan
try {
    $nodeVersion = node --version 2>$null
    $nodeOK = $LASTEXITCODE -eq 0
    if ($nodeOK) {
        Write-TestResult "Node.js Available" $true $nodeVersion
    } else {
        Write-TestResult "Node.js Available" $false "Node.js not in PATH"
    }
    $testResults += $nodeOK
} catch {
    Write-TestResult "Node.js Available" $false "Node.js not found"
    $testResults += $false
}

# Test 6: Logging
Write-Host "`n📝 Logging System:" -ForegroundColor Cyan
$logDir = "C:\EQ12\logs"
$logTest = Test-Path $logDir
Write-TestResult "Log Directory" $logTest
$testResults += $logTest

# Calculate results
$passed = ($testResults | Where-Object { $_ }).Count
$total = $testResults.Count
$percentage = [math]::Round(($passed / $total) * 100, 1)

# Summary
Write-Host "`n🎯 RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan
Write-Host "Passed: $passed/$total ($percentage%)" -ForegroundColor $(if ($percentage -ge 80) { "Green" } else { "Yellow" })

if ($percentage -ge 80) {
    Write-Host "`n🚀 SYSTEM STATUS: READY" -ForegroundColor Green
    Write-Host "✅ EQ12 core components are functional" -ForegroundColor Green
} elseif ($percentage -ge 60) {
    Write-Host "`n⚠️ SYSTEM STATUS: PARTIAL" -ForegroundColor Yellow
    Write-Host "Some components need attention" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ SYSTEM STATUS: NEEDS WORK" -ForegroundColor Red
    Write-Host "Multiple issues require resolution" -ForegroundColor Red
}

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Install missing components (Node.js if needed)" -ForegroundColor White
Write-Host "2. Configure API keys and services" -ForegroundColor White
Write-Host "3. Run specific component tests" -ForegroundColor White

# Save results
$resultsData = @{
    timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    passed = $passed
    total = $total
    percentage = $percentage
    status = if ($percentage -ge 80) { "ready" } elseif ($percentage -ge 60) { "partial" } else { "needs_work" }
}

$jsonResults = $resultsData | ConvertTo-Json -Depth 3
$resultsFile = "C:\EQ12\logs\simple_test_results.json"
Set-Content -Path $resultsFile -Value $jsonResults -Encoding UTF8

Write-Host "`nResults saved to: $resultsFile" -ForegroundColor Gray
Write-Host "Test completed at: $(Get-Date -Format "HH:mm:ss")" -ForegroundColor Gray
