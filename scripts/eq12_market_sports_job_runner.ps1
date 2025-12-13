# EQ12 Elite Copilot Master Prompt
#
# You are an **expert automation + PowerShell/Python engineer**.
# You are working on the EQ12 Elite Stack (stocks, crypto, sports, jobs, recycle, dashboard).
#
# ALWAYS DO:
# - Mirror Crypto JSON exporter pattern across all modules.
# - Fix issues globally — if you patch one (stocks), also patch others (crypto, jobs, recycle, sports).
# - Dashboard = C:\EQ12\dashboard\index.html → always table-based, consistent format.
# - Add JSON exporters (# TODO: export this as JSON for dashboard).
# - Add pytest unit tests (# TODO: add pytest unit test for JSON schema).
# - For PowerShell:
#   - Use CmdletBinding() and Verb-Noun names (e.g., Get-EQ12Status).
#   - Wrap errors with try/catch, log to C:\EQ12\logs.
# - For Python:
#   - Always output valid JSON + CSV.
#   - Handle API keys (ODDS_API_KEY, Coinbase, yfinance).
# - Hard-code $env:ODDS_API_KEY read from C:\EQ12\keys\oddsapi.txt.
#
# CHAIN PROMPTS:
# 1. Write base function
# 2. Add JSON export
# 3. Add pytest schema unit test
# 4. Rewrite in PowerShell style if PS1/PSM1
# 5. Add dashboard integration (table row builder)
#
# EXAMPLES:
# - Stocks: JSON like Crypto, includes EMA20, EMA50, RSI14, MOM5, signal.
# - Sports: Use Odds API → log odds_{sport}.json.
# - Jobs: Log to jobs_controltech.json.
# - Recycle: Export to recycle_report.json.
#
# LOGGING:
# - C:\EQ12\logs\elite_run_*.log for elite run.
# - Each module logs its JSON.
# - Dashboard builds tables from JSON logs.
#
# WATCHDOG:
# - eq12-watchdog.ps1 runs hourly:
#   - eq12-elite-run
#   - eq12-build-dashboard
#   - Telegram alert if FAIL > 0.
#
# ---
#
# ⚡ Copilot: ALWAYS treat this file as law.
# ⚡ No silent failures.
# ⚡ No $null paths.
# ⚡ Apply fixes consistently across all modules.

# === EQ12 Copilot Master Patch ===
# Apply these rules across all EQ12 scripts:
#
# 1. Runner Stability
#    - Define Retry-Exec BEFORE any calls.
#    - Replace invalid Write-Host interpolations:
#         ("[{0}] FAIL {1}: {2}" -f $Name, $i, $_.Exception.Message)
#    - Ensure $ok/$fail counters increment and final summary always logs.
#
# 2. Dashboard Build
#    - Always set $dashboardDir = "C:\EQ12\dashboard" and create if missing.
#    - Define $html = Join-Path $dashboardDir "index.html".
#    - Pre-seed HTML with <html><body> wrapper, close with </body></html>.
#    - Use Add-Content -Path $html (not $html as variable only).
#    - Auto-launch dashboard: Start-Process $html.
#
# 3. Odds API Integration
#    - Ensure $env:ODDS_API_KEY loads from C:\EQ12\keys\oddsapi.txt.
#    - If missing, prompt once, save, and reuse.
#    - In sports.py and PowerShell, always call https://api.the-odds-api.com with apiKey=$env:ODDS_API_KEY.
#
# 4. JSON Export Consistency
#    - Stocks, Crypto, Sports, Jobs, Recycle must export results to C:\EQ12\logs\*.json.
#    - Dashboard reads JSON logs and renders table-based panels for ALL modules.
#
# 5. Copilot Rewrite Rules
#    - PowerShell: rewrite functions with [CmdletBinding()] and Verb-Noun style.
#    - Python: add `# TODO: export this as JSON for dashboard`.
#    - Add `# TODO: add pytest unit test for this function`.
#    - Mirror Crypto’s working export pattern in Stocks, Sports, Jobs, Recycle.
#
# 6. Error Hardening
#    - Always wrap API/network calls in try/except or try/catch with logging.
#    - Default to empty JSON snapshot if data fetch fails, so dashboard never breaks.
#
# === End Patch ===

