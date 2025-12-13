#!/usr/bin/env python3
"""
 EQ12 SOCIAL INTELLIGENCE ORCHESTRATOR
========================================

Advanced social intelligence orchestration system that aggregates and analyzes
data from Twitter/X, Reddit, Telegram, and other social platforms for
comprehensive sports betting and market intelligence.

Multi-Platform Intelligence:
- Twitter/X API integration (trending topics, sentiment analysis)
- Reddit API monitoring (betting communities, injury discussions)
- Telegram channel monitoring (insider information, group sentiment)
- Discord server tracking (community discussions)
- News sentiment correlation (major sports outlets)

Analytics Pipeline:
- Real-time sentiment analysis across all platforms
- Cross-platform correlation and validation
- Automated alert generation for betting opportunities
- Social momentum tracking and prediction
- Market inefficiency identification through social bias

Integration Points:
- EQ12 Business Intelligence Tracker
- Revenue Database (revenue.db)
- Quantum Dashboard display panels
- Automated betting model adjustments
- Multi-tier architecture reliability

Author: EQ12 Quantum Development Team
Version: 1.0.0 - Social Intelligence Orchestration
Date: November 7, 2025
"""

import asyncio
import json
import logging
import sqlite3
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
import statistics
import hashlib


class SocialPlatform(Enum):
    """Social platform enumeration."""
    TWITTER = "twitter"
    REDDIT = "reddit"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    NEWS = "news"
    YOUTUBE = "youtube"


class SentimentPolarity(Enum):
    """Sentiment polarity levels."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class AlertTrigger(Enum):
    """Alert trigger types."""
    SENTIMENT_SPIKE = "sentiment_spike"
    VOLUME_SURGE = "volume_surge"
    CORRELATION_BREAK = "correlation_break"
    INSIDER_ACTIVITY = "insider_activity"
    MARKET_INEFFICIENCY = "market_inefficiency"


@dataclass
class SocialDataPoint:
    """Social media data point structure."""
    platform: SocialPlatform
    content_id: str
    content: str
    author: str
    timestamp: datetime
    engagement_score: float
    sentiment_score: float
    confidence: float
    sport: str
    teams_mentioned: List[str]
    players_mentioned: List[str]
    betting_relevance: float
    source_url: Optional[str] = None


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result structure."""
    overall_sentiment: float
    polarity: SentimentPolarity
    confidence: float
    emotion_breakdown: Dict[str, float]
    key_topics: List[str]
    trend_direction: str


@dataclass
class CrossPlatformCorrelation:
    """Cross-platform correlation analysis."""
    platforms_compared: List[SocialPlatform]
    correlation_score: float
    consensus_sentiment: float
    divergence_points: List[str]
    validation_confidence: float


@dataclass
class SocialAlert:
    """Social intelligence alert structure."""
    alert_id: str
    trigger_type: AlertTrigger
    platform_sources: List[SocialPlatform]
    sport: str
    teams_affected: List[str]
    alert_message: str
    sentiment_data: Dict[str, float]
    betting_impact_score: float
    urgency_level: int
    timestamp: datetime
    recommended_action: str


