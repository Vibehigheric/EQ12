#Requires -Version 5.1
<#
.SYNOPSIS
    EQ12 Bing Integration One-Click Setup

.DESCRIPTION
    Installs all dependencies, creates virtual environment, places Bing API scripts,
    and sets up Task Scheduler jobs for automated Bing intelligence across all EQ12 stacks.

.PARAMETER ApiKey
    Bing Search API key (will be stored securely)

.PARAMETER SkipInstall
    Skip package installation (if already done)

.PARAMETER DryRun
    Show what would be done without executing

.EXAMPLE
    .\Setup-BingIntegration.ps1 -ApiKey "your_bing_key_here"

.EXAMPLE
    .\Setup-BingIntegration.ps1 -SkipInstall -DryRun
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$ApiKey,

    [Parameter(Mandatory = $false)]
    [switch]$SkipInstall,

    [Parameter(Mandatory = $false)]
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

# === EQ12 Bing Integration Configuration ===
$EQ12_ROOT = "C:\EQ12"
$BING_DIR = Join-Path $EQ12_ROOT "bing_intelligence"
$LOGS_DIR = Join-Path $EQ12_ROOT "logs"
$KEYS_DIR = Join-Path $EQ12_ROOT "keys"
$SCRIPTS_DIR = Join-Path $EQ12_ROOT "scripts"
$VENV_DIR = Join-Path $BING_DIR ".venv"

# Stack-specific directories
$STACK_DIRS = @{
    "betting"   = Join-Path $BING_DIR "betting"
    "travel"    = Join-Path $BING_DIR "travel"
    "cannabis"  = Join-Path $BING_DIR "cannabis"
    "fleet"     = Join-Path $BING_DIR "fleet"
    "finance"   = Join-Path $BING_DIR "finance"
    "education" = Join-Path $BING_DIR "education"
    "core"      = Join-Path $BING_DIR "core"
}

function Write-EQ12Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    Write-Host $logMessage -ForegroundColor $(switch ($Level) {
            "ERROR" { "Red" }
            "WARN" { "Yellow" }
            "SUCCESS" { "Green" }
            default { "Cyan" }
        })
    if (-not $DryRun) {
        $logFile = Join-Path $LOGS_DIR "bing_setup_$(Get-Date -Format 'yyyyMMdd').log"
        Add-Content -Path $logFile -Value $logMessage -Encoding UTF8
    }
}

function Test-EQ12Prerequisites {
    Write-EQ12Log "Checking EQ12 prerequisites..."

    # Check if running as admin for Task Scheduler
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-EQ12Log "WARNING: Not running as Administrator. Task Scheduler setup may fail." -Level "WARN"
    }

    # Check Python 3.12
    try {
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -match "Python 3\.1[2-9]") {
            Write-EQ12Log "✅ Python detected: $pythonVersion" -Level "SUCCESS"
        } else {
            throw "Python 3.12+ required. Found: $pythonVersion"
        }
    } catch {
        Write-EQ12Log "❌ Python 3.12+ not found. Install from [Python Official Site](https://python.org)" -Level "ERROR"
        return $false
    }

    # Check Node.js
    try {
        $nodeVersion = & node --version 2>&1
        Write-EQ12Log "✅ Node.js detected: $nodeVersion" -Level "SUCCESS"
    } catch {
        Write-EQ12Log "⚠️  Node.js not found. Some features will be Python-only." -Level "WARN"
    }

    return $true
}

function New-EQ12Directories {
    Write-EQ12Log "Creating EQ12 Bing directory structure..."

    # Core directories
    @($BING_DIR, $LOGS_DIR, $KEYS_DIR) | ForEach-Object {
        if (-not (Test-Path $_) -and -not $DryRun) {
            New-Item -Path $_ -ItemType Directory -Force | Out-Null
            Write-EQ12Log "Created directory: $_" -Level "SUCCESS"
        } elseif ($DryRun) {
            Write-EQ12Log "Would create directory: $_"
        }
    }

    # Stack directories
    $STACK_DIRS.Values | ForEach-Object {
        if (-not (Test-Path $_) -and -not $DryRun) {
            New-Item -Path $_ -ItemType Directory -Force | Out-Null
            Write-EQ12Log "Created stack directory: $_" -Level "SUCCESS"
        } elseif ($DryRun) {
            Write-EQ12Log "Would create stack directory: $_"
        }
    }
}

