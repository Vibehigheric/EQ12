#!/usr/bin/env python3
"""
🤖 EQ12 X-Factor Data Pipeline
Advanced real-time social sentiment analysis for sports betting edge detection
Integrates X API, OpenAI sentiment analysis, and source-weighted scoring
"""

import asyncio
import json
import logging
import os
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from openai import AsyncOpenAI

# Setup logging with UTF-8 encoding fix
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/eq12_x_factor.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class XFactorEvent:
    """Represents a processed X/Twitter event with sentiment scoring"""

    tweet_id: str
    user_handle: str
    text: str
    raw_sentiment: float
    source_weight: float
    weighted_sentiment: float
    keywords: list[str]
    detected_entities: list[str]
    timestamp: datetime
    confidence_score: float


@dataclass
class SharpUser:
    """Represents a verified sharp bettor or insider source"""

    handle: str
    verification_status: str
    historical_accuracy: float
    follower_count: int
    weight_multiplier: float
    category: str  # 'insider', 'beat_writer', 'analyst', 'sharp_bettor'


class XFactorDatabase:
    """SQLite database for storing X-Factor events and user profiles"""

    def __init__(self, db_path: str = "data/xfactor.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # X-Factor events table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS xfactor_events (
            tweet_id TEXT PRIMARY KEY,
            user_handle TEXT,
            text TEXT,
            raw_sentiment REAL,
            source_weight REAL,
            weighted_sentiment REAL,
            keywords TEXT,
            detected_entities TEXT,
            timestamp TEXT,
            confidence_score REAL
        )
        """
        )

        # Sharp users table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS sharp_users (
            handle TEXT PRIMARY KEY,
            verification_status TEXT,
            historical_accuracy REAL,
            follower_count INTEGER,
            weight_multiplier REAL,
            category TEXT,
            last_updated TEXT
        )
        """
        )

        # Sentiment trends table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS sentiment_trends (
            entity TEXT,
            time_bucket TEXT,
            avg_sentiment REAL,
            event_count INTEGER,
            confidence REAL,
            PRIMARY KEY (entity, time_bucket)
        )
        """
        )

        conn.commit()
        conn.close()

    def store_xfactor_event(self, event: XFactorEvent):
        """Store X-Factor event in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        INSERT OR REPLACE INTO xfactor_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                event.tweet_id,
                event.user_handle,
                event.text,
                event.raw_sentiment,
                event.source_weight,
                event.weighted_sentiment,
                json.dumps(event.keywords),
                json.dumps(event.detected_entities),
                event.timestamp.isoformat(),
                event.confidence_score,
            ),
        )

        conn.commit()
        conn.close()


