#!/usr/bin/env python3
"""
EQ12 Enhanced Betting Analysis with Tiny Helpers Kit
Demonstrates robust LLM fallback, rate limiting, and structured responses

Date: October 4, 2025
Purpose: Show how to use eq12_helpers.py for production betting analysis
"""

import json
import sys

from eq12_helpers import (
    build_json_payload,
    call_with_fallbacks,
    create_openai_client,
    env_get,
    offline_stub,
    setup_utf8_logging,
    start_llm_health_probe,
)


def analyze_parlay_with_fallbacks(parlay_data):
    """Enhanced parlay analysis using EQ12 helpers with robust fallback"""

    # Build messages for LLM analysis
    messages = [
        {
            "role": "system",
            "content": """You are an expert sports betting analyst. Analyze parlays and return JSON matching this schema:
{
  "mode": "live",
  "task": "parlay_analysis",
  "result": {
    "recommendation": "string",
    "confidence": 0.0-1.0,
    "risk_level": "low|medium|high",
    "expected_value": "percentage",
    "key_factors": ["factor1", "factor2"],
    "warnings": ["warning1", "warning2"]
  },
  "meta": {
    "model": "string",
    "tokens_est": 0,
    "ts": 0
  }
}""",
        },
        {"role": "user", "content": f"Analyze this parlay: {json.dumps(parlay_data)}"},
    ]

    def payload_builder(model):
        return build_json_payload(
            model, messages, max_tokens=int(env_get("EQ12_MAX_OUTPUT_TOKENS", "1500"))
        )

    try:
        # Use robust fallback system
        response = call_with_fallbacks(
            create_openai_client,
            payload_builder,
            "parlay validator",
            on_result=lambda r: r.choices[0].message.content,
        )

        # Parse and validate JSON response
        result = json.loads(response)
        return result

    except RuntimeError as e:
        # Circuit breaker is open → use offline fallback
        if "breaker open" in str(e).lower():
            return offline_stub("parlay_analysis", messages)
        raise
    except json.JSONDecodeError:
        # Malformed JSON → return safe fallback
        return {
            "mode": "offline",
            "task": "parlay_analysis",
            "result": {
                "recommendation": "Unable to analyze - using conservative approach",
                "confidence": 0.3,
                "risk_level": "high",
                "expected_value": "unknown",
                "key_factors": ["System unavailable"],
                "warnings": ["AI analysis failed - manual review recommended"],
            },
            "meta": {"ts": __import__("time").time(), "model": "fallback"},
        }


def main():
    # Setup UTF-8 logging to handle emojis
    setup_utf8_logging()

    # Start health probe for circuit breaker recovery
    start_llm_health_probe(create_openai_client, interval_sec=900)

    # Example parlay from our earlier analysis
    parlay_data = {
        "game": "Los Angeles Dodgers @ Philadelphia Phillies",
        "date": "2025-10-04",
        "legs": [
            {
                "player": "Bryce Harper",
                "prop": "Home Run",
                "odds": "+219",
                "probability": "31.3%",
            },
            {
                "player": "Mookie Betts",
                "prop": "Home Run",
                "odds": "+268",
                "probability": "27.1%",
            },
        ],
        "combined_odds": "+1073",
        "estimated_probability": "8.5%",
    }

    print("🎯 EQ12 Enhanced Betting Analysis with Fallback Protection")
    print("=" * 65)

    try:
        # Analyze with robust fallback protection
        analysis = analyze_parlay_with_fallbacks(parlay_data)

        print("\n📊 ANALYSIS RESULTS:")
        print(f"Mode: {analysis['mode']} ({analysis.get('meta', {}).get('model', 'unknown')})")
        print("Task: {analysis['task']}")

        result = analysis.get("result", {})
        print("\n🎯 RECOMMENDATION: {result.get('recommendation', 'N/A')}")
        print("📈 Confidence: {result.get('confidence', 0):.1%}")
        print("⚠️  Risk Level: {result.get('risk_level', 'unknown').upper()}")
        print("💰 Expected Value: {result.get('expected_value', 'unknown')}")

        factors = result.get("key_factors", [])
        if factors:
            print("\n🔑 KEY FACTORS:")
            for _factor in factors:
                print("  • {factor}")

        warnings = result.get("warnings", [])
        if warnings:
            print("\n⚠️  WARNINGS:")
            for _warning in warnings:
                print("  • {warning}")

        # Save analysis with timestamp
        timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"C:/EQ12/logs/enhanced_parlay_analysis_{timestamp}.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2)
        print("\n💾 Analysis saved to: {log_file}")

    except Exception:
        print("❌ Error in analysis: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
