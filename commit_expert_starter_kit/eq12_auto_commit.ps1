<#
.SYNOPSIS
    EQ12 Automated Commit System - PowerShell Git Automation Suite

.DESCRIPTION
    Comprehensive commit automation for the EQ12 stack:
    1. Auto-commit after successful script execution
    2. Signed commits with GPG
    3. Commit message templating
    4. Pre-commit validation
    5. Rollback support

.EXAMPLE
    .\eq12_auto_commit.ps1 -Message "feat(odds): add live betting scanner" -Sign
    .\eq12_auto_commit.ps1 -Auto -ScriptResult $lastExitCode
    .\eq12_auto_commit.ps1 -Template "fix" -Scope "database" -Description "transaction rollback bug"

.NOTES
    Author: EQ12 System
    Date: 2025-11-29
    Version: 1.0
#>

[CmdletBinding()]
param(
    # Manual commit message
    [Parameter(Mandatory = $false, ParameterSetName = 'Manual')]
    [string]$Message,

    # Auto-commit based on script success
    [Parameter(Mandatory = $false, ParameterSetName = 'Auto')]
    [switch]$Auto,

    # Last script exit code for auto-commit
    [Parameter(Mandatory = $false, ParameterSetName = 'Auto')]
    [int]$ScriptResult = 0,

    # Use commit message template
    [Parameter(Mandatory = $false, ParameterSetName = 'Template')]
    [ValidateSet('feat', 'fix', 'docs', 'style', 'refactor', 'test', 'chore')]
    [string]$Template,

    # Template scope
    [Parameter(Mandatory = $false, ParameterSetName = 'Template')]
    [string]$Scope,

    # Template description
    [Parameter(Mandatory = $false, ParameterSetName = 'Template')]
    [string]$Description,

    # Sign commit with GPG
    [switch]$Sign,

    # Run pre-commit checks
    [switch]$PreCommit,

    # Push after commit
    [switch]$Push,

    # Remote name (default: origin)
    [string]$Remote = 'origin',

    # Branch name (default: main)
    [string]$Branch = 'main',

    # Dry run (don't actually commit)
    [switch]$DryRun
)

# ============================================================
# COMMIT EXPERT CONFIGURATION
# ============================================================

$Script:Config = @{
    LogPath                = "C:\EQ12\logs\commit_audit.log"
    GitIgnoreSecrets       = @('*.key', '*.env', 'secrets.json', 'api_keys.json')
    MaxCommitMessageLength = 72
    RequireScope           = $true
    AutoSign               = $Sign
}

# ============================================================
# LOGGING FUNCTIONS
# ============================================================

function Write-CommitLog {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('INFO', 'SUCCESS', 'WARNING', 'ERROR')]
        [string]$Level,

        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    # Console output with colors
    $color = switch ($Level) {
        'INFO' { 'Cyan' }
        'SUCCESS' { 'Green' }
        'WARNING' { 'Yellow' }
        'ERROR' { 'Red' }
    }

    Write-Host $logEntry -ForegroundColor $color

    # File logging
    $logDir = Split-Path $Script:Config.LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }

    Add-Content -Path $Script:Config.LogPath -Value $logEntry
}

# ============================================================
# PRE-COMMIT VALIDATION
# ============================================================

