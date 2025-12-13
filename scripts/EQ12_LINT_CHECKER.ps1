<#
.SYNOPSIS
    EQ12 PowerShell Formatting Lint Checker

.DESCRIPTION
    Scans all PowerShell scripts in the EQ12 repository for:
    - UTF-8 encoding corruption (emoji artifacts like "âœ…")
    - Emoji characters (should be ASCII-only)
    - Smart quotes (" " ' ' instead of " ')
    - Tab characters (should use spaces)
    - Unmatched braces {}
    - Unmatched parentheses ()
    - Unmatched brackets []
    - Invalid BOM markers
    - Mixed line endings
    
    Generates a detailed report of violations and optionally auto-fixes them.

.PARAMETER Path
    Root path to scan (defaults to repository root)

.PARAMETER AutoFix
    Automatically fix detected issues (creates backups first)

.PARAMETER ExcludePatterns
    Patterns to exclude from scanning (e.g., node_modules, .venv)

.PARAMETER ReportOnly
    Generate report without making any changes

.EXAMPLE
    .\EQ12_LINT_CHECKER.ps1 -Path C:\EQ12_BROKEN_20251122_210342\scripts -ReportOnly
    .\EQ12_LINT_CHECKER.ps1 -AutoFix -Verbose

.NOTES
    Author: EQ12 Copilot Workspace Architect
    Date: 2025-11-27
    Purpose: Prevent Unicode corruption and enforce ASCII-only PowerShell standards
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$Path = "C:\EQ12_BROKEN_20251122_210342",

    [Parameter(Mandatory = $false)]
    [switch]$AutoFix,

    [Parameter(Mandatory = $false)]
    [string[]]$ExcludePatterns = @(
        "*\node_modules\*",
        "*\.venv\*",
        "*\venv\*",
        "*\.git\*",
        "*\__pycache__\*",
        "*\dist\*",
        "*\build\*"
    ),

    [Parameter(Mandatory = $false)]
    [switch]$ReportOnly
)

# ==================== CONFIGURATION ====================
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$PSDefaultParameterValues['Out-File:Encoding'] = 'ASCII'

$script:ViolationReport = @{
    Timestamp       = (Get-Date).ToUniversalTime().ToString("o")
    TotalFiles      = 0
    CleanFiles      = 0
    FilesWithIssues = 0
    Violations      = @()
    Summary         = @{}
}

# ==================== LOGGING ====================
function Write-LintLog {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS", "FIX")]
        [string]$Level = "INFO"
    )

    $colors = @{
        INFO    = "Cyan"
        WARN    = "Yellow"
        ERROR   = "Red"
        SUCCESS = "Green"
        FIX     = "Magenta"
    }

    $timestamp = Get-Date -Format "HH:mm:ss"
    $line = "[{0}] [{1}] {2}" -f $timestamp, $Level, $Message
    Write-Host $line -ForegroundColor $colors[$Level]
}

