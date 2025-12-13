#!/usr/bin/env python3
"""
 EQ12 COMPREHENSIVE NBA RSS FEED SEARCHER
Searches all major NBA news sources for player status updates

SOURCES SEARCHED:
- ESPN NBA RSS
- NBA.com Official RSS
- The Athletic NBA
- Bleacher Report NBA
- Yahoo Sports NBA
- CBS Sports NBA
- SI.com NBA
- Milwaukee Bucks Official
- RotoWire NBA
- FantasyPros NBA
"""

import asyncio
import aiohttp
import feedparser
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import xml.etree.ElementTree as ET


class ComprehensiveNBAFeedSearcher:
    """ Comprehensive NBA RSS feed searcher"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.data_path = self.workspace_path / "data"
        self.logs_path = self.workspace_path / "logs"
        
        # Create directories
        for path in [self.data_path, self.logs_path]:
            path.mkdir(exist_ok=True)
        
        # NBA RSS Feeds and News Sources
        self.nba_feeds = {
            "ESPN_NBA": "https://www.espn.com/espn/rss/nba/news",
            "NBA_Official": "https://www.nba.com/news/rss.xml",
            "Yahoo_NBA": "https://sports.yahoo.com/nba/rss.xml",
            "CBS_NBA": "https://www.cbssports.com/rss/headlines/nba/",
            "Bleacher_Report": "https://bleacherreport.com/nba.rss",
            "The_Athletic": "https://theathletic.com/nba/rss/",
            "SI_NBA": "https://www.si.com/rss/nba.xml",
            "RotoWire_NBA": "https://www.rotowire.com/rss/news.php?sport=NBA",
            "FantasyPros": "https://www.fantasypros.com/nba/news/rss/",
            "Milwaukee_Bucks": "https://www.nba.com/bucks/rss.xml"
        }
        
        # Injury/Status keywords
        self.injury_keywords = [
            "out", "injured", "sidelined", "ruled out", "will not play",
            "questionable", "doubtful", "probable", "game-time decision",
            "rest", "load management", "day-to-day", "week-to-week",
            "injury report", "status update", "available", "cleared"
        ]
        
        # Player name variations
        self.player_variations = {
            "damian lillard": ["damian lillard", "d. lillard", "dame lillard", "dame", "lillard"],
            "giannis antetokounmpo": ["giannis antetokounmpo", "giannis", "antetokounmpo", "greek freak"],
            "lebron james": ["lebron james", "lebron", "lbj", "king james"],
            "kawhi leonard": ["kawhi leonard", "kawhi", "leonard", "the claw"],
            "paul george": ["paul george", "pg13", "p. george", "george"]
        }
        
        print(" Comprehensive NBA Feed Searcher initialized")
        print(f" Monitoring {len(self.nba_feeds)} RSS feeds")
    
    async def search_all_feeds(self, target_player: str = "damian lillard") -> Dict[str, List[Dict]]:
        """Search all NBA RSS feeds for player mentions"""
        print(f"\n SEARCHING ALL NBA FEEDS FOR: {target_player.upper()}")
        print("=" * 60)
        
        results = {}
        search_variations = self.player_variations.get(target_player.lower(), [target_player.lower()])
        
        # Search each feed
        for feed_name, feed_url in self.nba_feeds.items():
            print(f" Searching {feed_name}...")
            
            try:
                feed_results = await self._search_single_feed(feed_url, search_variations, feed_name)
                results[feed_name] = feed_results
                
                if feed_results:
                    print(f" Found {len(feed_results)} mentions in {feed_name}")
                else:
                    print(f"   No mentions found in {feed_name}")
                    
            except Exception as e:
                print(f" Error searching {feed_name}: {e}")
                results[feed_name] = []
        
        return results
    
    async def _search_single_feed(self, feed_url: str, search_terms: List[str], source: str) -> List[Dict]:
        """Search a single RSS feed"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(feed_url, headers=headers, timeout=15) as response:
                    if response.status != 200:
                        return []
                    
                    content = await response.text()
                    
                    # Parse RSS feed
                    feed = feedparser.parse(content)
                    
                    matches = []
                    
                    for entry in feed.entries:
                        title = entry.get('title', '').lower()
                        description = entry.get('description', '').lower()
                        summary = entry.get('summary', '').lower()
                        
                        # Check for player mentions
                        player_found = False
                        for term in search_terms:
                            if term in title or term in description or term in summary:
                                player_found = True
                                break
                        
                        if player_found:
                            # Check for injury/status keywords
                            injury_context = []
                            for keyword in self.injury_keywords:
                                if keyword in title or keyword in description or keyword in summary:
                                    injury_context.append(keyword)
                            
                            match = {
                                'title': entry.get('title', ''),
                                'description': entry.get('description', ''),
                                'summary': entry.get('summary', ''),
                                'link': entry.get('link', ''),
                                'published': entry.get('published', ''),
                                'source': source,
                                'injury_keywords_found': injury_context,
                                'priority': len(injury_context)  # Higher priority for more injury keywords
                            }
                            
                            matches.append(match)
                    
                    # Sort by priority (most injury keywords first)
                    matches.sort(key=lambda x: x['priority'], reverse=True)
                    
                    return matches
                    
        except Exception as e:
            print(f"   Error parsing {source}: {e}")
            return []
    
    async def search_web_apis(self, target_player: str = "damian lillard") -> Dict[str, Any]:
        """Search web APIs for additional player information"""
        print(f"\n SEARCHING WEB APIS FOR: {target_player.upper()}")
        print("=" * 50)
        
        api_results = {}
        
        # ESPN API search
        try:
            print(" Searching ESPN API...")
            espn_results = await self._search_espn_api(target_player)
            api_results['ESPN_API'] = espn_results
            
            if espn_results.get('mentions'):
                print(f" Found {len(espn_results['mentions'])} ESPN API mentions")
            else:
                print("   No ESPN API mentions found")
                
        except Exception as e:
            print(f" ESPN API error: {e}")
            api_results['ESPN_API'] = {'error': str(e)}
        
        # NBA Stats API search
        try:
            print(" Searching NBA Stats API...")
            nba_results = await self._search_nba_stats_api(target_player)
            api_results['NBA_STATS_API'] = nba_results
            
            if nba_results.get('player_info'):
                print(f" Found NBA Stats API player info")
            else:
                print("   No NBA Stats API info found")
                
        except Exception as e:
            print(f" NBA Stats API error: {e}")
            api_results['NBA_STATS_API'] = {'error': str(e)}
        
        return api_results
    
    async def _search_espn_api(self, player: str) -> Dict[str, Any]:
        """Search ESPN API for player news"""
        urls = [
            "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/news",
            "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
        ]
        
        results = {'mentions': []}
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    async with session.get(url, headers=headers, timeout=15) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Search news articles
                            if 'articles' in data:
                                for article in data.get('articles', []):
                                    headline = article.get('headline', '').lower()
                                    description = article.get('description', '').lower()
                                    
                                    if player.lower() in headline or player.lower() in description:
                                        results['mentions'].append({
                                            'headline': article.get('headline', ''),
                                            'description': article.get('description', ''),
                                            'published': article.get('published', ''),
                                            'type': 'espn_news'
                                        })
                            
                            # Search scoreboard for roster info
                            if 'events' in data:
                                for event in data.get('events', []):
                                    # Look for Milwaukee games
                                    competitors = event.get('competitions', [{}])[0].get('competitors', [])
                                    
                                    for competitor in competitors:
                                        team_abbrev = competitor.get('team', {}).get('abbreviation', '')
                                        if team_abbrev == 'MIL':
                                            results['milwaukee_game'] = {
                                                'date': event.get('date', ''),
                                                'status': event.get('status', {}).get('type', {}).get('description', ''),
                                                'competitors': [
                                                    {
                                                        'team': comp.get('team', {}).get('displayName', ''),
                                                        'abbreviation': comp.get('team', {}).get('abbreviation', '')
                                                    }
                                                    for comp in competitors
                                                ]
                                            }
                                            break
                
                except Exception as e:
                    print(f"   ESPN API URL error: {e}")
        
        return results
    
    async def _search_nba_stats_api(self, player: str) -> Dict[str, Any]:
        """Search NBA Stats API (simplified)"""
        # Note: NBA Stats API requires specific player IDs
        # This is a placeholder for more advanced NBA API integration
        
        return {
            'player_info': f"NBA Stats API search for {player} (requires player ID)",
            'note': 'Advanced NBA API integration would require player ID lookup'
        }
    
    def analyze_results(self, rss_results: Dict[str, List[Dict]], api_results: Dict[str, Any], target_player: str) -> Dict[str, Any]:
        """Analyze all search results for player status"""
        print(f"\n ANALYZING RESULTS FOR: {target_player.upper()}")
        print("=" * 50)
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'target_player': target_player,
            'total_sources_searched': len(self.nba_feeds),
            'sources_with_mentions': 0,
            'total_mentions': 0,
            'high_priority_mentions': [],
            'injury_status_indicators': [],
            'recommendation': 'UNKNOWN'
        }
        
        # Analyze RSS results
        for source, mentions in rss_results.items():
            if mentions:
                analysis['sources_with_mentions'] += 1
                analysis['total_mentions'] += len(mentions)
                
                # Identify high-priority mentions (injury-related)
                for mention in mentions:
                    if mention.get('priority', 0) > 0:
                        analysis['high_priority_mentions'].append({
                            'source': source,
                            'title': mention['title'],
                            'injury_keywords': mention['injury_keywords_found'],
                            'link': mention.get('link', ''),
                            'published': mention.get('published', '')
                        })
        
        # Analyze API results
        for api_name, api_data in api_results.items():
            if isinstance(api_data, dict) and 'mentions' in api_data:
                analysis['total_mentions'] += len(api_data['mentions'])
        
        # Generate recommendation
        if analysis['high_priority_mentions']:
            injury_keywords_found = set()
            for mention in analysis['high_priority_mentions']:
                injury_keywords_found.update(mention.get('injury_keywords', []))
            
            if any(keyword in injury_keywords_found for keyword in ['out', 'ruled out', 'will not play', 'sidelined']):
                analysis['recommendation'] = 'BLOCK_PLAYER'
                analysis['status'] = 'OUT'
            elif any(keyword in injury_keywords_found for keyword in ['questionable', 'doubtful', 'game-time decision']):
                analysis['recommendation'] = 'BLOCK_PLAYER'
                analysis['status'] = 'QUESTIONABLE'
            elif any(keyword in injury_keywords_found for keyword in ['rest', 'load management']):
                analysis['recommendation'] = 'BLOCK_PLAYER'
                analysis['status'] = 'REST'
            else:
                analysis['recommendation'] = 'MONITOR'
                analysis['status'] = 'UNCLEAR'
        elif analysis['total_mentions'] > 0:
            analysis['recommendation'] = 'MONITOR'
            analysis['status'] = 'MENTIONED_NO_INJURY_CONTEXT'
        else:
            analysis['recommendation'] = 'NO_NEWS_FOUND'
            analysis['status'] = 'NO_MENTIONS'
        
        # Display analysis
        print(f" ANALYSIS SUMMARY:")
        print(f"   Sources searched: {analysis['total_sources_searched']}")
        print(f"   Sources with mentions: {analysis['sources_with_mentions']}")
        print(f"   Total mentions: {analysis['total_mentions']}")
        print(f"   High-priority mentions: {len(analysis['high_priority_mentions'])}")
        print(f"   Status: {analysis['status']}")
        print(f"   Recommendation: {analysis['recommendation']}")
        
        if analysis['high_priority_mentions']:
            print(f"\n HIGH-PRIORITY MENTIONS:")
            for mention in analysis['high_priority_mentions'][:5]:  # Top 5
                print(f"    {mention['source']}: {mention['title']}")
                if mention['injury_keywords']:
                    print(f"      Keywords: {', '.join(mention['injury_keywords'])}")
        
        return analysis
    
    def save_comprehensive_report(self, rss_results: Dict, api_results: Dict, analysis: Dict, target_player: str) -> str:
        """Save comprehensive search report"""
        report = {
            'search_metadata': {
                'timestamp': datetime.now().isoformat(),
                'target_player': target_player,
                'search_date': datetime.now().date().isoformat(),
                'sources_searched': list(self.nba_feeds.keys())
            },
            'rss_results': rss_results,
            'api_results': api_results,
            'analysis': analysis,
            'feeds_configuration': self.nba_feeds
        }
        
        filename = f"comprehensive_nba_search_{target_player.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.data_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n Comprehensive report saved: {filepath}")
        return str(filepath)