function Test-CommitReadiness {
    [CmdletBinding()]
    param()

    Write-CommitLog -Level INFO -Message "Running pre-commit validation..."

    $issues = @()

    # Check 1: Is this a Git repository?
    if (-not (Test-Path ".git")) {
        $issues += "❌ Not a Git repository. Run 'git init' first."
    }
    else {
        Write-CommitLog -Level SUCCESS -Message "✅ Git repository detected"
    }

    # Check 2: Are there staged changes?
    $status = git status --porcelain
    if (-not $status) {
        $issues += "⚠️ No changes to commit. Run 'git add <file>' first."
    }
    else {
        $stagedCount = ($status | Where-Object { $_ -match '^[MADRCU]' }).Count
        Write-CommitLog -Level SUCCESS -Message "✅ $stagedCount file(s) staged for commit"
    }

    # Check 3: Are secrets being committed?
    $stagedFiles = git diff --cached --name-only
    $secretFiles = $stagedFiles | Where-Object {
        $file = $_
        $Script:Config.GitIgnoreSecrets | Where-Object { $file -like $_ }
    }

    if ($secretFiles) {
        $issues += "🔒 SECURITY WARNING: Potential secrets detected: $($secretFiles -join ', ')"
        Write-CommitLog -Level ERROR -Message "❌ Secrets may be exposed!"
    }

    # Check 4: Git user configured?
    $userName = git config user.name
    $userEmail = git config user.email

    if (-not $userName -or -not $userEmail) {
        $issues += "❌ Git user not configured. Run: git config user.name 'Your Name' && git config user.email 'you@example.com'"
    }
    else {
        Write-CommitLog -Level SUCCESS -Message "✅ Git user: $userName <$userEmail>"
    }

    # Check 5: GPG signing available (if requested)
    if ($Sign) {
        $gpgProgram = git config gpg.program
        if (-not $gpgProgram) {
            $issues += "⚠️ GPG program not configured. Signing may fail."
        }
        else {
            Write-CommitLog -Level SUCCESS -Message "✅ GPG program: $gpgProgram"
        }

        # Check for GPG keys
        $gpgKeys = & gpg --list-keys 2>$null
        if (-not $gpgKeys) {
            $issues += "⚠️ No GPG keys found. Generate with: gpg --gen-key"
        }
    }

    # Report issues
    if ($issues) {
        Write-CommitLog -Level WARNING -Message "Pre-commit issues found:"
        $issues | ForEach-Object {
            Write-CommitLog -Level WARNING -Message $_
        }
        return $false
    }

    Write-CommitLog -Level SUCCESS -Message "✅ All pre-commit checks passed"
    return $true
}

# ============================================================
# COMMIT MESSAGE GENERATION
# ============================================================

function New-CommitMessage {
    [CmdletBinding()]
    param(
        [string]$Type,
        [string]$Scope,
        [string]$Description
    )

    # Format: <type>(<scope>): <description>
    $message = $Type

    if ($Scope) {
        $message += "($Scope)"
    }

    $message += ": $Description"

    # Validate length
    if ($message.Length -gt $Script:Config.MaxCommitMessageLength) {
        Write-CommitLog -Level WARNING -Message "Commit message exceeds $($Script:Config.MaxCommitMessageLength) chars. Consider shortening."
    }

    return $message
}

# ============================================================
# AUTO-COMMIT GENERATOR
# ============================================================

function New-AutoCommitMessage {
    [CmdletBinding()]
    param(
        [int]$ExitCode
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    if ($ExitCode -eq 0) {
        $type = "chore"
        $desc = "auto-commit after successful execution at $timestamp"
    }
    else {
        $type = "fix"
        $desc = "auto-commit with errors (exit code: $ExitCode) at $timestamp"
    }

    return New-CommitMessage -Type $type -Scope "automation" -Description $desc
}

# ============================================================
# COMMIT EXECUTION
# ============================================================

function Invoke-GitCommit {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [bool]$SignCommit = $false,

        [bool]$DryRunMode = $false
    )

    Write-CommitLog -Level INFO -Message "Preparing commit: '$Message'"

    # Build commit command
    $commitArgs = @('commit', '-m', $Message)

    if ($SignCommit) {
        $commitArgs += '-S'
        Write-CommitLog -Level INFO -Message "Signing commit with GPG"
    }

    if ($DryRunMode) {
        Write-CommitLog -Level WARNING -Message "[DRY RUN] Would execute: git $($commitArgs -join ' ')"
        return $true
    }

    # Execute commit
    try {
        $output = & git @commitArgs 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-CommitLog -Level SUCCESS -Message "✅ Commit successful"
            
            # Show commit details
            $commitHash = git rev-parse --short HEAD
            Write-CommitLog -Level INFO -Message "Commit hash: $commitHash"

            # Verify signature if signed
            if ($SignCommit) {
                $signature = git log --show-signature -1 2>&1
                if ($signature -match "Good signature") {
                    Write-CommitLog -Level SUCCESS -Message "✅ GPG signature verified"
                }
                else {
                    Write-CommitLog -Level WARNING -Message "⚠️ GPG signature verification inconclusive"
                }
            }

            return $true
        }
        else {
            Write-CommitLog -Level ERROR -Message "❌ Commit failed: $output"
            return $false
        }
    }
    catch {
        Write-CommitLog -Level ERROR -Message "❌ Exception during commit: $($_.Exception.Message)"
        return $false
    }
}

