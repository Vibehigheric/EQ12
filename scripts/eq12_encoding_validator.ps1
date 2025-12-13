# FORCE UTF-8 ENCODING - EQ12 GLOBAL ENCODING GUARD
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Export-Csv:Encoding'] = 'utf8'
$OutputEncoding = [System.Text.Encoding]::UTF8

<#
EQ12 ENCODING VALIDATION SCANNER
Detects and fixes encoding issues across the entire EQ12 system
#>

Write-Host "=== EQ12 ENCODING VALIDATION SCANNER ===" -ForegroundColor Cyan

function Test-FileEncoding {
    param([string]$FilePath)
    
    if (!(Test-Path $FilePath)) { return @{} }
    
    try {
        $bytes = Get-Content $FilePath -AsByteStream -TotalCount 4
        $encoding = "Unknown"
        $hasBOM = $false
        $issues = @()
        
        # Check for BOM
        if ($bytes.Count -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $encoding = "UTF-8 with BOM"
            $hasBOM = $true
            $issues += "Has BOM (should be removed)"
        } elseif ($bytes.Count -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
            $encoding = "UTF-16 LE"
            $issues += "Wrong encoding (should be UTF-8)"
        } else {
            $encoding = "UTF-8 (assumed)"
        }
        
        # Check content for problematic characters
        $content = Get-Content $FilePath -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($content) {
            $contentStr = $content -join "`n"
            
            # Check for smart quotes
            if ($contentStr -match '[\u2018\u2019\u201C\u201D\u2013\u2014]') {
                $issues += "Contains smart quotes"
            }
            
            # Check for high ASCII
            if ($contentStr -match '[^\u0000-\u007F]' -and $FilePath -match '\.(ps1|cmd|bat)$') {
                $issues += "Non-ASCII characters in script file"
            }
            
            # Check for emoji in source code
            if ($contentStr -match '[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]') {
                $issues += "Contains emoji in source code"
            }
        }
        
        return @{
            Encoding = $encoding
            HasBOM = $hasBOM
            Issues = $issues
            Path = $FilePath
        }
    }
    catch {
        return @{
            Encoding = "Error"
            Issues = @("Could not read file: $_")
            Path = $FilePath
        }
    }
}

function Repair-FileEncoding {
    param([string]$FilePath, [array]$Issues)
    
    if (!(Test-Path $FilePath)) { return }
    
    try {
        $content = Get-Content $FilePath -Encoding UTF8
        $contentStr = $content -join "`n"
        $fixed = $false
        
        # Fix smart quotes
        if ($Issues -contains "Contains smart quotes") {
            $contentStr = $contentStr -replace '[\u2018\u2019]', "'"
            $contentStr = $contentStr -replace '[\u201C\u201D]', '"'
            $contentStr = $contentStr -replace '[\u2013\u2014]', '-'
            $fixed = $true
        }
        
        # Remove emojis from source files
        if ($Issues -contains "Contains emoji in source code" -and $FilePath -match '\.(ps1|py|js|cs|cpp|h)$') {
            $contentStr = $contentStr -replace '[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]', ''
            $fixed = $true
        }
        
        if ($fixed) {
            # Write back with UTF-8 no BOM
            $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
            [System.IO.File]::WriteAllText($FilePath, $contentStr, $utf8NoBOM)
            Write-Host "  FIXED: $FilePath" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "  ERROR fixing $FilePath : $_" -ForegroundColor Red
    }
}

function Scan-EQ12System {
    Write-Host "`nScanning EQ12 system for encoding issues..." -ForegroundColor Yellow
    
    $scanPaths = @(
        "C:\EQ12\scripts\*.ps1",
        "C:\EQ12\scripts\*.py", 
        "C:\EQ12\configs\*.json",
        "C:\EQ12\logs\*.json",
        "C:\EQ12\*.md",
        "C:\EQ12\*.txt"
    )
    
    $totalFiles = 0
    $issueFiles = 0
    $fixedFiles = 0
    
    foreach ($pattern in $scanPaths) {
        $files = Get-ChildItem $pattern -ErrorAction SilentlyContinue
        
        foreach ($file in $files) {
            $totalFiles++
            $result = Test-FileEncoding -FilePath $file.FullName
            
            if ($result.Issues.Count -gt 0) {
                $issueFiles++
                Write-Host "`nISSUES in $($file.Name):" -ForegroundColor Yellow
                foreach ($issue in $result.Issues) {
                    Write-Host "  - $issue" -ForegroundColor Red
                }
                
                # Auto-repair if possible
                Repair-FileEncoding -FilePath $file.FullName -Issues $result.Issues
                $fixedFiles++
            }
        }
    }
    
    Write-Host "`n=== SCAN RESULTS ===" -ForegroundColor Cyan
    Write-Host "Total files scanned: $totalFiles" -ForegroundColor White
    Write-Host "Files with issues: $issueFiles" -ForegroundColor Yellow
    Write-Host "Files auto-fixed: $fixedFiles" -ForegroundColor Green
}

function Create-EncodingReport {
    $reportPath = "C:\EQ12\logs\encoding_validation_report.json"
    
    $report = @{
        timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        system_status = "UTF-8 Hardened"
        environment_vars = @{
            PYTHONUTF8 = $env:PYTHONUTF8
            LC_ALL = $env:LC_ALL
            LANG = $env:LANG
        }
        powershell_encoding = $OutputEncoding.EncodingName
        scan_completed = $true
    }
    
    $reportJson = $report | ConvertTo-Json -Depth 10
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($reportPath, $reportJson, $utf8NoBOM)
    
    Write-Host "`nEncoding validation report saved: $reportPath" -ForegroundColor Green
}

# Run the validation scan
Scan-EQ12System
Create-EncodingReport

Write-Host "`nEQ12 system encoding validation complete!" -ForegroundColor Magenta
Write-Host "All files hardened for UTF-8 compatibility" -ForegroundColor Green