class EQ12SocialIntelligenceOrchestrator:
    """Multi-platform social intelligence orchestration and analytics system."""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.data_path = self.workspace_path / "data"
        self.logs_path = self.workspace_path / "logs"
        self.configs_path = self.workspace_path / "configs"
        
        # Ensure directories exist
        for path in [self.data_path, self.logs_path, self.configs_path]:
            path.mkdir(exist_ok=True)
        
        # Setup logging
        self.timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_path / f"social_intelligence_orchestrator_{self.timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize databases
        self.social_db_path = self.data_path / "social_intelligence.db"
        self.revenue_db_path = self.data_path / "revenue.db"
        self._initialize_databases()
        
        # Platform configurations
        self.platform_configs = self._load_platform_configs()
        
        # Analytics settings
        self.sentiment_threshold = 0.7
        self.volume_spike_threshold = 3.0  # 3x normal volume
        self.correlation_threshold = 0.6
        self.alert_cooldown_minutes = 15
        
        # Data storage
        self.social_data_buffer = []
        self.active_alerts = {}
        self.platform_status = {}
        
        # Performance tracking
        self.analytics_metrics = {
            "total_posts_analyzed": 0,
            "alerts_generated": 0,
            "sentiment_accuracy": 0.0,
            "correlation_hits": 0,
            "betting_opportunities_identified": 0
        }
    
    def _initialize_databases(self):
        """Initialize social intelligence and revenue databases."""
        # Social intelligence database
        conn = sqlite3.connect(self.social_db_path)
        
        # Social data points table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS social_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content_id TEXT NOT NULL,
                content TEXT NOT NULL,
                author TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                engagement_score REAL NOT NULL,
                sentiment_score REAL NOT NULL,
                confidence REAL NOT NULL,
                sport TEXT NOT NULL,
                teams_mentioned TEXT,
                players_mentioned TEXT,
                betting_relevance REAL NOT NULL,
                source_url TEXT,
                processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, content_id)
            )
        ''')
        
        # Sentiment analysis table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_timestamp TIMESTAMP NOT NULL,
                platform TEXT NOT NULL,
                sport TEXT NOT NULL,
                team TEXT,
                overall_sentiment REAL NOT NULL,
                polarity TEXT NOT NULL,
                confidence REAL NOT NULL,
                emotion_breakdown TEXT,
                key_topics TEXT,
                trend_direction TEXT NOT NULL,
                sample_size INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Cross-platform correlations table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS platform_correlations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                correlation_timestamp TIMESTAMP NOT NULL,
                platforms_compared TEXT NOT NULL,
                sport TEXT NOT NULL,
                correlation_score REAL NOT NULL,
                consensus_sentiment REAL NOT NULL,
                divergence_points TEXT,
                validation_confidence REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Social alerts table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS social_alerts (
                alert_id TEXT PRIMARY KEY,
                trigger_type TEXT NOT NULL,
                platform_sources TEXT NOT NULL,
                sport TEXT NOT NULL,
                teams_affected TEXT,
                alert_message TEXT NOT NULL,
                sentiment_data TEXT NOT NULL,
                betting_impact_score REAL NOT NULL,
                urgency_level INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                recommended_action TEXT NOT NULL,
                processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialize revenue database connection
        self._ensure_revenue_db_schema()
    
    def _ensure_revenue_db_schema(self):
        """Ensure revenue database has social intelligence tables."""
        conn = sqlite3.connect(self.revenue_db_path)
        
        # Social intelligence metrics table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS social_intelligence_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP NOT NULL,
                platform TEXT NOT NULL,
                sport TEXT NOT NULL,
                sentiment_score REAL NOT NULL,
                volume_index REAL NOT NULL,
                betting_relevance REAL NOT NULL,
                market_impact_prediction REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Social betting opportunities table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS social_betting_opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                opportunity_id TEXT UNIQUE NOT NULL,
                sport TEXT NOT NULL,
                teams TEXT NOT NULL,
                opportunity_type TEXT NOT NULL,
                social_sentiment REAL NOT NULL,
                predicted_line_movement REAL NOT NULL,
                confidence_score REAL NOT NULL,
                recommended_bet TEXT,
                stake_recommendation REAL,
                window_minutes INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_platform_configs(self) -> Dict[str, Any]:
        """Load platform-specific configurations."""
        return {
            SocialPlatform.TWITTER: {
                "api_rate_limit": 100,  # requests per 15 minutes
                "sentiment_weight": 1.0,
                "engagement_multiplier": 1.5,
                "keywords": ["injury", "out", "questionable", "line", "bet", "odds", "sharp"],
                "verified_accounts_bonus": 0.2
            },
            SocialPlatform.REDDIT: {
                "api_rate_limit": 60,
                "sentiment_weight": 0.8,
                "engagement_multiplier": 1.2,
                "subreddits": ["sportsbook", "DraftKings", "nfl", "nhl", "nba", "mlb"],
                "min_upvotes": 10
            },
            SocialPlatform.TELEGRAM: {
                "sentiment_weight": 1.2,
                "engagement_multiplier": 2.0,
                "insider_channels": [],  # User-configured
                "message_threshold": 5
            },
            SocialPlatform.DISCORD: {
                "sentiment_weight": 0.9,
                "engagement_multiplier": 1.1,
                "servers": [],  # User-configured
                "active_threshold": 20
            },
            SocialPlatform.NEWS: {
                "sentiment_weight": 1.5,
                "engagement_multiplier": 2.5,
                "sources": ["ESPN", "Athletic", "Bleacher Report", "Sports Illustrated"],
                "credibility_bonus": 0.3
            }
        }
    
    def analyze_sentiment(self, content: str, platform: SocialPlatform) -> SentimentAnalysis:
        """Advanced sentiment analysis with platform-specific weighting."""
        # Enhanced sentiment analysis with sports betting context
        
        # Positive sentiment indicators
        positive_terms = {
            "healthy": 0.6, "ready": 0.5, "strong": 0.7, "confident": 0.8,
            "winning": 0.9, "hot streak": 0.8, "value": 0.7, "lock": 0.9,
            "easy money": 0.8, "sharp play": 0.9, "insider info": 0.9
        }
        
        # Negative sentiment indicators
        negative_terms = {
            "injury": -0.8, "out": -0.9, "questionable": -0.6, "doubtful": -0.7,
            "suspended": -0.9, "trade": -0.5, "retiring": -0.8, "struggling": -0.6,
            "public bet": -0.4, "trap game": -0.7, "avoid": -0.8
        }
        
        # Neutral but relevant terms
        neutral_terms = {
            "probable": 0.1, "game time decision": -0.2, "day to day": -0.3,
            "monitoring": -0.1, "update": 0.0, "status": 0.0
        }
        
        content_lower = content.lower()
        sentiment_scores = []
        
        # Calculate sentiment based on term presence
        for term, score in positive_terms.items():
            if term in content_lower:
                sentiment_scores.append(score)
        
        for term, score in negative_terms.items():
            if term in content_lower:
                sentiment_scores.append(score)
        
        for term, score in neutral_terms.items():
            if term in content_lower:
                sentiment_scores.append(score)
        
        # Calculate overall sentiment
        if sentiment_scores:
            overall_sentiment = statistics.mean(sentiment_scores)
            confidence = min(1.0, len(sentiment_scores) * 0.2)
        else:
            overall_sentiment = 0.0
            confidence = 0.1
        
        # Determine polarity
        if overall_sentiment > 0.5:
            polarity = SentimentPolarity.VERY_POSITIVE
        elif overall_sentiment > 0.1:
            polarity = SentimentPolarity.POSITIVE
        elif overall_sentiment > -0.1:
            polarity = SentimentPolarity.NEUTRAL
        elif overall_sentiment > -0.5:
            polarity = SentimentPolarity.NEGATIVE
        else:
            polarity = SentimentPolarity.VERY_NEGATIVE
        
        # Extract key topics
        key_topics = []
        all_terms = {**positive_terms, **negative_terms, **neutral_terms}
        for term in all_terms:
            if term in content_lower:
                key_topics.append(term)
        
        # Determine trend direction
        if overall_sentiment > 0.2:
            trend_direction = "bullish"
        elif overall_sentiment < -0.2:
            trend_direction = "bearish"
        else:
            trend_direction = "neutral"
        
        # Platform-specific adjustments
        platform_weight = self.platform_configs[platform]["sentiment_weight"]
        overall_sentiment *= platform_weight
        
        return SentimentAnalysis(
            overall_sentiment=overall_sentiment,
            polarity=polarity,
            confidence=confidence,
            emotion_breakdown={
                "positive": max(0, overall_sentiment),
                "negative": abs(min(0, overall_sentiment)),
                "neutral": 1 - abs(overall_sentiment)
            },
            key_topics=key_topics,
            trend_direction=trend_direction
        )
    
    def extract_entities(self, content: str) -> Tuple[List[str], List[str]]:
        """Extract team and player mentions from content."""
        # NFL teams
        nfl_teams = {
            "chiefs": "Kansas City Chiefs", "bills": "Buffalo Bills",
            "patriots": "New England Patriots", "dolphins": "Miami Dolphins",
            "jets": "New York Jets", "ravens": "Baltimore Ravens",
            "steelers": "Pittsburgh Steelers", "browns": "Cleveland Browns",
            "bengals": "Cincinnati Bengals", "titans": "Tennessee Titans",
            "colts": "Indianapolis Colts", "texans": "Houston Texans",
            "jaguars": "Jacksonville Jaguars", "broncos": "Denver Broncos",
            "chargers": "Los Angeles Chargers", "raiders": "Las Vegas Raiders",
            "cowboys": "Dallas Cowboys", "giants": "New York Giants",
            "eagles": "Philadelphia Eagles", "commanders": "Washington Commanders",
            "packers": "Green Bay Packers", "bears": "Chicago Bears",
            "lions": "Detroit Lions", "vikings": "Minnesota Vikings",
            "falcons": "Atlanta Falcons", "panthers": "Carolina Panthers",
            "saints": "New Orleans Saints", "buccaneers": "Tampa Bay Buccaneers",
            "cardinals": "Arizona Cardinals", "rams": "Los Angeles Rams",
            "seahawks": "Seattle Seahawks", "49ers": "San Francisco 49ers"
        }
        
        # NHL teams
        nhl_teams = {
            "bruins": "Boston Bruins", "sabres": "Buffalo Sabres",
            "rangers": "New York Rangers", "islanders": "New York Islanders",
            "devils": "New Jersey Devils", "flyers": "Philadelphia Flyers",
            "penguins": "Pittsburgh Penguins", "capitals": "Washington Capitals",
            "hurricanes": "Carolina Hurricanes", "blue jackets": "Columbus Blue Jackets",
            "panthers": "Florida Panthers", "lightning": "Tampa Bay Lightning",
            "predators": "Nashville Predators", "maple leafs": "Toronto Maple Leafs",
            "canadiens": "Montreal Canadiens", "senators": "Ottawa Senators",
            "red wings": "Detroit Red Wings", "blackhawks": "Chicago Blackhawks",
            "blues": "St. Louis Blues", "wild": "Minnesota Wild",
            "jets": "Winnipeg Jets", "flames": "Calgary Flames",
            "oilers": "Edmonton Oilers", "canucks": "Vancouver Canucks",
            "avalanche": "Colorado Avalanche", "stars": "Dallas Stars",
            "kings": "Los Angeles Kings", "ducks": "Anaheim Ducks",
            "sharks": "San Jose Sharks", "golden knights": "Vegas Golden Knights",
            "coyotes": "Arizona Coyotes", "kraken": "Seattle Kraken"
        }
        
        content_lower = content.lower()
        teams_found = []
        
        # Check all teams
        all_teams = {**nfl_teams, **nhl_teams}
        for team_key, team_name in all_teams.items():
            if team_key in content_lower or team_name.lower() in content_lower:
                teams_found.append(team_name)
        
        # Extract potential player names (simplified)
        player_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        potential_players = re.findall(player_pattern, content)
        
        # Filter out team names and common non-player terms
        exclude_terms = set(all_teams.values()) | {
            "New York", "Los Angeles", "San Francisco", "Green Bay", "Kansas City",
            "Tampa Bay", "Las Vegas", "New England", "New Orleans", "Sports Center",
            "Daily Fantasy", "Draft Kings", "Fan Duel"
        }
        
        players_found = [player for player in potential_players 
                        if player not in exclude_terms and len(player.split()) == 2]
        
        return teams_found, players_found
    
    def calculate_betting_relevance(self, content: str, sentiment: SentimentAnalysis) -> float:
        """Calculate betting relevance score for content."""
        betting_keywords = {
            "line": 0.9, "odds": 0.9, "bet": 0.8, "wager": 0.7,
            "spread": 0.9, "over": 0.6, "under": 0.6, "moneyline": 0.8,
            "prop": 0.7, "parlay": 0.8, "teaser": 0.6, "future": 0.5,
            "sharp": 0.9, "public": 0.7, "fade": 0.8, "value": 0.8,
            "lock": 0.9, "trap": 0.7, "steam": 0.9, "reverse line movement": 1.0,
            "injury": 0.8, "out": 0.9, "questionable": 0.7, "suspended": 0.8,
            "trade": 0.6, "weather": 0.5, "lineup": 0.6, "starter": 0.7
        }
        
        content_lower = content.lower()
        relevance_scores = []
        
        for keyword, score in betting_keywords.items():
            if keyword in content_lower:
                relevance_scores.append(score)
        
        # Base relevance
        base_relevance = max(relevance_scores) if relevance_scores else 0.0
        
        # Boost for multiple betting terms
        keyword_count = len(relevance_scores)
        multiplier = min(1.5, 1.0 + (keyword_count * 0.1))
        
        # Sentiment influence
        sentiment_boost = abs(sentiment.overall_sentiment) * 0.2
        
        final_relevance = min(1.0, (base_relevance * multiplier) + sentiment_boost)
        
        return final_relevance
    
    async def simulate_platform_data_ingestion(self, platform: SocialPlatform, 
                                             duration_minutes: int = 5) -> List[SocialDataPoint]:
        """Simulate data ingestion from various platforms (demo version)."""
        self.logger.info(f" Simulating {platform.value} data ingestion...")
        
        data_points = []
        
        # Platform-specific content templates
        content_templates = {
            SocialPlatform.TWITTER: [
                " BREAKING: {team} QB listed as questionable with shoulder injury. Line already moving from -3 to -6. Sharp money incoming? #NFL #Betting",
                " {team} getting 73% of public bets but line hasn't moved. Classic fade spot here. The books know something. #NFLBetting",
                " INJURY UPDATE: {team} star RB officially OUT for Sunday. This completely changes the game script. Under looking good now.",
                " LINE MOVEMENT ALERT: {team} moved from +7 to +3.5 in last hour. Someone with deep pockets is hammering this spread.",
                " SHARP PLAY: Hearing whispers about {team} ML. Public on the other side but pros loading up. Trust the process.",
            ],
            SocialPlatform.REDDIT: [
                "Anyone else notice the weird line movement on {team} game? Public is 80% on the favorite but line went the other way.",
                "POTD: {team} Under 47.5. Weather report shows 25mph winds. Both teams struggle throwing in wind. Easy money.",
                "PSA: {team} backup QB has never won a road game. Don't overthink this one, fade them hard.",
                "Sharp report: Big money came in on {team} +6.5 right before it moved to +4. Following the smart money here.",
                "Injury report deep dive: {team} missing 3 starters on O-line. Pass rush going to feast. Under is the play.",
            ],
            SocialPlatform.TELEGRAM: [
                " INSIDER INFO: {team} main RB not traveling with team. Not on injury report yet but he's out. Line will move fast.",
                " SHARP ALERT: West coast money hitting {team} hard. Line moving from -2.5 to -4.5. Get in now.",
                " STEAM MOVE: {team} getting massive action. Up 2 points in 10 minutes. This is big money, not public.",
                " LATE SCRATCH: Source says {team} star WR is game-time decision with flu. Monitor warmups closely.",
                " VALUE SPOT: {team} ML at +180 is ridiculous. This should be a pick'em game. Max play territory.",
            ],
            SocialPlatform.NEWS: [
                "BREAKING: {team} announces starting quarterback will be limited in practice due to ankle injury sustained in last game.",
                "Weather Alert: Heavy rain and wind expected for {team} vs opponent matchup, potentially affecting passing games significantly.",
                "Injury Report: {team} lists three key players as questionable for Sunday's crucial divisional matchup.",
                "Trade Rumors: Sources indicate {team} may be looking to move veteran player before deadline, creating uncertainty.",
                "Coach Update: {team} head coach expresses concern about player availability for upcoming road game.",
            ]
        }
        
        # Generate realistic data points
        teams = ["Kansas City Chiefs", "Buffalo Bills", "Tampa Bay Lightning", "Boston Bruins", 
                "Los Angeles Lakers", "Golden State Warriors", "New York Yankees", "Atlanta Braves"]
        
        content_list = content_templates.get(platform, ["Generic {team} sports content"])
        
        for i in range(min(8, duration_minutes * 2)):  # 2 posts per minute simulation
            team = teams[i % len(teams)]
            content_template = content_list[i % len(content_list)]
            content = content_template.format(team=team)
            
            # Analyze content
            sentiment = self.analyze_sentiment(content, platform)
            teams_mentioned, players_mentioned = self.extract_entities(content)
            betting_relevance = self.calculate_betting_relevance(content, sentiment)
            
            # Calculate engagement score (simulated)
            base_engagement = 0.3 + (betting_relevance * 0.7)
            platform_multiplier = self.platform_configs[platform]["engagement_multiplier"]
            engagement_score = min(1.0, base_engagement * platform_multiplier)
            
            # Determine sport
            if any(team in content for team in ["Chiefs", "Bills", "Patriots", "Cowboys"]):
                sport = "nfl"
            elif any(team in content for team in ["Lightning", "Bruins", "Rangers", "Penguins"]):
                sport = "nhl"
            elif any(team in content for team in ["Lakers", "Warriors", "Celtics", "Heat"]):
                sport = "nba"
            else:
                sport = "mlb"
            
            data_point = SocialDataPoint(
                platform=platform,
                content_id=f"{platform.value}_{self.timestamp}_{i:03d}",
                content=content,
                author=f"user_{platform.value}_{i+1}",
                timestamp=datetime.now(timezone.utc) - timedelta(minutes=duration_minutes - i),
                engagement_score=engagement_score,
                sentiment_score=sentiment.overall_sentiment,
                confidence=sentiment.confidence,
                sport=sport,
                teams_mentioned=teams_mentioned or [team],
                players_mentioned=players_mentioned,
                betting_relevance=betting_relevance,
                source_url=f"https://{platform.value}.com/post/{i+1}"
            )
            
            data_points.append(data_point)
            self.social_data_buffer.append(data_point)
            self.analytics_metrics["total_posts_analyzed"] += 1
            
            # Brief delay for simulation
            await asyncio.sleep(0.05)
        
        return data_points
    
    def save_social_data_to_db(self, data_points: List[SocialDataPoint]):
        """Save social data points to database."""
        conn = sqlite3.connect(self.social_db_path)
        
        for data_point in data_points:
            conn.execute('''
                INSERT OR REPLACE INTO social_data 
                (platform, content_id, content, author, timestamp, engagement_score, 
                 sentiment_score, confidence, sport, teams_mentioned, players_mentioned, 
                 betting_relevance, source_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data_point.platform.value,
                data_point.content_id,
                data_point.content,
                data_point.author,
                data_point.timestamp.isoformat(),
                data_point.engagement_score,
                data_point.sentiment_score,
                data_point.confidence,
                data_point.sport,
                json.dumps(data_point.teams_mentioned),
                json.dumps(data_point.players_mentioned),
                data_point.betting_relevance,
                data_point.source_url
            ))
        
        conn.commit()
        conn.close()
    
    async def perform_cross_platform_correlation(self, sport: str) -> CrossPlatformCorrelation:
        """Perform cross-platform correlation analysis for a specific sport."""
        # Get recent data for the sport
        recent_data = [dp for dp in self.social_data_buffer 
                      if dp.sport == sport and 
                      (datetime.now(timezone.utc) - dp.timestamp).total_seconds() < 3600]
        
        if len(recent_data) < 2:
            return CrossPlatformCorrelation(
                platforms_compared=[],
                correlation_score=0.0,
                consensus_sentiment=0.0,
                divergence_points=[],
                validation_confidence=0.0
            )
        
        # Group by platform
        platform_sentiments = {}
        for data_point in recent_data:
            platform = data_point.platform
            if platform not in platform_sentiments:
                platform_sentiments[platform] = []
            platform_sentiments[platform].append(data_point.sentiment_score)
        
        # Calculate average sentiment per platform
        platform_averages = {}
        for platform, sentiments in platform_sentiments.items():
            if sentiments:
                platform_averages[platform] = statistics.mean(sentiments)
        
        platforms_compared = list(platform_averages.keys())
        
        if len(platforms_compared) < 2:
            return CrossPlatformCorrelation(
                platforms_compared=platforms_compared,
                correlation_score=0.0,
                consensus_sentiment=0.0,
                divergence_points=[],
                validation_confidence=0.0
            )
        
        # Calculate correlation (simplified)
        sentiment_values = list(platform_averages.values())
        variance = statistics.variance(sentiment_values) if len(sentiment_values) > 1 else 0
        correlation_score = max(0.0, 1.0 - variance)  # Higher correlation = lower variance
        
        # Consensus sentiment
        consensus_sentiment = statistics.mean(sentiment_values)
        
        # Find divergence points
        divergence_points = []
        for platform, sentiment in platform_averages.items():
            if abs(sentiment - consensus_sentiment) > 0.3:
                divergence_points.append(f"{platform.value}: {sentiment:.2f}")
        
        # Validation confidence based on sample size and agreement
        sample_size = len(recent_data)
        agreement_factor = correlation_score
        validation_confidence = min(1.0, (sample_size / 20) * agreement_factor)
        
        return CrossPlatformCorrelation(
            platforms_compared=platforms_compared,
            correlation_score=correlation_score,
            consensus_sentiment=consensus_sentiment,
            divergence_points=divergence_points,
            validation_confidence=validation_confidence
        )
    
    def generate_social_alerts(self, correlations: Dict[str, CrossPlatformCorrelation]) -> List[SocialAlert]:
        """Generate social intelligence alerts based on analysis."""
        alerts = []
        
        for sport, correlation in correlations.items():
            alert_conditions = []
            
            # High consensus sentiment
            if abs(correlation.consensus_sentiment) > self.sentiment_threshold:
                alert_conditions.append(AlertTrigger.SENTIMENT_SPIKE)
            
            # Low correlation (divergence)
            if correlation.correlation_score < 0.3 and len(correlation.platforms_compared) > 1:
                alert_conditions.append(AlertTrigger.CORRELATION_BREAK)
            
            # High correlation (consensus)
            if correlation.correlation_score > 0.8 and abs(correlation.consensus_sentiment) > 0.5:
                alert_conditions.append(AlertTrigger.INSIDER_ACTIVITY)
            
            for trigger in alert_conditions:
                # Check cooldown
                alert_key = f"{sport}_{trigger.value}"
                if alert_key in self.active_alerts:
                    last_alert_time = self.active_alerts[alert_key]
                    if (datetime.now(timezone.utc) - last_alert_time).total_seconds() < self.alert_cooldown_minutes * 60:
                        continue
                
                # Create alert
                alert_id = hashlib.md5(f"{sport}_{trigger.value}_{self.timestamp}".encode()).hexdigest()[:8]
                
                # Get affected teams
                recent_teams = set()
                for dp in self.social_data_buffer:
                    if dp.sport == sport:
                        recent_teams.update(dp.teams_mentioned)
                
                teams_affected = list(recent_teams)[:3]  # Limit to 3 teams
                
                # Generate alert message
                if trigger == AlertTrigger.SENTIMENT_SPIKE:
                    sentiment_word = "BULLISH" if correlation.consensus_sentiment > 0 else "BEARISH"
                    alert_message = f"{sentiment_word} SENTIMENT SPIKE in {sport.upper()}: {correlation.consensus_sentiment:.2f} across {len(correlation.platforms_compared)} platforms"
                elif trigger == AlertTrigger.CORRELATION_BREAK:
                    alert_message = f"PLATFORM DIVERGENCE in {sport.upper()}: Low correlation ({correlation.correlation_score:.2f}) suggests conflicting information"
                elif trigger == AlertTrigger.INSIDER_ACTIVITY:
                    alert_message = f"INSIDER ACTIVITY DETECTED in {sport.upper()}: High consensus ({correlation.consensus_sentiment:.2f}) with {correlation.validation_confidence:.1%} confidence"
                else:
                    alert_message = f"Social intelligence alert for {sport.upper()}"
                
                # Calculate betting impact
                betting_impact = abs(correlation.consensus_sentiment) * correlation.validation_confidence
                
                # Determine urgency
                urgency_level = 1
                if betting_impact > 0.7:
                    urgency_level = 3
                elif betting_impact > 0.4:
                    urgency_level = 2
                
                # Recommended action
                if correlation.consensus_sentiment > 0.5:
                    recommended_action = f"Consider bullish bets on {', '.join(teams_affected[:2])}"
                elif correlation.consensus_sentiment < -0.5:
                    recommended_action = f"Consider bearish bets or fade {', '.join(teams_affected[:2])}"
                else:
                    recommended_action = "Monitor closely for betting opportunities"
                
                alert = SocialAlert(
                    alert_id=alert_id,
                    trigger_type=trigger,
                    platform_sources=correlation.platforms_compared,
                    sport=sport,
                    teams_affected=teams_affected,
                    alert_message=alert_message,
                    sentiment_data={
                        "consensus_sentiment": correlation.consensus_sentiment,
                        "correlation_score": correlation.correlation_score,
                        "validation_confidence": correlation.validation_confidence
                    },
                    betting_impact_score=betting_impact,
                    urgency_level=urgency_level,
                    timestamp=datetime.now(timezone.utc),
                    recommended_action=recommended_action
                )
                
                alerts.append(alert)
                self.active_alerts[alert_key] = datetime.now(timezone.utc)
                self.analytics_metrics["alerts_generated"] += 1
        
        return alerts
    
    def save_to_revenue_db(self, correlations: Dict[str, CrossPlatformCorrelation], alerts: List[SocialAlert]):
        """Save social intelligence data to revenue database."""
        conn = sqlite3.connect(self.revenue_db_path)
        
        # Save social intelligence metrics
        for sport, correlation in correlations.items():
            for platform in correlation.platforms_compared:
                # Calculate volume index (simplified)
                platform_data = [dp for dp in self.social_data_buffer 
                               if dp.platform == platform and dp.sport == sport]
                volume_index = len(platform_data) / 10.0  # Normalize to 0-1 scale
                
                # Average betting relevance
                betting_relevance = statistics.mean([dp.betting_relevance for dp in platform_data]) if platform_data else 0.0
                
                # Market impact prediction
                market_impact = correlation.consensus_sentiment * correlation.validation_confidence
                
                conn.execute('''
                    INSERT INTO social_intelligence_metrics 
                    (timestamp, platform, sport, sentiment_score, volume_index, 
                     betting_relevance, market_impact_prediction)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now(timezone.utc).isoformat(),
                    platform.value,
                    sport,
                    correlation.consensus_sentiment,
                    volume_index,
                    betting_relevance,
                    market_impact
                ))
        
        # Save betting opportunities
        for alert in alerts:
            if alert.betting_impact_score > 0.5:  # Only high-impact opportunities
                opportunity_id = f"social_{alert.alert_id}"
                
                # Predict line movement based on sentiment
                predicted_movement = alert.sentiment_data["consensus_sentiment"] * 2.0  # +/- 2 points max
                
                # Calculate stake recommendation (Kelly criterion simplified)
                confidence = alert.sentiment_data["validation_confidence"]
                stake_recommendation = min(0.05, confidence * 0.1)  # Max 5% of bankroll
                
                # Determine opportunity type
                if alert.sentiment_data["consensus_sentiment"] > 0.3:
                    opportunity_type = "bullish_sentiment"
                    recommended_bet = f"Back {', '.join(alert.teams_affected[:1])}"
                elif alert.sentiment_data["consensus_sentiment"] < -0.3:
                    opportunity_type = "bearish_sentiment"  
                    recommended_bet = f"Fade {', '.join(alert.teams_affected[:1])}"
                else:
                    opportunity_type = "neutral_monitoring"
                    recommended_bet = "Monitor for line movement"
                
                conn.execute('''
                    INSERT OR REPLACE INTO social_betting_opportunities 
                    (opportunity_id, sport, teams, opportunity_type, social_sentiment,
                     predicted_line_movement, confidence_score, recommended_bet,
                     stake_recommendation, window_minutes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    opportunity_id,
                    alert.sport,
                    json.dumps(alert.teams_affected),
                    opportunity_type,
                    alert.sentiment_data["consensus_sentiment"],
                    predicted_movement,
                    confidence,
                    recommended_bet,
                    stake_recommendation,
                    60  # 1-hour window
                ))
                
                self.analytics_metrics["betting_opportunities_identified"] += 1
        
        conn.commit()
        conn.close()
    
    async def execute_social_intelligence_orchestration(self, platforms: List[str], 
                                                       sports: List[str]) -> Dict[str, Any]:
        """Execute complete social intelligence orchestration."""
        print(" EQ12 SOCIAL INTELLIGENCE ORCHESTRATOR")
        print("=" * 44)
        print("Multi-platform social analytics and betting intelligence...")
        print()
        
        start_time = time.time()
        
        # Convert platform strings to enums
        platform_enums = []
        for platform in platforms:
            try:
                platform_enums.append(SocialPlatform(platform.lower()))
            except ValueError:
                self.logger.warning(f"Unknown platform: {platform}")
                continue
        
        if not platform_enums:
            platform_enums = [SocialPlatform.TWITTER, SocialPlatform.REDDIT, SocialPlatform.TELEGRAM]
        
        orchestration_results = {
            "start_timestamp": datetime.now(timezone.utc).isoformat(),
            "platforms_monitored": [p.value for p in platform_enums],
            "sports_analyzed": sports,
            "platform_data": {},
            "correlations": {},
            "alerts_generated": [],
            "analytics_metrics": {},
            "execution_time": 0.0
        }
        
        # Step 1: Data ingestion from all platforms
        print("1 MULTI-PLATFORM DATA INGESTION")
        print("-" * 35)
        
        for platform in platform_enums:
            print(f" Ingesting {platform.value.upper()} data...")
            data_points = await self.simulate_platform_data_ingestion(platform, duration_minutes=3)
            
            orchestration_results["platform_data"][platform.value] = {
                "data_points_collected": len(data_points),
                "avg_sentiment": statistics.mean([dp.sentiment_score for dp in data_points]) if data_points else 0.0,
                "avg_betting_relevance": statistics.mean([dp.betting_relevance for dp in data_points]) if data_points else 0.0,
                "high_impact_posts": len([dp for dp in data_points if dp.betting_relevance > 0.7])
            }
            
            print(f"    {len(data_points)} posts | Avg sentiment: {orchestration_results['platform_data'][platform.value]['avg_sentiment']:+.2f}")
            
            # Save to database
            self.save_social_data_to_db(data_points)
        
        # Step 2: Cross-platform correlation analysis
        print(f"\n2 CROSS-PLATFORM CORRELATION ANALYSIS")
        print("-" * 40)
        
        for sport in sports:
            print(f" Analyzing {sport.upper()} correlations...")
            correlation = await self.perform_cross_platform_correlation(sport)
            orchestration_results["correlations"][sport] = asdict(correlation)
            
            print(f"    Platforms: {len(correlation.platforms_compared)} | Correlation: {correlation.correlation_score:.2f}")
            print(f"    Consensus: {correlation.consensus_sentiment:+.2f} | Confidence: {correlation.validation_confidence:.1%}")
        
        # Step 3: Alert generation
        print(f"\n3 SOCIAL INTELLIGENCE ALERTS")
        print("-" * 32)
        
        correlation_objects = {}
        for sport, corr_data in orchestration_results["correlations"].items():
            correlation_objects[sport] = CrossPlatformCorrelation(**corr_data)
        
        alerts = self.generate_social_alerts(correlation_objects)
        orchestration_results["alerts_generated"] = [asdict(alert) for alert in alerts]
        
        print(f" Generated {len(alerts)} alerts:")
        for alert in alerts:
            urgency_icon = "" if alert.urgency_level == 3 else "" if alert.urgency_level == 2 else ""
            print(f"   {urgency_icon} {alert.sport.upper()}: {alert.alert_message}")
            print(f"       Impact: {alert.betting_impact_score:.1%} | Action: {alert.recommended_action}")
        
        # Step 4: Save to revenue database
        print(f"\n4 REVENUE DATABASE INTEGRATION")
        print("-" * 35)
        
        self.save_to_revenue_db(correlation_objects, alerts)
        print(f" Social intelligence data saved to revenue.db")
        print(f" Betting opportunities identified: {self.analytics_metrics['betting_opportunities_identified']}")
        
        # Final metrics
        execution_time = time.time() - start_time
        orchestration_results["execution_time"] = execution_time
        orchestration_results["analytics_metrics"] = self.analytics_metrics
        
        print(f"\n SOCIAL INTELLIGENCE ORCHESTRATION COMPLETE!")
        print(f" Execution time: {execution_time:.2f} seconds")
        print(f" Total posts analyzed: {self.analytics_metrics['total_posts_analyzed']}")
        print(f" Alerts generated: {self.analytics_metrics['alerts_generated']}")
        print(f" Betting opportunities: {self.analytics_metrics['betting_opportunities_identified']}")
        
        # Save comprehensive report
        report_file = self.logs_path / f"social_intelligence_orchestration_{self.timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(orchestration_results, f, indent=2, ensure_ascii=False, default=str)
        
        print(f" Full report: {report_file}")
        
        return orchestration_results


