<#
EQ12 patch
Ensure-OddsAPIKey: Read and cache ODDS_API_KEY from environment
#>
[CmdletBinding()]
param()

function Get-CachedOddsApiKey {
    if ($script:OddsApiKey) { return $script:OddsApiKey }
    $k = $env:ODDS_API_KEY
    if (-not $k) {
        Write-Warning 'ODDS_API_KEY not set in environment'
        return $null
    }
    $script:OddsApiKey = $k
    return $script:OddsApiKey
}

Export-ModuleMember -Function Get-CachedOddsApiKey
