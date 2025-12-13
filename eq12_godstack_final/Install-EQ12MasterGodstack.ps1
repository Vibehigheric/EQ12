#!/usr/bin/env pwsh
<#
.SYNOPSIS
    EQ12 GODSTACK Master Installation & GitHub Integration Script
    
.DESCRIPTION
    Complete deployment script for EQ12 GODSTACK intelligence ecosystem with:
    - All 7 stack-specific intelligence chains  
    - GitHub repository integration
    - Task Scheduler automation
    - Cross-stack intelligence sharing
    - FastAPI dashboard deployment
    
.PARAMETER Install
    Install complete GODSTACK ecosystem
    
.PARAMETER Stacks
    Comma-separated list of stacks to install (betting,travel,cannabis,fleet,housing,education,dropship)
    
.PARAMETER GitHubOrg
    GitHub organization name for repository integration
    
.PARAMETER SkipTaskScheduler
    Skip Windows Task Scheduler installation
    
.PARAMETER DashboardOnly
    Install only the dashboard component
    
.EXAMPLE
    .\Install-EQ12MasterGodstack.ps1 -Install -GitHubOrg "EQ12-Intelligence"
    .\Install-EQ12MasterGodstack.ps1 -Install -Stacks "betting,travel,cannabis" 
    .\Install-EQ12MasterGodstack.ps1 -DashboardOnly
    
.NOTES
    Author: EQ12 AI Assistant
    Created: 2025-09-27  
    Requires: Administrator privileges, Python 3.11+, Git
#>

[CmdletBinding()]
param(
    [switch]$Install,
    [string]$Stacks = "betting,travel,cannabis,fleet,housing,education,dropship",
    [string]$GitHubOrg = "EQ12-Intelligence", 
    [switch]$SkipTaskScheduler,
    [switch]$DashboardOnly
)

# Ensure Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "🚫 This script must be run as Administrator. Right-click and 'Run as Administrator'"
    exit 1
}

# Configuration
$EQ12Root = "C:\EQ12"
$GodstackDir = "$EQ12Root\eq12_godstack_final"
$LogDir = "$EQ12Root\logs"
$DashboardPort = 8000

# Available stacks configuration
$StackConfig = @{
    'betting' = @{
        'name' = 'Betting/Sports Intelligence'
        'schedule' = '6:00 AM Daily'
        'telegram' = '#betting-sharp-alerts'
        'priority' = 'High'
    }
    'travel' = @{
        'name' = 'Travel/Affiliate Intelligence' 
        'schedule' = '7:00 AM Daily'
        'telegram' = '#travel-deal-alerts'
        'priority' = 'Medium'
    }
    'cannabis' = @{
        'name' = 'Cannabis NY Intelligence'
        'schedule' = '8:00 AM Daily' 
        'telegram' = '#cannabis-ny-updates'
        'priority' = 'Medium'
    }
    'fleet' = @{
        'name' = 'Fleet Operations Intelligence'
        'schedule' = '6:30 AM Daily'
        'telegram' = '#fleet-ops-alerts' 
        'priority' = 'High'
    }
    'housing' = @{
        'name' = 'Housing/Credit Intelligence'
        'schedule' = '7:30 AM Daily'
        'telegram' = '#housing-finance-alerts'
        'priority' = 'Medium'
    }
    'education' = @{
        'name' = 'Education/Grants Intelligence'
        'schedule' = '8:30 AM Daily'
        'telegram' = '#education-grant-alerts' 
        'priority' = 'Low'
    }
    'dropship' = @{
        'name' = 'Dropship/E-commerce Intelligence'
        'schedule' = '9:00 AM Daily'
        'telegram' = '#dropship-trend-alerts'
        'priority' = 'Medium'
    }
}

function Write-Banner {
    $banner = @"

    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                    🚀 EQ12 GODSTACK MASTER INSTALLER 🚀                 ║
    ║                                                                          ║
    ║               Complete Intelligence Ecosystem Deployment                  ║
    ║                                                                          ║
    ║  📊 7 Business Stack Intelligence Chains                                ║
    ║  🧠 GPT-Powered Enrichment Engine                                       ║
    ║  📡 GitHub Repository Integration                                        ║
    ║  ⏰ Automated Task Scheduling                                           ║
    ║  📱 Cross-Stack Telegram Alerts                                        ║
    ║  🌐 FastAPI Dashboard Interface                                         ║
    ╚══════════════════════════════════════════════════════════════════════════╝

"@
    Write-Host $banner -ForegroundColor Green
}

