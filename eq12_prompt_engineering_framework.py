#!/usr/bin/env python3
"""
EQ12 Advanced Prompt Engineering Framework
Sophisticated prompt templates, role management, and conversation handling
for optimal AI interaction across different use cases.

Features:
- Modular prompt template system with inheritance
- Dynamic context injection and variable substitution
- Conversation history management and context optimization
- Role-based prompt engineering (system, user, assistant, tool)
- A/B testing framework for prompt optimization
- Performance analytics and success rate tracking

Author: EQ12 GODSTACK Team
Version: 1.0.0
License: MIT
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class PromptCategory(Enum):
    """Categories of prompts for organization"""

    SPORTS_BETTING = "sports_betting"
    CODE_REVIEW = "code_review"
    GOVERNANCE = "governance"
    ANALYSIS = "analysis"
    CREATIVITY = "creativity"
    REASONING = "reasoning"
    CLASSIFICATION = "classification"


class ConversationRole(Enum):
    """Enhanced conversation roles"""

    SYSTEM = "system"  # System instructions and behavior
    USER = "user"  # User input and queries
    ASSISTANT = "assistant"  # AI responses
    TOOL = "tool"  # Tool/function call results
    CONTEXT = "context"  # Additional context (internal use)
    MEMORY = "memory"  # Long-term memory injection


@dataclass
class PromptVariable:
    """Variable definition for prompts"""

    name: str
    description: str
    required: bool = True
    default_value: Any | None = None
    validation_pattern: str | None = None
    suggestions: list[str] = field(default_factory=list)


@dataclass
class ConversationMessage:
    """Enhanced message structure"""

    role: ConversationRole
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    token_count: int | None = None


@dataclass
class PromptPerformanceMetrics:
    """Performance tracking for prompts"""

    template_name: str
    total_uses: int = 0
    success_rate: float = 0.0
    average_response_time: float = 0.0
    average_tokens_used: float = 0.0
    average_cost: float = 0.0
    user_satisfaction: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)


class BasePromptTemplate(ABC):
    """Abstract base class for all prompt templates"""

    def __init__(
        self,
        name: str,
        category: PromptCategory,
        description: str,
        version: str = "1.0",
    ):
        self.name = name
        self.category = category
        self.description = description
        self.version = version
        self.variables: dict[str, PromptVariable] = {}
        self.metrics = PromptPerformanceMetrics(template_name=name)

    @abstractmethod
    def generate_messages(self, **kwargs) -> list[ConversationMessage]:
        """Generate conversation messages from template"""
        pass

    def add_variable(self, variable: PromptVariable):
        """Add a variable to the template"""
        self.variables[variable.name] = variable

    def validate_inputs(self, inputs: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate input variables"""
        errors = []

        # Check required variables
        for var_name, var_def in self.variables.items():
            if var_def.required and var_name not in inputs:
                errors.append(f"Required variable '{var_name}' is missing")

        # Check validation patterns
        for var_name, value in inputs.items():
            if var_name in self.variables:
                var_def = self.variables[var_name]
                if var_def.validation_pattern:
                    if not re.match(var_def.validation_pattern, str(value)):
                        errors.append(f"Variable '{var_name}' does not match pattern")

        return len(errors) == 0, errors


