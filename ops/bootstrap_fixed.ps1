#!/usr/bin/env pwsh
<#
.SYNOPSIS
    EQ12 Expert Quantum Bootstrap - One-Command Setup (Fixed)
.DESCRIPTION
    Bootstrap complete Expert Quantum development environment
.PARAMETER Force
    Force reinstall even if environment exists
.PARAMETER SkipDocker
    Skip Docker validation
.PARAMETER VerboseOutput
    Show detailed output
#>

param(
    [switch]$Force,
    [switch]$SkipDocker,  
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"

function Write-BootstrapHeader($message) {
    Write-Host "`n $message" -ForegroundColor Magenta
    Write-Host ("=" * ($message.Length + 4)) -ForegroundColor DarkMagenta
}

function Write-Success($message) {
    Write-Host " $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "  $message" -ForegroundColor Yellow
}

function Write-Info($message) {
    Write-Host "  $message" -ForegroundColor Cyan
}

function Test-Command($command) {
    try {
        Get-Command $command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Install-PythonIfMissing {
    if (!(Test-Command python)) {
        Write-Warning "Python not found. Please install Python 3.12+ first."
        Write-Info "Download from: https://www.python.org/downloads/"
        exit 1
    }
    
    $pythonVersion = python --version
    Write-Success "Found $pythonVersion"
}

function New-VirtualEnvironment {
    Write-BootstrapHeader "Setting up Expert Quantum Virtual Environment"
    
    if ((Test-Path ".venv") -and (!$Force)) {
        Write-Info "Virtual environment exists. Use -Force to recreate."
        return
    }
    
    if (Test-Path ".venv") {
        Write-Info "Removing existing virtual environment..."
        Remove-Item -Recurse -Force ".venv"
    }
    
    Write-Info "Creating new virtual environment..."
    python -m venv .venv
    
    Write-Info "Activating virtual environment..."
    & ".\.venv\Scripts\Activate.ps1"
    
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip
    
    Write-Success "Virtual environment ready"
}

function Install-Dependencies {
    Write-BootstrapHeader "Installing Expert Quantum Dependencies"
    
    if (!(Test-Path ".venv\Scripts\Activate.ps1")) {
        Write-Warning "Virtual environment not found"
        exit 1
    }
    
    & ".\.venv\Scripts\Activate.ps1"
    
    # Core dependencies
    $requirements = @'
# EQ12 Expert Quantum Core Dependencies
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.15.0
streamlit>=1.25.0
fastapi>=0.100.0
uvicorn>=0.23.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
alembic>=1.11.0
psycopg2-binary>=2.9.0
redis>=4.6.0
celery>=5.3.0
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
black>=23.7.0
isort>=5.12.0
flake8>=6.0.0
ruff>=0.0.280
mypy>=1.5.0
bandit>=1.7.0
safety>=2.3.0
pre-commit>=3.3.0
notebook>=7.0.0
jupyterlab>=4.0.0
ipywidgets>=8.0.0
requests>=2.31.0
aiohttp>=3.8.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
selenium>=4.11.0
playwright>=1.36.0
openai>=0.27.0
anthropic>=0.3.0
transformers>=4.32.0
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0
tensorflow>=2.13.0
tensorflow-probability>=0.21.0
'@

    Write-Info "Creating requirements.txt..."
    $requirements | Out-File -FilePath "requirements.txt" -Encoding UTF8
    
    Write-Info "Installing Python packages..."
    python -m pip install -r requirements.txt
    
    Write-Success "Dependencies installed"
}

function Install-PreCommitHooks {
    Write-BootstrapHeader "Setting up Expert Quantum Pre-commit Hooks"
    
    if (!(Test-Path ".venv\Scripts\Activate.ps1")) {
        Write-Warning "Virtual environment not found"
        return
    }
    
    & ".\.venv\Scripts\Activate.ps1"
    
    $preCommitConfig = @'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: debug-statements
      
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3
        
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
        
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.280
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
        
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, scripts/, -f, json, -o, logs/bandit-report.json]
        pass_filenames: false
'@

    Write-Info "Creating .pre-commit-config.yaml..."
    $preCommitConfig | Out-File -FilePath ".pre-commit-config.yaml" -Encoding UTF8
    
    Write-Info "Installing pre-commit hooks..."
    try {
        & ".\.venv\Scripts\pre-commit.exe" install
        Write-Success "Pre-commit hooks installed"
    }
    catch {
        Write-Warning "Pre-commit setup failed: $($_.Exception.Message)"
    }
}

function Test-DockerSetup {
    if ($SkipDocker) {
        Write-Info "Skipping Docker validation"
        return
    }
    
    Write-BootstrapHeader "Validating Expert Quantum Docker Setup"
    
    if (!(Test-Command docker)) {
        Write-Warning "Docker not found. Install Docker Desktop for full functionality."
        Write-Info "Download from: https://www.docker.com/products/docker-desktop"
        return
    }
    
    try {
        $dockerVersion = docker --version
        Write-Success "Found $dockerVersion"
        
        # Test Docker daemon
        docker info | Out-Null
        Write-Success "Docker daemon is running"
        
        if (Test-Command "docker-compose") {
            $composeVersion = docker-compose --version
            Write-Success "Found $composeVersion"
        }
        else {
            Write-Info "docker-compose not found, using 'docker compose'"
        }
        
    }
    catch {
        Write-Warning "Docker daemon not running: $($_.Exception.Message)"
    }
}

function New-DirectoryStructure {
    Write-BootstrapHeader "Creating Expert Quantum Directory Structure"
    
    $dirs = @(
        "scripts/google_ai_examples",
        "tests/pester", 
        "configs",
        "logs",
        "data/raw",
        "data/processed",
        "data/models",
        "dashboard/static",
        "dashboard/templates",
        "ops",
        "docs",
        ".github/workflows"
    )
    
    foreach ($dir in $dirs) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Info "Created directory: $dir"
        }
    }
    
    # Create __init__.py files
    $initDirs = @("scripts", "tests", "configs", "logs", "data", "dashboard")
    foreach ($dir in $initDirs) {
        $initFile = "$dir\__init__.py"
        if (!(Test-Path $initFile)) {
            "# EQ12 Expert Quantum Package" | Out-File -FilePath $initFile -Encoding UTF8
        }
    }
    
    Write-Success "Directory structure ready"
}

