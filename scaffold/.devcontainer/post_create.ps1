[CmdletBinding()]
param()

Write-Host "EQ12 scaffold post-create: installing requirements and enabling profile"

# Ensure logs folder exists
$eq12Logs = $env:EQ12_LOGS -or '/workspaces/repo/logs'
if (-not (Test-Path $eq12Logs)) { New-Item -ItemType Directory -Path $eq12Logs -Force | Out-Null }

# Install Python requirements if present
$req = Join-Path $PSScriptRoot '..\\..\\requirements.txt'
if (Test-Path $req) {
    Write-Host "Installing requirements from $req"
    pip install -r $req
}

# Install Playwright browsers if playwright available
try {
    pip show playwright > $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Installing Playwright browsers"
        playwright install chromium firefox
    } else {
        Write-Host "Playwright not present; installing via pip and installing browsers"
        pip install playwright
        & python -m playwright install chromium firefox
    }
} catch {
    Write-Host "Playwright not installed, skipping browser install"
}

# Try to install stealth libs quietly
try {
    pip install undetected-chromedriver playwright-stealth fake-useragent -q
} catch {
    Write-Host "Could not install stealth libs automatically; please install in container if required."
}

# Auto-install dotfiles if DOTFILES_REPO provided (Codespaces convenience)
if ($env:DOTFILES_REPO) {
    $dotdir = "$HOME/.dotfiles"
    if (-not (Test-Path $dotdir)) {
        Write-Host "Cloning dotfiles from $env:DOTFILES_REPO"
        git clone $env:DOTFILES_REPO $dotdir
        $install = Join-Path $dotdir 'install.ps1'
        if (Test-Path $install) { & $install }
    } else { Write-Host 'Dotfiles already present; skipping' }
}

# Source EQ12 PowerShell profile if present
$eq12Profile = "$HOME/.dotfiles/powershell_profile.ps1"
if (Test-Path $eq12Profile) {
    Write-Host "Sourcing EQ12 PowerShell profile: $eq12Profile"
    . $eq12Profile
}

Write-Host "Post-create complete."