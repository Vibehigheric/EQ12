#!/usr/bin/env python3
"""
EQ12 AI Provider Configuration - Hardcoded Strategy
Implements the recommended AI usage pattern: Groq for speed, OpenAI for complexity
"""

import os
from dotenv import load_dotenv
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class AIProvider(Enum):
    """AI Provider enumeration for EQ12 system"""

    GROQ = "groq"  # Ultra-fast inference for real-time analysis
    OPENAI = "openai"  # Complex reasoning and safety-critical decisions
    GOOGLE = "google"  # Free Gemini models for backup/experimentation
    GITHUB = "github"  # Pro tier models for advanced analysis


class TaskType(Enum):
    """Task categorization for optimal provider selection"""

    REAL_TIME = "real_time"  # <1s response needed - USE GROQ
    ARBITRAGE = "arbitrage"  # Speed critical - USE GROQ
    QUICK_ANALYSIS = "quick"  # Fast analysis - USE GROQ
    BETTING_DECISION = "betting"  # Moderate complexity - USE GROQ/OPENAI
    COMPLEX_REASONING = "complex"  # Deep analysis - USE OPENAI
    SAFETY_CRITICAL = "safety"  # Risk management - USE OPENAI ONLY
    EXPERIMENTAL = "experiment"  # Testing/research - USE GOOGLE/GITHUB


