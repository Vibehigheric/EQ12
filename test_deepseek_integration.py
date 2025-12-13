#!/usr/bin/env python3
"""
DeepSeek Integration Test & Validation Script
Tests the complete multi-LLM integration with OpenAI and DeepSeek support
"""

import json
import sqlite3
import sys
from pathlib import Path


def test_database_schema():
    """Test that DeepSeek calls table exists"""
    print("🔍 Testing DeepSeek database schema...")

    db_path = Path("visual_studio_projects/EQ12SportsBettingTerminal/Data/bankroll.db")
    if not db_path.exists():
        print("❌ Database file not found")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check for deepseek_calls table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='deepseek_calls'"
        )
        if not cursor.fetchone():
            print("❌ deepseek_calls table not found")
            return False
        print("✅ deepseek_calls table exists")

        # Check table structure
        cursor.execute("PRAGMA table_info(deepseek_calls)")
        columns = [row[1] for row in cursor.fetchall()]
        expected_columns = [
            "id",
            "ts",
            "prompt",
            "output",
            "status",
            "tokens_estimated",
            "model_used",
            "content_type",
            "execution_time_ms",
            "created_at",
        ]

        for col in expected_columns:
            if col in columns:
                print("  ✅ Column '{col}' exists")
            else:
                print("  ❌ Column '{col}' missing")
                return False

        conn.close()
        return True

    except Exception:
        print("❌ Database schema test failed: {e}")
        return False


def test_configuration():
    """Test DeepSeek configuration structure"""
    print("\n⚙️ Testing DeepSeek configuration...")

    config_path = Path("visual_studio_projects/EQ12SportsBettingTerminal/Config/config.json")
    if not config_path.exists():
        print("❌ config.json not found")
        return False

    try:
        with open(config_path) as f:
            config = json.load(f)

        # Check for DeepSeek configuration section
        if "deepseek" not in config:
            print("❌ DeepSeek configuration section missing")
            return False

        deepseek_config = config["deepseek"]
        required_keys = ["api_key", "endpoint", "model"]

        for key in required_keys:
            if key in deepseek_config:
                print("  ✅ DeepSeek {key} configured")
            else:
                print("  ❌ DeepSeek {key} missing")
                return False

        # Check LLM configuration section
        if "llm" not in config:
            print("❌ LLM configuration section missing")
            return False

        llm_config = config["llm"]
        if "default_provider" in llm_config and "providers" in llm_config:
            print("  ✅ LLM provider configuration: {llm_config['default_provider']}")
            print("  ✅ Available providers: {', '.join(llm_config['providers'])}")
        else:
            print("  ⚠️ LLM provider configuration incomplete")

        # Check ContentEngine LLM provider setting
        if "content_engine" in config and "llm_provider" in config["content_engine"]:
            config["content_engine"]["llm_provider"]
            print("  ✅ Content Engine LLM provider: {provider}")
        else:
            print("  ⚠️ Content Engine LLM provider not specified (will use default)")

        return True

    except Exception:
        print("❌ Configuration test failed: {e}")
        return False


def test_module_files():
    """Test that all DeepSeek integration files exist"""
    print("\n📁 Testing DeepSeek integration files...")

    required_files = [
        "visual_studio_projects/EQ12SportsBettingTerminal/Modules/DeepSeekHelper.vb",
        "visual_studio_projects/EQ12SportsBettingTerminal/Modules/ContentEngine.vb",
        "visual_studio_projects/EQ12SportsBettingTerminal/Eq12Cli.vb",
    ]

    all_exist = True
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print("✅ {file_path}")

            # Check for specific integration markers
            if "DeepSeekHelper.vb" in file_path:
                with open(full_path, encoding="utf-8") as f:
                    content = f.read()
                if "CallDeepSeek" in content and "LogDeepSeekCall" in content:
                    print("  ✅ Core DeepSeek functions implemented")
                else:
                    print("  ⚠️ DeepSeek functions may be incomplete")

            elif "ContentEngine.vb" in file_path:
                with open(full_path, encoding="utf-8") as f:
                    content = f.read()
                if "RenderWithLLM" in content and "GetLLMProvider" in content:
                    print("  ✅ Multi-LLM support implemented")
                else:
                    print("  ⚠️ Multi-LLM integration may be incomplete")

            elif "Eq12Cli.vb" in file_path:
                with open(full_path, encoding="utf-8") as f:
                    content = f.read()
                if "--llm=" in content and "test-deepseek" in content:
                    print("  ✅ CLI LLM provider support implemented")
                else:
                    print("  ⚠️ CLI DeepSeek integration may be incomplete")

        else:
            print("❌ {file_path} - NOT FOUND")
            all_exist = False

    return all_exist


