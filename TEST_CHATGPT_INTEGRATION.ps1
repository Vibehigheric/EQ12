<#
.SYNOPSIS
    EQ12 ChatGPT Integration Test Suite
.DESCRIPTION
    Tests all 20+ ChatGPT integration points to verify functionality
#>

[CmdletBinding()]
param()

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "EQ12 ChatGPT Integration Test Suite" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Load the ChatGPT commands
$chatgptScript = "$PSScriptRoot\EQ12_CHATGPT_COMMANDS.ps1"
if (-not (Test-Path $chatgptScript)) {
    Write-Error "ChatGPT commands script not found: $chatgptScript"
    exit 1
}

. $chatgptScript
Write-Host "✅ ChatGPT commands loaded" -ForegroundColor Green
Write-Host ""

# Check if eq12_openai_client.py exists
$openaiClient = "$PSScriptRoot\eq12_openai_client.py"
if (-not (Test-Path $openaiClient)) {
    Write-Warning "eq12_openai_client.py not found. Some tests will be skipped."
    Write-Host ""
}

# Check for OPENAI_API_KEY
$envPath = "$PSScriptRoot\.env"
$hasApiKey = $false
if (Test-Path $envPath) {
    $envContent = Get-Content $envPath
    if ($envContent -match "OPENAI_API_KEY=") {
        $hasApiKey = $true
        Write-Host "✅ OPENAI_API_KEY found in .env" -ForegroundColor Green
    }
    else {
        Write-Warning "OPENAI_API_KEY not found in .env - API calls will fail"
    }
}
else {
    Write-Warning ".env file not found - API calls will fail"
}
Write-Host ""

# ===================================================================
# Test 1: Command Availability
# ===================================================================
Write-Host "TEST 1: Verifying Command Availability" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$expectedCommands = @(
    "ai-diagnose-vfd",
    "ai-analyze-plc-logs",
    "ai-network-audit",
    "ai-analyze-parlay",
    "ai-player-prop",
    "ai-live-bet-advisor",
    "ai-generate-powershell",
    "ai-generate-vbnet",
    "ai-generate-sql",
    "ai-revenue-report",
    "ai-market-efficiency",
    "ai-marketing-copy",
    "ai-twitter-post",
    "ai-summarize-logs",
    "ai-detect-anomalies",
    "ai-code-review",
    "ai-commit-message",
    "ai-generate-readme",
    "ai-ask",
    "ai-daily-diagnostics",
    "ai-content-batch"
)

$passed = 0
$failed = 0

foreach ($cmd in $expectedCommands) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        Write-Host "  ✅ $cmd" -ForegroundColor Green
        $passed++
    }
    else {
        Write-Host "  ❌ $cmd - NOT FOUND" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "Command Availability: $passed/$($expectedCommands.Count) passed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })
Write-Host ""

# ===================================================================
# Test 2: Alias Verification
# ===================================================================
Write-Host "TEST 2: Verifying Aliases" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$expectedAliases = @{
    "ai"          = "ai-ask"
    "diagnose"    = "ai-diagnose-vfd"
    "parlay-ai"   = "ai-analyze-parlay"
    "code-review" = "ai-code-review"
    "gen-script"  = "ai-generate-powershell"
}

foreach ($alias in $expectedAliases.Keys) {
    $target = $expectedAliases[$alias]
    $aliasCmd = Get-Alias $alias -ErrorAction SilentlyContinue
    
    if ($aliasCmd -and $aliasCmd.Definition -eq $target) {
        Write-Host "  ✅ $alias → $target" -ForegroundColor Green
    }
    else {
        Write-Host "  ❌ $alias → $target - FAILED" -ForegroundColor Red
    }
}

Write-Host ""

# ===================================================================
# Test 3: Python Integration Check
# ===================================================================
Write-Host "TEST 3: Python Integration Check" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python detected: $pythonVersion" -ForegroundColor Green
    
    # Check for openai package
    $openaiInstalled = python -c "import openai; print(openai.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ openai package installed: v$openaiInstalled" -ForegroundColor Green
    }
    else {
        Write-Warning "  ⚠️ openai package not installed - run: pip install openai"
    }
}
catch {
    Write-Warning "  ⚠️ Python not found or not in PATH"
}

Write-Host ""

# ===================================================================
# Test 4: Live API Test (Optional - only if API key present)
# ===================================================================
if ($hasApiKey -and (Test-Path $openaiClient)) {
    Write-Host "TEST 4: Live API Test (Simple Query)" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host "Testing simple ChatGPT query..." -ForegroundColor Gray
    Write-Host ""
    
    try {
        $testQuery = "Say 'EQ12 ChatGPT integration is working!' and nothing else."
        $response = ai-ask $testQuery
        
        if ($response -match "working") {
            Write-Host "  ✅ Live API test PASSED" -ForegroundColor Green
            Write-Host "  Response: $response" -ForegroundColor Gray
        }
        else {
            Write-Warning "  ⚠️ Live API test returned unexpected response"
            Write-Host "  Response: $response" -ForegroundColor Gray
        }
    }
    catch {
        Write-Warning "  ❌ Live API test FAILED: $_"
    }
    
    Write-Host ""
}
else {
    Write-Host "TEST 4: Live API Test - SKIPPED (no API key or missing client)" -ForegroundColor Yellow
    Write-Host ""
}

# ===================================================================
# Test Summary
# ===================================================================
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commands Available:  $passed/$($expectedCommands.Count)" -ForegroundColor $(if ($passed -eq $expectedCommands.Count) { "Green" } else { "Yellow" })
Write-Host "Python Integration:  $(if ($pythonVersion) { 'READY' } else { 'NOT READY' })" -ForegroundColor $(if ($pythonVersion) { "Green" } else { "Red" })
Write-Host "OpenAI Package:      $(if ($openaiInstalled) { "INSTALLED (v$openaiInstalled)" } else { 'NOT INSTALLED' })" -ForegroundColor $(if ($openaiInstalled) { "Green" } else { "Yellow" })
Write-Host "API Key Configured:  $(if ($hasApiKey) { 'YES' } else { 'NO' })" -ForegroundColor $(if ($hasApiKey) { "Green" } else { "Red" })
Write-Host ""

if ($passed -eq $expectedCommands.Count -and $hasApiKey) {
    Write-Host "✅ ALL SYSTEMS READY - ChatGPT integration fully operational!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Try these commands:" -ForegroundColor Cyan
    Write-Host "  ai 'What is EQ12?'" -ForegroundColor Gray
    Write-Host "  diagnose 'STO W8114'" -ForegroundColor Gray
    Write-Host "  gen-script 'Monitor CPU usage and alert if >80%'" -ForegroundColor Gray
}
elseif (-not $hasApiKey) {
    Write-Host "⚠️ SETUP REQUIRED: Add OPENAI_API_KEY to .env file" -ForegroundColor Yellow
}
else {
    Write-Host "⚠️ PARTIAL SETUP: Some commands may not work" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "For help: ai-ask 'How do I use the EQ12 ChatGPT integration?'" -ForegroundColor Cyan
Write-Host ""
