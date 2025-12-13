"""
EQ12 Unified AI Client - Azure-first with OpenAI fallback and 429-safe handling
Routes to Azure or OpenAI with automatic retry/backoff and budget guardrails
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import UTC, datetime, timedelta
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

try:
    from eq12_budget_enforcer import budget_enforcer
except ImportError:
    budget_enforcer = None

try:
    import hashlib
    import hmac
    import uuid
except ImportError:
    uuid = hmac = hashlib = None

try:
    import fnmatch
except ImportError:
    fnmatch = None

logger = logging.getLogger(__name__)


# Module-level debug function for API headers
def _log_api_debug_info(headers: dict[str, str], response_data: dict | None = None) -> None:
    """Log API debugging information including request ID and rate limits"""
    if not ENABLE_DEBUG_HEADERS:
        return

    debug_info = {
        "timestamp": datetime.now(UTC).isoformat(),
        "request_id": headers.get("x-request-id"),
        "organization": headers.get("openai-organization"),
        "processing_ms": headers.get("openai-processing-ms"),
        "api_version": headers.get("openai-version"),
        "rate_limits": {
            "requests_limit": headers.get("x-ratelimit-limit-requests"),
            "tokens_limit": headers.get("x-ratelimit-limit-tokens"),
            "requests_remaining": headers.get("x-ratelimit-remaining-requests"),
            "tokens_remaining": headers.get("x-ratelimit-remaining-tokens"),
            "requests_reset": headers.get("x-ratelimit-reset-requests"),
            "tokens_reset": headers.get("x-ratelimit-reset-tokens"),
        },
    }

    # Log to file for production troubleshooting
    try:
        os.makedirs(os.path.dirname(REQUEST_ID_LOG_FILE), exist_ok=True)
        with open(REQUEST_ID_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(debug_info) + "\n")
    except Exception as e:
        logger.debug(f"Failed to log request debug info: {e}")

    logger.debug(
        f"API Debug - Request ID: {debug_info['request_id']}, Processing: {debug_info['processing_ms']}ms"
    )

    def create_conversation(self, metadata: dict | None = None) -> dict[str, Any]:
        """
        Create a new conversation for stateful interactions

        Args:
            metadata: Optional metadata to attach to conversation

        Returns:
            Conversation object from OpenAI API
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        try:
            params = {}
            if metadata:
                params["metadata"] = metadata

            logger.info("Creating new conversation")
            conversation = self.openai_client.conversations.create(**params)

            # Send webhook event
            send_webhook_event(
                "openai.conversations.created",
                {
                    "conversation_id": getattr(conversation, "id", None),
                    "metadata": metadata,
                },
            )

            logger.info(f"Created conversation: {getattr(conversation, 'id', 'unknown')}")
            return conversation

        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            send_webhook_event(
                "openai.conversations.error", {"error": str(e), "operation": "create"}
            )
            raise

    def retrieve_conversation(self, conversation_id: str) -> dict[str, Any]:
        """
        Retrieve a conversation by ID

        Args:
            conversation_id: The ID of the conversation to retrieve

        Returns:
            Conversation object from OpenAI API
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        try:
            logger.info(f"Retrieving conversation {conversation_id}")
            conversation = self.openai_client.conversations.retrieve(conversation_id)

            send_webhook_event(
                "openai.conversations.retrieved",
                {
                    "conversation_id": conversation_id,
                },
            )

            return conversation

        except Exception as e:
            logger.error(f"Conversation retrieval failed: {e}")
            send_webhook_event(
                "openai.conversations.error",
                {"conversation_id": conversation_id, "error": str(e), "operation": "retrieve"},
            )
            raise

    def update_conversation(
        self, conversation_id: str, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Update a conversation's metadata

        Args:
            conversation_id: The ID of the conversation to update
            metadata: New metadata for the conversation

        Returns:
            Updated conversation object
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        try:
            params = {}
            if metadata is not None:
                params["metadata"] = metadata

            logger.info(f"Updating conversation {conversation_id}")
            conversation = self.openai_client.conversations.update(conversation_id, **params)

            send_webhook_event(
                "openai.conversations.updated",
                {
                    "conversation_id": conversation_id,
                    "metadata": metadata,
                },
            )

            return conversation

        except Exception as e:
            logger.error(f"Conversation update failed: {e}")
            send_webhook_event(
                "openai.conversations.error",
                {"conversation_id": conversation_id, "error": str(e), "operation": "update"},
            )
            raise

    def list_conversations(
        self,
        limit: int = 20,
        order: str = "desc",
        after: str | None = None,
        before: str | None = None,
    ) -> dict[str, Any]:
        """
        List conversations

        Args:
            limit: Number of conversations to return (1-100)
            order: Sort order ("asc" or "desc")
            after: Cursor for pagination
            before: Cursor for pagination

        Returns:
            List of conversation objects
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        params = {
            "limit": min(limit, 100),  # API max is 100
            "order": order,
        }

        if after:
            params["after"] = after
        if before:
            params["before"] = before

        try:
            logger.info(f"Listing conversations with params: {params}")
            response = self.openai_client.conversations.list(**params)

            send_webhook_event(
                "openai.conversations.listed",
                {
                    "count": len(getattr(response, "data", [])),
                    "limit": limit,
                },
            )

            return response

        except Exception as e:
            logger.error(f"Conversation listing failed: {e}")
            send_webhook_event("openai.conversations.error", {"error": str(e), "operation": "list"})
            raise

    def create_response(
        self,
        model: str = "gpt-4o",
        instructions: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        conversation_id: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        stream: bool = False,
        max_completion_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Create a new response using OpenAI Responses API

        Args:
            model: The model to use for the response
            instructions: System instructions for the assistant
            messages: List of messages for the conversation
            conversation_id: Optional conversation ID to associate with
            tools: List of tools the assistant can use
            stream: Whether to stream the response
            max_completion_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0-2)
            **kwargs: Additional parameters

        Returns:
            Response object from OpenAI API
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        # Apply model routing
        routed_model = route_model(model, task_type="chat")
        if routed_model != model:
            logger.info(f"Model routed: {model} → {routed_model}")
            model = routed_model

        # Build request parameters
        params = {
            "model": model,
        }

        if instructions:
            params["instructions"] = instructions
        if messages:
            params["messages"] = messages
        if conversation_id:
            params["conversation_id"] = conversation_id
        if tools:
            params["tools"] = tools
        if stream is not None:
            params["stream"] = stream
        if max_completion_tokens is not None:
            params["max_completion_tokens"] = max_completion_tokens
        if temperature is not None:
            params["temperature"] = temperature

        # Add any additional parameters
        params.update(kwargs)

        try:
            # Rate limit check
            estimated_tokens = self._estimate_request_tokens(params)
            if not enforce_local_rate_limit(model, estimated_tokens):
                raise RuntimeError(f"Rate limit exceeded for model {model}")

            # Budget check
            if budget_enforcer:
                allowed, reason, routing = budget_enforcer.check_request_allowed(
                    "responses_api", model, estimated_tokens, 0
                )
                if not allowed:
                    raise RuntimeError(f"Budget policy violation: {reason}")

                if routing.get("degraded"):
                    params["model"] = routing["model"]
                    model = routing["model"]
                    logger.info(f"Budget policy degraded to {model}")

            logger.info(f"Creating response with model {model}")
            response = self.openai_client.responses.create(**params)

            # Log API debug info if response has headers
            if hasattr(response, "_headers"):
                self._log_api_debug_info(response._headers, "responses.create")

            # Log usage if available
            usage = getattr(response, "usage", None)
            if usage:
                cost = self._estimate_responses_api_cost(model, usage, "create")
                self._log_responses_api_usage(
                    "create",
                    model,
                    response_id=getattr(response, "id", None),
                    conversation_id=conversation_id,
                    usage=usage,
                    cost=cost,
                    feature="responses_api",
                )

                # Record budget usage for policy enforcement
                if budget_enforcer:
                    budget_enforcer.record_usage(
                        "responses_api",
                        model,
                        usage.get("prompt_tokens", 0),
                        usage.get("completion_tokens", 0),
                        cost,
                    )

            # Send webhook event
            send_webhook_event(
                "openai.responses.created",
                {
                    "response_id": getattr(response, "id", None),
                    "model": model,
                    "status": getattr(response, "status", "unknown"),
                    "conversation_id": conversation_id,
                    "stream": stream,
                    "usage": usage,
                    "cost": cost if usage else None,
                },
            )

            return response

        except Exception as e:
            logger.error(f"Response creation failed: {e}")
            send_webhook_event(
                "openai.responses.error",
                {
                    "model": model,
                    "error": str(e),
                    "conversation_id": conversation_id,
                    "operation": "create",
                },
            )
            raise

    def retrieve_response(self, response_id: str) -> dict[str, Any]:
        """
        Retrieve a response by ID

        Args:
            response_id: The ID of the response to retrieve

        Returns:
            Response object from OpenAI API
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        try:
            logger.info(f"Retrieving response {response_id}")
            response = self.openai_client.responses.retrieve(response_id)

            # Log API debug info if response has headers
            if hasattr(response, "_headers"):
                self._log_api_debug_info(response._headers, "responses.retrieve")

            send_webhook_event(
                "openai.responses.retrieved",
                {
                    "response_id": response_id,
                    "status": getattr(response, "status", "unknown"),
                },
            )

            return response

        except Exception as e:
            logger.error(f"Response retrieval failed: {e}")
            send_webhook_event(
                "openai.responses.error",
                {"response_id": response_id, "error": str(e), "operation": "retrieve"},
            )
            raise

    def list_responses(
        self,
        conversation_id: str | None = None,
        limit: int = 20,
        order: str = "desc",
        after: str | None = None,
        before: str | None = None,
    ) -> dict[str, Any]:
        """
        List responses, optionally filtered by conversation

        Args:
            conversation_id: Optional conversation ID to filter by
            limit: Number of responses to return (1-100)
            order: Sort order ("asc" or "desc")
            after: Cursor for pagination
            before: Cursor for pagination

        Returns:
            List of response objects
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        params = {
            "limit": min(limit, 100),  # API max is 100
            "order": order,
        }

        if conversation_id:
            params["conversation_id"] = conversation_id
        if after:
            params["after"] = after
        if before:
            params["before"] = before

        try:
            logger.info(f"Listing responses with params: {params}")
            response = self.openai_client.responses.list(**params)

            send_webhook_event(
                "openai.responses.listed",
                {
                    "conversation_id": conversation_id,
                    "count": len(getattr(response, "data", [])),
                    "limit": limit,
                },
            )

            return response

        except Exception as e:
            logger.error(f"Response listing failed: {e}")
            send_webhook_event(
                "openai.responses.error",
                {"conversation_id": conversation_id, "error": str(e), "operation": "list"},
            )
            raise

    def ask_with_responses_api(
        self,
        prompt: str,
        conversation_id: str | None = None,
        tools: list[str] | None = None,
        structured_output: dict | None = None,
        model: str = "gpt-4o",
        stream: bool = False,
        **kwargs,
    ) -> dict:
        """
        Convenience method using Responses API for advanced interactions

        Args:
            prompt: User message
            conversation_id: Optional conversation ID for stateful interactions
            tools: List of tools to enable ('file_search', 'web_search', 'function')
            structured_output: Optional Pydantic schema for structured outputs
            model: Model to use
            stream: Whether to stream the response
            **kwargs: Additional parameters

        Returns:
            Complete response data with headers and metadata
        """
        if not self.openai_client:
            logger.warning("Responses API not available, falling back to standard chat")
            response_text = self.ask(prompt, model=model, **kwargs)
            return {"content": response_text, "conversation_id": None, "tools_used": []}

        try:
            # Prepare messages
            messages = [{"role": "user", "content": prompt}]

            # Prepare tools if specified
            prepared_tools = None
            if tools:
                prepared_tools = self._prepare_tools(tools)

            # Use the Responses API
            response = self.create_response(
                model=model,
                messages=messages,
                conversation_id=conversation_id,
                tools=prepared_tools,
                stream=stream,
                **kwargs,
            )

            # Handle streaming vs non-streaming response
            if stream:
                return {
                    "response_id": getattr(response, "id", None),
                    "status": getattr(response, "status", "unknown"),
                    "conversation_id": conversation_id,
                    "stream": True,
                    "response_object": response,
                }
            else:
                # For non-streaming, we may need to poll for completion
                response_id = getattr(response, "id", None)
                if response_id and response.status in ["queued", "in_progress"]:
                    # Poll for completion
                    response = self._poll_for_completion(response_id)

                return {
                    "content": getattr(response, "output", {}).get("content", ""),
                    "conversation_id": conversation_id,
                    "tools_used": getattr(response, "output", {}).get("tool_calls", []),
                    "usage": getattr(response, "usage", {}),
                    "model": getattr(response, "model", model),
                    "response_id": getattr(response, "id", None),
                    "status": getattr(response, "status", "unknown"),
                }

        except Exception as e:
            logger.error(f"Responses API request failed: {e}")
            # Fallback to regular ask method
            response_text = self.ask(prompt, model=model, **kwargs)
            return {
                "content": response_text,
                "conversation_id": None,
                "tools_used": [],
                "error": str(e),
            }

    def _prepare_tools(self, tool_names: list[str] | list[dict]) -> list[dict]:
        """
        Prepare tools configuration for Responses API

        Args:
            tool_names: List of tool names or full tool definitions

        Returns:
            List of tool configuration objects
        """
        if not tool_names:
            return []

        # If already formatted as tool objects, return as-is
        if isinstance(tool_names[0], dict):
            return tool_names

        # Standard tool definitions
        available_tools = {
            "file_search": {
                "type": "file_search",
                "file_search": {
                    "max_num_results": 20,
                    "ranking_options": {"score_threshold": 0.0, "ranker": "default_2024_08_21"},
                },
            },
            "web_search": {"type": "web_search", "web_search": {"max_num_results": 10}},
            "function": {
                "type": "function",
                "function": {
                    "name": "eq12_function_call",
                    "description": "Execute EQ12 system functions for automation and data processing",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "function_name": {
                                "type": "string",
                                "description": "Name of the EQ12 function to call",
                                "enum": [
                                    "parlay_analysis",
                                    "odds_comparison",
                                    "market_data",
                                    "risk_assessment",
                                    "bet_tracking",
                                    "performance_analysis",
                                ],
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Parameters for the function call",
                            },
                        },
                        "required": ["function_name"],
                    },
                },
            },
            "computer_use": {
                "type": "computer_use",
                "computer_use": {
                    "display_width_px": 1920,
                    "display_height_px": 1080,
                    "display_number": 0,
                },
            },
        }

        # EQ12-specific custom tools
        eq12_tools = {
            "eq12_parlay_analyzer": {
                "type": "function",
                "function": {
                    "name": "analyze_parlay_opportunities",
                    "description": "Analyze NFL games for optimal parlay betting strategies",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "games_data": {
                                "type": "array",
                                "description": "Array of game data objects with teams, odds, and metadata",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "home_team": {"type": "string"},
                                        "away_team": {"type": "string"},
                                        "commence_time": {"type": "string"},
                                        "odds": {"type": "object"},
                                    },
                                },
                            },
                            "bankroll": {
                                "type": "number",
                                "description": "Available bankroll for betting",
                                "minimum": 0,
                            },
                            "risk_tolerance": {
                                "type": "string",
                                "enum": ["conservative", "balanced", "aggressive"],
                                "description": "Risk tolerance level",
                            },
                        },
                        "required": ["games_data"],
                    },
                },
            },
            "eq12_odds_tracker": {
                "type": "function",
                "function": {
                    "name": "track_odds_movement",
                    "description": "Track and analyze sports betting odds movements across sportsbooks",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sport": {
                                "type": "string",
                                "enum": ["american_football", "basketball", "baseball", "hockey"],
                            },
                            "market": {"type": "string", "enum": ["h2h", "spreads", "totals"]},
                            "lookback_hours": {"type": "number", "minimum": 1, "maximum": 168},
                            "sportsbooks": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of sportsbook keys to track",
                            },
                        },
                        "required": ["sport", "market"],
                    },
                },
            },
            "eq12_browser_automation": {
                "type": "function",
                "function": {
                    "name": "automate_browser_task",
                    "description": "Automate browser tasks for governance and data collection",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_type": {
                                "type": "string",
                                "enum": [
                                    "governance_check",
                                    "data_scraping",
                                    "form_submission",
                                    "bookmark_management",
                                ],
                                "description": "Type of browser automation task",
                            },
                            "target_url": {
                                "type": "string",
                                "description": "Target URL for the task",
                            },
                            "actions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string"},
                                        "selector": {"type": "string"},
                                        "value": {"type": "string"},
                                    },
                                },
                            },
                        },
                        "required": ["task_type"],
                    },
                },
            },
        }

        # Combine standard and EQ12 tools
        all_tools = {**available_tools, **eq12_tools}

        # Return requested tools
        prepared_tools = []
        for name in tool_names:
            if name in all_tools:
                prepared_tools.append(all_tools[name])
            else:
                logger.warning(f"Unknown tool: {name}")

        logger.info(
            f"Prepared {len(prepared_tools)} tools: {[t.get('type', 'unknown') for t in prepared_tools]}"
        )
        return prepared_tools

    def _estimate_request_tokens(self, params: dict[str, Any]) -> int:
        """
        Estimate token count for a request

        Args:
            params: Request parameters

        Returns:
            Estimated token count
        """
        total_tokens = 0

        # Estimate from messages
        messages = params.get("messages", [])
        for message in messages:
            content = message.get("content", "")
            if isinstance(content, str):
                total_tokens += len(content.split()) * 1.33  # Rough estimation

        # Estimate from instructions
        instructions = params.get("instructions", "")
        if instructions:
            total_tokens += len(instructions.split()) * 1.33

        # Add buffer for tools and other parameters
        if params.get("tools"):
            total_tokens += 200  # Approximate overhead for tools

        return int(total_tokens)

    def _poll_for_completion(
        self, response_id: str, max_attempts: int = 30, poll_interval: float = 2.0
    ) -> dict[str, Any]:
        """
        Poll for response completion

        Args:
            response_id: ID of the response to poll
            max_attempts: Maximum number of polling attempts
            poll_interval: Time to wait between polls in seconds

        Returns:
            Completed response object
        """
        for attempt in range(max_attempts):
            try:
                response = self.retrieve_response(response_id)
                status = getattr(response, "status", "unknown")

                if status == "completed":
                    logger.info(f"Response {response_id} completed after {attempt + 1} polls")
                    return response
                elif status == "failed":
                    error_msg = f"Response {response_id} failed: {getattr(response, 'error', 'Unknown error')}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
                elif status in ["queued", "in_progress"]:
                    logger.debug(
                        f"Response {response_id} status: {status}, polling again in {poll_interval}s"
                    )
                    time.sleep(poll_interval)
                    continue
                else:
                    logger.warning(f"Unknown response status: {status}")
                    time.sleep(poll_interval)
                    continue

            except Exception as e:
                logger.error(f"Error polling response {response_id}: {e}")
                if attempt == max_attempts - 1:
                    raise
                time.sleep(poll_interval)

        raise RuntimeError(
            f"Response {response_id} did not complete within {max_attempts} attempts"
        )

    def stream_response(
        self,
        model: str = "gpt-4o",
        instructions: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        conversation_id: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs,
    ):
        """
        Create a streaming response using OpenAI Responses API

        Args:
            model: The model to use for the response
            instructions: System instructions for the assistant
            messages: List of messages for the conversation
            conversation_id: Optional conversation ID to associate with
            tools: List of tools the assistant can use
            **kwargs: Additional parameters

        Yields:
            Streaming response events from OpenAI API
        """
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized. Check OPENAI_API_KEY.")

        # Create streaming response
        response_stream = self.create_response(
            model=model,
            instructions=instructions,
            messages=messages,
            conversation_id=conversation_id,
            tools=tools,
            stream=True,
            **kwargs,
        )

        try:
            for event in response_stream:
                # Process and yield each streaming event
                event_data = {
                    "type": getattr(event, "event_type", "unknown"),
                    "data": getattr(event, "data", {}),
                    "timestamp": datetime.now(UTC).isoformat(),
                }

                # Log streaming events
                if hasattr(event, "event_type"):
                    logger.debug(f"Streaming event: {event.event_type}")

                # Send webhook for important events
                if event_data["type"] in ["content.delta", "response.done", "error"]:
                    send_webhook_event(
                        f"openai.streaming.{event_data['type']}",
                        {"conversation_id": conversation_id, "model": model, "event": event_data},
                    )

                yield event

        except Exception as e:
            logger.error(f"Streaming response failed: {e}")
            send_webhook_event(
                "openai.streaming.error",
                {"conversation_id": conversation_id, "model": model, "error": str(e)},
            )
            raise

    def process_streaming_events(self, response_stream) -> dict[str, Any]:
        """
        Process a streaming response and collect the final result

        Args:
            response_stream: Streaming response from OpenAI API

        Returns:
            Processed response data
        """
        collected_content = []
        tool_calls = []
        usage_data = {}
        response_metadata = {}

        try:
            for event in response_stream:
                event_type = getattr(event, "event_type", None)

                if event_type == "response.content.delta":
                    # Collect content deltas
                    delta = getattr(event, "data", {}).get("delta", {})
                    if "text" in delta:
                        collected_content.append(delta["text"])

                elif event_type == "response.function_call_delta":
                    # Collect function call information
                    function_data = getattr(event, "data", {})
                    tool_calls.append(function_data)

                elif event_type == "response.done":
                    # Collect final metadata
                    response_data = getattr(event, "data", {})
                    usage_data = response_data.get("usage", {})
                    response_metadata = response_data.get("response", {})

                elif event_type == "error":
                    error_data = getattr(event, "data", {})
                    logger.error(f"Streaming error: {error_data}")
                    raise RuntimeError(f"Streaming failed: {error_data}")

            # Combine collected data
            final_content = "".join(collected_content)

            return {
                "content": final_content,
                "tool_calls": tool_calls,
                "usage": usage_data,
                "metadata": response_metadata,
                "status": "completed",
            }

        except Exception as e:
            logger.error(f"Error processing streaming events: {e}")
            return {
                "content": "",
                "tool_calls": [],
                "usage": {},
                "metadata": {},
                "status": "failed",
                "error": str(e),
            }

    async def async_stream_response(
        self,
        model: str = "gpt-4o",
        instructions: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        conversation_id: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        **kwargs,
    ):
        """
        Async version of stream_response for non-blocking streaming

        Args:
            model: The model to use for the response
            instructions: System instructions for the assistant
            messages: List of messages for the conversation
            conversation_id: Optional conversation ID to associate with
            tools: List of tools the assistant can use
            **kwargs: Additional parameters

        Yields:
            Streaming response events from OpenAI API
        """
        # Note: This would require async OpenAI client
        # For now, we'll run the sync version in an executor
        import asyncio
        import concurrent.futures

        def _sync_stream():
            return list(
                self.stream_response(
                    model=model,
                    instructions=instructions,
                    messages=messages,
                    conversation_id=conversation_id,
                    tools=tools,
                    **kwargs,
                )
            )

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            events = await loop.run_in_executor(executor, _sync_stream)

            for event in events:
                yield event

    def get_response_status(self, response_id: str) -> dict[str, Any]:
        """
        Get the current status of a response

        Args:
            response_id: ID of the response to check

        Returns:
            Response status information
        """
        try:
            response = self.retrieve_response(response_id)
            status = getattr(response, "status", "unknown")

            status_info = {
                "response_id": response_id,
                "status": status,
                "created_at": getattr(response, "created_at", None),
                "completed_at": getattr(response, "completed_at", None),
                "model": getattr(response, "model", None),
                "conversation_id": getattr(response, "conversation_id", None),
            }

            # Add error details if failed
            if status == "failed":
                status_info["error"] = getattr(response, "error", {})

            # Add progress info if in progress
            if status == "in_progress":
                status_info["progress"] = getattr(response, "progress", {})

            return status_info

        except Exception as e:
            logger.error(f"Failed to get response status for {response_id}: {e}")
            return {"response_id": response_id, "status": "error", "error": str(e)}

    def wait_for_response(
        self, response_id: str, timeout: float = 300.0, poll_interval: float = 2.0
    ) -> dict[str, Any]:
        """
        Wait for a response to complete with timeout

        Args:
            response_id: ID of the response to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: How often to check status in seconds

        Returns:
            Completed response object
        """
        start_time = time.time()
        max_attempts = int(timeout / poll_interval)

        logger.info(f"Waiting for response {response_id} (timeout: {timeout}s)")

        for attempt in range(max_attempts):
            try:
                response = self.retrieve_response(response_id)
                status = getattr(response, "status", "unknown")

                if status == "completed":
                    elapsed = time.time() - start_time
                    logger.info(f"Response {response_id} completed in {elapsed:.1f}s")
                    return response
                elif status == "failed":
                    error = getattr(response, "error", "Unknown error")
                    raise RuntimeError(f"Response {response_id} failed: {error}")
                elif status in ["queued", "in_progress"]:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        raise TimeoutError(f"Response {response_id} timed out after {timeout}s")

                    logger.debug(f"Response {response_id} status: {status} ({elapsed:.1f}s)")
                    time.sleep(poll_interval)
                    continue
                else:
                    logger.warning(f"Unknown response status: {status}")
                    time.sleep(poll_interval)
                    continue

            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                logger.warning(f"Error checking response status: {e}")
                time.sleep(poll_interval)

        raise TimeoutError(f"Response {response_id} did not complete within {timeout}s")

    def cancel_response(self, response_id: str) -> bool:
        """
        Attempt to cancel a queued or in-progress response

        Args:
            response_id: ID of the response to cancel

        Returns:
            True if cancellation was successful
        """
        try:
            # Check current status
            response = self.retrieve_response(response_id)
            status = getattr(response, "status", "unknown")

            if status in ["completed", "failed"]:
                logger.info(f"Response {response_id} already finished ({status})")
                return False

            # Attempt cancellation (API method may vary)
            if hasattr(self.openai_client.responses, "cancel"):
                self.openai_client.responses.cancel(response_id)

                send_webhook_event(
                    "openai.responses.cancelled",
                    {"response_id": response_id, "previous_status": status},
                )

                logger.info(f"Response {response_id} cancellation requested")
                return True
            else:
                logger.warning("Response cancellation not supported by API")
                return False

        except Exception as e:
            logger.error(f"Failed to cancel response {response_id}: {e}")
            send_webhook_event(
                "openai.responses.error",
                {"response_id": response_id, "error": str(e), "operation": "cancel"},
            )
            return False

    def get_background_responses(self) -> list[dict[str, Any]]:
        """
        Get all background/async responses that are still processing

        Returns:
            List of background response status objects
        """
        try:
            # List recent responses
            responses = self.list_responses(limit=50)
            background_responses = []

            for response_data in getattr(responses, "data", []):
                status = getattr(response_data, "status", "unknown")
                if status in ["queued", "in_progress"]:
                    background_responses.append(
                        {
                            "response_id": response_data.id,
                            "status": status,
                            "created_at": response_data.created_at,
                            "model": response_data.model,
                            "conversation_id": response_data.conversation_id,
                        }
                    )

            logger.info(f"Found {len(background_responses)} background responses")
            return background_responses

        except Exception as e:
            logger.error(f"Failed to get background responses: {e}")
            return []

    def _log_responses_api_usage(
        self,
        operation: str,
        model: str,
        response_id: str | None = None,
        conversation_id: str | None = None,
        usage: dict[str, Any] | None = None,
        cost: float | None = None,
        feature: str = "responses_api",
    ):
        """
        Log Responses API usage with enhanced tracking

        Args:
            operation: Type of operation (create, retrieve, stream, etc.)
            model: Model used
            response_id: Response ID if applicable
            conversation_id: Conversation ID if applicable
            usage: Usage statistics from API
            cost: Estimated cost
            feature: Feature name for tracking
        """
        usage_record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "operation": operation,
            "api_type": "responses",
            "model": model,
            "feature": feature,
            "response_id": response_id,
            "conversation_id": conversation_id,
            "usage": usage or {},
            "estimated_cost": cost or 0.0,
            "provider": "openai_responses",
        }

        # Add detailed usage info if available
        if usage:
            usage_record.update(
                {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                }
            )

        try:
            os.makedirs(os.path.dirname(self.usage_log_path), exist_ok=True)
            with open(self.usage_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(usage_record) + "\n")

            logger.debug(f"Logged {operation} usage: {response_id or 'N/A'}")

        except Exception as e:
            logger.warning(f"Could not log Responses API usage: {e}")

    def _estimate_responses_api_cost(
        self, model: str, usage: dict[str, Any] | None = None, operation: str = "create"
    ) -> float:
        """
        Estimate cost for Responses API operations

        Args:
            model: Model used
            usage: Usage statistics
            operation: Type of operation

        Returns:
            Estimated cost in USD
        """
        if not usage:
            return 0.0

        # Base costs (may need adjustment based on actual API pricing)
        base_cost = self._estimate_cost(
            model, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
        )

        # Add operation overhead for Responses API
        operation_multipliers = {
            "create": 1.0,
            "retrieve": 0.1,  # Minimal cost for retrieval
            "list": 0.05,  # Very low cost for listing
            "stream": 1.2,  # Slight overhead for streaming
            "poll": 0.02,  # Very low cost for status polling
        }

        multiplier = operation_multipliers.get(operation, 1.0)
        total_cost = base_cost * multiplier

        logger.debug(
            f"Estimated {operation} cost: ${total_cost:.6f} (base: ${base_cost:.6f}, multiplier: {multiplier})"
        )
        return total_cost

    def get_responses_api_usage_summary(self, days: int = 1) -> dict[str, Any]:
        """
        Get usage summary specifically for Responses API calls

        Args:
            days: Number of days to analyze

        Returns:
            Detailed usage summary for Responses API
        """
        if not os.path.exists(self.usage_log_path):
            return {"error": "No usage log found"}

        try:
            cutoff_date = (datetime.now(UTC) - timedelta(days=days)).date()

            responses_usage = {
                "total_operations": 0,
                "total_cost": 0.0,
                "operations_by_type": {},
                "models_used": {},
                "conversations": set(),
                "responses": set(),
                "features": {},
            }

            with open(self.usage_log_path, encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)

                        # Skip non-Responses API records
                        if record.get("api_type") != "responses":
                            continue

                        record_date = datetime.fromisoformat(record["timestamp"]).date()
                        if record_date < cutoff_date:
                            continue

                        # Collect statistics
                        operation = record.get("operation", "unknown")
                        model = record.get("model", "unknown")
                        cost = float(record.get("estimated_cost", 0))
                        feature = record.get("feature", "unknown")

                        responses_usage["total_operations"] += 1
                        responses_usage["total_cost"] += cost

                        # By operation type
                        responses_usage["operations_by_type"][operation] = (
                            responses_usage["operations_by_type"].get(operation, 0) + 1
                        )

                        # By model
                        responses_usage["models_used"][model] = (
                            responses_usage["models_used"].get(model, 0) + cost
                        )

                        # By feature
                        responses_usage["features"][feature] = (
                            responses_usage["features"].get(feature, 0) + cost
                        )

                        # Collect unique IDs
                        if record.get("conversation_id"):
                            responses_usage["conversations"].add(record["conversation_id"])
                        if record.get("response_id"):
                            responses_usage["responses"].add(record["response_id"])

                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        logger.debug(f"Skipped invalid usage record: {e}")
                        continue

            # Convert sets to counts
            responses_usage["unique_conversations"] = len(responses_usage["conversations"])
            responses_usage["unique_responses"] = len(responses_usage["responses"])
            del responses_usage["conversations"]
            del responses_usage["responses"]

            # Round costs
            responses_usage["total_cost"] = round(responses_usage["total_cost"], 4)
            for model in responses_usage["models_used"]:
                responses_usage["models_used"][model] = round(
                    responses_usage["models_used"][model], 4
                )
            for feature in responses_usage["features"]:
                responses_usage["features"][feature] = round(
                    responses_usage["features"][feature], 4
                )

            return {"period_days": days, "responses_api_usage": responses_usage}

        except Exception as e:
            return {"error": f"Failed to analyze Responses API usage: {e}"}

    def get_conversation_state(self, conversation_id: str) -> dict:
        """Get current state of a conversation"""
        # This would interact with Responses API to get conversation history
        # Implementation depends on actual API interface
        return {"conversation_id": conversation_id, "status": "conceptual"}

    def get_last_request_debug_info(self) -> dict:
        """Get debugging info from the last API request"""
        return {
            "request_id": self.last_request_id,
            "headers": self.last_headers,
            "rate_limits": {
                k: v for k, v in self.last_headers.items() if k.startswith("x-ratelimit-")
            },
        }


