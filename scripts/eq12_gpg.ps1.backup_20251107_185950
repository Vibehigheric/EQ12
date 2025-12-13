<#
eq12_gpg.ps1
PowerShell wrappers around GPG/Kleopatra for the EQ12 stack.
Provides functions:
 - Protect-EQ12Log - encrypt and/or clearsign a file for a recipient
 - Unprotect-EQ12Log - decrypt and/or verify a file
 - Sign-EQ12File - clearsign a file
 - Verify-EQ12Sig - verify a clearsigned file

These functions call the `gpg` CLI (Gpg4win/Kleopatra must be installed and gpg.exe on PATH).
#>

function Get-GpgPath {
    $gpg = Get-Command gpg.exe -ErrorAction SilentlyContinue
    if ($gpg) { return $gpg.Source }
    # Try common Gpg4win path
    $possible = "$env:ProgramFiles\GnuPG\bin\gpg.exe"
    if (Test-Path $possible) { return $possible }
    Write-Error "gpg.exe not found. Install Gpg4win/Kleopatra and ensure gpg.exe is on PATH."
    return $null
}

function Protect-EQ12Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [string]$Recipient,
        [switch]$Encrypt,
        [switch]$Sign,
        [switch]$Armor
    )
    $gpg = Get-GpgPath
    if (-not $gpg) { return $false }
    if (-not (Test-Path $Path)) { Write-Error "File not found: $Path"; return $false }

    $out = $Path
    if ($Encrypt) { $out = "$Path.gpg" }
    if ($Sign -and -not $Encrypt) { $out = "$Path.asc" }

    $gpgArgs = @()
    if ($Encrypt) {
        if (-not $Recipient) { Write-Error "Recipient is required for encryption"; return $false }
    $gpgArgs += "--encrypt"; $gpgArgs += "--recipient"; $gpgArgs += $Recipient
    }
    if ($Sign) {
        if ($Encrypt) { $gpgArgs += "--sign" } else { $gpgArgs += "--clearsign" }
    }
    if ($Armor) { $gpgArgs += "--armor" }
    $gpgArgs += "--output"; $gpgArgs += $out; $gpgArgs += $Path

    & $gpg @gpgArgs
    if ($LASTEXITCODE -ne 0) { Write-Error "gpg failed with code $LASTEXITCODE"; return $false }
    Write-Host "Wrote: $out"
    return $true
}

function Unprotect-EQ12Log {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [string]$Output
    )
    $gpg = Get-GpgPath
    if (-not $gpg) { return $false }
    if (-not (Test-Path $Path)) { Write-Error "File not found: $Path"; return $false }

    if (-not $Output) {
        $Output = if ($Path -like '*.gpg') { $Path -replace '\.gpg$','' } elseif ($Path -like '*.asc') { $Path -replace '\.asc$','' } else { "$Path.decrypted" }
    }

    # Try decryption first; if file is clearsigned, decrypt will write text
    & $gpg --yes --output $Output --decrypt $Path
    if ($LASTEXITCODE -ne 0) {
        Write-Error "gpg decrypt/verify failed with code $LASTEXITCODE"; return $false
    }
    Write-Host "Wrote: $Output"
    return $true
}

function New-EQ12Signature {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [switch]$Armor
    )
    $gpg = Get-GpgPath
    if (-not $gpg) { return $false }
    if (-not (Test-Path $Path)) { Write-Error "File not found: $Path"; return $false }
    $out = "$Path.asc"
    $gpgArgs = @("--clearsign","--output",$out,$Path)
    if ($Armor) { $gpgArgs = @("--armor") + $gpgArgs }
    & $gpg @gpgArgs
    if ($LASTEXITCODE -ne 0) { Write-Error "gpg failed with code $LASTEXITCODE"; return $false }
    Write-Host "Created clearsigned file: $out"
    return $true
}

function Test-EQ12Signature {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$Path
    )
    $gpg = Get-GpgPath
    if (-not $gpg) { return $false }
    if (-not (Test-Path $Path)) { Write-Error "File not found: $Path"; return $false }
    & $gpg --verify $Path
    $code = $LASTEXITCODE
    if ($code -ne 0) { Write-Error "gpg verify failed with code $code"; return $false }
    Write-Host "Signature verified for $Path"
    return $true
}

# Backwards-compatible aliases for older names
Set-Alias -Name Sign-EQ12File -Value New-EQ12Signature -Scope Global -ErrorAction SilentlyContinue
Set-Alias -Name Verify-EQ12Sig -Value Test-EQ12Signature -Scope Global -ErrorAction SilentlyContinue

Export-ModuleMember -Function Protect-EQ12Log,Unprotect-EQ12Log,New-EQ12Signature,Test-EQ12Signature,Get-GpgPath
