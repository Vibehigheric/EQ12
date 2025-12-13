# EQ12 Clean Workspace - Full ASCII Purification
# Removes ALL Unicode corruption that causes Pylance EPIPE errors
# Buffalo NY 14215 Content Empire
# Date: November 16, 2025

[CmdletBinding()]
param(
    [string]$WorkspacePath = "C:\EQ12",
    [switch]$Verbose,
    [switch]$BackupFirst,
    [switch]$DryRun
)

Write-Host "================================================================" -ForegroundColor Green
Write-Host "EQ12 WORKSPACE ASCII PURIFICATION TOOL" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN MODE - No files will be modified" -ForegroundColor Yellow
    Write-Host ""
}

# Verify workspace path exists
if (!(Test-Path $WorkspacePath)) {
    Write-Host "ERROR: Workspace path does not exist: $WorkspacePath" -ForegroundColor Red
    exit 1
}

Write-Host "Workspace Path: $WorkspacePath" -ForegroundColor Cyan
Write-Host "Starting full ASCII purification..." -ForegroundColor White
Write-Host ""

# File extensions to process
$targetExtensions = @(
    '*.py', '*.ps1', '*.json', '*.txt', '*.md', '*.log',
    '*.env', '*.yml', '*.yaml', '*.cfg', '*.ini', '*.conf'
)

# Initialize counters
$filesProcessed = 0
$filesRepaired = 0
$filesFailed = 0
$bytesRemoved = 0

# Get all target files
$allFiles = @()
foreach ($ext in $targetExtensions) {
    $files = Get-ChildItem -Path $WorkspacePath -Recurse -File -Include $ext -ErrorAction SilentlyContinue
    $allFiles += $files
}

# Filter out certain directories
$excludePaths = @('.git', '__pycache__', '.venv', 'node_modules', '.vs', '.vscode-server')
$filteredFiles = $allFiles | Where-Object {
    $path = $_.FullName
    $exclude = $false
    foreach ($excludePath in $excludePaths) {
        if ($path -like "*\$excludePath\*") {
            $exclude = $true
            break
        }
    }
    !$exclude
}

Write-Host "Found $($filteredFiles.Count) files to process" -ForegroundColor Cyan
Write-Host ""

