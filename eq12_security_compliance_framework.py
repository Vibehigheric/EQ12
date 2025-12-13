# eq12_security_compliance_framework.py
"""
EQ12 Security & Compliance Framework
Audit logging, responsible gaming controls, API security hardening,
encryption at rest, regulatory compliance features
"""

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import re
import secrets
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from eq12_helpers import env_get, setup_utf8_logging

setup_utf8_logging()


@dataclass
class AuditLogEntry:
    """Structured audit log entry for compliance tracking"""

    timestamp: datetime
    user_id: str
    action: str
    resource: str
    details: dict[str, Any]
    ip_address: str
    user_agent: str
    session_id: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    compliance_flags: list[str]


@dataclass
class SecurityEvent:
    """Security event for monitoring and alerting"""

    event_id: str
    event_type: str
    severity: str  # INFO, WARNING, CRITICAL
    source: str
    timestamp: datetime
    details: dict[str, Any]
    remediation_required: bool


@dataclass
class ResponsibleGamingProfile:
    """User responsible gaming profile and controls"""

    user_id: str
    daily_limit: float
    weekly_limit: float
    monthly_limit: float
    cooling_off_until: datetime | None
    self_exclusion_until: datetime | None
    deposit_limits: dict[str, float]
    session_time_limits: dict[str, int]
    risk_assessment_score: float
    last_assessment: datetime
    intervention_flags: list[str]


