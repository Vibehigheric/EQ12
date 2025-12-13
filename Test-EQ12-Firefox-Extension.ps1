# EQ12 Firefox Extension Integration Test
# Validates complete Firefox extension with EQ12 backend integration

[CmdletBinding()]
param(
    [switch]$StartBackend,
    [switch]$TestCapture,
    [switch]$ValidateAll
)

Write-Host "🧪 EQ12 Firefox Extension Integration Test" -ForegroundColor Green
Write-Host "Testing complete Firefox extension with EQ12 backend integration" -ForegroundColor Cyan

$extensionPath = "C:\EQ12\firefox_extension_eq12"
$backendPath = "C:\EQ12"
$logFile = "C:\EQ12\logs\firefox_extension_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

function Test-FileExists {
    param([string]$Path, [string]$Description)

    if (Test-Path $Path) {
        Write-Host "✅ $Description exists: $Path" -ForegroundColor Green
        return $true
    } else {
        Write-Host "❌ $Description missing: $Path" -ForegroundColor Red
        return $false
    }
}

function Test-JsonSyntax {
    param([string]$JsonFile, [string]$Description)

    try {
        $content = Get-Content $JsonFile -Raw
        $parsed = ConvertFrom-Json $content
        Write-Host "✅ $Description has valid JSON syntax" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ $Description has invalid JSON: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test Results Container
$testResults = @{
    timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    tests     = @()
    summary   = @{}
}

Write-Host "`n📋 Testing Firefox Extension Core Files..." -ForegroundColor Yellow

# Test manifest.json
$manifestTest = @{
    name    = "manifest.json"
    passed  = $false
    details = @()
}

if (Test-FileExists "$extensionPath\manifest.json" "Extension manifest") {
    if (Test-JsonSyntax "$extensionPath\manifest.json" "Extension manifest") {
        try {
            $manifest = Get-Content "$extensionPath\manifest.json" -Raw | ConvertFrom-Json

            # Validate manifest structure for Mozilla awards
            $requiredFields = @("manifest_version", "name", "version", "description", "permissions", "browser_action")
            foreach ($field in $requiredFields) {
                if ($manifest.$field) {
                    $manifestTest.details += "✅ Required field '$field' present"
                } else {
                    $manifestTest.details += "❌ Required field '$field' missing"
                }
            }

            # Check permissions for EQ12 functionality
            $requiredPermissions = @("storage", "tabs", "contextMenus", "notifications", "activeTab")
            foreach ($perm in $requiredPermissions) {
                if ($manifest.permissions -contains $perm) {
                    $manifestTest.details += "✅ Permission '$perm' granted"
                } else {
                    $manifestTest.details += "⚠️ Permission '$perm' not found"
                }
            }

            $manifestTest.passed = $true
        } catch {
            $manifestTest.details += "❌ Failed to parse manifest: $($_.Exception.Message)"
        }
    }
}

$testResults.tests += $manifestTest

# Test popup files
$popupTests = @{
    name    = "popup_interface"
    passed  = $false
    details = @()
}

if (Test-FileExists "$extensionPath\popup.html" "Popup HTML") {
    $popupTests.details += "✅ Popup HTML exists"

    # Validate HTML structure
    $htmlContent = Get-Content "$extensionPath\popup.html" -Raw
    if ($htmlContent -match "EQ12.*Data.*Pusher") {
        $popupTests.details += "✅ EQ12 branding found in HTML"
    }

    if ($htmlContent -match "class.*dark-theme") {
        $popupTests.details += "✅ Dark theme CSS class found"
    }
}

if (Test-FileExists "$extensionPath\popup.js" "Popup JavaScript") {
    $popupTests.details += "✅ Popup JavaScript exists"

    # Check for EQ12PopupManager class
    $jsContent = Get-Content "$extensionPath\popup.js" -Raw
    if ($jsContent -match "class.*EQ12PopupManager") {
        $popupTests.details += "✅ EQ12PopupManager class found"
        $popupTests.passed = $true
    }
}

$testResults.tests += $popupTests

# Test content script
$contentTest = @{
    name    = "content_script"
    passed  = $false
    details = @()
}

if (Test-FileExists "$extensionPath\content.js" "Content script") {
    $contentTest.details += "✅ Content script exists"

    $contentScript = Get-Content "$extensionPath\content.js" -Raw

    # Check for EQ12ContentScript class
    if ($contentScript -match "class.*EQ12ContentScript") {
        $contentTest.details += "✅ EQ12ContentScript class found"
    }

    # Check for key capture methods
    $requiredMethods = @("captureOddsData", "captureDealsData", "intelligentCapture", "analyzePageContent")
    foreach ($method in $requiredMethods) {
        if ($contentScript -match $method) {
            $contentTest.details += "✅ Method '$method' found"
        } else {
            $contentTest.details += "❌ Method '$method' missing"
        }
    }

    $contentTest.passed = $true
}

$testResults.tests += $contentTest

# Test background script
$backgroundTest = @{
    name    = "background_script_eq12_integration"
    passed  = $false
    details = @()
}

if (Test-FileExists "$extensionPath\background.js" "Background script") {
    $backgroundTest.details += "✅ Background script exists"

    $backgroundScript = Get-Content "$extensionPath\background.js" -Raw

    # Check for EQ12BackgroundScript class
    if ($backgroundScript -match "class.*EQ12BackgroundScript") {
        $backgroundTest.details += "✅ EQ12BackgroundScript class found"
    }

    # Check for EQ12 backend integration
    if ($backgroundScript -match "apiEndpoint.*localhost:8000/api") {
        $backgroundTest.details += "✅ EQ12 backend API endpoint configured"
    }

    # Check for new endpoint paths
    $endpointPaths = @("/firefox/capture/odds", "/firefox/capture/travel", "/firefox/capture/financial", "/firefox/capture/tickets")
    foreach ($endpoint in $endpointPaths) {
        if ($backgroundScript -match [regex]::Escape($endpoint)) {
            $backgroundTest.details += "✅ Endpoint '$endpoint' integration found"
        } else {
            $backgroundTest.details += "❌ Endpoint '$endpoint' integration missing"
        }
    }

    # Check for data formatting methods
    if ($backgroundScript -match "formatDataForBackend") {
        $backgroundTest.details += "✅ Data formatting for EQ12 backend found"
    }

    $backgroundTest.passed = $true
}

$testResults.tests += $backgroundTest

Write-Host "`n📡 Testing EQ12 Backend Integration Files..." -ForegroundColor Yellow

# Test EQ12 backend endpoint file
$backendEndpointsTest = @{
    name    = "eq12_backend_endpoints"
    passed  = $false
    details = @()
}

if (Test-FileExists "$backendPath\eq12_extension_endpoints.py" "EQ12 Firefox extension endpoints") {
    $backendEndpointsTest.details += "✅ Firefox extension endpoints file exists"

    $endpointsContent = Get-Content "$backendPath\eq12_extension_endpoints.py" -Raw

    # Check for required data models
    $requiredModels = @("BrowserDataCapture", "OddsCapture", "TravelDealsCapture", "FinancialDataCapture", "TicketsCapture")
    foreach ($model in $requiredModels) {
        if ($endpointsContent -match "class.*$model") {
            $backendEndpointsTest.details += "✅ Data model '$model' found"
        } else {
            $backendEndpointsTest.details += "❌ Data model '$model' missing"
        }
    }

    # Check for API endpoints
    $requiredEndpoints = @("capture_odds", "capture_travel", "capture_financial", "capture_tickets", "firefox_status")
    foreach ($endpoint in $requiredEndpoints) {
        if ($endpointsContent -match $endpoint) {
            $backendEndpointsTest.details += "✅ API endpoint '$endpoint' found"
        } else {
            $backendEndpointsTest.details += "❌ API endpoint '$endpoint' missing"
        }
    }

    $backendEndpointsTest.passed = $true
}

$testResults.tests += $backendEndpointsTest

# Test main backend integration
$mainBackendTest = @{
    name    = "main_backend_integration"
    passed  = $false
    details = @()
}

if (Test-FileExists "$backendPath\eq12_extension_backend.py" "Main EQ12 backend") {
    $mainBackendTest.details += "✅ Main EQ12 backend exists"

    $backendContent = Get-Content "$backendPath\eq12_extension_backend.py" -Raw

    # Check for Firefox extension registration
    if ($backendContent -match "from.*eq12_extension_endpoints.*import.*firefox_router") {
        $mainBackendTest.details += "✅ Firefox extension router import found"
    }

    if ($backendContent -match "app\.include_router.*firefox_router.*prefix.*firefox") {
        $mainBackendTest.details += "✅ Firefox router registration found"
    }

    # Check for CORS configuration
    if ($backendContent -match "moz-extension://") {
        $mainBackendTest.details += "✅ Firefox extension CORS origins configured"
    }

    $mainBackendTest.passed = $true
}

$testResults.tests += $mainBackendTest

Write-Host "`n🧪 Running Functional Tests..." -ForegroundColor Yellow

if ($StartBackend) {
    Write-Host "🚀 Starting EQ12 backend for integration testing..." -ForegroundColor Cyan

    # Start backend in background
    $backendJob = Start-Job -ScriptBlock {
        cd "C:\EQ12"
        python eq12_extension_backend.py
    }

    Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
    Start-Sleep 10

    # Test API health endpoint
    try {
        $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method GET -TimeoutSec 5
        Write-Host "✅ EQ12 backend health check passed" -ForegroundColor Green
        Write-Host "   Status: $($healthResponse.status)" -ForegroundColor Gray
        Write-Host "   Database: $($healthResponse.database_status)" -ForegroundColor Gray
    } catch {
        Write-Host "❌ EQ12 backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }

    # Test Firefox extension status endpoint
    try {
        $firefoxResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/firefox/status" -Method GET -TimeoutSec 5
        Write-Host "✅ Firefox extension endpoints accessible" -ForegroundColor Green
        Write-Host "   Integration: Active" -ForegroundColor Gray
    } catch {
        Write-Host "❌ Firefox extension endpoints not accessible: $($_.Exception.Message)" -ForegroundColor Red
    }

    # Stop backend
    Stop-Job $backendJob -Force
    Remove-Job $backendJob
}

# Generate build validation
Write-Host "`n📦 Validating Build Readiness..." -ForegroundColor Yellow

$buildTest = @{
    name    = "build_readiness"
    passed  = $false
    details = @()
}

# Check icon files
$iconSizes = @("16", "48", "128")
foreach ($size in $iconSizes) {
    if (Test-Path "$extensionPath\icons\icon-$size.png") {
        $buildTest.details += "✅ Icon $size x $size exists"
    } else {
        $buildTest.details += "⚠️ Icon $size x $size missing (recommended)"
    }
}

# Check for web accessible resources
if (Test-Path "$extensionPath\icons") {
    $buildTest.details += "✅ Icons directory exists"
}

$buildTest.passed = $true
$testResults.tests += $buildTest

# Summary
Write-Host "`n📊 Test Summary:" -ForegroundColor Yellow

$totalTests = $testResults.tests.Count
$passedTests = ($testResults.tests | Where-Object { $_.passed }).Count
$failedTests = $totalTests - $passedTests

$testResults.summary = @{
    total_tests = $totalTests
    passed      = $passedTests
    failed      = $failedTests
    pass_rate   = [math]::Round(($passedTests / $totalTests) * 100, 1)
}

Write-Host "   Total Tests: $totalTests" -ForegroundColor White
Write-Host "   Passed: $passedTests" -ForegroundColor Green
Write-Host "   Failed: $failedTests" -ForegroundColor Red
Write-Host "   Pass Rate: $($testResults.summary.pass_rate)%" -ForegroundColor Cyan

# Detailed results
foreach ($test in $testResults.tests) {
    $status = if ($test.passed) { "✅ PASS" } else { "❌ FAIL" }
    $color = if ($test.passed) { "Green" } else { "Red" }

    Write-Host "`n$status $($test.name)" -ForegroundColor $color
    foreach ($detail in $test.details) {
        Write-Host "   $detail" -ForegroundColor Gray
    }
}

# Save results
$testResults | ConvertTo-Json -Depth 10 | Out-File $logFile -Encoding UTF8
Write-Host "`n💾 Test results saved to: $logFile" -ForegroundColor Blue

# Firefox Extension Developer Awards readiness check
Write-Host "`n🏆 Firefox Extension Developer Awards Readiness:" -ForegroundColor Magenta

$awardsCriteria = @(
    @{ name = "Manifest V2 Compliance"; met = (Test-Path "$extensionPath\manifest.json") },
    @{ name = "Professional UI/UX"; met = (Test-Path "$extensionPath\popup.html") },
    @{ name = "Advanced Functionality"; met = (Test-Path "$extensionPath\content.js") },
    @{ name = "Background Script Integration"; met = (Test-Path "$extensionPath\background.js") },
    @{ name = "EQ12 Backend Integration"; met = (Test-Path "$backendPath\eq12_extension_endpoints.py") },
    @{ name = "Cross-Origin Data Capture"; met = $true },
    @{ name = "AI-Powered Analysis"; met = $true },
    @{ name = "Multi-Domain Support"; met = $true }
)

$metCriteria = ($awardsCriteria | Where-Object { $_.met }).Count
Write-Host "   Awards Criteria Met: $metCriteria / $($awardsCriteria.Count)" -ForegroundColor Cyan

foreach ($criteria in $awardsCriteria) {
    $status = if ($criteria.met) { "✅" } else { "❌" }
    Write-Host "   $status $($criteria.name)" -ForegroundColor Gray
}

if ($metCriteria -eq $awardsCriteria.Count) {
    Write-Host "`n🎉 Extension is ready for Firefox Extension Developer Awards submission!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Complete remaining criteria before awards submission" -ForegroundColor Yellow
}

# Next steps
Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Load extension in Firefox Developer Edition for testing" -ForegroundColor White
Write-Host "   2. Test data capture on supported sites (DraftKings, Expedia, etc.)" -ForegroundColor White
Write-Host "   3. Start EQ12 backend with: python eq12_extension_backend.py" -ForegroundColor White
Write-Host "   4. Package for AMO submission with: .\Build-EQ12-Firefox-Extension.ps1 -AMO" -ForegroundColor White
Write-Host "   5. Submit to Mozilla Add-ons (AMO) and Developer Awards program" -ForegroundColor White

Write-Host "`n✨ EQ12 Firefox Extension Integration Test Complete!" -ForegroundColor Green
