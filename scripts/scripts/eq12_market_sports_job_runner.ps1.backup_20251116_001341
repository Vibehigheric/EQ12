# eq12_market_sports_job_runner.ps1
param([switch]$Headless)
$ErrorActionPreference = "Continue"
$LogDir = "C:\EQ12\logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$SessionLog = Join-Path $LogDir ("elite_run_{0}.log" -f $ts)
function Write-Log($m) { $t=Get-Date -Format "yyyy-MM-dd HH:mm:ss"; "$t - $m" | Tee-Object -FilePath $SessionLog -Append }
function Retry-Exec($Cmd, $Name, $Retries=3, $Delay=5) {
  for ($i=1; $i -le $Retries; $i++) {
    try { Write-Log ("[{0}] Attempt {1}" -f $Name,$i); & $Cmd; Write-Log ("[{0}] OK" -f $Name); return $true }
    catch { Write-Log ("[{0}] FAIL {1}: {2}" -f $Name,$i,$_.Exception.Message); if ($i -lt $Retries) { Start-Sleep -Seconds $Delay } }
  }
  return $false
}
$Python = "C:\Program Files\Python312\python.exe"; if (-not (Test-Path $Python)) { $Python = "python" }
$head = $null; if ($Headless) { $head="--headless" }
$jobs = @(
  @{ n="stocks";  cmd={ & $Python "C:\EQ12\scripts\py\stocks.py"  $head | Tee-Object -FilePath (Join-Path $LogDir "stocks_out.txt") -Append } },
  @{ n="crypto";  cmd={ & $Python "C:\EQ12\scripts\py\crypto.py"  $head | Tee-Object -FilePath (Join-Path $LogDir "crypto_out.txt") -Append } },
  @{ n="sports";  cmd={ & $Python "C:\EQ12\scripts\py\sports.py"  $head | Tee-Object -FilePath (Join-Path $LogDir "sports_out.txt") -Append } },
  @{ n="jobs";    cmd={ & $Python "C:\EQ12\scripts\py\jobs_controltech.py" $head | Tee-Object -FilePath (Join-Path $LogDir "jobs_out.txt") -Append } }
)
$ok=0;$fail=0
foreach ($j in $jobs) { if (Retry-Exec $j.cmd $j.n 3 5) { $ok++ } else { $fail++ } }
try {
  Import-Module "C:\EQ12\scripts\eq12_recycle.psm1" -Force -ErrorAction SilentlyContinue
  $summary = "🚀 EQ12 Elite run finished.`nOK: {0}  FAIL: {1}`nLog: {2}" -f $ok,$fail,$SessionLog
  if (Get-Command Send-Telegram -ErrorAction SilentlyContinue) { Send-Telegram -Message $summary | Out-Null }
  Write-Log $summary
} catch { Write-Log "Telegram summary failed: $($_.Exception.Message)" }
Write-Log "Done."