class EncryptionManager:
    """Handles encryption/decryption for sensitive data"""

    def __init__(self):
        self.setup_encryption_keys()

    def setup_encryption_keys(self):
        """Initialize encryption keys from environment or generate new ones"""

        # Main encryption key for data at rest
        key_material = env_get("EQ12_MASTER_KEY", "").encode()
        if not key_material:
            # Generate new key if not provided
            key_material = secrets.token_bytes(32)
            logging.warning("Generated new master key - store securely!")

        # Derive Fernet key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"eq12_salt_2024",  # In production, use random salt
            iterations=100000,
        )

        derived_key = kdf.derive(key_material)
        self.fernet = Fernet(base64.urlsafe_b64encode(derived_key))

        # Generate RSA key pair for API signatures
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data for storage"""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data from storage"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

    def sign_api_response(self, data: str) -> str:
        """Sign API response with private key"""
        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode()

    def verify_signature(self, data: str, signature: str) -> bool:
        """Verify API signature with public key"""
        try:
            signature_bytes = base64.b64decode(signature)
            self.public_key.verify(
                signature_bytes,
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False


class AuditLogger:
    """Comprehensive audit logging for compliance"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.encryption_manager = EncryptionManager()
        self.setup_audit_database()

    def setup_audit_database(self):
        """Initialize audit log database with proper schema"""

        self.db_path.parent.mkdir(exist_ok=True, parents=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Audit logs table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                details TEXT,  -- Encrypted JSON
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                risk_level TEXT DEFAULT 'LOW',
                compliance_flags TEXT,  -- JSON array
                hash_signature TEXT  -- Integrity check
            )
        """
        )

        # Security events table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT,  -- Encrypted JSON
                remediation_required INTEGER DEFAULT 0,
                resolved INTEGER DEFAULT 0,
                resolved_at TEXT
            )
        """
        )

        # Create indexes for performance
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp
            ON audit_logs(timestamp)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_audit_user
            ON audit_logs(user_id)
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_audit_action
            ON audit_logs(action)
        """
        )

        conn.commit()
        conn.close()

    def log_action(self, entry: AuditLogEntry):
        """Log user action with encryption and integrity checking"""

        # Encrypt sensitive details
        encrypted_details = self.encryption_manager.encrypt_sensitive_data(
            json.dumps(entry.details)
        )

        # Create integrity hash
        hash_data = f"{entry.timestamp.isoformat()}{entry.user_id}{entry.action}"
        hash_signature = hashlib.sha256(hash_data.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO audit_logs
            (timestamp, user_id, action, resource, details, ip_address,
             user_agent, session_id, risk_level, compliance_flags, hash_signature)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                entry.timestamp.isoformat(),
                entry.user_id,
                entry.action,
                entry.resource,
                encrypted_details,
                entry.ip_address,
                entry.user_agent,
                entry.session_id,
                entry.risk_level,
                json.dumps(entry.compliance_flags),
                hash_signature,
            ),
        )

        conn.commit()
        conn.close()

        logging.info(f"Audit log created: {entry.action} by {entry.user_id}")

    def log_security_event(self, event: SecurityEvent):
        """Log security event for monitoring"""

        encrypted_details = self.encryption_manager.encrypt_sensitive_data(
            json.dumps(event.details)
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO security_events
            (event_id, event_type, severity, source, timestamp, details, remediation_required)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                event.event_id,
                event.event_type,
                event.severity,
                event.source,
                event.timestamp.isoformat(),
                encrypted_details,
                1 if event.remediation_required else 0,
            ),
        )

        conn.commit()
        conn.close()

        logging.warning(f"Security event: {event.event_type} - {event.severity}")

    def get_audit_report(
        self, start_date: datetime, end_date: datetime, user_id: str | None = None
    ) -> list[dict]:
        """Generate audit report for compliance"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT timestamp, user_id, action, resource, details,
                   ip_address, risk_level, compliance_flags
            FROM audit_logs
            WHERE timestamp BETWEEN ? AND ?
        """

        params = [start_date.isoformat(), end_date.isoformat()]

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        # Decrypt and return results
        report = []
        for row in results:
            try:
                decrypted_details = self.encryption_manager.decrypt_sensitive_data(row[4])
                details = json.loads(decrypted_details)
            except Exception:
                details = {"error": "Failed to decrypt details"}

            report.append(
                {
                    "timestamp": row[0],
                    "user_id": row[1],
                    "action": row[2],
                    "resource": row[3],
                    "details": details,
                    "ip_address": row[5],
                    "risk_level": row[6],
                    "compliance_flags": json.loads(row[7] or "[]"),
                }
            )

        return report


class ResponsibleGamingManager:
    """Implements responsible gaming controls and monitoring"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.encryption_manager = EncryptionManager()
        self.audit_logger = AuditLogger(db_path)
        self.setup_rg_database()

    def setup_rg_database(self):
        """Initialize responsible gaming database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # User profiles table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rg_profiles (
                user_id TEXT PRIMARY KEY,
                daily_limit REAL DEFAULT 100.0,
                weekly_limit REAL DEFAULT 500.0,
                monthly_limit REAL DEFAULT 2000.0,
                cooling_off_until TEXT,
                self_exclusion_until TEXT,
                deposit_limits TEXT,  -- Encrypted JSON
                session_time_limits TEXT,  -- Encrypted JSON
                risk_assessment_score REAL DEFAULT 0.0,
                last_assessment TEXT,
                intervention_flags TEXT,  -- JSON array
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Betting activity tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS betting_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                bet_amount REAL NOT NULL,
                bet_type TEXT NOT NULL,
                outcome TEXT,  -- 'win', 'loss', 'pending'
                payout REAL DEFAULT 0.0,
                session_id TEXT,
                risk_indicators TEXT,  -- JSON array
                FOREIGN KEY (user_id) REFERENCES rg_profiles(user_id)
            )
        """
        )

        # Interventions log
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rg_interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                intervention_type TEXT NOT NULL,
                trigger_reason TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                action_taken TEXT,
                effectiveness_score REAL,
                FOREIGN KEY (user_id) REFERENCES rg_profiles(user_id)
            )
        """
        )

        conn.commit()
        conn.close()

    def create_user_profile(
        self, user_id: str, initial_limits: dict | None = None
    ) -> ResponsibleGamingProfile:
        """Create new responsible gaming profile for user"""

        profile = ResponsibleGamingProfile(
            user_id=user_id,
            daily_limit=initial_limits.get("daily", 100.0) if initial_limits else 100.0,
            weekly_limit=(initial_limits.get("weekly", 500.0) if initial_limits else 500.0),
            monthly_limit=(initial_limits.get("monthly", 2000.0) if initial_limits else 2000.0),
            cooling_off_until=None,
            self_exclusion_until=None,
            deposit_limits={"daily": 200.0, "weekly": 1000.0},
            session_time_limits={"daily": 240, "weekly": 1200},  # minutes
            risk_assessment_score=0.0,
            last_assessment=datetime.now(),
            intervention_flags=[],
        )

        self.save_profile(profile)

        # Log profile creation
        self.audit_logger.log_action(
            AuditLogEntry(
                timestamp=datetime.now(),
                user_id=user_id,
                action="CREATE_RG_PROFILE",
                resource="responsible_gaming",
                details={"initial_limits": initial_limits or {}},
                ip_address="system",
                user_agent="system",
                session_id="system",
                risk_level="LOW",
                compliance_flags=["PROFILE_CREATED"],
            )
        )

        return profile

    def save_profile(self, profile: ResponsibleGamingProfile):
        """Save responsible gaming profile to database"""

        # Encrypt sensitive data
        encrypted_deposit_limits = self.encryption_manager.encrypt_sensitive_data(
            json.dumps(profile.deposit_limits)
        )
        encrypted_session_limits = self.encryption_manager.encrypt_sensitive_data(
            json.dumps(profile.session_time_limits)
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO rg_profiles
            (user_id, daily_limit, weekly_limit, monthly_limit,
             cooling_off_until, self_exclusion_until, deposit_limits,
             session_time_limits, risk_assessment_score, last_assessment,
             intervention_flags, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                profile.user_id,
                profile.daily_limit,
                profile.weekly_limit,
                profile.monthly_limit,
                (profile.cooling_off_until.isoformat() if profile.cooling_off_until else None),
                (
                    profile.self_exclusion_until.isoformat()
                    if profile.self_exclusion_until
                    else None
                ),
                encrypted_deposit_limits,
                encrypted_session_limits,
                profile.risk_assessment_score,
                profile.last_assessment.isoformat(),
                json.dumps(profile.intervention_flags),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def get_profile(self, user_id: str) -> ResponsibleGamingProfile | None:
        """Retrieve user's responsible gaming profile"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT user_id, daily_limit, weekly_limit, monthly_limit,
                   cooling_off_until, self_exclusion_until, deposit_limits,
                   session_time_limits, risk_assessment_score, last_assessment,
                   intervention_flags
            FROM rg_profiles WHERE user_id = ?
        """,
            (user_id,),
        )

        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        # Decrypt sensitive data
        try:
            deposit_limits = json.loads(self.encryption_manager.decrypt_sensitive_data(result[6]))
            session_limits = json.loads(self.encryption_manager.decrypt_sensitive_data(result[7]))
        except Exception:
            deposit_limits = {"daily": 200.0, "weekly": 1000.0}
            session_limits = {"daily": 240, "weekly": 1200}

        return ResponsibleGamingProfile(
            user_id=result[0],
            daily_limit=result[1],
            weekly_limit=result[2],
            monthly_limit=result[3],
            cooling_off_until=datetime.fromisoformat(result[4]) if result[4] else None,
            self_exclusion_until=(datetime.fromisoformat(result[5]) if result[5] else None),
            deposit_limits=deposit_limits,
            session_time_limits=session_limits,
            risk_assessment_score=result[8],
            last_assessment=datetime.fromisoformat(result[9]),
            intervention_flags=json.loads(result[10] or "[]"),
        )

    def check_betting_limits(self, user_id: str, bet_amount: float) -> dict[str, Any]:
        """Check if user can place bet within their limits"""

        profile = self.get_profile(user_id)
        if not profile:
            return {"allowed": False, "reason": "No responsible gaming profile found"}

        # Check self-exclusion
        if profile.self_exclusion_until and datetime.now() < profile.self_exclusion_until:
            return {
                "allowed": False,
                "reason": "User is self-excluded",
                "until": profile.self_exclusion_until.isoformat(),
            }

        # Check cooling off period
        if profile.cooling_off_until and datetime.now() < profile.cooling_off_until:
            return {
                "allowed": False,
                "reason": "User is in cooling off period",
                "until": profile.cooling_off_until.isoformat(),
            }

        # Check spending limits
        current_spending = self.get_current_spending(user_id)

        # Daily limit check
        if current_spending["daily"] + bet_amount > profile.daily_limit:
            return {
                "allowed": False,
                "reason": "Daily spending limit exceeded",
                "current": current_spending["daily"],
                "limit": profile.daily_limit,
                "attempted": bet_amount,
            }

        # Weekly limit check
        if current_spending["weekly"] + bet_amount > profile.weekly_limit:
            return {
                "allowed": False,
                "reason": "Weekly spending limit exceeded",
                "current": current_spending["weekly"],
                "limit": profile.weekly_limit,
            }

        # Monthly limit check
        if current_spending["monthly"] + bet_amount > profile.monthly_limit:
            return {
                "allowed": False,
                "reason": "Monthly spending limit exceeded",
                "current": current_spending["monthly"],
                "limit": profile.monthly_limit,
            }

        return {
            "allowed": True,
            "warnings": self.generate_warnings(profile, current_spending, bet_amount),
        }

    def get_current_spending(self, user_id: str) -> dict[str, float]:
        """Get user's current spending within different time periods"""

        now = datetime.now()
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        weekly_start = daily_start - timedelta(days=now.weekday())
        monthly_start = daily_start.replace(day=1)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Daily spending
        cursor.execute(
            """
            SELECT COALESCE(SUM(bet_amount), 0)
            FROM betting_activity
            WHERE user_id = ? AND timestamp >= ?
        """,
            (user_id, daily_start.isoformat()),
        )
        daily_spending = cursor.fetchone()[0]

        # Weekly spending
        cursor.execute(
            """
            SELECT COALESCE(SUM(bet_amount), 0)
            FROM betting_activity
            WHERE user_id = ? AND timestamp >= ?
        """,
            (user_id, weekly_start.isoformat()),
        )
        weekly_spending = cursor.fetchone()[0]

        # Monthly spending
        cursor.execute(
            """
            SELECT COALESCE(SUM(bet_amount), 0)
            FROM betting_activity
            WHERE user_id = ? AND timestamp >= ?
        """,
            (user_id, monthly_start.isoformat()),
        )
        monthly_spending = cursor.fetchone()[0]

        conn.close()

        return {
            "daily": daily_spending,
            "weekly": weekly_spending,
            "monthly": monthly_spending,
        }

    def generate_warnings(
        self,
        profile: ResponsibleGamingProfile,
        current_spending: dict[str, float],
        bet_amount: float,
    ) -> list[str]:
        """Generate responsible gaming warnings for user"""

        warnings = []

        # Check if approaching limits (80% threshold)
        daily_usage = (current_spending["daily"] + bet_amount) / profile.daily_limit
        if daily_usage >= 0.8:
            warnings.append(f"You're approaching your daily limit ({daily_usage:.0%} used)")

        weekly_usage = (current_spending["weekly"] + bet_amount) / profile.weekly_limit
        if weekly_usage >= 0.8:
            warnings.append(f"You're approaching your weekly limit ({weekly_usage:.0%} used)")

        # Check risk assessment score
        if profile.risk_assessment_score >= 0.7:
            warnings.append(
                "Your betting patterns indicate elevated risk. Consider taking a break."
            )

        return warnings

    def record_betting_activity(
        self,
        user_id: str,
        bet_amount: float,
        bet_type: str,
        session_id: str,
        outcome: str = "pending",
    ) -> None:
        """Record betting activity for monitoring"""

        # Calculate risk indicators
        risk_indicators = self.calculate_risk_indicators(user_id, bet_amount)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO betting_activity
            (user_id, timestamp, bet_amount, bet_type, outcome, session_id, risk_indicators)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                user_id,
                datetime.now().isoformat(),
                bet_amount,
                bet_type,
                outcome,
                session_id,
                json.dumps(risk_indicators),
            ),
        )

        conn.commit()
        conn.close()

        # Update risk assessment
        self.update_risk_assessment(user_id)

        # Log activity for audit
        self.audit_logger.log_action(
            AuditLogEntry(
                timestamp=datetime.now(),
                user_id=user_id,
                action="PLACE_BET",
                resource="betting",
                details={
                    "bet_amount": bet_amount,
                    "bet_type": bet_type,
                    "risk_indicators": risk_indicators,
                },
                ip_address="system",
                user_agent="system",
                session_id=session_id,
                risk_level=self.determine_risk_level(risk_indicators),
                compliance_flags=["BETTING_ACTIVITY"],
            )
        )

    def calculate_risk_indicators(self, user_id: str, bet_amount: float) -> list[str]:
        """Calculate risk indicators for current bet"""

        indicators = []

        # Get recent betting history
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check for rapid successive bets (within 5 minutes)
        recent_cutoff = (datetime.now() - timedelta(minutes=5)).isoformat()
        cursor.execute(
            """
            SELECT COUNT(*) FROM betting_activity
            WHERE user_id = ? AND timestamp >= ?
        """,
            (user_id, recent_cutoff),
        )

        recent_bets = cursor.fetchone()[0]
        if recent_bets >= 3:
            indicators.append("RAPID_BETTING")

        # Check for increasing bet sizes
        cursor.execute(
            """
            SELECT bet_amount FROM betting_activity
            WHERE user_id = ?
            ORDER BY timestamp DESC LIMIT 5
        """,
            (user_id,),
        )

        recent_amounts = [row[0] for row in cursor.fetchall()]
        if len(recent_amounts) >= 3 and all(
            recent_amounts[i] < recent_amounts[i - 1] for i in range(1, len(recent_amounts))
        ):
            indicators.append("CHASING_LOSSES")

        # Check for large bet relative to history
        cursor.execute(
            """
            SELECT AVG(bet_amount) FROM betting_activity
            WHERE user_id = ? AND timestamp >= ?
        """,
            (user_id, (datetime.now() - timedelta(days=30)).isoformat()),
        )

        avg_bet = cursor.fetchone()[0]
        if avg_bet and bet_amount > avg_bet * 2:
            indicators.append("LARGE_BET")

        conn.close()

        return indicators

    def determine_risk_level(self, risk_indicators: list[str]) -> str:
        """Determine risk level based on indicators"""

        if any(indicator in risk_indicators for indicator in ["CHASING_LOSSES", "RAPID_BETTING"]):
            return "HIGH"
        if "LARGE_BET" in risk_indicators:
            return "MEDIUM"
        return "LOW"

    def update_risk_assessment(self, user_id: str):
        """Update user's risk assessment score"""

        # Get recent betting patterns
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get activity from last 30 days
        cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
        cursor.execute(
            """
            SELECT risk_indicators FROM betting_activity
            WHERE user_id = ? AND timestamp >= ?
        """,
            (user_id, cutoff_date),
        )

        all_indicators = []
        for row in cursor.fetchall():
            indicators = json.loads(row[0] or "[]")
            all_indicators.extend(indicators)

        conn.close()

        # Calculate risk score (0-1 scale)
        risk_score = 0.0

        # Count problematic patterns
        if all_indicators.count("RAPID_BETTING") >= 5:
            risk_score += 0.3
        if all_indicators.count("CHASING_LOSSES") >= 3:
            risk_score += 0.4
        if all_indicators.count("LARGE_BET") >= 10:
            risk_score += 0.2

        # Update profile
        profile = self.get_profile(user_id)
        if profile:
            profile.risk_assessment_score = min(1.0, risk_score)
            profile.last_assessment = datetime.now()

            # Add intervention flags if high risk
            if risk_score >= 0.7 and "HIGH_RISK" not in profile.intervention_flags:
                profile.intervention_flags.append("HIGH_RISK")

            self.save_profile(profile)


