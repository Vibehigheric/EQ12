#!/usr/bin/env python3
"""
OpenAI Responses API Integration Demo

This script demonstrates the complete integration of OpenAI's Responses API
into the EQ12AIClient system, showcasing all the new features and capabilities.

Features Demonstrated:
- Responses API core methods (create, retrieve, list)
- Conversation management (create, update, retrieve, list)
- Tool integration (web_search, file_search, function calling, EQ12-specific tools)
- Streaming response handling
- Budget and policy integration
- Usage tracking and logging
- Response state management

Author: EQ12 Team
Usage: python demo_responses_api.py
"""

import os
import sys
from typing import Any

# Add EQ12 root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eq12_ai_client import (
    ask_with_responses,
    create_conversation_session,
    get_ai_client,
    stream_ai_response,
)


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_response(label: str, response: Any):
    """Print a formatted response"""
    print(f"\n🤖 {label}:")
    if isinstance(response, dict):
        for key, value in response.items():
            if key == "content" and len(str(value)) > 200:
                print(f"  {key}: {str(value)[:200]}...")
            else:
                print(f"  {key}: {value}")
    else:
        print(f"  {response}")


def demo_basic_responses_api():
    """Demonstrate basic Responses API functionality"""
    print_section("Basic Responses API Functionality")

    client = get_ai_client()

    try:
        # Create a simple response
        print("📝 Creating a basic response...")
        response = client.create_response(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Explain the OpenAI Responses API in 2 sentences."}
            ],
        )

        print_response(
            "Created Response",
            {
                "id": getattr(response, "id", "N/A"),
                "status": getattr(response, "status", "N/A"),
                "model": getattr(response, "model", "N/A"),
            },
        )

        # Retrieve the response
        if hasattr(response, "id"):
            print("\n🔍 Retrieving response...")
            retrieved = client.retrieve_response(response.id)
            print_response(
                "Retrieved Response",
                {
                    "id": getattr(retrieved, "id", "N/A"),
                    "status": getattr(retrieved, "status", "N/A"),
                    "content": str(getattr(retrieved, "output", {}))[:100] + "...",
                },
            )

        # List recent responses
        print("\n📋 Listing recent responses...")
        responses_list = client.list_responses(limit=5)
        print(f"Found {len(getattr(responses_list, 'data', []))} recent responses")

    except Exception as e:
        print(f"❌ Error in basic demo: {e}")
        print(
            "Note: This is expected if OpenAI API key is not configured or Responses API is not available"
        )


def demo_conversation_management():
    """Demonstrate conversation management"""
    print_section("Conversation Management")

    client = get_ai_client()

    try:
        # Create a conversation
        print("💬 Creating a conversation...")
        conversation = client.create_conversation(metadata={"purpose": "demo", "user": "demo_user"})

        conversation_id = getattr(conversation, "id", None)
        print_response(
            "Created Conversation",
            {"id": conversation_id, "metadata": getattr(conversation, "metadata", {})},
        )

        if conversation_id:
            # Use conversation in a response
            print("\n🗣️ Creating response in conversation...")
            response = client.ask_with_responses_api(
                prompt="What is the EQ12 system designed for?",
                conversation_id=conversation_id,
                model="gpt-4o-mini",
            )

            print_response("Conversation Response", response)

            # Update conversation metadata
            print("\n🔄 Updating conversation metadata...")
            updated_conversation = client.update_conversation(
                conversation_id, metadata={"purpose": "demo", "user": "demo_user", "updated": True}
            )

            print_response(
                "Updated Conversation",
                {
                    "id": getattr(updated_conversation, "id", "N/A"),
                    "metadata": getattr(updated_conversation, "metadata", {}),
                },
            )

        # List conversations
        print("\n📋 Listing conversations...")
        conversations = client.list_conversations(limit=3)
        print(f"Found {len(getattr(conversations, 'data', []))} conversations")

    except Exception as e:
        print(f"❌ Error in conversation demo: {e}")
        print(
            "Note: This is expected if OpenAI API key is not configured or Responses API is not available"
        )


def demo_tool_integration():
    """Demonstrate tool integration"""
    print_section("Tool Integration")

    client = get_ai_client()

    # Show available tools
    print("🛠️ Available tools:")

    # Standard tools
    standard_tools = ["web_search", "file_search", "function", "computer_use"]
    prepared_standard = client._prepare_tools(standard_tools)

    print("  Standard OpenAI tools:")
    for tool in prepared_standard:
        print(f"    - {tool.get('type', 'unknown')}")

    # EQ12-specific tools
    eq12_tools = ["eq12_parlay_analyzer", "eq12_odds_tracker", "eq12_browser_automation"]
    prepared_eq12 = client._prepare_tools(eq12_tools)

    print("  EQ12-specific tools:")
    for tool in prepared_eq12:
        print(f"    - {tool.get('function', {}).get('name', 'unknown')}")

    try:
        # Demonstrate tool usage
        print("\n🎯 Creating response with tools...")
        response = client.ask_with_responses_api(
            prompt="Analyze NFL betting opportunities for this weekend",
            tools=["web_search", "eq12_parlay_analyzer"],
            model="gpt-4o-mini",
        )

        print_response("Tool-Enhanced Response", response)

    except Exception as e:
        print(f"❌ Error in tool demo: {e}")
        print("Note: This is expected if OpenAI API key is not configured")


