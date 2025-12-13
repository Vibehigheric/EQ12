<#
.SYNOPSIS
Generate an ed25519 SSH key, add it to the ssh-agent, and print the public key.

.DESCRIPTION
Safe helper for Windows PowerShell. By default it creates ~/.ssh/id_ed25519 unless a different path is provided.
It will not overwrite an existing key unless -Force is used. Optionally upload the public key to GitHub using the GitHub CLI (`gh`) if -UploadWithGh is supplied.

USAGE
.
    .\generate_and_add_ssh_key.ps1 [-KeyPath <string>] [-Force] [-UploadWithGh] [-Title <string>]

#>
[CmdletBinding()]
param(
    [string]$KeyPath = "$env:USERPROFILE\\.ssh\\id_ed25519",
    [switch]$Force,
    [switch]$UploadWithGh,
    [string]$Title = "EQ12 key $(Get-Date -Format yyyy-MM-dd)"
)

function Write-Log($msg) { Write-Output $msg }

# Ensure .ssh directory exists
$sshDir = Split-Path -Parent $KeyPath
if (-not (Test-Path $sshDir)) { New-Item -ItemType Directory -Path $sshDir -Force | Out-Null }

# Generate key if not exists or --Force
if ((Test-Path $KeyPath) -and -not $Force) {
    Write-Log "Key already exists at $KeyPath (use -Force to overwrite)."
} else {
    if (Test-Path $KeyPath) { Remove-Item $KeyPath -Force -ErrorAction SilentlyContinue; Remove-Item "$KeyPath.pub" -Force -ErrorAction SilentlyContinue }
    # Use ssh-keygen (should be available with Git for Windows / OpenSSH)
    Write-Log "Generating new ed25519 key: $KeyPath"
    # Prefer invoking ssh-keygen directly
    if (-not (Get-Command -Name 'ssh-keygen' -ErrorAction SilentlyContinue)) {
        Write-Log 'ssh-keygen not found on PATH. Install Git for Windows or OpenSSH client.'
        Exit 1
    }
    try {
        # Build comment separately to avoid parsing issues with '@'
        $comment = "$($env:USERNAME)@$($env:COMPUTERNAME)"
        $args = @('-t','ed25519','-C',$comment,'-f',$KeyPath,'-N','""')
        & ssh-keygen @args
        if ($LASTEXITCODE -ne 0) { Write-Log "ssh-keygen exited with code $LASTEXITCODE"; Exit 1 }
    } catch {
    Write-Log ("Failed to run ssh-keygen: {0}" -f $_.Exception.Message); Exit 1
    }
}

# Start ssh-agent service (Windows)
try {
    if (-not (Get-Service -Name ssh-agent -ErrorAction SilentlyContinue)) {
        Write-Log 'OpenSSH ssh-agent service not found; make sure OpenSSH is installed.'
    } else {
        $svc = Get-Service -Name ssh-agent
        if ($svc.Status -ne 'Running') { Start-Service ssh-agent }
    }
} catch {
    Write-Log ("Could not start ssh-agent: {0}" -f $_.Exception.Message)
}

# Add key to agent
try {
    ssh-add $KeyPath | Out-Null
    Write-Log "Added private key to ssh-agent: $KeyPath"
} catch {
    Write-Log ("ssh-add failed: {0}" -f $_.Exception.Message)
}

# Print public key
$pubPath = "$KeyPath.pub"
if (Test-Path $pubPath) {
    Write-Log "Public key path: $pubPath"
    Write-Log "---BEGIN PUBLIC KEY---"
    Get-Content $pubPath -Raw
    Write-Log "---END PUBLIC KEY---"
} else {
    Write-Log "Public key not found at $pubPath"
}

# Optionally upload with gh
if ($UploadWithGh) {
    if (-not (Get-Command -Name 'gh' -ErrorAction SilentlyContinue)) {
        Write-Log 'gh CLI not found on PATH. Install and authenticate (gh auth login) to use -UploadWithGh.'
    } else {
        try {
            gh ssh-key add $pubPath --title "$Title"
            Write-Log 'Uploaded public key to GitHub via gh.'
        } catch {
            Write-Log ("gh upload failed: {0}" -f $_.Exception.Message)
        }
    }
}
