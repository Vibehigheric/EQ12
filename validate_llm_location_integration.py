#!/usr/bin/env python3
"""
EQ12 Meta-LLM Router & Location Sharing Validation Script
Tests comprehensive AI provider routing and location-based monetization features
"""

import json
import os
import sys


def check_file_exists(file_path, description):
    """Check if a required file exists"""
    if os.path.exists(file_path):
        print("✅ {description}: Found")
        return True
    print("❌ Missing {description}: {file_path}")
    return False


def validate_llm_router_config(config_path):
    """Validate LLM Router configuration in config.json"""
    try:
        with open(config_path) as f:
            config = json.load(f)

        print("🤖 Validating LLM Router Configuration...")

        # Check llm_router section
        if "llm_router" not in config:
            print("❌ Missing llm_router section in config.json")
            return False

        llm_router = config["llm_router"]

        # Check required fields
        required_fields = [
            "enabled",
            "default",
            "rules",
            "cost_thresholds",
            "providers",
        ]
        missing_fields = [field for field in required_fields if field not in llm_router]

        if missing_fields:
            print("❌ Missing LLM Router fields: {', '.join(missing_fields)}")
            return False

        # Check provider configurations
        providers = ["openai", "deepseek", "gemini", "claude", "copilot", "llama"]
        configured_providers = []

        for provider in providers:
            if provider in config:
                print("✅ {provider.upper()} configuration found")
                configured_providers.append(provider)

        # Check routing rules
        rules = llm_router.get("rules", {})
        rule_types = [
            "reporting",
            "bulk_stats",
            "code_gen",
            "search_insights",
            "long_context",
            "offline",
        ]

        missing_rules = [rule for rule in rule_types if rule not in rules]
        if missing_rules:
            print("⚠️ Missing routing rules: {', '.join(missing_rules)}")

        # Check cost thresholds
        cost_config = llm_router.get("cost_thresholds", {})
        cost_fields = [
            "high_cost_limit_usd",
            "medium_cost_limit_usd",
            "bulk_processing_limit_usd",
        ]

        for field in cost_fields:
            if field in cost_config:
                print("✅ Cost threshold configured: {field}")

        print(f"✅ LLM Router validation passed - {len(configured_providers)} providers configured")
        return True

    except json.JSONDecodeError:
        print("❌ Invalid JSON in config file: {e}")
        return False
    except Exception:
        print("❌ Error validating LLM Router config: {e}")
        return False


def validate_location_config(config_path):
    """Validate Location Sharing configuration in config.json"""
    try:
        with open(config_path) as f:
            config = json.load(f)

        print("📍 Validating Location Sharing Configuration...")

        # Check location section
        if "location" not in config:
            print("❌ Missing location section in config.json")
            return False

        location_config = config["location"]

        # Check required fields
        required_fields = ["enabled", "source", "geofence_alerts"]
        missing_fields = [field for field in required_fields if field not in location_config]

        if missing_fields:
            print("❌ Missing Location fields: {', '.join(missing_fields)}")
            return False

        # Check geofence configuration
        geofence_config = location_config.get("geofence_alerts", {})
        if "zones" in geofence_config:
            zones = geofence_config["zones"]
            zone_types = ["stadium", "casino", "sportsbook"]

            for zone_type in zone_types:
                if zone_type in zones:
                    zone = zones[zone_type]
                    if "radius_meters" in zone and "alert_message" in zone:
                        print("✅ Geofence zone configured: {zone_type}")
                    else:
                        print("⚠️ Incomplete geofence zone: {zone_type}")

        # Check monetization features
        if "monetization" in location_config:
            monetization = location_config["monetization"]
            features = [
                "affiliate_campaigns",
                "location_based_offers",
                "travel_recommendations",
            ]

            for feature in features:
                if monetization.get(feature, False):
                    print("✅ Monetization feature enabled: {feature}")

        # Check compliance settings
        if "compliance" in location_config:
            compliance = location_config["compliance"]
            if compliance.get("legal_jurisdiction_check", False):
                print("✅ Legal jurisdiction checking enabled")

        print("✅ Location Sharing validation passed")
        return True

    except Exception:
        print("❌ Error validating Location config: {e}")
        return False