class SportsBettingPromptTemplate(BasePromptTemplate):
    """Advanced sports betting analysis prompt"""

    def __init__(self):
        super().__init__(
            name="sports_betting_expert",
            category=PromptCategory.SPORTS_BETTING,
            description="Expert sports betting analysis with Kelly Criterion and EV calculations",
            version="2.0",
        )

        # Define template variables
        self.add_variable(
            PromptVariable(
                name="game_info",
                description="Information about the game (teams, date, league)",
                required=True,
                suggestions=["Team A vs Team B", "Date and time", "League/competition"],
            )
        )

        self.add_variable(
            PromptVariable(
                name="bet_type",
                description="Type of bet being analyzed",
                required=True,
                suggestions=["Moneyline", "Spread", "Total", "Prop Bet", "Parlay"],
            )
        )

        self.add_variable(
            PromptVariable(
                name="odds",
                description="Betting odds in American format",
                required=True,
                validation_pattern=r"[+-]\d+",
            )
        )

        self.add_variable(
            PromptVariable(
                name="estimated_probability",
                description="Your estimated true probability (0-100)",
                required=True,
                validation_pattern=r"^(100|[0-9]?[0-9](\.[0-9]+)?)$",
            )
        )

        self.add_variable(
            PromptVariable(
                name="bankroll",
                description="Total bankroll amount",
                required=True,
                validation_pattern=r"^\d+(\.\d{2})?$",
            )
        )

        self.add_variable(
            PromptVariable(
                name="context",
                description="Additional context or factors to consider",
                required=False,
                default_value="No additional context provided.",
            )
        )

        self.add_variable(
            PromptVariable(
                name="risk_tolerance",
                description="Risk tolerance level (conservative, moderate, aggressive)",
                required=False,
                default_value="moderate",
                suggestions=["conservative", "moderate", "aggressive"],
            )
        )

    def generate_messages(self, **kwargs) -> list[ConversationMessage]:
        """Generate sports betting analysis conversation"""

        # Validate inputs
        valid, errors = self.validate_inputs(kwargs)
        if not valid:
            raise ValueError(f"Invalid inputs: {', '.join(errors)}")

        # Fill in defaults
        for var_name, var_def in self.variables.items():
            if var_name not in kwargs and var_def.default_value is not None:
                kwargs[var_name] = var_def.default_value

        system_message = ConversationMessage(
            role=ConversationRole.SYSTEM,
            content="""You are an elite sports betting analyst with expertise in:

            🎯 CORE COMPETENCIES:
            - Statistical modeling and probability analysis
            - Kelly Criterion bankroll management
            - Expected Value (EV) calculations
            - Line movement and market efficiency analysis
            - Risk assessment and variance management
            - Sharp vs public betting patterns

            📊 ANALYSIS FRAMEWORK:
            1. Calculate true implied probability from given odds
            2. Compare with user's estimated probability
            3. Determine Expected Value: EV = (True Prob × Payout) - (1 - True Prob)
            4. Apply Kelly Criterion: f* = (bp - q) / b
               where: b = decimal odds - 1, p = true probability, q = 1 - p
            5. Assess risk level based on variance and bankroll management
            6. Provide clear BET/PASS recommendation with reasoning

            🎲 OUTPUT REQUIREMENTS:
            - Clear recommendation: STRONG BET, BET, LEAN, or PASS
            - Confidence level (0-100%)
            - Expected Value percentage
            - Optimal Kelly fraction (0-25% max for safety)
            - Risk assessment (LOW/MEDIUM/HIGH)
            - Detailed reasoning with key factors

            Always prioritize long-term profitability over short-term gains.
            Apply conservative bankroll management principles.
            """,
            metadata={
                "template_version": self.version,
                "category": self.category.value,
            },
        )

        user_message = ConversationMessage(
            role=ConversationRole.USER,
            content=f"""🎯 BETTING ANALYSIS REQUEST

            📊 GAME DETAILS:
            Game: {kwargs["game_info"]}
            Bet Type: {kwargs["bet_type"]}
            Odds: {kwargs["odds"]}

            📈 MY ANALYSIS:
            Estimated True Probability: {kwargs["estimated_probability"]}%
            Available Bankroll: ${kwargs["bankroll"]}
            Risk Tolerance: {kwargs["risk_tolerance"]}

            📝 ADDITIONAL CONTEXT:
            {kwargs["context"]}

            Please provide a comprehensive betting analysis following your framework.
            Include specific calculations and clear reasoning for your recommendation.
            """,
            metadata={
                "bet_details": {
                    "odds": kwargs["odds"],
                    "probability": kwargs["estimated_probability"],
                    "bankroll": kwargs["bankroll"],
                }
            },
        )

        return [system_message, user_message]


