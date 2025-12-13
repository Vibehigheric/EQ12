#!/usr/bin/env python3
"""
EQ12 Bankroll & Compliance Copilot - AI-Powered Risk Management & Legal Compliance
================================================================================

Comprehensive bankroll management and legal compliance system:
- AI-powered bankroll optimization with Kelly Criterion
- State-by-state legal compliance monitoring
- Sportsbook terms and restrictions tracking
- Risk management alerts and interventions
- Responsible gambling tools and safeguards
- Automated compliance reporting

Revenue Streams:
- Professional bankroll management: $99/month
- Compliance consulting: $299/month per operator
- Risk management tools: $49/month per bettor
- B2B compliance API: $999/month + usage
- Legal monitoring service: $199/month
- Responsible gambling certification: $499/month

AI Features:
- Real-time risk assessment with ML models
- Behavioral pattern analysis for problem gambling
- Automated compliance alerts and recommendations
- Dynamic bet sizing optimization
- Legal change monitoring with impact analysis
- Personalized responsible gambling interventions

Author: EQ12 Development Team
Version: 2.0.0
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression

# Import EQ12 components
from eq12_openai_security import EQ12OpenAISecurityManager
from eq12_sports_betting_engine import EQ12BettingEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class BankrollProfile:
    """User bankroll profile"""

    user_id: str
    total_bankroll: float
    risk_tolerance: str  # conservative, moderate, aggressive
    max_bet_size: float
    daily_limit: float
    monthly_limit: float
    kelly_multiplier: float = 0.25  # Quarter Kelly default
    stop_loss_percent: float = 0.20  # Stop at 20% loss
    profit_target_percent: float = 0.50  # Take profits at 50% gain
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class BettingSession:
    """Individual betting session tracking"""

    session_id: str
    user_id: str
    start_time: datetime
    end_time: datetime | None
    starting_bankroll: float
    current_bankroll: float
    total_wagered: float
    total_won: float
    bet_count: int
    largest_bet: float
    longest_streak: int
    risk_score: float = 0.0


@dataclass
class ComplianceRule:
    """Legal compliance rule"""

    rule_id: str
    jurisdiction: str  # state/country code
    rule_type: str  # age_limit, bet_limits, operator_requirements
    description: str
    penalty: str
    effective_date: datetime
    source: str  # regulatory body
    active: bool = True


@dataclass
class RiskAlert:
    """Risk management alert"""

    alert_id: str
    user_id: str
    alert_type: str  # spending, behavior, legal, technical
    severity: str  # low, medium, high, critical
    description: str
    recommended_action: str
    triggered_at: datetime
    resolved_at: datetime | None = None


class EQ12BankrollComplianceCopilot:
    """AI-powered bankroll management and compliance system"""

    def __init__(self):
        # Core components
        self.openai_manager = EQ12OpenAISecurityManager("compliance_copilot")
        self.betting_engine = EQ12BettingEngine()

        # Database
        self.db_path = "C:/EQ12/logs/compliance_copilot.db"

        # ML models for risk detection
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.problem_gambling_model = LogisticRegression(random_state=42)

        # Compliance databases
        self.state_rules = {}
        self.sportsbook_terms = {}

        # Risk thresholds
        self.risk_thresholds = {
            "max_session_hours": 8,
            "max_daily_loss_percent": 0.05,  # 5% of bankroll
            "max_bet_size_percent": 0.10,  # 10% of bankroll
            "chasing_threshold": 3,  # 3 consecutive losses followed by size increase
            "velocity_threshold": 10,  # 10 bets per hour
        }

        # Pricing
        self.pricing = {
            "bankroll_management": 99.00,
            "compliance_consulting": 299.00,
            "risk_management": 49.00,
            "b2b_api": 999.00,
            "legal_monitoring": 199.00,
            "certification": 499.00,
        }

        # Revenue tracking
        self.revenue_stats = {
            "monthly_subscribers": 0,
            "total_revenue": 0.0,
            "compliance_clients": 0,
            "risk_interventions": 0,
        }

        self.setup_database()
        self.load_compliance_rules()
        self.train_risk_models()

    def setup_database(self):
        """Initialize compliance and bankroll database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Bankroll profiles
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bankroll_profiles (
                user_id TEXT PRIMARY KEY,
                total_bankroll REAL,
                risk_tolerance TEXT,
                max_bet_size REAL,
                daily_limit REAL,
                monthly_limit REAL,
                kelly_multiplier REAL,
                stop_loss_percent REAL,
                profit_target_percent REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Betting sessions
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS betting_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                start_time DATETIME,
                end_time DATETIME,
                starting_bankroll REAL,
                current_bankroll REAL,
                total_wagered REAL,
                total_won REAL,
                bet_count INTEGER,
                largest_bet REAL,
                longest_streak INTEGER,
                risk_score REAL,
                FOREIGN KEY (user_id) REFERENCES bankroll_profiles (user_id)
            )
        """
        )

        # Individual bets tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bet_history (
                bet_id TEXT PRIMARY KEY,
                session_id TEXT,
                user_id TEXT,
                sportsbook TEXT,
                bet_amount REAL,
                odds REAL,
                selection TEXT,
                bet_type TEXT,
                outcome TEXT,
                profit_loss REAL,
                placed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                settled_at DATETIME,
                kelly_suggested REAL,
                kelly_actual REAL,
                FOREIGN KEY (session_id) REFERENCES betting_sessions (session_id)
            )
        """
        )

        # Compliance rules
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS compliance_rules (
                rule_id TEXT PRIMARY KEY,
                jurisdiction TEXT,
                rule_type TEXT,
                description TEXT,
                penalty TEXT,
                effective_date DATETIME,
                source TEXT,
                active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Risk alerts
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS risk_alerts (
                alert_id TEXT PRIMARY KEY,
                user_id TEXT,
                alert_type TEXT,
                severity TEXT,
                description TEXT,
                recommended_action TEXT,
                triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES bankroll_profiles (user_id)
            )
        """
        )

        # Compliance monitoring
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS compliance_monitoring (
                check_id TEXT PRIMARY KEY,
                user_id TEXT,
                jurisdiction TEXT,
                check_type TEXT,
                status TEXT,
                details TEXT,
                checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                next_check DATETIME
            )
        """
        )

        # Revenue tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS compliance_revenue (
                transaction_id TEXT PRIMARY KEY,
                user_id TEXT,
                service_type TEXT,
                amount REAL,
                stripe_payment_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("✅ Compliance copilot database initialized")

    def load_compliance_rules(self):
        """Load state-by-state compliance rules"""

        # Sample compliance rules (in production, would load from regulatory APIs)
        sample_rules = [
            {
                "jurisdiction": "NY",
                "rule_type": "age_limit",
                "description": "Must be 21+ to place sports bets",
                "penalty": "Account suspension, fines up to $1000",
                "source": "NY Gaming Commission",
            },
            {
                "jurisdiction": "NJ",
                "rule_type": "bet_limits",
                "description": "Maximum $1000 per bet for new accounts",
                "penalty": "Bet rejection, account review",
                "source": "NJ Division of Gaming Enforcement",
            },
            {
                "jurisdiction": "PA",
                "rule_type": "responsible_gambling",
                "description": "Mandatory loss limits and session time limits",
                "penalty": "Account restrictions, mandatory cooling off",
                "source": "PA Gaming Control Board",
            },
            {
                "jurisdiction": "federal",
                "rule_type": "anti_money_laundering",
                "description": "Report transactions over $10,000",
                "penalty": "Criminal charges, license revocation",
                "source": "FinCEN",
            },
        ]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for rule in sample_rules:
            rule_id = hashlib.md5(f"{rule['jurisdiction']}{rule['rule_type']}".encode()).hexdigest()
            cursor.execute(
                """
                INSERT OR IGNORE INTO compliance_rules
                (rule_id, jurisdiction, rule_type, description, penalty,
                 effective_date, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    rule_id,
                    rule["jurisdiction"],
                    rule["rule_type"],
                    rule["description"],
                    rule["penalty"],
                    datetime.now(),
                    rule["source"],
                ),
            )

        conn.commit()
        conn.close()

        logger.info("✅ Loaded compliance rules database")

    def train_risk_models(self):
        """Train ML models for risk detection"""

        # Generate synthetic training data for problem gambling detection
        np.random.seed(42)

        # Normal betting patterns
        normal_sessions = []
        for _ in range(500):
            normal_sessions.append(
                [
                    np.random.uniform(1, 6),  # session_hours
                    np.random.uniform(50, 500),  # total_wagered
                    np.random.uniform(5, 50),  # avg_bet_size
                    np.random.uniform(0, 10),  # bet_velocity (bets/hour)
                    np.random.uniform(-0.1, 0.1),  # loss_rate
                    np.random.uniform(0, 2),  # streak_length
                    0,  # label: 0 = normal
                ]
            )

        # Problem gambling patterns
        problem_sessions = []
        for _ in range(100):
            problem_sessions.append(
                [
                    np.random.uniform(6, 15),  # long_sessions
                    np.random.uniform(500, 5000),  # high_wagering
                    np.random.uniform(50, 500),  # large_bets
                    np.random.uniform(10, 30),  # high_velocity
                    np.random.uniform(0.2, 0.8),  # high_loss_rate
                    np.random.uniform(3, 10),  # chasing_streaks
                    1,  # label: 1 = problem
                ]
            )

        # Combine and train
        all_data = normal_sessions + problem_sessions
        X = np.array([[row[i] for i in range(6)] for row in all_data])
        y = np.array([row[6] for row in all_data])

        # Train models
        self.anomaly_detector.fit(X)
        self.problem_gambling_model.fit(X, y)

        logger.info("✅ Risk detection models trained")

    # ==================== BANKROLL MANAGEMENT ====================

    async def create_bankroll_profile(self, user_data: dict[str, Any]) -> BankrollProfile:
        """Create new bankroll management profile"""

        try:
            profile = BankrollProfile(
                user_id=user_data["user_id"],
                total_bankroll=user_data["total_bankroll"],
                risk_tolerance=user_data.get("risk_tolerance", "moderate"),
                max_bet_size=user_data.get("max_bet_size", user_data["total_bankroll"] * 0.05),
                daily_limit=user_data.get("daily_limit", user_data["total_bankroll"] * 0.10),
                monthly_limit=user_data.get("monthly_limit", user_data["total_bankroll"] * 0.50),
                kelly_multiplier=user_data.get("kelly_multiplier", 0.25),
            )

            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO bankroll_profiles
                (user_id, total_bankroll, risk_tolerance, max_bet_size,
                 daily_limit, monthly_limit, kelly_multiplier,
                 stop_loss_percent, profit_target_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    profile.user_id,
                    profile.total_bankroll,
                    profile.risk_tolerance,
                    profile.max_bet_size,
                    profile.daily_limit,
                    profile.monthly_limit,
                    profile.kelly_multiplier,
                    profile.stop_loss_percent,
                    profile.profit_target_percent,
                ),
            )

            conn.commit()
            conn.close()

            logger.info(f"✅ Created bankroll profile for {profile.user_id}")
            return profile

        except Exception as e:
            logger.error(f"Bankroll profile creation error: {e}")
            raise

    async def calculate_optimal_bet_size(
        self, user_id: str, bet_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Calculate optimal bet size using Kelly Criterion and risk management"""

        try:
            # Get user profile
            profile = await self.get_bankroll_profile(user_id)
            if not profile:
                raise ValueError("User profile not found")

            # Extract bet parameters
            odds = bet_data["odds"]
            win_probability = bet_data.get("win_probability")

            # Calculate implied probability if win_probability not provided
            if not win_probability:
                100 / (odds + 100) if odds > 0 else abs(odds) / (abs(odds) + 100)

                # Use AI to estimate true probability
                true_prob = await self.estimate_true_probability(bet_data)
                win_probability = true_prob

            # Kelly Criterion calculation
            decimal_odds = odds / 100 + 1 if odds > 0 else 100 / abs(odds) + 1

            kelly_fraction = (win_probability * decimal_odds - 1) / (decimal_odds - 1)
            kelly_bet = profile.total_bankroll * kelly_fraction * profile.kelly_multiplier

            # Apply risk management constraints
            max_bet = min(
                profile.max_bet_size,
                profile.daily_limit / 5,  # No more than 1/5 of daily limit per bet
                profile.total_bankroll * 0.10,  # Never more than 10% of bankroll
            )

            recommended_bet = max(0, min(kelly_bet, max_bet))

            # Risk assessment
            risk_level = self.assess_bet_risk(profile, bet_data, recommended_bet)

            return {
                "recommended_bet_size": recommended_bet,
                "kelly_fraction": kelly_fraction,
                "max_allowed_bet": max_bet,
                "win_probability": win_probability,
                "expected_value": recommended_bet
                * (win_probability * (decimal_odds - 1) - (1 - win_probability)),
                "risk_level": risk_level,
                "risk_warnings": self.get_risk_warnings(risk_level, bet_data),
            }

        except Exception as e:
            logger.error(f"Bet size calculation error: {e}")
            raise

    async def estimate_true_probability(self, bet_data: dict[str, Any]) -> float:
        """Use AI to estimate true win probability"""

        try:
            prompt = f"""
            Analyze this betting opportunity and estimate the true win probability:

            Selection: {bet_data.get("selection", "N/A")}
            Odds: {bet_data.get("odds", "N/A")}
            Sport: {bet_data.get("sport", "N/A")}
            Market: {bet_data.get("market", "N/A")}
            Context: {bet_data.get("context", "N/A")}

            Consider:
            - Implied probability from odds
            - Historical performance
            - Current form and injuries
            - Market conditions and line movement
            - Public vs sharp money

            Provide your best estimate of true win probability as a decimal (0.0 to 1.0).
            Be conservative and factor in uncertainty.
            """

            response = await self.openai_manager.secure_openai_request(
                "gpt-4o-mini",
                [
                    {
                        "role": "system",
                        "content": "You are a professional sports betting analyst. Provide probability estimates as decimal numbers only (e.g., 0.55 for 55%).",
                    },
                    {"role": "user", "content": prompt},
                ],
                {"max_tokens": 50, "temperature": 0.3},
            )

            # Extract probability from response
            content = response["response"]["choices"][0]["message"]["content"].strip()

            # Parse probability
            import re

            prob_match = re.search(r"0\.\d+", content)
            if prob_match:
                probability = float(prob_match.group())
                return max(0.05, min(0.95, probability))  # Clamp between 5% and 95%
            else:
                # Fallback to implied probability
                odds = bet_data.get("odds", -110)
                if odds > 0:
                    return 100 / (odds + 100)
                else:
                    return abs(odds) / (abs(odds) + 100)

        except Exception as e:
            logger.error(f"Probability estimation error: {e}")
            # Return implied probability as fallback
            odds = bet_data.get("odds", -110)
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)

    def assess_bet_risk(
        self, profile: BankrollProfile, bet_data: dict[str, Any], bet_size: float
    ) -> str:
        """Assess risk level of proposed bet"""

        risk_factors = []

        # Size risk
        size_percent = bet_size / profile.total_bankroll
        if size_percent > 0.10:
            risk_factors.append("high_size")
        elif size_percent > 0.05:
            risk_factors.append("medium_size")

        # Odds risk
        odds = bet_data.get("odds", -110)
        if abs(odds) < 120:  # Close to even odds
            risk_factors.append("low_odds_risk")
        elif abs(odds) > 300:  # Long shots
            risk_factors.append("high_odds_risk")

        # Market risk
        market = bet_data.get("market", "").lower()
        if market in ["player_props", "novelty", "futures"]:
            risk_factors.append("high_variance_market")

        # Time risk
        bet_time = bet_data.get("bet_time", datetime.now())
        if bet_time.hour < 6 or bet_time.hour > 22:
            risk_factors.append("off_hours_betting")

        # Determine overall risk
        if len(risk_factors) >= 3:
            return "high"
        elif len(risk_factors) >= 2:
            return "medium"
        elif len(risk_factors) >= 1:
            return "low"
        else:
            return "minimal"

    def get_risk_warnings(self, risk_level: str, bet_data: dict[str, Any]) -> list[str]:
        """Generate risk warnings for the bet"""

        warnings = []

        if risk_level == "high":
            warnings.extend(
                [
                    "⚠️ HIGH RISK BET - Consider reducing bet size",
                    "🛑 This bet exceeds recommended risk parameters",
                    "💡 Consider waiting for better opportunities",
                ]
            )
        elif risk_level == "medium":
            warnings.extend(
                ["⚠️ Medium risk - Monitor carefully", "💡 Consider position sizing carefully"]
            )

        # Specific warnings
        odds = bet_data.get("odds", -110)
        if abs(odds) > 300:
            warnings.append("🎯 Long shot bet - high variance expected")

        if bet_data.get("market", "").lower() in ["player_props"]:
            warnings.append("🏃 Player prop bet - injury risk present")

        return warnings

    async def get_bankroll_profile(self, user_id: str) -> BankrollProfile | None:
        """Get user bankroll profile"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM bankroll_profiles WHERE user_id = ?
        """,
            (user_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return BankrollProfile(
            user_id=row[0],
            total_bankroll=row[1],
            risk_tolerance=row[2],
            max_bet_size=row[3],
            daily_limit=row[4],
            monthly_limit=row[5],
            kelly_multiplier=row[6],
            stop_loss_percent=row[7],
            profit_target_percent=row[8],
        )

    # ==================== RISK MONITORING ====================

    async def start_betting_session(self, user_id: str) -> str:
        """Start new betting session with monitoring"""

        profile = await self.get_bankroll_profile(user_id)
        if not profile:
            raise ValueError("User profile required to start session")

        session_id = hashlib.md5(f"{user_id}{time.time()}".encode()).hexdigest()

        session = BettingSession(
            session_id=session_id,
            user_id=user_id,
            start_time=datetime.now(),
            end_time=None,
            starting_bankroll=profile.total_bankroll,
            current_bankroll=profile.total_bankroll,
            total_wagered=0.0,
            total_won=0.0,
            bet_count=0,
            largest_bet=0.0,
            longest_streak=0,
        )

        # Store session
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO betting_sessions
            (session_id, user_id, start_time, starting_bankroll, current_bankroll,
             total_wagered, total_won, bet_count, largest_bet, longest_streak, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                session.session_id,
                session.user_id,
                session.start_time,
                session.starting_bankroll,
                session.current_bankroll,
                session.total_wagered,
                session.total_won,
                session.bet_count,
                session.largest_bet,
                session.longest_streak,
                0.0,
            ),
        )

        conn.commit()
        conn.close()

        logger.info(f"✅ Started betting session {session_id} for {user_id}")
        return session_id

    async def monitor_bet_placement(self, bet_data: dict[str, Any]) -> dict[str, Any]:
        """Monitor bet placement for risk factors"""

        user_id = bet_data["user_id"]
        session_id = bet_data.get("session_id")
        bet_amount = bet_data["bet_amount"]

        # Get current session and profile
        profile = await self.get_bankroll_profile(user_id)
        session = await self.get_current_session(session_id) if session_id else None

        # Risk checks
        risk_alerts = []

        # Check bet size limits
        if bet_amount > profile.max_bet_size:
            risk_alerts.append(
                {
                    "type": "bet_size_exceeded",
                    "severity": "high",
                    "message": f"Bet size ${bet_amount:.2f} exceeds limit ${profile.max_bet_size:.2f}",
                }
            )

        # Check daily limits
        daily_wagered = await self.get_daily_wagered(user_id)
        if daily_wagered + bet_amount > profile.daily_limit:
            risk_alerts.append(
                {
                    "type": "daily_limit_exceeded",
                    "severity": "medium",
                    "message": f"Daily limit would be exceeded: ${daily_wagered + bet_amount:.2f} > ${profile.daily_limit:.2f}",
                }
            )

        # Check session patterns
        if session:
            session_risk = await self.analyze_session_risk(session)
            if session_risk["risk_score"] > 0.7:
                risk_alerts.append(
                    {
                        "type": "high_risk_session",
                        "severity": "high",
                        "message": f"Session risk score: {session_risk['risk_score']:.2f}",
                    }
                )

        # Check for chasing behavior
        recent_bets = await self.get_recent_bets(user_id, limit=5)
        if self.detect_chasing_behavior(recent_bets, bet_amount):
            risk_alerts.append(
                {
                    "type": "chasing_detected",
                    "severity": "critical",
                    "message": "Potential chasing behavior detected - increasing bet size after losses",
                }
            )

        # Generate recommendations
        recommendations = []
        if risk_alerts:
            if any(alert["severity"] == "critical" for alert in risk_alerts):
                recommendations.append("🛑 STOP BETTING - Take a break and reassess")
                recommendations.append("🧘 Consider using responsible gambling tools")
            elif any(alert["severity"] == "high" for alert in risk_alerts):
                recommendations.append("⚠️ Reduce bet size significantly")
                recommendations.append("💡 Review bankroll management strategy")
            else:
                recommendations.append("💡 Proceed with caution")
                recommendations.append("📊 Monitor session progress closely")

        # AI-powered risk analysis
        ai_risk_assessment = await self.ai_risk_analysis(bet_data, risk_alerts)

        return {
            "risk_alerts": risk_alerts,
            "recommendations": recommendations,
            "ai_assessment": ai_risk_assessment,
            "approval_status": (
                "blocked"
                if any(alert["severity"] == "critical" for alert in risk_alerts)
                else "approved"
            ),
        }

    async def ai_risk_analysis(
        self, bet_data: dict[str, Any], risk_alerts: list[dict]
    ) -> dict[str, Any]:
        """AI-powered comprehensive risk analysis"""

        try:
            context = {
                "bet_amount": bet_data.get("bet_amount", 0),
                "user_history": await self.get_user_betting_history(bet_data["user_id"], days=30),
                "risk_alerts": risk_alerts,
                "market_conditions": bet_data.get("market_conditions", {}),
                "time_of_bet": datetime.now().isoformat(),
            }

            prompt = f"""
            Analyze this betting situation for risk factors and provide recommendations:

            BETTING CONTEXT:
            {json.dumps(context, indent=2)}

            RISK ASSESSMENT REQUIRED:
            1. Problem gambling indicators
            2. Financial risk level
            3. Behavioral pattern analysis
            4. Recommended interventions
            5. Confidence level in assessment

            Provide a structured risk assessment with specific, actionable recommendations.
            Focus on responsible gambling and financial safety.
            """

            response = await self.openai_manager.secure_openai_request(
                "gpt-4o",
                [
                    {
                        "role": "system",
                        "content": "You are a responsible gambling AI advisor. Prioritize user safety and financial wellbeing in all assessments.",
                    },
                    {"role": "user", "content": prompt},
                ],
                {"max_tokens": 500, "temperature": 0.2},
            )

            ai_response = response["response"]["choices"][0]["message"]["content"]

            return {
                "assessment": ai_response,
                "confidence": 0.85,  # Default confidence
                "cost": response.get("cost_check", {}).get("estimated_cost", 0),
            }

        except Exception as e:
            logger.error(f"AI risk analysis error: {e}")
            return {
                "assessment": "AI analysis unavailable - proceed with manual risk assessment",
                "confidence": 0.0,
                "cost": 0.0,
            }

    def detect_chasing_behavior(self, recent_bets: list[dict], current_bet_amount: float) -> bool:
        """Detect chasing behavior patterns"""

        if len(recent_bets) < 3:
            return False

        # Check for consecutive losses followed by bet size increase
        consecutive_losses = 0
        last_bet_amount = 0

        for bet in recent_bets:
            if bet["outcome"] == "loss":
                consecutive_losses += 1
            else:
                consecutive_losses = 0

            last_bet_amount = bet["bet_amount"]

        # Chasing detected if 2+ consecutive losses and current bet > 1.5x last bet
        return consecutive_losses >= 2 and current_bet_amount > last_bet_amount * 1.5

    async def get_daily_wagered(self, user_id: str) -> float:
        """Get total amount wagered today"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COALESCE(SUM(bet_amount), 0) FROM bet_history
            WHERE user_id = ? AND DATE(placed_at) = DATE('now')
        """,
            (user_id,),
        )

        result = cursor.fetchone()[0]
        conn.close()

        return result or 0.0

    async def get_recent_bets(self, user_id: str, limit: int = 10) -> list[dict]:
        """Get recent betting history"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT bet_amount, outcome, placed_at, profit_loss
            FROM bet_history
            WHERE user_id = ?
            ORDER BY placed_at DESC
            LIMIT ?
        """,
            (user_id, limit),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {"bet_amount": row[0], "outcome": row[1], "placed_at": row[2], "profit_loss": row[3]}
            for row in rows
        ]

    # ==================== COMPLIANCE MONITORING ====================

    async def check_legal_compliance(
        self, user_location: str, bet_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Check legal compliance for bet placement"""

        try:
            # Get applicable rules
            applicable_rules = await self.get_applicable_rules(user_location)

            compliance_issues = []

            # Age verification (simulated)
            if not await self.verify_age(bet_data.get("user_id")):
                compliance_issues.append(
                    {
                        "rule_type": "age_verification",
                        "severity": "critical",
                        "message": "Age verification required",
                        "action": "Block bet placement",
                    }
                )

            # Bet limits check
            bet_amount = bet_data.get("bet_amount", 0)
            for rule in applicable_rules:
                if rule["rule_type"] == "bet_limits":
                    # Parse limit from rule description (simplified)
                    if "Maximum $1000" in rule["description"] and bet_amount > 1000:
                        compliance_issues.append(
                            {
                                "rule_type": "bet_limits",
                                "severity": "high",
                                "message": f"Bet amount ${bet_amount} exceeds state limit",
                                "action": "Reduce bet or reject",
                            }
                        )

            # Geolocation compliance
            if not await self.verify_geolocation(user_location, bet_data):
                compliance_issues.append(
                    {
                        "rule_type": "geolocation",
                        "severity": "critical",
                        "message": "Bet placed from restricted location",
                        "action": "Block immediately",
                    }
                )

            # Responsible gambling compliance
            if await self.check_self_exclusion(bet_data.get("user_id")):
                compliance_issues.append(
                    {
                        "rule_type": "self_exclusion",
                        "severity": "critical",
                        "message": "User is self-excluded",
                        "action": "Block all betting activity",
                    }
                )

            # Generate compliance report
            compliance_status = "compliant" if not compliance_issues else "non_compliant"

            return {
                "compliance_status": compliance_status,
                "issues": compliance_issues,
                "applicable_rules": applicable_rules,
                "recommendations": self.generate_compliance_recommendations(compliance_issues),
            }

        except Exception as e:
            logger.error(f"Compliance check error: {e}")
            return {
                "compliance_status": "error",
                "issues": [{"severity": "high", "message": "Compliance check failed"}],
                "applicable_rules": [],
                "recommendations": ["Manual review required"],
            }

    async def get_applicable_rules(self, location: str) -> list[dict[str, Any]]:
        """Get compliance rules applicable to location"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT jurisdiction, rule_type, description, penalty, source
            FROM compliance_rules
            WHERE (jurisdiction = ? OR jurisdiction = 'federal') AND active = 1
        """,
            (location,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "jurisdiction": row[0],
                "rule_type": row[1],
                "description": row[2],
                "penalty": row[3],
                "source": row[4],
            }
            for row in rows
        ]

    async def verify_age(self, user_id: str) -> bool:
        """Verify user age compliance (simulated)"""
        # In production, would integrate with ID verification service
        return True  # Simulated pass

    async def verify_geolocation(self, location: str, bet_data: dict[str, Any]) -> bool:
        """Verify geolocation compliance"""
        # In production, would use real geolocation services
        legal_states = [
            "NY",
            "NJ",
            "PA",
            "MI",
            "IN",
            "IA",
            "IL",
            "CO",
            "TN",
            "VA",
            "WV",
            "NV",
            "DE",
            "NH",
            "CT",
            "MT",
            "AZ",
            "WY",
            "LA",
        ]
        return location in legal_states

    async def check_self_exclusion(self, user_id: str) -> bool:
        """Check if user is self-excluded"""
        # In production, would check against self-exclusion databases
        return False  # Simulated not excluded

    def generate_compliance_recommendations(self, issues: list[dict]) -> list[str]:
        """Generate compliance recommendations"""

        recommendations = []

        if any(issue["severity"] == "critical" for issue in issues):
            recommendations.extend(
                [
                    "🚨 IMMEDIATE ACTION REQUIRED",
                    "Block all betting activity until issues resolved",
                    "Contact legal compliance team",
                    "Document all actions taken",
                ]
            )
        elif any(issue["severity"] == "high" for issue in issues):
            recommendations.extend(
                [
                    "⚠️ High priority compliance issues detected",
                    "Review and resolve before proceeding",
                    "Consider enhanced monitoring",
                ]
            )

        return recommendations

    # ==================== REVENUE & API ENDPOINTS ====================

    def create_fastapi_app(self):
        """Create FastAPI app for compliance copilot"""

        from fastapi import FastAPI, HTTPException

        app = FastAPI(title="EQ12 Compliance Copilot API", version="2.0.0")

        @app.post("/api/bankroll/create-profile")
        async def create_profile_api(profile_data: dict[str, Any]):
            """Create bankroll management profile"""
            try:
                profile = await self.create_bankroll_profile(profile_data)
                return asdict(profile)
            except Exception as e:
                raise HTTPException(500, str(e))

        @app.post("/api/bankroll/calculate-bet-size")
        async def calculate_bet_size_api(bet_request: dict[str, Any]):
            """Calculate optimal bet size"""
            try:
                result = await self.calculate_optimal_bet_size(bet_request["user_id"], bet_request)
                return result
            except Exception as e:
                raise HTTPException(500, str(e))

        @app.post("/api/risk/monitor-bet")
        async def monitor_bet_api(bet_data: dict[str, Any]):
            """Monitor bet for risk factors"""
            try:
                result = await self.monitor_bet_placement(bet_data)
                return result
            except Exception as e:
                raise HTTPException(500, str(e))

        @app.post("/api/compliance/check")
        async def compliance_check_api(check_data: dict[str, Any]):
            """Check legal compliance"""
            try:
                result = await self.check_legal_compliance(check_data["location"], check_data)
                return result
            except Exception as e:
                raise HTTPException(500, str(e))

        @app.get("/api/revenue/stats")
        async def revenue_stats_api():
            """Get revenue statistics"""
            return {"pricing": self.pricing, "revenue_stats": self.revenue_stats}

        return app


# ==================== MAIN EXECUTION ====================


async def main():
    """Main compliance copilot execution"""

    copilot = EQ12BankrollComplianceCopilot()

    logger.info("🚀 EQ12 Bankroll & Compliance Copilot Started")
    logger.info("💰 Revenue streams:")
    logger.info("   - Bankroll management: $99/month per user")
    logger.info("   - Compliance consulting: $299/month per operator")
    logger.info("   - Risk management tools: $49/month per bettor")
    logger.info("   - B2B compliance API: $999/month + usage")
    logger.info("🎯 Target: $25,000/month from compliance services")

    # Create and start FastAPI app
    app = copilot.create_fastapi_app()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)


if __name__ == "__main__":
    asyncio.run(main())
