#!/usr/bin/env python3
"""
EQ12 Parlay API - Simplified Demo Version
Demonstrates the API functionality without complex ML imports.
"""

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    logger.warning("FastAPI dependencies not available - running in demo mode")


# Pydantic models for API
class ParlayRequest(BaseModel):
    """Request model for parlay suggestions."""

    sport: str = "NFL"
    max_legs: int = 3
    budget: float = 25.0
    risk_tolerance: str = "moderate"
    min_win_probability: float = 0.35
    min_expected_value: float = 0.15


class ParlayLeg(BaseModel):
    """Individual parlay leg."""

    team: str
    line: str
    odds: int
    probability: float


class ParlayResponse(BaseModel):
    """Response model for parlay suggestions."""

    request_id: str
    timestamp: str
    sport: str
    suggestions: list[dict]
    risk_parameters: dict
    reasoning: str


# Simplified ML prediction simulator
class MLPredictor:
    """Simplified ML predictor for demonstration."""

    def __init__(self):
        self.model_loaded = True
        logger.info("ML Predictor initialized (demo mode)")

    def predict_parlay_probability(self, legs: list[str]) -> float:
        """Simulate ML-enhanced probability prediction."""
        # Base implied probability from odds
        base_prob = 0.14  # ~+600 odds

        # ML enhancement based on number of legs (simulate model learning)
        if len(legs) == 2:
            enhancement = 0.28  # 2-leg safer
        elif len(legs) == 3:
            enhancement = 0.18  # 3-leg moderate
        else:
            enhancement = 0.08  # 4+ legs riskier

        return min(base_prob + enhancement, 0.55)  # Cap at 55%

    def calculate_expected_value(
        self, probability: float, odds_american: int, stake: float
    ) -> float:
        """Calculate expected value."""
        if odds_american > 0:
            decimal_odds = (odds_american / 100) + 1
        else:
            decimal_odds = (100 / abs(odds_american)) + 1

        payout = stake * (decimal_odds - 1)
        ev = (probability * payout) - ((1 - probability) * stake)
        return ev

    def kelly_fraction(self, probability: float, odds_american: int) -> float:
        """Calculate Kelly Criterion fraction."""
        b = odds_american / 100 if odds_american > 0 else 100 / abs(odds_american)

        q = 1 - probability
        kelly = (b * probability - q) / b
        return max(0, min(kelly, 0.25))  # Cap at 25%


# Risk Manager
class RiskManager:
    """Comprehensive risk management."""

    def __init__(self):
        self.max_legs = 4
        self.min_win_probability = 0.35
        self.min_expected_value = 0.15
        self.max_kelly_fraction = 0.25

    def assess_risk(self, legs: list[str], probability: float, ev_pct: float, kelly: float) -> dict:
        """Assess parlay risk."""
        checks = {
            "leg_count": len(legs) <= self.max_legs,
            "win_probability": probability >= self.min_win_probability,
            "expected_value": ev_pct >= self.min_expected_value,
            "kelly_criterion": kelly <= self.max_kelly_fraction,
        }

        return {
            "approved": all(checks.values()),
            "checks": checks,
            "risk_level": "LOW" if all(checks.values()) else "HIGH",
        }


# Sample data generator
class SampleDataGenerator:
    """Generate sample NFL parlay suggestions."""

    def __init__(self):
        self.nfl_games = [
            {"home": "KC", "away": "DEN", "spread": -7.0, "total": 45.5},
            {"home": "DAL", "away": "NYG", "spread": -3.5, "total": 47.0},
            {"home": "BUF", "away": "MIA", "spread": -6.0, "total": 50.5},
            {"home": "SF", "away": "LAR", "spread": -2.5, "total": 48.0},
        ]

    def generate_legs(self, max_legs: int = 3) -> list[str]:
        """Generate sample parlay legs."""
        legs = []
        for i, game in enumerate(self.nfl_games[:max_legs]):
            if i % 2 == 0:
                legs.append(f"{game['home']} {game['spread']:+.1f} (-110)")
            else:
                legs.append(f"Over {game['total']} (-110)")
        return legs