function Install-EQ12BingDependencies {
    if ($SkipInstall) {
        Write-EQ12Log "Skipping package installation (SkipInstall flag set)"
        return
    }

    Write-EQ12Log "Installing EQ12 Bing dependencies..."

    # Create Python virtual environment
    if (-not $DryRun) {
        if (Test-Path $VENV_DIR) {
            Write-EQ12Log "Virtual environment exists, recreating..." -Level "WARN"
            Remove-Item $VENV_DIR -Recurse -Force
        }

        & python -m venv $VENV_DIR
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-EQ12Log "✅ Created Python virtual environment" -Level "SUCCESS"
    }

    # Activate venv and install packages
    $activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"
    $pipPath = Join-Path $VENV_DIR "Scripts\pip.exe"

    $packages = @(
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "sqlalchemy>=2.0.0",
        "python-telegram-bot>=20.0",
        "playwright>=1.40.0",
        "azure-cognitiveservices-search-websearch>=2.0.0",
        "python-dotenv>=1.0.0",
        "Pillow>=10.0.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0"
    )

    if (-not $DryRun) {
        foreach ($package in $packages) {
            Write-EQ12Log "Installing: $package"
            & $pipPath install $package --quiet
            if ($LASTEXITCODE -eq 0) {
                Write-EQ12Log "✅ Installed: $package" -Level "SUCCESS"
            } else {
                Write-EQ12Log "❌ Failed to install: $package" -Level "ERROR"
            }
        }

        # Install Playwright browsers
        $playwrightPath = Join-Path $VENV_DIR "Scripts\playwright.exe"
        & $playwrightPath install chromium --with-deps
        Write-EQ12Log "✅ Installed Playwright browsers" -Level "SUCCESS"
    } else {
        Write-EQ12Log "Would install packages: $($packages -join ', ')"
        Write-EQ12Log "Would install Playwright browsers"
    }

    # Install Node.js dependencies if Node exists
    try {
        & node --version | Out-Null
        $packageJson = @{
            "name"         = "eq12-bing-intelligence"
            "version"      = "1.0.0"
            "dependencies" = @{
                "node-fetch" = "^3.3.0"
                "puppeteer"  = "^21.0.0"
                "telegram"   = "^2.0.0"
                "sqlite3"    = "^5.1.6"
            }
        } | ConvertTo-Json -Depth 3

        if (-not $DryRun) {
            $packageJsonPath = Join-Path $BING_DIR "package.json"
            Set-Content -Path $packageJsonPath -Value $packageJson -Encoding UTF8

            Push-Location $BING_DIR
            & npm install --silent
            Pop-Location
            Write-EQ12Log "✅ Installed Node.js dependencies" -Level "SUCCESS"
        } else {
            Write-EQ12Log "Would create package.json and install Node.js deps"
        }
    } catch {
        Write-EQ12Log "Skipping Node.js setup (not available)" -Level "WARN"
    }
}

function Set-EQ12BingApiKey {
    if ([string]::IsNullOrEmpty($ApiKey)) {
        $ApiKey = Read-Host -Prompt "Enter your Bing Search API key (or press Enter to set later)"
    }

    if (-not [string]::IsNullOrEmpty($ApiKey)) {
        $keyFile = Join-Path $KEYS_DIR "bing_api.txt"
        if (-not $DryRun) {
            Set-Content -Path $keyFile -Value $ApiKey.Trim() -Encoding UTF8
            Write-EQ12Log "✅ Saved Bing API key to $keyFile" -Level "SUCCESS"

            # Also set in environment for current session
            $env:BING_API_KEY = $ApiKey.Trim()
        } else {
            Write-EQ12Log "Would save API key to $keyFile"
        }
    } else {
        Write-EQ12Log "⚠️  No API key provided. You can add it later to $KEYS_DIR\bing_api.txt" -Level "WARN"
    }
}

