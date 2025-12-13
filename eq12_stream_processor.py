#!/usr/bin/env python3
"""
EQ12 GODSTACK - Advanced Streaming Event Processor
Comprehensive real-time event handling for all OpenAI Responses API event types.

This module provides specialized handlers for every streaming event type from the
OpenAI Responses API documentation, including:

- Text output events (delta, done, annotations)
- Function call events (arguments, completion)
- Reasoning events (summary, text, transparency)
- Image generation events (progress, partial, completion)
- File/Web search events (progress, results)
- MCP (Model Context Protocol) events
- Code interpreter events
- Error handling and recovery

Author: EQ12 GODSTACK Team
Version: 2.0.0 (Comprehensive Event Handling)
License: MIT
"""

import asyncio
import base64
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init(autoreset=True)


@dataclass
class EventMetrics:
    """Metrics tracking for streaming events."""

    total_events: int = 0
    text_deltas: int = 0
    function_calls: int = 0
    reasoning_events: int = 0
    error_events: int = 0
    image_events: int = 0
    search_events: int = 0
    mcp_events: int = 0
    code_interpreter_events: int = 0
    start_time: datetime = field(default_factory=datetime.now)

    @property
    def duration_seconds(self) -> float:
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def events_per_second(self) -> float:
        duration = self.duration_seconds
        return self.total_events / duration if duration > 0 else 0


@dataclass
class StreamingContent:
    """Accumulated content from streaming events."""

    main_text: str = ""
    reasoning_text: str = ""
    reasoning_summary: str = ""
    function_calls: list[dict[str, Any]] = field(default_factory=list)
    code_snippets: list[dict[str, str]] = field(default_factory=list)
    images: list[dict[str, Any]] = field(default_factory=list)
    search_results: list[dict[str, Any]] = field(default_factory=list)
    annotations: list[dict[str, Any]] = field(default_factory=list)
    refusals: list[str] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


