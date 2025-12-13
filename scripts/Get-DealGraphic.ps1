[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$JsonIn,
    [string]$Template,
    [string]$Font,
    [string]$Out
)

function Get-DealGraphic {
    param($JsonIn, $Template, $Font, $Out)

    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { Write-Error "python not found in PATH"; return }

    $pythonArgs = @()
    $pythonArgs += '--in'; $pythonArgs += $JsonIn
    if ($Template) { $pythonArgs += '--template'; $pythonArgs += $Template }
    if ($Font) { $pythonArgs += '--font'; $pythonArgs += $Font }
    if ($Out) { $pythonArgs += '--out'; $pythonArgs += $Out }

    & $python.Source '-m' 'graphics.graphics_alert' @pythonArgs
}

Get-DealGraphic -JsonIn $JsonIn -Template $Template -Font $Font -Out $Out
