<#
eq12_cleanup.ps1
Safe, interactive cleanup utility for C:\EQ12

Usage examples:
# Dry-run to see actions (default)
powershell -ExecutionPolicy Bypass -File C:\EQ12\eq12_cleanup.ps1

# Archive virtualenvs and caches into C:\EQ12\archive (dry-run suppressed)
powershell -ExecutionPolicy Bypass -File C:\EQ12\eq12_cleanup.ps1 --Archive --Confirm

# Archive then remove (destructive) - requires explicit --Remove and --Confirm
powershell -ExecutionPolicy Bypass -File C:\EQ12\eq12_cleanup.ps1 --Archive --Remove --Confirm

Notes:
- This script is conservative: without --Remove it will not delete anything.
- Use --DryRun to preview actions (default true unless --Confirm provided).
- Creates a log at C:\EQ12\cleanup_log.txt
- Run as Administrator if you will remove protected files (-RunAsAdministrator comment)
#>

param(
    [switch]$Archive,
    [switch]$Remove,
    [switch]$Confirm,
    [switch]$VerboseMode,
    [switch]$DryRun = $true,
    [string]$Folder = 'C:\EQ12',
    [string]$ArchiveFolder = 'C:\EQ12\archive',
    [string[]]$Targets = @('.ven*','.pytest_cache','.ruff_cache','node_modules'),
    [int]$CompressionLevel = 5
)

$ErrorActionPreference = 'Stop'
$log = Join-Path $Folder 'cleanup_log.txt'
"Cleanup run: $(Get-Date)" | Out-File $log -Encoding utf8

if (-not (Test-Path $Folder)) { Write-Host "Folder $Folder not found"; exit 1 }

function LogWrite([string]$line) {
    $line | Out-File -Append $log -Encoding utf8
    if ($VerboseMode) { Write-Host $line }
}

LogWrite "Parameters: Archive=$Archive; Remove=$Remove; Confirm=$Confirm; DryRun=$DryRun; Targets=$($Targets -join ',')"

# Discover candidates
$candidates = @()
foreach ($t in $Targets) {
    $found = Get-ChildItem -Path $Folder -Recurse -Force -ErrorAction SilentlyContinue | Where-Object { $_.PSIsContainer -and ($_.Name -like $t) }
    foreach ($f in $found) { $candidates += $f }
}

if ($candidates.Count -eq 0) {
    LogWrite "No cleanup candidates found for targets: $($Targets -join ',')"
    Write-Host "No cleanup candidates found. See $log for details."; exit 0
}

# Summarize candidates with sizes
LogWrite "Found $($candidates.Count) candidate directories:" 
foreach ($c in $candidates) {
    $size = (Get-ChildItem -Path $c.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round(($size/1MB),2)
    LogWrite "  $sizeMB MB  $($c.FullName)"
}

# If user didn't pass Confirm, keep DryRun true
if (-not $Confirm) { $DryRun = $true }

if ($DryRun) { Write-Host "DRY RUN: No files will be deleted. Use --Confirm to allow actions." }

# Ensure archive folder exists if archiving
if ($Archive) {
    if (-not (Test-Path $ArchiveFolder)) {
        if ($DryRun) { LogWrite "(Dry) Would create archive folder: $ArchiveFolder" } else { New-Item -Path $ArchiveFolder -ItemType Directory -Force | Out-Null; LogWrite "Created archive folder: $ArchiveFolder" }
    }
}

# Perform actions per candidate
foreach ($c in $candidates) {
    $size = (Get-ChildItem -Path $c.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $sizeMB = [math]::Round(($size/1MB),2)
    $safeName = ($c.FullName -replace '[:\\]','_') -replace '\s+','_'
    $zipPath = Join-Path $ArchiveFolder "archive_$($safeName)_$(Get-Date -Format yyyyMMdd_HHmmss).zip"

    if ($Archive) {
        if ($DryRun) {
            LogWrite "(Dry) Would compress $($c.FullName) -> $zipPath (approx $sizeMB MB)"
        } else {
            Write-Host "Compressing $($c.FullName) -> $zipPath"
            try {
                Compress-Archive -Path "$($c.FullName)\*" -DestinationPath $zipPath -Force
                LogWrite "Compressed $($c.FullName) -> $zipPath"
            } catch {
                LogWrite "Error compressing $($c.FullName): $_"
            }
        }
    }

    if ($Remove) {
        if ($DryRun) {
            LogWrite "(Dry) Would remove $($c.FullName)"
        } else {
            Write-Host "Removing $($c.FullName)"
            try {
                Remove-Item -Path $c.FullName -Recurse -Force -ErrorAction Stop
                LogWrite "Removed $($c.FullName)"
            } catch {
                LogWrite "Error removing $($c.FullName): $_"
            }
        }
    }
}

# Additional cache prune suggestions (non-destructive)
LogWrite "Suggested manual cache pruning commands:"
LogWrite "  Remove-Item -Path C:\EQ12\**\.pytest_cache -Recurse -Force  # remove pytest caches"
LogWrite "  Remove-Item -Path C:\EQ12\**\.ruff_cache -Recurse -Force    # remove ruff caches"
LogWrite "  npm prune --prefix C:\EQ12\<project>                         # prune node_modules"

Write-Host "Cleanup actions recorded in: $log"
if ($DryRun) { Write-Host "Dry run completed. To perform actions, re-run with --Archive and/or --Remove and include --Confirm." }

exit 0
