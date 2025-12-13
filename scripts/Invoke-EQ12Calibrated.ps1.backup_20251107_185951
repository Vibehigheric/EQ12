[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$Prompt,
  [string]$Truth = "",
  [string]$Model = "gpt-5-mini"
)

function Invoke-EQ12Calibrated {
  [CmdletBinding()]
  param([string]$Prompt,[string]$Truth,[string]$Model)

  $py = Join-Path $PSScriptRoot "eq12_ai_guardrails.py"
  $venv = "C:\EQ12\.venv\Scripts\python.exe"
  if (Test-Path $venv) { $python = $venv } else { $python = "python" }

  $pyArgs = @("--prompt", $Prompt, "--model", $Model)
  if ($Truth) { $pyArgs += @("--truth", $Truth) }

  $out = & $python $py $pyArgs 2>&1
  if ($LASTEXITCODE -ne 0) {
    Write-Error "Calibrated run failed: $out"
    return
  }
  $out | Write-Output
}

Invoke-EQ12Calibrated -Prompt $Prompt -Truth $Truth -Model $Model
