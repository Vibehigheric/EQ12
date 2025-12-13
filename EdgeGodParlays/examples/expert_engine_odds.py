#!/usr/bin/env python3
"""
Enhanced Expert Engine Odds Client - Python Version
Combines your sample odds.py with EdgeGod rate limiting + expert engine integration points

Features:
- Built-in 429 error prevention (EdgeGod rate limiting)
- Expert filter integration hooks
- Time window filtering (commenceTimeFrom/commenceTimeTo)
- Best price detection
- Implied probability calculations
- Value threshold analysis
- Production-ready error handling
"""

import hashlib
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class ExpertFilter:
    """Configuration for expert engine filters"""

    min_implied_probability: float = 0.40  # 40% minimum
    max_implied_probability: float = 0.65  # 65% maximum
    min_value_threshold: float = 0.05  # 5% minimum edge
    preferred_markets: list[str] = None
    preferred_sports: list[str] = None
    time_window_hours: int = 24  # Next 24 hours

    def __post_init__(self):
        if self.preferred_markets is None:
            self.preferred_markets = ["h2h", "spreads", "totals"]
        if self.preferred_sports is None:
            self.preferred_sports = [
                "americanfootball_nfl",
                "basketball_nba",
                "soccer_epl",
            ]


class EdgeGodExpertOddsClient:
    """Enhanced Odds API client with expert engine integration"""

    def __init__(self, api_key: str, expert_filter: ExpertFilter = None):
        self.api_key = api_key
        self.expert_filter = expert_filter or ExpertFilter()
        self.base_url = "https://api.the-odds-api.com/v4"

        # EdgeGod rate limiting
        self.rate_limit = 25.0  # Conservative 25 req/sec
        self.min_interval = 1.0 / self.rate_limit
        self.last_request_time = 0.0
        self.cache = {}

        # Setup session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _wait_for_rate_limit(self):
        """EdgeGod rate limiting implementation"""
        now = time.time()
        time_since_last = now - self.last_request_time

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _get_cache_key(self, url: str, params: dict) -> str:
        """Generate cache key for request"""
        cache_data = f"{url}_{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _make_request(self, url: str, params: dict) -> dict:
        """Make rate-limited API request with caching"""
        params = params.copy()
        params["apiKey"] = self.api_key

        # Check cache (15 min TTL)
        cache_key = self._get_cache_key(url, params)
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 900:  # 15 minutes
                print(f"✅ Cache hit for {url.split('/')[-1]}")
                return cached_data

        # Apply rate limiting
        self._wait_for_rate_limit()

        try:
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 429:
                print("⚠️ Rate limit hit, applying backoff...")
                time.sleep(2)
                return self._make_request(url, params)

            response.raise_for_status()
            data = response.json()

            # Cache successful response
            self.cache[cache_key] = (data, time.time())

            return data

        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            raise

    def get_sports(self) -> list[dict]:
        """Get available sports - enhanced version of your original"""
        url = f"{self.base_url}/sports/"
        sports = self._make_request(url, {})

        # 🎯 EXPERT ENGINE INTEGRATION POINT
        if self.expert_filter.preferred_sports:
            sports = [s for s in sports if s["key"] in self.expert_filter.preferred_sports]
            print(f"🎯 Filtered to {len(sports)} preferred sports")

        return sports

    def get_odds(
        self,
        sport_key: str,
        regions="us",
        markets="h2h",
        odds_format="american",
        with_time_filter=True,
    ) -> list[dict]:
        """Get odds with expert engine enhancements"""
        url = f"{self.base_url}/sports/{sport_key}/odds"
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format,
        }

        # 🎯 EXPERT ENGINE TIME FILTERING
        if with_time_filter:
            now = datetime.utcnow()
            commence_from = now.isoformat() + "Z"
            commence_to = (
                now + timedelta(hours=self.expert_filter.time_window_hours)
            ).isoformat() + "Z"
            params["commenceTimeFrom"] = commence_from
            params["commenceTimeTo"] = commence_to
            print(f"🕒 Filtering events: next {self.expert_filter.time_window_hours} hours")

        odds_data = self._make_request(url, params)

        # 🎯 EXPERT ENGINE FILTERING
        filtered_odds = []
        for event in odds_data:
            expert_analysis = self.analyze_event_for_expert_engine(event)
            if expert_analysis["passes_filters"]:
                event["expert_analysis"] = expert_analysis
                filtered_odds.append(event)

        print(f"🎯 Expert filter: {len(filtered_odds)}/{len(odds_data)} events passed")
        return filtered_odds

    def analyze_event_for_expert_engine(self, event: dict) -> dict:
        """
        🎯 EXPERT ENGINE CORE ANALYSIS
        This is where you'd plug in your expert logic
        """
        analysis = {
            "passes_filters": False,
            "best_prices": {},
            "implied_probabilities": {},
            "value_opportunities": [],
            "recommended_bets": [],
        }

        try:
            # Find best prices across all bookmakers for each market
            for bookmaker in event.get("bookmakers", []):
                for market in bookmaker.get("markets", []):
                    market_key = market["key"]

                    # Skip if not in preferred markets
                    if market_key not in self.expert_filter.preferred_markets:
                        continue

                    for outcome in market.get("outcomes", []):
                        outcome_name = outcome["name"]
                        price = outcome["price"]

                        # Track best price for each outcome
                        key = f"{market_key}_{outcome_name}"
                        if (
                            key not in analysis["best_prices"]
                            or price > analysis["best_prices"][key]["price"]
                        ):
                            analysis["best_prices"][key] = {
                                "price": price,
                                "bookmaker": bookmaker["key"],
                                "market": market_key,
                                "outcome": outcome_name,
                            }

                        # Calculate implied probability
                        if price > 0:  # American odds
                            implied_prob = (
                                100 / (price + 100) if price > 0 else (-price) / (-price + 100)
                            )
                        else:
                            implied_prob = (-price) / (-price + 100)

                        analysis["implied_probabilities"][key] = implied_prob

                        # 🎯 EXPERT FILTER: Check if within probability range
                        if (
                            self.expert_filter.min_implied_probability
                            <= implied_prob
                            <= self.expert_filter.max_implied_probability
                        ):

                            # Calculate potential value (simplified - you'd use your model here)
                            estimated_true_prob = self._estimate_true_probability(event, outcome)
                            value = estimated_true_prob - implied_prob

                            if value >= self.expert_filter.min_value_threshold:
                                analysis["value_opportunities"].append(
                                    {
                                        "market": market_key,
                                        "outcome": outcome_name,
                                        "price": price,
                                        "implied_prob": implied_prob,
                                        "estimated_prob": estimated_true_prob,
                                        "value": value,
                                        "bookmaker": bookmaker["key"],
                                    }
                                )

                                analysis["recommended_bets"].append(
                                    {
                                        "confidence": ("HIGH" if value > 0.10 else "MEDIUM"),
                                        "bet_type": market_key,
                                        "selection": outcome_name,
                                        "odds": price,
                                        "value_edge": f"{value:.1%}",
                                        "bookmaker": bookmaker["key"],
                                    }
                                )

            # Event passes if it has value opportunities
            analysis["passes_filters"] = len(analysis["value_opportunities"]) > 0

        except Exception as e:
            print(f"⚠️ Error analyzing event {event.get('id', 'unknown')}: {e}")

        return analysis

    def _estimate_true_probability(self, event: dict, outcome: dict) -> float:
        """
        🎯 EXPERT ENGINE: Your probability model goes here
        This is a placeholder - replace with your actual model
        """
        # Placeholder logic - you'd implement your sophisticated model here
        # Consider factors like: team strength, historical performance, injuries, etc.

        # For now, return a simple estimate based on market consensus
        return 0.50  # Replace with your model

    def get_expert_recommendations(self, sports_list: list[str] = None) -> dict:
        """
        🎯 EXPERT ENGINE MAIN FUNCTION
        Get recommendations across multiple sports
        """
        sports_list = sports_list or self.expert_filter.preferred_sports
        all_recommendations = []

        print("🎯 Running Expert Engine Analysis...")
        print("=" * 50)

        for sport in sports_list:
            try:
                print(f"\n🏆 Analyzing {sport}...")
                odds_data = self.get_odds(
                    sport,
                    regions="us",
                    markets=",".join(self.expert_filter.preferred_markets),
                    odds_format="american",
                )

                for event in odds_data:
                    if "expert_analysis" in event and event["expert_analysis"]["recommended_bets"]:
                        event_info = {
                            "sport": sport,
                            "home_team": event["home_team"],
                            "away_team": event["away_team"],
                            "commence_time": event["commence_time"],
                            "recommendations": event["expert_analysis"]["recommended_bets"],
                        }
                        all_recommendations.append(event_info)

            except Exception as e:
                print(f"❌ Error processing {sport}: {e}")

        return {
            "total_events_analyzed": sum(
                len(self.get_odds(sport, with_time_filter=False)) for sport in sports_list
            ),
            "events_with_value": len(all_recommendations),
            "recommendations": all_recommendations,
            "filter_settings": {
                "min_probability": f"{self.expert_filter.min_implied_probability:.1%}",
                "max_probability": f"{self.expert_filter.max_implied_probability:.1%}",
                "min_value": f"{self.expert_filter.min_value_threshold:.1%}",
                "time_window": f"{self.expert_filter.time_window_hours} hours",
            },
        }


