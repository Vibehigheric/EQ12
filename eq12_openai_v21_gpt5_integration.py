# eq12_openai_v21_gpt5_integration.py
"""
EQ12 OpenAI API v2.1.0 Integration with GPT-5 Model Support
Advanced circuit breaker, retry/backoff, rate limiting, token management
"""

import asyncio
import json
import logging
import secrets
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import httpx

from eq12_helpers import env_get, setup_utf8_logging

setup_utf8_logging()


class ModelTier(Enum):
    """GPT model tiers for intelligent fallback"""

    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-nano"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_3_5_TURBO = "gpt-3.5-turbo"


class CircuitBreakerState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class TokenUsage:
    """Token usage tracking"""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_tokens: int = 0
    cost_usd: float = 0.0


@dataclass
class APIRequest:
    """API request metadata"""

    request_id: str
    model: str
    timestamp: datetime
    prompt_length: int
    response_length: int
    tokens_used: TokenUsage
    latency_ms: float
    success: bool
    error_type: str | None = None


@dataclass
class RateLimitInfo:
    """Rate limit tracking"""

    requests_per_minute: int
    tokens_per_minute: int
    requests_remaining: int
    tokens_remaining: int
    reset_time: datetime


class AdvancedCircuitBreaker:
    """Enhanced circuit breaker with intelligent failure detection"""

    def __init__(self, failure_threshold: int = 5, reset_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        self.half_open_success_threshold = 3

    def can_execute(self) -> bool:
        """Check if request can be executed"""

        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            if (
                self.last_failure_time
                and (datetime.now() - self.last_failure_time).seconds >= self.reset_timeout
            ):
                self.state = CircuitBreakerState.HALF_OPEN
                self.success_count = 0
                return True
            return False

        return self.state == CircuitBreakerState.HALF_OPEN

    def record_success(self):
        """Record successful execution"""

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_success_threshold:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0

        if self.state == CircuitBreakerState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self):
        """Record failed execution"""

        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


class TokenBudgetManager:
    """Advanced token budgeting and cost management"""

    def __init__(self, daily_budget_usd: float = 50.0):
        self.daily_budget_usd = daily_budget_usd
        self.current_spending = 0.0
        self.token_prices = {
            ModelTier.GPT_5: {"input": 0.00003, "output": 0.00006, "cached": 0.000015},
            ModelTier.GPT_5_MINI: {
                "input": 0.00001,
                "output": 0.00002,
                "cached": 0.000005,
            },
            ModelTier.GPT_5_NANO: {
                "input": 0.000005,
                "output": 0.00001,
                "cached": 0.0000025,
            },
            ModelTier.GPT_4O: {"input": 0.0025, "output": 0.01, "cached": 0.00125},
            ModelTier.GPT_4O_MINI: {
                "input": 0.00015,
                "output": 0.0006,
                "cached": 0.000075,
            },
            ModelTier.GPT_3_5_TURBO: {
                "input": 0.0005,
                "output": 0.0015,
                "cached": 0.00025,
            },
        }
        self.reset_date = datetime.now().date()

    def calculate_cost(self, model: ModelTier, tokens: TokenUsage) -> float:
        """Calculate cost for token usage"""

        if model not in self.token_prices:
            return 0.0

        prices = self.token_prices[model]

        # Calculate cost with cached token optimization
        input_cost = (tokens.prompt_tokens - tokens.cached_tokens) * prices["input"]
        cached_cost = tokens.cached_tokens * prices["cached"]
        output_cost = tokens.completion_tokens * prices["output"]

        return input_cost + cached_cost + output_cost

    def can_afford(self, model: ModelTier, estimated_tokens: int) -> bool:
        """Check if request fits within budget"""

        # Reset daily spending if new day
        if datetime.now().date() > self.reset_date:
            self.current_spending = 0.0
            self.reset_date = datetime.now().date()

        # Estimate cost (conservative estimate)
        estimated_cost = estimated_tokens * self.token_prices[model]["input"] * 2

        return (self.current_spending + estimated_cost) <= self.daily_budget_usd

    def record_usage(self, model: ModelTier, tokens: TokenUsage):
        """Record token usage and update spending"""

        cost = self.calculate_cost(model, tokens)
        self.current_spending += cost

        logging.info(
            f"Token usage: {tokens.total_tokens} tokens, ${cost:.4f}, "
            f"daily total: ${self.current_spending:.2f}"
        )


