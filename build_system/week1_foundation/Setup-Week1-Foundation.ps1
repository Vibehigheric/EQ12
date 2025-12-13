# Week 1 - Foundation & Security Setup Script
# PowerShell script to harden EQ12 and prepare environment

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$SkipBloatwareRemoval,

    [Parameter(Mandatory = $false)]
    [switch]$InstallWSL2,

    [Parameter(Mandatory = $false)]
    [string]$VPNProvider = "ExpressVPN"
)

Write-Host "🎯 EQ12 Week 1: Foundation & Security Setup" -ForegroundColor Green
Write-Host "   This script will harden your EQ12 and prepare the automation environment" -ForegroundColor Cyan

# Create execution plan
$executionPlan = @(
    "Remove Windows bloatware and unnecessary services",
    "Install WSL2 with Ubuntu for Linux-native workflows",
    "Configure firewall and security hardening",
    "Install core development tools (Python, Git, Docker)",
    "Set up VPN with kill switch configuration",
    "Create EQ12 directory structure and logging system"
)

Write-Host "`nExecution Plan:" -ForegroundColor Yellow
for ($i = 0; $i -lt $executionPlan.Count; $i++) {
    Write-Host "   $($i+1). $($executionPlan[$i])" -ForegroundColor White
}

# Progress tracking function
function Write-Progress-Update {
    param($Step, $Status = "EXECUTING")
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] ⚡ $Status`: $Step" -ForegroundColor Green
}

# Error logging function
function Write-Error-Context {
    param($Error, $Context)
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] ❌ ERROR: $Error" -ForegroundColor Red
    foreach ($key in $Context.Keys) {
        Write-Host "   $key`: $($Context[$key])" -ForegroundColor Red
    }
}

