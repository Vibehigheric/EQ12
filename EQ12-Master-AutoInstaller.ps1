#Requires -RunAsAdministrator
<#
.SYNOPSIS
EQ12 Master Auto-Installer and Persistence Manager

.DESCRIPTION
Comprehensive installation, auto-start, and persistence system for the complete EQ12
sports betting and automation stack including:
- Visual Studio Build Tools & VB.NET
- Python data science & betting packages
- Node.js browser automation
- GitHub CLI, Git, APIs
- LLM clients (OpenAI, Gemini)
- Telegram, Discord, ngrok
- WordPress development tools
- Auto-startup and persistence mechanisms

.PARAMETER Action
Action to perform: Install, Update, Repair, Configure, Status, Uninstall

.PARAMETER Force
Force reinstallation of components

.PARAMETER AutoStart
Configure auto-start mechanisms

.PARAMETER CreateScheduledTasks
Create Windows scheduled tasks for persistence

.EXAMPLE
.\EQ12-Master-AutoInstaller.ps1 -Action Install -AutoStart -CreateScheduledTasks

.NOTES
Author: EQ12 Development Team
Version: 2.0.0
Requires: PowerShell 5.1+ running as Administrator
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('Install', 'Update', 'Repair', 'Configure', 'Status', 'Uninstall')]
    [string]$Action = 'Install',

    [switch]$Force,
    [switch]$AutoStart,
    [switch]$CreateScheduledTasks,
    [switch]$Verbose,
    [switch]$Silent
)

# ================================
# CONFIGURATION & GLOBALS
# ================================

$EQ12Root = "C:\EQ12"
$LogsDir = Join-Path $EQ12Root "logs"
$ConfigsDir = Join-Path $EQ12Root "configs"
$ScriptsDir = Join-Path $EQ12Root "scripts"
$InstallDir = Join-Path $EQ12Root "installation"
$ScheduledTasksDir = Join-Path $EQ12Root "scheduled_tasks"

$LogFile = Join-Path $LogsDir "master_installer_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# Component Installation Status Tracking
$InstallationState = @{
    Chocolatey       = $false
    GitHubCLI        = $false
    Git              = $false
    Python           = $false
    NodeJS           = $false
    VSBuildTools     = $false
    VSCode           = $false
    PHP              = $false
    SQLServerExpress = $false
    ngrok            = $false
    PythonPackages   = $false
    NodePackages     = $false
    WordPressTools   = $false
    LLMClients       = $false
    ScheduledTasks   = $false
    AutoStartup      = $false
}

# Required Python Packages for Sports Betting & Automation
$PythonPackages = @(
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "scikit-learn>=1.3.0",
    "xgboost>=1.7.0",
    "lightgbm>=4.0.0",
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    "selenium>=4.15.0",
    "playwright>=1.40.0",
    "flask>=2.3.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "gunicorn>=21.2.0",
    "python-telegram-bot>=20.7.0",
    "discord.py>=2.3.0",
    "openai>=1.3.0",
    "google-generativeai>=0.3.0",
    "betfairlightweight>=2.17.0",
    "oddsapi-client>=1.0.0",
    "tweepy>=4.14.0",
    "python-dotenv>=1.0.0",
    "sqlalchemy>=2.0.0",
    "psycopg2>=2.9.0",
    "pymongo>=4.6.0",
    "redis>=5.0.0",
    "celery>=5.3.0",
    "apscheduler>=3.10.0",
    "yfinance>=0.2.0",
    "alpha-vantage>=2.3.0",
    "ccxt>=4.1.0"
)

# Required Node.js Packages
$NodePackages = @(
    "yarn",
    "@playwright/test",
    "puppeteer",
    "http-server",
    "express",
    "socket.io",
    "axios",
    "@azure/openai",
    "openai",
    "discord.js",
    "telegraf",
    "node-cron",
    "cheerio",
    "jsdom"
)

# Chocolatey Packages
$ChocoPackages = @(
    "gh",
    "git",
    "python",
    "nodejs",
    "visualstudio2022buildtools --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools --add Microsoft.VisualStudio.Workload.NETBuildTools",
    "vscode",
    "php",
    "sql-server-express",
    "ngrok",
    "wget",
    "curl",
    "7zip",
    "jq"
)

# ================================
# UTILITY FUNCTIONS
# ================================

