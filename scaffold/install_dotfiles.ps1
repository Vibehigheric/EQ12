[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$DotfilesRepo = 'https://github.com/yourusername/dotfiles.git',
    [Parameter(Mandatory=$false)]
    [string]$Target = "$env:USERPROFILE\\.dotfiles"
)

Write-Host "Scaffold: installing dotfiles to $Target"
if (-not (Test-Path $Target)) {
    git clone $DotfilesRepo $Target
} else {
    Write-Host "Dotfiles already present at $Target; pulling updates"
    Push-Location $Target
    git pull --ff-only
    Pop-Location
}

# Add an import into the user's PowerShell profile
$profilePath = Join-Path $env:USERPROFILE 'Documents\PowerShell\Microsoft.PowerShell_profile.ps1'
if (-not (Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force | Out-Null
}

$importLine = "`n# EQ12 dotfiles import`n. '$Target\\powershell_profile.ps1'`n"
if (-not (Select-String -Path $profilePath -Pattern 'EQ12 dotfiles import' -Quiet)) {
    Add-Content -Path $profilePath -Value $importLine
    Write-Host "Injected EQ12 dotfiles import into PowerShell profile: $profilePath"
} else {
    Write-Host "EQ12 dotfiles already referenced in $profilePath"
}
