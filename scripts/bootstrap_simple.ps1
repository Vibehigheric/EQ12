# EQ12 Bootstrap Script - Professional Sports Betting Automation Setup
# Configures uv, ruff, pre-commit, and Python environment

[CmdletBinding()]
param()

Write-Host "Starting EQ12 Professional Bootstrap..." -ForegroundColor Green

# Set strict error handling
$ErrorActionPreference = "Stop"

# Workspace root
$WorkspaceRoot = Split-Path -Parent $PSScriptRoot
Write-Host "Workspace root: $WorkspaceRoot" -ForegroundColor Cyan

# 1) Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python 3.12+ required. Install from python.org" -ForegroundColor Red
    exit 1
}

# 2) Install uv if not present
Write-Host "Installing uv package manager..." -ForegroundColor Yellow
try {
    uv --version | Out-Null
    Write-Host "uv already installed" -ForegroundColor Green
} catch {
    Write-Host "Installing uv..." -ForegroundColor Yellow
    python -m pip install uv
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install uv"
    }
}

# 3) Create virtual environment with uv
Write-Host "Setting up Python virtual environment..." -ForegroundColor Yellow
cd $WorkspaceRoot
uv venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: venv creation failed, continuing..." -ForegroundColor Yellow
}

# 4) Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
uv sync --all-extras
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Some dependencies failed, continuing..." -ForegroundColor Yellow
}

# 5) Install pre-commit
Write-Host "Setting up pre-commit hooks..." -ForegroundColor Yellow
try {
    pre-commit --version | Out-Null
    Write-Host "pre-commit already installed" -ForegroundColor Green
} catch {
    uv add pre-commit
}

# Install pre-commit hooks
pre-commit install
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: pre-commit hook installation failed" -ForegroundColor Yellow
}

# 6) Validate environment variables
Write-Host "Checking environment variables..." -ForegroundColor Yellow
$requiredVars = @("ODDS_API_KEY", "OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN")
foreach ($var in $requiredVars) {
    if ([string]::IsNullOrEmpty((Get-Item "env:$var" -ErrorAction SilentlyContinue).Value)) {
        Write-Host "WARNING: $var not set" -ForegroundColor Yellow
    } else {
        Write-Host "$var is configured" -ForegroundColor Green
    }
}

# 7) Create logs directory
$logsDir = Join-Path $WorkspaceRoot "logs"
if (-not (Test-Path $logsDir)) {
    Write-Host "Creating logs directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

# 8) Verify tools
Write-Host "Verifying installation..." -ForegroundColor Yellow
try {
    python --version
    uv --version
    Write-Host "All tools verified successfully!" -ForegroundColor Green
} catch {
    Write-Host "Tool verification failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "EQ12 Bootstrap Complete!" -ForegroundColor Green
Write-Host "Ready for expert sports betting automation" -ForegroundColor Cyan