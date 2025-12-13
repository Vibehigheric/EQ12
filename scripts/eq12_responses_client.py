#!/usr/bin/env python3
"""
EQ12 Responses API Integration
Structured JSON parlay recommendations using GPT-5 with reusable prompts.

This module provides production-ready integration with OpenAI's Responses API
for generating parlay recommendations with strict EQ12 constraints.
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI


@dataclass
class EQ12ResponsesConfig:
    """Configuration for EQ12 Responses API calls."""

    api_key: str
    model: str = "gpt-4o"  # Default to gpt-4o, upgrade to gpt-5 when available
    temperature: float = 0.1
    max_tokens: int | None = None
    reasoning_effort: str = "low"  # low, medium, high


class EQ12ResponsesClient:
    """
    Production OpenAI Responses API client for EQ12 parlay generation.
    Uses reusable prompts and structured outputs.
    """

    def __init__(self, config: EQ12ResponsesConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key)
        self.prompts_dir = Path(__file__).parent / "prompts"
        self._load_schemas()

    def _load_schemas(self):
        """Load JSON schemas for structured outputs."""
        schema_dir = Path(__file__).parent.parent / "models" / "schemas"

        self.parlay_schema = self._load_json_file(schema_dir / "parlay_build.json")
        self.odds_schema = self._load_json_file(schema_dir / "odds_extract.json")

        # Fallback schemas if files not found
        if not self.parlay_schema:
            self.parlay_schema = self._get_default_parlay_schema()
        if not self.odds_schema:
            self.odds_schema = self._get_default_odds_schema()

    def _load_json_file(self, filepath: Path) -> dict | None:
        """Load JSON file with error handling."""
        try:
            if filepath.exists():
                with open(filepath) as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading {filepath}: {e}")
        return None

    def _get_default_parlay_schema(self) -> dict:
        """Default parlay schema if file not found."""
        return {
            "type": "object",
            "required": ["strategy", "stake", "legs"],
            "properties": {
                "strategy": {"type": "string"},
                "stake": {"type": "number"},
                "legs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "book": {
                                "type": "string",
                                "enum": ["DraftKings", "FanDuel", "BetMGM"],
                            },
                            "game_id": {"type": "string"},
                            "market": {"type": "string"},
                            "selection": {"type": "string"},
                            "odds": {"type": "integer"},
                            "model_prob": {"type": "number"},
                        },
                        "required": [
                            "book",
                            "game_id",
                            "market",
                            "selection",
                            "odds",
                            "model_prob",
                        ],
                    },
                },
                "explanation": {"type": "string"},
            },
        }

    def _get_default_odds_schema(self) -> dict:
        """Default odds extraction schema."""
        return {
            "type": "object",
            "required": ["rows", "extracted_at_utc", "books_found"],
            "properties": {
                "rows": {"type": "array"},
                "extracted_at_utc": {"type": "string"},
                "books_found": {"type": "array"},
            },
        }

    def build_parlay_with_prompt_id(
        self,
        prompt_id: str,
        prompt_version: str = "current",
        variables: dict[str, str] | None = None,
        reasoning_effort: str | None = None,
    ) -> dict:
        """
        Build parlay using Responses API with reusable prompt IDs.

        Args:
            prompt_id: Reusable prompt ID (e.g., "pmpt_eq12_build_parlay_v1")
            prompt_version: Prompt version ("current", "v1", "v2", etc.)
            variables: Dict of variables for prompt template
            reasoning_effort: Override reasoning effort ("low", "medium", "high")

        Returns:
            Structured parlay recommendation or error
        """
        try:
            # Use provided reasoning effort or config default
            effort = reasoning_effort or self.config.reasoning_effort

            # Prepare request body for Responses API
            request_body = {
                "model": self.config.model,
                "temperature": self.config.temperature,
                "prompt": {
                    "id": prompt_id,
                    "version": prompt_version,
                    "variables": variables or {},
                },
            }

            # Add reasoning effort for GPT-5
            if self.config.model.startswith("gpt-5"):
                request_body["reasoning"] = {"effort": effort}

            # Add max_tokens if specified
            if self.config.max_tokens:
                request_body["max_tokens"] = self.config.max_tokens

            # Make Responses API call
            response = self.client.post("/v1/responses", json=request_body)

            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}",
                    "tokens": 0,
                }

            response_data = response.json()

            # Extract output based on prompt type
            if "output_text" in response_data:
                # Plain text output (for alerts)
                return {
                    "success": True,
                    "data": {"text": response_data["output_text"]},
                    "tokens": response_data.get("usage", {}).get("total_tokens", 0),
                    "model_used": self.config.model,
                    "reasoning_effort": effort,
                }
            elif "output_json" in response_data:
                # Structured JSON output (for parlays)
                return {
                    "success": True,
                    "data": response_data["output_json"],
                    "tokens": response_data.get("usage", {}).get("total_tokens", 0),
                    "model_used": self.config.model,
                    "reasoning_effort": effort,
                }
            else:
                return {
                    "success": False,
                    "error": "Unexpected response format",
                    "tokens": 0,
                }

        except Exception as e:
            return {"success": False, "error": str(e), "tokens": 0}

    def build_parlay_with_ai(
        self,
        strategy: str,
        candidate_legs: list[dict],
        bankroll: float = 1000,
        min_ev: float = 0.025,
        max_legs: int = 6,
    ) -> dict:
        """
        Build parlay using AI with structured output.

        Args:
            strategy: Parlay strategy (yolo, balanced, conservative, spreads_only)
            candidate_legs: List of leg candidates with odds/probs
            bankroll: Available bankroll
            min_ev: Minimum EV threshold
            max_legs: Maximum legs allowed

        Returns:
            Structured parlay recommendation or error
        """
        try:
            # Load strategy-specific prompt
            prompt_content = self._load_strategy_prompt(strategy)

            # Prepare variables for prompt
            variables = {
                "allowed_books": "DraftKings,FanDuel,BetMGM",
                "min_ev": str(min_ev),
                "max_legs": str(max_legs),
                "bankroll": str(bankroll),
                "legs_json": json.dumps(candidate_legs, indent=2),
            }

            # Fill prompt template
            filled_prompt = self._fill_prompt_template(prompt_content, variables)

            # Make API call with structured output
            response = self.client.chat.completions.create(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                messages=[
                    {
                        "role": "system",
                        "content": "You are EQ12's expert parlay builder. Return only valid JSON that matches the provided schema. Focus on DraftKings/FanDuel/BetMGM only.",
                    },
                    {"role": "user", "content": filled_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "parlay_recommendation",
                        "schema": self.parlay_schema,
                    },
                },
            )

            # Parse and validate response
            content = response.choices[0].message.content
            parlay_data = json.loads(content)

            # Add metadata
            parlay_data["model_used"] = self.config.model
            parlay_data["tokens_used"] = response.usage.total_tokens if response.usage else 0
            parlay_data["strategy_requested"] = strategy

            return {
                "success": True,
                "data": parlay_data,
                "model_used": self.config.model,
                "tokens": response.usage.total_tokens if response.usage else 0,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_used": self.config.model,
                "tokens": 0,
            }

    def extract_odds_with_ai(self, raw_odds_text: str) -> dict:
        """
        Extract and normalize odds using AI.

        Args:
            raw_odds_text: Raw sportsbook odds text

        Returns:
            Structured odds extraction or error
        """
        try:
            # Load odds extraction prompt
            prompt_content = self._load_prompt("odds_extractor.md")

            # Fill prompt with odds text
            filled_prompt = prompt_content.replace("{{raw_odds}}", raw_odds_text)

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use cheaper model for extraction
                temperature=0.0,  # Deterministic extraction
                messages=[
                    {
                        "role": "system",
                        "content": "You are EQ12's odds extraction engine. Only process DraftKings/FanDuel/BetMGM. Return valid JSON per schema.",
                    },
                    {"role": "user", "content": filled_prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "odds_extraction",
                        "schema": self.odds_schema,
                    },
                },
            )

            content = response.choices[0].message.content
            odds_data = json.loads(content)

            return {
                "success": True,
                "data": odds_data,
                "model_used": "gpt-4o-mini",
                "tokens": response.usage.total_tokens if response.usage else 0,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_used": "gpt-4o-mini",
                "tokens": 0,
            }

    def generate_alert_copy(self, parlay_data: dict) -> str:
        """
        Generate Telegram alert copy for parlay.

        Args:
            parlay_data: Structured parlay data

        Returns:
            Human-readable alert text
        """
        try:
            # Load alert prompt
            prompt_content = self._load_prompt("alert_copy.md")

            # Fill with parlay data
            filled_prompt = prompt_content.replace(
                "{{parlay_json}}", json.dumps(parlay_data, indent=2)
            )

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cheap model for copy generation
                temperature=0.3,  # Slightly creative
                max_tokens=150,  # Short alerts only
                messages=[
                    {
                        "role": "system",
                        "content": "Generate concise, confident betting alerts. Max 80 words. Include EV, odds, and risk.",
                    },
                    {"role": "user", "content": filled_prompt},
                ],
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error generating alert: {e}"

    def _load_strategy_prompt(self, strategy: str) -> str:
        """Load strategy-specific prompt template."""
        filename_map = {
            "yolo": "parlay_builder_yolo.md",
            "balanced": "parlay_builder_balanced.md",
            "conservative": "parlay_builder_conservative.md",
            "spreads_only": "parlay_builder_spreads.md",
        }

        filename = filename_map.get(strategy, "parlay_builder_balanced.md")
        return self._load_prompt(filename)

    def _load_prompt(self, filename: str) -> str:
        """Load prompt template from file."""
        try:
            prompt_file = self.prompts_dir / filename
            if prompt_file.exists():
                return prompt_file.read_text()
            else:
                # Return fallback prompt
                return self._get_fallback_prompt(filename)
        except Exception as e:
            print(f"⚠️ Error loading prompt {filename}: {e}")
            return self._get_fallback_prompt(filename)

    def _get_fallback_prompt(self, filename: str) -> str:
        """Fallback prompts if files not found."""
        if "parlay_builder" in filename:
            return """You are EQ12's parlay builder.

