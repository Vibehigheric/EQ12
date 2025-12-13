#!/usr/bin/env python3
"""
EQ12 GitHub Integration Module
Automated Issue creation, PR enhancement, and cross-stack intelligence sharing via GitHub API.

Author: EQ12 AI Assistant
Created: 2025-09-27
"""

import argparse
import logging
import os
import sqlite3
import sys
from datetime import UTC, datetime

# GitHub API integration
try:
    from github import Github

    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    print("⚠️ PyGithub not installed. Run: pip install PyGithub")

# Database configuration
DB_PATH = os.getenv("META_DB_PATH", "meta_search.sqlite3")

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_ORG = os.getenv("GITHUB_ORG", "EQ12-Intelligence")
GITHUB_REPO_PREFIX = "eq12"

# Stack configuration mapping
STACK_CONFIG = {
    "betting": {
        "repo": "eq12-betting-intelligence",
        "telegram_channel": "#betting-sharp-alerts",
        "labels": ["betting", "sports", "auto-generated"],
        "priority_keywords": ["injury", "suspension", "sharp", "line movement", "edge"],
        "queries": ["NFL injuries", "NBA suspensions", "betting news", "sharp money"],
    },
    "travel": {
        "repo": "eq12-travel-intelligence",
        "telegram_channel": "#travel-deal-alerts",
        "labels": ["travel", "deals", "affiliate"],
        "priority_keywords": ["flight deal", "hotel promotion", "cashback", "booking"],
        "queries": [
            "cheap flights",
            "hotel deals",
            "travel restrictions",
            "destination trends",
        ],
    },
    "cannabis": {
        "repo": "eq12-cannabis-intelligence",
        "telegram_channel": "#cannabis-ny-updates",
        "labels": ["cannabis", "regulation", "new-york"],
        "priority_keywords": [
            "license",
            "dispensary",
            "regulation",
            "buffalo",
            "ny cannabis",
        ],
        "queries": [
            "NY cannabis license",
            "Buffalo marijuana",
            "CBD legal",
            "dispensary opening",
        ],
    },
    "fleet": {
        "repo": "eq12-fleet-intelligence",
        "telegram_channel": "#fleet-ops-alerts",
        "labels": ["fleet", "automotive", "operations"],
        "priority_keywords": [
            "recall",
            "insurance",
            "turo",
            "vehicle demand",
            "safety",
        ],
        "queries": [
            "vehicle recalls",
            "car insurance",
            "Turo earnings",
            "fleet management",
        ],
    },
    "housing": {
        "repo": "eq12-housing-intelligence",
        "telegram_channel": "#housing-finance-alerts",
        "labels": ["housing", "credit", "finance"],
        "priority_keywords": [
            "mortgage rate",
            "credit score",
            "housing market",
            "fha loan",
        ],
        "queries": [
            "Buffalo housing market",
            "mortgage rates",
            "FHA requirements",
            "credit improvement",
        ],
    },
    "education": {
        "repo": "eq12-education-intelligence",
        "telegram_channel": "#education-grant-alerts",
        "labels": ["education", "grants", "licensing"],
        "priority_keywords": [
            "suny",
            "excelsior",
            "grant deadline",
            "license requirement",
        ],
        "queries": [
            "SUNY programs",
            "education grants",
            "NY licensing",
            "Excelsior updates",
        ],
    },
    "dropship": {
        "repo": "eq12-dropship-intelligence",
        "telegram_channel": "#dropship-trend-alerts",
        "labels": ["ecommerce", "dropship", "seo"],
        "priority_keywords": [
            "trending product",
            "keyword trend",
            "conversion rate",
            "seo",
        ],
        "queries": [
            "dropshipping trends",
            "product keywords",
            "ecommerce seo",
            "ali express",
        ],
    },
}

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EQ12GitHubIntegration:
    """GitHub API integration for EQ12 intelligence automation"""

    def __init__(self):
        if not GITHUB_AVAILABLE:
            raise ImportError("PyGithub library required. Install with: pip install PyGithub")

        if not GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN environment variable required")

        self.github = Github(GITHUB_TOKEN)
        self.org_name = GITHUB_ORG

        try:
            self.org = self.github.get_organization(self.org_name)
            logger.info(f"Connected to GitHub organization: {self.org_name}")
        except:
            # Fallback to user repositories if org doesn't exist
            self.org = None
            logger.warning(f"Organization {self.org_name} not found, using user repositories")

    def get_repository(self, stack: str) -> object:
        """Get GitHub repository for specific stack"""
        repo_name = STACK_CONFIG[stack]["repo"]

        try:
            if self.org:
                return self.org.get_repo(repo_name)
            return self.github.get_user().get_repo(repo_name)
        except:
            logger.error(f"Repository {repo_name} not found for stack {stack}")
            return None

    def create_intelligence_issue(
        self,
        stack: str,
        title: str,
        analysis: str,
        priority: str = "medium",
        data_sources: list[str] | None = None,
    ) -> bool:
        """Create GitHub Issue for high-priority intelligence alerts"""

        if stack not in STACK_CONFIG:
            logger.error(f"Unknown stack: {stack}")
            return False

        repo = self.get_repository(stack)
        if not repo:
            return False

        config = STACK_CONFIG[stack]
        labels = config["labels"] + [f"priority-{priority}", "intelligence-alert"]

        # Format issue body
        issue_body = f"""
## 🤖 Automated Intelligence Alert

**Stack:** {stack.title()}
**Priority:** {priority.upper()}
**Generated:** {datetime.now(UTC).isoformat()}
**Telegram Channel:** {config["telegram_channel"]}

### 🧠 Analysis Summary
{analysis}

### 📊 Data Sources
{chr(10).join([f"- {source}" for source in (data_sources or ["News Aggregation", "Meta Search", "Offers Analysis"])])}

### 🎯 Recommended Actions
- [ ] Review analysis for accuracy and relevance
- [ ] Implement suggested actions if applicable
- [ ] Update relevant stack configurations
- [ ] Cross-reference with other stack intelligence
- [ ] Close issue when resolved or dismissed

### 🔗 Related Intelligence
*This alert may be relevant to other EQ12 stacks. Check cross-stack repository issues.*

---
*🤖 This issue was automatically generated by EQ12 GODSTACK Intelligence System*
*⏰ Generated at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}*
        """

        try:
            issue = repo.create_issue(
                title=f"[{stack.upper()}] {title}",
                body=issue_body,
                labels=[l for l in labels if l],  # Filter out any None labels
            )

            logger.info(f"Created GitHub issue #{issue.number} for {stack}: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to create GitHub issue for {stack}: {e}")
            return False

    def create_enrichment_pr_comment(
        self, repo_name: str, pr_number: int, enrichment_data: dict, stack: str | None = None
    ) -> bool:
        """Add enrichment analysis as PR review comment"""

        try:
            if self.org:
                repo = self.org.get_repo(repo_name)
            else:
                repo = self.github.get_user().get_repo(repo_name)

            pr = repo.get_pull(pr_number)

            comment_body = f"""
## 🧠 EQ12 Intelligence Analysis

**Stack Context:** {stack.title() if stack else "Cross-Stack"}
**Analysis Timestamp:** {datetime.now().isoformat()}

### 📈 Market Intelligence
{enrichment_data.get("market_intel", "No market intelligence available")}

### 🎯 Strategic Insights
{enrichment_data.get("analysis", "No strategic analysis available")}

### 💡 Recommended Considerations
{enrichment_data.get("recommendations", "No specific recommendations available")}

### 🔄 Cross-Stack Implications
{enrichment_data.get("cross_stack_impact", "No cross-stack analysis performed")}

---
*🤖 Analysis provided by EQ12 GODSTACK Intelligence System*
*📊 Data sources: News aggregation, meta search, offers analysis*
            """

            pr.create_issue_comment(comment_body)
            logger.info(f"Added enrichment comment to PR #{pr_number} in {repo_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add PR comment to {repo_name}#{pr_number}: {e}")
            return False

    def sync_cross_stack_intelligence(self, intelligence_summary: dict) -> list[str]:
        """Share relevant intelligence across stack repositories"""

        created_issues = []

        for stack, data in intelligence_summary.items():
            if stack not in STACK_CONFIG:
                continue

            # Determine if intelligence is significant enough for cross-stack sharing
            confidence = data.get("confidence", 0)
            cross_stack_relevance = data.get("cross_stack_relevance", 0)

            if confidence > 0.7 and cross_stack_relevance > 0.5:
                title = f"Cross-Stack Intelligence: {data.get('title', 'Intelligence Update')}"
                analysis = data.get("analysis", "No analysis available")

                if self.create_intelligence_issue(
                    stack=stack,
                    title=title,
                    analysis=analysis,
                    priority="medium",
                    data_sources=data.get("sources", []),
                ):
                    created_issues.append(f"{stack}#{title}")

        return created_issues

    def get_recent_intelligence_from_db(self, hours: int = 24, stack: str | None = None) -> dict:
        """Fetch recent enriched intelligence from database"""

        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row

            # Query for recent results with potential stack filtering
            if stack:
                stack_keywords = STACK_CONFIG.get(stack, {}).get("priority_keywords", [])
                keyword_filter = " OR ".join(
                    [f"title LIKE '%{kw}%' OR snippet LIKE '%{kw}%'" for kw in stack_keywords]
                )
                query = f"""
                SELECT query, title, snippet, url, source, fetched_at
                FROM results
                WHERE ({keyword_filter})
                AND fetched_at > datetime('now', '-{hours} hours')
                ORDER BY fetched_at DESC
                LIMIT 50
                """
            else:
                query = f"""
                SELECT query, title, snippet, url, source, fetched_at
                FROM results
                WHERE fetched_at > datetime('now', '-{hours} hours')
                ORDER BY fetched_at DESC
                LIMIT 100
                """

            cursor = conn.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return {
                "results": results,
                "total_count": len(results),
                "timeframe_hours": hours,
                "stack_filter": stack,
            }

        except Exception as e:
            logger.error(f"Database query failed: {e}")
            return {"results": [], "total_count": 0, "error": str(e)}


