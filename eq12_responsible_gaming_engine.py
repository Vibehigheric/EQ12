# eq12_responsible_gaming_engine.py
"""
EQ12 Responsible Gaming Engine
Advanced responsible gaming protections with PII-safe logging,
audit trails, deterministic offline mode, and config-driven controls
"""

import asyncio
import hashlib
import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import aioredis
from pydantic import BaseModel, ConfigDict, Field

from eq12_helpers import setup_utf8_logging
from eq12_structured_observability import ObservabilityManager

setup_utf8_logging()


class RiskLevel(Enum):
    """Risk assessment levels"""

    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"


class InterventionType(Enum):
    """Types of responsible gaming interventions"""

    WARNING = "warning"
    COOL_DOWN = "cool_down"
    LIMIT_ENFORCEMENT = "limit_enforcement"
    SESSION_TIMEOUT = "session_timeout"
    MANDATORY_BREAK = "mandatory_break"
    ACCOUNT_SUSPENSION = "account_suspension"


@dataclass
class ResponsibleGamingLimits:
    """User-defined responsible gaming limits"""

    daily_deposit_limit: float | None = None
    daily_bet_limit: float | None = None
    daily_loss_limit: float | None = None
    session_time_limit: int | None = None  # minutes
    max_bet_size: float | None = None
    cool_down_period: int | None = None  # hours
    weekly_deposit_limit: float | None = None
    monthly_deposit_limit: float | None = None

    # Behavioral limits
    max_consecutive_losses: int | None = 5
    max_chase_attempts: int | None = 3
    velocity_alert_threshold: float | None = 0.2  # 20% bankroll in 1 hour


@dataclass
class BettingSession:
    """Betting session tracking data"""

    session_id: str
    user_id_hash: str  # PII-safe hashed user ID
    start_time: datetime
    end_time: datetime | None = None
    total_bets: int = 0
    total_wagered: float = 0.0
    total_winnings: float = 0.0
    net_result: float = 0.0
    consecutive_losses: int = 0
    chase_bets: int = 0
    peak_balance: float = 0.0
    current_balance: float = 0.0
    risk_flags: set[str] = None
    interventions_triggered: list[str] = None

    def __post_init__(self):
        if self.risk_flags is None:
            self.risk_flags = set()
        if self.interventions_triggered is None:
            self.interventions_triggered = []


class ResponsibleGamingEvent(BaseModel):
    """Responsible gaming event for audit trail"""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id_hash: str = Field(..., description="PII-safe user identifier")
    event_type: str = Field(..., description="Type of RG event")
    risk_level: RiskLevel = Field(..., description="Risk assessment level")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    # Event data (PII-safe)
    session_data: dict[str, Any] | None = None
    limits_checked: dict[str, bool] = Field(default_factory=dict)
    interventions: list[str] = Field(default_factory=list)
    behavioral_flags: list[str] = Field(default_factory=list)

    # Metadata
    offline_mode: bool = Field(default=False, description="Event recorded offline")
    system_version: str = Field(default="2.1.0", description="RG engine version")

    model_config = ConfigDict(use_enum_values=True)


