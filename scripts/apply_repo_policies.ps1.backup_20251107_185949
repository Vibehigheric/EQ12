[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$RepoPath = (Get-Location).Path,
    [Parameter(Mandatory=$false)]
    [string]$UserName = 'Ricoj100',
    [Parameter(Mandatory=$false)]
    [string]$UserEmail = 'ricoj100@example.com',
    [Parameter(Mandatory=$false)]
    [string]$GpgProgram = 'C:\Program Files (x86)\GnuPG\bin\gpg.exe',
    [Parameter(Mandatory=$false)]
    [switch]$VerboseOutput
)

if (-not (Test-Path $RepoPath)) { Throw "Repo path $RepoPath does not exist" }

Push-Location $RepoPath
try {
    if (-not (Test-Path .git)) {
        Write-Warning "$RepoPath is not a git repository (no .git); skipping"
        return
    }

    Write-Host "Applying repo-local git config in $RepoPath"
    git config user.name "$UserName"
    git config user.email "$UserEmail"
    git config commit.gpgsign true
    git config gpg.program "${GpgProgram}"

    if ($VerboseOutput) {
        git config --list --local
    }
} finally {
    Pop-Location
}

Write-Host "Repository policies applied."