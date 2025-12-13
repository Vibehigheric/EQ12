# EQ12 Free Toolchain Bootstrap Script
# ====================================
# Purpose: First-run installer for free/open-source tools only
# Idempotent: Safe to run multiple times
# No paid APIs: Respects no-key/no-bill mode

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$SkipPrompts
)

$ErrorActionPreference = "Stop"
$InformationPreference = "Continue"

# Colors for PowerShell output
$Green = "Green"
$Yellow = "Yellow" 
$Red = "Red"
$Cyan = "Cyan"

function Write-StatusMessage {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host "🚀 $Message" -ForegroundColor $Color
}

function Write-SuccessMessage {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-WarningMessage {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Yellow
}

function Write-ErrorMessage {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-CommandExists {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Install-WingetIfMissing {
    Write-StatusMessage "Checking for winget..."
    
    if (Test-CommandExists "winget") {
        Write-SuccessMessage "winget is already installed"
        return $true
    }
    
    Write-WarningMessage "winget is not installed"
    Write-Host "Please install the Microsoft Store App Installer to get winget:" -ForegroundColor $Yellow
    Write-Host "https://apps.microsoft.com/detail/9NBLGGH4NNS1" -ForegroundColor $Cyan
    Write-Host ""
    Write-Host "Alternative: Install via GitHub releases:" -ForegroundColor $Yellow
    Write-Host "https://github.com/microsoft/winget-cli/releases" -ForegroundColor $Cyan
    
    if (-not $SkipPrompts) {
        $continue = Read-Host "Press Enter after installing winget, or 'q' to quit"
        if ($continue -eq 'q') {
            exit 1
        }
    }
    
    # Recheck after user installs
    if (Test-CommandExists "winget") {
        Write-SuccessMessage "winget detected successfully"
        return $true
    } else {
        Write-ErrorMessage "winget still not found. Please install it manually."
        return $false
    }
}

function Install-ToolWithWinget {
    param(
        [string]$PackageName,
        [string]$WingetId,
        [string]$CheckCommand = ""
    )
    
    Write-StatusMessage "Checking $PackageName..."
    
    # Use custom check command if provided, otherwise use the winget ID as the command
    $commandToCheck = if ($CheckCommand) { $CheckCommand } else { $WingetId.Split('.')[-1].ToLower() }
    
    if (Test-CommandExists $commandToCheck) {
        Write-SuccessMessage "$PackageName is already installed"
        return $true
    }
    
    Write-StatusMessage "Installing $PackageName via winget..."
    try {
        $result = winget install --id $WingetId --source winget --silent --accept-package-agreements --accept-source-agreements 2>&1
        
        if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq -1978335189) {
            # -1978335189 is "already installed" code
            Write-SuccessMessage "$PackageName installed successfully"
            
            # Refresh PATH for current session
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
            
            return $true
        } else {
            Write-WarningMessage "$PackageName installation may have failed (exit code: $LASTEXITCODE)"
            Write-Host "Output: $result" -ForegroundColor $Yellow
            return $false
        }
    } catch {
        Write-ErrorMessage "Failed to install $PackageName`: $_"
        return $false
    }
}

function Setup-PythonEnvironment {
    Write-StatusMessage "Setting up Python virtual environment..."
    
    # Check if .venv already exists
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        Write-SuccessMessage "Virtual environment already exists"
    } else {
        Write-StatusMessage "Creating Python virtual environment..."
        try {
            python -m venv .venv
            Write-SuccessMessage "Virtual environment created"
        } catch {
            Write-ErrorMessage "Failed to create virtual environment: $_"
            return $false
        }
    }
    
    # Activate environment
    Write-StatusMessage "Activating virtual environment..."
    try {
        & ".\.venv\Scripts\Activate.ps1"
        Write-SuccessMessage "Virtual environment activated"
    } catch {
        Write-ErrorMessage "Failed to activate virtual environment: $_"
        return $false
    }
    
    # Upgrade pip and install pip-tools
    Write-StatusMessage "Upgrading pip and installing pip-tools..."
    try {
        python -m pip install --upgrade pip pip-tools
        Write-SuccessMessage "pip and pip-tools updated"
    } catch {
        Write-ErrorMessage "Failed to update pip: $_"
        return $false
    }
    
    # Install requirements if requirements.txt exists
    if (Test-Path "requirements.txt") {
        Write-StatusMessage "Installing Python dependencies from requirements.txt..."
        try {
            pip-sync requirements.txt
            Write-SuccessMessage "Python dependencies installed"
        } catch {
            Write-WarningMessage "Failed to sync requirements.txt, trying regular pip install..."
            try {
                pip install -r requirements.txt
                Write-SuccessMessage "Python dependencies installed via pip install"
            } catch {
                Write-ErrorMessage "Failed to install Python dependencies: $_"
                return $false
            }
        }
    }
    
    return $true
}

function Setup-NodeEnvironment {
    Write-StatusMessage "Setting up Node.js environment..."
    
    # Install pnpm globally if not present
    if (-not (Test-CommandExists "pnpm")) {
        Write-StatusMessage "Installing pnpm..."
        try {
            npm install -g pnpm
            Write-SuccessMessage "pnpm installed"
        } catch {
            Write-WarningMessage "Failed to install pnpm: $_"
        }
    } else {
        Write-SuccessMessage "pnpm is already installed"
    }
    
    # Install dependencies if package.json exists
    if (Test-Path "package.json") {
        if (Test-Path "package-lock.json") {
            Write-StatusMessage "Installing Node.js dependencies with npm ci..."
            try {
                npm ci
                Write-SuccessMessage "Node.js dependencies installed"
            } catch {
                Write-WarningMessage "npm ci failed, trying npm install: $_"
                try {
                    npm install
                    Write-SuccessMessage "Node.js dependencies installed via npm install"
                } catch {
                    Write-ErrorMessage "Failed to install Node.js dependencies: $_"
                    return $false
                }
            }
        } else {
            Write-StatusMessage "Installing Node.js dependencies with npm install..."
            try {
                npm install
                Write-SuccessMessage "Node.js dependencies installed"
            } catch {
                Write-ErrorMessage "Failed to install Node.js dependencies: $_"
                return $false
            }
        }
    } else {
        Write-StatusMessage "No package.json found, creating minimal one..."
        $minimalPackageJson = @{
            "name" = "eq12-free-toolchain"
            "version" = "1.0.0"
            "description" = "EQ12 Free Toolchain"
            "private" = $true
            "scripts" = @{
                "test" = "echo `"No tests specified`""
            }
        } | ConvertTo-Json -Depth 3
        
        $minimalPackageJson | Out-File -FilePath "package.json" -Encoding utf8
        Write-SuccessMessage "Created minimal package.json"
    }
    
    return $true
}

function Setup-WindowsFirewallExclusions {
    if (-not (Test-Administrator)) {
        Write-WarningMessage "Firewall configuration requires administrator privileges"
        if (-not $SkipPrompts) {
            $configureFirewall = Read-Host "Configure Windows Firewall exclusions for development? (y/N)"
            if ($configureFirewall -eq 'y' -or $configureFirewall -eq 'Y') {
                Write-Host "Please run this script as Administrator to configure firewall settings" -ForegroundColor $Yellow
            }
        }
        return $false
    }
    
    Write-StatusMessage "Configuring Windows Firewall exclusions..."
    
    # Common development ports
    $ports = @(3000, 5000, 8000, 8080, 8888, 9000)
    
    foreach ($port in $ports) {
        try {
            $ruleName = "EQ12 Development Port $port"
            $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
            
            if (-not $existingRule) {
                New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort $port -Action Allow | Out-Null
                Write-SuccessMessage "Added firewall rule for port $port"
            }
        } catch {
            Write-WarningMessage "Failed to add firewall rule for port $port`: $_"
        }
    }
    
    return $true
}

function Show-InstallationSummary {
    Write-Host ""
    Write-Host "🎉 EQ12 FREE TOOLCHAIN BOOTSTRAP COMPLETE!" -ForegroundColor $Green
    Write-Host "==========================================" -ForegroundColor $Green
    Write-Host ""
    
    # Show installed versions
    $tools = @{
        "Git" = "git --version"
        "GitHub CLI" = "gh --version"
        "Python" = "python --version"
        "Node.js" = "node --version"
        "npm" = "npm --version"
        "pnpm" = "pnpm --version"
        "7-Zip" = "7z"
        "jq" = "jq --version"
    }
    
    Write-Host "Installed Tool Versions:" -ForegroundColor $Cyan
    Write-Host "------------------------" -ForegroundColor $Cyan
    
    foreach ($tool in $tools.GetEnumerator()) {
        try {
            if ($tool.Value -eq "7z") {
                # 7z just shows help, check if command exists
                if (Test-CommandExists "7z") {
                    Write-Host "✅ $($tool.Key): Available" -ForegroundColor $Green
                } else {
                    Write-Host "❌ $($tool.Key): Not found" -ForegroundColor $Red
                }
            } else {
                $version = Invoke-Expression $tool.Value 2>&1 | Select-Object -First 1
                Write-Host "✅ $($tool.Key): $version" -ForegroundColor $Green
            }
        } catch {
            Write-Host "❌ $($tool.Key): Not found or error" -ForegroundColor $Red
        }
    }
    
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor $Yellow
    Write-Host "----------" -ForegroundColor $Yellow
    Write-Host "1. Run: scripts\eq12_update_all.ps1" -ForegroundColor $White
    Write-Host "2. Run: scripts\eq12_env_check.ps1" -ForegroundColor $White
    Write-Host "3. Run: python eq12_free_smoke_test.py" -ForegroundColor $White
    Write-Host ""
    Write-Host "VS Code Tasks Available:" -ForegroundColor $Yellow
    Write-Host "- EQ12: Bootstrap (free)" -ForegroundColor $White
    Write-Host "- EQ12: Update all" -ForegroundColor $White
    Write-Host "- EQ12: Lint+Fix (Ruff)" -ForegroundColor $White
    Write-Host "- EQ12: Smoke test" -ForegroundColor $White
    Write-Host ""
}

# Main execution
function Start-Bootstrap {
    Write-Host ""
    Write-Host "🚀 EQ12 FREE TOOLCHAIN BOOTSTRAP" -ForegroundColor $Green
    Write-Host "================================" -ForegroundColor $Green
    Write-Host "Installing only free/open-source tools" -ForegroundColor $Cyan
    Write-Host ""
    
    # Check if winget is available
    if (-not (Install-WingetIfMissing)) {
        Write-ErrorMessage "Cannot proceed without winget"
        exit 1
    }
    
    # Install core tools
    $coreTools = @(
        @{ Name = "Git"; Id = "Git.Git"; CheckCommand = "git" },
        @{ Name = "GitHub CLI"; Id = "GitHub.cli"; CheckCommand = "gh" },
        @{ Name = "Python 3.12"; Id = "Python.Python.3.12"; CheckCommand = "python" },
        @{ Name = "Node.js LTS"; Id = "OpenJS.NodeJS.LTS"; CheckCommand = "node" },
        @{ Name = "7-Zip"; Id = "7zip.7zip"; CheckCommand = "7z" },
        @{ Name = "jq"; Id = "jqlang.jq"; CheckCommand = "jq" }
    )
    
    Write-Host "Installing core development tools..." -ForegroundColor $Cyan
    $installSuccess = $true
    
    foreach ($tool in $coreTools) {
        $success = Install-ToolWithWinget -PackageName $tool.Name -WingetId $tool.Id -CheckCommand $tool.CheckCommand
        if (-not $success) {
            $installSuccess = $false
        }
    }
    
    # Optional: Visual Studio Build Tools
    if (-not $SkipPrompts) {
        $installBuildTools = Read-Host "Install Visual Studio Build Tools for Python native extensions? (y/N)"
        if ($installBuildTools -eq 'y' -or $installBuildTools -eq 'Y') {
            Install-ToolWithWinget -PackageName "VS Build Tools" -WingetId "Microsoft.VisualStudio.2022.BuildTools" -CheckCommand ""
        }
    }
    
    # Setup Python environment
    if (-not (Setup-PythonEnvironment)) {
        Write-ErrorMessage "Python environment setup failed"
        $installSuccess = $false
    }
    
    # Setup Node.js environment
    if (-not (Setup-NodeEnvironment)) {
        Write-ErrorMessage "Node.js environment setup failed"
        $installSuccess = $false
    }
    
    # Optional firewall configuration
    Setup-WindowsFirewallExclusions | Out-Null
    
    # Show summary
    Show-InstallationSummary
    
    if (-not $installSuccess) {
        Write-ErrorMessage "Some installations failed. Please check the output above."
        exit 1
    }
    
    Write-SuccessMessage "Bootstrap completed successfully!"
    return 0
}

# Script entry point
try {
    Start-Bootstrap
} catch {
    Write-ErrorMessage "Bootstrap failed: $_"
    exit 1
}