<##
Bootstrap script for EQ12. Dry-run by default; use -Apply to perform actions. Scans subdirectories and deploys boilerplate files and repo policies.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [switch]$Apply,
    [Parameter(Mandatory=$false)]
    [string]$Root = 'C:\EQ12'
)

$scaffoldDir = 'C:\EQ12\scaffold'

Write-Host "Scanning for git repos under $Root"
$repos = Get-ChildItem -Path $Root -Directory | Where-Object { Test-Path (Join-Path $_.FullName '.git') }
if ($repos.Count -eq 0) { Write-Host "No sub-repos found under $Root"; return }

foreach ($r in $repos) {
    Write-Host "Found repo: $($r.FullName)"
    if ($Apply) {
        Write-Host "Applying repo policies to $($r.FullName)"
        & C:\EQ12\scripts\apply_repo_policies.ps1 -RepoPath $r.FullName -VerboseOutput

        # Copy scaffold files into repo root (only if missing)
        if (Test-Path $scaffoldDir) {
            Get-ChildItem -Path $scaffoldDir -Recurse -File | ForEach-Object {
                $relative = $_.FullName.Substring($scaffoldDir.Length).TrimStart('\\')
                $dest = Join-Path $r.FullName $relative
                $destDir = Split-Path $dest -Parent
                if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
                if (-not (Test-Path $dest)) {
                    Copy-Item -Path $_.FullName -Destination $dest -Force
                    Write-Host "Copied scaffold $_.Name to $dest"
                }
            }
        }
    } else {
        Write-Host "Dry-run: would apply policies and scaffold to $($r.FullName)"
    }
}

Write-Host "Bootstrap complete. Use -Apply to actually deploy changes."