def get_ai_client() -> EQ12AIClient:
    """Get global AI client singleton"""
    global _global_client
    if _global_client is None:
        _global_client = EQ12AIClient()
    return _global_client


def ask(prompt: str, system: str | None = None, model: str = "gpt-4o", **kwargs) -> str:
    """Convenience function for AI queries"""
    return get_ai_client().ask(prompt, system, model, **kwargs)


def ask_with_responses(prompt: str, tools: list[str] | None = None, **kwargs) -> dict:
    """Convenience function for Responses API queries"""
    return get_ai_client().ask_with_responses_api(prompt, tools=tools, **kwargs)


# Responses API configuration
ALLOWED_MODELS = set(os.getenv("EQ12_ALLOWED_MODELS", "gpt-4o-mini,gpt-4o").split(","))
BLOCKED_MODELS = os.getenv("EQ12_BLOCKED_MODELS", "").split(",")
DEFAULT_CHAT_MODEL = os.getenv("EQ12_DEFAULT_CHAT_MODEL", "gpt-4o-mini")
DEFAULT_EMBEDDING_MODEL = os.getenv("EQ12_DEFAULT_EMBEDDING_MODEL", "text-embedding-3-small")

# Responses API configuration
ENABLE_RESPONSES_API = os.getenv("EQ12_ENABLE_RESPONSES_API", "true").lower() == "true"
ENABLE_DEBUG_HEADERS = os.getenv("EQ12_DEBUG_HEADERS", "true").lower() == "true"
REQUEST_ID_LOG_FILE = os.getenv("EQ12_REQUEST_ID_LOG", "logs/api_requests.jsonl")
FALLBACK_MODEL = os.getenv("EQ12_FALLBACK_MODEL", "gpt-4o")
ENFORCE_POLICY = os.getenv("EQ12_ENFORCE_MODEL_POLICY", "true").lower() == "true"

