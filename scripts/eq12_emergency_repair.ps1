# EQ12 PowerShell Script Emergency Repair Utility v3.0
# SIMPLIFIED ASCII-SAFE CORRUPTION REPAIR SYSTEM
# Buffalo NY 14215 - Content Empire

param(
    [string]$ScriptDirectory = "C:\EQ12\scripts",
    [switch]$AutoFix,
    [switch]$BackupFiles
)

Write-Host "=== EQ12 EMERGENCY SCRIPT REPAIR v3.0 ===" -ForegroundColor Green
Write-Host "Scanning: $ScriptDirectory" -ForegroundColor Cyan
Write-Host "Auto-Fix: $AutoFix" -ForegroundColor Yellow

$LogPath = "C:\EQ12\logs\emergency_repair_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    Add-Content -Path $LogPath -Value $logEntry
}

function Repair-Script {
    param($FilePath)

    Write-Log "CHECKING: $FilePath"

    try {
        # Read file content
        $content = Get-Content $FilePath -Raw
        $originalContent = $content
        $fixCount = 0

        # Fix 1: Remove problematic characters
        $cleanContent = $content -replace '[^\x00-\x7F]', ''
        if ($cleanContent -ne $content) {
            $content = $cleanContent
            $fixCount++
            Write-Log "  FIX 1: Removed non-ASCII characters"
        }

        # Fix 2: Count and balance braces
        $openBraces = ($content.ToCharArray() | Where-Object { $_ -eq '{' }).Count
        $closeBraces = ($content.ToCharArray() | Where-Object { $_ -eq '}' }).Count

        if ($openBraces -gt $closeBraces) {
            $missingBraces = $openBraces - $closeBraces
            $content = $content + ("`n}" * $missingBraces)
            $fixCount++
            Write-Log "  FIX 2: Added $missingBraces missing closing braces"
        }

        # Fix 3: Simple syntax validation
        $tempFile = "$env:TEMP\test_$(Get-Random).ps1"
        Set-Content -Path $tempFile -Value $content

        $parseResult = powershell -NoProfile -Command "try { [System.Management.Automation.PSParser]::Tokenize('$content', [ref]`$null) | Out-Null; 'VALID' } catch { 'INVALID' }"
        Remove-Item $tempFile -Force -ErrorAction SilentlyContinue

        if ($parseResult -eq 'VALID') {
            Write-Log "  SYNTAX: Valid PowerShell"
        } else {
            Write-Log "  SYNTAX: Still has errors after basic fixes"
        }

        # Apply fixes if requested
        if ($AutoFix -and $fixCount -gt 0) {
            if ($BackupFiles) {
                $backupPath = $FilePath + ".backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                Copy-Item $FilePath $backupPath
                Write-Log "  BACKUP: Created $backupPath"
            }

            Set-Content -Path $FilePath -Value $content
            Write-Log "  SAVED: Applied $fixCount fixes"
        }

        return @{
            File = $FilePath
            Fixes = $fixCount
            Valid = ($parseResult -eq 'VALID')
        }

    } catch {
        Write-Log "  ERROR: $_"
        return @{
            File = $FilePath
            Fixes = 0
            Valid = $false
        }
    }
}

# Main execution
if (-not (Test-Path "C:\EQ12\logs")) {
    New-Item -Path "C:\EQ12\logs" -ItemType Directory -Force | Out-Null
}

$psFiles = Get-ChildItem -Path $ScriptDirectory -Filter "*.ps1" -Recurse
Write-Log "Found $($psFiles.Count) PowerShell files"

$results = @()
$totalFixes = 0

foreach ($file in $psFiles) {
    $result = Repair-Script -FilePath $file.FullName
    $results += $result
    $totalFixes += $result.Fixes
}

Write-Log "=== REPAIR COMPLETE ==="
Write-Log "Files processed: $($results.Count)"
Write-Log "Total fixes applied: $totalFixes"
Write-Log "Valid files: $(($results | Where-Object { $_.Valid }).Count)"
Write-Log "Invalid files: $(($results | Where-Object { -not $_.Valid }).Count)"

$invalidFiles = $results | Where-Object { -not $_.Valid }
if ($invalidFiles.Count -gt 0) {
    Write-Log "Files still needing manual repair:"
    foreach ($invalid in $invalidFiles) {
        Write-Log "  - $($invalid.File)"
    }
}

Write-Host "`nLog saved: $LogPath" -ForegroundColor Green
return $results
