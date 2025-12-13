[CmdletBinding()]
param(
    [string]$LogsDir = 'C:\EQ12\logs',
    [string]$ArchiveDir = 'C:\EQ12\logs\archive',
    [int]$Days = 7
)

function Sync-EQ12Drive {
    param($LogsDir, $ArchiveDir, $Days)

    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { Write-Error "python not found in PATH"; return }

    $pyArgs = @('archive_logs', $LogsDir, $ArchiveDir, '--days', $Days.ToString())
    & $python.Source '-m' 'drive.eq12_drive' @pyArgs | Out-Host
}

Sync-EQ12Drive -LogsDir $LogsDir -ArchiveDir $ArchiveDir -Days $Days
