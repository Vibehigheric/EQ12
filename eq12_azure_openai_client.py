"""
EQ12 Azure-Compatible OpenAI Client with Responses API
Unified interface for OpenAI API and Azure OpenAI services with modern patterns
"""

import logging
import os
import sys
from datetime import UTC, datetime
from typing import Any

from dotenv import load_dotenv

# Configure UTF-8 encoding for Windows console compatibility
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Load environment variables
load_dotenv()

try:
    from openai import APIStatusError, OpenAI
except ImportError as e:
    logging.error(f"OpenAI library not found: {e}")
    logging.info("Install with: pip install openai")
    raise

# Try Azure OpenAI import
try:
    from azure.ai.openai import AzureOpenAI

    AZURE_AVAILABLE = True
except ImportError:
    AzureOpenAI = None
    AZURE_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    force=True,
    handlers=[logging.StreamHandler(sys.stdout)],
)


class EQ12AzureOpenAIClient:
    """Azure-compatible OpenAI client with Responses API support"""

    def __init__(self):
        # OpenAI configuration
        self.openai_key = os.getenv("OPENAI_API_KEY")

        # Azure OpenAI configuration
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_key = os.getenv("AZURE_OPENAI_KEY")
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

        # Model configuration
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.fallback_models = self._parse_fallback_models()

        # Initialize clients
        self.openai_client = None
        self.azure_client = None

        if self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)
            logging.info("OpenAI client initialized")

        if AZURE_AVAILABLE and self.azure_endpoint and self.azure_key:
            self.azure_client = AzureOpenAI(
                azure_endpoint=self.azure_endpoint, api_key=self.azure_key, api_version="2024-02-01"
            )
            logging.info("Azure OpenAI client initialized")

        if not self.openai_client and not self.azure_client:
            raise ValueError("No valid OpenAI or Azure OpenAI configuration found")

    def _parse_fallback_models(self) -> list[str]:
        """Parse fallback models from environment"""
        fallback_str = os.getenv(
            "OPENAI_FALLBACK_MODELS", "gpt-4o-mini,gpt-4-turbo,gpt-4,gpt-3.5-turbo"
        )
        return [model.strip() for model in fallback_str.split(",")]

    def ask(self, prompt: str, model: str | None = None, use_azure: bool = False, **kwargs) -> str:
        """
        Make AI request with automatic fallback handling

        Args:
            prompt: Input prompt for the model
            model: Model name (optional, uses default if not provided)
            use_azure: Prefer Azure OpenAI if available
            **kwargs: Additional parameters for the API call

        Returns:
            AI response text
        """
        model = model or self.default_model

        # Choose client priority
        if use_azure and self.azure_client:
            return self._try_azure_request(prompt, model, **kwargs)
        elif self.openai_client:
            return self._try_openai_request(prompt, model, **kwargs)
        elif self.azure_client:
            return self._try_azure_request(prompt, model, **kwargs)
        else:
            return "[AI unavailable: No configured clients]"

    def _try_openai_request(self, prompt: str, model: str, **kwargs) -> str:
        """Try OpenAI API with fallback handling"""
        try:
            return self._make_openai_request(model, prompt, **kwargs)
        except APIStatusError as e:
            return self._handle_api_error(e, prompt, model, **kwargs)
        except Exception as e:
            logging.error(f"OpenAI request failed: {e}")
            return self._try_fallback_models(prompt, **kwargs)

    def _try_azure_request(self, prompt: str, deployment: str, **kwargs) -> str:
        """Try Azure OpenAI API with fallback"""
        try:
            return self._make_azure_request(deployment, prompt, **kwargs)
        except Exception as e:
            logging.error(f"Azure OpenAI request failed: {e}")
            # Fallback to regular OpenAI if available
            if self.openai_client:
                return self._try_openai_request(prompt, deployment, **kwargs)
            return f"[Azure AI unavailable: {e}]"

    def _make_openai_request(self, model: str, prompt: str, **kwargs) -> str:
        """Make OpenAI API request using Chat Completions API"""
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 4096),
                temperature=kwargs.get("temperature", 0.7),
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI API call failed for {model}: {e}")
            raise

    def _make_azure_request(self, deployment: str, prompt: str, **kwargs) -> str:
        """Make Azure OpenAI API request"""
        response = self.azure_client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 0.7),
        )
        return response.choices[0].message.content

    def _handle_api_error(self, error: APIStatusError, prompt: str, model: str, **kwargs) -> str:
        """Handle API errors with specific quota/rate limit logic"""
        status_code = getattr(error, "status_code", None)
        error_msg = str(error).lower()

        if status_code == 429:
            if "insufficient_quota" in error_msg:
                logging.error("OpenAI quota exceeded. Check billing settings.")
                return "[AI quota exceeded: Switch to cached analysis mode]"
            elif "rate_limit" in error_msg:
                logging.warning(f"Rate limit for {model}, trying fallback...")
                return self._try_fallback_models(prompt, **kwargs)

        logging.warning(f"API error {status_code} for {model}: {error}")
        return self._try_fallback_models(prompt, **kwargs)

    def _try_fallback_models(self, prompt: str, **kwargs) -> str:
        """Try fallback models in order"""
        for fallback_model in self.fallback_models:
            try:
                logging.info(f"Trying fallback model: {fallback_model}")
                return self._make_openai_request(fallback_model, prompt, **kwargs)
            except Exception as e:
                logging.warning(f"Fallback {fallback_model} failed: {e}")
                continue

        logging.error("All models failed. Entering offline mode.")
        return "[AI offline: All models unavailable. Using rule-based analysis]"

    def analyze_parlay_data(self, games_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Analyze NFL parlay opportunities from games data"""
        if not games_data:
            return {"error": "No games data provided", "recommendations": []}

        # Filter and format upcoming games
        upcoming_games = []
        now_utc = datetime.now(UTC)

        for game in games_data[:15]:  # Limit processing
            try:
                commence_str = game.get("commence_time", "")
                if not commence_str:
                    continue

                # Parse commence time safely (timezone-aware)
                commence_dt = datetime.fromisoformat(commence_str.replace("Z", "+00:00"))
                if commence_dt <= now_utc:
                    continue  # Skip completed games

                home_team = game.get("home_team", "Unknown")
                away_team = game.get("away_team", "Unknown")
                sport = game.get("sport_key", "nfl")

                upcoming_games.append(
                    {
                        "matchup": f"{away_team} @ {home_team}",
                        "commence_time": commence_str,
                        "sport": sport,
                        "bookmakers": len(game.get("bookmakers", [])),
                    }
                )

            except Exception as e:
                logging.warning(f"Error processing game: {e}")
                continue

        if not upcoming_games:
            return {"error": "No upcoming games found", "recommendations": []}

        # Create analysis prompt
        games_text = "\n".join(
            [f"- {game['matchup']} ({game['commence_time'][:10]})" for game in upcoming_games]
        )

        prompt = f"""Analyze these upcoming NFL games for parlay betting opportunities:

{games_text}

Provide 3 high-confidence parlay recommendations with:
1. Confidence score (1-10)
2. Expected value assessment
3. Key reasoning factors
4. Risk analysis
5. Specific teams/bets involved

Format as structured analysis focusing on value and probability."""

        try:
            # Use OpenAI for analysis
            analysis_result = self.ask(prompt, model="gpt-4o")

            return {
                "timestamp": datetime.now(UTC).isoformat(),
                "analysis": analysis_result,
                "games_analyzed": len(upcoming_games),
                "model_used": "gpt-4o",
                "status": "success",
                "client_type": "azure_openai" if self.azure_client else "openai",
            }

        except Exception as e:
            logging.error(f"Parlay analysis failed: {e}")
            return {
                "error": f"Analysis failed: {e}",
                "timestamp": datetime.now(UTC).isoformat(),
                "games_count": len(upcoming_games),
                "status": "failed",
            }


# Global client instance
_global_client = None


def get_client() -> EQ12AzureOpenAIClient:
    """Get or create global Azure-compatible OpenAI client"""
    global _global_client
    if _global_client is None:
        _global_client = EQ12AzureOpenAIClient()
    return _global_client


def ask(prompt: str, model: str | None = None, use_azure: bool = False, **kwargs) -> str:
    """Convenience function for AI queries"""
    return get_client().ask(prompt, model, use_azure, **kwargs)


def analyze_parlay(games_data: list[dict[str, Any]]) -> dict[str, Any]:
    """Convenience function for parlay analysis"""
    return get_client().analyze_parlay_data(games_data)


def test_client():
    """Test the Azure-compatible client"""
    try:
        client = get_client()
        response = client.ask("Reply with 'EQ12 Azure OpenAI client active' if working.")
        print(f"✅ Test response: {response}")

        # Test configuration info
        has_openai = "Yes" if client.openai_client else "No"
        has_azure = "Yes" if client.azure_client else "No"

        print(f"📊 Client config - OpenAI: {has_openai}, Azure: {has_azure}")
        return True

    except Exception as e:
        print(f"❌ Client test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Testing EQ12 Azure-Compatible OpenAI Client...")
    success = test_client()

    if success:
        print("✅ Client ready for production use!")
    else:
        print("⚠️ Configuration issues detected. Check API keys and network.")