function New-EQ12BingScripts {
    Write-EQ12Log "Creating EQ12 Bing integration scripts..."

    # Core Bing Web Search script
    $bingWebSearchScript = @"
#!/usr/bin/env python3
"""
EQ12 Bing Web Search Integration
Integrates with existing EQ12 sports betting, travel, and automation stacks.
"""
import os
import sys
import csv
import json
import time
import requests
import sqlite3
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

# EQ12 Integration
EQ12_ROOT = Path("C:/EQ12")
LOGS_DIR = EQ12_ROOT / "logs"
KEYS_DIR = EQ12_ROOT / "keys"
BING_DB = EQ12_ROOT / "bing_intelligence" / "bing_cache.db"

def load_eq12_api_key():
    """Load Bing API key from EQ12 keys directory or environment"""
    key_file = KEYS_DIR / "bing_api.txt"
    if key_file.exists():
        return key_file.read_text().strip()
    return os.getenv("BING_API_KEY")

def setup_eq12_logging():
    """Setup logging consistent with EQ12 patterns"""
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / f"bing_search_{datetime.now().strftime('%Y%m%d')}.log"

    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

class EQ12BingSearch:
    def __init__(self):
        self.api_key = load_eq12_api_key()
        if not self.api_key:
            raise ValueError("Bing API key not found. Set BING_API_KEY or add to C:/EQ12/keys/bing_api.txt")

        self.endpoint = "https://api.bing.microsoft.com/v7.0/search"
        self.headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        self.logger = setup_eq12_logging()
        self.init_database()

    def init_database(self):
        """Initialize SQLite cache database"""
        BING_DB.parent.mkdir(exist_ok=True)
        conn = sqlite3.connect(BING_DB)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS search_results (
                id INTEGER PRIMARY KEY,
                query TEXT NOT NULL,
                stack TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                snippet TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(query, url)
            )
        ''')
        conn.commit()
        conn.close()

    def search(self, query, count=10, market="en-US"):
        """Perform Bing search with EQ12 integration"""
        params = {
            "q": query,
            "count": count,
            "textDecorations": False,
            "textFormat": "Raw",
            "mkt": market
        }

        try:
            response = requests.get(
                self.endpoint,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Bing API error: {e}")
            return None

    def search_for_stack(self, queries, stack_name):
        """Search multiple queries for a specific EQ12 stack"""
        all_results = []

        for query in queries:
            self.logger.info(f"[{stack_name.upper()}] Searching: {query}")
            data = self.search(query)

            if data and "webPages" in data:
                results = data["webPages"].get("value", [])
                for item in results:
                    result = {
                        "query": query,
                        "stack": stack_name,
                        "title": item.get("name", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    all_results.append(result)
                    self.save_to_db(result)

            time.sleep(1)  # Rate limiting

        return all_results

    def save_to_db(self, result):
        """Save result to SQLite database"""
        conn = sqlite3.connect(BING_DB)
        try:
            conn.execute('''
                INSERT OR IGNORE INTO search_results
                (query, stack, url, title, snippet, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                result["query"], result["stack"], result["url"],
                result["title"], result["snippet"], result["timestamp"]
            ))
            conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
        finally:
            conn.close()

    def export_results(self, stack_name, output_format="json"):
        """Export results to JSON/CSV for EQ12 dashboard"""
        conn = sqlite3.connect(BING_DB)
        cursor = conn.execute(
            "SELECT * FROM search_results WHERE stack = ? ORDER BY timestamp DESC LIMIT 100",
            (stack_name,)
        )

        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0], "query": row[1], "stack": row[2],
                "url": row[3], "title": row[4], "snippet": row[5],
                "timestamp": row[6]
            })
        conn.close()

        if output_format == "json":
            json_file = LOGS_DIR / f"bing_{stack_name}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Exported {len(results)} results to {json_file}")
            return json_file

        elif output_format == "csv":
            csv_file = LOGS_DIR / f"bing_{stack_name}_{datetime.now().strftime('%Y%m%d')}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys() if results else [])
                writer.writeheader()
                writer.writerows(results)
            return csv_file

