# EQ12_Quick_Deployment_Test.ps1
"""
Quick deployment test for EQ12 Sports Betting Analytics Platform
Validates core functionality and readiness for production
"""

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("quick", "full", "security", "performance")]
    [string]$TestType = "quick",

    [Parameter(Mandatory = $false)]
    [switch]$SkipDependencies,

    [Parameter(Mandatory = $false)]
    [switch]$Verbose
)

# Force UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Enhanced logging function
function Write-StructuredLog {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS", "DEBUG")]
        [string]$Level = "INFO",
        [hashtable]$Data = @{}
    )

    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
    $logEntry = @{
        timestamp = $timestamp
        level     = $Level
        message   = $Message
        component = "EQ12_Deployment_Test"
        data      = $Data
    }

    $jsonLog = $logEntry | ConvertTo-Json -Compress

    # Color output for console
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARN" { "Yellow" }
        "DEBUG" { "Gray" }
        default { "White" }
    }

    Write-Host "[$Level] $Message" -ForegroundColor $color

    # Log to file
    $logDir = "C:\EQ12\logs"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    $logFile = Join-Path $logDir "deployment_test_$(Get-Date -Format 'yyyyMMdd').log"
    $jsonLog | Out-File -FilePath $logFile -Append -Encoding UTF8
}

function Test-PythonEnvironment {
    Write-StructuredLog "Testing Python environment..." -Level "INFO"

    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found in PATH"
        }

        Write-StructuredLog "Python found: $pythonVersion" -Level "SUCCESS"

        # Test required packages
        $requiredPackages = @("pytest", "asyncio", "json", "logging", "pathlib")
        foreach ($package in $requiredPackages) {
            try {
                python -c "import $package" 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-StructuredLog "Package available: $package" -Level "SUCCESS"
                }
                else {
                    Write-StructuredLog "Package missing: $package" -Level "WARN"
                }
            }
            catch {
                Write-StructuredLog "Package check failed: $package" -Level "WARN"
            }
        }

        return $true
    }
    catch {
        Write-StructuredLog "Python environment test failed: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Test-NodeEnvironment {
    Write-StructuredLog "Testing Node.js environment..." -Level "INFO"

    try {
        $nodeVersion = node --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-StructuredLog "Node.js not found in PATH" -Level "WARN"
            return $false
        }

        Write-StructuredLog "Node.js found: $nodeVersion" -Level "SUCCESS"

        $npmVersion = npm --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-StructuredLog "NPM found: $npmVersion" -Level "SUCCESS"
        }

        return $true
    }
    catch {
        Write-StructuredLog "Node.js environment test failed: $($_.Exception.Message)" -Level "WARN"
        return $false
    }
}

function Test-RedisConnection {
    Write-StructuredLog "Testing Redis availability..." -Level "INFO"

    try {
        # Test if Redis is running on default port
        $redisTest = Test-NetConnection -ComputerName "localhost" -Port 6379 -WarningAction SilentlyContinue

        if ($redisTest.TcpTestSucceeded) {
            Write-StructuredLog "Redis connection successful" -Level "SUCCESS"
            return $true
        }
        else {
            Write-StructuredLog "Redis not available on localhost:6379" -Level "WARN"
            return $false
        }
    }
    catch {
        Write-StructuredLog "Redis test failed: $($_.Exception.Message)" -Level "WARN"
        return $false
    }
}

function Test-FileStructure {
    Write-StructuredLog "Testing file structure..." -Level "INFO"

    $requiredFiles = @(
        "eq12_sports_betting_analytics_platform.py",
        "eq12_responsible_gaming_engine.py",
        "eq12_realtime_betting_dashboard.js",
        "EQ12_LLM_Platform_Launcher.ps1",
        "EQ12_LLM_Platform_Job_Postings.md",
        "test_eq12_comprehensive_platform.py"
    )

    $missingFiles = @()
    $foundFiles = @()

    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            $foundFiles += $file
            Write-StructuredLog "File found: $file" -Level "SUCCESS"
        }
        else {
            $missingFiles += $file
            Write-StructuredLog "File missing: $file" -Level "ERROR"
        }
    }

    $result = @{
        foundFiles    = $foundFiles
        missingFiles  = $missingFiles
        totalRequired = $requiredFiles.Length
        foundCount    = $foundFiles.Length
    }

    Write-StructuredLog "File structure check complete" -Level "INFO" -Data $result

    return $missingFiles.Length -eq 0
}