# ==================== DETECTION PATTERNS ====================
$script:ViolationPatterns = @{
    # UTF-8 corruption artifacts
    UTF8Corruption     = @{
        Pattern     = '[â€™â€œâ€âœ"âœ—âœ…â��â—�ğŸ"�]'
        Description = "UTF-8 corruption artifacts (e.g., emoji converted to âœ…)"
        Severity    = "CRITICAL"
    }

    # Actual emoji characters
    EmojiCharacters    = @{
        Pattern     = '[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{2300}-\u{23FF}\u{2B50}\u{2705}\u{274C}\u{2714}\u{2716}]'
        Description = "Emoji characters (not ASCII-safe)"
        Severity    = "HIGH"
    }

    # Smart quotes
    SmartQuotes        = @{
        Pattern     = '[â€œâ€â€™â€˜â€šâ€žâ€ºâ€¹]|[\u{201C}\u{201D}\u{2018}\u{2019}]'
        Description = "Smart quotes (should use ASCII quotes)"
        Severity    = "MEDIUM"
    }

    # Tab characters
    TabCharacters      = @{
        Pattern     = '\t'
        Description = "Tab characters (should use spaces)"
        Severity    = "LOW"
    }

    # Control characters
    ControlCharacters  = @{
        Pattern     = '[\x00-\x08\x0B\x0C\x0E-\x1F]'
        Description = "Control characters (non-printable)"
        Severity    = "HIGH"
    }

    # Unmatched braces (simple check)
    UnmatchedBraces    = @{
        Pattern     = $null # Custom logic required
        Description = "Unmatched curly braces {}"
        Severity    = "CRITICAL"
    }

    # Unmatched parentheses
    UnmatchedParens    = @{
        Pattern     = $null # Custom logic required
        Description = "Unmatched parentheses ()"
        Severity    = "CRITICAL"
    }

    # Unmatched brackets
    UnmatchedBrackets  = @{
        Pattern     = $null # Custom logic required
        Description = "Unmatched square brackets []"
        Severity    = "CRITICAL"
    }

    # Mixed line endings
    MixedLineEndings   = @{
        Pattern     = $null # Custom logic required
        Description = "Mixed line endings (CR/LF inconsistent)"
        Severity    = "MEDIUM"
    }

    # UTF-8 BOM
    UTF8BOM            = @{
        Pattern     = $null # Byte-level check required
        Description = "UTF-8 BOM detected (should be UTF-8 without BOM)"
        Severity    = "MEDIUM"
    }

    # Invalid PowerShell syntax indicators
    UnclosedStrings    = @{
        Pattern     = '"[^"]*$'
        Description = "Potentially unclosed string literals"
        Severity    = "CRITICAL"
    }

    # Common typos from corruption
    CorruptionTypos    = @{
        Pattern     = 'â€|Ã©|Ã¨|Ã |Ã¢|Ãª|Ã®|Ã´|Ã»|Ã§|Ã€|Ã‚|Ãˆ|ÃŠ|ÃŽ|Ã"|Ã›|Ã‡'
        Description = "Common UTF-8 to ANSI corruption sequences"
        Severity    = "CRITICAL"
    }
}

# ==================== FILE SCANNING ====================
function Test-FileEncoding {
    param([string]$FilePath)

    $bytes = [System.IO.File]::ReadAllBytes($FilePath)

    # Check for BOM
    $hasBOM = $false
    if ($bytes.Length -ge 3) {
        if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $hasBOM = $true
        }
    }

    return @{
        HasBOM   = $hasBOM
        SizeKB   = [math]::Round($bytes.Length / 1KB, 2)
        FirstByte = if ($bytes.Length -gt 0) { $bytes[0] } else { $null }
    }
}

function Test-BracketBalance {
    param(
        [string]$Content,
        [char]$Open,
        [char]$Close
    )

    $depth = 0
    $unmatched = @()

    for ($i = 0; $i -lt $Content.Length; $i++) {
        if ($Content[$i] -eq $Open) {
            $depth++
        }
        elseif ($Content[$i] -eq $Close) {
            $depth--
            if ($depth -lt 0) {
                $unmatched += "Extra closing '$Close' at position $i"
            }
        }
    }

    if ($depth -gt 0) {
        $unmatched += "$depth unclosed '$Open' character(s)"
    }

    return @{
        Balanced  = ($depth -eq 0 -and $unmatched.Count -eq 0)
        Unmatched = $unmatched
    }
}

function Test-LineEndings {
    param([string]$Content)

    $crlfCount = ([regex]::Matches($Content, "`r`n")).Count
    $lfCount = ([regex]::Matches($Content, "(?<!\r)`n")).Count
    $crCount = ([regex]::Matches($Content, "`r(?!`n)")).Count

    $mixed = ($crlfCount -gt 0 -and $lfCount -gt 0) -or ($crCount -gt 0)

    return @{
        IsMixed  = $mixed
        CRLF     = $crlfCount
        LF       = $lfCount
        CR       = $crCount
        Dominant = if ($crlfCount -gt $lfCount) { "CRLF" } else { "LF" }
    }
}

