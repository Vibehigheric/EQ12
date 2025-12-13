# EQ12 2025 Revenue Dashboard Generator
# Creates real-time HTML dashboard for monitoring all 5 revenue streams

[CmdletBinding()]
param(
    [Parameter()]
    [string]$ConfigPath = "C:\EQ12_BROKEN_20251122_210342\config\master_config.json",
    
    [Parameter()]
    [string]$OutputPath = "C:\EQ12_BROKEN_20251122_210342\reports\revenue_dashboard.html"
)

$ErrorActionPreference = "Stop"

Write-Host "📊 Generating EQ12 2025 Revenue Dashboard..." -ForegroundColor Cyan

# Load config
if (-not (Test-Path $ConfigPath)) {
    Write-Host "❌ Config file not found: $ConfigPath" -ForegroundColor Red
    exit 1
}

$config = Get-Content $ConfigPath | ConvertFrom-Json

# Calculate metrics
$totalTarget = 0
$totalActual = 0
$streamsEnabled = 0

foreach ($stream in $config.revenue_streams.PSObject.Properties) {
    $streamData = $stream.Value
    if ($streamData.enabled) {
        $streamsEnabled++
        # Get monthly target from main orchestrator mapping
        $monthlyTargets = @{
            "betting_intelligence" = 300000
            "prompt_monetization" = 150000
            "pacer_legal" = 12500
            "travel_automation" = 25000
            "content_empire" = 75000
        }
        $totalTarget += $monthlyTargets[$stream.Name]
        $totalActual += $streamData.revenue
    }
}

$achievementPct = if ($totalTarget -gt 0) { ($totalActual / $totalTarget * 100) } else { 0 }
$successRate = if ($config.performance_metrics.total_executions -gt 0) {
    ($config.performance_metrics.successful_executions / $config.performance_metrics.total_executions * 100)
} else { 0 }

# Generate HTML
$html = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300">
    <title>EQ12 2025 Revenue Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 3px solid rgba(255,255,255,0.2);
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s;
        }
        .metric-card:hover { transform: translateY(-5px); }
        .metric-card h3 {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-card .value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .metric-card .label { font-size: 0.9em; opacity: 0.7; }
        .streams-section {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .streams-section h2 {
            font-size: 2em;
            margin-bottom: 20px;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 10px;
        }
        .stream {
            background: rgba(0,0,0,0.2);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 5px solid;
        }
        .stream.priority-1 { border-left-color: #ff6b6b; }
        .stream.priority-2 { border-left-color: #ffd93d; }
        .stream.priority-3 { border-left-color: #6bcf7f; }
        .stream-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .stream-name {
            font-size: 1.3em;
            font-weight: bold;
        }
        .stream-status {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .status-completed { background: #4caf50; }
        .status-running { background: #2196f3; }
        .status-failed { background: #f44336; }
        .status-idle { background: #9e9e9e; }
        .stream-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .stream-detail {
            background: rgba(255,255,255,0.05);
            padding: 10px;
            border-radius: 5px;
        }
        .stream-detail label {
            display: block;
            font-size: 0.8em;
            opacity: 0.7;
            margin-bottom: 5px;
        }
        .stream-detail value { font-size: 1.1em; font-weight: bold; }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.2);
            opacity: 0.7;
        }
        .progress-bar {
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            height: 30px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            background: linear-gradient(90deg, #4caf50, #8bc34a);
            height: 100%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 EQ12 2025 Revenue Dashboard</h1>
            <p>Real-Time Monitoring | 5 Revenue Streams | `$12M Annual Target</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Last Updated: $(Get-Date -Format 'MMMM dd, yyyy HH:mm:ss')</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <h3>💰 Monthly Revenue</h3>
                <div class="value">`$$($totalActual.ToString('N0'))</div>
                <div class="label">of `$$($totalTarget.ToString('N0')) target</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: $($achievementPct.ToString('F0'))%">
                        $($achievementPct.ToString('F1'))%
                    </div>
                </div>
            </div>

            <div class="metric-card">
                <h3>📊 Success Rate</h3>
                <div class="value">$($successRate.ToString('F1'))%</div>
                <div class="label">$($config.performance_metrics.successful_executions) of $($config.performance_metrics.total_executions) executions</div>
            </div>

            <div class="metric-card">
                <h3>🎯 Active Streams</h3>
                <div class="value">$streamsEnabled</div>
                <div class="label">of 5 revenue streams</div>
            </div>

            <div class="metric-card">
                <h3>⚡ Status</h3>
                <div class="value">$(if ($successRate -ge 90) { '✅' } elseif ($successRate -ge 70) { '⚠️' } else { '❌' })</div>
                <div class="label">$(if ($successRate -ge 90) { 'Excellent' } elseif ($successRate -ge 70) { 'Good' } else { 'Needs Attention' })</div>
            </div>
        </div>

        <div class="streams-section">
            <h2>💼 Revenue Streams</h2>
"@

# Add each stream
$streamTargets = @{
    "betting_intelligence" = @{ target = 300000; priority = 1; name = "AI Betting Intelligence Suite" }
    "prompt_monetization" = @{ target = 150000; priority = 1; name = "AI Prompt Monetization Engine" }
    "pacer_legal" = @{ target = 12500; priority = 2; name = "PACER Legal Intelligence" }
    "travel_automation" = @{ target = 25000; priority = 3; name = "Travel Deal Automation" }
    "content_empire" = @{ target = 75000; priority = 2; name = "Content Empire Builder" }
}

foreach ($stream in $config.revenue_streams.PSObject.Properties) {
    $streamData = $stream.Value
    $streamInfo = $streamTargets[$stream.Name]
    $statusClass = "status-$($streamData.status)"
    
    $html += @"
            <div class="stream priority-$($streamInfo.priority)">
                <div class="stream-header">
                    <div class="stream-name">$($streamInfo.name)</div>
                    <div class="stream-status $statusClass">$($streamData.status.ToUpper())</div>
                </div>
                <div class="stream-details">
                    <div class="stream-detail">
                        <label>💰 Monthly Target</label>
                        <value>`$$($streamInfo.target.ToString('N0'))</value>
                    </div>
                    <div class="stream-detail">
                        <label>📈 Actual Revenue</label>
                        <value>`$$($streamData.revenue.ToString('N0'))</value>
                    </div>
                    <div class="stream-detail">
                        <label>⚠️ Error Count</label>
                        <value>$($streamData.error_count)</value>
                    </div>
                    <div class="stream-detail">
                        <label>🕒 Last Run</label>
                        <value>$(if ($streamData.last_run) { (Get-Date $streamData.last_run).ToString('MM/dd HH:mm') } else { 'Never' })</value>
                    </div>
                </div>
            </div>
"@
}

$html += @"
        </div>

        <div class="footer">
            <p>Auto-refreshes every 5 minutes</p>
            <p>EQ12 2025 Master Orchestrator | Built with PowerShell + Python</p>
        </div>
    </div>
</body>
</html>
"@

# Save dashboard
$OutputDir = Split-Path $OutputPath
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$html | Out-File -FilePath $OutputPath -Encoding UTF8
Write-Host "✅ Dashboard generated: $OutputPath" -ForegroundColor Green

# Open in browser
if (Get-Command Start-Process -ErrorAction SilentlyContinue) {
    Write-Host "🌐 Opening dashboard in browser..." -ForegroundColor Cyan
    Start-Process $OutputPath
}
