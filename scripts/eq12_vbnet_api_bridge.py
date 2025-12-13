#!/usr/bin/env python3
"""
EQ12 VB.NET API Bridge - Python Integration Layer
==================================================
Purpose: Call VB.NET API clients from Python automation scripts
Enables seamless interop between .NET compiled modules and Python workflows
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import sqlite3
from datetime import datetime

class VBNetApiBridge:
    """
    Python bridge to VB.NET API orchestrator
    Calls compiled .NET executables and parses JSON output
    """
    
    def __init__(self, vbnet_exe_path: Optional[str] = None):
        """
        Initialize bridge with path to compiled VB.NET executable
        
        Args:
            vbnet_exe_path: Path to BettingOrchestrator.exe (auto-detected if None)
        """
        if vbnet_exe_path is None:
            # Auto-detect in visual_studio_projects
            project_dir = Path(r"C:\EQ12_BROKEN_20251122_210342\visual_studio_projects")
            exe_search = list(project_dir.rglob("BettingOrchestrator.exe"))
            
            if exe_search:
                self.vbnet_exe = str(exe_search[0])
            else:
                raise FileNotFoundError(
                    "BettingOrchestrator.exe not found. Build the VB.NET project first."
                )
        else:
            self.vbnet_exe = vbnet_exe_path
        
        self.logs_dir = Path(r"C:\EQ12_BROKEN_20251122_210342\logs")
        self.db_path = self.logs_dir / "betting_data.db"
    
    def call_vbnet(self, command: str, args: List[str] = None) -> subprocess.CompletedProcess:
        """
        Execute VB.NET orchestrator with given command
        
        Args:
            command: Command to pass (odds, scores, stocks, etc.)
            args: Additional arguments
            
        Returns:
            CompletedProcess object with stdout/stderr
        """
        cmd_args = [self.vbnet_exe, command]
        if args:
            cmd_args.extend(args)
        
        print(f"[VB.NET CALL] {' '.join(cmd_args)}")
        
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"[ERROR] VB.NET call failed: {result.stderr}")
        
        return result
    
    def get_odds(self, sport: str = "upcoming", region: str = "us") -> Dict[str, Any]:
        """
        Fetch betting odds via VB.NET API client
        
        Args:
            sport: Sport identifier (upcoming, americanfootball_nfl, basketball_nba, etc.)
            region: Bookmaker region (us, uk, au)
            
        Returns:
            Dictionary with odds data
        """
        self.call_vbnet("odds", [sport, region])
        
        # Read generated JSON
        json_path = self.logs_dir / "latest_odds.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        else:
            return {"error": "No odds data generated"}
    
    def get_scores(self, sport: str = "football", league: str = "nfl") -> Dict[str, Any]:
        """
        Fetch live scores via VB.NET ESPN API client
        
        Args:
            sport: Sport type (football, basketball, baseball, etc.)
            league: League identifier (nfl, nba, mlb, etc.)
            
        Returns:
            Dictionary with scores data
        """
        self.call_vbnet("scores", [sport, league])
        
        json_path = self.logs_dir / f"{league}_scores.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        else:
            return {"error": "No scores data generated"}
    
    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch stock quote via VB.NET Alpha Vantage API client
        
        Args:
            symbol: Stock ticker symbol (SPY, AAPL, TSLA, etc.)
            
        Returns:
            Dictionary with stock quote data
        """
        self.call_vbnet("stocks", [symbol])
        
        # Query from SQLite database
        if self.db_path.exists():
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM stocks WHERE symbol = ? ORDER BY fetched_at DESC LIMIT 1",
                (symbol,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "symbol": row[1],
                    "price": row[2],
                    "change_percent": row[3],
                    "volume": row[4],
                    "fetched_at": row[5]
                }
        
        return {"error": "No stock data found"}
    
    def get_crypto_data(self, coin_id: str = "bitcoin") -> Dict[str, Any]:
        """
        Fetch cryptocurrency data via VB.NET CoinGecko API client
        
        Args:
            coin_id: Coin identifier (bitcoin, ethereum, etc.)
            
        Returns:
            Dictionary with crypto market data
        """
        self.call_vbnet("crypto", [coin_id])
        
        json_path = self.logs_dir / f"crypto_{coin_id}.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        else:
            return {"error": "No crypto data generated"}
    
    def get_flight_deals(self, departure: str = "BUF", arrival: str = "LAX") -> Dict[str, Any]:
        """
        Fetch flight deals via VB.NET Aviationstack API client
        
        Args:
            departure: Departure airport code (BUF, JFK, etc.)
            arrival: Arrival airport code (LAX, SFO, etc.)
            
        Returns:
            Dictionary with flight data
        """
        self.call_vbnet("flights", [departure, arrival])
        
        json_path = self.logs_dir / f"flights_{departure}_{arrival}.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        else:
            return {"error": "No flight data generated"}
    
    def get_news(self, category: str = "sports", country: str = "us") -> Dict[str, Any]:
        """
        Fetch news headlines via VB.NET NewsAPI client
        
        Args:
            category: News category (sports, business, technology, etc.)
            country: Country code (us, uk, ca, etc.)
            
        Returns:
            Dictionary with news articles
        """
        self.call_vbnet("news", [category, country])
        
        json_path = self.logs_dir / f"news_{category}.json"
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        else:
            return {"error": "No news data generated"}
    
    def run_full_pipeline(self) -> subprocess.CompletedProcess:
        """
        Execute full VB.NET data pipeline (all APIs)
        
        Returns:
            CompletedProcess with pipeline output
        """
        return self.call_vbnet("all")
    
    def test_all_apis(self) -> subprocess.CompletedProcess:
        """
        Test all API endpoints via VB.NET orchestrator
        
        Returns:
            CompletedProcess with test results
        """
        return self.call_vbnet("test")


