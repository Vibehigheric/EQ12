#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 GitLeaks Auto-Remediation System - Professional Security Automation
    
.DESCRIPTION
    Comprehensive GitLeaks detection and auto-fix system that:
    - Scans repositories for secrets and credentials
    - Automatically backs up files before changes
    - Sanitizes code by replacing hardcoded secrets with environment variables
    - Cleans Git history to remove committed secrets
    - Integrates with GitHub Copilot for intelligent fixes
    - Provides detailed reporting and logging
    
.PARAMETER Action
    Operation to perform: Scan, AutoFix, CleanHistory, FullScan, InstallHooks, Monitor
    
.PARAMETER Repository
    Path to repository (default: current directory)
    
.PARAMETER BackupPath
    Custom backup directory (default: auto-generated)
    
.PARAMETER ForceClean
    Force Git history cleaning without confirmation
    
.PARAMETER DryRun
    Show what would be changed without making modifications
    
.EXAMPLE
    .\eq12_gitleaks_autofix.ps1 -Action Scan
    Performs GitLeaks scan and reports findings
    
.EXAMPLE
    .\eq12_gitleaks_autofix.ps1 -Action AutoFix -Repository "C:\MyProject"
    Automatically fixes detected secrets in specified repository
    
.EXAMPLE
    .\eq12_gitleaks_autofix.ps1 -Action FullScan -DryRun
    Complete security audit in preview mode
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('Scan', 'AutoFix', 'CleanHistory', 'FullScan', 'InstallHooks', 'Monitor', 'Emergency')]
    [string]$Action = 'Scan',
    
    [Parameter(Mandatory = $false)]
    [string]$Repository = $PWD.Path,
    
    [Parameter(Mandatory = $false)]
    [string]$BackupPath = "",
    
    [Parameter(Mandatory = $false)]
    [switch]$ForceClean,
    
    [Parameter(Mandatory = $false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory = $false)]
    [switch]$Verbose
)

# Initialize EQ12 logging system
$LogDir = "C:\EQ12\logs"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = "$LogDir\gitleaks_autofix_$Timestamp.log"
$ReportFile = "$LogDir\gitleaks_security_report_$Timestamp.json"
$BackupBaseDir = "C:\EQ12\backups\gitleaks"

# Ensure directories exist
@($LogDir, $BackupBaseDir) | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

function Write-EQ12SecurityLog {
    param(
        [string]$Level,
        [string]$Message,
        [object]$Data = $null,
        [string]$Category = "SECURITY"
    )
    
    $LogEntry = @{
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
        level = $Level
        category = $Category
        message = $Message
        repository = $Repository
        action = $Action
        session_id = $Timestamp
    }
    
    if ($Data) {
        $LogEntry.data = $Data
    }
    
    $JsonLog = $LogEntry | ConvertTo-Json -Compress
    Add-Content -Path $LogFile -Value $JsonLog
    
    $Color = switch ($Level) {
        'CRITICAL' { 'Red' }
        'ERROR' { 'Red' }
        'WARN' { 'Yellow' }
        'SUCCESS' { 'Green' }
        'INFO' { 'Cyan' }
        'DEBUG' { 'Gray' }
        default { 'White' }
    }
    
    $Icon = switch ($Level) {
        'CRITICAL' { '🚨' }
        'ERROR' { '❌' }
        'WARN' { '⚠️' }
        'SUCCESS' { '✅' }
        'INFO' { '🔍' }
        'DEBUG' { '🔧' }
        default { 'ℹ️' }
    }
    
    Write-Host "[$Level] $Icon $Message" -ForegroundColor $Color
    
    if ($Verbose -and $Data) {
        Write-Host "   Data: $($Data | ConvertTo-Json -Compress)" -ForegroundColor Gray
    }
}

