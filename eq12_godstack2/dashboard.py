#!/usr/bin/env python3
"""
EQ12 GODSTACK Dashboard
FastAPI-based web interface for browsing and managing EQ12 GODSTACK results.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import os
import sqlite3
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Database configuration
DB_PATH = os.getenv("META_DB_PATH", "meta_search.sqlite3")

app = FastAPI(
    title="EQ12 GODSTACK Dashboard",
    description="Web interface for EQ12 GODSTACK search results and offers",
    version="1.0.0",
)

# Templates setup (create basic HTML templates)
templates = Jinja2Templates(directory="templates")


# Database helper functions
def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)


def dict_factory(cursor, row):
    """Convert sqlite3 row to dict"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# API Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""

    # Get basic stats
    with get_db_connection() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        stats = {}

        # Results stats
        try:
            cursor.execute("SELECT COUNT(*) as count FROM results")
            stats["total_results"] = cursor.fetchone()["count"]

            cursor.execute(
                "SELECT COUNT(*) as count FROM results WHERE DATE(fetched_at) = DATE('now')"
            )
            stats["today_results"] = cursor.fetchone()["count"]
        except:
            stats["total_results"] = 0
            stats["today_results"] = 0

        # Offers stats
        try:
            cursor.execute("SELECT COUNT(*) as count FROM offers")
            stats["total_offers"] = cursor.fetchone()["count"]

            cursor.execute(
                "SELECT COUNT(*) as count FROM offers WHERE DATE(fetched_at) = DATE('now')"
            )
            stats["today_offers"] = cursor.fetchone()["count"]
        except:
            stats["total_offers"] = 0
            stats["today_offers"] = 0

        # Recent activity
        recent_results = []
        try:
            cursor.execute(
                """
                SELECT query, title, source, fetched_at
                FROM results
                ORDER BY fetched_at DESC
                LIMIT 10
            """
            )
            recent_results = cursor.fetchall()
        except:
            pass

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 GODSTACK Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .section {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .nav-buttons {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }}
        .btn {{ padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; }}
        .btn:hover {{ background: #5a67d8; }}
        .btn-success {{ background: #48bb78; }}
        .btn-warning {{ background: #ed8936; }}
        .btn-danger {{ background: #f56565; }}
        .recent-item {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .recent-item:last-child {{ border-bottom: none; }}
        .query {{ font-weight: bold; color: #667eea; }}
        .source {{ color: #666; font-size: 0.9em; }}
        .timestamp {{ color: #999; font-size: 0.8em; float: right; }}
        .actions {{ display: flex; gap: 10px; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 EQ12 GODSTACK Dashboard</h1>
            <p>Comprehensive search intelligence and offer management</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{stats["total_results"]}</div>
                <div class="stat-label">Total Results</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats["today_results"]}</div>
                <div class="stat-label">Today's Results</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats["total_offers"]}</div>
                <div class="stat-label">Total Offers</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats["today_offers"]}</div>
                <div class="stat-label">Today's Offers</div>
            </div>
        </div>

        <div class="nav-buttons">
            <a href="/results" class="btn">📋 Browse Results</a>
            <a href="/offers" class="btn">💰 Browse Offers</a>
            <a href="/search" class="btn">🔍 Search</a>
            <a href="/analytics" class="btn">📊 Analytics</a>
            <a href="/tools" class="btn btn-success">🛠️ Tools</a>
        </div>

        <div class="section">
            <h2>🕒 Recent Activity</h2>
            {"<p>No recent activity</p>" if not recent_results else ""}
            {
        "".join(
            [
                f'''
            <div class="recent-item">
                <span class="query">{result["query"]}</span>
                <span class="timestamp">{result["fetched_at"]}</span><br>
                <span>{result["title"]}</span><br>
                <span class="source">Source: {result["source"]}</span>
            </div>
            '''
                for result in recent_results
            ]
        )
    }
        </div>

        <div class="section">
            <h2>⚡ Quick Actions</h2>
            <div class="actions">
                <button class="btn btn-success" onclick="runScript('news_aggregator')">Run News Aggregator</button>
                <button class="btn btn-warning" onclick="runScript('swagbucks_offers')">Scrape Swagbucks</button>
                <button class="btn btn-danger" onclick="runScript('enrichment')">Generate Analysis</button>
                <button class="btn" onclick="runScript('meta_search')">Meta Search</button>
            </div>
        </div>
    </div>

    <script>
        function runScript(scriptName) {{
            fetch(`/api/run/${{scriptName}}`, {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        alert(`${{scriptName}} started successfully!`);
                    }} else {{
                        alert(`Error: ${{data.error}}`);
                    }}
                }});
        }}
    </script>
</body>
</html>
    """

    return HTMLResponse(content=html_content)


@app.get("/results")
async def browse_results(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    query: str | None = Query(None),
    source: str | None = Query(None),
    hours: int | None = Query(None),
):
    """Browse search results with pagination and filtering"""

    offset = (page - 1) * limit
    where_clauses = []
    params = []

    if query:
        where_clauses.append("query LIKE ?")
        params.append(f"%{query}%")

    if source:
        where_clauses.append("source = ?")
        params.append(source)

    if hours:
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        where_clauses.append("fetched_at >= ?")
        params.append(cutoff.isoformat())

    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    with get_db_connection() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        # Get total count
        count_sql = f"SELECT COUNT(*) as total FROM results{where_sql}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]

        # Get results
        results_sql = f"""
            SELECT query, title, url, snippet, source, published_at, fetched_at
            FROM results{where_sql}
            ORDER BY fetched_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(results_sql, [*params, limit, offset])
        results = cursor.fetchall()

    return {
        "results": results,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,
        },
        "filters": {"query": query, "source": source, "hours": hours},
    }


@app.get("/offers")
async def browse_offers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
):
    """Browse Swagbucks offers with pagination"""

    offset = (page - 1) * limit
    where_clauses = []
    params = []

    if category:
        where_clauses.append("category = ?")
        params.append(category)

    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    try:
        with get_db_connection() as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()

            # Check if offers table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='offers'")
            if not cursor.fetchone():
                return {
                    "error": "Offers table not found",
                    "results": [],
                    "pagination": {"total": 0},
                }

            # Get total count
            count_sql = f"SELECT COUNT(*) as total FROM offers{where_sql}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()["total"]

            # Get offers
            offers_sql = f"""
                SELECT title, url, reward, category, source, fetched_at
                FROM offers{where_sql}
                ORDER BY fetched_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(offers_sql, [*params, limit, offset])
            offers = cursor.fetchall()

        return {
            "results": offers,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit,
            },
        }
    except Exception as e:
        return {"error": str(e), "results": [], "pagination": {"total": 0}}


@app.get("/search")
async def search_interface(request: Request):
    """Search interface page"""

    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 GODSTACK - Search</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; }
        .search-box { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        .btn { padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        .btn:hover { background: #5a67d8; }
        .results { margin-top: 30px; }
        .result-item { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 1px 5px rgba(0,0,0,0.1); }
        .result-title { font-weight: bold; color: #667eea; margin-bottom: 5px; }
        .result-url { color: #666; font-size: 0.9em; }
        .back-btn { margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="back-btn">
            <a href="/" class="btn">← Back to Dashboard</a>
        </div>

        <div class="search-box">
            <h1>🔍 Search EQ12 GODSTACK</h1>

            <form id="searchForm">
                <div class="form-group">
                    <label for="query">Search Query:</label>
                    <input type="text" id="query" name="query" placeholder="Enter your search query..." required>
                </div>

                <div class="form-group">
                    <label for="source">Filter by Source:</label>
                    <select id="source" name="source">
                        <option value="">All Sources</option>
                        <option value="bing">Bing</option>
                        <option value="google">Google</option>
                        <option value="news">News</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="hours">Time Range (hours):</label>
                    <select id="hours" name="hours">
                        <option value="">All Time</option>
                        <option value="1">Last Hour</option>
                        <option value="6">Last 6 Hours</option>
                        <option value="24">Last 24 Hours</option>
                        <option value="168">Last Week</option>
                    </select>
                </div>

                <button type="submit" class="btn">Search Results</button>
            </form>
        </div>

        <div id="results" class="results" style="display: none;"></div>
    </div>

    <script>
        document.getElementById('searchForm').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(e.target);
            const params = new URLSearchParams();

            for (let [key, value] of formData.entries()) {
                if (value) params.append(key, value);
            }

            fetch('/results?' + params.toString())
                .then(response => response.json())
                .then(data => {
                    const resultsDiv = document.getElementById('results');

                    if (data.results && data.results.length > 0) {
                        const resultsHtml = data.results.map(result => `
                            <div class="result-item">
                                <div class="result-title">${result.title || 'No title'}</div>
                                <div class="result-url">
                                    <a href="${result.url}" target="_blank">${result.url}</a>
                                    | Source: ${result.source}
                                    | Query: ${result.query}
                                </div>
                                ${result.snippet ? `<div style="margin-top: 5px; color: #666;">${result.snippet}</div>` : ''}
                            </div>
                        `).join('');

                        resultsDiv.innerHTML = `
                            <h2>Search Results (${data.pagination.total} total)</h2>
                            ${resultsHtml}
                        `;
                    } else {
                        resultsDiv.innerHTML = '<h2>No results found</h2>';
                    }

                    resultsDiv.style.display = 'block';
                })
                .catch(error => {
                    console.error('Search error:', error);
                    document.getElementById('results').innerHTML = '<h2>Search error occurred</h2>';
                });
        });
    </script>
</body>
</html>
    """

    return HTMLResponse(content=html_content)


@app.get("/analytics")
async def analytics_page(request: Request):
    """Analytics and statistics page"""

    with get_db_connection() as conn:
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        analytics = {}

        try:
            # Query frequency
            cursor.execute(
                """
                SELECT query, COUNT(*) as count
                FROM results
                GROUP BY query
                ORDER BY count DESC
                LIMIT 10
            """
            )
            analytics["top_queries"] = cursor.fetchall()

            # Source distribution
            cursor.execute(
                """
                SELECT source, COUNT(*) as count
                FROM results
                GROUP BY source
                ORDER BY count DESC
            """
            )
            analytics["source_distribution"] = cursor.fetchall()

            # Daily activity (last 7 days)
            cursor.execute(
                """
                SELECT DATE(fetched_at) as date, COUNT(*) as count
                FROM results
                WHERE fetched_at >= datetime('now', '-7 days')
                GROUP BY DATE(fetched_at)
                ORDER BY date DESC
            """
            )
            analytics["daily_activity"] = cursor.fetchall()

        except Exception as e:
            analytics["error"] = str(e)

    # Generate analytics HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 GODSTACK - Analytics</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        .section {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .chart {{ display: flex; flex-direction: column; gap: 5px; }}
        .bar {{ background: linear-gradient(to right, #667eea, #764ba2); color: white; padding: 8px; border-radius: 4px; }}
        .bar-label {{ font-weight: bold; }}
        .bar-value {{ float: right; }}
        .back-btn {{ margin-bottom: 20px; }}
        .btn {{ padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="back-btn">
            <a href="/" class="btn">← Back to Dashboard</a>
        </div>

        <div class="section">
            <h1>📊 EQ12 GODSTACK Analytics</h1>
        </div>

        <div class="section">
            <h2>🔥 Top Queries</h2>
            <div class="chart">
                {"".join([f'<div class="bar"><span class="bar-label">{q["query"]}</span><span class="bar-value">{q["count"]}</span></div>' for q in analytics.get("top_queries", [])]) if analytics.get("top_queries") else "<p>No query data available</p>"}
            </div>
        </div>

        <div class="section">
            <h2>📡 Source Distribution</h2>
            <div class="chart">
                {"".join([f'<div class="bar"><span class="bar-label">{s["source"]}</span><span class="bar-value">{s["count"]}</span></div>' for s in analytics.get("source_distribution", [])]) if analytics.get("source_distribution") else "<p>No source data available</p>"}
            </div>
        </div>

        <div class="section">
            <h2>📅 Daily Activity (Last 7 Days)</h2>
            <div class="chart">
                {"".join([f'<div class="bar"><span class="bar-label">{d["date"]}</span><span class="bar-value">{d["count"]} results</span></div>' for d in analytics.get("daily_activity", [])]) if analytics.get("daily_activity") else "<p>No activity data available</p>"}
            </div>
        </div>
    </div>
</body>
</html>
    """

    return HTMLResponse(content=html_content)


@app.get("/tools")
async def tools_page(request: Request):
    """Tools and utilities page"""

    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>EQ12 GODSTACK - Tools</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; }
        .section { background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .tool-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .tool-card { border: 1px solid #ddd; padding: 15px; border-radius: 8px; }
        .tool-title { font-weight: bold; margin-bottom: 10px; color: #667eea; }
        .tool-description { color: #666; margin-bottom: 15px; }
        .btn { padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #5a67d8; }
        .btn-success { background: #48bb78; }
        .btn-warning { background: #ed8936; }
        .btn-danger { background: #f56565; }
        .back-btn { margin-bottom: 20px; }
        .output { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px; margin-top: 10px; font-family: monospace; white-space: pre-wrap; max-height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="back-btn">
            <a href="/" class="btn">← Back to Dashboard</a>
        </div>

        <div class="section">
            <h1>🛠️ EQ12 GODSTACK Tools</h1>
            <p>Manage and execute GODSTACK operations</p>
        </div>

        <div class="section">
            <h2>📡 Data Collection Tools</h2>
            <div class="tool-grid">
                <div class="tool-card">
                    <div class="tool-title">📰 News Aggregator</div>
                    <div class="tool-description">Collect latest news from Bing News API and Google News RSS</div>
                    <button class="btn btn-success" onclick="runTool('news_aggregator', '--query general')">Run News Collection</button>
                    <div id="news_aggregator_output" class="output" style="display: none;"></div>
                </div>

                <div class="tool-card">
                    <div class="tool-title">💰 Swagbucks Scraper</div>
                    <div class="tool-description">Scrape latest Swagbucks offers and deals</div>
                    <button class="btn btn-warning" onclick="runTool('swagbucks_offers', '')">Scrape Offers</button>
                    <div id="swagbucks_offers_output" class="output" style="display: none;"></div>
                </div>

                <div class="tool-card">
                    <div class="tool-title">🔍 Meta Search</div>
                    <div class="tool-description">Dual-engine Google + Bing search with deduplication</div>
                    <button class="btn" onclick="runCustomSearch()">Custom Search</button>
                    <div id="meta_search_output" class="output" style="display: none;"></div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🧠 Intelligence Tools</h2>
            <div class="tool-grid">
                <div class="tool-card">
                    <div class="tool-title">📊 GPT Enrichment</div>
                    <div class="tool-description">Analyze recent results with GPT intelligence</div>
                    <select id="stack_select">
                        <option value="general">General</option>
                        <option value="betting">Betting</option>
                        <option value="travel">Travel</option>
                        <option value="cannabis">Cannabis</option>
                        <option value="finance">Finance</option>
                        <option value="fleet">Fleet</option>
                        <option value="auto">Auto-detect</option>
                    </select>
                    <button class="btn btn-danger" onclick="runEnrichment()">Generate Analysis</button>
                    <div id="enrichment_output" class="output" style="display: none;"></div>
                </div>

                <div class="tool-card">
                    <div class="tool-title">🔤 Autosuggest</div>
                    <div class="tool-description">Generate keyword suggestions for SEO and content</div>
                    <input type="text" id="autosuggest_query" placeholder="Enter query...">
                    <button class="btn" onclick="runAutosuggest()">Get Suggestions</button>
                    <div id="autosuggest_output" class="output" style="display: none;"></div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>⚙️ System Tools</h2>
            <div class="tool-grid">
                <div class="tool-card">
                    <div class="tool-title">🗄️ Database Status</div>
                    <div class="tool-description">Check database health and statistics</div>
                    <button class="btn" onclick="checkDatabase()">Check DB</button>
                    <div id="database_output" class="output" style="display: none;"></div>
                </div>

                <div class="tool-card">
                    <div class="tool-title">🧹 Cleanup Tools</div>
                    <div class="tool-description">Clean old data and optimize database</div>
                    <button class="btn btn-warning" onclick="cleanupDatabase()">Cleanup DB</button>
                    <div id="cleanup_output" class="output" style="display: none;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function runTool(tool, args) {
            const outputDiv = document.getElementById(tool + '_output');
            outputDiv.style.display = 'block';
            outputDiv.textContent = 'Running ' + tool + '...';

            fetch(`/api/run/${tool}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({args: args})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    outputDiv.textContent = `✅ ${tool} completed successfully!\\n\\nOutput:\\n${data.output || 'No output'}`;
                } else {
                    outputDiv.textContent = `❌ ${tool} failed:\\n${data.error}`;
                }
            })
            .catch(error => {
                outputDiv.textContent = `❌ Error running ${tool}:\\n${error}`;
            });
        }

        function runEnrichment() {
            const stack = document.getElementById('stack_select').value;
            const outputDiv = document.getElementById('enrichment_output');
            outputDiv.style.display = 'block';
            outputDiv.textContent = `Running enrichment analysis for ${stack} stack...`;

            fetch('/api/run/enrichment', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({args: `--stack ${stack} --hours 24`})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    outputDiv.textContent = `✅ Enrichment completed!\\n\\n${data.output || 'Analysis generated'}`;
                } else {
                    outputDiv.textContent = `❌ Enrichment failed:\\n${data.error}`;
                }
            });
        }

        function runCustomSearch() {
            const query = prompt('Enter search query:');
            if (query) {
                runTool('meta_search', `--query "${query}"`);
            }
        }

        function runAutosuggest() {
            const query = document.getElementById('autosuggest_query').value;
            if (query) {
                runTool('autosuggest_merge', `--query "${query}" --json`);
            } else {
                alert('Please enter a query');
            }
        }

        function checkDatabase() {
            fetch('/api/database/status')
            .then(response => response.json())
            .then(data => {
                const outputDiv = document.getElementById('database_output');
                outputDiv.style.display = 'block';
                outputDiv.textContent = JSON.stringify(data, null, 2);
            });
        }

        function cleanupDatabase() {
            if (confirm('This will remove old data. Continue?')) {
                fetch('/api/database/cleanup', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    const outputDiv = document.getElementById('cleanup_output');
                    outputDiv.style.display = 'block';
                    outputDiv.textContent = JSON.stringify(data, null, 2);
                });
            }
        }
    </script>
</body>
</html>
    """

    return HTMLResponse(content=html_content)


# API endpoints for tool execution
@app.post("/api/run/{tool}")
async def run_tool(tool: str, request: Request):
    """Execute GODSTACK tools via API"""

    try:
        body = await request.json()
        args = body.get("args", "")
    except:
        args = ""

    # Tool mapping
    tool_commands = {
        "news_aggregator": f"python news_aggregator.py {args}",
        "swagbucks_offers": f"python swagbucks_offers.py {args}",
        "meta_search": f"python meta_search.py {args}",
        "enrichment": f"python enrichment.py {args}",
        "autosuggest_merge": f"python autosuggest_merge.py {args}",
    }

    if tool not in tool_commands:
        return {"success": False, "error": f"Unknown tool: {tool}"}

    try:
        # Run the tool command
        result = subprocess.run(
            tool_commands[tool],
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path(__file__).parent,
        )

        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else None,
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Tool execution timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/database/status")
async def database_status():
    """Get database status and statistics"""

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            status = {}

            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            status["tables"] = tables

            # Get counts for each table
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    status[f"{table}_count"] = cursor.fetchone()[0]
                except:
                    status[f"{table}_count"] = "error"

            # Database file size
            db_path = Path(DB_PATH)
            if db_path.exists():
                status["db_size_mb"] = round(db_path.stat().st_size / 1024 / 1024, 2)

            return status

    except Exception as e:
        return {"error": str(e)}


@app.post("/api/database/cleanup")
async def cleanup_database():
    """Cleanup old database entries"""

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Delete entries older than 30 days
            cutoff = datetime.now(UTC) - timedelta(days=30)

            cleanup_results = {}

            # Clean results table
            try:
                cursor.execute("DELETE FROM results WHERE fetched_at < ?", (cutoff.isoformat(),))
                cleanup_results["results_deleted"] = cursor.rowcount
            except:
                cleanup_results["results_deleted"] = "error"

            # Clean offers table
            try:
                cursor.execute("DELETE FROM offers WHERE fetched_at < ?", (cutoff.isoformat(),))
                cleanup_results["offers_deleted"] = cursor.rowcount
            except:
                cleanup_results["offers_deleted"] = "error"

            # Vacuum database
            cursor.execute("VACUUM")
            cleanup_results["vacuum"] = "completed"

            conn.commit()

            return {"success": True, "results": cleanup_results}

    except Exception as e:
        return {"success": False, "error": str(e)}


# Main entry point
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
