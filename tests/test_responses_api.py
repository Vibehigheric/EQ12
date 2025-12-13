#!/usr/bin/env python3
"""
Test suite for OpenAI Responses API integration in EQ12AIClient

Tests cover:
- Responses API core methods (create, retrieve, list)
- Conversation management
- Tool integration
- Streaming support
- Budget and policy integration
- Usage tracking and logging

Author: EQ12 Team
"""

import json
import os

# Import the client
import sys
import tempfile
from datetime import datetime
from datetime import timezone as UTC
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eq12_ai_client import EQ12AIClient


class TestResponsesAPICore:
    """Test core Responses API functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.client = EQ12AIClient()

        # Mock OpenAI client
        self.mock_openai_client = Mock()
        self.client.openai_client = self.mock_openai_client

    def test_create_response_basic(self):
        """Test basic response creation"""
        # Mock response
        mock_response = Mock()
        mock_response.id = "resp_123"
        mock_response.status = "completed"
        mock_response.usage = {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        }

        self.mock_openai_client.responses.create.return_value = mock_response

        # Test call
        with patch("eq12_ai_client.route_model", return_value="gpt-4o"):
            with patch("eq12_ai_client.enforce_local_rate_limit", return_value=True):
                response = self.client.create_response(
                    model="gpt-4o", messages=[{"role": "user", "content": "Hello"}]
                )

        # Verify
        assert response.id == "resp_123"
        assert response.status == "completed"
        self.mock_openai_client.responses.create.assert_called_once()

    def test_create_response_with_conversation(self):
        """Test response creation with conversation ID"""
        mock_response = Mock()
        mock_response.id = "resp_456"
        mock_response.status = "queued"

        self.mock_openai_client.responses.create.return_value = mock_response

        with patch("eq12_ai_client.route_model", return_value="gpt-4o"):
            with patch("eq12_ai_client.enforce_local_rate_limit", return_value=True):
                response = self.client.create_response(
                    model="gpt-4o",
                    conversation_id="conv_123",
                    messages=[{"role": "user", "content": "Continue conversation"}],
                )

        assert response.id == "resp_456"

        # Verify conversation_id was passed
        call_args = self.mock_openai_client.responses.create.call_args[1]
        assert call_args.get("conversation_id") == "conv_123"

    def test_create_response_with_tools(self):
        """Test response creation with tools"""
        mock_response = Mock()
        mock_response.id = "resp_789"

        self.mock_openai_client.responses.create.return_value = mock_response

        tools = [{"type": "web_search"}, {"type": "file_search"}]

        with patch("eq12_ai_client.route_model", return_value="gpt-4o"):
            with patch("eq12_ai_client.enforce_local_rate_limit", return_value=True):
                response = self.client.create_response(
                    model="gpt-4o",
                    tools=tools,
                    messages=[{"role": "user", "content": "Search for information"}],
                )

        assert response.id == "resp_789"

        # Verify tools were passed
        call_args = self.mock_openai_client.responses.create.call_args[1]
        assert call_args.get("tools") == tools

    def test_retrieve_response(self):
        """Test response retrieval"""
        mock_response = Mock()
        mock_response.id = "resp_123"
        mock_response.status = "completed"
        mock_response.output = {"content": "Test response"}

        self.mock_openai_client.responses.retrieve.return_value = mock_response

        response = self.client.retrieve_response("resp_123")

        assert response.id == "resp_123"
        assert response.status == "completed"
        self.mock_openai_client.responses.retrieve.assert_called_once_with("resp_123")

    def test_list_responses(self):
        """Test response listing"""
        mock_response_list = Mock()
        mock_response_list.data = [
            Mock(id="resp_1", status="completed"),
            Mock(id="resp_2", status="in_progress"),
        ]

        self.mock_openai_client.responses.list.return_value = mock_response_list

        responses = self.client.list_responses(limit=10)

        assert len(responses.data) == 2
        self.mock_openai_client.responses.list.assert_called_once()

        call_args = self.mock_openai_client.responses.list.call_args[1]
        assert call_args["limit"] == 10
        assert call_args["order"] == "desc"


class TestConversationManagement:
    """Test conversation management functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.client = EQ12AIClient()
        self.mock_openai_client = Mock()
        self.client.openai_client = self.mock_openai_client

    def test_create_conversation(self):
        """Test conversation creation"""
        mock_conversation = Mock()
        mock_conversation.id = "conv_123"

        self.mock_openai_client.conversations.create.return_value = mock_conversation

        metadata = {"user": "test_user", "purpose": "testing"}
        conversation = self.client.create_conversation(metadata=metadata)

        assert conversation.id == "conv_123"

        call_args = self.mock_openai_client.conversations.create.call_args[1]
        assert call_args.get("metadata") == metadata

    def test_retrieve_conversation(self):
        """Test conversation retrieval"""
        mock_conversation = Mock()
        mock_conversation.id = "conv_456"

        self.mock_openai_client.conversations.retrieve.return_value = mock_conversation

        conversation = self.client.retrieve_conversation("conv_456")

        assert conversation.id == "conv_456"
        self.mock_openai_client.conversations.retrieve.assert_called_once_with("conv_456")

    def test_update_conversation(self):
        """Test conversation updating"""
        mock_conversation = Mock()
        mock_conversation.id = "conv_789"

        self.mock_openai_client.conversations.update.return_value = mock_conversation

        metadata = {"updated": True}
        conversation = self.client.update_conversation("conv_789", metadata=metadata)

        assert conversation.id == "conv_789"

        call_args = self.mock_openai_client.conversations.update.call_args
        assert call_args[0][0] == "conv_789"  # First positional arg
        assert call_args[1].get("metadata") == metadata

    def test_list_conversations(self):
        """Test conversation listing"""
        mock_conversation_list = Mock()
        mock_conversation_list.data = [Mock(id="conv_1"), Mock(id="conv_2")]

        self.mock_openai_client.conversations.list.return_value = mock_conversation_list

        conversations = self.client.list_conversations(limit=20)

        assert len(conversations.data) == 2
        self.mock_openai_client.conversations.list.assert_called_once()


