#!/usr/bin/env python3
"""
EQ12 GODSTACK - Research Engine Planner
Query decomposition and research strategy planning

Core Features:
- Intelligent query classification and decomposition
- Research step planning and prioritization
- Context-aware subquery generation
- Strategy selection based on query complexity
- Dynamic step adjustment based on results
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/planner.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Query classification types"""

    MLB_PLAYER_ANALYSIS = "mlb_player"
    MLB_GAME_ANALYSIS = "mlb_game"
    MLB_PROPS_RESEARCH = "mlb_props"
    INJURY_INTELLIGENCE = "injury_intel"
    MARKET_ANALYSIS = "market_analysis"
    WEATHER_ANALYSIS = "weather"
    ODDS_COMPARISON = "odds_comparison"
    GENERAL_RESEARCH = "general"
    MULTI_DOMAIN = "multi_domain"


class PlanningComplexity(Enum):
    """Planning complexity levels"""

    SIMPLE = "simple"  # 1-2 steps, single source
    MODERATE = "moderate"  # 3-5 steps, multiple sources
    COMPLEX = "complex"  # 6+ steps, cross-domain analysis
    ADAPTIVE = "adaptive"  # Dynamic based on intermediate results


@dataclass
class ResearchStep:
    """Individual research step definition"""

    step_id: str
    name: str
    description: str
    priority: int

    # Execution details
    query_template: str
    retrievers: list[str]
    expected_sources: int

    # Dependencies
    depends_on: list[str] = field(default_factory=list)
    provides_context_for: list[str] = field(default_factory=list)

    # Quality controls
    min_confidence: float = 0.7
    required: bool = True
    timeout_seconds: int = 30

    # Context handling
    context_keys: list[str] = field(default_factory=list)
    output_format: str = "structured"


@dataclass
class ResearchPlan:
    """Complete research execution plan"""

    plan_id: str
    query_type: QueryType
    complexity: PlanningComplexity

    # Original query context
    original_query: str
    processed_query: str
    query_context: dict[str, Any]

    # Execution plan
    steps: list[ResearchStep]
    total_estimated_time: int
    max_parallel_steps: int = 3

    # Quality requirements
    min_overall_confidence: float = 0.75
    require_citations: bool = True

    # Budget constraints
    max_api_calls: int = 50
    max_cost_usd: float = 2.0

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    created_by: str = "planner_v2"