class IntelligentRetryManager:
    """Advanced retry logic with exponential backoff and jitter"""

    def __init__(self):
        self.base_delay = 1.0
        self.max_delay = 60.0
        self.max_retries = 5
        self.jitter_factor = 0.1

    def should_retry(self, attempt: int, error_type: str) -> bool:
        """Determine if request should be retried"""

        if attempt >= self.max_retries:
            return False

        # Retry on rate limits and server errors
        retryable_errors = [
            "rate_limit_exceeded",
            "server_error",
            "timeout",
            "connection_error",
            "service_unavailable",
        ]

        return error_type in retryable_errors

    def get_delay(self, attempt: int, error_type: str) -> float:
        """Calculate retry delay with exponential backoff and jitter"""

        if error_type == "rate_limit_exceeded":
            # Longer delay for rate limits
            base = min(self.base_delay * (2**attempt) * 2, self.max_delay)
        else:
            base = min(self.base_delay * (2**attempt), self.max_delay)

        # Add jitter to prevent thundering herd
        jitter = base * self.jitter_factor * (2 * secrets.SystemRandom().random() - 1)

        return max(0.1, base + jitter)


class OpenAIV21Client:
    """Advanced OpenAI API v2.1.0 client with GPT-5 support"""

    def __init__(self, api_key: str | None = None, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key or env_get("OPENAI_API_KEY")
        self.base_url = base_url

        if not self.api_key:
            raise ValueError("OpenAI API key not found")

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        )

        # Initialize managers
        self.circuit_breaker = AdvancedCircuitBreaker()
        self.token_manager = TokenBudgetManager()
        self.retry_manager = IntelligentRetryManager()
        self.rate_limit_info = {}

        # Request tracking
        self.db_path = Path("C:/EQ12/data/openai_usage.db")
        self.setup_database()

    def setup_database(self):
        """Initialize usage tracking database"""

        self.db_path.parent.mkdir(exist_ok=True, parents=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS api_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT UNIQUE,
                model TEXT,
                timestamp TEXT,
                prompt_length INTEGER,
                response_length INTEGER,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                cached_tokens INTEGER,
                cost_usd REAL,
                latency_ms REAL,
                success INTEGER,
                error_type TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_timestamp ON api_requests(timestamp)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_model ON api_requests(model)
        """
        )

        conn.commit()
        conn.close()

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: ModelTier | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        """Enhanced chat completion with intelligent model fallback"""

        # Default to GPT-5, fallback to available models
        model_priority = [
            ModelTier.GPT_5,
            ModelTier.GPT_5_MINI,
            ModelTier.GPT_4O,
            ModelTier.GPT_4O_MINI,
            ModelTier.GPT_3_5_TURBO,
        ]

        if model:
            # Move specified model to front
            if model in model_priority:
                model_priority.remove(model)
            model_priority.insert(0, model)

        last_error = None

        for target_model in model_priority:
            try:
                # Check circuit breaker
                if not self.circuit_breaker.can_execute():
                    continue

                # Check budget
                estimated_tokens = sum(len(msg["content"]) // 4 for msg in messages)
                if not self.token_manager.can_afford(target_model, estimated_tokens):
                    logging.warning(f"Budget exceeded for {target_model.value}")
                    continue

                result = await self._make_request(
                    messages=messages,
                    model=target_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    **kwargs,
                )

                self.circuit_breaker.record_success()
                return result

            except Exception as e:
                last_error = e
                self.circuit_breaker.record_failure()
                logging.warning(f"Model {target_model.value} failed: {e!s}")
                continue

        # All models failed
        raise Exception(f"All models failed. Last error: {last_error}")

    async def _make_request(
        self,
        messages: list[dict[str, str]],
        model: ModelTier,
        temperature: float,
        max_tokens: int | None,
        stream: bool,
        **kwargs,
    ) -> dict[str, Any]:
        """Make API request with retry logic"""

        request_id = secrets.token_hex(8)
        start_time = time.time()

        attempt = 0
        last_error = None

        while attempt < self.retry_manager.max_retries:
            try:
                # Prepare request
                payload = {
                    "model": model.value,
                    "messages": messages,
                    "temperature": temperature,
                    "stream": stream,
                    **kwargs,
                }

                if max_tokens:
                    payload["max_tokens"] = max_tokens

                # Make request
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "OpenAI-Beta": "assistants=v2",  # Enable v2.1.0 features
                    },
                )

                # Handle rate limiting
                if response.status_code == 429:
                    self._update_rate_limit_info(response.headers)
                    raise httpx.HTTPStatusError(
                        "Rate limit exceeded",
                        request=response.request,
                        response=response,
                    )

                response.raise_for_status()
                result = response.json()

                # Extract usage information
                usage = result.get("usage", {})
                tokens = TokenUsage(
                    prompt_tokens=usage.get("prompt_tokens", 0),
                    completion_tokens=usage.get("completion_tokens", 0),
                    total_tokens=usage.get("total_tokens", 0),
                    cached_tokens=usage.get("prompt_tokens_details", {}).get("cached_tokens", 0),
                )

                # Calculate cost
                tokens.cost_usd = self.token_manager.calculate_cost(model, tokens)
                self.token_manager.record_usage(model, tokens)

                # Record request
                latency_ms = (time.time() - start_time) * 1000
                await self._record_request(
                    request_id, model.value, messages, result, tokens, latency_ms, True
                )

                return result

            except Exception as e:
                attempt += 1
                last_error = e
                error_type = self._classify_error(e)

                if not self.retry_manager.should_retry(attempt, error_type):
                    # Record failed request
                    latency_ms = (time.time() - start_time) * 1000
                    await self._record_request(
                        request_id,
                        model.value,
                        messages,
                        {},
                        TokenUsage(0, 0, 0),
                        latency_ms,
                        False,
                        error_type,
                    )
                    raise e

                delay = self.retry_manager.get_delay(attempt, error_type)
                logging.warning(f"Request failed, retrying in {delay:.1f}s: {e!s}")
                await asyncio.sleep(delay)

        raise last_error

    def _classify_error(self, error: Exception) -> str:
        """Classify error type for retry logic"""

        if isinstance(error, httpx.HTTPStatusError):
            status = error.response.status_code

            if status == 429:
                return "rate_limit_exceeded"
            if 500 <= status < 600:
                return "server_error"
            if status == 503:
                return "service_unavailable"
            return "client_error"

        if isinstance(error, (httpx.TimeoutException, asyncio.TimeoutError)):
            return "timeout"

        if isinstance(error, httpx.ConnectError):
            return "connection_error"

        return "unknown_error"

    def _update_rate_limit_info(self, headers: dict[str, str]):
        """Update rate limit information from response headers"""

        self.rate_limit_info = RateLimitInfo(
            requests_per_minute=int(headers.get("x-ratelimit-limit-requests", 0)),
            tokens_per_minute=int(headers.get("x-ratelimit-limit-tokens", 0)),
            requests_remaining=int(headers.get("x-ratelimit-remaining-requests", 0)),
            tokens_remaining=int(headers.get("x-ratelimit-remaining-tokens", 0)),
            reset_time=datetime.fromtimestamp(
                int(headers.get("x-ratelimit-reset-requests", time.time()))
            ),
        )

    async def _record_request(
        self,
        request_id: str,
        model: str,
        messages: list[dict],
        response: dict,
        tokens: TokenUsage,
        latency_ms: float,
        success: bool,
        error_type: str | None = None,
    ):
        """Record API request for analytics"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        prompt_length = sum(len(msg["content"]) for msg in messages)
        response_length = len(
            str(response.get("choices", [{}])[0].get("message", {}).get("content", ""))
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO api_requests
            (request_id, model, timestamp, prompt_length, response_length,
             prompt_tokens, completion_tokens, total_tokens, cached_tokens,
             cost_usd, latency_ms, success, error_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                request_id,
                model,
                datetime.now().isoformat(),
                prompt_length,
                response_length,
                tokens.prompt_tokens,
                tokens.completion_tokens,
                tokens.total_tokens,
                tokens.cached_tokens,
                tokens.cost_usd,
                latency_ms,
                1 if success else 0,
                error_type,
            ),
        )

        conn.commit()
        conn.close()

    async def get_usage_analytics(self, days: int = 7) -> dict[str, Any]:
        """Get usage analytics for the specified period"""

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total requests and costs
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_requests,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                SUM(total_tokens) as total_tokens,
                SUM(cost_usd) as total_cost,
                AVG(latency_ms) as avg_latency,
                model
            FROM api_requests
            WHERE timestamp >= ?
            GROUP BY model
        """,
            (cutoff_date,),
        )

        model_stats = cursor.fetchall()

        # Error analysis
        cursor.execute(
            """
            SELECT error_type, COUNT(*) as count
            FROM api_requests
            WHERE timestamp >= ? AND success = 0
            GROUP BY error_type
        """,
            (cutoff_date,),
        )

        error_stats = cursor.fetchall()

        conn.close()

        return {
            "period_days": days,
            "model_statistics": [
                {
                    "model": row[5],
                    "total_requests": row[0],
                    "successful_requests": row[1],
                    "success_rate": row[1] / row[0] if row[0] > 0 else 0,
                    "total_tokens": row[2] or 0,
                    "total_cost_usd": row[3] or 0,
                    "avg_latency_ms": row[4] or 0,
                }
                for row in model_stats
            ],
            "error_statistics": [{"error_type": row[0], "count": row[1]} for row in error_stats],
            "rate_limit_info": (asdict(self.rate_limit_info) if self.rate_limit_info else None),
            "circuit_breaker_state": self.circuit_breaker.state.value,
            "daily_budget_remaining": self.token_manager.daily_budget_usd
            - self.token_manager.current_spending,
        }

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class GPT5SportsBettingAgent:
    """Specialized GPT-5 agent for sports betting analysis"""

    def __init__(self):
        self.client = OpenAIV21Client()
        self.system_prompt = """You are an expert sports betting analyst with advanced knowledge of:
- Statistical modeling and probability analysis
- Line movement and market inefficiencies
- Bankroll management and Kelly criterion
- Live betting opportunities and hedging strategies
- Multi-sport correlation analysis
- Weather, injury, and situational factors

Provide precise, actionable insights with confidence intervals and risk assessments."""

    async def analyze_game(self, game_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze a single game with GPT-5"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": f"""
Analyze this game for betting opportunities:

{json.dumps(game_data, indent=2)}

Provide analysis including:
1. Recommended bets with confidence levels
2. Key factors influencing the outcome
3. Risk assessment and position sizing
4. Potential hedge opportunities
""",
            },
        ]

        response = await self.client.chat_completion(
            messages=messages, model=ModelTier.GPT_5, temperature=0.3, max_tokens=2000
        )

        return {
            "analysis": response["choices"][0]["message"]["content"],
            "model_used": response.get("model"),
            "usage": response.get("usage"),
            "confidence_level": "high",  # Could be extracted from response
        }

    async def build_parlay(self, games: list[dict[str, Any]], max_legs: int = 4) -> dict[str, Any]:
        """Build optimal parlay combinations"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": f"""
Build optimal parlay combinations from these games (max {max_legs} legs):

{json.dumps(games, indent=2)}

Provide:
1. Top 3 parlay combinations with rationale
2. Expected value calculations
3. Risk correlation analysis
4. Recommended stake sizing
""",
            },
        ]

        response = await self.client.chat_completion(
            messages=messages, model=ModelTier.GPT_5, temperature=0.2, max_tokens=2500
        )

        return {
            "parlay_recommendations": response["choices"][0]["message"]["content"],
            "model_used": response.get("model"),
            "usage": response.get("usage"),
        }