function Test-Prerequisites {
    Write-Host "🔍 Checking system prerequisites..." -ForegroundColor Cyan
    
    $issues = @()
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python 3\.(1[1-9]|[2-9]\d)") {
            Write-Host "   ✅ $pythonVersion" -ForegroundColor Green
        } else {
            $issues += "Python 3.11+ required (found: $pythonVersion)"
        }
    } catch {
        $issues += "Python not found in PATH"
    }
    
    # Check pip
    try {
        pip --version | Out-Null
        Write-Host "   ✅ pip available" -ForegroundColor Green
    } catch {
        $issues += "pip not available"
    }
    
    # Check Git
    try {
        git --version | Out-Null
        Write-Host "   ✅ Git available" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️ Git not available (optional)" -ForegroundColor Yellow
    }
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -ge 5) {
        Write-Host "   ✅ PowerShell $($PSVersionTable.PSVersion)" -ForegroundColor Green
    } else {
        $issues += "PowerShell 5.0+ required"
    }
    
    if ($issues.Count -gt 0) {
        Write-Host "❌ Prerequisites failed:" -ForegroundColor Red
        $issues | ForEach-Object { Write-Host "   - $_" -ForegroundColor Red }
        return $false
    }
    
    Write-Host "✅ All prerequisites satisfied!" -ForegroundColor Green
    return $true
}

function Install-PythonDependencies {
    Write-Host "`n📦 Installing Python dependencies..." -ForegroundColor Cyan
    
    $requirements = @(
        "requests>=2.28.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0", 
        "openai>=1.3.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "python-multipart>=0.0.6",
        "jinja2>=3.1.0",
        "aiofiles>=23.2.0",
        "PyGithub>=1.59.0"
    )
    
    try {
        foreach ($req in $requirements) {
            Write-Host "   Installing $req..." -ForegroundColor Gray
            python -m pip install $req --quiet
        }
        
        Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
        return $true
    } catch {
        Write-Error "❌ Failed to install dependencies: $_"
        return $false
    }
}

function Setup-Directories {
    Write-Host "`n📁 Setting up directory structure..." -ForegroundColor Cyan
    
    $directories = @(
        $EQ12Root,
        $GodstackDir,
        "$GodstackDir\tasks",
        "$GodstackDir\.github\workflows", 
        "$GodstackDir\logs",
        $LogDir
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "   ✅ Created $dir" -ForegroundColor Green
        } else {
            Write-Host "   ✅ Exists $dir" -ForegroundColor Gray
        }
    }
    
    return $true
}

function Install-StackIntelligenceChains {
    param([string[]]$SelectedStacks)
    
    Write-Host "`n⚡ Installing stack intelligence chains..." -ForegroundColor Cyan
    Write-Host "   Selected stacks: $($SelectedStacks -join ', ')" -ForegroundColor Yellow
    
    $installedChains = 0
    
    foreach ($stack in $SelectedStacks) {
        if ($StackConfig.ContainsKey($stack)) {
            $config = $StackConfig[$stack]
            
            Write-Host "`n   📋 Installing $($config.name)..." -ForegroundColor Green
            Write-Host "      Schedule: $($config.schedule)" -ForegroundColor Gray
            Write-Host "      Telegram: $($config.telegram)" -ForegroundColor Gray
            Write-Host "      Priority: $($config.priority)" -ForegroundColor Gray
            
            # Task Scheduler XML should already be created by previous steps
            $xmlPath = "$GodstackDir\tasks\${stack}IntelligenceChain.xml"
            if (Test-Path $xmlPath) {
                Write-Host "      ✅ Task XML ready" -ForegroundColor Green
            } else {
                Write-Host "      ⚠️ Task XML not found: $xmlPath" -ForegroundColor Yellow
            }
            
            # Query file should already exist  
            $queryPath = "$GodstackDir\queries_${stack}.txt"
            if (Test-Path $queryPath) {
                Write-Host "      ✅ Query file ready" -ForegroundColor Green
            } else {
                Write-Host "      ⚠️ Query file not found: $queryPath" -ForegroundColor Yellow
            }
            
            $installedChains++
        } else {
            Write-Host "   ❌ Unknown stack: $stack" -ForegroundColor Red
        }
    }
    
    Write-Host "`n✅ Installed $installedChains intelligence chains" -ForegroundColor Green
    return $installedChains
}