class SentimentAnalyzer:
    """Advanced sentiment analysis with sarcasm detection using OpenAI"""

    def __init__(self, api_key: str, config: dict):
        self.client = AsyncOpenAI(api_key=api_key)
        self.config = config
        self.sarcasm_threshold = config.get("NLP_SARCASM_THRESHOLD", 0.85)

    async def analyze_sentiment(self, text: str, context: dict | None = None) -> dict[str, Any]:
        """
        Analyze sentiment with advanced sarcasm detection and sports context
        Returns: {sentiment: float, confidence: float, sarcasm_detected: bool}
        """
        try:
            # Enhanced prompt with sports betting context
            prompt = self._build_sentiment_prompt(text, context)

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=100,
                temperature=0.1,
            )

            # Parse structured response
            result = self._parse_sentiment_response(response.choices[0].message.content)

            logger.info(
                f"🧠 Sentiment analyzed: {result['sentiment']:.3f} (confidence: {result['confidence']:.3f})"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Sentiment analysis failed: {e}")
            return {"sentiment": 0.0, "confidence": 0.0, "sarcasm_detected": False}

    def _build_sentiment_prompt(self, text: str, context: dict | None = None) -> str:
        """Build comprehensive sentiment analysis prompt"""
        prompt = f"""
        Analyze the sentiment of this sports-related social media post for betting implications:

        Text: "{text}"

        Consider:
        1. Sarcasm and irony (common in sports discourse)
        2. Injury news impact (negative for player, positive for opposing bets)
        3. Weather conditions for outdoor sports
        4. Lineup changes and coaching decisions
        5. Fan emotional reactions vs. factual reporting

        Return ONLY this format:
        SENTIMENT: [number between -1.0 and 1.0]
        CONFIDENCE: [number between 0.0 and 1.0]
        SARCASM: [YES/NO]
        """

        if context:
            prompt += f"\nAdditional context: {json.dumps(context, indent=2)}"

        return prompt

    def _get_system_prompt(self) -> str:
        """System prompt for sports sentiment analysis"""
        return """You are an expert sports betting sentiment analyzer. You understand:
        - Sarcasm and irony in sports social media
        - The difference between fan emotion and actionable information
        - How injury news, weather, and lineup changes affect betting lines
        - The credibility indicators of different source types

        Provide precise numerical sentiment scores optimized for betting edge detection."""

    def _parse_sentiment_response(self, response_text: str) -> dict[str, Any]:
        """Parse structured sentiment response"""
        try:
            sentiment_match = re.search(r"SENTIMENT:\s*([-+]?\d*\.?\d+)", response_text)
            confidence_match = re.search(r"CONFIDENCE:\s*([-+]?\d*\.?\d+)", response_text)
            sarcasm_match = re.search(r"SARCASM:\s*(YES|NO)", response_text)

            sentiment = float(sentiment_match.group(1)) if sentiment_match else 0.0
            confidence = float(confidence_match.group(1)) if confidence_match else 0.5
            sarcasm = sarcasm_match.group(1) == "YES" if sarcasm_match else False

            # Clamp values to valid ranges
            sentiment = max(-1.0, min(1.0, sentiment))
            confidence = max(0.0, min(1.0, confidence))

            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "sarcasm_detected": sarcasm,
            }

        except Exception as e:
            logger.error(f"❌ Failed to parse sentiment response: {e}")
            return {"sentiment": 0.0, "confidence": 0.0, "sarcasm_detected": False}


