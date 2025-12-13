#!/usr/bin/env python3
"""
EQ12 Telegram Router
Advanced message routing, chat management, and token-gated access system.
Supports multiple chat types, dynamic routing, and blockchain integration.
"""

import asyncio
import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\telegram_router.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Message type enumeration"""
    ALERT = "alert"
    SYSTEM = "system"
    FINANCIAL = "financial"
    BETTING = "betting"
    AI = "ai"
    COMMAND = "command"
    BROADCAST = "broadcast"
    NOTIFICATION = "notification"


class Priority(Enum):
    """Message priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ChatType(Enum):
    """Chat type enumeration"""
    ADMIN = "admin"
    CHANNEL = "channel"
    GROUP = "group"
    SUBSCRIBER = "subscriber"
    VIP = "vip"
    PUBLIC = "public"


@dataclass
class ChatConfig:
    """Chat configuration data structure"""
    chat_id: int
    chat_type: ChatType
    username: Optional[str] = None
    wallet_address: Optional[str] = None
    token_balance: float = 0.0
    access_level: int = 0
    message_types: Set[MessageType] = None
    rate_limit: int = 10
    enabled: bool = True
    created_at: str = ""
    last_active: str = ""


@dataclass
class RouteRule:
    """Message routing rule"""
    message_type: MessageType
    priority: Priority
    target_chats: List[ChatType]
    conditions: Dict[str, Any] = None
    rate_limit: int = 0
    token_threshold: float = 0.0
    access_level: int = 0


@dataclass
class QueuedMessage:
    """Queued message for delivery"""
    id: str
    message_type: MessageType
    priority: Priority
    title: str
    content: str
    target_chats: List[int]
    created_at: str
    scheduled_at: Optional[str] = None
    attempts: int = 0
    delivered: bool = False
    error_message: Optional[str] = None


