[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$DotfilesRepo = 'https://github.com/yourusername/dotfiles.git',
    [Parameter(Mandatory=$false)]
    [string]$Target = "$env:USERPROFILE\\.dotfiles"
)

Write-Host "Installing dotfiles to $Target"
if (-not (Test-Path $Target)) {
    git clone $DotfilesRepo $Target
} else {
    Write-Host "Dotfiles already present at $Target; pulling updates"
    Push-Location $Target
    git pull --ff-only
    Pop-Location
}

# Run install script if exists
$installer = Join-Path $Target 'install.ps1'
if (Test-Path $installer) {
    Write-Host "Running dotfiles installer"
    & $installer
}

Write-Host "Dotfiles install complete."