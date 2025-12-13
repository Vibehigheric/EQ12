"""
EQ12 Parlay API Server
FastAPI server for ML-driven parlay suggestions with risk management.

Provides RESTful endpoints for intelligent parlay generation and analysis.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import asyncio
from contextlib import asynccontextmanager

# EQ12 imports
from builder import (IntelligentParlayBuilder, ParlayRecommendation, 
                    BetLeg, RiskManager, MockBettingDataProvider)

# Logging setup
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(
            log_dir / f"parlay_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global state
parlay_builder: Optional[IntelligentParlayBuilder] = None
request_counter = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup for FastAPI app."""
    global parlay_builder
    
    # Startup
    logger.info("🚀 Starting EQ12 Parlay API Server...")
    
    # Initialize parlay builder
    model_path = "C:/EQ12/eq12_learn/parlay_ensemble_model.pkl"
    parlay_builder = IntelligentParlayBuilder(
        model_path=model_path if Path(model_path).exists() else None
    )
    
    logger.info("✅ Parlay builder initialized")
    yield
    
    # Shutdown
    logger.info("👋 Shutting down EQ12 Parlay API Server")


# FastAPI app
app = FastAPI(
    title="EQ12 Intelligent Parlay API",
    description="ML-driven parlay suggestions with mathematical risk management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API
class ParlayRequest(BaseModel):
    """Request model for parlay suggestions."""
    sport: str = Field(..., description="Sport (NFL, NBA, MLB, etc.)")
    max_legs: int = Field(default=3, ge=2, le=4, description="Maximum parlay legs")
    budget: float = Field(default=25.0, ge=5.0, le=100.0, 
                         description="Maximum stake amount")
    risk_tolerance: str = Field(default="moderate", 
                               description="Risk level: conservative, moderate, aggressive")
    min_win_probability: Optional[float] = Field(
        default=None, ge=0.1, le=0.9,
        description="Minimum win probability (overrides defaults)"
    )
    min_expected_value: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Minimum expected value percentage"
    )
    
    @validator('sport')
    def validate_sport(cls, v):
        allowed_sports = ['NFL', 'NBA', 'MLB', 'NHL', 'NCAAF', 'NCAAB']
        if v.upper() not in allowed_sports:
            raise ValueError(f'Sport must be one of {allowed_sports}')
        return v.upper()
    
    @validator('risk_tolerance')
    def validate_risk_tolerance(cls, v):
        allowed = ['conservative', 'moderate', 'aggressive']
        if v.lower() not in allowed:
            raise ValueError(f'Risk tolerance must be one of {allowed}')
        return v.lower()


class BetLegResponse(BaseModel):
    """Response model for individual bet legs."""
    team: str
    opponent: str
    bet_type: str
    line: float
    odds_american: int
    sport: str
    confidence: float


class ParlayResponse(BaseModel):
    """Response model for parlay recommendations."""
    legs: List[BetLegResponse]
    total_odds_american: int
    win_probability: float
    expected_value: float
    kelly_fraction: float
    confidence_score: float
    risk_score: float
    correlation_warning: bool
    reasoning: str
    max_stake: float
    potential_payout: float
    leg_count: int


class SuggestionsResponse(BaseModel):
    """Response model for multiple parlay suggestions."""
    request_id: str
    timestamp: datetime
    sport: str
    suggestions: List[ParlayResponse]
    risk_parameters: Dict
    performance_summary: Dict


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    model_loaded: bool
    total_requests: int


class PerformanceRequest(BaseModel):
    """Request model for performance tracking."""
    parlay_id: str
    actual_outcome: str  # 'win', 'loss', 'pending'
    actual_payout: Optional[float] = None
    notes: Optional[str] = None


# Rate limiting and dependencies
async def rate_limit():
    """Simple rate limiting (can be enhanced with Redis)."""
    global request_counter
    request_counter += 1
    
    # Basic rate limiting (100 requests per minute)
    if request_counter > 100:
        raise HTTPException(
            status_code=429, 
            detail="Rate limit exceeded. Try again later."
        )


async def get_parlay_builder() -> IntelligentParlayBuilder:
    """Dependency to get parlay builder instance."""
    if parlay_builder is None:
        raise HTTPException(
            status_code=500,
            detail="Parlay builder not initialized"
        )
    return parlay_builder


# API endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with service information."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        model_loaded=parlay_builder is not None,
        total_requests=request_counter
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy" if parlay_builder is not None else "unhealthy",
        timestamp=datetime.now(),
        version="1.0.0",
        model_loaded=parlay_builder is not None,
        total_requests=request_counter
    )


