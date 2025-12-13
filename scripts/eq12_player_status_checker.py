#!/usr/bin/env python3
"""
 EQ12 NBA Player Status Checker - Enhanced Real-Time Injury Reports
Integrates with multiple reliable sources for definitive player availability
"""

import requests
import json
import os
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from urllib.parse import urljoin
import hashlib

# Try to import BeautifulSoup for HTML parsing
try:
    from bs4 import BeautifulSoup
    HTML_PARSING_AVAILABLE = True
except ImportError:
    HTML_PARSING_AVAILABLE = False
    print(" BeautifulSoup not available - using JSON APIs only")


class PlayerStatusChecker:
    """
     Enhanced NBA Player Status Checker
    Multi-source injury report aggregation with caching and validation
    """
    
    def __init__(self, workspace: str = "C:/EQ12"):
        self.workspace = Path(workspace)
        self.cache_dir = self.workspace / "cache"
        self.logs_dir = self.workspace / "logs"
        
        # Create directories
        self.cache_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Cache files
        self.status_cache_file = self.cache_dir / "player_status_today.json"
        self.manual_overrides_file = self.cache_dir / "manual_player_overrides.json"
        
        # Setup logging
        self.setup_logging()
        
        # API endpoints and configurations
        self.api_sources = {
            "espn": {
                "url": "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news",
                "backup_url": "https://www.espn.com/nba/injuries",
                "enabled": True
            },
            "nba_official": {
                "url": "https://stats.nba.com/stats/leaguegamefinder",
                "enabled": False  # Requires more complex authentication
            },
            "cbs_sports": {
                "url": "https://www.cbssports.com/nba/injuries/",
                "enabled": HTML_PARSING_AVAILABLE
            },
            "rotowire": {
                "url": "https://www.rotowire.com/basketball/nba-lineups.php",
                "enabled": HTML_PARSING_AVAILABLE
            }
        }
        
        # Status mappings for different sources
        self.status_mappings = {
            "out": ["out", "inactive", "does not play", "dnp", "suspended", "away"],
            "doubtful": ["doubtful", "unlikely"],
            "questionable": ["questionable", "game time decision", "gtd"],
            "probable": ["probable", "likely"],
            "active": ["active", "available", "playing", "healthy", "cleared"]
        }
        
        # Load manual overrides
        self.manual_overrides = self.load_manual_overrides()
        
        self.logger.info(" Player status checker initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.logs_dir / f"player_status_checker_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("player_status_checker")
    
    def load_manual_overrides(self) -> Dict[str, Dict]:
        """Load manual player status overrides"""
        if not self.manual_overrides_file.exists():
            # Create default overrides for known situations
            default_overrides = {
                "lebron james": {
                    "status": "out",
                    "reason": "Load management - confirmed out for Nov 3",
                    "date": "2025-11-03",
                    "source": "manual_override"
                }
            }
            with open(self.manual_overrides_file, 'w') as f:
                json.dump(default_overrides, f, indent=2)
            return default_overrides
        
        try:
            with open(self.manual_overrides_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f" Failed to load manual overrides: {e}")
            return {}
    
    def normalize_status(self, raw_status: str) -> str:
        """Normalize status from different sources to standard format"""
        if not raw_status:
            return "unknown"
        
        raw_lower = raw_status.lower().strip()
        
        for standard_status, variants in self.status_mappings.items():
            if any(variant in raw_lower for variant in variants):
                return standard_status
        
        return "unknown"
    
    def fetch_espn_injuries(self) -> Dict[str, Dict]:
        """Fetch injury data from ESPN"""
        self.logger.info(" Fetching ESPN injury data...")
        players = {}
        
        try:
            # Try ESPN API first
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(
                self.api_sources["espn"]["url"],
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse ESPN news for injury information
                for article in data.get("articles", []):
                    headline = article.get("headline", "").lower()
                    description = article.get("description", "").lower()
                    
                    # Look for injury keywords
                    if any(keyword in headline or keyword in description 
                           for keyword in ["injury", "out", "questionable", "doubtful", "probable"]):
                        
                        # Extract player names and status (simplified pattern matching)
                        # This would need more sophisticated NLP in production
                        text = f"{headline} {description}"
                        
                        # Pattern matching for common injury report formats
                        patterns = [
                            r"(\w+\s+\w+)\s+(?:is\s+)?(?:ruled\s+)?(out|questionable|doubtful|probable)",
                            r"(\w+\s+\w+)\s+(?:will\s+)?(?:not\s+)?(play|sit)",
                            r"(\w+\s+\w+)\s+(?:remains\s+)?(active|available)"
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            for match in matches:
                                player_name = match[0].strip().title()
                                status = self.normalize_status(match[1])
                                
                                players[player_name.lower()] = {
                                    "name": player_name,
                                    "status": status,
                                    "source": "espn_api",
                                    "last_updated": datetime.now().isoformat(),
                                    "raw_status": match[1]
                                }
                
                self.logger.info(f" ESPN API: Found {len(players)} player updates")
            
        except Exception as e:
            self.logger.warning(f" ESPN API failed: {e}")
        
        return players
    
    def fetch_cbs_injuries(self) -> Dict[str, Dict]:
        """Fetch injury data from CBS Sports"""
        if not HTML_PARSING_AVAILABLE:
            return {}
        
        self.logger.info(" Fetching CBS Sports injury data...")
        players = {}
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(
                self.api_sources["cbs_sports"]["url"],
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for injury table or player status elements
                # CBS Sports typically has structured injury tables
                injury_rows = soup.find_all(['tr', 'div'], class_=lambda x: x and 'injury' in x.lower())
                
                for row in injury_rows:
                    try:
                        # Extract player name and status
                        name_elem = row.find(['td', 'span', 'div'], class_=lambda x: x and 'name' in x.lower())
                        status_elem = row.find(['td', 'span', 'div'], class_=lambda x: x and 'status' in x.lower())
                        
                        if name_elem and status_elem:
                            player_name = name_elem.get_text(strip=True)
                            raw_status = status_elem.get_text(strip=True)
                            status = self.normalize_status(raw_status)
                            
                            players[player_name.lower()] = {
                                "name": player_name,
                                "status": status,
                                "source": "cbs_sports",
                                "last_updated": datetime.now().isoformat(),
                                "raw_status": raw_status
                            }
                    
                    except Exception as e:
                        self.logger.debug(f"Parsing error for row: {e}")
                        continue
                
                self.logger.info(f" CBS Sports: Found {len(players)} player updates")
            
        except Exception as e:
            self.logger.warning(f" CBS Sports failed: {e}")
        
        return players
    
    def fetch_rotowire_lineups(self) -> Dict[str, Dict]:
        """Fetch starting lineup data from RotoWire"""
        if not HTML_PARSING_AVAILABLE:
            return {}
        
        self.logger.info(" Fetching RotoWire lineup data...")
        players = {}
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(
                self.api_sources["rotowire"]["url"],
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for lineup information
                lineup_sections = soup.find_all(['div', 'section'], class_=lambda x: x and 'lineup' in x.lower())
                
                for section in lineup_sections:
                    # Extract confirmed starters (these are definitely playing)
                    starter_elements = section.find_all(['span', 'div'], class_=lambda x: x and 'starter' in x.lower())
                    
                    for elem in starter_elements:
                        player_name = elem.get_text(strip=True)
                        if player_name and len(player_name.split()) >= 2:  # Full name check
                            players[player_name.lower()] = {
                                "name": player_name,
                                "status": "active",
                                "source": "rotowire_lineup",
                                "last_updated": datetime.now().isoformat(),
                                "raw_status": "confirmed_starter"
                            }
                
                self.logger.info(f" RotoWire: Found {len(players)} confirmed starters")
            
        except Exception as e:
            self.logger.warning(f" RotoWire failed: {e}")
        
        return players
    
    def aggregate_player_data(self) -> Dict[str, Dict]:
        """Aggregate player data from all sources"""
        self.logger.info(" Aggregating player data from all sources...")
        
        all_players = {}
        
        # Fetch from all enabled sources
        sources_data = []
        
        if self.api_sources["espn"]["enabled"]:
            espn_data = self.fetch_espn_injuries()
            sources_data.append(("espn", espn_data))
        
        if self.api_sources["cbs_sports"]["enabled"]:
            cbs_data = self.fetch_cbs_injuries()
            sources_data.append(("cbs", cbs_data))
        
        if self.api_sources["rotowire"]["enabled"]:
            rotowire_data = self.fetch_rotowire_lineups()
            sources_data.append(("rotowire", rotowire_data))
        
        # Merge data with source priority (manual > espn > cbs > rotowire)
        for source_name, source_data in sources_data:
            for player_key, player_info in source_data.items():
                if player_key not in all_players:
                    all_players[player_key] = player_info
                else:
                    # Update with more recent or higher priority data
                    existing = all_players[player_key]
                    if (source_name == "espn" and existing["source"] != "manual_override") or \
                       (existing["source"] == "rotowire" and source_name in ["espn", "cbs"]):
                        all_players[player_key] = player_info
        
        # Apply manual overrides (highest priority)
        for player_key, override_info in self.manual_overrides.items():
            if player_key in all_players:
                all_players[player_key].update(override_info)
                all_players[player_key]["source"] = "manual_override"
            else:
                all_players[player_key] = {
                    "name": player_key.title(),
                    **override_info
                }
        
        self.logger.info(f" Aggregated data for {len(all_players)} players")
        return all_players
    
    def fetch_injury_report(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """Fetch comprehensive injury report with caching"""
        
        # Check cache freshness
        if not force_refresh and self.status_cache_file.exists():
            try:
                with open(self.status_cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is less than 2 hours old
                cache_time = datetime.fromisoformat(cached_data["timestamp"])
                if datetime.now() - cache_time < timedelta(hours=2):
                    self.logger.info(" Using cached player status data")
                    return cached_data["players"]
            
            except Exception as e:
                self.logger.warning(f" Cache read error: {e}")
        
        # Fetch fresh data
        self.logger.info(" Fetching fresh player status data...")
        players = self.aggregate_player_data()
        
        # Save to cache
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "players": players,
            "sources_used": [name for name, config in self.api_sources.items() if config["enabled"]],
            "total_players": len(players)
        }
        
        try:
            with open(self.status_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            self.logger.info(f" Cached status for {len(players)} players")
        except Exception as e:
            self.logger.error(f" Failed to save cache: {e}")
        
        return players
    
    def load_status_cache(self) -> Dict[str, Dict]:
        """Load player status from cache or fetch fresh data"""
        return self.fetch_injury_report(force_refresh=False)
    
    def is_playing(self, name: str, team: str = "") -> bool:
        """
         Main function: Check if a player is playing tonight
        
        Args:
            name: Player's full name
            team: Team abbreviation (optional, for disambiguation)
        
        Returns:
            bool: True if player is expected to play, False if out/doubtful
        """
        players = self.load_status_cache()
        player_key = name.lower().strip()
        
        # Direct lookup
        player_info = players.get(player_key)
        
        if not player_info:
            # Try fuzzy matching for partial names
            for cached_key, cached_info in players.items():
                if all(part.lower() in cached_key for part in name.lower().split()):
                    player_info = cached_info
                    break
        
        if not player_info:
            # Player not found in injury reports - assume playing
            self.logger.info(f" {name} not in injury reports - assuming available")
            return True
        
        status = player_info.get("status", "unknown").lower()
        
        # Log the check
        source = player_info.get("source", "unknown")
        self.logger.info(f" {name}: {status.upper()} (source: {source})")
        
        # Return False for definite non-playing statuses
        if status in ["out", "doubtful", "inactive"]:
            return False
        
        # Return True for active/probable/questionable players
        return True
    
    def get_player_status_detailed(self, name: str, team: str = "") -> Dict[str, Any]:
        """Get detailed player status information"""
        players = self.load_status_cache()
        player_key = name.lower().strip()
        
        player_info = players.get(player_key)
        
        if not player_info:
            # Try fuzzy matching
            for cached_key, cached_info in players.items():
                if all(part.lower() in cached_key for part in name.lower().split()):
                    player_info = cached_info
                    break
        
        if not player_info:
            return {
                "name": name,
                "status": "unknown",
                "playing": True,
                "source": "not_found",
                "reason": "Player not found in injury reports",
                "last_updated": None
            }
        
        status = player_info.get("status", "unknown")
        
        return {
            "name": player_info.get("name", name),
            "status": status,
            "playing": self.is_playing(name, team),
            "source": player_info.get("source", "unknown"),
            "reason": player_info.get("reason", player_info.get("raw_status", "")),
            "last_updated": player_info.get("last_updated")
        }
    
    def update_manual_override(self, player_name: str, status: str, reason: str = ""):
        """Add or update manual player status override"""
        self.manual_overrides[player_name.lower()] = {
            "status": status.lower(),
            "reason": reason,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "source": "manual_override"
        }
        
        # Save to file
        try:
            with open(self.manual_overrides_file, 'w') as f:
                json.dump(self.manual_overrides, f, indent=2)
            self.logger.info(f" Updated manual override: {player_name} -> {status}")
        except Exception as e:
            self.logger.error(f" Failed to save manual override: {e}")
    
    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive player status report"""
        players = self.fetch_injury_report(force_refresh=True)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_players": len(players),
            "status_breakdown": {},
            "sources_breakdown": {},
            "notable_absences": [],
            "confirmed_starters": []
        }
        
        # Analyze status breakdown
        for player_info in players.values():
            status = player_info.get("status", "unknown")
            source = player_info.get("source", "unknown")
            
            # Status counts
            report["status_breakdown"][status] = report["status_breakdown"].get(status, 0) + 1
            
            # Source counts
            report["sources_breakdown"][source] = report["sources_breakdown"].get(source, 0) + 1
            
            # Notable lists
            if status == "out":
                report["notable_absences"].append({
                    "name": player_info.get("name"),
                    "reason": player_info.get("reason", player_info.get("raw_status", ""))
                })
            elif source == "rotowire_lineup":
                report["confirmed_starters"].append(player_info.get("name"))
        
        return report


def main():
    """CLI interface for player status checker"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NBA Player Status Checker")
    parser.add_argument("--workspace", default="C:/EQ12", help="Workspace path")
    parser.add_argument("--player", help="Check specific player status")
    parser.add_argument("--refresh", action="store_true", help="Force refresh data")
    parser.add_argument("--report", action="store_true", help="Generate full status report")
    parser.add_argument("--override", nargs=3, metavar=('PLAYER', 'STATUS', 'REASON'), 
                       help="Add manual override: player status reason")
    
    args = parser.parse_args()
    
    print(" EQ12 NBA PLAYER STATUS CHECKER")
    print("=" * 50)
    
    checker = PlayerStatusChecker(args.workspace)
    
    if args.override:
        player, status, reason = args.override
        checker.update_manual_override(player, status, reason)
        print(f" Manual override added: {player} -> {status}")
        return
    
    if args.player:
        # Check specific player
        status_info = checker.get_player_status_detailed(args.player)
        
        print(f"\n PLAYER STATUS: {status_info['name']}")
        print(f"   Status: {status_info['status'].upper()}")
        print(f"   Playing Tonight: {' YES' if status_info['playing'] else ' NO'}")
        print(f"   Source: {status_info['source']}")
        if status_info['reason']:
            print(f"   Reason: {status_info['reason']}")
        if status_info['last_updated']:
            print(f"   Last Updated: {status_info['last_updated']}")
    
    elif args.report:
        # Generate full report
        report = checker.generate_status_report()
        
        print(f"\n STATUS REPORT ({report['total_players']} players)")
        print(f"   Generated: {report['timestamp']}")
        
        print(f"\n STATUS BREAKDOWN:")
        for status, count in report['status_breakdown'].items():
            print(f"   {status.upper()}: {count}")
        
        print(f"\n SOURCES:")
        for source, count in report['sources_breakdown'].items():
            print(f"   {source}: {count}")
        
        if report['notable_absences']:
            print(f"\n NOTABLE ABSENCES:")
            for absence in report['notable_absences'][:10]:  # Top 10
                print(f"   {absence['name']}: {absence['reason']}")
        
        if report['confirmed_starters']:
            print(f"\n CONFIRMED STARTERS ({len(report['confirmed_starters'])}):")
            for starter in report['confirmed_starters'][:15]:  # Top 15
                print(f"   {starter}")
        
        # Save report
        report_file = Path(args.workspace) / "logs" / f"player_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n Full report saved: {report_file}")
    
    else:
        # Quick status check
        if args.refresh:
            checker.fetch_injury_report(force_refresh=True)
        
        print(f"\n Status cache updated")
        print(f" Use --player 'Player Name' to check specific player")
        print(f" Use --report for comprehensive analysis")


if __name__ == "__main__":
    main()