function New-VSCodeSettings {
    Write-BootstrapHeader "Configuring Expert Quantum VS Code Settings"
    
    if (!(Test-Path ".vscode")) {
        New-Item -ItemType Directory -Path ".vscode" -Force | Out-Null
    }
    
    $settings = @{
        "python.pythonPath"                = "./.venv/Scripts/python.exe"
        "python.linting.enabled"           = $true
        "python.linting.flake8Enabled"     = $true
        "python.formatting.provider"       = "black"
        "python.formatting.blackArgs"      = @("--line-length=88")
        "python.sortImports.args"          = @("--profile", "black")
        "python.testing.pytestEnabled"     = $true
        "python.testing.pytestArgs"        = @("tests/")
        "files.exclude"                    = @{
            "**/__pycache__" = $true
            "**/*.pyc"       = $true
            ".pytest_cache"  = $true
            "htmlcov"        = $true
        }
        "files.associations"               = @{
            "*.ps1" = "powershell"
        }
        "powershell.scriptAnalysis.enable" = $true
        "editor.formatOnSave"              = $true
        "editor.codeActionsOnSave"         = @{
            "source.organizeImports" = $true
        }
    }
    
    $settings | ConvertTo-Json -Depth 10 | Out-File -FilePath ".vscode/settings.json" -Encoding UTF8
    Write-Success "VS Code settings configured"
}

function Show-BootstrapSummary {
    Write-BootstrapHeader "Expert Quantum Bootstrap Complete!"
    
    Write-Host " Next Steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Activate virtual environment:" -ForegroundColor White
    Write-Host "   .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Run development tasks:" -ForegroundColor White
    Write-Host "   .\ops\make_fixed.ps1 lint" -ForegroundColor Gray
    Write-Host "   .\ops\make_fixed.ps1 test" -ForegroundColor Gray
    Write-Host "   .\ops\make_fixed.ps1 status" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Start development:" -ForegroundColor White
    Write-Host "   .\ops\make_fixed.ps1 up" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Access services:" -ForegroundColor White
    Write-Host "    Main app: http://localhost:8000" -ForegroundColor Gray
    Write-Host "    Dashboard: http://localhost:8080" -ForegroundColor Gray
    Write-Host "    Jupyter: http://localhost:8888" -ForegroundColor Gray
    Write-Host ""
    Write-Host " Development Tools Ready:" -ForegroundColor Cyan
    Write-Host "    Python virtual environment with 30+ packages" -ForegroundColor Gray
    Write-Host "    Pre-commit hooks for code quality" -ForegroundColor Gray
    Write-Host "    Docker containerization" -ForegroundColor Gray
    Write-Host "    VS Code integration" -ForegroundColor Gray
    Write-Host "    Testing framework with pytest" -ForegroundColor Gray
    Write-Host "    Linting with ruff, flake8, black, isort" -ForegroundColor Gray
    Write-Host "    Security scanning with bandit" -ForegroundColor Gray
    Write-Host ""
    Write-Host " Expert Quantum mode activated!" -ForegroundColor Magenta
}

# Main Bootstrap Execution
try {
    Write-BootstrapHeader "EQ12 Expert Quantum Bootstrap Starting"
    
    if ($VerboseOutput) {
        Write-Info "Running in verbose mode"
        Write-Info "Working directory: $(Get-Location)"
        Write-Info "PowerShell version: $($PSVersionTable.PSVersion)"
    }
    
    Install-PythonIfMissing
    New-DirectoryStructure
    New-VirtualEnvironment
    Install-Dependencies
    Install-PreCommitHooks
    Test-DockerSetup
    New-VSCodeSettings
    Show-BootstrapSummary
    
    Write-Success "Bootstrap completed successfully!"
    
}
catch {
    Write-Host " Bootstrap failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}