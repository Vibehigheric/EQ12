#!/usr/bin/env python3
"""
EQ12 GitHub CLI Integration
Command-line interface for the enhanced GitHub repository integrator
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from github_repo_integrator_enhanced import EnhancedGitHubIntegrator
except ImportError:
    print("❌ Error importing enhanced integrator: {e}")
    print("Falling back to basic integration...")
    from github_repo_integrator import GitHubRepoIntegrator as EnhancedGitHubIntegrator


def main():
    parser = argparse.ArgumentParser(
        description="EQ12 GitHub Integration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python github_cli.py search --category arbitrage --max-repos 10
  python github_cli.py integrate --category kelly --max-repos 5
  python github_cli.py auto --all-categories --max-repos 20
  python github_cli.py status

Categories: all, arbitrage, kelly, oddsapi
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search GitHub repositories")
    search_parser.add_argument(
        "--category",
        default="all",
        choices=["all", "arbitrage", "kelly", "oddsapi"],
        help="Repository category to search for",
    )
    search_parser.add_argument(
        "--max-repos", type=int, default=20, help="Maximum repositories to return"
    )
    search_parser.add_argument(
        "--output", choices=["json", "table"], default="table", help="Output format"
    )

    # Integrate command
    integrate_parser = subparsers.add_parser("integrate", help="Integrate repositories")
    integrate_parser.add_argument(
        "--category",
        default="all",
        choices=["all", "arbitrage", "kelly", "oddsapi"],
        help="Repository category to integrate",
    )
    integrate_parser.add_argument(
        "--max-repos", type=int, default=10, help="Maximum repositories to integrate"
    )
    integrate_parser.add_argument(
        "--min-score",
        type=int,
        default=40,
        help="Minimum monetization score for integration",
    )

    # Auto command (search + integrate)
    auto_parser = subparsers.add_parser("auto", help="Auto search and integrate")
    auto_parser.add_argument("--all-categories", action="store_true", help="Process all categories")
    auto_parser.add_argument("--category", default="all", help="Specific category to process")
    auto_parser.add_argument(
        "--max-repos", type=int, default=15, help="Maximum repositories per category"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show integration status")
    status_parser.add_argument(
        "--detailed", action="store_true", help="Show detailed status information"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize integrator
    try:
        integrator = EnhancedGitHubIntegrator()
        print("✅ Enhanced GitHub Integrator initialized")
    except Exception:
        print("❌ Failed to initialize integrator: {e}")
        return

    # Execute command
    if args.command == "search":
        run_search(integrator, args)
    elif args.command == "integrate":
        run_integration(integrator, args)
    elif args.command == "auto":
        run_auto_integration(integrator, args)
    elif args.command == "status":
        show_status(args)


def run_search(integrator, args):
    """Run repository search"""
    print("🔍 Searching GitHub for {args.category} repositories...")

    try:
        repos = integrator.search_repositories(args.category, args.max_repos)

        if args.output == "json":
            print(json.dumps(repos, indent=2))
        else:
            print_repos_table(repos)

    except Exception:
        print("❌ Search failed: {e}")


def run_integration(integrator, args):
    """Run repository integration"""
    print("⚡ Integrating {args.category} repositories...")

    try:
        results = integrator.run_enhanced_integration(args.category, args.max_repos)
        print_integration_results(results)

    except Exception:
        print("❌ Integration failed: {e}")


def run_auto_integration(integrator, args):
    """Run automatic search and integration"""
    categories = ["arbitrage", "kelly", "oddsapi"] if args.all_categories else [args.category]

    total_results = {
        "total_searched": 0,
        "total_cloned": 0,
        "total_modules": 0,
        "all_modules": [],
        "all_errors": [],
    }

    for category in categories:
        print("\n🚀 Auto-processing category: {category}")
        print("=" * 60)

        try:
            results = integrator.run_enhanced_integration(category, args.max_repos)

            # Accumulate results
            total_results["total_searched"] += results["searched_repos"]
            total_results["total_cloned"] += results["cloned_repos"]
            total_results["total_modules"] += results["generated_modules"]
            total_results["all_modules"].extend(results["modules"])
            total_results["all_errors"].extend(results["errors"])

            print_integration_results(results)

        except Exception as e:
            error_msg = f"Category {category} failed: {e}"
            total_results["all_errors"].append(error_msg)
            print("❌ {error_msg}")

    # Print summary
    print("\n" + "=" * 80)
    print("🎯 AUTO INTEGRATION COMPLETE SUMMARY")
    print("=" * 80)
    print("📊 Total repositories searched: {total_results['total_searched']}")
    print("📥 Total repositories cloned: {total_results['total_cloned']}")
    print("⚡ Total VB.NET modules generated: {total_results['total_modules']}")

    if total_results["all_modules"]:
        print("\n🔥 Generated {len(total_results['all_modules'])} Enhanced Modules:")
        for i, module in enumerate(total_results["all_modules"], 1):
            print(
                f"  {i}. {module['repo']} → {module['integration_type']} "
                f"(Score: {module['monetization_score']})"
            )

    if total_results["all_errors"]:
        print("\n⚠️ Total errors: {len(total_results['all_errors'])}")
        for _error in total_results["all_errors"][:3]:
            print("  • {error}")


def print_repos_table(repos):
    """Print repositories in table format"""
    if not repos:
        print("No repositories found.")
        return

    print("\n📦 Found {len(repos)} repositories:\n")

    # Header
    print("{'Name':<40} {'Stars':<8} {'Language':<12} {'Score':<8}")
    print("-" * 80)

    # Rows
    for repo in repos:
        repo.get("full_name", repo.get("name", "Unknown"))[:39]
        str(repo.get("stargazers_count", repo.get("stars", 0)))
        repo.get("language", "Unknown")[:11]
        str(repo.get("monetization_score", "N/A"))

        print("{name:<40} {stars:<8} {language:<12} {score:<8}")


def print_integration_results(results):
    """Print integration results"""
    print("\n📊 Integration Results:")
    print("  Searched: {results['searched_repos']}")
    print("  Cloned: {results['cloned_repos']}")
    print("  Generated: {results['generated_modules']} VB.NET modules")

    if results.get("summary"):
        results["summary"]
        print("  Languages: {', '.join(summary.get('languages_found', []))}")
        print("  Success rate: {summary.get('success_rate', 'N/A')}")
        print("  Avg complexity: {summary.get('avg_complexity', 'N/A'):.1f}")
        print("  Avg monetization: {summary.get('avg_monetization', 'N/A'):.1f}")

    if results["modules"]:
        print("\n🎯 Generated Modules:")
        for _i, module in enumerate(results["modules"], 1):
            print("  {i}. {module['repo']}")
            print(
                f"     Type: {module['integration_type']} | "
                f"Score: {module['monetization_score']} | "
                f"Languages: {', '.join(module.get('languages', []))}"
            )
            print("     Path: {module['module_path']}")

    if results["errors"]:
        print("\n⚠️ Errors ({len(results['errors'])}):")
        for _error in results["errors"][:5]:
            print("  • {error}")


def show_status(args):
    """Show integration status"""
    db_path = "C:\\\\EQ12\\\\data\\github_integration_enhanced.db"

    if not os.path.exists(db_path):
        print("❌ No integration database found. Run integration first.")
        return

    try:
        import sqlite3

        with sqlite3.connect(db_path) as conn:
            # Get search stats
            cursor = conn.execute(
                "SELECT COUNT(*), category FROM searches_enhanced GROUP BY category"
            )
            searches = cursor.fetchall()

            # Get repo stats
            cursor = conn.execute("SELECT COUNT(*), status FROM repos_enhanced GROUP BY status")
            repos = cursor.fetchall()

            # Get module stats
            cursor = conn.execute(
                "SELECT COUNT(*), integration_type FROM vb_modules_enhanced GROUP BY integration_type"
            )
            modules = cursor.fetchall()

            print("📊 EQ12 GitHub Integration Status")
            print("=" * 50)

            print("\n🔍 Searches by category:")
            for _count, _category in searches:
                print("  {category}: {count}")

            print("\n📦 Repositories by status:")
            for _count, _status in repos:
                print("  {status}: {count}")

            print("\n⚡ Modules by type:")
            for _count, _integration_type in modules:
                print("  {integration_type}: {count}")

            if args.detailed:
                # Show recent modules
                cursor = conn.execute(
                    """
                    SELECT module_name, source_repo, integration_type, timestamp
                    FROM vb_modules_enhanced
                    ORDER BY timestamp DESC
                    LIMIT 10
                """
                )
                recent_modules = cursor.fetchall()

                print("\n🆕 Recent modules:")
                for _name, _repo, _int_type, _timestamp in recent_modules:
                    print("  {name} ({int_type}) from {repo} at {timestamp}")

    except Exception:
        print("❌ Error reading status: {e}")


if __name__ == "__main__":
    main()