def create_stack_queries_file(stack: str, output_dir: str = ".") -> str:
    """Create stack-specific queries file for automated collection"""

    if stack not in STACK_CONFIG:
        raise ValueError(f"Unknown stack: {stack}")

    config = STACK_CONFIG[stack]
    queries = config["queries"]

    filename = f"queries_{stack}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w") as f:
        f.write(f"# EQ12 {stack.title()} Stack Queries\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Telegram: {config['telegram_channel']}\n\n")

        for query in queries:
            f.write(f"{query}\n")

    logger.info(f"Created {stack} queries file: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="EQ12 GitHub Integration")
    parser.add_argument(
        "--stack",
        choices=[*list(STACK_CONFIG.keys()), "all"],
        help="Target business stack",
    )
    parser.add_argument(
        "--create-issue",
        action="store_true",
        help="Create GitHub issues from recent intelligence",
    )
    parser.add_argument(
        "--sync-cross-stack",
        action="store_true",
        help="Sync intelligence across all stack repositories",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours of recent data to analyze (default: 24)",
    )
    parser.add_argument(
        "--generate-queries",
        action="store_true",
        help="Generate stack-specific query files",
    )
    parser.add_argument("--test-connection", action="store_true", help="Test GitHub API connection")

    args = parser.parse_args()

    try:
        integration = EQ12GitHubIntegration()

        if args.test_connection:
            logger.info("✅ GitHub API connection successful")
            logger.info(f"Organization: {integration.org_name}")
            return 0

        if args.generate_queries:
            stacks = [args.stack] if args.stack != "all" else list(STACK_CONFIG.keys())
            for stack in stacks:
                create_stack_queries_file(stack)
            return 0

        if args.create_issue and args.stack and args.stack != "all":
            # Get recent intelligence for specific stack
            intel_data = integration.get_recent_intelligence_from_db(args.hours, args.stack)

            if intel_data["total_count"] > 0:
                # Create summary of findings
                summary = f"Found {intel_data['total_count']} intelligence items in the last {args.hours} hours"

                integration.create_intelligence_issue(
                    stack=args.stack,
                    title=f"Recent Intelligence Summary ({args.hours}h)",
                    analysis=summary,
                    priority="medium",
                    data_sources=["Automated Collection"],
                )
            else:
                logger.info(f"No recent intelligence found for {args.stack} stack")

        if args.sync_cross_stack:
            # Analyze intelligence for all stacks
            all_intelligence = {}

            for stack in STACK_CONFIG:
                intel_data = integration.get_recent_intelligence_from_db(args.hours, stack)
                if intel_data["total_count"] > 0:
                    all_intelligence[stack] = {
                        "title": f"Intelligence Update - {intel_data['total_count']} items",
                        "analysis": f"Recent intelligence collection yielded {intel_data['total_count']} relevant items",
                        "confidence": 0.8,  # Static for now, could be enhanced with ML
                        "cross_stack_relevance": 0.6,
                        "sources": [
                            "News Aggregation",
                            "Meta Search",
                            "Offers Analysis",
                        ],
                    }

            created = integration.sync_cross_stack_intelligence(all_intelligence)
            logger.info(f"Created {len(created)} cross-stack intelligence issues")

    except Exception as e:
        logger.error(f"GitHub integration error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
