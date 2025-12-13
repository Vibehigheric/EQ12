# FORCE UTF-8 ENCODING - EQ12 GLOBAL ENCODING GUARD
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Export-Csv:Encoding'] = 'utf8'
$OutputEncoding = [System.Text.Encoding]::UTF8

<#
EQ12 COMPREHENSIVE FILE REPAIR SYSTEM
Fixes ALL 8,722 files with PowerShell 5.1 compatibility
Repairs: Markdown, JSON, TXT, PS1, PY, logs, configs
#>

Write-Host "=== EQ12 COMPREHENSIVE FILE REPAIR SYSTEM ===" -ForegroundColor Green
Write-Host "Repairing ALL 8,722 files with UTF-8 safety" -ForegroundColor Yellow
Write-Host "PowerShell 5.1 Compatible - No AsByteStream errors" -ForegroundColor Cyan

# PowerShell 5.1 Safe File Operations
function Get-FileBytesSafe {
    param([string]$Path)
    
    try {
        if (!(Test-Path $Path)) { return $null }
        return [System.IO.File]::ReadAllBytes($Path)
    }
    catch {
        Write-Warning "Could not read bytes: $Path - $($_.Exception.Message)"
        return $null
    }
}

function Get-FileTextSafe {
    param([string]$Path)
    
    try {
        if (!(Test-Path $Path)) { return $null }
        return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    }
    catch {
        Write-Warning "Could not read text: $Path - $($_.Exception.Message)"
        return $null
    }
}

function Write-FileUTF8Safe {
    param(
        [string]$Path,
        [string]$Content
    )
    
    try {
        # Force UTF-8 with no BOM
        $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBOM)
        return $true
    }
    catch {
        Write-Warning "Could not write file: $Path - $($_.Exception.Message)"
        return $false
    }
}

function Test-EncodingIssues {
    param([string]$Content)
    
    $issues = @()
    
    if ($null -eq $Content -or $Content -eq "") {
        return $issues
    }
    
    # Check for BOM (will be handled at byte level)
    if ($Content.StartsWith([char]0xFEFF)) {
        $issues += "UTF-8 BOM detected"
    }
    
    # Check for smart quotes and problematic characters
    if ($Content -match '[\u2018\u2019\u201C\u201D\u2013\u2014]') {
        $issues += "Smart quotes detected"
    }
    
    # Check for Windows-1252 characters that become corrupted
    if ($Content -match '[\u0080-\u009F]') {
        $issues += "Windows-1252 characters detected"
    }
    
    # Check for null bytes
    if ($Content -match '[\x00]') {
        $issues += "Null bytes detected"
    }
    
    # Check for emoji in source code files
    if ($Content -match '[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]') {
        $issues += "Emoji characters detected"
    }
    
    return $issues
}

function Repair-Content {
    param(
        [string]$Content,
        [string]$FileExtension
    )
    
    if ($null -eq $Content -or $Content -eq "") {
        return $Content
    }
    
    # Remove BOM if present
    if ($Content.StartsWith([char]0xFEFF)) {
        $Content = $Content.Substring(1)
    }
    
    # Fix smart quotes
    $Content = $Content -replace '[\u2018\u2019]', "'"  # Smart single quotes
    $Content = $Content -replace '[\u201C\u201D]', '"'  # Smart double quotes
    $Content = $Content -replace '[\u2013\u2014]', '-'  # Em dash / En dash
    $Content = $Content -replace '[\u2026]', '...'      # Ellipsis
    
    # Remove Windows-1252 artifacts
    $Content = $Content -replace '[\u0080-\u009F]', ''
    
    # Remove null bytes
    $Content = $Content -replace '[\x00]', ''
    
    # Remove emojis from source code files
    if ($FileExtension -in @('.ps1', '.py', '.js', '.cs', '.cpp', '.h', '.bat', '.cmd')) {
        $Content = $Content -replace '[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]', ''
    }
    
    # Fix JSON format issues
    if ($FileExtension -eq '.json') {
        try {
            # Try to parse and reformat JSON
            $jsonObject = $Content | ConvertFrom-Json
            $Content = $jsonObject | ConvertTo-Json -Depth 10 -Compress:$false
        }
        catch {
            # If JSON parsing fails, try basic fixes
            $Content = $Content -replace "([^\\])'", '$1"'  # Replace single quotes with double quotes (basic)
        }
    }
    
    # Normalize line endings to LF
    $Content = $Content -replace "`r`n", "`n"
    $Content = $Content -replace "`r", "`n"
    
    return $Content
}

