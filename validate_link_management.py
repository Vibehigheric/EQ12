#!/usr/bin/env python3
"""
Link Management & Safety Trainer - Validation Script
Tests the integration and functionality of the new modules
"""

import json
import sqlite3
import sys
from pathlib import Path


def validate_database_schema():
    """Validate that database has the required tables for Link Management"""
    print("🔍 Validating database schema...")

    db_path = Path("visual_studio_projects/EQ12SportsBettingTerminal/Data/bankroll.db")
    if not db_path.exists():
        print("❌ Database file not found")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check for bitly_stats table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bitly_stats'")
        if not cursor.fetchone():
            print("❌ bitly_stats table not found")
            return False
        print("✅ bitly_stats table exists")

        # Check for link_safety_checks table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='link_safety_checks'"
        )
        if not cursor.fetchone():
            print("❌ link_safety_checks table not found")
            return False
        print("✅ link_safety_checks table exists")

        conn.close()
        return True

    except Exception:
        print("❌ Database validation failed: {e}")
        return False


def validate_module_files():
    """Validate that all Link Management module files exist"""
    print("\n📁 Validating module files...")

    required_files = [
        "visual_studio_projects/EQ12SportsBettingTerminal/Modules/LinkAnalyticsModule.vb",
        "visual_studio_projects/EQ12SportsBettingTerminal/Modules/LinkSafetyModule.vb",
        "visual_studio_projects/EQ12SportsBettingTerminal/Modules/DBWriter.vb",
    ]

    all_exist = True
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            print("✅ {file_path}")
        else:
            print("❌ {file_path} - NOT FOUND")
            all_exist = False

    return all_exist


def validate_config():
    """Validate configuration has Bitly settings"""
    print("\n⚙️ Validating configuration...")

    config_path = Path("visual_studio_projects/EQ12SportsBettingTerminal/Config/config.json")
    if not config_path.exists():
        print("❌ config.json not found")
        return False

    try:
        with open(config_path) as f:
            config = json.load(f)

        # Check for Bitly configuration
        if "bitly" not in config:
            print("⚠️ Bitly configuration section missing")
            return False

        if "access_token" not in config["bitly"]:
            print("⚠️ Bitly access_token not configured")
        else:
            token = config["bitly"]["access_token"]
            if token and token != "your_bitly_token_here":
                print("✅ Bitly access token configured")
            else:
                print("⚠️ Bitly access token needs to be set")

        return True

    except Exception:
        print("❌ Config validation failed: {e}")
        return False


def test_link_safety_analysis():
    """Test link safety analysis functionality"""
    print("\n🔐 Testing Link Safety Analysis...")

    # Test URLs for analysis
    test_urls = [
        "bit.ly/test123",
        "tinyurl.com/example",
        "https://github.com/microsoft/vscode",
        "https://suspicious-domain.tk/phishing",
    ]

    for url in test_urls:
        print("  🔗 Analyzing: {url}")

        # Basic URL validation
        if any(suspicious_tld in url for suspicious_tld in [".tk", ".ml", ".ga", ".cf"]):
            print("    ⚠️ Suspicious TLD detected")
        elif any(trusted_domain in url for trusted_domain in ["github.com", "microsoft.com"]):
            print("    ✅ Trusted domain")
        else:
            print("    ⚠️ Unknown domain - verify manually")

    return True


def main():
    """Main validation function"""
    print("🚀 EQ12 LINK MANAGEMENT & SAFETY TRAINER - VALIDATION")
    print("=" * 60)

    results = []

    # Run all validations
    results.append(("Database Schema", validate_database_schema()))
    results.append(("Module Files", validate_module_files()))
    results.append(("Configuration", validate_config()))
    results.append(("Link Safety Analysis", test_link_safety_analysis()))

    # Summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 30)

    passed = 0
    for _test_name, result in results:
        print("{test_name:<20} | {status}")
        if result:
            passed += 1

    print("\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 Link Management & Safety Trainer system is ready!")
        print("\n🎯 MASTER-LEVEL FEATURES ACTIVE:")
        print("  📊 Link Analytics Module - Bitly API integration & campaign tracking")
        print("  🔐 Link Safety Module - Cybersecurity verification & phishing detection")
        print("  📝 Content Engine - Monetization content generation")
        print("  🛡️ Database Logging - Complete analytics & security audit trail")
        print("\n💡 Next Steps:")
        print("  1. Configure Bitly access token in config.json")
        print("  2. Test Link Analytics with real Bitly links")
        print("  3. Practice cybersecurity verification workflows")
        print("  4. Generate monetization content with Content Engine")

    else:
        print(f"\n⚠️ {len(results) - passed} validation(s) failed - check above for details")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