class APISecurityHardening:
    """API security hardening and protection mechanisms"""

    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.rate_limits = {}  # In-memory rate limiting (use Redis in production)
        self.blocked_ips = set()
        self.api_keys = {}  # Store in secure database in production

    def generate_api_key(self, user_id: str) -> str:
        """Generate secure API key for user"""

        # Generate random key
        key = secrets.token_urlsafe(32)

        # Store with user mapping (encrypt in production)
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        self.api_keys[key_hash] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "permissions": ["read", "write"],  # Configure as needed
            "rate_limit": 1000,  # Requests per hour
        }

        return key

    def validate_api_key(self, api_key: str) -> dict | None:
        """Validate API key and return user info"""

        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        if key_hash not in self.api_keys:
            return None

        # Update last used
        self.api_keys[key_hash]["last_used"] = datetime.now().isoformat()

        return self.api_keys[key_hash]

    def check_rate_limit(self, api_key: str, endpoint: str) -> bool:
        """Check API rate limiting"""

        rate_key = f"{api_key}:{endpoint}"
        current_time = int(time.time())
        window_start = current_time - 3600  # 1 hour window

        # Initialize if not exists
        if rate_key not in self.rate_limits:
            self.rate_limits[rate_key] = []

        # Clean old requests outside window
        self.rate_limits[rate_key] = [
            req_time for req_time in self.rate_limits[rate_key] if req_time > window_start
        ]

        # Check limit
        key_info = self.validate_api_key(api_key)
        if not key_info:
            return False

        limit = key_info.get("rate_limit", 100)

        if len(self.rate_limits[rate_key]) >= limit:
            return False

        # Add current request
        self.rate_limits[rate_key].append(current_time)

        return True

    def validate_request_signature(self, request_body: str, signature: str, api_key: str) -> bool:
        """Validate HMAC signature of request"""

        # Get API key info
        key_info = self.validate_api_key(api_key)
        if not key_info:
            return False

        # Calculate expected signature
        expected_sig = hmac.new(api_key.encode(), request_body.encode(), hashlib.sha256).hexdigest()

        # Compare signatures (constant time)
        return hmac.compare_digest(expected_sig, signature)

    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input to prevent injection attacks"""

        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\'\\\x00-\x1f\x7f-\x9f]', "", user_input)

        # Limit length
        sanitized = sanitized[:1000]

        return sanitized.strip()

    def check_ip_reputation(self, ip_address: str) -> bool:
        """Check if IP address is blocked or suspicious"""

        if ip_address in self.blocked_ips:
            return False

        # Add additional IP reputation checks here
        # (GeoIP, threat feeds, etc.)

        return True


async def main():
    """Demonstrate the security and compliance framework"""

    setup_utf8_logging()
    logging.info("🔒 Starting EQ12 Security & Compliance Framework")

    # Initialize components
    audit_logger = AuditLogger("C:/EQ12/data/security.db")
    rg_manager = ResponsibleGamingManager("C:/EQ12/data/security.db")
    api_security = APISecurityHardening()

    # Create sample user profile
    user_id = "user123"
    profile = rg_manager.create_user_profile(
        user_id, {"daily": 150.0, "weekly": 750.0, "monthly": 2500.0}
    )

    print(f"✅ Created RG profile for {user_id}")
    print(f"Daily limit: ${profile.daily_limit}")
    print(f"Risk score: {profile.risk_assessment_score}")

    # Test betting limits
    bet_check = rg_manager.check_betting_limits(user_id, 75.0)
    print(f"\n💰 Bet check for $75: {bet_check['allowed']}")

    if bet_check["allowed"]:
        # Record betting activity
        rg_manager.record_betting_activity(user_id, 75.0, "parlay", "session_123")
        print("✅ Betting activity recorded")

    # Generate API key
    api_key = api_security.generate_api_key(user_id)
    print(f"\n🔑 Generated API key: {api_key[:16]}...")

    # Test API security
    if api_security.check_rate_limit(api_key, "/api/predictions"):
        print("✅ Rate limit check passed")

    # Generate audit report
    report = audit_logger.get_audit_report(
        datetime.now() - timedelta(days=1), datetime.now(), user_id
    )

    print(f"\n📊 Audit report: {len(report)} entries")
    for entry in report[:3]:  # Show first 3 entries
        print(f"  {entry['timestamp']}: {entry['action']} - {entry['risk_level']}")

    print("\n🛡️ Security & Compliance Framework demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
