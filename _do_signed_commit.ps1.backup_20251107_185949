<#
EQ12 patch
Signed commit helper: stage all, commit -S, and show signature
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$Message = 'chore: signed commit via helper',
    [switch]$Amend
)

Write-Host "Adding files to index..."
git add -A

if ($Amend) {
    Write-Host "Amending last commit with signed change: $Message"
    git commit --amend -S -m $Message
} else {
    Write-Host "Creating signed commit: $Message"
    # Use --gpg-sign to ensure gpg.program is used
    git commit -S -m $Message --allow-empty
}

Write-Host "Verifying last commit signature..."
git --no-pager log --show-signature -1

Write-Host "Helper finished."