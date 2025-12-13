#!/usr/bin/env python
import os
import sqlite3
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

# Add meta search directory to path for HumanLayer integration
PROJECT_DIR = Path("C:/EQ12/eq12_meta_search")
if PROJECT_DIR.exists():
    sys.path.insert(0, str(PROJECT_DIR))
    try:
        from hlayer_wrapper import analyze_cross_stack_patterns, query_codebase

        HLAYER_AVAILABLE = True
    except ImportError:
        HLAYER_AVAILABLE = False
else:
    HLAYER_AVAILABLE = False

DB_PATH = os.getenv("META_DB_PATH", "meta_search.sqlite3")

app = FastAPI(title="EQ12 GODSTACK Dashboard - Enhanced with HumanLayer")


def query_db(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(sql, params)
    cols = [c[0] for c in cur.description]
    rows = [dict(zip(cols, r, strict=False)) for r in cur.fetchall()]
    conn.close()
    return rows


@app.get("/", response_class=HTMLResponse)
def home():
    hlayer_status = "✅ Available" if HLAYER_AVAILABLE else "❌ Not Available"

    return f"""
    <h2>🚀 EQ12 GODSTACK Dashboard - Enhanced</h2>
    <p><strong>HumanLayer Integration:</strong> {hlayer_status}</p>

    <h3>📊 Data Endpoints</h3>
    <ul>
      <li><a href='/results'>Latest Search Results</a></li>
      <li><a href='/offers'>Latest Offers</a></li>
      <li><a href='/trending'>Trending Repos</a></li>
    </ul>

    <h3>🤖 AI Intelligence</h3>
    <ul>
      <li><a href='/humanlayer?q=Where are Telegram messages sent?'>HumanLayer Query Example</a></li>
      <li><a href='/cross-stack-analysis'>Cross-Stack Pattern Analysis</a></li>
      <li><a href='/devtools-status'>DevTools Agent Status</a></li>
    </ul>

    <h3>📈 Monitoring</h3>
    <ul>
      <li><a href='/health'>System Health</a></li>
      <li><a href='/stats'>Database Statistics</a></li>
    </ul>
    """


@app.get("/results")
def get_results(q: str = Query(None, description="Filter by query")):
    if q:
        rows = query_db(
            "SELECT query,title,url,snippet,source,fetched_at FROM results WHERE query LIKE ? ORDER BY fetched_at DESC LIMIT 100",
            (f"%{q}%",),
        )
    else:
        rows = query_db(
            "SELECT query,title,url,snippet,source,fetched_at FROM results ORDER BY fetched_at DESC LIMIT 100"
        )
    return rows


@app.get("/offers")
def get_offers():
    rows = query_db(
        "SELECT source,title,url,reward,category,fetched_at FROM offers ORDER BY fetched_at DESC LIMIT 100"
    )
    return rows


@app.get("/trending")
def get_trending_repos():
    """Get trending GitHub repositories from database."""
    try:
        rows = query_db(
            """
            SELECT name, url, description, language, stars_today, stars_total,
                   scraped_date, enrichment_status
            FROM trending_repos
            ORDER BY stars_today DESC, scraped_date DESC
            LIMIT 50
        """
        )
        return rows
    except:
        return {"error": "Trending repos table not available"}


@app.get("/humanlayer")
def humanlayer_query(q: str = Query(..., description="Question about EQ12 codebase")):
    """Query EQ12 codebase using HumanLayer AI analysis."""
    if not HLAYER_AVAILABLE:
        raise HTTPException(status_code=503, detail="HumanLayer integration not available")

    try:
        result = query_codebase(q)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HumanLayer query failed: {e!s}")


@app.get("/cross-stack-analysis")
def cross_stack_analysis():
    """Analyze patterns across EQ12 business stacks."""
    if not HLAYER_AVAILABLE:
        raise HTTPException(status_code=503, detail="HumanLayer integration not available")

    try:
        result = analyze_cross_stack_patterns()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cross-stack analysis failed: {e!s}")


@app.get("/devtools-status")
def devtools_status():
    """Check DevTools agent availability and configuration."""
    devtools_enabled = os.getenv("EQ12_DEVTOOLS_ENABLED", "false").lower() == "true"
    devtools_port = os.getenv("EQ12_DEVTOOLS_PORT", "9222")

    return {
        "devtools_enabled": devtools_enabled,
        "devtools_port": int(devtools_port),
        "chrome_available": True,  # Could add actual Chrome detection
        "mcp_integration": "placeholder",  # Would check actual MCP connection
        "status": "ready" if devtools_enabled else "disabled",
    }


@app.get("/health")
def system_health():
    """Get overall system health status."""
    health = {
        "database": "unknown",
        "telegram": "unknown",
        "openai": "unknown",
        "hlayer": HLAYER_AVAILABLE,
        "devtools": os.getenv("EQ12_DEVTOOLS_ENABLED", "false").lower() == "true",
    }

    # Check database
    try:
        query_db("SELECT COUNT(*) as count FROM sqlite_master")
        health["database"] = "connected"
    except:
        health["database"] = "error"

    # Check environment variables
    health["telegram"] = "configured" if os.getenv("TELEGRAM_BOT_TOKEN") else "missing"
    health["openai"] = "configured" if os.getenv("OPENAI_SERVICE_KEY") else "missing"

    return health


@app.get("/stats")
def database_stats():
    """Get database statistics and table information."""
    stats = {}

    try:
        # Get table names
        tables = query_db("SELECT name FROM sqlite_master WHERE type='table'")

        for table in tables:
            table_name = table["name"]
            try:
                count_result = query_db(f"SELECT COUNT(*) as count FROM {table_name}")
                stats[table_name] = count_result[0]["count"] if count_result else 0
            except:
                stats[table_name] = "error"

        return {"tables": stats, "total_tables": len(tables), "database_path": DB_PATH}
    except Exception as e:
        return {"error": f"Database stats failed: {e!s}"}