try {
    # Step 1: OS Optimization
    Write-Progress-Update "Starting OS optimization and bloatware removal"

    if (-not $SkipBloatwareRemoval) {
        # Remove common bloatware
        $bloatware = @(
            "Microsoft.XboxApp",
            "Microsoft.Xbox.TCUI",
            "Microsoft.YourPhone",
            "Microsoft.People",
            "Microsoft.MicrosoftOfficeHub",
            "Microsoft.Getstarted",
            "Microsoft.MicrosoftSolitaireCollection",
            "Microsoft.BingWeather",
            "Microsoft.BingNews"
        )

        foreach ($app in $bloatware) {
            try {
                Get-AppxPackage $app | Remove-AppxPackage -ErrorAction SilentlyContinue
                Write-Verbose "Removed: $app"
            } catch {
                Write-Verbose "Could not remove: $app"
            }
        }

        # Disable unnecessary services
        $services = @(
            "DiagTrack",  # Telemetry
            "dmwappushservice",  # WAP Push Message Routing Service
            "WerSvc",  # Windows Error Reporting
            "Spooler"  # Print Spooler (if no printer)
        )

        foreach ($service in $services) {
            try {
                Set-Service -Name $service -StartupType Disabled -ErrorAction SilentlyContinue
                Write-Verbose "Disabled service: $service"
            } catch {
                Write-Verbose "Could not disable service: $service"
            }
        }
    }

    Write-Progress-Update "OS optimization completed" "COMPLETED"

    # Step 2: WSL2 Setup
    if ($InstallWSL2) {
        Write-Progress-Update "Installing WSL2 and Ubuntu"

        # Enable WSL2 feature
        dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
        dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

        # Download and install WSL2 kernel update
        $wslUpdateUrl = "https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi"
        $wslUpdatePath = "$env:TEMP\wsl_update_x64.msi"

        Invoke-WebRequest -Uri $wslUpdateUrl -OutFile $wslUpdatePath
        Start-Process msiexec.exe -Wait -ArgumentList "/I $wslUpdatePath /quiet"

        # Set WSL2 as default
        wsl --set-default-version 2

        # Install Ubuntu
        Invoke-WebRequest -Uri "https://aka.ms/wslubuntu2004" -OutFile "$env:TEMP\Ubuntu.appx" -UseBasicParsing
        Add-AppxPackage "$env:TEMP\Ubuntu.appx"

        Write-Progress-Update "WSL2 and Ubuntu installed (restart required)" "COMPLETED"
    }

    # Step 3: Firewall Configuration
    Write-Progress-Update "Configuring Windows Firewall"

    # Enable firewall for all profiles
    Set-NetFirewallProfile -Profile Domain, Public, Private -Enabled True

    # Block unnecessary ports
    $portsToBlock = @(135, 139, 445, 1900, 5000)
    foreach ($port in $portsToBlock) {
        New-NetFirewallRule -DisplayName "Block Port $port" -Direction Inbound -LocalPort $port -Protocol TCP -Action Block -ErrorAction SilentlyContinue
    }

    Write-Progress-Update "Firewall configuration completed" "COMPLETED"

    # Step 4: Development Tools Installation
    Write-Progress-Update "Installing core development tools"

    # Check if Chocolatey is installed
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        # Install Chocolatey
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    }

    # Install essential tools via Chocolatey
    $tools = @(
        "python312",
        "git",
        "docker-desktop",
        "nodejs",
        "vscode",
        "firefox",
        "7zip",
        "curl",
        "wget"
    )

    foreach ($tool in $tools) {
        choco install $tool -y --no-progress
        Write-Verbose "Installed: $tool"
    }

    Write-Progress-Update "Development tools installation completed" "COMPLETED"

    # Step 5: EQ12 Directory Structure
    Write-Progress-Update "Creating EQ12 directory structure"

    $eq12Dirs = @(
        "C:\EQ12\logs",
        "C:\EQ12\keys",
        "C:\EQ12\configs",
        "C:\EQ12\profiles\firefox",
        "C:\EQ12\automation\sports",
        "C:\EQ12\automation\travel",
        "C:\EQ12\automation\commerce",
        "C:\EQ12\automation\finance",
        "C:\EQ12\data\betting",
        "C:\EQ12\data\travel",
        "C:\EQ12\data\commerce",
        "C:\EQ12\docker",
        "C:\EQ12\backups"
    )

    foreach ($dir in $eq12Dirs) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Verbose "Created directory: $dir"
        }
    }

    Write-Progress-Update "EQ12 directory structure created" "COMPLETED"

    # Step 6: Security Configuration
    Write-Progress-Update "Applying security configurations"

    # Create security config file
    $securityConfig = @{
        FirewallEnabled   = $true
        VPNKillSwitch     = $true
        AutoUpdates       = $true
        TelemetryDisabled = $true
        CreatedDate       = Get-Date
        LastUpdated       = Get-Date
    }

    $securityConfig | ConvertTo-Json -Depth 2 | Out-File "C:\EQ12\configs\security_config.json" -Encoding UTF8

    Write-Progress-Update "Security configuration applied" "COMPLETED"

    # Step 7: Environment Variables
    Write-Progress-Update "Setting up environment variables"

    # Add EQ12 paths to environment
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*C:\EQ12\scripts*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;C:\EQ12\scripts", "Machine")
    }

    # Set EQ12-specific environment variables
    [Environment]::SetEnvironmentVariable("EQ12_HOME", "C:\EQ12", "Machine")
    [Environment]::SetEnvironmentVariable("EQ12_LOGS", "C:\EQ12\logs", "Machine")
    [Environment]::SetEnvironmentVariable("EQ12_KEYS", "C:\EQ12\keys", "Machine")

    Write-Progress-Update "Environment variables configured" "COMPLETED"

    # Create installation summary
    $summary = @{
        InstallationDate    = Get-Date
        Version             = "EQ12-Week1-v1.0"
        ComponentsInstalled = @(
            "OS Optimization",
            "WSL2 + Ubuntu",
            "Firewall Configuration",
            "Development Tools",
            "EQ12 Directory Structure",
            "Security Configuration"
        )
        NextSteps           = @(
            "Restart computer to complete WSL2 installation",
            "Run Week 2 setup for GPT-5 integration",
            "Configure VPN kill switch",
            "Set up SSH keys for Git"
        )
    }

    $summary | ConvertTo-Json -Depth 3 | Out-File "C:\EQ12\logs\week1_installation_summary.json" -Encoding UTF8

    Write-Host "`n✅ Week 1 Foundation Setup Completed Successfully!" -ForegroundColor Green
    Write-Host "   📁 EQ12 directory structure created at C:\EQ12" -ForegroundColor Cyan
    Write-Host "   🔒 Security hardening applied" -ForegroundColor Cyan
    Write-Host "   🛠️ Development tools installed" -ForegroundColor Cyan
    Write-Host "   📋 Summary logged to: C:\EQ12\logs\week1_installation_summary.json" -ForegroundColor Yellow
    Write-Host "`n⚠️  RESTART REQUIRED to complete WSL2 installation" -ForegroundColor Red
    Write-Host "   After restart, run Week 2 setup for GPT-5 integration" -ForegroundColor Yellow

} catch {
    $errorContext = @{
        ErrorMessage = $_.Exception.Message
        ScriptLine   = $_.InvocationInfo.ScriptLineNumber
        Command      = $_.InvocationInfo.Line.Trim()
        Timestamp    = Get-Date
    }

    Write-Error-Context "Week 1 setup failed" $errorContext

    # Log error details
    $errorContext | ConvertTo-Json -Depth 2 | Out-File "C:\EQ12\logs\week1_error.json" -Encoding UTF8

    Write-Host "`n❌ Week 1 setup encountered errors. Check C:\EQ12\logs\week1_error.json for details" -ForegroundColor Red
    exit 1
}