function Write-EQ12Log {
    param(
        [string]$Message,
        [ValidateSet('Info', 'Warning', 'Error', 'Success')]
        [string]$Level = 'Info',
        [string]$Icon = "📋"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    # Console output with colors
    $color = switch ($Level) {
        'Info' { 'Cyan' }
        'Warning' { 'Yellow' }
        'Error' { 'Red' }
        'Success' { 'Green' }
    }

    if (-not $Silent) {
        Write-Host "$Icon $Message" -ForegroundColor $color
    }

    # File logging
    if (Test-Path $LogsDir) {
        Add-Content -Path $LogFile -Value $logMessage
    }
}

function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Initialize-EQ12Directories {
    $directories = @($EQ12Root, $LogsDir, $ConfigsDir, $ScriptsDir, $InstallDir, $ScheduledTasksDir)

    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-EQ12Log "Created directory: $dir" -Level Success -Icon "📁"
        }
    }
}

function Test-InternetConnection {
    try {
        $response = Invoke-WebRequest -Uri "https://www.google.com" -UseBasicParsing -TimeoutSec 10
        return $response.StatusCode -eq 200
    }
    catch {
        return $false
    }
}

function Install-Chocolatey {
    Write-EQ12Log "Installing Chocolatey package manager..." -Icon "🍫"

    try {
        if (Get-Command choco -ErrorAction SilentlyContinue) {
            Write-EQ12Log "Chocolatey already installed" -Level Success -Icon "✅"
            $InstallationState.Chocolatey = $true
            return $true
        }

        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        if (Get-Command choco -ErrorAction SilentlyContinue) {
            Write-EQ12Log "Chocolatey installed successfully" -Level Success -Icon "✅"
            $InstallationState.Chocolatey = $true
            return $true
        }
        else {
            throw "Chocolatey installation verification failed"
        }
    }
    catch {
        Write-EQ12Log "Failed to install Chocolatey: $($_.Exception.Message)" -Level Error -Icon "❌"
        return $false
    }
}