# Rate limiting configuration
try:
    import json

    RUNTIME_LIMITS = json.loads(os.getenv("EQ12_RUNTIME_LIMITS_JSON", "{}"))
except (json.JSONDecodeError, ImportError):
    RUNTIME_LIMITS = {}

# Rate limiting tracking (simple in-memory buckets)
_rate_buckets = {}
_last_reset = time.time()


def is_blocked(model: str) -> bool:
    """
    Check if a model is blocked by policy using pattern matching
    Supports wildcards like gpt-3.5-turbo* and gpt-5*
    """
    if not fnmatch or not ENFORCE_POLICY:
        return False

    for pattern in BLOCKED_MODELS:
        pattern = pattern.strip()
        if pattern and fnmatch.fnmatch(model, pattern):
            logger.warning(f"Model {model} blocked by policy (matches {pattern})")
            return True
    return False


def route_model(requested: str, task_type: str = "chat") -> str:
    """
    Route model requests according to EQ12 policy

    Args:
        requested: The originally requested model
        task_type: Type of task ('chat', 'embedding', 'moderation', etc.)

    Returns:
        Safe, allowed model name

    Raises:
        ValueError: If no safe model is available
    """
    if not ENFORCE_POLICY:
        return requested

    # Clean model name
    requested = requested.strip()

    # Check if requested model is allowed and not blocked
    if requested in ALLOWED_MODELS and not is_blocked(requested):
        logger.debug(f"Model routing: {requested} → {requested} (allowed)")
        return requested

    # Route based on task type
    if task_type == "embedding" or "embed" in requested.lower():
        target = DEFAULT_EMBEDDING_MODEL
    elif task_type == "moderation" or "moderation" in requested.lower():
        target = os.getenv("EQ12_MODERATION_MODEL", "omni-moderation-latest")
    elif task_type == "transcription" or "whisper" in requested.lower():
        target = "whisper-1"
    elif task_type == "image" or "dall" in requested.lower() or "image" in requested.lower():
        target = "gpt-image-1"
    elif task_type == "tts" or "tts" in requested.lower():
        target = "tts-1"
    else:
        # Default to chat model routing
        # For complex/reasoning tasks, use gpt-4o; otherwise gpt-4o-mini
        if any(
            keyword in requested.lower()
            for keyword in ["reasoning", "complex", "analysis", "research", "o1"]
        ):
            target = FALLBACK_MODEL
        else:
            target = DEFAULT_CHAT_MODEL

    # Verify target is not blocked
    if is_blocked(target):
        raise ValueError(f"Target model {target} is blocked by policy. Cannot route {requested}.")

    # Log the routing decision
    if requested != target:
        logger.info(f"Model routing: {requested} → {target} (policy enforcement)")

    return target


