#!/usr/bin/env python3
"""
EQ12 OpenAI Key Engine
Advanced AI key management, rotation, optimization, and monetization system.
"""

import asyncio
import hashlib
import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import requests
import openai
from cryptography.fernet import Fernet
from dataclasses import dataclass
import psutil
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\openai_key_engine.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class APIKeyMetrics:
    """API Key performance metrics"""
    key_id: str
    total_requests: int
    total_tokens: int
    avg_latency: float
    error_rate: float
    daily_cost: float
    last_used: str
    status: str


@dataclass
class KeyRotationEvent:
    """Key rotation event record"""
    timestamp: str
    old_key_id: str
    new_key_id: str
    reason: str
    success: bool


class OpenAIKeyEngine:
    """Advanced OpenAI API Key Management System"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.config_path = self.workspace_path / "configs"
        self.keys_db_path = self.workspace_path / "data" / "openai_keys.db"
        self.cache_path = self.workspace_path / "data" / "ai_cache.db"
        
        # Create directories
        for path in [
            self.workspace_path / "data",
            self.workspace_path / "configs",
            self.workspace_path / "logs" / "openai"
        ]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize configuration
        self.config = self.load_config()
        self.init_databases()
        
        # Key pool management
        self.active_keys = {}
        self.key_rotation_schedule = {}
        
        # Performance tracking
        self.request_cache = {}
        self.usage_stats = {}
        
        # Encryption setup
        self.setup_encryption()
        
        logger.info("EQ12 OpenAI Key Engine initialized")

    def setup_encryption(self):
        """Setup encryption for key storage"""
        try:
            key_file = self.config_path / ".encryption_key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                self.encryption_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
                # Make file hidden on Windows
                if os.name == 'nt':
                    os.system(f'attrib +h "{key_file}"')
            
            self.cipher = Fernet(self.encryption_key)
            logger.info("Encryption setup completed")
            
        except Exception as e:
            logger.error(f"Encryption setup failed: {e}")
            raise

    def load_config(self) -> Dict:
        """Load OpenAI key management configuration"""
        default_config = {
            "key_rotation": {
                "auto_rotate": True,
                "rotation_interval_days": 30,
                "rotation_triggers": {
                    "high_usage_threshold": 0.85,
                    "error_rate_threshold": 0.05,
                    "latency_threshold": 5.0
                }
            },
            "load_balancing": {
                "enabled": True,
                "strategy": "round_robin",  # round_robin, least_used, performance_based
                "health_check_interval": 300
            },
            "optimization": {
                "caching_enabled": True,
                "cache_ttl_hours": 24,
                "compression_enabled": True,
                "batch_processing": True
            },
            "monitoring": {
                "real_time_alerts": True,
                "daily_reports": True,
                "performance_thresholds": {
                    "max_latency": 3.0,
                    "min_success_rate": 0.95,
                    "max_daily_cost": 150.0
                }
            },
            "security": {
                "key_masking": True,
                "audit_logging": True,
                "access_control": True
            },
            "monetization": {
                "api_gateway_enabled": False,
                "rate_limiting": {
                    "requests_per_minute": 60,
                    "requests_per_day": 10000
                },
                "pricing_tiers": {
                    "basic": {"cost_per_request": 0.01, "daily_limit": 100},
                    "premium": {"cost_per_request": 0.005, "daily_limit": 1000}
                }
            }
        }
        
        config_file = self.config_path / "openai_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Config load failed: {e}, using defaults")
        
        return default_config

    def init_databases(self):
        """Initialize key management databases"""
        try:
            # Keys management database
            with sqlite3.connect(self.keys_db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key_id TEXT UNIQUE NOT NULL,
                        encrypted_key TEXT NOT NULL,
                        key_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_rotation TEXT,
                        usage_quota REAL,
                        cost_limit REAL,
                        tags TEXT
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS key_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        requests_count INTEGER,
                        tokens_used INTEGER,
                        avg_latency REAL,
                        error_count INTEGER,
                        cost REAL,
                        model_used TEXT
                    )
                ''')
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS rotation_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        old_key_id TEXT,
                        new_key_id TEXT,
                        rotation_reason TEXT,
                        success BOOLEAN,
                        details TEXT
                    )
                ''')
                
                conn.commit()
            
            # Cache database
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ai_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt_hash TEXT UNIQUE NOT NULL,
                        prompt_text TEXT NOT NULL,
                        response_data TEXT NOT NULL,
                        model_used TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        usage_count INTEGER DEFAULT 1,
                        expires_at TEXT
                    )
                ''')
                
                conn.commit()
            
            logger.info("OpenAI databases initialized")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    # ===============================
    # KEY MANAGEMENT
    # ===============================
    
    def add_api_key(self, key: str, key_id: str, key_type: str = "production") -> bool:
        """Add new API key to management system"""
        try:
            # Encrypt the key
            encrypted_key = self.cipher.encrypt(key.encode()).decode()
            
            with sqlite3.connect(self.keys_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO api_keys 
                    (key_id, encrypted_key, key_type, status, created_at, usage_quota, cost_limit)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    key_id,
                    encrypted_key,
                    key_type,
                    "active",
                    datetime.now(timezone.utc).isoformat(),
                    100000,  # Default quota
                    500.0    # Default cost limit
                ))
                conn.commit()
            
            logger.info(f"API key added: {key_id[:8]}...{key_id[-4:]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add API key: {e}")
            return False

    def get_api_key(self, key_id: str) -> Optional[str]:
        """Retrieve and decrypt API key"""
        try:
            with sqlite3.connect(self.keys_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT encrypted_key FROM api_keys 
                    WHERE key_id = ? AND status = 'active'
                ''', (key_id,))
                
                result = cursor.fetchone()
                if result:
                    encrypted_key = result[0]
                    decrypted_key = self.cipher.decrypt(encrypted_key.encode()).decode()
                    return decrypted_key
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve API key: {e}")
            return None

    def get_active_keys(self) -> List[Dict]:
        """Get list of active API keys with metadata"""
        try:
            with sqlite3.connect(self.keys_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT key_id, key_type, status, created_at, last_rotation, 
                           usage_quota, cost_limit
                    FROM api_keys 
                    WHERE status = 'active'
                    ORDER BY created_at DESC
                ''')
                
                keys = []
                for row in cursor.fetchall():
                    keys.append({
                        "key_id": row[0],
                        "key_type": row[1],
                        "status": row[2],
                        "created_at": row[3],
                        "last_rotation": row[4],
                        "usage_quota": row[5],
                        "cost_limit": row[6]
                    })
                
                return keys
                
        except Exception as e:
            logger.error(f"Failed to get active keys: {e}")
            return []

    def select_optimal_key(self, task_type: str = "general") -> Optional[str]:
        """Select optimal API key based on current load and performance"""
        try:
            active_keys = self.get_active_keys()
            
            if not active_keys:
                logger.warning("No active API keys available")
                return None
            
            if len(active_keys) == 1:
                return active_keys[0]["key_id"]
            
            # Load balancing logic
            strategy = self.config["load_balancing"]["strategy"]
            
            if strategy == "round_robin":
                # Simple round-robin selection
                if not hasattr(self, '_key_index'):
                    self._key_index = 0
                key_id = active_keys[self._key_index]["key_id"]
                self._key_index = (self._key_index + 1) % len(active_keys)
                return key_id
                
            elif strategy == "performance_based":
                # Select key with best performance metrics
                best_key = None
                best_score = float('inf')
                
                for key_info in active_keys:
                    metrics = self.get_key_metrics(key_info["key_id"])
                    if metrics:
                        # Calculate performance score (lower is better)
                        score = (metrics.avg_latency * 0.4 + 
                                metrics.error_rate * 100 * 0.6)
                        if score < best_score:
                            best_score = score
                            best_key = key_info["key_id"]
                
                return best_key or active_keys[0]["key_id"]
            
            else:  # Default to first available
                return active_keys[0]["key_id"]
                
        except Exception as e:
            logger.error(f"Key selection failed: {e}")
            return None

    async def test_api_key(self, key_id: str) -> Dict:
        """Test API key performance and functionality"""
        try:
            api_key = self.get_api_key(key_id)
            if not api_key:
                return {"status": "error", "message": "Key not found"}
            
            # Test request
            start_time = time.time()
            
            openai.api_key = api_key
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test message. Respond with 'OK'."}],
                max_tokens=10,
                temperature=0
            )
            
            latency = time.time() - start_time
            
            # Update metrics
            await self.update_key_metrics(key_id, {
                "requests_count": 1,
                "tokens_used": response.usage.total_tokens,
                "latency": latency,
                "error_count": 0,
                "model_used": "gpt-3.5-turbo"
            })
            
            test_result = {
                "status": "success",
                "key_id": key_id[:8] + "..." + key_id[-4:],
                "latency": round(latency, 3),
                "tokens_used": response.usage.total_tokens,
                "response": response.choices[0].message.content.strip()
            }
            
            logger.info(f"API key test successful: {key_id[:8]}... ({latency:.3f}s)")
            return test_result
            
        except Exception as e:
            await self.update_key_metrics(key_id, {
                "requests_count": 1,
                "error_count": 1
            })
            
            logger.error(f"API key test failed: {e}")
            return {
                "status": "error",
                "key_id": key_id[:8] + "..." + key_id[-4:],
                "message": str(e)
            }

    # ===============================
    # CACHING & OPTIMIZATION
    # ===============================
    
    def generate_prompt_hash(self, prompt: str, model: str) -> str:
        """Generate hash for prompt caching"""
        combined = f"{prompt}|{model}"
        return hashlib.sha256(combined.encode()).hexdigest()

    async def get_cached_response(self, prompt: str, model: str) -> Optional[Dict]:
        """Retrieve cached AI response"""
        try:
            if not self.config["optimization"]["caching_enabled"]:
                return None
            
            prompt_hash = self.generate_prompt_hash(prompt, model)
            
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT response_data, timestamp, expires_at, usage_count
                    FROM ai_cache 
                    WHERE prompt_hash = ?
                ''', (prompt_hash,))
                
                result = cursor.fetchone()
                if result:
                    response_data, timestamp, expires_at, usage_count = result
                    
                    # Check expiration
                    if expires_at and datetime.fromisoformat(expires_at) < datetime.now(timezone.utc):
                        return None
                    
                    # Update usage count
                    cursor.execute('''
                        UPDATE ai_cache 
                        SET usage_count = usage_count + 1 
                        WHERE prompt_hash = ?
                    ''', (prompt_hash,))
                    conn.commit()
                    
                    logger.info(f"Cache hit for prompt hash: {prompt_hash[:16]}...")
                    return json.loads(response_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None

    async def cache_response(self, prompt: str, model: str, response: Dict):
        """Cache AI response for future use"""
        try:
            if not self.config["optimization"]["caching_enabled"]:
                return
            
            prompt_hash = self.generate_prompt_hash(prompt, model)
            expires_at = datetime.now(timezone.utc) + timedelta(
                hours=self.config["optimization"]["cache_ttl_hours"]
            )
            
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO ai_cache 
                    (prompt_hash, prompt_text, response_data, model_used, 
                     timestamp, expires_at, usage_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prompt_hash,
                    prompt[:1000],  # Truncate for storage
                    json.dumps(response),
                    model,
                    datetime.now(timezone.utc).isoformat(),
                    expires_at.isoformat(),
                    1
                ))
                conn.commit()
            
            logger.debug(f"Response cached: {prompt_hash[:16]}...")
            
        except Exception as e:
            logger.error(f"Caching failed: {e}")

    async def optimized_ai_request(self, prompt: str, model: str = "gpt-4", **kwargs) -> Dict:
        """Make optimized AI request with caching and load balancing"""
        try:
            # Check cache first
            cached_response = await self.get_cached_response(prompt, model)
            if cached_response:
                return {
                    "status": "success",
                    "source": "cache",
                    "response": cached_response
                }
            
            # Select optimal API key
            key_id = self.select_optimal_key()
            if not key_id:
                return {"status": "error", "message": "No API keys available"}
            
            api_key = self.get_api_key(key_id)
            if not api_key:
                return {"status": "error", "message": "Failed to retrieve API key"}
            
            # Make request
            start_time = time.time()
            
            openai.api_key = api_key
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            latency = time.time() - start_time
            
            # Update metrics
            await self.update_key_metrics(key_id, {
                "requests_count": 1,
                "tokens_used": response.usage.total_tokens,
                "latency": latency,
                "error_count": 0,
                "model_used": model
            })
            
            # Cache response
            response_dict = {
                "choices": [{"message": {"content": response.choices[0].message.content}}],
                "usage": dict(response.usage)
            }
            await self.cache_response(prompt, model, response_dict)
            
            return {
                "status": "success",
                "source": "api",
                "key_id": key_id[:8] + "..." + key_id[-4:],
                "latency": latency,
                "response": response_dict
            }
            
        except Exception as e:
            logger.error(f"Optimized AI request failed: {e}")
            return {"status": "error", "message": str(e)}

    # ===============================
    # METRICS & MONITORING
    # ===============================
    
    async def update_key_metrics(self, key_id: str, metrics: Dict):
        """Update API key performance metrics"""
        try:
            with sqlite3.connect(self.keys_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO key_metrics 
                    (key_id, timestamp, requests_count, tokens_used, avg_latency, 
                     error_count, cost, model_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    key_id,
                    datetime.now(timezone.utc).isoformat(),
                    metrics.get("requests_count", 0),
                    metrics.get("tokens_used", 0),
                    metrics.get("latency", 0.0),
                    metrics.get("error_count", 0),
                    metrics.get("cost", 0.0),
                    metrics.get("model_used", "unknown")
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Metrics update failed: {e}")

    def get_key_metrics(self, key_id: str, hours: int = 24) -> Optional[APIKeyMetrics]:
        """Get aggregated metrics for API key"""
        try:
            time_threshold = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            with sqlite3.connect(self.keys_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_requests,
                        SUM(tokens_used) as total_tokens,
                        AVG(avg_latency) as avg_latency,
                        SUM(error_count) * 1.0 / COUNT(*) as error_rate,
                        SUM(cost) as daily_cost,
                        MAX(timestamp) as last_used
                    FROM key_metrics 
                    WHERE key_id = ? AND timestamp > ?
                ''', (key_id, time_threshold))
                
                result = cursor.fetchone()
                if result and result[0] > 0:
                    return APIKeyMetrics(
                        key_id=key_id,
                        total_requests=result[0],
                        total_tokens=result[1] or 0,
                        avg_latency=result[2] or 0.0,
                        error_rate=result[3] or 0.0,
                        daily_cost=result[4] or 0.0,
                        last_used=result[5] or "",
                        status="active"
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Metrics retrieval failed: {e}")
            return None

    async def generate_key_health_report(self) -> Dict:
        """Generate comprehensive key health report"""
        try:
            active_keys = self.get_active_keys()
            report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_keys": len(active_keys),
                "key_details": [],
                "summary": {
                    "total_requests_24h": 0,
                    "total_tokens_24h": 0,
                    "avg_latency": 0.0,
                    "total_cost_24h": 0.0,
                    "overall_error_rate": 0.0
                }
            }
            
            total_requests = 0
            total_latency = 0
            total_errors = 0
            
            for key_info in active_keys:
                metrics = self.get_key_metrics(key_info["key_id"])
                
                if metrics:
                    key_detail = {
                        "key_id": key_info["key_id"][:8] + "..." + key_info["key_id"][-4:],
                        "requests_24h": metrics.total_requests,
                        "tokens_24h": metrics.total_tokens,
                        "avg_latency": round(metrics.avg_latency, 3),
                        "error_rate": round(metrics.error_rate * 100, 2),
                        "cost_24h": round(metrics.daily_cost, 2),
                        "status": "healthy" if metrics.error_rate < 0.05 else "warning",
                        "last_used": metrics.last_used
                    }
                    
                    report["key_details"].append(key_detail)
                    
                    # Aggregate for summary
                    report["summary"]["total_requests_24h"] += metrics.total_requests
                    report["summary"]["total_tokens_24h"] += metrics.total_tokens
                    report["summary"]["total_cost_24h"] += metrics.daily_cost
                    
                    total_requests += metrics.total_requests
                    total_latency += metrics.avg_latency * metrics.total_requests
                    total_errors += metrics.error_rate * metrics.total_requests
            
            # Calculate averages
            if total_requests > 0:
                report["summary"]["avg_latency"] = round(total_latency / total_requests, 3)
                report["summary"]["overall_error_rate"] = round((total_errors / total_requests) * 100, 2)
            
            return report
            
        except Exception as e:
            logger.error(f"Health report generation failed: {e}")
            return {"error": str(e)}

    # ===============================
    # KEY ROTATION
    # ===============================
    
    async def should_rotate_key(self, key_id: str) -> Tuple[bool, str]:
        """Determine if key should be rotated"""
        try:
            metrics = self.get_key_metrics(key_id)
            if not metrics:
                return False, "No metrics available"
            
            triggers = self.config["key_rotation"]["rotation_triggers"]
            
            # Check error rate
            if metrics.error_rate > triggers["error_rate_threshold"]:
                return True, f"High error rate: {metrics.error_rate:.2%}"
            
            # Check latency
            if metrics.avg_latency > triggers["latency_threshold"]:
                return True, f"High latency: {metrics.avg_latency:.2f}s"
            
            # Check usage threshold
            daily_requests = metrics.total_requests
            if daily_requests > triggers["high_usage_threshold"] * 10000:  # Assuming 10k daily limit
                return True, f"High usage: {daily_requests} requests"
            
            # Check age-based rotation
            with sqlite3.connect(self.keys_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT created_at, last_rotation FROM api_keys WHERE key_id = ?
                ''', (key_id,))
                
                result = cursor.fetchone()
                if result:
                    last_rotation = result[1] if result[1] else result[0]
                    rotation_date = datetime.fromisoformat(last_rotation)
                    days_since_rotation = (datetime.now(timezone.utc) - rotation_date).days
                    
                    rotation_interval = self.config["key_rotation"]["rotation_interval_days"]
                    if days_since_rotation >= rotation_interval:
                        return True, f"Scheduled rotation: {days_since_rotation} days"
            
            return False, "Key is healthy"
            
        except Exception as e:
            logger.error(f"Rotation check failed: {e}")
            return False, f"Check failed: {e}"

    async def rotate_api_key(self, old_key_id: str, new_key: str) -> bool:
        """Rotate API key with new key"""
        try:
            # Generate new key ID
            new_key_id = f"openai_key_{int(time.time())}"
            
            # Add new key
            if not self.add_api_key(new_key, new_key_id):
                return False
            
            # Test new key
            test_result = await self.test_api_key(new_key_id)
            if test_result["status"] != "success":
                logger.error(f"New key test failed: {test_result}")
                return False
            
            # Deactivate old key
            with sqlite3.connect(self.keys_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE api_keys SET status = 'rotated' WHERE key_id = ?
                ''', (old_key_id,))
                
                # Log rotation
                cursor.execute('''
                    INSERT INTO rotation_log 
                    (timestamp, old_key_id, new_key_id, rotation_reason, success, details)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now(timezone.utc).isoformat(),
                    old_key_id,
                    new_key_id,
                    "Manual rotation",
                    True,
                    json.dumps(test_result)
                ))
                
                conn.commit()
            
            logger.info(f"Key rotation successful: {old_key_id[:8]}...  {new_key_id[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            return False

    # ===============================
    # MONETIZATION FEATURES
    # ===============================
    
    async def create_api_gateway(self, port: int = 8080) -> bool:
        """Create API gateway for monetizing key access"""
        try:
            # This would implement a Flask/FastAPI gateway
            # For now, just log the capability
            logger.info(f"API Gateway setup initiated on port {port}")
            
            gateway_config = {
                "enabled": True,
                "port": port,
                "rate_limits": self.config["monetization"]["rate_limiting"],
                "pricing": self.config["monetization"]["pricing_tiers"]
            }
            
            # Save gateway config
            with open(self.config_path / "gateway_config.json", 'w') as f:
                json.dump(gateway_config, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"API Gateway setup failed: {e}")
            return False

    # ===============================
    # MAIN CONTROL FUNCTIONS
    # ===============================
    
    async def run_health_monitoring(self):
        """Continuous health monitoring loop"""
        logger.info("Starting OpenAI key health monitoring...")
        
        while True:
            try:
                # Generate health report
                report = await self.generate_key_health_report()
                
                # Check for issues
                for key_detail in report.get("key_details", []):
                    if key_detail["status"] == "warning":
                        logger.warning(f"Key health warning: {key_detail}")
                
                # Auto-rotation checks
                if self.config["key_rotation"]["auto_rotate"]:
                    active_keys = self.get_active_keys()
                    
                    for key_info in active_keys:
                        should_rotate, reason = await self.should_rotate_key(key_info["key_id"])
                        if should_rotate:
                            logger.info(f"Key rotation triggered: {reason}")
                            # In production, this would trigger actual rotation
                
                # Sleep until next check
                await asyncio.sleep(self.config["load_balancing"]["health_check_interval"])
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        try:
            with sqlite3.connect(self.cache_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM ai_cache 
                    WHERE expires_at < ? AND expires_at IS NOT NULL
                ''', (datetime.now(timezone.utc).isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} expired cache entries")
                    
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 OpenAI Key Engine")
    parser.add_argument("--workspace", default="C:\\EQ12", help="Workspace path")
    parser.add_argument("--add-key", help="Add new API key")
    parser.add_argument("--key-id", help="Key ID for operations")
    parser.add_argument("--test-all", action="store_true", help="Test all active keys")
    parser.add_argument("--health-report", action="store_true", help="Generate health report")
    parser.add_argument("--monitor", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--cleanup-cache", action="store_true", help="Clean expired cache")
    
    args = parser.parse_args()
    
    engine = OpenAIKeyEngine(args.workspace)
    
    if args.add_key:
        if not args.key_id:
            key_id = f"openai_key_{int(time.time())}"
        else:
            key_id = args.key_id
        
        success = engine.add_api_key(args.add_key, key_id)
        print(f"Key addition: {'Success' if success else 'Failed'}")
        return 0
    
    if args.test_all:
        async def test_all():
            active_keys = engine.get_active_keys()
            for key_info in active_keys:
                result = await engine.test_api_key(key_info["key_id"])
                print(json.dumps(result, indent=2))
        asyncio.run(test_all())
        return 0
    
    if args.health_report:
        async def health_report():
            report = await engine.generate_key_health_report()
            print(json.dumps(report, indent=2))
        asyncio.run(health_report())
        return 0
    
    if args.cleanup_cache:
        async def cleanup():
            await engine.cleanup_expired_cache()
        asyncio.run(cleanup())
        return 0
    
    if args.monitor:
        try:
            asyncio.run(engine.run_health_monitoring())
        except KeyboardInterrupt:
            logger.info("Monitoring stopped")
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())