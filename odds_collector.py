#!/usr/bin/env python3
"""
EQ12 Odds Collector - Godlike Betting Automation
Collects odds from The Odds API and other sources
Matches with schedule data and normalizes across all bookmakers
"""

import asyncio
import json
import logging
import os
import sys
import warnings
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore")

import time

import pandas as pd
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Add EQ12 to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

# Configure logging
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)
data_dir = Path("C:/EQ12/data")
data_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'odds_collector_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EQ12.OddsCollector")

class OddsCollector:
    """Collects and normalizes odds from multiple sources"""
    
    def __init__(self, concurrency: int = 5):
        self.odds_api_key = os.getenv("THE_ODDS_API_KEY")
        self.sportsdataio_key = os.getenv("SPORTSDATAIO_API_KEY")  
        self.sportradar_key = os.getenv("SPORTRADAR_API_KEY")
        
        self.concurrency = concurrency
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EQ12-GodlikeBetting/1.0 (contact@eq12.com)'
        })
        
        # Sport key mapping for The Odds API
        self.sport_key_map = {
            'NBA': 'basketball_nba',
            'MLB': 'baseball_mlb', 
            'NFL': 'americanfootball_nfl',
            'CFB': 'americanfootball_ncaaf',
            'NHL': 'icehockey_nhl',
            'Soccer': 'soccer_epl'  # Default to EPL, can expand
        }
        
        logger.info("🎰 Odds collector initialized")
        if not self.odds_api_key:
            logger.warning("⚠️ THE_ODDS_API_KEY missing - primary source unavailable")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_odds_for_sport(self, sport_key: str, league: str) -> list[dict]:
        """Fetch odds for a specific sport from The Odds API"""
        if not self.odds_api_key:
            logger.warning(f"❌ Cannot fetch {league} odds - API key missing")
            return []
            
        odds_data = []
        
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
            
            params = {
                'apiKey': self.odds_api_key,
                'regions': 'us',
                'markets': 'h2h,spreads,totals',
                'oddsFormat': 'american',
                'dateFormat': 'iso'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check API usage
            remaining = response.headers.get('x-requests-remaining')
            if remaining:
                logger.info(f"📊 Odds API requests remaining: {remaining}")
            
            for event in data:
                try:
                    event_odds = self.parse_odds_event(event, league)
                    if event_odds:
                        odds_data.extend(event_odds)
                        
                except Exception as e:
                    logger.warning(f"Error parsing {league} event: {e}")
                    
            logger.info(f"✅ Fetched odds for {len(odds_data)} {league} markets")
            
            # Rate limiting
            time.sleep(0.5)  # Be respectful to the API
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.error(f"🚫 Rate limited for {league}")
                time.sleep(60)  # Wait 1 minute
            else:
                logger.error(f"❌ HTTP error fetching {league} odds: {e}")
        except Exception as e:
            logger.error(f"❌ Error fetching {league} odds: {e}")
            
        return odds_data
    
    def parse_odds_event(self, event: dict, league: str) -> list[dict]:
        """Parse odds data for a single event"""
        odds_data = []
        
        try:
            game_id = f"{league.lower()}_{event.get('id')}"
            commence_time = event.get('commence_time')
            home_team = event.get('home_team', '')
            away_team = event.get('away_team', '')
            
            for bookmaker in event.get('bookmakers', []):
                bookmaker_name = bookmaker.get('title', bookmaker.get('key', ''))
                last_update = bookmaker.get('last_update')
                
                for market in bookmaker.get('markets', []):
                    market_key = market.get('key')
                    
                    # Parse different market types
                    if market_key == 'h2h':  # Moneyline
                        for outcome in market.get('outcomes', []):
                            odds_data.append({
                                'game_id': game_id,
                                'league': league,
                                'home_team': home_team,
                                'away_team': away_team,
                                'commence_time': commence_time,
                                'bookmaker': bookmaker_name,
                                'last_update': last_update,
                                'market': 'moneyline',
                                'team': outcome.get('name'),
                                'odds': outcome.get('price'),
                                'point': None,
                                'api_source': 'the_odds_api'
                            })
                            
                    elif market_key == 'spreads':  # Point spreads
                        for outcome in market.get('outcomes', []):
                            odds_data.append({
                                'game_id': game_id,
                                'league': league,
                                'home_team': home_team,
                                'away_team': away_team,
                                'commence_time': commence_time,
                                'bookmaker': bookmaker_name,
                                'last_update': last_update,
                                'market': 'spread',
                                'team': outcome.get('name'),
                                'odds': outcome.get('price'),
                                'point': outcome.get('point'),
                                'api_source': 'the_odds_api'
                            })
                            
                    elif market_key == 'totals':  # Over/Under
                        for outcome in market.get('outcomes', []):
                            odds_data.append({
                                'game_id': game_id,
                                'league': league,
                                'home_team': home_team,
                                'away_team': away_team,
                                'commence_time': commence_time,
                                'bookmaker': bookmaker_name,
                                'last_update': last_update,
                                'market': 'total',
                                'team': outcome.get('name'),  # 'Over' or 'Under'
                                'odds': outcome.get('price'),
                                'point': outcome.get('point'),
                                'api_source': 'the_odds_api'
                            })
                            
        except Exception as e:
            logger.warning(f"Error parsing odds event: {e}")
            
        return odds_data
    
    async def collect_all_odds(self) -> pd.DataFrame:
        """Collect odds for all sports concurrently"""
        logger.info("🚀 Starting concurrent odds collection...")
        
        tasks = []
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = []
            
            for league, sport_key in self.sport_key_map.items():
                future = executor.submit(self.fetch_odds_for_sport, sport_key, league)
                futures.append((future, league))
            
            # Collect results
            all_odds = []
            for future, league in futures:
                try:
                    result = future.result()
                    all_odds.extend(result)
                except Exception as e:
                    logger.error(f"❌ Failed to collect {league} odds: {e}")
        
        if not all_odds:
            logger.warning("⚠️ No odds data collected")
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(all_odds)
        
        # Clean and normalize
        df = self.clean_odds_data(df)
        
        logger.info(f"✅ Collected {len(df)} total odds entries across {df['league'].nunique()} leagues")
        
        return df
    
    def clean_odds_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize odds data"""
        if df.empty:
            return df
            
        # Convert commence_time to datetime
        df['commence_time_dt'] = pd.to_datetime(df['commence_time'])
        
        # Normalize bookmaker names
        df['bookmaker'] = df['bookmaker'].str.title()
        
        # Convert odds to numeric
        df['odds'] = pd.to_numeric(df['odds'], errors='coerce')
        
        # Convert points to numeric
        df['point'] = pd.to_numeric(df['point'], errors='coerce')
        
        # Sort by league, game, market, bookmaker
        df = df.sort_values(['league', 'game_id', 'market', 'bookmaker']).reset_index(drop=True)
        
        return df
    
    def match_with_schedule(self, odds_df: pd.DataFrame, schedule_csv: str) -> pd.DataFrame:
        """Match odds data with schedule data"""
        try:
            # Load schedule data
            schedule_df = pd.read_csv(schedule_csv)
            
            if schedule_df.empty or odds_df.empty:
                logger.warning("⚠️ Cannot match - schedule or odds data is empty")
                return odds_df
            
            # Normalize team names for matching
            schedule_df['home_team_clean'] = schedule_df['home_team'].str.lower().str.strip()
            schedule_df['away_team_clean'] = schedule_df['away_team'].str.lower().str.strip()
            
            odds_df['home_team_clean'] = odds_df['home_team'].str.lower().str.strip()
            odds_df['away_team_clean'] = odds_df['away_team'].str.lower().str.strip()
            
            # Match by league and teams
            merged_df = odds_df.merge(
                schedule_df[['league', 'home_team_clean', 'away_team_clean', 'start_time', 'venue', 'game_id']],
                on=['league', 'home_team_clean', 'away_team_clean'],
                how='left',
                suffixes=('_odds', '_schedule')
            )
            
            # Use schedule start_time if available
            merged_df['start_time'] = merged_df['start_time'].fillna(merged_df['commence_time'])
            
            # Drop temporary columns
            merged_df = merged_df.drop(['home_team_clean', 'away_team_clean'], axis=1)
            
            match_rate = len(merged_df[merged_df['start_time'].notna()]) / len(odds_df) * 100
            logger.info(f"📊 Schedule match rate: {match_rate:.1f}%")
            
            return merged_df
            
        except Exception as e:
            logger.error(f"❌ Error matching with schedule: {e}")
            return odds_df
    
    def calculate_implied_probabilities(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate implied probabilities from American odds"""
        if df.empty:
            return df
            
        def american_to_probability(odds):
            if pd.isna(odds):
                return None
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)
        
        df['implied_prob'] = df['odds'].apply(american_to_probability)
        return df
    
    def find_arbitrage_opportunities(self, df: pd.DataFrame) -> pd.DataFrame:
        """Find arbitrage opportunities across bookmakers"""
        arb_opportunities = []
        
        if df.empty:
            return pd.DataFrame()
        
        # Group by game and market type
        for (game_id, market), group in df.groupby(['game_id', 'market']):
            if market == 'moneyline' and len(group) >= 2:
                # Find best odds for each team
                home_odds = group[group['team'] == group['home_team'].iloc[0]]
                away_odds = group[group['team'] == group['away_team'].iloc[0]]
                
                if not home_odds.empty and not away_odds.empty:
                    best_home = home_odds.loc[home_odds['odds'].idxmax()]
                    best_away = away_odds.loc[away_odds['odds'].idxmax()]
                    
                    # Calculate arbitrage
                    home_prob = american_to_probability(best_home['odds'])
                    away_prob = american_to_probability(best_away['odds'])
                    
                    if home_prob and away_prob:
                        total_prob = home_prob + away_prob
                        if total_prob < 1.0:  # Arbitrage opportunity
                            profit_margin = (1 - total_prob) * 100
                            
                            arb_opportunities.append({
                                'game_id': game_id,
                                'league': group['league'].iloc[0],
                                'home_team': group['home_team'].iloc[0],
                                'away_team': group['away_team'].iloc[0],
                                'profit_margin': profit_margin,
                                'home_bookmaker': best_home['bookmaker'],
                                'home_odds': best_home['odds'],
                                'away_bookmaker': best_away['bookmaker'], 
                                'away_odds': best_away['odds']
                            })
        
        arb_df = pd.DataFrame(arb_opportunities)
        if not arb_df.empty:
            arb_df = arb_df.sort_values('profit_margin', ascending=False)
            logger.info(f"🔍 Found {len(arb_df)} arbitrage opportunities")
        
        return arb_df
    
    def save_odds_data(self, df: pd.DataFrame, merged_df: pd.DataFrame | None = None, arb_df: pd.DataFrame | None = None) -> dict[str, str]:
        """Save odds data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filepaths = {}
        
        # Save raw odds
        if not df.empty:
            odds_path = data_dir / f"odds_{timestamp}.csv"
            df.to_csv(odds_path, index=False)
            filepaths['odds'] = str(odds_path)
            logger.info(f"💾 Saved odds data: {odds_path}")
        
        # Save merged schedule+odds
        if merged_df is not None and not merged_df.empty:
            merged_path = data_dir / f"schedule_odds_{timestamp}.csv"
            merged_df.to_csv(merged_path, index=False)
            filepaths['merged'] = str(merged_path)
            logger.info(f"💾 Saved merged data: {merged_path}")
        
        # Save arbitrage opportunities
        if arb_df is not None and not arb_df.empty:
            arb_path = data_dir / f"arbitrage_{timestamp}.csv"
            arb_df.to_csv(arb_path, index=False)
            filepaths['arbitrage'] = str(arb_path)
            logger.info(f"💾 Saved arbitrage data: {arb_path}")
        
        return filepaths
    
    def print_summary(self, df: pd.DataFrame, arb_df: pd.DataFrame | None = None):
        """Print odds collection summary"""
        if df.empty:
            logger.info("📊 No odds data collected")
            return
        
        logger.info("📊 ODDS COLLECTION SUMMARY")
        logger.info("=" * 50)
        
        # Odds per sport
        sport_counts = df.groupby('league')['game_id'].nunique()
        for league, count in sport_counts.items():
            total_markets = len(df[df['league'] == league])
            logger.info(f"  {league}: {count} games, {total_markets} market entries")
        
        # Bookmaker coverage
        bookmaker_counts = df['bookmaker'].value_counts()
        logger.info(f"\n🏪 Bookmakers: {', '.join(bookmaker_counts.head(5).index.tolist())}")
        
        # Market types
        market_counts = df['market'].value_counts()
        logger.info(f"📈 Markets: {', '.join(market_counts.index.tolist())}")
        
        # Arbitrage opportunities
        if arb_df is not None and not arb_df.empty:
            logger.info(f"🔍 Arbitrage Opportunities: {len(arb_df)}")
            if len(arb_df) > 0:
                best_arb = arb_df.iloc[0]
                logger.info(f"  Best: {best_arb['away_team']} @ {best_arb['home_team']} ({best_arb['profit_margin']:.2f}%)")

def american_to_probability(odds):
    """Convert American odds to implied probability"""
    if pd.isna(odds):
        return None
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Godlike Odds Collector")
    parser.add_argument("--schedule", help="Path to schedule CSV file")
    parser.add_argument("--concurrency", type=int, default=5, help="API concurrency level")
    parser.add_argument("--arbitrage", action="store_true", help="Find arbitrage opportunities")
    
    args = parser.parse_args()
    
    try:
        collector = OddsCollector(concurrency=args.concurrency)
        
        # Collect odds data
        odds_df = await collector.collect_all_odds()
        
        if odds_df.empty:
            logger.warning("❌ No odds data collected")
            return None
        
        # Add implied probabilities
        odds_df = collector.calculate_implied_probabilities(odds_df)
        
        merged_df = None
        arb_df = None
        
        # Match with schedule if provided
        if args.schedule:
            merged_df = collector.match_with_schedule(odds_df, args.schedule)
        
        # Find arbitrage opportunities
        if args.arbitrage:
            arb_df = collector.find_arbitrage_opportunities(odds_df)
        
        # Save data
        filepaths = collector.save_odds_data(odds_df, merged_df, arb_df)
        
        # Print summary
        collector.print_summary(odds_df, arb_df)
        
        # Save summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "odds_collected": len(odds_df),
            "leagues": odds_df['league'].value_counts().to_dict(),
            "bookmakers": odds_df['bookmaker'].value_counts().to_dict(),
            "markets": odds_df['market'].value_counts().to_dict(),
            "arbitrage_opportunities": len(arb_df) if arb_df is not None else 0,
            "filepaths": filepaths
        }
        
        summary_path = data_dir / f"odds_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("✅ EQ12 Odds Collector completed successfully!")
        return filepaths.get('merged') or filepaths.get('odds')
        
    except Exception as e:
        logger.error(f"❌ Odds collector failed: {e}")
        raise

if __name__ == "__main__":
    # Handle event loop for Windows
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
    except:
        pass
    
    asyncio.run(main())