# ============================================================
# PUSH TO REMOTE
# ============================================================

function Invoke-GitPush {
    [CmdletBinding()]
    param(
        [string]$RemoteName,
        [string]$BranchName,
        [bool]$DryRunMode = $false
    )

    Write-CommitLog -Level INFO -Message "Pushing to $RemoteName/$BranchName..."

    if ($DryRunMode) {
        Write-CommitLog -Level WARNING -Message "[DRY RUN] Would execute: git push $RemoteName $BranchName"
        return $true
    }

    try {
        $output = & git push $RemoteName $BranchName 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-CommitLog -Level SUCCESS -Message "✅ Push successful"
            return $true
        }
        else {
            Write-CommitLog -Level ERROR -Message "❌ Push failed: $output"
            return $false
        }
    }
    catch {
        Write-CommitLog -Level ERROR -Message "❌ Exception during push: $($_.Exception.Message)"
        return $false
    }
}

# ============================================================
# ROLLBACK SUPPORT
# ============================================================

function Invoke-CommitRollback {
    [CmdletBinding()]
    param(
        [switch]$Hard,
        [switch]$Soft
    )

    Write-CommitLog -Level WARNING -Message "Rolling back last commit..."

    $resetType = if ($Hard) { '--hard' } elseif ($Soft) { '--soft' } else { '--mixed' }

    try {
        $lastCommit = git rev-parse --short HEAD
        Write-CommitLog -Level INFO -Message "Last commit: $lastCommit"

        $output = & git reset $resetType HEAD~1 2>&1

        if ($LASTEXITCODE -eq 0) {
            Write-CommitLog -Level SUCCESS -Message "✅ Rollback successful ($resetType)"
            Write-CommitLog -Level INFO -Message "Changes are now unstaged (--mixed) or removed (--hard)"
            return $true
        }
        else {
            Write-CommitLog -Level ERROR -Message "❌ Rollback failed: $output"
            return $false
        }
    }
    catch {
        Write-CommitLog -Level ERROR -Message "❌ Exception during rollback: $($_.Exception.Message)"
        return $false
    }
}

# ============================================================
# MAIN EXECUTION
# ============================================================

function Main {
    Write-CommitLog -Level INFO -Message "=== EQ12 Auto-Commit System ==="

    # Pre-commit validation (if requested or auto-enabled)
    if ($PreCommit -or $PSCmdlet.ParameterSetName -ne 'Manual') {
        $isReady = Test-CommitReadiness
        if (-not $isReady) {
            Write-CommitLog -Level ERROR -Message "Pre-commit validation failed. Fix issues and try again."
            exit 1
        }
    }

    # Generate commit message based on mode
    $commitMessage = switch ($PSCmdlet.ParameterSetName) {
        'Manual' {
            $Message
        }
        'Auto' {
            New-AutoCommitMessage -ExitCode $ScriptResult
        }
        'Template' {
            if (-not $Description) {
                Write-CommitLog -Level ERROR -Message "Template mode requires -Description parameter"
                exit 1
            }
            New-CommitMessage -Type $Template -Scope $Scope -Description $Description
        }
    }

    if (-not $commitMessage) {
        Write-CommitLog -Level ERROR -Message "No commit message generated"
        exit 1
    }

    # Execute commit
    $commitSuccess = Invoke-GitCommit -Message $commitMessage -SignCommit $Sign -DryRunMode:$DryRun

    if (-not $commitSuccess) {
        Write-CommitLog -Level ERROR -Message "Commit failed. Exiting."
        exit 1
    }

    # Push if requested
    if ($Push -and -not $DryRun) {
        $pushSuccess = Invoke-GitPush -RemoteName $Remote -BranchName $Branch -DryRunMode:$DryRun

        if (-not $pushSuccess) {
            Write-CommitLog -Level WARNING -Message "Push failed. Commit is local only."
        }
    }

    Write-CommitLog -Level SUCCESS -Message "=== Commit workflow complete ==="
}

# Run main
Main