class TestToolIntegration:
    """Test tool integration and preparation"""

    def setup_method(self):
        """Setup test environment"""
        self.client = EQ12AIClient()

    def test_prepare_tools_standard(self):
        """Test preparing standard tools"""
        tool_names = ["file_search", "web_search", "function"]
        prepared = self.client._prepare_tools(tool_names)

        assert len(prepared) == 3
        assert any(tool["type"] == "file_search" for tool in prepared)
        assert any(tool["type"] == "web_search" for tool in prepared)
        assert any(tool["type"] == "function" for tool in prepared)

    def test_prepare_tools_eq12_specific(self):
        """Test preparing EQ12-specific tools"""
        tool_names = ["eq12_parlay_analyzer", "eq12_odds_tracker"]
        prepared = self.client._prepare_tools(tool_names)

        assert len(prepared) == 2

        # Check parlay analyzer
        parlay_tool = next(t for t in prepared if "parlay" in t["function"]["name"])
        assert parlay_tool["type"] == "function"
        assert "games_data" in parlay_tool["function"]["parameters"]["properties"]

    def test_prepare_tools_already_formatted(self):
        """Test handling pre-formatted tool objects"""
        tools = [
            {"type": "web_search", "web_search": {"max_num_results": 5}},
            {"type": "function", "function": {"name": "custom_tool"}},
        ]

        prepared = self.client._prepare_tools(tools)

        assert prepared == tools  # Should return as-is

    def test_prepare_tools_unknown(self):
        """Test handling unknown tool names"""
        tool_names = ["unknown_tool", "file_search", "another_unknown"]
        prepared = self.client._prepare_tools(tool_names)

        assert len(prepared) == 1  # Only file_search should be included
        assert prepared[0]["type"] == "file_search"