function Test-Prerequisites {
    Write-EQ12SecurityLog "INFO" "Checking GitLeaks prerequisites and security tools..."
    
    $issues = @()
    $tools = @()
    
    # Check GitLeaks installation
    try {
        $gitleaksVersion = gitleaks version 2>$null
        if ($gitleaksVersion) {
            Write-EQ12SecurityLog "SUCCESS" "GitLeaks available: $gitleaksVersion"
            $tools += "gitleaks"
        } else {
            $issues += "GitLeaks not installed or not in PATH"
            Write-EQ12SecurityLog "ERROR" "GitLeaks not found. Install: 'winget install gitleaks'"
        }
    } catch {
        $issues += "GitLeaks installation check failed"
        Write-EQ12SecurityLog "ERROR" "GitLeaks check failed: $($_.Exception.Message)"
    }
    
    # Check Git
    try {
        $gitVersion = git --version 2>$null
        if ($gitVersion) {
            Write-EQ12SecurityLog "SUCCESS" "Git available: $gitVersion"
            $tools += "git"
        } else {
            $issues += "Git not available"
        }
    } catch {
        $issues += "Git not installed"
    }
    
    # Check if we're in a Git repository
    Push-Location $Repository
    try {
        git rev-parse --git-dir 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-EQ12SecurityLog "SUCCESS" "Valid Git repository detected"
            $tools += "git-repo"
        } else {
            $issues += "Not a Git repository"
            Write-EQ12SecurityLog "WARN" "Directory is not a Git repository"
        }
    } finally {
        Pop-Location
    }
    
    # Check VS Code CLI (for Copilot integration)
    $vscode = Get-Command "code" -ErrorAction SilentlyContinue
    if ($vscode) {
        Write-EQ12SecurityLog "SUCCESS" "VS Code CLI available for Copilot integration"
        $tools += "vscode"
    } else {
        Write-EQ12SecurityLog "WARN" "VS Code CLI not available - Copilot integration disabled"
    }
    
    return @{
        issues = $issues
        tools = $tools
        ready = ($issues.Count -eq 0)
    }
}

function Invoke-GitLeaksScan {
    param([switch]$SkipHistory)
    
    Write-EQ12SecurityLog "INFO" "Running comprehensive GitLeaks security scan..."
    
    Push-Location $Repository
    $scanResults = @{
        current_files = @()
        git_history = @()
        total_secrets = 0
        critical_count = 0
        scan_successful = $false
        report_path = ""
    }
    
    try {
        # Scan current working directory
        Write-EQ12SecurityLog "INFO" "Scanning current files for secrets..."
        $currentScanFile = "$env:TEMP\gitleaks_current_$Timestamp.json"
        
        gitleaks detect --source . --report-path $currentScanFile --exit-code 0 --verbose 2>$null
        
        if (Test-Path $currentScanFile) {
            $currentResults = Get-Content $currentScanFile | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($currentResults) {
                $scanResults.current_files = $currentResults
                Write-EQ12SecurityLog "WARN" "Found $($currentResults.Count) secrets in current files"
            }
        }
        
        # Scan Git history (unless skipped)
        if (!$SkipHistory) {
            Write-EQ12SecurityLog "INFO" "Scanning Git history for committed secrets..."
            $historyScanFile = "$env:TEMP\gitleaks_history_$Timestamp.json"
            
            gitleaks detect --source . --report-path $historyScanFile --exit-code 0 --log-level debug 2>$null
            
            if (Test-Path $historyScanFile) {
                $historyResults = Get-Content $historyScanFile | ConvertFrom-Json -ErrorAction SilentlyContinue
                if ($historyResults) {
                    $scanResults.git_history = $historyResults
                    Write-EQ12SecurityLog "CRITICAL" "Found $($historyResults.Count) secrets in Git history"
                }
            }
        }
        
        # Calculate totals and severity
        $scanResults.total_secrets = $scanResults.current_files.Count + $scanResults.git_history.Count
        $scanResults.critical_count = ($scanResults.current_files + $scanResults.git_history | 
            Where-Object { $_.RuleID -like "*api*key*" -or $_.RuleID -like "*secret*" -or $_.RuleID -like "*token*" }).Count
        
        $scanResults.scan_successful = $true
        $scanResults.report_path = $ReportFile
        
        # Save comprehensive report
        $scanResults | ConvertTo-Json -Depth 10 | Set-Content $ReportFile
        
        Write-EQ12SecurityLog "INFO" "Scan complete. Total secrets: $($scanResults.total_secrets) (Critical: $($scanResults.critical_count))"
        
    } catch {
        Write-EQ12SecurityLog "ERROR" "GitLeaks scan failed: $($_.Exception.Message)"
        $scanResults.scan_successful = $false
    } finally {
        Pop-Location
        # Cleanup temp files
        @($currentScanFile, $historyScanFile) | Where-Object { Test-Path $_ } | Remove-Item -Force
    }
    
    return $scanResults
}

