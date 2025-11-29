<#
.SYNOPSIS
    Initialize Git Repository for EQ12 System

.DESCRIPTION
    Complete Git initialization with:
    - Repository creation
    - .gitignore with security patterns
    - Initial commit
    - Remote configuration

.EXAMPLE
    .\git_init_script.ps1
    .\git_init_script.ps1 -RemoteUrl "https://github.com/yourusername/EQ12.git"
    .\git_init_script.ps1 -SkipInitialCommit

.NOTES
    Author: EQ12 System
    Date: 2025-11-29
#>

[CmdletBinding()]
param(
    # Git remote URL (optional)
    [string]$RemoteUrl,

    # Remote name (default: origin)
    [string]$RemoteName = 'origin',

    # Skip initial commit
    [switch]$SkipInitialCommit
)

Write-Host "=== EQ12 Git Repository Initialization ===" -ForegroundColor Cyan
Write-Host ""

# ============================================================
# CHECK 1: Verify we're in the right directory
# ============================================================

$repoRoot = "C:\EQ12_BROKEN_20251122_210342"
$currentDir = Get-Location

if ($currentDir.Path -ne $repoRoot) {
    Write-Host "⚠️ Warning: Current directory is not $repoRoot" -ForegroundColor Yellow
    Write-Host "Current: $currentDir" -ForegroundColor Yellow
    
    $response = Read-Host "Change to $repoRoot? (y/n)"
    if ($response -eq 'y') {
        Set-Location $repoRoot
        Write-Host "✅ Changed to $repoRoot" -ForegroundColor Green
    } else {
        Write-Host "❌ Aborted. Run from $repoRoot" -ForegroundColor Red
        exit 1
    }
}

# ============================================================
# CHECK 2: Is Git already initialized?
# ============================================================

if (Test-Path ".git") {
    Write-Host "⚠️ Git repository already exists (.git directory found)" -ForegroundColor Yellow
    
    $response = Read-Host "Reinitialize? This will NOT delete existing commits. (y/n)"
    if ($response -ne 'y') {
        Write-Host "❌ Aborted. Use 'git status' to check repository state." -ForegroundColor Red
        exit 0
    }
}

# ============================================================
# STEP 1: Initialize Git Repository
# ============================================================

Write-Host ""
Write-Host "[1/6] Initializing Git repository..." -ForegroundColor Yellow

