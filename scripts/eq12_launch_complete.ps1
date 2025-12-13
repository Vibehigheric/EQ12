# EQ12 Complete Firefox Extension Launch Script
# Launches backend API server and Firefox with the extension

[CmdletBinding()]
param(
    [Parameter()]
    [switch]$SkipBackend,

    [Parameter()]
    [switch]$DevMode,

    [Parameter()]
    [switch]$OpenBrowser,

    [Parameter()]
    [string]$Port = "8000"
)

$ErrorActionPreference = "Continue"

function Write-EQ12Log($Message, $Level = "INFO") {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-Host $logEntry -ForegroundColor $(
        switch ($Level) {
            "INFO" { "Green" }
            "WARN" { "Yellow" }
            "ERROR" { "Red" }
            default { "White" }
        }
    )
}

Write-EQ12Log "EQ12 Complete Extension System Launcher" "INFO"
Write-EQ12Log "Extension Path: C:\EQ12\firefox_extensions\eq12_betting_dashboard" "INFO"

# Check if backend should be started
if (!$SkipBackend) {
    Write-EQ12Log "Starting EQ12 Extension Backend API Server..." "INFO"

    try {
        # Start the backend server in background
        $backendScript = @"
import uvicorn
import sys
import os
sys.path.append('C:\\EQ12\\scripts')
os.chdir('C:\\EQ12')
from eq12_extension_backend import app
print('EQ12 Backend: Starting on port $Port...')
uvicorn.run(app, host='0.0.0.0', port=$Port, reload=False, log_level='info')
"@

        $backendJob = Start-Job -ScriptBlock {
            param($script)
            python -c $script
        } -ArgumentList $backendScript

        Write-EQ12Log "Backend API server started (Job ID: $($backendJob.Id))" "INFO"

        # Wait a moment for server to start
        Start-Sleep -Seconds 3

        # Test the API
        try {
            $testResponse = Invoke-WebRequest -Uri "http://localhost:$Port/api/ping" -UseBasicParsing -TimeoutSec 5
            Write-EQ12Log "✅ Backend API responding (Status: $($testResponse.StatusCode))" "INFO"
        } catch {
            Write-EQ12Log "⚠️ Backend API not responding yet - may need more time to start" "WARN"
        }

    } catch {
        Write-EQ12Log "❌ Failed to start backend: $($_.Exception.Message)" "ERROR"
    }
}

# Firefox Extension Setup
Write-EQ12Log "🦊 Setting up Firefox Extension..." "INFO"

$extensionPath = "C:\EQ12\firefox_extensions\eq12_betting_dashboard"
$manifestPath = "$extensionPath\manifest_integrated.json"

# Check if integrated files exist, otherwise use originals
$popupFile = if (Test-Path "$extensionPath\popup_v3_integrated.html") {
    "popup_v3_integrated.html"
} else {
    "popup_v3_enhanced.html"
}

$backgroundFile = if (Test-Path "$extensionPath\background_v3_integrated.js") {
    "background_v3_integrated.js"
} else {
    "background_v3_enhanced.js"
}

$manifestFile = if (Test-Path $manifestPath) {
    "manifest_integrated.json"
} else {
    "manifest.json"
}

Write-EQ12Log "Using manifest: $manifestFile" "INFO"
Write-EQ12Log "Using popup: $popupFile" "INFO"
Write-EQ12Log "Using background: $backgroundFile" "INFO"