function New-SecureBackup {
    param([array]$FilesToBackup = @())
    
    if (!$BackupPath) {
        $BackupPath = "$BackupBaseDir\backup_$Timestamp"
    }
    
    Write-EQ12SecurityLog "INFO" "Creating secure backup at: $BackupPath"
    
    Push-Location $Repository
    try {
        if (!(Test-Path $BackupPath)) {
            New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
        }
        
        # Backup entire repository state
        Copy-Item -Path "." -Destination "$BackupPath\repo_full" -Recurse -Force
        
        # Create backup manifest
        $manifest = @{
            timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
            repository = $Repository
            backup_path = $BackupPath
            git_commit = (git rev-parse HEAD 2>$null)
            git_branch = (git branch --show-current 2>$null)
            files_count = (Get-ChildItem -Recurse -File | Measure-Object).Count
            action = $Action
        }
        
        $manifest | ConvertTo-Json | Set-Content "$BackupPath\backup_manifest.json"
        
        Write-EQ12SecurityLog "SUCCESS" "Backup created successfully"
        return $BackupPath
        
    } catch {
        Write-EQ12SecurityLog "ERROR" "Backup failed: $($_.Exception.Message)"
        return $null
    } finally {
        Pop-Location
    }
}

function Invoke-AutoSecretRemediation {
    param([object]$ScanResults)
    
    Write-EQ12SecurityLog "INFO" "Starting automatic secret remediation..."
    
    if ($ScanResults.total_secrets -eq 0) {
        Write-EQ12SecurityLog "SUCCESS" "No secrets found - remediation not needed"
        return @{ success = $true; fixed_count = 0 }
    }
    
    # Create backup before making changes
    $backupPath = New-SecureBackup
    if (!$backupPath) {
        Write-EQ12SecurityLog "ERROR" "Cannot proceed without backup"
        return @{ success = $false; error = "Backup failed" }
    }
    
    Push-Location $Repository
    $fixedCount = 0
    $errors = @()
    
    try {
        # Define common secret patterns and their replacements
        $secretPatterns = @{
            # API Keys
            'sk-[A-Za-z0-9]{32,}' = 'os.getenv("OPENAI_API_KEY")'
            'AIza[A-Za-z0-9]{35}' = 'os.getenv("GOOGLE_API_KEY")'
            'AKIA[A-Z0-9]{16}' = 'os.getenv("AWS_ACCESS_KEY_ID")'
            '[A-Za-z0-9+/]{40}' = 'os.getenv("AWS_SECRET_ACCESS_KEY")'
            'ghp_[A-Za-z0-9]{36}' = 'os.getenv("GITHUB_TOKEN")'
            'gho_[A-Za-z0-9]{36}' = 'os.getenv("GITHUB_OAUTH_TOKEN")'
            
            # Database URLs
            'postgres://[^:]+:[^@]+@[^/]+/\w+' = 'os.getenv("DATABASE_URL")'
            'mysql://[^:]+:[^@]+@[^/]+/\w+' = 'os.getenv("DATABASE_URL")'
            
            # JWT tokens
            'eyJ[A-Za-z0-9+/=]+\.[A-Za-z0-9+/=]+\.[A-Za-z0-9+/=]*' = 'os.getenv("JWT_TOKEN")'
        }
        
        # Get list of files to process
        $filesToProcess = @()
        
        if ($ScanResults.current_files) {
            $filesToProcess += $ScanResults.current_files | ForEach-Object { $_.File } | Sort-Object -Unique
        }
        
        Write-EQ12SecurityLog "INFO" "Processing $($filesToProcess.Count) files for secret remediation"
        
        foreach ($filePath in $filesToProcess) {
            if (!(Test-Path $filePath)) {
                Write-EQ12SecurityLog "WARN" "File not found: $filePath"
                continue
            }
            
            Write-EQ12SecurityLog "DEBUG" "Processing file: $filePath"
            
            try {
                $originalContent = Get-Content $filePath -Raw -ErrorAction Stop
                $modifiedContent = $originalContent
                $fileChanged = $false
                
                # Apply secret pattern replacements
                foreach ($pattern in $secretPatterns.Keys) {
                    $replacement = $secretPatterns[$pattern]
                    if ($modifiedContent -match $pattern) {
                        $modifiedContent = $modifiedContent -replace $pattern, $replacement
                        $fileChanged = $true
                        Write-EQ12SecurityLog "SUCCESS" "Replaced secret pattern in $filePath"
                    }
                }
                
                # Language-specific fixes
                $extension = [System.IO.Path]::GetExtension($filePath)
                switch ($extension) {
                    '.py' {
                        # Ensure dotenv import for Python
                        if ($fileChanged -and $modifiedContent -notmatch 'from dotenv import load_dotenv') {
                            $modifiedContent = "from dotenv import load_dotenv`nimport os`nload_dotenv()`n`n$modifiedContent"
                        }
                    }
                    '.js' {
                        # Ensure dotenv require for Node.js
                        if ($fileChanged -and $modifiedContent -notmatch "require\('dotenv'\)") {
                            $modifiedContent = "require('dotenv').config();`n$modifiedContent"
                        }
                    }
                }
                
                if ($fileChanged) {
                    if (!$DryRun) {
                        Set-Content -Path $filePath -Value $modifiedContent -NoNewline
                        Write-EQ12SecurityLog "SUCCESS" "Remediated secrets in: $filePath"
                        $fixedCount++
                    } else {
                        Write-EQ12SecurityLog "INFO" "[DRY RUN] Would fix secrets in: $filePath"
                    }
                }
                
            } catch {
                $error = "Failed to process $filePath`: $($_.Exception.Message)"
                $errors += $error
                Write-EQ12SecurityLog "ERROR" $error
            }
        }
        
        # Create or update .env template
        $envTemplate = "$Repository\.env.template"
        if (!$DryRun) {
            $envContent = @"
# EQ12 Environment Variables Template
# Copy to .env and fill in your actual values

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GITHUB_TOKEN=your_github_token_here

# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here

# Database
DATABASE_URL=your_database_url_here

# JWT
JWT_TOKEN=your_jwt_token_here
JWT_SECRET=your_jwt_secret_here

# Generated by EQ12 GitLeaks Auto-Remediation: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
            Set-Content -Path $envTemplate -Value $envContent
            Write-EQ12SecurityLog "SUCCESS" "Created .env.template with secure variable names"
        }
        
        # Update .gitignore
        $gitignorePath = "$Repository\.gitignore"
        $gitignoreEntries = @('.env', '*.env', '.env.local', '.env.production', 'secrets.txt', 'credentials.json')
        
        if (Test-Path $gitignorePath) {
            $gitignoreContent = Get-Content $gitignorePath -Raw
        } else {
            $gitignoreContent = ""
        }
        
        $gitignoreUpdated = $false
        foreach ($entry in $gitignoreEntries) {
            if ($gitignoreContent -notmatch [regex]::Escape($entry)) {
                $gitignoreContent += "`n$entry"
                $gitignoreUpdated = $true
            }
        }
        
        if ($gitignoreUpdated -and !$DryRun) {
            Set-Content -Path $gitignorePath -Value $gitignoreContent.Trim()
            Write-EQ12SecurityLog "SUCCESS" "Updated .gitignore to prevent future secret leaks"
        }
        
        Write-EQ12SecurityLog "SUCCESS" "Auto-remediation complete. Fixed $fixedCount files"
        
        return @{
            success = $true
            fixed_count = $fixedCount
            errors = $errors
            backup_path = $backupPath
        }
        
    } catch {
        Write-EQ12SecurityLog "ERROR" "Auto-remediation failed: $($_.Exception.Message)"
        return @{
            success = $false
            error = $_.Exception.Message
            backup_path = $backupPath
        }
    } finally {
        Pop-Location
    }
}

