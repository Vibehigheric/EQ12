#!/usr/bin/env python3
"""
EQ12 Quick Demo Launcher
Launch the full GitHub Community learning and NFL Week 6 automation system.

Usage:
    python eq12_quick_demo.py
"""

import json
import subprocess
import time
from pathlib import Path


def run_command(command: list, description: str) -> dict:
    """Run a command and return results"""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd="C:/EQ12", timeout=60)

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(command),
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print("🏈 EQ12 GitHub Community Learning + NFL Week 6 Automation Demo")
    print("=" * 60)

    # Demo sequence
    demos = [
        {
            "command": ["python", "eq12_forum_learner.py", "--report"],
            "description": "Forum Intelligence Gathering (GitHub Community)",
        },
        {
            "command": [
                "python",
                "eq12_forum_actions.py",
                "--create-issues",
                "--dry-run",
                "--max-issues",
                "2",
            ],
            "description": "Auto-Issue Creation from Intelligence",
        },
        {
            "command": ["python", "eq12_nfl_week6_seeder.py", "--generate-posts", "--dry-run"],
            "description": "NFL Week 6 Content Generation (100 Posts)",
        },
        {
            "command": [
                "python",
                "eq12_bills_analyzer.py",
                "--build-parlay",
                "--target-odds",
                "22000",
            ],
            "description": "Bills Mega-Parlay: $5 → $1000+ Optimizer",
        },
        {
            "command": ["python", "eq12_production_orchestrator.py", "--health-check"],
            "description": "Production System Health Check",
        },
    ]

    results = []

    for demo in demos:
        result = run_command(demo["command"], demo["description"])
        results.append(result)

        if result["success"]:
            print("✅ SUCCESS")
            # Show first 500 chars of output
            if result["stdout"]:
                preview = result["stdout"][:500]
                if len(result["stdout"]) > 500:
                    preview += "... (truncated)"
                print(f"Output: {preview}")
        else:
            print("❌ FAILED")
            if "error" in result:
                print(f"Error: {result['error']}")
            if result.get("stderr"):
                print(f"Error output: {result['stderr'][:300]}")

        print("-" * 40)
        time.sleep(2)  # Brief pause between demos

    # Summary
    print("\n📊 DEMO SUMMARY")
    print("=" * 40)

    successful = sum(1 for r in results if r["success"])
    total = len(results)

    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")

    if successful == total:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("\n🔥 EQ12 is ready for:")
        print("   • GitHub Community intelligence gathering")
        print("   • Automated issue creation from forum insights")
        print("   • NFL Week 6 content generation (100 monetizable posts)")
        print("   • Bills mega-parlay optimization ($5 → $1000+)")
        print("   • Production automation with rate limits & budget guards")

        print("\n💎 Next Steps:")
        print("   1. Configure GitHub token: set GITHUB_TOKEN=your_token")
        print("   2. Run full cycle: python eq12_production_orchestrator.py --full-cycle")
        print("   3. Start monitoring: python eq12_production_orchestrator.py --monitor")
        print("   4. Generate NFL content: python eq12_nfl_week6_seeder.py --export-json")
        print("   5. Build Bills parlay: python eq12_bills_analyzer.py --build-parlay")

    else:
        print("\n⚠️ Some systems need attention. Check the logs above for details.")

    # Save demo results
    demo_file = Path("C:/EQ12/logs/demo_results.json")
    demo_file.parent.mkdir(exist_ok=True)

    with demo_file.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "demo_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_demos": total,
                "successful_demos": successful,
                "results": results,
            },
            f,
            indent=2,
        )

    print(f"\n📄 Demo results saved to: {demo_file}")


if __name__ == "__main__":
    main()
