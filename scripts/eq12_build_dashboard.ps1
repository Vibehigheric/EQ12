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

# eq12_build_dashboard.ps1 — EQ12 Synergy Dashboard


# === EQ12 Dashboard Builder ===
$dashboardDir = "C:\EQ12\dashboard"
if (-not (Test-Path $dashboardDir)) {
    New-Item -ItemType Directory -Path $dashboardDir -Force | Out-Null
}

$html = Join-Path $dashboardDir "index.html"
# reset file on each run
Set-Content -Path $html -Value "<html><head><title>EQ12 Dashboard</title></head><body><h1>EQ12 Dashboard</h1>"

# Pull in latest logs
$recycle = if (Test-Path "C:\EQ12\logs\recycle_report.json") { Get-Content "C:\EQ12\logs\recycle_report.json" -Raw } else { "{}" }
$jobs    = if (Test-Path "C:\EQ12\logs\jobs_controltech.json") { Get-Content "C:\EQ12\logs\jobs_controltech.json" -Raw } else { "{}" }
$crypto  = if (Test-Path "C:\EQ12\logs\crypto_latest.json") { Get-Content "C:\EQ12\logs\crypto_latest.json" -Raw } else { "{}" }

@"
<!doctype html><html><head><meta charset="utf-8">
<title>EQ12 Synergy Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>
<script src="https://d3js.org/d3.v7.min.js"></script>
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css"/>
<style>
body{background:#0b0e11;color:#e7e7e7;font-family:Segoe UI,Arial}
.card{background:#14181d;padding:16px;margin:16px;border-radius:10px}
h1{margin-bottom:20px}
</style>
</head><body>

<h1>EQ12 Synergy Dashboard</h1>


<div class="card">
  <h2>Stocks</h2>
  <div id="stocks"></div>
</div>
<script>
fetch("stocks_latest.json")
  .then(resp => resp.json())
  .then(data => {
    let html = "<table><tr><th>Ticker</th><th>Close</th><th>EMA20</th><th>EMA50</th><th>RSI14</th><th>Momentum</th><th>Signal</th></tr>";
    (data.results || []).forEach(r => {
      html += `<tr>
        <td>${r.ticker}</td>
        <td>${r.close.toFixed(2)}</td>
        <td>${r.ema20.toFixed(2)}</td>
        <td>${r.ema50.toFixed(2)}</td>
        <td>${r.rsi14.toFixed(1)}</td>
        <td>${(r.mom5*100).toFixed(2)}%</td>
        <td>${r.signal}</td>
      </tr>`;
    });
    html += "</table>";
    document.getElementById("stocks").innerHTML = html;
  });

<div class="card">
  <h2>Crypto</h2>
  <div id="crypto"></div>
</div>
<script>
fetch("stocks_latest.json")
  .then(resp => resp.json())
  .then(data => {
    let html = "<table><tr><th>Ticker</th><th>Close</th><th>EMA20</th><th>EMA50</th><th>RSI14</th><th>Momentum</th><th>Signal</th></tr>";
    (data.results || []).forEach(r => {
      html += `<tr>
        <td>${r.ticker}</td>
        <td>${r.close.toFixed(2)}</td>
        <td>${r.ema20.toFixed(2)}</td>
        <td>${r.ema50.toFixed(2)}</td>
        <td>${r.rsi14.toFixed(1)}</td>
        <td>${(r.mom5*100).toFixed(2)}%</td>
        <td>${r.signal}</td>
      </tr>`;
    });
    html += "</table>";
    document.getElementById("stocks").innerHTML = html;
  })
  .catch(err => {
    document.getElementById("stocks").innerHTML = "<p>No stock data available.</p>";
  });
</script>
<script>
fetch("crypto_latest.json")
  .then(resp => resp.json())
  .then(data => {
    let html = "<table><tr><th>Pair</th><th>Spot Price</th></tr>";
    (data.results || []).forEach(r => {
      html += `<tr><td>${r.pair}</td><td>${r.coinbase_spot?.toFixed(2) || "N/A"}</td></tr>`;
    });
    html += "</table>";
    document.getElementById("crypto").innerHTML = html;
  })
  .catch(err => {
    document.getElementById("crypto").innerHTML = "<p>No crypto data available.</p>";
  });
</script>
    (data.results || []).forEach(r => {
      html += `<tr><td>${r.pair}</td><td>${r.coinbase_spot?.toFixed(2) || "N/A"}</td></tr>`;
    });
    html += "</table>";
    document.getElementById("crypto").innerHTML = html;
<script>
fetch("jobs_controltech.json")
  .then(resp => resp.json())
  .then(data => {
    let html = "<table><tr><th>Title</th><th>Link</th><th>Date</th></tr>";
    (data.results || []).forEach(j => {
      html += `<tr>
        <td>${j.title}</td>
        <td><a href="${j.link}" target="_blank">View</a></td>
        <td>${j.published}</td>
      </tr>`;
    });
    html += "</table>";
    document.getElementById("jobs").innerHTML = html;
  })
  .catch(err => {
    document.getElementById("jobs").innerHTML = "<p>No job data available.</p>";
  });
</script>
  });

<div class="card">
  <h2>Control Tech Jobs</h2>
  <div id="jobs"></div>
<script>
fetch("recycle_report.json")
  .then(resp => resp.json())
  .then(data => {
    let html = "<table><tr><th>Index</th><th>Name</th><th>Path</th><th>Date</th><th>Size</th></tr>";
    (data.items || []).forEach((r, idx) => {
      html += `<tr>
        <td>${idx}</td>
        <td>${r.Name}</td>
        <td>${r.OriginalPath}</td>
        <td>${r.DeletionDate}</td>
        <td>${r.Size}</td>
      </tr>`;
    });
    html += "</table>";
    document.getElementById("recycle").innerHTML = html;
  })
  .catch(err => {
    document.getElementById("recycle").innerHTML = "<p>No recycle data available.</p>";
  });