def main():
    """Enhanced main function with expert engine integration"""
    # Setup
    API_KEY = os.getenv("ODDS_API_KEY") or "YOUR_API_KEY"

    if API_KEY == "YOUR_API_KEY":
        print("❌ Please set ODDS_API_KEY environment variable")
        return

    # Configure expert filters
    expert_config = ExpertFilter(
        min_implied_probability=0.35,  # 35% minimum
        max_implied_probability=0.70,  # 70% maximum
        min_value_threshold=0.03,  # 3% minimum edge
        preferred_sports=["americanfootball_nfl", "basketball_nba"],
        time_window_hours=48,  # Next 48 hours
    )

    # Initialize enhanced client
    client = EdgeGodExpertOddsClient(API_KEY, expert_config)

    print("🎯 EdgeGod Expert Engine - Enhanced Odds Analysis")
    print("=" * 60)
    print("✅ Built-in 429 error prevention")
    print("✅ Expert filter integration")
    print("✅ Best price detection")
    print("✅ Value opportunity analysis")
    print("✅ Time window filtering")
    print("=" * 60)

    try:
        # Get expert recommendations
        recommendations = client.get_expert_recommendations()

        print("\n📊 EXPERT ENGINE RESULTS:")
        print(f"   📈 Events analyzed: {recommendations['total_events_analyzed']}")
        print(f"   🎯 Events with value: {recommendations['events_with_value']}")
        print(f"   ⚙️ Filter settings: {recommendations['filter_settings']}")

        if recommendations["recommendations"]:
            print("\n🏆 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations["recommendations"][:5], 1):
                print(f"\n   {i}. {rec['home_team']} vs {rec['away_team']}")
                print(f"      🕒 {rec['commence_time']}")
                print(f"      🏆 {rec['sport']}")

                for bet in rec["recommendations"]:
                    print(
                        f"      💰 {bet['confidence']} confidence: {bet['selection']} @ {bet['odds']} "
                        f"(Edge: {bet['value_edge']}) via {bet['bookmaker']}"
                    )
        else:
            print("\n📋 No value opportunities found with current filters")
            print("💡 Try adjusting ExpertFilter settings for different results")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