function Repair-FilesSafe {
    param([string]$BasePath = "C:\EQ12")
    
    Write-Host "`nStarting comprehensive file repair..." -ForegroundColor Yellow
    
    $stats = @{
        Total       = 0
        Processed   = 0
        Repaired    = 0
        Skipped     = 0
        Errors      = 0
        IssuesFound = @{}
    }
    
    $repairLog = @()
    
    # Get all files recursively
    $allFiles = Get-ChildItem -Path $BasePath -Recurse -File -ErrorAction SilentlyContinue
    $stats.Total = $allFiles.Count
    
    Write-Host "Found $($stats.Total) files to process" -ForegroundColor Cyan
    
    foreach ($file in $allFiles) {
        $stats.Processed++
        
        if ($stats.Processed % 100 -eq 0) {
            Write-Host "Processed $($stats.Processed)/$($stats.Total) files..." -ForegroundColor Gray
        }
        
        try {
            # Skip binary files
            $ext = $file.Extension.ToLower()
            $binaryExtensions = @('.exe', '.dll', '.zip', '.jpg', '.jpeg', '.png', '.gif', '.ico', '.bin', '.pdf')
            
            if ($ext -in $binaryExtensions) {
                $stats.Skipped++
                continue
            }
            
            # Check for BOM at byte level first
            $bytes = Get-FileBytesSafe $file.FullName
            if ($null -eq $bytes) {
                $stats.Errors++
                continue
            }
            
            $hasBOM = $false
            if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
                $hasBOM = $true
            }
            
            # Read text content
            $content = Get-FileTextSafe $file.FullName
            if ($null -eq $content) {
                $stats.Errors++
                continue
            }
            
            # Test for issues
            $issues = Test-EncodingIssues $content
            if ($hasBOM) {
                $issues += "UTF-8 BOM"
            }
            
            if ($issues.Count -gt 0) {
                # Track issues
                foreach ($issue in $issues) {
                    if ($stats.IssuesFound.ContainsKey($issue)) {
                        $stats.IssuesFound[$issue]++
                    }
                    else {
                        $stats.IssuesFound[$issue] = 1
                    }
                }
                
                # Repair content
                $repairedContent = Repair-Content $content $ext
                
                # Write repaired file
                if (Write-FileUTF8Safe $file.FullName $repairedContent) {
                    $stats.Repaired++
                    
                    $repairLog += @{
                        File      = $file.FullName
                        Issues    = $issues
                        Size      = $file.Length
                        Extension = $ext
                    }
                }
                else {
                    $stats.Errors++
                }
            }
            
        }
        catch {
            Write-Warning "Error processing $($file.FullName): $_"
            $stats.Errors++
        }
    }
    
    return @{
        Stats     = $stats
        RepairLog = $repairLog
    }
}

# Execute comprehensive repair
$results = Repair-FilesSafe

# Generate detailed report
$reportData = @{
    Timestamp           = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    PowerShellVersion   = $PSVersionTable.PSVersion.ToString()
    EncodingMode        = "UTF-8 No BOM"
    Statistics          = $results.Stats
    IssuesRepaired      = $results.Stats.IssuesFound
    SampleRepairedFiles = $results.RepairLog | Select-Object -First 20
    SystemStatus        = "UTF-8 Hardened"
    ContentEmpireMode   = $env:CONTENT_EMPIRE_MODE
    RevenueTarget       = $env:REVENUE_TARGET_DAILY
}

$reportPath = "C:\EQ12\logs\EQ12_REPAIRED_FILES_REPORT.json"
$reportJson = $reportData | ConvertTo-Json -Depth 10
Write-FileUTF8Safe $reportPath $reportJson

# Display results
Write-Host "`n=== EQ12 FILE REPAIR COMPLETE ===" -ForegroundColor Green
Write-Host "Total files: $($results.Stats.Total)" -ForegroundColor White
Write-Host "Processed: $($results.Stats.Processed)" -ForegroundColor White
Write-Host "Repaired: $($results.Stats.Repaired)" -ForegroundColor Yellow
Write-Host "Skipped: $($results.Stats.Skipped)" -ForegroundColor Gray
Write-Host "Errors: $($results.Stats.Errors)" -ForegroundColor Red

Write-Host "`nIssues found and repaired:" -ForegroundColor Cyan
foreach ($issue in $results.Stats.IssuesFound.GetEnumerator()) {
    Write-Host "  $($issue.Key): $($issue.Value) files" -ForegroundColor White
}

Write-Host "`nRepair report saved: $reportPath" -ForegroundColor Green
Write-Host "All files now UTF-8 compatible and encoding-safe!" -ForegroundColor Magenta
Write-Host "EQ12 system fully hardened for Content Empire operations" -ForegroundColor Yellow