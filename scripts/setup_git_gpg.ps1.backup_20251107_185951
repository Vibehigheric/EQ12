<#
Script: setup_git_gpg.ps1
Purpose: Configure git global settings for user, enable commit signing, and persist GNUPGHOME.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$UserName = "Ricoj100",
    [Parameter(Mandatory=$false)]
    [string]$UserEmail = "ricoj100@example.com",
    [Parameter(Mandatory=$false)]
    [string]$GpgProgram = 'C:\Program Files (x86)\GnuPG\bin\gpg.exe',
    [Parameter(Mandatory=$false)]
    [string]$GnupgHome = 'C:\Users\Ricoj100\AppData\Roaming\gnupg'
)

Write-Host "Configuring git global user.name and user.email..."
git config --global user.name "$UserName"
git config --global user.email "$UserEmail"

Write-Host "Setting git to sign commits and setting gpg.program to $GpgProgram"
git config --global commit.gpgsign true
git config --global gpg.program "${GpgProgram}"

# Persist GNUPGHOME in user environment if not set
$current = [Environment]::GetEnvironmentVariable('GNUPGHOME', 'User')
if ([string]::IsNullOrEmpty($current)) {
    Write-Host "Setting user environment GNUPGHOME to $GnupgHome"
    [Environment]::SetEnvironmentVariable('GNUPGHOME', $GnupgHome, 'User')
} else {
    Write-Host "User environment GNUPGHOME already set to: $current"
}

Write-Host "Done. Please restart your PowerShell session for GNUPGHOME to take effect in current shells."