@app.post("/model/suggest", response_model=SuggestionsResponse)
async def suggest_parlays(
    request: ParlayRequest,
    background_tasks: BackgroundTasks,
    _: None = Depends(rate_limit),
    builder: IntelligentParlayBuilder = Depends(get_parlay_builder)
):
    """Generate intelligent parlay suggestions."""
    request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request_counter:04d}"
    
    logger.info(f"Processing parlay request {request_id}: {request.sport}, "
                f"max_legs={request.max_legs}, budget=${request.budget}")
    
    try:
        # Adjust risk parameters based on request
        original_params = {}
        if request.risk_tolerance == "conservative":
            original_params['min_win_prob'] = builder.risk_manager.MIN_WIN_PROBABILITY
            original_params['min_ev'] = builder.risk_manager.MIN_EXPECTED_VALUE
            builder.risk_manager.MIN_WIN_PROBABILITY = 0.45
            builder.risk_manager.MIN_EXPECTED_VALUE = 0.20
            
        elif request.risk_tolerance == "aggressive":
            original_params['min_win_prob'] = builder.risk_manager.MIN_WIN_PROBABILITY
            original_params['min_ev'] = builder.risk_manager.MIN_EXPECTED_VALUE
            builder.risk_manager.MIN_WIN_PROBABILITY = 0.25
            builder.risk_manager.MIN_EXPECTED_VALUE = 0.10
            
        # Override with specific request parameters
        if request.min_win_probability is not None:
            original_params['min_win_prob'] = builder.risk_manager.MIN_WIN_PROBABILITY
            builder.risk_manager.MIN_WIN_PROBABILITY = request.min_win_probability
            
        if request.min_expected_value is not None:
            original_params['min_ev'] = builder.risk_manager.MIN_EXPECTED_VALUE
            builder.risk_manager.MIN_EXPECTED_VALUE = request.min_expected_value
        
        # Generate suggestions
        suggestions = builder.generate_suggestions(
            sport=request.sport,
            max_suggestions=3
        )
        
        # Restore original parameters
        for key, value in original_params.items():
            if key == 'min_win_prob':
                builder.risk_manager.MIN_WIN_PROBABILITY = value
            elif key == 'min_ev':
                builder.risk_manager.MIN_EXPECTED_VALUE = value
        
        # Convert to response format
        response_suggestions = []
        for suggestion in suggestions:
            # Adjust max stake based on budget
            adjusted_stake = min(suggestion.max_stake, request.budget)
            
            response_legs = [
                BetLegResponse(
                    team=leg.team,
                    opponent=leg.opponent,
                    bet_type=leg.bet_type,
                    line=leg.line,
                    odds_american=leg.odds_american,
                    sport=leg.sport,
                    confidence=leg.confidence
                ) for leg in suggestion.legs
            ]
            
            response_suggestions.append(ParlayResponse(
                legs=response_legs,
                total_odds_american=suggestion.total_odds_american,
                win_probability=suggestion.win_probability,
                expected_value=suggestion.expected_value,
                kelly_fraction=suggestion.kelly_fraction,
                confidence_score=suggestion.confidence_score,
                risk_score=suggestion.risk_score,
                correlation_warning=suggestion.correlation_warning,
                reasoning=suggestion.reasoning,
                max_stake=adjusted_stake,
                potential_payout=suggestion.potential_payout * (adjusted_stake / suggestion.max_stake),
                leg_count=suggestion.leg_count
            ))
        
        # Performance summary
        if suggestions:
            avg_win_prob = sum(s.win_probability for s in suggestions) / len(suggestions)
            avg_ev = sum(s.expected_value for s in suggestions) / len(suggestions)
            avg_confidence = sum(s.confidence_score for s in suggestions) / len(suggestions)
        else:
            avg_win_prob = avg_ev = avg_confidence = 0.0
        
        performance_summary = {
            'suggestions_generated': len(suggestions),
            'average_win_probability': avg_win_prob,
            'average_expected_value': avg_ev,
            'average_confidence': avg_confidence,
            'risk_tolerance': request.risk_tolerance
        }
        
        # Risk parameters used
        risk_parameters = {
            'min_win_probability': builder.risk_manager.MIN_WIN_PROBABILITY,
            'min_expected_value': builder.risk_manager.MIN_EXPECTED_VALUE,
            'max_correlation_score': builder.risk_manager.MAX_CORRELATION_SCORE,
            'max_kelly_fraction': builder.risk_manager.MAX_KELLY_FRACTION,
            'max_legs': request.max_legs
        }
        
        # Background task: save suggestions
        if suggestions:
            background_tasks.add_task(
                save_suggestions_background,
                suggestions, request_id
            )
        
        response = SuggestionsResponse(
            request_id=request_id,
            timestamp=datetime.now(),
            sport=request.sport,
            suggestions=response_suggestions,
            risk_parameters=risk_parameters,
            performance_summary=performance_summary
        )
        
        logger.info(f"Generated {len(suggestions)} suggestions for request {request_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing request {request_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/model/feedback")