class TestStreamingSupport:
    """Test streaming response functionality"""

    def setup_method(self):
        """Setup test environment"""
        self.client = EQ12AIClient()
        self.mock_openai_client = Mock()
        self.client.openai_client = self.mock_openai_client

    def test_stream_response_events(self):
        """Test streaming response processing"""
        # Mock streaming events
        mock_events = [
            Mock(event_type="response.content.delta", data={"delta": {"text": "Hello"}}),
            Mock(event_type="response.content.delta", data={"delta": {"text": " world"}}),
            Mock(event_type="response.done", data={"usage": {"total_tokens": 10}}),
        ]

        # Mock create_response to return streaming response
        with patch.object(self.client, "create_response", return_value=iter(mock_events)):
            events = list(
                self.client.stream_response(
                    model="gpt-4o", messages=[{"role": "user", "content": "Hello"}]
                )
            )

        assert len(events) == 3
        assert events[0].event_type == "response.content.delta"
        assert events[-1].event_type == "response.done"

    def test_process_streaming_events(self):
        """Test processing streaming events into final result"""
        mock_events = [
            Mock(event_type="response.content.delta", data={"delta": {"text": "Hello"}}),
            Mock(event_type="response.content.delta", data={"delta": {"text": " world"}}),
            Mock(
                event_type="response.done",
                data={"usage": {"total_tokens": 15}, "response": {"id": "resp_123"}},
            ),
        ]

        result = self.client.process_streaming_events(mock_events)

        assert result["content"] == "Hello world"
        assert result["usage"]["total_tokens"] == 15
        assert result["status"] == "completed"


class TestBudgetPolicyIntegration:
    """Test integration with budget and policy controls"""

    def setup_method(self):
        """Setup test environment"""
        self.client = EQ12AIClient()
        self.mock_openai_client = Mock()
        self.client.openai_client = self.mock_openai_client

    def test_model_routing_applied(self):
        """Test that model routing is applied to Responses API calls"""
        mock_response = Mock()
        mock_response.id = "resp_123"

        self.mock_openai_client.responses.create.return_value = mock_response

        with patch("eq12_ai_client.route_model", return_value="gpt-4o-mini") as mock_route:
            with patch("eq12_ai_client.enforce_local_rate_limit", return_value=True):
                self.client.create_response(
                    model="gpt-4o",  # Original model
                    messages=[{"role": "user", "content": "Test"}],
                )

        # Verify routing was called and applied
        mock_route.assert_called_once_with("gpt-4o", task_type="chat")

        # Verify routed model was used
        call_args = self.mock_openai_client.responses.create.call_args[1]
        assert call_args["model"] == "gpt-4o-mini"

    def test_rate_limit_enforcement(self):
        """Test that rate limits are enforced"""
        with patch("eq12_ai_client.route_model", return_value="gpt-4o"):
            with patch("eq12_ai_client.enforce_local_rate_limit", return_value=False):
                with pytest.raises(RuntimeError, match="Rate limit exceeded"):
                    self.client.create_response(
                        model="gpt-4o", messages=[{"role": "user", "content": "Test"}]
                    )


