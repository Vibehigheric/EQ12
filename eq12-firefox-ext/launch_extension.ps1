# EQ12 Firefox Extension Launcher
# Starts the backend API and prepares extension for loading

param(
    [switch]$StartBackend = $true,
    [switch]$BuildExtension = $false,
    [switch]$InstallDeps = $false
)

Write-Host "EQ12 Firefox Extension Launcher" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Set paths
$BackendScript = "C:\EQ12\scripts\eq12_extension_backend.py"
$ExtensionPath = "C:\EQ12\eq12-firefox-ext"
$LogPath = "C:\EQ12\logs\extension_launcher.log"

# Ensure logs directory exists
if (!(Test-Path "C:\EQ12\logs")) {
    New-Item -ItemType Directory -Path "C:\EQ12\logs" -Force | Out-Null
}

# Install dependencies if requested
if ($InstallDeps) {
    Write-Host "Installing extension dependencies..." -ForegroundColor Yellow
    Set-Location $ExtensionPath

    if (Test-Path "package.json") {
        npm install
        Write-Host "✅ NPM dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ No package.json found - skipping npm install" -ForegroundColor Yellow
    }
}

# Build extension if requested
if ($BuildExtension) {
    Write-Host "🔨 Building Firefox extension..." -ForegroundColor Yellow
    Set-Location $ExtensionPath

    # Windows-compatible build
    if (Test-Path "dist-firefox") {
        Remove-Item "dist-firefox" -Recurse -Force
    }

    # Copy files manually for Windows
    New-Item -ItemType Directory -Path "dist-firefox" -Force | Out-Null
    Copy-Item "src\*" "dist-firefox\" -Recurse -Force
    Copy-Item "icons\*" "dist-firefox\icons\" -Recurse -Force
    Copy-Item "manifest.firefox.json" "dist-firefox\manifest.json" -Force

    Write-Host "✅ Extension built in dist-firefox/" -ForegroundColor Green
}

# Start backend API server
if ($StartBackend) {
    Write-Host "🚀 Starting EQ12 backend API..." -ForegroundColor Yellow

    # Check if backend is already running
    $existingJobs = Get-Job | Where-Object { $_.Name -like "*EQ12-API*" -and $_.State -eq "Running" }
    if ($existingJobs) {
        Write-Host "⚠️ Backend already running (Job: $($existingJobs[0].Name))" -ForegroundColor Yellow
    } else {
        # Start backend as background job
        $job = Start-Job -ScriptBlock {
            Set-Location "C:\EQ12\scripts"
            python eq12_extension_backend.py 2>&1 | Tee-Object -FilePath "C:\EQ12\logs\backend_output.log"
        } -Name "EQ12-API-Extension"

        Write-Host "✅ Backend started (Job ID: $($job.Id))" -ForegroundColor Green

        # Wait for server to start
        Write-Host "⏳ Waiting for server startup..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5

        # Test API connectivity
        try {
            $ping = Invoke-RestMethod -Uri "http://localhost:8000/api/ping" -TimeoutSec 10
            Write-Host "✅ API is responding!" -ForegroundColor Green
            Write-Host "   Server: $($ping.server)" -ForegroundColor Cyan
        } catch {
            Write-Host "⚠️ API not responding yet - give it a moment..." -ForegroundColor Yellow
        }
    }
}

Write-Host "`n🦊 FIREFOX EXTENSION READY!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open Firefox" -ForegroundColor White
Write-Host "2. Go to about:debugging#/runtime/this-firefox" -ForegroundColor White
Write-Host "3. Click 'Load Temporary Add-on'" -ForegroundColor White
Write-Host "4. Navigate to: $ExtensionPath\" -ForegroundColor Yellow
Write-Host "5. Select: manifest.json" -ForegroundColor Yellow

Write-Host "`n🔗 Extension Features:" -ForegroundColor Cyan
Write-Host "• 🎯 Generate 5-leg and 10-leg parlays" -ForegroundColor White
Write-Host "• 📊 View audit reports and analytics" -ForegroundColor White
Write-Host "• ❤️ System health monitoring" -ForegroundColor White
Write-Host "• 🟢 EV highlighting on sportsbook pages" -ForegroundColor White

Write-Host "`n🌐 API Endpoints:" -ForegroundColor Cyan
Write-Host "• Ping: http://localhost:8000/api/ping" -ForegroundColor White
Write-Host "• Health: http://localhost:8000/api/health" -ForegroundColor White
Write-Host "• Parlay: http://localhost:8000/api/parlay?size=5" -ForegroundColor White
Write-Host "• Audit: http://localhost:8000/api/audit" -ForegroundColor White

Write-Host "`n⚡ Pro Tips:" -ForegroundColor Cyan
Write-Host "• Set API key in extension settings (default: eq12-api-key)" -ForegroundColor White
Write-Host "• Content script highlights EV+ bets on sportsbook pages" -ForegroundColor White
Write-Host "• Extension works with DraftKings, FanDuel, BetMGM, Caesars, Barstool" -ForegroundColor White

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Add-Content -Path $LogPath -Value "$timestamp - Extension launcher completed successfully"

Write-Host "`nEQ12 Extension System Ready!" -ForegroundColor Green
