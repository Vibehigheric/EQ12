# EQ12 GODSTACK Preview Environment Testing Guide

## 🎯 Overview

This guide provides comprehensive testing procedures for the EQ12 GODSTACK preview environment, including ngrok tunneling, service validation, and business stack compliance verification.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- ngrok CLI installed and configured
- PowerShell 5.1+ (Windows) or PowerShell Core (cross-platform)
- Git with signed commit capability

### Initial Setup
```powershell
# 1. Navigate to EQ12 directory
cd C:\EQ12

# 2. Start preview environment
docker-compose -f docker-compose.preview.yml up -d

# 3. Initialize ngrok tunnels
.\eq12_ngrok_manager.ps1 -Action Start -Environment preview

# 4. Verify all services
.\eq12_ngrok_manager.ps1 -Action Status
```

## 🧪 Testing Procedures

### 1. Core Service Testing

#### Dashboard Testing
```powershell
# Test dashboard accessibility
$dashboardUrl = "https://eq12-pr-123-dash.ngrok-free.app"
$credentials = @{
    Username = "preview"
    Password = "eq12preview123"
}

# Basic connectivity test
Invoke-WebRequest -Uri "$dashboardUrl/health" -Credential $credentials

# UI functionality test
Start-Process $dashboardUrl
```

#### API Testing
```powershell
# Test API endpoints
$apiUrl = "https://eq12-pr-123-api.ngrok-free.app"
$headers = @{
    "Authorization" = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("preview:eq12preview123"))
    "Content-Type" = "application/json"
}

# Health check
Invoke-RestMethod -Uri "$apiUrl/health" -Headers $headers

# Test core endpoints
$endpoints = @("/health", "/api/v1/status", "/api/v1/config", "/metrics")
foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-RestMethod -Uri "$apiUrl$endpoint" -Headers $headers
        Write-Host "✅ $endpoint - OK" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $endpoint - Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}
```

#### Webhook Testing
```powershell
# Test webhook endpoint
$webhookUrl = "https://eq12-pr-123-hook.ngrok-free.app"

# Send test payload
$testPayload = @{
    event = "test"
    timestamp = Get-Date -Format "o"
    data = @{
        test_id = [System.Guid]::NewGuid().ToString()
        environment = "preview"
    }
} | ConvertTo-Json

Invoke-RestMethod -Uri "$webhookUrl/webhook" -Method Post -Body $testPayload -ContentType "application/json"
```

### 2. Security Testing

#### HTTPS Enforcement
```powershell
function Test-HttpsRedirect {
    param([string]$Url)
    
    $httpUrl = $Url -replace "https://", "http://"
    try {
        $response = Invoke-WebRequest -Uri $httpUrl -MaximumRedirection 0 -ErrorAction Stop
        if ($response.StatusCode -in @(301, 302)) {
            Write-Host "✅ HTTPS redirect working for $Url" -ForegroundColor Green
            return $true
        }
    }
    catch {
        if ($_.Exception.Response.StatusCode -in @("MovedPermanently", "Found")) {
            Write-Host "✅ HTTPS redirect working for $Url" -ForegroundColor Green
            return $true
        }
    }
    
    Write-Host "❌ HTTPS redirect not working for $Url" -ForegroundColor Red
    return $false
}

# Test all preview URLs
Test-HttpsRedirect $dashboardUrl
Test-HttpsRedirect $apiUrl
Test-HttpsRedirect $webhookUrl
```

#### Authentication Testing
```powershell
function Test-Authentication {
    param([string]$Url)
    
    # Test without credentials
    try {
        Invoke-WebRequest -Uri $Url -ErrorAction Stop
        Write-Host "❌ $Url - No authentication required" -ForegroundColor Red
        return $false
    }
    catch {
        if ($_.Exception.Response.StatusCode -eq "Unauthorized") {
            Write-Host "✅ $Url - Authentication required" -ForegroundColor Green
            return $true
        }
    }
    
    Write-Host "⚠️ $Url - Unexpected response" -ForegroundColor Yellow
    return $false
}

# Test authentication on all services
Test-Authentication $dashboardUrl
Test-Authentication $apiUrl
# Note: Webhook might not require auth for POST requests
```

