#!/usr/bin/env python3
"""
EQ12 Forum Intelligence System
Safely monitors GitHub Community for OpenAI API updates and betting automation insights.

Usage:
    python eq12_forum_learner.py --report
    python eq12_forum_learner.py --update-issues
"""

import argparse
import json
import logging
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/forum_learner.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class ForumSignal:
    """Represents an actionable signal from forum content"""

    tag: str
    description: str
    confidence: float
    source_title: str
    source_url: str
    timestamp: str


class EQ12ForumLearner:
    """Safe GitHub Community intelligence gatherer"""

    def __init__(self):
        self.base_url = "https://github.community"
        self.headers = {
            "User-Agent": "EQ12-Learner/1.0 (+https://github.com/yourusername/EQ12)",
            "Accept": "application/json",
            "Cache-Control": "no-cache",
        }
        self.cache_dir = Path("C:/EQ12/data/forum_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "topics.jsonl"

        # Intelligence extraction rules for EQ12-relevant content
        self.extraction_rules = [
            # OpenAI API Evolution
            (
                r"\bResponses API\b|\bclient\.responses\.create\(",
                "MIGRATE_RESPONSES",
                "Adopt Responses API over Chat Completions",
                0.95,
            ),
            (
                r"\bgpt-4o\b|\bgpt-4o-mini\b|\bo1-preview\b",
                "MODEL_UPDATES",
                "Update model preferences and cost calculations",
                0.90,
            ),
            (
                r"\bstructured outputs\b|\bresponse_format.*json_schema",
                "STRUCTURED_OUTPUT",
                "Implement structured response parsing",
                0.85,
            ),
            # Rate Limiting & Cost Control
            (
                r"\brate limit|\bTPM\b|\bRPM\b|\bquota exceeded\b",
                "RATE_LIMITING",
                "Improve rate-limit guards & backoff strategies",
                0.92,
            ),
            (
                r"\bcost optimization\b|\bbatch api\b|\btoken usage\b",
                "COST_OPTIMIZATION",
                "Optimize token usage and API costs",
                0.88,
            ),
            (
                r"\bbudget\b.*\blimit\b|\bspend management\b",
                "BUDGET_GUARDS",
                "Enhance budget monitoring systems",
                0.85,
            ),
            # Webhook & Automation
            (
                r"\bwebhook\b|\bevent handler\b|\bcallback url\b",
                "WEBHOOKS",
                "Add OpenAI webhook endpoints for real-time events",
                0.80,
            ),
            (
                r"\bautomatic retry\b|\bexponential backoff\b",
                "RETRY_LOGIC",
                "Improve retry and error handling",
                0.75,
            ),
            # Azure & Enterprise
            (
                r"\bAzure OpenAI\b|\bmanaged identity\b|\bkey vault\b",
                "AZURE_ENTERPRISE",
                "Azure OpenAI enterprise best practices",
                0.85,
            ),
            (
                r"\bembeddings\b|\btext-embedding-3-\w+\b",
                "EMBED_PIPELINE",
                "Refresh embedding stack and vector operations",
                0.70,
            ),
            # Sports Betting & EQ12 Specific
            (
                r"\bsports.*api\b|\bodds.*api\b|\bbetting.*data\b",
                "SPORTS_DATA",
                "Sports betting API integration patterns",
                0.90,
            ),
            (
                r"\breal.*time\b.*\bdata\b|\blive.*updates\b",
                "LIVE_DATA",
                "Real-time data processing for live betting",
                0.85,
            ),
            (
                r"\brisk management\b|\bbankroll\b|\bkelly criterion\b",
                "RISK_MGMT",
                "Risk management and bankroll strategies",
                0.88,
            ),
        ]

        # Rate limiting: be respectful
        self.request_delay = 2.0  # 2 seconds between requests
        self.last_request = 0

    def _rate_limit(self):
        """Enforce polite rate limiting"""
        elapsed = time.time() - self.last_request
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        self.last_request = time.time()

    def _safe_request(self, url: str, timeout: int = 15) -> dict[str, Any] | None:
        """Make a safe, rate-limited request"""
        try:
            self._rate_limit()
            logger.info(f"Fetching: {url}")

            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.raise_for_status()

            # Check content type
            if "application/json" not in response.headers.get("content-type", ""):
                logger.warning(f"Non-JSON response from {url}")
                return None

            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {url}: {e}")
            return None

    def fetch_latest_topics(self, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch latest topics from GitHub Community (public endpoints only)"""
        topics = []

        # Try Discourse-style endpoints (common for GitHub Community)
        endpoints_to_try = [
            f"{self.base_url}/latest.json",
            f"{self.base_url}/top.json",
            f"{self.base_url}/c/api/5/l/latest.json",  # API category
            f"{self.base_url}/c/code-to-cloud/6/l/latest.json",  # Code category
        ]

        for url in endpoints_to_try:
            data = self._safe_request(url)
            if data and "topic_list" in data:
                topic_list = data["topic_list"].get("topics", [])
                for topic in topic_list[:limit]:
                    # Enrich with metadata
                    topic["_fetched_at"] = datetime.now(UTC).isoformat()
                    topic["_source_endpoint"] = url
                    topics.append(topic)

                    # Cache for later analysis
                    with self.cache_file.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(topic, ensure_ascii=False) + "\n")

                logger.info(f"Fetched {len(topic_list)} topics from {url}")
                break  # Success, no need to try other endpoints

        if not topics:
            logger.warning("No topics fetched from any endpoint")

        return topics[:limit]

    def extract_signals(
        self, text: str, source_title: str = "", source_url: str = ""
    ) -> list[ForumSignal]:
        """Extract actionable signals from forum content"""
        signals = []
        text.lower()

        for pattern, tag, description, confidence in self.extraction_rules:
            if re.search(pattern, text, flags=re.IGNORECASE):
                signal = ForumSignal(
                    tag=tag,
                    description=description,
                    confidence=confidence,
                    source_title=source_title[:200],  # Truncate for readability
                    source_url=source_url,
                    timestamp=datetime.now(UTC).isoformat(),
                )
                signals.append(signal)

        return signals

    def analyze_topics(self, topics: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze topics and extract actionable intelligence"""
        all_signals = []
        signal_summary = {}

        for topic in topics:
            title = topic.get("title", "")
            excerpt = topic.get("excerpt", "")
            slug = topic.get("slug", "")

            # Combine text for analysis
            combined_text = f"{title} {excerpt}"
            topic_url = f"{self.base_url}/t/{slug}/{topic.get('id', '')}"

            # Extract signals
            signals = self.extract_signals(combined_text, title, topic_url)
            all_signals.extend(signals)

            # Build summary
            for signal in signals:
                if signal.tag not in signal_summary:
                    signal_summary[signal.tag] = {
                        "description": signal.description,
                        "count": 0,
                        "avg_confidence": 0.0,
                        "examples": [],
                        "urls": [],
                    }

                bucket = signal_summary[signal.tag]
                bucket["count"] += 1
                bucket["avg_confidence"] = (
                    bucket["avg_confidence"] * (bucket["count"] - 1) + signal.confidence
                ) / bucket["count"]

                if len(bucket["examples"]) < 5:
                    bucket["examples"].append(signal.source_title[:140])
                    bucket["urls"].append(signal.source_url)

        # Sort by priority (count * avg_confidence)
        sorted_signals = sorted(
            signal_summary.items(),
            key=lambda x: x[1]["count"] * x[1]["avg_confidence"],
            reverse=True,
        )

        result = {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_topics_analyzed": len(topics),
            "total_signals_found": len(all_signals),
            "signal_summary": dict(sorted_signals),
            "raw_signals": [
                {
                    "tag": s.tag,
                    "description": s.description,
                    "confidence": s.confidence,
                    "source_title": s.source_title,
                    "source_url": s.source_url,
                    "timestamp": s.timestamp,
                }
                for s in all_signals
            ],
        }

        return result

    def generate_report(self) -> str:
        """Generate a comprehensive intelligence report"""
        logger.info("Starting forum intelligence gathering...")

        topics = self.fetch_latest_topics(limit=40)
        if not topics:
            return "⚠️ No topics retrieved. Check network connection and endpoints."

        analysis = self.analyze_topics(topics)

        # Generate markdown report
        report = []
        report.append("# 🤖 EQ12 Forum Intelligence Report")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append(f"**Topics Analyzed:** {analysis['total_topics_analyzed']}")
        report.append(f"**Signals Found:** {analysis['total_signals_found']}")
        report.append("")

        if analysis["signal_summary"]:
            report.append("## 🎯 Priority Actions")
            for tag, data in list(analysis["signal_summary"].items())[:8]:  # Top 8
                priority_score = data["count"] * data["avg_confidence"]
                report.append(f"### {tag} (Priority: {priority_score:.1f})")
                report.append(f"**Action:** {data['description']}")
                report.append(
                    f"**Confidence:** {data['avg_confidence']:.1f}% | **Mentions:** {data['count']}"
                )

                if data["examples"]:
                    report.append("**Examples:**")
                    for i, example in enumerate(data["examples"][:3]):
                        url = data["urls"][i] if i < len(data["urls"]) else ""
                        if url:
                            report.append(f"- [{example}]({url})")
                        else:
                            report.append(f"- {example}")
                report.append("")
        else:
            report.append("## ℹ️ No High-Priority Signals")
            report.append("Forum content doesn't show immediate actionable items for EQ12.")
            report.append("")

        report.append("---")
        report.append("*Generated by EQ12 Forum Learner - Respecting ToS & Rate Limits*")

        # Save report
        report_text = "\n".join(report)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.cache_dir / f"intelligence_report_{timestamp}.md"

        with report_file.open("w", encoding="utf-8") as f:
            f.write(report_text)

        logger.info(f"Report saved to {report_file}")
        return report_text


def main():
    parser = argparse.ArgumentParser(description="EQ12 Forum Intelligence System")
    parser.add_argument("--report", action="store_true", help="Generate intelligence report")
    parser.add_argument(
        "--update-issues", action="store_true", help="Create GitHub issues from signals"
    )

    args = parser.parse_args()

    learner = EQ12ForumLearner()

    if args.report or not any([args.report, args.update_issues]):
        print(learner.generate_report())

    if args.update_issues:
        # This will be implemented in eq12_forum_actions.py
        print("Issue creation functionality moved to eq12_forum_actions.py")


if __name__ == "__main__":
    main()
