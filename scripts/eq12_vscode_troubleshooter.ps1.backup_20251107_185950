#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Visual Studio Code Troubleshooter - Professional-Level Diagnostics and Auto-Repair
    
.DESCRIPTION
    Comprehensive VS Code troubleshooting script that automatically diagnoses and fixes common issues:
    - Build errors and dependency problems
    - Cache corruption and IntelliSense issues  
    - GitHub Copilot integration problems
    - Project configuration mismatches
    - Node.js and Python environment issues
    
.PARAMETER Action
    Troubleshooting action to perform: Full, Clean, Dependencies, Cache, Copilot, Config, Test
    
.PARAMETER Workspace
    Path to workspace/project directory (default: current directory)
    
.PARAMETER GenerateReport
    Generate detailed fix report in logs directory
    
.EXAMPLE
    .\eq12_vscode_troubleshooter.ps1 -Action Full
    Runs complete diagnostic and repair cycle
    
.EXAMPLE
    .\eq12_vscode_troubleshooter.ps1 -Action Dependencies -Workspace "C:\MyProject"
    Fixes dependency issues in specific workspace
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('Full', 'Clean', 'Dependencies', 'Cache', 'Copilot', 'Config', 'Test', 'Quick')]
    [string]$Action = 'Full',
    
    [Parameter(Mandatory = $false)]
    [string]$Workspace = $PWD.Path,
    
    [Parameter(Mandatory = $false)]
    [switch]$GenerateReport,
    
    [Parameter(Mandatory = $false)]
    [switch]$AutoFix = $true
)

# Initialize logging
$LogDir = "C:\EQ12\logs"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$LogDir\vscode_troubleshooter_$Timestamp.log"
$ReportFile = "$LogDir\VSCode_FixReport_$Timestamp.txt"

if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-EQ12Log {
    param(
        [string]$Level,
        [string]$Message,
        [object]$Data = $null
    )
    
    $LogEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        level = $Level
        message = $Message
        workspace = $Workspace
        action = $Action
    }
    
    if ($Data) {
        $LogEntry.data = $Data
    }
    
    $JsonLog = $LogEntry | ConvertTo-Json -Compress
    Add-Content -Path $LogFile -Value $JsonLog
    
    $Color = switch ($Level) {
        'ERROR' { 'Red' }
        'WARN' { 'Yellow' }
        'SUCCESS' { 'Green' }
        'INFO' { 'Cyan' }
        default { 'White' }
    }
    
    Write-Host "[$Level] $Message" -ForegroundColor $Color
}

function Test-Prerequisites {
    Write-EQ12Log "INFO" "🔍 Checking VS Code prerequisites..."
    
    $issues = @()
    
    # Check VS Code installation
    $vscodePaths = @(
        "${env:LOCALAPPDATA}\Programs\Microsoft VS Code\Code.exe",
        "${env:ProgramFiles}\Microsoft VS Code\Code.exe",
        "${env:ProgramFiles(x86)}\Microsoft VS Code\Code.exe"
    )
    
    $vscodeInstalled = $false
    foreach ($path in $vscodePaths) {
        if (Test-Path $path) {
            $vscodeInstalled = $true
            Write-EQ12Log "SUCCESS" "✅ VS Code found at: $path"
            break
        }
    }
    
    if (!$vscodeInstalled) {
        $issues += "VS Code not found in standard locations"
        Write-EQ12Log "ERROR" "❌ VS Code installation not detected"
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>$null
        if ($nodeVersion) {
            Write-EQ12Log "SUCCESS" "✅ Node.js version: $nodeVersion"
        } else {
            $issues += "Node.js not available in PATH"
        }
    } catch {
        $issues += "Node.js not installed or not in PATH"
    }
    
    # Check Python
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-EQ12Log "SUCCESS" "✅ Python version: $pythonVersion"
        } else {
            $issues += "Python not available in PATH"
        }
    } catch {
        $issues += "Python not installed or not in PATH"
    }
    
    return $issues
}