class EQ12TelegramRouter:
    """Advanced Telegram message routing and management system"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "data" / "telegram_router.db"
        self.config_path = self.workspace_path / "configs" / "telegram_router_config.json"
        self.api_endpoint = "https://api.telegram.org"
        
        # Create directories
        for path in [
            self.workspace_path / "data",
            self.workspace_path / "logs" / "telegram",
            self.workspace_path / "configs"
        ]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self.load_configuration()
        self.routing_rules = self.load_routing_rules()
        self.chat_configs: Dict[int, ChatConfig] = {}
        
        # Initialize database
        self.init_database()
        
        # Load chat configurations
        self.load_chat_configs()
        
        # Telegram credentials
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        
        # Message queue
        self.message_queue: List[QueuedMessage] = []
        self.rate_limits: Dict[int, List[float]] = {}
        
        logger.info("EQ12 Telegram Router initialized")

    def load_configuration(self) -> Dict:
        """Load router configuration"""
        default_config = {
            "global_rate_limit": 30,  # messages per minute
            "retry_attempts": 3,
            "retry_delay": 60,  # seconds
            "queue_max_size": 1000,
            "token_verification": {
                "enabled": False,
                "contract_address": "",
                "required_balance": 1.0
            },
            "message_types": {
                "alert": {"enabled": True, "default_priority": "high"},
                "system": {"enabled": True, "default_priority": "medium"},
                "financial": {"enabled": True, "default_priority": "high"},
                "betting": {"enabled": True, "default_priority": "medium"},
                "ai": {"enabled": True, "default_priority": "low"},
                "notification": {"enabled": True, "default_priority": "low"}
            },
            "webhook_integration": {
                "enabled": False,
                "port": 8443,
                "ssl_cert": "",
                "ssl_key": ""
            }
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                # Create default config
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return default_config

    def load_routing_rules(self) -> List[RouteRule]:
        """Load message routing rules"""
        default_rules = [
            RouteRule(
                message_type=MessageType.ALERT,
                priority=Priority.CRITICAL,
                target_chats=[ChatType.ADMIN],
                access_level=0
            ),
            RouteRule(
                message_type=MessageType.SYSTEM,
                priority=Priority.HIGH,
                target_chats=[ChatType.ADMIN],
                access_level=0
            ),
            RouteRule(
                message_type=MessageType.FINANCIAL,
                priority=Priority.HIGH,
                target_chats=[ChatType.ADMIN, ChatType.VIP],
                token_threshold=10.0,
                access_level=1
            ),
            RouteRule(
                message_type=MessageType.BETTING,
                priority=Priority.MEDIUM,
                target_chats=[ChatType.ADMIN, ChatType.SUBSCRIBER],
                token_threshold=1.0,
                access_level=1
            ),
            RouteRule(
                message_type=MessageType.AI,
                priority=Priority.LOW,
                target_chats=[ChatType.ADMIN, ChatType.SUBSCRIBER],
                access_level=0
            ),
            RouteRule(
                message_type=MessageType.BROADCAST,
                priority=Priority.MEDIUM,
                target_chats=[ChatType.CHANNEL, ChatType.GROUP],
                rate_limit=5,
                access_level=0
            )
        ]
        
        rules_file = self.workspace_path / "configs" / "routing_rules.json"
        
        try:
            if rules_file.exists():
                with open(rules_file) as f:
                    rules_data = json.load(f)
                
                rules = []
                for rule_data in rules_data:
                    rule = RouteRule(
                        message_type=MessageType(rule_data["message_type"]),
                        priority=Priority(rule_data["priority"]),
                        target_chats=[ChatType(ct) for ct in rule_data["target_chats"]],
                        conditions=rule_data.get("conditions"),
                        rate_limit=rule_data.get("rate_limit", 0),
                        token_threshold=rule_data.get("token_threshold", 0.0),
                        access_level=rule_data.get("access_level", 0)
                    )
                    rules.append(rule)
                
                return rules
            else:
                # Save default rules
                rules_data = []
                for rule in default_rules:
                    rule_dict = {
                        "message_type": rule.message_type.value,
                        "priority": rule.priority.value,
                        "target_chats": [ct.value for ct in rule.target_chats],
                        "conditions": rule.conditions,
                        "rate_limit": rule.rate_limit,
                        "token_threshold": rule.token_threshold,
                        "access_level": rule.access_level
                    }
                    rules_data.append(rule_dict)
                
                with open(rules_file, 'w') as f:
                    json.dump(rules_data, f, indent=2)
                
                return default_rules
                
        except Exception as e:
            logger.error(f"Failed to load routing rules: {e}")
            return default_rules

    def init_database(self):
        """Initialize SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Chat configurations table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS chat_configs (
                        chat_id INTEGER PRIMARY KEY,
                        chat_type TEXT NOT NULL,
                        username TEXT,
                        wallet_address TEXT,
                        token_balance REAL DEFAULT 0.0,
                        access_level INTEGER DEFAULT 0,
                        message_types TEXT,
                        rate_limit INTEGER DEFAULT 10,
                        enabled BOOLEAN DEFAULT TRUE,
                        created_at TEXT NOT NULL,
                        last_active TEXT
                    )
                """)
                
                # Message queue table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS message_queue (
                        id TEXT PRIMARY KEY,
                        message_type TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        target_chats TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        scheduled_at TEXT,
                        attempts INTEGER DEFAULT 0,
                        delivered BOOLEAN DEFAULT FALSE,
                        error_message TEXT
                    )
                """)
                
                # Delivery log table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS delivery_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message_id TEXT NOT NULL,
                        chat_id INTEGER NOT NULL,
                        delivered_at TEXT NOT NULL,
                        success BOOLEAN NOT NULL,
                        response_code INTEGER,
                        error_message TEXT
                    )
                """)
                
                # Analytics table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS message_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        message_type TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        total_sent INTEGER DEFAULT 0,
                        total_delivered INTEGER DEFAULT 0,
                        total_failed INTEGER DEFAULT 0,
                        avg_delivery_time REAL DEFAULT 0.0
                    )
                """)
                
                conn.commit()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def load_chat_configs(self):
        """Load chat configurations from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT chat_id, chat_type, username, wallet_address, 
                           token_balance, access_level, message_types, 
                           rate_limit, enabled, created_at, last_active
                    FROM chat_configs
                """)
                
                for row in cursor.fetchall():
                    chat_id = row[0]
                    message_types = set()
                    
                    if row[6]:  # message_types JSON
                        try:
                            types_list = json.loads(row[6])
                            message_types = {MessageType(t) for t in types_list}
                        except:
                            pass
                    
                    config = ChatConfig(
                        chat_id=chat_id,
                        chat_type=ChatType(row[1]),
                        username=row[2],
                        wallet_address=row[3],
                        token_balance=row[4] or 0.0,
                        access_level=row[5] or 0,
                        message_types=message_types,
                        rate_limit=row[7] or 10,
                        enabled=bool(row[8]),
                        created_at=row[9] or "",
                        last_active=row[10] or ""
                    )
                    
                    self.chat_configs[chat_id] = config
                    
        except Exception as e:
            logger.error(f"Failed to load chat configs: {e}")

    def register_chat(self, chat_id: int, chat_type: ChatType, 
                     username: str = None, wallet_address: str = None) -> bool:
        """Register a new chat configuration"""
        try:
            # Default message types based on chat type
            default_types = {
                ChatType.ADMIN: [MessageType.ALERT, MessageType.SYSTEM, MessageType.FINANCIAL, MessageType.BETTING, MessageType.AI],
                ChatType.VIP: [MessageType.FINANCIAL, MessageType.BETTING, MessageType.AI],
                ChatType.SUBSCRIBER: [MessageType.BETTING, MessageType.AI, MessageType.NOTIFICATION],
                ChatType.CHANNEL: [MessageType.BROADCAST, MessageType.NOTIFICATION],
                ChatType.GROUP: [MessageType.BROADCAST, MessageType.NOTIFICATION],
                ChatType.PUBLIC: [MessageType.NOTIFICATION]
            }
            
            message_types = set(default_types.get(chat_type, [MessageType.NOTIFICATION]))
            
            config = ChatConfig(
                chat_id=chat_id,
                chat_type=chat_type,
                username=username,
                wallet_address=wallet_address,
                message_types=message_types,
                created_at=datetime.now(timezone.utc).isoformat()
            )
            
            self.chat_configs[chat_id] = config
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO chat_configs 
                    (chat_id, chat_type, username, wallet_address, 
                     message_types, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    chat_id, chat_type.value, username, wallet_address,
                    json.dumps([t.value for t in message_types]),
                    config.created_at
                ))
                conn.commit()
            
            logger.info(f"Registered chat {chat_id} as {chat_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register chat {chat_id}: {e}")
            return False

    def update_token_balance(self, chat_id: int, balance: float) -> bool:
        """Update token balance for a chat"""
        try:
            if chat_id in self.chat_configs:
                self.chat_configs[chat_id].token_balance = balance
                
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE chat_configs 
                        SET token_balance = ? 
                        WHERE chat_id = ?
                    """, (balance, chat_id))
                    conn.commit()
                
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update token balance for {chat_id}: {e}")
            return False

    def check_access_permissions(self, chat_id: int, message_type: MessageType, 
                               priority: Priority) -> bool:
        """Check if chat has access permissions for message type"""
        if chat_id not in self.chat_configs:
            return False
        
        config = self.chat_configs[chat_id]
        
        # Check if chat is enabled
        if not config.enabled:
            return False
        
        # Check message type permissions
        if config.message_types and message_type not in config.message_types:
            return False
        
        # Find applicable routing rule
        for rule in self.routing_rules:
            if rule.message_type == message_type and rule.priority == priority:
                # Check chat type
                if config.chat_type not in rule.target_chats:
                    continue
                
                # Check access level
                if config.access_level < rule.access_level:
                    return False
                
                # Check token balance
                if rule.token_threshold > 0 and config.token_balance < rule.token_threshold:
                    return False
                
                return True
        
        return False

    def check_rate_limits(self, chat_id: int) -> bool:
        """Check rate limits for a chat"""
        current_time = time.time()
        
        if chat_id not in self.rate_limits:
            self.rate_limits[chat_id] = []
        
        # Clean old timestamps (older than 1 minute)
        self.rate_limits[chat_id] = [
            ts for ts in self.rate_limits[chat_id] 
            if current_time - ts < 60
        ]
        
        # Get rate limit for chat
        config = self.chat_configs.get(chat_id)
        limit = config.rate_limit if config else self.config["global_rate_limit"]
        
        # Check if under limit
        if len(self.rate_limits[chat_id]) < limit:
            self.rate_limits[chat_id].append(current_time)
            return True
        
        return False

    async def route_message(self, message_type: MessageType, priority: Priority,
                          title: str, content: str, conditions: Dict = None) -> str:
        """Route message based on type and rules"""
        message_id = f"{int(time.time())}_{hash(content) % 10000}"
        
        try:
            # Find applicable routing rules
            applicable_rules = [
                rule for rule in self.routing_rules
                if rule.message_type == message_type and rule.priority == priority
            ]
            
            if not applicable_rules:
                logger.warning(f"No routing rules found for {message_type.value}/{priority.value}")
                return message_id
            
            # Collect target chats
            target_chats = []
            
            for rule in applicable_rules:
                for chat_id, config in self.chat_configs.items():
                    if config.chat_type in rule.target_chats:
                        if self.check_access_permissions(chat_id, message_type, priority):
                            if self.check_rate_limits(chat_id):
                                target_chats.append(chat_id)
                            else:
                                logger.warning(f"Rate limit exceeded for chat {chat_id}")
            
            if not target_chats:
                logger.warning(f"No eligible targets for message {message_id}")
                return message_id
            
            # Create queued message
            queued_msg = QueuedMessage(
                id=message_id,
                message_type=message_type,
                priority=priority,
                title=title,
                content=content,
                target_chats=target_chats,
                created_at=datetime.now(timezone.utc).isoformat()
            )
            
            # Add to queue
            await self.add_to_queue(queued_msg)
            
            logger.info(f"Message {message_id} routed to {len(target_chats)} chats")
            return message_id
            
        except Exception as e:
            logger.error(f"Message routing failed: {e}")
            return message_id

    async def add_to_queue(self, message: QueuedMessage):
        """Add message to delivery queue"""
        try:
            # Add to memory queue
            self.message_queue.append(message)
            
            # Sort by priority
            priority_order = {
                Priority.CRITICAL: 0,
                Priority.HIGH: 1,
                Priority.MEDIUM: 2,
                Priority.LOW: 3
            }
            
            self.message_queue.sort(key=lambda m: priority_order.get(m.priority, 3))
            
            # Keep queue size manageable
            max_size = self.config["queue_max_size"]
            if len(self.message_queue) > max_size:
                self.message_queue = self.message_queue[:max_size]
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO message_queue 
                    (id, message_type, priority, title, content, target_chats, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    message.id, message.message_type.value, message.priority.value,
                    message.title, message.content, json.dumps(message.target_chats),
                    message.created_at
                ))
                conn.commit()
            
        except Exception as e:
            logger.error(f"Failed to add message to queue: {e}")

    async def process_queue(self):
        """Process message delivery queue"""
        while True:
            try:
                if not self.message_queue:
                    await asyncio.sleep(5)
                    continue
                
                # Get next message
                message = self.message_queue.pop(0)
                
                # Attempt delivery
                success_count = 0
                for chat_id in message.target_chats:
                    if await self.deliver_message(chat_id, message):
                        success_count += 1
                
                # Update message status
                message.attempts += 1
                message.delivered = success_count > 0
                
                # Retry logic for failed messages
                if not message.delivered and message.attempts < self.config["retry_attempts"]:
                    # Re-queue for retry
                    message.scheduled_at = datetime.fromtimestamp(
                        time.time() + self.config["retry_delay"]
                    ).isoformat()
                    self.message_queue.append(message)
                
                # Update database
                await self.update_message_status(message)
                
                # Update analytics
                await self.update_analytics(message, success_count)
                
                await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(10)

    async def deliver_message(self, chat_id: int, message: QueuedMessage) -> bool:
        """Deliver message to specific chat"""
        try:
            if not self.bot_token:
                return False
            
            # Format message based on type
            formatted_content = self.format_message(message)
            
            # Send via Telegram API
            url = f"{self.api_endpoint}/bot{self.bot_token}/sendMessage"
            
            payload = {
                "chat_id": chat_id,
                "text": formatted_content,
                "parse_mode": "Markdown",
                "disable_notification": message.priority == Priority.LOW
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            # Log delivery attempt
            await self.log_delivery(message.id, chat_id, response)
            
            # Update last active for chat
            if chat_id in self.chat_configs:
                self.chat_configs[chat_id].last_active = datetime.now(timezone.utc).isoformat()
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Message delivery failed for chat {chat_id}: {e}")
            await self.log_delivery(message.id, chat_id, None, str(e))
            return False

    def format_message(self, message: QueuedMessage) -> str:
        """Format message based on type and priority"""
        # Priority icons
        priority_icons = {
            Priority.CRITICAL: "",
            Priority.HIGH: "",
            Priority.MEDIUM: "",
            Priority.LOW: ""
        }
        
        # Type icons
        type_icons = {
            MessageType.ALERT: "",
            MessageType.SYSTEM: "",
            MessageType.FINANCIAL: "",
            MessageType.BETTING: "",
            MessageType.AI: "",
            MessageType.BROADCAST: "",
            MessageType.NOTIFICATION: ""
        }
        
        priority_icon = priority_icons.get(message.priority, "")
        type_icon = type_icons.get(message.message_type, "")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        formatted = f"{priority_icon} {type_icon} **{message.title}**\n\n"
        formatted += f"{message.content}\n\n"
        formatted += f"*{message.message_type.value.upper()} | {timestamp}*"
        
        return formatted

    async def log_delivery(self, message_id: str, chat_id: int, response: requests.Response = None, error: str = None):
        """Log delivery attempt"""
        try:
            success = response is not None and response.status_code == 200
            response_code = response.status_code if response else None
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO delivery_log 
                    (message_id, chat_id, delivered_at, success, response_code, error_message)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    message_id, chat_id, datetime.now(timezone.utc).isoformat(),
                    success, response_code, error
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log delivery: {e}")

    async def update_message_status(self, message: QueuedMessage):
        """Update message status in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE message_queue 
                    SET attempts = ?, delivered = ?, error_message = ?
                    WHERE id = ?
                """, (message.attempts, message.delivered, message.error_message, message.id))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update message status: {e}")

    async def update_analytics(self, message: QueuedMessage, success_count: int):
        """Update delivery analytics"""
        try:
            date = datetime.now().strftime("%Y-%m-%d")
            failed_count = len(message.target_chats) - success_count
            
            with sqlite3.connect(self.db_path) as conn:
                # Check if entry exists for today
                cursor = conn.execute("""
                    SELECT total_sent, total_delivered, total_failed 
                    FROM message_analytics 
                    WHERE date = ? AND message_type = ? AND priority = ?
                """, (date, message.message_type.value, message.priority.value))
                
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing
                    conn.execute("""
                        UPDATE message_analytics 
                        SET total_sent = total_sent + ?, 
                            total_delivered = total_delivered + ?,
                            total_failed = total_failed + ?
                        WHERE date = ? AND message_type = ? AND priority = ?
                    """, (
                        len(message.target_chats), success_count, failed_count,
                        date, message.message_type.value, message.priority.value
                    ))
                else:
                    # Insert new
                    conn.execute("""
                        INSERT INTO message_analytics 
                        (date, message_type, priority, total_sent, total_delivered, total_failed)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        date, message.message_type.value, message.priority.value,
                        len(message.target_chats), success_count, failed_count
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to update analytics: {e}")

    # Token Verification Methods
    async def verify_token_balance(self, wallet_address: str) -> float:
        """Verify token balance for wallet (placeholder for blockchain integration)"""
        try:
            # This would integrate with actual blockchain API
            # For now, return mock balance
            if wallet_address:
                # Mock verification - replace with real Web3 integration
                return 10.0
            return 0.0
        except Exception as e:
            logger.error(f"Token verification failed for {wallet_address}: {e}")
            return 0.0

    async def update_all_token_balances(self):
        """Update token balances for all registered wallets"""
        for chat_id, config in self.chat_configs.items():
            if config.wallet_address:
                balance = await self.verify_token_balance(config.wallet_address)
                self.update_token_balance(chat_id, balance)

    # API Integration Methods
    async def send_alert(self, alert_type: str, title: str, content: str, priority: str = "medium"):
        """Send alert through router system"""
        try:
            message_type = MessageType.ALERT
            msg_priority = Priority(priority.lower())
            
            return await self.route_message(message_type, msg_priority, title, content)
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return None

    async def send_financial_update(self, title: str, content: str, priority: str = "high"):
        """Send financial update"""
        try:
            return await self.route_message(MessageType.FINANCIAL, Priority(priority), title, content)
        except Exception as e:
            logger.error(f"Failed to send financial update: {e}")
            return None

    async def send_betting_signal(self, title: str, content: str, priority: str = "medium"):
        """Send betting signal"""
        try:
            return await self.route_message(MessageType.BETTING, Priority(priority), title, content)
        except Exception as e:
            logger.error(f"Failed to send betting signal: {e}")
            return None

    async def broadcast_announcement(self, title: str, content: str, priority: str = "medium"):
        """Broadcast announcement to channels/groups"""
        try:
            return await self.route_message(MessageType.BROADCAST, Priority(priority), title, content)
        except Exception as e:
            logger.error(f"Failed to broadcast announcement: {e}")
            return None

    # Dashboard Integration
    def get_analytics_summary(self, days: int = 7) -> Dict:
        """Get analytics summary for dashboard"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT message_type, priority, 
                           SUM(total_sent) as sent,
                           SUM(total_delivered) as delivered,
                           SUM(total_failed) as failed
                    FROM message_analytics 
                    WHERE date >= date('now', '-{} days')
                    GROUP BY message_type, priority
                """.format(days))
                
                analytics = {
                    "summary": {
                        "total_sent": 0,
                        "total_delivered": 0,
                        "total_failed": 0,
                        "delivery_rate": 0.0
                    },
                    "by_type": {},
                    "by_priority": {}
                }
                
                for row in cursor.fetchall():
                    msg_type, priority, sent, delivered, failed = row
                    
                    analytics["summary"]["total_sent"] += sent
                    analytics["summary"]["total_delivered"] += delivered
                    analytics["summary"]["total_failed"] += failed
                    
                    if msg_type not in analytics["by_type"]:
                        analytics["by_type"][msg_type] = {"sent": 0, "delivered": 0, "failed": 0}
                    
                    analytics["by_type"][msg_type]["sent"] += sent
                    analytics["by_type"][msg_type]["delivered"] += delivered
                    analytics["by_type"][msg_type]["failed"] += failed
                    
                    if priority not in analytics["by_priority"]:
                        analytics["by_priority"][priority] = {"sent": 0, "delivered": 0, "failed": 0}
                    
                    analytics["by_priority"][priority]["sent"] += sent
                    analytics["by_priority"][priority]["delivered"] += delivered
                    analytics["by_priority"][priority]["failed"] += failed
                
                # Calculate delivery rate
                total_sent = analytics["summary"]["total_sent"]
                if total_sent > 0:
                    analytics["summary"]["delivery_rate"] = (
                        analytics["summary"]["total_delivered"] / total_sent * 100
                    )
                
                return analytics
                
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {}

    async def run_router(self):
        """Run the router system"""
        logger.info("Starting Telegram Router...")
        
        # Start queue processor
        queue_task = asyncio.create_task(self.process_queue())
        
        # Start token balance updater (if enabled)
        if self.config["token_verification"]["enabled"]:
            balance_task = asyncio.create_task(self.periodic_balance_update())
            await asyncio.gather(queue_task, balance_task)
        else:
            await queue_task

    async def periodic_balance_update(self):
        """Periodically update token balances"""
        while True:
            try:
                await self.update_all_token_balances()
                await asyncio.sleep(3600)  # Update every hour
            except Exception as e:
                logger.error(f"Balance update error: {e}")
                await asyncio.sleep(300)


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Telegram Router")
    parser.add_argument("--workspace", default="C:\\EQ12", help="Workspace path")
    parser.add_argument("--register-chat", nargs=3, metavar=("CHAT_ID", "CHAT_TYPE", "USERNAME"), 
                       help="Register a new chat")
    parser.add_argument("--test-alert", help="Send test alert")
    parser.add_argument("--analytics", action="store_true", help="Show analytics")
    
    args = parser.parse_args()
    
    router = EQ12TelegramRouter(args.workspace)
    
    if args.register_chat:
        chat_id, chat_type, username = args.register_chat
        success = router.register_chat(int(chat_id), ChatType(chat_type), username)
        print(f"Chat registration {'successful' if success else 'failed'}")
        return 0
    
    if args.test_alert:
        message_id = await router.send_alert("test", "Test Alert", args.test_alert)
        print(f"Test alert queued with ID: {message_id}")
        return 0
    
    if args.analytics:
        analytics = router.get_analytics_summary()
        print(json.dumps(analytics, indent=2))
        return 0
    
    # Run router
    await router.run_router()
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Telegram Router stopped by user")
        exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)