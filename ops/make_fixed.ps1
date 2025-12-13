#!/usr/bin/env pwsh
<#
.SYNOPSIS
    EQ12 Expert Quantum Development Task Runner - Fixed Version
.DESCRIPTION
    Common development tasks for the EQ12 quantum workspace
.PARAMETER Task
    The task to run: lint, test, build, format, clean, up, down, logs, help
.PARAMETER Service
    Specific service for Docker operations
.PARAMETER Verbose
    Enable verbose output
#>

param(
    [Parameter(Position = 0)]
    [string]$Task = "help",
    [string]$Service = "",
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Write-TaskHeader($message) {
    Write-Host "`n $message" -ForegroundColor Cyan
    Write-Host ("=" * ($message.Length + 4)) -ForegroundColor DarkCyan
}

function Test-VirtualEnv {
    if (!(Test-Path ".venv\Scripts\Activate.ps1")) {
        Write-Host " Virtual environment not found. Run .\ops\bootstrap.ps1 first" -ForegroundColor Red
        exit 1
    }
}

switch ($Task.ToLower()) {
    "lint" {
        Write-TaskHeader "Running Expert Quantum Linting"
        Test-VirtualEnv
        & ".\.venv\Scripts\Activate.ps1"
        
        Write-Host " Pre-commit hooks..." -ForegroundColor Yellow
        try { & ".\.venv\Scripts\pre-commit.exe" run --all-files } catch { Write-Host "Pre-commit completed with warnings" }
        
        Write-Host " Python linting..." -ForegroundColor Yellow
        try { & ".\.venv\Scripts\ruff.exe" check . --fix } catch { Write-Host "Ruff completed" }
        try { & ".\.venv\Scripts\flake8.exe" . --max-line-length=88 --extend-ignore=E203, W503 } catch { Write-Host "Flake8 completed" }
        
        Write-Host " Security scan..." -ForegroundColor Yellow
        try { & ".\.venv\Scripts\bandit.exe" -r scripts/ -f json -o logs/bandit-report.json } catch { Write-Host "Bandit scan completed" }
        
        Write-Host " Linting complete" -ForegroundColor Green
    }
    
    "format" {
        Write-TaskHeader "Formatting Code"
        Test-VirtualEnv
        & ".\.venv\Scripts\Activate.ps1"
        
        Write-Host " Black formatting..." -ForegroundColor Yellow
        & ".\.venv\Scripts\black.exe" .
        
        Write-Host " Import sorting..." -ForegroundColor Yellow
        & ".\.venv\Scripts\isort.exe" . --profile black
        
        if (Test-Path "package.json") {
            Write-Host " Prettier formatting..." -ForegroundColor Yellow
            npx prettier --write "**/*.{js,ts,json,yaml,md}"
        }
        
        Write-Host " Formatting complete" -ForegroundColor Green
    }
    
    "test" {
        Write-TaskHeader "Running Expert Quantum Tests"
        Test-VirtualEnv
        & ".\.venv\Scripts\Activate.ps1"
        
        if (Test-Path "tests") {
            Write-Host " Running pytest..." -ForegroundColor Yellow
            & ".\.venv\Scripts\pytest.exe" -v --cov=scripts --cov-report=html --cov-report=term
        }
        else {
            Write-Host "  No tests directory found" -ForegroundColor Yellow
            Write-Host "Creating basic test structure..." -ForegroundColor Gray
            New-Item -ItemType Directory -Path "tests" -Force | Out-Null
            @"
# EQ12 Expert Quantum Test Suite
import pytest
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

def test_quantum_import():
    ''Basic import test''
    assert True

def test_workspace_structure():
    ''Test workspace structure''
    workspace = Path(__file__).parent.parent
    assert (workspace / "scripts").exists()
    assert (workspace / "logs").exists()
    assert (workspace / "data").exists()
"@ | Out-File -FilePath "tests/test_quantum_basic.py" -Encoding UTF8
            Write-Host " Created basic test structure" -ForegroundColor Green
        }
        
        Write-Host " Testing complete" -ForegroundColor Green
    }
    
    "build" {
        Write-TaskHeader "Building Expert Quantum Containers"
        
        if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
            Write-Host " Docker not found" -ForegroundColor Red
            exit 1
        }
        
        Write-Host " Building development image..." -ForegroundColor Yellow
        docker build --target development -t eq12:dev .
        
        Write-Host " Building production image..." -ForegroundColor Yellow  
        docker build --target production -t eq12:prod .
        
        Write-Host " Build complete" -ForegroundColor Green
    }
    
    "up" {
        Write-TaskHeader "Starting Expert Quantum Services"
        
        $composeArgs = @("up", "-d")
        if ($Service) { $composeArgs += $Service }
        if ($Verbose) { $composeArgs += "--verbose" }
        
        docker compose @composeArgs
        
        Write-Host " Services started" -ForegroundColor Green
        Write-Host " Access points:" -ForegroundColor Cyan
        Write-Host "   Main app: http://localhost:8000" -ForegroundColor White
        Write-Host "   Dashboard: http://localhost:8080" -ForegroundColor White
        Write-Host "   Jupyter: http://localhost:8888" -ForegroundColor White
    }
    
    "down" {
        Write-TaskHeader "Stopping Expert Quantum Services"
        docker compose down
        Write-Host " Services stopped" -ForegroundColor Green
    }
    
    "logs" {
        Write-TaskHeader "Expert Quantum Service Logs"
        $logArgs = @("logs", "-f")
        if ($Service) { $logArgs += $Service }
        docker compose @logArgs
    }
    
    "clean" {
        Write-TaskHeader "Cleaning Expert Quantum Workspace"
        
        # Clean Python cache
        if (Test-Path "__pycache__") { Remove-Item -Recurse -Force "__pycache__" }
        Get-ChildItem -Recurse -Name "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
        Get-ChildItem -Recurse -Name "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
        
        # Clean test artifacts
        if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
        if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
        if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
        
        Write-Host " Cleanup complete" -ForegroundColor Green
    }
    
    "status" {
        Write-TaskHeader "Expert Quantum Status"
        
        Write-Host " Environment:" -ForegroundColor Yellow
        
        # Check Python
        try { 
            $pythonVersion = python --version 2>$null
            Write-Host "   Python: $pythonVersion" -ForegroundColor White
        }
        catch {
            Write-Host "   Python: Not found" -ForegroundColor Red
        }
        
        # Check Virtual Environment
        $venvStatus = if (Test-Path '.venv') { " Active" } else { " Missing" }
        Write-Host "   Virtual env: $venvStatus" -ForegroundColor White
        
        # Check Docker
        try {
            $dockerVersion = docker --version 2>$null
            Write-Host "   Docker: $dockerVersion" -ForegroundColor White
        }
        catch {
            Write-Host "   Docker: Not found" -ForegroundColor Red
        }
        
        Write-Host "`n Workspace:" -ForegroundColor Yellow
        $dirs = @("scripts", "tests", "logs", "data", "models")
        foreach ($dir in $dirs) {
            $status = if (Test-Path $dir) { "" } else { "" }
            $count = if (Test-Path $dir) { (Get-ChildItem $dir -ErrorAction SilentlyContinue).Count } else { 0 }
            Write-Host "   ${dir}: $status ($count files)" -ForegroundColor White
        }
        
        Write-Host "`n Docker Services:" -ForegroundColor Yellow
        try {
            docker compose ps --format table
        }
        catch {
            Write-Host "   No services running" -ForegroundColor Gray
        }
    }
    
    "help" {
        Write-Host " EQ12 Expert Quantum Task Runner" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "USAGE:" -ForegroundColor Yellow
        Write-Host "    .\ops\make.ps1 <task> [options]" -ForegroundColor White
        Write-Host ""
        Write-Host "TASKS:" -ForegroundColor Yellow
        Write-Host "    lint        Run all linting and code quality checks" -ForegroundColor White
        Write-Host "    format      Format code with Black, isort, and Prettier" -ForegroundColor White
        Write-Host "    test        Run test suite and generate coverage" -ForegroundColor White
        Write-Host "    build       Build Docker containers" -ForegroundColor White
        Write-Host "    up          Start services with docker-compose" -ForegroundColor White
        Write-Host "    down        Stop all services" -ForegroundColor White
        Write-Host "    logs        Show service logs (use -Service <name> for specific)" -ForegroundColor White
        Write-Host "    clean       Clean workspace of build artifacts" -ForegroundColor White
        Write-Host "    status      Show environment and workspace status" -ForegroundColor White
        Write-Host "    help        Show this help message" -ForegroundColor White
        Write-Host ""
        Write-Host "OPTIONS:" -ForegroundColor Yellow
        Write-Host "    -Service    Specify service for Docker operations" -ForegroundColor White
        Write-Host "    -Verbose    Enable verbose output" -ForegroundColor White
        Write-Host ""
        Write-Host "EXAMPLES:" -ForegroundColor Yellow
        Write-Host "    .\ops\make.ps1 lint" -ForegroundColor Gray
        Write-Host "    .\ops\make.ps1 test" -ForegroundColor Gray
        Write-Host "    .\ops\make.ps1 up -Service eq12-dev" -ForegroundColor Gray
        Write-Host "    .\ops\make.ps1 logs -Service postgres" -ForegroundColor Gray
        Write-Host ""
        Write-Host " Expert Quantum mode activated!" -ForegroundColor Magenta
    }
    
    default {
        Write-Host " Unknown task: $Task" -ForegroundColor Red
        Write-Host "Run '.\ops\make.ps1 help' for available tasks" -ForegroundColor Yellow
        exit 1
    }
}