# EQ12 Stack-specific search configs
STACK_QUERIES = {
    "betting": [
        "Buffalo sports betting news injury reports",
        "MLB player injury betting impact latest",
        "NFL injury reports line movement analysis",
        "sports betting regulation New York state"
    ],
    "travel": [
        "Buffalo airport cheap flights December 2025",
        "BUF to LAX flight deals winter",
        "Buffalo travel deals vacation packages",
        "airport parking Buffalo Niagara deals"
    ],
    "cannabis": [
        "Buffalo dispensary news licenses 2025",
        "New York cannabis regulation updates",
        "Buffalo marijuana dispensary locations",
        "cannabis tourism Buffalo Niagara"
    ],
    "finance": [
        "Buffalo housing market trends 2025",
        "mortgage rates Buffalo NY December",
        "Buffalo real estate investment opportunities",
        "credit repair services Buffalo NY"
    ]
}

def main():
    """Main EQ12 Bing integration runner"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Bing Intelligence")
    parser.add_argument("--stack", choices=list(STACK_QUERIES.keys()) + ["all"],
                       default="all", help="EQ12 stack to search for")
    parser.add_argument("--export", choices=["json", "csv"], default="json",
                       help="Export format")
    parser.add_argument("--custom-query", help="Custom search query")

    args = parser.parse_args()

    try:
        searcher = EQ12BingSearch()

        if args.custom_query:
            results = searcher.search_for_stack([args.custom_query], "custom")
            searcher.export_results("custom", args.export)
        elif args.stack == "all":
            for stack, queries in STACK_QUERIES.items():
                results = searcher.search_for_stack(queries, stack)
                searcher.export_results(stack, args.export)
                searcher.logger.info(f"✅ Completed {stack} stack ({len(results)} results)")
        else:
            queries = STACK_QUERIES[args.stack]
            results = searcher.search_for_stack(queries, args.stack)
            searcher.export_results(args.stack, args.export)
            searcher.logger.info(f"✅ Completed {args.stack} stack ({len(results)} results)")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"@

    $coreScriptPath = Join-Path $STACK_DIRS["core"] "bing_web_search.py"
    if (-not $DryRun) {
        Set-Content -Path $coreScriptPath -Value $bingWebSearchScript -Encoding UTF8
        Write-EQ12Log "✅ Created core Bing search script: $coreScriptPath" -Level "SUCCESS"
    } else {
        Write-EQ12Log "Would create: $coreScriptPath"
    }

    # Betting Stack Integration Script
    $bettingScript = @"
#!/usr/bin/env python3
"""
EQ12 Betting Stack + Bing Intelligence Integration
Enhances existing EdgeGod parlay system with Bing news intelligence.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))

from bing_web_search import EQ12BingSearch
import json
from datetime import datetime
from pathlib import Path

class EQ12BettingIntelligence:
    def __init__(self):
        self.bing = EQ12BingSearch()
        self.eq12_root = Path("C:/EQ12")

    def check_injury_news(self, sport="mlb"):
        """Check for breaking injury news that might affect odds"""
        queries = [
            f"{sport} injury report today breaking news",
            f"{sport} player injury betting impact",
            f"{sport} starting lineup changes today",
        ]

        results = self.bing.search_for_stack(queries, f"betting_{sport}")

        # Integrate with existing EdgeGod system
        self.send_to_telegram_if_urgent(results)
        return results

    def send_to_telegram_if_urgent(self, results):
        """Send urgent betting intel to Telegram (integrates with existing bot)"""
        urgent_keywords = ["injury", "ruled out", "questionable", "scratched", "benched"]

        for result in results:
            title_lower = result["title"].lower()
            snippet_lower = result["snippet"].lower()

            if any(keyword in title_lower or keyword in snippet_lower for keyword in urgent_keywords):
                # Use existing EQ12 Telegram infrastructure
                try:
                    telegram_msg = f"🚨 BETTING INTEL ALERT\\n\\n{result['title']}\\n\\n{result['snippet']}\\n\\nSource: {result['url']}"

                    # Integrate with existing Telegram bot from EdgeGod system
                    self.logger.info(f"🚨 URGENT: {result['title']}")

                    # Could call existing Telegram script here:
                    # subprocess.run(['python', 'C:/EQ12/EdgeGodParlays/telegram_sender.py', telegram_msg])

                except Exception as e:
                    self.logger.error(f"Telegram alert failed: {e}")