function Install-ChocoPackages {
    Write-EQ12Log "Installing core packages via Chocolatey..." -Icon "📦"

    if (-not $InstallationState.Chocolatey) {
        Write-EQ12Log "Chocolatey not available, cannot install packages" -Level Error -Icon "❌"
        return $false
    }

    foreach ($package in $ChocoPackages) {
        try {
            Write-EQ12Log "Installing: $package" -Icon "⬬"

            if ($package -like "*visualstudio*") {
                # Visual Studio Build Tools requires special handling
                $result = Start-Process -FilePath "choco" -ArgumentList "install", $package, "-y", "--no-progress" -Wait -PassThru -WindowStyle Hidden
            }
            else {
                $result = Start-Process -FilePath "choco" -ArgumentList "install", $package, "-y" -Wait -PassThru -WindowStyle Hidden
            }

            if ($result.ExitCode -eq 0 -or $result.ExitCode -eq 1641 -or $result.ExitCode -eq 3010) {
                Write-EQ12Log "Successfully installed: $package" -Level Success -Icon "✅"

                # Update installation state
                switch -Wildcard ($package) {
                    "gh" { $InstallationState.GitHubCLI = $true }
                    "git" { $InstallationState.Git = $true }
                    "python" { $InstallationState.Python = $true }
                    "nodejs" { $InstallationState.NodeJS = $true }
                    "*visualstudio*" { $InstallationState.VSBuildTools = $true }
                    "vscode" { $InstallationState.VSCode = $true }
                    "php" { $InstallationState.PHP = $true }
                    "*sql-server*" { $InstallationState.SQLServerExpress = $true }
                    "ngrok" { $InstallationState.ngrok = $true }
                }
            }
            else {
                Write-EQ12Log "Failed to install: $package (Exit code: $($result.ExitCode))" -Level Warning -Icon "⚠️"
            }
        }
        catch {
            Write-EQ12Log "Error installing $package : $($_.Exception.Message)" -Level Error -Icon "❌"
        }

        Start-Sleep -Seconds 2
    }

    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

function Install-PythonPackages {
    Write-EQ12Log "Installing Python packages for sports betting and automation..." -Icon "🐍"

    if (-not $InstallationState.Python) {
        Write-EQ12Log "Python not available, skipping package installation" -Level Warning -Icon "⚠️"
        return $false
    }

    try {
        # Upgrade pip first
        Write-EQ12Log "Upgrading pip..." -Icon "⬆️"
        $result = Start-Process -FilePath "python" -ArgumentList "-m", "pip", "install", "--upgrade", "pip" -Wait -PassThru -WindowStyle Hidden

        if ($result.ExitCode -ne 0) {
            Write-EQ12Log "Failed to upgrade pip" -Level Warning -Icon "⚠️"
        }

        # Install packages in batches to avoid timeout
        $batchSize = 5
        $batches = @()

        for ($i = 0; $i -lt $PythonPackages.Count; $i += $batchSize) {
            $end = [Math]::Min($i + $batchSize - 1, $PythonPackages.Count - 1)
            $batches += , @($PythonPackages[$i..$end])
        }

        foreach ($batch in $batches) {
            $packageList = $batch -join " "
            Write-EQ12Log "Installing Python batch: $($batch -join ', ')" -Icon "📦"

            $result = Start-Process -FilePath "python" -ArgumentList "-m", "pip", "install", $batch -Wait -PassThru -WindowStyle Hidden

            if ($result.ExitCode -eq 0) {
                Write-EQ12Log "Successfully installed batch" -Level Success -Icon "✅"
            }
            else {
                Write-EQ12Log "Failed to install some packages in batch" -Level Warning -Icon "⚠️"
            }

            Start-Sleep -Seconds 2
        }

        $InstallationState.PythonPackages = $true
        Write-EQ12Log "Python package installation completed" -Level Success -Icon "✅"
        return $true
    }
    catch {
        Write-EQ12Log "Error installing Python packages: $($_.Exception.Message)" -Level Error -Icon "❌"
        return $false
    }
}

function Install-NodePackages {
    Write-EQ12Log "Installing Node.js packages..." -Icon "📦"

    if (-not $InstallationState.NodeJS) {
        Write-EQ12Log "Node.js not available, skipping package installation" -Level Warning -Icon "⚠️"
        return $false
    }

    try {
        foreach ($package in $NodePackages) {
            Write-EQ12Log "Installing Node package: $package" -Icon "⬬"

            $result = Start-Process -FilePath "npm" -ArgumentList "install", "-g", $package -Wait -PassThru -WindowStyle Hidden

            if ($result.ExitCode -eq 0) {
                Write-EQ12Log "Successfully installed: $package" -Level Success -Icon "✅"
            }
            else {
                Write-EQ12Log "Failed to install: $package" -Level Warning -Icon "⚠️"
            }

            Start-Sleep -Seconds 1
        }

        $InstallationState.NodePackages = $true
        return $true
    }
    catch {
        Write-EQ12Log "Error installing Node.js packages: $($_.Exception.Message)" -Level Error -Icon "❌"
        return $false
    }
}

function Install-WordPressTools {
    Write-EQ12Log "Installing WordPress development tools..." -Icon "🌐"

    try {
        # Install WP-CLI
        $wpCliPath = Join-Path $EQ12Root "wp-cli"
        if (-not (Test-Path $wpCliPath)) {
            New-Item -ItemType Directory -Path $wpCliPath -Force | Out-Null
        }

        $wpCliPhar = Join-Path $wpCliPath "wp-cli.phar"

        Write-EQ12Log "Downloading WP-CLI..." -Icon "⬇️"
        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar" -OutFile $wpCliPhar

        # Create wp.bat wrapper
        $wpBat = Join-Path $wpCliPath "wp.bat"
        @"
@echo off
php "$wpCliPhar" %*
"@ | Out-File -FilePath $wpBat -Encoding ASCII

        # Add to PATH
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        if ($currentPath -notlike "*$wpCliPath*") {
            [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$wpCliPath", "User")
        }

        $InstallationState.WordPressTools = $true
        Write-EQ12Log "WordPress tools installed successfully" -Level Success -Icon "✅"
        return $true
    }
    catch {
        Write-EQ12Log "Error installing WordPress tools: $($_.Exception.Message)" -Level Error -Icon "❌"
        return $false
    }
}

function Install-LLMClients {
    Write-EQ12Log "Configuring LLM API clients..." -Icon "🤖"

    try {
        # Create API configuration template
        $apiConfig = @{
            openai       = @{
                api_key    = ""
                model      = "gpt-4"
                max_tokens = 4096
            }
            gemini       = @{
                api_key = ""
                model   = "gemini-pro"
            }
            telegram     = @{
                bot_token = ""
                chat_id   = ""
            }
            discord      = @{
                bot_token = ""
                guild_id  = ""
            }
            twitter      = @{
                api_key             = ""
                api_secret          = ""
                access_token        = ""
                access_token_secret = ""
                bearer_token        = ""
            }
            betting_apis = @{
                odds_api_key     = ""
                betfair_username = ""
                betfair_password = ""
                betfair_app_key  = ""
            }
        }

        $configFile = Join-Path $ConfigsDir "api_credentials.json"
        $apiConfig | ConvertTo-Json -Depth 3 | Out-File -FilePath $configFile -Encoding UTF8

        Write-EQ12Log "Created API configuration template: $configFile" -Level Success -Icon "✅"
        Write-EQ12Log "Please update the configuration file with your actual API keys" -Level Warning -Icon "⚠️"

        $InstallationState.LLMClients = $true
        return $true
    }
    catch {
        Write-EQ12Log "Error configuring LLM clients: $($_.Exception.Message)" -Level Error -Icon "❌"
        return $false
    }
}

function Create-ScheduledTasks {
    Write-EQ12Log "Creating Windows scheduled tasks for persistence..." -Icon "⏰"

    try {
        # Task 1: EQ12 System Health Monitor (runs every 30 minutes)
        $healthMonitorAction = New-ScheduledTaskAction -Execute "python" -Argument "$ScriptsDir\eq12_health_monitor.py" -WorkingDirectory $EQ12Root
        $healthMonitorTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Days 365)
        $healthMonitorSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

        Register-ScheduledTask -TaskName "EQ12-HealthMonitor" -Action $healthMonitorAction -Trigger $healthMonitorTrigger -Settings $healthMonitorSettings -Description "EQ12 System Health Monitor" -Force

        # Task 2: EQ12 Sports Data Updater (runs every 2 hours)
        $dataUpdaterAction = New-ScheduledTaskAction -Execute "python" -Argument "$ScriptsDir\eq12_sports_data_updater.py" -WorkingDirectory $EQ12Root
        $dataUpdaterTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 2) -RepetitionDuration (New-TimeSpan -Days 365)
        $dataUpdaterSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

        Register-ScheduledTask -TaskName "EQ12-SportsDataUpdater" -Action $dataUpdaterAction -Trigger $dataUpdaterTrigger -Settings $dataUpdaterSettings -Description "EQ12 Sports Data Updater" -Force

        # Task 3: EQ12 Installation Validator (runs at startup and daily)
        $validatorAction = New-ScheduledTaskAction -Execute "powershell" -Argument "-ExecutionPolicy Bypass -File `"$PSCommandPath`" -Action Status" -WorkingDirectory $EQ12Root
        $validatorTriggerStartup = New-ScheduledTaskTrigger -AtStartup
        $validatorTriggerDaily = New-ScheduledTaskTrigger -Daily -At "06:00"
        $validatorSettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

        Register-ScheduledTask -TaskName "EQ12-InstallationValidator" -Action $validatorAction -Trigger @($validatorTriggerStartup, $validatorTriggerDaily) -Settings $validatorSettings -Description "EQ12 Installation Validator and Auto-Repair" -Force

        Write-EQ12Log "Scheduled tasks created successfully" -Level Success -Icon "✅"
        $InstallationState.ScheduledTasks = $true
        return $true
    }
    catch {
        Write-EQ12Log "Error creating scheduled tasks: $($_.Exception.Message)" -Level Error -Icon "❌"
        return $false
    }
}

function Configure-AutoStartup {
    Write-EQ12Log "Configuring auto-startup mechanisms..." -Icon "🚀"

    try {
        # Create startup script
        $startupScript = @"
# EQ12 Auto-Startup Script
# This script runs at system startup to ensure EQ12 services are running

Set-Location "$EQ12Root"

# Start EQ12 Core Services
if (Test-Path "$ScriptsDir\eq12_core_service.py") {
    Start-Process python -ArgumentList "$ScriptsDir\eq12_core_service.py" -WindowStyle Hidden
}

# Start ngrok if configured
if (Test-Path "$ConfigsDir\ngrok.yml") {
    Start-Process ngrok -ArgumentList "start --config $ConfigsDir\ngrok.yml --all" -WindowStyle Hidden
}

# Verify installation status
Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`" -Action Status -Silent" -WindowStyle Hidden
"@

        $startupScriptPath = Join-Path $EQ12Root "EQ12-Startup.ps1"
        $startupScript | Out-File -FilePath $startupScriptPath -Encoding UTF8

        # Add to Windows startup (registry method)
        $registryPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
        $registryName = "EQ12-AutoStart"
        $registryValue = "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$startupScriptPath`""

        Set-ItemProperty -Path $registryPath -Name $registryName -Value $registryValue

        Write-EQ12Log "Auto-startup configured successfully" -Level Success -Icon "✅"
        $InstallationState.AutoStartup = $true
        return $true
    }
    catch {
        Write-EQ12Log "Error configuring auto-startup: $($_.Exception.Message)" -Level Error -Icon "❌"
        return $false
    }
}

