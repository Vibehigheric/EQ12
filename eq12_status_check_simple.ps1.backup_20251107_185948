# EQ12 Enhanced Status Check - Simple Working Version
param([switch]$Json)

function Test-Endpoint {
    param([string]$Url, [int]$ExpectedCode = 200)
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 5 -MaximumRedirection 0 -ErrorAction SilentlyContinue
        @{ url = $Url; code = $response.StatusCode; ok = ($response.StatusCode -eq $ExpectedCode); note = "OK" }
    }
    catch {
        $code = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { 0 }
        @{ url = $Url; code = $code; ok = ($code -eq $ExpectedCode); note = $_.Exception.Message }
    }
}

$checks = @()
$port = 3000

# Check environment variables
$openaiKey = $env:OPENAI_API_KEY
$useLLM = $env:EQ12_USE_LLM
$checks += @{ name = "OPENAI_API_KEY"; ok = [bool]$openaiKey; detail = if ($openaiKey) { "Present" } else { "Missing" } }
$checks += @{ name = "EQ12_USE_LLM"; ok = ($useLLM -eq "1"); detail = "Value: $useLLM" }

# Check Node.js
$node = Get-Command node -ErrorAction SilentlyContinue
$checks += @{ name = "Node.js on PATH"; ok = [bool]$node; detail = if ($node) { $node.Source } else { "Not found" } }

# Check port listening
$tcp = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
$checks += @{ name = "Port $port listening"; ok = [bool]$tcp; detail = if ($tcp) { "PID: $($tcp[0].OwningProcess)" } else { "Not listening" } }

# Check endpoints
$healthTest = Test-Endpoint "http://localhost:$port/health" 200
$checks += @{ name = "Health endpoint"; ok = $healthTest.ok; detail = "HTTP $($healthTest.code)" }

$rootTest = Test-Endpoint "http://localhost:$port/" 302
$checks += @{ name = "Root redirect"; ok = $rootTest.ok; detail = "HTTP $($rootTest.code)" }

# Calculate score
$total = $checks.Count
$passed = ($checks | Where-Object { $_.ok }).Count
$percent = if ($total -gt 0) { [math]::Round(($passed / $total) * 100, 1) } else { 0 }

if ($Json) {
    @{
        timestamp   = (Get-Date).ToString('s')
        totalChecks = $total
        passed      = $passed
        percent     = $percent
        checks      = $checks
    } | ConvertTo-Json -Depth 3
    return
}

# Display results
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " EQ12 Enhanced Status Check" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

foreach ($check in $checks) {
    $status = if ($check.ok) { "[OK]" } else { "[FAIL]" }
    $color = if ($check.ok) { "Green" } else { "Red" }
    Write-Host "$status $($check.name) - $($check.detail)" -ForegroundColor $color
}

Write-Host "------------------------------------------------------------" -ForegroundColor DarkGray
Write-Host "Health Score: $passed/$total ($percent%)" -ForegroundColor Yellow

if ($passed -eq $total) {
    Write-Host "All systems operational!" -ForegroundColor Green
}
else {
    Write-Host "Some issues detected - check failed items above" -ForegroundColor Yellow
}