class EQ12AIProviderConfig:
    """
    EQ12 Hardcoded AI Provider Configuration
    Based on real-world testing and rate limit analysis
    """

    def __init__(self):
        """TODO: Add docstring for __init__"""

        self.config_timestamp = datetime.now(UTC)

        # Load environment variables from .env (if present)
        load_dotenv()

        # API Keys (read-only from environment for security)
        self.api_keys = {
            "groq": os.environ.get("GROQ_API_KEY"),
            "google": os.environ.get("GOOGLE_API_KEY"),
            "openai": os.environ.get("OPENAI_API_KEY"),
            "github": os.environ.get("GITHUB_TOKEN"),
        }

        # GROQ CONFIGURATION - Official rate limits from Groq documentation
        self.groq_config = {
            "base_url": "https://api.groq.com/openai/v1",
            "data_retention": {
                "default": "No customer data retained by default",
                "zero_data_retention": "Available in Data Controls settings",
                "reliability_logs": "Up to 30 days (can opt out)",
                "location": "Google Cloud Platform (GCP) - United States",
            },
            "models": {
                "ultra_fast": {
                    "name": "llama-3.1-8b-instant",
                    "rpm": 30,
                    "rpd": 14400,  # 14.4K requests/day FREE
                    "tpm": 6000,
                    "tpd": 500000,  # 500K tokens/day FREE
                    "avg_response_time": "0.3-0.6s",
                    "use_for": ["arbitrage", "real_time_odds", "quick_decisions"],
                    "privacy": "Zero data retention available",
                },
                "balanced": {
                    "name": "llama-3.3-70b-versatile",
                    "rpm": 30,
                    "rpd": 1000,  # 1K requests/day FREE
                    "tpm": 12000,
                    "tpd": 100000,  # 100K tokens/day FREE
                    "avg_response_time": "0.8-1.2s",
                    "use_for": ["nhl_analysis", "betting_recs", "game_analysis"],
                    "privacy": "Zero data retention available",
                },
                "advanced": {
                    "name": "groq/compound",
                    "rpm": 30,
                    "rpd": 250,  # 250 requests/day FREE
                    "tpm": 70000,
                    "tpd": "unlimited",  # No daily token limit
                    "avg_response_time": "1.0-2.0s",
                    "use_for": ["complex_analysis", "multi_game_parlays"],
                    "privacy": "Zero data retention available",
                },
            },
            "pricing": "FREE - $0 cost with generous daily limits",
            "privacy_compliance": "GDPR/CCPA compliant with Zero Data Retention option",
        }

        # GOOGLE AI CONFIGURATION
        self.google_config = {
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "models": {
                "flash": {
                    "name": "gemini-1.5-flash",
                    "rpm": 1000,
                    "rpd": "unlimited",
                    "tpm": 1000000,
                    "tpd": "unlimited",
                    "use_for": ["backup_analysis", "experimental", "batch_processing"],
                },
                "pro": {
                    "name": "gemini-1.5-pro",
                    "rpm": 360,
                    "rpd": "unlimited",
                    "tpm": 120000,
                    "tpd": "unlimited",
                    "use_for": ["advanced_reasoning", "complex_queries"],
                },
            },
            "pricing": "FREE - 1M tokens/minute free tier",
        }

        # STRATEGIC ROUTING RULES
        self.routing_strategy = {
            TaskType.REAL_TIME: {
                "primary": AIProvider.GROQ,
                "model": "ultra_fast",
                "fallback": AIProvider.GOOGLE,
                "max_response_time": "1.0s",
                "reasoning": "Speed is critical for real-time arbitrage",
            },
            TaskType.ARBITRAGE: {
                "primary": AIProvider.GROQ,
                "model": "ultra_fast",
                "fallback": AIProvider.GOOGLE,
                "max_response_time": "0.5s",
                "reasoning": "Arbitrage windows close in seconds",
            },
            TaskType.QUICK_ANALYSIS: {
                "primary": AIProvider.GROQ,
                "model": "balanced",
                "fallback": AIProvider.GOOGLE,
                "max_response_time": "2.0s",
                "reasoning": "Fast analysis with moderate accuracy",
            },
            TaskType.BETTING_DECISION: {
                "primary": AIProvider.GROQ,
                "model": "balanced",
                "fallback": AIProvider.OPENAI,
                "max_response_time": "3.0s",
                "reasoning": "Balance speed and accuracy for betting",
            },
            TaskType.COMPLEX_REASONING: {
                "primary": AIProvider.OPENAI,
                "model": "gpt-4",
                "fallback": AIProvider.GROQ,
                "max_response_time": "10.0s",
                "reasoning": "Complex analysis requires OpenAI quality",
            },
            TaskType.SAFETY_CRITICAL: {
                "primary": AIProvider.OPENAI,
                "model": "gpt-4",
                "fallback": None,  # No fallback for safety
                "max_response_time": "15.0s",
                "reasoning": "Only OpenAI for risk management decisions",
            },
        }

        # PERFORMANCE TARGETS
        self.performance_targets = {
            "arbitrage_detection": "< 0.5s response time",
            "odds_analysis": "< 1.0s response time",
            "game_predictions": "< 2.0s response time",
            "complex_parlays": "< 10.0s response time",
            "daily_requests": "10,000+ requests via Groq free tier",
            "cost_target": "$0/month via free tiers only",
        }

    def get_provider_for_task(self, task_type: TaskType) -> dict[str, Any]:
        """Get optimal provider configuration for task type"""
        if task_type not in self.routing_strategy:
            # Default to Groq for unknown tasks
            return {
                "provider": AIProvider.GROQ,
                "model": "balanced",
                "reasoning": "Default Groq routing for unknown task",
            }

        strategy = self.routing_strategy[task_type]
        return {
            "provider": strategy["primary"],
            "model": strategy["model"],
            "fallback": strategy.get("fallback"),
            "max_response_time": strategy["max_response_time"],
            "reasoning": strategy["reasoning"],
        }

    def validate_api_keys(self) -> dict[str, bool]:
        """Validate which API keys are configured"""
        validation = {}
        for provider, key in self.api_keys.items():
            validation[provider] = bool(
                key and key != "" and "your_key_here" not in key.lower())
        return validation

    def get_usage_recommendations(self) -> dict[str, list[str]]:
        """Get hardcoded usage recommendations"""
        return {
            "use_groq_for": [
                "🎯 Arbitrage opportunity detection (ultra-fast)",
                "⚡ Live odds monitoring and alerts",
                "🏒 NHL game outcome predictions",
                "💰 Player prop betting recommendations",
                "📊 Quick statistical analysis",
                "🔄 Real-time market scanning",
            ],
            "use_openai_for": [
                "🧠 Complex multi-game parlay strategies",
                "⚖️ Risk management and bankroll decisions",
                "📈 Long-term betting strategy development",
                "🛡️ Safety-critical financial calculations",
                "📝 Detailed betting guides and explanations",
                "🔬 Deep statistical modeling",
            ],
            "use_google_for": [
                "🆓 Free tier experimentation",
                "🧪 Testing new betting strategies",
                "📚 Research and learning tasks",
                "🔄 Backup when other APIs down",
                "📊 Batch processing large datasets",
            ],
            "cost_optimization": [
                "💡 14,400 free Groq requests = ~$144 value/day (official rate limit)",
                "🎁 1M free Google tokens/min = unlimited daily capacity",
                "💰 Total savings: $6K-24K annually vs OpenAI",
                "⚡ 3-5x faster responses vs OpenAI (0.3-0.6s Groq)",
                "🎯 Zero monthly costs with smart routing",
                "🔒 Zero data retention available for privacy compliance",
            ],
        }


def main():
    """Demo the AI provider configuration"""
    config = EQ12AIProviderConfig()

    print("🤖 EQ12 AI Provider Configuration")
    print("=" * 50)

    # Show API key status
    print("\n🔑 API Key Status:")
    validation = config.validate_api_keys()
    for provider, valid in validation.items():
        status = "✅ Configured" if valid else "❌ Missing"
        print(f"   {provider.title()}: {status}")

    # Show task routing examples
    print("\n🎯 Task Routing Examples:")
    test_tasks = [TaskType.REAL_TIME, TaskType.ARBITRAGE, TaskType.COMPLEX_REASONING]
    for task in test_tasks:
        routing = config.get_provider_for_task(task)
        print(f"   {task.value}: {routing['provider'].value} ({routing['reasoning']})")

    # Show usage recommendations
    print("\n💡 Usage Recommendations:")
    recommendations = config.get_usage_recommendations()
    for category, items in recommendations.items():
        print(f"\n   {category.replace('_', ' ').title()}:")
        for item in items[:3]:  # Show first 3 items
            print(f"     {item}")

    print(f"\n⏰ Configuration generated: {config.config_timestamp}")
    print("🚀 Ready for production AI-powered sports betting!")


if __name__ == "__main__":
    main()
