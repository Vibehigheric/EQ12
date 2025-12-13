# EQ12 Environment Check Script
# =============================
# Purpose: Verify all free tools are installed and free-safe
# Output: logs/doctor_free.json with detailed environment report
# Free mode: No paid API calls

[CmdletBinding()]
param(
    [string]$OutputFile = "logs\doctor_free.json",
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"  # Don't stop on individual check failures
$InformationPreference = "Continue"

# Colors for PowerShell output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-CheckMessage {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "🔍 $Message" -ForegroundColor $Cyan
    }
}

function Write-PassMessage {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-FailMessage {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

function Write-WarnMessage {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Yellow
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

function Get-CommandVersion {
    param(
        [string]$Command,
        [string]$VersionArg = "--version"
    )
    
    try {
        if ($Command -eq "7z") {
            # 7z doesn't have a version flag, just check if it exists
            if (Test-CommandExists "7z") {
                return "Available"
            } else {
                return $null
            }
        }
        
        $output = & $Command $VersionArg 2>&1 | Select-Object -First 3
        if ($output) {
            return ($output -join " ").Trim()
        }
        return $null
    } catch {
        return $null
    }
}

function Test-PythonEnvironment {
    $result = @{
        "python_available" = $false
        "python_version" = $null
        "venv_active" = $false
        "venv_path" = $null
        "pip_version" = $null
        "pip_tools_available" = $false
        "site_packages_count" = 0
    }
    
    Write-CheckMessage "Checking Python environment..."
    
    # Check Python availability
    if (Test-CommandExists "python") {
        $result.python_available = $true
        $result.python_version = Get-CommandVersion "python"
        Write-PassMessage "Python is available: $($result.python_version)"
    } else {
        Write-FailMessage "Python is not available"
        return $result
    }
    
    # Check virtual environment
    try {
        $pythonPrefix = python -c "import sys; print(sys.prefix)" 2>$null
        $pythonBasePrefix = python -c "import sys; print(getattr(sys, 'base_prefix', sys.prefix))" 2>$null
        
        if ($pythonPrefix -ne $pythonBasePrefix) {
            $result.venv_active = $true
            $result.venv_path = $pythonPrefix
            Write-PassMessage "Virtual environment active: $pythonPrefix"
        } else {
            Write-WarnMessage "No virtual environment detected"
        }
    } catch {
        Write-WarnMessage "Could not determine virtual environment status"
    }
    
    # Check pip
    if (Test-CommandExists "pip") {
        $result.pip_version = Get-CommandVersion "pip"
        Write-PassMessage "pip is available: $($result.pip_version)"
        
        # Check pip-tools
        try {
            pip show pip-tools 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) {
                $result.pip_tools_available = $true
                Write-PassMessage "pip-tools is available"
            }
        } catch {}
    } else {
        Write-FailMessage "pip is not available"
    }
    
    # Count installed packages
    try {
        $packages = pip list --format=freeze 2>$null | Measure-Object -Line
        $result.site_packages_count = $packages.Lines
        Write-CheckMessage "Installed packages: $($result.site_packages_count)"
    } catch {}
    
    return $result
}

function Test-NodeEnvironment {
    $result = @{
        "node_available" = $false
        "node_version" = $null
        "npm_available" = $false
        "npm_version" = $null
        "pnpm_available" = $false
        "pnpm_version" = $null
        "package_json_exists" = $false
        "node_modules_exists" = $false
    }
    
    Write-CheckMessage "Checking Node.js environment..."
    
    # Check Node.js
    if (Test-CommandExists "node") {
        $result.node_available = $true
        $result.node_version = Get-CommandVersion "node"
        Write-PassMessage "Node.js is available: $($result.node_version)"
    } else {
        Write-FailMessage "Node.js is not available"
        return $result
    }
    
    # Check npm
    if (Test-CommandExists "npm") {
        $result.npm_available = $true
        $result.npm_version = Get-CommandVersion "npm"
        Write-PassMessage "npm is available: $($result.npm_version)"
    } else {
        Write-FailMessage "npm is not available"
    }
    
    # Check pnpm
    if (Test-CommandExists "pnpm") {
        $result.pnpm_available = $true
        $result.pnpm_version = Get-CommandVersion "pnpm"
        Write-PassMessage "pnpm is available: $($result.pnpm_version)"
    } else {
        Write-CheckMessage "pnpm is not available (optional)"
    }
    
    # Check package.json and node_modules
    $result.package_json_exists = Test-Path "package.json"
    $result.node_modules_exists = Test-Path "node_modules"
    
    if ($result.package_json_exists) {
        Write-PassMessage "package.json exists"
    } else {
        Write-CheckMessage "No package.json found"
    }
    
    return $result
}

function Test-CoreTools {
    $tools = @{
        "git" = @{ "command" = "git"; "version_arg" = "--version" }
        "github_cli" = @{ "command" = "gh"; "version_arg" = "--version" }
        "7zip" = @{ "command" = "7z"; "version_arg" = "" }
        "jq" = @{ "command" = "jq"; "version_arg" = "--version" }
        "winget" = @{ "command" = "winget"; "version_arg" = "--version" }
        "ruff" = @{ "command" = "ruff"; "version_arg" = "--version" }
    }
    
    $result = @{}
    
    Write-CheckMessage "Checking core development tools..."
    
    foreach ($toolName in $tools.Keys) {
        $tool = $tools[$toolName]
        $toolResult = @{
            "available" = $false
            "version" = $null
            "path" = $null
        }
        
        if (Test-CommandExists $tool.command) {
            $toolResult.available = $true
            
            if ($tool.version_arg) {
                $toolResult.version = Get-CommandVersion $tool.command $tool.version_arg
            } else {
                $toolResult.version = Get-CommandVersion $tool.command
            }
            
            try {
                $commandInfo = Get-Command $tool.command -ErrorAction Stop
                $toolResult.path = $commandInfo.Source
            } catch {}
            
            Write-PassMessage "$($tool.command) is available: $($toolResult.version)"
        } else {
            Write-FailMessage "$($tool.command) is not available"
        }
        
        $result[$toolName] = $toolResult
    }
    
    return $result
}

function Test-ProjectStructure {
    $requiredPaths = @(
        "scripts",
        "tests", 
        "logs",
        ".vscode",
        ".git"
    )
    
    $optionalPaths = @(
        "requirements.txt",
        "requirements.in",
        "package.json",
        ".pre-commit-config.yaml",
        "pyproject.toml"
    )
    
    $result = @{
        "required_paths" = @{}
        "optional_paths" = @{}
        "is_git_repo" = $false
        "has_python_config" = $false
        "has_node_config" = $false
    }
    
    Write-CheckMessage "Checking project structure..."
    
    # Check required paths
    foreach ($path in $requiredPaths) {
        $exists = Test-Path $path
        $result.required_paths[$path] = $exists
        
        if ($exists) {
            Write-PassMessage "$path exists"
        } else {
            Write-FailMessage "$path is missing"
        }
    }
    
    # Check optional paths
    foreach ($path in $optionalPaths) {
        $exists = Test-Path $path
        $result.optional_paths[$path] = $exists
        
        if ($exists) {
            Write-PassMessage "$path exists"
        } else {
            Write-CheckMessage "$path not found (optional)"
        }
    }
    
    # Derived checks
    $result.is_git_repo = Test-Path ".git"
    $result.has_python_config = (Test-Path "requirements.txt") -or (Test-Path "pyproject.toml")
    $result.has_node_config = Test-Path "package.json"
    
    return $result
}

function Test-FreeModeCompliance {
    $result = @{
        "api_keys_present" = @{}
        "dry_run_supported" = $false
        "free_mode_enforced" = $false
    }
    
    Write-CheckMessage "Checking free mode compliance..."
    
    # Check for API keys in environment
    $apiKeys = @("OPENAI_API_KEY", "AZURE_OPENAI_KEY", "CODEX_API_KEY", "ODDS_API_KEY")
    
    foreach ($key in $apiKeys) {
        $value = [System.Environment]::GetEnvironmentVariable($key)
        $isPresent = -not [string]::IsNullOrEmpty($value)
        $result.api_keys_present[$key] = $isPresent
        
        if ($isPresent) {
            Write-WarnMessage "$key is present (paid API available)"
        } else {
            Write-PassMessage "$key not set (free mode)"
        }
    }
    
    # Check for DRY_RUN support
    $dryRun = [System.Environment]::GetEnvironmentVariable("DRY_RUN")
    $result.dry_run_supported = $dryRun -eq "true" -or $dryRun -eq "1"
    
    if ($result.dry_run_supported) {
        Write-PassMessage "DRY_RUN mode is enabled"
    } else {
        Write-CheckMessage "DRY_RUN mode not enabled"
    }
    
    # Check for free guard module
    $result.free_mode_enforced = Test-Path "eq12_free_guard.py"
    
    if ($result.free_mode_enforced) {
        Write-PassMessage "Free mode guard module found"
    } else {
        Write-WarnMessage "Free mode guard module not found"
    }
    
    return $result
}

function Get-SystemInfo {
    $result = @{
        "os" = $null
        "powershell_version" = $null
        "timezone" = $null
        "utf8_support" = $false
        "admin_rights" = $false
        "execution_policy" = $null
    }
    
    Write-CheckMessage "Gathering system information..."
    
    # OS Information
    try {
        $os = Get-CimInstance -ClassName Win32_OperatingSystem
        $result.os = "$($os.Caption) $($os.Version)"
        Write-PassMessage "OS: $($result.os)"
    } catch {
        $result.os = "Unknown Windows"
    }
    
    # PowerShell version
    $result.powershell_version = $PSVersionTable.PSVersion.ToString()
    Write-PassMessage "PowerShell: $($result.powershell_version)"
    
    # Timezone
    try {
        $result.timezone = (Get-TimeZone).Id
        Write-PassMessage "Timezone: $($result.timezone)"
    } catch {
        $result.timezone = "Unknown"
    }
    
    # UTF-8 support
    try {
        $result.utf8_support = [System.Console]::OutputEncoding.WebName -eq "utf-8"
        if ($result.utf8_support) {
            Write-PassMessage "UTF-8 console encoding detected"
        } else {
            Write-WarnMessage "Console encoding: $([System.Console]::OutputEncoding.WebName)"
        }
    } catch {
        Write-WarnMessage "Could not determine console encoding"
    }
    
    # Admin rights
    try {
        $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
        $result.admin_rights = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        
        if ($result.admin_rights) {
            Write-PassMessage "Running with administrator privileges"
        } else {
            Write-CheckMessage "Running without administrator privileges"
        }
    } catch {
        Write-WarnMessage "Could not determine admin rights"
    }
    
    # Execution policy
    try {
        $result.execution_policy = (Get-ExecutionPolicy).ToString()
        Write-CheckMessage "Execution Policy: $($result.execution_policy)"
    } catch {
        $result.execution_policy = "Unknown"
    }
    
    return $result
}

function Export-DoctorReport {
    param([hashtable]$Report, [string]$FilePath)
    
    Write-CheckMessage "Generating doctor report..."
    
    # Ensure logs directory exists
    $logsDir = Split-Path $FilePath -Parent
    if (-not (Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }
    
    # Add metadata to report
    $Report.metadata = @{
        "generated_at" = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        "generated_by" = "eq12_env_check.ps1"
        "version" = "1.0.0"
        "machine" = $env:COMPUTERNAME
        "user" = $env:USERNAME
        "working_directory" = (Get-Location).Path
    }
    
    # Calculate overall health score
    $totalChecks = 0
    $passedChecks = 0
    
    # Count Python checks
    if ($Report.python_environment.python_available) { $passedChecks++ }
    if ($Report.python_environment.venv_active) { $passedChecks++ }
    if ($Report.python_environment.pip_tools_available) { $passedChecks++ }
    $totalChecks += 3
    
    # Count Node checks
    if ($Report.node_environment.node_available) { $passedChecks++ }
    if ($Report.node_environment.npm_available) { $passedChecks++ }
    $totalChecks += 2
    
    # Count core tools
    foreach ($tool in $Report.core_tools.GetEnumerator()) {
        $totalChecks++
        if ($tool.Value.available) { $passedChecks++ }
    }
    
    # Count required paths
    foreach ($path in $Report.project_structure.required_paths.GetEnumerator()) {
        $totalChecks++
        if ($path.Value) { $passedChecks++ }
    }
    
    $Report.health_score = if ($totalChecks -gt 0) { 
        [math]::Round(($passedChecks / $totalChecks) * 100, 1) 
    } else { 
        0 
    }
    
    # Export to JSON
    try {
        $jsonOutput = $Report | ConvertTo-Json -Depth 10 -Compress:$false
        $jsonOutput | Out-File -FilePath $FilePath -Encoding UTF8
        Write-PassMessage "Doctor report saved to: $FilePath"
    } catch {
        Write-FailMessage "Failed to save doctor report: $_"
    }
}

function Show-HealthSummary {
    param([hashtable]$Report)
    
    Write-Host ""
    Write-Host "🏥 EQ12 ENVIRONMENT HEALTH CHECK" -ForegroundColor $Green
    Write-Host "================================" -ForegroundColor $Green
    Write-Host ""
    
    # Overall health score
    $score = $Report.health_score
    $color = if ($score -ge 90) { $Green } elseif ($score -ge 70) { $Yellow } else { $Red }
    Write-Host "Overall Health Score: $score%" -ForegroundColor $color
    Write-Host ""
    
    # Key findings
    Write-Host "Key Findings:" -ForegroundColor $Cyan
    Write-Host "------------" -ForegroundColor $Cyan
    
    # Python environment
    if ($Report.python_environment.python_available) {
        Write-PassMessage "Python environment ready"
    } else {
        Write-FailMessage "Python environment needs attention"
    }
    
    # Node.js environment  
    if ($Report.node_environment.node_available) {
        Write-PassMessage "Node.js environment ready"
    } else {
        Write-FailMessage "Node.js environment needs attention"
    }
    
    # Core tools
    $availableTools = ($Report.core_tools.GetEnumerator() | Where-Object { $_.Value.available }).Count
    $totalTools = $Report.core_tools.Count
    
    if ($availableTools -eq $totalTools) {
        Write-PassMessage "All core tools available ($availableTools/$totalTools)"
    } else {
        Write-WarnMessage "Some core tools missing ($availableTools/$totalTools)"
    }
    
    # Free mode compliance
    $hasApiKeys = ($Report.free_mode.api_keys_present.GetEnumerator() | Where-Object { $_.Value }).Count
    
    if ($hasApiKeys -eq 0) {
        Write-PassMessage "Running in free mode (no API keys detected)"
    } else {
        Write-WarnMessage "API keys detected - paid features available"
    }
    
    Write-Host ""
    Write-Host "Recommendations:" -ForegroundColor $Yellow
    Write-Host "---------------" -ForegroundColor $Yellow
    
    if ($score -lt 90) {
        Write-Host "- Run: scripts\eq12_free_toolchain_bootstrap.ps1" -ForegroundColor $White
        Write-Host "- Run: scripts\eq12_update_all.ps1" -ForegroundColor $White
    }
    
    if (-not $Report.python_environment.venv_active) {
        Write-Host "- Activate Python virtual environment" -ForegroundColor $White
    }
    
    if (-not $Report.free_mode.free_mode_enforced) {
        Write-Host "- Install free mode guard: eq12_free_guard.py" -ForegroundColor $White
    }
    
    Write-Host ""
}

# Main execution
function Start-EnvironmentCheck {
    Write-Host ""
    Write-Host "🔍 EQ12 ENVIRONMENT CHECK" -ForegroundColor $Green
    Write-Host "=========================" -ForegroundColor $Green
    Write-Host "Verifying free toolchain setup" -ForegroundColor $Cyan
    Write-Host ""
    
    $report = @{}
    
    # Run all checks
    $report.system_info = Get-SystemInfo
    $report.python_environment = Test-PythonEnvironment
    $report.node_environment = Test-NodeEnvironment
    $report.core_tools = Test-CoreTools
    $report.project_structure = Test-ProjectStructure
    $report.free_mode = Test-FreeModeCompliance
    
    # Export report
    Export-DoctorReport -Report $report -FilePath $OutputFile
    
    # Show summary
    Show-HealthSummary -Report $report
    
    # Return success based on health score
    return $report.health_score -ge 70
}

# Script entry point
try {
    $success = Start-EnvironmentCheck
    
    if ($success) {
        Write-PassMessage "Environment check completed successfully!"
        exit 0
    } else {
        Write-WarnMessage "Environment check completed with issues. See recommendations above."
        exit 1
    }
} catch {
    Write-FailMessage "Environment check failed: $_"
    exit 1
}