function Clear-VSCodeCache {
    Write-EQ12Log "INFO" "🧹 Clearing VS Code cache and temporary files..."
    
    $cacheLocations = @(
        "$env:APPDATA\Code\User\workspaceStorage",
        "$env:APPDATA\Code\logs",
        "$env:APPDATA\Code\CachedExtensions",
        "$env:LOCALAPPDATA\Microsoft\vscode-cpptools",
        "$Workspace\.vscode\settings.json.bak*"
    )
    
    $cleared = @()
    
    foreach ($location in $cacheLocations) {
        if (Test-Path $location) {
            try {
                Remove-Item -Path $location -Recurse -Force -ErrorAction Stop
                $cleared += $location
                Write-EQ12Log "SUCCESS" "✅ Cleared: $location"
            } catch {
                Write-EQ12Log "ERROR" "❌ Failed to clear: $location - $($_.Exception.Message)"
            }
        }
    }
    
    # Clear project-specific caches
    $projectCaches = @(
        "$Workspace\.vs",
        "$Workspace\.vscode\.ropeproject",
        "$Workspace\node_modules\.cache",
        "$Workspace\__pycache__",
        "$Workspace\.pytest_cache"
    )
    
    foreach ($cache in $projectCaches) {
        if (Test-Path $cache) {
            try {
                Remove-Item -Path $cache -Recurse -Force
                $cleared += $cache
                Write-EQ12Log "SUCCESS" "✅ Cleared project cache: $cache"
            } catch {
                Write-EQ12Log "WARN" "⚠️ Could not clear: $cache"
            }
        }
    }
    
    return $cleared
}

function Repair-Dependencies {
    Write-EQ12Log "INFO" "🔧 Repairing project dependencies..."
    
    Push-Location $Workspace
    $repairs = @()
    
    try {
        # Node.js projects
        if (Test-Path "package.json") {
            Write-EQ12Log "INFO" "📦 Found Node.js project, repairing npm dependencies..."
            
            # Clear npm cache
            npm cache clean --force 2>$null
            
            # Remove node_modules and package-lock.json
            if (Test-Path "node_modules") {
                Remove-Item "node_modules" -Recurse -Force
                $repairs += "Removed node_modules"
            }
            
            if (Test-Path "package-lock.json") {
                Remove-Item "package-lock.json" -Force
                $repairs += "Removed package-lock.json"
            }
            
            # Fresh install
            npm install --verbose 2>&1 | Tee-Object -Variable npmOutput
            if ($LASTEXITCODE -eq 0) {
                Write-EQ12Log "SUCCESS" "✅ npm install completed successfully"
                $repairs += "Fresh npm install"
            } else {
                Write-EQ12Log "ERROR" "❌ npm install failed"
                # Try npm audit fix
                npm audit fix --force 2>&1 | Out-Null
                $repairs += "Attempted npm audit fix"
            }
        }
        
        # Python projects
        if (Test-Path "requirements.txt" -or Test-Path "pyproject.toml" -or Test-Path "setup.py") {
            Write-EQ12Log "INFO" "🐍 Found Python project, checking pip dependencies..."
            
            if (Test-Path "requirements.txt") {
                pip install -r requirements.txt --upgrade 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    $repairs += "Updated Python requirements"
                }
            }
        }
        
        # .NET projects
        if (Test-Path "*.csproj" -or Test-Path "*.sln") {
            Write-EQ12Log "INFO" "🔷 Found .NET project, restoring packages..."
            dotnet restore 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $repairs += "Restored .NET packages"
            }
        }
        
    } finally {
        Pop-Location
    }
    
    return $repairs
}

function Test-CopilotIntegration {
    Write-EQ12Log "INFO" "🤖 Testing GitHub Copilot integration..."
    
    $copilotIssues = @()
    
    # Check if Copilot extension is installed
    $extensions = code --list-extensions 2>$null
    $copilotExtensions = $extensions | Where-Object { $_ -like "*copilot*" }
    
    if ($copilotExtensions) {
        Write-EQ12Log "SUCCESS" "✅ GitHub Copilot extensions found: $($copilotExtensions -join ', ')"
    } else {
        $copilotIssues += "GitHub Copilot extension not installed"
        Write-EQ12Log "WARN" "⚠️ GitHub Copilot extension not detected"
    }
    
    # Check authentication
    $authStatus = gh auth status 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-EQ12Log "SUCCESS" "✅ GitHub CLI authenticated"
    } else {
        $copilotIssues += "GitHub CLI not authenticated"
    }
    
    return $copilotIssues
}