class QueryClassifier:
    """Classify queries to determine research strategy"""

    def __init__(self):
        # MLB-specific patterns
        self.mlb_patterns = {
            "player_names": ["judge", "ohtani", "betts", "trout", "acuna", "tatis"],
            "positions": ["pitcher", "catcher", "infield", "outfield", "dh"],
            "stats": ["era", "whip", "ops", "avg", "hr", "rbi", "sb", "k%"],
            "prop_types": ["over", "under", "strikeouts", "hits", "runs", "rbis"],
        }

        # Market patterns
        self.market_patterns = {
            "movement": ["line movement", "odds shift", "sharp money", "public"],
            "comparison": ["vs", "versus", "compare", "best odds", "shop"],
            "timing": ["live", "pregame", "closing", "opening"],
        }

        # Injury patterns
        self.injury_patterns = {
            "status": ["injury", "dtd", "il", "disabled", "questionable"],
            "types": ["hamstring", "shoulder", "elbow", "knee", "oblique", "back"],
            "impact": ["impact", "replacement", "depth", "lineup"],
        }

    def classify_query(
        self, query: str, context: dict[str, Any] | None = None
    ) -> tuple[QueryType, float]:
        """Classify query and return confidence score"""

        query_lower = query.lower()
        scores = {}

        # MLB Player Analysis
        player_score = 0
        for pattern_type, patterns in self.mlb_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in query_lower)
            if pattern_type == "player_names" and matches > 0:
                player_score += 0.4
            elif matches > 0:
                player_score += 0.2 * min(matches, 2) / 2

        if any(word in query_lower for word in ["player", "batter", "hitter"]):
            player_score += 0.2

        scores[QueryType.MLB_PLAYER_ANALYSIS] = min(player_score, 1.0)

        # MLB Props Research
        props_score = 0
        prop_indicators = [
            "props",
            "prop",
            "strikeouts",
            "hits allowed",
            "over",
            "under",
        ]
        props_score += sum(0.25 for indicator in prop_indicators if indicator in query_lower)

        if any(stat in query_lower for stat in self.mlb_patterns["stats"]):
            props_score += 0.3

        scores[QueryType.MLB_PROPS_RESEARCH] = min(props_score, 1.0)

        # Market Analysis
        market_score = 0
        for pattern_type, patterns in self.market_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in query_lower)
            market_score += 0.3 * min(matches, 2) / 2

        scores[QueryType.MARKET_ANALYSIS] = min(market_score, 1.0)

        # Injury Intelligence
        injury_score = 0
        for pattern_type, patterns in self.injury_patterns.items():
            matches = sum(1 for pattern in patterns if pattern in query_lower)
            injury_score += 0.35 * min(matches, 2) / 2

        scores[QueryType.INJURY_INTELLIGENCE] = min(injury_score, 1.0)

        # Weather Analysis
        weather_indicators = [
            "weather",
            "wind",
            "temperature",
            "rain",
            "dome",
            "outdoor",
        ]
        weather_score = sum(0.3 for indicator in weather_indicators if indicator in query_lower)
        scores[QueryType.WEATHER_ANALYSIS] = min(weather_score, 1.0)

        # Odds Comparison
        odds_indicators = ["odds", "line", "spread", "moneyline", "total", "best price"]
        odds_score = sum(0.25 for indicator in odds_indicators if indicator in query_lower)
        scores[QueryType.ODDS_COMPARISON] = min(odds_score, 1.0)

        # Multi-domain (if multiple high scores)
        high_scores = [score for score in scores.values() if score > 0.4]
        if len(high_scores) >= 2:
            scores[QueryType.MULTI_DOMAIN] = max(high_scores) * 0.8

        # General fallback
        if not scores or max(scores.values()) < 0.3:
            scores[QueryType.GENERAL_RESEARCH] = 0.6

        # Return highest confidence classification
        best_type = max(scores.items(), key=lambda x: x[1])
        return best_type[0], best_type[1]

    def extract_entities(self, query: str) -> dict[str, list[str]]:
        """Extract entities from query for context"""

        entities = {"players": [], "teams": [], "stats": [], "dates": [], "numbers": []}

        # Simple pattern matching (could be enhanced with NER)
        query.lower().split()

        # Extract potential player names (capitalized words)
        import re

        player_pattern = r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"
        players = re.findall(player_pattern, query)
        entities["players"] = players

        # Extract numbers (for props, odds, etc)
        number_pattern = r"\b\d+\.?\d*\b"
        numbers = re.findall(number_pattern, query)
        entities["numbers"] = numbers

        # Extract known stats
        for stat in self.mlb_patterns["stats"]:
            if stat in query.lower():
                entities["stats"].append(stat)

        return entities


