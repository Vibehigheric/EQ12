#!/usr/bin/env python3
"""
EQ12 Enhanced Status Checker with Async/Sync Compatibility
Fixes validation issues and provides truthful health status
"""

import asyncio
import json
import os
from datetime import datetime


def check_environment():
    """Enhanced environment check"""
    print("🔍 Environment Configuration")

    results = {}

    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("CHATGPT_API_KEY")
    if openai_key and openai_key.startswith("sk-"):
        print("  ✅ OpenAI API Key configured")
        results["api_key"] = True
        results["key_format"] = "valid"
    else:
        print("  ❌ OpenAI API Key missing or invalid")
        results["api_key"] = False
        results["key_format"] = "invalid"

    # Check LLM usage setting
    llm_enabled = os.getenv("EQ12_USE_LLM", "1") == "1"
    results["llm_enabled"] = llm_enabled
    print(f"  {'✅' if llm_enabled else '❌'} EQ12 LLM {'enabled' if llm_enabled else 'disabled'}")

    # Check model configuration
    primary_model = os.getenv("OPENAI_MODEL", "gpt-4o")
    fallback_models = os.getenv("OPENAI_FALLBACK_MODELS", "")
    results["primary_model"] = primary_model
    results["fallback_count"] = len([m for m in fallback_models.split(",") if m.strip()])

    print("  ⚙️ Primary model: {primary_model}")
    print("  📋 Fallback models: {results['fallback_count']}")

    return results


def check_openai_client():
    """Check OpenAI client functionality"""
    print("🤖 OpenAI Client Status")

    results = {}

    try:
        from eq12_openai_client_enhanced import get_openai_client

        client = get_openai_client()
        results["client_created"] = True
        results["mode"] = client.mode
        results["available"] = client.is_available()

        print("  ✅ Client created (mode: {client.mode})")
        print(
            f"  {'✅' if results['available'] else '❌'} Client available: {results['available']}"
        )

        # Test simple completion with proper sync handling
        if results["available"]:
            try:
                response = client.chat_sync(
                    [{"role": "user", "content": "Reply with just 'OK'"}],
                    timeout=10,
                    max_tokens=5,
                )

                if response.success and "OK" in response.content:
                    print("  ✅ Simple completion successful")
                    results["completion_test"] = True
                else:
                    print("  ⚠️ Completion returned: {response.content[:50]}")
                    results["completion_test"] = False

            except Exception:
                print("  ❌ Completion test failed: {e}")
                results["completion_test"] = False
        else:
            print("  ⏭️ Skipping completion test (client offline)")
            results["completion_test"] = None

    except Exception as e:
        print("  ❌ Client initialization failed: {e}")
        results["client_created"] = False
        results["error"] = str(e)

    return results


def check_circuit_breaker():
    """Check circuit breaker system"""
    print("🛡️ Circuit Breaker Status")

    results = {}

    try:
        from eq12_llm_offline import LLMOffline

        is_offline = LLMOffline.is_offline()
        status = LLMOffline.status()

        results["functional"] = True
        results["offline"] = is_offline
        results["status"] = status

        if is_offline:
            print("  ⚠️ Circuit breaker ACTIVE: {status.get('reason', 'unknown')}")
            if "until" in status:
                print("  ⏰ Active until: {status['until']}")
        else:
            print("  ✅ Circuit breaker ready (not tripped)")

    except Exception as e:
        print("  ❌ Circuit breaker error: {e}")
        results["functional"] = False
        results["error"] = str(e)

    return results


def check_async_compatibility():
    """Check async/sync compatibility"""
    print("🔄 Async/Sync Compatibility")

    results = {}

    try:
        from eq12_async_compat import in_running_loop, run_coro_blocking

        # Test if we can detect running loop
        in_loop = in_running_loop()
        results["loop_detection"] = True
        results["in_running_loop"] = in_loop

        print("  ✅ Loop detection working (in_loop: {in_loop})")

        # Test sync->async bridging
        async def test_coro():
            await asyncio.sleep(0.01)
            return "success"

        try:
            result = run_coro_blocking(test_coro(), timeout=1.0)
            results["sync_async_bridge"] = result == "success"
            print("  ✅ Sync->Async bridge working")
        except Exception:
            results["sync_async_bridge"] = False
            print("  ❌ Sync->Async bridge failed: {e}")

    except Exception as e:
        print("  ❌ Async compatibility error: {e}")
        results["loop_detection"] = False
        results["error"] = str(e)

    return results