function Test-InstallationStatus {
    Write-EQ12Log "Testing installation status..." -Icon "🔍"

    $results = @{}

    # Test Chocolatey
    try {
        $null = Get-Command choco -ErrorAction Stop
        $results.Chocolatey = @{ Status = "Installed"; Version = (choco --version) }
    }
    catch {
        $results.Chocolatey = @{ Status = "Not Installed"; Version = $null }
    }

    # Test Git & GitHub CLI
    try {
        $gitVersion = git --version
        $results.Git = @{ Status = "Installed"; Version = $gitVersion }
    }
    catch {
        $results.Git = @{ Status = "Not Installed"; Version = $null }
    }

    try {
        $ghVersion = gh --version | Select-Object -First 1
        $results.GitHubCLI = @{ Status = "Installed"; Version = $ghVersion }
    }
    catch {
        $results.GitHubCLI = @{ Status = "Not Installed"; Version = $null }
    }

    # Test Python
    try {
        $pythonVersion = python --version
        $results.Python = @{ Status = "Installed"; Version = $pythonVersion }
    }
    catch {
        $results.Python = @{ Status = "Not Installed"; Version = $null }
    }

    # Test Node.js
    try {
        $nodeVersion = node --version
        $results.NodeJS = @{ Status = "Installed"; Version = $nodeVersion }
    }
    catch {
        $results.NodeJS = @{ Status = "Not Installed"; Version = $null }
    }

    # Test ngrok
    try {
        $ngrokVersion = ngrok version
        $results.ngrok = @{ Status = "Installed"; Version = $ngrokVersion }
    }
    catch {
        $results.ngrok = @{ Status = "Not Installed"; Version = $null }
    }

    return $results
}