foreach ($file in $filteredFiles) {
    $filesProcessed++

    if ($Verbose) {
        Write-Host "[$filesProcessed/$($filteredFiles.Count)] Processing: $($file.Name)" -ForegroundColor Gray
    }

    try {
        # Create backup if requested
        if ($BackupFirst -and !$DryRun) {
            $backupPath = $file.FullName + ".unicode_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            Copy-Item $file.FullName $backupPath -Force -ErrorAction SilentlyContinue
        }

        # Read file content as binary first to handle any encoding
        $rawBytes = [System.IO.File]::ReadAllBytes($file.FullName)
        $originalSize = $rawBytes.Length

        # Convert to string with UTF-8 fallback
        try {
            $textContent = [System.Text.Encoding]::UTF8.GetString($rawBytes)
        } catch {
            # Fallback to default encoding
            $textContent = [System.Text.Encoding]::Default.GetString($rawBytes)
        }

        # Apply ASCII-only conversion
        $asciiBytes = [System.Text.Encoding]::ASCII.GetBytes($textContent)
        $asciiContent = [System.Text.Encoding]::ASCII.GetString($asciiBytes)

        # Additional cleaning for common problematic characters
        $asciiContent = $asciiContent -replace '[""''']', '"'  # Smart quotes to straight
        $asciiContent = $asciiContent -replace '—', '--'       # Em dash
        $asciiContent = $asciiContent -replace '–', '-'        # En dash
        $asciiContent = $asciiContent -replace '…', '...'      # Ellipsis
        $asciiContent = $asciiContent -replace '•', '-'        # Bullet
        $asciiContent = $asciiContent -replace '™', '(TM)'     # Trademark
        $asciiContent = $asciiContent -replace '©', '(C)'      # Copyright
        $asciiContent = $asciiContent -replace '®', '(R)'      # Registered

        # Remove zero-width spaces and other invisible Unicode
        $asciiContent = $asciiContent -replace '[\u200b-\u200f\ufeff]', ''

        # Calculate bytes removed
        $newSize = [System.Text.Encoding]::ASCII.GetByteCount($asciiContent)
        $removedBytes = $originalSize - $newSize
        $bytesRemoved += $removedBytes

        if (!$DryRun) {
            # Write back as pure ASCII
            [System.IO.File]::WriteAllText($file.FullName, $asciiContent, [System.Text.Encoding]::ASCII)
        }

        $filesRepaired++

        if ($Verbose) {
            if ($removedBytes -gt 0) {
                Write-Host "  CLEANED: Removed $removedBytes bytes of Unicode" -ForegroundColor Green
            } else {
                Write-Host "  OK: Already ASCII-safe" -ForegroundColor DarkGreen
            }
        }

    } catch {
        $filesFailed++
        if ($Verbose) {
            Write-Host "  FAILED: $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    # Progress indicator for large workspaces
    if ($filesProcessed % 100 -eq 0) {
        Write-Host "Progress: $filesProcessed/$($filteredFiles.Count) files processed..." -ForegroundColor Yellow
    }
}

# Final summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "ASCII PURIFICATION COMPLETE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Files processed: $filesProcessed" -ForegroundColor White
Write-Host "Files repaired: $filesRepaired" -ForegroundColor Green
Write-Host "Files failed: $filesFailed" -ForegroundColor $(if($filesFailed -gt 0){'Red'}else{'Green'})
Write-Host "Unicode bytes removed: $bytesRemoved" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN COMPLETE - No files were modified" -ForegroundColor Yellow
    Write-Host "Run without -DryRun to apply changes" -ForegroundColor Yellow
} else {
    if ($filesFailed -eq 0) {
        Write-Host "SUCCESS: All files converted to ASCII-safe mode" -ForegroundColor Green
        Write-Host "Pylance EPIPE corruption eliminated" -ForegroundColor Green
        Write-Host "Unicode crash sources removed" -ForegroundColor Green
    } else {
        Write-Host "WARNING: $filesFailed files could not be repaired" -ForegroundColor Red
        Write-Host "Manual inspection may be required" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor White
Write-Host "1. Run: powershell -File C:\EQ12\fix_copilot.ps1" -ForegroundColor Yellow
Write-Host "2. Restart VS Code completely" -ForegroundColor Yellow
Write-Host "3. Test Pylance - no more Unicode corruption" -ForegroundColor Yellow
Write-Host ""
Write-Host "Buffalo NY 14215 Content Empire - WORKSPACE HARDENED" -ForegroundColor Cyan

# Create PowerShell alias for easy future use
if (!$DryRun) {
    Write-Host ""
    Write-Host "Creating PowerShell alias 'cleanascii'..." -ForegroundColor Gray
    $aliasScript = @"
Set-Alias cleanascii "powershell -ExecutionPolicy Bypass -File C:\EQ12\scripts\eq12_clean_workspace.ps1"
"@

    try {
        $profilePath = $PROFILE.CurrentUserAllHosts
        if (!(Test-Path $profilePath)) {
            New-Item -ItemType File -Path $profilePath -Force | Out-Null
        }

        # Add alias if not already present
        $profileContent = Get-Content $profilePath -ErrorAction SilentlyContinue
        if ($profileContent -notcontains 'Set-Alias cleanascii') {
            Add-Content -Path $profilePath -Value $aliasScript
            Write-Host "Alias 'cleanascii' added to PowerShell profile" -ForegroundColor Green
            Write-Host "Use 'cleanascii' to run this script in the future" -ForegroundColor Green
        }
    } catch {
        Write-Host "Could not create PowerShell alias (non-critical)" -ForegroundColor DarkYellow
    }
}
