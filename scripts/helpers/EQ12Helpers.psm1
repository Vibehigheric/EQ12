<#
EQ12 patch
PowerShell helper module: re-export helpers and small utilities
#>
## EQ12 patch: dot-source local helper scripts so module exports are valid
$moduleDir = $PSScriptRoot

# Try to import PSScriptAnalyzer if available (helpful in CI/devcontainers)
try {
    Import-Module PSScriptAnalyzer -ErrorAction SilentlyContinue
} catch {
    Write-Verbose "PSScriptAnalyzer not available; skipping import"
}

# Dot-source helper scripts; fail gracefully if missing
$retry = Join-Path $moduleDir 'Retry-Exec.ps1'
if (Test-Path $retry) { . $retry } else { Write-Warning "Missing helper: $retry" }

$odds = Join-Path $moduleDir 'Ensure-OddsAPIKey.ps1'
if (Test-Path $odds) { . $odds } else { Write-Warning "Missing helper: $odds" }

function Get-EQ12LogsPath {
    [CmdletBinding()]
    param()

    $path = $env:EQ12_LOGS
    if ([string]::IsNullOrWhiteSpace($path)) {
        if ($IsWindows) { $path = 'C:\EQ12\logs' } else { $path = '/workspaces/EQ12/logs' }
    }

    if (-not (Test-Path $path)) {
        try { New-Item -Path $path -ItemType Directory -Force | Out-Null } catch { Write-Warning "Failed to create logs path $path: $_" }
    }
    return $path
}


function Set-EQ12Secret {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Value,
        [switch]$UseGpg
    )

    $secretsRoot = Join-Path (Split-Path -Path $PSScriptRoot -Parent) 'secrets'
    if (-not (Test-Path $secretsRoot)) { New-Item -Path $secretsRoot -ItemType Directory -Force | Out-Null }
    $file = Join-Path $secretsRoot ($Name + '.secret')

    if ($UseGpg) {
        $recipient = $env:EQ12_GPG_RECIPIENT
        if ([string]::IsNullOrWhiteSpace($recipient)) {
            Write-Warning "EQ12_GPG_RECIPIENT not set; cannot use GPG encryption. Use DPAPI on Windows instead."
            return
        }
        try {
            # Encrypt using gpg; write value to stdin
            $enc = "" | Out-Null
            $valueEscaped = $Value
            $cmd = "gpg --batch --yes --encrypt --recipient $recipient --output `"$file`""
            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = 'gpg'
            $psi.Arguments = "--batch --yes --encrypt --recipient $recipient --output `"$file`""
            $psi.RedirectStandardInput = $true
            $psi.UseShellExecute = $false
            $proc = [System.Diagnostics.Process]::Start($psi)
            $proc.StandardInput.Write($Value)
            $proc.StandardInput.Close()
            $proc.WaitForExit()
            if ($proc.ExitCode -ne 0) { Write-Warning "gpg exit code $($proc.ExitCode) while encrypting secret" }
        } catch {
            Write-Warning "Failed to encrypt secret with gpg: $_"
        }
    } else {
        # Use DPAPI on Windows (ProtectedData). On non-Windows, fall back to plain text with a warning.
        if ($IsWindows) {
            try {
                $bytes = [System.Text.Encoding]::UTF8.GetBytes($Value)
                $encBytes = [System.Security.Cryptography.ProtectedData]::Protect($bytes, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
                [System.IO.File]::WriteAllBytes($file, $encBytes)
            } catch {
                Write-Warning "Failed to protect secret with DPAPI: $_"
            }
        } else {
            Write-Warning "DPAPI not available on this platform; storing secret in plaintext at $file"
            try { Set-Content -Path $file -Value $Value -Encoding UTF8 -Force } catch { Write-Warning "Failed to write secret: $_" }
        }
    }
}


function Get-EQ12Secret {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [switch]$UseGpg
    )

    $secretsRoot = Join-Path (Split-Path -Path $PSScriptRoot -Parent) 'secrets'
    $file = Join-Path $secretsRoot ($Name + '.secret')
    if (-not (Test-Path $file)) { return $null }

    if ($UseGpg) {
        try {
            $psi = New-Object System.Diagnostics.ProcessStartInfo
            $psi.FileName = 'gpg'
            $psi.Arguments = "--batch --yes --decrypt `"$file`""
            $psi.RedirectStandardOutput = $true
            $psi.UseShellExecute = $false
            $proc = [System.Diagnostics.Process]::Start($psi)
            $out = $proc.StandardOutput.ReadToEnd()
            $proc.WaitForExit()
            if ($proc.ExitCode -ne 0) { Write-Warning "gpg exit code $($proc.ExitCode) while decrypting secret" }
            return $out
        } catch {
            Write-Warning "Failed to decrypt secret with gpg: $_"
            return $null
        }
    } else {
        if ($IsWindows) {
            try {
                $enc = [System.IO.File]::ReadAllBytes($file)
                $decBytes = [System.Security.Cryptography.ProtectedData]::Unprotect($enc, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
                return [System.Text.Encoding]::UTF8.GetString($decBytes)
            } catch {
                Write-Warning "Failed to unprotect secret: $_"
                return $null
            }
        } else {
            try { return Get-Content -Path $file -Raw -ErrorAction Stop } catch { Write-Warning "Failed to read secret: $_"; return $null }
        }
    }
}

# Export public functions
Export-ModuleMember -Function Invoke-Eq12Retry, Get-CachedOddsApiKey, Get-EQ12LogsPath, Set-EQ12Secret, Get-EQ12Secret