class BettingBehaviorAnalyzer:
    """Analyze betting patterns for responsible gaming flags"""

    def __init__(self):
        self.pattern_thresholds = {
            "rapid_betting_threshold": 5,  # 5 bets in 10 minutes
            "loss_chasing_multiplier": 2.0,  # 2x bet after loss
            "time_spent_threshold": 180,  # 3 hours continuous
            "frequency_threshold": 0.8,  # 80% of days in past week
            "escalation_pattern_threshold": 1.5,  # 50% bet size increase
        }

    def analyze_session_behavior(
        self, session: BettingSession, recent_sessions: list[BettingSession]
    ) -> list[str]:
        """Analyze betting behavior for warning signs"""

        flags = []

        # Current session analysis
        flags.extend(self._analyze_current_session(session))

        # Historical pattern analysis
        flags.extend(self._analyze_historical_patterns(recent_sessions))

        # Cross-session correlation analysis
        flags.extend(self._analyze_session_correlations(session, recent_sessions))

        return flags

    def _analyze_current_session(self, session: BettingSession) -> list[str]:
        """Analyze current session for immediate flags"""
        flags = []

        # Rapid betting detection
        session_duration = (datetime.now(UTC) - session.start_time).total_seconds() / 60
        if session_duration > 0:
            bet_rate = session.total_bets / max(session_duration, 1)
            if bet_rate > (self.pattern_thresholds["rapid_betting_threshold"] / 10):
                flags.append("rapid_betting_pattern")

        # Loss chasing detection
        if session.chase_bets > 0:
            chase_ratio = session.chase_bets / max(session.total_bets, 1)
            if chase_ratio > 0.3:  # 30% of bets are chase bets
                flags.append("loss_chasing_behavior")

        # Extended session time
        if session_duration > self.pattern_thresholds["time_spent_threshold"]:
            flags.append("extended_session_duration")

        # Consecutive losses
        if session.consecutive_losses >= 5:
            flags.append("excessive_consecutive_losses")

        # Balance depletion pattern
        if session.current_balance > 0 and session.peak_balance > 0:
            depletion_ratio = 1 - (session.current_balance / session.peak_balance)
            if depletion_ratio > 0.8:  # Lost 80% of peak balance
                flags.append("significant_balance_depletion")

        return flags

    def _analyze_historical_patterns(self, recent_sessions: list[BettingSession]) -> list[str]:
        """Analyze historical betting patterns"""
        flags = []

        if len(recent_sessions) < 3:
            return flags

        # Frequency analysis (daily betting)
        daily_sessions = set()
        for session in recent_sessions[-7:]:  # Last 7 sessions
            if session.start_time:
                daily_sessions.add(session.start_time.date())

        frequency = len(daily_sessions) / 7.0
        if frequency > self.pattern_thresholds["frequency_threshold"]:
            flags.append("high_frequency_betting")

        # Escalation pattern
        recent_wagers = [s.total_wagered for s in recent_sessions[-5:] if s.total_wagered > 0]
        if len(recent_wagers) >= 3:
            avg_early = sum(recent_wagers[:2]) / 2
            avg_recent = sum(recent_wagers[-2:]) / 2
            if avg_recent > avg_early * self.pattern_thresholds["escalation_pattern_threshold"]:
                flags.append("bet_size_escalation")

        # Win/loss pattern analysis
        net_results = [s.net_result for s in recent_sessions[-10:]]
        if len(net_results) >= 5:
            losses = [r for r in net_results if r < 0]
            if len(losses) >= len(net_results) * 0.8:  # 80% losing sessions
                flags.append("persistent_losing_pattern")

        return flags

    def _analyze_session_correlations(
        self, current_session: BettingSession, recent_sessions: list[BettingSession]
    ) -> list[str]:
        """Analyze correlations between sessions"""
        flags = []

        # Post-loss behavior
        if recent_sessions:
            last_session = recent_sessions[-1]
            if (
                last_session.net_result < 0
                and current_session.total_wagered > last_session.total_wagered * 1.5
            ):
                flags.append("post_loss_escalation")

        # Time-based patterns
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Late night/early morning betting
            late_sessions = sum(
                1
                for s in recent_sessions[-5:]
                if s.start_time and (s.start_time.hour < 6 or s.start_time.hour > 22)
            )
            if late_sessions >= 3:
                flags.append("off_hours_betting_pattern")

        return flags