function Validate-ProjectConfiguration {
    Write-EQ12Log "INFO" "⚙️ Validating project configuration..."
    
    Push-Location $Workspace
    $configIssues = @()
    
    try {
        # Check .vscode/settings.json
        $vscodePath = ".vscode/settings.json"
        if (Test-Path $vscodePath) {
            try {
                $settings = Get-Content $vscodePath | ConvertFrom-Json
                Write-EQ12Log "SUCCESS" "✅ VS Code settings.json is valid JSON"
            } catch {
                $configIssues += "Invalid JSON in .vscode/settings.json"
                Write-EQ12Log "ERROR" "❌ Invalid JSON in VS Code settings"
            }
        }
        
        # Check package.json syntax
        if (Test-Path "package.json") {
            try {
                $package = Get-Content "package.json" | ConvertFrom-Json
                Write-EQ12Log "SUCCESS" "✅ package.json is valid JSON"
                
                # Check for ES module compatibility
                if ($package.type -eq "module") {
                    Write-EQ12Log "INFO" "📋 ES modules enabled in package.json"
                }
            } catch {
                $configIssues += "Invalid JSON in package.json"
            }
        }
        
        # Check Python configuration
        if (Test-Path "pyproject.toml") {
            Write-EQ12Log "SUCCESS" "✅ Found pyproject.toml configuration"
        }
        
    } finally {
        Pop-Location
    }
    
    return $configIssues
}

function Run-ProjectTests {
    Write-EQ12Log "INFO" "🧪 Running project tests and validation..."
    
    Push-Location $Workspace
    $testResults = @()
    
    try {
        # Node.js tests
        if (Test-Path "package.json") {
            $package = Get-Content "package.json" | ConvertFrom-Json
            if ($package.scripts -and $package.scripts.test) {
                Write-EQ12Log "INFO" "Running npm test..."
                npm test 2>&1 | Tee-Object -Variable testOutput
                if ($LASTEXITCODE -eq 0) {
                    $testResults += "npm test: PASSED"
                } else {
                    $testResults += "npm test: FAILED"
                }
            }
        }
        
        # Python tests
        if (Test-Path "tests" -PathType Container) {
            Write-EQ12Log "INFO" "Running Python tests..."
            python -m pytest tests/ -v 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $testResults += "pytest: PASSED"
            } else {
                $testResults += "pytest: FAILED"
            }
        }
        
        # Linting
        if (Test-Path "package.json") {
            npm run lint 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $testResults += "lint: PASSED"
            }
        }
        
    } finally {
        Pop-Location
    }
    
    return $testResults
}

function Generate-FixReport {
    param(
        [array]$Issues,
        [array]$Repairs,
        [array]$TestResults
    )
    
    $reportLines = @()
    $reportLines += "# EQ12 VS Code Troubleshooter Report"
    $reportLines += "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $reportLines += "Workspace: $Workspace"
    $reportLines += "Action: $Action"
    $reportLines += ""
    $reportLines += "## Issues Found"
    if ($Issues) {
        $Issues | ForEach-Object { $reportLines += "- $_" }
    } else {
        $reportLines += "No critical issues detected"
    }
    $reportLines += ""
    $reportLines += "## Repairs Applied"
    if ($Repairs) {
        $Repairs | ForEach-Object { $reportLines += "- $_" }
    } else {
        $reportLines += "No repairs needed"
    }
    $reportLines += ""
    $reportLines += "## Test Results"
    if ($TestResults) {
        $TestResults | ForEach-Object { $reportLines += "- $_" }
    } else {
        $reportLines += "No tests run"
    }
    $reportLines += ""
    $reportLines += "## Recommendations"
    $reportLines += "- Keep VS Code extensions up to date"
    $reportLines += "- Run npm audit regularly for security updates"
    $reportLines += "- Use code --install-extension ms-python.python for Python support"
    $reportLines += "- Enable auto-save: File > Auto Save"
    $reportLines += "- Configure Copilot: Ctrl+Shift+P > GitHub Copilot: Sign In"
    $reportLines += ""
    $reportLines += "---"
    $reportLines += "EQ12 Platform - Automated Troubleshooting System"
    
    $report = $reportLines -join "`n"
    Set-Content -Path $ReportFile -Value $report
    Write-EQ12Log "SUCCESS" "Fix report generated: $ReportFile"
}