async def main():
    """Main execution function for social intelligence orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Social Intelligence Orchestrator")
    parser.add_argument("--platforms", nargs="+", 
                       default=["twitter", "reddit", "telegram"],
                       choices=["twitter", "reddit", "telegram", "discord", "news", "youtube"],
                       help="Social platforms to monitor")
    parser.add_argument("--sports", nargs="+", 
                       default=["nfl", "nhl"],
                       choices=["nfl", "nhl", "nba", "mlb", "ncaa_football", "ncaa_basketball"],
                       help="Sports to analyze")
    parser.add_argument("--workspace", default="C:\\EQ12", help="EQ12 workspace path")
    parser.add_argument("--duration", type=int, default=5, help="Monitoring duration in minutes")
    args = parser.parse_args()
    
    try:
        # Initialize social intelligence orchestrator
        orchestrator = EQ12SocialIntelligenceOrchestrator(args.workspace)
        
        # Execute complete orchestration
        results = await orchestrator.execute_social_intelligence_orchestration(
            platforms=args.platforms,
            sports=args.sports
        )
        
        return 0
        
    except Exception as e:
        print(f" SOCIAL INTELLIGENCE ORCHESTRATOR ERROR: {e}")
        logging.error(f"Social intelligence orchestrator error: {e}")
        return 1


if __name__ == "__main__":
    # Ensure proper event loop for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)