#  Expert Quantum: Complete EQ12 Repo Transformation

## Copy-Paste Copilot Chat Prompt

```
Transform this workspace into an Expert Quantum development environment with complete infrastructure modernization. Execute this comprehensive upgrade:

** PRIMARY OBJECTIVES:**
1. **Infrastructure Modernization**: Implement production-grade DevContainer, Docker, CI/CD workflows
2. **Code Quality Enforcement**: Set up comprehensive linting, formatting, testing, security scanning  
3. **Development Experience**: Create one-command setup, automated tasks, VS Code integration
4. **Documentation & Standards**: Establish complete project documentation and coding standards

** REQUIRED FILE STRUCTURE:**
Create these files exactly as specified:

**`.devcontainer/devcontainer.json`**:
```json
{
  "name": "EQ12 Expert Quantum",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "eq12-dev", 
  "workspaceFolder": "/workspace",
  "postCreateCommand": "ops/bootstrap_clean.ps1",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.black-formatter", 
        "ms-python.isort",
        "charliermarsh.ruff",
        "ms-python.flake8",
        "ms-toolsai.jupyter",
        "redhat.vscode-yaml",
        "ms-vscode.powershell",
        "eamodio.gitlens",
        "github.copilot",
        "github.copilot-chat"
      ]
    }
  },
  "forwardPorts": [8000, 8080, 8888],
  "remoteUser": "vscode"
}
```

**`Dockerfile`**:
```dockerfile
FROM python:3.12-slim as base
WORKDIR /workspace
RUN apt-get update && apt-get install -y git curl build-essential && rm -rf /var/lib/apt/lists/*

FROM base as development  
RUN useradd -m vscode && chown -R vscode:vscode /workspace
USER vscode
COPY requirements.txt .
RUN pip install --user -r requirements.txt
EXPOSE 8000 8080 8888

FROM base as production
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scripts/ scripts/
COPY data/ data/  
COPY configs/ configs/
EXPOSE 8000
CMD ["python", "scripts/eq12_main.py"]
```

**`docker-compose.yml`** (enhance existing):
Add this service to your existing docker-compose.yml:
```yaml
  eq12-dev:
    build:
      context: .
      target: development
    ports:
      - "8000:8000"
      - "8080:8080" 
      - "8888:8888"
    volumes:
      - .:/workspace
      - eq12-vscode-extensions:/home/vscode/.vscode-server/extensions
    environment:
      - PYTHONPATH=/workspace
    depends_on:
      - redis
      - postgres-dataviz

volumes:
  eq12-vscode-extensions:
```

**`.github/workflows/expert-quantum-ci.yml`**:
```yaml
name: Expert Quantum CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  quality:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.12]
    
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Lint with Ruff
      run: ruff check .
    
    - name: Format check with Black  
      run: black --check .
    
    - name: Type check with mypy
      run: mypy scripts/
    
    - name: Security scan with Bandit
      run: bandit -r scripts/
    
    - name: Test with pytest
      run: pytest --cov=scripts --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    runs-on: ubuntu-latest
    needs: quality
    
    steps:
    - uses: actions/checkout@v4
    - name: Build Docker images
      run: |
        docker build --target development -t eq12:dev .
        docker build --target production -t eq12:prod .
```

**`ops/bootstrap_clean.ps1`** (create automation script):
```powershell
#!/usr/bin/env pwsh
param([switch]$Force, [switch]$SkipDocker, [switch]$VerboseOutput)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Write-Warning($msg) { Write-Host "[WARNING] $msg" -ForegroundColor Yellow }

try {
    Write-Host "[BOOTSTRAP] EQ12 Expert Quantum Starting" -ForegroundColor Magenta

    # Setup virtual environment
    if ((Test-Path ".venv") -and $Force) {
        Remove-Item -Recurse -Force ".venv"
    }
    if (!(Test-Path ".venv")) {
        python -m venv .venv
        & ".\.venv\Scripts\Activate.ps1"
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    }

    # Install pre-commit hooks
    & ".\.venv\Scripts\Activate.ps1"
    pre-commit install

    Write-Success "Bootstrap completed! Run: .\ops\make_clean.ps1 status"
} catch {
    Write-Host "[ERROR] Bootstrap failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
```

**`ops/make_clean.ps1`** (task runner):
```powershell
#!/usr/bin/env pwsh
param([string]$Task = "help", [string]$Service = "", [switch]$VerboseOutput)

switch ($Task.ToLower()) {
    "lint" { 
        & ".\.venv\Scripts\Activate.ps1"
        ruff check . --fix
        flake8 . --max-line-length=88
        bandit -r scripts/
    }
    "test" { 
        & ".\.venv\Scripts\Activate.ps1"
        pytest -v --cov=scripts --cov-report=html
    }
    "format" {
        & ".\.venv\Scripts\Activate.ps1" 
        black .
        isort . --profile black
    }
    "up" { docker compose up -d }
    "down" { docker compose down }
    "status" {
        Write-Host "EQ12 Expert Quantum Status:" -ForegroundColor Cyan
        python --version
        docker compose ps
    }
    default { 
        Write-Host "Tasks: lint, test, format, up, down, status" -ForegroundColor Cyan
    }
}
```

**`requirements.txt`** (comprehensive):
```
# Core Data Science
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
plotly>=5.15.0

# Web Framework  
fastapi>=0.100.0
streamlit>=1.25.0
uvicorn>=0.23.0

# Database
sqlalchemy>=2.0.0
alembic>=1.11.0
psycopg2-binary>=2.9.0
redis>=4.6.0

# AI/ML
openai>=0.27.0
anthropic>=0.3.0
torch>=2.0.0
tensorflow>=2.13.0

# Development Tools
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.7.0
ruff>=0.0.280
mypy>=1.5.0
bandit>=1.7.0
pre-commit>=3.3.0
```

**`.pre-commit-config.yaml`**:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json

  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort  
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.280
    hooks:
      - id: ruff
        args: [--fix]
```

** EXECUTION STEPS:**
1. **Create all files above in the exact structure shown**
2. **Run setup**: `.\ops\bootstrap_clean.ps1` 
3. **Test workflow**: `.\ops\make_clean.ps1 status`
4. **Start services**: `.\ops\make_clean.ps1 up`

** SUCCESS CRITERIA:**
-  One-command environment setup 
-  Automated code quality checks
-  Docker containerization working
-  CI/CD pipeline configured
-  VS Code DevContainer ready
-  Pre-commit hooks active

** IMMEDIATE ACTIONS:**
Execute this transformation now. Create every file exactly as specified. This will modernize your EQ12 workspace with production-grade infrastructure, automated quality control, and streamlined development workflow.

** Result**: Complete Expert Quantum development environment ready for accelerated productivity and professional-grade code delivery.
```

##  What This Prompt Delivers

When you paste this prompt into Copilot Chat, it will:

1. **Create Complete Infrastructure**: DevContainer, Docker, CI/CD workflows
2. **Set Up Automation**: One-command bootstrap and task runner scripts  
3. **Implement Quality Controls**: Linting, formatting, testing, security scanning
4. **Configure VS Code**: Full extension integration and workspace settings
5. **Establish Standards**: Pre-commit hooks, code formatting, documentation

##  Immediate Next Steps

1. **Copy the prompt above** (the entire text block in the code fence)
2. **Paste into Copilot Chat** in VS Code
3. **Let Copilot create all files** as specified
4. **Run**: `.\ops\bootstrap_clean.ps1` to initialize
5. **Test**: `.\ops\make_clean.ps1 status` to verify setup

##  Verification Commands

After Copilot completes the transformation:

```powershell
# Test the Expert Quantum environment
.\ops\make_clean.ps1 status
.\ops\make_clean.ps1 lint  
.\ops\make_clean.ps1 test
.\ops\make_clean.ps1 up
```

##  Expert Quantum Features Activated

- **Production DevContainer** with Python 3.12, extensions, port forwarding
- **Multi-stage Docker builds** for development and production
- **Comprehensive CI/CD** with quality gates, testing, security scanning  
- **Automated task runner** for lint, test, format, deploy operations
- **Pre-commit hooks** ensuring code quality before commits
- **VS Code integration** with 10+ productivity extensions
- **One-command setup** for new developers joining the project

Your EQ12 workspace will be transformed into a modern, professional development environment with all the tools and automation needed for accelerated productivity.