def check_model_routing():
    """Check model routing and fallbacks"""
    print("📊 Model Routing & Fallbacks")

    results = {}

    try:
        from eq12_openai_client_enhanced import get_openai_client

        client = get_openai_client()

        results["primary_model"] = client.primary_model
        results["fallback_models"] = client.fallback_models
        results["total_models"] = 1 + len(client.fallback_models)

        print("  ⚙️ Primary: {client.primary_model}")
        print("  📋 Fallbacks: {len(client.fallback_models)} models")
        print("  📈 Total routing options: {results['total_models']}")

        # Validate model names
        valid_models = []
        for model in [client.primary_model, *client.fallback_models]:
            if model and isinstance(model, str) and len(model) > 3:
                valid_models.append(model)

        results["valid_models"] = len(valid_models)
        results["routing_health"] = len(valid_models) >= 2

        print(
            f"  {'✅' if results['routing_health'] else '❌'} Routing health: {len(valid_models)} valid models"
        )

    except Exception as e:
        print("  ❌ Model routing error: {e}")
        results["routing_health"] = False
        results["error"] = str(e)

    return results


def generate_status_summary(all_results):
    """Generate truthful system status summary"""
    print("\n" + "=" * 60)
    print("🎯 EQ12 ENHANCED SYSTEM STATUS")
    print("=" * 60)

    # Calculate overall health
    critical_checks = []

    # Environment checks
    env_results = all_results.get("environment", {})
    if not env_results.get("api_key", False):
        critical_checks.append("Missing API key")
    if not env_results.get("llm_enabled", False):
        critical_checks.append("LLM disabled")

    # Client checks
    client_results = all_results.get("openai_client", {})
    if not client_results.get("available", False):
        critical_checks.append("OpenAI client unavailable")

    # Circuit breaker checks
    cb_results = all_results.get("circuit_breaker", {})
    if cb_results.get("offline", False):
        critical_checks.append("Circuit breaker active")

    # Async compatibility
    async_results = all_results.get("async_compat", {})
    if not async_results.get("sync_async_bridge", False):
        critical_checks.append("Async compatibility issues")

    # Determine overall status
    if not critical_checks:
        status = "🟢 HEALTHY"
        status_msg = "All systems operational"
    elif len(critical_checks) <= 2:
        status = "🟡 DEGRADED"
        status_msg = f"Issues: {', '.join(critical_checks)}"
    else:
        status = "🔴 CRITICAL"
        status_msg = f"Multiple issues: {', '.join(critical_checks)}"

    print("Overall Status: {status}")
    print("Status Message: {status_msg}")
    print("Critical Issues: {len(critical_checks)}")

    # Detailed breakdown
    print("\n📊 Component Status:")
    components = [
        (
            "Environment",
            env_results.get("api_key", False) and env_results.get("llm_enabled", False),
        ),
        ("OpenAI Client", client_results.get("available", False)),
        ("Circuit Breaker", cb_results.get("functional", False)),
        ("Async Compatibility", async_results.get("sync_async_bridge", False)),
        (
            "Model Routing",
            all_results.get("model_routing", {}).get("routing_health", False),
        ),
    ]

    for _name, _healthy in components:
        print("  {icon} {name}")

    # Save enhanced report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"logs/eq12_enhanced_status_{timestamp}.json"

    report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": status,
        "status_message": status_msg,
        "critical_issues": critical_checks,
        "component_results": all_results,
        "health_score": (5 - len(critical_checks)) / 5 * 100,
    }

    try:
        os.makedirs("logs", exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print("\n📋 Enhanced report saved: {report_path}")
        print("🏥 Health Score: {report['health_score']:.1f}%")

    except Exception:
        print("⚠️ Could not save report: {e}")

    return report


def main():
    """Enhanced status check main function"""
    print("🚀 EQ12 ENHANCED SYSTEM STATUS CHECK")
    print("=" * 60)

    all_results = {}

    # Run all checks
    all_results["environment"] = check_environment()
    all_results["openai_client"] = check_openai_client()
    all_results["circuit_breaker"] = check_circuit_breaker()
    all_results["async_compat"] = check_async_compatibility()
    all_results["model_routing"] = check_model_routing()

    # Generate truthful summary
    report = generate_status_summary(all_results)

    return report


if __name__ == "__main__":
    main()