function Invoke-Retry {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [scriptblock]$ScriptBlock,
        [Parameter(Mandatory)] [string]$Name,
        [int]$Retries = 3,
        [int]$Delay = 5
    )
    for ($i=1; $i -le $Retries; $i++) {
        try {
            & $ScriptBlock
            Write-Host ("[{0}] OK on attempt {1}" -f $Name, $i)
            return $true
        } catch {
            $failMsg = ("[{0}] FAIL {1}: {2}" -f $Name, $i, $_.Exception.Message)
            Write-Host $failMsg
            Write-Log $failMsg
            if ($i -lt $Retries) { Start-Sleep -Seconds $Delay }
        }
    }
    return $false
}
param([switch]$Headless)

$ErrorActionPreference = "Continue"
$LogDir = "C:\EQ12\logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$SessionLog = Join-Path $LogDir ("elite_run_{0}.log" -f $ts)

function Write-Log($m) { $t=Get-Date -Format "yyyy-MM-dd HH:mm:ss"; "$t - $m" | Tee-Object -FilePath $SessionLog -Append }

$Python = "C:\Program Files\Python312\python.exe"; if (-not (Test-Path $Python)) { $Python = "python" }
$head = $null; if ($Headless) { $head="--headless" }

$jobs = @(
  @{ n="stocks";  cmd={ & $Python "C:\EQ12\scripts\py\stocks.py"  $head | Tee-Object -FilePath (Join-Path $LogDir "stocks_out.txt") -Append } },
  @{ n="crypto";  cmd={ & $Python "C:\EQ12\scripts\py\crypto.py"  $head | Tee-Object -FilePath (Join-Path $LogDir "crypto_out.txt") -Append } },
  @{ n="sports";  cmd={ & $Python "C:\EQ12\scripts\py\sports.py"  $head | Tee-Object -FilePath (Join-Path $LogDir "sports_out.txt") -Append } },
  @{ n="jobs";    cmd={ & $Python "C:\EQ12\scripts\py\jobs_controltech.py" $head | Tee-Object -FilePath (Join-Path $LogDir "jobs_out.txt") -Append } }
)


$ok=0;$fail=0
foreach ($j in $jobs) {
        try {
                Write-Log ("[{0}] Start" -f $j.n)
                & $j.cmd
                Write-Log ("[{0}] OK" -f $j.n)
                $ok++
        } catch {
                $failMsg = ("[{0}] FAIL: {1}" -f $j.n, $_.Exception.Message)
                Write-Host $failMsg
                Write-Log $failMsg
                $fail++
        }
}


# --- Odds API Fetch ---
Invoke-Retry { 
    & $Python "C:\EQ12\scripts\py\odds_fetcher.py" | Out-File "C:\EQ12\logs\odds_out.txt" -Append
} "odds_api"

try {
  $summary = "🚀 EQ12 Elite run finished.`nOK: {0}  FAIL: {1}`nLog: {2}" -f $ok,$fail,$SessionLog
  if (Get-Command Send-TelegramMessage -ErrorAction SilentlyContinue) { Send-TelegramMessage -Message $summary | Out-Null }
  Write-Log $summary
} catch { Write-Log "Telegram summary failed: $($_.Exception.Message)" }

& "C:\EQ12\scripts\eq12_build_dashboard.ps1"
Write-Log "Done."

function Test-EQ12Dashboard {
    $dashboardPath = "C:\EQ12\dashboard\index.html"
    $sections = @("Stocks", "Crypto", "Sports Odds", "Jobs")
    $results = @{}
    $allPass = $true

    if (-not (Test-Path $dashboardPath)) {
        Write-Host "❌ Dashboard file not found: $dashboardPath"
        return $false
    }

    foreach ($section in $sections) {
        $found = Select-String -Path $dashboardPath -Pattern $section -Quiet
        $results[$section] = $found
        if (-not $found) { $allPass = $false }
    }

    foreach ($section in $sections) {
        if ($results[$section]) {
            Write-Host "✅ Section found: $section"
        } else {
            Write-Host "❌ Section missing: $section"
        }
    }

    if ($allPass) {
        Write-Host "`n🎉 All dashboard sections present."
        return $true
    } else {
        Write-Host "`n⚠️  One or more dashboard sections missing."
        return $false
    }
}
