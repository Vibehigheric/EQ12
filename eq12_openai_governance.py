#!/usr/bin/env python3
"""
EQ12 GODSTACK - OpenAI Governance Integration
Advanced AI-powered governance automation using OpenAI's Responses API
for intelligent Chrome automation, security analysis, and compliance monitoring.

Features:
- OpenAI Responses API integration with conversation management
- AI-powered bookmark intelligence and URL analysis
- Governance task automation with conversational AI
- Daily governance reports with AI insights
- Security audit recommendations and compliance checks

Author: EQ12 GODSTACK Team
Version: 1.0.0
License: MIT
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiohttp


@dataclass
class EQ12GovernancePrompt:
    """Structured prompts for governance tasks."""

    task_type: str
    system_message: str
    context: dict[str, Any]
    metadata: dict[str, str]


@dataclass
class GovernanceInsight:
    """AI-generated governance insights."""

    insight_type: str
    title: str
    description: str
    severity: str  # low, medium, high, critical
    recommendations: list[str]
    confidence: float
    timestamp: datetime


class EQ12OpenAIClient:
    """Enhanced OpenAI client for EQ12 governance operations."""

    def __init__(self, api_key: str | None = None, eq12_root: str | None = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.eq12_root = Path(
            eq12_root
            or os.getenv("EQ12_ROOT", "C:/EQ12" if os.name == "nt" else "/workspaces/EQ12")
        )
        self.logs_dir = self.eq12_root / "logs"
        self.reports_dir = self.eq12_root / "reports"

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        self.logger = self._setup_logging()

        # Active conversations for stateful interactions
        self.conversations: dict[str, str] = {}  # task_type -> conversation_id

        # Governance-specific models and prompts
        self.governance_models = {
            "analysis": "gpt-4o",  # For deep analysis
            "monitoring": "gpt-4o-mini",  # For quick checks
            "reporting": "gpt-4o",  # For comprehensive reports
            "security": "gpt-4o",  # For security analysis
        }

    def _setup_logging(self) -> logging.Logger:
        """Configure comprehensive logging for AI operations."""
        log_file = self.logs_dir / f"eq12_openai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        logger = logging.getLogger(__name__)
        logger.info("EQ12 OpenAI Governance Client initialized")
        logger.info(f"API Key configured: {'✓' if self.api_key else '✗'}")
        logger.info(f"EQ12 Root: {self.eq12_root}")

        return logger

    async def create_governance_conversation(self, task_type: str, context: dict[str, Any]) -> str:
        """Create a new governance conversation with context."""
        try:
            payload = {
                "metadata": {
                    "task_type": task_type,
                    "eq12_context": "governance_automation",
                    "created_by": "eq12_godstack",
                    "session": datetime.now().isoformat(),
                },
                "items": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": f"EQ12 GODSTACK Governance Context:\nTask Type: {task_type}\nContext: {json.dumps(context, indent=2)}\n\nReady for governance analysis and recommendations.",
                    }
                ],
            }

            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    f"{self.base_url}/conversations", headers=self.headers, json=payload
                ) as response,
            ):
                if response.status == 200:
                    result = await response.json()
                    conversation_id = result["id"]
                    self.conversations[task_type] = conversation_id

                    self.logger.info(
                        f"✅ Created governance conversation: {conversation_id} for {task_type}"
                    )
                    return conversation_id
                error_text = await response.text()
                self.logger.error(f"❌ Failed to create conversation: {error_text}")
                raise Exception(f"Conversation creation failed: {error_text}")

        except Exception as e:
            self.logger.error(f"❌ Error creating conversation: {e}")
            raise

    def create_governance_prompt(
        self, task_type: str, data: dict[str, Any]
    ) -> EQ12GovernancePrompt:
        """Generate governance-specific prompts based on task type."""

        governance_prompts = {
            "chrome_bookmarks": EQ12GovernancePrompt(
                task_type="chrome_bookmarks",
                system_message="""You are an EQ12 GODSTACK governance analyst specializing in Chrome bookmark intelligence and URL analysis.

                Your role is to:
                1. Analyze Chrome governance bookmarks for security, relevance, and optimization
                2. Suggest intelligent bookmark categorization and URL improvements
                3. Identify potential security risks in bookmarked URLs
                4. Recommend governance workflow optimizations
                5. Generate bookmark refresh strategies with dynamic URL management

                Provide actionable insights in JSON format with recommendations, priority levels, and implementation steps.""",
                context=data,
                metadata={"domain": "browser_governance", "priority": "high"},
            ),
            "security_audit": EQ12GovernancePrompt(
                task_type="security_audit",
                system_message="""You are an EQ12 GODSTACK security analyst with expertise in governance security auditing.

                Your responsibilities:
                1. Analyze system security configurations and browser profiles
                2. Identify potential vulnerabilities in governance workflows
                3. Recommend security hardening measures for EQ12 stack
                4. Assess compliance with security best practices
                5. Generate actionable security improvement plans

                Focus on practical, implementable security enhancements with risk assessments.""",
                context=data,
                metadata={"domain": "security_governance", "priority": "critical"},
            ),
            "daily_governance": EQ12GovernancePrompt(
                task_type="daily_governance",
                system_message="""You are an EQ12 GODSTACK daily governance coordinator with comprehensive system oversight.

                Your daily tasks:
                1. Analyze daily governance automation execution results
                2. Review Chrome and Firefox browser governance status
                3. Assess GitHub Actions, Grafana dashboards, and system metrics
                4. Identify governance workflow improvements and optimizations
                5. Generate executive summary reports with actionable recommendations

                Provide structured governance insights with priority rankings and next steps.""",
                context=data,
                metadata={"domain": "daily_operations", "priority": "medium"},
            ),
            "compliance_check": EQ12GovernancePrompt(
                task_type="compliance_check",
                system_message="""You are an EQ12 GODSTACK compliance analyst ensuring governance standards adherence.

                Your compliance focus:
                1. Verify EQ12 governance processes meet established standards
                2. Check browser security configurations and extension compliance
                3. Audit automation task execution and logging compliance
                4. Assess documentation and audit trail completeness
                5. Recommend compliance improvements and corrective actions

                Deliver compliance status reports with clear pass/fail assessments and remediation steps.""",
                context=data,
                metadata={"domain": "compliance_governance", "priority": "high"},
            ),
        }

        return governance_prompts.get(
            task_type,
            EQ12GovernancePrompt(
                task_type="general",
                system_message="You are an EQ12 GODSTACK general governance assistant. Analyze the provided data and give structured recommendations.",
                context=data,
                metadata={"domain": "general_governance", "priority": "medium"},
            ),
        )

    async def analyze_governance_data(
        self, task_type: str, data: dict[str, Any], conversation_id: str | None = None
    ) -> GovernanceInsight:
        """Analyze governance data using OpenAI Responses API."""
        try:
            prompt = self.create_governance_prompt(task_type, data)
            model = self.governance_models.get(task_type.split("_")[0], "gpt-4o-mini")

            # Prepare the response request
            payload = {
                "model": model,
                "instructions": prompt.system_message,
                "input": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": f"EQ12 Governance Analysis Request:\n\nTask: {task_type}\n\nData to analyze:\n{json.dumps(data, indent=2, default=str)}\n\nPlease provide a comprehensive governance analysis with actionable recommendations in JSON format.",
                    }
                ],
                "text": {"format": {"type": "json_object"}},
                "temperature": 0.3,  # Lower temperature for consistent governance analysis
                "max_output_tokens": 2000,
                "metadata": {
                    "eq12_task": task_type,
                    "analysis_type": "governance",
                    "timestamp": datetime.now().isoformat(),
                },
            }

            # Use existing conversation if provided
            if conversation_id:
                payload["conversation"] = conversation_id

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/responses", headers=self.headers, json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()

                        # Extract the AI response text
                        output_text = ""
                        if result["output"] and len(result["output"]) > 0:
                            content = result["output"][0].get("content", [])
                            if content and len(content) > 0:
                                output_text = content[0].get("text", "")

                        # Parse AI response as JSON
                        try:
                            ai_analysis = json.loads(output_text)
                        except json.JSONDecodeError:
                            # Fallback if JSON parsing fails
                            ai_analysis = {
                                "title": f"Governance Analysis - {task_type}",
                                "description": output_text[:500] + "...",
                                "severity": "medium",
                                "recommendations": ["Review the full analysis output"],
                                "confidence": 0.7,
                            }

                        # Create structured insight
                        insight = GovernanceInsight(
                            insight_type=task_type,
                            title=ai_analysis.get("title", f"Governance Analysis - {task_type}"),
                            description=ai_analysis.get(
                                "description", "AI governance analysis completed"
                            ),
                            severity=ai_analysis.get("severity", "medium"),
                            recommendations=ai_analysis.get("recommendations", []),
                            confidence=ai_analysis.get("confidence", 0.8),
                            timestamp=datetime.now(UTC),
                        )

                        # Save analysis to file
                        analysis_file = (
                            self.reports_dir
                            / f"governance_analysis_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        )
                        with open(analysis_file, "w", encoding="utf-8") as f:
                            json.dump(
                                {
                                    "insight": asdict(insight),
                                    "full_response": result,
                                    "input_data": data,
                                },
                                f,
                                indent=2,
                                default=str,
                            )

                        self.logger.info(f"✅ Governance analysis completed: {insight.title}")
                        self.logger.info(f"📊 Analysis saved: {analysis_file}")

                        return insight

                    error_text = await response.text()
                    self.logger.error(f"❌ API request failed: {error_text}")
                    raise Exception(f"OpenAI API error: {error_text}")

        except Exception as e:
            self.logger.error(f"❌ Governance analysis failed: {e}")
            raise

    def analyze_chrome_bookmarks_sync(self, bookmarks_data: dict[str, Any]) -> GovernanceInsight:
        """Synchronous wrapper for Chrome bookmarks analysis."""
        return asyncio.run(self.analyze_governance_data("chrome_bookmarks", bookmarks_data))

    def generate_daily_governance_report_sync(
        self, system_data: dict[str, Any]
    ) -> GovernanceInsight:
        """Synchronous wrapper for daily governance report generation."""
        return asyncio.run(self.analyze_governance_data("daily_governance", system_data))

    def perform_security_audit_sync(self, security_data: dict[str, Any]) -> GovernanceInsight:
        """Synchronous wrapper for security audit analysis."""
        return asyncio.run(self.analyze_governance_data("security_audit", security_data))


class EQ12GovernanceAI:
    """High-level governance AI coordination class."""

    def __init__(self, openai_client: EQ12OpenAIClient):
        self.client = openai_client
        self.logger = openai_client.logger

    def analyze_chrome_governance_data(
        self, chrome_profile_path: str, bookmarks_file: str
    ) -> dict[str, Any]:
        """Analyze Chrome governance profile and bookmarks for AI insights."""
        try:
            governance_data = {
                "chrome_profile": chrome_profile_path,
                "timestamp": datetime.now().isoformat(),
                "bookmarks": {},
                "profile_stats": {},
                "security_config": {},
            }

            # Load and analyze bookmarks
            bookmarks_path = Path(bookmarks_file)
            if bookmarks_path.exists():
                with open(bookmarks_path, encoding="utf-8") as f:
                    bookmarks_data = json.load(f)
                governance_data["bookmarks"] = bookmarks_data

                # Extract bookmark statistics
                bookmark_count = 0

                def count_bookmarks(node):
                    nonlocal bookmark_count
                    if isinstance(node, dict):
                        if node.get("type") == "url":
                            bookmark_count += 1
                        elif "children" in node:
                            for child in node["children"]:
                                count_bookmarks(child)

                count_bookmarks(bookmarks_data)
                governance_data["profile_stats"]["total_bookmarks"] = bookmark_count

            # Profile directory analysis
            profile_path = Path(chrome_profile_path)
            if profile_path.exists():
                governance_data["profile_stats"]["profile_exists"] = True
                governance_data["profile_stats"]["profile_size_mb"] = sum(
                    f.stat().st_size for f in profile_path.rglob("*") if f.is_file()
                ) / (1024 * 1024)
            else:
                governance_data["profile_stats"]["profile_exists"] = False

            self.logger.info(
                f"📊 Chrome governance data analyzed: {bookmark_count} bookmarks, {governance_data['profile_stats'].get('profile_size_mb', 0):.1f} MB profile"
            )

            return governance_data

        except Exception as e:
            self.logger.error(f"❌ Chrome governance data analysis failed: {e}")
            return {}

    def generate_governance_summary(self) -> dict[str, Any]:
        """Generate comprehensive governance summary for AI analysis."""
        try:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "eq12_root": str(self.client.eq12_root),
                "system_health": {},
                "governance_tasks": {},
                "security_status": {},
                "recommendations": [],
            }

            # Check EQ12 directory structure
            eq12_dirs = ["logs", "reports", "scripts", "configs", "tasks"]
            for dir_name in eq12_dirs:
                dir_path = self.client.eq12_root / dir_name
                summary["system_health"][f"{dir_name}_exists"] = dir_path.exists()
                if dir_path.exists():
                    summary["system_health"][f"{dir_name}_file_count"] = len(
                        list(dir_path.glob("*"))
                    )

            # Analyze recent logs
            logs_dir = self.client.logs_dir
            if logs_dir.exists():
                log_files = list(logs_dir.glob("*.log"))
                summary["governance_tasks"]["recent_log_files"] = len(log_files)
                summary["governance_tasks"]["latest_log"] = str(
                    max(log_files, key=lambda x: x.stat().st_mtime, default="none")
                )

            # Check Chrome governance files
            chrome_files = {
                "chrome_governance_automation.py": self.client.eq12_root
                / "chrome_governance_automation.py",
                "chrome_daily_task_simple.ps1": self.client.eq12_root
                / "chrome_daily_task_simple.ps1",
                "tasks_xml": self.client.eq12_root / "tasks" / "ChromeGovernanceDailyRefresh.xml",
            }

            for file_key, file_path in chrome_files.items():
                summary["governance_tasks"][f"{file_key}_exists"] = file_path.exists()
                if file_path.exists():
                    summary["governance_tasks"][f"{file_key}_size"] = file_path.stat().st_size

            self.logger.info("📋 Governance summary generated successfully")
            return summary

        except Exception as e:
            self.logger.error(f"❌ Governance summary generation failed: {e}")
            return {}


def main():
    """Main execution function for EQ12 OpenAI Governance Integration."""
    parser = argparse.ArgumentParser(
        description="EQ12 GODSTACK OpenAI Governance Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python eq12_openai_governance.py --analyze-chrome --verbose
  python eq12_openai_governance.py --daily-report --security-audit
  python eq12_openai_governance.py --governance-summary
        """,
    )

    parser.add_argument(
        "--analyze-chrome",
        action="store_true",
        help="Analyze Chrome governance bookmarks with AI",
    )
    parser.add_argument(
        "--daily-report",
        action="store_true",
        help="Generate AI-powered daily governance report",
    )
    parser.add_argument(
        "--security-audit",
        action="store_true",
        help="Perform AI security audit of governance systems",
    )
    parser.add_argument(
        "--governance-summary",
        action="store_true",
        help="Generate comprehensive governance summary",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize OpenAI client
        client = EQ12OpenAIClient()
        governance_ai = EQ12GovernanceAI(client)

        success = True

        if args.analyze_chrome or not any(
            [args.daily_report, args.security_audit, args.governance_summary]
        ):
            print("🤖 Analyzing Chrome governance with AI...")

            # Analyze Chrome governance data
            chrome_profile = Path.home() / "AppData/Local/Google/Chrome/User Data/EQ12Governance"
            bookmarks_file = chrome_profile / "Default/Bookmarks"

            chrome_data = governance_ai.analyze_chrome_governance_data(
                str(chrome_profile), str(bookmarks_file)
            )

            if chrome_data:
                insight = client.analyze_chrome_bookmarks_sync(chrome_data)
                print(f"✅ AI Analysis: {insight.title}")
                print(f"📊 Severity: {insight.severity}")
                print(f"🔍 Recommendations: {len(insight.recommendations)}")
                for i, rec in enumerate(insight.recommendations[:3], 1):
                    print(f"   {i}. {rec}")
            else:
                print("⚠️ Chrome governance data not available")
                success = False

        if args.daily_report:
            print("📊 Generating AI daily governance report...")

            summary_data = governance_ai.generate_governance_summary()
            if summary_data:
                insight = client.generate_daily_governance_report_sync(summary_data)
                print(f"✅ Daily Report: {insight.title}")
                print(f"🎯 Confidence: {insight.confidence:.1%}")
            else:
                print("⚠️ Unable to generate governance summary")
                success = False

        if args.security_audit:
            print("🔒 Performing AI security audit...")

            security_data = governance_ai.generate_governance_summary()
            if security_data:
                insight = client.perform_security_audit_sync(security_data)
                print(f"✅ Security Audit: {insight.title}")
                print(f"⚠️ Severity: {insight.severity}")
                if insight.severity in ["high", "critical"]:
                    print("🚨 URGENT: Review security recommendations immediately")
            else:
                print("⚠️ Security audit data unavailable")
                success = False

        if args.governance_summary:
            print("📋 Generating governance system summary...")

            summary_data = governance_ai.generate_governance_summary()
            if summary_data:
                print("✅ Governance Summary Generated")
                print(f"📁 EQ12 Root: {summary_data['eq12_root']}")
                print(
                    f"📊 System Health: {sum(1 for k, v in summary_data['system_health'].items() if k.endswith('_exists') and v)}/5 directories"
                )
                print(
                    f"🔧 Governance Tasks: {summary_data['governance_tasks'].get('recent_log_files', 0)} recent logs"
                )
            else:
                print("⚠️ Governance summary generation failed")
                success = False

        if success:
            print("\n🎉 EQ12 OpenAI Governance operations completed successfully!")
            print(f"📊 Reports saved to: {client.reports_dir}")
            print(f"📝 Logs saved to: {client.logs_dir}")
        else:
            print("\n⚠️ Some operations encountered issues. Check logs for details.")

        return 0 if success else 1

    except Exception as e:
        print(f"\n❌ EQ12 OpenAI Governance failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
