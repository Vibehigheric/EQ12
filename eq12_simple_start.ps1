# EQ12 Performance Optimized - 2025-10-11T06:54:20.694076
# Startup optimization applied by Master System Fixer

# EQ12 Simple Cold Start
# Basic startup script with error handling for PowerShell 5.1 compatibility

param(
    [switch]$SkipNgrok,
    [switch]$TestOnly
)

$logPath = "C:\EQ12\logs\eq12_simple_start.log"

function Write-Log($msg) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $msg" | Out-File $logPath -Append -Encoding UTF8
    Write-Host "$timestamp - $msg"
}

function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        Write-Log "Python check: $pythonVersion"
        return $true
    } catch {
        Write-Log "Python not available: $_"
        return $false
    }
}

function Test-RequiredFiles {
    $requiredFiles = @(
        "C:\EQ12\scripts\odds_parser.py",
        "C:\EQ12\scripts\parlay_builder.py",
        "C:\EQ12\requirements.txt"
    )
    
    $allExist = $true
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Log "Found: $file"
        } else {
            Write-Log "Missing: $file"
            $allExist = $false
        }
    }
    return $allExist
}

Write-Log "=== EQ12 Simple Cold Start BEGIN ==="

# Test Python environment
if (-not (Test-Python)) {
    Write-Log "Python environment not ready. Exiting."
    exit 1
}

# Test required files
if (-not (Test-RequiredFiles)) {
    Write-Log "Required files missing. Exiting."
    exit 1
}

if ($TestOnly) {
    Write-Log "Test mode complete. Environment ready."
    exit 0
}

# Start ngrok if not skipped
if (-not $SkipNgrok) {
    Write-Log "Starting ngrok services..."
    try {
        $ngrokProcess = Get-Process -Name "ngrok" -ErrorAction SilentlyContinue
        if ($ngrokProcess) {
            Write-Log "Ngrok already running (PID: $($ngrokProcess.Id))"
        } else {
            Write-Log "Starting basic ngrok tunnel..."
            Start-Process -FilePath "ngrok" -ArgumentList "http", "8080" -WindowStyle Minimized
            Start-Sleep 3
            Write-Log "Ngrok tunnel started"
        }
    } catch {
        Write-Log "Ngrok start failed: $_"
    }
}

# Run core Python scripts
Write-Log "Starting core EQ12 services..."

try {
    Write-Log "Running odds parser..."
    python "C:\EQ12\scripts\odds_parser.py"
    Write-Log "Odds parser completed"
} catch {
    Write-Log "Odds parser failed: $_"
}

try {
    Write-Log "Running parlay builder..."
    python "C:\EQ12\scripts\parlay_builder.py"
    Write-Log "Parlay builder completed"
} catch {
    Write-Log "Parlay builder failed: $_"
}

Write-Log "EQ12 basic services started"
Write-Log "Check logs at: $logPath"
Write-Log "=== EQ12 Simple Cold Start END ==="

Write-Host ""
Write-Host "EQ12 GODSTACK Simple Start Complete!" -ForegroundColor Green
Write-Host "Core services: Started" -ForegroundColor Green
if ($SkipNgrok) {
    Write-Host "Ngrok tunnel: Skipped" -ForegroundColor Yellow
} else {
    Write-Host "Ngrok tunnel: Started" -ForegroundColor Yellow
}
Write-Host "Logs: $logPath" -ForegroundColor Cyan