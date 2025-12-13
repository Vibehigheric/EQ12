# EQ12 Dashboard Status Check
# Quick verification that all endpoints are working properly

Write-Host "=== EQ12 DASHBOARD STATUS CHECK ===" -ForegroundColor Green
Write-Host "Checking all endpoints..." -ForegroundColor Yellow

$results = @()

# Test Health Endpoint
try {
    $health = Invoke-WebRequest http://localhost:3000/health -TimeoutSec 5
    $results += [PSCustomObject]@{
        Endpoint = "/health"
        Status   = $health.StatusCode
        Result   = "✓ PASS"
        Details  = "Health check working"
    }
}
catch {
    $results += [PSCustomObject]@{
        Endpoint = "/health"
        Status   = "ERROR"
        Result   = "✗ FAIL"
        Details  = $_.Exception.Message
    }
}

# Test API Health Endpoint
try {
    $apiHealth = Invoke-WebRequest http://localhost:3000/api/health -TimeoutSec 5
    $results += [PSCustomObject]@{
        Endpoint = "/api/health"
        Status   = $apiHealth.StatusCode
        Result   = "✓ PASS"
        Details  = "API health working"
    }
}
catch {
    $results += [PSCustomObject]@{
        Endpoint = "/api/health"
        Status   = "ERROR"
        Result   = "✗ FAIL"
        Details  = $_.Exception.Message
    }
}

# Test Root Redirect
try {
    $root = Invoke-WebRequest http://localhost:3000/ -TimeoutSec 5 -MaximumRedirection 0
    $results += [PSCustomObject]@{
        Endpoint = "/"
        Status   = $root.StatusCode
        Result   = "✗ UNEXPECTED"
        Details  = "Expected 302 redirect"
    }
}
catch {
    if ($_.Exception.Response.StatusCode -eq "Found") {
        $results += [PSCustomObject]@{
            Endpoint = "/"
            Status   = "302"
            Result   = "✓ PASS"
            Details  = "Properly redirects to /dashboard"
        }
    }
    else {
        $results += [PSCustomObject]@{
            Endpoint = "/"
            Status   = "ERROR"
            Result   = "✗ FAIL"
            Details  = $_.Exception.Message
        }
    }
}

# Test Dashboard
try {
    $dashboard = Invoke-WebRequest http://localhost:3000/dashboard -TimeoutSec 5
    $contentSize = [math]::Round($dashboard.Content.Length / 1024, 1)
    $results += [PSCustomObject]@{
        Endpoint = "/dashboard"
        Status   = $dashboard.StatusCode
        Result   = "✓ PASS"
        Details  = "Dashboard loaded (${contentSize}KB)"
    }
}
catch {
    $results += [PSCustomObject]@{
        Endpoint = "/dashboard"
        Status   = "ERROR"
        Result   = "✗ FAIL"
        Details  = $_.Exception.Message
    }
}

# Display Results
Write-Host ""
$results | Format-Table -AutoSize
Write-Host ""

# Summary
$passed = ($results | Where-Object { $_.Result -eq "✓ PASS" }).Count
$total = $results.Count
$allPassed = $passed -eq $total

if ($allPassed) {
    Write-Host "🎉 ALL TESTS PASSED ($passed/$total)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Dashboard is ready for use:" -ForegroundColor Green
    Write-Host "  • Main URL: http://localhost:3000/dashboard" -ForegroundColor White
    Write-Host "  • Health: http://localhost:3000/health" -ForegroundColor White
    Write-Host "  • Root redirects properly to dashboard" -ForegroundColor White
}
else {
    Write-Host "⚠️ SOME TESTS FAILED ($passed/$total)" -ForegroundColor Red
    Write-Host "Check the failed endpoints above" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Dashboard server process:" -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq "python" } | Format-Table Id, ProcessName, CPU -AutoSize
