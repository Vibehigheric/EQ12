
$source = "C:\EQ12_BROKEN_20251122_210342\restored_from_backup"
$dest = "C:\EQ12_BROKEN_20251122_210342\legacy_swarm"

$categories = @{
    "NBA"             = "*nba*"
    "NFL"             = "*nfl*"
    "NHL"             = "*nhl*"
    "Betting_General" = "*betting*"
    "Parlays"         = "*parlay*"
    "Intelligence"    = "*intelligence*"
    "Monitors"        = "*monitor*"
    "Orchestrators"   = "*orchestrator*"
    "Scrapers"        = "*scraper*"
}

foreach ($cat in $categories.Keys) {
    $catPath = Join-Path $dest $cat
    if (-not (Test-Path $catPath)) {
        New-Item -ItemType Directory -Path $catPath | Out-Null
    }
    
    $pattern = $categories[$cat]
    Get-ChildItem -Path $source -Filter $pattern | ForEach-Object {
        $target = Join-Path $catPath $_.Name
        if (-not (Test-Path $target)) {
            Move-Item -Path $_.FullName -Destination $target
            Write-Host "Moved $($_.Name) to $cat"
        }
    }
}

# Move remaining python files to "Misc_Python"
$miscPath = Join-Path $dest "Misc_Python"
if (-not (Test-Path $miscPath)) { New-Item -ItemType Directory -Path $miscPath | Out-Null }
Get-ChildItem -Path $source -Filter "*.py" | Move-Item -Destination $miscPath
