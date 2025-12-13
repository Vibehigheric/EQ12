# EQ12 GitLeaks Auto-Remediation System - Quick Test Version
# Professional security automation without emoji encoding issues

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('Scan', 'AutoFix', 'Test')]
    [string]$Action = 'Test',
    
    [Parameter(Mandatory = $false)]
    [string]$Repository = $PWD.Path,
    
    [Parameter(Mandatory = $false)]
    [switch]$DryRun
)

# Initialize logging
$LogDir = "C:\EQ12\logs"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$LogDir\gitleaks_test_$Timestamp.log"

if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

function Write-SecurityLog {
    param([string]$Level, [string]$Message)
    
    $LogEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        level = $Level
        message = $Message
        repository = $Repository
        action = $Action
    } | ConvertTo-Json -Compress
    
    Add-Content -Path $LogFile -Value $LogEntry
    
    $Color = switch ($Level) {
        'ERROR' { 'Red' }
        'WARN' { 'Yellow' }
        'SUCCESS' { 'Green' }
        default { 'Cyan' }
    }
    
    Write-Host "[$Level] $Message" -ForegroundColor $Color
}

function Test-GitLeaksAvailable {
    try {
        $version = gitleaks version 2>$null
        if ($version) {
            Write-SecurityLog "SUCCESS" "GitLeaks available: $version"
            return $true
        }
    } catch {
        Write-SecurityLog "ERROR" "GitLeaks not found. Install with: winget install gitleaks"
        return $false
    }
    return $false
}

function Test-SecuritySetup {
    Write-SecurityLog "INFO" "Testing EQ12 GitLeaks security setup..."
    
    $issues = @()
    
    # Check GitLeaks
    if (!(Test-GitLeaksAvailable)) {
        $issues += "GitLeaks not installed"
    }
    
    # Check if we're in a Git repo
    Push-Location $Repository
    try {
        git rev-parse --git-dir 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-SecurityLog "SUCCESS" "Valid Git repository detected"
        } else {
            $issues += "Not a Git repository"
        }
    } finally {
        Pop-Location
    }
    
    # Check Python monitoring script
    $pythonScript = "$Repository\scripts\eq12_gitleaks_monitor.py"
    if (Test-Path $pythonScript) {
        Write-SecurityLog "SUCCESS" "Python monitoring system available"
    } else {
        $issues += "Python monitoring script missing"
    }
    
    # Check VS Code tasks
    $tasksFile = "$Repository\.vscode\tasks.json"
    if (Test-Path $tasksFile) {
        $tasksContent = Get-Content $tasksFile -Raw
        if ($tasksContent -like "*GitLeaks*") {
            Write-SecurityLog "SUCCESS" "VS Code GitLeaks tasks configured"
        } else {
            $issues += "VS Code tasks not configured"
        }
    }
    
    return $issues
}

function Show-SecuritySummary {
    param([array]$Issues)
    
    Write-SecurityLog "INFO" "EQ12 GitLeaks Security System Status"
    Write-Host "=" * 60 -ForegroundColor Blue
    
    if ($Issues.Count -eq 0) {
        Write-SecurityLog "SUCCESS" "All security components ready!"
        Write-Host ""
        Write-SecurityLog "INFO" "Available commands:"
        Write-SecurityLog "INFO" "- Scan: powershell -File scripts/eq12_gitleaks_autofix.ps1 -Action Scan"
        Write-SecurityLog "INFO" "- Auto-fix: powershell -File scripts/eq12_gitleaks_autofix.ps1 -Action AutoFix"
        Write-SecurityLog "INFO" "- Monitor: python scripts/eq12_gitleaks_monitor.py --action monitor"
        Write-SecurityLog "INFO" "- VS Code: Use Task Runner (Ctrl+Shift+P > Tasks: Run Task)"
    } else {
        Write-SecurityLog "WARN" "$($Issues.Count) issues found:"
        foreach ($issue in $Issues) {
            Write-SecurityLog "WARN" "  - $issue"
        }
        
        Write-Host ""
        Write-SecurityLog "INFO" "Installation instructions:"
        if ($Issues -contains "GitLeaks not installed") {
            Write-SecurityLog "INFO" "  Install GitLeaks: winget install gitleaks"
        }
    }
    
    Write-Host ""
    Write-SecurityLog "INFO" "Security features available:"
    Write-SecurityLog "INFO" "  - Automatic secret detection and remediation"
    Write-SecurityLog "INFO" "  - Git history cleanup for committed secrets" 
    Write-SecurityLog "INFO" "  - Pre-commit hooks to prevent future leaks"
    Write-SecurityLog "INFO" "  - VS Code integration for seamless workflows"
    Write-SecurityLog "INFO" "  - Continuous monitoring and reporting"
    Write-SecurityLog "INFO" "  - GitHub Copilot integration for smart fixes"
}

# Main execution
Write-SecurityLog "INFO" "EQ12 GitLeaks Security Test starting..."
Write-SecurityLog "INFO" "Action: $Action | Repository: $Repository"

switch ($Action) {
    'Test' {
        $issues = Test-SecuritySetup
        Show-SecuritySummary -Issues $issues
        
        if ($issues.Count -eq 0) {
            exit 0
        } else {
            exit 1
        }
    }
    
    'Scan' {
        if (Test-GitLeaksAvailable) {
            Write-SecurityLog "INFO" "Running GitLeaks scan..."
            Push-Location $Repository
            try {
                gitleaks detect --source . --exit-code 0 --verbose
                Write-SecurityLog "SUCCESS" "Security scan completed"
            } finally {
                Pop-Location
            }
        }
    }
    
    'AutoFix' {
        Write-SecurityLog "INFO" "Auto-fix functionality requires the full script"
        Write-SecurityLog "INFO" "Use: powershell -File scripts/eq12_gitleaks_autofix.ps1 -Action AutoFix"
    }
}

Write-SecurityLog "SUCCESS" "EQ12 GitLeaks security test completed"
Write-SecurityLog "INFO" "Logs saved to: $LogFile"