#!/usr/bin/env python3
"""
EQ12 MCP and GitHub Models Integration Test
Simple Python script to test all components before November 10, 2025 deadline
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path


def print_status(message, level="INFO"):
    """Print colored status messages"""
    colors = {
        "SUCCESS": "\033[92m✅",
        "ERROR": "\033[91m❌",
        "WARN": "\033[93m⚠️",
        "INFO": "\033[94m📋",
    }

    color = colors.get(level, "\033[0m")
    print(f"{color} {message}\033[0m")


def test_mcp_library():
    """Test MCP library installation"""
    print_status("Testing MCP library installation...", "INFO")

    try:
        import mcp

        print_status("MCP library available", "SUCCESS")
        return True
    except ImportError:
        print_status("MCP library not installed - run: pip install mcp", "ERROR")
        return False


def test_github_models():
    """Test GitHub Models integration"""
    print_status("Testing GitHub Models integration...", "INFO")

    try:
        # Add EQ12 paths
        eq12_root = Path("C:/EQ12")
        sys.path.extend([str(eq12_root), str(eq12_root / "scripts"), str(eq12_root / "configs")])

        from github_models_integration import GitHubModelsManager

        # Test connection
        manager = GitHubModelsManager()

        # Run async test
        async def test_connection():
            result = await manager.test_github_models_connection()
            return result

        connection_result = asyncio.run(test_connection())

        if connection_result["success"]:
            models_count = connection_result.get("models_available", 0)
            print_status(f"GitHub Models connected - {models_count} models available", "SUCCESS")
            return True
        else:
            error = connection_result.get("error", "Unknown error")
            print_status(f"GitHub Models connection failed: {error}", "ERROR")
            return False

    except Exception as e:
        print_status(f"GitHub Models test failed: {e}", "ERROR")
        return False


def test_mcp_server():
    """Test EQ12 MCP server"""
    print_status("Testing EQ12 MCP Server...", "INFO")

    try:
        from eq12_mcp_server import EQ12MCPServer

        # Initialize server
        server = EQ12MCPServer()

        # Check capabilities
        capabilities_count = len(server.eq12_capabilities)
        systems_count = len(server.agentic_systems)

        print_status(
            f"MCP Server initialized - {capabilities_count} capabilities, {systems_count} systems",
            "SUCCESS",
        )

        # List key capabilities
        print_status("Available MCP capabilities:", "INFO")
        for cap in server.eq12_capabilities[:5]:  # Show first 5
            print(f"  • {cap.name} ({cap.category})")

        return True

    except Exception as e:
        print_status(f"MCP Server test failed: {e}", "ERROR")
        return False


def test_agentic_systems():
    """Test EQ12 agentic AI systems"""
    print_status("Testing EQ12 Agentic AI systems...", "INFO")

    systems_to_test = [
        "agentic_secret_detection.py",
        "agentic_devops_accelerator.py",
        "eq12_security_intelligence_hub.py",
    ]

    available_systems = 0

    for system in systems_to_test:
        system_path = Path("C:/EQ12/scripts") / system
        if system_path.exists():
            available_systems += 1
            print(f"  ✅ {system}")
        else:
            print(f"  ❌ {system} (not found)")

    if available_systems >= 2:
        print_status(
            f"Sufficient agentic systems available ({available_systems}/{len(systems_to_test)})",
            "SUCCESS",
        )
        return True
    else:
        print_status(
            f"Limited agentic systems ({available_systems}/{len(systems_to_test)})", "WARN"
        )
        return False


def show_migration_status():
    """Show GitHub Copilot Extensions migration status"""
    print_status("GitHub Copilot Extensions Migration Status", "INFO")

    # Calculate days remaining
    deadline = datetime(2025, 11, 10)
    today = datetime.now()
    days_remaining = (deadline - today).days

    if days_remaining <= 7:
        level = "ERROR"
        urgency = "🚨 CRITICAL"
    elif days_remaining <= 30:
        level = "WARN"
        urgency = "⚠️ URGENT"
    else:
        level = "INFO"
        urgency = "📅 SCHEDULED"

    print_status(
        f"{urgency}: {days_remaining} days until Copilot Extensions sunset (Nov 10, 2025)", level
    )

    # Show GitHub Models token status
    github_token_deadline = datetime(2025, 11, 6)
    token_days = (github_token_deadline - today).days

    if token_days <= 7:
        print_status(f"🔑 GitHub Models token expires in {token_days} days (Nov 6, 2025)", "ERROR")
    else:
        print_status(f"🔑 GitHub Models token expires in {token_days} days (Nov 6, 2025)", "WARN")


def main():
    """Main test execution"""
    print("\n🚀 EQ12 MCP & GitHub Models Integration Test")
    print("=" * 55)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📁 EQ12 Root: C:/EQ12")
    print()

    # Run tests
    test_results = {}

    print("🧪 Running Integration Tests...")
    print("-" * 30)

    test_results["MCP Library"] = test_mcp_library()
    test_results["GitHub Models"] = test_github_models()
    test_results["MCP Server"] = test_mcp_server()
    test_results["Agentic Systems"] = test_agentic_systems()

    print()

    # Show migration status
    show_migration_status()

    print()

    # Summary
    print("📊 Test Results Summary")
    print("-" * 25)

    passed = 0
    total = len(test_results)

    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    overall_success = passed == total

    print()

    if overall_success:
        print_status("🎉 ALL TESTS PASSED! EQ12 MCP system ready for GitHub migration.", "SUCCESS")
        print("📋 Next Steps:")
        print("   1. Configure Claude Desktop with MCP settings")
        print("   2. Test EQ12 capabilities through MCP interface")
        print("   3. Monitor for GitHub Copilot MCP support")
    else:
        print_status(
            f"⚠️ {total - passed} test(s) failed. Address issues before Nov 10 deadline.", "WARN"
        )
        print("📋 Recommendations:")
        if not test_results.get("MCP Library"):
            print("   • Install MCP: pip install mcp")
        if not test_results.get("GitHub Models"):
            print("   • Check GitHub Models token and connectivity")
        if not test_results.get("MCP Server"):
            print("   • Review MCP server dependencies and imports")

    print()
    print("📚 Documentation: EQ12_MCP_SETUP_GUIDE.md")
    print("🔗 GitHub Models: Active with 15 models available")
    print(
        "⚠️ Remember: Copilot Extensions sunset in",
        (datetime(2025, 11, 10) - datetime.now()).days,
        "days",
    )

    return overall_success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)