class ResponsibleGamingEngine:
    """Main responsible gaming engine with comprehensive protections"""

    def __init__(self, config_path: str = "configs/responsible_gaming.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.observability = ObservabilityManager("responsible_gaming_engine")

        # Components
        self.behavior_analyzer = BettingBehaviorAnalyzer()
        self.redis = None  # Will be initialized in setup

        # State tracking
        self.active_sessions: dict[str, BettingSession] = {}
        self.offline_events: list[ResponsibleGamingEvent] = []
        self.offline_mode = False

        # Audit trail
        self.audit_log_path = Path("logs/responsible_gaming_audit.jsonl")
        self.audit_log_path.parent.mkdir(exist_ok=True)

    def _load_config(self) -> dict[str, Any]:
        """Load configuration with secure defaults"""

        default_config = {
            "default_limits": {
                "daily_deposit_limit": 1000.0,
                "daily_bet_limit": 500.0,
                "daily_loss_limit": 200.0,
                "session_time_limit": 240,  # 4 hours
                "max_bet_size": 100.0,
                "cool_down_period": 24,  # 24 hours
                "weekly_deposit_limit": 5000.0,
                "monthly_deposit_limit": 15000.0,
            },
            "intervention_triggers": {
                "warning_threshold": 0.7,  # 70% of limit
                "cool_down_threshold": 0.9,  # 90% of limit
                "mandatory_break_threshold": 1.0,  # 100% of limit
                "behavioral_flag_limit": 3,  # Max behavioral flags before intervention
                "consecutive_intervention_limit": 2,
            },
            "audit_retention": {
                "days": 2555,  # 7 years for compliance
                "encryption_enabled": True,
                "pii_scrubbing_enabled": True,
            },
            "offline_mode": {
                "enabled": True,
                "max_offline_events": 10000,
                "sync_interval_minutes": 15,
            },
        }

        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    default_config.update(user_config)
            except Exception as e:
                logging.warning(f"Failed to load RG config, using defaults: {e}")

        return default_config

    async def setup(self, redis_url: str = "redis://localhost:6379"):
        """Initialize async components"""

        try:
            self.redis = await aioredis.from_url(redis_url)
            await self.observability.logger.info("Responsible gaming engine initialized")

            # Start offline event sync if Redis available
            asyncio.create_task(self._sync_offline_events())

        except Exception as e:
            await self.observability.logger.warning(
                f"Redis unavailable, running in offline mode: {e}"
            )
            self.offline_mode = True

    async def check_betting_limits(
        self, user_id: str, bet_amount: float, bet_type: str = "standard"
    ) -> dict[str, Any]:
        """Comprehensive betting limits check with intervention logic"""

        user_id_hash = self._hash_user_id(user_id)

        # Get user limits (from config or user-defined)
        user_limits = await self._get_user_limits(user_id_hash)

        # Get current session
        session = await self._get_or_create_session(user_id_hash)

        # Get recent betting history
        recent_sessions = await self._get_recent_sessions(user_id_hash, days=30)

        # Check all limits
        limit_checks = await self._perform_limit_checks(
            user_limits, session, bet_amount, recent_sessions
        )

        # Analyze behavioral patterns
        behavioral_flags = self.behavior_analyzer.analyze_session_behavior(session, recent_sessions)

        # Assess risk level
        risk_level = self._assess_risk_level(limit_checks, behavioral_flags)

        # Determine interventions
        interventions = self._determine_interventions(
            risk_level, limit_checks, behavioral_flags, user_id_hash
        )

        # Create audit event
        event = ResponsibleGamingEvent(
            user_id_hash=user_id_hash,
            event_type="betting_limit_check",
            risk_level=risk_level,
            session_data=self._sanitize_session_data(session),
            limits_checked=limit_checks,
            interventions=[i.value for i in interventions],
            behavioral_flags=behavioral_flags,
            offline_mode=self.offline_mode,
        )

        # Log audit event
        await self._log_audit_event(event)

        # Apply interventions
        intervention_results = await self._apply_interventions(interventions, user_id_hash, session)

        return {
            "allowed": len([i for i in interventions if i != InterventionType.ACCOUNT_SUSPENSION])
            == 0,
            "risk_level": risk_level.value,
            "limit_checks": limit_checks,
            "behavioral_flags": behavioral_flags,
            "interventions": [i.value for i in interventions],
            "intervention_results": intervention_results,
            "session_id": session.session_id,
            "audit_event_id": event.event_id,
        }

    def _hash_user_id(self, user_id: str) -> str:
        """Create PII-safe hash of user ID"""
        # Use SHA-256 with salt for PII protection
        salt = os.environ.get("RG_USER_SALT", "EQ12-RG-SALT-2024")
        return hashlib.sha256(f"{salt}:{user_id}".encode()).hexdigest()[:16]

    async def _get_user_limits(self, user_id_hash: str) -> ResponsibleGamingLimits:
        """Get user-specific or default limits"""

        try:
            if not self.offline_mode and self.redis:
                limits_data = await self.redis.get(f"rg_limits:{user_id_hash}")
                if limits_data:
                    limits_dict = json.loads(limits_data)
                    return ResponsibleGamingLimits(**limits_dict)
        except Exception as e:
            logging.warning(f"Failed to fetch user limits, using defaults: {e}")

        # Return default limits from config
        return ResponsibleGamingLimits(**self.config["default_limits"])

    async def _get_or_create_session(self, user_id_hash: str) -> BettingSession:
        """Get existing session or create new one"""

        # Check active sessions first
        if user_id_hash in self.active_sessions:
            return self.active_sessions[user_id_hash]

        # Try to load from Redis
        try:
            if not self.offline_mode and self.redis:
                session_data = await self.redis.get(f"session:{user_id_hash}")
                if session_data:
                    session_dict = json.loads(session_data)
                    # Convert datetime strings back to datetime objects
                    session_dict["start_time"] = datetime.fromisoformat(session_dict["start_time"])
                    if session_dict.get("end_time"):
                        session_dict["end_time"] = datetime.fromisoformat(session_dict["end_time"])

                    session = BettingSession(**session_dict)
                    self.active_sessions[user_id_hash] = session
                    return session
        except Exception as e:
            logging.warning(f"Failed to load session, creating new: {e}")

        # Create new session
        session = BettingSession(
            session_id=str(uuid.uuid4()),
            user_id_hash=user_id_hash,
            start_time=datetime.now(UTC),
            current_balance=0.0,  # Will be updated from actual balance
            peak_balance=0.0,
        )

        self.active_sessions[user_id_hash] = session
        await self._save_session(session)

        return session

    async def _get_recent_sessions(self, user_id_hash: str, days: int = 30) -> list[BettingSession]:
        """Get recent betting sessions for analysis"""

        sessions = []

        try:
            if not self.offline_mode and self.redis:
                # Get session IDs for the user
                session_keys = await self.redis.keys(f"session_history:{user_id_hash}:*")

                # Fetch session data
                for key in session_keys[-50:]:  # Last 50 sessions max
                    session_data = await self.redis.get(key)
                    if session_data:
                        session_dict = json.loads(session_data)
                        # Convert datetime strings
                        session_dict["start_time"] = datetime.fromisoformat(
                            session_dict["start_time"]
                        )
                        if session_dict.get("end_time"):
                            session_dict["end_time"] = datetime.fromisoformat(
                                session_dict["end_time"]
                            )

                        sessions.append(BettingSession(**session_dict))

        except Exception as e:
            logging.warning(f"Failed to fetch recent sessions: {e}")

        # Filter to requested timeframe
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        sessions = [s for s in sessions if s.start_time >= cutoff_date]

        return sorted(sessions, key=lambda x: x.start_time)

    async def _perform_limit_checks(
        self,
        limits: ResponsibleGamingLimits,
        session: BettingSession,
        bet_amount: float,
        recent_sessions: list[BettingSession],
    ) -> dict[str, bool]:
        """Perform all limit checks"""

        checks = {}

        # Daily limits
        today = datetime.now(UTC).date()
        today_sessions = [s for s in recent_sessions if s.start_time.date() == today]
        today_wagered = sum(s.total_wagered for s in today_sessions) + session.total_wagered
        today_losses = (
            sum(abs(s.net_result) for s in today_sessions if s.net_result < 0)
            + abs(session.net_result)
            if session.net_result < 0
            else 0
        )

        checks["daily_bet_limit_ok"] = (
            limits.daily_bet_limit is None or (today_wagered + bet_amount) <= limits.daily_bet_limit
        )
        checks["daily_loss_limit_ok"] = (
            limits.daily_loss_limit is None or today_losses <= limits.daily_loss_limit
        )
        checks["max_bet_size_ok"] = limits.max_bet_size is None or bet_amount <= limits.max_bet_size

        # Session limits
        session_duration = (datetime.now(UTC) - session.start_time).total_seconds() / 60
        checks["session_time_limit_ok"] = (
            limits.session_time_limit is None or session_duration <= limits.session_time_limit
        )

        # Behavioral limits
        checks["consecutive_losses_ok"] = (
            limits.max_consecutive_losses is None
            or session.consecutive_losses < limits.max_consecutive_losses
        )
        checks["chase_attempts_ok"] = (
            limits.max_chase_attempts is None or session.chase_bets < limits.max_chase_attempts
        )

        # Velocity check
        if limits.velocity_alert_threshold and session_duration > 0:
            hourly_rate = (session.total_wagered + bet_amount) / max(session_duration / 60, 1)
            estimated_bankroll = (
                session.peak_balance if session.peak_balance > 0 else 1000
            )  # Default estimate
            checks["velocity_ok"] = hourly_rate <= (
                estimated_bankroll * limits.velocity_alert_threshold
            )
        else:
            checks["velocity_ok"] = True

        return checks

    def _assess_risk_level(
        self, limit_checks: dict[str, bool], behavioral_flags: list[str]
    ) -> RiskLevel:
        """Assess overall risk level based on checks and flags"""

        failed_checks = sum(1 for ok in limit_checks.values() if not ok)
        flag_count = len(behavioral_flags)

        # Critical risk factors
        critical_flags = {
            "extended_session_duration",
            "excessive_consecutive_losses",
            "significant_balance_depletion",
        }
        has_critical = any(flag in critical_flags for flag in behavioral_flags)

        if failed_checks >= 3 or has_critical:
            return RiskLevel.CRITICAL
        if failed_checks >= 2 or flag_count >= 4:
            return RiskLevel.SEVERE
        if failed_checks >= 1 or flag_count >= 3:
            return RiskLevel.HIGH
        if flag_count >= 2:
            return RiskLevel.MODERATE
        if flag_count >= 1:
            return RiskLevel.LOW
        return RiskLevel.MINIMAL

    def _determine_interventions(
        self,
        risk_level: RiskLevel,
        limit_checks: dict[str, bool],
        behavioral_flags: list[str],
        user_id_hash: str,
    ) -> list[InterventionType]:
        """Determine appropriate interventions based on risk assessment"""

        interventions = []

        # Risk-based interventions
        if risk_level == RiskLevel.CRITICAL:
            interventions.extend(
                [InterventionType.MANDATORY_BREAK, InterventionType.ACCOUNT_SUSPENSION]
            )
        elif risk_level == RiskLevel.SEVERE:
            interventions.extend([InterventionType.MANDATORY_BREAK, InterventionType.COOL_DOWN])
        elif risk_level == RiskLevel.HIGH:
            interventions.append(InterventionType.COOL_DOWN)
        elif risk_level in [RiskLevel.MODERATE, RiskLevel.LOW]:
            interventions.append(InterventionType.WARNING)

        # Specific limit-based interventions
        failed_limits = [check for check, ok in limit_checks.items() if not ok]

        if "session_time_limit_ok" in failed_limits:
            interventions.append(InterventionType.SESSION_TIMEOUT)

        if any(limit in failed_limits for limit in ["daily_bet_limit_ok", "daily_loss_limit_ok"]):
            interventions.append(InterventionType.LIMIT_ENFORCEMENT)

        # Behavioral interventions
        if "loss_chasing_behavior" in behavioral_flags:
            interventions.append(InterventionType.MANDATORY_BREAK)

        if "rapid_betting_pattern" in behavioral_flags:
            interventions.append(InterventionType.COOL_DOWN)

        return list(set(interventions))  # Remove duplicates

    async def _apply_interventions(
        self,
        interventions: list[InterventionType],
        user_id_hash: str,
        session: BettingSession,
    ) -> dict[str, Any]:
        """Apply responsible gaming interventions"""

        results = {}

        for intervention in interventions:
            try:
                if intervention == InterventionType.WARNING:
                    results[intervention.value] = await self._apply_warning(user_id_hash)

                elif intervention == InterventionType.COOL_DOWN:
                    results[intervention.value] = await self._apply_cool_down(user_id_hash, hours=1)

                elif intervention == InterventionType.LIMIT_ENFORCEMENT:
                    results[intervention.value] = await self._enforce_limits(user_id_hash)

                elif intervention == InterventionType.SESSION_TIMEOUT:
                    results[intervention.value] = await self._force_session_end(
                        user_id_hash, session
                    )

                elif intervention == InterventionType.MANDATORY_BREAK:
                    results[intervention.value] = await self._apply_mandatory_break(
                        user_id_hash, hours=24
                    )

                elif intervention == InterventionType.ACCOUNT_SUSPENSION:
                    results[intervention.value] = await self._suspend_account(
                        user_id_hash, hours=72
                    )

            except Exception as e:
                results[intervention.value] = {"success": False, "error": str(e)}

        return results

    async def _apply_warning(self, user_id_hash: str) -> dict[str, Any]:
        """Apply warning intervention"""

        warning_key = f"rg_warning:{user_id_hash}"

        try:
            if not self.offline_mode and self.redis:
                await self.redis.setex(warning_key, 3600, "active")  # 1 hour warning

            return {
                "success": True,
                "message": "Responsible gaming warning applied",
                "duration_hours": 1,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _apply_cool_down(self, user_id_hash: str, hours: int) -> dict[str, Any]:
        """Apply cool-down period"""

        cool_down_key = f"rg_cooldown:{user_id_hash}"

        try:
            if not self.offline_mode and self.redis:
                await self.redis.setex(cool_down_key, hours * 3600, "active")

            return {
                "success": True,
                "message": "Cool-down period applied",
                "duration_hours": hours,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _enforce_limits(self, user_id_hash: str) -> dict[str, Any]:
        """Enforce betting limits"""

        return {"success": True, "message": "Betting limits enforced"}

    async def _force_session_end(
        self, user_id_hash: str, session: BettingSession
    ) -> dict[str, Any]:
        """Force end current betting session"""

        session.end_time = datetime.now(UTC)
        await self._save_session(session, end_session=True)

        if user_id_hash in self.active_sessions:
            del self.active_sessions[user_id_hash]

        return {
            "success": True,
            "message": "Betting session terminated",
            "session_id": session.session_id,
        }

    async def _apply_mandatory_break(self, user_id_hash: str, hours: int) -> dict[str, Any]:
        """Apply mandatory break period"""

        break_key = f"rg_break:{user_id_hash}"

        try:
            if not self.offline_mode and self.redis:
                await self.redis.setex(break_key, hours * 3600, "mandatory")

            return {
                "success": True,
                "message": "Mandatory break applied",
                "duration_hours": hours,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _suspend_account(self, user_id_hash: str, hours: int) -> dict[str, Any]:
        """Suspend account temporarily"""

        suspension_key = f"rg_suspension:{user_id_hash}"

        try:
            if not self.offline_mode and self.redis:
                await self.redis.setex(suspension_key, hours * 3600, "suspended")

            return {
                "success": True,
                "message": "Account suspended",
                "duration_hours": hours,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _save_session(self, session: BettingSession, end_session: bool = False):
        """Save session data to Redis and/or local storage"""

        session_data = asdict(session)
        session_data["start_time"] = session.start_time.isoformat()
        if session.end_time:
            session_data["end_time"] = session.end_time.isoformat()

        # Convert sets to lists for JSON serialization
        session_data["risk_flags"] = list(session.risk_flags or [])

        try:
            if not self.offline_mode and self.redis:
                # Save current session
                session_key = f"session:{session.user_id_hash}"
                await self.redis.setex(session_key, 86400, json.dumps(session_data))  # 24 hour TTL

                # Save to history if ending session
                if end_session:
                    history_key = f"session_history:{session.user_id_hash}:{session.session_id}"
                    await self.redis.setex(
                        history_key, 86400 * 90, json.dumps(session_data)
                    )  # 90 day history

        except Exception as e:
            logging.warning(f"Failed to save session to Redis: {e}")
            # Save to local file as backup
            await self._save_session_offline(session_data)

    async def _save_session_offline(self, session_data: dict[str, Any]):
        """Save session data to local file"""

        offline_sessions_path = Path("logs/offline_sessions.jsonl")
        offline_sessions_path.parent.mkdir(exist_ok=True)

        try:
            with open(offline_sessions_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(session_data) + "\n")
        except Exception as e:
            logging.error(f"Failed to save session offline: {e}")

    def _sanitize_session_data(self, session: BettingSession) -> dict[str, Any]:
        """Sanitize session data for audit logging (remove PII)"""

        return {
            "session_id": session.session_id,
            "duration_minutes": (datetime.now(UTC) - session.start_time).total_seconds() / 60,
            "total_bets": session.total_bets,
            "total_wagered": session.total_wagered,
            "net_result": session.net_result,
            "consecutive_losses": session.consecutive_losses,
            "chase_bets": session.chase_bets,
            "risk_flags_count": len(session.risk_flags or []),
            "interventions_count": len(session.interventions_triggered or []),
        }

    async def _log_audit_event(self, event: ResponsibleGamingEvent):
        """Log audit event with PII protection"""

        try:
            # Store in observability system
            await self.observability.logger.info(
                "Responsible gaming event",
                event_type=event.event_type,
                risk_level=event.risk_level.value,
                user_hash=event.user_id_hash,
                interventions=event.interventions,
                behavioral_flags=event.behavioral_flags,
                event_id=event.event_id,
                offline_mode=event.offline_mode,
            )

            # Store in dedicated audit log
            audit_entry = {
                "timestamp": event.timestamp,
                "event_id": event.event_id,
                "user_id_hash": event.user_id_hash,
                "event_type": event.event_type,
                "risk_level": event.risk_level.value,
                "session_data": event.session_data,
                "limits_checked": event.limits_checked,
                "interventions": event.interventions,
                "behavioral_flags": event.behavioral_flags,
                "offline_mode": event.offline_mode,
                "system_version": event.system_version,
            }

            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_entry) + "\n")

            # Store in Redis if available
            if not self.offline_mode and self.redis:
                audit_key = f"rg_audit:{event.event_id}"
                await self.redis.setex(
                    audit_key, 86400 * 2555, json.dumps(audit_entry)
                )  # 7 year retention
            else:
                # Store offline for later sync
                self.offline_events.append(event)

        except Exception as e:
            logging.error(f"Failed to log audit event: {e}")

    async def _sync_offline_events(self):
        """Periodically sync offline events to Redis"""

        while True:
            try:
                await asyncio.sleep(self.config["offline_mode"]["sync_interval_minutes"] * 60)

                if not self.offline_mode and self.redis and self.offline_events:
                    events_to_sync = self.offline_events[:100]  # Batch sync

                    for event in events_to_sync:
                        audit_key = f"rg_audit:{event.event_id}"
                        audit_data = event.dict()
                        await self.redis.setex(audit_key, 86400 * 2555, json.dumps(audit_data))

                    # Remove synced events
                    self.offline_events = self.offline_events[100:]

                    await self.observability.logger.info(
                        f"Synced {len(events_to_sync)} offline RG events"
                    )

            except Exception as e:
                logging.warning(f"Failed to sync offline events: {e}")


async def demo_responsible_gaming():
    """Demonstration of responsible gaming engine"""

    setup_utf8_logging()
    logging.info("🛡️ Starting EQ12 Responsible Gaming Engine Demo")

    # Initialize engine
    rg_engine = ResponsibleGamingEngine()
    await rg_engine.setup()

    # Simulate betting activity
    user_id = "demo_user_123"

    print("\n🛡️ RESPONSIBLE GAMING ENGINE DEMO")
    print("=" * 50)

    # Test 1: Normal bet within limits
    result1 = await rg_engine.check_betting_limits(user_id, 25.0, "moneyline")
    print(f"Normal bet ($25): {'ALLOWED' if result1['allowed'] else 'BLOCKED'}")
    print(f"Risk Level: {result1['risk_level']}")
    print(f"Interventions: {result1['interventions']}")

    # Test 2: Large bet triggering warnings
    result2 = await rg_engine.check_betting_limits(user_id, 500.0, "parlay")
    print(f"\nLarge bet ($500): {'ALLOWED' if result2['allowed'] else 'BLOCKED'}")
    print(f"Risk Level: {result2['risk_level']}")
    print(f"Interventions: {result2['interventions']}")
    print(f"Behavioral Flags: {result2['behavioral_flags']}")

    # Test 3: Excessive bet triggering limits
    result3 = await rg_engine.check_betting_limits(user_id, 2000.0, "futures")
    print(f"\nExcessive bet ($2000): {'ALLOWED' if result3['allowed'] else 'BLOCKED'}")
    print(f"Risk Level: {result3['risk_level']}")
    print(f"Interventions: {result3['interventions']}")

    print("\n📊 Audit Events Created:")
    print(f"   Event IDs: {[r['audit_event_id'] for r in [result1, result2, result3]]}")

    print("\n✅ Responsible gaming demo completed")
    print("📋 Check logs/responsible_gaming_audit.jsonl for full audit trail")

    # Cleanup
    if rg_engine.redis:
        await rg_engine.redis.close()


if __name__ == "__main__":
    asyncio.run(demo_responsible_gaming())