class CodeReviewPromptTemplate(BasePromptTemplate):
    """Advanced code review prompt template"""

    def __init__(self):
        super().__init__(
            name="code_review_expert",
            category=PromptCategory.CODE_REVIEW,
            description="Expert-level code review with security, performance, and best practices",
            version="1.5",
        )

        self.add_variable(
            PromptVariable(
                name="language",
                description="Programming language",
                required=True,
                suggestions=[
                    "Python",
                    "JavaScript",
                    "TypeScript",
                    "PowerShell",
                    "C#",
                    "Java",
                ],
            )
        )

        self.add_variable(PromptVariable(name="code", description="Code to review", required=True))

        self.add_variable(
            PromptVariable(name="file_path", description="File path or name", required=True)
        )

        self.add_variable(
            PromptVariable(
                name="review_focus",
                description="Areas to focus on",
                required=False,
                default_value="security, performance, maintainability",
                suggestions=[
                    "security",
                    "performance",
                    "maintainability",
                    "readability",
                    "testing",
                ],
            )
        )

    def generate_messages(self, **kwargs) -> list[ConversationMessage]:
        """Generate code review conversation"""

        valid, errors = self.validate_inputs(kwargs)
        if not valid:
            raise ValueError(f"Invalid inputs: {', '.join(errors)}")

        system_message = ConversationMessage(
            role=ConversationRole.SYSTEM,
            content="""You are a senior software engineer conducting a comprehensive code review.

            🔍 REVIEW CRITERIA:
            - Security vulnerabilities and best practices
            - Performance optimization opportunities
            - Code maintainability and readability
            - Error handling and edge cases
            - Testing coverage and quality
            - Documentation and comments
            - Adherence to language conventions

            📋 OUTPUT FORMAT:
            1. SUMMARY: Overall assessment (Excellent/Good/Needs Work/Poor)
            2. SECURITY: Vulnerabilities and recommendations
            3. PERFORMANCE: Optimization opportunities
            4. MAINTAINABILITY: Structure and organization feedback
            5. SPECIFIC ISSUES: Line-by-line detailed feedback
            6. RECOMMENDATIONS: Prioritized improvement suggestions

            Provide specific examples and actionable feedback.
            """,
            metadata={"review_type": "comprehensive", "language": kwargs["language"]},
        )

        user_message = ConversationMessage(
            role=ConversationRole.USER,
            content=f"""📋 CODE REVIEW REQUEST

            🔧 FILE DETAILS:
            File: {kwargs["file_path"]}
            Language: {kwargs["language"]}
            Focus Areas: {kwargs.get("review_focus", "general review")}

            📄 CODE TO REVIEW:
            ```{kwargs["language"].lower()}
            {kwargs["code"]}
            ```

            Please provide a thorough code review following your criteria.
            """,
            metadata={
                "file_info": {
                    "path": kwargs["file_path"],
                    "language": kwargs["language"],
                    "code_length": len(kwargs["code"]),
                }
            },
        )

        return [system_message, user_message]