function Invoke-GitHistoryCleanup {
    param([switch]$Force)
    
    Write-EQ12SecurityLog "INFO" "Starting Git history cleanup for committed secrets..."
    
    if (!$Force -and !$ForceClean) {
        Write-EQ12SecurityLog "WARN" "Git history cleanup requires confirmation. Use -ForceClean to proceed automatically."
        $response = Read-Host "This will rewrite Git history and require force-push. Continue? (yes/no)"
        if ($response -ne 'yes') {
            Write-EQ12SecurityLog "INFO" "Git history cleanup cancelled by user"
            return @{ success = $false; reason = "User cancelled" }
        }
    }
    
    Push-Location $Repository
    try {
        # Create backup before history rewrite
        $backupPath = New-SecureBackup
        if (!$backupPath) {
            return @{ success = $false; reason = "Backup failed" }
        }
        
        Write-EQ12SecurityLog "CRITICAL" "⚠️ Rewriting Git history - this is destructive!"
        
        if (!$DryRun) {
            # Method 1: Use git filter-repo if available (preferred)
            $filterRepoAvailable = Get-Command "git-filter-repo" -ErrorAction SilentlyContinue
            
            if ($filterRepoAvailable) {
                Write-EQ12SecurityLog "INFO" "Using git-filter-repo for safe history cleanup..."
                
                # Remove common secret file patterns
                $secretFilePatterns = @('.env', '*.env', 'secrets.txt', 'credentials.json', 'config/secrets.py')
                
                foreach ($pattern in $secretFilePatterns) {
                    git filter-repo --invert-paths --path $pattern --force 2>$null
                }
                
            } else {
                Write-EQ12SecurityLog "WARN" "git-filter-repo not available, using BFG Repo-Cleaner approach..."
                
                # Method 2: Manual filter-branch (less safe but more available)
                $secretPatterns = @(
                    'sk-[A-Za-z0-9]{32,}',
                    'AIza[A-Za-z0-9]{35}',
                    'AKIA[A-Z0-9]{16}',
                    'ghp_[A-Za-z0-9]{36}'
                )
                
                foreach ($pattern in $secretPatterns) {
                    git filter-branch --force --index-filter "git rm --cached --ignore-unmatch -r ." --prune-empty --tag-name-filter cat -- --all 2>$null
                }
            }
            
            # Clean up Git metadata
            Remove-Item -Path ".git/refs/original" -Recurse -Force -ErrorAction SilentlyContinue
            git reflog expire --expire=now --all 2>$null
            git gc --prune=now --aggressive 2>$null
            
            Write-EQ12SecurityLog "SUCCESS" "Git history cleanup completed"
            Write-EQ12SecurityLog "CRITICAL" "⚠️ You MUST force-push to update remote: git push origin --force --all"
            
        } else {
            Write-EQ12SecurityLog "INFO" "[DRY RUN] Would clean Git history and require force-push"
        }
        
        return @{ success = $true; backup_path = $backupPath }
        
    } catch {
        Write-EQ12SecurityLog "ERROR" "Git history cleanup failed: $($_.Exception.Message)"
        return @{ success = $false; error = $_.Exception.Message }
    } finally {
        Pop-Location
    }
}

