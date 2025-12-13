<#
.SYNOPSIS
Generate or import a GPG key for commit signing and prepare instructions to add it to GitHub.

.DESCRIPTION
This helper checks for `gpg` on PATH. If present, it prompts for a name/email and generates a key (RSA 4096 by default).
It exports the public key to a file and prints the commands to upload it to GitHub (via UI or gh) and to configure git to use it for commit signing.

USAGE
    .\generate_and_add_gpg_key.ps1 [-Name <string>] [-Email <string>] [-NoInteract]

#>
[CmdletBinding()]
param(
    [string]$Name = $env:USERNAME,
    [string]$Email = "",
    [switch]$NoInteract
)

function Write-Log($m) { Write-Output $m }

# Check for gpg
if (-not (Get-Command -Name gpg -ErrorAction SilentlyContinue)) {
    Write-Log 'gpg not found on PATH. Please install GPG (GnuPG) and try again. See: https://www.gnupg.org/download/'
    Exit 1
}

if (-not $Email -and -not $NoInteract) {
    $Email = Read-Host 'Email for GPG key (used for Git commit signing)'
}

if (-not $Email) { Write-Log 'Email is required.'; Exit 1 }

# Prepare batch input for gpg --batch key generation
$gpgBatch = @"
Key-Type: RSA
Key-Length: 4096
Name-Real: $Name
Name-Email: $Email
Expire-Date: 0
%commit
"@

# Write batch file to temp
$temp = Join-Path $env:TEMP "gpg_batch_$(Get-Random).txt"
# Write batch file without BOM and with LF endings to satisfy gpg --batch parser
# Normalize to LF only (remove CR) and write ASCII without BOM
$gpgBatchNormalized = $gpgBatch -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($temp, $gpgBatchNormalized, [System.Text.Encoding]::ASCII)

Write-Log "Generating GPG key for $Name <$Email> (this may take a moment)..."
& gpg --batch --generate-key $temp

# get the key id
$pubs = & gpg --list-secret-keys --keyid-format LONG $Email 2>$null
if (-not $pubs) { Write-Log 'Failed to find newly created key'; Exit 1 }

# Parse the key ID from output (search for sec line)
$keyLine = ($pubs -split "`n" | Where-Object { $_ -match '^sec\s' } | Select-Object -First 1)
if (-not $keyLine) { Write-Log 'Could not parse key id'; Exit 1 }
# Example sec line: sec   rsa4096/AAAAAAAAAAAAAAAA 2025-09-20 [SC]
if ($keyLine -match '/([0-9A-F]{16})') { $keyId = $matches[1] } else { Write-Log 'Could not extract key id'; Exit 1 }

Write-Log "Generated key ID: $keyId"

# Export public key to file
$outPath = Join-Path $env:USERPROFILE ".ssh\gpg_public_$keyId.asc"
& gpg --armor --export $keyId | Out-File -FilePath $outPath -Encoding ascii
Write-Log "Public key exported to: $outPath"

Write-Log "Public key (copy this into GitHub -> Settings -> SSH and GPG keys -> New GPG key):"
Get-Content $outPath -Raw

# Git config instructions
Write-Log "Configure git to use the key for signing (global):"
Write-Log "git config --global user.signingkey $keyId"
Write-Log "git config --global commit.gpgSign true"

# gh upload hint
if (Get-Command -Name gh -ErrorAction SilentlyContinue) {
    Write-Log "You can upload the GPG key with gh (if authenticated):"
    Write-Log "gh gpg-key add $outPath"
} else {
    Write-Log "To upload, open GitHub -> Settings -> SSH and GPG keys -> New GPG key and paste the public key above."
}

# clean temp
Remove-Item $temp -Force -ErrorAction SilentlyContinue