class AdvancedStreamEventProcessor:
    """Advanced processor for all OpenAI streaming event types."""

    def __init__(self, eq12_root: str | None = None, enable_file_output: bool = True):
        self.eq12_root = Path(
            eq12_root
            or os.getenv("EQ12_ROOT", "C:/EQ12" if os.name == "nt" else "/workspaces/EQ12")
        )
        self.logs_dir = self.eq12_root / "logs" / "streaming_events"
        self.output_dir = self.eq12_root / "outputs" / "streaming"
        self.enable_file_output = enable_file_output

        if enable_file_output:
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = self._setup_logging()
        self.metrics = EventMetrics()
        self.content = StreamingContent()

        # Visual indicators
        self.progress_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_progress = 0

        # Event type counters for advanced metrics
        self.event_type_counts = {}

        self.logger.info(f"{Fore.CYAN}🔄 Advanced Stream Event Processor initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging for event processing."""
        if self.enable_file_output:
            log_file = (
                self.logs_dir / f"stream_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )

            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(log_file, encoding="utf-8"),
                    logging.StreamHandler(),
                ],
            )
        else:
            logging.basicConfig(level=logging.INFO)

        return logging.getLogger(__name__ + "_event_processor")

    def get_progress_indicator(self) -> str:
        """Get current progress indicator character."""
        char = self.progress_chars[self.current_progress]
        self.current_progress = (self.current_progress + 1) % len(self.progress_chars)
        return char

    def update_metrics(self, event_type: str):
        """Update event metrics and counters."""
        self.metrics.total_events += 1
        self.event_type_counts[event_type] = self.event_type_counts.get(event_type, 0) + 1

    # ==================== TEXT OUTPUT EVENT HANDLERS ====================

    async def handle_output_text_delta(self, event_data: dict[str, Any]) -> None:
        """Handle response.output_text.delta - Real-time text streaming."""
        delta = event_data.get("delta", "")
        self.content.main_text += delta
        self.metrics.text_deltas += 1
        self.update_metrics("output_text_delta")

        # Real-time display with typing effect
        print(f"{Fore.WHITE}{delta}", end="", flush=True)

        self.logger.debug(f"Text delta: {len(delta)} chars")

    async def handle_output_text_done(self, event_data: dict[str, Any]) -> None:
        """Handle response.output_text.done - Text completion."""
        final_text = event_data.get("text", self.content.main_text)
        content_index = event_data.get("content_index", 0)

        self.update_metrics("output_text_done")

        print(f"\n{Fore.GREEN}✅ Text Complete [{content_index}]: {len(final_text)} characters")

        # Save text output if file output enabled
        if self.enable_file_output:
            await self._save_text_output(final_text, content_index)

        self.logger.info(f"Text output complete: {len(final_text)} chars")

    async def handle_output_text_annotation_added(self, event_data: dict[str, Any]) -> None:
        """Handle response.output_text.annotation.added - Text annotations."""
        annotation = event_data.get("annotation", {})
        annotation_index = event_data.get("annotation_index", 0)

        self.content.annotations.append(
            {
                "annotation": annotation,
                "index": annotation_index,
                "timestamp": datetime.now(),
            }
        )

        self.update_metrics("annotation_added")

        annotation_type = annotation.get("type", "unknown")
        print(f"\n{Fore.CYAN}📝 Annotation [{annotation_index}]: {annotation_type}")

        self.logger.info(f"Annotation added: {annotation_type}")

    # ==================== FUNCTION CALL EVENT HANDLERS ====================

    async def handle_function_call_arguments_delta(self, event_data: dict[str, Any]) -> None:
        """Handle response.function_call_arguments.delta - Function call streaming."""
        delta = event_data.get("delta", "")

        self.update_metrics("function_call_delta")
        self.metrics.function_calls += 1

        print(f"{Fore.MAGENTA}🔧 {delta}", end="", flush=True)

        self.logger.debug(f"Function call delta: {delta}")

    async def handle_function_call_arguments_done(self, event_data: dict[str, Any]) -> None:
        """Handle response.function_call_arguments.done - Function call completion."""
        function_name = event_data.get("name", "unknown")
        arguments = event_data.get("arguments", "{}")
        item_id = event_data.get("item_id", "unknown")

        function_call = {
            "name": function_name,
            "arguments": arguments,
            "item_id": item_id,
            "timestamp": datetime.now(),
        }

        self.content.function_calls.append(function_call)
        self.update_metrics("function_call_done")

        print(f"\n{Fore.MAGENTA}🔧 Function Call Complete: {function_name}")
        print(f"{Fore.CYAN}   Arguments: {arguments}")

        # Save function call if file output enabled
        if self.enable_file_output:
            await self._save_function_call(function_call)

        self.logger.info(f"Function call complete: {function_name}")

    # ==================== REASONING EVENT HANDLERS ====================

    async def handle_reasoning_text_delta(self, event_data: dict[str, Any]) -> None:
        """Handle response.reasoning_text.delta - AI reasoning transparency."""
        delta = event_data.get("delta", "")
        self.content.reasoning_text += delta
        self.metrics.reasoning_events += 1
        self.update_metrics("reasoning_delta")

        # Display reasoning in special color
        print(f"{Fore.YELLOW}💭 {delta}", end="", flush=True)

        self.logger.debug(f"Reasoning delta: {len(delta)} chars")

    async def handle_reasoning_text_done(self, event_data: dict[str, Any]) -> None:
        """Handle response.reasoning_text.done - Reasoning completion."""
        final_reasoning = event_data.get("text", self.content.reasoning_text)

        self.update_metrics("reasoning_done")

        print(f"\n{Fore.YELLOW}🧠 AI Reasoning Complete: {len(final_reasoning)} characters")

        # Save reasoning if file output enabled
        if self.enable_file_output:
            await self._save_reasoning_output(final_reasoning)

        self.logger.info(f"Reasoning complete: {len(final_reasoning)} chars")

    async def handle_reasoning_summary_part_added(self, event_data: dict[str, Any]) -> None:
        """Handle response.reasoning_summary_part.added - Summary part addition."""
        event_data.get("part", {})
        summary_index = event_data.get("summary_index", 0)

        self.update_metrics("reasoning_summary_added")

        print(f"\n{Fore.CYAN}📊 Reasoning Summary Part [{summary_index}] Added")

        self.logger.info(f"Reasoning summary part added: {summary_index}")

    async def handle_reasoning_summary_text_delta(self, event_data: dict[str, Any]) -> None:
        """Handle response.reasoning_summary_text.delta - Summary streaming."""
        delta = event_data.get("delta", "")
        self.content.reasoning_summary += delta

        self.update_metrics("reasoning_summary_delta")

        print(f"{Fore.CYAN}📊 {delta}", end="", flush=True)

    async def handle_reasoning_summary_text_done(self, event_data: dict[str, Any]) -> None:
        """Handle response.reasoning_summary_text.done - Summary completion."""
        final_summary = event_data.get("text", self.content.reasoning_summary)

        self.update_metrics("reasoning_summary_done")

        print(f"\n{Fore.CYAN}📊 Reasoning Summary Complete: {len(final_summary)} chars")

        if self.enable_file_output:
            await self._save_reasoning_summary(final_summary)

    # ==================== REFUSAL EVENT HANDLERS ====================

    async def handle_refusal_delta(self, event_data: dict[str, Any]) -> None:
        """Handle response.refusal.delta - Refusal streaming."""
        delta = event_data.get("delta", "")

        self.update_metrics("refusal_delta")

        print(f"{Fore.RED}🚫 {delta}", end="", flush=True)

        self.logger.warning(f"Refusal delta: {delta}")

    async def handle_refusal_done(self, event_data: dict[str, Any]) -> None:
        """Handle response.refusal.done - Refusal completion."""
        refusal_text = event_data.get("refusal", "")

        self.content.refusals.append(refusal_text)
        self.update_metrics("refusal_done")

        print(f"\n{Fore.RED}🚫 AI Refusal: {refusal_text}")

        self.logger.warning(f"AI refused request: {refusal_text}")

    # ==================== IMAGE GENERATION EVENT HANDLERS ====================

    async def handle_image_generation_call_in_progress(self, event_data: dict[str, Any]) -> None:
        """Handle response.image_generation_call.in_progress - Image generation started."""
        item_id = event_data.get("item_id", "unknown")

        self.metrics.image_events += 1
        self.update_metrics("image_generation_in_progress")

        print(f"\n{Fore.BLUE}🎨 Image Generation Started [{item_id}]")

        self.logger.info(f"Image generation started: {item_id}")

    async def handle_image_generation_call_generating(self, event_data: dict[str, Any]) -> None:
        """Handle response.image_generation_call.generating - Image being generated."""
        progress_char = self.get_progress_indicator()

        self.update_metrics("image_generation_generating")

        print(f"\r{Fore.BLUE}{progress_char} Generating image...", end="", flush=True)

    async def handle_image_generation_call_partial_image(self, event_data: dict[str, Any]) -> None:
        """Handle response.image_generation_call.partial_image - Partial image data."""
        partial_image_b64 = event_data.get("partial_image_b64", "")
        partial_image_index = event_data.get("partial_image_index", 0)

        self.update_metrics("image_generation_partial")

        print(
            f"\n{Fore.BLUE}🖼️  Partial Image [{partial_image_index}]: {len(partial_image_b64)} bytes"
        )

        # Save partial image if file output enabled
        if self.enable_file_output and partial_image_b64:
            await self._save_partial_image(partial_image_b64, partial_image_index)

    async def handle_image_generation_call_completed(self, event_data: dict[str, Any]) -> None:
        """Handle response.image_generation_call.completed - Image generation complete."""
        item_id = event_data.get("item_id", "unknown")

        self.update_metrics("image_generation_completed")

        print(f"\n{Fore.GREEN}🎨 Image Generation Complete [{item_id}]")

        self.logger.info(f"Image generation completed: {item_id}")

    # ==================== FILE/WEB SEARCH EVENT HANDLERS ====================

    async def handle_file_search_call_in_progress(self, event_data: dict[str, Any]) -> None:
        """Handle response.file_search_call.in_progress - File search started."""
        self.metrics.search_events += 1
        self.update_metrics("file_search_in_progress")

        print(f"\n{Fore.MAGENTA}🔍 File Search Started")

    async def handle_file_search_call_searching(self, event_data: dict[str, Any]) -> None:
        """Handle response.file_search_call.searching - File search in progress."""
        progress_char = self.get_progress_indicator()

        self.update_metrics("file_search_searching")

        print(f"\r{Fore.MAGENTA}{progress_char} Searching files...", end="", flush=True)

    async def handle_file_search_call_completed(self, event_data: dict[str, Any]) -> None:
        """Handle response.file_search_call.completed - File search complete."""
        item_id = event_data.get("item_id", "unknown")

        self.update_metrics("file_search_completed")

        print(f"\n{Fore.GREEN}🔍 File Search Complete [{item_id}]")

    async def handle_web_search_call_in_progress(self, event_data: dict[str, Any]) -> None:
        """Handle response.web_search_call.in_progress - Web search started."""
        self.metrics.search_events += 1
        self.update_metrics("web_search_in_progress")

        print(f"\n{Fore.BLUE}🌐 Web Search Started")

    async def handle_web_search_call_searching(self, event_data: dict[str, Any]) -> None:
        """Handle response.web_search_call.searching - Web search in progress."""
        progress_char = self.get_progress_indicator()

        self.update_metrics("web_search_searching")

        print(f"\r{Fore.BLUE}{progress_char} Searching web...", end="", flush=True)

    async def handle_web_search_call_completed(self, event_data: dict[str, Any]) -> None:
        """Handle response.web_search_call.completed - Web search complete."""
        item_id = event_data.get("item_id", "unknown")

        self.update_metrics("web_search_completed")

        print(f"\n{Fore.GREEN}🌐 Web Search Complete [{item_id}]")

    # ==================== MCP EVENT HANDLERS ====================

    async def handle_mcp_call_in_progress(self, event_data: dict[str, Any]) -> None:
        """Handle response.mcp_call.in_progress - MCP call started."""
        self.metrics.mcp_events += 1
        self.update_metrics("mcp_call_in_progress")

        print(f"\n{Fore.MAGENTA}🔗 MCP Call Started")

    async def handle_mcp_call_completed(self, event_data: dict[str, Any]) -> None:
        """Handle response.mcp_call.completed - MCP call complete."""
        item_id = event_data.get("item_id", "unknown")

        self.update_metrics("mcp_call_completed")

        print(f"\n{Fore.GREEN}🔗 MCP Call Complete [{item_id}]")

    async def handle_mcp_call_failed(self, event_data: dict[str, Any]) -> None:
        """Handle response.mcp_call.failed - MCP call failed."""
        item_id = event_data.get("item_id", "unknown")

        self.update_metrics("mcp_call_failed")

        print(f"\n{Fore.RED}❌ MCP Call Failed [{item_id}]")

        self.logger.error(f"MCP call failed: {item_id}")

    # ==================== CODE INTERPRETER EVENT HANDLERS ====================

    async def handle_code_interpreter_call_in_progress(self, event_data: dict[str, Any]) -> None:
        """Handle response.code_interpreter_call.in_progress - Code execution started."""
        self.metrics.code_interpreter_events += 1
        self.update_metrics("code_interpreter_in_progress")

        print(f"\n{Fore.GREEN}💻 Code Interpreter Started")

    async def handle_code_interpreter_call_interpreting(self, event_data: dict[str, Any]) -> None:
        """Handle response.code_interpreter_call.interpreting - Code being executed."""
        progress_char = self.get_progress_indicator()

        self.update_metrics("code_interpreter_interpreting")

        print(f"\r{Fore.GREEN}{progress_char} Executing code...", end="", flush=True)

    async def handle_code_interpreter_call_completed(self, event_data: dict[str, Any]) -> None:
        """Handle response.code_interpreter_call.completed - Code execution complete."""
        item_id = event_data.get("item_id", "unknown")

        self.update_metrics("code_interpreter_completed")

        print(f"\n{Fore.GREEN}💻 Code Execution Complete [{item_id}]")

    async def handle_code_interpreter_call_code_delta(self, event_data: dict[str, Any]) -> None:
        """Handle response.code_interpreter_call_code.delta - Code streaming."""
        delta = event_data.get("delta", "")

        self.update_metrics("code_interpreter_code_delta")

        print(f"{Fore.GREEN}{delta}", end="", flush=True)

    async def handle_code_interpreter_call_code_done(self, event_data: dict[str, Any]) -> None:
        """Handle response.code_interpreter_call_code.done - Code complete."""
        code = event_data.get("code", "")

        code_snippet = {
            "code": code,
            "timestamp": datetime.now(),
            "item_id": event_data.get("item_id", "unknown"),
        }

        self.content.code_snippets.append(code_snippet)
        self.update_metrics("code_interpreter_code_done")

        print(f"\n{Fore.GREEN}💻 Code Complete: {len(code)} characters")

        if self.enable_file_output:
            await self._save_code_snippet(code_snippet)

    # ==================== ERROR AND RESPONSE LIFECYCLE HANDLERS ====================

    async def handle_error(self, event_data: dict[str, Any]) -> None:
        """Handle error events."""
        error_code = event_data.get("code", "UNKNOWN")
        error_message = event_data.get("message", "No message provided")
        error_param = event_data.get("param")

        error_info = {
            "code": error_code,
            "message": error_message,
            "param": error_param,
            "timestamp": datetime.now(),
        }

        self.content.errors.append(error_info)
        self.metrics.error_events += 1
        self.update_metrics("error")

        print(f"\n{Fore.RED}❌ ERROR [{error_code}]: {error_message}")
        if error_param:
            print(f"   Parameter: {error_param}")

        self.logger.error(f"Stream error [{error_code}]: {error_message}")

    async def handle_response_created(self, event_data: dict[str, Any]) -> None:
        """Handle response.created - Response creation."""
        response_id = event_data.get("id", "unknown")

        self.update_metrics("response_created")

        print(f"\n{Fore.GREEN}🚀 Response Created [{response_id}]")

        self.logger.info(f"Response created: {response_id}")

    async def handle_response_done(self, event_data: dict[str, Any]) -> None:
        """Handle response.done - Response completion."""
        response_id = event_data.get("id", "unknown")

        self.update_metrics("response_done")

        print(f"\n{Fore.GREEN}🎉 Response Complete [{response_id}]")

        # Generate final report
        if self.enable_file_output:
            await self._generate_final_report()

        self.logger.info(f"Response completed: {response_id}")

    # ==================== CONTENT PART HANDLERS ====================

    async def handle_content_part_added(self, event_data: dict[str, Any]) -> None:
        """Handle response.content_part.added - Content part addition."""
        part = event_data.get("part", {})
        content_index = event_data.get("content_index", 0)

        self.update_metrics("content_part_added")

        part_type = part.get("type", "unknown")
        print(f"\n{Fore.BLUE}📝 Content Part Added [{content_index}]: {part_type}")

    async def handle_content_part_done(self, event_data: dict[str, Any]) -> None:
        """Handle response.content_part.done - Content part completion."""
        part = event_data.get("part", {})
        content_index = event_data.get("content_index", 0)

        self.update_metrics("content_part_done")

        part_type = part.get("type", "unknown")
        print(f"\n{Fore.GREEN}✅ Content Part Complete [{content_index}]: {part_type}")

    # ==================== FILE OUTPUT METHODS ====================

    async def _save_text_output(self, text: str, content_index: int) -> None:
        """Save text output to file."""
        filename = f"text_output_{content_index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

        self.logger.info(f"Saved text output: {filepath}")

    async def _save_function_call(self, function_call: dict[str, Any]) -> None:
        """Save function call to file."""
        filename = (
            f"function_call_{function_call['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(function_call, f, indent=2, default=str)

        self.logger.info(f"Saved function call: {filepath}")

    async def _save_reasoning_output(self, reasoning: str) -> None:
        """Save reasoning output to file."""
        filename = f"reasoning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(reasoning)

        self.logger.info(f"Saved reasoning: {filepath}")

    async def _save_reasoning_summary(self, summary: str) -> None:
        """Save reasoning summary to file."""
        filename = f"reasoning_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(summary)

    async def _save_partial_image(self, image_b64: str, image_index: int) -> None:
        """Save partial image to file."""
        filename = f"partial_image_{image_index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = self.output_dir / filename

        try:
            image_data = base64.b64decode(image_b64)
            with open(filepath, "wb") as f:
                f.write(image_data)

            self.logger.info(f"Saved partial image: {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to save partial image: {e}")

    async def _save_code_snippet(self, code_snippet: dict[str, Any]) -> None:
        """Save code snippet to file."""
        filename = f"code_snippet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Generated by AI Code Interpreter\n")
            f.write(f"# Timestamp: {code_snippet['timestamp']}\n")
            f.write(f"# Item ID: {code_snippet['item_id']}\n\n")
            f.write(code_snippet["code"])

    async def _generate_final_report(self) -> None:
        """Generate comprehensive final report."""
        report = {
            "session_summary": {
                "start_time": self.metrics.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": self.metrics.duration_seconds,
                "total_events": self.metrics.total_events,
                "events_per_second": self.metrics.events_per_second,
            },
            "event_metrics": {
                "text_deltas": self.metrics.text_deltas,
                "function_calls": self.metrics.function_calls,
                "reasoning_events": self.metrics.reasoning_events,
                "error_events": self.metrics.error_events,
                "image_events": self.metrics.image_events,
                "search_events": self.metrics.search_events,
                "mcp_events": self.metrics.mcp_events,
                "code_interpreter_events": self.metrics.code_interpreter_events,
            },
            "event_type_counts": self.event_type_counts,
            "content_summary": {
                "main_text_length": len(self.content.main_text),
                "reasoning_length": len(self.content.reasoning_text),
                "reasoning_summary_length": len(self.content.reasoning_summary),
                "function_call_count": len(self.content.function_calls),
                "code_snippet_count": len(self.content.code_snippets),
                "image_count": len(self.content.images),
                "annotation_count": len(self.content.annotations),
                "error_count": len(self.content.errors),
            },
        }

        filename = f"streaming_session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"Generated final report: {filepath}")

        # Print summary to console
        print(f"\n{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.GREEN}{Style.BRIGHT}📊 STREAMING SESSION COMPLETE")
        print(f"{Fore.CYAN}{'=' * 80}")
        print(f"{Fore.YELLOW}Duration: {Fore.WHITE}{self.metrics.duration_seconds:.1f} seconds")
        print(f"{Fore.YELLOW}Total Events: {Fore.WHITE}{self.metrics.total_events}")
        print(f"{Fore.YELLOW}Events/Second: {Fore.WHITE}{self.metrics.events_per_second:.1f}")
        print(f"{Fore.YELLOW}Text Length: {Fore.WHITE}{len(self.content.main_text)} chars")
        print(f"{Fore.YELLOW}Function Calls: {Fore.WHITE}{len(self.content.function_calls)}")
        print(f"{Fore.YELLOW}Report Saved: {Fore.WHITE}{filepath}")
        print(f"{Fore.CYAN}{'=' * 80}")

    # ==================== MAIN EVENT ROUTER ====================

    async def process_event(self, event_data: dict[str, Any]) -> None:
        """Main event router - dispatches events to appropriate handlers."""
        event_type = event_data.get("type", "unknown")

        # Event handler mapping
        handlers = {
            # Text output events
            "response.output_text.delta": self.handle_output_text_delta,
            "response.output_text.done": self.handle_output_text_done,
            "response.output_text.annotation.added": self.handle_output_text_annotation_added,
            # Function call events
            "response.function_call_arguments.delta": self.handle_function_call_arguments_delta,
            "response.function_call_arguments.done": self.handle_function_call_arguments_done,
            # Reasoning events
            "response.reasoning_text.delta": self.handle_reasoning_text_delta,
            "response.reasoning_text.done": self.handle_reasoning_text_done,
            "response.reasoning_summary_part.added": self.handle_reasoning_summary_part_added,
            "response.reasoning_summary_text.delta": self.handle_reasoning_summary_text_delta,
            "response.reasoning_summary_text.done": self.handle_reasoning_summary_text_done,
            # Refusal events
            "response.refusal.delta": self.handle_refusal_delta,
            "response.refusal.done": self.handle_refusal_done,
            # Image generation events
            "response.image_generation_call.in_progress": self.handle_image_generation_call_in_progress,
            "response.image_generation_call.generating": self.handle_image_generation_call_generating,
            "response.image_generation_call.partial_image": self.handle_image_generation_call_partial_image,
            "response.image_generation_call.completed": self.handle_image_generation_call_completed,
            # File search events
            "response.file_search_call.in_progress": self.handle_file_search_call_in_progress,
            "response.file_search_call.searching": self.handle_file_search_call_searching,
            "response.file_search_call.completed": self.handle_file_search_call_completed,
            # Web search events
            "response.web_search_call.in_progress": self.handle_web_search_call_in_progress,
            "response.web_search_call.searching": self.handle_web_search_call_searching,
            "response.web_search_call.completed": self.handle_web_search_call_completed,
            # MCP events
            "response.mcp_call.in_progress": self.handle_mcp_call_in_progress,
            "response.mcp_call.completed": self.handle_mcp_call_completed,
            "response.mcp_call.failed": self.handle_mcp_call_failed,
            # Code interpreter events
            "response.code_interpreter_call.in_progress": self.handle_code_interpreter_call_in_progress,
            "response.code_interpreter_call.interpreting": self.handle_code_interpreter_call_interpreting,
            "response.code_interpreter_call.completed": self.handle_code_interpreter_call_completed,
            "response.code_interpreter_call_code.delta": self.handle_code_interpreter_call_code_delta,
            "response.code_interpreter_call_code.done": self.handle_code_interpreter_call_code_done,
            # Response lifecycle events
            "response.created": self.handle_response_created,
            "response.done": self.handle_response_done,
            # Content part events
            "response.content_part.added": self.handle_content_part_added,
            "response.content_part.done": self.handle_content_part_done,
            # Error events
            "error": self.handle_error,
        }

        # Dispatch to handler
        if event_type in handlers:
            await handlers[event_type](event_data)
        else:
            # Handle unknown event types
            self.update_metrics(f"unknown_{event_type}")
            print(f"\n{Fore.YELLOW}⚠️  Unknown event type: {event_type}")
            self.logger.warning(f"Unknown event type: {event_type}")

    def print_metrics_summary(self) -> None:
        """Print current metrics summary."""
        print(f"\n{Fore.CYAN}📊 Event Metrics Summary:")
        print(f"   {Fore.YELLOW}Total Events: {Fore.WHITE}{self.metrics.total_events}")
        print(f"   {Fore.YELLOW}Duration: {Fore.WHITE}{self.metrics.duration_seconds:.1f}s")
        print(f"   {Fore.YELLOW}Rate: {Fore.WHITE}{self.metrics.events_per_second:.1f} events/sec")
        print(f"   {Fore.YELLOW}Text Deltas: {Fore.WHITE}{self.metrics.text_deltas}")
        print(f"   {Fore.YELLOW}Function Calls: {Fore.WHITE}{len(self.content.function_calls)}")
        print(f"   {Fore.YELLOW}Errors: {Fore.WHITE}{self.metrics.error_events}")