class XFactorPipeline:
    """Main X-Factor pipeline for real-time social sentiment analysis"""

    def __init__(self, config_path: str = "sports_betting_config.json"):
        self.config = self._load_config(config_path)
        self.xfactor_config = self.config.get("X_FACTOR_SETTINGS", {})
        self.database = XFactorDatabase()
        self.sentiment_analyzer = None
        self.sharp_users = self._load_sharp_users()
        self.running = False

        # Performance metrics
        self.stats = {
            "events_processed": 0,
            "high_confidence_events": 0,
            "api_calls": 0,
            "start_time": None,
        }

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"⚠️ Config file not found: {config_path}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> dict:
        """Default configuration for X-Factor pipeline"""
        return {
            "X_FACTOR_SETTINGS": {
                "SHARP_USER_LIST_PATH": "configs/sharp_bettors.txt",
                "NLP_SARCASM_THRESHOLD": 0.85,
                "REAL_TIME_SPIKE_THRESHOLD_PPM": 500,
                "SENTIMENT_WEIGHTING": {
                    "VERIFIED_INSIDER": 1.5,
                    "TEAM_BEAT_WRITER": 1.2,
                    "VERIFIED_ANALYST": 1.1,
                    "SHARP_BETTOR": 1.3,
                    "GENERIC_FAN_ACCOUNT": 0.1,
                },
                "MIN_CONFIDENCE_THRESHOLD": 0.7,
                "KEYWORDS": [
                    "injury",
                    "injured",
                    "questionable",
                    "doubtful",
                    "out",
                    "weather",
                    "rain",
                    "snow",
                    "wind",
                    "conditions",
                    "lineup",
                    "starting",
                    "benched",
                    "suspended",
                    "trade",
                ],
            }
        }

    def _load_sharp_users(self) -> dict[str, SharpUser]:
        """Load sharp user database from file"""
        sharp_users = {}

        # Load from database
        conn = sqlite3.connect(self.database.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sharp_users")
        rows = cursor.fetchall()

        for row in rows:
            user = SharpUser(
                handle=row[0],
                verification_status=row[1],
                historical_accuracy=row[2],
                follower_count=row[3],
                weight_multiplier=row[4],
                category=row[5],
            )
            sharp_users[user.handle.lower()] = user

        conn.close()

        # If no users in database, load defaults
        if not sharp_users:
            sharp_users = self._get_default_sharp_users()

        logger.info(f"📊 Loaded {len(sharp_users)} sharp users")
        return sharp_users

    def _get_default_sharp_users(self) -> dict[str, SharpUser]:
        """Default sharp users for testing"""
        default_users = [
            SharpUser("adamschefter", "verified", 0.92, 10000000, 1.5, "insider"),
            SharpUser("wojespn", "verified", 0.95, 6000000, 1.5, "insider"),
            SharpUser("shamscharania", "verified", 0.90, 2000000, 1.4, "insider"),
            SharpUser("rapoport", "verified", 0.88, 4000000, 1.3, "insider"),
        ]

        return {user.handle.lower(): user for user in default_users}

    async def initialize(self):
        """Initialize the X-Factor pipeline"""
        try:
            # Initialize sentiment analyzer
            openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("CHATGPT_API_KEY")
            if not openai_key:
                raise ValueError("OpenAI API key not found in environment variables")

            self.sentiment_analyzer = SentimentAnalyzer(openai_key, self.xfactor_config)

            logger.info("✅ X-Factor Pipeline initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize X-Factor Pipeline: {e}")
            raise

    async def process_social_event(self, event_data: dict) -> XFactorEvent | None:
        """Process a single social media event"""
        try:
            # Extract basic event information
            tweet_id = event_data.get("id", "")
            text = event_data.get("text", "")
            user_data = event_data.get("user", {})
            user_handle = user_data.get("username", "").lower()

            if not text or not user_handle:
                return None

            # Check for sports betting keywords
            if not self._contains_relevant_keywords(text):
                return None

            # Analyze sentiment
            sentiment_result = await self.sentiment_analyzer.analyze_sentiment(text)

            # Get source weight
            source_weight = self._get_source_weight(user_handle, user_data)

            # Calculate weighted sentiment
            weighted_sentiment = sentiment_result["sentiment"] * source_weight

            # Extract entities and keywords
            keywords = self._extract_keywords(text)
            entities = self._extract_entities(text)

            # Create X-Factor event
            xfactor_event = XFactorEvent(
                tweet_id=tweet_id,
                user_handle=user_handle,
                text=text,
                raw_sentiment=sentiment_result["sentiment"],
                source_weight=source_weight,
                weighted_sentiment=weighted_sentiment,
                keywords=keywords,
                detected_entities=entities,
                timestamp=datetime.now(UTC),
                confidence_score=sentiment_result["confidence"],
            )

            # Store in database
            self.database.store_xfactor_event(xfactor_event)

            # Update statistics
            self.stats["events_processed"] += 1
            if sentiment_result["confidence"] > self.xfactor_config.get(
                "MIN_CONFIDENCE_THRESHOLD", 0.7
            ):
                self.stats["high_confidence_events"] += 1

            logger.info(
                f"🎯 X-Factor event: @{user_handle} | Sentiment: {weighted_sentiment:.3f} | Confidence: {sentiment_result['confidence']:.3f}"
            )

            return xfactor_event

        except Exception as e:
            logger.error(f"❌ Failed to process social event: {e}")
            return None

    def _contains_relevant_keywords(self, text: str) -> bool:
        """Check if text contains sports betting relevant keywords"""
        keywords = self.xfactor_config.get("KEYWORDS", [])
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in keywords)

    def _get_source_weight(self, user_handle: str, user_data: dict) -> float:
        """Calculate source weight based on user credibility"""
        # Check if user is in sharp users database
        if user_handle in self.sharp_users:
            return self.sharp_users[user_handle].weight_multiplier

        # Use verification status and follower count for unknown users
        verified = user_data.get("verified", False)
        followers = user_data.get("public_metrics", {}).get("followers_count", 0)

        if verified and followers > 1000000:
            return 1.2  # Verified high-profile account
        if verified and followers > 100000:
            return 1.0  # Verified moderate account
        if followers > 500000:
            return 0.8  # High-follower unverified
        return 0.1  # Generic account

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract relevant keywords from text"""
        keywords = []
        text_lower = text.lower()

        for keyword in self.xfactor_config.get("KEYWORDS", []):
            if keyword.lower() in text_lower:
                keywords.append(keyword)

        return keywords

    def _extract_entities(self, text: str) -> list[str]:
        """Extract sports entities (teams, players) from text"""
        # Simple entity extraction (could be enhanced with NER)
        entities = []

        # Common team abbreviations
        team_patterns = [
            r"\b[A-Z]{2,4}\b",  # Team abbreviations like LAL, GSW
            r"@\w+",  # Mentions
            r"#\w+",  # Hashtags
        ]

        for pattern in team_patterns:
            matches = re.findall(pattern, text)
            entities.extend(matches)

        return entities

    async def run_demo_mode(self):
        """Run X-Factor pipeline in demo mode with simulated events"""
        logger.info("🎭 Starting X-Factor Pipeline in Demo Mode...")

        # Initialize pipeline
        await self.initialize()

        # Simulate social media events
        demo_events = [
            {
                "id": "1234567890",
                "text": "BREAKING: LeBron James questionable for tonight's game with ankle injury. Lakers spread now moving from -3.5 to -1.5 #NBA",
                "user": {
                    "username": "ESPNStatsInfo",
                    "verified": True,
                    "public_metrics": {"followers_count": 2500000},
                },
            },
            {
                "id": "1234567891",
                "text": "Weather update: Heavy rain expected for Bills vs Patriots game. Over/Under could be affected significantly",
                "user": {
                    "username": "WeatherChannel",
                    "verified": True,
                    "public_metrics": {"followers_count": 1500000},
                },
            },
            {
                "id": "1234567892",
                "text": "Mahomes looking sharp in warmups. That knee injury must be fine. Chiefs going to cover easily! 🔥",
                "user": {
                    "username": "ChiefsFan2024",
                    "verified": False,
                    "public_metrics": {"followers_count": 150},
                },
            },
        ]

        # Process demo events
        for event in demo_events:
            xfactor_event = await self.process_social_event(event)
            if xfactor_event:
                print(f"📊 Processed: {xfactor_event.weighted_sentiment:.3f} weighted sentiment")
            await asyncio.sleep(1)  # Small delay for demo

        # Print statistics
        self._print_statistics()

        logger.info("✅ X-Factor Pipeline demo completed")

    def _print_statistics(self):
        """Print pipeline statistics"""
        print("\n" + "=" * 60)
        print("🎯 X-FACTOR PIPELINE STATISTICS")
        print("=" * 60)
        print(f"📊 Events Processed: {self.stats['events_processed']}")
        print(f"🎯 High Confidence Events: {self.stats['high_confidence_events']}")
        print(f"🧠 API Calls Made: {self.stats['api_calls']}")
        print(f"👥 Sharp Users Loaded: {len(self.sharp_users)}")
        print("=" * 60)


async def main():
    """Main entry point for X-Factor Pipeline"""
    pipeline = XFactorPipeline()
    await pipeline.run_demo_mode()


if __name__ == "__main__":
    asyncio.run(main())
