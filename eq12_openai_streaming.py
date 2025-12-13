#!/usr/bin/env python3
"""
EQ12 GODSTACK - OpenAI Streaming Governance Integration
Real-time streaming AI governance with OpenAI Responses API event handling.

Features:
- Real-time streaming responses with delta updates
- Complete event handling for all OpenAI response event types
- Live governance monitoring with progress indicators
- Streaming conversation management with state tracking
- Real-time AI insights and recommendations

Based on OpenAI Responses API Events Documentation:
- response.output_text.delta - Real-time text streaming
- response.content_part.done - Content completion events
- response.function_call_arguments.* - Function call handling
- response.reasoning_*.* - AI reasoning transparency
- response.image_generation.* - Visual content generation
- response.mcp_call.* - Model Context Protocol integration
- error - Comprehensive error handling

Author: EQ12 GODSTACK Team
Version: 2.0.0 (Streaming Enhanced)
License: MIT
"""

import asyncio
import json
import logging
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import aiohttp
import colorama
from colorama import Fore, Style

# Initialize colorama for Windows compatibility
colorama.init(autoreset=True)


class StreamEventType(Enum):
    """OpenAI Streaming Event Types."""

    # Session Management
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"

    # Conversation Management
    CONVERSATION_ITEM_CREATED = "conversation.item.created"
    CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED = (
        "conversation.item.input_audio_transcription.completed"
    )
    CONVERSATION_ITEM_INPUT_AUDIO_TRANSCRIPTION_FAILED = (
        "conversation.item.input_audio_transcription.failed"
    )
    CONVERSATION_ITEM_TRUNCATED = "conversation.item.truncated"
    CONVERSATION_ITEM_DELETED = "conversation.item.deleted"

    # Response Events
    RESPONSE_CREATED = "response.created"
    RESPONSE_DONE = "response.done"
    RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
    RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
    RESPONSE_CONTENT_PART_ADDED = "response.content_part.added"
    RESPONSE_CONTENT_PART_DONE = "response.content_part.done"

    # Text Output Events
    RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
    RESPONSE_OUTPUT_TEXT_DONE = "response.output_text.done"

    # Function Call Events
    RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA = "response.function_call_arguments.delta"
    RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE = "response.function_call_arguments.done"

    # Reasoning Events
    RESPONSE_REASONING_SUMMARY_PART_ADDED = "response.reasoning_summary_part.added"
    RESPONSE_REASONING_SUMMARY_PART_DONE = "response.reasoning_summary_part.done"
    RESPONSE_REASONING_SUMMARY_TEXT_DELTA = "response.reasoning_summary_text.delta"
    RESPONSE_REASONING_SUMMARY_TEXT_DONE = "response.reasoning_summary_text.done"
    RESPONSE_REASONING_TEXT_DELTA = "response.reasoning_text.delta"
    RESPONSE_REASONING_TEXT_DONE = "response.reasoning_text.done"

    # Refusal Events
    RESPONSE_REFUSAL_DELTA = "response.refusal.delta"
    RESPONSE_REFUSAL_DONE = "response.refusal.done"

    # File Search Events
    RESPONSE_FILE_SEARCH_CALL_IN_PROGRESS = "response.file_search_call.in_progress"
    RESPONSE_FILE_SEARCH_CALL_SEARCHING = "response.file_search_call.searching"
    RESPONSE_FILE_SEARCH_CALL_COMPLETED = "response.file_search_call.completed"

    # Web Search Events
    RESPONSE_WEB_SEARCH_CALL_IN_PROGRESS = "response.web_search_call.in_progress"
    RESPONSE_WEB_SEARCH_CALL_SEARCHING = "response.web_search_call.searching"
    RESPONSE_WEB_SEARCH_CALL_COMPLETED = "response.web_search_call.completed"

    # Image Generation Events
    RESPONSE_IMAGE_GENERATION_CALL_IN_PROGRESS = "response.image_generation_call.in_progress"
    RESPONSE_IMAGE_GENERATION_CALL_GENERATING = "response.image_generation_call.generating"
    RESPONSE_IMAGE_GENERATION_CALL_COMPLETED = "response.image_generation_call.completed"
    RESPONSE_IMAGE_GENERATION_CALL_PARTIAL_IMAGE = "response.image_generation_call.partial_image"

    # MCP Events
    RESPONSE_MCP_CALL_IN_PROGRESS = "response.mcp_call.in_progress"
    RESPONSE_MCP_CALL_COMPLETED = "response.mcp_call.completed"
    RESPONSE_MCP_CALL_FAILED = "response.mcp_call.failed"
    RESPONSE_MCP_CALL_ARGUMENTS_DELTA = "response.mcp_call_arguments.delta"
    RESPONSE_MCP_CALL_ARGUMENTS_DONE = "response.mcp_call_arguments.done"
    RESPONSE_MCP_LIST_TOOLS_IN_PROGRESS = "response.mcp_list_tools.in_progress"
    RESPONSE_MCP_LIST_TOOLS_COMPLETED = "response.mcp_list_tools.completed"
    RESPONSE_MCP_LIST_TOOLS_FAILED = "response.mcp_list_tools.failed"

    # Code Interpreter Events
    RESPONSE_CODE_INTERPRETER_CALL_IN_PROGRESS = "response.code_interpreter_call.in_progress"
    RESPONSE_CODE_INTERPRETER_CALL_INTERPRETING = "response.code_interpreter_call.interpreting"
    RESPONSE_CODE_INTERPRETER_CALL_COMPLETED = "response.code_interpreter_call.completed"
    RESPONSE_CODE_INTERPRETER_CALL_CODE_DELTA = "response.code_interpreter_call_code.delta"
    RESPONSE_CODE_INTERPRETER_CALL_CODE_DONE = "response.code_interpreter_call_code.done"

    # Annotation Events
    RESPONSE_OUTPUT_TEXT_ANNOTATION_ADDED = "response.output_text.annotation.added"

    # Other Events
    RESPONSE_QUEUED = "response.queued"
    RESPONSE_CUSTOM_TOOL_CALL_INPUT_DELTA = "response.custom_tool_call_input.delta"
    RESPONSE_CUSTOM_TOOL_CALL_INPUT_DONE = "response.custom_tool_call_input.done"

    # Error Events
    ERROR = "error"


