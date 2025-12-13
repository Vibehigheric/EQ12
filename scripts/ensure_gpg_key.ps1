<#
ensure_gpg_key.ps1
Checks that a GPG key with the given fingerprint exists in the local keyring.
If missing and an import file is provided, attempts to import it.
#>
param(
    [Parameter(Mandatory=$true)][string]$Fingerprint,
    [string]$ImportFile
)

$gpg = Get-Command gpg.exe -ErrorAction SilentlyContinue
if (-not $gpg) { Write-Error "gpg.exe not found. Install Gpg4win/Kleopatra."; exit 2 }

$found = & gpg --list-secret-keys --with-colons | Select-String $Fingerprint -Quiet
if ($found) { Write-Host "GPG key $Fingerprint found."; exit 0 }

if ($ImportFile) {
    if (-not (Test-Path $ImportFile)) { Write-Error "Import file not found: $ImportFile"; exit 3 }
    Write-Host "Importing key from $ImportFile"
    & gpg --import $ImportFile
    if ($LASTEXITCODE -ne 0) { Write-Error "gpg import failed"; exit 4 }
    Write-Host "Imported. Please verify in Kleopatra."
    exit 0
}

Write-Error "GPG key $Fingerprint not found. Provide an --ImportFile to import or create the key in Kleopatra."; exit 1
