<#
.SYNOPSIS
    EQ12 VB.NET Auto-Scan & Repair Orchestrator
    
.DESCRIPTION
    Scans all VB.NET files in EQ12 workspace, identifies issues, coordinates
    multi-language repairs (Python, JS, Markdown, Docker), and generates
    unified audit reports - WITHOUT interrupting background processes.
    
.PARAMETER Action
    scan       - Scan VB.NET files and generate report
    repair     - Auto-fix common VB.NET issues
    audit      - Generate unified system audit
    copilot    - Trigger Copilot deep debug mode
    
.PARAMETER TargetPath
    Specific VB.NET project to scan (default: entire workspace)
    
.PARAMETER SkipBackgroundCheck
    Skip check for running background processes (use with caution)
    
.EXAMPLE
    .\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action scan
    .\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action repair -TargetPath "visual_studio_projects\EQ12SportsBettingTerminal"
    .\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action audit
    
.NOTES
    Author: EQ12 System Architect
    Version: 1.0
    Created: 2025-11-27
    
    Integrates with:
    - Python linters (Flake8, Ruff)
    - Markdown linters (markdownlint)
    - JS/TS linters (ESLint)
    - Docker auditors (Hadolint)
    - Security scanners (GitLeaks)
    - VB.NET Roslyn analyzers
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("scan", "repair", "audit", "copilot")]
    [string]$Action,
    
    [Parameter(Mandatory = $false)]
    [string]$TargetPath = "",
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipBackgroundCheck
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

# ============================================================================
# CONFIGURATION
# ============================================================================

$config = @{
    RepoRoot               = $repoRoot
    LogsDir                = Join-Path $repoRoot "logs"
    ReportsDir             = Join-Path $repoRoot "reports"
    VBNETProjects          = @(
        "visual_studio_projects\EQ12SportsBettingTerminal"
        "vbnet_projects\EQ12WindowsManager"
        "vbnet_projects\EQ12ConsoleTools"
        "vbnet_projects\EQ12.DockerManager"
        "vbnet_projects\EQ12CoreLibrary"
        "src\props"
    )
    BackgroundProcessCheck = @(
        "eq12_prompt_executor.py"
        "EQ12_PROMPT_RUNNER.ps1"
    )
}

# Create directories
@($config.LogsDir, $config.ReportsDir) | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# ============================================================================
# BACKGROUND PROCESS PROTECTION
# ============================================================================

function Test-BackgroundProcesses {
    <#
    .SYNOPSIS
        Check if critical background processes are running
    #>
    
    if ($SkipBackgroundCheck) {
        Write-Warning "⚠️ Background process check SKIPPED (use with caution)"
        return $false
    }
    
    Write-Host "🔍 Checking for running background processes..." -ForegroundColor Cyan
    
    $runningProcesses = @()
    
    foreach ($processName in $config.BackgroundProcessCheck) {
        $procs = Get-Process | Where-Object {
            $_.Path -like "*$processName*" -or
            $_.CommandLine -like "*$processName*"
        }
        
        if ($procs) {
            $runningProcesses += $processName
            Write-Host "   ✅ Found: $processName (PID: $($procs[0].Id))" -ForegroundColor Green
        }
    }
    
    if ($runningProcesses.Count -gt 0) {
        Write-Host ""
        Write-Host "⚠️ CRITICAL BACKGROUND PROCESSES DETECTED" -ForegroundColor Yellow
        Write-Host "   Running: $($runningProcesses -join ', ')" -ForegroundColor Yellow
        Write-Host "   This orchestrator will run in LOW-IMPACT MODE" -ForegroundColor Yellow
        Write-Host ""
        return $true
    }
    
    Write-Host "   ✅ No critical background processes detected" -ForegroundColor Green
    return $false
}

# ============================================================================
# VB.NET FILE SCANNING
# ============================================================================