#### Security Headers Testing
```powershell
function Test-SecurityHeaders {
    param([string]$Url)
    
    $requiredHeaders = @(
        "X-Frame-Options",
        "X-Content-Type-Options",
        "Strict-Transport-Security"
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Credential $credentials
        $missing = @()
        
        foreach ($header in $requiredHeaders) {
            if (-not $response.Headers[$header]) {
                $missing += $header
            }
        }
        
        if ($missing.Count -eq 0) {
            Write-Host "✅ $Url - All security headers present" -ForegroundColor Green
            return $true
        } else {
            Write-Host "⚠️ $Url - Missing headers: $($missing -join ', ')" -ForegroundColor Yellow
            return $false
        }
    }
    catch {
        Write-Host "❌ $Url - Could not check headers: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test security headers
Test-SecurityHeaders $dashboardUrl
Test-SecurityHeaders $apiUrl
```

### 3. Performance Testing

#### Load Testing
```powershell
function Test-LoadPerformance {
    param(
        [string]$Url,
        [int]$Requests = 10,
        [int]$Concurrent = 2
    )
    
    Write-Host "🔄 Running load test on $Url ($Requests requests, $Concurrent concurrent)"
    
    $jobs = @()
    $times = @()
    
    for ($i = 0; $i -lt $Concurrent; $i++) {
        $job = Start-Job -ScriptBlock {
            param($Url, $RequestsPerJob, $Credentials)
            
            $results = @()
            for ($j = 0; $j -lt $RequestsPerJob; $j++) {
                $start = Get-Date
                try {
                    Invoke-WebRequest -Uri $Url -Credential $Credentials -TimeoutSec 30
                    $duration = (Get-Date) - $start
                    $results += @{
                        Success = $true
                        Duration = $duration.TotalMilliseconds
                    }
                }
                catch {
                    $duration = (Get-Date) - $start
                    $results += @{
                        Success = $false
                        Duration = $duration.TotalMilliseconds
                        Error = $_.Exception.Message
                    }
                }
            }
            return $results
        } -ArgumentList $Url, [math]::Ceiling($Requests / $Concurrent), $credentials
        
        $jobs += $job
    }
    
    # Wait for all jobs to complete
    $allResults = $jobs | ForEach-Object { 
        Receive-Job $_ -Wait
        Remove-Job $_
    }
    
    # Analyze results
    $successful = ($allResults | Where-Object { $_.Success }).Count
    $failed = ($allResults | Where-Object { -not $_.Success }).Count
    $avgTime = ($allResults | Measure-Object Duration -Average).Average
    $maxTime = ($allResults | Measure-Object Duration -Maximum).Maximum
    
    Write-Host "📊 Load Test Results for $Url:"
    Write-Host "   ✅ Successful: $successful"
    Write-Host "   ❌ Failed: $failed"
    Write-Host "   ⏱️ Average Response Time: $([math]::Round($avgTime, 2))ms"
    Write-Host "   ⏱️ Max Response Time: $([math]::Round($maxTime, 2))ms"
    
    return @{
        Successful = $successful
        Failed = $failed
        AverageTime = $avgTime
        MaxTime = $maxTime
    }
}

# Run load tests on key endpoints
$dashboardResults = Test-LoadPerformance "$dashboardUrl/health" -Requests 20 -Concurrent 3
$apiResults = Test-LoadPerformance "$apiUrl/health" -Requests 20 -Concurrent 3
```

### 4. Business Stack Testing

