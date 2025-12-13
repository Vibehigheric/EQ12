#!/usr/bin/env python3
"""
EQ12 System Status Check
Quick validation of key system components after upgrades
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_environment():
    """Check environment configuration"""
    print("🔍 Environment Check")

    results = {}

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.startswith("sk-"):
        print("  ✅ OpenAI API Key configured")
        results["openai_key"] = True
    else:
        print("  ❌ OpenAI API Key missing")
        results["openai_key"] = False

    # Check EQ12 LLM setting
    llm_enabled = os.getenv("EQ12_USE_LLM", "0") == "1"
    if llm_enabled:
        print("  ✅ EQ12 LLM enabled")
        results["llm_enabled"] = True
    else:
        print("  ❌ EQ12 LLM disabled")
        results["llm_enabled"] = False

    return results


def check_openai_library():
    """Check OpenAI library installation"""
    print("🤖 OpenAI Library Check")

    results = {}

    try:
        import openai

        version = openai.__version__
        print(f"  ✅ OpenAI library v{version}")
        results["installed"] = True
        results["version"] = version

        # Check if version is 2.x or higher
        major_version = int(version.split(".")[0])
        if major_version >= 2:
            print("  ✅ Modern OpenAI API (v2+)")
            results["modern_api"] = True
        else:
            print("  ⚠️ Older OpenAI API (v1)")
            results["modern_api"] = False

    except ImportError:
        print("  ❌ OpenAI library not installed")
        results["installed"] = False
    except Exception as e:
        print(f"  ❌ OpenAI library check failed: {e}")
        results["error"] = str(e)

    return results


def check_circuit_breaker():
    """Check circuit breaker system"""
    print("🛡️ Circuit Breaker Check")

    results = {}

    try:
        from eq12_llm_offline import LLMOffline

        is_offline = LLMOffline.is_offline()
        status = LLMOffline.status()

        if is_offline:
            print(f"  ⚠️ Circuit breaker active: {status}")
            results["active"] = True
            results["status"] = status
        else:
            print("  ✅ Circuit breaker ready")
            results["active"] = False
            results["status"] = "ready"

        results["functional"] = True

    except ImportError:
        print("  ❌ Circuit breaker module not found")
        results["functional"] = False
    except Exception as e:
        print(f"  ❌ Circuit breaker error: {e}")
        results["functional"] = False
        results["error"] = str(e)

    return results


def check_configurations():
    """Check key configuration files"""
    print("⚙️ Configuration Files Check")

    results = {}

    # Check .env
    env_path = Path(".env")
    if env_path.exists():
        print("  ✅ .env file exists")
        results["env_file"] = True
    else:
        print("  ❌ .env file missing")
        results["env_file"] = False

    # Check AI config
    ai_config_path = Path("configs/ai_enhanced_config.json")
    if ai_config_path.exists():
        try:
            with open(ai_config_path) as f:
                config = json.load(f)

            # Check for GPT-4o models
            if "gpt-4o" in str(config):
                print("  ✅ AI config has GPT-4o models")
                results["ai_config_modern"] = True
            else:
                print("  ⚠️ AI config may need GPT-4o upgrade")
                results["ai_config_modern"] = False

            results["ai_config"] = True
        except Exception as e:
            print(f"  ❌ AI config error: {e}")
            results["ai_config"] = False
    else:
        print("  ❌ AI config missing")
        results["ai_config"] = False

    return results


def check_directories():
    """Check key directories"""
    print("📁 Directory Structure Check")

    results = {}

    directories = ["scripts", "tests", "configs", "logs", "dashboard", "data"]

    for directory in directories:
        path = Path(directory)
        if path.exists() and path.is_dir():
            print(f"  ✅ {directory}/ exists")
            results[directory] = True
        else:
            print(f"  ❌ {directory}/ missing")
            results[directory] = False

    return results


def generate_summary(all_results):
    """Generate system status summary"""
    print("\n" + "=" * 50)
    print("🎯 EQ12 SYSTEM STATUS SUMMARY")
    print("=" * 50)

    total_checks = 0
    passed_checks = 0

    for category, results in all_results.items():
        category_passed = 0
        category_total = 0

        for _key, value in results.items():
            if isinstance(value, bool):
                category_total += 1
                if value:
                    category_passed += 1

        if category_total > 0:
            success_rate = (category_passed / category_total) * 100
            print(f"{category}: {category_passed}/{category_total} ({success_rate:.1f}%)")
            total_checks += category_total
            passed_checks += category_passed

    overall_success = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

    print(f"\nOverall: {passed_checks}/{total_checks} ({overall_success:.1f}%)")

    if overall_success >= 80:
        status = "🟢 HEALTHY"
    elif overall_success >= 60:
        status = "🟡 NEEDS_ATTENTION"
    else:
        status = "🔴 CRITICAL"

    print(f"System Status: {status}")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"logs/eq12_status_check_{timestamp}.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_success_rate": overall_success,
        "status": status,
        "checks": all_results,
        "summary": {"total_checks": total_checks, "passed_checks": passed_checks},
    }

    try:
        os.makedirs("logs", exist_ok=True)
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"📊 Detailed report: {report_path}")
    except Exception as e:
        print(f"⚠️ Could not save report: {e}")


def main():
    """Main status check function"""
    print("🚀 EQ12 SYSTEM STATUS CHECK")
    print("=" * 50)

    all_results = {}

    # Run all checks
    all_results["environment"] = check_environment()
    all_results["openai_library"] = check_openai_library()
    all_results["circuit_breaker"] = check_circuit_breaker()
    all_results["configurations"] = check_configurations()
    all_results["directories"] = check_directories()

    # Generate summary
    generate_summary(all_results)


if __name__ == "__main__":
    main()