def enforce_local_rate_limit(model: str, tokens: int = 0) -> bool:
    """
    Enforce local rate limits using token buckets

    Args:
        model: Model name to check limits for
        tokens: Number of tokens being requested

    Returns:
        True if request is allowed, False if rate limited

    Raises:
        RuntimeError: If model is completely blocked (0 limits)
    """
    global _rate_buckets, _last_reset

    # Get limits for this model (fall back to default)
    limits = RUNTIME_LIMITS.get(model) or RUNTIME_LIMITS.get("default", {})
    tpm_limit = limits.get("tpm", 0)
    rpm_limit = limits.get("rpm", 0)

    # Hard block if limits are 0
    if (tpm_limit == 0 and tokens > 0) or rpm_limit == 0:
        raise RuntimeError(
            f"Model {model} blocked by local rate policy (TPM={tpm_limit}, RPM={rpm_limit})"
        )

    # Reset buckets every minute
    current_time = time.time()
    if current_time - _last_reset >= 60:
        _rate_buckets.clear()
        _last_reset = current_time

    # Initialize bucket if needed
    if model not in _rate_buckets:
        _rate_buckets[model] = {"tokens": 0, "requests": 0}

    bucket = _rate_buckets[model]

    # Check if we would exceed limits
    if bucket["tokens"] + tokens > tpm_limit:
        logger.warning(f"TPM limit exceeded for {model}: {bucket['tokens'] + tokens} > {tpm_limit}")
        return False

    if bucket["requests"] + 1 > rpm_limit:
        logger.warning(f"RPM limit exceeded for {model}: {bucket['requests'] + 1} > {rpm_limit}")
        return False

    # Update buckets
    bucket["tokens"] += tokens
    bucket["requests"] += 1

    logger.debug(
        f"Rate limit check passed for {model}: {bucket['tokens']}/{tpm_limit} TPM, {bucket['requests']}/{rpm_limit} RPM"
    )
    return True


