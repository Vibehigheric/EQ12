# EQ12 Safe Repository Gatekeeper
# Automatically blocks execution of unsafe code in untrusted repos
# Enterprise-grade security for DevSecOps workflows

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [string]$RepoPath,

    [Parameter(Mandatory=$false)]
    [ValidateSet("Scan", "Trust", "Sandbox", "Reject")]
    [string]$Action = "Scan",

    [Parameter(Mandatory=$false)]
    [switch]$AutoFix
)

$ErrorActionPreference = "Stop"

# Security configuration
$TRUSTED_REPOS = @(
    "C:\EQ12_TRUSTED",
    "C:\EQ12"
)

$SANDBOXED_REPOS = @(
    "C:\EQ12_SANDBOXED",
    "C:\Sandbox"
)

$DANGEROUS_EXTENSIONS = @(
    "*.exe", "*.dll", "*.so", "*.dylib",
    "*.bat", "*.cmd", "*.vbs",
    "*.msi", "*.scr", "*.pif"
)

$SUSPICIOUS_PATTERNS = @(
    "eval\(",
    "exec\(",
    "subprocess.call",
    "os.system",
    "__import__",
    "base64.b64decode",
    "pickle.loads",
    "shell=True",
    "powershell.exe -enc",
    "Invoke-Expression",
    "IEX"
)

function Write-SecurityLog {
    param($Message, $Level = "INFO")

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logFile = "C:\EQ12\logs\security_gatekeeper_$(Get-Date -Format 'yyyyMMdd').log"

    $entry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $logFile -Value $entry

    switch ($Level) {
        "ERROR" { Write-Host $entry -ForegroundColor Red }
        "WARN" { Write-Host $entry -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $entry -ForegroundColor Green }
        default { Write-Host $entry -ForegroundColor Cyan }
    }
}

function Test-RepositoryTrust {
    param([string]$Path)

    $normalizedPath = $Path -replace '/', '\'

    foreach ($trustedPath in $TRUSTED_REPOS) {
        if ($normalizedPath -like "$trustedPath*") {
            return "TRUSTED"
        }
    }

    foreach ($sandboxPath in $SANDBOXED_REPOS) {
        if ($normalizedPath -like "$sandboxPath*") {
            return "SANDBOXED"
        }
    }

    return "UNTRUSTED"
}

function Find-DangerousFiles {
    param([string]$Path)

    $dangerous = @()

    foreach ($ext in $DANGEROUS_EXTENSIONS) {
        $files = Get-ChildItem -Path $Path -Filter $ext -Recurse -ErrorAction SilentlyContinue
        foreach ($file in $files) {
            $dangerous += [PSCustomObject]@{
                Path = $file.FullName
                Type = "Executable"
                Risk = "HIGH"
            }
        }
    }

    return $dangerous
}

function Find-SuspiciousCode {
    param([string]$Path)

    $suspicious = @()

    $codeFiles = Get-ChildItem -Path $Path -Include "*.py","*.ps1","*.sh","*.js" -Recurse -ErrorAction SilentlyContinue

    foreach ($file in $codeFiles) {
        $content = Get-Content -Path $file.FullName -Raw -ErrorAction SilentlyContinue

        foreach ($pattern in $SUSPICIOUS_PATTERNS) {
            if ($content -match [regex]::Escape($pattern)) {
                $suspicious += [PSCustomObject]@{
                    File = $file.FullName
                    Pattern = $pattern
                    Risk = "MEDIUM"
                }
            }
        }
    }

    return $suspicious
}

function Test-GitOwnership {
    param([string]$Path)

    if (Test-Path "$Path\.git") {
        try {
            $gitCheck = git -C $Path config --get safe.directory

            if ($LASTEXITCODE -ne 0) {
                return $false
            }
            return $true
        }
        catch {
            return $false
        }
    }

    return $null  # Not a git repo
}