function Test-PythonSyntax {
    Write-StructuredLog "Testing Python syntax..." -Level "INFO"

    $pythonFiles = @(
        "eq12_sports_betting_analytics_platform.py",
        "eq12_responsible_gaming_engine.py",
        "test_eq12_comprehensive_platform.py"
    )

    $syntaxErrors = @()

    foreach ($file in $pythonFiles) {
        if (Test-Path $file) {
            try {
                $syntaxCheck = python -m py_compile $file 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-StructuredLog "Syntax OK: $file" -Level "SUCCESS"
                }
                else {
                    $syntaxErrors += $file
                    Write-StructuredLog "Syntax ERROR: $file - $syntaxCheck" -Level "ERROR"
                }
            }
            catch {
                $syntaxErrors += $file
                Write-StructuredLog "Syntax check failed: $file" -Level "ERROR"
            }
        }
    }

    return $syntaxErrors.Length -eq 0
}

function Test-NodeJSSyntax {
    Write-StructuredLog "Testing Node.js syntax..." -Level "INFO"

    $nodeFiles = @("eq12_realtime_betting_dashboard.js")

    $syntaxErrors = @()

    foreach ($file in $nodeFiles) {
        if (Test-Path $file) {
            try {
                $syntaxCheck = node -c $file 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-StructuredLog "Syntax OK: $file" -Level "SUCCESS"
                }
                else {
                    $syntaxErrors += $file
                    Write-StructuredLog "Syntax ERROR: $file - $syntaxCheck" -Level "ERROR"
                }
            }
            catch {
                $syntaxErrors += $file
                Write-StructuredLog "Syntax check failed: $file" -Level "ERROR"
            }
        }
    }

    return $syntaxErrors.Length -eq 0
}

function Test-PowerShellSyntax {
    Write-StructuredLog "Testing PowerShell syntax..." -Level "INFO"

    $psFiles = @("EQ12_LLM_Platform_Launcher.ps1")

    $syntaxErrors = @()

    foreach ($file in $psFiles) {
        if (Test-Path $file) {
            try {
                # Test PowerShell syntax by parsing
                $errors = $null
                $ast = [System.Management.Automation.Language.Parser]::ParseFile(
                    (Resolve-Path $file).Path,
                    [ref]$null,
                    [ref]$errors
                )

                if ($errors.Count -eq 0) {
                    Write-StructuredLog "Syntax OK: $file" -Level "SUCCESS"
                }
                else {
                    $syntaxErrors += $file
                    Write-StructuredLog "Syntax ERROR: $file - $($errors[0].Message)" -Level "ERROR"
                }
            }
            catch {
                $syntaxErrors += $file
                Write-StructuredLog "Syntax check failed: $file" -Level "ERROR"
            }
        }
    }

    return $syntaxErrors.Length -eq 0
}

function Test-EnvironmentVariables {
    Write-StructuredLog "Testing environment variables..." -Level "INFO"

    $requiredEnvVars = @(
        "OPENAI_API_KEY",
        "ODDS_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID"
    )

    $missingVars = @()

    foreach ($var in $requiredEnvVars) {
        $value = [Environment]::GetEnvironmentVariable($var)
        if ($value) {
            Write-StructuredLog "Environment variable set: $var" -Level "SUCCESS"
        }
        else {
            $missingVars += $var
            Write-StructuredLog "Environment variable missing: $var" -Level "WARN"
        }
    }

    if ($missingVars.Length -gt 0) {
        Write-StructuredLog "Missing environment variables - platform will use fallback mode" -Level "WARN"
    }

    return $true  # Don't fail on missing env vars, just warn
}

function Run-QuickTests {
    Write-StructuredLog "Running quick deployment tests..." -Level "INFO"

    $testResults = @{
        fileStructure        = Test-FileStructure
        pythonEnvironment    = Test-PythonEnvironment
        nodeEnvironment      = Test-NodeEnvironment
        pythonSyntax         = Test-PythonSyntax
        nodeJSSyntax         = Test-NodeJSSyntax
        powerShellSyntax     = Test-PowerShellSyntax
        environmentVariables = Test-EnvironmentVariables
    }

    $passedTests = ($testResults.Values | Where-Object { $_ -eq $true }).Count
    $totalTests = $testResults.Keys.Count

    Write-StructuredLog "Quick tests completed: $passedTests/$totalTests passed" -Level "INFO" -Data $testResults

    return $testResults
}

function Run-FullTests {
    Write-StructuredLog "Running full test suite..." -Level "INFO"

    # Run quick tests first
    $quickResults = Run-QuickTests

    # Add Redis test
    $quickResults.redisConnection = Test-RedisConnection

    # Run Python test suite if available
    if (Test-Path "test_eq12_comprehensive_platform.py") {
        Write-StructuredLog "Running Python test suite..." -Level "INFO"

        try {
            $pytestResult = python -m pytest test_eq12_comprehensive_platform.py -v --tb=short 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-StructuredLog "Python test suite PASSED" -Level "SUCCESS"
                $quickResults.pytestSuite = $true
            }
            else {
                Write-StructuredLog "Python test suite FAILED: $pytestResult" -Level "ERROR"
                $quickResults.pytestSuite = $false
            }
        }
        catch {
            Write-StructuredLog "Python test suite execution failed" -Level "ERROR"
            $quickResults.pytestSuite = $false
        }
    }

    return $quickResults
}