function Show-InstallationReport {
    param([hashtable]$Results)

    Write-EQ12Log "=== EQ12 INSTALLATION STATUS REPORT ===" -Level Success -Icon "📊"

    foreach ($component in $Results.Keys) {
        $status = $Results[$component]
        $icon = if ($status.Status -eq "Installed") { "✅" } else { "❌" }
        $version = if ($status.Version) { "($($status.Version))" } else { "" }

        Write-EQ12Log "$component : $($status.Status) $version" -Icon $icon
    }

    # Count installed components
    $installed = ($Results.Values | Where-Object { $_.Status -eq "Installed" }).Count
    $total = $Results.Count

    Write-EQ12Log "Installation Progress: $installed/$total components installed" -Level Info -Icon "📈"
}

# ================================
# MAIN INSTALLATION LOGIC
# ================================

function Invoke-MasterInstallation {
    Write-EQ12Log "🏈 Starting EQ12 Master Installation System" -Level Success -Icon "🚀"

    # Pre-flight checks
    if (-not (Test-AdminRights)) {
        Write-EQ12Log "This script requires Administrator privileges. Please run as Administrator." -Level Error -Icon "❌"
        exit 1
    }

    if (-not (Test-InternetConnection)) {
        Write-EQ12Log "Internet connection required for installation. Please check your connection." -Level Error -Icon "❌"
        exit 1
    }

    # Initialize directories
    Initialize-EQ12Directories

    # Phase 1: Core System Installation
    Write-EQ12Log "=== PHASE 1: CORE SYSTEM INSTALLATION ===" -Level Success -Icon "🔧"

    if (-not (Install-Chocolatey)) {
        Write-EQ12Log "Failed to install Chocolatey. Aborting installation." -Level Error -Icon "❌"
        exit 1
    }

    Install-ChocoPackages

    # Phase 2: Language-Specific Packages
    Write-EQ12Log "=== PHASE 2: LANGUAGE-SPECIFIC PACKAGES ===" -Level Success -Icon "📦"

    Install-PythonPackages
    Install-NodePackages
    Install-WordPressTools
    Install-LLMClients

    # Phase 3: Persistence and Auto-Start
    if ($CreateScheduledTasks) {
        Write-EQ12Log "=== PHASE 3: PERSISTENCE CONFIGURATION ===" -Level Success -Icon "⏰"
        Create-ScheduledTasks
    }

    if ($AutoStart) {
        Configure-AutoStartup
    }

    # Final status report
    Write-EQ12Log "=== INSTALLATION COMPLETE ===" -Level Success -Icon "🎉"
    $results = Test-InstallationStatus
    Show-InstallationReport -Results $results

    Write-EQ12Log "EQ12 Master Installation completed successfully!" -Level Success -Icon "✅"
    Write-EQ12Log "Log file: $LogFile" -Level Info -Icon "📝"
}