function Invoke-FileLint {
    param([string]$FilePath)

    $violations = @()

    try {
        # Read file content
        $content = Get-Content $FilePath -Raw -ErrorAction Stop
        $encodingInfo = Test-FileEncoding -FilePath $FilePath

        # Check BOM
        if ($encodingInfo.HasBOM) {
            $violations += @{
                Type        = "UTF8BOM"
                Description = $script:ViolationPatterns.UTF8BOM.Description
                Severity    = $script:ViolationPatterns.UTF8BOM.Severity
                Line        = 1
                Details     = "File starts with UTF-8 BOM (EF BB BF)"
            }
        }

        # Check line endings
        $lineEndingCheck = Test-LineEndings -Content $content
        if ($lineEndingCheck.IsMixed) {
            $violations += @{
                Type        = "MixedLineEndings"
                Description = $script:ViolationPatterns.MixedLineEndings.Description
                Severity    = $script:ViolationPatterns.MixedLineEndings.Severity
                Line        = "N/A"
                Details     = "CRLF: $($lineEndingCheck.CRLF), LF: $($lineEndingCheck.LF), CR: $($lineEndingCheck.CR)"
            }
        }

        # Check bracket balancing
        $braceCheck = Test-BracketBalance -Content $content -Open '{' -Close '}'
        if (-not $braceCheck.Balanced) {
            $violations += @{
                Type        = "UnmatchedBraces"
                Description = $script:ViolationPatterns.UnmatchedBraces.Description
                Severity    = $script:ViolationPatterns.UnmatchedBraces.Severity
                Line        = "N/A"
                Details     = ($braceCheck.Unmatched -join "; ")
            }
        }

        $parenCheck = Test-BracketBalance -Content $content -Open '(' -Close ')'
        if (-not $parenCheck.Balanced) {
            $violations += @{
                Type        = "UnmatchedParens"
                Description = $script:ViolationPatterns.UnmatchedParens.Description
                Severity    = $script:ViolationPatterns.UnmatchedParens.Severity
                Line        = "N/A"
                Details     = ($parenCheck.Unmatched -join "; ")
            }
        }

        $bracketCheck = Test-BracketBalance -Content $content -Open '[' -Close ']'
        if (-not $bracketCheck.Balanced) {
            $violations += @{
                Type        = "UnmatchedBrackets"
                Description = $script:ViolationPatterns.UnmatchedBrackets.Description
                Severity    = $script:ViolationPatterns.UnmatchedBrackets.Severity
                Line        = "N/A"
                Details     = ($bracketCheck.Unmatched -join "; ")
            }
        }

        # Pattern-based checks
        $lines = $content -split "`r?`n"

        foreach ($key in $script:ViolationPatterns.Keys) {
            $patternInfo = $script:ViolationPatterns[$key]

            if ($null -eq $patternInfo.Pattern) { continue }

            for ($i = 0; $i -lt $lines.Count; $i++) {
                $line = $lines[$i]

                if ($line -match $patternInfo.Pattern) {
                    $match = [regex]::Match($line, $patternInfo.Pattern)

                    $violations += @{
                        Type        = $key
                        Description = $patternInfo.Description
                        Severity    = $patternInfo.Severity
                        Line        = $i + 1
                        Details     = "Matched: '$($match.Value)'"
                    }
                }
            }
        }

        return @{
            Success    = $true
            Violations = $violations
        }
    }
    catch {
        return @{
            Success    = $false
            Error      = $_.Exception.Message
            Violations = @()
        }
    }
}

function Invoke-AutoFix {
    param(
        [string]$FilePath,
        [array]$Violations
    )

    Write-LintLog "Attempting auto-fix for: $FilePath" "FIX"

    # Create backup
    $backupPath = "$FilePath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $FilePath $backupPath -Force

    Write-LintLog "Created backup: $backupPath" "INFO"

    try {
        $content = Get-Content $FilePath -Raw

        # Fix UTF-8 corruption artifacts (replace with ASCII equivalents)
        $content = $content -replace 'âœ…', '[OK]'
        $content = $content -replace 'âœ—', '[X]'
        $content = $content -replace 'âœ"', '[CHECK]'
        $content = $content -replace 'â—�', '[WARN]'
        $content = $content -replace 'â€™', "'"
        $content = $content -replace 'â€œ', '"'
        $content = $content -replace 'â€�', '"'
        $content = $content -replace 'â€', '-'

        # Replace tabs with 4 spaces
        $content = $content -replace "`t", "    "

        # Normalize line endings to CRLF (Windows standard)
        $content = $content -replace "`r?`n", "`r`n"

        # Save with ASCII encoding, no BOM
        [System.IO.File]::WriteAllText($FilePath, $content, [System.Text.Encoding]::ASCII)

        Write-LintLog "[OK] Auto-fix completed for: $FilePath" "SUCCESS"
        return $true
    }
    catch {
        Write-LintLog "Auto-fix failed: $_" "ERROR"
        return $false
    }
}