def validate_vb_modules():
    """Validate VB.NET module implementations"""
    base_path = "c:/EQ12/visual_studio_projects/EQ12SportsBettingTerminal/Modules"

    print("🔧 Validating VB.NET Module Implementations...")

    modules = [
        (
            "LLMRouter.vb",
            [
                "Public Shared Function DecideProvider",
                "Public Shared Function CallLLM",
                "Private Shared Function AnalyzePrompt",
                "Private Shared Function ApplySelectionHeuristics",
                "Private Shared Function CallGemini",
                "Private Shared Function CallClaude",
                "Public Shared Function GetUsageStats",
            ],
        ),
        (
            "LocationHelper.vb",
            [
                "Public Shared Function FetchLocationGoogle",
                "Public Shared Function FetchLocationIP",
                "Public Shared Sub LogLocation",
                "Public Shared Function CheckGeofence",
                "Public Shared Function CheckCompliance",
                "Public Shared Function ExportLocationData",
                "Public Shared Sub TriggerMonetizationCampaign",
            ],
        ),
    ]

    all_valid = True

    for module_name, required_functions in modules:
        module_path = os.path.join(base_path, module_name)

        if not check_file_exists(module_path, f"VB.NET Module {module_name}"):
            all_valid = False
            continue

        try:
            with open(module_path, encoding="utf-8") as f:
                content = f.read()

            missing_functions = []
            for func in required_functions:
                if func not in content:
                    function_name = func.split(" ")[-1]  # Get function name only
                    missing_functions.append(function_name)

            if missing_functions:
                print(f"❌ {module_name} missing functions: {', '.join(missing_functions)}")
                all_valid = False
            else:
                print("✅ {module_name} structure validation passed")

        except Exception:
            print("❌ Error reading {module_name}: {e}")
            all_valid = False

    return all_valid


def validate_database_schema():
    """Validate database schema includes new tables"""
    schema_path = "c:/EQ12/visual_studio_projects/EQ12SportsBettingTerminal/Data/schema.sql"

    print("🗄️ Validating Database Schema...")

    if not check_file_exists(schema_path, "Database Schema"):
        return False

    try:
        with open(schema_path) as f:
            content = f.read()

        required_tables = [
            "CREATE TABLE IF NOT EXISTS llm_calls",
            "CREATE TABLE IF NOT EXISTS location_logs",
            "CREATE TABLE IF NOT EXISTS geofence_events",
        ]

        missing_tables = []
        for table in required_tables:
            if table not in content:
                table_name = table.split()[-1]  # Get table name
                missing_tables.append(table_name)

        if missing_tables:
            print("❌ Database missing tables: {', '.join(missing_tables)}")
            return False

        # Check for specific columns in key tables
        if "llm_calls" in content:
            llm_columns = [
                "provider",
                "task_type",
                "tokens_used",
                "cost_estimate",
                "execution_time_ms",
            ]
            for col in llm_columns:
                if col in content:
                    print("✅ llm_calls table includes {col} column")

        if "location_logs" in content:
            location_columns = ["lat", "lon", "accuracy", "source", "compliance_status"]
            for col in location_columns:
                if col in content:
                    print("✅ location_logs table includes {col} column")

        print("✅ Database schema validation passed")
        return True

    except Exception:
        print("❌ Error reading schema file: {e}")
        return False


def validate_cli_integration():
    """Validate CLI command integration"""
    cli_path = "c:/EQ12/visual_studio_projects/EQ12SportsBettingTerminal/Eq12Cli.vb"

    print("⚡ Validating CLI Integration...")

    if not check_file_exists(cli_path, "CLI Module"):
        return False

    try:
        with open(cli_path, encoding="utf-8") as f:
            content = f.read()

        required_commands = [
            'Case "test-llm-router"',
            'Case "llm-stats"',
            'Case "log-location"',
            'Case "report-location"',
            "Private Sub TestLLMRouter",
            "Private Sub ShowLLMStats",
            "Private Sub LogCurrentLocation",
            "Private Sub ReportLocationHistory",
        ]

        missing_commands = []
        for cmd in required_commands:
            if cmd not in content:
                missing_commands.append(cmd)

        if missing_commands:
            print("❌ CLI missing commands: {', '.join(missing_commands)}")
            return False

        print("✅ CLI integration validation passed")
        return True

    except Exception:
        print("❌ Error reading CLI file: {e}")
        return False