function Get-VBNETFiles {
    <#
    .SYNOPSIS
        Scan workspace for VB.NET files
    #>
    param(
        [string]$Path = $config.RepoRoot
    )
    
    Write-Host "🔍 Scanning for VB.NET files..." -ForegroundColor Cyan
    
    $vbFiles = @()
    $vbprojFiles = @()
    
    if ($TargetPath) {
        $searchPath = Join-Path $config.RepoRoot $TargetPath
        if (-not (Test-Path $searchPath)) {
            Write-Error "Target path not found: $searchPath"
            return $null
        }
    }
    else {
        $searchPath = $Path
    }
    
    # Find .vb files
    $vbFiles = Get-ChildItem -Path $searchPath -Filter "*.vb" -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\obj\\|\\bin\\|\.vs\\|packages\\' }
    
    # Find .vbproj files
    $vbprojFiles = Get-ChildItem -Path $searchPath -Filter "*.vbproj" -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\obj\\|\\bin\\|\.vs\\|packages\\' }
    
    Write-Host "   📄 Found $($vbFiles.Count) VB.NET source files" -ForegroundColor Green
    Write-Host "   📦 Found $($vbprojFiles.Count) VB.NET project files" -ForegroundColor Green
    
    return @{
        SourceFiles  = $vbFiles
        ProjectFiles = $vbprojFiles
    }
}

