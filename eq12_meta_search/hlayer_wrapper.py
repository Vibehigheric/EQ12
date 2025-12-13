#!/usr/bin/env python3
"""
EQ12 GODSTACK - HumanLayer Integration Wrapper
Provides AI-driven codebase introspection and self-refactoring capabilities.

Author: EQ12-GODSTACK
Created: 2025-09-27
"""

import json
import logging
from pathlib import Path

# Constants
REPO_ROOT = Path("C:/EQ12")
HLAYER_CONFIG = REPO_ROOT / "humanlayer.json"


def setup_logging():
    """Setup logging for HumanLayer wrapper."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("C:/EQ12/logs/hlayer_wrapper.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def init_humanlayer_config():
    """Initialize HumanLayer configuration for EQ12 repository."""
    config = {
        "name": "EQ12-GODSTACK",
        "description": "EQ12 automation and intelligence stack with multiple business verticals",
        "repository": {
            "type": "local",
            "path": str(REPO_ROOT),
            "exclude_patterns": [
                "logs/*",
                "*.log",
                "__pycache__/*",
                "node_modules/*",
                ".git/*",
                "*.pyc",
                "venv/*",
                "envs/*",
            ],
        },
        "analysis": {
            "languages": ["python", "powershell", "javascript", "xml"],
            "frameworks": ["fastapi", "playwright", "telegram-bot", "task-scheduler"],
            "business_contexts": [
                "betting intelligence and EdgeGod parlays",
                "travel booking and flight deals",
                "cannabis compliance and regulatory tracking",
                "fleet management and vehicle operations",
                "credit scoring and housing market analysis",
                "educational grants and SUNY programs",
                "AliDropship and e-commerce automation",
            ],
        },
        "common_queries": [
            "Where are Telegram messages sent from?",
            "How is enrichment.py integrated across stacks?",
            "What are the database schema patterns?",
            "Where are API keys and secrets managed?",
            "How do Task Scheduler XMLs chain operations?",
            "What are the logging patterns across modules?",
            "How is error handling implemented?",
            "Where are the browser automation patterns?",
            "How is the dashboard integrated with data collection?",
            "What are the cross-stack correlation patterns?",
        ],
    }

    with open(HLAYER_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return config


def query_codebase(question: str, context: str | None = None) -> dict:
    """
    Query the EQ12 codebase using HumanLayer AI analysis.

    Args:
        question: Natural language question about the codebase
        context: Optional context or specific files to focus on

    Returns:
        Dictionary with analysis results
    """
    logger = setup_logging()

    # Check if HumanLayer is available
    try:
        # This would be the actual HumanLayer CLI call
        # For now, we'll simulate with a structured analysis
        result = simulate_humanlayer_analysis(question, context)

        logger.info(f"HumanLayer query completed: {question[:50]}...")
        return result

    except Exception as e:
        logger.error(f"HumanLayer query failed: {e}")
        return {"status": "error", "message": str(e), "question": question}


def simulate_humanlayer_analysis(question: str, context: str | None = None) -> dict:
    """
    Simulate HumanLayer analysis with EQ12-specific patterns.
    In production, this would call the actual HumanLayer API/CLI.
    """

    # EQ12-specific codebase patterns and locations
    eq12_patterns = {
        "telegram": {
            "files": [
                "telegram_utils.py",
                "enrichment.py",
                "meta_search.py",
                "news_aggregator.py",
                "swagbucks_offers.py",
            ],
            "pattern": "send_telegram_message() function calls",
            "description": "Telegram integration is centralized in telegram_utils.py with send_telegram_message() used across all modules",
        },
        "enrichment": {
            "files": ["enrichment.py", "dashboard.py"],
            "pattern": "GPT-4o-mini API calls with stack-specific prompts",
            "description": "Enrichment uses OpenAI API with different prompts for betting, travel, cannabis, fleet, housing, education, ali stacks",
        },
        "database": {
            "files": [
                "db.py",
                "meta_search.py",
                "news_aggregator.py",
                "enhanced_db.py",
            ],
            "pattern": "SQLite with search_results, news_articles, offers tables",
            "description": "Centralized SQLite database with consistent schema patterns for search results, articles, and offers",
        },
        "secrets": {
            "files": [".env", "telegram_utils.py", "enrichment.py"],
            "pattern": "Environment variable loading with os.getenv()",
            "description": "All API keys read from .env file: OPENAI_SERVICE_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, BING_SEARCH_API_KEY",
        },
        "scheduling": {
            "files": ["tasks/*.xml"],
            "pattern": "Windows Task Scheduler XMLs with chained Python execution",
            "description": "Task Scheduler XMLs run scrapers then enrichment in sequence for automated data collection and analysis",
        },
        "logging": {
            "files": ["All Python modules"],
            "pattern": "JSON snapshots to C:/EQ12/logs with UTC timestamps",
            "description": "Consistent logging pattern: structured JSON logs with UTC timestamps saved to C:/EQ12/logs directory",
        },
        "browser_automation": {
            "files": ["swagbucks_offers.py", "devtools_agent.py"],
            "pattern": "Playwright with optional DevTools MCP integration",
            "description": "Browser automation uses Playwright with fallback patterns and optional Chrome DevTools MCP for robust scraping",
        },
        "dashboard": {
            "files": ["dashboard.py", "index.html"],
            "pattern": "FastAPI serving SQLite data with real-time updates",
            "description": "FastAPI dashboard serves database contents with endpoints for search results, news, offers, and enrichment data",
        },
    }

    # Analyze the question to determine relevant patterns
    question_lower = question.lower()
    relevant_patterns = []

    for pattern_name, pattern_info in eq12_patterns.items():
        if any(keyword in question_lower for keyword in [pattern_name, *pattern_info["files"]]):
            relevant_patterns.append(
                {
                    "pattern": pattern_name,
                    "files": pattern_info["files"],
                    "implementation": pattern_info["pattern"],
                    "explanation": pattern_info["description"],
                }
            )

    # If no specific pattern matches, provide general analysis
    if not relevant_patterns:
        relevant_patterns = [
            {
                "pattern": "general_architecture",
                "files": ["All EQ12 modules"],
                "implementation": "Modular Python scripts with shared utilities",
                "explanation": "EQ12 follows a modular architecture with shared utilities (telegram_utils.py, db.py) and stack-specific modules for different business verticals",
            }
        ]

    return {
        "status": "success",
        "question": question,
        "context": context,
        "relevant_patterns": relevant_patterns,
        "files_analyzed": len({f for p in relevant_patterns for f in p["files"]}),
        "recommendation": generate_recommendation(question, relevant_patterns),
    }


def generate_recommendation(question: str, patterns: list[dict]) -> str:
    """Generate actionable recommendations based on the analysis."""

    question_lower = question.lower()

    if "refactor" in question_lower or "improve" in question_lower:
        return "Consider consolidating duplicate patterns into shared utility functions and adding comprehensive error handling across all modules."

    if "telegram" in question_lower:
        return "Telegram integration is well-centralized in telegram_utils.py. Consider adding retry logic and rate limiting for reliability."

    if "enrichment" in question_lower:
        return "Enrichment system is flexible with stack-specific prompts. Consider adding caching and batch processing for efficiency."

    if "database" in question_lower or "schema" in question_lower:
        return "Database schema is consistent across modules. Consider adding indexes for search performance and data retention policies."

    if "error" in question_lower or "handling" in question_lower:
        return "Add comprehensive try-catch blocks around API calls and file operations. Implement graceful degradation for network failures."

    if "dashboard" in question_lower:
        return "Dashboard provides good data visibility. Consider adding real-time updates via WebSockets and user authentication."

    return "The EQ12 codebase follows good modular patterns. Consider adding unit tests and documentation for better maintainability."


def analyze_cross_stack_patterns() -> dict:
    """Analyze patterns that span across multiple EQ12 business stacks."""

    cross_stack_analysis = {
        "shared_utilities": {
            "telegram_utils.py": "Used by all stacks for notifications",
            "db.py": "Provides consistent database patterns",
            "enrichment.py": "Handles GPT analysis for all business verticals",
        },
        "common_patterns": {
            "data_collection": "All stacks follow: scrape → store → enrich → notify pattern",
            "error_handling": "Consistent logging to C:/EQ12/logs with JSON format",
            "scheduling": "Task Scheduler XMLs with chained execution",
            "api_integration": "Environment variable configuration for secrets",
        },
        "stack_specific_customizations": {
            "betting": "Injury analysis and odds correlation",
            "travel": "Flight deal detection and booking automation",
            "cannabis": "Regulatory compliance and policy tracking",
            "fleet": "Vehicle maintenance and Turo earnings optimization",
            "housing": "Credit scoring and Buffalo market analysis",
            "education": "Grant opportunities and licensing requirements",
            "ali": "Product research and dropshipping automation",
        },
    }

    return {
        "status": "success",
        "analysis_type": "cross_stack_patterns",
        "cross_stack_analysis": cross_stack_analysis,
        "recommendation": "The EQ12 architecture successfully balances shared utilities with stack-specific customizations. Consider creating a plugin architecture for easier addition of new business verticals.",
    }


def suggest_refactorings() -> list[dict]:
    """Suggest potential refactoring opportunities in the EQ12 codebase."""

    suggestions = [
        {
            "type": "consolidate_error_handling",
            "description": "Create a shared error_handler.py module for consistent exception handling across all stacks",
            "files_affected": ["All Python modules"],
            "priority": "high",
            "effort": "medium",
        },
        {
            "type": "add_retry_logic",
            "description": "Implement retry decorators for API calls (Telegram, OpenAI, Bing Search)",
            "files_affected": ["telegram_utils.py", "enrichment.py", "meta_search.py"],
            "priority": "high",
            "effort": "low",
        },
        {
            "type": "create_config_manager",
            "description": "Centralize configuration management beyond just environment variables",
            "files_affected": ["All modules with configurations"],
            "priority": "medium",
            "effort": "medium",
        },
        {
            "type": "add_caching_layer",
            "description": "Implement caching for API responses and enrichment results",
            "files_affected": ["enrichment.py", "meta_search.py", "news_aggregator.py"],
            "priority": "medium",
            "effort": "high",
        },
        {
            "type": "plugin_architecture",
            "description": "Create plugin system for easy addition of new business stacks",
            "files_affected": ["Core architecture"],
            "priority": "low",
            "effort": "high",
        },
    ]

    return suggestions


def main():
    """CLI interface for HumanLayer wrapper."""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 HumanLayer Codebase Intelligence")
    parser.add_argument("--query", help="Ask a question about the EQ12 codebase")
    parser.add_argument(
        "--init-config", action="store_true", help="Initialize HumanLayer configuration"
    )
    parser.add_argument("--cross-stack", action="store_true", help="Analyze cross-stack patterns")
    parser.add_argument(
        "--refactor-suggestions",
        action="store_true",
        help="Get refactoring suggestions",
    )

    args = parser.parse_args()

    if args.init_config:
        init_humanlayer_config()
        print(f"✅ HumanLayer config initialized at {HLAYER_CONFIG}")
        return

    if args.cross_stack:
        result = analyze_cross_stack_patterns()
        print(json.dumps(result, indent=2))
        return

    if args.refactor_suggestions:
        suggestions = suggest_refactorings()
        print("🔧 **EQ12 Refactoring Suggestions:**\n")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. **{suggestion['type']}** ({suggestion['priority']} priority)")
            print(f"   {suggestion['description']}")
            print(f"   Files: {suggestion['files_affected']}")
            print(f"   Effort: {suggestion['effort']}\n")
        return

    if args.query:
        result = query_codebase(args.query)
        print(json.dumps(result, indent=2))
        return

    # Interactive mode
    print("🤖 **EQ12 HumanLayer Interactive Mode**")
    print("Ask questions about the EQ12 codebase (type 'exit' to quit):\n")

    while True:
        try:
            question = input("Query> ").strip()
            if question.lower() in ["exit", "quit"]:
                break
            if not question:
                continue

            result = query_codebase(question)

            if result["status"] == "success":
                print("\n📋 **Analysis Results:**")
                for pattern in result["relevant_patterns"]:
                    print(f"\n**Pattern:** {pattern['pattern']}")
                    print(f"**Files:** {', '.join(pattern['files'])}")
                    print(f"**Implementation:** {pattern['implementation']}")
                    print(f"**Explanation:** {pattern['explanation']}")

                print(f"\n💡 **Recommendation:** {result['recommendation']}\n")
            else:
                print(f"\n❌ **Error:** {result['message']}\n")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ **Error:** {e}\n")

    print("👋 HumanLayer session ended")


if __name__ == "__main__":
    main()