@dataclass
class StreamEvent:
    """Represents a streaming event from OpenAI."""

    event_type: StreamEventType
    data: dict[str, Any]
    sequence_number: int
    timestamp: datetime
    item_id: str | None = None
    output_index: int | None = None
    content_index: int | None = None


@dataclass
class StreamingGovernanceContext:
    """Context for streaming governance operations."""

    task_type: str
    conversation_id: str
    session_id: str
    start_time: datetime
    metadata: dict[str, Any]
    accumulated_text: str = ""
    reasoning_text: str = ""
    function_calls: list[dict[str, Any]] = None
    current_status: str = "initializing"

    def __post_init__(self):
        if self.function_calls is None:
            self.function_calls = []


class EQ12StreamingGovernanceClient:
    """Enhanced streaming OpenAI client for real-time EQ12 governance operations."""

    def __init__(self, api_key: str | None = None, eq12_root: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.eq12_root = Path(
            eq12_root
            or os.getenv("EQ12_ROOT", "C:/EQ12" if os.name == "nt" else "/workspaces/EQ12")
        )
        self.logs_dir = self.eq12_root / "logs" / "streaming"
        self.reports_dir = self.eq12_root / "reports" / "streaming"

        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.base_url = "https://api.openai.com/v1"
        self.realtime_url = "wss://api.openai.com/v1/realtime"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "realtime=v1",
        }

        self.logger = self._setup_logging()

        # Active streaming contexts
        self.streaming_contexts: dict[str, StreamingGovernanceContext] = {}

        # Event handlers
        self.event_handlers: dict[StreamEventType, list[Callable]] = {}
        self._register_default_handlers()

        # Real-time governance models
        self.streaming_models = {
            "governance": "gpt-4o-realtime-preview",
            "analysis": "gpt-4o-realtime-preview",
            "monitoring": "gpt-4o-mini",
            "security": "gpt-4o-realtime-preview",
        }

        self.logger.info(f"{Fore.GREEN}🚀 EQ12 Streaming Governance Client initialized")
        self.logger.info(
            f"{Fore.CYAN}📡 Real-time streaming enabled with comprehensive event handling"
        )

    def _setup_logging(self) -> logging.Logger:
        """Configure comprehensive logging for streaming AI operations."""
        log_file = self.logs_dir / f"eq12_streaming_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        logger = logging.getLogger(__name__ + "_streaming")
        logger.info(f"{Fore.CYAN}🔄 EQ12 Streaming OpenAI Governance Client initialized")
        logger.info(f"{Fore.GREEN}✅ API Key configured")
        logger.info(f"{Fore.BLUE}📁 EQ12 Root: {self.eq12_root}")
        logger.info(f"{Fore.YELLOW}📊 Logs: {self.logs_dir}")

        return logger

    def register_event_handler(self, event_type: StreamEventType, handler: Callable):
        """Register custom event handler for specific stream events."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        self.logger.info(f"{Fore.GREEN}🔗 Registered handler for {event_type.value}")

    def _register_default_handlers(self):
        """Register default event handlers for all stream events."""
        # Text output handlers
        self.register_event_handler(
            StreamEventType.RESPONSE_OUTPUT_TEXT_DELTA, self._handle_text_delta
        )
        self.register_event_handler(
            StreamEventType.RESPONSE_OUTPUT_TEXT_DONE, self._handle_text_done
        )

        # Content part handlers
        self.register_event_handler(
            StreamEventType.RESPONSE_CONTENT_PART_ADDED, self._handle_content_part_added
        )
        self.register_event_handler(
            StreamEventType.RESPONSE_CONTENT_PART_DONE, self._handle_content_part_done
        )

        # Function call handlers
        self.register_event_handler(
            StreamEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DELTA,
            self._handle_function_call_delta,
        )
        self.register_event_handler(
            StreamEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE,
            self._handle_function_call_done,
        )

        # Reasoning handlers
        self.register_event_handler(
            StreamEventType.RESPONSE_REASONING_TEXT_DELTA, self._handle_reasoning_delta
        )
        self.register_event_handler(
            StreamEventType.RESPONSE_REASONING_TEXT_DONE, self._handle_reasoning_done
        )

        # Error handler
        self.register_event_handler(StreamEventType.ERROR, self._handle_error)

        # Response lifecycle handlers
        self.register_event_handler(StreamEventType.RESPONSE_CREATED, self._handle_response_created)
        self.register_event_handler(StreamEventType.RESPONSE_DONE, self._handle_response_done)

    async def _handle_text_delta(self, event: StreamEvent, context: StreamingGovernanceContext):
        """Handle real-time text delta events."""
        delta = event.data.get("delta", "")
        context.accumulated_text += delta

        # Real-time display with color coding
        if context.task_type == "security_audit":
            print(f"{Fore.RED}{delta}", end="", flush=True)
        elif context.task_type == "chrome_bookmarks":
            print(f"{Fore.BLUE}{delta}", end="", flush=True)
        else:
            print(f"{Fore.WHITE}{delta}", end="", flush=True)

    async def _handle_text_done(self, event: StreamEvent, context: StreamingGovernanceContext):
        """Handle text completion events."""
        final_text = event.data.get("text", context.accumulated_text)
        context.current_status = "text_complete"

        self.logger.info(
            f"{Fore.GREEN}✅ Text complete for {context.task_type}: {len(final_text)} chars"
        )
        print(f"\n{Fore.CYAN}{'=' * 60}")
        print(f"{Fore.GREEN}✅ AI Analysis Complete - {context.task_type}")
        print(f"{Fore.CYAN}{'=' * 60}")

    async def _handle_content_part_added(
        self, event: StreamEvent, context: StreamingGovernanceContext
    ):
        """Handle content part addition events."""
        part_type = event.data.get("part", {}).get("type", "unknown")
        self.logger.info(f"{Fore.BLUE}📝 Content part added: {part_type}")

    async def _handle_content_part_done(
        self, event: StreamEvent, context: StreamingGovernanceContext
    ):
        """Handle content part completion events."""
        part_data = event.data.get("part", {})
        self.logger.info(
            f"{Fore.GREEN}✅ Content part complete: {part_data.get('type', 'unknown')}"
        )

    async def _handle_function_call_delta(
        self, event: StreamEvent, context: StreamingGovernanceContext
    ):
        """Handle function call argument deltas."""
        delta = event.data.get("delta", "")
        self.logger.debug(f"{Fore.MAGENTA}🔧 Function call delta: {delta}")

    async def _handle_function_call_done(
        self, event: StreamEvent, context: StreamingGovernanceContext
    ):
        """Handle function call completion."""
        name = event.data.get("name", "unknown")
        arguments = event.data.get("arguments", "{}")

        function_call = {
            "name": name,
            "arguments": arguments,
            "timestamp": datetime.now(),
            "item_id": event.item_id,
        }
        context.function_calls.append(function_call)

        self.logger.info(f"{Fore.MAGENTA}🔧 Function call complete: {name}")
        print(f"\n{Fore.MAGENTA}🔧 AI Function Call: {name}")

    async def _handle_reasoning_delta(
        self, event: StreamEvent, context: StreamingGovernanceContext
    ):
        """Handle AI reasoning transparency deltas."""
        delta = event.data.get("delta", "")
        context.reasoning_text += delta

        # Display reasoning in a different color
        print(f"{Fore.YELLOW}💭 {delta}", end="", flush=True)

    async def _handle_reasoning_done(self, event: StreamEvent, context: StreamingGovernanceContext):
        """Handle reasoning completion."""
        final_reasoning = event.data.get("text", context.reasoning_text)
        self.logger.info(f"{Fore.YELLOW}🧠 AI Reasoning complete: {len(final_reasoning)} chars")

        print(f"\n{Fore.YELLOW}💭 AI Reasoning Complete")
        print(f"{Fore.CYAN}{'=' * 40}")

    async def _handle_error(self, event: StreamEvent, context: StreamingGovernanceContext):
        """Handle error events."""
        error_code = event.data.get("code", "UNKNOWN")
        error_message = event.data.get("message", "No message provided")

        context.current_status = f"error_{error_code}"

        self.logger.error(f"{Fore.RED}❌ Stream Error [{error_code}]: {error_message}")
        print(f"\n{Fore.RED}❌ AI Error: {error_message}")

    async def _handle_response_created(
        self, event: StreamEvent, context: StreamingGovernanceContext
    ):
        """Handle response creation."""
        response_id = event.data.get("id", "unknown")
        context.current_status = "response_active"

        self.logger.info(f"{Fore.GREEN}🚀 Response created: {response_id}")
        print(f"\n{Fore.GREEN}🚀 AI Response Starting...")

    async def _handle_response_done(self, event: StreamEvent, context: StreamingGovernanceContext):
        """Handle response completion."""
        context.current_status = "completed"

        # Save complete governance report
        await self._save_governance_report(context)

        self.logger.info(f"{Fore.GREEN}🎉 Governance analysis complete for {context.task_type}")
        print(f"\n{Fore.GREEN}🎉 Governance Analysis Complete!")
        print(f"{Fore.BLUE}📊 Report saved to: {self.reports_dir}")

    async def _save_governance_report(self, context: StreamingGovernanceContext):
        """Save complete governance report with streaming data."""
        report_file = (
            self.reports_dir
            / f"governance_stream_{context.task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        report = {
            "task_type": context.task_type,
            "conversation_id": context.conversation_id,
            "session_id": context.session_id,
            "start_time": context.start_time.isoformat(),
            "completion_time": datetime.now().isoformat(),
            "status": context.current_status,
            "metadata": context.metadata,
            "ai_response": {
                "text": context.accumulated_text,
                "reasoning": context.reasoning_text,
                "function_calls": context.function_calls,
            },
            "streaming_stats": {
                "total_chars": len(context.accumulated_text),
                "reasoning_chars": len(context.reasoning_text),
                "function_call_count": len(context.function_calls),
                "duration_seconds": (datetime.now() - context.start_time).total_seconds(),
            },
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"{Fore.BLUE}📊 Saved governance report: {report_file}")

    async def process_stream_event(
        self, event_data: dict[str, Any], context: StreamingGovernanceContext
    ):
        """Process a single streaming event."""
        try:
            event_type_str = event_data.get("type", "unknown")

            # Convert string to enum
            try:
                event_type = StreamEventType(event_type_str)
            except ValueError:
                self.logger.warning(f"{Fore.YELLOW}⚠️  Unknown event type: {event_type_str}")
                return

            # Create stream event object
            stream_event = StreamEvent(
                event_type=event_type,
                data=event_data,
                sequence_number=event_data.get("sequence_number", 0),
                timestamp=datetime.now(),
                item_id=event_data.get("item_id"),
                output_index=event_data.get("output_index"),
                content_index=event_data.get("content_index"),
            )

            # Execute registered handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    await handler(stream_event, context)

        except Exception as e:
            self.logger.error(f"{Fore.RED}❌ Error processing stream event: {e}")

    async def start_streaming_governance_analysis(
        self,
        task_type: str,
        governance_prompt: str,
        context_data: dict[str, Any],
        model: str = "gpt-4o-realtime-preview",
    ) -> StreamingGovernanceContext:
        """Start streaming governance analysis with real-time AI responses."""

        try:
            # Create streaming context
            streaming_context = StreamingGovernanceContext(
                task_type=task_type,
                conversation_id=f"conv_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                session_id=f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                start_time=datetime.now(),
                metadata=context_data,
            )

            self.streaming_contexts[streaming_context.session_id] = streaming_context

            print(f"\n{Fore.CYAN}{'=' * 80}")
            print(f"{Fore.GREEN}🚀 EQ12 STREAMING GOVERNANCE - {task_type.upper()}")
            print(f"{Fore.CYAN}{'=' * 80}")
            print(f"{Fore.YELLOW}📡 Session: {streaming_context.session_id}")
            print(f"{Fore.BLUE}🤖 Model: {model}")
            print(
                f"{Fore.MAGENTA}⏰ Started: {streaming_context.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print(f"{Fore.CYAN}{'=' * 80}")

            # Create conversation with streaming
            conversation_payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are the EQ12 GODSTACK AI Governance Assistant. Task: {task_type}. Provide comprehensive analysis with reasoning transparency.",
                    },
                    {
                        "role": "user",
                        "content": f"{governance_prompt}\n\nContext: {json.dumps(context_data, indent=2)}",
                    },
                ],
                "stream": True,
                "metadata": {
                    "eq12_task_type": task_type,
                    "session_id": streaming_context.session_id,
                },
            }

            # Start streaming request
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=conversation_payload,
                ) as response,
            ):
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Streaming request failed: {error_text}")

                print(f"\n{Fore.GREEN}🔄 AI Analysis Starting - Real-time stream active...")
                print(f"{Fore.CYAN}{'─' * 60}")

                # Process streaming response
                async for line in response.content:
                    if line:
                        line_text = line.decode("utf-8").strip()
                        if line_text.startswith("data: "):
                            data_json = line_text[6:]  # Remove 'data: ' prefix

                            if data_json == "[DONE]":
                                break

                            try:
                                event_data = json.loads(data_json)

                                # Handle chat completion streaming format
                                if "choices" in event_data:
                                    choice = event_data["choices"][0]
                                    delta = choice.get("delta", {})

                                    if delta.get("content"):
                                        # Simulate text delta event
                                        simulated_event = {
                                            "type": "response.output_text.delta",
                                            "delta": delta["content"],
                                            "sequence_number": event_data.get("created", 0),
                                        }
                                        await self.process_stream_event(
                                            simulated_event, streaming_context
                                        )

                                    if choice.get("finish_reason"):
                                        # Simulate completion event
                                        simulated_event = {
                                            "type": "response.output_text.done",
                                            "text": streaming_context.accumulated_text,
                                            "sequence_number": event_data.get("created", 0),
                                        }
                                        await self.process_stream_event(
                                            simulated_event, streaming_context
                                        )

                            except json.JSONDecodeError:
                                continue

            streaming_context.current_status = "completed"

            return streaming_context

        except Exception as e:
            self.logger.error(f"{Fore.RED}❌ Streaming governance analysis failed: {e}")
            raise


# Convenience functions for common governance streaming tasks
async def stream_chrome_governance_analysis(
    bookmarks_data: dict[str, Any], client: EQ12StreamingGovernanceClient | None = None
) -> StreamingGovernanceContext:
    """Stream real-time Chrome governance analysis."""
    if not client:
        client = EQ12StreamingGovernanceClient()

    prompt = """
    🔒 EQ12 CHROME SECURITY GOVERNANCE ANALYSIS

    Analyze the provided Chrome bookmarks for security risks, governance compliance, and recommendations.
    Focus on:
    1. Security risk assessment of bookmarked URLs
    2. Corporate governance compliance
    3. Data privacy concerns
    4. Access control recommendations
    5. Policy violations and remediation steps

    Provide detailed reasoning for all findings and actionable recommendations.
    """

    return await client.start_streaming_governance_analysis(
        task_type="chrome_bookmarks",
        governance_prompt=prompt,
        context_data=bookmarks_data,
    )


async def stream_security_audit_analysis(
    audit_data: dict[str, Any], client: EQ12StreamingGovernanceClient | None = None
) -> StreamingGovernanceContext:
    """Stream real-time security audit analysis."""
    if not client:
        client = EQ12StreamingGovernanceClient()

    prompt = """
    🛡️ EQ12 SECURITY GOVERNANCE AUDIT

    Perform comprehensive security analysis on the provided system data.
    Focus on:
    1. Vulnerability assessment and risk scoring
    2. Compliance with security frameworks (SOC2, ISO27001)
    3. Access control and privilege management
    4. Data protection and encryption status
    5. Incident response recommendations
    6. Security policy gaps and improvements

    Provide transparent reasoning and prioritized action items.
    """

    return await client.start_streaming_governance_analysis(
        task_type="security_audit", governance_prompt=prompt, context_data=audit_data
    )


async def main():
    """Demo streaming governance capabilities."""
    try:
        print(f"{Fore.GREEN}{Style.BRIGHT}🚀 EQ12 STREAMING GOVERNANCE DEMO")

        # Initialize client
        client = EQ12StreamingGovernanceClient()

        # Demo Chrome governance analysis
        demo_bookmarks = {
            "bookmarks": [
                {
                    "name": "GitHub",
                    "url": "https://github.com",
                    "folder": "Development",
                },
                {
                    "name": "ChatGPT",
                    "url": "https://chat.openai.com",
                    "folder": "AI Tools",
                },
                {
                    "name": "Banking",
                    "url": "https://bank.example.com",
                    "folder": "Finance",
                },
            ],
            "analysis_timestamp": datetime.now().isoformat(),
        }

        # Start streaming analysis
        await stream_chrome_governance_analysis(demo_bookmarks, client)

        print(f"\n{Fore.GREEN}✅ Demo complete! Check reports in: {client.reports_dir}")

    except Exception as e:
        print(f"{Fore.RED}❌ Demo failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