class ResearchPlanner:
    """Main research planning engine"""

    def __init__(self, recipe_config: dict[str, Any] | None = None):
        self.classifier = QueryClassifier()
        self.recipe_config = recipe_config or {}

        # Planning templates by query type
        self.planning_templates = self._init_planning_templates()

        logger.info("ResearchPlanner initialized")

    def create_research_plan(
        self, query: str, context: dict[str, Any] | None = None
    ) -> ResearchPlan:
        """Create complete research plan for query"""

        # Classify query
        query_type, confidence = self.classifier.classify_query(query, context)

        # Extract entities and context
        entities = self.classifier.extract_entities(query)

        # Determine complexity
        complexity = self._determine_complexity(query, query_type, entities)

        # Generate plan ID
        plan_id = self._generate_plan_id(query, query_type)

        # Get planning template
        template = self.planning_templates.get(
            query_type, self.planning_templates[QueryType.GENERAL_RESEARCH]
        )

        # Create research steps
        steps = self._create_research_steps(query, query_type, entities, template)

        # Estimate timing
        total_time = sum(step.timeout_seconds for step in steps)

        # Apply recipe constraints
        max_calls, max_cost = self._get_budget_constraints()

        # Create plan
        plan = ResearchPlan(
            plan_id=plan_id,
            query_type=query_type,
            complexity=complexity,
            original_query=query,
            processed_query=self._process_query(query, entities),
            query_context={
                "entities": entities,
                "classification_confidence": confidence,
                **(context or {}),
            },
            steps=steps,
            total_estimated_time=total_time,
            max_api_calls=max_calls,
            max_cost_usd=max_cost,
        )

        logger.info(f"Created research plan: {plan_id} ({query_type.value}, {complexity.value})")

        return plan

    def optimize_plan(
        self, plan: ResearchPlan, constraints: dict[str, Any] | None = None
    ) -> ResearchPlan:
        """Optimize plan based on constraints and priorities"""

        constraints = constraints or {}

        # Apply time constraints
        if "max_time_seconds" in constraints:
            max_time = constraints["max_time_seconds"]
            if plan.total_estimated_time > max_time:
                plan = self._reduce_plan_time(plan, max_time)

        # Apply cost constraints
        if "max_cost_usd" in constraints:
            max_cost = constraints["max_cost_usd"]
            if plan.max_cost_usd > max_cost:
                plan.max_cost_usd = max_cost
                plan = self._reduce_plan_cost(plan, max_cost)

        # Reorder steps by priority
        plan.steps.sort(key=lambda step: (-step.priority, step.required))

        return plan

    def _init_planning_templates(self) -> dict[QueryType, dict[str, Any]]:
        """Initialize planning templates for each query type"""

        templates = {
            QueryType.MLB_PLAYER_ANALYSIS: {
                "base_steps": [
                    "player_stats",
                    "recent_performance",
                    "matchup_analysis",
                    "injury_status",
                    "prop_history",
                ],
                "retrievers": ["mlb_api", "fangraphs", "statcast", "injury_reports"],
                "parallel_capable": True,
            },
            QueryType.MLB_PROPS_RESEARCH: {
                "base_steps": [
                    "prop_history",
                    "current_form",
                    "matchup_context",
                    "market_comparison",
                    "value_assessment",
                ],
                "retrievers": ["odds_api", "prop_tracking", "mlb_api", "weather"],
                "parallel_capable": True,
            },
            QueryType.INJURY_INTELLIGENCE: {
                "base_steps": [
                    "injury_details",
                    "recovery_timeline",
                    "replacement_analysis",
                    "lineup_impact",
                    "historical_patterns",
                ],
                "retrievers": ["injury_reports", "depth_charts", "news_feeds"],
                "parallel_capable": False,  # Sequential for injury analysis
            },
            QueryType.MARKET_ANALYSIS: {
                "base_steps": [
                    "line_movement",
                    "volume_analysis",
                    "sharp_indicators",
                    "public_sentiment",
                    "value_spots",
                ],
                "retrievers": ["odds_api", "line_tracking", "volume_feeds"],
                "parallel_capable": True,
            },
            QueryType.GENERAL_RESEARCH: {
                "base_steps": ["main_query", "supporting_context", "verification"],
                "retrievers": ["web_search", "news_feeds"],
                "parallel_capable": True,
            },
        }

        return templates

    def _determine_complexity(
        self, query: str, query_type: QueryType, entities: dict[str, Any]
    ) -> PlanningComplexity:
        """Determine planning complexity based on query characteristics"""

        complexity_score = 0

        # Entity complexity
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        if total_entities > 5:
            complexity_score += 2
        elif total_entities > 2:
            complexity_score += 1

        # Query length complexity
        word_count = len(query.split())
        if word_count > 20:
            complexity_score += 2
        elif word_count > 10:
            complexity_score += 1

        # Multi-domain queries are inherently complex
        if query_type == QueryType.MULTI_DOMAIN:
            complexity_score += 3

        # Query type complexity
        complex_types = [QueryType.INJURY_INTELLIGENCE, QueryType.MARKET_ANALYSIS]
        if query_type in complex_types:
            complexity_score += 1

        # Map score to complexity level
        if complexity_score >= 5:
            return PlanningComplexity.COMPLEX
        if complexity_score >= 3 or complexity_score >= 1:
            return PlanningComplexity.MODERATE
        return PlanningComplexity.SIMPLE

    def _create_research_steps(
        self,
        query: str,
        query_type: QueryType,
        entities: dict[str, Any],
        template: dict[str, Any],
    ) -> list[ResearchStep]:
        """Create detailed research steps from template"""

        steps = []
        base_steps = template["base_steps"]
        available_retrievers = template["retrievers"]

        for i, step_name in enumerate(base_steps):
            step = ResearchStep(
                step_id=f"step_{i + 1:02d}",
                name=step_name,
                description=self._get_step_description(step_name, query_type),
                priority=len(base_steps) - i,  # Higher number = higher priority
                query_template=self._generate_query_template(step_name, query, entities),
                retrievers=self._select_step_retrievers(step_name, available_retrievers),
                expected_sources=self._estimate_source_count(step_name),
                timeout_seconds=30,
                required=i < 3,  # First 3 steps are required
            )

            # Set dependencies
            if i > 0 and not template.get("parallel_capable", True):
                step.depends_on = [f"step_{i:02d}"]

            steps.append(step)

        return steps

    def _get_step_description(self, step_name: str, query_type: QueryType) -> str:
        """Get human-readable description for step"""

        descriptions = {
            "player_stats": "Gather current season and career statistics",
            "recent_performance": "Analyze last 10-15 games performance trends",
            "matchup_analysis": "Evaluate matchup-specific factors",
            "injury_status": "Check current injury reports and status",
            "prop_history": "Review historical prop betting performance",
            "current_form": "Assess recent form and trends",
            "matchup_context": "Analyze specific game matchup context",
            "market_comparison": "Compare across multiple sportsbooks",
            "value_assessment": "Determine betting value and edge",
            "injury_details": "Gather detailed injury information",
            "recovery_timeline": "Estimate recovery and return timeline",
            "replacement_analysis": "Analyze replacement player impact",
            "lineup_impact": "Assess impact on team lineup",
            "historical_patterns": "Review historical injury patterns",
            "line_movement": "Track line movement patterns",
            "volume_analysis": "Analyze betting volume indicators",
            "sharp_indicators": "Identify sharp money indicators",
            "public_sentiment": "Assess public betting sentiment",
            "value_spots": "Identify potential value opportunities",
            "main_query": "Execute primary research query",
            "supporting_context": "Gather supporting context",
            "verification": "Verify key claims and data",
        }

        return descriptions.get(step_name, f"Execute {step_name} research step")

    def _generate_query_template(
        self, step_name: str, original_query: str, entities: dict[str, Any]
    ) -> str:
        """Generate query template for specific step"""

        # Extract key context
        players = " ".join(entities.get("players", []))
        stats = " ".join(entities.get("stats", []))

        templates = {
            "player_stats": f"Current season stats for {players} {stats}",
            "recent_performance": f"Last 15 games performance {players}",
            "matchup_analysis": f"Matchup factors {players} vs opponent",
            "injury_status": f"Injury report status {players}",
            "prop_history": f"Prop betting history {players} {stats}",
            "line_movement": f"Line movement analysis {original_query}",
            "market_comparison": f"Sportsbook comparison {original_query}",
        }

        return templates.get(step_name, original_query)

    def _select_step_retrievers(self, step_name: str, available_retrievers: list[str]) -> list[str]:
        """Select appropriate retrievers for step"""

        step_retriever_preferences = {
            "player_stats": ["mlb_api", "fangraphs", "statcast"],
            "recent_performance": ["mlb_api", "statcast"],
            "matchup_analysis": ["matchup_db", "fangraphs"],
            "injury_status": ["injury_reports", "news_feeds"],
            "prop_history": ["prop_tracking", "odds_api"],
            "line_movement": ["odds_api", "line_tracking"],
            "market_comparison": ["odds_api", "sportsbook_apis"],
        }

        preferred = step_retriever_preferences.get(step_name, available_retrievers[:2])

        # Return intersection of preferred and available
        return [r for r in preferred if r in available_retrievers][:3]

    def _estimate_source_count(self, step_name: str) -> int:
        """Estimate expected source count for step"""

        estimates = {
            "player_stats": 3,
            "recent_performance": 2,
            "matchup_analysis": 4,
            "injury_status": 2,
            "prop_history": 3,
            "line_movement": 5,
            "market_comparison": 6,
        }

        return estimates.get(step_name, 3)

    def _process_query(self, query: str, entities: dict[str, Any]) -> str:
        """Process and enhance original query"""

        # For now, just return cleaned query
        # Could add query expansion, synonym replacement, etc.

        processed = query.strip()

        # Add entity context if helpful
        players = entities.get("players", [])
        if players:
            processed += f" [Players: {', '.join(players)}]"

        return processed

    def _get_budget_constraints(self) -> tuple[int, float]:
        """Get budget constraints from recipe config"""

        budgets = self.recipe_config.get("budgets", {})

        # Calculate API calls from rate limits
        rpm = budgets.get("rpm", 100)
        estimated_duration_min = 5  # Default 5 minutes
        max_calls = int(rpm * estimated_duration_min * 0.8)  # 80% of limit

        max_cost = budgets.get("cost_usd", 1.0)

        return max_calls, max_cost

    def _reduce_plan_time(self, plan: ResearchPlan, max_time: int) -> ResearchPlan:
        """Reduce plan execution time to fit constraints"""

        # Remove non-required steps if over time
        required_steps = [step for step in plan.steps if step.required]
        optional_steps = [step for step in plan.steps if not step.required]

        required_time = sum(step.timeout_seconds for step in required_steps)

        if required_time <= max_time:
            # Add optional steps until time limit
            available_time = max_time - required_time
            selected_optional = []

            for step in sorted(optional_steps, key=lambda s: s.priority, reverse=True):
                if step.timeout_seconds <= available_time:
                    selected_optional.append(step)
                    available_time -= step.timeout_seconds

            plan.steps = required_steps + selected_optional
        else:
            # Reduce timeout for required steps
            time_reduction = required_time - max_time
            reduction_per_step = time_reduction // len(required_steps)

            for step in required_steps:
                step.timeout_seconds = max(10, step.timeout_seconds - reduction_per_step)

            plan.steps = required_steps

        plan.total_estimated_time = sum(step.timeout_seconds for step in plan.steps)

        return plan

    def _reduce_plan_cost(self, plan: ResearchPlan, max_cost: float) -> ResearchPlan:
        """Reduce plan cost to fit budget constraints"""

        # Simple cost reduction - remove lowest priority optional steps
        required_steps = [step for step in plan.steps if step.required]
        optional_steps = [step for step in plan.steps if not step.required]

        # Estimate cost per step (rough)
        cost_per_step = plan.max_cost_usd / len(plan.steps)
        required_cost = len(required_steps) * cost_per_step

        if required_cost <= max_cost:
            # Determine how many optional steps we can afford
            remaining_budget = max_cost - required_cost
            affordable_optional = int(remaining_budget // cost_per_step)

            # Select highest priority optional steps
            selected_optional = sorted(optional_steps, key=lambda s: s.priority, reverse=True)[
                :affordable_optional
            ]

            plan.steps = required_steps + selected_optional
        else:
            # Only keep required steps
            plan.steps = required_steps

        return plan

    def _generate_plan_id(self, query: str, query_type: QueryType) -> str:
        """Generate unique plan ID"""

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]

        return f"plan_{query_type.value}_{timestamp}_{query_hash}"


