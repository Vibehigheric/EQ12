#!/usr/bin/env python3
"""
EQ12 Decision Engine - "Build This or Use What We Have?"

Evaluates whether to build new systems, extend existing ones, or reject proposals.
Integrates with EQ12 stack, 5-USB architecture, and AI providers.

Created: 2025-11-22
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DecisionResult:
    """Structure for decision engine results"""
    build_score: int  # 0-100
    use_current_score: int  # 0-100
    reasoning: str
    decision: str  # BUILD / USE_CURRENT / EXTEND / DELAY / REJECT
    next_actions: List[str]
    system_conflicts: List[str]
    revenue_impact: str  # HIGH / MEDIUM / LOW / NONE
    complexity_score: int  # 0-100
    maintenance_burden: str  # HIGH / MEDIUM / LOW
    timestamp: str


class EQ12DecisionEngine:
    """
    Master decision engine for evaluating build vs use decisions
    """

    def __init__(self, workspace_root: str = "/workspaces/EQ12"):
        self.workspace_root = Path(workspace_root)
        self.scripts_dir = self.workspace_root / "scripts"
        self.configs_dir = self.workspace_root / "configs"
        self.logs_dir = self.workspace_root / "logs"

        # Load existing capabilities
        self.existing_systems = self._scan_existing_systems()
        self.usb_architecture = self._load_usb_architecture()
        self.api_providers = self._load_api_providers()

    def _scan_existing_systems(self) -> List[str]:
        """Scan for existing EQ12 modules and capabilities"""
        systems = []

        if self.scripts_dir.exists():
            for script_file in self.scripts_dir.glob("*.py"):
                systems.append(script_file.stem)

        logger.info(f"Found {len(systems)} existing systems")
        return systems

    def _load_usb_architecture(self) -> Dict[str, str]:
        """Load 5-USB architecture configuration"""
        return {
            "USB1": "Recovery System",
            "USB2": "Coral Model Cache",
            "USB3": "Buffalo 14215 Intelligence",
            "USB4": "Revenue Empire Vault",
            "USB5": "Enterprise Security Auth"
        }

    def _load_api_providers(self) -> Dict[str, bool]:
        """Check which API providers are configured"""
        providers = {
            "GROQ": "GROQ_API_KEY" in os.environ,
            "OPENAI": "OPENAI_API_KEY" in os.environ,
            "GOOGLE_AI": "GOOGLE_AI_API_KEY" in os.environ,
            "ODDS_API": "ODDS_API_KEY" in os.environ,
            "OPENWEATHER": "OPENWEATHER_API_KEY" in os.environ,
            "TELEGRAM": "TELEGRAM_BOT_TOKEN" in os.environ,
        }

        configured = [k for k, v in providers.items() if v]
        logger.info(f"Configured API providers: {', '.join(configured)}")

        return providers

    def _check_duplication(self, proposal: str) -> List[str]:
        """Check if proposed system duplicates existing functionality"""
        conflicts = []
        proposal_lower = proposal.lower()

        keywords_map = {
            "betting": ["betting", "odds", "sports", "parlay"],
            "weather": ["weather", "forecast", "climate"],
            "shopify": ["shopify", "store", "ecommerce"],
            "chrome": ["chrome", "extension", "browser"],
            "coral": ["coral", "tpu", "edge", "inference"],
            "dashboard": ["dashboard", "report", "visualization"],
        }

        for system in self.existing_systems:
            system_lower = system.lower()
            for category, keywords in keywords_map.items():
                if any(kw in proposal_lower for kw in keywords) and \
                   any(kw in system_lower for kw in keywords):
                    conflicts.append(f"Overlaps with existing: {system}")

        return conflicts

    def _calculate_build_score(
        self,
        proposal: str,
        conflicts: List[str],
        revenue_potential: str,
        complexity: int
    ) -> int:
        """Calculate build score (0-100)"""
        score = 50  # Start neutral

        # Penalties
        if conflicts:
            score -= len(conflicts) * 15
        if complexity > 70:
            score -= 20
        if "HIGH" in revenue_potential:
            score += 30
        elif "MEDIUM" in revenue_potential:
            score += 15

        # Check API availability
        required_apis = self._extract_required_apis(proposal)
        if required_apis and not all(self.api_providers.get(api, False) for api in required_apis):
            score -= 25

        return max(0, min(100, score))

    def _calculate_use_current_score(
        self,
        conflicts: List[str],
        complexity: int
    ) -> int:
        """Calculate score for using current systems (0-100)"""
        score = 50  # Start neutral

        if conflicts:
            score += len(conflicts) * 20  # Existing system can handle it
        if complexity < 30:
            score += 15  # Simple feature, extend existing

        return max(0, min(100, score))

    def _extract_required_apis(self, proposal: str) -> List[str]:
        """Extract required API providers from proposal text"""
        apis = []
        proposal_lower = proposal.lower()

        api_keywords = {
            "GROQ": ["groq", "llama"],
            "OPENAI": ["openai", "gpt", "chatgpt"],
            "GOOGLE_AI": ["gemini", "google ai"],
            "ODDS_API": ["odds", "betting", "sports"],
            "OPENWEATHER": ["weather", "forecast"],
            "TELEGRAM": ["telegram", "bot", "alert"],
        }

        for api, keywords in api_keywords.items():
            if any(kw in proposal_lower for kw in keywords):
                apis.append(api)

        return apis

    def _assess_revenue_impact(self, proposal: str) -> str:
        """Assess potential revenue impact"""
        proposal_lower = proposal.lower()

        high_revenue_keywords = [
            "shopify", "marketplace", "api monetization",
            "subscription", "saas", "betting", "revenue"
        ]
        medium_revenue_keywords = [
            "automation", "dashboard", "analytics", "optimization"
        ]

        if any(kw in proposal_lower for kw in high_revenue_keywords):
            return "HIGH"
        elif any(kw in proposal_lower for kw in medium_revenue_keywords):
            return "MEDIUM"
        else:
            return "LOW"

    def _assess_complexity(self, proposal: str) -> int:
        """Assess implementation complexity (0-100)"""
        complexity = 30  # Base complexity

        proposal_lower = proposal.lower()

        # Complexity indicators
        if "machine learning" in proposal_lower or "ai model" in proposal_lower:
            complexity += 30
        if "real-time" in proposal_lower:
            complexity += 15
        if "integration" in proposal_lower:
            complexity += 10
        if "database" in proposal_lower:
            complexity += 10
        if "multi-platform" in proposal_lower:
            complexity += 15

        return min(100, complexity)

    def _generate_next_actions(
        self,
        decision: str,
        proposal: str,
        conflicts: List[str]
    ) -> List[str]:
        """Generate recommended next steps"""
        actions = []

        if decision == "BUILD":
            actions.extend([
                "Create detailed technical specification",
                "Set up development environment",
                "Implement core functionality",
                "Write comprehensive tests",
                "Deploy to staging for validation",
                "Document API endpoints and usage",
                "Create user guide"
            ])
        elif decision == "USE_CURRENT":
            actions.extend([
                f"Extend existing system: {conflicts[0] if conflicts else 'TBD'}",
                "Refactor to support new use case",
                "Add configuration options",
                "Update documentation"
            ])
        elif decision == "EXTEND":
            actions.extend([
                "Identify extension points in existing system",
                "Design plugin/module architecture",
                "Implement extension",
                "Test integration with core system"
            ])
        elif decision == "DELAY":
            actions.extend([
                "Complete prerequisite systems first",
                "Gather missing API keys",
                "Validate hardware requirements",
                "Reassess in 30 days"
            ])
        else:  # REJECT
            actions.extend([
                "Document rejection reasoning",
                "Archive proposal for future reference",
                "Consider alternative approaches"
            ])

        return actions[:7]  # Limit to 7 actions

    def evaluate(self, proposal: str) -> DecisionResult:
        """
        Main evaluation method

        Args:
            proposal: Description of the proposed system/feature

        Returns:
            DecisionResult with scores, reasoning, and recommendations
        """
        logger.info(f"Evaluating proposal: {proposal[:100]}...")

        # Analyze proposal
        conflicts = self._check_duplication(proposal)
        revenue_impact = self._assess_revenue_impact(proposal)
        complexity = self._assess_complexity(proposal)

        # Calculate scores
        build_score = self._calculate_build_score(
            proposal, conflicts, revenue_impact, complexity
        )
        use_current_score = self._calculate_use_current_score(
            conflicts, complexity
        )

        # Determine decision
        if build_score > 70 and build_score > use_current_score:
            decision = "BUILD"
        elif use_current_score > 70:
            decision = "USE_CURRENT"
        elif conflicts and build_score > 40:
            decision = "EXTEND"
        elif build_score < 30 and use_current_score < 30:
            decision = "REJECT"
        else:
            decision = "DELAY"

        # Generate reasoning
        reasoning_parts = []

        if conflicts:
            reasoning_parts.append(
                f"Conflicts with {len(conflicts)} existing system(s): "
                f"{', '.join(conflicts[:2])}"
            )

        if revenue_impact == "HIGH":
            reasoning_parts.append("High revenue potential justifies development")
        elif revenue_impact == "LOW":
            reasoning_parts.append("Low revenue impact, prefer existing solutions")

        if complexity > 70:
            reasoning_parts.append(f"High complexity ({complexity}/100) increases risk")

        required_apis = self._extract_required_apis(proposal)
        missing_apis = [api for api in required_apis if not self.api_providers.get(api, False)]
        if missing_apis:
            reasoning_parts.append(f"Missing API keys: {', '.join(missing_apis)}")

        reasoning = ". ".join(reasoning_parts) if reasoning_parts else \
            "Proposal evaluated against current capabilities"

        # Generate next actions
        next_actions = self._generate_next_actions(decision, proposal, conflicts)

        # Assess maintenance burden
        if complexity > 70 or len(conflicts) > 2:
            maintenance = "HIGH"
        elif complexity > 40:
            maintenance = "MEDIUM"
        else:
            maintenance = "LOW"

        result = DecisionResult(
            build_score=build_score,
            use_current_score=use_current_score,
            reasoning=reasoning,
            decision=decision,
            next_actions=next_actions,
            system_conflicts=conflicts,
            revenue_impact=revenue_impact,
            complexity_score=complexity,
            maintenance_burden=maintenance,
            timestamp=datetime.utcnow().isoformat()
        )

        # Log result
        self._save_decision_log(proposal, result)

        return result

    def _save_decision_log(self, proposal: str, result: DecisionResult):
        """Save decision to log file"""
        log_file = self.logs_dir / f"decision_engine_{datetime.now().strftime('%Y%m%d')}.json"

        entry = {
            "proposal": proposal,
            "result": asdict(result)
        }

        try:
            # Append to existing log or create new
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []

            logs.append(entry)

            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)

            logger.info(f"Decision logged to: {log_file}")
        except Exception as e:
            logger.error(f"Failed to save decision log: {e}")

    def print_result(self, result: DecisionResult):
        """Pretty print decision result"""
        print("\n" + "="*70)
        print("EQ12 DECISION ENGINE RESULT")
        print("="*70)
        print(f"\n📊 BUILD SCORE: {result.build_score}/100")
        print(f"📊 USE CURRENT SYSTEM SCORE: {result.use_current_score}/100")
        print(f"\n🧠 REASONING: {result.reasoning}")
        print(f"\n🎯 DECISION: {result.decision}")
        print(f"\n💰 REVENUE IMPACT: {result.revenue_impact}")
        print(f"⚙️  COMPLEXITY: {result.complexity_score}/100")
        print(f"🔧 MAINTENANCE: {result.maintenance_burden}")

        if result.system_conflicts:
            print(f"\n⚠️  CONFLICTS:")
            for conflict in result.system_conflicts:
                print(f"   - {conflict}")

        print(f"\n📋 NEXT ACTIONS:")
        for i, action in enumerate(result.next_actions, 1):
            print(f"   {i}. {action}")

        print("\n" + "="*70 + "\n")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="EQ12 Decision Engine - Build vs Use Evaluator"
    )
    parser.add_argument(
        "proposal",
        help="Description of proposed system/feature"
    )
    parser.add_argument(
        "--workspace",
        default="/workspaces/EQ12",
        help="EQ12 workspace root directory"
    )
    parser.add_argument(
        "--output",
        help="Save result to JSON file"
    )

    args = parser.parse_args()

    # Initialize engine
    engine = EQ12DecisionEngine(workspace_root=args.workspace)

    # Evaluate proposal
    result = engine.evaluate(args.proposal)

    # Print result
    engine.print_result(result)

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(asdict(result), f, indent=2)
        print(f"✅ Result saved to: {args.output}")

    # Exit with code based on decision
    exit_codes = {
        "BUILD": 0,
        "EXTEND": 0,
        "USE_CURRENT": 0,
        "DELAY": 1,
        "REJECT": 2
    }
    sys.exit(exit_codes.get(result.decision, 1))


if __name__ == "__main__":
    main()
