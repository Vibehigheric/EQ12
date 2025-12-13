#!/usr/bin/env powershell
# EQ12 Development Server Startup Script

[CmdletBinding()]
param(
    [switch]$Dev,
    [switch]$Prod,
    [switch]$Stop,
    [switch]$Restart,
    [int]$Port = 3000
)

$ServerPath = "C:\EQ12\server"
$ProcessName = "node"

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $Color = switch ($Level) {
        "INFO" { "Green" }
        "WARN" { "Yellow" }
        "ERROR" { "Red" }
        default { "White" }
    }
    Write-Host "[$Timestamp] [$Level] $Message" -ForegroundColor $Color
}

function Test-NodeJS {
    try {
        $nodeVersion = & node --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-EQ12Log "✅ Node.js found: $nodeVersion"
            return $true
        }
    }
    catch {
        Write-EQ12Log "❌ Node.js not found in PATH" "ERROR"
        return $false
    }
}

function Start-EQ12Server {
    param([switch]$DevMode)

    Write-EQ12Log "🚀 Starting EQ12 Server..."

    if (!(Test-Path $ServerPath)) {
        Write-EQ12Log "❌ Server directory not found: $ServerPath" "ERROR"
        return
    }

    if (!(Test-NodeJS)) {
        Write-EQ12Log "❌ Node.js installation required" "ERROR"
        Write-EQ12Log "Run: winget install OpenJS.NodeJS.LTS" "INFO"
        return
    }

    Set-Location $ServerPath

    # Check if package.json exists
    if (!(Test-Path "package.json")) {
        Write-EQ12Log "❌ package.json not found. Running npm init..." "WARN"
        & npm init -y
    }

    # Install dependencies if node_modules doesn't exist
    if (!(Test-Path "node_modules")) {
        Write-EQ12Log "📦 Installing dependencies..."
        & npm install
    }

    # Set environment variables
    $env:NODE_ENV = if ($DevMode) { "development" } else { "production" }
    $env:PORT = $Port

    Write-EQ12Log "🌍 Environment: $env:NODE_ENV"
    Write-EQ12Log "🌐 Port: $Port"

    if ($DevMode) {
        Write-EQ12Log "🔄 Starting in development mode with nodemon..."
        if (Get-Command nodemon -ErrorAction SilentlyContinue) {
            & nodemon server.js
        }
        else {
            Write-EQ12Log "⚠️ nodemon not found, using regular node..." "WARN"
            & node server.js
        }
    }
    else {
        Write-EQ12Log "🚀 Starting in production mode..."
        & node server.js
    }
}

function Stop-EQ12Server {
    Write-EQ12Log "🛑 Stopping EQ12 Server..."

    # Find and kill node processes running the server
    $processes = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*server.js*" }

    if ($processes) {
        foreach ($process in $processes) {
            Write-EQ12Log "Killing process $($process.Id)..."
            Stop-Process -Id $process.Id -Force
        }
        Write-EQ12Log "✅ Server stopped"
    }
    else {
        Write-EQ12Log "⚠️ No server processes found" "WARN"
    }
}

function Test-ServerConnection {
    param([int]$Port = 3000)

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/api/health" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-EQ12Log "✅ Server is responding on port $Port"
            return $true
        }
    }
    catch {
        Write-EQ12Log "❌ Server not responding on port $Port" "WARN"
        return $false
    }
}

function Open-Dashboard {
    param([int]$Port = 3000)

    $dashboardUrl = "http://localhost:$Port/dashboard/enhanced.html"
    Write-EQ12Log "🌐 Opening dashboard: $dashboardUrl"

    try {
        Start-Process $dashboardUrl
    }
    catch {
        Write-EQ12Log "❌ Failed to open browser" "ERROR"
        Write-EQ12Log "Manually open: $dashboardUrl" "INFO"
    }
}

# Main execution
Write-EQ12Log "🎯 EQ12 Development Server Manager"
Write-EQ12Log "═══════════════════════════════════"

if ($Stop) {
    Stop-EQ12Server
}
elseif ($Restart) {
    Stop-EQ12Server
    Start-Sleep -Seconds 2
    Start-EQ12Server -DevMode:$Dev
}
elseif ($Dev) {
    Write-EQ12Log "🔧 Development mode enabled"
    Start-EQ12Server -DevMode
}
elseif ($Prod) {
    Write-EQ12Log "🏭 Production mode enabled"
    Start-EQ12Server
}
else {
    Write-EQ12Log "ℹ️ Usage examples:"
    Write-EQ12Log "  .\start-eq12.ps1 -Dev          # Start in development mode"
    Write-EQ12Log "  .\start-eq12.ps1 -Prod         # Start in production mode"
    Write-EQ12Log "  .\start-eq12.ps1 -Stop         # Stop the server"
    Write-EQ12Log "  .\start-eq12.ps1 -Restart -Dev # Restart in dev mode"
    Write-EQ12Log ""
    Write-EQ12Log "🔗 Quick Start:"
    Write-EQ12Log "1. .\start-eq12.ps1 -Dev"
    Write-EQ12Log "2. Open http://localhost:3000/dashboard/enhanced.html"
    Write-EQ12Log ""
    Write-EQ12Log "📊 Available Endpoints:"
    Write-EQ12Log "- http://localhost:3000/api/health"
    Write-EQ12Log "- http://localhost:3000/api/odds"
    Write-EQ12Log "- http://localhost:3000/api/arbitrage"
    Write-EQ12Log "- http://localhost:3000/api/revenue/projections"
    Write-EQ12Log "- http://localhost:3000/dashboard/enhanced.html"

    # Test if server is already running
    if (Test-ServerConnection -Port $Port) {
        Write-EQ12Log ""
        Write-EQ12Log "🎉 Server is already running! Opening dashboard..."
        Open-Dashboard -Port $Port
    }
}
