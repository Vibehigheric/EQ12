<# EQ12 patch: user profile for PowerShell in Codespaces/Windows #>
Import-Module "$env:HOME/.local/share/eq12/helpers/EQ12Helpers.psm1" -ErrorAction SilentlyContinue

# Load Retry helper if available
if (Get-Command Invoke-Eq12Retry -ErrorAction SilentlyContinue) {
    Write-Verbose 'EQ12: Retry helper loaded'
}

# Ensure GNUPGHOME is exported for the session
if (-not $env:GNUPGHOME) {
    $env:GNUPGHOME = Join-Path $env:APPDATA 'gnupg'
}

# TODO: add Pester test