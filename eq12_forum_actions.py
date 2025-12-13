#!/usr/bin/env python3
"""
EQ12 Forum Action System
Creates GitHub issues and improvements based on forum intelligence.

Usage:
    python eq12_forum_actions.py --create-issues --dry-run
    python eq12_forum_actions.py --update-roadmap
"""

import argparse
import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/forum_actions.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class ActionableIssue:
    """Represents a GitHub issue to be created"""

    title: str
    body: str
    labels: list[str]
    priority: str
    source_signals: list[dict]
    estimated_effort: str


class EQ12ForumActions:
    """Converts forum intelligence into GitHub issues and roadmap updates"""

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "yourusername")
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "EQ12")

        if not self.github_token:
            logger.warning("GITHUB_TOKEN not found. Issue creation will be disabled.")

        self.github_headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "EQ12-Actions/1.0",
        }

        self.cache_dir = Path("C:/EQ12/data/forum_cache")
        self.issues_file = self.cache_dir / "generated_issues.jsonl"

        # Issue templates by signal type
        self.issue_templates = {
            "MIGRATE_RESPONSES": {
                "title_template": "🔄 Migrate to OpenAI Responses API",
                "labels": ["enhancement", "api-migration", "priority-high"],
                "body_template": """
## Context
Forum intelligence indicates the OpenAI Responses API is becoming
preferred over Chat Completions.

## Proposed Changes
- [ ] Update `eq12_opsbot/` to use client.responses.create()
- [ ] Migrate existing chat completions endpoints
- [ ] Update documentation and examples
- [ ] Add backward compatibility layer

## Benefits
- Better alignment with OpenAI's recommended patterns
- Improved response handling and debugging
- Future-proof API integration

## Source Intelligence
{source_details}

## Estimated Effort
**Medium** (2-4 hours) - API endpoint changes with testing

---
*Auto-generated from EQ12 Forum Intelligence System*
""",
                "priority": "high",
            },
            "MODEL_UPDATES": {
                "title_template": "🤖 Update Model Preferences and Cost Calculations",
                "labels": ["models", "cost-optimization", "priority-medium"],
                "body_template": """
## Context
New OpenAI models detected in community discussions: GPT-4o, GPT-4o-mini, o1-preview.

## Proposed Changes
- [ ] Update model cost calculations in budget guards
- [ ] Test new models for EQ12 use cases (betting analysis, automation)
- [ ] Update model selection logic for different tasks
- [ ] Benchmark performance vs. cost trade-offs

## Models to Evaluate
- **GPT-4o**: Potentially better reasoning for sports analysis
- **GPT-4o-mini**: Cost-effective option for simple tasks
- **o1-preview**: Advanced reasoning for complex betting correlations

## Source Intelligence
{source_details}

## Estimated Effort
**Small** (1-2 hours) - Configuration updates and testing

---
*Auto-generated from EQ12 Forum Intelligence System*
""",
                "priority": "medium",
            },
            "RATE_LIMITING": {
                "title_template": "⚡ Improve Rate Limiting and Backoff Strategies",
                "labels": ["rate-limiting", "reliability", "priority-high"],
                "body_template": """
## Context
Community reports suggest enhanced rate limiting patterns for production workloads.

## Proposed Changes
- [ ] Implement exponential backoff with jitter
- [ ] Add circuit breaker patterns for failed API calls
- [ ] Monitor TPM/RPM usage with alerts
- [ ] Create rate limit recovery strategies

## EQ12 Integration Points
- Webhook processing in `eq12_opsbot/webhook_server.py`
- Betting analysis API calls
- Bulk forum post generation

## Source Intelligence
{source_details}

## Estimated Effort
**Medium** (3-5 hours) - Core infrastructure changes

---
*Auto-generated from EQ12 Forum Intelligence System*
""",
                "priority": "high",
            },
            "SPORTS_DATA": {
                "title_template": "🏈 Enhance Sports Betting API Integration",
                "labels": ["sports-betting", "api-integration", "priority-medium"],
                "body_template": """
## Context
Forum discussions highlight new patterns for sports betting API integration.

## Proposed Changes
- [ ] Research new sports data providers and APIs
- [ ] Implement real-time odds monitoring
- [ ] Add correlation analysis between multiple sources
- [ ] Build automated arbitrage detection

## EQ12 Enhancement Areas
- NFL Week 6 analysis automation
- Bills mega-parlay optimization ($5 → $1000+)
- Live betting data pipelines

## Source Intelligence
{source_details}

## Estimated Effort
**Large** (6-10 hours) - New data pipeline development

---
*Auto-generated from EQ12 Forum Intelligence System*
""",
                "priority": "medium",
            },
            "COST_OPTIMIZATION": {
                "title_template": "💰 Implement Advanced Cost Optimization",
                "labels": ["cost-optimization", "efficiency", "priority-medium"],
                "body_template": """
## Context
Community shares new approaches to OpenAI API cost management and token optimization.

## Proposed Changes
- [ ] Implement token usage analytics and reporting
- [ ] Add batch API processing for bulk operations
- [ ] Optimize prompt engineering for token efficiency
- [ ] Create cost alerts and budget guards

## EQ12 Cost Centers
- Forum post generation (100 posts = significant token usage)
- Betting analysis and correlation processing
- Automated issue creation from intelligence

## Source Intelligence
{source_details}

## Estimated Effort
**Medium** (4-6 hours) - Monitoring and optimization systems

---
*Auto-generated from EQ12 Forum Intelligence System*
""",
                "priority": "medium",
            },
        }

    def load_latest_intelligence(self) -> dict[str, Any] | None:
        """Load the most recent forum intelligence report"""
        try:
            intelligence_files = list(self.cache_dir.glob("intelligence_report_*.md"))
            if not intelligence_files:
                logger.warning("No intelligence reports found")
                return None

            # Also check for JSON analysis files
            json_files = list(self.cache_dir.glob("analysis_*.json"))
            if json_files:
                latest_json = max(json_files, key=os.path.getmtime)
                with latest_json.open("r", encoding="utf-8") as f:
                    return json.load(f)

            # Fallback to parsing cached topics
            topics_file = self.cache_dir / "topics.jsonl"
            if topics_file.exists():
                topics = []
                with topics_file.open("r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            topics.append(json.loads(line))

                # Return recent topics (last 50)
                return {
                    "signal_summary": {},
                    "raw_signals": [],
                    "topics": topics[-50:] if len(topics) > 50 else topics,
                }

            return None

        except Exception as e:
            logger.error(f"Error loading intelligence: {e}")
            return None

    def generate_actionable_issues(self, intelligence: dict[str, Any]) -> list[ActionableIssue]:
        """Convert intelligence signals into GitHub issues"""
        issues = []

        signal_summary = intelligence.get("signal_summary", {})
        raw_signals = intelligence.get("raw_signals", [])

        for signal_tag, _signal_data in signal_summary.items():
            if signal_tag not in self.issue_templates:
                logger.info(f"No template for signal type: {signal_tag}")
                continue

            template = self.issue_templates[signal_tag]

            # Filter raw signals for this tag
            tag_signals = [s for s in raw_signals if s.get("tag") == signal_tag]

            # Build source details
            source_details = []
            for signal in tag_signals[:5]:  # Limit to top 5 examples
                source_details.append(
                    f"- **{signal.get('source_title', 'Unknown')}** "
                    f"(Confidence: {signal.get('confidence', 0):.1f}%)"
                )
                if signal.get("source_url"):
                    source_details[-1] += f" - [Link]({signal['source_url']})"

            source_text = (
                "\n".join(source_details) if source_details else "No specific sources available"
            )

            # Create issue
            issue = ActionableIssue(
                title=template["title_template"],
                body=template["body_template"].format(source_details=source_text),
                labels=template["labels"],
                priority=template["priority"],
                source_signals=tag_signals,
                estimated_effort=template.get("estimated_effort", "Unknown"),
            )

            issues.append(issue)

        # Sort by priority and signal strength
        priority_order = {"high": 3, "medium": 2, "low": 1}
        issues.sort(
            key=lambda x: (priority_order.get(x.priority, 0), len(x.source_signals)), reverse=True
        )

        return issues

    def create_github_issue(self, issue: ActionableIssue, dry_run: bool = True) -> str | None:
        """Create a GitHub issue (or simulate if dry_run=True)"""

        if not self.github_token:
            logger.warning("Cannot create issue: GITHUB_TOKEN not configured")
            return None

        issue_data = {"title": issue.title, "body": issue.body, "labels": issue.labels}

        if dry_run:
            logger.info(f"[DRY RUN] Would create issue: {issue.title}")
            logger.info(f"Labels: {', '.join(issue.labels)}")
            logger.info(f"Priority: {issue.priority}")
            return f"dry-run-{hash(issue.title)}"

        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues"
            response = requests.post(url, headers=self.github_headers, json=issue_data)
            response.raise_for_status()

            issue_url = response.json().get("html_url", "")
            logger.info(f"Created issue: {issue.title} - {issue_url}")

            # Log the created issue
            with self.issues_file.open("a", encoding="utf-8") as f:
                log_entry = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "title": issue.title,
                    "url": issue_url,
                    "labels": issue.labels,
                    "priority": issue.priority,
                    "source_signals_count": len(issue.source_signals),
                }
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            return issue_url

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create issue '{issue.title}': {e}")
            return None

    def run_issue_creation(self, dry_run: bool = True, max_issues: int = 5) -> dict[str, Any]:
        """Main workflow: Load intelligence and create issues"""
        logger.info("Starting automated issue creation...")

        # Load intelligence
        intelligence = self.load_latest_intelligence()
        if not intelligence:
            return {"error": "No intelligence data available"}

        # Generate issues
        issues = self.generate_actionable_issues(intelligence)
        if not issues:
            return {
                "message": "No actionable issues found",
                "intelligence_signals": len(intelligence.get("signal_summary", {})),
            }

        # Create issues (limited)
        created_issues = []
        for issue in issues[:max_issues]:
            issue_url = self.create_github_issue(issue, dry_run=dry_run)
            if issue_url:
                created_issues.append(
                    {
                        "title": issue.title,
                        "url": issue_url,
                        "priority": issue.priority,
                        "labels": issue.labels,
                    }
                )

        result = {
            "timestamp": datetime.now(UTC).isoformat(),
            "intelligence_loaded": True,
            "total_signals": len(intelligence.get("signal_summary", {})),
            "actionable_issues_generated": len(issues),
            "issues_created": len(created_issues),
            "dry_run": dry_run,
            "created_issues": created_issues,
        }

        # Save results
        results_file = (
            self.cache_dir / f"issue_creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with results_file.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Issue creation complete. Results saved to {results_file}")
        return result


def main():
    parser = argparse.ArgumentParser(description="EQ12 Forum Action System")
    parser.add_argument(
        "--create-issues", action="store_true", help="Create GitHub issues from intelligence"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Simulate issue creation without actually creating",
    )
    parser.add_argument(
        "--max-issues", type=int, default=5, help="Maximum number of issues to create"
    )

    args = parser.parse_args()

    actions = EQ12ForumActions()

    if args.create_issues:
        result = actions.run_issue_creation(dry_run=args.dry_run, max_issues=args.max_issues)
        print(json.dumps(result, indent=2))
    else:
        print("Use --create-issues to generate GitHub issues from forum intelligence")


if __name__ == "__main__":
    main()
