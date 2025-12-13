#Requires -Version 5.1
param(
    [Parameter(Mandatory=$true)]
    [string]$File
)

Write-Host "CLEANING FILE (ASCII-SAFE): $File"

if (-not (Test-Path $File)) {
    Write-Host "ERROR: File not found: $File" -ForegroundColor Red
    exit 1
}

try {
    $content = Get-Content $File -Raw -Encoding UTF8

    Write-Host "Original size: $($content.Length) characters"

    # Remove non-ASCII characters (keep only 0-127 ASCII range)
    $clean = $content -replace '[^\x00-\x7F]', ''

    # Normalize quotes - remove smart quotes
    $clean = $clean -replace '[""]', '"'
    $clean = $clean -replace "['']", "'"

    # Remove Unicode line breaks
    $clean = $clean -replace "`u2028|`u2029", "`r`n"

    # Replace fancy dashes with ASCII (using char codes to avoid corruption)
    $clean = $clean -replace [char]8211, "-"
    $clean = $clean -replace [char]8212, "-"

    # Fix common PowerShell issues
    $clean = $clean -replace [char]96, "'"    # Ensure proper Windows line endings
    $clean = $clean -replace "`r?`n", "`r`n"

    Write-Host "Cleaned size: $($clean.Length) characters"
    Write-Host "Removed: $($content.Length - $clean.Length) non-ASCII characters"

    # Create backup
    $backup = "$File.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $File $backup
    Write-Host "Backup created: $backup"

    # Save as pure ASCII
    Set-Content -Path $File -Value $clean -Encoding ASCII

    Write-Host "SUCCESS: FILE CLEANED AND SAVED AS ASCII" -ForegroundColor Green

} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