#### Mock Stack Services Testing
```powershell
function Test-BusinessStack {
    param([string]$Stack)
    
    $stackUrls = @{
        "betting" = "https://eq12-pr-123-betting.ngrok-free.app"
        "cannabis" = "https://eq12-pr-123-cannabis.ngrok-free.app"
        "credit" = "https://eq12-pr-123-credit.ngrok-free.app"
        "analytics" = "https://eq12-pr-123-analytics.ngrok-free.app"
    }
    
    $url = $stackUrls[$Stack]
    if (-not $url) {
        Write-Host "❌ Unknown stack: $Stack" -ForegroundColor Red
        return $false
    }
    
    Write-Host "🧪 Testing $Stack stack at $url"
    
    try {
        # Test health endpoint
        $response = Invoke-RestMethod -Uri "$url/health" -Headers $headers
        
        # Verify mock mode
        if ($response.mode -eq "mock" -and $response.environment -eq "preview") {
            Write-Host "✅ $Stack stack - Mock mode confirmed" -ForegroundColor Green
            
            # Test stack-specific endpoints
            switch ($Stack) {
                "betting" {
                    $odds = Invoke-RestMethod -Uri "$url/api/odds" -Headers $headers
                    Write-Host "✅ Betting - Mock odds data retrieved" -ForegroundColor Green
                }
                "cannabis" {
                    $products = Invoke-RestMethod -Uri "$url/api/products" -Headers $headers
                    Write-Host "✅ Cannabis - Mock product data retrieved" -ForegroundColor Green
                }
                "credit" {
                    $scores = Invoke-RestMethod -Uri "$url/api/scores" -Headers $headers
                    Write-Host "✅ Credit - Mock score data retrieved" -ForegroundColor Green
                }
                "analytics" {
                    $metrics = Invoke-RestMethod -Uri "$url/api/metrics" -Headers $headers
                    Write-Host "✅ Analytics - Mock metrics retrieved" -ForegroundColor Green
                }
            }
            
            return $true
        }
        else {
            Write-Host "❌ $Stack stack - Not in proper mock mode" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "❌ $Stack stack - Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test all business stacks (if enabled)
$stacks = @("betting", "cannabis", "credit", "analytics")
foreach ($stack in $stacks) {
    Test-BusinessStack $stack
}
```

### 5. Integration Testing

#### End-to-End Workflow Testing
```powershell
function Test-E2EWorkflow {
    Write-Host "🔄 Running end-to-end workflow test"
    
    # 1. Dashboard → API communication
    try {
        $configResponse = Invoke-RestMethod -Uri "$apiUrl/api/v1/config" -Headers $headers
        Write-Host "✅ Dashboard can fetch API config" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Dashboard → API communication failed" -ForegroundColor Red
        return $false
    }
    
    # 2. API → Webhook communication
    try {
        $webhookTest = @{
            source = "api_test"
            timestamp = Get-Date -Format "o"
            test_data = "integration_test"
        } | ConvertTo-Json
        
        Invoke-RestMethod -Uri "$apiUrl/api/v1/webhook/test" -Method Post -Body $webhookTest -Headers $headers
        Write-Host "✅ API can send webhook notifications" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ API → Webhook communication failed" -ForegroundColor Red
        return $false
    }
    
    # 3. Webhook → API callback
    try {
        $callbackTest = @{
            callback_url = "$apiUrl/api/v1/webhook/callback"
            test_id = [System.Guid]::NewGuid().ToString()
        } | ConvertTo-Json
        
        Invoke-RestMethod -Uri "$webhookUrl/webhook/callback" -Method Post -Body $callbackTest -ContentType "application/json"
        Write-Host "✅ Webhook can call back to API" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Webhook → API callback failed" -ForegroundColor Red
        return $false
    }
    
    Write-Host "🎉 End-to-end workflow test completed successfully" -ForegroundColor Green
    return $true
}

Test-E2EWorkflow
```

## 📊 Test Report Generation

### Automated Test Report
```powershell
function Generate-TestReport {
    param([string]$OutputPath = "C:\EQ12\logs\preview_test_report.json")
    
    $report = @{
        timestamp = Get-Date -Format "o"
        environment = "preview"
        pr_number = $env:GITHUB_PR_NUMBER
        tests = @{
            connectivity = @()
            security = @()
            performance = @()
            integration = @()
        }
    }
    
    # Run all tests and collect results
    Write-Host "📋 Generating comprehensive test report..."
    
    # Add connectivity tests
    $urls = @($dashboardUrl, $apiUrl, $webhookUrl)
    foreach ($url in $urls) {
        try {
            $start = Get-Date
            $response = Invoke-WebRequest -Uri "$url/health" -Credential $credentials
            $duration = (Get-Date) - $start
            
            $report.tests.connectivity += @{
                url = $url
                status = "pass"
                response_time_ms = $duration.TotalMilliseconds
                status_code = $response.StatusCode
            }
        }
        catch {
            $report.tests.connectivity += @{
                url = $url
                status = "fail"
                error = $_.Exception.Message
            }
        }
    }
    
    # Add security test results
    foreach ($url in $urls) {
        $httpsResult = Test-HttpsRedirect $url
        $authResult = Test-Authentication $url
        $headersResult = Test-SecurityHeaders $url
        
        $report.tests.security += @{
            url = $url
            https_redirect = $httpsResult
            authentication_required = $authResult
            security_headers = $headersResult
        }
    }
    
    # Add performance test results
    $perfResults = Test-LoadPerformance "$dashboardUrl/health" -Requests 10 -Concurrent 2
    $report.tests.performance += @{
        service = "dashboard"
        successful_requests = $perfResults.Successful
        failed_requests = $perfResults.Failed
        average_response_time_ms = $perfResults.AverageTime
        max_response_time_ms = $perfResults.MaxTime
    }
    
    # Add integration test results
    $e2eResult = Test-E2EWorkflow
    $report.tests.integration += @{
        end_to_end_workflow = $e2eResult
        timestamp = Get-Date -Format "o"
    }
    
    # Calculate overall status
    $allConnectivityPassed = ($report.tests.connectivity | Where-Object { $_.status -eq "fail" }).Count -eq 0
    $allSecurityPassed = $report.tests.security | ForEach-Object { $_.https_redirect -and $_.authentication_required -and $_.security_headers } | Where-Object { $_ -eq $false } | Measure-Object | Select-Object -ExpandProperty Count
    $performanceAcceptable = $report.tests.performance[0].average_response_time_ms -lt 2000
    
    $report.overall_status = if ($allConnectivityPassed -and ($allSecurityPassed -eq 0) -and $performanceAcceptable -and $e2eResult) { "pass" } else { "fail" }
    
    # Save report
    $report | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8
    
    Write-Host "📄 Test report saved to: $OutputPath" -ForegroundColor Green
    Write-Host "📊 Overall Status: $($report.overall_status.ToUpper())" -ForegroundColor $(if ($report.overall_status -eq "pass") { "Green" } else { "Red" })
    
    return $report
}

# Generate final test report
$testReport = Generate-TestReport
```