class GovernancePromptTemplate(BasePromptTemplate):
    """Governance and compliance analysis prompt"""

    def __init__(self):
        super().__init__(
            name="governance_expert",
            category=PromptCategory.GOVERNANCE,
            description="Expert governance analysis and compliance recommendations",
            version="1.0",
        )

        self.add_variable(
            PromptVariable(
                name="task_type",
                description="Type of governance task",
                required=True,
                suggestions=[
                    "security_audit",
                    "compliance_check",
                    "policy_review",
                    "risk_assessment",
                ],
            )
        )

        self.add_variable(
            PromptVariable(name="scope", description="Scope of analysis", required=True)
        )

        self.add_variable(
            PromptVariable(
                name="context",
                description="Additional context",
                required=False,
                default_value="Standard governance review",
            )
        )

    def generate_messages(self, **kwargs) -> list[ConversationMessage]:
        """Generate governance analysis conversation"""

        valid, errors = self.validate_inputs(kwargs)
        if not valid:
            raise ValueError(f"Invalid inputs: {', '.join(errors)}")

        system_message = ConversationMessage(
            role=ConversationRole.SYSTEM,
            content="""You are a governance and compliance expert specializing in:

            🛡️ EXPERTISE AREAS:
            - Information security governance
            - Regulatory compliance (SOX, GDPR, CCPA, HIPAA)
            - Risk management frameworks
            - Policy development and review
            - Audit preparation and response
            - Business continuity planning

            📊 ANALYSIS FRAMEWORK:
            1. Assess current state against best practices
            2. Identify gaps and vulnerabilities
            3. Evaluate risk levels and potential impact
            4. Recommend specific remediation steps
            5. Provide implementation timeline and priorities
            6. Suggest monitoring and review processes
            """,
            metadata={"expertise": "governance_compliance"},
        )

        user_message = ConversationMessage(
            role=ConversationRole.USER,
            content=f"""🏛️ GOVERNANCE ANALYSIS REQUEST

            📋 TASK DETAILS:
            Type: {kwargs["task_type"]}
            Scope: {kwargs["scope"]}

            📄 CONTEXT:
            {kwargs.get("context", "Standard governance review")}

            Please provide comprehensive governance analysis with specific recommendations.
            """,
            metadata={"task_type": kwargs["task_type"]},
        )

        return [system_message, user_message]


