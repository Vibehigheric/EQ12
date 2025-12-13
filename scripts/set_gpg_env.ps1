<#
Set GNUPGHOME permanently for the current user and configure git to use the bundled gpg program.
Run this in PowerShell once (non-elevated). To update the machine PATH or machine git config, run elevated.
#>
param(
    [string]$GpgPath = 'C:\Program Files (x86)\GnuPG\bin\gpg.exe'
)
function Write-Log($m){ Write-Host "[set-gpg] $m" }

if (-not (Test-Path $GpgPath)){
    Write-Log "gpg not found at $GpgPath. Please install Gpg4win or set -GpgPath to the correct location."; exit 1
}

# Persist GNUPGHOME to user environment
$gnupg = Join-Path $HOME '.gnupg'
if (-not (Test-Path $gnupg)){
    Write-Log "Creating GNUPGHOME directory: $gnupg"
    New-Item -ItemType Directory -Path $gnupg -Force | Out-Null
}
[Environment]::SetEnvironmentVariable('GNUPGHOME',$gnupg,'User')
$env:GNUPGHOME = $gnupg
Write-Log "Set GNUPGHOME to $gnupg"

# Configure git to use this gpg binary
git config --global gpg.program "${GpgPath}"
Write-Log "git global gpg.program set to ${GpgPath}"

Write-Log "Done. Open a new PowerShell session to pick up the changed user env if needed."
