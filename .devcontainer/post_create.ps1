# EQ12 patch: Codespaces bootstrap
$ErrorActionPreference = "Stop"

# Ensure logs dir
$logs = "/workspaces/EQ12/logs"
if (-not (Test-Path $logs)) { New-Item -ItemType Directory -Path $logs | Out-Null }

# Install Python deps
if (Test-Path "requirements.txt") {
    python -m pip install -r requirements.txt
}

# Playwright install
try { playwright install --with-deps } catch { Write-Warning "Playwright not installed." }

# Dotfiles
if ($env:DOTFILES_REPO) {
    git clone $env:DOTFILES_REPO ~/.dotfiles
    if (Test-Path "~/.dotfiles/install.ps1") { pwsh ~/.dotfiles/install.ps1 }
}
[CmdletBinding()]
param()

Write-Host "Running devcontainer post-create actions: installing pip requirements and enabling git/gpg settings"

# Install Python requirements if present
$req = Join-Path $PSScriptRoot '..\requirements.txt'
if (Test-Path $req) {
    Write-Host "Installing Python requirements from $req"
    pip install -r $req
}

# Source PowerShell profile if exists
$profilePath = "$env:HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
if (Test-Path $profilePath) {
    Write-Host "Sourcing PowerShell profile: $profilePath"
    . $profilePath
}

# Ensure GNUPGHOME exists
if (-not (Test-Path $env:GNUPGHOME)) {
    Write-Host "Creating GNUPGHOME at $env:GNUPGHOME"
    New-Item -ItemType Directory -Path $env:GNUPGHOME -Force | Out-Null
}

# If the repo contains bookmarks, copy them into the container workspace and run a dry-run
$repoBookmarks = Join-Path $PSScriptRoot '..\..\configs\bookmarks.json'
if (Test-Path $repoBookmarks) {
    Write-Host "Found repository bookmarks.json at $repoBookmarks; copying into container workspace"
    $containerConfigs = '/workspaces/eq12/configs'
    New-Item -ItemType Directory -Path $containerConfigs -Force | Out-Null
    Copy-Item -Path $repoBookmarks -Destination (Join-Path $containerConfigs 'bookmarks.json') -Force
    # Attempt to run the Python helper in dry-run to surface what would be applied
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host "Running bookmarks dry-run with python"
        python scripts/eq12_firefox_bookmarks.py --bookmarks $containerConfigs/bookmarks.json
    } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
        Write-Host "Running bookmarks dry-run with python3"
        python3 scripts/eq12_firefox_bookmarks.py --bookmarks $containerConfigs/bookmarks.json
    } else {
        Write-Host "Python not found; skipping bookmarks dry-run"
    }
}

# If ngrok auth token is present in env, attempt to install ngrok CLI and configure it
if ($env:NGROK_AUTHTOKEN) {
    Write-Host "NGROK_AUTHTOKEN detected; installing/configuring ngrok"
    $ngrokUrl = 'https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip'
    $zip = Join-Path $PSScriptRoot 'ngrok.zip'
    Invoke-WebRequest -Uri $ngrokUrl -OutFile $zip -UseBasicParsing -ErrorAction SilentlyContinue
    if (Test-Path $zip) {
        Expand-Archive -Path $zip -DestinationPath $PSScriptRoot -Force
        Remove-Item $zip -Force
        Write-Host "ngrok downloaded to $PSScriptRoot"
        # configure authtoken
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Write-Host "Configuring ngrok authtoken"
            & "$PSScriptRoot/ngrok" authtoken $env:NGROK_AUTHTOKEN
        } else {
            Write-Host "ngrok installed but not configuring (missing runtime to run ngrok)"
        }
    } else {
        Write-Warning "Failed to download ngrok from $ngrokUrl"
    }
}

Write-Host "Post-create complete."