def get_rate_limit_status(model: str | None = None) -> dict:
    """
    Get current rate limit status for model(s)

    Args:
        model: Specific model to check, or None for all models

    Returns:
        Dictionary with rate limit status
    """
    status = {}

    if model:
        limits = RUNTIME_LIMITS.get(model) or RUNTIME_LIMITS.get("default", {})
        bucket = _rate_buckets.get(model, {"tokens": 0, "requests": 0})

        status[model] = {
            "limits": limits,
            "usage": bucket,
            "utilization_tpm": bucket["tokens"] / max(limits.get("tpm", 1), 1),
            "utilization_rpm": bucket["requests"] / max(limits.get("rpm", 1), 1),
        }
    else:
        # All models
        for model_name in RUNTIME_LIMITS:
            if model_name == "default":
                continue
            status.update(get_rate_limit_status(model_name))

    return status


# Webhook configuration
WEBHOOK_URL = os.getenv("EQ12_WEBHOOK_URL", "http://127.0.0.1:8000/webhooks/openai")
WEBHOOK_SECRET = os.getenv("EQ12_WEBHOOK_SECRET", "change-me-in-production")


def send_webhook_event(event_type: str, payload: dict, source: str = "openai"):
    """
    Send event to EQ12 webhook endpoint with HMAC signature
    Non-blocking - failures don't interrupt main request flow
    """
    if not (uuid and hmac and hashlib and httpx):
        return  # Dependencies not available

    try:
        body = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": source,
            "payload": payload,
            "schema_version": "1.0.0",
        }

        raw_body = json.dumps(body, ensure_ascii=False).encode()
        signature = hmac.new(WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-EQ12-Signature": signature,
            "X-EQ12-Delivery": body["id"],
        }

        # Non-blocking HTTP request with short timeout
        response = httpx.post(WEBHOOK_URL, content=raw_body, headers=headers, timeout=2.0)

        if response.status_code == 200:
            logger.debug(f"Webhook event sent: {event_type} [{body['id']}]")
        else:
            logger.warning(f"Webhook failed: {response.status_code} for {event_type}")

    except Exception as e:
        # Don't log errors unless debug mode to avoid log spam
        logger.debug(f"Webhook send failed: {e}")
        pass  # Never block the main request path