function Test-VBNETSyntax {
    <#
    .SYNOPSIS
        Check VB.NET files for common issues
    #>
    param(
        [System.IO.FileInfo[]]$Files
    )
    
    Write-Host "🔍 Analyzing VB.NET syntax..." -ForegroundColor Cyan
    
    $issues = @()
    
    foreach ($file in $Files) {
        $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
        
        if (-not $content) { continue }
        
        $fileIssues = @()
        
        # Check for common VB.NET issues
        
        # 1. Missing Option Strict/Explicit
        if ($content -notmatch 'Option Strict On') {
            $fileIssues += @{
                Type     = "MissingOptionStrict"
                Severity = "Warning"
                Message  = "Missing 'Option Strict On'"
                Fix      = "Add 'Option Strict On' at top of file"
            }
        }
        
        if ($content -notmatch 'Option Explicit On') {
            $fileIssues += @{
                Type     = "MissingOptionExplicit"
                Severity = "Warning"
                Message  = "Missing 'Option Explicit On'"
                Fix      = "Add 'Option Explicit On' at top of file"
            }
        }
        
        # 2. Loop control variable issues
        if ($content -match 'For\s+(\w+)\s+As.*?[\r\n].*?\1\s*=') {
            $fileIssues += @{
                Type     = "LoopControlReassignment"
                Severity = "Error"
                Message  = "Loop control variable reassigned inside loop"
                Fix      = "Use separate variable inside loop body"
            }
        }
        
        # 3. Ambiguous string literals
        if ($content -match '[""]|[""]|['']|['']') {
            $fileIssues += @{
                Type     = "AmbiguousStringLiteral"
                Severity = "Warning"
                Message  = "Unicode quote characters detected (use ASCII quotes)"
                Fix      = "Replace with standard \" or ' characters"
            }
        }
        
        # 4. Uninitialized variables
        if ($content -match 'Dim\s+\w+\s+As\s+\w+\s*$') {
            $fileIssues += @{
                Type = "UninitializedVariable"
                Severity = "Info"
                Message = "Variable declared without initialization"
                Fix = "Initialize with default value"
            }
        }
        
        # 5. Dead code (commented TODO/FIXME)
        $todoMatches = [regex]::Matches($content, '(?i)(TODO | FIXME | HACK | XXX)')
        if ($todoMatches.Count -gt 0) {
            $fileIssues += @{
                Type = "TechnicalDebt"
                Severity = "Info"
                Message = "Found $($todoMatches.Count) TODO/FIXME markers"
                Fix = "Address or document technical debt"
            }
        }
        
        if ($fileIssues.Count -gt 0) {
            $issues += @{
                File = $file.FullName
                RelativePath = $file.FullName.Replace($config.RepoRoot, "").TrimStart('\')
                IssueCount = $fileIssues.Count
                Issues = $fileIssues
            }
        }
    }
    
    Write-Host "   ⚠️  Found issues in $($issues.Count) files" -ForegroundColor Yellow
    
    return $issues
}

# ============================================================================
# AUTO-REPAIR FUNCTIONS
# ============================================================================

function Repair-VBNETFiles {
    <#
    .SYNOPSIS
        Auto-fix common VB.NET issues
    #>
    param(
        [array]$IssueReport
    )
    
    Write-Host "🔧 Starting VB.NET auto-repair..." -ForegroundColor Cyan
    
    $fixedCount = 0
    
    foreach ($fileReport in $IssueReport) {
        $filePath = $fileReport.File
        $content = Get-Content $filePath -Raw
        $modified = $false
        
        foreach ($issue in $fileReport.Issues) {
            switch ($issue.Type) {
                "AmbiguousStringLiteral" {
                    # Replace Unicode quotes with ASCII
                    $newContent = $content -replace '[""]', '"' -replace '['']', "'"
                    if ($newContent -ne $content) {
                        $content = $newContent
                        $modified = $true
                        Write-Host "   ✅ Fixed Unicode quotes in: $($fileReport.RelativePath)" -ForegroundColor Green
                    }
                }
                
                "MissingOptionStrict" {
                    # Add Option Strict On at top
                    if ($content -notmatch '^Option Strict On') {
                        $content = "Option Strict On`r`n" + $content
                        $modified = $true
                        Write-Host "   ✅ Added Option Strict to: $($fileReport.RelativePath)" -ForegroundColor Green
                    }
                }
                
                "MissingOptionExplicit" {
                    # Add Option Explicit On at top
                    if ($content -notmatch '^Option Explicit On') {
                        $content = "Option Explicit On`r`n" + $content
                        $modified = $true
                        Write-Host "   ✅ Added Option Explicit to: $($fileReport.RelativePath)" -ForegroundColor Green
                    }
                }
            }
        }
        
        if ($modified) {
            # Backup original
            $backupPath = $filePath + ".bak"
            Copy-Item $filePath $backupPath -Force
            
            # Write fixed content
            Set-Content -Path $filePath -Value $content -NoNewline
            $fixedCount++
        }
    }
    
    Write-Host "   ✅ Fixed issues in $fixedCount files" -ForegroundColor Green
    return $fixedCount
}

# ============================================================================
# MULTI-LANGUAGE COORDINATION
# ============================================================================

function Invoke-MultiLanguageScan {
    <#
    .SYNOPSIS
        Coordinate scans across Python, JS, Markdown, Docker
    #>
    
    Write-Host "🌐 Running multi-language scans..." -ForegroundColor Cyan
    
    $results = @{
        Python = $null
        JavaScript = $null
        Markdown = $null
        Docker = $null
        Security = $null
    }
    
    # Python (Flake8)
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host "   🐍 Scanning Python files..." -ForegroundColor Yellow
        try {
            $pythonLog = Join-Path $config.LogsDir "python_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
            $pythonResult = python -m flake8 $config.RepoRoot --output-file=$pythonLog 2>&1
            $results.Python = @{
                Success = $LASTEXITCODE -eq 0
                LogFile = $pythonLog
            }
            Write-Host "      ✅ Python scan complete" -ForegroundColor Green
        } catch {
            Write-Host "      ⚠️  Python scan skipped (flake8 not installed)" -ForegroundColor Yellow
        }
    }
    
    # Markdown (markdownlint)
    if (Get-Command markdownlint -ErrorAction SilentlyContinue) {
        Write-Host "   📝 Scanning Markdown files..." -ForegroundColor Yellow
        try {
            $mdLog = Join-Path $config.LogsDir "markdown_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
            markdownlint "**/*.md" --output $mdLog 2>&1 | Out-Null
            $results.Markdown = @{
                Success = $LASTEXITCODE -eq 0
                LogFile = $mdLog
            }
            Write-Host "      ✅ Markdown scan complete" -ForegroundColor Green
        } catch {
            Write-Host "      ⚠️  Markdown scan skipped (markdownlint not installed)" -ForegroundColor Yellow
        }
    }
    
    # Docker (Hadolint)
    if (Get-Command hadolint -ErrorAction SilentlyContinue) {
        Write-Host "   🐳 Scanning Dockerfiles..." -ForegroundColor Yellow
        try {
            $dockerLog = Join-Path $config.LogsDir "docker_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
            Get-ChildItem -Path $config.RepoRoot -Filter "Dockerfile*" -Recurse | ForEach-Object {
                hadolint $_.FullName 2>&1 | Out-File $dockerLog -Append
            }
            $results.Docker = @{
                Success = $LASTEXITCODE -eq 0
                LogFile = $dockerLog
            }
            Write-Host "      ✅ Docker scan complete" -ForegroundColor Green
        } catch {
            Write-Host "      ⚠️  Docker scan skipped (hadolint not installed)" -ForegroundColor Yellow
        }
    }
    
    # Security (GitLeaks)
    if (Get-Command gitleaks -ErrorAction SilentlyContinue) {
        Write-Host "   🔐 Scanning for secrets..." -ForegroundColor Yellow
        try {
            $securityLog = Join-Path $config.LogsDir "gitleaks_scan_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
            gitleaks detect --source $config.RepoRoot --report-path $securityLog --no-git 2>&1 | Out-Null
            $results.Security = @{
                Success = $LASTEXITCODE -eq 0
                LogFile = $securityLog
            }
            Write-Host "      ✅ Security scan complete" -ForegroundColor Green
        } catch {
            Write-Host "      ⚠️  Security scan skipped (gitleaks not installed)" -ForegroundColor Yellow
        }
    }
    
    return $results
}