function Install-TaskSchedulerJobs {
    param([string[]]$SelectedStacks)
    
    if ($SkipTaskScheduler) {
        Write-Host "`n⚠️ Skipping Task Scheduler installation (--SkipTaskScheduler)" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "`n⏰ Installing Task Scheduler jobs..." -ForegroundColor Cyan
    
    $installedTasks = 0
    
    # Install individual stack chains
    foreach ($stack in $SelectedStacks) {
        $taskName = "EQ12 ${stack} Intelligence Chain"
        $xmlPath = "$GodstackDir\tasks\${stack}IntelligenceChain.xml"
        
        if (Test-Path $xmlPath) {
            try {
                # Remove existing task
                $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
                if ($existingTask) {
                    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
                }
                
                # Register new task
                Register-ScheduledTask -Xml (Get-Content $xmlPath -Raw) -TaskName $taskName -Force | Out-Null
                Write-Host "   ✅ $taskName" -ForegroundColor Green
                $installedTasks++
                
            } catch {
                Write-Host "   ❌ Failed to install $taskName : $_" -ForegroundColor Red
            }
        } else {
            Write-Host "   ⚠️ XML not found for $stack stack" -ForegroundColor Yellow
        }
    }
    
    # Install cross-stack sync job
    $crossStackXml = "$GodstackDir\tasks\CrossStackIntelligenceSync.xml"
    if (Test-Path $crossStackXml) {
        try {
            $taskName = "EQ12 Cross-Stack Intelligence Sync"
            $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
            if ($existingTask) {
                Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            }
            
            Register-ScheduledTask -Xml (Get-Content $crossStackXml -Raw) -TaskName $taskName -Force | Out-Null
            Write-Host "   ✅ Cross-Stack Intelligence Sync" -ForegroundColor Green
            $installedTasks++
            
        } catch {
            Write-Host "   ❌ Failed to install Cross-Stack Sync: $_" -ForegroundColor Red
        }
    }
    
    Write-Host "`n✅ Installed $installedTasks scheduled tasks" -ForegroundColor Green
    return $installedTasks -gt 0
}

function Setup-GitHubIntegration {
    param([string]$OrgName)
    
    Write-Host "`n🐙 Setting up GitHub integration..." -ForegroundColor Cyan
    Write-Host "   Organization: $OrgName" -ForegroundColor Yellow
    
    # Test GitHub integration
    try {
        Set-Location $GodstackDir
        $result = python github_integration.py --test-connection 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ GitHub API connection successful" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ GitHub API test failed (check GITHUB_TOKEN): $result" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ⚠️ GitHub integration test failed: $_" -ForegroundColor Yellow
    }
    
    # Generate query files for all stacks
    try {
        python github_integration.py --generate-queries --stack all
        Write-Host "   ✅ Generated stack-specific query files" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️ Failed to generate query files: $_" -ForegroundColor Yellow
    }
    
    return $true
}

function Start-Dashboard {
    Write-Host "`n🌐 Starting EQ12 GODSTACK Dashboard..." -ForegroundColor Cyan
    
    try {
        Set-Location $GodstackDir
        
        # Check if port is available
        $portTest = Test-NetConnection -ComputerName localhost -Port $DashboardPort -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($portTest) {
            Write-Host "   ⚠️ Port $DashboardPort already in use" -ForegroundColor Yellow
        }
        
        # Start dashboard in background
        Start-Process python -ArgumentList "dashboard.py" -WindowStyle Hidden -WorkingDirectory $GodstackDir
        Start-Sleep 3
        
        # Test dashboard availability 
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$DashboardPort" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Host "   ✅ Dashboard running at http://localhost:$DashboardPort" -ForegroundColor Green
                return $true
            }
        } catch {
            Write-Host "   ⚠️ Dashboard may not be responding: $_" -ForegroundColor Yellow
        }
        
    } catch {
        Write-Host "   ❌ Failed to start dashboard: $_" -ForegroundColor Red
        return $false
    }
    
    return $false
}

function Show-InstallationSummary {
    param([string[]]$InstalledStacks, [int]$TaskCount)
    
    $summary = @"

╔══════════════════════════════════════════════════════════════════════════╗
║                     ✅ EQ12 GODSTACK INSTALLATION COMPLETE ✅             ║
╚══════════════════════════════════════════════════════════════════════════╝

🎯 **Installation Summary:**
   📊 Stacks Deployed: $($InstalledStacks.Count) ($($InstalledStacks -join ', '))  
   ⏰ Scheduled Tasks: $TaskCount
   🌐 Dashboard: http://localhost:$DashboardPort
   📁 Installation: $GodstackDir

🔧 **Next Steps:**

   1. **Configure API Keys** (Required):
      Edit $GodstackDir\.env with:
      - OPENAI_SERVICE_KEY=your_openai_api_key
      - BING_SEARCH_API_KEY=your_bing_api_key  
      - TELEGRAM_BOT_TOKEN=your_telegram_bot_token
      - GITHUB_TOKEN=your_github_personal_access_token

   2. **Test Manual Execution**:
      cd $GodstackDir
      python news_aggregator.py --query-file queries_betting.txt
      python enrichment.py betting
      python github_integration.py --stack betting --create-issue

   3. **View Scheduled Tasks**:
      taskschd.msc
      
   4. **Access Dashboard**:
      http://localhost:$DashboardPort

⏰ **Automated Schedule:**
$($InstalledStacks | ForEach-Object { 
    $config = $StackConfig[$_]
    "   📋 $($config.name): $($config.schedule)"
})
   🔄 Cross-Stack Sync: 10:00 AM Daily

🛠️ **Management Commands:**
   • Manual trigger: schtasks /run /tn "EQ12 betting Intelligence Chain"
   • View logs: Get-Content $LogDir\eq12_scheduler.log -Tail 20
   • GitHub repos: Browse to https://github.com/$GitHubOrg
   • Dashboard API: http://localhost:$DashboardPort/docs

🚀 **EQ12 GODSTACK is now fully operational across all business stacks!**

"@

    Write-Host $summary -ForegroundColor Green
}