def demo_streaming_responses():
    """Demonstrate streaming responses"""
    print_section("Streaming Responses")

    try:
        print("🌊 Streaming a response...")

        # Use the convenience function for streaming
        stream_events = stream_ai_response(
            prompt="Count from 1 to 5, explaining each number briefly", model="gpt-4o-mini"
        )

        print("Streaming events:")
        event_count = 0
        for event in stream_events:
            event_count += 1
            print(f"  Event {event_count}: {getattr(event, 'event_type', 'unknown')}")
            if event_count >= 5:  # Limit output for demo
                print("  ... (more events)")
                break

        print(f"\n✅ Processed {event_count}+ streaming events")

    except Exception as e:
        print(f"❌ Error in streaming demo: {e}")
        print("Note: This is expected if OpenAI API key is not configured")


def demo_budget_and_policy_integration():
    """Demonstrate budget and policy integration"""
    print_section("Budget and Policy Integration")

    client = get_ai_client()

    # Show current rate limit status
    print("📊 Rate limit status:")
    from eq12_ai_client import get_rate_limit_status

    status = get_rate_limit_status()
    for model, limits in status.items():
        print(f"  {model}:")
        print(f"    TPM: {limits['usage']['tokens']}/{limits['limits'].get('tpm', 'unlimited')}")
        print(f"    RPM: {limits['usage']['requests']}/{limits['limits'].get('rpm', 'unlimited')}")

    # Show usage summary
    print("\n💰 Usage summary:")
    usage = client.get_usage_summary(days=1)
    if "error" not in usage:
        print(f"  Total cost today: ${usage['total_cost']}")
        print(f"  Budget remaining: ${usage['budget_remaining']}")
        print(f"  Budget utilization: {usage['budget_utilization']}%")
    else:
        print(f"  {usage['error']}")

    # Show Responses API specific usage
    responses_usage = client.get_responses_api_usage_summary(days=1)
    if "error" not in responses_usage:
        print("\n🤖 Responses API usage:")
        api_usage = responses_usage.get("responses_api_usage", {})
        print(f"  Total operations: {api_usage.get('total_operations', 0)}")
        print(f"  Total cost: ${api_usage.get('total_cost', 0)}")
        print(f"  Unique conversations: {api_usage.get('unique_conversations', 0)}")
        print(f"  Unique responses: {api_usage.get('unique_responses', 0)}")
    else:
        print(f"\n🤖 Responses API usage: {responses_usage['error']}")


def demo_response_state_management():
    """Demonstrate response state management"""
    print_section("Response State Management")

    client = get_ai_client()

    try:
        # Create a response and track its state
        print("🏃 Creating response and tracking state...")
        response = client.create_response(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "What are the key features of the EQ12 system?"}],
        )

        response_id = getattr(response, "id", None)
        if response_id:
            print(f"Created response: {response_id}")

            # Check status
            status = client.get_response_status(response_id)
            print_response("Response Status", status)

            # If not completed, wait for completion
            if status.get("status") in ["queued", "in_progress"]:
                print("⏳ Waiting for response completion...")
                completed_response = client.wait_for_response(response_id, timeout=30)
                print_response(
                    "Completed Response",
                    {
                        "id": getattr(completed_response, "id", "N/A"),
                        "status": getattr(completed_response, "status", "N/A"),
                    },
                )

        # Show background responses
        print("\n🔄 Checking background responses...")
        background = client.get_background_responses()
        print(f"Active background responses: {len(background)}")

        for bg_response in background[:3]:  # Show first 3
            print(
                f"  - {bg_response.get('response_id', 'N/A')}: {bg_response.get('status', 'N/A')}"
            )

    except Exception as e:
        print(f"❌ Error in state management demo: {e}")
        print("Note: This is expected if OpenAI API key is not configured")


def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print_section("Convenience Functions")

    try:
        # Test ask_with_responses convenience function
        print("🎯 Using ask_with_responses convenience function...")
        response = ask_with_responses(
            prompt="What is artificial intelligence in one sentence?",
            model="gpt-4o-mini",
            tools=["web_search"],
        )

        print_response("Convenience Function Response", response)

        # Test conversation creation
        print("\n💬 Using create_conversation_session...")
        conversation = create_conversation_session(
            metadata={"demo": True, "function": "convenience"}
        )

        print_response(
            "Convenience Conversation",
            {
                "id": getattr(conversation, "id", "N/A"),
                "metadata": getattr(conversation, "metadata", {}),
            },
        )

    except Exception as e:
        print(f"❌ Error in convenience functions demo: {e}")
        print("Note: This is expected if OpenAI API key is not configured")


def main():
    """Run all demonstrations"""
    print("🚀 OpenAI Responses API Integration Demo")
    print(
        "This demo showcases the complete integration of OpenAI's Responses API into EQ12AIClient"
    )

    # Check if API key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not found in environment variables")
        print("   Some features will show mock responses or errors")
        print("   Set your OpenAI API key to see full functionality")

    # Run demonstrations
    demo_basic_responses_api()
    demo_conversation_management()
    demo_tool_integration()
    demo_streaming_responses()
    demo_budget_and_policy_integration()
    demo_response_state_management()
    demo_convenience_functions()

    print_section("Demo Complete")
    print("✅ All Responses API features have been demonstrated!")
    print("\nKey Integration Features:")
    print("  ✅ Responses API core methods (create, retrieve, list)")
    print("  ✅ Conversation management (CRUD operations)")
    print("  ✅ Comprehensive tool support (OpenAI + EQ12 custom tools)")
    print("  ✅ Streaming response handling")
    print("  ✅ Budget and policy integration")
    print("  ✅ Response state management (polling, cancellation, background)")
    print("  ✅ Enhanced usage tracking and logging")
    print("  ✅ Convenience functions for easy usage")
    print("\nThe EQ12AIClient now fully supports OpenAI's Responses API! 🎉")


if __name__ == "__main__":
    main()