async def submit_feedback(
    feedback: PerformanceRequest,
    builder: IntelligentParlayBuilder = Depends(get_parlay_builder)
):
    """Submit feedback on parlay performance for model improvement."""
    logger.info(f"Received feedback for parlay {feedback.parlay_id}: {feedback.actual_outcome}")
    
    try:
        # Save feedback for model retraining
        feedback_data = {
            'timestamp': datetime.now().isoformat(),
            'parlay_id': feedback.parlay_id,
            'actual_outcome': feedback.actual_outcome,
            'actual_payout': feedback.actual_payout,
            'notes': feedback.notes
        }
        
        feedback_file = log_dir / "parlay_feedback.jsonl"
        with open(feedback_file, 'a') as f:
            f.write(json.dumps(feedback_data) + '\n')
        
        return {"status": "success", "message": "Feedback recorded for model improvement"}
        
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to record feedback")


@app.get("/analytics/performance")
async def get_performance_analytics():
    """Get performance analytics for the parlay suggestion system."""
    try:
        # Read feedback data
        feedback_file = log_dir / "parlay_feedback.jsonl"
        
        if not feedback_file.exists():
            return {
                "total_feedback": 0,
                "win_rate": 0.0,
                "avg_payout": 0.0,
                "message": "No feedback data available"
            }
        
        feedback_data = []
        with open(feedback_file, 'r') as f:
            for line in f:
                feedback_data.append(json.loads(line.strip()))
        
        # Calculate analytics
        total_feedback = len(feedback_data)
        wins = sum(1 for fb in feedback_data if fb['actual_outcome'] == 'win')
        total_payouts = sum(fb.get('actual_payout', 0) or 0 for fb in feedback_data)
        
        analytics = {
            "total_feedback": total_feedback,
            "win_rate": wins / total_feedback if total_feedback > 0 else 0.0,
            "total_wins": wins,
            "total_losses": sum(1 for fb in feedback_data if fb['actual_outcome'] == 'loss'),
            "avg_payout": total_payouts / wins if wins > 0 else 0.0,
            "feedback_period_days": 30  # Could calculate actual period
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error calculating analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate analytics")


@app.get("/model/status")
async def model_status(builder: IntelligentParlayBuilder = Depends(get_parlay_builder)):
    """Get current model status and configuration."""
    return {
        "model_loaded": builder.model is not None,
        "risk_parameters": {
            "min_win_probability": builder.risk_manager.MIN_WIN_PROBABILITY,
            "min_expected_value": builder.risk_manager.MIN_EXPECTED_VALUE,
            "max_correlation_score": builder.risk_manager.MAX_CORRELATION_SCORE,
            "max_kelly_fraction": builder.risk_manager.MAX_KELLY_FRACTION,
            "max_legs": builder.risk_manager.MAX_LEGS
        },
        "suggestions_made_today": len(builder.suggestions_made),
        "api_version": "1.0.0",
        "server_time": datetime.now().isoformat()
    }


# Background tasks
async def save_suggestions_background(suggestions: List[ParlayRecommendation], 
                                    request_id: str):
    """Background task to save suggestions to file."""
    try:
        filename = f"C:/EQ12/logs/api_suggestions_{request_id}.json"
        
        suggestions_data = {
            'request_id': request_id,
            'generation_timestamp': datetime.now().isoformat(),
            'suggestions_count': len(suggestions),
            'suggestions': [s.to_dict() for s in suggestions]
        }
        
        with open(filename, 'w') as f:
            json.dump(suggestions_data, f, indent=2, default=str)
            
        logger.info(f"Background: Saved suggestions to {filename}")
        
    except Exception as e:
        logger.error(f"Background task error: {e}")


# Reset rate limiter periodically
@app.on_event("startup")
async def setup_periodic_tasks():
    """Setup periodic background tasks."""
    async def reset_rate_limit():
        global request_counter
        while True:
            await asyncio.sleep(60)  # Reset every minute
            request_counter = 0
    
    asyncio.create_task(reset_rate_limit())


def run_server(host: str = "127.0.0.1", port: int = 8000, 
               reload: bool = False):
    """Run the FastAPI server."""
    logger.info(f"Starting EQ12 Parlay API on {host}:{port}")
    
    uvicorn.run(
        "eq12_parlay_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='EQ12 Parlay API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', 
                       help='Enable auto-reload for development')
    
    args = parser.parse_args()
    
    run_server(host=args.host, port=args.port, reload=args.reload)