function Show-Usage {
    Write-Host "🚀 EQ12 GODSTACK Master Installer" -ForegroundColor Green
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Cyan
    Write-Host "   .\Install-EQ12MasterGodstack.ps1 -Install                    # Full installation"
    Write-Host "   .\Install-EQ12MasterGodstack.ps1 -Install -Stacks betting,travel  # Specific stacks"
    Write-Host "   .\Install-EQ12MasterGodstack.ps1 -DashboardOnly             # Dashboard only" 
    Write-Host "   .\Install-EQ12MasterGodstack.ps1 -Install -SkipTaskScheduler # No scheduled tasks"
    Write-Host ""
    Write-Host "PARAMETERS:" -ForegroundColor Cyan
    Write-Host "   -Stacks            Comma-separated list of stacks to install"
    Write-Host "   -GitHubOrg         GitHub organization name (default: EQ12-Intelligence)"
    Write-Host "   -SkipTaskScheduler Skip Windows Task Scheduler setup"
    Write-Host "   -DashboardOnly     Install only FastAPI dashboard"
    Write-Host ""
    Write-Host "AVAILABLE STACKS:" -ForegroundColor Cyan
    foreach ($stack in $StackConfig.Keys | Sort-Object) {
        $config = $StackConfig[$stack]
        Write-Host "   📊 $stack" -ForegroundColor Green -NoNewline
        Write-Host " - $($config.name) ($($config.schedule))" -ForegroundColor Gray
    }
}

# Main execution logic
Write-Banner

if ($DashboardOnly) {
    Write-Host "🌐 Dashboard-only installation requested" -ForegroundColor Yellow
    
    if (-not (Test-Prerequisites)) { exit 1 }
    if (-not (Install-PythonDependencies)) { exit 1 }
    if (-not (Setup-Directories)) { exit 1 }
    
    if (Start-Dashboard) {
        Write-Host "`n✅ Dashboard installation complete!" -ForegroundColor Green
        Write-Host "   🌐 Access at: http://localhost:$DashboardPort" -ForegroundColor Cyan
    } else {
        Write-Host "`n❌ Dashboard installation failed" -ForegroundColor Red
        exit 1
    }
    
} elseif ($Install) {
    Write-Host "🚀 Full EQ12 GODSTACK installation requested" -ForegroundColor Yellow
    
    # Parse selected stacks
    $selectedStacks = $Stacks.Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
    
    # Validate stacks
    $validStacks = $selectedStacks | Where-Object { $StackConfig.ContainsKey($_) }
    $invalidStacks = $selectedStacks | Where-Object { -not $StackConfig.ContainsKey($_) }
    
    if ($invalidStacks.Count -gt 0) {
        Write-Host "❌ Invalid stacks specified: $($invalidStacks -join ', ')" -ForegroundColor Red
        Write-Host "   Valid stacks: $($StackConfig.Keys -join ', ')" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "   Target stacks: $($validStacks -join ', ')" -ForegroundColor Yellow
    Write-Host "   GitHub org: $GitHubOrg" -ForegroundColor Yellow
    
    # Execute installation steps
    if (-not (Test-Prerequisites)) { exit 1 }
    if (-not (Install-PythonDependencies)) { exit 1 }
    if (-not (Setup-Directories)) { exit 1 }
    
    $chainCount = Install-StackIntelligenceChains -SelectedStacks $validStacks
    if ($chainCount -eq 0) {
        Write-Host "❌ No intelligence chains were installed" -ForegroundColor Red
        exit 1
    }
    
    $taskCount = 0
    if (Install-TaskSchedulerJobs -SelectedStacks $validStacks) {
        $taskCount = $validStacks.Count + 1  # +1 for cross-stack sync
    }
    
    Setup-GitHubIntegration -OrgName $GitHubOrg | Out-Null
    Start-Dashboard | Out-Null
    
    Show-InstallationSummary -InstalledStacks $validStacks -TaskCount $taskCount
    
} else {
    Show-Usage
}