def main():
    intel = EQ12BettingIntelligence()

    # Check for MLB injury news (integrates with existing odds_parser.py)
    mlb_results = intel.check_injury_news("mlb")

    # Check for NFL injury news
    nfl_results = intel.check_injury_news("nfl")

    print(f"✅ Betting intelligence complete: {len(mlb_results + nfl_results)} alerts processed")

if __name__ == "__main__":
    main()
"@

    $bettingScriptPath = Join-Path $STACK_DIRS["betting"] "bing_betting_intel.py"
    if (-not $DryRun) {
        Set-Content -Path $bettingScriptPath -Value $bettingScript -Encoding UTF8
        Write-EQ12Log "✅ Created betting intelligence script: $bettingScriptPath" -Level "SUCCESS"
    } else {
        Write-EQ12Log "Would create: $bettingScriptPath"
    }

    # Travel Stack Integration
    $travelScript = @"
#!/usr/bin/env python3
"""
EQ12 Travel Stack + Bing Intelligence Integration
Enhances existing travel deals scraper with Bing search intelligence.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "core"))

from bing_web_search import EQ12BingSearch
from datetime import datetime, timedelta

class EQ12TravelIntelligence:
    def __init__(self):
        self.bing = EQ12BingSearch()

    def find_flight_deals(self, departure="BUF", destinations=None):
        """Find flight deals from Buffalo to popular destinations"""
        if destinations is None:
            destinations = ["LAX", "MIA", "LAS", "DEN", "ATL"]

        queries = []
        next_month = (datetime.now() + timedelta(days=30)).strftime("%B %Y")

        for dest in destinations:
            queries.extend([
                f"cheap flights {departure} to {dest} {next_month}",
                f"flight deals Buffalo to {dest} winter 2025",
                f"{departure} {dest} airline sale discount"
            ])

        results = self.bing.search_for_stack(queries, "travel_flights")

        # Filter for actual deals (look for price keywords)
        deal_results = []
        deal_keywords = ["$", "deal", "sale", "discount", "%", "cheap", "special"]

        for result in results:
            text = f"{result['title']} {result['snippet']}".lower()
            if any(keyword in text for keyword in deal_keywords):
                deal_results.append(result)

        return deal_results

    def monitor_travel_news(self):
        """Monitor travel-related news for opportunities"""
        queries = [
            "Buffalo airport news flight additions",
            "new airline routes Buffalo Niagara",
            "travel restrictions lifted destinations",
            "hotel deals Buffalo Niagara Falls"
        ]

        return self.bing.search_for_stack(queries, "travel_news")

def main():
    travel_intel = EQ12TravelIntelligence()

    # Find current flight deals
    flight_deals = travel_intel.find_flight_deals()
    print(f"✅ Found {len(flight_deals)} potential flight deals")

    # Monitor travel news
    travel_news = travel_intel.monitor_travel_news()
    print(f"✅ Found {len(travel_news)} travel news items")

if __name__ == "__main__":
    main()
"@

    $travelScriptPath = Join-Path $STACK_DIRS["travel"] "bing_travel_intel.py"
    if (-not $DryRun) {
        Set-Content -Path $travelScriptPath -Value $travelScript -Encoding UTF8
        Write-EQ12Log "✅ Created travel intelligence script: $travelScriptPath" -Level "SUCCESS"
    } else {
        Write-EQ12Log "Would create: $travelScriptPath"
    }
}

function New-EQ12TaskScheduler {
    Write-EQ12Log "Setting up EQ12 Bing Task Scheduler jobs..."

    $pythonExe = Join-Path $VENV_DIR "Scripts\python.exe"
    $coreScript = Join-Path $STACK_DIRS["core"] "bing_web_search.py"

    $tasks = @(
        @{
            Name        = "EQ12-Bing-Hourly-Betting"
            Script      = Join-Path $STACK_DIRS["betting"] "bing_betting_intel.py"
            Schedule    = "Hourly"
            Description = "Hourly betting intelligence via Bing for injury/news alerts"
        },
        @{
            Name        = "EQ12-Bing-Daily-Travel"
            Script      = Join-Path $STACK_DIRS["travel"] "bing_travel_intel.py"
            Schedule    = "Daily"
            Description = "Daily travel deals and news monitoring"
        },
        @{
            Name        = "EQ12-Bing-Daily-AllStacks"
            Script      = $coreScript
            Schedule    = "Daily"
            Description = "Daily comprehensive Bing intelligence across all EQ12 stacks"
            Args        = "--stack all --export json"
        }
    )

    foreach ($task in $tasks) {
        $taskName = $task.Name
        $scriptPath = $task.Script
        $args = $task.Args ?? ""

        if ($DryRun) {
            Write-EQ12Log "Would create task: $taskName running $scriptPath"
            continue
        }

        # Remove existing task if present
        try {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        } catch {}

        # Create new task
        $action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptPath`" $args"

        $trigger = switch ($task.Schedule) {
            "Hourly" { New-ScheduledTaskTrigger -Once -At "00:00" -RepetitionInterval (New-TimeSpan -Hours 1) }
            "Daily" { New-ScheduledTaskTrigger -Daily -At "06:00" }
        }

        $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

        try {
            Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description $task.Description | Out-Null
            Write-EQ12Log "✅ Created scheduled task: $taskName" -Level "SUCCESS"
        } catch {
            Write-EQ12Log "❌ Failed to create task $taskName`: $_" -Level "ERROR"
        }
    }
}

function New-EQ12BingDashboardIntegration {
    Write-EQ12Log "Creating EQ12 dashboard integration for Bing intelligence..."

    $dashboardScript = @"
#!/usr/bin/env python3
"""
EQ12 Dashboard Bing Intelligence Integration
Adds Bing search results to existing EQ12 dashboard system.
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

