#!/usr/bin/env python3
"""
EQ12 Advanced Conversation Management System
Sophisticated conversation handling with role management, context optimization,
memory systems, and intelligent conversation flow control.

Features:
- Advanced message role management (system, user, assistant, tool, memory)
- Context window optimization and intelligent truncation
- Conversation history persistence and retrieval
- Memory injection and long-term context management
- Multi-turn conversation handling with state management
- Performance optimization for token usage

Author: EQ12 GODSTACK Team
Version: 1.0.0
License: MIT
"""

import hashlib
import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import tiktoken


class ConversationRole(Enum):
    """Enhanced conversation roles for sophisticated interactions"""

    SYSTEM = "system"  # Core system instructions and behavior
    USER = "user"  # User input and queries
    ASSISTANT = "assistant"  # AI responses and analysis
    TOOL = "tool"  # Tool/function call results
    MEMORY = "memory"  # Injected long-term memory
    CONTEXT = "context"  # Additional contextual information


class MessageType(Enum):
    """Message type classification"""

    INSTRUCTION = "instruction"  # System instructions
    QUERY = "query"  # User questions/requests
    RESPONSE = "response"  # AI responses
    TOOL_CALL = "tool_call"  # Function/tool invocations
    TOOL_RESULT = "tool_result"  # Tool execution results
    MEMORY_INJECT = "memory_inject"  # Memory system injections


class ConversationState(Enum):
    """Conversation state tracking"""

    ACTIVE = "active"  # Ongoing conversation
    PAUSED = "paused"  # Temporarily paused
    COMPLETED = "completed"  # Successfully completed
    ERROR = "error"  # Error occurred
    ARCHIVED = "archived"  # Archived for reference


@dataclass
class ConversationMessage:
    """Enhanced message structure with metadata and tracking"""

    role: ConversationRole
    content: str
    message_type: MessageType
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(
        default_factory=lambda: hashlib.md5(
            f"{datetime.now().isoformat()}{id(object())}".encode()
        ).hexdigest()[:12]
    )
    token_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    parent_id: str | None = None  # For threading/branching
    importance: float = 1.0  # Priority/importance score (0.0-1.0)
    expires_at: datetime | None = None  # Expiration for temporary messages


@dataclass
class ConversationMemory:
    """Persistent conversation memory"""

    conversation_id: str
    key: str
    value: Any
    memory_type: str  # facts, preferences, context, history
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    importance: float = 1.0
    expires_at: datetime | None = None


@dataclass
class ConversationSummary:
    """Conversation summary for context compression"""

    conversation_id: str
    summary_text: str
    original_message_count: int
    compressed_message_count: int
    token_savings: int
    created_at: datetime = field(default_factory=datetime.now)
    summary_quality: float = 0.8  # Confidence in summary quality


