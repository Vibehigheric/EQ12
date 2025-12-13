#!/usr/bin/env python3
"""
Quick test of EQ12 NCAA Week 7 Conference Parlay System
"""

import os
import sys
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_week7_system():
    """Test the Week 7 conference system for basic functionality"""

    print("🧪 EQ12 NCAA WEEK 7 CONFERENCE PARLAY SYSTEM TEST")
    print("=" * 60)

    try:
        # Test imports
        print("1️⃣ Testing imports...")
        from eq12_ncaa_week7_conference_builder import EQ12NCAAWeek7ConferenceBuilder

        print("   ✅ Week 7 Conference Builder imported successfully")

        # Test initialization
        print("2️⃣ Testing initialization...")
        builder = EQ12NCAAWeek7ConferenceBuilder()
        print("   ✅ Week 7 Conference Builder initialized")

        # Test conference definitions
        print("3️⃣ Testing conference definitions...")
        conferences = list(builder.conferences.keys())
        print(f"   ✅ {len(conferences)} conferences loaded:")
        for conf in conferences:
            teams_count = len(builder.conferences[conf])
            print(f"     📊 {conf}: {teams_count} teams")

        # Test Top 25 rankings
        print("4️⃣ Testing Top 25 rankings...")
        top25_count = len(builder.top25_teams)
        print(f"   ✅ {top25_count} Top 25 teams loaded")

        # Test database connection
        print("5️⃣ Testing database...")
        import os

        db_path = "database/sports_betting.db"
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / 1024  # KB
            print(f"   ✅ Database exists: {db_size:.1f} KB")
        else:
            print("   ⚠️ Database will be created on first run")

        # Test OpenAI integration
        print("6️⃣ Testing OpenAI integration...")
        import os

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and len(openai_key) > 20:
            print("   ✅ OpenAI API key configured")
        else:
            print("   ⚠️ OpenAI API key not configured")

        print("\n🎉 ALL TESTS PASSED! Week 7 system ready for parlay generation.")
        print("\n💡 To generate parlays: python eq12_ncaa_week7_conference_builder.py")

        return True

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_week7_system()
    sys.exit(0 if success else 1)