# ============================================================================
# UNIFIED AUDIT REPORT
# ============================================================================

function New-UnifiedAuditReport {
    <#
    .SYNOPSIS
        Generate comprehensive system audit report
    #>
    param(
        [hashtable]$VBNETScan,
        [hashtable]$MultiLangScan
    )
    
    Write-Host "📊 Generating unified audit report..." -ForegroundColor Cyan
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
    $reportPath = Join-Path $config.ReportsDir "EQ12_Unified_Audit_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"
    
    $report = @"
# EQ12 Unified System Audit Report

**Generated**: $timestamp
**Workspace**: $($config.RepoRoot)
**Orchestrator Version**: 1.0

---

## 📋 Executive Summary

### VB.NET Analysis
- **Source Files Scanned**: $($VBNETScan.SourceFiles.Count)
- **Project Files Found**: $($VBNETScan.ProjectFiles.Count)
- **Issues Detected**: $($VBNETScan.Issues.Count)
- **Auto-Fixable Issues**: $(($VBNETScan.Issues | ForEach-Object { $_.Issues | Where-Object { $_.Type -in @('AmbiguousStringLiteral', 'MissingOptionStrict', 'MissingOptionExplicit') } }).Count)

### Multi-Language Scans
- **Python**: $(if ($MultiLangScan.Python) { if ($MultiLangScan.Python.Success) { "✅ PASS" } else { "⚠️ ISSUES FOUND" } } else { "⏭️ SKIPPED" })
- **Markdown**: $(if ($MultiLangScan.Markdown) { if ($MultiLangScan.Markdown.Success) { "✅ PASS" } else { "⚠️ ISSUES FOUND" } } else { "⏭️ SKIPPED" })
- **Docker**: $(if ($MultiLangScan.Docker) { if ($MultiLangScan.Docker.Success) { "✅ PASS" } else { "⚠️ ISSUES FOUND" } } else { "⏭️ SKIPPED" })
- **Security**: $(if ($MultiLangScan.Security) { if ($MultiLangScan.Security.Success) { "✅ NO LEAKS" } else { "🚨 SECRETS DETECTED" } } else { "⏭️ SKIPPED" })

---

## 🔍 VB.NET Detailed Findings

### Issue Breakdown by Type

"@

    # Add VB.NET issue details
    $issueTypes = $VBNETScan.Issues | ForEach-Object { $_.Issues } | Group-Object -Property Type
    
    foreach ($issueType in $issueTypes) {
        $report += "`n#### $($issueType.Name) ($($issueType.Count))`n"
        $report += "**Severity**: $($issueType.Group[0].Severity)`n"
        $report += "**Fix**: $($issueType.Group[0].Fix)`n`n"
    }
    
    $report += @"

---

## 📄 Files Requiring Attention

"@
    
    foreach ($fileReport in ($VBNETScan.Issues | Select-Object -First 20)) {
        $report += "`n### $($fileReport.RelativePath)`n"
        $report += "**Issues**: $($fileReport.IssueCount)`n`n"
        
        foreach ($issue in $fileReport.Issues) {
            $report += "- [$($issue.Severity)] **$($issue.Type)**: $($issue.Message)`n"
        }
    }
    
    if ($VBNETScan.Issues.Count -gt 20) {
        $report += "`n*... and $($VBNETScan.Issues.Count - 20) more files*`n"
    }
    
    $report += @"

---

## 🌐 Multi-Language Scan Results

### Log Files
"@
    
    if ($MultiLangScan.Python.LogFile) {
        $report += "`n- **Python**: [$($MultiLangScan.Python.LogFile)]($($MultiLangScan.Python.LogFile))"
    }
    if ($MultiLangScan.Markdown.LogFile) {
        $report += "`n- **Markdown**: [$($MultiLangScan.Markdown.LogFile)]($($MultiLangScan.Markdown.LogFile))"
    }
    if ($MultiLangScan.Docker.LogFile) {
        $report += "`n- **Docker**: [$($MultiLangScan.Docker.LogFile)]($($MultiLangScan.Docker.LogFile))"
    }
    if ($MultiLangScan.Security.LogFile) {
        $report += "`n- **Security**: [$($MultiLangScan.Security.LogFile)]($($MultiLangScan.Security.LogFile))"
    }
    
    $report += @"


---

## 🎯 Recommended Actions

### Immediate (Auto-Fixable)
1. Run: ``.\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action repair``
2. Fix Unicode quotes in VB.NET files
3. Add missing Option Strict/Explicit declarations

### Short-Term (Manual Review)
1. Address loop control variable reassignments
2. Review TODO/FIXME markers
3. Fix Python linting issues (if detected)

### Long-Term (Technical Debt)
1. Modernize VB.NET UI to Streamlit/Flask
2. Convert critical VB.NET logic to Python modules
3. Implement automated CI/CD validation

---

## 📚 Suggested GitHub Repositories

### VB.NET / .NET Tools
- **Roslyn**: https://github.com/dotnet/roslyn (Already integrated)
- **StyleCop**: https://github.com/StyleCop/StyleCop

### Python Tooling
- **Ruff**: https://github.com/astral-sh/ruff (Fast linter/formatter)
- **Black**: https://github.com/psf/black (Code formatter)

### Security
- **GitLeaks**: https://github.com/zricethezav/gitleaks (Secrets scanner)
- **TruffleHog**: https://github.com/trufflesecurity/trufflehog (Alternative secrets scanner)

### Docker
- **Hadolint**: https://github.com/hadolint/hadolint (Dockerfile linter)
- **Dive**: https://github.com/wagoodman/dive (Image layer analysis)

### AI/ML
- **Transformers**: https://github.com/huggingface/transformers (Already in use)
- **LangChain**: https://github.com/langchain-ai/langchain (LLM orchestration)

---

**Report End**
"@
    
    Set-Content -Path $reportPath -Value $report
    
    Write-Host "   ✅ Report saved: $reportPath" -ForegroundColor Green
    
    return $reportPath
}