class PromptTemplateManager:
    """Manages prompt templates and performance tracking"""

    def __init__(self, templates_dir: Path | None = None):
        self.templates_dir = templates_dir or Path("C:/EQ12/prompts")
        self.templates_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger(f"{__name__}.PromptTemplateManager")

        # Built-in templates
        self.templates: dict[str, BasePromptTemplate] = {
            "sports_betting_expert": SportsBettingPromptTemplate(),
            "code_review_expert": CodeReviewPromptTemplate(),
            "governance_expert": GovernancePromptTemplate(),
        }

        # Performance tracking
        self.metrics_file = self.templates_dir / "performance_metrics.json"
        self.load_metrics()

    def register_template(self, template: BasePromptTemplate):
        """Register a new prompt template"""
        self.templates[template.name] = template
        self.logger.info(f"Registered template: {template.name}")

    def get_template(self, name: str) -> BasePromptTemplate:
        """Get template by name"""
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")
        return self.templates[name]

    def list_templates(self) -> dict[str, dict[str, Any]]:
        """List all available templates"""
        return {
            name: {
                "category": template.category.value,
                "description": template.description,
                "version": template.version,
                "variables": list(template.variables.keys()),
                "metrics": asdict(template.metrics),
            }
            for name, template in self.templates.items()
        }

    def generate_conversation(self, template_name: str, **kwargs) -> list[ConversationMessage]:
        """Generate conversation from template"""
        template = self.get_template(template_name)

        try:
            messages = template.generate_messages(**kwargs)

            # Update metrics
            template.metrics.total_uses += 1

            self.logger.info(f"Generated conversation using template: {template_name}")
            return messages

        except Exception as e:
            self.logger.error(f"Failed to generate conversation: {e}")
            raise

    def update_performance_metrics(
        self,
        template_name: str,
        success: bool,
        response_time: float,
        tokens_used: int,
        cost: float,
        satisfaction: float | None = None,
    ):
        """Update performance metrics for a template"""
        if template_name not in self.templates:
            return

        template = self.templates[template_name]
        metrics = template.metrics

        # Update success rate
        total_attempts = metrics.total_uses
        current_success_rate = metrics.success_rate

        if total_attempts > 0:
            new_success_rate = (
                (current_success_rate * (total_attempts - 1)) + (1.0 if success else 0.0)
            ) / total_attempts
            metrics.success_rate = new_success_rate

        # Update averages
        if total_attempts > 0:
            metrics.average_response_time = (
                (metrics.average_response_time * (total_attempts - 1)) + response_time
            ) / total_attempts
            metrics.average_tokens_used = (
                (metrics.average_tokens_used * (total_attempts - 1)) + tokens_used
            ) / total_attempts
            metrics.average_cost = (
                (metrics.average_cost * (total_attempts - 1)) + cost
            ) / total_attempts

        if satisfaction is not None:
            if total_attempts > 0:
                metrics.user_satisfaction = (
                    (metrics.user_satisfaction * (total_attempts - 1)) + satisfaction
                ) / total_attempts
            else:
                metrics.user_satisfaction = satisfaction

        metrics.last_updated = datetime.now()
        self.save_metrics()

    def load_metrics(self):
        """Load performance metrics from file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file) as f:
                    data = json.load(f)

                for template_name, metrics_data in data.items():
                    if template_name in self.templates:
                        template = self.templates[template_name]
                        template.metrics = PromptPerformanceMetrics(**metrics_data)

            except Exception as e:
                self.logger.warning(f"Failed to load metrics: {e}")

    def save_metrics(self):
        """Save performance metrics to file"""
        try:
            data = {name: asdict(template.metrics) for name, template in self.templates.items()}

            with open(self.metrics_file, "w") as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            self.logger.warning(f"Failed to save metrics: {e}")

    def export_template(self, template_name: str, file_path: Path):
        """Export template to YAML file"""
        template = self.get_template(template_name)

        template_data = {
            "name": template.name,
            "category": template.category.value,
            "description": template.description,
            "version": template.version,
            "variables": {
                var_name: {
                    "description": var.description,
                    "required": var.required,
                    "default_value": var.default_value,
                    "validation_pattern": var.validation_pattern,
                    "suggestions": var.suggestions,
                }
                for var_name, var in template.variables.items()
            },
        }

        with open(file_path, "w") as f:
            yaml.dump(template_data, f, indent=2)

        self.logger.info(f"Exported template {template_name} to {file_path}")


# Example usage
if __name__ == "__main__":
    # Initialize template manager
    manager = PromptTemplateManager()

    print("🎯 EQ12 Advanced Prompt Engineering Framework")
    print("=" * 50)

    # List available templates
    templates = manager.list_templates()
    print(f"\n📋 Available Templates ({len(templates)}):")
    for name, info in templates.items():
        print(f"  • {name} ({info['category']}): {info['description']}")

    # Example: Generate sports betting conversation
    print("\n🎲 Example: Sports Betting Analysis")
    try:
        messages = manager.generate_conversation(
            "sports_betting_expert",
            game_info="Chiefs vs Bills, NFL Week 8, Sunday 1PM EST",
            bet_type="Moneyline",
            odds="-150",
            estimated_probability="65.0",
            bankroll="1000.00",
            context="Chiefs coming off bye week, Bills missing Stefon Diggs",
        )

        print(f"Generated {len(messages)} messages:")
        for i, msg in enumerate(messages, 1):
            print(f"\n{i}. {msg.role.value.upper()}:")
            print(f"   {msg.content[:200]}...")

    except Exception as e:
        print(f"❌ Failed: {e}")

    # Performance metrics example
    print("\n📊 Template Performance Metrics:")
    for name, template in manager.templates.items():
        metrics = template.metrics
        print(f"\n{name}:")
        print(f"  Uses: {metrics.total_uses}")
        print(f"  Success Rate: {metrics.success_rate:.1%}")
        if metrics.average_cost > 0:
            print(f"  Avg Cost: ${metrics.average_cost:.4f}")