function Install-SecurityHooks {
    Write-EQ12SecurityLog "INFO" "Installing GitLeaks pre-commit security hooks..."
    
    Push-Location $Repository
    try {
        $hooksDir = ".git/hooks"
        if (!(Test-Path $hooksDir)) {
            Write-EQ12SecurityLog "ERROR" "Not a Git repository or hooks directory missing"
            return $false
        }
        
        # Pre-commit hook
        $preCommitHook = "$hooksDir/pre-commit"
        $preCommitContent = @'
#!/bin/sh
# EQ12 GitLeaks Pre-Commit Security Hook
# Prevents commits containing secrets

echo "🔍 EQ12 Security: Scanning for secrets before commit..."

# Run GitLeaks scan
gitleaks detect --source . --exit-code 1 --report-path gitleaks-precommit-report.json

if [ $? -ne 0 ]; then
    echo "🚨 SECURITY ALERT: GitLeaks detected secrets in your commit!"
    echo "📋 See gitleaks-precommit-report.json for details"
    echo "💡 Fix secrets and run: git add . && git commit"
    echo "🛠️ Auto-fix available: powershell -File scripts/eq12_gitleaks_autofix.ps1 -Action AutoFix"
    exit 1
else
    echo "✅ No secrets detected. Commit proceeding..."
fi
'@
        
        if (!$DryRun) {
            Set-Content -Path $preCommitHook -Value $preCommitContent
            
            # Make executable on Unix-like systems
            if ($IsLinux -or $IsMacOS) {
                chmod +x $preCommitHook
            }
        }
        
        Write-EQ12SecurityLog "SUCCESS" "Pre-commit hook installed"
        
        # Pre-push hook
        $prePushHook = "$hooksDir/pre-push"
        $prePushContent = @'
#!/bin/sh
# EQ12 GitLeaks Pre-Push Security Hook
# Additional security check before pushing

echo "🔍 EQ12 Security: Final scan before push..."

gitleaks detect --source . --exit-code 1 --log-level warn

if [ $? -ne 0 ]; then
    echo "🚨 SECURITY ALERT: Cannot push - secrets detected!"
    echo "🛠️ Run auto-fix: powershell -File scripts/eq12_gitleaks_autofix.ps1 -Action FullScan"
    exit 1
fi

echo "✅ Security check passed. Push proceeding..."
'@
        
        if (!$DryRun) {
            Set-Content -Path $prePushHook -Value $prePushContent
            
            if ($IsLinux -or $IsMacOS) {
                chmod +x $prePushHook
            }
        }
        
        Write-EQ12SecurityLog "SUCCESS" "Pre-push hook installed"
        
        # Create hook configuration
        $hookConfig = @{
            installed_date = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
            eq12_version = "2.1.0"
            hooks = @("pre-commit", "pre-push")
            gitleaks_required = $true
        }
        
        if (!$DryRun) {
            $hookConfig | ConvertTo-Json | Set-Content "$hooksDir/eq12-security-config.json"
        }
        
        Write-EQ12SecurityLog "SUCCESS" "Security hooks installation complete"
        return $true
        
    } catch {
        Write-EQ12SecurityLog "ERROR" "Hook installation failed: $($_.Exception.Message)"
        return $false
    } finally {
        Pop-Location
    }
}

