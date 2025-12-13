# ====================================================
# EQ12 UTF-8 + PARAM BLOCK SANITY GUARD (HARDENED)
# ====================================================
# Include this at the TOP of every EQ12 PowerShell script

# Force guaranteed UTF-8 output
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Prevent NoProfile from removing encoding behaviors
$PSDefaultParameterValues['Out-File:Encoding'] = 'UTF8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'UTF8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'UTF8'

# Auto-clean the current script of dangerous characters
if ($MyInvocation.MyCommand.Path) {
    $script = $MyInvocation.MyCommand.Path
    $raw = Get-Content -Raw $script -ErrorAction SilentlyContinue

    if ($raw) {
        $clean = $raw -replace '[^\x00-\x7F]', '' `
                      -replace '[""'']', '"' `
                      -replace '[]', '-' `
                      -replace '[]', '' `
                      -replace '[\u2018\u2019]', "'" `
                      -replace '[\u201C\u201D]', '"'

        if ($raw -ne $clean) {
            Write-Host "Unicode corruption detected. Auto-repairing script..." -ForegroundColor Yellow
            Set-Content -Path $script -Value $clean -Encoding UTF8
        }
    }
}

# Set environment variables for UTF-8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:LC_ALL = "C.UTF-8"
$env:LANG = "C.UTF-8"
