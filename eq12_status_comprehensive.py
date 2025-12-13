"""
EQ12 Comprehensive Status Checker
Shows system status, budget configuration, and production readiness without requiring API keys
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path


def check_system_status():
    """Check comprehensive system status"""

    print("🎯 EQ12 COMPREHENSIVE STATUS CHECK")
    print("=" * 60)
    print(f"Timestamp: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()

    status = {"timestamp": datetime.now(UTC).isoformat(), "checks": {}}

    # 1. Directory Structure
    print("📁 DIRECTORY STRUCTURE")
    eq12_root = Path("C:/EQ12")
    required_dirs = ["logs", "configs", "data", "scripts", "tests"]

    for dir_name in required_dirs:
        dir_path = eq12_root / dir_name
        exists = dir_path.exists()
        status_icon = "✅" if exists else "❌"
        print(f"   {status_icon} {dir_name}/")

        if exists and dir_name == "logs":
            log_count = len(list(dir_path.glob("*.log")))
            json_count = len(list(dir_path.glob("*.json")))
            print(f"      {log_count} log files, {json_count} JSON files")

    status["checks"]["directories"] = {
        dir_name: (eq12_root / dir_name).exists() for dir_name in required_dirs
    }
    print()

    # 2. Core Files
    print("📄 CORE FILES")
    core_files = [
        "eq12_ai_client.py",
        "eq12_budget_enforcer.py",
        "eq12_budget_dashboard.py",
        "eq12_system_fixer.py",
        "configs/eq12_budget_policy.yaml",
    ]

    for file_path in core_files:
        full_path = eq12_root / file_path
        exists = full_path.exists()
        status_icon = "✅" if exists else "❌"
        print(f"   {status_icon} {file_path}")

        if exists and file_path.endswith(".py"):
            try:
                with open(full_path, encoding="utf-8") as f:
                    lines = len(f.readlines())
                print(f"      {lines} lines of code")
            except Exception:
                pass

    status["checks"]["core_files"] = {
        file_path: (eq12_root / file_path).exists() for file_path in core_files
    }
    print()

    # 3. Budget Configuration
    print("💰 BUDGET CONFIGURATION")
    try:
        from eq12_budget_enforcer import budget_enforcer

        budget_status = budget_enforcer.get_status()

        print("   ✅ Budget enforcer loaded")
        print(f"   📊 Daily cap: ${budget_status['daily_cap']:.2f}")
        print(f"   📊 Monthly cap: ${budget_status['monthly_cap']:.2f}")
        print(f"   💡 Current daily usage: ${budget_status['daily_usage']:.3f}")
        print(f"   💡 Current monthly usage: ${budget_status['monthly_usage']:.3f}")

        # Bucket status
        for bucket, data in budget_status["buckets"].items():
            usage_pct = (data["usage"] / data["cap"]) * 100 if data["cap"] > 0 else 0
            print(
                f"   🎯 {bucket.upper()}: ${data['usage']:.3f}/${data['cap']:.2f} ({usage_pct:.1f}%)"
            )

        status["checks"]["budget_system"] = True
        status["budget_status"] = budget_status

    except ImportError:
        print("   ❌ Budget enforcer not available")
        status["checks"]["budget_system"] = False
    except Exception as e:
        print(f"   ⚠️  Budget enforcer error: {e}")
        status["checks"]["budget_system"] = False
    print()

    # 4. AI Client Status
    print("🤖 AI CLIENT STATUS")
    try:
        from eq12_ai_client import EQ12AIClient

        print("   ✅ EQ12AIClient available")

        # Check client initialization (without API calls)
        client = EQ12AIClient()
        print(f"   📊 Max retries: {client.max_retries}")
        print(f"   📊 Daily budget: ${client.daily_budget}")

        # Check API key presence (masked)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print(f"   🔑 OpenAI key: {openai_key[:10]}...{openai_key[-4:]}")
        else:
            print("   ❌ OpenAI key not set")

        odds_key = os.getenv("ODDS_API_KEY")
        if odds_key:
            print(f"   🔑 Odds API key: {odds_key[:10]}...{odds_key[-4:]}")
        else:
            print("   ❌ Odds API key not set")

        status["checks"]["ai_client"] = True

    except ImportError as e:
        print(f"   ❌ AI client import error: {e}")
        status["checks"]["ai_client"] = False
    except Exception as e:
        print(f"   ⚠️  AI client error: {e}")
        status["checks"]["ai_client"] = False
    print()

    # 5. Environment Variables
    print("🌍 ENVIRONMENT VARIABLES")
    env_vars = {
        "OPENAI_API_KEY": "OpenAI API access",
        "ODDS_API_KEY": "Sports odds data",
        "TELEGRAM_BOT_TOKEN": "Telegram notifications (optional)",
        "TELEGRAM_CHAT_ID": "Telegram chat target (optional)",
        "AZURE_OPENAI_KEY": "Azure OpenAI (optional)",
        "AZURE_OPENAI_ENDPOINT": "Azure endpoint (optional)",
    }

    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive data
            masked = f"{value[:6]}...{value[-4:]}" if len(value) > 10 else "***"
            print(f"   ✅ {var}: {masked} ({description})")
        else:
            optional = "(optional)" in description
            status_icon = "⚠️ " if optional else "❌"
            print(f"   {status_icon} {var}: Not set ({description})")

    status["checks"]["environment"] = {var: bool(os.getenv(var)) for var in env_vars}
    print()

    # 6. Python Environment
    print("🐍 PYTHON ENVIRONMENT")
    print(f"   📊 Python version: {sys.version}")
    print(f"   📊 Platform: {sys.platform}")
    print(f"   📊 Executable: {sys.executable}")

    # Check key imports
    key_imports = [
        ("httpx", "HTTP client for API calls"),
        ("yaml", "YAML configuration parsing"),
        ("json", "JSON data processing"),
        ("pathlib", "Path handling"),
    ]

    for module, description in key_imports:
        try:
            __import__(module)
            print(f"   ✅ {module}: Available ({description})")
        except ImportError:
            print(f"   ❌ {module}: Missing ({description})")

    status["checks"]["python_env"] = True
    print()

    # 7. Recent Activity
    print("📊 RECENT ACTIVITY")
    logs_dir = Path("C:/EQ12/logs")
    if logs_dir.exists():
        # Find recent files
        recent_files = []
        for file_path in logs_dir.glob("*"):
            if file_path.is_file():
                mtime = file_path.stat().st_mtime
                recent_files.append((file_path, mtime))

        # Sort by modification time, most recent first
        recent_files.sort(key=lambda x: x[1], reverse=True)

        print("   📄 Most recent files:")
        for file_path, mtime in recent_files[:5]:
            mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            print(f"      {mod_time} - {file_path.name}")

        if len(recent_files) > 5:
            print(f"      ... and {len(recent_files) - 5} more files")
    else:
        print("   ❌ Logs directory not found")
    print()

    # 8. Overall Status
    print("🎯 OVERALL STATUS")

    # Calculate readiness score
    total_checks = 0
    passed_checks = 0

    for _check_category, check_results in status["checks"].items():
        if isinstance(check_results, dict):
            for _check_name, check_result in check_results.items():
                total_checks += 1
                if check_result:
                    passed_checks += 1
        elif isinstance(check_results, bool):
            total_checks += 1
            if check_results:
                passed_checks += 1

    readiness_pct = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    # Determine overall status
    if readiness_pct >= 90:
        overall_status = "🎉 EXCELLENT"
    elif readiness_pct >= 75:
        overall_status = "✅ GOOD"
    elif readiness_pct >= 50:
        overall_status = "⚠️  NEEDS ATTENTION"
    else:
        overall_status = "❌ CRITICAL"

    print(f"   Status: {overall_status}")
    print(f"   Readiness: {passed_checks}/{total_checks} checks passed ({readiness_pct:.1f}%)")

    # Specific recommendations
    recommendations = []

    if not status["checks"].get("budget_system"):
        recommendations.append("Fix budget enforcer import issues")

    if not status["checks"].get("ai_client"):
        recommendations.append("Fix AI client configuration")

    env_checks = status["checks"].get("environment", {})
    if not env_checks.get("OPENAI_API_KEY"):
        recommendations.append("Set OPENAI_API_KEY environment variable")

    if not env_checks.get("ODDS_API_KEY"):
        recommendations.append("Set ODDS_API_KEY environment variable")

    if recommendations:
        print("   📋 Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"      {i}. {rec}")
    else:
        print("   🎉 No critical issues found!")

    # Save status to file
    status_file = Path("C:/EQ12/logs/system_status.json")
    try:
        status_file.parent.mkdir(exist_ok=True)
        with open(status_file, "w") as f:
            json.dump(status, f, indent=2)
        print(f"\n📄 Status saved to: {status_file}")
    except Exception as e:
        print(f"\n❌ Failed to save status: {e}")

    return readiness_pct >= 75


if __name__ == "__main__":
    success = check_system_status()
    sys.exit(0 if success else 1)
