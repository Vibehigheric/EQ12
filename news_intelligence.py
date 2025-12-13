#!/usr/bin/env python3
"""
EQ12 News Intelligence Module
Integrates Bing News API + Google News RSS with EQ12 stack-specific intelligence and analysis.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import json
import logging
import sys
import time
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

# Add paths for integration
BASE_DIR = Path(__file__).resolve().parent
GODSTACK2_DIR = Path(r"C:\EQ12\eq12_godstack2")
sys.path.insert(0, str(GODSTACK2_DIR))

# Import existing news aggregator components
try:
    from clients import BingClient
    from news_aggregator import GOOGLE_NEWS_RSS, google_news

    NEWS_AGGREGATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: News aggregator not available: {e}")
    NEWS_AGGREGATOR_AVAILABLE = False

# Import enhanced database for intelligence storage
try:
    sys.path.insert(0, str(BASE_DIR / "eq12_meta_search"))
    from enhanced_db import (
        cache_stack_analysis,
        get_cached_analysis,
        record_performance_metric,
        upsert_enhanced_results,
    )

    ENHANCED_DB_AVAILABLE = True
except ImportError:
    ENHANCED_DB_AVAILABLE = False

logger = logging.getLogger("news_intelligence")


class NewsIntelligence:
    """
    Enhanced news aggregation with EQ12 stack intelligence
    """

    # Stack-specific news keywords and sentiment indicators
    STACK_NEWS_PROFILES = {
        "betting": {
            "keywords": [
                # Injuries and roster
                "injury",
                "injured",
                "out for",
                "questionable",
                "doubtful",
                "probable",
                "roster",
                "lineup",
                "starting",
                "benched",
                "suspended",
                "traded",
                # Performance indicators
                "upset",
                "underdog",
                "favorite",
                "odds",
                "line movement",
                "sharp money",
                "public betting",
                "consensus",
                "contrarian",
                "value bet",
                # League-specific
                "nfl",
                "nba",
                "mlb",
                "nhl",
                "ncaa",
                "college basketball",
                "march madness",
                "playoff",
                "championship",
                "super bowl",
                "world series",
                "stanley cup",
            ],
            "sentiment_boosters": {
                "positive": [
                    "healthy",
                    "cleared",
                    "expected to play",
                    "upgraded",
                    "probable",
                ],
                "negative": [
                    "injured",
                    "out",
                    "surgery",
                    "IR",
                    "doubtful",
                    "downgraded",
                ],
            },
            "priority_sources": [
                "espn.com",
                "nfl.com",
                "nba.com",
                "athletic.com",
                "yahoo.com",
            ],
            "urgency_indicators": ["breaking", "just in", "urgent", "alert", "now"],
            "telegram_emoji": "🏈",
        },
        "travel": {
            "keywords": [
                # Deals and disruptions
                "flight deal",
                "airfare",
                "hotel deal",
                "vacation package",
                "travel alert",
                "airport delay",
                "flight cancellation",
                "tsa",
                "security",
                "weather",
                # Destinations and events
                "buffalo",
                "destination",
                "tourism",
                "attractions",
                "events",
                "festival",
                "conference",
                "convention",
                "holiday travel",
                "peak season",
                # Airlines and services
                "southwest",
                "jetblue",
                "american",
                "delta",
                "united",
                "booking",
                "expedia",
            ],
            "sentiment_boosters": {
                "positive": [
                    "deal",
                    "discount",
                    "sale",
                    "cheap",
                    "promotion",
                    "special offer",
                ],
                "negative": ["delay", "cancellation", "strike", "disruption", "closed"],
            },
            "priority_sources": ["cnn.com", "usatoday.com", "travelandleisure.com"],
            "urgency_indicators": [
                "today only",
                "limited time",
                "flash sale",
                "breaking",
            ],
            "telegram_emoji": "✈️",
        },
        "cannabis": {
            "keywords": [
                # Legal and regulatory
                "cannabis",
                "marijuana",
                "legalization",
                "dispensary",
                "license",
                "regulation",
                "medical marijuana",
                "recreational",
                "decriminalization",
                "reform",
                # Market and business
                "cannabis industry",
                "hemp",
                "cbd",
                "cultivation",
                "grower",
                "processor",
                "retail",
                "investment",
                "stock",
                "earnings",
                "merger",
                "ipo",
                # Local (Buffalo/NY specific)
                "new york cannabis",
                "ny marijuana",
                "buffalo dispensary",
                "western ny",
            ],
            "sentiment_boosters": {
                "positive": ["legalized", "approved", "passed", "expansion", "growth"],
                "negative": ["banned", "rejected", "crackdown", "illegal", "seized"],
            },
            "priority_sources": ["leafly.com", "marijuanamoment.net", "cannabis.net"],
            "urgency_indicators": ["breaking", "just passed", "approved today"],
            "telegram_emoji": "🌿",
        },
        "finance": {
            "keywords": [
                # Markets and trading
                "stock market",
                "crypto",
                "bitcoin",
                "ethereum",
                "trading",
                "investment",
                "earnings",
                "dividend",
                "ipo",
                "merger",
                "acquisition",
                "fed",
                "interest rate",
                # Economic indicators
                "inflation",
                "gdp",
                "unemployment",
                "consumer confidence",
                "recession",
                "bull market",
                "bear market",
                "volatility",
                "correction",
                # Specific assets
                "tesla",
                "apple",
                "microsoft",
                "amazon",
                "google",
                "meta",
                "nvidia",
            ],
            "sentiment_boosters": {
                "positive": [
                    "up",
                    "gains",
                    "rally",
                    "bullish",
                    "breakthrough",
                    "record high",
                ],
                "negative": [
                    "down",
                    "losses",
                    "crash",
                    "bearish",
                    "decline",
                    "selloff",
                ],
            },
            "priority_sources": [
                "bloomberg.com",
                "reuters.com",
                "marketwatch.com",
                "yahoo.com",
            ],
            "urgency_indicators": ["breaking", "alert", "flash", "urgent"],
            "telegram_emoji": "📈",
        },
        "fleet": {
            "keywords": [
                # Auto industry
                "auto",
                "car",
                "vehicle",
                "automotive",
                "dealership",
                "sales",
                "recall",
                "safety",
                "insurance",
                "maintenance",
                "repair",
                "fuel",
                "gas prices",
                # Electric and tech
                "electric vehicle",
                "ev",
                "tesla",
                "charging",
                "battery",
                "autonomous",
                "self-driving",
                "uber",
                "lyft",
                "rideshare",
                "car sharing",
                # Fleet specific
                "rental car",
                "fleet management",
                "commercial vehicle",
                "truck",
                "logistics",
            ],
            "sentiment_boosters": {
                "positive": [
                    "innovation",
                    "breakthrough",
                    "efficiency",
                    "savings",
                    "green",
                ],
                "negative": [
                    "recall",
                    "defect",
                    "accident",
                    "lawsuit",
                    "investigation",
                ],
            },
            "priority_sources": [
                "automotive.com",
                "cars.com",
                "edmunds.com",
                "motortrend.com",
            ],
            "urgency_indicators": ["recall alert", "breaking", "urgent safety"],
            "telegram_emoji": "🚗",
        },
    }

    def __init__(self, verbose: bool = False):
        """Initialize News Intelligence module"""
        self.verbose = verbose
        self.setup_logging()

        if not NEWS_AGGREGATOR_AVAILABLE:
            raise ValueError("News aggregator not available - check godstack2 installation")

        # Initialize clients
        self.bing_client = BingClient()

    def setup_logging(self):
        """Setup EQ12-standard logging"""
        log_level = logging.INFO if self.verbose else logging.WARNING
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def detect_news_stack(self, article: dict[str, Any]) -> tuple[str | None, float]:
        """
        Detect which EQ12 stack a news article belongs to

        Args:
            article: News article dictionary

        Returns:
            Tuple of (stack_name, confidence_score)
        """
        title = article.get("title", "").lower()
        snippet = article.get("snippet", "").lower()

        # Combine text for analysis
        article_text = f"{title} {snippet}"

        stack_scores = {}

        # Score each stack based on keyword matches
        for stack, profile in self.STACK_NEWS_PROFILES.items():
            score = 0
            matched_keywords = []

            for keyword in profile["keywords"]:
                if keyword in article_text:
                    score += 1
                    matched_keywords.append(keyword)

            # Bonus for source authority
            url = article.get("url", "")
            for priority_source in profile.get("priority_sources", []):
                if priority_source in url:
                    score += 2
                    break

            # Urgency bonus
            for urgency_term in profile.get("urgency_indicators", []):
                if urgency_term in article_text:
                    score += 1.5
                    break

            if score > 0:
                # Normalize confidence (rough heuristic)
                confidence = min(1.0, score / 5.0)
                stack_scores[stack] = (confidence, matched_keywords)

        if stack_scores:
            # Return stack with highest confidence
            best_stack = max(stack_scores.keys(), key=lambda k: stack_scores[k][0])
            confidence, _keywords = stack_scores[best_stack]

            if confidence >= 0.2:  # Minimum threshold
                return best_stack, confidence

        return None, 0.0

    def analyze_news_sentiment(self, article: dict[str, Any], stack: str | None) -> dict[str, Any]:
        """
        Analyze news sentiment for stack-specific implications

        Args:
            article: News article dictionary
            stack: Detected stack (optional)

        Returns:
            Sentiment analysis dictionary
        """
        title = article.get("title", "").lower()
        snippet = article.get("snippet", "").lower()
        article_text = f"{title} {snippet}"

        sentiment_data = {
            "overall_sentiment": "neutral",
            "sentiment_score": 0.0,  # -1.0 to 1.0
            "confidence": 0.5,
            "key_indicators": [],
            "stack_impact": "neutral",
        }

        if not stack:
            return sentiment_data

        profile = self.STACK_NEWS_PROFILES.get(stack, {})
        sentiment_boosters = profile.get("sentiment_boosters", {})

        positive_score = 0
        negative_score = 0
        indicators = []

        # Check positive indicators
        for term in sentiment_boosters.get("positive", []):
            if term in article_text:
                positive_score += 1
                indicators.append(f"+{term}")

        # Check negative indicators
        for term in sentiment_boosters.get("negative", []):
            if term in article_text:
                negative_score += 1
                indicators.append(f"-{term}")

        # Calculate overall sentiment
        if positive_score > negative_score:
            sentiment_data["overall_sentiment"] = "positive"
            sentiment_data["sentiment_score"] = min(1.0, (positive_score - negative_score) / 3.0)
            sentiment_data["stack_impact"] = (
                "bullish" if stack in ["finance", "betting"] else "positive"
            )
        elif negative_score > positive_score:
            sentiment_data["overall_sentiment"] = "negative"
            sentiment_data["sentiment_score"] = max(-1.0, -(negative_score - positive_score) / 3.0)
            sentiment_data["stack_impact"] = (
                "bearish" if stack in ["finance", "betting"] else "negative"
            )

        sentiment_data["key_indicators"] = indicators
        sentiment_data["confidence"] = min(1.0, (positive_score + negative_score) / 2.0)

        return sentiment_data

    def calculate_news_urgency(self, article: dict[str, Any], stack: str | None) -> dict[str, Any]:
        """
        Calculate urgency and time-sensitivity of news article

        Args:
            article: News article dictionary
            stack: Detected stack

        Returns:
            Urgency analysis dictionary
        """
        title = article.get("title", "").lower()
        snippet = article.get("snippet", "").lower()
        article_text = f"{title} {snippet}"

        urgency_data = {
            "urgency_score": 0.0,  # 0.0 to 1.0
            "time_sensitivity": "normal",
            "action_required": False,
            "indicators": [],
        }

        # General urgency indicators
        general_urgent = ["breaking", "urgent", "alert", "just in", "now", "live"]
        urgent_score = sum(1 for term in general_urgent if term in article_text)

        # Stack-specific urgency
        if stack:
            profile = self.STACK_NEWS_PROFILES.get(stack, {})
            stack_urgent = profile.get("urgency_indicators", [])
            urgent_score += sum(1 for term in stack_urgent if term in article_text) * 1.5

        # Time-based indicators
        time_sensitive = ["today", "tonight", "now", "immediate", "expires", "deadline"]
        urgent_score += sum(0.5 for term in time_sensitive if term in article_text)

        # Calculate final urgency
        urgency_data["urgency_score"] = min(1.0, urgent_score / 3.0)

        if urgency_data["urgency_score"] >= 0.8:
            urgency_data["time_sensitivity"] = "critical"
            urgency_data["action_required"] = True
        elif urgency_data["urgency_score"] >= 0.5:
            urgency_data["time_sensitivity"] = "high"
        elif urgency_data["urgency_score"] >= 0.3:
            urgency_data["time_sensitivity"] = "medium"

        # Stack-specific action requirements
        if stack == "betting" and any(
            term in article_text for term in ["injury", "lineup", "suspended"]
        ):
            urgency_data["action_required"] = True
            urgency_data["indicators"].append("Betting line impact")

        if stack == "travel" and any(
            term in article_text for term in ["flight deal", "sale", "limited time"]
        ):
            urgency_data["action_required"] = True
            urgency_data["indicators"].append("Time-limited deal")

        return urgency_data

    def enhance_news_with_intelligence(
        self, articles: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Enhance news articles with EQ12 intelligence metadata

        Args:
            articles: List of raw news articles

        Returns:
            List of enhanced articles with intelligence metadata
        """
        enhanced_articles = []

        for article in articles:
            # Detect stack and confidence
            detected_stack, confidence = self.detect_news_stack(article)

            # Analyze sentiment
            sentiment = self.analyze_news_sentiment(article, detected_stack)

            # Calculate urgency
            urgency = self.calculate_news_urgency(article, detected_stack)

            # Enhance article with intelligence metadata
            enhanced_article = {
                **article,
                # Intelligence metadata
                "detected_stack": detected_stack,
                "confidence_score": confidence,
                "intelligence_used": True,
                "enhancement_source": "news_intelligence",
                # Sentiment analysis
                "sentiment_analysis": sentiment,
                "sentiment_score": sentiment["sentiment_score"],
                # Urgency analysis
                "urgency_analysis": urgency,
                "urgency_score": urgency["urgency_score"],
                "time_sensitivity": urgency["time_sensitivity"],
                "action_required": urgency["action_required"],
                # EQ12 integration fields
                "content_type": "news",
                "primary_category": "news",
                "secondary_category": detected_stack or "general",
                "telegram_emoji": self._get_telegram_emoji(detected_stack),
                # Processing metadata
                "processing_timestamp": datetime.now(UTC).isoformat(),
                "relevance_score": confidence * (1 + urgency["urgency_score"]),
            }

            enhanced_articles.append(enhanced_article)

        # Sort by relevance (confidence * urgency)
        enhanced_articles.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return enhanced_articles

    def _get_telegram_emoji(self, stack: str | None) -> str:
        """Get emoji for Telegram alerts based on stack"""
        if not stack:
            return "📰"
        return self.STACK_NEWS_PROFILES.get(stack, {}).get("telegram_emoji", "📰")

    def aggregate_news_with_analysis(
        self, query: str, stack: str | None = None, count: int = 10, hours: int = 24
    ) -> dict[str, Any]:
        """
        Aggregate news with comprehensive intelligence analysis

        Args:
            query: Search query for news
            stack: Target stack (optional, will auto-detect)
            count: Number of articles to return
            hours: Time window for news (hours back)

        Returns:
            Dictionary with news and analysis
        """
        start_time = time.time()

        # Auto-detect stack from query if not provided
        if not stack:
            for stack_name, profile in self.STACK_NEWS_PROFILES.items():
                if any(keyword in query.lower() for keyword in profile["keywords"][:10]):
                    stack = stack_name
                    break

        all_articles = []

        try:
            # Get Bing News
            if hasattr(self.bing_client, "news_search"):
                bing_articles = self.bing_client.news_search(query, count)
                all_articles.extend(bing_articles)
            else:
                logger.warning("Bing news search not available")

            # Get Google News RSS
            google_articles = google_news(query, count)
            all_articles.extend(google_articles)

        except Exception as e:
            logger.error(f"News aggregation failed: {e}")

        # Enhance with intelligence
        enhanced_articles = self.enhance_news_with_intelligence(all_articles)

        # Filter by time window if published_at is available
        if hours < 168:  # Only filter if less than a week
            cutoff_time = datetime.now(UTC) - timedelta(hours=hours)
            time_filtered = []

            for article in enhanced_articles:
                pub_date = article.get("published_at")
                if pub_date:
                    try:
                        # Parse various date formats
                        if isinstance(pub_date, str):
                            # Try to parse ISO format first
                            try:
                                article_time = datetime.fromisoformat(
                                    pub_date.replace("Z", "+00:00")
                                )
                            except:
                                # Try other common formats
                                from dateutil.parser import parse

                                article_time = parse(pub_date)

                            if article_time >= cutoff_time:
                                time_filtered.append(article)
                        else:
                            time_filtered.append(article)  # Keep if no date
                    except:
                        time_filtered.append(article)  # Keep if date parsing fails
                else:
                    time_filtered.append(article)  # Keep if no published date

            enhanced_articles = time_filtered

        # Filter by stack relevance if specified
        if stack:
            stack_articles = [
                article
                for article in enhanced_articles
                if article.get("detected_stack") == stack
                or article.get("confidence_score", 0) >= 0.3
            ]
            enhanced_articles = stack_articles

        # Limit results
        final_articles = enhanced_articles[:count]

        # Generate comprehensive analysis
        analysis = self._generate_news_analysis(final_articles, query, stack)

        # Record performance metrics
        processing_time = (time.time() - start_time) * 1000
        if ENHANCED_DB_AVAILABLE:
            try:
                record_performance_metric(
                    "news_aggregation_time",
                    processing_time,
                    stack=stack,
                    source="news_intelligence",
                    metadata={
                        "articles_found": len(final_articles),
                        "query": query,
                        "time_window_hours": hours,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to record performance metric: {e}")

        return {
            "query": query,
            "detected_stack": stack,
            "results": final_articles,
            "analysis": analysis,
            "metadata": {
                "total_articles_found": len(all_articles),
                "enhanced_articles": len(enhanced_articles),
                "final_articles": len(final_articles),
                "processing_time_ms": int(processing_time),
                "time_window_hours": hours,
                "intelligence_used": True,
                "enhancement_source": "news_intelligence",
            },
        }

    def _generate_news_analysis(
        self, articles: list[dict], query: str, stack: str | None
    ) -> dict[str, Any]:
        """Generate comprehensive analysis of news articles"""
        if not articles:
            return {"summary": "No relevant news found"}

        analysis = {
            "total_articles": len(articles),
            "stack_distribution": {},
            "sentiment_summary": {"positive": 0, "negative": 0, "neutral": 0},
            "urgency_summary": {"critical": 0, "high": 0, "medium": 0, "normal": 0},
            "avg_confidence": 0.0,
            "avg_sentiment": 0.0,
            "avg_urgency": 0.0,
            "action_required_count": 0,
            "top_sources": [],
            "key_themes": [],
            "recommendations": [],
        }

        # Stack distribution
        for article in articles:
            detected_stack = article.get("detected_stack", "general")
            analysis["stack_distribution"][detected_stack] = (
                analysis["stack_distribution"].get(detected_stack, 0) + 1
            )

        # Sentiment summary
        sentiment_scores = []
        for article in articles:
            sentiment = article.get("sentiment_analysis", {}).get("overall_sentiment", "neutral")
            analysis["sentiment_summary"][sentiment] += 1

            score = article.get("sentiment_score", 0.0)
            sentiment_scores.append(score)

        # Urgency summary
        urgency_scores = []
        for article in articles:
            urgency = article.get("time_sensitivity", "normal")
            analysis["urgency_summary"][urgency] += 1

            score = article.get("urgency_score", 0.0)
            urgency_scores.append(score)

            if article.get("action_required", False):
                analysis["action_required_count"] += 1

        # Averages
        confidence_scores = [article.get("confidence_score", 0.0) for article in articles]
        analysis["avg_confidence"] = (
            sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        )
        analysis["avg_sentiment"] = (
            sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        )
        analysis["avg_urgency"] = (
            sum(urgency_scores) / len(urgency_scores) if urgency_scores else 0.0
        )

        # Top sources
        sources = [article.get("source", "unknown") for article in articles]
        source_counts = Counter(sources)
        analysis["top_sources"] = [source for source, count in source_counts.most_common(5)]

        # Key themes (extract from titles)
        all_titles = " ".join([article.get("title", "") for article in articles]).lower()
        # Simple keyword extraction (could be enhanced with NLP)
        common_words = Counter(word for word in all_titles.split() if len(word) > 4)
        analysis["key_themes"] = [word for word, count in common_words.most_common(5)]

        # Generate recommendations
        if analysis["action_required_count"] > 0:
            analysis["recommendations"].append(
                f"{analysis['action_required_count']} articles require immediate attention"
            )

        if analysis["avg_urgency"] > 0.6:
            analysis["recommendations"].append(
                "High urgency news detected - review breaking stories"
            )

        if analysis["sentiment_summary"]["negative"] > analysis["sentiment_summary"]["positive"]:
            analysis["recommendations"].append("Negative sentiment dominates - monitor for risks")
        elif analysis["sentiment_summary"]["positive"] > analysis["sentiment_summary"]["negative"]:
            analysis["recommendations"].append(
                "Positive sentiment detected - look for opportunities"
            )

        if stack and analysis["stack_distribution"].get(stack, 0) > 5:
            analysis["recommendations"].append(f"Strong {stack} news coverage - high relevance")

        return analysis


# Integration functions for EQ12 system
def search_news_for_stack(stack: str, count: int = 10, hours: int = 24) -> dict[str, Any]:
    """Convenience function for stack-specific news search"""
    intel = NewsIntelligence()

    # Generate stack-specific query
    stack_queries = {
        "betting": "sports injury news roster updates",
        "travel": "flight deals travel alerts airport news",
        "cannabis": "cannabis news marijuana legalization dispensary",
        "finance": "stock market news crypto bitcoin earnings",
        "fleet": "auto news car recall vehicle industry",
    }

    query = stack_queries.get(stack, f"{stack} news")
    return intel.aggregate_news_with_analysis(query, stack=stack, count=count, hours=hours)


def analyze_news_query(query: str, count: int = 10, hours: int = 24) -> dict[str, Any]:
    """Convenience function for query-based news analysis"""
    intel = NewsIntelligence()
    return intel.aggregate_news_with_analysis(query, count=count, hours=hours)


# CLI interface
def main():
    """CLI interface for News Intelligence module"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 News Intelligence Module")
    parser.add_argument("--query", help="Search query for news")
    parser.add_argument(
        "--stack",
        choices=["betting", "travel", "cannabis", "finance", "fleet"],
        help="Target EQ12 stack",
    )
    parser.add_argument("--count", type=int, default=10, help="Number of articles to return")
    parser.add_argument("--hours", type=int, default=24, help="Time window (hours back)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    try:
        intel = NewsIntelligence(verbose=args.verbose)

        if args.stack and not args.query:
            # Stack-specific search
            results = search_news_for_stack(args.stack, args.count, args.hours)
        else:
            # Query-based search
            query = args.query or "general news"
            results = intel.aggregate_news_with_analysis(
                query, stack=args.stack, count=args.count, hours=args.hours
            )

        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print("📰 News Intelligence Results")
            print(f"Query: {results['query']}")
            print(f"Stack: {results['detected_stack'] or 'Auto-detect'}")
            print(f"Time Window: {results['metadata']['time_window_hours']} hours")
            print(f"Articles Found: {len(results['results'])}")
            print()

            for i, article in enumerate(results["results"][:5], 1):
                emoji = article.get("telegram_emoji", "📰")
                sentiment = article.get("sentiment_analysis", {}).get(
                    "overall_sentiment", "neutral"
                )
                urgency = article.get("time_sensitivity", "normal")
                confidence = article.get("confidence_score", 0.0)

                print(f"{i}. {emoji} {article.get('title', 'No title')}")
                print(f"   Source: {article.get('source', 'Unknown')}")
                print(
                    f"   Stack: {article.get('detected_stack', 'general')} (confidence: {confidence:.2f})"
                )
                print(f"   Sentiment: {sentiment} | Urgency: {urgency}")
                if article.get("action_required"):
                    print("   🚨 ACTION REQUIRED")
                print(f"   URL: {article.get('url', '')}")
                print()

            # Show analysis
            analysis = results.get("analysis", {})
            if analysis.get("recommendations"):
                print("📊 Recommendations:")
                for rec in analysis["recommendations"]:
                    print(f"  • {rec}")

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