# Main API application
if DEPENDENCIES_AVAILABLE:
    app = FastAPI(
        title="EQ12 Parlay API", description="ML-Enhanced Parlay Suggestion System", version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize components
    ml_predictor = MLPredictor()
    risk_manager = RiskManager()
    data_generator = SampleDataGenerator()

    @app.get("/")
    async def root():
        """API root endpoint."""
        return {
            "message": "EQ12 Parlay API - ML Enhanced Betting System",
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "endpoints": ["/model/suggest", "/analytics/performance", "/health", "/docs"],
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "ml_model": "loaded",
            "risk_manager": "active",
            "timestamp": datetime.now().isoformat(),
        }

    @app.post("/model/suggest", response_model=ParlayResponse)
    async def suggest_parlay(request: ParlayRequest):
        """Generate ML-enhanced parlay suggestions."""
        try:
            # Generate sample legs
            legs = data_generator.generate_legs(request.max_legs)

            # ML prediction
            probability = ml_predictor.predict_parlay_probability(legs)

            # Calculate odds (assume +260 for 2-leg, +595 for 3-leg)
            odds_map = {2: 260, 3: 595, 4: 1200}
            odds_american = odds_map.get(len(legs), 595)

            # Calculate metrics
            ev = ml_predictor.calculate_expected_value(probability, odds_american, request.budget)
            ev_pct = ev / request.budget
            kelly = ml_predictor.kelly_fraction(probability, odds_american)

            # Risk assessment
            risk_assessment = risk_manager.assess_risk(legs, probability, ev_pct, kelly)

            # Build response
            suggestion = {
                "legs": legs,
                "total_odds_american": odds_american,
                "win_probability": probability,
                "expected_value": ev_pct,
                "kelly_fraction": kelly,
                "confidence_score": 0.78,
                "max_stake": kelly * 1000,  # For $1000 bankroll
                "potential_payout": request.budget
                * (odds_american / 100 if odds_american > 0 else 100 / abs(odds_american)),
                "reasoning": f"{len(legs)}-leg {request.sport} parlay with {probability:.1%} win probability and {ev_pct:+.1%} EV",
                "risk_assessment": risk_assessment,
            }

            response = ParlayResponse(
                request_id=f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_0001",
                timestamp=datetime.now().isoformat(),
                sport=request.sport,
                suggestions=[suggestion],
                risk_parameters={
                    "min_win_probability": risk_manager.min_win_probability,
                    "min_expected_value": risk_manager.min_expected_value,
                    "max_kelly_fraction": risk_manager.max_kelly_fraction,
                },
                reasoning="ML-enhanced prediction with mathematical risk controls",
            )

            # Log the suggestion
            logger.info(
                f"Generated parlay suggestion: {probability:.1%} win prob, {ev_pct:+.1%} EV"
            )

            return response

        except Exception as e:
            logger.error(f"Error generating suggestion: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/analytics/performance")
    async def get_performance():
        """Get system performance analytics."""
        return {
            "baseline_metrics": {
                "total_parlays_analyzed": 958,
                "baseline_win_rate": 0.0298,
                "nfl_win_rate": 0.0,
                "total_wagered": 5220.0,
            },
            "ml_enhanced_metrics": {
                "target_win_rate": "35-45%",
                "expected_value_improvement": "+15% minimum",
                "risk_controls": "Kelly + correlation + position limits",
                "model_status": "operational",
            },
            "recent_performance": {
                "suggestions_generated": 47,
                "avg_win_probability": 0.38,
                "avg_expected_value": 0.21,
                "risk_approvals": 0.89,
            },
            "timestamp": datetime.now().isoformat(),
        }


def run_demo():
    """Run demonstration without FastAPI server."""
    print("🚀 EQ12 PARLAY API DEMONSTRATION")
    print("=" * 50)

    # Initialize components
    predictor = MLPredictor()
    risk_mgr = RiskManager()
    generator = SampleDataGenerator()

    # Generate sample suggestion
    legs = generator.generate_legs(3)
    probability = predictor.predict_parlay_probability(legs)

    print("\n📊 Sample ML Parlay Suggestion:")
    print(f"   Legs: {legs}")
    print(f"   ML Win Probability: {probability:.1%}")
    print(f"   Expected Value: {(probability * 148.75 - (1 - probability) * 25) / 25:+.1%}")
    print(f"   Kelly Fraction: {predictor.kelly_fraction(probability, 595):.2%}")

    # Risk assessment
    ev_pct = (probability * 148.75 - (1 - probability) * 25) / 25
    kelly = predictor.kelly_fraction(probability, 595)
    risk = risk_mgr.assess_risk(legs, probability, ev_pct, kelly)

    print("\n🛡️ Risk Assessment:")
    for check, passed in risk["checks"].items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check.replace('_', ' ').title()}: {passed}")
    print(f"   Overall: {'🟢 APPROVED' if risk['approved'] else '🔴 REJECTED'}")

    print("\n✅ Demo completed - API system operational!")


def main():
    """Main execution."""
    if DEPENDENCIES_AVAILABLE:
        print("🚀 Starting EQ12 Parlay API Server...")
        print("📡 Server will be available at: http://127.0.0.1:8000")
        print("📋 Documentation at: http://127.0.0.1:8000/docs")
        print("🛑 Press Ctrl+C to stop server")

        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    else:
        print("⚠️  FastAPI not available - running demo mode")
        run_demo()


if __name__ == "__main__":
    main()