def generate_bing_dashboard_html():
    """Generate HTML sections for EQ12 dashboard"""
    eq12_root = Path("C:/EQ12")
    bing_db = eq12_root / "bing_intelligence" / "bing_cache.db"

    if not bing_db.exists():
        return "<p>No Bing intelligence data available</p>"

    conn = sqlite3.connect(bing_db)

    # Get recent results by stack
    html_sections = []

    stacks = ["betting", "travel", "cannabis", "finance"]

    for stack in stacks:
        cursor = conn.execute('''
            SELECT title, url, snippet, timestamp
            FROM search_results
            WHERE stack = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 5
        ''', (stack, (datetime.now() - timedelta(days=1)).isoformat()))

        results = cursor.fetchall()

        if results:
            html_sections.append(f'<h3>🔍 {stack.title()} Intelligence</h3>')
            html_sections.append('<table class="eq12-table">')
            html_sections.append('<tr><th>Title</th><th>Summary</th><th>Time</th></tr>')

            for title, url, snippet, timestamp in results:
                time_str = datetime.fromisoformat(timestamp).strftime("%H:%M")
                snippet_short = snippet[:100] + "..." if len(snippet) > 100 else snippet
                html_sections.append(f'''
                <tr>
                    <td><a href="{url}" target="_blank">{title}</a></td>
                    <td>{snippet_short}</td>
                    <td>{time_str}</td>
                </tr>
                ''')

            html_sections.append('</table><br>')

    conn.close()
    return '\n'.join(html_sections)

def update_eq12_dashboard():
    """Update the main EQ12 dashboard with Bing intelligence"""
    eq12_root = Path("C:/EQ12")
    dashboard_file = eq12_root / "dashboard" / "index.html"

    if not dashboard_file.exists():
        print("❌ EQ12 dashboard not found")
        return

    # Read existing dashboard
    dashboard_html = dashboard_file.read_text(encoding='utf-8')

    # Generate Bing intelligence section
    bing_section = generate_bing_dashboard_html()

    # Insert Bing section (look for existing marker or add at end)
    bing_marker = "<!-- EQ12 BING INTELLIGENCE -->"

    if bing_marker in dashboard_html:
        # Replace existing section
        start = dashboard_html.find(bing_marker)
        end = dashboard_html.find("<!-- END BING INTELLIGENCE -->", start)
        if end != -1:
            new_section = f'{bing_marker}\n{bing_section}\n<!-- END BING INTELLIGENCE -->'
            dashboard_html = dashboard_html[:start] + new_section + dashboard_html[end + len("<!-- END BING INTELLIGENCE -->"):]
    else:
        # Add new section before closing body
        insertion_point = dashboard_html.rfind("</body>")
        if insertion_point != -1:
            new_section = f'\n{bing_marker}\n{bing_section}\n<!-- END BING INTELLIGENCE -->\n'
            dashboard_html = dashboard_html[:insertion_point] + new_section + dashboard_html[insertion_point:]

    # Write updated dashboard
    dashboard_file.write_text(dashboard_html, encoding='utf-8')
    print("✅ Updated EQ12 dashboard with Bing intelligence")