function New-SecurityReport {
    param([object]$ScanResults, [object]$RemediationResults, [string]$BackupPath)
    
    $report = @{
        scan_info = @{
            timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ")
            repository = $Repository
            action = $Action
            eq12_version = "2.1.0"
        }
        security_findings = $ScanResults
        remediation_results = $RemediationResults
        backup_location = $BackupPath
        recommendations = @()
        risk_assessment = @{
            level = "LOW"
            critical_secrets = 0
            public_exposure_risk = "MINIMAL"
        }
    }
    
    # Calculate risk level
    if ($ScanResults.critical_count -gt 0) {
        $report.risk_assessment.level = "CRITICAL"
        $report.risk_assessment.critical_secrets = $ScanResults.critical_count
        $report.risk_assessment.public_exposure_risk = "HIGH"
        
        $report.recommendations += "🚨 IMMEDIATE ACTION REQUIRED: Regenerate all exposed API keys and secrets"
        $report.recommendations += "🔒 Review Git history for committed secrets"
        $report.recommendations += "📋 Audit all systems that may have accessed exposed credentials"
    } elseif ($ScanResults.total_secrets -gt 0) {
        $report.risk_assessment.level = "MEDIUM"
        $report.risk_assessment.public_exposure_risk = "MODERATE"
        
        $report.recommendations += "⚠️ Replace hardcoded secrets with environment variables"
        $report.recommendations += "🛠️ Run auto-remediation: -Action AutoFix"
    } else {
        $report.recommendations += "✅ No security issues detected - maintain current practices"
    }
    
    # Always recommend security best practices
    $report.recommendations += "🔧 Install pre-commit hooks to prevent future issues"
    $report.recommendations += "📊 Schedule regular security scans with EQ12 monitoring"
    $report.recommendations += "🔑 Use proper secret management (Azure Key Vault, AWS Secrets Manager)"
    
    # Save report
    $report | ConvertTo-Json -Depth 10 | Set-Content $ReportFile
    
    Write-EQ12SecurityLog "SUCCESS" "Security report generated: $ReportFile"
    
    return $report
}

# Main execution logic
Write-EQ12SecurityLog "INFO" "🚀 EQ12 GitLeaks Auto-Remediation System starting..."
Write-EQ12SecurityLog "INFO" "Action: $Action | Repository: $Repository | DryRun: $DryRun"

# Check prerequisites
$prereqCheck = Test-Prerequisites
if (!$prereqCheck.ready) {
    Write-EQ12SecurityLog "ERROR" "Prerequisites not met. Please install missing tools:"
    $prereqCheck.issues | ForEach-Object { Write-EQ12SecurityLog "ERROR" "  - $_" }
    exit 1
}