class TestUsageTracking:
    """Test usage tracking and logging functionality"""

    def setup_method(self):
        """Setup test environment"""
        # Use temporary file for usage log
        self.temp_log = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl")
        self.temp_log.close()

        self.client = EQ12AIClient()
        self.client.usage_log_path = self.temp_log.name

    def teardown_method(self):
        """Cleanup test environment"""
        if os.path.exists(self.temp_log.name):
            os.unlink(self.temp_log.name)

    def test_log_responses_api_usage(self):
        """Test logging Responses API usage"""
        usage_data = {
            "prompt_tokens": 50,
            "completion_tokens": 100,
            "total_tokens": 150,
        }

        self.client._log_responses_api_usage(
            operation="create",
            model="gpt-4o",
            response_id="resp_123",
            conversation_id="conv_456",
            usage=usage_data,
            cost=0.005,
            feature="test_feature",
        )

        # Read and verify log entry
        with open(self.temp_log.name) as f:
            log_entry = json.loads(f.readline())

        assert log_entry["operation"] == "create"
        assert log_entry["api_type"] == "responses"
        assert log_entry["model"] == "gpt-4o"
        assert log_entry["response_id"] == "resp_123"
        assert log_entry["conversation_id"] == "conv_456"
        assert log_entry["prompt_tokens"] == 50
        assert log_entry["completion_tokens"] == 100
        assert log_entry["estimated_cost"] == 0.005

    def test_estimate_responses_api_cost(self):
        """Test cost estimation for Responses API"""
        usage = {"prompt_tokens": 100, "completion_tokens": 50}

        cost_create = self.client._estimate_responses_api_cost("gpt-4o", usage, "create")
        cost_retrieve = self.client._estimate_responses_api_cost("gpt-4o", usage, "retrieve")
        cost_stream = self.client._estimate_responses_api_cost("gpt-4o", usage, "stream")

        # Stream should cost more than create, create more than retrieve
        assert cost_stream > cost_create > cost_retrieve > 0

    def test_get_responses_api_usage_summary(self):
        """Test usage summary generation"""
        # Create some test log entries
        test_entries = [
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "api_type": "responses",
                "operation": "create",
                "model": "gpt-4o",
                "estimated_cost": 0.01,
                "response_id": "resp_1",
                "conversation_id": "conv_1",
                "feature": "test_feature",
            },
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "api_type": "responses",
                "operation": "retrieve",
                "model": "gpt-4o-mini",
                "estimated_cost": 0.002,
                "response_id": "resp_2",
                "feature": "test_feature",
            },
        ]

        with open(self.temp_log.name, "w") as f:
            for entry in test_entries:
                f.write(json.dumps(entry) + "\n")

        summary = self.client.get_responses_api_usage_summary(days=1)

        assert "responses_api_usage" in summary
        usage = summary["responses_api_usage"]

        assert usage["total_operations"] == 2
        assert usage["total_cost"] == 0.012  # 0.01 + 0.002
        assert usage["operations_by_type"]["create"] == 1
        assert usage["operations_by_type"]["retrieve"] == 1
        assert usage["unique_conversations"] == 1  # Only conv_1
        assert usage["unique_responses"] == 2


class TestIntegrationScenarios:
    """Test complete integration scenarios"""

    def setup_method(self):
        """Setup test environment"""
        self.client = EQ12AIClient()
        self.mock_openai_client = Mock()
        self.client.openai_client = self.mock_openai_client

    def test_full_conversation_workflow(self):
        """Test complete conversation workflow"""
        # Mock conversation creation
        mock_conversation = Mock()
        mock_conversation.id = "conv_workflow_test"
        self.mock_openai_client.conversations.create.return_value = mock_conversation

        # Mock response creation
        mock_response = Mock()
        mock_response.id = "resp_workflow_test"
        mock_response.status = "completed"
        mock_response.output = {"content": "Hello! How can I help?"}
        self.mock_openai_client.responses.create.return_value = mock_response

        with patch("eq12_ai_client.route_model", return_value="gpt-4o"):
            with patch("eq12_ai_client.enforce_local_rate_limit", return_value=True):
                # Create conversation
                conversation = self.client.create_conversation(
                    metadata={"purpose": "workflow_test"}
                )

                # Create response in conversation
                response = self.client.ask_with_responses_api(
                    prompt="Hello",
                    conversation_id=conversation.id,
                    tools=["web_search"],
                    model="gpt-4o",
                )

        # Verify workflow
        assert conversation.id == "conv_workflow_test"
        assert response["status"] == "completed"
        assert response["conversation_id"] == "conv_workflow_test"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
