<#
Fix and clean PATH environment variable (user, and machine if run as admin),
append common program paths and C:\EQ12\scripts, then ensure gpg is available.
If no secret key exists for the provided email, generate a batch-mode GPG key.

Safe and conservative: we only REMOVE PATH entries that do not exist on disk.
We add a short whitelist of well-known install locations if missing.

Usage: Run in PowerShell (non-destructive). To update the MACHINE path, open an elevated PowerShell and re-run.
#>
[CmdletBinding()]
param(
    [string]$Name = 'Ricoj100',
    [string]$Email = 'ricoj100@example.com',
    [switch]$ForceGenerateGpg  # if set, generate GPG key even if one exists for the email
)

function Write-Log($m){ Write-Host "[fix_path] $m" }

function Is-Admin {
    $id = [System.Security.Principal.WindowsIdentity]::GetCurrent()
    $p = New-Object System.Security.Principal.WindowsPrincipal($id)
    return $p.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Known good paths to ensure are present (don't overwrite existing values)
$knownPaths = @(
    'C:\Program Files\Git\cmd',
    'C:\Program Files (x86)\GnuPG\bin',
    'C:\Windows\System32\OpenSSH',
    'C:\Program Files\Microsoft VS Code\bin',
    'C:\Program Files\dotnet',
    'C:\EQ12\scripts'
)

function Clean-PathString([string]$pathString){
    if (-not $pathString) { return @() }
    $parts = $pathString -split ';' | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }
    # Keep only entries that are absolute paths and exist on disk OR that look like valid paths (abs) so we don't lose useful values
    $kept = @()
    foreach ($p in $parts){
        # ignore entries that are clearly fragments without a colon (like "Program")
        if ($p -notmatch '^[A-Za-z]:\\'){
            Write-Log "Dropping non-absolute PATH entry: '$p'"
            continue
        }
        if (Test-Path $p){
            $kept += $p
        } else {
            Write-Log "Dropping non-existing PATH entry: '$p'"
        }
    }
    # deduplicate while preserving order
    $seen = @{}
    $result = @()
    foreach ($e in $kept){ if (-not $seen.ContainsKey($e.ToLower())){ $seen[$e.ToLower()] = $true; $result += $e } }
    return $result
}

Write-Log "Starting PATH cleanup (User + Machine if elevated). IsAdmin=$(Is-Admin)"

$userPath = [Environment]::GetEnvironmentVariable('Path','User')
$machinePath = [Environment]::GetEnvironmentVariable('Path','Machine')

Write-Log "Reading current User PATH entries..."
$userEntries = Clean-PathString $userPath
Write-Log "Reading current Machine PATH entries..."
$machineEntries = Clean-PathString $machinePath

# Ensure knownPaths are present (if the path exists on disk, append; if not present but in knownPaths append anyway so user can install later)
foreach ($kp in $knownPaths){
    if (-not ($userEntries -contains $kp) -and -not ($machineEntries -contains $kp)){
        # prefer adding to User PATH
        Write-Log "Adding known path to User PATH: $kp"
        $userEntries += $kp
    }
}

# Build new PATH strings
$newUserPath = ($userEntries -join ';')
$newMachinePath = ($machineEntries -join ';')

# Apply User PATH always
try{
    [Environment]::SetEnvironmentVariable('Path',$newUserPath,'User')
    Write-Log "User PATH updated. Please open a new shell to pick up changes."
} catch {
    Write-Log "Failed to set User PATH: $_"
}

# Optionally update machine PATH if elevated
if (Is-Admin){
    try{
        [Environment]::SetEnvironmentVariable('Path',$newMachinePath,'Machine')
        Write-Log "Machine PATH updated (running as admin)."
    } catch {
        Write-Log "Failed to set Machine PATH: $_"
    }
} else {
    Write-Log "Not running elevated; Machine PATH left unchanged. Re-run elevated to update Machine PATH."
}

# Refresh current process PATH variable so subsequent commands in this session see changes
$env:PATH = ([Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')).Trim(';')
Write-Log "Session PATH refreshed."

# Show a short diagnostics listing for key tools
Write-Log "Tool diagnostics (where.exe):"
try{ where.exe git 2>$null | ForEach-Object { Write-Log "git -> $_" } } catch {}
try{ where.exe gpg 2>$null | ForEach-Object { Write-Log "gpg -> $_" } } catch {}
try{ where.exe gh 2>$null | ForEach-Object { Write-Log "gh -> $_" } } catch {}

# If gpg is not present in PATH now, but the typical install folder exists, add it to the session PATH
if (-not (Get-Command gpg -ErrorAction SilentlyContinue)){
    $maybe = 'C:\Program Files (x86)\GnuPG\bin'
    if (Test-Path "$maybe\gpg.exe"){
        Write-Log "Found gpg at $maybe; adding to session PATH"
        $env:PATH = "$maybe;" + $env:PATH
    } else {
        Write-Log "gpg not found on PATH and not found at $maybe. Install Gpg4win if needed."
    }
}

# Check for existing secret key by email
$existing = & gpg --list-secret-keys --keyid-format LONG $Email 2>$null
if ($existing -and -not $ForceGenerateGpg){
    Write-Log "Found existing secret key for $Email. Skipping generation."
    Write-Log $existing
    exit 0
}

# Generate GPG key non-interactively
Write-Log "No secret key found for $Email (or ForceGenerateGpg set). Generating new key..."
$gpgBatch = @"
Key-Type: RSA
Key-Length: 4096
Name-Real: $Name
Name-Email: $Email
Expire-Date: 0
%commit
"@

$temp = Join-Path $env:TEMP "gpg_batch_$(Get-Random).txt"
# Normalize newlines and write ASCII
$gpgBatchNormalized = $gpgBatch -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($temp,$gpgBatchNormalized,[System.Text.Encoding]::ASCII)
Write-Log "Written batch file to $temp"

# Invoke gpg
try{
    & gpg --batch --generate-key $temp 2>&1 | ForEach-Object { Write-Log "gpg: $_" }
} catch {
    Write-Log "gpg invocation failed: $_"
}

# Confirm key created
$pubs = & gpg --list-secret-keys --keyid-format LONG $Email 2>$null
if (-not $pubs){
    Write-Log 'Failed to find newly created key'
    exit 2
}

# Parse the key ID
$keyLine = ($pubs -split "`n" | Where-Object { $_ -match '^sec\s' } | Select-Object -First 1)
if ($keyLine -match '/([0-9A-F]{16})') { $keyId = $matches[1] } else { Write-Log 'Could not extract key id'; exit 3 }
Write-Log "Generated key ID: $keyId"

# Export public key
$outPath = Join-Path $env:USERPROFILE ".ssh\gpg_public_$keyId.asc"
& gpg --armor --export $keyId | Out-File -FilePath $outPath -Encoding ascii
Write-Log "Public key exported to: $outPath"
Write-Log "To upload: open GitHub > Settings > SSH and GPG keys > New GPG key and paste contents of $outPath"

# Finished
Remove-Item $temp -ErrorAction SilentlyContinue
Write-Log "Done. If you updated Machine PATH, open a new elevated shell to see changes."