async def main():
    """Run comprehensive NBA feed search"""
    print(" EQ12 COMPREHENSIVE NBA RSS FEED SEARCHER")
    print("=" * 60)
    print("Searching ALL NBA news sources for player status...")
    
    searcher = ComprehensiveNBAFeedSearcher()
    
    # Search for Damian Lillard
    target_player = "damian lillard"
    
    # Search RSS feeds
    rss_results = await searcher.search_all_feeds(target_player)
    
    # Search web APIs
    api_results = await searcher.search_web_apis(target_player)
    
    # Analyze results
    analysis = searcher.analyze_results(rss_results, api_results, target_player)
    
    # Save comprehensive report
    report_file = searcher.save_comprehensive_report(rss_results, api_results, analysis, target_player)
    
    # Final recommendation
    print(f"\n FINAL RECOMMENDATION FOR {target_player.upper()}:")
    print("=" * 50)
    
    if analysis['recommendation'] == 'BLOCK_PLAYER':
        print(f" BLOCK PLAYER: {target_player.title()}")
        print(f"   Status: {analysis['status']}")
        print(f"   Evidence: {len(analysis['high_priority_mentions'])} high-priority mentions")
        print(f"   Action: Add to blocked players list immediately")
    elif analysis['recommendation'] == 'MONITOR':
        print(f" MONITOR PLAYER: {target_player.title()}")
        print(f"   Status: {analysis['status']}")
        print(f"   Action: Manual verification recommended")
    else:
        print(f" NO NEWS FOUND: {target_player.title()}")
        print(f"   Status: {analysis['status']}")
        print(f"   Action: Likely available, but verify with official sources")
    
    print(f"\n Full report: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())