def example_usage():
    """
    Example: Integrate VB.NET API calls into Python automation workflow
    """
    print("=== EQ12 Python-VB.NET Integration Example ===\n")
    
    # Initialize bridge
    bridge = VBNetApiBridge()
    
    # Example 1: Get betting odds
    print("[1] Fetching NFL betting odds...")
    odds = bridge.get_odds(sport="americanfootball_nfl", region="us")
    print(f"    Result: {len(odds.get('events', []))} events found\n")
    
    # Example 2: Get live scores
    print("[2] Fetching NBA scores...")
    scores = bridge.get_scores(sport="basketball", league="nba")
    print(f"    Result: {scores.get('status', 'N/A')}\n")
    
    # Example 3: Get stock data
    print("[3] Fetching stock quote for SPY...")
    stock = bridge.get_stock_data("SPY")
    print(f"    Result: ${stock.get('price', 'N/A')} ({stock.get('change_percent', 'N/A')})\n")
    
    # Example 4: Get crypto data
    print("[4] Fetching Bitcoin market data...")
    crypto = bridge.get_crypto_data("bitcoin")
    if "market_data" in crypto:
        price = crypto["market_data"]["current_price"]["usd"]
        change = crypto["market_data"]["price_change_percentage_24h"]
        print(f"    Result: ${price:,.2f} ({change:+.2f}%)\n")
    
    # Example 5: Get flight deals
    print("[5] Fetching BUF → LAX flight deals...")
    flights = bridge.get_flight_deals("BUF", "LAX")
    print(f"    Result: {flights.get('status', 'N/A')}\n")
    
    # Example 6: Get news
    print("[6] Fetching sports news...")
    news = bridge.get_news(category="sports", country="us")
    if "articles" in news:
        print(f"    Result: {len(news['articles'])} articles found")
        for article in news["articles"][:3]:
            print(f"      • {article['title']}")
    
    print("\n=== Integration Complete ===")


def integrate_with_pi_cluster():
    """
    Example: Deploy VB.NET API polling to Raspberry Pi cluster
    (Requires .NET runtime on Pi or Docker containerization)
    """
    print("=== Pi Cluster Integration Strategy ===\n")
    
    print("Option 1: Dockerize VB.NET Orchestrator")
    print("  - Build .NET Docker image (mcr.microsoft.com/dotnet/runtime:8.0)")
    print("  - Deploy to Pi cluster via Docker Swarm or Ray")
    print("  - Each Pi polls different API endpoints in parallel")
    print()
    
    print("Option 2: Use Python bridge on EQ12, distribute results to Pis")
    print("  - EQ12 runs VB.NET orchestrator (Windows-native)")
    print("  - Python bridge fetches data and distributes to Pi workers")
    print("  - Pis process/analyze data (embeddings, classification, etc.)")
    print()
    
    print("Option 3: Port critical APIs to Python, run natively on Pis")
    print("  - Use Python requests library for simple REST APIs")
    print("  - Keep VB.NET for complex Windows-specific tasks")
    print("  - Best for lightweight distributed polling")
    print()
    
    print("Recommended: Option 2 (Hybrid - VB.NET on EQ12, Python on Pis)")


if __name__ == "__main__":
    example_usage()
    print("\n" + "="*60 + "\n")
    integrate_with_pi_cluster()