# ==================== DEMO AND TESTING ====================


async def demo_event_processor():
    """Demo the advanced event processor with simulated events."""
    processor = AdvancedStreamEventProcessor()

    print(f"{Fore.GREEN}{Style.BRIGHT}🚀 EQ12 Advanced Stream Event Processor Demo")
    print(f"{Fore.CYAN}{'=' * 80}")

    # Simulate various events
    test_events = [
        {"type": "response.created", "id": "resp_demo_123"},
        {"type": "response.output_text.delta", "delta": "Hello, "},
        {"type": "response.output_text.delta", "delta": "this is "},
        {"type": "response.output_text.delta", "delta": "a streaming "},
        {"type": "response.output_text.delta", "delta": "response!"},
        {"type": "response.reasoning_text.delta", "delta": "I'm thinking about "},
        {"type": "response.reasoning_text.delta", "delta": "how to respond..."},
        {"type": "response.function_call_arguments.delta", "delta": '{"query": '},
        {"type": "response.function_call_arguments.delta", "delta": '"test"}'},
        {
            "type": "response.function_call_arguments.done",
            "name": "search",
            "arguments": '{"query": "test"}',
        },
        {
            "type": "response.output_text.done",
            "text": "Hello, this is a streaming response!",
        },
        {"type": "response.done", "id": "resp_demo_123"},
    ]

    print(f"\n{Fore.BLUE}Processing {len(test_events)} simulated events...")

    for _i, event in enumerate(test_events):
        await processor.process_event(event)
        await asyncio.sleep(0.2)  # Simulate real-time delay

    processor.print_metrics_summary()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(demo_event_processor()))