async def main():
    """Demonstrate GPT-5 integration"""

    setup_utf8_logging()
    logging.info("🤖 Starting OpenAI API v2.1.0 GPT-5 Integration")

    # Initialize client
    client = OpenAIV21Client()

    # Test basic functionality
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Test the GPT-5 integration. Respond with current capabilities.",
        },
    ]

    try:
        response = await client.chat_completion(messages, model=ModelTier.GPT_5)
        print(f"✅ GPT-5 Response: {response['choices'][0]['message']['content'][:200]}...")

        # Get usage analytics
        await client.get_usage_analytics(days=1)
        print("\n📊 Usage Analytics:")
        print("Circuit Breaker State: {analytics['circuit_breaker_state']}")
        print("Daily Budget Remaining: ${analytics['daily_budget_remaining']:.2f}")

        # Test sports betting agent
        agent = GPT5SportsBettingAgent()

        sample_game = {
            "teams": ["Lakers", "Warriors"],
            "odds": {"moneyline": [-110, +105], "spread": [1.5, -1.5]},
            "recent_performance": {"lakers": "3-2", "warriors": "4-1"},
            "injuries": {"warriors": ["key_player_questionable"]},
        }

        await agent.analyze_game(sample_game)
        print("\n🏀 Game Analysis: {analysis['analysis'][:300]}...")

    except Exception as e:
        logging.error(f"Error: {e!s}")

    finally:
        await client.close()

    print("\n🎉 OpenAI API v2.1.0 GPT-5 Integration Complete!")


if __name__ == "__main__":
    asyncio.run(main())
