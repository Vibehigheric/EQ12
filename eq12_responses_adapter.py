# eq12_responses_adapter.py
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

try:
    from eq12_limit_guard import require_budget
    from eq12_vector_service import rag_search
except ImportError:
    # Fallback if modules not found
    def require_budget(service: str, est_cost_usd: float):
        def decorator(func):
            return func

        return decorator

    def rag_search(query: str, k: int = 5):
        return []


class ParlayLeg(BaseModel):
    """Individual bet within a parlay"""

    game_id: str
    market: Literal["Moneyline", "Spread", "Total"]
    selection: str
    odds: int
    sportsbook: str


class ParlayAdvice(BaseModel):
    """Structured parlay recommendation"""

    legs: list[ParlayLeg]
    edge_pct: float = Field(ge=-100, le=100, description="Expected edge percentage")
    bankroll_stake: float = Field(ge=0, description="Recommended stake as % of bankroll")
    rationale: str = Field(min_length=10, description="Analysis and reasoning")
    risk: Literal["LOW", "MEDIUM", "MEDIUM-HIGH", "HIGH"]


class EVSummary(BaseModel):
    """Expected value analysis summary"""

    bankroll_optimal_stake: float = Field(ge=0, description="Kelly-optimal stake %")
    expected_profit_pct: float = Field(description="Expected profit as % of stake")
    win_probability: float = Field(ge=0, le=1, description="Estimated win probability")
    max_loss_pct: float = Field(ge=0, description="Maximum loss as % of bankroll")
    confidence: Literal["LOW", "MEDIUM", "HIGH"]
    recommendation: Literal["AVOID", "SMALL", "MEDIUM", "LARGE"]
    analysis: str = Field(min_length=20, description="Detailed EV analysis")


class UsageSnapshot(BaseModel):
    """API usage tracking snapshot"""

    timestamp: str
    service: str
    cost_usd: float
    daily_total: float
    budget_remaining: float
    request_type: str


def get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"


def get_openai_client():
    """Get configured OpenAI client"""
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        return OpenAI(api_key=api_key)
    except ImportError:
        raise ImportError("OpenAI package required: pip install openai")


@require_budget("parlay_analysis", 0.15)
def advise_parlay(prompt: str, context_docs: list[str] | None = None) -> ParlayAdvice:
    """
    Generate structured parlay advice with RAG context

    Args:
        prompt: User's parlay request or game details
        context_docs: Optional pre-selected context documents

    Returns:
        ParlayAdvice: Structured parlay recommendation
    """
    client = get_openai_client()

    # Get context from RAG if not provided
    nuggets = context_docs or [d["text"] for d in rag_search(prompt, k=5)]

    rag_context = "\n".join(nuggets) if nuggets else "No additional context available."

    system = """You are EQ12 Sports Analyst. Return ONLY a JSON object matching this exact schema:
{
  "legs": [{"game_id": "string", "market": "Moneyline|Spread|Total", "selection": "string", "odds": integer, "sportsbook": "string"}],
  "edge_pct": float (-100 to 100),
  "bankroll_stake": float,
  "rationale": "string",
  "risk": "LOW|MEDIUM|MEDIUM-HIGH|HIGH"
}
Do not nest in a "parlay" key. Return the flat JSON object directly."""

    user = f"""Analyze this parlay request:
{prompt}

Context from knowledge base:
{rag_context}

Return structured parlay advice as JSON."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.1,
            max_tokens=1000,
        )

        txt = response.choices[0].message.content
        if not txt:
            raise ValueError("Empty response from OpenAI")

        data = json.loads(txt)
        return ParlayAdvice(**data)

    except json.JSONDecodeError as e:
        raise ValueError(f"Structured parse failed: {e}\nRaw: {txt[:400]}") from e
    except Exception as e:
        raise ValueError(f"Parlay analysis failed: {e}") from e


@require_budget("ev_analysis", 0.10)
def analyze_ev(bet_details: str, market_data: str | None = None) -> EVSummary:
    """
    Analyze expected value of a betting opportunity

    Args:
        bet_details: Description of the bet or betting opportunity
        market_data: Optional market data or odds comparison

    Returns:
        EVSummary: Structured EV analysis
    """
    client = get_openai_client()

    system = """You are EQ12 EV Calculator. Return ONLY a JSON object:
{
  "bankroll_optimal_stake": float,
  "expected_profit_pct": float,
  "win_probability": float (0.0 to 1.0),
  "max_loss_pct": float,
  "confidence": "LOW|MEDIUM|HIGH",
  "recommendation": "AVOID|SMALL|MEDIUM|LARGE",
  "analysis": "detailed string"
}"""

    user_prompt = f"Analyze EV for: {bet_details}"
    if market_data:
        user_prompt += f"\n\nMarket data: {market_data}"

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=800,
        )

        txt = response.choices[0].message.content
        if not txt:
            raise ValueError("Empty response from OpenAI")

        data = json.loads(txt)
        return EVSummary(**data)

    except json.JSONDecodeError as e:
        raise ValueError(f"EV analysis parse failed: {e}\nRaw: {txt[:400]}") from e
    except Exception as e:
        raise ValueError(f"EV analysis failed: {e}") from e


def advise_parlay_enhanced(prompt: str, use_responses_api: bool = True) -> dict:
    """
    Enhanced parlay analysis using Responses API when available

    Args:
        prompt: User's parlay request or game details
        use_responses_api: Whether to use Responses API features

    Returns:
        Enhanced response with Responses API features or fallback to regular analysis
    """
    try:
        if use_responses_api:
            from eq12_responses_client import ask_with_responses, get_responses_client

            client = get_responses_client()
            if client and client.openai_client:
                # Get RAG context
                nuggets = [d["text"] for d in rag_search(prompt, k=5)]
                rag_context = "\n".join(nuggets) if nuggets else "No context available."

                # Enhanced prompt with context
                enhanced_prompt = f"""Analyze this parlay request with expert sports betting knowledge:
{prompt}