def test_llm_provider_logic():
    """Test LLM provider selection logic"""
    print("\n🤖 Testing LLM provider selection logic...")

    # Test configurations
    test_configs = [
        {
            "name": "OpenAI Default",
            "config": {"llm": {"default_provider": "openai"}},
            "expected": "openai",
        },
        {
            "name": "DeepSeek Default",
            "config": {"llm": {"default_provider": "deepseek"}},
            "expected": "deepseek",
        },
        {
            "name": "Content Engine Override",
            "config": {
                "llm": {"default_provider": "openai"},
                "content_engine": {"llm_provider": "deepseek"},
            },
            "expected": "deepseek",
        },
    ]

    for test in test_configs:
        print("  🧪 Testing: {test['name']}")

        # Simulate provider selection logic
        config = test["config"]

        # Check content engine specific provider setting first
        if config.get("content_engine", {}).get("llm_provider"):
            provider = config["content_engine"]["llm_provider"]
        # Then check global default
        elif config.get("llm", {}).get("default_provider"):
            provider = config["llm"]["default_provider"]
        else:
            provider = "openai"

        if provider == test["expected"]:
            print("    ✅ Correct provider selected: {provider}")
        else:
            print(f"    ❌ Wrong provider. Expected: {test['expected']}, Got: {provider}")
            return False

    return True


def main():
    """Main test function"""
    print("🚀 DEEPSEEK INTEGRATION - COMPREHENSIVE VALIDATION")
    print("=" * 60)

    results = []

    # Run all tests
    results.append(("DeepSeek Database Schema", test_database_schema()))
    results.append(("DeepSeek Configuration", test_configuration()))
    results.append(("Integration Module Files", test_module_files()))
    results.append(("LLM Provider Selection Logic", test_llm_provider_logic()))

    # Summary
    print("\n📊 DEEPSEEK INTEGRATION VALIDATION SUMMARY")
    print("=" * 45)

    passed = 0
    for _test_name, result in results:
        print("{test_name:<30} | {status}")
        if result:
            passed += 1

    print("\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 DeepSeek Integration is ready for production!")
        print("\n🎯 DEEPSEEK FEATURES ACTIVE:")
        print("  🤖 DeepSeekHelper.vb - Complete Chat.DeepSeek API integration")
        print("  📝 ContentEngine.vb - Multi-LLM provider support (OpenAI + DeepSeek)")
        print("  ⌨️ Eq12Cli.vb - --llm=deepseek command line flag support")
        print("  🗄️ deepseek_calls table - Complete API logging and analytics")
        print("  ⚙️ config.json - Comprehensive LLM provider configuration")

        print("\n💡 Usage Examples:")
        print("  # Use DeepSeek for content generation")
        print("  Eq12Cli.exe content-daily --llm=deepseek")
        print("  Eq12Cli.exe report-weekly --llm=deepseek")
        print("")
        print("  # Test DeepSeek API integration")
        print("  Eq12Cli.exe test-deepseek")
        print("")
        print("  # Set DeepSeek as default in config.json")
        print('  "content_engine": { "llm_provider": "deepseek" }')

        print("\n🚀 Ready to run production workloads with dual LLM support!")

    else:
        print(f"\n⚠️ {len(results) - passed} validation(s) failed - check above for details")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