function Show-DeploymentSummary {
    param([hashtable]$TestResults)

    Write-Host "`n" -NoNewline
    Write-Host "🎯 EQ12 DEPLOYMENT TEST SUMMARY" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan

    $passed = 0
    $failed = 0

    foreach ($test in $TestResults.GetEnumerator()) {
        $status = if ($test.Value) { "✅ PASS" } else { "❌ FAIL" }
        $color = if ($test.Value) { "Green" } else { "Red" }

        Write-Host "$($test.Key): $status" -ForegroundColor $color

        if ($test.Value) { $passed++ } else { $failed++ }
    }

    Write-Host "`n" -NoNewline
    Write-Host "OVERALL: $passed PASSED, $failed FAILED" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })

    if ($failed -eq 0) {
        Write-Host "`n🚀 PLATFORM READY FOR DEPLOYMENT!" -ForegroundColor Green
        Write-Host "📋 Next Steps:" -ForegroundColor Cyan
        Write-Host "   1. Configure missing environment variables (if any)" -ForegroundColor White
        Write-Host "   2. Run: .\EQ12_LLM_Platform_Launcher.ps1 -Action install -Environment development" -ForegroundColor White
        Write-Host "   3. Run: .\EQ12_LLM_Platform_Launcher.ps1 -Action start -Environment development" -ForegroundColor White
        Write-Host "   4. Access dashboard: http://localhost:3000/dashboard" -ForegroundColor White
    }
    else {
        Write-Host "`n⚠️  DEPLOYMENT ISSUES DETECTED" -ForegroundColor Yellow
        Write-Host "🔍 Fix the failed tests above before deploying" -ForegroundColor Yellow
        Write-Host "📋 Common fixes:" -ForegroundColor Cyan
        Write-Host "   - Install missing dependencies" -ForegroundColor White
        Write-Host "   - Fix syntax errors" -ForegroundColor White
        Write-Host "   - Install Redis if needed" -ForegroundColor White
        Write-Host "   - Set environment variables" -ForegroundColor White
    }
}

function Show-JobPostingInfo {
    Write-Host "`n" -NoNewline
    Write-Host "💼 JOB POSTING COPY BLOCKS READY" -ForegroundColor Magenta
    Write-Host "=" * 50 -ForegroundColor Magenta

    if (Test-Path "EQ12_LLM_Platform_Job_Postings.md") {
        Write-Host "✅ Job posting templates available in EQ12_LLM_Platform_Job_Postings.md" -ForegroundColor Green
        Write-Host "📋 Includes:" -ForegroundColor Cyan
        Write-Host "   - LLM Platform Engineer positions" -ForegroundColor White
        Write-Host "   - OpenAI v2.x, GPT-5, fallback routing focus" -ForegroundColor White
        Write-Host "   - Multiple platform variations (LinkedIn, Indeed, etc.)" -ForegroundColor White
        Write-Host "   - Complete hiring funnel materials" -ForegroundColor White
        Write-Host "   - Salary ranges and technical requirements" -ForegroundColor White
    }
    else {
        Write-Host "❌ Job posting file not found" -ForegroundColor Red
    }
}

# Main execution
try {
    Write-Host "🧪 EQ12 DEPLOYMENT TEST SUITE" -ForegroundColor Cyan
    Write-Host "Test Type: $TestType" -ForegroundColor White
    Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
    Write-Host ""

    Write-StructuredLog "Starting deployment test suite" -Level "INFO" -Data @{
        testType         = $TestType
        skipDependencies = $SkipDependencies.IsPresent
        verbose          = $Verbose.IsPresent
    }

    $testResults = switch ($TestType) {
        "quick" { Run-QuickTests }
        "full" { Run-FullTests }
        "security" {
            Write-StructuredLog "Security tests not yet implemented" -Level "WARN"
            Run-QuickTests  # Fall back to quick tests
        }
        "performance" {
            Write-StructuredLog "Performance tests not yet implemented" -Level "WARN"
            Run-QuickTests  # Fall back to quick tests
        }
        default { Run-QuickTests }
    }

    Show-DeploymentSummary -TestResults $testResults
    Show-JobPostingInfo

    Write-StructuredLog "Deployment test suite completed" -Level "SUCCESS" -Data $testResults

    # Set exit code based on results
    $failedTests = ($testResults.Values | Where-Object { $_ -eq $false }).Count
    exit $failedTests

}
catch {
    Write-StructuredLog "Deployment test suite failed: $($_.Exception.Message)" -Level "ERROR"
    Write-Host "❌ CRITICAL ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