function Invoke-RepositoryScan {
    param([string]$Path)

    Write-SecurityLog "Starting security scan: $Path" "INFO"

    # Check trust level
    $trustLevel = Test-RepositoryTrust -Path $Path
    Write-SecurityLog "Trust Level: $trustLevel" "INFO"

    # Scan for dangerous files
    Write-SecurityLog "Scanning for dangerous executables..." "INFO"
    $dangerousFiles = Find-DangerousFiles -Path $Path

    if ($dangerousFiles.Count -gt 0) {
        Write-SecurityLog "Found $($dangerousFiles.Count) dangerous files!" "ERROR"
        $dangerousFiles | Format-Table -AutoSize
    }
    else {
        Write-SecurityLog "No dangerous executables found" "SUCCESS"
    }

    # Scan for suspicious code patterns
    Write-SecurityLog "Scanning for suspicious code patterns..." "INFO"
    $suspiciousCode = Find-SuspiciousCode -Path $Path

    if ($suspiciousCode.Count -gt 0) {
        Write-SecurityLog "Found $($suspiciousCode.Count) suspicious patterns!" "WARN"
        $suspiciousCode | Select-Object -First 10 | Format-Table -AutoSize
    }
    else {
        Write-SecurityLog "No suspicious patterns found" "SUCCESS"
    }

    # Check Git ownership
    $gitOwnership = Test-GitOwnership -Path $Path

    if ($gitOwnership -eq $false) {
        Write-SecurityLog "Git ownership mismatch detected!" "ERROR"
    }
    elseif ($gitOwnership -eq $true) {
        Write-SecurityLog "Git ownership validated" "SUCCESS"
    }

    # Generate report
    $report = [PSCustomObject]@{
        Path = $Path
        TrustLevel = $trustLevel
        DangerousFiles = $dangerousFiles.Count
        SuspiciousPatterns = $suspiciousCode.Count
        GitOwnershipValid = $gitOwnership
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Recommendation = ""
    }

    # Determine recommendation
    if ($trustLevel -eq "UNTRUSTED" -and ($dangerousFiles.Count -gt 0 -or $suspiciousCode.Count -gt 5)) {
        $report.Recommendation = "REJECT - High risk detected"
    }
    elseif ($trustLevel -eq "UNTRUSTED" -and $suspiciousCode.Count -gt 0) {
        $report.Recommendation = "SANDBOX - Review in isolated environment"
    }
    elseif ($trustLevel -eq "SANDBOXED") {
        $report.Recommendation = "REVIEW - Safe to inspect, do not execute"
    }
    else {
        $report.Recommendation = "ACCEPT - Appears safe"
    }

    return $report
}

function Set-RepositoryTrust {
    param([string]$Path)

    Write-SecurityLog "Adding repository to safe.directory: $Path" "INFO"

    try {
        git config --global --add safe.directory $Path
        Write-SecurityLog "Repository trusted successfully" "SUCCESS"
    }
    catch {
        Write-SecurityLog "Failed to trust repository: $_" "ERROR"
    }
}

function Move-ToSandbox {
    param([string]$Path)

    $repoName = Split-Path $Path -Leaf
    $sandboxPath = "C:\EQ12_SANDBOXED\$repoName"

    Write-SecurityLog "Moving repository to sandbox: $sandboxPath" "INFO"

    if (Test-Path $sandboxPath) {
        Write-SecurityLog "Sandbox path already exists, removing..." "WARN"
        Remove-Item -Path $sandboxPath -Recurse -Force
    }

    Copy-Item -Path $Path -Destination $sandboxPath -Recurse

    # Set read-only
    attrib +R $sandboxPath /S /D

    Write-SecurityLog "Repository sandboxed successfully" "SUCCESS"
    return $sandboxPath
}

# Main execution
Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   EQ12 SAFE REPOSITORY GATEKEEPER" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

if (-not (Test-Path $RepoPath)) {
    Write-SecurityLog "Repository path not found: $RepoPath" "ERROR"
    exit 1
}

switch ($Action) {
    "Scan" {
        $report = Invoke-RepositoryScan -Path $RepoPath

        Write-Host "`n═══════ SECURITY REPORT ═══════" -ForegroundColor Yellow
        $report | Format-List

        Write-Host "`nRECOMMENDATION: $($report.Recommendation)" -ForegroundColor $(
            if ($report.Recommendation -like "*REJECT*") { "Red" }
            elseif ($report.Recommendation -like "*SANDBOX*") { "Yellow" }
            else { "Green" }
        )
    }

    "Trust" {
        Set-RepositoryTrust -Path $RepoPath
    }

    "Sandbox" {
        $sandboxPath = Move-ToSandbox -Path $RepoPath
        Write-Host "`nSandboxed at: $sandboxPath" -ForegroundColor Green
    }

    "Reject" {
        Write-SecurityLog "Repository rejected by user: $RepoPath" "WARN"
        Write-Host "`nRepository rejected. Do not execute any code from this location." -ForegroundColor Red
    }
}

Write-Host "`n═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