# Main execution logic
Write-EQ12Log "INFO" "🚀 EQ12 VS Code Troubleshooter starting..."
Write-EQ12Log "INFO" "Action: $Action | Workspace: $Workspace"

$allIssues = @()
$allRepairs = @()
$testResults = @()

switch ($Action) {
    'Quick' {
        Write-EQ12Log "INFO" "⚡ Running quick diagnostic..."
        $allIssues += Test-Prerequisites
        $cleared = Clear-VSCodeCache
        $allRepairs += $cleared
    }
    
    'Clean' {
        Write-EQ12Log "INFO" "🧹 Deep cleaning VS Code..."
        $cleared = Clear-VSCodeCache
        $allRepairs += $cleared
    }
    
    'Dependencies' {
        Write-EQ12Log "INFO" "📦 Repairing dependencies..."
        $repairs = Repair-Dependencies
        $allRepairs += $repairs
    }
    
    'Cache' {
        $cleared = Clear-VSCodeCache
        $allRepairs += $cleared
    }
    
    'Copilot' {
        $copilotIssues = Test-CopilotIntegration
        $allIssues += $copilotIssues
    }
    
    'Config' {
        $configIssues = Validate-ProjectConfiguration
        $allIssues += $configIssues
    }
    
    'Test' {
        $testResults = Run-ProjectTests
    }
    
    'Full' {
        Write-EQ12Log "INFO" "🔄 Running complete troubleshooting cycle..."
        
        # Phase 1: Prerequisites
        $allIssues += Test-Prerequisites
        
        # Phase 2: Clean cache
        $cleared = Clear-VSCodeCache
        $allRepairs += $cleared
        
        # Phase 3: Fix dependencies
        $repairs = Repair-Dependencies
        $allRepairs += $repairs
        
        # Phase 4: Validate configuration
        $configIssues = Validate-ProjectConfiguration
        $allIssues += $configIssues
        
        # Phase 5: Test Copilot
        $copilotIssues = Test-CopilotIntegration
        $allIssues += $copilotIssues
        
        # Phase 6: Run tests
        $testResults = Run-ProjectTests
    }
}

# Generate summary
$criticalIssues = $allIssues | Where-Object { $_ -like "*not found*" -or $_ -like "*failed*" -or $_ -like "*invalid*" }
$totalRepairs = $allRepairs.Count

if ($criticalIssues) {
    Write-EQ12Log "WARN" "⚠️ $($criticalIssues.Count) critical issues found"
    $criticalIssues | ForEach-Object { Write-EQ12Log "WARN" "  - $_" }
} else {
    Write-EQ12Log "SUCCESS" "✅ No critical issues detected"
}

Write-EQ12Log "INFO" "🔧 Applied $totalRepairs repairs"

# Auto-fix critical issues if enabled
if ($AutoFix -and $criticalIssues) {
    Write-EQ12Log "INFO" "🛠️ Attempting auto-fixes..."
    
    # Restart VS Code if it's running
    $vscodeProcess = Get-Process -Name "Code" -ErrorAction SilentlyContinue
    if ($vscodeProcess) {
        Write-EQ12Log "INFO" "Restarting VS Code..."
        $vscodeProcess | Stop-Process -Force
        Start-Sleep 3
        & code $Workspace
        $allRepairs += "Restarted VS Code"
    }
}

# Generate report if requested
if ($GenerateReport) {
    Generate-FixReport -Issues $allIssues -Repairs $allRepairs -TestResults $testResults
}

# Final status
if ($criticalIssues.Count -eq 0 -and $totalRepairs -gt 0) {
    Write-EQ12Log "SUCCESS" "🎉 Troubleshooting completed successfully!"
} elseif ($criticalIssues.Count -gt 0) {
    Write-EQ12Log "WARN" "⚠️ Some issues require manual attention"
} else {
    Write-EQ12Log "INFO" "ℹ️ System appears healthy"
}

Write-EQ12Log "INFO" "📊 Summary: $($allIssues.Count) issues, $totalRepairs repairs, $($testResults.Count) tests"
Write-EQ12Log "INFO" "📝 Logs saved to: $LogFile"

# Return status code
if ($criticalIssues.Count -eq 0) { 
    exit 0 
} else { 
    exit 1 
}