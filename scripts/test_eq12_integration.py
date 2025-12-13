#!/usr/bin/env python3
"""
EQ12 System Integration Test
Tests the complete logging and migration system integration.
"""

import json
import sys
from pathlib import Path

# Add configs to path for logging system
sys.path.append(str(Path(__file__).parent.parent / "configs"))


def test_logging_system():
    """Test the comprehensive logging system."""
    print("🧪 Testing EQ12 Logging System...")

    try:
        from logging_eq12 import EQ12Logger, LoggingConfig

        # Test basic logger creation
        logger = LoggingConfig.create_module_logger("test_integration")
        logger.info("EQ12 logging system test started")

        # Test structured logging
        eq12_logger = EQ12Logger("test_structured", log_level="DEBUG")
        test_logger = eq12_logger.get_logger()

        # Test various log types
        test_logger.info("Basic info log")
        test_logger.warning("Warning with sensitive data: api_key=sk-test123")
        test_logger.error("Error simulation", extra={"error_code": "TEST_001"})

        # Test performance logging
        eq12_logger.log_performance("test_operation", 42.5, user="test_user")

        # Test security event logging
        eq12_logger.log_security_event(
            "test_event", {"ip": "127.0.0.1", "action": "test_action"}, severity="info"
        )

        # Test API call logging
        eq12_logger.log_api_call("/test/endpoint", "GET", 200, 15.2, test_param="value")

        print("✅ Logging system tests passed")
        return True

    except Exception as e:
        print(f"❌ Logging system test failed: {e}")
        return False


def test_migration_helper():
    """Test the OpenAI migration helper integration."""
    print("🧪 Testing OpenAI Migration Helper...")

    try:
        # Import the migration helper
        sys.path.append(str(Path(__file__).parent))
        from openai_migration_helper import EQ12OpenAIUpgradeBot

        # Create bot instance
        bot = EQ12OpenAIUpgradeBot()

        # Test analysis function (without actually running it)
        print(f"Bot initialized with root: {bot.eq12_root}")
        print(f"Backup directory: {bot.backup_dir}")

        # Verify the bot can access its methods
        assert hasattr(bot, "analyze_current_state")
        assert hasattr(bot, "fix_legacy_api_usage")
        assert hasattr(bot, "create_migration_pr")

        print("✅ Migration helper integration test passed")
        return True

    except Exception as e:
        print(f"❌ Migration helper test failed: {e}")
        return False


def test_repo_scanner():
    """Test the repository scanner with Windows fixes."""
    print("🧪 Testing Repository Scanner...")

    try:
        sys.path.append(str(Path(__file__).parent))
        from openai_repo_scan import OpenAIRepoScanner

        # Create scanner instance
        scanner = OpenAIRepoScanner()

        # Test initialization
        assert scanner.research_dir.exists() or scanner.research_dir.parent.exists()
        print(f"Scanner initialized with research dir: {scanner.research_dir}")

        # Verify Windows-safe configuration
        assert "openai-python" in scanner.priority_repos
        assert "*.exe" in scanner.excluded_paths
        assert "MIT" in scanner.safe_licenses

        print("✅ Repository scanner test passed")
        return True

    except Exception as e:
        print(f"❌ Repository scanner test failed: {e}")
        return False


def test_log_analysis():
    """Test log analytics and parsing."""
    print("🧪 Testing Log Analytics...")

    try:
        from logging_eq12 import LogAnalytics

        # Test JSONL parsing (with empty file if needed)
        log_dir = Path("C:/EQ12/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create a test log file
        test_log_file = log_dir / "test_analytics.jsonl"
        test_entries = [
            {
                "timestamp": "2025-10-06T23:30:00Z",
                "level": "INFO",
                "message": "Test log 1",
            },
            {
                "timestamp": "2025-10-06T23:31:00Z",
                "level": "ERROR",
                "message": "Test error",
            },
        ]

        with open(test_log_file, "w", encoding="utf-8") as f:
            for entry in test_entries:
                f.write(json.dumps(entry) + "\n")

        # Test parsing
        parsed_logs = LogAnalytics.parse_jsonl_logs(test_log_file)
        assert len(parsed_logs) == 2
        assert parsed_logs[0]["message"] == "Test log 1"

        # Clean up
        test_log_file.unlink()

        print("✅ Log analytics test passed")
        return True

    except Exception as e:
        print(f"❌ Log analytics test failed: {e}")
        return False


def run_integration_tests():
    """Run all integration tests."""
    print("🚀 EQ12 System Integration Test Suite")
    print("=" * 50)

    tests = [
        test_logging_system,
        test_migration_helper,
        test_repo_scanner,
        test_log_analysis,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All integration tests passed!")
        print("✅ EQ12 system ready for production use")
    else:
        print("⚠️  Some tests failed - check logs for details")

    return failed == 0


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
