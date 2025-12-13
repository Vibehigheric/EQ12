#!/usr/bin/env python3
"""
EQ12 Copilot Content Scripts - Enhanced Code Analysis and PR Automation
Advanced content processing for Copilot integration with EQ12 workflows

Author: EQ12 AI System Enhanced
Version: 2.0.0 - Content Scripts Integration
"""

import asyncio
import json
import logging
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Add EQ12 scripts to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

try:
    from eq12_enhanced_ai import EQ12EnhancedAI

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/copilot_content.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class CommitAnalysis:
    """Enhanced commit analysis with AI insights"""

    suggested_message: str
    message_type: str  # feat, fix, docs, refactor, etc.
    scope: str
    confidence: float
    key_changes: list[str]
    impact_assessment: str
    conventional_format: str
    eq12_context: str


@dataclass
class PRAnalysis:
    """Pull request analysis and summary generation"""

    title: str
    description: str
    changes_summary: list[str]
    impact_analysis: str
    testing_suggestions: list[str]
    eq12_integration_notes: str
    breaking_changes: list[str]
    confidence: float


class EQ12CopilotContentEngine:
    """Advanced content engine for Copilot integration"""

    def __init__(self):
        self.config_dir = "C:/EQ12/configs"
        self.data_dir = "C:/EQ12/data"
        self.logs_dir = "C:/EQ12/logs"

        # Initialize AI system if available
        self.ai_system = None
        if AI_AVAILABLE:
            try:
                self.ai_system = EQ12EnhancedAI()
                logger.info("AI system initialized for enhanced content processing")
            except Exception as e:
                logger.warning(f"AI system initialization failed: {e}")

        # EQ12-specific patterns and contexts
        self.eq12_patterns = {
            "betting": [
                r"parlay|odds|bet|gambling|sportsbook",
                r"EdgeGodParlays|betting_.*\.py",
                r"odds_api|betting_engine",
            ],
            "automation": [
                r"scraper|automation|bot|workflow",
                r"eq12_.*\.py|omni_scraper",
                r"scheduler|task|cron",
            ],
            "finance": [
                r"finance|trading|crypto|portfolio",
                r"finance_.*\.py|trading_.*\.py",
                r"market|stock|investment",
            ],
            "ai": [
                r"openai|gpt|ai|ml|nlp",
                r"eq12_.*ai.*\.py|enhanced_ai",
                r"classification|model|training",
            ],
            "dashboard": [
                r"dashboard|ui|interface|web",
                r"dashboard_.*\.py|.*_dashboard\.py",
                r"html|css|js|react",
            ],
            "devops": [
                r"deploy|ci|cd|docker|k8s",
                r"\.yml|\.yaml|Dockerfile",
                r"github|workflow|action",
            ],
        }

        # Conventional commit types
        self.commit_types = {
            "feat": "New feature addition",
            "fix": "Bug fix",
            "docs": "Documentation changes",
            "style": "Code style changes",
            "refactor": "Code refactoring",
            "per": "Performance improvements",
            "test": "Test additions or updates",
            "build": "Build system changes",
            "ci": "CI/CD changes",
            "chore": "Maintenance tasks",
        }

    def analyze_git_changes(self) -> dict[str, Any]:
        """Analyze current git changes for enhanced commit message generation"""
        try:
            # Get staged changes
            staged_result = subprocess.run(
                ["git", "dif", "--cached", "--name-status"],
                capture_output=True,
                text=True,
                cwd="C:/EQ12",
            )

            # Get unstaged changes
            unstaged_result = subprocess.run(
                ["git", "dif", "--name-status"],
                capture_output=True,
                text=True,
                cwd="C:/EQ12",
            )

            # Get file content changes
            diff_result = subprocess.run(
                ["git", "dif", "--cached"],
                capture_output=True,
                text=True,
                cwd="C:/EQ12",
            )

            staged_files = self._parse_git_status(staged_result.stdout)
            unstaged_files = self._parse_git_status(unstaged_result.stdout)
            diff_content = diff_result.stdout

            return {
                "staged_files": staged_files,
                "unstaged_files": unstaged_files,
                "diff_content": diff_content,
                "has_changes": bool(staged_files or unstaged_files),
            }

        except Exception as e:
            logger.error(f"Failed to analyze git changes: {e}")
            return {"error": str(e), "has_changes": False}

    def _parse_git_status(self, status_output: str) -> list[dict[str, str]]:
        """Parse git status output into structured format"""
        files = []
        for line in status_output.strip().split("\n"):
            if not line:
                continue

            parts = line.split("\t", 1)
            if len(parts) == 2:
                status, filename = parts
                files.append(
                    {
                        "status": status,
                        "filename": filename,
                        "change_type": self._get_change_type(status),
                        "eq12_category": self._categorize_file(filename),
                    }
                )

        return files

    def _get_change_type(self, status: str) -> str:
        """Convert git status to human-readable change type"""
        type_map = {
            "A": "added",
            "M": "modified",
            "D": "deleted",
            "R": "renamed",
            "C": "copied",
            "U": "updated",
        }
        return type_map.get(status[0], "modified")

    def _categorize_file(self, filename: str) -> str:
        """Categorize file based on EQ12 patterns"""
        for category, patterns in self.eq12_patterns.items():
            for pattern in patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    return category
        return "general"

    async def generate_enhanced_commit_message(
            self, changes: dict[str, Any]) -> CommitAnalysis:
        """Generate enhanced commit message with AI analysis"""
        if not changes.get("has_changes"):
            return CommitAnalysis(
                suggested_message="No changes to commit",
                message_type="chore",
                scope="",
                confidence=0.0,
                key_changes=[],
                impact_assessment="No impact",
                conventional_format="chore: no changes",
                eq12_context="No changes detected",
            )

        try:
            # Analyze changes for patterns
            staged_files = changes.get("staged_files", [])
            categories = set(f.get("eq12_category", "general") for f in staged_files)
            change_types = set(f.get("change_type", "modified") for f in staged_files)

            # Determine primary scope and type
            primary_category = self._determine_primary_category(categories)
            commit_type = self._determine_commit_type(change_types, staged_files)

            # Generate AI-enhanced commit message if available
            if self.ai_system:
                ai_analysis = await self._generate_ai_commit_message(
                    changes, primary_category, commit_type
                )
                return ai_analysis
            # Fallback to rule-based generation
            return self._generate_rule_based_commit_message(
                changes, primary_category, commit_type)

        except Exception as e:
            logger.error(f"Failed to generate commit message: {e}")
            return CommitAnalysis(
                suggested_message="Update files",
                message_type="chore",
                scope="",
                confidence=0.3,
                key_changes=[],
                impact_assessment="Unknown",
                conventional_format="chore: update files",
                eq12_context="Error in analysis",
            )

    async def _generate_ai_commit_message(
        self, changes: dict[str, Any], category: str, commit_type: str
    ) -> CommitAnalysis:
        """Generate commit message using AI analysis"""
        try:
            staged_files = changes.get("staged_files", [])
            diff_content = changes.get("diff_content", "")[:2000]  # Limit diff size

            # Build context for AI
            files_context = "\n".join(
                [
                    f"- {f['change_type'].title()} {f['filename']} ({f['eq12_category']})"
                    for f in staged_files[:10]  # Limit to 10 files
                ]
            )

            context = """
            Analyze these git changes for an EQ12 automation system commit:

            Files Changed:
            {files_context}

            Primary Category: {category}
            Suggested Type: {commit_type}

            Diff Sample:
            {diff_content}

            Generate a commit message following these requirements:
            1. Use conventional commit format: type(scope): description
            2. Focus on EQ12 system context (betting, automation, finance, AI, dashboard)
            3. Be concise but descriptive
            4. Indicate business impact if significant

            Respond with JSON:
            {{
                "message": "conventional commit message",
                "type": "commit type",
                "scope": "scope area",
                "description": "detailed description",
                "key_changes": ["change1", "change2"],
                "impact": "business impact assessment",
                "confidence": 0.0-1.0
            }}
            """

            result = await self.ai_system.enhanced_classify_content(
                content=context, url="", context="Commit message generation"
            )

            # Parse AI response (simplified for demo)
            message_parts = result.reasoning.split("\n")
            suggested_message = next(
                (line for line in message_parts if ":" in line),
                f"{commit_type}({category}): update files",
            )

            return CommitAnalysis(
                suggested_message=suggested_message,
                message_type=commit_type,
                scope=category,
                confidence=result.confidence,
                key_changes=result.key_features,
                impact_assessment=result.reasoning[:200],
                conventional_format=suggested_message,
                eq12_context=f"EQ12 {category} system changes",
            )

        except Exception as e:
            logger.error(f"AI commit message generation failed: {e}")
            return self._generate_rule_based_commit_message(
                changes, category, commit_type)

    def _generate_rule_based_commit_message(
        self, changes: dict[str, Any], category: str, commit_type: str
    ) -> CommitAnalysis:
        """Generate commit message using rule-based approach"""
        staged_files = changes.get("staged_files", [])

        # Build description based on files
        if len(staged_files) == 1:
            file_info = staged_files[0]
            description = f"{
                file_info['change_type']} {
                Path(
                    file_info['filename']).name}"
        elif len(staged_files) <= 3:
            description = f"update {len(staged_files)} files"
        else:
            description = f"update {len(staged_files)} files in {category}"

        # Create conventional commit message
        scope = category if category != "general" else ""
        if scope:
            conventional_format = f"{commit_type}({scope}): {description}"
        else:
            conventional_format = f"{commit_type}: {description}"

        key_changes = [f"{f['change_type']} {f['filename']}" for f in staged_files[:5]]

        return CommitAnalysis(
            suggested_message=conventional_format,
            message_type=commit_type,
            scope=scope,
            confidence=0.7,
            key_changes=key_changes,
            impact_assessment=f"Updates to {category} system",
            conventional_format=conventional_format,
            eq12_context=f"EQ12 {category} system modifications",
        )

    def _determine_primary_category(self, categories: set) -> str:
        """Determine primary category from set of categories"""
        category_priority = [
            "betting",
            "ai",
            "automation",
            "finance",
            "dashboard",
            "devops",
            "general",
        ]

        for cat in category_priority:
            if cat in categories:
                return cat

        return list(categories)[0] if categories else "general"

    def _determine_commit_type(self, change_types: set,
                               files: list[dict[str, str]]) -> str:
        """Determine commit type based on changes"""
        # Check for new files
        if "added" in change_types:
            return "feat"

        # Check for deleted files
        if "deleted" in change_types:
            return "refactor"

        # Check file patterns for specific types
        for file_info in files:
            filename = file_info["filename"].lower()

            if "test" in filename:
                return "test"
            if filename.endswith((".md", ".txt", ".rst")):
                return "docs"
            if filename.endswith((".yml", ".yaml", ".json")):
                return "ci" if "workflow" in filename or ".github" in filename else "build"

        # Default to fix for modifications
        return "fix"

    async def generate_pr_analysis(self, branch: str = None) -> PRAnalysis:
        """Generate comprehensive PR analysis and description"""
        try:
            # Get branch changes
            if not branch:
                # Get current branch
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    cwd="C:/EQ12",
                )
                branch = result.stdout.strip()

            # Get commits in branch
            commits_result = subprocess.run(
                ["git", "log", "--oneline", "main..HEAD"],
                capture_output=True,
                text=True,
                cwd="C:/EQ12",
            )

            # Get overall diff
            diff_result = subprocess.run(
                ["git", "dif", "main...HEAD", "--name-status"],
                capture_output=True,
                text=True,
                cwd="C:/EQ12",
            )

            commits = (commits_result.stdout.strip().split("\n")
                       if commits_result.stdout.strip() else [])
            file_changes = self._parse_git_status(diff_result.stdout)

            # Analyze with AI if available
            if self.ai_system:
                return await self._generate_ai_pr_analysis(branch, commits, file_changes)
            return self._generate_rule_based_pr_analysis(branch, commits, file_changes)

        except Exception as e:
            logger.error(f"Failed to generate PR analysis: {e}")
            return PRAnalysis(
                title=f"Update {branch}",
                description="Pull request updates",
                changes_summary=[],
                impact_analysis="Unknown impact",
                testing_suggestions=[],
                eq12_integration_notes="",
                breaking_changes=[],
                confidence=0.3,
            )

    async def _generate_ai_pr_analysis(
        self, branch: str, commits: list[str], files: list[dict[str, str]]
    ) -> PRAnalysis:
        """Generate PR analysis using AI"""
        try:
            # Build context
            commits_context = "\n".join([f"- {commit}" for commit in commits[:10]])
            files_context = "\n".join(
                [
                    f"- {f['change_type'].title()} {f['filename']} ({f['eq12_category']})"
                    for f in files[:15]
                ]
            )

            context = """
            Analyze this pull request for the EQ12 automation system:

            Branch: {branch}

            Commits:
            {commits_context}

            Files Changed:
            {files_context}

            Generate a comprehensive PR analysis including:
            1. Clear title summarizing the changes
            2. Detailed description of what was changed and why
            3. Impact on the EQ12 system (betting, automation, finance, AI, dashboard)
            4. Testing recommendations
            5. Any breaking changes or migration notes

            Focus on business value and technical clarity for the EQ12 team.
            """

            result = await self.ai_system.enhanced_classify_content(
                content=context, url="", context="Pull request analysis"
            )

            # Extract structured information from AI response
            title = self._extract_pr_title(branch, files)
            changes_summary = (
                result.key_features if result.key_features else [
                    f"Updated {
                        len(files)} files"])

            return PRAnalysis(
                title=title,
                description=result.reasoning,
                changes_summary=changes_summary,
                impact_analysis=(
                    f"Impact on EQ12 {
                        result.category} system: {
                        result.eq12_relevance:.0%} relevance",
                )
                testing_suggestions=result.suggested_actions,
                eq12_integration_notes=f"Integration with EQ12 {
                    result.category} workflows",
                breaking_changes=[],  # Could be enhanced to detect breaking changes
                confidence=result.confidence,
            )

        except Exception as e:
            logger.error(f"AI PR analysis failed: {e}")
            return self._generate_rule_based_pr_analysis(branch, commits, files)

    def _generate_rule_based_pr_analysis(
        self, branch: str, commits: list[str], files: list[dict[str, str]]
    ) -> PRAnalysis:
        """Generate PR analysis using rule-based approach"""
        # Determine primary changes
        categories = set(f.get("eq12_category", "general") for f in files)
        primary_category = self._determine_primary_category(categories)

        # Build title
        title = self._extract_pr_title(branch, files)

        # Build description
        description_parts = []
        description_parts.append(
            f"This PR updates the EQ12 {primary_category} system with {
                len(commits)} commits affecting {
                len(files)} files.")

        if len(commits) <= 5:
            description_parts.append("\n**Changes:**")
            for commit in commits[:5]:
                description_parts.append(f"- {commit}")

        # Categorize files
        by_category = {}
        for file_info in files:
            cat = file_info.get("eq12_category", "general")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(file_info)

        description_parts.append("\n**Files Modified by Category:**")
        for cat, cat_files in by_category.items():
            description_parts.append(f"- {cat.title()}: {len(cat_files)} files")

        changes_summary = [
            f"{cat}: {len(cat_files)} files" for cat, cat_files in by_category.items()
        ]

        testing_suggestions = [
            f"Test {primary_category} functionality",
            "Run existing test suite",
            "Verify EQ12 system integration",
        ]

        return PRAnalysis(
            title=title,
            description="\n".join(description_parts),
            changes_summary=changes_summary,
            impact_analysis=f"Primary impact on EQ12 {primary_category} system",
            testing_suggestions=testing_suggestions,
            eq12_integration_notes=f"Integrates with existing EQ12 {primary_category} workflows",
            breaking_changes=[],
            confidence=0.8,
        )

    def _extract_pr_title(self, branch: str, files: list[dict[str, str]]) -> str:
        """Extract meaningful PR title from branch and files"""
        # Clean branch name
        clean_branch = branch.replace("-", " ").replace("_", " ")

        if len(files) == 1:
            file_info = files[0]
            return f"{
                file_info['change_type'].title()} {
                Path(
                    file_info['filename']).stem}"

        # Determine category focus
        categories = set(f.get("eq12_category", "general") for f in files)
        if len(categories) == 1:
            category = list(categories)[0]
            return f"Update EQ12 {category} system"

        return f"Update EQ12 system ({clean_branch})"

    def save_analysis_results(self, analysis: Any, analysis_type: str) -> str:
        """Save analysis results to EQ12 data directory"""
        try:
            filename = f"copilot_{analysis_type}_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = Path(self.data_dir) / filename

            with open(filepath, "w") as f:
                json.dump(asdict(analysis), f, indent=2, default=str)

            logger.info(f"Analysis results saved to {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to save analysis results: {e}")
            return ""