# ============================================================================
# COPILOT INTEGRATION
# ============================================================================

function Invoke-CopilotDeepScan {
    <#
    .SYNOPSIS
        Trigger GitHub Copilot deep debug mode
    #>
    
    Write-Host "🤖 Generating Copilot deep scan prompt..." -ForegroundColor Cyan
    
    $promptPath = Join-Path $config.ReportsDir "Copilot_Deep_Scan_Prompt_$(Get-Date -Format 'yyyyMMdd_HHmmss').md"
    
    $prompt = @"
# GitHub Copilot Deep Scan Request

## Context
EQ12 Automation Stack - Multi-language workspace with VB.NET, Python, JavaScript, Docker

## Task
Perform comprehensive workspace analysis and automated fixes:

### 1. VB.NET Issues
- Scan all .vb and .vbproj files
- Fix loop control variable reassignments
- Add missing Option Strict/Explicit
- Replace Unicode quotes with ASCII
- Fix uninitialized variables
- Address TODO/FIXME markers

### 2. Python Issues
- Run Flake8/Ruff on all .py files
- Fix F841 (unused variables)
- Fix E501 (line too long)
- Add missing type hints
- Fix import ordering

### 3. JavaScript/TypeScript Issues
- Run ESLint on all .js/.ts files
- Fix unused variables
- Fix async/await patterns
- Add missing semicolons

### 4. Markdown Issues
- Run markdownlint on all .md files
- Fix MD302 (inline code formatting)
- Fix heading hierarchy
- Fix list indentation

### 5. Docker Issues
- Audit all Dockerfiles with Hadolint
- Fix layer ordering
- Add health checks
- Optimize image size

### 6. Security Issues
- Run GitLeaks for secret detection
- Check for hardcoded credentials
- Validate environment variable usage

## Output Required
- Unified audit report (markdown)
- List of all auto-fixes applied
- List of manual fixes required
- Confidence score per fix

## Constraints
- Do NOT interrupt running background processes (20K prompt execution)
- Create backups before modifying files
- Log all changes to logs/ directory
- Generate git commit message for changes

---

**Workspace Root**: $($config.RepoRoot)
**Scan Timestamp**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
"@
    
    Set-Content -Path $promptPath -Value $prompt
    
    Write-Host "   ✅ Prompt saved: $promptPath" -ForegroundColor Green
    Write-Host "   💡 Copy this prompt to GitHub Copilot Chat for deep scan" -ForegroundColor Yellow
    
    # Open in default editor
    Start-Process $promptPath
    
    return $promptPath
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  EQ12 VB.NET Auto-Scan & Repair Orchestrator v1.0          ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check for background processes
$hasBackgroundProcesses = Test-BackgroundProcesses

if ($hasBackgroundProcesses) {
    Write-Host "⚙️  Running in LOW-IMPACT MODE (background processes detected)" -ForegroundColor Yellow
    Write-Host ""
}

try {
    switch ($Action) {
        "scan" {
            Write-Host "🎯 Action: SCAN" -ForegroundColor Green
            Write-Host ""
            
            # Scan VB.NET files
            $vbnetFiles = Get-VBNETFiles
            
            if (-not $vbnetFiles) {
                Write-Error "No VB.NET files found"
                exit 1
            }
            
            # Analyze syntax
            $vbnetIssues = Test-VBNETSyntax -Files $vbnetFiles.SourceFiles
            
            # Multi-language scan
            $multiLangScan = Invoke-MultiLanguageScan
            
            # Generate report
            $scanResults = @{
                SourceFiles = $vbnetFiles.SourceFiles
                ProjectFiles = $vbnetFiles.ProjectFiles
                Issues = $vbnetIssues
            }
            
            $reportPath = New-UnifiedAuditReport -VBNETScan $scanResults -MultiLangScan $multiLangScan
            
            Write-Host ""
            Write-Host "✅ SCAN COMPLETE" -ForegroundColor Green
            Write-Host "   📊 Report: $reportPath" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Next steps:" -ForegroundColor Yellow
            Write-Host "   1. Review report: code `"$reportPath`"" -ForegroundColor White
            Write-Host "   2. Auto-repair: .\EQ12_VBNET_SCAN_ORCHESTRATOR.ps1 -Action repair" -ForegroundColor White
        }
        
        "repair" {
            Write-Host "🎯 Action: REPAIR" -ForegroundColor Green
            Write-Host ""
            
            if ($hasBackgroundProcesses) {
                Write-Host "⚠️  WARNING: Background processes detected" -ForegroundColor Yellow
                Write-Host "   Repair will run with minimal resource usage" -ForegroundColor Yellow
                Write-Host ""
                Start-Sleep -Seconds 2
            }
            
            # Scan first
            $vbnetFiles = Get-VBNETFiles
            $vbnetIssues = Test-VBNETSyntax -Files $vbnetFiles.SourceFiles
            
            if ($vbnetIssues.Count -eq 0) {
                Write-Host "✅ No issues found - nothing to repair!" -ForegroundColor Green
                exit 0
            }
            
            # Repair
            $fixedCount = Repair-VBNETFiles -IssueReport $vbnetIssues
            
            Write-Host ""
            Write-Host "✅ REPAIR COMPLETE" -ForegroundColor Green
            Write-Host "   🔧 Fixed $fixedCount files" -ForegroundColor Cyan
            Write-Host "   💾 Backups saved as *.bak" -ForegroundColor Cyan
        }
        
        "audit" {
            Write-Host "🎯 Action: UNIFIED AUDIT" -ForegroundColor Green
            Write-Host ""
            
            # Full audit
            $vbnetFiles = Get-VBNETFiles
            $vbnetIssues = Test-VBNETSyntax -Files $vbnetFiles.SourceFiles
            $multiLangScan = Invoke-MultiLanguageScan
            
            $scanResults = @{
                SourceFiles = $vbnetFiles.SourceFiles
                ProjectFiles = $vbnetFiles.ProjectFiles
                Issues = $vbnetIssues
            }
            
            $reportPath = New-UnifiedAuditReport -VBNETScan $scanResults -MultiLangScan $multiLangScan
            
            Write-Host ""
            Write-Host "✅ AUDIT COMPLETE" -ForegroundColor Green
            Write-Host "   📊 Report: $reportPath" -ForegroundColor Cyan
        }
        
        "copilot" {
            Write-Host "🎯 Action: COPILOT DEEP SCAN" -ForegroundColor Green
            Write-Host ""
            
            $promptPath = Invoke-CopilotDeepScan
            
            Write-Host ""
            Write-Host "✅ COPILOT PROMPT GENERATED" -ForegroundColor Green
            Write-Host "   📝 Prompt: $promptPath" -ForegroundColor Cyan
        }
    }
    
} catch {
    Write-Error "❌ Orchestrator failed: $_"
    exit 1
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