def validate_content_engine_integration():
    """Validate ContentEngine LLM Router integration"""
    content_engine_path = (
        "c:/EQ12/visual_studio_projects/EQ12SportsBettingTerminal/Modules/ContentEngine.vb"
    )

    print("📝 Validating ContentEngine Integration...")

    if not check_file_exists(content_engine_path, "ContentEngine Module"):
        return False

    try:
        with open(content_engine_path, encoding="utf-8") as f:
            content = f.read()

        # Check for LLM Router integration
        integration_markers = [
            "LLMRouter.DecideProvider",
            "LLMRouter.CallLLM",
            'taskType = $"content_{kind}"',
        ]

        missing_integration = []
        for marker in integration_markers:
            if marker not in content:
                missing_integration.append(marker)

        if missing_integration:
            print(
                f"❌ ContentEngine missing LLM Router integration: {', '.join(missing_integration)}"
            )
            return False

        print("✅ ContentEngine LLM Router integration validated")
        return True

    except Exception:
        print("❌ Error reading ContentEngine file: {e}")
        return False


def generate_test_scenarios():
    """Generate test scenarios for manual validation"""
    print("\n🧪 MANUAL TEST SCENARIOS")
    print("=" * 50)

    print("\n🤖 LLM Router Test Cases:")
    print("1. Test different task types:")
    print("   Eq12Cli.exe test-llm-router")
    print("   Eq12Cli.exe test-llm-router --provider=deepseek")
    print("   Eq12Cli.exe test-llm-router --provider=gemini")

    print("\n2. Check LLM usage statistics:")
    print("   Eq12Cli.exe llm-stats")

    print("\n📍 Location Sharing Test Cases:")
    print("1. Log current location:")
    print("   Eq12Cli.exe log-location")

    print("\n2. Export location history:")
    print("   Eq12Cli.exe report-location --days=30")
    print("   Eq12Cli.exe report-location --output=location_export.csv")

    print("\n💰 Monetization Integration Tests:")
    print("1. Test geofence alerts with location simulation")
    print("2. Verify affiliate campaign triggers")
    print("3. Check compliance alerts for restricted jurisdictions")

    print("\n🔄 Content Engine Integration:")
    print("1. Generate content with automatic provider selection:")
    print("   Eq12Cli.exe content-daily")
    print("   Eq12Cli.exe content-weekly --llm=gemini")


def main():
    """Run comprehensive validation for LLM Router and Location Sharing"""
    print("🚀 EQ12 Meta-LLM Router & Location Sharing Validation")
    print("=" * 60)
    print()

    # Configuration validation
    print("📋 Validating Configuration...")
    config_path = "c:/EQ12/visual_studio_projects/EQ12SportsBettingTerminal/Config/config.json"
    llm_config_valid = validate_llm_router_config(config_path)
    location_config_valid = validate_location_config(config_path)
    print()

    # VB.NET modules validation
    print("🔧 Validating VB.NET Modules...")
    modules_valid = validate_vb_modules()
    print()

    # Database schema validation
    print("🗄️ Validating Database Schema...")
    db_valid = validate_database_schema()
    print()

    # CLI integration validation
    print("⚡ Validating CLI Integration...")
    cli_valid = validate_cli_integration()
    print()

    # ContentEngine integration validation
    print("📝 Validating ContentEngine Integration...")
    content_valid = validate_content_engine_integration()
    print()

    # Summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 30)

    results = [
        ("LLM Router Configuration", llm_config_valid),
        ("Location Sharing Configuration", location_config_valid),
        ("VB.NET Module Structure", modules_valid),
        ("Database Schema", db_valid),
        ("CLI Integration", cli_valid),
        ("ContentEngine Integration", content_valid),
    ]

    passed = sum(1 for _, valid in results if valid)
    total = len(results)

    for _name, _valid in results:
        print("  {status} {name}")

    print()
    print("Overall: {passed}/{total} validations passed")

    if passed == total:
        print("🎉 Meta-LLM Router & Location Sharing validation completed successfully!")
        print()
        print("🔑 KEY FEATURES IMPLEMENTED:")
        print("✅ Intelligent AI provider selection based on task type and cost")
        print("✅ Comprehensive location tracking with geofencing alerts")
        print("✅ Location-based monetization campaign triggers")
        print("✅ Legal compliance checking for betting jurisdictions")
        print("✅ Complete audit trail for AI usage and cost optimization")
        print("✅ CLI integration for testing and monitoring")
        print("✅ ContentEngine integration for automatic provider routing")

        # Generate test scenarios
        generate_test_scenarios()

        return True
    print("❌ Validation failed - please fix issues above")
    return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