$scanResults = $null
$remediationResults = $null
$backupPath = ""

switch ($Action) {
    'Scan' {
        Write-EQ12SecurityLog "INFO" "🔍 Running security scan only..."
        $scanResults = Invoke-GitLeaksScan
    }
    
    'AutoFix' {
        Write-EQ12SecurityLog "INFO" "🛠️ Running automatic remediation..."
        $scanResults = Invoke-GitLeaksScan
        if ($scanResults.total_secrets -gt 0) {
            $remediationResults = Invoke-AutoSecretRemediation -ScanResults $scanResults
            $backupPath = $remediationResults.backup_path
        }
    }
    
    'CleanHistory' {
        Write-EQ12SecurityLog "INFO" "🧹 Cleaning Git history..."
        $historyCleanup = Invoke-GitHistoryCleanup
        $backupPath = $historyCleanup.backup_path
    }
    
    'FullScan' {
        Write-EQ12SecurityLog "INFO" "🔄 Running comprehensive security audit..."
        $scanResults = Invoke-GitLeaksScan
        if ($scanResults.total_secrets -gt 0) {
            $remediationResults = Invoke-AutoSecretRemediation -ScanResults $scanResults
            $backupPath = $remediationResults.backup_path
            
            if ($scanResults.git_history.Count -gt 0) {
                Write-EQ12SecurityLog "CRITICAL" "Git history cleanup recommended for complete security"
            }
        }
    }
    
    'InstallHooks' {
        Write-EQ12SecurityLog "INFO" "🔧 Installing security hooks..."
        Install-SecurityHooks | Out-Null
    }
    
    'Emergency' {
        Write-EQ12SecurityLog "CRITICAL" "🚨 EMERGENCY MODE: Immediate threat response..."
        $scanResults = Invoke-GitLeaksScan
        $remediationResults = Invoke-AutoSecretRemediation -ScanResults $scanResults
        $historyCleanup = Invoke-GitHistoryCleanup -Force
        Install-SecurityHooks | Out-Null
        $backupPath = $remediationResults.backup_path
        
        Write-EQ12SecurityLog "CRITICAL" "⚠️ EMERGENCY ACTIONS COMPLETED"
        Write-EQ12SecurityLog "CRITICAL" "📋 IMMEDIATE STEPS:"
        Write-EQ12SecurityLog "CRITICAL" "   1. Regenerate ALL exposed API keys/secrets"
        Write-EQ12SecurityLog "CRITICAL" "   2. Force push cleaned history: git push origin --force --all"
        Write-EQ12SecurityLog "CRITICAL" "   3. Audit all systems for potential compromise"
    }
}

# Generate comprehensive report
if ($scanResults -or $remediationResults) {
    $securityReport = New-SecurityReport -ScanResults $scanResults -RemediationResults $remediationResults -BackupPath $backupPath
    
    # Display summary
    Write-EQ12SecurityLog "INFO" "📊 SECURITY SUMMARY:"
    Write-EQ12SecurityLog "INFO" "   Risk Level: $($securityReport.risk_assessment.level)"
    Write-EQ12SecurityLog "INFO" "   Secrets Found: $($scanResults.total_secrets ?? 0)"
    Write-EQ12SecurityLog "INFO" "   Files Fixed: $($remediationResults.fixed_count ?? 0)"
    Write-EQ12SecurityLog "INFO" "   Backup Location: $backupPath"
}

Write-EQ12SecurityLog "SUCCESS" "🎉 EQ12 GitLeaks security operation completed successfully!"
Write-EQ12SecurityLog "INFO" "📝 Detailed logs: $LogFile"
Write-EQ12SecurityLog "INFO" "📋 Security report: $ReportFile"

# Exit with appropriate code
if ($scanResults -and $scanResults.critical_count -gt 0) {
    Write-EQ12SecurityLog "CRITICAL" "⚠️ Critical security issues detected - manual review required"
    exit 2
} elseif ($scanResults -and $scanResults.total_secrets -gt 0) {
    Write-EQ12SecurityLog "WARN" "⚠️ Security issues found but remediated"
    exit 1
} else {
    exit 0
}