Knowledge base context:
{rag_context}

Provide structured parlay advice as JSON matching this exact schema:
{{
  "legs": [{{"game_id": "string", "market": "Moneyline|Spread|Total", "selection": "string", "odds": integer, "sportsbook": "string"}}],
  "edge_pct": float (-100 to 100),
  "bankroll_stake": float,
  "rationale": "string",
  "risk": "LOW|MEDIUM|MEDIUM-HIGH|HIGH"
}}

Include detailed reasoning about correlations, value, and risk assessment."""

                system_msg = "You are EQ12 Sports Analyst with access to real-time data and advanced analytics."

                response = ask_with_responses(
                    enhanced_prompt,
                    system_message=system_msg,
                    tools=["web_search", "function"],
                    model="gpt-4o-mini",
                )

                # Parse structured response
                content = response.get("content", "")
                if "```json" in content:
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    json_str = content[json_start:json_end].strip()
                elif "{" in content and "}" in content:
                    # Find the JSON object in the response
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    json_str = content[start:end]
                else:
                    json_str = content

                try:
                    parsed = json.loads(json_str)
                    validated = ParlayAdvice(**parsed)
                    return {
                        "advice": validated.model_dump(),
                        "enhanced": True,
                        "debug": response.get("debug", {}),
                        "tools_used": response.get("tools_used", []),
                        "request_id": response.get("debug", {}).get("request_id"),
                    }
                except (json.JSONDecodeError, ValueError) as e:
                    # Return raw response with error info
                    return {
                        "advice": {"error": f"Parse failed: {e}", "raw_content": content},
                        "enhanced": True,
                        "parse_error": str(e),
                    }

    except ImportError:
        pass  # Fall through to regular analysis
    except Exception as e:
        print(f"Enhanced analysis failed: {e}")

    # Fallback to regular analysis
    advice = advise_parlay(prompt)
    return {"advice": advice.model_dump(), "enhanced": False}


def track_usage(service: str, cost_usd: float, request_type: str) -> UsageSnapshot:
    """Create usage tracking snapshot"""
    return UsageSnapshot(
        timestamp=get_utc_timestamp(),
        service=service,
        cost_usd=cost_usd,
        daily_total=cost_usd,  # Placeholder
        budget_remaining=25.00 - cost_usd,  # Placeholder
        request_type=request_type,
    )


if __name__ == "__main__":
    # Test both regular and enhanced parlay analysis
    test_prompt = "I want to bet on Lakers moneyline + over 215.5 points tonight"

    print("🏀 Testing Regular Parlay Analysis:")
    try:
        advice = advise_parlay(test_prompt)
        print(f"Parlay Advice: {advice.model_dump_json(indent=2)}")
    except Exception as e:
        print(f"Regular test failed: {e}")

    print("\n🚀 Testing Enhanced Responses API Analysis:")
    try:
        enhanced_response = advise_parlay_enhanced(test_prompt)
        print(f"Enhanced Analysis: {json.dumps(enhanced_response, indent=2)}")
    except Exception as e:
        print(f"Enhanced test failed: {e}")
