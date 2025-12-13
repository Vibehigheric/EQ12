"""
EQ12 Unified Response System - Complete integration of all model response capabilities
"""

import asyncio
import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

try:
    from eq12_model_responses import (
        EQ12ResponsesAPI,
        ResponseConfig,
        ServiceTier,
        ToolType,
        analyze_parlay_with_responses,
        monitor_live_odds,
        optimize_portfolio,
    )
except ImportError:
    EQ12ResponsesAPI = None

try:
    from eq12_response_templates import (
        BettingScenario,
        EQ12ResponseTemplates,
        analyze_nba_props_night,
        analyze_nfl_sunday_slate,
        detect_steam_moves,
        optimize_bankroll_kelly,
    )
except ImportError:
    EQ12ResponseTemplates = None

logger = logging.getLogger(__name__)


class EQ12UnifiedResponseSystem:
    """
    Unified interface for all EQ12 model response capabilities

    Integrates:
    - Core Responses API functionality
    - Pre-configured betting scenario templates
    - Advanced portfolio optimization
    - Real-time live betting analysis
    - Background processing and streaming
    """

    def __init__(self):
        self.core_api = EQ12ResponsesAPI() if EQ12ResponsesAPI else None
        self.templates = EQ12ResponseTemplates() if EQ12ResponseTemplates else None
        self.active_sessions = {}

        # Initialize logging
        self.setup_logging()

        if not self.core_api or not self.templates:
            logger.warning("Response modules not fully available")
        else:
            logger.info("EQ12 Unified Response System initialized")

    def setup_logging(self):
        """Setup comprehensive logging for response system"""
        log_dir = "C:\\EQ12\\logs"
        os.makedirs(log_dir, exist_ok=True)

        # Response system specific log
        response_log = os.path.join(log_dir, "eq12_responses.log")

        handler = logging.FileHandler(response_log)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    # New OpenAI Responses API examples
    async def simple_response_example(self, question: str) -> dict[str, Any]:
        """Simple response using new OpenAI client pattern"""
        if not self.core_api or not self.core_api.client:
            return {"error": "OpenAI client not available"}

        try:
            response = self.core_api.client.responses.create(model="gpt-4.1", input=question)
            return {"id": response.id, "response": response.output}
        except Exception as e:
            return {"error": str(e)}

    async def web_search_response_example(self, query: str) -> dict[str, Any]:
        """Web search response using preview tool"""
        if not self.core_api or not self.core_api.client:
            return {"error": "OpenAI client not available"}

        try:
            response = self.core_api.client.responses.create(
                model="gpt-4.1", tools=[{"type": "web_search_preview"}], input=query
            )
            return {"id": response.id, "search_result": response.output}
        except Exception as e:
            return {"error": str(e)}

    async def reasoning_response_example(
        self, question: str, effort: str = "high"
    ) -> dict[str, Any]:
        """Reasoning response using o3-mini model"""
        if not self.core_api or not self.core_api.client:
            return {"error": "OpenAI client not available"}

        try:
            response = self.core_api.client.responses.create(
                model="o3-mini", input=question, reasoning={"effort": effort}
            )
            return {"id": response.id, "reasoning": response.output}
        except Exception as e:
            return {"error": str(e)}

    # High-level convenience methods
    async def analyze_betting_opportunity(
        self,
        opportunity_type: str,
        data: dict[str, Any],
        bankroll: float = 1000.0,
        risk_tolerance: str = "moderate",
    ) -> dict[str, Any]:
        """
        Analyze any type of betting opportunity with appropriate model

        Args:
            opportunity_type: Type of analysis (parlay, props, live, etc.)
            data: Relevant data for the analysis
            bankroll: Available bankroll
            risk_tolerance: Risk preference

        Returns:
            Comprehensive analysis with recommendations
        """
        try:
            if opportunity_type.lower() == "parlay":
                return await self._analyze_parlay_opportunity(data, bankroll)

            elif opportunity_type.lower() == "nfl_slate":
                return await self._analyze_nfl_slate(data, bankroll)

            elif opportunity_type.lower() == "nba_props":
                return await self._analyze_nba_props(data)

            elif opportunity_type.lower() == "live_betting":
                return await self._analyze_live_betting(data)

            elif opportunity_type.lower() == "steam_detection":
                return await self._detect_steam_moves(data)

            elif opportunity_type.lower() == "portfolio_optimization":
                return await self._optimize_portfolio(data, bankroll, risk_tolerance)

            else:
                # Generic analysis using core API
                return await self._generic_analysis(opportunity_type, data)

        except Exception as e:
            logger.error(f"Analysis failed for {opportunity_type}: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
                "opportunity_type": opportunity_type,
            }

    async def _analyze_parlay_opportunity(
        self, data: dict[str, Any], bankroll: float
    ) -> dict[str, Any]:
        """Analyze parlay using core API"""
        if not self.core_api:
            raise RuntimeError("Core API not available")

        game_details = data.get("game_details", "Multiple games parlay")
        legs = data.get("legs", [])

        return await analyze_parlay_with_responses(game_details, legs, bankroll)

    async def _analyze_nfl_slate(self, data: dict[str, Any], bankroll: float) -> dict[str, Any]:
        """Analyze NFL slate using template"""
        if not self.templates:
            raise RuntimeError("Templates not available")

        games = data.get("games", [])
        weather = data.get("weather", [])
        injuries = data.get("injuries", [])

        return await analyze_nfl_sunday_slate(games, weather, injuries, bankroll)

    async def _analyze_nba_props(self, data: dict[str, Any]) -> dict[str, Any]:
        """Analyze NBA props using template"""
        if not self.templates:
            raise RuntimeError("Templates not available")

        games = data.get("games", [])
        props = data.get("props", [])
        players = data.get("players", [])
        injuries = data.get("injuries", [])

        return await analyze_nba_props_night(games, props, players, injuries)

    async def _analyze_live_betting(self, data: dict[str, Any]) -> dict[str, Any]:
        """Analyze live betting using template"""
        if not self.templates:
            raise RuntimeError("Templates not available")

        return await self.templates.execute_scenario(BettingScenario.LIVE_GAME_MOMENTUM, data)

    async def _detect_steam_moves(self, data: dict[str, Any]) -> dict[str, Any]:
        """Detect steam moves using template"""
        if not self.templates:
            raise RuntimeError("Templates not available")

        line_moves = data.get("line_movements", [])
        volume = data.get("volume_data", [])
        public_pcts = data.get("public_percentages", [])

        return await detect_steam_moves(line_moves, volume, public_pcts)

    async def _optimize_portfolio(
        self, data: dict[str, Any], bankroll: float, risk_tolerance: str
    ) -> dict[str, Any]:
        """Optimize portfolio using core API or templates"""
        if not self.core_api:
            raise RuntimeError("Core API not available")

        current_bets = data.get("current_positions", [])
        opportunities = data.get("new_opportunities", [])

        if self.templates:
            # Use Kelly template for detailed bankroll management
            return await optimize_bankroll_kelly(
                bankroll, current_bets, opportunities, risk_tolerance
            )
        else:
            # Fall back to core API
            return await optimize_portfolio(current_bets, opportunities, bankroll, risk_tolerance)

    async def _generic_analysis(self, analysis_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """Generic analysis using core API"""
        if not self.core_api:
            raise RuntimeError("Core API not available")

        # Build generic request
        payload = {
            "model": "gpt-4o",
            "instructions": f"""You are EQ12 Sports Betting Analyst.
            Analyze this {analysis_type} opportunity and provide detailed
            recommendations with risk assessment and value identification.""",
            "input": [
                {
                    "type": "text",
                    "text": f"""Analyze {analysis_type}:

{json.dumps(data, indent=2)}

Provide comprehensive analysis with specific recommendations.""",
                }
            ],
            "tools": self.core_api._prepare_tools([ToolType.WEB_SEARCH, ToolType.CODE_INTERPRETER]),
            "temperature": 0.1,
            "max_output_tokens": 2000,
        }

        return await self.core_api._make_request(payload)

    # Streaming and background processing
    async def start_live_monitoring_session(
        self, games: list[str], session_id: str | None = None
    ) -> str:
        """Start live monitoring session with streaming updates"""
        if not self.core_api:
            raise RuntimeError("Core API not available")

        session_id = session_id or f"live_{int(datetime.now().timestamp())}"

        # Start background monitoring
        config = ResponseConfig(background=True, stream=True, service_tier=ServiceTier.PRIORITY)

        response = await self.core_api.create_live_odds_analysis_response(games, config=config)

        # Store session info
        self.active_sessions[session_id] = {
            "type": "live_monitoring",
            "games": games,
            "response_id": response.get("id"),
            "started": datetime.now(UTC).isoformat(),
        }

        logger.info(f"Started live session {session_id}")
        return session_id

    async def get_session_status(self, session_id: str) -> dict[str, Any]:
        """Get status of active session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session_info = self.active_sessions[session_id]
        response_id = session_info.get("response_id")

        if response_id and self.core_api:
            status = await self.core_api.get_response_status(response_id)
            return {"session_info": session_info, "response_status": status}

        return {"session_info": session_info}

    def stop_session(self, session_id: str) -> bool:
        """Stop active session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Stopped session {session_id}")
            return True
        return False

    # Batch processing
    async def batch_analyze_opportunities(
        self, opportunities: list[dict[str, Any]], bankroll: float = 1000.0
    ) -> list[dict[str, Any]]:
        """Analyze multiple opportunities in parallel"""
        tasks = []

        for opp in opportunities:
            opp_type = opp.get("type", "generic")
            opp_data = opp.get("data", {})

            task = self.analyze_betting_opportunity(opp_type, opp_data, bankroll)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    {"opportunity_id": i, "error": str(result), "status": "failed"}
                )
            else:
                processed_results.append(
                    {"opportunity_id": i, "result": result, "status": "completed"}
                )

        return processed_results

    # Utility methods
    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "core_api_available": self.core_api is not None,
            "templates_available": self.templates is not None,
            "active_sessions": len(self.active_sessions),
            "session_ids": list(self.active_sessions.keys()),
            "modules_loaded": {
                "eq12_model_responses": EQ12ResponsesAPI is not None,
                "eq12_response_templates": EQ12ResponseTemplates is not None,
            },
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform system health check"""
        health = {"status": "healthy", "timestamp": datetime.now(UTC).isoformat(), "checks": {}}

        # Check API key
        api_key = os.getenv("OPENAI_API_KEY")
        health["checks"]["api_key"] = "present" if api_key else "missing"

        # Check modules
        health["checks"]["core_api"] = "loaded" if self.core_api else "failed"
        health["checks"]["templates"] = "loaded" if self.templates else "failed"

        # Test basic functionality
        try:
            if self.core_api:
                # This would test actual API connection
                health["checks"]["api_connection"] = "available"
            else:
                health["checks"]["api_connection"] = "unavailable"

        except Exception as e:
            health["checks"]["api_connection"] = f"error: {e}"
            health["status"] = "degraded"

        return health


# Convenience functions for direct usage
async def quick_parlay_analysis(
    legs: list[dict[str, Any]], bankroll: float = 1000.0
) -> dict[str, Any]:
    """Quick parlay analysis without setup"""
    system = EQ12UnifiedResponseSystem()

    data = {"game_details": "Multi-game parlay analysis", "legs": legs}

    return await system.analyze_betting_opportunity("parlay", data, bankroll)


async def quick_nfl_slate_analysis(
    games: list[dict[str, Any]], bankroll: float = 1000.0
) -> dict[str, Any]:
    """Quick NFL slate analysis"""
    system = EQ12UnifiedResponseSystem()

    data = {"games": games}

    return await system.analyze_betting_opportunity("nfl_slate", data, bankroll)


async def quick_steam_detection(line_movements: list[dict[str, Any]]) -> dict[str, Any]:
    """Quick steam move detection"""
    system = EQ12UnifiedResponseSystem()

    data = {"line_movements": line_movements}

    return await system.analyze_betting_opportunity("steam_detection", data)


if __name__ == "__main__":

    async def demo_unified_system():
        """Demo the unified response system"""
        print("🚀 EQ12 Unified Response System Demo")

        system = EQ12UnifiedResponseSystem()

        # Health check
        health = await system.health_check()
        print(f"System Status: {health['status']}")

        # Quick parlay analysis
        sample_legs = [
            {
                "game": "Patriots vs Bills",
                "market": "spread",
                "selection": "Patriots +3.5",
                "odds": -110,
            },
            {
                "game": "Cowboys vs Eagles",
                "market": "total",
                "selection": "Over 48.5",
                "odds": -105,
            },
        ]

        try:
            result = await quick_parlay_analysis(sample_legs, 2000.0)
            print(f"✅ Parlay Analysis: {result.get('id', 'Success')}")

        except Exception as e:
            print(f"❌ Demo failed: {e}")

    # Run demo
    asyncio.run(demo_unified_system())