function Invoke-StatusCheck {
    Write-EQ12Log "🔍 EQ12 Installation Status Check" -Level Info -Icon "📊"

    $results = Test-InstallationStatus
    Show-InstallationReport -Results $results

    # Check scheduled tasks
    $tasks = Get-ScheduledTask -TaskName "EQ12-*" -ErrorAction SilentlyContinue
    Write-EQ12Log "Scheduled Tasks: $($tasks.Count) EQ12 tasks found" -Icon "⏰"

    # Check auto-startup
    $startupEntry = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "EQ12-AutoStart" -ErrorAction SilentlyContinue
    $autoStartStatus = if ($startupEntry) { "Configured" } else { "Not Configured" }
    Write-EQ12Log "Auto-Startup: $autoStartStatus" -Icon "🚀"
}

function Invoke-RepairInstallation {
    Write-EQ12Log "🔧 Starting EQ12 Installation Repair" -Level Warning -Icon "🛠️"

    # Check what's missing and reinstall
    $results = Test-InstallationStatus

    foreach ($component in $results.Keys) {
        if ($results[$component].Status -ne "Installed") {
            Write-EQ12Log "Repairing: $component" -Level Warning -Icon "🔧"

            switch ($component) {
                "Chocolatey" { Install-Chocolatey }
                "Python" { Start-Process -FilePath "choco" -ArgumentList "install", "python", "-y", "--force" -Wait }
                "NodeJS" { Start-Process -FilePath "choco" -ArgumentList "install", "nodejs", "-y", "--force" -Wait }
                "Git" { Start-Process -FilePath "choco" -ArgumentList "install", "git", "-y", "--force" -Wait }
                "GitHubCLI" { Start-Process -FilePath "choco" -ArgumentList "install", "gh", "-y", "--force" -Wait }
                "ngrok" { Start-Process -FilePath "choco" -ArgumentList "install", "ngrok", "-y", "--force" -Wait }
            }
        }
    }

    Write-EQ12Log "Repair process completed" -Level Success -Icon "✅"
}

# ================================
# MAIN EXECUTION
# ================================

try {
    switch ($Action) {
        'Install' {
            Invoke-MasterInstallation
        }
        'Status' {
            Invoke-StatusCheck
        }
        'Repair' {
            Invoke-RepairInstallation
        }
        'Update' {
            Write-EQ12Log "Updating EQ12 installation..." -Icon "⬆️"
            # Force reinstall with latest versions
            $Force = $true
            Invoke-MasterInstallation
        }
        'Configure' {
            Write-EQ12Log "Configuring EQ12 settings..." -Icon "⚙️"
            Install-LLMClients
            if ($AutoStart) { Configure-AutoStartup }
            if ($CreateScheduledTasks) { Create-ScheduledTasks }
        }
        'Uninstall' {
            Write-EQ12Log "Uninstalling EQ12 components..." -Level Warning -Icon "🗑️"
            # Remove scheduled tasks
            Get-ScheduledTask -TaskName "EQ12-*" | Unregister-ScheduledTask -Confirm:$false
            # Remove startup entry
            Remove-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name "EQ12-AutoStart" -ErrorAction SilentlyContinue
            Write-EQ12Log "EQ12 persistence components removed" -Level Success -Icon "✅"
        }
    }
}
catch {
    Write-EQ12Log "Fatal error during $Action operation: $($_.Exception.Message)" -Level Error -Icon "💥"
    exit 1
}

Write-EQ12Log "EQ12 Master Auto-Installer operation completed: $Action" -Level Success -Icon "🎯"
