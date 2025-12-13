<# EQ12 patch: PowerShell wrapper for Rakuten scraper #>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [string]$OutPath = "C:\EQ12\logs\rakuten.json"
)

function Get-RakutenDeals {
    [CmdletBinding()]
    param(
        [switch]$DryRun,
        [string]$OutPath = "C:\EQ12\logs\rakuten.json"
    )

    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Error "Python not found in PATH."
        return
    }

    $pythonArgs = @()
    if ($DryRun) { $pythonArgs += '--dry-run' } else { $pythonArgs += '--no-dry-run' }
    $pythonArgs += '--out'; $pythonArgs += $OutPath

    Write-Host ("Running Rakuten scraper (DryRun={0}) -> {1}" -f $DryRun, $OutPath)
    & $python.Source @pythonArgs
}

if ($MyInvocation.InvocationName -ne '.') {
    # invoked directly
    Get-RakutenDeals -DryRun:$DryRun -OutPath $OutPath
}

# TODO: add Pester test
