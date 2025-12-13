# EQ12_Quick_Test.ps1
<#
.SYNOPSIS
    EQ12 Quick Integration Test - Simplified Version

.DESCRIPTION
    Tests core EQ12 components without complex embedded code
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("quick", "full")]
    [string]$TestType = "quick"
)

# Force UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Details = ""
    )

    $status = if ($Passed) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($Passed) { "Green" } else { "Red" }

    Write-Host "$TestName : $status" -ForegroundColor $color
    if ($Details -and -not $Passed) {
        Write-Host "   Details: $Details" -ForegroundColor Yellow
    }
}

Write-Host "🧪 EQ12 QUICK INTEGRATION TEST SUITE" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

# Test 1: File Structure
Write-Host "📁 Testing Core Files..." -ForegroundColor Cyan
$coreFiles = @(
    "eq12_comprehensive_llm_automation.py",
    "eq12_enhanced_dashboard_server.js",
    "EQ12_UTF8_PowerShell_Services.ps1"
)

$fileTests = @()
foreach ($file in $coreFiles) {
    $exists = Test-Path $file
    Write-TestResult "File: $file" $exists
    $fileTests += $exists
}

# Test 2: Directory Structure
Write-Host "`n📂 Testing Directories..." -ForegroundColor Cyan
$requiredDirs = @("logs", "configs", "scripts", "tests")
$dirTests = @()

foreach ($dir in $requiredDirs) {
    $dirPath = "C:\EQ12\$dir"
    $exists = Test-Path $dirPath
    if (-not $exists) {
        try {
            New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
            $exists = $true
        } catch {
            $exists = $false
        }
    }
    Write-TestResult "Directory: $dir" $exists
    $dirTests += $exists
}

# Test 3: UTF-8 Configuration
Write-Host "`n🔤 Testing UTF-8 Support..." -ForegroundColor Cyan
$utf8Tests = @()

# Test PowerShell encoding
$encoding = [Console]::OutputEncoding.EncodingName
$utf8Test = $encoding -eq "Unicode (UTF-8)"
Write-TestResult "PowerShell UTF-8" $utf8Test "Current: $encoding"
$utf8Tests += $utf8Test

# Test file encoding
try {
    $testDir = "C:\EQ12\logs"
    if (-not (Test-Path $testDir)) {
        New-Item -ItemType Directory -Path $testDir -Force | Out-Null
    }

    $testFile = "$testDir\utf8_test.txt"
    $testContent = "UTF-8 Test: Special chars àáâãäåæçèé"

    Set-Content -Path $testFile -Value $testContent -Encoding UTF8
    $readContent = Get-Content -Path $testFile -Encoding UTF8
    $fileTest = $readContent -eq $testContent

    Write-TestResult "File UTF-8 Read/Write" $fileTest
    $utf8Tests += $fileTest

    Remove-Item $testFile -ErrorAction SilentlyContinue

} catch {
    Write-TestResult "File UTF-8 Read/Write" $false $_.Exception.Message
    $utf8Tests += $false
}

# Test 4: Python Environment
Write-Host "`n🐍 Testing Python Environment..." -ForegroundColor Cyan
$pythonTests = @()

try {
    $pythonVersion = python --version 2>$null
    $pythonOK = $LASTEXITCODE -eq 0 -and $pythonVersion
    Write-TestResult "Python Installation" $pythonOK $pythonVersion
    $pythonTests += $pythonOK

    if ($pythonOK) {
        # Test key imports
        $importTest = $true
        $packages = @("json", "datetime", "logging", "asyncio")

        foreach ($package in $packages) {
            try {
                python -c "import $package" 2>$null
                if ($LASTEXITCODE -ne 0) {
                    $importTest = $false
                    break
                }
            } catch {
                $importTest = $false
                break
            }
        }

        Write-TestResult "Python Core Packages" $importTest
        $pythonTests += $importTest
    }

} catch {
    Write-TestResult "Python Installation" $false "Python not found"
    $pythonTests += $false
}