class ConversationManager:
    """Advanced conversation management with memory and optimization"""

    def __init__(
        self,
        storage_path: Path | None = None,
        max_context_tokens: int = 128000,
        target_context_tokens: int = 100000,
    ):
        self.storage_path = storage_path or Path("C:/EQ12/conversations")
        self.storage_path.mkdir(exist_ok=True)

        self.max_context_tokens = max_context_tokens
        self.target_context_tokens = target_context_tokens

        self.logger = logging.getLogger(f"{__name__}.ConversationManager")

        # Initialize database for persistent storage
        self.db_path = self.storage_path / "conversations.db"
        self._init_database()

        # Active conversations in memory
        self.active_conversations: dict[str, dict[str, Any]] = {}

        # Token encoding for different models
        self.encoders = {}

        # Performance metrics
        self.metrics = {
            "total_conversations": 0,
            "messages_processed": 0,
            "tokens_saved_by_compression": 0,
            "memory_retrievals": 0,
        }

    def _init_database(self):
        """Initialize SQLite database for conversation storage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Conversations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT,
                    state TEXT,
                    created_at TEXT,
                    last_activity TEXT,
                    total_messages INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """
            )

            # Messages table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    message_id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    message_type TEXT,
                    timestamp TEXT,
                    token_count INTEGER,
                    parent_id TEXT,
                    importance REAL,
                    expires_at TEXT,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
                )
            """
            )

            # Memory table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    key TEXT,
                    value TEXT,
                    memory_type TEXT,
                    created_at TEXT,
                    last_accessed TEXT,
                    access_count INTEGER DEFAULT 0,
                    importance REAL,
                    expires_at TEXT
                )
            """
            )

            # Summaries table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    summary_text TEXT,
                    original_message_count INTEGER,
                    compressed_message_count INTEGER,
                    token_savings INTEGER,
                    created_at TEXT,
                    summary_quality REAL
                )
            """
            )

            conn.commit()

    def get_encoder(self, model: str = "gpt-4") -> tiktoken.Encoding:
        """Get token encoder for model"""
        if model not in self.encoders:
            try:
                self.encoders[model] = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fallback for newer models
                self.encoders[model] = tiktoken.get_encoding("cl100k_base")

        return self.encoders[model]

    def count_tokens(self, text: str, model: str = "gpt-4") -> int:
        """Count tokens in text"""
        encoder = self.get_encoder(model)
        return len(encoder.encode(text))

    def create_conversation(
        self,
        conversation_id: str | None = None,
        title: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        """Create new conversation"""

        if not conversation_id:
            conversation_id = hashlib.md5(
                f"{datetime.now().isoformat()}{id(object())}".encode()
            ).hexdigest()[:16]

        conversation = {
            "conversation_id": conversation_id,
            "title": title or f"Conversation {conversation_id[:8]}",
            "state": ConversationState.ACTIVE.value,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "messages": [],
            "memory": {},
            "metadata": metadata or {},
        }

        self.active_conversations[conversation_id] = conversation

        # Persist to database
        self._save_conversation_to_db(conversation)

        self.metrics["total_conversations"] += 1
        self.logger.info(f"Created conversation: {conversation_id}")

        return conversation_id

    def add_message(
        self,
        conversation_id: str,
        role: ConversationRole,
        content: str,
        message_type: MessageType = MessageType.QUERY,
        parent_id: str | None = None,
        importance: float = 1.0,
        expires_at: datetime | None = None,
        metadata: dict | None = None,
    ) -> ConversationMessage:
        """Add message to conversation"""

        if conversation_id not in self.active_conversations:
            self._load_conversation_from_db(conversation_id)

        conversation = self.active_conversations[conversation_id]

        message = ConversationMessage(
            role=role,
            content=content,
            message_type=message_type,
            parent_id=parent_id,
            importance=importance,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        # Count tokens
        message.token_count = self.count_tokens(content)

        # Add to conversation
        conversation["messages"].append(message)
        conversation["last_activity"] = datetime.now()

        # Persist message
        self._save_message_to_db(conversation_id, message)

        self.metrics["messages_processed"] += 1

        # Check if context optimization is needed
        total_tokens = sum(msg.token_count or 0 for msg in conversation["messages"])
        if total_tokens > self.max_context_tokens:
            self._optimize_context(conversation_id)

        return message

    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int | None = None,
        include_expired: bool = False,
        min_importance: float = 0.0,
        model: str = "gpt-4",
    ) -> list[dict[str, Any]]:
        """Get conversation messages optimized for API calls"""

        if conversation_id not in self.active_conversations:
            self._load_conversation_from_db(conversation_id)

        conversation = self.active_conversations[conversation_id]
        messages = conversation["messages"]

        # Filter messages
        filtered_messages = []
        now = datetime.now()

        for msg in messages:
            # Skip expired messages
            if not include_expired and msg.expires_at and msg.expires_at < now:
                continue

            # Skip low importance messages if needed
            if msg.importance < min_importance:
                continue

            filtered_messages.append(msg)

        # Sort by timestamp
        filtered_messages.sort(key=lambda x: x.timestamp)

        # Apply limit
        if limit:
            filtered_messages = filtered_messages[-limit:]

        # Convert to OpenAI format
        openai_messages = []
        total_tokens = 0

        for msg in filtered_messages:
            # Include memory context for system messages
            if msg.role == ConversationRole.SYSTEM:
                memory_context = self._get_relevant_memory(conversation_id, msg.content)
                if memory_context:
                    content = f"{msg.content}\n\nRELEVANT CONTEXT:\n{memory_context}"
                else:
                    content = msg.content
            else:
                content = msg.content

            openai_msg = {"role": msg.role.value, "content": content}

            # Add tool calls if present
            if hasattr(msg, "tool_calls") and msg.metadata.get("tool_calls"):
                openai_msg["tool_calls"] = msg.metadata["tool_calls"]

            msg_tokens = self.count_tokens(content, model)

            # Check token limit
            if total_tokens + msg_tokens > self.target_context_tokens and openai_messages:
                # Try compression if we're hitting limits
                break

            openai_messages.append(openai_msg)
            total_tokens += msg_tokens

        self.logger.debug(f"Retrieved {len(openai_messages)} messages ({total_tokens} tokens)")
        return openai_messages

    def add_memory(
        self,
        conversation_id: str,
        key: str,
        value: Any,
        memory_type: str = "facts",
        importance: float = 1.0,
        expires_at: datetime | None = None,
    ):
        """Add item to conversation memory"""

        memory_item = ConversationMemory(
            conversation_id=conversation_id,
            key=key,
            value=value,
            memory_type=memory_type,
            importance=importance,
            expires_at=expires_at,
        )

        # Store in active conversation
        if conversation_id in self.active_conversations:
            conversation = self.active_conversations[conversation_id]
            if "memory" not in conversation:
                conversation["memory"] = {}
            conversation["memory"][key] = memory_item

        # Persist to database
        self._save_memory_to_db(memory_item)

        self.logger.debug(f"Added memory: {key} to conversation {conversation_id}")

    def _get_relevant_memory(self, conversation_id: str, context: str, limit: int = 5) -> str:
        """Retrieve relevant memory items for context injection"""

        # Simple keyword matching for now - could be enhanced with embeddings
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT key, value, importance
                FROM conversation_memory
                WHERE conversation_id = ?
                AND (expires_at IS NULL OR expires_at > ?)
                ORDER BY importance DESC, last_accessed DESC
                LIMIT ?
            """,
                (conversation_id, datetime.now().isoformat(), limit),
            )

            memories = cursor.fetchall()

        if not memories:
            return ""

        memory_text = []
        for key, value, _importance in memories:
            memory_text.append(f"- {key}: {value}")

            # Update access count
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE conversation_memory
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE conversation_id = ? AND key = ?
                """,
                    (datetime.now().isoformat(), conversation_id, key),
                )
                conn.commit()

        self.metrics["memory_retrievals"] += len(memories)
        return "\n".join(memory_text)

    def _optimize_context(self, conversation_id: str):
        """Optimize conversation context when approaching token limits"""

        conversation = self.active_conversations[conversation_id]
        messages = conversation["messages"]

        if len(messages) < 10:
            return  # Too few messages to optimize

        # Calculate current token count
        total_tokens = sum(msg.token_count or 0 for msg in messages)

        if total_tokens <= self.target_context_tokens:
            return  # Already within target

        # Identify messages that can be compressed or removed
        # Keep system messages and recent important messages

        system_messages = [msg for msg in messages if msg.role == ConversationRole.SYSTEM]
        recent_messages = messages[-5:]  # Keep last 5 messages
        important_messages = [msg for msg in messages if msg.importance >= 0.8]

        # Messages to keep
        keep_messages = set()
        for msg_list in [system_messages, recent_messages, important_messages]:
            keep_messages.update(msg.message_id for msg in msg_list)

        # Compress or remove other messages
        compressed_messages = []
        tokens_saved = 0

        for msg in messages:
            if msg.message_id in keep_messages:
                compressed_messages.append(msg)
            else:
                # Create summary for removed messages
                if msg.role == ConversationRole.USER:
                    summary_content = f"[User asked: {msg.content[:100]}...]"
                elif msg.role == ConversationRole.ASSISTANT:
                    summary_content = f"[Assistant responded: {msg.content[:100]}...]"
                else:
                    continue  # Skip other roles

                summary_msg = ConversationMessage(
                    role=ConversationRole.CONTEXT,
                    content=summary_content,
                    message_type=MessageType.INSTRUCTION,
                    importance=0.5,
                    metadata={"compressed_from": msg.message_id},
                )
                summary_msg.token_count = self.count_tokens(summary_content)

                compressed_messages.append(summary_msg)
                tokens_saved += (msg.token_count or 0) - summary_msg.token_count

        # Update conversation with compressed messages
        conversation["messages"] = compressed_messages

        # Save compression summary
        summary = ConversationSummary(
            conversation_id=conversation_id,
            summary_text=f"Compressed {len(messages) - len(compressed_messages)} messages",
            original_message_count=len(messages),
            compressed_message_count=len(compressed_messages),
            token_savings=tokens_saved,
        )

        self._save_summary_to_db(summary)
        self.metrics["tokens_saved_by_compression"] += tokens_saved

        self.logger.info(f"Optimized context for {conversation_id}: saved {tokens_saved} tokens")

    def _save_conversation_to_db(self, conversation: dict):
        """Save conversation metadata to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO conversations
                (conversation_id, title, state, created_at, last_activity, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    conversation["conversation_id"],
                    conversation["title"],
                    conversation["state"],
                    conversation["created_at"].isoformat(),
                    conversation["last_activity"].isoformat(),
                    json.dumps(conversation["metadata"]),
                ),
            )
            conn.commit()

    def _save_message_to_db(self, conversation_id: str, message: ConversationMessage):
        """Save message to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO messages
                (message_id, conversation_id, role, content, message_type, timestamp,
                 token_count, parent_id, importance, expires_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    message.message_id,
                    conversation_id,
                    message.role.value,
                    message.content,
                    message.message_type.value,
                    message.timestamp.isoformat(),
                    message.token_count,
                    message.parent_id,
                    message.importance,
                    message.expires_at.isoformat() if message.expires_at else None,
                    json.dumps(message.metadata),
                ),
            )
            conn.commit()

    def _save_memory_to_db(self, memory: ConversationMemory):
        """Save memory item to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO conversation_memory
                (conversation_id, key, value, memory_type, created_at, last_accessed,
                 access_count, importance, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    memory.conversation_id,
                    memory.key,
                    (
                        json.dumps(memory.value)
                        if not isinstance(memory.value, str)
                        else memory.value
                    ),
                    memory.memory_type,
                    memory.created_at.isoformat(),
                    memory.last_accessed.isoformat(),
                    memory.access_count,
                    memory.importance,
                    memory.expires_at.isoformat() if memory.expires_at else None,
                ),
            )
            conn.commit()

    def _save_summary_to_db(self, summary: ConversationSummary):
        """Save compression summary to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO conversation_summaries
                (conversation_id, summary_text, original_message_count,
                 compressed_message_count, token_savings, created_at, summary_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    summary.conversation_id,
                    summary.summary_text,
                    summary.original_message_count,
                    summary.compressed_message_count,
                    summary.token_savings,
                    summary.created_at.isoformat(),
                    summary.summary_quality,
                ),
            )
            conn.commit()

    def _load_conversation_from_db(self, conversation_id: str):
        """Load conversation from database to memory"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Load conversation metadata
            cursor.execute(
                """
                SELECT title, state, created_at, last_activity, metadata
                FROM conversations WHERE conversation_id = ?
            """,
                (conversation_id,),
            )

            conv_data = cursor.fetchone()
            if not conv_data:
                raise ValueError(f"Conversation {conversation_id} not found")

            title, state, created_at, last_activity, metadata = conv_data

            conversation = {
                "conversation_id": conversation_id,
                "title": title,
                "state": state,
                "created_at": datetime.fromisoformat(created_at),
                "last_activity": datetime.fromisoformat(last_activity),
                "messages": [],
                "memory": {},
                "metadata": json.loads(metadata) if metadata else {},
            }

            # Load messages
            cursor.execute(
                """
                SELECT message_id, role, content, message_type, timestamp,
                       token_count, parent_id, importance, expires_at, metadata
                FROM messages WHERE conversation_id = ?
                ORDER BY timestamp
            """,
                (conversation_id,),
            )

            for row in cursor.fetchall():
                (
                    msg_id,
                    role,
                    content,
                    msg_type,
                    timestamp,
                    token_count,
                    parent_id,
                    importance,
                    expires_at,
                    metadata,
                ) = row

                message = ConversationMessage(
                    role=ConversationRole(role),
                    content=content,
                    message_type=MessageType(msg_type),
                    timestamp=datetime.fromisoformat(timestamp),
                    message_id=msg_id,
                    token_count=token_count,
                    parent_id=parent_id,
                    importance=importance,
                    expires_at=(datetime.fromisoformat(expires_at) if expires_at else None),
                    metadata=json.loads(metadata) if metadata else {},
                )

                conversation["messages"].append(message)

        self.active_conversations[conversation_id] = conversation
        self.logger.debug(f"Loaded conversation {conversation_id} from database")

    def get_metrics(self) -> dict[str, Any]:
        """Get conversation management metrics"""
        return {
            **self.metrics,
            "active_conversations": len(self.active_conversations),
            "database_path": str(self.db_path),
            "max_context_tokens": self.max_context_tokens,
            "target_context_tokens": self.target_context_tokens,
        }