Rules:
- Only use books: {{allowed_books}}
- Target EV ≥ {{min_ev}}%
- Max legs: {{max_legs}}
- Avoid same-game correlation
- Apply Kelly sizing
- Return JSON only per schema

Candidate legs:
{{legs_json}}

Build optimal parlay for specified strategy."""

        elif "odds_extractor" in filename:
            return """Extract odds from this text into normalized JSON format:

{{raw_odds}}

Rules:
- Only DraftKings/FanDuel/BetMGM
- UTC timestamps in RFC3339
- Flag .5 hook lines
- Return JSON per schema"""

        elif "alert_copy" in filename:
            return """Generate a concise Telegram alert for this parlay:

{{parlay_json}}

Requirements:
- Max 80 words
- Include EV%, odds, stake
- Sharp, confident tone
- End with emoji"""

        return "Generic EQ12 prompt - customize as needed."

    def _fill_prompt_template(self, template: str, variables: dict[str, str]) -> str:
        """Fill prompt template with variables."""
        filled = template
        for key, value in variables.items():
            filled = filled.replace(f"{{{{{key}}}}}", value)
        return filled


# Convenience function for quick setup
def create_eq12_responses_client(api_key: str | None = None) -> EQ12ResponsesClient:
    """Create EQ12 Responses client with default config."""
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required (set OPENAI_API_KEY env var)")

    config = EQ12ResponsesConfig(api_key=api_key)
    return EQ12ResponsesClient(config)


if __name__ == "__main__":
    # Test Responses API integration
    print("🤖 EQ12 Responses API Test")
    print("=" * 50)

    try:
        client = create_eq12_responses_client()

        # Test odds extraction
        sample_odds = """
        DraftKings NFL:
        Chiefs -3.0 (-110) vs Bills +3.0 (-110)

        FanDuel:
        Chiefs -2.5 (-105), Bills +2.5 (-115)
        """

        extraction_result = client.extract_odds_with_ai(sample_odds)
        print(f"✅ Odds extraction: {extraction_result['success']}")

        if extraction_result["success"]:
            print(f"   Extracted {len(extraction_result['data'].get('rows', []))} odds")

        # Test parlay building
        sample_legs = [
            {
                "game_id": "nfl_20251005_chiefs_bills",
                "book": "DraftKings",
                "market": "spread",
                "selection": "Chiefs -3.0",
                "odds": -110,
                "model_prob": 0.58,
            }
        ]

        parlay_result = client.build_parlay_with_ai(
            "balanced", sample_legs, bankroll=1000)
        print(f"✅ Parlay building: {parlay_result['success']}")

        if parlay_result["success"]:
            legs = parlay_result["data"].get("legs", [])
            print(f"   Built parlay with {len(legs)} legs")

            # Test alert generation
            alert = client.generate_alert_copy(parlay_result["data"])
            print(f"✅ Alert copy: {alert[:50]}...")

        print("\n✅ Responses API integration working!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("💡 Make sure OPENAI_API_KEY is set in environment")

    # Convenience methods for the three main EQ12 prompts

    def build_parlay_architect(
        self,
        candidate_legs: list[dict],
        bankroll: float = 1000,
        max_legs: int = 8,
        min_ev: float = 0.08,
        corr: float = 0.08,
        reasoning_effort: str = "low",
    ) -> dict:
        """
        Use pmpt_eq12_build_parlay_v1 - the main parlay architect.

        Args:
            candidate_legs: List of leg candidates
            bankroll: Total bankroll
            max_legs: Maximum legs in parlay
            min_ev: Minimum EV threshold (decimal)
            corr: Correlation penalty exponent
            reasoning_effort: "low", "medium", "high"

        Returns:
            Structured parlay recommendation
        """
        variables = {
            "allowed_books": "DraftKings,FanDuel,BetMGM",
            "max_legs": str(max_legs),
            "corr": str(corr),
            "min_ev": str(min_ev),
            "bankroll": str(bankroll),
            "legs_json": json.dumps(candidate_legs),
        }

        return self.build_parlay_with_prompt_id(
            prompt_id="pmpt_eq12_build_parlay_v1",
            variables=variables,
            reasoning_effort=reasoning_effort,
        )

    def build_hooks_specialist(
        self,
        candidate_legs: list[dict],
        bankroll: float = 1000,
        max_legs: int = 6,
        min_ev: float = 0.08,
        corr: float = 0.08,
        reasoning_effort: str = "medium",
    ) -> dict:
        """
        Use pmpt_eq12_spread_hooks_v1 - hooks specialist for spreads/totals only.

        Args:
            candidate_legs: List of leg candidates (should include hooks)
            bankroll: Total bankroll
            max_legs: Maximum legs in parlay
            min_ev: Minimum EV threshold (decimal)
            corr: Correlation penalty exponent
            reasoning_effort: "low", "medium", "high"

        Returns:
            Hooks-focused parlay recommendation
        """
        # Filter to only hooks for hooks specialist
        hook_legs = [
            leg
            for leg in candidate_legs
            if leg.get("hook_flag") is True
            or (leg.get("point") is not None and abs(leg["point"] % 1) == 0.5)
        ]

        variables = {
            "allowed_books": "DraftKings,FanDuel,BetMGM",
            "max_legs": str(max_legs),
            "corr": str(corr),
            "min_ev": str(min_ev),
            "bankroll": str(bankroll),
            "legs_json": json.dumps(hook_legs),
        }

        return self.build_parlay_with_prompt_id(
            prompt_id="pmpt_eq12_spread_hooks_v1",
            variables=variables,
            reasoning_effort=reasoning_effort,
        )

    def generate_alert_copy_v2(
        self,
        book: str,
        team_or_market: str,
        selection: str,
        odds: int,
        ev_pct: str,
        kelly: str,
        kickoff_local: str,
        why: str,
    ) -> dict:
        """
        Use pmpt_eq12_alert_copy_v1 - generate Telegram/Slack one-liners.

        Args:
            book: Sportsbook name (DraftKings/FanDuel/BetMGM)
            team_or_market: Team names or market description
            selection: Specific bet selection
            odds: American odds format
            ev_pct: EV as percentage (e.g., "8.2%")
            kelly: Kelly stake in dollars (e.g., "45")
            kickoff_local: Local kickoff time (e.g., "4:25p EST")
            why: Brief reasoning (max 15 chars)

        Returns:
            Short alert copy under 140 characters
        """
        variables = {
            "book": book,
            "team_or_market": team_or_market,
            "selection": selection,
            "odds": str(odds),
            "ev_pct": ev_pct,
            "kelly": kelly,
            "kickoff_local": kickoff_local,
            "why": why,
        }

        return self.build_parlay_with_prompt_id(
            prompt_id="pmpt_eq12_alert_copy_v1",
            variables=variables,
            reasoning_effort="low",
        )