def main():
    """CLI interface for research planning"""

    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Research Planner")
    parser.add_argument("query", help="Research query to plan")
    parser.add_argument("--classify-only", action="store_true", help="Only classify query")
    parser.add_argument("--optimize", action="store_true", help="Optimize plan")
    parser.add_argument("--max-time", type=int, help="Maximum execution time in seconds")
    parser.add_argument("--max-cost", type=float, help="Maximum cost in USD")
    parser.add_argument("--output", help="Output plan to file")

    args = parser.parse_args()

    planner = ResearchPlanner()

    if args.classify_only:
        query_type, confidence = planner.classifier.classify_query(args.query)
        print(f"Query Type: {query_type.value}")
        print(f"Confidence: {confidence:.2f}")

        entities = planner.classifier.extract_entities(args.query)
        if any(entities.values()):
            print("\nExtracted Entities:")
            for entity_type, entity_list in entities.items():
                if entity_list:
                    print(f"  {entity_type}: {entity_list}")
    else:
        print(f"📋 Creating research plan for: {args.query}")

        plan = planner.create_research_plan(args.query)

        if args.optimize:
            constraints = {}
            if args.max_time:
                constraints["max_time_seconds"] = args.max_time
            if args.max_cost:
                constraints["max_cost_usd"] = args.max_cost

            if constraints:
                plan = planner.optimize_plan(plan, constraints)

        print(f"\n✅ Plan Created: {plan.plan_id}")
        print(f"   Query Type: {plan.query_type.value}")
        print(f"   Complexity: {plan.complexity.value}")
        print(f"   Steps: {len(plan.steps)}")
        print(f"   Estimated Time: {plan.total_estimated_time}s")
        print(f"   Max Cost: ${plan.max_cost_usd:.2f}")

        print("\n📝 Research Steps:")
        for i, step in enumerate(plan.steps, 1):
            required_mark = "🔸" if step.required else "🔹"
            print(f"   {i}. {required_mark} {step.name} ({step.timeout_seconds}s)")
            print(f"      {step.description}")
            print(f"      Retrievers: {', '.join(step.retrievers)}")

        if args.output:
            plan_dict = {
                "plan_id": plan.plan_id,
                "query_type": plan.query_type.value,
                "complexity": plan.complexity.value,
                "original_query": plan.original_query,
                "processed_query": plan.processed_query,
                "query_context": plan.query_context,
                "total_estimated_time": plan.total_estimated_time,
                "max_cost_usd": plan.max_cost_usd,
                "steps": [
                    {
                        "step_id": step.step_id,
                        "name": step.name,
                        "description": step.description,
                        "priority": step.priority,
                        "query_template": step.query_template,
                        "retrievers": step.retrievers,
                        "expected_sources": step.expected_sources,
                        "timeout_seconds": step.timeout_seconds,
                        "required": step.required,
                    }
                    for step in plan.steps
                ],
                "created_at": plan.created_at.isoformat(),
            }

            with open(args.output, "w") as f:
                json.dump(plan_dict, f, indent=2)

            print(f"\n💾 Plan saved to: {args.output}")


if __name__ == "__main__":
    main()
