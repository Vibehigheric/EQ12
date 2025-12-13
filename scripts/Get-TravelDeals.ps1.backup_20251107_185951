<# EQ12 patch: PowerShell wrapper for TravelDeals scraper #>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [string]$Watchlist = "configs/travel_watchlist.json",
    [string]$OutPath = "C:\EQ12\logs\travel_deals.json"
)

function Get-TravelDeals {
    [CmdletBinding()]
    param(
        [switch]$DryRun,
        [string]$Watchlist = "configs/travel_watchlist.json",
        [string]$OutPath = "C:\EQ12\logs\travel_deals.json"
    )

    $py = Get-Command python -ErrorAction SilentlyContinue
    if (-not $py) { Write-Error "Python not found"; return }

    $pyArgs = @('scripts/travel_deals_scraper.py')
    $pyArgs += '--watchlist'; $pyArgs += $Watchlist
    if ($DryRun) { $pyArgs += '--dry-run' } else { $pyArgs += '--no-dry-run' }
    $pyArgs += '--out'; $pyArgs += $OutPath

    Write-Host "Invoking travel_deals_scraper with args: $($pyArgs -join ' ')"
    & $py.Source @pyArgs
}

if ($null -ne $PSCommandPath -and $MyInvocation.InvocationName -eq '.') {
    # dot-sourced
} elseif ($null -ne $MyInvocation.InvocationName) {
    Get-TravelDeals -DryRun:$DryRun -Watchlist $Watchlist -OutPath $OutPath
}

# TODO: add Pester test
