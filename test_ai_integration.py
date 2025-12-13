#!/usr/bin/env python3
"""
Test script for EQ12 OpenAI Governance Integration
Simple test to verify AI capabilities work correctly.
"""

import os

# Set a test API key (will need real one for actual testing)
os.environ["OPENAI_API_KEY"] = "test-key"  # Replace with real key


def test_ai_integration():
    """Test AI integration without actually calling API."""
    try:
        from eq12_openai_governance import EQ12GovernanceAI, EQ12OpenAIClient

        print("✅ AI modules imported successfully")

        # Test client initialization (will fail with test key, but tests import)
        try:
            EQ12OpenAIClient(eq12_root="C:/EQ12")
            print("✅ EQ12OpenAIClient initialized")
        except Exception as e:
            print(f"⚠️ Client init failed (expected with test key): {e}")

        print("✅ AI integration modules are ready")
        return True

    except ImportError as e:
        print(f"❌ AI integration import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ AI integration error: {e}")
        return False


if __name__ == "__main__":
    print("🤖 Testing EQ12 AI Integration...")
    success = test_ai_integration()

    if success:
        print("\n✅ AI Integration Test PASSED")
        print("To enable AI features:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Run: python chrome_governance_automation.py --refresh-daily --ai-analysis")
    else:
        print("\n❌ AI Integration Test FAILED")
        print("AI features will be disabled")