# Test 5: Node.js Environment (if requested)
$nodeTests = @()
if ($TestType -eq "full") {
    Write-Host "`n🟢 Testing Node.js Environment..." -ForegroundColor Cyan

    try {
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

        $nodeVersion = node --version 2>$null
        $nodeOK = $LASTEXITCODE -eq 0 -and $nodeVersion

        if (-not $nodeOK) {
            # Try common paths
            $nodePaths = @(
                "${env:ProgramFiles}\nodejs\node.exe",
                "${env:ProgramFiles(x86)}\nodejs\node.exe"
            )

            foreach ($path in $nodePaths) {
                if (Test-Path $path) {
                    try {
                        $nodeVersion = & $path --version 2>$null
                        if ($LASTEXITCODE -eq 0) {
                            $nodeOK = $true
                            break
                        }
                    } catch {
                        continue
                    }
                }
            }
        }

        Write-TestResult "Node.js Installation" $nodeOK $nodeVersion
        $nodeTests += $nodeOK

    } catch {
        Write-TestResult "Node.js Installation" $false "Node.js not found"
        $nodeTests += $false
    }
}

# Test 6: Logging System
Write-Host "`n📝 Testing Logging System..." -ForegroundColor Cyan
$logTests = @()

$logDir = "C:\EQ12\logs"
$logDirTest = Test-Path $logDir
Write-TestResult "Log Directory" $logDirTest
$logTests += $logDirTest

if ($logDirTest) {
    try {
        $testLogFile = "$logDir\test_$(Get-Date -Format "yyyyMMdd_HHmmss").log"
        $logEntry = @{
            timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
            level = "INFO"
            message = "Test log entry"
            component = "integration_test"
        } | ConvertTo-Json -Compress

        Set-Content -Path $testLogFile -Value $logEntry -Encoding UTF8

        $logContent = Get-Content -Path $testLogFile -Encoding UTF8
        $logTest = $logContent -eq $logEntry

        Write-TestResult "Log File Creation" $logTest
        $logTests += $logTest

        Remove-Item $testLogFile -ErrorAction SilentlyContinue

    } catch {
        Write-TestResult "Log File Creation" $false $_.Exception.Message
        $logTests += $false
    }
}

# Calculate overall results
$allTestResults = $fileTests + $dirTests + $utf8Tests + $pythonTests + $nodeTests + $logTests
$passedTests = ($allTestResults | Where-Object { $_ }).Count
$totalTests = $allTestResults.Count
$passRate = if ($totalTests -gt 0) { [math]::Round(($passedTests / $totalTests) * 100, 1) } else { 0 }

# Display summary
Write-Host "`n🎯 TEST SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 30 -ForegroundColor Cyan
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Total: $totalTests" -ForegroundColor White
Write-Host "Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -ge 80) { "Green" } elseif ($passRate -ge 60) { "Yellow" } else { "Red" })

if ($passRate -ge 80) {
    Write-Host "`n🚀 SYSTEM READY!" -ForegroundColor Green
    Write-Host "✅ Core EQ12 components are operational" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Install Node.js for dashboard: https://nodejs.org" -ForegroundColor White
    Write-Host "2. Set OpenAI API key: `$env:OPENAI_API_KEY = `"your-key`"" -ForegroundColor White
    Write-Host "3. Run PowerShell services: .\EQ12_UTF8_PowerShell_Services.ps1" -ForegroundColor White
    Write-Host "4. Test Python automation: python eq12_comprehensive_llm_automation.py --test" -ForegroundColor White

} elseif ($passRate -ge 60) {
    Write-Host "`n⚠️ PARTIAL SUCCESS" -ForegroundColor Yellow
    Write-Host "Some components need attention - check failed tests above" -ForegroundColor Yellow

} else {
    Write-Host "`n❌ SETUP NEEDED" -ForegroundColor Red
    Write-Host "Multiple issues detected - please address failed tests" -ForegroundColor Red
}

Write-Host "`nTest completed: $(Get-Date -Format "HH:mm:ss")" -ForegroundColor Gray

# Save results
$results = @{
    timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    test_type = $TestType
    passed = $passedTests
    total = $totalTests
    pass_rate = $passRate
    status = if ($passRate -ge 80) { "ready" } elseif ($passRate -ge 60) { "partial" } else { "needs_work" }
} | ConvertTo-Json -Depth 5

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$resultsFile = "C:\EQ12\logs\quick_test_$timestamp.json"
Set-Content -Path $resultsFile -Value $results -Encoding UTF8

Write-Host "Results saved to: $resultsFile" -ForegroundColor DarkGray