async def main():
    """Test the content engine capabilities"""
    print("🧠 EQ12 Copilot Content Engine - Enhanced Analysis")
    print("=" * 60)

    engine = EQ12CopilotContentEngine()

    # Test git changes analysis
    print("\n🔍 Analyzing current git changes...")
    changes = engine.analyze_git_changes()

    if changes.get("error"):
        print(f"❌ Error analyzing changes: {changes['error']}")
        return

    if not changes.get("has_changes"):
        print("ℹ️ No git changes detected")
        return

    print(f"📊 Found {len(changes.get('staged_files', []))} staged files")

    # Generate commit message
    print("\n💬 Generating enhanced commit message...")
    commit_analysis = await engine.generate_enhanced_commit_message(changes)

    print("✅ Suggested Commit Message:")
    print(f"  Message: {commit_analysis.suggested_message}")
    print(f"  Type: {commit_analysis.message_type}")
    print(f"  Scope: {commit_analysis.scope}")
    print(f"  Confidence: {commit_analysis.confidence:.2%}")
    print(f"  EQ12 Context: {commit_analysis.eq12_context}")

    if commit_analysis.key_changes:
        print("  Key Changes:")
        for change in commit_analysis.key_changes[:3]:
            print(f"    - {change}")

    # Generate PR analysis
    print("\n📝 Generating PR analysis...")
    pr_analysis = await engine.generate_pr_analysis()

    print("✅ PR Analysis:")
    print(f"  Title: {pr_analysis.title}")
    print(f"  Confidence: {pr_analysis.confidence:.2%}")
    print(f"  Changes: {len(pr_analysis.changes_summary)} categories")
    print(f"  Testing Suggestions: {len(pr_analysis.testing_suggestions)}")

    # Save results
    commit_file = engine.save_analysis_results(commit_analysis, "commit")
    pr_file = engine.save_analysis_results(pr_analysis, "pr")

    print("\n💾 Results saved:")
    print(f"  Commit Analysis: {commit_file}")
    print(f"  PR Analysis: {pr_file}")

    print("\n🎉 EQ12 Copilot Content Engine ready for integration!")


if __name__ == "__main__":
    asyncio.run(main())
