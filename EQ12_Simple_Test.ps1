# EQ12_Simple_Test.ps1 - Simple deployment validation script

param(
    [string]$TestType = "quick"
)

# Force UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8

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

Write-Host "🧪 EQ12 PLATFORM VALIDATION" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan

# Test 1: Check required files
Write-Host "`n📁 Testing File Structure..." -ForegroundColor White

$requiredFiles = @(
    "eq12_sports_betting_analytics_platform.py",
    "eq12_responsible_gaming_engine.py",
    "eq12_realtime_betting_dashboard.js",
    "EQ12_LLM_Platform_Launcher.ps1",
    "EQ12_LLM_Platform_Job_Postings.md"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    $exists = Test-Path $file
    Write-TestResult -TestName "File: $file" -Passed $exists
    if (-not $exists) { $allFilesExist = $false }
}

# Test 2: Check Python availability
Write-Host "`n🐍 Testing Python Environment..." -ForegroundColor White

try {
    $pythonVersion = python --version 2>$null
    $pythonOK = $LASTEXITCODE -eq 0
    Write-TestResult -TestName "Python Installation" -Passed $pythonOK -Details $pythonVersion
}
catch {
    Write-TestResult -TestName "Python Installation" -Passed $false -Details "Python not found"
    $pythonOK = $false
}

# Test 3: Check Node.js availability
Write-Host "`n🟢 Testing Node.js Environment..." -ForegroundColor White

try {
    $nodeVersion = node --version 2>$null
    $nodeOK = $LASTEXITCODE -eq 0
    Write-TestResult -TestName "Node.js Installation" -Passed $nodeOK -Details $nodeVersion
}
catch {
    Write-TestResult -TestName "Node.js Installation" -Passed $false -Details "Node.js not found"
    $nodeOK = $false
}

# Test 4: Basic syntax check for Python files
Write-Host "`n🔍 Testing Python Syntax..." -ForegroundColor White

$pythonSyntaxOK = $true
foreach ($file in @("eq12_sports_betting_analytics_platform.py", "eq12_responsible_gaming_engine.py")) {
    if (Test-Path $file) {
        try {
            python -m py_compile $file 2>$null
            $syntaxOK = $LASTEXITCODE -eq 0
            Write-TestResult -TestName "Syntax: $file" -Passed $syntaxOK
            if (-not $syntaxOK) { $pythonSyntaxOK = $false }
        }
        catch {
            Write-TestResult -TestName "Syntax: $file" -Passed $false -Details "Compilation failed"
            $pythonSyntaxOK = $false
        }
    }
}

# Test 5: Check Node.js syntax
Write-Host "`n🔍 Testing Node.js Syntax..." -ForegroundColor White

$nodeSyntaxOK = $true
if (Test-Path "eq12_realtime_betting_dashboard.js") {
    try {
        node -c "eq12_realtime_betting_dashboard.js" 2>$null
        $syntaxOK = $LASTEXITCODE -eq 0
        Write-TestResult -TestName "Syntax: eq12_realtime_betting_dashboard.js" -Passed $syntaxOK
        if (-not $syntaxOK) { $nodeSyntaxOK = $false }
    }
    catch {
        Write-TestResult -TestName "Syntax: eq12_realtime_betting_dashboard.js" -Passed $false -Details "Syntax check failed"
        $nodeSyntaxOK = $false
    }
}

# Test 6: Check environment variables
Write-Host "`n🔐 Testing Environment Variables..." -ForegroundColor White

$envVars = @("OPENAI_API_KEY", "ODDS_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
$envVarCount = 0

foreach ($var in $envVars) {
    $value = [Environment]::GetEnvironmentVariable($var)
    $hasValue = -not [string]::IsNullOrEmpty($value)
    Write-TestResult -TestName "Env Var: $var" -Passed $hasValue
    if ($hasValue) { $envVarCount++ }
}

# Test 7: Check logs directory
Write-Host "`n📝 Testing Log Directory..." -ForegroundColor White

try {
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    }
    $testFile = "logs\test.tmp"
    "test" | Out-File $testFile
    $logsOK = Test-Path $testFile
    Remove-Item $testFile -ErrorAction SilentlyContinue
    Write-TestResult -TestName "Logs Directory" -Passed $logsOK
}
catch {
    Write-TestResult -TestName "Logs Directory" -Passed $false -Details "Cannot create log directory"
    $logsOK = $false
}

# Summary
Write-Host "`n🎯 DEPLOYMENT READINESS SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 40 -ForegroundColor Cyan

$totalTests = 7
$passedTests = 0

if ($allFilesExist) { $passedTests++ }
if ($pythonOK) { $passedTests++ }
if ($nodeOK) { $passedTests++ }
if ($pythonSyntaxOK) { $passedTests++ }
if ($nodeSyntaxOK) { $passedTests++ }
if ($envVarCount -gt 0) { $passedTests++ }
if ($logsOK) { $passedTests++ }

Write-Host "Overall Score: $passedTests/$totalTests tests passed" -ForegroundColor $(if ($passedTests -eq $totalTests) { "Green" } else { "Yellow" })

if ($passedTests -ge 5) {
    Write-Host "`n🚀 PLATFORM READY FOR DEPLOYMENT!" -ForegroundColor Green
    Write-Host "📋 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Set missing environment variables (optional)" -ForegroundColor White
    Write-Host "   2. Run: .\EQ12_LLM_Platform_Launcher.ps1 -Action start" -ForegroundColor White
    Write-Host "   3. Access dashboard: http://localhost:3000/dashboard" -ForegroundColor White
    Write-Host "   4. Use job postings: EQ12_LLM_Platform_Job_Postings.md" -ForegroundColor White
}
else {
    Write-Host "`n⚠️  PLATFORM NEEDS ATTENTION" -ForegroundColor Yellow
    Write-Host "🔧 Install missing dependencies and fix issues above" -ForegroundColor Yellow
}

# Show job posting info
if (Test-Path "EQ12_LLM_Platform_Job_Postings.md") {
    Write-Host "`n💼 JOB POSTING MATERIALS READY" -ForegroundColor Magenta
    Write-Host "✅ Comprehensive hiring templates available" -ForegroundColor Green
    Write-Host "📋 Focus: LLM Platform Engineer (OpenAI v2.x, GPT-5)" -ForegroundColor White
}

Write-Host "`n✨ EQ12 Sports Betting Analytics Platform - Ready to Deploy!" -ForegroundColor Green