try {
    $initOutput = git init 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Git repository initialized" -ForegroundColor Green
    } else {
        Write-Host "❌ Git init failed: $initOutput" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "❌ Exception during git init: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# ============================================================
# STEP 2: Configure Git User (if not already set)
# ============================================================

Write-Host ""
Write-Host "[2/6] Checking Git user configuration..." -ForegroundColor Yellow

$gitUserName = git config user.name
$gitUserEmail = git config user.email

if (-not $gitUserName -or -not $gitUserEmail) {
    Write-Host "⚠️ Git user not configured globally" -ForegroundColor Yellow
    
    if (-not $gitUserName) {
        $userName = Read-Host "Enter your name"
        git config user.name $userName
        Write-Host "✅ Set user.name = $userName" -ForegroundColor Green
    }
    
    if (-not $gitUserEmail) {
        $userEmail = Read-Host "Enter your email"
        git config user.email $userEmail
        Write-Host "✅ Set user.email = $userEmail" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Git user already configured: $gitUserName <$gitUserEmail>" -ForegroundColor Green
}

# ============================================================
# STEP 3: Create/Update .gitignore
# ============================================================

Write-Host ""
Write-Host "[3/6] Creating .gitignore with security patterns..." -ForegroundColor Yellow

$gitignoreContent = @"
# EQ12 Enhanced .gitignore - Comprehensive Security & Privacy Protection
# ======================================================================

# 🔒 Security & Secrets (CRITICAL - Never commit these)
# API Keys and Tokens
*.key
*.pem
*.pfx
*.p12
*.crt
*.cer
*.der
.env
.env.*
!.env.template
!.env.example
api_keys.json
secrets.json
config.json
.secrets
.keys/
tokens/
credentials/
auth/

# SSH and GPG Keys
id_rsa*
id_dsa*
id_ecdsa*
id_ed25519*
*.ppk

# Database Credentials
database.json
connection_strings.json
*.sql.backup

# ⚙️ Operating System & IDE
# Windows
Thumbs.db
ehthumbs.db
Desktop.ini
$RECYCLE.BIN/
*.lnk

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Linux
*~
.directory

# Visual Studio / VS Code
.vs/
.vscode/settings.json
.vscode/launch.json
*.suo
*.user
*.userosscache
*.sln.docstates

# 🗂️ Build & Runtime Artifacts
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.ruff_cache/
.mypy_cache/
.dmypy.json
dmypy.json

# .NET / VB.NET
bin/
obj/
[Dd]ebug/
[Rr]elease/
*.dll
*.exe
*.pdb
*.cache

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 📊 Logs & Temporary Files
logs/
*.log
*.log.*
temp/
tmp/
*.tmp
*.temp
*.swp
*.swo
*~

# 💾 Databases (local only)
*.db
*.sqlite
*.sqlite3
*.db-journal
*.db-shm
*.db-wal

# Except test/example databases
!*test*.db
!*example*.db

# 📦 Compressed Files (large)
*.zip
*.tar.gz
*.rar
*.7z

# 🎨 Media (large files)
*.mp4
*.avi
*.mov
*.mp3
*.wav

# 📈 EQ12-Specific
# Scraped data (too large for Git)
scraped_data/
cache/

# Model files (use Git LFS)
*.h5
*.pkl
*.pickle
*.joblib
*.model

# Generated reports
reports/*.pdf
reports/*.xlsx

# Backup files
*.bak
*.backup

# ✅ Explicitly Include (override patterns above)
!.gitignore
!.gitattributes
!README.md
"@

$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding utf8 -Force
Write-Host "✅ .gitignore created/updated with security patterns" -ForegroundColor Green

# ============================================================
# STEP 4: Create .gitattributes (line ending normalization)
# ============================================================

Write-Host ""
Write-Host "[4/6] Creating .gitattributes for cross-platform compatibility..." -ForegroundColor Yellow

$gitattributesContent = @"
# Auto detect text files and perform LF normalization
* text=auto

# Source code
*.vb text eol=crlf
*.cs text eol=crlf
*.sql text eol=crlf
*.ps1 text eol=crlf
*.py text eol=lf
*.sh text eol=lf

# Documentation
*.md text eol=lf
*.txt text eol=lf

# Binary files
*.png binary
*.jpg binary
*.gif binary
*.ico binary
*.db binary
*.sqlite binary
*.exe binary
*.dll binary
"@

$gitattributesContent | Out-File -FilePath ".gitattributes" -Encoding utf8 -Force
Write-Host "✅ .gitattributes created" -ForegroundColor Green

# ============================================================
# STEP 5: Initial Commit (if not skipped)
# ============================================================

if (-not $SkipInitialCommit) {
    Write-Host ""
    Write-Host "[5/6] Creating initial commit..." -ForegroundColor Yellow
    
    # Stage .gitignore and .gitattributes
    git add .gitignore .gitattributes
    
    # Check if commit signing is enabled
    $commitGpgSign = git config commit.gpgsign
    
    if ($commitGpgSign -eq "true") {
        Write-Host "✅ GPG signing enabled, creating signed commit..." -ForegroundColor Green
        $commitResult = git commit -S -m "chore: initialize Git repository with security-first .gitignore" 2>&1
    } else {
        Write-Host "⚠️ GPG signing not enabled (run gpg_setup_guide.md to configure)" -ForegroundColor Yellow
        $commitResult = git commit -m "chore: initialize Git repository with security-first .gitignore" 2>&1
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Initial commit created" -ForegroundColor Green
        
        # Show commit details
        $commitHash = git rev-parse --short HEAD
        Write-Host "   Commit: $commitHash" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️ Commit failed (may be no changes): $commitResult" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "[5/6] Skipping initial commit (use -SkipInitialCommit)" -ForegroundColor Yellow
}

# ============================================================
# STEP 6: Configure Remote (if provided)
# ============================================================

Write-Host ""
Write-Host "[6/6] Configuring remote repository..." -ForegroundColor Yellow

if ($RemoteUrl) {
    # Check if remote already exists
    $existingRemote = git remote get-url $RemoteName 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "⚠️ Remote '$RemoteName' already exists: $existingRemote" -ForegroundColor Yellow
        
        $response = Read-Host "Update to $RemoteUrl? (y/n)"
        if ($response -eq 'y') {
            git remote set-url $RemoteName $RemoteUrl
            Write-Host "✅ Updated remote '$RemoteName' to: $RemoteUrl" -ForegroundColor Green
        }
    } else {
        git remote add $RemoteName $RemoteUrl
        Write-Host "✅ Added remote '$RemoteName': $RemoteUrl" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "To push to remote, run:" -ForegroundColor Cyan
    Write-Host "  git push -u $RemoteName main" -ForegroundColor White
} else {
    Write-Host "⏭️ No remote URL provided (use -RemoteUrl parameter to add)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To add remote later, run:" -ForegroundColor Cyan
    Write-Host "  git remote add origin https://github.com/yourusername/EQ12.git" -ForegroundColor White
    Write-Host "  git push -u origin main" -ForegroundColor White
}

# ============================================================
# SUMMARY
# ============================================================

Write-Host ""
Write-Host "=== Git Repository Initialization Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Repository initialized: .git/" -ForegroundColor Green
Write-Host "✅ Security-first .gitignore created" -ForegroundColor Green
Write-Host "✅ Cross-platform .gitattributes created" -ForegroundColor Green

if (-not $SkipInitialCommit) {
    Write-Host "✅ Initial commit created" -ForegroundColor Green
}

if ($RemoteUrl) {
    Write-Host "✅ Remote configured: $RemoteName -> $RemoteUrl" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review .gitignore for EQ12-specific exclusions" -ForegroundColor White
Write-Host "  2. Configure GPG signing (see gpg_setup_guide.md)" -ForegroundColor White
Write-Host "  3. Install pre-commit hooks (see README_COMMIT_EXPERT.md)" -ForegroundColor White
Write-Host "  4. Make your first commit: git add . && git commit -m 'feat: initial EQ12 system'" -ForegroundColor White

if ($RemoteUrl) {
    Write-Host "  5. Push to remote: git push -u $RemoteName main" -ForegroundColor White
}

Write-Host ""
Write-Host "Repository Status:" -ForegroundColor Cyan
git status --short

Write-Host ""
Write-Host "Happy Committing! 🎉" -ForegroundColor Green