# ==================== MAIN EXECUTION ====================
function Invoke-MainLintCheck {
    Write-LintLog "EQ12 PowerShell Formatting Lint Checker" "INFO"
    Write-LintLog "Scanning path: $Path" "INFO"
    Write-LintLog "" "INFO"

    # Find all PowerShell scripts
    $allScripts = Get-ChildItem -Path $Path -Filter "*.ps1" -Recurse -ErrorAction SilentlyContinue

    # Exclude patterns
    $scriptsToCheck = $allScripts | Where-Object {
        $filePath = $_.FullName
        $excluded = $false

        foreach ($pattern in $ExcludePatterns) {
            if ($filePath -like $pattern) {
                $excluded = $true
                break
            }
        }

        -not $excluded
    }

    $script:ViolationReport.TotalFiles = $scriptsToCheck.Count

    Write-LintLog "Found $($scriptsToCheck.Count) PowerShell scripts to check" "INFO"
    Write-LintLog "" "INFO"

    foreach ($script in $scriptsToCheck) {
        Write-Verbose "Checking: $($script.FullName)"

        $result = Invoke-FileLint -FilePath $script.FullName

        if ($result.Success) {
            if ($result.Violations.Count -eq 0) {
                $script:ViolationReport.CleanFiles++
            }
            else {
                $script:ViolationReport.FilesWithIssues++

                $fileViolation = @{
                    File       = $script.FullName
                    RelPath    = $script.FullName.Replace($Path, "")
                    Violations = $result.Violations
                }

                $script:ViolationReport.Violations += $fileViolation

                Write-LintLog "ISSUES FOUND: $($script.Name) ($($result.Violations.Count) violations)" "WARN"

                foreach ($v in $result.Violations) {
                    Write-LintLog "  [$($v.Severity)] Line $($v.Line): $($v.Description) - $($v.Details)" "ERROR"

                    # Update summary counts
                    if (-not $script:ViolationReport.Summary.ContainsKey($v.Type)) {
                        $script:ViolationReport.Summary[$v.Type] = 0
                    }
                    $script:ViolationReport.Summary[$v.Type]++
                }

                # Auto-fix if requested
                if ($AutoFix -and -not $ReportOnly) {
                    Invoke-AutoFix -FilePath $script.FullName -Violations $result.Violations
                }
            }
        }
        else {
            Write-LintLog "ERROR scanning $($script.Name): $($result.Error)" "ERROR"
        }
    }

    # Generate report
    Write-LintLog "" "INFO"
    Write-LintLog "==================================================================" "INFO"
    Write-LintLog "LINT CHECK SUMMARY" "INFO"
    Write-LintLog "==================================================================" "INFO"
    Write-LintLog "Total Files Scanned: $($script:ViolationReport.TotalFiles)" "INFO"
    Write-LintLog "Clean Files: $($script:ViolationReport.CleanFiles)" "SUCCESS"
    Write-LintLog "Files With Issues: $($script:ViolationReport.FilesWithIssues)" "WARN"
    Write-LintLog "" "INFO"

    if ($script:ViolationReport.Summary.Count -gt 0) {
        Write-LintLog "Violations by Type:" "WARN"
        foreach ($type in $script:ViolationReport.Summary.Keys) {
            Write-LintLog "  $type: $($script:ViolationReport.Summary[$type])" "ERROR"
        }
    }

    # Export report
    $reportsDir = Join-Path $Path "reports"
    if (-not (Test-Path $reportsDir)) {
        New-Item -Path $reportsDir -ItemType Directory -Force | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $reportPath = Join-Path $reportsDir "lint_report_$timestamp.json"

    $script:ViolationReport | ConvertTo-Json -Depth 10 | Set-Content $reportPath -Force -Encoding ASCII

    Write-LintLog "" "INFO"
    Write-LintLog "[OK] Report saved: $reportPath" "SUCCESS"
}

# Run main lint check
Invoke-MainLintCheck