</script>
</div>
<script>
fetch("jobs_controltech.json")
  .then(resp => resp.json())
  .then(data => {
    let html = "<table><tr><th>Title</th><th>Link</th><th>Date</th></tr>";
    (data.results || []).forEach(j => {
      html += `<tr>
        <td>${j.title}</td>
        <td><a href="${j.link}" target="_blank">View</a></td>
        <td>${j.published}</td>
      </tr>`;
    });
    html += "</table>";
    document.getElementById("jobs").innerHTML = html;
  });

<div class="card">
  <h2>Recycle Bin</h2>
  <div id="recycle"></div>
</div>
<script>
fetch("recycle_report.json")
  .then(resp => resp.json())
  .then(data => {
    let html = "<table><tr><th>Index</th><th>Name</th><th>Path</th><th>Date</th><th>Size</th></tr>";
    (data.items || []).forEach((r, idx) => {
      html += `<tr>
        <td>${idx}</td>
        <td>${r.Name}</td>
        <td>${r.OriginalPath}</td>
        <td>${r.DeletionDate}</td>
        <td>${r.Size}</td>
      </tr>`;
    });
    html += "</table>";
    document.getElementById("recycle").innerHTML = html;
  });

<div class="card">
  <h2>Odds</h2>
  <div id="odds"></div>
</div>
<script>
fetch("odds_snapshot.json")
  .then(resp => resp.json())
  .then(data => {
    let html = "<table><tr><th>Sport</th><th>Home</th><th>Away</th><th>Spread</th><th>Moneyline</th></tr>";
    (data || []).forEach(sport => {
      if (sport.events && sport.events.length) {
        sport.events.forEach(ev => {
          let home = ev.home_team || (ev.teams && ev.teams[0]) || "";
          let away = ev.away_team || (ev.teams && ev.teams[1]) || "";
          let spread = "";
          let moneyline = "";
          if (ev.bookmakers && ev.bookmakers.length) {
            let bm = ev.bookmakers[0];
            let spreadMarket = bm.markets && bm.markets.find(m => m.key === "spreads");
            let h2hMarket = bm.markets && bm.markets.find(m => m.key === "h2h");
            if (spreadMarket && spreadMarket.outcomes && spreadMarket.outcomes.length >= 2) {
              spread = `${spreadMarket.outcomes[0].point || ''} / ${spreadMarket.outcomes[1].point || ''}`;
            }
            if (h2hMarket && h2hMarket.outcomes && h2hMarket.outcomes.length >= 2) {
              moneyline = `${h2hMarket.outcomes[0].price || ''} / ${h2hMarket.outcomes[1].price || ''}`;
            }
          }
          html += `<tr>
            <td>${sport.sport}</td>
            <td>${home}</td>
            <td>${away}</td>
            <td>${spread}</td>
            <td>${moneyline}</td>
          </tr>`;
        });
      }
    });
    html += "</table>";
    document.getElementById("odds").innerHTML = html;
  })
  .catch(err => {
    document.getElementById("odds").innerHTML = "<p>No odds data available.</p>";
  });
</script>
<script>
// Inject JSON
const recycle = $($recycle | ConvertTo-Json -Compress);
const crypto  = $($crypto | ConvertTo-Json -Compress);
const jobs    = $($jobs | ConvertTo-Json -Compress);

// Show recycle JSON as text
document.getElementById('recycle').textContent = JSON.stringify(recycle,null,2);

// Crypto chart example (BTC vs ETH spot)
if(crypto.results){
  const labels = crypto.results.map(r=>r.pair);
  const prices = crypto.results.map(r=>r.coinbase_spot);
  new Chart(document.getElementById('cryptoChart'),{
    type:'bar',
    data:{labels:labels,datasets:[{label:"Coinbase Spot",data:prices,backgroundColor:"#4bc0c0"}]}
  });
}

// Build jobs table
`$(document).ready(function(){
  if(jobs.results){
    jobs.results.forEach(j=>{
      `$('#jobsTable tbody').append(
        `<tr><td>${j.title||""}</td><td><a href="${j.link}" target="_blank">Link</a></td><td>${j.published||""}</td></tr>`
      )
    });
    `$('#jobsTable').DataTable();
  }
});
</script>
</body></html>
"@ | Out-File $html -Encoding UTF8

Start-Process $html

# --- Sports Odds Panel ---
$oddsFile = "C:\EQ12\logs\odds_americanfootball_nfl.json"
if (Test-Path $oddsFile) {
    $odds = Get-Content $oddsFile | ConvertFrom-Json
  Add-Content -Path $html -Value "<h2>Sports Odds</h2><table border=1><tr><th>Match</th><th>Bookmaker</th><th>Odds</th></tr>"
    foreach ($ev in $odds) {
        $match = "$($ev.home_team) vs $($ev.away_team)"
        foreach ($book in $ev.bookmakers) {
            $h2h = ($book.markets | Where-Object { $_.key -eq 'h2h' }).outcomes
            if ($h2h) {
                $oddsline = ($h2h | ForEach-Object { "$( $_.name ): $( $_.price )" }) -join " | "
                Add-Content -Path $html -Value "<tr><td>$match</td><td>$($book.title)</td><td>$oddsline</td></tr>"
            }
        }
    }
  Add-Content -Path $html -Value "</table>"
}

# --- Close HTML and open in browser ---
Add-Content -Path $html -Value "</body></html>"
Start-Process $html   # open in browser