# Create a quick test of the extension files
$requiredFiles = @(
    $manifestFile,
    $popupFile,
    $backgroundFile,
    "styles.css"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $extensionPath $file
    if (!(Test-Path $filePath)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-EQ12Log "⚠️ Missing extension files: $($missingFiles -join ', ')" "WARN"
} else {
    Write-EQ12Log "✅ All required extension files present" "INFO"
}

# Firefox Detection and Launch
$firefoxPaths = @(
    "${env:ProgramFiles}\Mozilla Firefox\firefox.exe",
    "${env:ProgramFiles(x86)}\Mozilla Firefox\firefox.exe"
)

$firefoxPath = $null
foreach ($path in $firefoxPaths) {
    if (Test-Path $path) {
        $firefoxPath = $path
        Write-EQ12Log "✅ Firefox found: $path" "INFO"
        break
    }
}

if (!$firefoxPath) {
    Write-EQ12Log "❌ Firefox not found! Please install Firefox first." "ERROR"
    Write-EQ12Log "Download from: https://www.mozilla.org/firefox/" "INFO"
    return
}

if ($OpenBrowser) {
    Write-EQ12Log "🚀 Launching Firefox with debugging enabled..." "INFO"

    # Create Firefox profile for development
    $profileName = "EQ12_Extension_Profile"
    $profilePath = Join-Path $env:APPDATA "Mozilla\Firefox\Profiles\$profileName"

    if (!(Test-Path $profilePath)) {
        Write-EQ12Log "Creating Firefox development profile..." "INFO"
        & $firefoxPath -CreateProfile "$profileName $profilePath" -headless | Out-Null
        Start-Sleep -Seconds 2
    }

    # Configure profile for extension development
    $prefsFile = Join-Path $profilePath "prefs.js"
    $devPrefs = @(
        'user_pref("xpinstall.signatures.required", false);',
        'user_pref("extensions.ui.developer.hidden", false);',
        'user_pref("devtools.chrome.enabled", true);',
        'user_pref("devtools.debugger.remote-enabled", true);',
        'user_pref("extensions.autoDisableScopes", 0);',
        'user_pref("security.tls.insecure_fallback_hosts", "localhost");'
    )

    foreach ($pref in $devPrefs) {
        Add-Content -Path $prefsFile -Value $pref -Force
    }

    Write-EQ12Log "Firefox profile configured for extension development" "INFO"

    # Launch Firefox with extension debugging
    $firefoxArgs = @(
        "-profile", $profilePath,
        "about:debugging#/runtime/this-firefox"
    )

    if ($DevMode) {
        $firefoxArgs += @("-jsconsole")
    }

    Start-Process -FilePath $firefoxPath -ArgumentList $firefoxArgs
    Write-EQ12Log "🦊 Firefox launched! Load the extension manually:" "INFO"
}

# Display setup instructions
Write-Host "`n" -NoNewline
Write-EQ12Log "🎯 EQ12 Extension System Ready!" "INFO"
Write-Host "`n=== SETUP INSTRUCTIONS ===" -ForegroundColor Cyan
Write-Host "1. Open Firefox (launched automatically if -OpenBrowser used)" -ForegroundColor White
Write-Host "2. Navigate to: about:debugging#/runtime/this-firefox" -ForegroundColor White
Write-Host "3. Click 'Load Temporary Add-on'" -ForegroundColor White
Write-Host "4. Select: $extensionPath\$manifestFile" -ForegroundColor Yellow
Write-Host "5. Configure API settings in extension options" -ForegroundColor White
Write-Host "`n=== API ENDPOINTS ===" -ForegroundColor Cyan
Write-Host "Backend URL: http://localhost:$Port" -ForegroundColor Yellow
Write-Host "Dashboard: http://localhost:$Port/dashboard" -ForegroundColor Yellow
Write-Host "Health Check: http://localhost:$Port/api/health" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:$Port/api/docs" -ForegroundColor Yellow

if (!$SkipBackend) {
    Write-Host "`n=== BACKGROUND SERVICES ===" -ForegroundColor Cyan
    Write-Host "Backend API Job ID: $($backendJob.Id)" -ForegroundColor Yellow
    Write-Host "To stop backend: Stop-Job -Id $($backendJob.Id); Remove-Job -Id $($backendJob.Id)" -ForegroundColor White
}

Write-Host "`n=== FEATURES AVAILABLE ===" -ForegroundColor Cyan
Write-Host "Parlay Generation - AI-powered betting combinations" -ForegroundColor Green
Write-Host "Privacy Protection - Tracker blocking, fingerprinting protection" -ForegroundColor Green
Write-Host "Developer Tools - Enhanced debugging and monitoring" -ForegroundColor Green
Write-Host "UI Enhancement - Dark mode, auto-reload, custom styles" -ForegroundColor Green
Write-Host "VPN Management - Connection monitoring and leak detection" -ForegroundColor Green
Write-Host "Audit Reports - Betting performance analytics" -ForegroundColor Green

Write-EQ12Log "Launch completed! Happy betting!" "INFO"