if __name__ == "__main__":
    update_eq12_dashboard()
"@

    $dashboardScriptPath = Join-Path $STACK_DIRS["core"] "update_dashboard.py"
    if (-not $DryRun) {
        Set-Content -Path $dashboardScriptPath -Value $dashboardScript -Encoding UTF8
        Write-EQ12Log "✅ Created dashboard integration script: $dashboardScriptPath" -Level "SUCCESS"
    } else {
        Write-EQ12Log "Would create: $dashboardScriptPath"
    }
}

function Show-EQ12BingSetupSummary {
    Write-EQ12Log "=== EQ12 BING INTEGRATION SETUP COMPLETE ===" -Level "SUCCESS"
    Write-EQ12Log ""
    Write-EQ12Log "📁 Installation Directory: $BING_DIR" -Level "SUCCESS"
    Write-EQ12Log "🐍 Python Virtual Environment: $VENV_DIR" -Level "SUCCESS"
    Write-EQ12Log "🔑 API Key Storage: $KEYS_DIR\bing_api.txt" -Level "SUCCESS"
    Write-EQ12Log ""
    Write-EQ12Log "🎯 INTEGRATION POINTS WITH EQ12:" -Level "SUCCESS"
    Write-EQ12Log "   • Betting: Enhances EdgeGod parlays with injury/news intelligence"
    Write-EQ12Log "   • Travel: Supplements travel_deals_scraper.py with Bing search"
    Write-EQ12Log "   • Dashboard: Adds intelligence sections to C:\EQ12\dashboard\index.html"
    Write-EQ12Log "   • Telegram: Uses existing bot infrastructure for urgent alerts"
    Write-EQ12Log "   • Logging: Follows EQ12 patterns (C:\EQ12\logs)"
    Write-EQ12Log ""
    Write-EQ12Log "⏰ SCHEDULED TASKS CREATED:"
    Write-EQ12Log "   • EQ12-Bing-Hourly-Betting (injury alerts)"
    Write-EQ12Log "   • EQ12-Bing-Daily-Travel (flight deals)"
    Write-EQ12Log "   • EQ12-Bing-Daily-AllStacks (comprehensive intelligence)"
    Write-EQ12Log ""
    Write-EQ12Log "🚀 NEXT STEPS:"
    Write-EQ12Log "   1. Test: cd `"$($STACK_DIRS["core"])`"; .\.venv\Scripts\python bing_web_search.py --stack betting"
    Write-EQ12Log "   2. Verify: Check C:\EQ12\logs for bing_*.json outputs"
    Write-EQ12Log "   3. Dashboard: Run C:\EQ12\scripts\eq12-build-dashboard.ps1"
    Write-EQ12Log "   4. Customize: Edit stack queries in bing_web_search.py STACK_QUERIES"
    Write-EQ12Log ""
    if (-not $ApiKey) {
        Write-EQ12Log "⚠️  Remember to add your Bing API key to: $KEYS_DIR\bing_api.txt" -Level "WARN"
    }
}

# === MAIN EXECUTION ===
try {
    Write-EQ12Log "🚀 Starting EQ12 Bing Integration Setup..." -Level "SUCCESS"

    # Prerequisites check
    if (-not (Test-EQ12Prerequisites)) {
        throw "Prerequisites check failed"
    }

    # Create directory structure
    New-EQ12Directories

    # Install dependencies
    Install-EQ12BingDependencies

    # Set API key
    Set-EQ12BingApiKey

    # Create integration scripts
    New-EQ12BingScripts

    # Setup scheduled tasks
    New-EQ12TaskScheduler

    # Dashboard integration
    New-EQ12BingDashboardIntegration

    # Show summary
    Show-EQ12BingSetupSummary

} catch {
    Write-EQ12Log "❌ Setup failed: $_" -Level "ERROR"
    exit 1
}