class EQ12AIClient:
    """
    Unified AI client with Azure-first routing and production safety features

    Features:
    - Azure OpenAI first, OpenAI API fallback
    - OpenAI Responses API support with stateful interactions
    - Automatic retry with exponential backoff
    - Budget guardrails and usage tracking
    - 429/quota error handling
    - Structured output support
    - Request ID logging and header debugging
    - Built-in tools (file search, web search, function calling)
    """

    def __init__(self):
        # Azure OpenAI configuration
        self.azure_config = {
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "key": os.getenv("AZURE_OPENAI_API_KEY"),
            "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
        }

        # OpenAI configuration
        self.openai_key = os.getenv("OPENAI_API_KEY")

        # Budget and safety settings
        self.daily_budget = float(os.getenv("EQ12_DAILY_BUDGET", "25.0"))
        self.usage_log_path = os.getenv("EQ12_USAGE_LOG", "logs/usage.jsonl")

        # Client settings
        self.timeout = 60
        self.max_retries = 3
        self.base_backoff = 1.0

        # Initialize OpenAI SDK client for Responses API
        self.openai_client = None
        if OpenAI and self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)

        # Request tracking
        self.last_request_id = None
        self.last_headers = {}

        logger.info("EQ12AIClient initialized")
        if self.azure_config["endpoint"]:
            logger.info("Azure OpenAI endpoint configured")
        if self.openai_key:
            logger.info("OpenAI API key configured")
        if self.openai_client and ENABLE_RESPONSES_API:
            logger.info("OpenAI Responses API client ready")

    def _get_headers(self, use_azure: bool = True) -> dict[str, str]:
        """Get appropriate headers for API requests"""
        if use_azure:
            return {
                "Content-Type": "application/json",
                "api-key": self.azure_config["key"],
            }
        else:
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_key}",
            }

    def _get_azure_url(self) -> str:
        """Get Azure OpenAI API URL"""
        endpoint = self.azure_config["endpoint"]
        deployment = self.azure_config["deployment"]
        api_version = self.azure_config["api_version"]

        # Try newer Responses API first, fallback to Chat Completions
        return (
            f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
        )

    def _get_openai_url(self) -> str:
        """Get OpenAI API URL"""
        return "https://api.openai.com/v1/chat/completions"

    def _make_request(
        self, url: str, headers: dict[str, str], payload: dict[str, Any]
    ) -> httpx.Response:
        """Make HTTP request with timeout handling"""
        if not httpx:
            raise RuntimeError("httpx library not installed. Run: pip install httpx")

        with httpx.Client(timeout=self.timeout) as client:
            return client.post(url, headers=headers, json=payload)

    def _create_chat_payload(
        self, prompt: str, system: str | None = None, model: str = "gpt-4o", **kwargs
    ) -> dict[str, Any]:
        """Create chat completion payload"""
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        payload = {
            "messages": messages,
            "model": model,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
        }

        # Add structured output if requested
        if kwargs.get("response_format"):
            payload["response_format"] = kwargs["response_format"]

        return payload

    def _extract_response_content(self, response_data: dict[str, Any]) -> str:
        """Extract content from API response"""
        try:
            # Handle chat completions response
            if "choices" in response_data:
                return response_data["choices"][0]["message"]["content"].strip()

            # Handle responses API (if available)
            if "output_text" in response_data:
                return response_data["output_text"].strip()

            return str(response_data)

        except (KeyError, IndexError, AttributeError) as e:
            logger.error(f"Failed to extract response content: {e}")
            return f"[Error extracting response: {e}]"

    def _log_usage(
        self, model: str, prompt_tokens: int, completion_tokens: int, cost: float, provider: str
    ):
        """Log API usage for budget tracking"""
        usage_record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "model": model,
            "provider": provider,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "estimated_cost": cost,
        }

        try:
            os.makedirs(os.path.dirname(self.usage_log_path), exist_ok=True)
            with open(self.usage_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(usage_record) + "\n")
        except Exception as e:
            logger.warning(f"Could not log usage: {e}")

    def _check_budget(self) -> bool:
        """Check if daily budget has been exceeded"""
        try:
            if not os.path.exists(self.usage_log_path):
                return False

            today = datetime.now(UTC).date()
            daily_cost = 0.0

            with open(self.usage_log_path, encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        record_date = datetime.fromisoformat(record["timestamp"]).date()

                        if record_date == today:
                            daily_cost += float(record.get("estimated_cost", 0))

                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

            over_budget = daily_cost >= self.daily_budget

            if over_budget:
                warning_msg = f"Daily budget exceeded: ${daily_cost:.2f} / ${self.daily_budget:.2f}"
                logger.warning(warning_msg)

            return over_budget

        except Exception as e:
            logger.warning(f"Budget check failed: {e}")
            return False

    def _estimate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate API call cost based on model and tokens"""
        # Cost per 1K tokens (approximate as of 2025)
        cost_table = {
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        }

        # Default to gpt-4o costs if model not found
        model_costs = cost_table.get(model, cost_table["gpt-4o"])

        input_cost = (prompt_tokens / 1000) * model_costs["input"]
        output_cost = (completion_tokens / 1000) * model_costs["output"]

        return input_cost + output_cost

    def ask(
        self,
        prompt: str,
        system: str | None = None,
        model: str = "gpt-4o",
        feature: str = "general",
        use_azure_first: bool = True,
        **kwargs,
    ) -> str:
        """
        Make AI request with strict budget enforcement and intelligent routing

        Args:
            prompt: User prompt/question
            system: Optional system message
            model: Model to use (gpt-4o, gpt-4o-mini, etc.)
            feature: Feature name for budget tracking (parlay_final, odds_summarization, etc.)
            use_azure_first: Whether to try Azure first (default True)
            **kwargs: Additional parameters (max_tokens, temperature, etc.)

        Returns:
            AI response text
        """
        # Estimate token usage for budget check
        estimated_input = len(prompt.split()) * 1.33  # Rough token estimation
        estimated_output = kwargs.get("max_tokens", 800)

        # Apply model policy routing first
        original_model = model
        model = route_model(model, task_type="chat")
        if model != original_model:
            logger.info(f"Model policy routing: {original_model} → {model}")

        # Check local rate limits
        try:
            if not enforce_local_rate_limit(model, int(estimated_input + estimated_output)):
                logger.warning(f"Rate limit exceeded for {model}, will retry with backoff")
                # Could implement retry logic here or queue the request
                return "[Rate limit: Request queued due to TPM/RPM limits]"
        except RuntimeError as e:
            logger.error(f"Rate limit enforcement blocked request: {e}")
            return f"[Blocked: {e}]"

        # Check strict budget policy
        if budget_enforcer:
            allowed, reason, routing = budget_enforcer.check_request_allowed(
                feature, model, int(estimated_input), int(estimated_output)
            )

            if not allowed:
                logger.warning(f"Request blocked by budget policy: {reason}")
                if "budget exceeded" in reason.lower():
                    return "[Budget exceeded: Request blocked by cost controls]"
                elif "limit exceeded" in reason.lower():
                    return "[Rate limit: Feature usage exceeded daily quota]"
                else:
                    return f"[Policy violation: {reason}]"

            # Use routing recommendations
            if routing.get("degraded"):
                model = routing["model"]
                logger.info(f"Budget policy degraded request to {model}")

        # Fallback to legacy budget check if enforcer unavailable
        elif self._check_budget():
            logger.warning("Daily budget exceeded - using cached/offline mode")
            return "[Budget exceeded: Using offline analysis mode]"

        # Store feature for usage recording
        self._current_feature = feature

        # Create request payload
        payload = self._create_chat_payload(prompt, system, model, **kwargs)

        # Try Azure first if configured and requested
        if use_azure_first and all(self.azure_config.values()):
            try:
                return self._try_azure_request(payload, model)
            except Exception as e:
                logger.warning(f"Azure request failed: {e}")
                # Fall through to OpenAI

        # Try OpenAI API
        if self.openai_key:
            try:
                return self._try_openai_request(payload, model)
            except Exception as e:
                logger.error(f"OpenAI request failed: {e}")

        # All backends failed
        error_msg = "All AI backends failed - check keys, quota, and network connectivity"
        raise RuntimeError(error_msg)

    def _try_azure_request(self, payload: dict[str, Any], model: str) -> str:
        """Try Azure OpenAI request with retry logic"""
        url = self._get_azure_url()
        headers = self._get_headers(use_azure=True)

        backoff = self.base_backoff

        for attempt in range(self.max_retries):
            try:
                response = self._make_request(url, headers, payload)

                if response.status_code == 200:
                    response_data = response.json()
                    content = self._extract_response_content(response_data)

                    # Log usage
                    usage = response_data.get("usage", {})
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    completion_tokens = usage.get("completion_tokens", 0)
                    cost = self._estimate_cost(model, prompt_tokens, completion_tokens)

                    self._log_usage(model, prompt_tokens, completion_tokens, cost, "azure")

                    # Record budget usage for policy enforcement
                    if budget_enforcer and hasattr(self, "_current_feature"):
                        budget_enforcer.record_usage(
                            self._current_feature, model, prompt_tokens, completion_tokens, cost
                        )

                    # Send webhook event for successful completion
                    feature = getattr(self, "_current_feature", "general")
                    send_webhook_event(
                        "openai.response.completed",
                        {
                            "model": model,
                            "provider": "azure",
                            "feature": feature,
                            "usage": {
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": completion_tokens,
                                "total_tokens": prompt_tokens + completion_tokens,
                                "cost_usd": cost,
                            },
                            "response_length": len(content),
                            "tag": "parlay_analysis" if "parlay" in feature else None,
                        },
                    )

                    return content

                elif response.status_code == 429:
                    logger.warning(f"Azure rate limit hit, waiting {backoff}s")

                    # Send webhook event for rate limit
                    feature = getattr(self, "_current_feature", "general")
                    send_webhook_event(
                        "openai.rate_limit.hit",
                        {
                            "model": model,
                            "provider": "azure",
                            "feature": feature,
                            "status_code": 429,
                            "retry_after": backoff,
                            "attempt": attempt + 1,
                        },
                    )

                    time.sleep(backoff)
                    backoff *= 2
                    continue

                elif response.status_code in (500, 502, 503, 504):
                    msg = f"Azure server error {response.status_code}, retrying"
                    logger.warning(msg)
                    time.sleep(backoff)
                    backoff *= 1.5
                    continue

                else:
                    response.raise_for_status()

            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Send webhook event for final failure
                    feature = getattr(self, "_current_feature", "general")
                    send_webhook_event(
                        "openai.response.error",
                        {
                            "model": model,
                            "provider": "azure",
                            "feature": feature,
                            "error": str(e),
                            "code": getattr(e, "status_code", None),
                            "attempts": self.max_retries,
                        },
                    )
                    raise
                logger.warning(f"Azure request attempt {attempt + 1} failed: {e}")
                time.sleep(backoff)
                backoff *= 1.5

        # Send final error event if all retries exhausted
        feature = getattr(self, "_current_feature", "general")
        send_webhook_event(
            "openai.response.error",
            {
                "model": model,
                "provider": "azure",
                "feature": feature,
                "error": "All retries exhausted",
                "attempts": self.max_retries,
            },
        )
        raise RuntimeError("Azure requests exhausted all retries")

    def _try_openai_request(self, payload: dict[str, Any], model: str) -> str:
        """Try OpenAI API request with retry logic"""
        url = self._get_openai_url()
        headers = self._get_headers(use_azure=False)

        # Set model in payload for OpenAI
        payload["model"] = model

        backoff = self.base_backoff

        for attempt in range(self.max_retries):
            try:
                response = self._make_request(url, headers, payload)

                if response.status_code == 200:
                    response_data = response.json()
                    content = self._extract_response_content(response_data)

                    # Log usage
                    usage = response_data.get("usage", {})
                    prompt_tokens = usage.get("prompt_tokens", 0)
                    completion_tokens = usage.get("completion_tokens", 0)
                    cost = self._estimate_cost(model, prompt_tokens, completion_tokens)

                    self._log_usage(model, prompt_tokens, completion_tokens, cost, "openai")

                    # Record budget usage for policy enforcement
                    if budget_enforcer and hasattr(self, "_current_feature"):
                        budget_enforcer.record_usage(
                            self._current_feature, model, prompt_tokens, completion_tokens, cost
                        )

                    # Send webhook event for successful completion
                    feature = getattr(self, "_current_feature", "general")
                    send_webhook_event(
                        "openai.response.completed",
                        {
                            "model": model,
                            "provider": "openai",
                            "feature": feature,
                            "usage": {
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": completion_tokens,
                                "total_tokens": prompt_tokens + completion_tokens,
                                "cost_usd": cost,
                            },
                            "response_length": len(content),
                            "tag": "parlay_analysis" if "parlay" in feature else None,
                        },
                    )

                    return content

                elif response.status_code == 429:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", "")

                    if "insufficient_quota" in error_message.lower():
                        # Send quota exceeded event
                        feature = getattr(self, "_current_feature", "general")
                        send_webhook_event(
                            "openai.quota.low",
                            {
                                "model": model,
                                "provider": "openai",
                                "feature": feature,
                                "error": "Quota exceeded",
                                "message": error_message,
                            },
                        )
                        error_msg = "OpenAI quota exceeded - check billing settings"
                        raise RuntimeError(error_msg)

                    # Send rate limit event
                    feature = getattr(self, "_current_feature", "general")
                    send_webhook_event(
                        "openai.rate_limit.hit",
                        {
                            "model": model,
                            "provider": "openai",
                            "feature": feature,
                            "status_code": 429,
                            "retry_after": backoff,
                            "attempt": attempt + 1,
                            "message": error_message,
                        },
                    )

                    logger.warning(f"OpenAI rate limit hit, waiting {backoff}s")
                    time.sleep(backoff)
                    backoff *= 2
                    continue

                elif response.status_code in (500, 502, 503, 504):
                    msg = f"OpenAI server error {response.status_code}, retrying"
                    logger.warning(msg)
                    time.sleep(backoff)
                    backoff *= 1.5
                    continue

                else:
                    response.raise_for_status()

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"OpenAI request attempt {attempt + 1} failed: {e}")
                time.sleep(backoff)
                backoff *= 1.5

        raise RuntimeError("OpenAI requests exhausted all retries")

    def analyze_parlay_opportunities(
        self, games_data: list[dict[str, Any]], bankroll: float = 1000.0
    ) -> str:
        """Specialized method for parlay analysis"""
        if not games_data:
            return "No games data provided for analysis"

        # Prepare games summary
        games_summary = []
        for i, game in enumerate(games_data[:8]):  # Limit to avoid token limits
            home = game.get("home_team", "Home")
            away = game.get("away_team", "Away")
            commence = game.get("commence_time", "")[:16]  # Date + time

            games_summary.append(f"{i + 1}. {away} @ {home} ({commence})")

        prompt = f"""Analyze these upcoming NFL games for smart parlay opportunities:

{chr(10).join(games_summary)}

CRITICAL REQUIREMENTS:
- ONE sportsbook per parlay (DraftKings, FanDuel, or BetMGM only)
- NO contradictory selections (Over+Under same game, both sides)
- Maximum 6 legs per parlay for realistic odds
- Focus on high-confidence, value-driven selections

Provide 3 parlay strategies:
1. Conservative (2-3 legs, heavy favorites, safer picks)
2. Balanced (3-4 legs, mixed risk/reward)
3. Aggressive (4-6 legs, higher variance for bigger payouts)

For each strategy, specify:
- Exact sportsbook to use
- Specific selections with point spreads/totals
- Brief reasoning for each pick
- Expected confidence level (1-10)

Bankroll: ${bankroll:,.0f}"""

        system_msg = """You are an expert sports betting analyst. Focus on realistic,
        placeable bets that follow sportsbook rules. Avoid impossible parlays with
        conflicting selections or mixed sportsbooks."""

        try:
            return self.ask(prompt, system=system_msg, model="gpt-4o", max_tokens=2000)
        except Exception as e:
            logger.error(f"Parlay analysis failed: {e}")
            return f"Analysis unavailable due to technical error: {e}"

    def get_usage_summary(self, days: int = 1) -> dict[str, Any]:
        """Get usage and cost summary for recent days"""
        if not os.path.exists(self.usage_log_path):
            return {"error": "No usage log found"}

        try:
            cutoff_date = (datetime.now(UTC) - timedelta(days=days)).date()

            total_tokens = 0
            total_cost = 0.0
            provider_breakdown = {}
            model_breakdown = {}

            with open(self.usage_log_path, encoding="utf-8") as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        record_date = datetime.fromisoformat(record["timestamp"]).date()

                        if record_date >= cutoff_date:
                            tokens = record.get("total_tokens", 0)
                            cost = float(record.get("estimated_cost", 0))
                            provider = record.get("provider", "unknown")
                            model = record.get("model", "unknown")

                            total_tokens += tokens
                            total_cost += cost

                            provider_breakdown[provider] = (
                                provider_breakdown.get(provider, 0) + cost
                            )
                            model_breakdown[model] = model_breakdown.get(model, 0) + cost

                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

            return {
                "period_days": days,
                "total_tokens": total_tokens,
                "total_cost": round(total_cost, 2),
                "budget_remaining": round(self.daily_budget * days - total_cost, 2),
                "budget_utilization": round(total_cost / (self.daily_budget * days) * 100, 1),
                "provider_breakdown": provider_breakdown,
                "model_breakdown": model_breakdown,
            }

        except Exception as e:
            return {"error": f"Failed to analyze usage: {e}"}


# Global client instance for convenience
_global_client = None


def get_ai_client() -> EQ12AIClient:
    """Get or create global AI client instance"""
    global _global_client
    if _global_client is None:
        _global_client = EQ12AIClient()
    return _global_client


def ask(prompt: str, system: str | None = None, model: str = "gpt-4o", **kwargs) -> str:
    """Convenience function for AI queries"""
    return get_ai_client().ask(prompt, system, model, **kwargs)


def ask_with_responses(
    prompt: str,
    conversation_id: str | None = None,
    tools: list[str] | None = None,
    model: str = "gpt-4o",
    stream: bool = False,
    **kwargs,
) -> dict:
    """
    Convenience function for Responses API queries

    Args:
        prompt: User prompt/question
        conversation_id: Optional conversation ID for stateful interactions
        tools: List of tools to enable
        model: Model to use
        stream: Whether to stream the response
        **kwargs: Additional parameters

    Returns:
        Response data with enhanced metadata
    """
    return get_ai_client().ask_with_responses_api(
        prompt=prompt,
        conversation_id=conversation_id,
        tools=tools,
        model=model,
        stream=stream,
        **kwargs,
    )


def create_conversation_session(metadata: dict | None = None) -> dict[str, Any]:
    """
    Convenience function to create a new conversation session

    Args:
        metadata: Optional metadata for the conversation

    Returns:
        Conversation object
    """
    return get_ai_client().create_conversation(metadata=metadata)


def stream_ai_response(
    prompt: str,
    conversation_id: str | None = None,
    tools: list[str] | None = None,
    model: str = "gpt-4o",
    **kwargs,
):
    """
    Convenience function for streaming AI responses

    Args:
        prompt: User prompt/question
        conversation_id: Optional conversation ID
        tools: List of tools to enable
        model: Model to use
        **kwargs: Additional parameters

    Yields:
        Streaming response events
    """
    client = get_ai_client()

    # Prepare messages
    messages = [{"role": "user", "content": prompt}]

    # Prepare tools
    prepared_tools = None
    if tools:
        prepared_tools = client._prepare_tools(tools)

    # Stream the response
    yield from client.stream_response(
        model=model,
        messages=messages,
        conversation_id=conversation_id,
        tools=prepared_tools,
        **kwargs,
    )


def test_ai_client():
    """Test AI client functionality"""
    try:
        client = get_ai_client()

        print("🧪 Testing EQ12 AI Client...")

        # Test basic functionality
        test_prompt = "Reply with 'EQ12 AI Client working!' if you receive this."
        response = client.ask(test_prompt)
        print(f"✅ Response: {response}")

        # Test usage tracking
        usage = client.get_usage_summary(days=1)
        print(f"📊 Usage Summary: {usage}")

        return True

    except Exception as e:
        print(f"❌ AI client test failed: {e}")
        return False


if __name__ == "__main__":
    # Run client test
    test_ai_client()
