<#
PowerShell wrapper for eq12_chatgpt.py

Usage:
  .\eq12_chatgpt.ps1 -Prompt 'Hello world'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Prompt
)

function Invoke-EQ12ChatGPT {
    [CmdletBinding()]
    param([string]$Prompt)

    $venvPython = 'C:\EQ12\.venv\Scripts\python.exe'
    $systemPython = (Get-Command python -ErrorAction SilentlyContinue).Source
    $script = 'C:\EQ12\scripts\eq12_chatgpt.py'

    if (-not (Test-Path -Path $script)) {
        Write-Error "ChatGPT script not found at $script"
        return
    }

    if (Test-Path -Path $venvPython) {
        $python = $venvPython
    }
    elseif ($systemPython) {
        $python = $systemPython
    }
    else {
        Write-Error "No python executable found (looked for $venvPython and 'python' on PATH)."
        return
    }

    try {
        # Try to decrypt API key via gpg-encrypted file and set OPENAI_API_KEY for the subprocess
        $keysDir = 'C:\EQ12\keys'
        $encCandidates = @(Join-Path $keysDir 'openai_api.txt.gpg', Join-Path $keysDir 'openai.txt.gpg')
        $decrypted = $null
        foreach ($enc in $encCandidates) {
            if (Test-Path $enc) {
                try {
                    $decrypted = & gpg --quiet --batch --yes --decrypt $enc
                    break
                } catch {
                    Write-Host "gpg decrypt failed for $enc: $_"
                }
            }
        }

        if ($decrypted) {
            $env:OPENAI_API_KEY = $decrypted.Trim()
        }

        & $python $script --prompt $Prompt
    }
    catch {
        Write-Error "Execution failed: $_"
    }
}

Invoke-EQ12ChatGPT -Prompt $Prompt