# Example usage
if __name__ == "__main__":
    # Initialize conversation manager
    manager = ConversationManager()

    print("💬 EQ12 Advanced Conversation Management System")
    print("=" * 50)

    # Create a sample conversation
    conv_id = manager.create_conversation(title="Sports Betting Analysis")

    # Add system message
    manager.add_message(
        conv_id,
        ConversationRole.SYSTEM,
        "You are an expert sports betting analyst.",
        MessageType.INSTRUCTION,
        importance=1.0,
    )

    # Add memory
    manager.add_memory(conv_id, "user_bankroll", 1000.0, "preferences")
    manager.add_memory(conv_id, "risk_tolerance", "moderate", "preferences")

    # Add user query
    manager.add_message(
        conv_id,
        ConversationRole.USER,
        "Analyze this Chiefs vs Bills game with -150 odds on Chiefs",
        MessageType.QUERY,
    )

    # Get optimized messages for API
    api_messages = manager.get_conversation_messages(conv_id)

    print(f"\n📊 Conversation: {conv_id}")
    print(f"Messages for API: {len(api_messages)}")

    for i, msg in enumerate(api_messages):
        print(f"\n{i + 1}. {msg['role'].upper()}:")
        print(f"   {msg['content'][:100]}...")

    # Show metrics
    metrics = manager.get_metrics()
    print("\n📈 System Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
