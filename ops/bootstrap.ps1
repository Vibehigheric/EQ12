#!/usr/bin/env pwsh
<#
.SYNOPSIS
    EQ12 Expert Quantum Bootstrap Script
.DESCRIPTION
    One-shot setup for local EQ12 development environment
.PARAMETER Force
    Force reinstall even if components exist
.PARAMETER SkipGit
    Skip git hooks setup
#>

param(
    [switch]$Force,
    [switch]$SkipGit
)

Write-Host " EQ12 Expert Quantum Bootstrap Starting..." -ForegroundColor Cyan

# Check prerequisites
$requirements = @{
    "Python 3.12+" = { python --version 2>$null }
    "Git"          = { git --version 2>$null }
    "Node.js"      = { node --version 2>$null }
    "Docker"       = { docker --version 2>$null }
}

Write-Host "`n Checking prerequisites..." -ForegroundColor Yellow
foreach ($req in $requirements.GetEnumerator()) {
    $result = & $req.Value
    if ($LASTEXITCODE -eq 0) {
        Write-Host " $($req.Key): $result" -ForegroundColor Green
    }
    else {
        Write-Host " $($req.Key): Missing" -ForegroundColor Red
    }
}

# Create directories
$dirs = @("logs", "data", "models", "docs", "tests", "_third_party")
Write-Host "`n Creating directories..." -ForegroundColor Yellow
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host " Created: $dir" -ForegroundColor Green
    }
    else {
        Write-Host " Exists: $dir" -ForegroundColor Blue
    }
}

# Setup Python virtual environment
Write-Host "`n Setting up Python environment..." -ForegroundColor Yellow
if (!(Test-Path ".venv") -or $Force) {
    if (Test-Path ".venv") { Remove-Item -Recurse -Force ".venv" }
    python -m venv .venv
    Write-Host " Created virtual environment" -ForegroundColor Green
}
else {
    Write-Host " Virtual environment exists" -ForegroundColor Blue
}

# Activate venv and install dependencies
Write-Host " Installing Python dependencies..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
& ".\.venv\Scripts\pip.exe" install --upgrade pip setuptools wheel

$pythonDeps = @(
    "pre-commit", "pytest", "pytest-cov", "black", "isort", "ruff", "flake8", "bandit",
    "numpy", "pandas", "requests", "fastapi", "uvicorn", "streamlit", "jupyter"
)

foreach ($dep in $pythonDeps) {
    Write-Host "  Installing $dep..." -ForegroundColor Gray
    & ".\.venv\Scripts\pip.exe" install $dep --quiet
}
Write-Host " Python dependencies installed" -ForegroundColor Green

# Setup Node.js dependencies
if (Test-Path "package.json") {
    Write-Host "`n Installing Node.js dependencies..." -ForegroundColor Yellow
    npm install --silent
    Write-Host " Node.js dependencies installed" -ForegroundColor Green
}

# Setup pre-commit hooks
if (!$SkipGit) {
    Write-Host "`n Setting up git hooks..." -ForegroundColor Yellow
    try {
        & ".\.venv\Scripts\pre-commit.exe" install --install-hooks --overwrite
        Write-Host " Pre-commit hooks installed" -ForegroundColor Green
    }
    catch {
        Write-Host "  Pre-commit setup skipped (not a git repo?)" -ForegroundColor Yellow
    }
}

# Create .env from example
if (!(Test-Path ".env") -and (Test-Path ".env.example")) {
    Write-Host "`n  Creating .env from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host " Created .env file" -ForegroundColor Green
    Write-Host "  Remember to update .env with real values!" -ForegroundColor Yellow
}

# Setup Docker if available
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "`n Checking Docker setup..." -ForegroundColor Yellow
    try {
        docker info | Out-Null
        Write-Host " Docker is running" -ForegroundColor Green
    }
    catch {
        Write-Host "  Docker not running - start Docker Desktop" -ForegroundColor Yellow
    }
}

# Final status
Write-Host "`n EQ12 Expert Quantum Bootstrap Complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Update .env with real API keys" -ForegroundColor White
Write-Host "  2. Run: .\ops\make.ps1 lint" -ForegroundColor White  
Write-Host "  3. Run: .\ops\make.ps1 test" -ForegroundColor White
Write-Host "  4. Run: .\ops\make.ps1 build" -ForegroundColor White
Write-Host "  5. Run: docker compose up -d" -ForegroundColor White

Write-Host "`nExpert Quantum mode activated!" -ForegroundColor Magenta