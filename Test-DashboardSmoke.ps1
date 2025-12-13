# EQ12 Post-Upgrade Smoke Tests - PowerShell Dashboard Tests
# Copy-paste this block to validate dashboard functionality

Write-Host "=== EQ12 Dashboard Smoke Tests ===" -ForegroundColor Green

# 1. Health endpoint test
Write-Host "`n1. Testing /health endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest http://localhost:3000/health -UseBasicParsing -TimeoutSec 5
    if ($health.StatusCode -eq 200) {
        Write-Host "   ✅ Health: HTTP $($health.StatusCode)" -ForegroundColor Green
        $healthData = $health.Content | ConvertFrom-Json
        Write-Host "   Service: $($healthData.service)" -ForegroundColor Gray
        Write-Host "   Uptime: $($healthData.uptime) seconds" -ForegroundColor Gray
    }
    else {
        Write-Host "   ❌ Health: HTTP $($health.StatusCode)" -ForegroundColor Red
    }
}
catch {
    Write-Host "   ❌ Health: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Root redirect test (expect 302)
Write-Host "`n2. Testing root redirect..." -ForegroundColor Yellow
try {
    $redirect = Invoke-WebRequest http://localhost:3000/ -MaximumRedirection 0 -ErrorAction SilentlyContinue
    Write-Host "   ⚠️ Root: HTTP $($redirect.StatusCode) (expected 302)" -ForegroundColor Yellow
}
catch {
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode.value__ -eq 302) {
        $location = $_.Exception.Response.Headers.Location
        Write-Host "   ✅ Root redirect: HTTP 302 → $location" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ Root: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 3. Dashboard endpoint test
Write-Host "`n3. Testing /dashboard endpoint..." -ForegroundColor Yellow
try {
    $dashboard = Invoke-WebRequest http://localhost:3000/dashboard -UseBasicParsing -TimeoutSec 5
    if ($dashboard.StatusCode -eq 200) {
        Write-Host "   ✅ Dashboard: HTTP $($dashboard.StatusCode)" -ForegroundColor Green
        $contentLength = $dashboard.RawContentLength
        Write-Host "   Content: $contentLength bytes" -ForegroundColor Gray
    }
    else {
        Write-Host "   ❌ Dashboard: HTTP $($dashboard.StatusCode)" -ForegroundColor Red
    }
}
catch {
    Write-Host "   ❌ Dashboard: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. API health endpoint (legacy support)
Write-Host "`n4. Testing /api/health endpoint..." -ForegroundColor Yellow
try {
    $apiHealth = Invoke-WebRequest http://localhost:3000/api/health -UseBasicParsing -TimeoutSec 5
    if ($apiHealth.StatusCode -eq 200) {
        Write-Host "   ✅ API Health: HTTP $($apiHealth.StatusCode)" -ForegroundColor Green
        $apiData = $apiHealth.Content | ConvertFrom-Json
        Write-Host "   Status: $($apiData.status)" -ForegroundColor Gray
    }
    else {
        Write-Host "   ❌ API Health: HTTP $($apiHealth.StatusCode)" -ForegroundColor Red
    }
}
catch {
    Write-Host "   ❌ API Health: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. 404 handling test
Write-Host "`n5. Testing 404 error handling..." -ForegroundColor Yellow
try {
    $notFound = Invoke-WebRequest http://localhost:3000/nonexistent -UseBasicParsing -ErrorAction Stop
    Write-Host "   ⚠️ 404 Test: HTTP $($notFound.StatusCode) (expected 404)" -ForegroundColor Yellow
}
catch {
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode.value__ -eq 404) {
        Write-Host "   ✅ 404 Handling: HTTP 404 (correct)" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ 404 Test: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n=== Dashboard Tests Complete ===" -ForegroundColor Green
Write-Host "🌐 Access dashboard at: http://localhost:3000/" -ForegroundColor Cyan
