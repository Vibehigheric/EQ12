#!/usr/bin/env python3
"""
EQ12 OpenAI Optimization Module
Advanced parameter control for OpenAI API calls with preset profiles
Based on temperature and top_p sampling best practices
"""

import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProfile(Enum):
    """Predefined AI personality profiles for different use cases"""

    COMPLIANCE = "compliance"
    CREATIVE = "creative"
    BALANCED = "balanced"
    CODE_GENERATION = "code_generation"
    CODE_COMMENTS = "code_comments"
    DATA_ANALYSIS = "data_analysis"
    EXPLORATORY = "exploratory"
    CHATBOT = "chatbot"
    GOVERNANCE = "governance"
    RISK_ASSESSMENT = "risk_assessment"


@dataclass
class OptimizationProfile:
    """Configuration for OpenAI API optimization parameters"""

    name: str
    description: str
    temperature: float
    top_p: float
    max_tokens: int | None = None
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    use_case: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert profile to dictionary for API calls"""
        params = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
        }
        if self.max_tokens:
            params["max_tokens"] = self.max_tokens
        return params


class OpenAIOptimizer:
    """Advanced OpenAI API optimizer with intelligent parameter selection"""

    def __init__(self, api_key: str | None = None):
        """Initialize OpenAI optimizer"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable."
            )

        self.client = OpenAI(api_key=self.api_key, max_retries=0, timeout=30.0)
        self.profiles = self._initialize_profiles()
        self.usage_stats = {}

    def _initialize_profiles(self) -> dict[AIProfile, OptimizationProfile]:
        """Initialize predefined optimization profiles"""
        return {
            AIProfile.COMPLIANCE: OptimizationProfile(
                name="Compliance Mode",
                description="Generates deterministic, policy-focused responses for governance and compliance tasks",
                temperature=0.2,
                top_p=0.1,
                max_tokens=1500,
                use_case="Generates code that adheres to established patterns and conventions. Output is more deterministic and focused.",
            ),
            AIProfile.CREATIVE: OptimizationProfile(
                name="Creative Problem-Solving",
                description="Generates innovative, diverse solutions for complex governance challenges",
                temperature=0.7,
                top_p=0.8,
                max_tokens=2000,
                use_case="Generates creative and diverse text for innovative problem-solving. Output is more exploratory and less constrained.",
            ),
            AIProfile.BALANCED: OptimizationProfile(
                name="Balanced Analysis",
                description="Provides natural, comprehensive responses balancing accuracy and creativity",
                temperature=0.5,
                top_p=0.5,
                max_tokens=1800,
                use_case="Generates balanced responses that are both coherent and engaging for general analysis tasks.",
            ),
            AIProfile.CODE_GENERATION: OptimizationProfile(
                name="Code Generation",
                description="Optimized for generating syntactically correct, conventional code",
                temperature=0.2,
                top_p=0.1,
                max_tokens=2500,
                use_case="Generates code that adheres to established patterns and conventions. Output is deterministic and focused.",
            ),
            AIProfile.CODE_COMMENTS: OptimizationProfile(
                name="Code Documentation",
                description="Generates concise, relevant code comments and documentation",
                temperature=0.3,
                top_p=0.2,
                max_tokens=1000,
                use_case="Generates code comments that are concise and relevant. Output adheres to documentation conventions.",
            ),
            AIProfile.DATA_ANALYSIS: OptimizationProfile(
                name="Data Analysis Scripting",
                description="Creates efficient, correct data analysis scripts and reports",
                temperature=0.2,
                top_p=0.1,
                max_tokens=2000,
                use_case="Generates data analysis scripts that are correct and efficient. Output is deterministic and focused.",
            ),
            AIProfile.EXPLORATORY: OptimizationProfile(
                name="Exploratory Code Writing",
                description="Explores alternative solutions and creative approaches to coding challenges",
                temperature=0.6,
                top_p=0.7,
                max_tokens=2200,
                use_case="Generates code that explores alternative solutions. Output is less constrained by established patterns.",
            ),
            AIProfile.CHATBOT: OptimizationProfile(
                name="Conversational Responses",
                description="Natural, engaging responses for interactive conversations",
                temperature=0.5,
                top_p=0.5,
                max_tokens=1200,
                use_case="Generates conversational responses that balance coherence and diversity for natural engagement.",
            ),
            AIProfile.GOVERNANCE: OptimizationProfile(
                name="Governance Analysis",
                description="Structured analysis for organizational governance and policy decisions",
                temperature=0.3,
                top_p=0.3,
                max_tokens=2500,
                frequency_penalty=0.1,
                use_case="Generates structured governance analysis with focus on policy compliance and organizational standards.",
            ),
            AIProfile.RISK_ASSESSMENT: OptimizationProfile(
                name="Risk Assessment",
                description="Thorough risk analysis with conservative, evidence-based recommendations",
                temperature=0.1,
                top_p=0.05,
                max_tokens=2000,
                frequency_penalty=0.2,
                use_case="Generates conservative risk assessments based on evidence and established risk management frameworks.",
            ),
        }

    def get_profile(self, profile: AIProfile | str) -> OptimizationProfile:
        """Get optimization profile by enum or string name"""
        if isinstance(profile, str):
            try:
                profile = AIProfile(profile.lower())
            except ValueError:
                raise ValueError(f"Unknown profile: {profile}")

        return self.profiles[profile]

    def create_custom_profile(
        self,
        name: str,
        temperature: float,
        top_p: float,
        description: str = "",
        max_tokens: int | None = None,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
    ) -> OptimizationProfile:
        """Create a custom optimization profile"""
        return OptimizationProfile(
            name=name,
            description=description,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

    def optimize_completion(
        self,
        prompt: str,
        profile: AIProfile | str | OptimizationProfile,
        model: str = "gpt-4",
        system_prompt: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generate optimized completion using specified profile

        Args:
            prompt: The user prompt
            profile: AI profile to use (enum, string, or custom profile)
            model: OpenAI model to use
            system_prompt: Optional system prompt
            **kwargs: Additional OpenAI API parameters

        Returns:
            Dictionary containing response and metadata
        """
        # Get optimization parameters
        if isinstance(profile, OptimizationProfile):
            opt_profile = profile
        else:
            opt_profile = self.get_profile(profile)

        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Merge optimization parameters with any additional kwargs
        api_params = {
            "model": model,
            "messages": messages,
            **opt_profile.to_dict(),
            **kwargs,
        }

        try:
            # Make API call
            logger.info(f"Making OpenAI call with profile: {opt_profile.name}")
            response = self.client.chat.completions.create(**api_params)

            # Track usage statistics
            self._track_usage(opt_profile.name, response.usage)

            # Return structured response
            return {
                "content": response.choices[0].message.content,
                "profile_used": opt_profile.name,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "parameters_used": opt_profile.to_dict(),
                "model": model,
            }

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e!s}")
            raise

    def optimize_governance_task(
        self, task_type: str, content: str, context: str | None = None
    ) -> dict[str, Any]:
        """
        Optimize for specific governance tasks with intelligent profile selection

        Args:
            task_type: Type of governance task (compliance, risk, policy, etc.)
            content: The content to analyze
            context: Additional context for the analysis

        Returns:
            Optimized analysis result
        """
        # Intelligent profile selection based on task type
        profile_mapping = {
            "compliance": AIProfile.COMPLIANCE,
            "risk": AIProfile.RISK_ASSESSMENT,
            "policy": AIProfile.GOVERNANCE,
            "audit": AIProfile.COMPLIANCE,
            "analysis": AIProfile.BALANCED,
            "creative": AIProfile.CREATIVE,
            "code": AIProfile.CODE_GENERATION,
            "documentation": AIProfile.CODE_COMMENTS,
        }

        selected_profile = profile_mapping.get(task_type.lower(), AIProfile.BALANCED)

        # Build optimized prompt
        system_prompt = f"""You are an expert governance analyst specializing in {task_type} tasks.
        Provide structured, actionable insights based on the content provided."""

        user_prompt = f"Task Type: {task_type}\n\nContent: {content}"
        if context:
            user_prompt += f"\n\nAdditional Context: {context}"

        return self.optimize_completion(
            prompt=user_prompt, profile=selected_profile, system_prompt=system_prompt
        )

    def _track_usage(self, profile_name: str, usage: Any) -> None:
        """Track usage statistics for optimization analysis"""
        if profile_name not in self.usage_stats:
            self.usage_stats[profile_name] = {
                "calls": 0,
                "total_tokens": 0,
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
            }

        stats = self.usage_stats[profile_name]
        stats["calls"] += 1
        stats["total_tokens"] += usage.total_tokens
        stats["total_prompt_tokens"] += usage.prompt_tokens
        stats["total_completion_tokens"] += usage.completion_tokens

    def get_usage_report(self) -> dict[str, Any]:
        """Get comprehensive usage statistics and cost analysis"""
        total_tokens = sum(stats["total_tokens"] for stats in self.usage_stats.values())
        total_calls = sum(stats["calls"] for stats in self.usage_stats.values())

        return {
            "summary": {
                "total_calls": total_calls,
                "total_tokens": total_tokens,
                "profiles_used": len(self.usage_stats),
            },
            "by_profile": self.usage_stats,
            "recommendations": self._generate_optimization_recommendations(),
        }

    def _generate_optimization_recommendations(self) -> list[str]:
        """Generate recommendations for further optimization"""
        recommendations = []

        if not self.usage_stats:
            return ["No usage data available for analysis"]

        # Analyze token efficiency by profile
        for profile, stats in self.usage_stats.items():
            avg_tokens = stats["total_tokens"] / stats["calls"] if stats["calls"] > 0 else 0
            if avg_tokens > 2000:
                recommendations.append(
                    f"Consider reducing max_tokens for {profile} profile to improve efficiency"
                )

        # Check for overuse of high-creativity profiles
        creative_calls = sum(
            stats["calls"]
            for profile, stats in self.usage_stats.items()
            if "creative" in profile.lower() or "exploratory" in profile.lower()
        )
        if creative_calls > total_calls * 0.5:
            recommendations.append(
                "High usage of creative profiles detected. Consider using more deterministic profiles for routine tasks"
            )

        if len(recommendations) == 0:
            recommendations.append(
                "Usage patterns look optimal. Continue current optimization strategy."
            )

        return recommendations

    def export_profiles(self, filepath: str) -> None:
        """Export all profiles to JSON file for backup/sharing"""
        profiles_data = {}
        for profile_enum, profile_obj in self.profiles.items():
            profiles_data[profile_enum.value] = {
                "name": profile_obj.name,
                "description": profile_obj.description,
                "temperature": profile_obj.temperature,
                "top_p": profile_obj.top_p,
                "max_tokens": profile_obj.max_tokens,
                "frequency_penalty": profile_obj.frequency_penalty,
                "presence_penalty": profile_obj.presence_penalty,
                "use_case": profile_obj.use_case,
            }

        with open(filepath, "w") as f:
            json.dump(profiles_data, f, indent=2)

        logger.info(f"Profiles exported to {filepath}")


# Example usage and testing
if __name__ == "__main__":
    try:
        # Initialize optimizer
        optimizer = OpenAIOptimizer()

        # Test different profiles
        test_prompt = "Analyze the compliance implications of implementing automated decision-making in financial services."

        print("=== OpenAI Optimization Module Test ===\n")

        # Test compliance profile
        print("1. Testing Compliance Profile:")
        compliance_result = optimizer.optimize_completion(
            prompt=test_prompt, profile=AIProfile.COMPLIANCE, model="gpt-3.5-turbo"
        )
        print(f"Profile: {compliance_result['profile_used']}")
        print(f"Tokens used: {compliance_result['usage']['total_tokens']}")
        print(f"Response length: {len(compliance_result['content'])} characters")
        print(f"Parameters: {compliance_result['parameters_used']}\n")

        # Test creative profile
        print("2. Testing Creative Profile:")
        creative_result = optimizer.optimize_completion(
            prompt="How can we innovate governance frameworks for remote work?",
            profile=AIProfile.CREATIVE,
            model="gpt-3.5-turbo",
        )
        print(f"Profile: {creative_result['profile_used']}")
        print(f"Tokens used: {creative_result['usage']['total_tokens']}")
        print(f"Response length: {len(creative_result['content'])} characters")
        print(f"Parameters: {creative_result['parameters_used']}\n")

        # Test governance task optimization
        print("3. Testing Governance Task Optimization:")
        governance_result = optimizer.optimize_governance_task(
            task_type="risk",
            content="New AI deployment in customer service",
            context="Financial services company with 10,000+ customers",
        )
        print(f"Profile selected: {governance_result['profile_used']}")
        print(f"Tokens used: {governance_result['usage']['total_tokens']}")
        print(f"Response preview: {governance_result['content'][:200]}...\n")

        # Display usage report
        print("4. Usage Report:")
        usage_report = optimizer.get_usage_report()
        print(json.dumps(usage_report, indent=2))

        # Export profiles
        optimizer.export_profiles("eq12_ai_profiles_backup.json")

    except Exception as e:
        print(f"Error testing OpenAI Optimizer: {e}")
        print("Make sure OPENAI_API_KEY is set in your environment variables.")
