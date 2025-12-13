#!/usr/bin/env python3
"""
EQ12 GODSTACK Enrichment Engine
GPT-powered result analysis, ranking, and summarization with stack-specific intelligence.

Author: EQ12 AI Assistant
Created: 2025-01-27
"""

import logging
import os
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

# Add paths for EQ12 integration
BASE_DIR = Path(__file__).resolve().parent
EQ12_BASE = Path(r"C:\EQ12")
sys.path.insert(0, str(EQ12_BASE))

# Import EQ12 components
try:
    from alert_pipe import send_telegram_text

    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

# Import OpenAI for enrichment
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    print("Warning: OpenAI not available. Install with: pip install openai")
    OPENAI_AVAILABLE = False

logger = logging.getLogger("enrichment")


class EQ12EnrichmentEngine:
    """GPT-powered enrichment engine for EQ12 GODSTACK results"""

    # Stack-specific enrichment prompts
    STACK_PROMPTS = {
        "betting": {
            "system": "You are an expert sports betting analyst. Focus on injury reports, line movements, roster changes, and actionable betting intelligence.",
            "analysis_focus": [
                "Injury severity and timeline impact on team performance",
                "Roster changes affecting key player availability",
                "Line movement opportunities and market inefficiencies",
                "Weather conditions impacting game totals",
                "Historical matchup trends and situational advantages",
            ],
        },
        "travel": {
            "system": "You are a travel deals and logistics expert. Focus on flight deals, destination alerts, and travel optimization opportunities.",
            "analysis_focus": [
                "Flight deal value analysis and booking windows",
                "Destination safety and accessibility updates",
                "Seasonal pricing trends and optimization timing",
                "Airport delays and alternative routing options",
                "Cashback and rewards optimization strategies",
            ],
        },
        "cannabis": {
            "system": "You are a cannabis industry analyst. Focus on regulatory changes, market opportunities, and compliance updates.",
            "analysis_focus": [
                "Regulatory changes affecting market access",
                "New dispensary openings and market expansion",
                "Product availability and pricing trends",
                "Legal compliance and licensing updates",
                "Investment opportunities and market consolidation",
            ],
        },
        "finance": {
            "system": "You are a financial markets analyst. Focus on market movements, investment opportunities, and economic indicators.",
            "analysis_focus": [
                "Earnings surprises and market reaction opportunities",
                "Economic indicators affecting sector performance",
                "Cryptocurrency trends and adoption developments",
                "Interest rate impacts on various asset classes",
                "Merger and acquisition activity and arbitrage opportunities",
            ],
        },
        "fleet": {
            "system": "You are an automotive industry analyst. Focus on vehicle deals, recalls, insurance impacts, and fleet management opportunities.",
            "analysis_focus": [
                "Vehicle recall impacts on safety and resale value",
                "Insurance rate changes and coverage optimization",
                "Fleet management cost reduction opportunities",
                "Electric vehicle adoption and infrastructure development",
                "Automotive financing deals and incentive programs",
            ],
        },
        "general": {
            "system": "You are a comprehensive business intelligence analyst. Focus on actionable insights and opportunity identification.",
            "analysis_focus": [
                "Market trends affecting business opportunities",
                "Competitive intelligence and positioning advantages",
                "Operational efficiency improvement opportunities",
                "Revenue optimization and cost reduction strategies",
                "Risk mitigation and compliance considerations",
            ],
        },
    }

    def __init__(self, db_path: str = "meta_search.sqlite3", verbose: bool = False):
        """Initialize enrichment engine"""
        self.db_path = db_path
        self.verbose = verbose
        self.setup_logging()

        if not OPENAI_AVAILABLE:
            raise ValueError("OpenAI library not available - run: pip install openai")

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_SERVICE_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required - set OPENAI_SERVICE_KEY or OPENAI_API_KEY")

        self.client = OpenAI(api_key=api_key)

    def setup_logging(self):
        """Setup logging"""
        log_level = logging.INFO if self.verbose else logging.WARNING
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def fetch_recent_results(self, hours: int = 24, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch recent search results from godstack2 database"""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)

        results = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Fetch search results
                cursor.execute(
                    """SELECT query, title, url, snippet, source, published_at, fetched_at
                    FROM results WHERE fetched_at >= ?
                    ORDER BY fetched_at DESC LIMIT ?""",
                    (cutoff_time.isoformat(), limit),
                )

                columns = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    result = dict(zip(columns, row, strict=False))
                    result["content_type"] = "search_result"
                    results.append(result)

        except sqlite3.Error as e:
            logger.error(f"Database error fetching results: {e}")

        return results

    def fetch_recent_offers(self, hours: int = 24, limit: int = 30) -> list[dict[str, Any]]:
        """Fetch recent Swagbucks offers from godstack2 database"""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)

        offers = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if offers table exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='offers'"
                )
                if not cursor.fetchone():
                    logger.warning("Offers table not found in database")
                    return offers

                # Fetch offers
                cursor.execute(
                    """SELECT title, url, reward, category, source, fetched_at
                    FROM offers WHERE fetched_at >= ?
                    ORDER BY fetched_at DESC LIMIT ?""",
                    (cutoff_time.isoformat(), limit),
                )

                columns = [desc[0] for desc in cursor.description]
                for row in cursor.fetchall():
                    offer = dict(zip(columns, row, strict=False))
                    offer["content_type"] = "offer"
                    offers.append(offer)

        except sqlite3.Error as e:
            logger.error(f"Database error fetching offers: {e}")

        return offers

    def detect_content_stack(self, items: list[dict[str, Any]]) -> dict[str, float]:
        """Detect which EQ12 stack the content relates to"""
        stack_keywords = {
            "betting": [
                "injury",
                "roster",
                "odds",
                "betting",
                "sports",
                "nfl",
                "nba",
                "mlb",
                "nhl",
                "prediction",
            ],
            "travel": [
                "flight",
                "hotel",
                "travel",
                "airport",
                "vacation",
                "booking",
                "deal",
                "airline",
            ],
            "cannabis": [
                "cannabis",
                "marijuana",
                "dispensary",
                "cbd",
                "thc",
                "weed",
                "strain",
                "legal",
            ],
            "finance": [
                "stock",
                "crypto",
                "bitcoin",
                "investment",
                "market",
                "trading",
                "earnings",
                "finance",
            ],
            "fleet": [
                "car",
                "vehicle",
                "auto",
                "truck",
                "insurance",
                "recall",
                "fleet",
                "automotive",
            ],
        }

        stack_scores = dict.fromkeys(stack_keywords.keys(), 0)

        for item in items:
            text = f"{item.get('title', '')} {item.get('snippet', '')} {item.get('category', '')}".lower()

            for stack, keywords in stack_keywords.items():
                score = sum(1 for keyword in keywords if keyword in text)
                stack_scores[stack] += score

        # Normalize scores
        total_score = sum(stack_scores.values())
        if total_score > 0:
            stack_scores = {stack: score / total_score for stack, score in stack_scores.items()}

        return stack_scores

    def enrich_with_gpt(
        self, items: list[dict[str, Any]], stack: str = "general"
    ) -> dict[str, Any]:
        """Use GPT to analyze and enrich content"""
        if not items:
            return {
                "summary": "No content to analyze",
                "action_items": [],
                "stack_analysis": {},
            }

        # Get stack-specific prompt
        prompt_config = self.STACK_PROMPTS.get(stack, self.STACK_PROMPTS["general"])

        # Prepare content for GPT analysis
        content_text = ""
        for i, item in enumerate(items[:20], 1):  # Limit to 20 items for token efficiency
            title = item.get("title", "Untitled")
            snippet = item.get("snippet", "")
            source = item.get("source", "Unknown")
            content_type = item.get("content_type", "result")

            content_text += f"{i}. [{content_type.upper()}] {title}\n"
            if snippet:
                content_text += f"   Summary: {snippet}\n"
            content_text += f"   Source: {source}\n\n"

        # Create enrichment prompt
        user_prompt = f"""
Analyze the following {stack} content and provide:

1. **EXECUTIVE SUMMARY** (2-3 sentences)
2. **TOP 5 ACTION ITEMS** (specific, actionable recommendations)
3. **RISK ASSESSMENT** (potential risks and mitigation strategies)
4. **OPPORTUNITY ANALYSIS** (immediate and strategic opportunities)
5. **PRIORITY RANKING** (rank items by urgency and impact)

Focus Areas for {stack.title()}:
{chr(10).join(f"• {focus}" for focus in prompt_config["analysis_focus"])}

Content to Analyze:
{content_text}

Provide clear, actionable intelligence suitable for immediate business decisions.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-efficient model
                messages=[
                    {"role": "system", "content": prompt_config["system"]},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=800,
                temperature=0.3,
            )

            analysis = response.choices[0].message.content

            # Parse structured response if possible
            sections = self._parse_gpt_response(analysis)

            return {
                "summary": sections.get("executive_summary", analysis[:200] + "..."),
                "action_items": sections.get("action_items", []),
                "risk_assessment": sections.get("risk_assessment", ""),
                "opportunities": sections.get("opportunity_analysis", ""),
                "priority_ranking": sections.get("priority_ranking", ""),
                "full_analysis": analysis,
                "model_used": "gpt-4o-mini",
                "tokens_used": response.usage.total_tokens,
                "cost_estimate": round(
                    response.usage.total_tokens * 0.00015 / 1000, 4
                ),  # Rough cost estimate
            }

        except Exception as e:
            logger.error(f"GPT enrichment failed: {e}")
            return {
                "summary": f"Analysis failed: {e!s}",
                "action_items": [],
                "error": str(e),
            }

    def _parse_gpt_response(self, analysis: str) -> dict[str, Any]:
        """Parse structured GPT response into sections"""
        sections = {}

        # Simple parsing for common headers
        current_section = None
        current_content = []

        for line in analysis.split("\n"):
            line = line.strip()

            # Check for section headers
            if any(header in line.lower() for header in ["executive summary", "summary"]):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "executive_summary"
                current_content = []
            elif "action item" in line.lower():
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "action_items"
                current_content = []
            elif "risk" in line.lower() and "assessment" in line.lower():
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "risk_assessment"
                current_content = []
            elif "opportunit" in line.lower():
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "opportunity_analysis"
                current_content = []
            elif "priority" in line.lower() or "ranking" in line.lower():
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "priority_ranking"
                current_content = []
            else:
                if current_section:
                    current_content.append(line)

        # Add final section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()

        # Extract action items as list if possible
        if "action_items" in sections:
            action_text = sections["action_items"]
            # Simple bullet point extraction
            actions = [
                line.strip().lstrip("•-*123456789. ")
                for line in action_text.split("\n")
                if line.strip() and any(c in line for c in "•-*123456789")
            ]
            sections["action_items"] = actions if actions else [action_text]

        return sections

    def generate_comprehensive_analysis(
        self, stack: str = "general", hours: int = 24
    ) -> dict[str, Any]:
        """Generate comprehensive analysis of recent content"""
        start_time = datetime.now()

        # Fetch recent data
        results = self.fetch_recent_results(hours=hours)
        offers = self.fetch_recent_offers(hours=hours)
        all_items = results + offers

        if not all_items:
            return {
                "status": "no_content",
                "message": f"No content found in the last {hours} hours",
                "timestamp": start_time.isoformat(),
            }

        # Auto-detect stack if not specified
        if stack == "auto":
            stack_scores = self.detect_content_stack(all_items)
            detected_stack = max(stack_scores.keys(), key=lambda k: stack_scores[k])
            if stack_scores[detected_stack] > 0.3:  # Confidence threshold
                stack = detected_stack
            else:
                stack = "general"

        logger.info(f"Analyzing {len(all_items)} items for {stack} stack")

        # GPT enrichment
        enrichment = self.enrich_with_gpt(all_items, stack)

        # Generate analysis metadata
        processing_time = (datetime.now() - start_time).total_seconds()

        analysis_result = {
            "stack": stack,
            "content_summary": {
                "total_items": len(all_items),
                "search_results": len(results),
                "offers": len(offers),
                "time_window_hours": hours,
                "sources": list({item.get("source", "Unknown") for item in all_items}),
            },
            "enrichment": enrichment,
            "metadata": {
                "analysis_timestamp": start_time.isoformat(),
                "processing_time_seconds": round(processing_time, 2),
                "model_cost_estimate": enrichment.get("cost_estimate", 0),
            },
        }

        return analysis_result

    def send_enriched_alert(
        self, analysis: dict[str, Any], include_raw: bool = False
    ) -> str | None:
        """Send enriched analysis via Telegram"""
        if not TELEGRAM_AVAILABLE:
            return "Telegram not available"

        stack = analysis.get("stack", "general")
        enrichment = analysis.get("enrichment", {})
        content_summary = analysis.get("content_summary", {})

        # Build Telegram message
        message_parts = []

        # Header with emoji
        stack_emojis = {
            "betting": "🏈",
            "travel": "✈️",
            "cannabis": "🌿",
            "finance": "📈",
            "fleet": "🚗",
            "general": "📊",
        }
        emoji = stack_emojis.get(stack, "📊")

        message_parts.append(f"{emoji} *EQ12 {stack.upper()} INTELLIGENCE*")
        message_parts.append(f"_{content_summary['total_items']} items analyzed_")
        message_parts.append("")

        # Executive summary
        if enrichment.get("summary"):
            message_parts.append("*📋 EXECUTIVE SUMMARY*")
            message_parts.append(enrichment["summary"])
            message_parts.append("")

        # Action items
        if enrichment.get("action_items"):
            message_parts.append("*🎯 ACTION ITEMS*")
            for i, action in enumerate(enrichment["action_items"][:5], 1):
                message_parts.append(f"{i}. {action}")
            message_parts.append("")

        # Risk assessment
        if enrichment.get("risk_assessment"):
            message_parts.append("*⚠️ RISK ASSESSMENT*")
            message_parts.append(enrichment["risk_assessment"])
            message_parts.append("")

        # Opportunities
        if enrichment.get("opportunities"):
            message_parts.append("*💡 OPPORTUNITIES*")
            message_parts.append(enrichment["opportunities"])
            message_parts.append("")

        # Processing metadata
        metadata = analysis.get("metadata", {})
        processing_time = metadata.get("processing_time_seconds", 0)
        cost = metadata.get("model_cost_estimate", 0)

        message_parts.append(f"_Analysis: {processing_time}s | Cost: ${cost}_")

        # Send message
        message_text = "\n".join(message_parts)

        # Truncate if too long (Telegram limit ~4096 chars)
        if len(message_text) > 4000:
            message_text = message_text[:3900] + "\n\n_[Message truncated]_"

        return send_telegram_text(message_text)


# CLI and integration functions
def enrich_and_alert(stack: str = "general", hours: int = 24, telegram: bool = True) -> None:
    """Main enrichment and alerting function"""
    try:
        engine = EQ12EnrichmentEngine(verbose=True)

        # Generate analysis
        analysis = engine.generate_comprehensive_analysis(stack=stack, hours=hours)

        if analysis.get("status") == "no_content":
            print(f"No content found for {stack} stack in the last {hours} hours")
            return

        # Print analysis
        print("=" * 60)
        print(f"EQ12 {stack.upper()} INTELLIGENCE ANALYSIS")
        print("=" * 60)

        enrichment = analysis.get("enrichment", {})
        if enrichment.get("summary"):
            print("\n📋 EXECUTIVE SUMMARY:")
            print(enrichment["summary"])

        if enrichment.get("action_items"):
            print("\n🎯 ACTION ITEMS:")
            for i, action in enumerate(enrichment["action_items"], 1):
                print(f"  {i}. {action}")

        if enrichment.get("risk_assessment"):
            print("\n⚠️ RISK ASSESSMENT:")
            print(enrichment["risk_assessment"])

        if enrichment.get("opportunities"):
            print("\n💡 OPPORTUNITIES:")
            print(enrichment["opportunities"])

        # Send to Telegram if requested
        if telegram:
            error = engine.send_enriched_alert(analysis)
            if error:
                print(f"\n⚠️ Telegram send failed: {error}")
            else:
                print("\n✅ Enriched alert sent to Telegram")

        # Print metadata
        metadata = analysis.get("metadata", {})
        print("\n📊 METADATA:")
        print(f"  Processing Time: {metadata.get('processing_time_seconds', 0)}s")
        print(f"  Model Cost: ${metadata.get('model_cost_estimate', 0)}")
        print(f"  Items Analyzed: {analysis['content_summary']['total_items']}")

    except Exception as e:
        print(f"❌ Enrichment failed: {e}")
        if telegram and TELEGRAM_AVAILABLE:
            send_telegram_text(f"🚨 *EQ12 Enrichment Error*\n\n{e!s}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 GODSTACK Enrichment Engine")
    parser.add_argument(
        "--stack",
        default="general",
        choices=[
            "betting",
            "travel",
            "cannabis",
            "finance",
            "fleet",
            "general",
            "auto",
        ],
        help="Target stack for analysis",
    )
    parser.add_argument("--hours", type=int, default=24, help="Hours of data to analyze")
    parser.add_argument("--telegram", action="store_true", help="Send results to Telegram")
    parser.add_argument("--no-telegram", action="store_true", help="Skip Telegram sending")
    parser.add_argument("--db-path", default="meta_search.sqlite3", help="Database path")

    args = parser.parse_args()

    # Override telegram setting
    send_telegram = args.telegram and not args.no_telegram

    # Set database path if provided
    if hasattr(EQ12EnrichmentEngine, "__init__"):
        original_init = EQ12EnrichmentEngine.__init__

        def new_init(self, db_path=args.db_path, verbose=True):
            return original_init(self, db_path=db_path, verbose=verbose)

        EQ12EnrichmentEngine.__init__ = new_init

    # Run enrichment
    enrich_and_alert(stack=args.stack, hours=args.hours, telegram=send_telegram)


if __name__ == "__main__":
    main()