## 🧹 Cleanup Procedures

### Manual Cleanup
```powershell
# Stop ngrok tunnels
.\eq12_ngrok_manager.ps1 -Action Stop

# Stop Docker services
docker-compose -f docker-compose.preview.yml down --remove-orphans

# Clean up volumes (optional)
docker volume prune -f

# Clean up networks (optional)  
docker network prune -f
```

### Automated Cleanup (scheduled)
```powershell
# Set up scheduled cleanup task
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\EQ12\eq12_ngrok_manager.ps1 -Action Cleanup -Environment preview"
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00AM"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

Register-ScheduledTask -TaskName "EQ12-Preview-Cleanup" -Action $action -Trigger $trigger -Settings $settings -Principal $principal
```

## 📚 Troubleshooting

### Common Issues

#### 1. Ngrok Tunnel Not Starting
```powershell
# Check ngrok installation
ngrok version

# Check authentication
ngrok authtoken --log=stdout

# Test basic tunnel
ngrok http 8000 --log=stdout
```

#### 2. Docker Services Not Starting
```powershell
# Check Docker status
docker system info

# Check service logs
docker-compose -f docker-compose.preview.yml logs

# Rebuild services
docker-compose -f docker-compose.preview.yml build --no-cache
```

#### 3. Authentication Issues
```powershell
# Test credentials manually
$creds = Get-Credential -UserName "preview"
Invoke-WebRequest -Uri $dashboardUrl -Credential $creds
```

#### 4. Performance Issues
```powershell
# Check system resources
Get-Process | Where-Object {$_.ProcessName -like "*docker*" -or $_.ProcessName -like "*ngrok*"} | Select-Object Name, CPU, WorkingSet

# Check Docker stats
docker stats --no-stream
```

## 🎯 Success Criteria

A successful preview environment test should meet these criteria:

### ✅ Connectivity
- All services respond to health checks within 5 seconds
- All ngrok tunnels are accessible via HTTPS
- Inter-service communication works properly

### ✅ Security
- HTTPS enforcement is working (HTTP redirects to HTTPS)
- Authentication is required for protected endpoints
- Security headers are present and properly configured
- No sensitive production data is exposed

### ✅ Performance
- Average response time < 2 seconds under normal load
- Can handle at least 10 concurrent requests without errors
- Memory usage stays under reasonable limits

### ✅ Functionality
- Dashboard UI loads and displays mock data
- API endpoints return expected responses
- Webhook receives and processes test payloads
- End-to-end workflows complete successfully

### ✅ Business Stack Compliance
- Mock mode is enabled for all business stack services
- No real business stack data is processed
- Business stack services respond with test data only
- Compliance controls prevent real data exposure

---

*This testing guide ensures comprehensive validation of the EQ12 GODSTACK preview environment while maintaining security and compliance standards.*